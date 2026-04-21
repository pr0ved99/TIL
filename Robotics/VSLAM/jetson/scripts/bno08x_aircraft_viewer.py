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


def _mat_mul(a, b):
    return tuple(
        tuple(sum(a[row][k] * b[k][col] for k in range(3)) for col in range(3))
        for row in range(3)
    )


def _mat_transpose(matrix):
    return tuple(tuple(matrix[col][row] for col in range(3)) for row in range(3))


def _set_axes_equal(ax, radius):
    ax.set_xlim(-radius, radius)
    ax.set_ylim(-radius, radius)
    ax.set_zlim(-radius, radius)
    ax.set_box_aspect((1.0, 1.0, 1.0))


class BnoTracker:
    def __init__(self, bno, source_label):
        self.bno = bno
        self.source_label = source_label
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._started = False
        self._latest_quat = None
        self._latest_accel = None
        self._latest_gyro = None
        self._latest_euler = None
        self._latest_update = None
        self._first_sample_printed = False
        self._last_error = None

    def start(self, rate_hz: float) -> None:
        if self._started:
            return
        self._started = True
        period = 1.0 / max(rate_hz, 1.0)

        def _run():
            next_tick = time.monotonic()
            while not self._stop_event.is_set():
                try:
                    quat = self.bno.quaternion
                    accel = self.bno.acceleration
                    gyro = self.bno.gyro
                    euler = _quat_to_euler_deg(quat)
                    with self._lock:
                        self._latest_quat = quat
                        self._latest_accel = accel
                        self._latest_gyro = gyro
                        self._latest_euler = euler
                        self._latest_update = time.time()
                        self._last_error = None
                    if (not self._first_sample_printed) and quat is not None:
                        print("first quaternion:", quat)
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

        self._thread = threading.Thread(target=_run, daemon=True, name="bno08x-aircraft-poll")
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    def snapshot(self):
        with self._lock:
            return {
                "quat": self._latest_quat,
                "accel": self._latest_accel,
                "gyro": self._latest_gyro,
                "euler": self._latest_euler,
                "update": self._latest_update,
                "error": self._last_error,
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Visualize BNO08x orientation with a simple aircraft model.")
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
        "--rate",
        type=float,
        default=20.0,
        help="Viewer redraw rate in Hz",
    )
    parser.add_argument(
        "--sensor-rate",
        type=float,
        default=100.0,
        help="Background sensor polling rate in Hz",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=1.2,
        help="View radius for the 3D scene",
    )
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from adafruit_bno08x import (
            BNO_REPORT_ACCELEROMETER,
            BNO_REPORT_GYROSCOPE,
            BNO_REPORT_MAGNETOMETER,
            BNO_REPORT_ROTATION_VECTOR,
        )
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

    bno.enable_feature(BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

    tracker = BnoTracker(bno, source_label)
    tracker.start(args.sensor_rate)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    fig.suptitle(
        f"BNO08x Aircraft Viewer ({source_label})"
        f"\npoll={args.sensor_rate:.0f}Hz draw={args.rate:.0f}Hz"
    )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.view_init(elev=20, azim=35)
    _set_axes_equal(ax, args.radius)
    ax.grid(True, alpha=0.3)

    body_points = {
        "nose": (1.0, 0.0, 0.0),
        "tail": (-0.7, 0.0, 0.0),
        "wing_l": (0.0, 0.8, 0.0),
        "wing_r": (0.0, -0.8, 0.0),
        "tail_top": (-0.45, 0.0, 0.45),
    }
    segments = [
        ("nose", "tail"),
        ("wing_l", "wing_r"),
        ("tail", "tail_top"),
        ("nose", "wing_l"),
        ("nose", "wing_r"),
    ]

    aircraft_lines = [ax.plot([], [], [], linewidth=3.0, color="#1f77b4")[0] for _ in segments]
    axis_lines = [
        ax.plot([], [], [], linewidth=2.0, color="#d62728")[0],
        ax.plot([], [], [], linewidth=2.0, color="#2ca02c")[0],
        ax.plot([], [], [], linewidth=2.0, color="#ff7f0e")[0],
    ]

    ax.text(args.radius, 0.0, 0.0, "X", color="#d62728")
    ax.text(0.0, args.radius, 0.0, "Y", color="#2ca02c")
    ax.text(0.0, 0.0, args.radius, "Z", color="#ff7f0e")

    info_text = fig.text(0.02, 0.02, "waiting for samples...", fontsize=10)
    reference_matrix = None

    world_axis_lines = [
        ax.plot([0.0, 0.8], [0.0, 0.0], [0.0, 0.0], linestyle="--", linewidth=1.5, color="#d62728", alpha=0.45)[0],
        ax.plot([0.0, 0.0], [0.0, 0.8], [0.0, 0.0], linestyle="--", linewidth=1.5, color="#2ca02c", alpha=0.45)[0],
        ax.plot([0.0, 0.0], [0.0, 0.0], [0.0, 0.8], linestyle="--", linewidth=1.5, color="#ff7f0e", alpha=0.45)[0],
    ]
    reference_lines = [ax.plot([], [], [], linewidth=2.0, linestyle=":", color="#7f7f7f", alpha=0.8)[0] for _ in segments]

    def _update(_frame):
        nonlocal reference_matrix
        snapshot = tracker.snapshot()
        quaternion = snapshot["quat"]
        accel = snapshot["accel"]
        gyro = snapshot["gyro"]
        euler = snapshot["euler"]
        matrix = _quat_to_matrix(quaternion)

        if matrix is None:
            if snapshot["error"]:
                info_text.set_text(f"sensor read error: {snapshot['error']}")
            else:
                info_text.set_text("quaternion not ready yet")
            return (*aircraft_lines, *axis_lines, *world_axis_lines, *reference_lines, info_text)

        if reference_matrix is None:
            reference_matrix = matrix

        relative_matrix = _mat_mul(_mat_transpose(reference_matrix), matrix)

        transformed = {name: _apply_matrix(relative_matrix, point) for name, point in body_points.items()}
        for line, (start_name, end_name) in zip(aircraft_lines, segments):
            start = transformed[start_name]
            end = transformed[end_name]
            line.set_data([start[0], end[0]], [start[1], end[1]])
            line.set_3d_properties([start[2], end[2]])

        basis = (
            ((0.0, 0.0, 0.0), _apply_matrix(relative_matrix, (0.8, 0.0, 0.0))),
            ((0.0, 0.0, 0.0), _apply_matrix(relative_matrix, (0.0, 0.8, 0.0))),
            ((0.0, 0.0, 0.0), _apply_matrix(relative_matrix, (0.0, 0.0, 0.8))),
        )
        for line, (start, end) in zip(axis_lines, basis):
            line.set_data([start[0], end[0]], [start[1], end[1]])
            line.set_3d_properties([start[2], end[2]])

        for line, (start_name, end_name) in zip(reference_lines, segments):
            start = body_points[start_name]
            end = body_points[end_name]
            line.set_data([start[0], end[0]], [start[1], end[1]])
            line.set_3d_properties([start[2], end[2]])

        if euler is not None:
            roll, pitch, yaw = euler
            info_text.set_text(
                f"roll={roll: .1f} deg   pitch={pitch: .1f} deg   yaw={yaw: .1f} deg   "
                "body: +X nose / +Y left wing / +Z up   "
                f"accel={accel}   gyro={gyro}   "
                f"poll={args.sensor_rate:.0f}Hz draw={args.rate:.0f}Hz"
            )

        return (*aircraft_lines, *axis_lines, *world_axis_lines, *reference_lines, info_text)

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
