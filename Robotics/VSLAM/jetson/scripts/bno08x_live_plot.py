#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
import sys
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


def _vector_magnitude(value):
    if value is None:
        return None
    return math.sqrt(sum(v * v for v in value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Live-plot BNO08x values.")
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
        default=10.0,
        help="Sampling and redraw rate in Hz",
    )
    parser.add_argument(
        "--history",
        type=float,
        default=20.0,
        help="Seconds of history to keep in the plot",
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

    max_points = max(int(args.history * max(args.rate, 0.1)) + 2, 10)
    times = deque(maxlen=max_points)
    accel_x = deque(maxlen=max_points)
    accel_y = deque(maxlen=max_points)
    accel_z = deque(maxlen=max_points)
    gyro_x = deque(maxlen=max_points)
    gyro_y = deque(maxlen=max_points)
    gyro_z = deque(maxlen=max_points)
    mag_x = deque(maxlen=max_points)
    mag_y = deque(maxlen=max_points)
    mag_z = deque(maxlen=max_points)
    roll_hist = deque(maxlen=max_points)
    pitch_hist = deque(maxlen=max_points)
    yaw_hist = deque(maxlen=max_points)

    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    fig.suptitle(f"BNO08x Live Plot ({source_label})")

    accel_lines = [
        axes[0].plot([], [], label="ax")[0],
        axes[0].plot([], [], label="ay")[0],
        axes[0].plot([], [], label="az")[0],
    ]
    gyro_lines = [
        axes[1].plot([], [], label="gx")[0],
        axes[1].plot([], [], label="gy")[0],
        axes[1].plot([], [], label="gz")[0],
    ]
    mag_lines = [
        axes[2].plot([], [], label="mx")[0],
        axes[2].plot([], [], label="my")[0],
        axes[2].plot([], [], label="mz")[0],
    ]
    rpy_lines = [
        axes[3].plot([], [], label="roll")[0],
        axes[3].plot([], [], label="pitch")[0],
        axes[3].plot([], [], label="yaw")[0],
    ]

    axes[0].set_ylabel("m/s^2")
    axes[1].set_ylabel("rad/s")
    axes[2].set_ylabel("uT")
    axes[3].set_ylabel("deg")
    axes[3].set_xlabel("time (s)")

    for axis, title in zip(
        axes,
        (
            "Acceleration",
            "Gyroscope",
            "Magnetometer",
            "Orientation (roll / pitch / yaw)",
        ),
    ):
        axis.set_title(title)
        axis.grid(True, alpha=0.3)
        axis.legend(loc="upper left")

    status_text = fig.text(0.01, 0.01, "waiting for samples...", fontsize=10)
    start_time = time.monotonic()
    first_sample_printed = False

    def _redraw_axis(axis, x_data, y_lists):
        if not x_data:
            return
        axis.set_xlim(max(0.0, x_data[-1] - args.history), max(args.history, x_data[-1]))

        values = [value for values in y_lists for value in values]
        if values:
            vmin = min(values)
            vmax = max(values)
            if math.isclose(vmin, vmax):
                pad = 1.0 if math.isclose(vmin, 0.0) else abs(vmin) * 0.1
            else:
                pad = (vmax - vmin) * 0.15
            axis.set_ylim(vmin - pad, vmax + pad)

    def _update(_frame):
        nonlocal first_sample_printed
        accel = bno.acceleration
        gyro = bno.gyro
        magnetic = bno.magnetic
        quaternion = bno.quaternion
        euler = _quat_to_euler_deg(quaternion)

        t_now = time.monotonic() - start_time
        times.append(t_now)

        for target, value in zip((accel_x, accel_y, accel_z), accel or (float("nan"),) * 3):
            target.append(value)
        for target, value in zip((gyro_x, gyro_y, gyro_z), gyro or (float("nan"),) * 3):
            target.append(value)
        for target, value in zip((mag_x, mag_y, mag_z), magnetic or (float("nan"),) * 3):
            target.append(value)
        for target, value in zip((roll_hist, pitch_hist, yaw_hist), euler or (float("nan"),) * 3):
            target.append(value)

        for line, values in zip(accel_lines, (accel_x, accel_y, accel_z)):
            line.set_data(times, values)
        for line, values in zip(gyro_lines, (gyro_x, gyro_y, gyro_z)):
            line.set_data(times, values)
        for line, values in zip(mag_lines, (mag_x, mag_y, mag_z)):
            line.set_data(times, values)
        for line, values in zip(rpy_lines, (roll_hist, pitch_hist, yaw_hist)):
            line.set_data(times, values)

        _redraw_axis(axes[0], times, (accel_x, accel_y, accel_z))
        _redraw_axis(axes[1], times, (gyro_x, gyro_y, gyro_z))
        _redraw_axis(axes[2], times, (mag_x, mag_y, mag_z))
        _redraw_axis(axes[3], times, (roll_hist, pitch_hist, yaw_hist))

        accel_mag = _vector_magnitude(accel)
        gyro_mag = _vector_magnitude(gyro)
        quat_norm = _vector_magnitude(quaternion[:3]) if quaternion is not None else None
        if quaternion is not None:
            quat_norm = math.sqrt(sum(v * v for v in quaternion))

        status_parts = []
        if accel_mag is not None:
            status_parts.append(f"|a|={accel_mag:.3f} m/s^2")
        if gyro_mag is not None:
            status_parts.append(f"|g|={gyro_mag:.3f} rad/s")
        if quat_norm is not None:
            status_parts.append(f"|q|={quat_norm:.3f}")
        status_text.set_text("   ".join(status_parts) if status_parts else "waiting for samples...")

        if not first_sample_printed:
            print(
                "first sample:",
                f"accel={accel}",
                f"gyro={gyro}",
                f"mag={magnetic}",
                f"quat={quaternion}",
            )
            first_sample_printed = True

        return (
            *accel_lines,
            *gyro_lines,
            *mag_lines,
            *rpy_lines,
            status_text,
        )

    interval_ms = int(1000.0 / max(args.rate, 0.1))
    animation = FuncAnimation(fig, _update, interval=interval_ms, blit=False, cache_frame_data=False)

    plt.tight_layout()
    plt.show()
    _ = animation
    return 0


if __name__ == "__main__":
    sys.exit(main())
