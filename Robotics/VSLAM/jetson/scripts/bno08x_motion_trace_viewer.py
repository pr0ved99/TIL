#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
import sys
import threading
import time
from collections import deque


def _parse_int(value: str) -> int:
    return int(value, 0)


def _print_missing_dependency(exc: Exception) -> None:
    print(f"missing dependency: {exc}")
    print()
    print("install steps:")
    print("  sudo apt update")
    print("  sudo apt install -y python3-pip python3-dev python3-venv python3-smbus i2c-tools")
    print("  python3 -m venv ~/venvs/bno08x")
    print("  source ~/venvs/bno08x/bin/activate")
    print(
        "  pip install adafruit-blinka "
        "adafruit-circuitpython-bno08x "
        "adafruit-extended-bus "
        "pyserial smbus2 matplotlib"
    )


def _make_bno_i2c(bus: int, address: int):
    try:
        from adafruit_extended_bus import ExtendedI2C
        from adafruit_bno08x.i2c import BNO08X_I2C
    except ModuleNotFoundError as exc:
        _print_missing_dependency(exc)
        raise SystemExit(1) from exc

    i2c = ExtendedI2C(bus)
    return BNO08X_I2C(i2c, address=address)


def _make_bno_uart(port: str, baud: int):
    try:
        import serial
        from adafruit_bno08x.uart import BNO08X_UART
    except ModuleNotFoundError as exc:
        _print_missing_dependency(exc)
        raise SystemExit(1) from exc

    uart = serial.Serial(port, baudrate=baud, timeout=1)
    return BNO08X_UART(uart)


def _quat_to_matrix(quat):
    if quat is None:
        return None

    x, y, z, w = quat
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if math.isclose(norm, 0.0):
        return None

    x /= norm
    y /= norm
    z /= norm
    w /= norm

    return (
        (
            1.0 - 2.0 * (y * y + z * z),
            2.0 * (x * y - z * w),
            2.0 * (x * z + y * w),
        ),
        (
            2.0 * (x * y + z * w),
            1.0 - 2.0 * (x * x + z * z),
            2.0 * (y * z - x * w),
        ),
        (
            2.0 * (x * z - y * w),
            2.0 * (y * z + x * w),
            1.0 - 2.0 * (x * x + y * y),
        ),
    )


def _apply_matrix(matrix, point):
    x, y, z = point
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z,
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z,
        matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z,
    )


def _vector_magnitude(vector):
    if vector is None:
        return None
    return math.sqrt(sum(v * v for v in vector))


def _set_axes_equal(ax, radius):
    ax.set_xlim(-radius, radius)
    ax.set_ylim(-radius, radius)
    ax.set_zlim(-radius, radius)
    ax.set_box_aspect((1.0, 1.0, 1.0))


class MotionTracker:
    def __init__(self, bno, deadband: float, damping: float, speed_floor: float, trail_length: int):
        self.bno = bno
        self.deadband = deadband
        self.damping = damping
        self.speed_floor = speed_floor
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._latest_quat = None
        self._latest_linear_body = None
        self._latest_linear_world = None
        self._position = (0.0, 0.0, 0.0)
        self._velocity = (0.0, 0.0, 0.0)
        self._trail = deque(maxlen=trail_length)
        self._latest_update = None
        self._last_error = None
        self._first_sample_printed = False

    def reset(self) -> None:
        with self._lock:
            self._position = (0.0, 0.0, 0.0)
            self._velocity = (0.0, 0.0, 0.0)
            self._trail.clear()

    def start(self, rate_hz: float) -> None:
        period = 1.0 / max(rate_hz, 1.0)

        def _run():
            next_tick = time.monotonic()
            prev_tick = None
            while not self._stop_event.is_set():
                try:
                    quat = self.bno.quaternion
                    linear_body = self.bno.linear_acceleration
                    matrix = _quat_to_matrix(quat)
                    now = time.monotonic()
                    dt = period if prev_tick is None else max(1e-4, min(0.2, now - prev_tick))
                    prev_tick = now

                    if matrix is not None and linear_body is not None:
                        linear_world = _apply_matrix(matrix, linear_body)
                    else:
                        linear_world = None

                    if linear_world is not None:
                        linear_world = tuple(
                            0.0 if abs(component) < self.deadband else component for component in linear_world
                        )
                        if _vector_magnitude(linear_world) is not None and _vector_magnitude(linear_world) < self.deadband:
                            linear_world = (0.0, 0.0, 0.0)

                    with self._lock:
                        velocity = self._velocity
                        position = self._position

                        if linear_world is not None:
                            decay = math.exp(-self.damping * dt)
                            velocity = tuple((v + a * dt) * decay for v, a in zip(velocity, linear_world))
                            if _vector_magnitude(velocity) is not None and _vector_magnitude(velocity) < self.speed_floor:
                                velocity = (0.0, 0.0, 0.0)
                            position = tuple(p + v * dt for p, v in zip(position, velocity))

                        self._latest_quat = quat
                        self._latest_linear_body = linear_body
                        self._latest_linear_world = linear_world
                        self._velocity = velocity
                        self._position = position
                        self._trail.append(position)
                        self._latest_update = time.time()
                        self._last_error = None

                    if (not self._first_sample_printed) and linear_body is not None:
                        print(
                            "first motion sample:",
                            f"linear_body={linear_body}",
                            f"linear_world={linear_world}",
                            f"position={position}",
                            f"velocity={velocity}",
                        )
                        self._first_sample_printed = True
                except Exception as exc:  # noqa: BLE001
                    with self._lock:
                        self._last_error = str(exc)

                next_tick += period
                sleep_time = next_tick - time.monotonic()
                if sleep_time > 0.0:
                    self._stop_event.wait(sleep_time)
                else:
                    next_tick = time.monotonic()
                    self._stop_event.wait(0.001)

        self._thread = threading.Thread(target=_run, daemon=True, name="bno08x-motion-trace-poll")
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    def snapshot(self):
        with self._lock:
            return {
                "quat": self._latest_quat,
                "linear_body": self._latest_linear_body,
                "linear_world": self._latest_linear_world,
                "position": self._position,
                "velocity": self._velocity,
                "trail": list(self._trail),
                "update": self._latest_update,
                "error": self._last_error,
            }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Visualize short-term pseudo-position from BNO08x linear acceleration."
    )
    parser.add_argument("--interface", choices=("i2c", "uart"), required=True)
    parser.add_argument("--bus", type=int, default=1, help="I2C bus number for I2C mode")
    parser.add_argument(
        "--address",
        type=_parse_int,
        default=0x4B,
        help="I2C address for I2C mode, e.g. 0x4A or 0x4B",
    )
    parser.add_argument("--uart-port", default="/dev/ttyTHS1", help="UART port for UART mode")
    parser.add_argument("--baud", type=int, default=3000000, help="UART baud rate for UART mode")
    parser.add_argument("--sensor-rate", type=float, default=100.0, help="Background sensor polling rate in Hz")
    parser.add_argument("--rate", type=float, default=30.0, help="Viewer redraw rate in Hz")
    parser.add_argument("--radius", type=float, default=0.6, help="Minimum 3D view radius")
    parser.add_argument("--trail-length", type=int, default=180, help="Number of past points to keep")
    parser.add_argument("--accel-deadband", type=float, default=0.15, help="Deadband for linear acceleration in m/s^2")
    parser.add_argument("--velocity-damping", type=float, default=1.5, help="Velocity damping coefficient")
    parser.add_argument("--speed-floor", type=float, default=0.02, help="Velocity magnitude below this is clamped to zero")
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from adafruit_bno08x import BNO_REPORT_LINEAR_ACCELERATION, BNO_REPORT_ROTATION_VECTOR
    except ModuleNotFoundError as exc:
        _print_missing_dependency(exc)
        return 1

    if args.interface == "i2c":
        bno = _make_bno_i2c(args.bus, args.address)
        source_label = f"I2C bus={args.bus} address={hex(args.address)}"
    else:
        bno = _make_bno_uart(args.uart_port, args.baud)
        source_label = f"UART port={args.uart_port} baud={args.baud}"

    print(f"opened BNO08x over {source_label}")
    bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

    tracker = MotionTracker(
        bno=bno,
        deadband=args.accel_deadband,
        damping=args.velocity_damping,
        speed_floor=args.speed_floor,
        trail_length=args.trail_length,
    )
    tracker.start(args.sensor_rate)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    fig.suptitle(
        f"BNO08x Motion Trace Viewer ({source_label})\n"
        f"poll={args.sensor_rate:.0f}Hz draw={args.rate:.0f}Hz pseudo-position from linear acceleration"
    )

    ax.set_title("Pseudo Position / Motion Trace")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.view_init(elev=22, azim=35)
    _set_axes_equal(ax, args.radius)
    ax.grid(True, alpha=0.3)

    ax.plot([0.0, 0.5], [0.0, 0.0], [0.0, 0.0], linestyle="--", linewidth=1.5, color="#d62728", alpha=0.45)
    ax.plot([0.0, 0.0], [0.0, 0.5], [0.0, 0.0], linestyle="--", linewidth=1.5, color="#2ca02c", alpha=0.45)
    ax.plot([0.0, 0.0], [0.0, 0.0], [0.0, 0.5], linestyle="--", linewidth=1.5, color="#ff7f0e", alpha=0.45)
    ax.text(0.55, 0.0, 0.0, "X", color="#d62728")
    ax.text(0.0, 0.55, 0.0, "Y", color="#2ca02c")
    ax.text(0.0, 0.0, 0.55, "Z", color="#ff7f0e")

    trail_line = ax.plot([], [], [], linewidth=2.0, color="#1f77b4", alpha=0.85)[0]
    current_point = ax.plot([0.0], [0.0], [0.0], marker="o", markersize=9, color="#1f77b4")[0]
    origin_point = ax.plot([0.0], [0.0], [0.0], marker="x", markersize=10, color="#777777")[0]
    _ = origin_point

    info_text = fig.text(0.5, 0.07, "waiting for motion samples...", ha="center", fontsize=12, family="monospace")
    help_text = fig.text(
        0.5,
        0.035,
        "This is short-term pseudo-position, not true position. Press 'r' to reset trace.",
        ha="center",
        fontsize=10,
    )
    _ = help_text

    def _on_key(event):
        if event.key == "r":
            tracker.reset()
            print("[INFO] motion trace reset")

    fig.canvas.mpl_connect("key_press_event", _on_key)

    def _update(_frame):
        snapshot = tracker.snapshot()
        position = snapshot["position"]
        velocity = snapshot["velocity"]
        linear_world = snapshot["linear_world"]
        linear_body = snapshot["linear_body"]
        trail = snapshot["trail"]

        if not trail:
            message = f"sensor read error: {snapshot['error']}" if snapshot["error"] else "waiting for linear acceleration samples..."
            info_text.set_text(message)
            return trail_line, current_point, info_text

        xs = [point[0] for point in trail]
        ys = [point[1] for point in trail]
        zs = [point[2] for point in trail]
        trail_line.set_data(xs, ys)
        trail_line.set_3d_properties(zs)
        current_point.set_data([position[0]], [position[1]])
        current_point.set_3d_properties([position[2]])

        max_extent = max(args.radius, max((abs(v) for point in trail for v in point), default=0.0) * 1.25 + 0.05)
        _set_axes_equal(ax, max_extent)

        pos_mag = _vector_magnitude(position)
        vel_mag = _vector_magnitude(velocity)
        lin_mag = _vector_magnitude(linear_world)
        info_text.set_text(
            "   ".join(
                [
                    f"pos=({position[0]: .3f}, {position[1]: .3f}, {position[2]: .3f}) m*",
                    f"|pos|={pos_mag:.3f}" if pos_mag is not None else "|pos|=--",
                    f"vel=({velocity[0]: .3f}, {velocity[1]: .3f}, {velocity[2]: .3f}) m/s",
                    f"|vel|={vel_mag:.3f}" if vel_mag is not None else "|vel|=--",
                    f"lin_world=({linear_world[0]: .3f}, {linear_world[1]: .3f}, {linear_world[2]: .3f})"
                    if linear_world is not None else "lin_world=--",
                    f"|lin|={lin_mag:.3f}" if lin_mag is not None else "|lin|=--",
                    f"lin_body=({linear_body[0]: .3f}, {linear_body[1]: .3f}, {linear_body[2]: .3f})"
                    if linear_body is not None else "lin_body=--",
                ]
            )
        )
        return trail_line, current_point, info_text

    interval_ms = int(1000.0 / max(args.rate, 0.1))
    animation = FuncAnimation(fig, _update, interval=interval_ms, blit=False, cache_frame_data=False)

    try:
        plt.tight_layout(rect=(0.0, 0.11, 1.0, 0.93))
        plt.show()
    finally:
        tracker.stop()
        _ = animation

    return 0


if __name__ == "__main__":
    sys.exit(main())
