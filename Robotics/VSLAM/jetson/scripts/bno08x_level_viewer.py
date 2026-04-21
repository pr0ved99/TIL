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


def _vector_magnitude(value):
    if value is None:
        return None
    return math.sqrt(sum(v * v for v in value))


class BnoTracker:
    def __init__(self, bno):
        self.bno = bno
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._latest_quat = None
        self._latest_accel = None
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
                    accel = self.bno.acceleration
                    euler = _quat_to_euler_deg(quat)
                    with self._lock:
                        self._latest_quat = quat
                        self._latest_accel = accel
                        self._latest_euler = euler
                        self._latest_update = time.time()
                        self._last_error = None
                    if (not self._first_sample_printed) and euler is not None:
                        print("first level sample:", f"euler={euler}", f"accel={accel}")
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

        self._thread = threading.Thread(target=_run, daemon=True, name="bno08x-level-poll")
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
                "euler": self._latest_euler,
                "update": self._latest_update,
                "error": self._last_error,
            }


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Visualize BNO08x roll/pitch as a spirit level.")
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
        default=30.0,
        help="Viewer redraw rate in Hz",
    )
    parser.add_argument(
        "--max-angle",
        type=float,
        default=15.0,
        help="Angle in degrees that maps to the outer ring edge",
    )
    parser.add_argument(
        "--level-threshold",
        type=float,
        default=2.0,
        help="Absolute roll/pitch threshold in degrees considered level",
    )
    parser.add_argument(
        "--roll-offset",
        type=float,
        default=0.0,
        help="Manual roll correction in degrees",
    )
    parser.add_argument(
        "--pitch-offset",
        type=float,
        default=0.0,
        help="Manual pitch correction in degrees",
    )
    parser.add_argument(
        "--zero-on-start",
        action="store_true",
        help="Treat the first valid sample as the level reference",
    )
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from adafruit_bno08x import BNO_REPORT_ACCELEROMETER, BNO_REPORT_ROTATION_VECTOR
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
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

    tracker = BnoTracker(bno)
    tracker.start(args.sensor_rate)

    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111)
    fig.suptitle(
        f"BNO08x Level Viewer ({source_label})\n"
        f"poll={args.sensor_rate:.0f}Hz draw={args.rate:.0f}Hz"
    )
    ax.set_aspect("equal")
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.axis("off")

    outer = plt.Circle((0.0, 0.0), 1.0, fill=False, linewidth=2.2, color="#444444")
    threshold_radius = min(1.0, args.level_threshold / max(args.max_angle, 0.1))
    inner = plt.Circle((0.0, 0.0), threshold_radius, fill=False, linewidth=1.2, color="#8bc34a")
    ax.add_patch(outer)
    ax.add_patch(inner)

    ax.plot([0.0, 0.0], [-1.0, 1.0], linestyle="--", linewidth=1.0, color="#cccccc")
    ax.plot([-1.0, 1.0], [0.0, 0.0], linestyle="--", linewidth=1.0, color="#cccccc")

    ax.text(0.0, 1.08, "+pitch", ha="center", va="center", fontsize=12)
    ax.text(0.0, -1.08, "-pitch", ha="center", va="center", fontsize=12)
    ax.text(1.08, 0.0, "+roll", ha="center", va="center", fontsize=12)
    ax.text(-1.08, 0.0, "-roll", ha="center", va="center", fontsize=12)

    bubble = ax.plot([0.0], [0.0], marker="o", markersize=18, color="#1f77b4")[0]
    bubble_shadow = ax.plot([0.0], [0.0], marker="o", markersize=26, alpha=0.15, color="#1f77b4")[0]
    center_mark = ax.plot([0.0], [0.0], marker="+", markersize=16, mew=2, color="#666666")[0]

    status_text = fig.text(0.5, 0.08, "waiting for level data...", ha="center", fontsize=16)
    detail_text = fig.text(0.5, 0.035, "", ha="center", fontsize=10)

    zero_roll = None
    zero_pitch = None

    def _update(_frame):
        nonlocal zero_roll, zero_pitch
        snapshot = tracker.snapshot()
        euler = snapshot["euler"]
        accel = snapshot["accel"]

        if euler is None:
            if snapshot["error"]:
                status_text.set_text(f"sensor read error: {snapshot['error']}")
            else:
                status_text.set_text("waiting for roll/pitch...")
            detail_text.set_text("")
            return bubble, bubble_shadow, center_mark, status_text, detail_text

        raw_roll, raw_pitch, yaw = euler

        if args.zero_on_start and zero_roll is None:
            zero_roll = raw_roll
            zero_pitch = raw_pitch

        roll = raw_roll - (zero_roll if zero_roll is not None else 0.0) - args.roll_offset
        pitch = raw_pitch - (zero_pitch if zero_pitch is not None else 0.0) - args.pitch_offset

        normalized_x = _clamp(roll / max(args.max_angle, 0.1), -1.0, 1.0)
        normalized_y = _clamp(pitch / max(args.max_angle, 0.1), -1.0, 1.0)

        bubble.set_data([normalized_x], [normalized_y])
        bubble_shadow.set_data([normalized_x], [normalized_y])

        is_level = abs(roll) <= args.level_threshold and abs(pitch) <= args.level_threshold
        bubble_color = "#2ca02c" if is_level else "#1f77b4"
        bubble.set_color(bubble_color)
        bubble_shadow.set_color(bubble_color)

        status = "LEVEL" if is_level else "TILTED"
        status_text.set_text(
            f"{status}   roll={roll: .2f} deg   pitch={pitch: .2f} deg"
        )

        parts = [
            f"raw_roll={raw_roll: .2f}",
            f"raw_pitch={raw_pitch: .2f}",
            f"yaw={yaw: .2f}",
            f"|a|={_vector_magnitude(accel):.2f} m/s²" if accel is not None else "accel=none",
            f"threshold={args.level_threshold:.1f} deg",
        ]
        if args.zero_on_start:
            parts.append(
                f"zero_ref=({(zero_roll if zero_roll is not None else 0.0): .2f}, {(zero_pitch if zero_pitch is not None else 0.0): .2f})"
            )
        detail_text.set_text("   ".join(parts))

        return bubble, bubble_shadow, center_mark, status_text, detail_text

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
