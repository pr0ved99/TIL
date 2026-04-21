#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
import sys
import threading
import time


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


def _quat_to_euler_deg(quat):
    if quat is None:
        return None

    x, y, z, w = quat

    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.degrees(math.atan2(sinr_cosp, cosr_cosp))

    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.degrees(math.copysign(math.pi / 2.0, sinp))
    else:
        pitch = math.degrees(math.asin(sinp))

    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.degrees(math.atan2(siny_cosp, cosy_cosp))
    return (roll, pitch, yaw)


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


def _vector_magnitude(value):
    if value is None:
        return None
    return math.sqrt(sum(v * v for v in value))


def _heading_to_cardinal(heading_deg: float) -> str:
    labels = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    index = int((heading_deg + 22.5) % 360.0 // 45.0)
    return labels[index]


def _parse_forward_axis(label: str):
    axes = {
        "x": (1.0, 0.0, 0.0),
        "y": (0.0, 1.0, 0.0),
        "-x": (-1.0, 0.0, 0.0),
        "-y": (0.0, -1.0, 0.0),
    }
    return axes[label]


def _heading_from_vector_xy(vector):
    vx, vy, _ = vector
    if math.isclose(vx, 0.0, abs_tol=1e-9) and math.isclose(vy, 0.0, abs_tol=1e-9):
        return None
    return math.degrees(math.atan2(vx, vy)) % 360.0


class BnoTracker:
    def __init__(self, bno):
        self.bno = bno
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._latest_quat = None
        self._latest_mag = None
        self._latest_euler = None
        self._latest_update = None
        self._last_error = None
        self._first_sample_printed = False

    def start(self, rate_hz: float) -> None:
        period = 1.0 / max(rate_hz, 1.0)

        def _run():
            next_tick = time.monotonic()
            while not self._stop_event.is_set():
                try:
                    quat = self.bno.quaternion
                    mag = self.bno.magnetic
                    euler = _quat_to_euler_deg(quat)
                    with self._lock:
                        self._latest_quat = quat
                        self._latest_mag = mag
                        self._latest_euler = euler
                        self._latest_update = time.time()
                        self._last_error = None
                    if (not self._first_sample_printed) and quat is not None:
                        print("first compass sample:", f"quat={quat}", f"mag={mag}", f"euler={euler}")
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

        self._thread = threading.Thread(target=_run, daemon=True, name="bno08x-compass-poll")
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    def snapshot(self):
        with self._lock:
            return {
                "quat": self._latest_quat,
                "mag": self._latest_mag,
                "euler": self._latest_euler,
                "update": self._latest_update,
                "error": self._last_error,
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Visualize BNO08x fused heading as a compass.")
    parser.add_argument("--interface", choices=("i2c", "uart"), required=True)
    parser.add_argument("--bus", type=int, default=1, help="I2C bus number for I2C mode")
    parser.add_argument(
        "--address",
        type=_parse_int,
        default=0x4B,
        help="I2C address for I2C mode, e.g. 0x4A or 0x4B",
    )
    parser.add_argument(
        "--uart-port",
        default="/dev/ttyTHS1",
        help="UART port for UART mode, e.g. /dev/ttyTHS1",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=3000000,
        help="UART baud rate for UART mode",
    )
    parser.add_argument(
        "--sensor-rate",
        type=float,
        default=100.0,
        help="Background sensor polling rate in Hz",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=20.0,
        help="Viewer redraw rate in Hz",
    )
    parser.add_argument(
        "--heading-offset",
        type=float,
        default=0.0,
        help="Manual compass rotation offset in degrees",
    )
    parser.add_argument(
        "--declination",
        type=float,
        default=0.0,
        help="Magnetic declination correction in degrees",
    )
    parser.add_argument(
        "--forward-axis",
        choices=("x", "y", "-x", "-y"),
        default="x",
        help="Which body axis should be treated as the heading direction on the compass",
    )
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from adafruit_bno08x import BNO_REPORT_MAGNETOMETER, BNO_REPORT_ROTATION_VECTOR
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
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

    tracker = BnoTracker(bno)
    tracker.start(args.sensor_rate)
    body_forward = _parse_forward_axis(args.forward_axis)

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.suptitle(
        f"BNO08x Compass Viewer ({source_label})\n"
        f"poll={args.sensor_rate:.0f}Hz draw={args.rate:.0f}Hz axis={args.forward_axis}"
    )
    ax.set_aspect("equal")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")

    circle = plt.Circle((0.0, 0.0), 1.0, fill=False, linewidth=2.0, color="#444444")
    ax.add_patch(circle)
    ax.plot([0.0, 0.0], [-1.0, 1.0], linestyle="--", linewidth=1.0, color="#cccccc")
    ax.plot([-1.0, 1.0], [0.0, 0.0], linestyle="--", linewidth=1.0, color="#cccccc")

    ax.text(0.0, 1.08, "N", ha="center", va="center", fontsize=16, color="#d62728", weight="bold")
    ax.text(1.08, 0.0, "E", ha="center", va="center", fontsize=14)
    ax.text(0.0, -1.08, "S", ha="center", va="center", fontsize=14)
    ax.text(-1.08, 0.0, "W", ha="center", va="center", fontsize=14)

    arrow_line = ax.plot([], [], linewidth=4.0, color="#1f77b4")[0]
    center_dot = ax.plot([0.0], [0.0], marker="o", markersize=8, color="#1f77b4")[0]
    relative_arrow_line = ax.plot([], [], linewidth=2.0, linestyle=":", color="#7f7f7f", alpha=0.9)[0]

    heading_text = fig.text(0.5, 0.06, "waiting for heading...", ha="center", fontsize=16)
    detail_text = fig.text(0.5, 0.02, "", ha="center", fontsize=10)

    first_heading = None

    def _update(_frame):
        nonlocal first_heading
        snapshot = tracker.snapshot()
        euler = snapshot["euler"]
        quat = snapshot["quat"]
        mag = snapshot["mag"]

        matrix = _quat_to_matrix(quat)
        if matrix is None:
            if snapshot["error"]:
                heading_text.set_text(f"sensor read error: {snapshot['error']}")
            else:
                heading_text.set_text("waiting for compass heading...")
            detail_text.set_text("")
            return arrow_line, center_dot, relative_arrow_line, heading_text, detail_text

        world_forward = _apply_matrix(matrix, body_forward)
        heading = _heading_from_vector_xy(world_forward)
        if heading is None:
            heading_text.set_text("heading is not ready yet")
            detail_text.set_text("")
            return arrow_line, center_dot, relative_arrow_line, heading_text, detail_text

        heading = (heading + args.heading_offset + args.declination) % 360.0
        if first_heading is None:
            first_heading = heading
        relative_heading = (heading - first_heading) % 360.0

        theta = math.radians(90.0 - heading)
        x = 0.85 * math.cos(theta)
        y = 0.85 * math.sin(theta)
        arrow_line.set_data([0.0, x], [0.0, y])

        rel_theta = math.radians(90.0 - relative_heading)
        rel_x = 0.65 * math.cos(rel_theta)
        rel_y = 0.65 * math.sin(rel_theta)
        relative_arrow_line.set_data([0.0, rel_x], [0.0, rel_y])

        heading_text.set_text(
            f"{heading:05.1f} deg   {_heading_to_cardinal(heading)}   axis={args.forward_axis}"
        )
        yaw_text = ""
        if euler is not None:
            yaw_text = f"   fused yaw={euler[2]: .1f} deg"
        detail_text.set_text(
            f"relative={relative_heading: .1f} deg{yaw_text}   "
            f"world_axis=({world_forward[0]: .3f}, {world_forward[1]: .3f}, {world_forward[2]: .3f})   "
            f"mag={mag}   |B|={_vector_magnitude(mag):.1f} uT"
            if mag is not None
            else
            f"relative={relative_heading: .1f} deg{yaw_text}   "
            f"world_axis=({world_forward[0]: .3f}, {world_forward[1]: .3f}, {world_forward[2]: .3f})"
        )

        return arrow_line, center_dot, relative_arrow_line, heading_text, detail_text

    interval_ms = int(1000.0 / max(args.rate, 0.1))
    animation = FuncAnimation(fig, _update, interval=interval_ms, blit=False, cache_frame_data=False)

    try:
        plt.tight_layout()
        plt.show()
    finally:
        tracker.stop()
        _ = animation
    return 0


if __name__ == "__main__":
    sys.exit(main())
