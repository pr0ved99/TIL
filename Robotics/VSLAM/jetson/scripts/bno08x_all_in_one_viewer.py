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


def _vector_magnitude(value):
    if value is None:
        return None
    return math.sqrt(sum(v * v for v in value))


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


def _heading_to_cardinal(heading_deg: float) -> str:
    labels = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    index = int((heading_deg + 22.5) % 360.0 // 45.0)
    return labels[index]


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _vector_dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _left_axis_from_forward(forward):
    fx, fy, _ = forward
    return (-fy, fx, 0.0)


def _movement_hint(linear_accel, forward_axis, move_threshold, vertical_threshold):
    if linear_accel is None:
        return "--"

    forward_component = _vector_dot(linear_accel, forward_axis)
    left_component = _vector_dot(linear_accel, _left_axis_from_forward(forward_axis))
    up_component = linear_accel[2]
    linear_mag = _vector_magnitude(linear_accel)

    if linear_mag is None or linear_mag < move_threshold:
        return "still"

    parts = []
    if forward_component >= move_threshold:
        parts.append("forward")
    elif forward_component <= -move_threshold:
        parts.append("back")

    if left_component >= move_threshold:
        parts.append("left")
    elif left_component <= -move_threshold:
        parts.append("right")

    vertical_parts = []
    if up_component >= vertical_threshold:
        vertical_parts.append("up")
    elif up_component <= -vertical_threshold:
        vertical_parts.append("down")

    if not parts and not vertical_parts:
        dominant = max(
            (
                ("forward", abs(forward_component), forward_component >= 0.0),
                ("left", abs(left_component), left_component >= 0.0),
                ("up", abs(up_component), up_component >= 0.0),
            ),
            key=lambda item: item[1],
        )
        label, _, positive = dominant
        if label == "forward":
            return "forward" if positive else "back"
        if label == "left":
            return "left" if positive else "right"
        return "up" if positive else "down"

    movement = "-".join(parts) if parts else "drift"
    if vertical_parts:
        movement += f" +{vertical_parts[0]}"
    return movement


def _calibration_label(status: int, labels):
    if 0 <= status < len(labels):
        return labels[status].replace("Accuracy ", "")
    return str(status)


class BnoTracker:
    def __init__(self, bno):
        self.bno = bno
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._latest_quat = None
        self._latest_accel = None
        self._latest_gyro = None
        self._latest_mag = None
        self._latest_gravity = None
        self._latest_linear_accel = None
        self._latest_calibration = None
        self._latest_calibration_label = None
        self._latest_euler = None
        self._latest_update = None
        self._last_error = None
        self._first_sample_printed = False

    def start(self, rate_hz: float) -> None:
        period = 1.0 / max(rate_hz, 1.0)
        calibration_period = 0.5

        def _run():
            next_tick = time.monotonic()
            next_calibration_read = next_tick
            while not self._stop_event.is_set():
                try:
                    quat = self.bno.quaternion
                    accel = self.bno.acceleration
                    gyro = self.bno.gyro
                    mag = self.bno.magnetic
                    gravity = self.bno.gravity
                    linear_accel = self.bno.linear_acceleration
                    calibration = None
                    calibration_label = None
                    now = time.monotonic()
                    if now >= next_calibration_read:
                        calibration = self.bno.calibration_status
                        calibration_label = calibration if calibration is None else calibration
                        next_calibration_read = now + calibration_period
                    euler = _quat_to_euler_deg(quat)
                    with self._lock:
                        self._latest_quat = quat
                        self._latest_accel = accel
                        self._latest_gyro = gyro
                        self._latest_mag = mag
                        self._latest_gravity = gravity
                        self._latest_linear_accel = linear_accel
                        if calibration is not None:
                            self._latest_calibration = calibration
                            self._latest_calibration_label = calibration_label
                        self._latest_euler = euler
                        self._latest_update = time.time()
                        self._last_error = None
                    if (not self._first_sample_printed) and quat is not None:
                        print(
                            "first all-in-one sample:",
                            f"quat={quat}",
                            f"euler={euler}",
                            f"accel={accel}",
                            f"gyro={gyro}",
                            f"mag={mag}",
                            f"gravity={gravity}",
                            f"linear_accel={linear_accel}",
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

        self._thread = threading.Thread(target=_run, daemon=True, name="bno08x-all-in-one-poll")
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
                "mag": self._latest_mag,
                "gravity": self._latest_gravity,
                "linear_accel": self._latest_linear_accel,
                "calibration": self._latest_calibration,
                "calibration_label": self._latest_calibration_label,
                "euler": self._latest_euler,
                "update": self._latest_update,
                "error": self._last_error,
            }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Visualize BNO08x heading, level, attitude and rotation in one dashboard."
    )
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
    parser.add_argument("--sensor-rate", type=float, default=100.0, help="Background sensor polling rate in Hz")
    parser.add_argument("--rate", type=float, default=30.0, help="Viewer redraw rate in Hz")
    parser.add_argument("--radius", type=float, default=1.2, help="3D scene radius")
    parser.add_argument(
        "--forward-axis",
        choices=("x", "y", "-x", "-y"),
        default="x",
        help="Which body axis should be treated as heading direction",
    )
    parser.add_argument("--heading-offset", type=float, default=0.0, help="Manual compass rotation offset in degrees")
    parser.add_argument("--declination", type=float, default=0.0, help="Magnetic declination correction in degrees")
    parser.add_argument("--max-angle", type=float, default=15.0, help="Level bubble outer ring angle in degrees")
    parser.add_argument("--level-threshold", type=float, default=2.0, help="Absolute roll/pitch threshold in degrees considered level")
    parser.add_argument("--roll-offset", type=float, default=0.0, help="Manual roll correction in degrees")
    parser.add_argument("--pitch-offset", type=float, default=0.0, help="Manual pitch correction in degrees")
    parser.add_argument("--move-threshold", type=float, default=0.20, help="Linear acceleration threshold in m/s^2 to classify movement")
    parser.add_argument("--vertical-threshold", type=float, default=0.25, help="Vertical linear acceleration threshold in m/s^2")
    parser.add_argument("--zero-on-start", action="store_true", help="Treat first valid sample as level reference")
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from matplotlib.gridspec import GridSpec
        from adafruit_bno08x import (
            BNO_REPORT_ACCELEROMETER,
            BNO_REPORT_GRAVITY,
            BNO_REPORT_GYROSCOPE,
            BNO_REPORT_LINEAR_ACCELERATION,
            BNO_REPORT_MAGNETOMETER,
            BNO_REPORT_ROTATION_VECTOR,
            REPORT_ACCURACY_STATUS,
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
    bno.enable_feature(BNO_REPORT_GRAVITY)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

    tracker = BnoTracker(bno)
    tracker.start(args.sensor_rate)
    body_forward = _parse_forward_axis(args.forward_axis)

    fig = plt.figure(figsize=(14, 8))
    gs = GridSpec(2, 2, figure=fig, width_ratios=[1.45, 1.0], height_ratios=[1.0, 1.0])
    ax3d = fig.add_subplot(gs[:, 0], projection="3d")
    ax_compass = fig.add_subplot(gs[0, 1])
    ax_level = fig.add_subplot(gs[1, 1])

    fig.suptitle(
        f"BNO08x All-In-One Viewer ({source_label})\n"
        f"poll={args.sensor_rate:.0f}Hz draw={args.rate:.0f}Hz axis={args.forward_axis}"
    )

    ax3d.set_title("Attitude / Tilt")
    ax3d.set_xlabel("X")
    ax3d.set_ylabel("Y")
    ax3d.set_zlabel("Z")
    ax3d.view_init(elev=20, azim=35)
    _set_axes_equal(ax3d, args.radius)
    ax3d.grid(True, alpha=0.3)

    ax_compass.set_title("Compass / Heading")
    ax_compass.set_aspect("equal")
    ax_compass.set_xlim(-1.2, 1.2)
    ax_compass.set_ylim(-1.2, 1.2)
    ax_compass.axis("off")

    ax_level.set_title("Level / Roll-Pitch")
    ax_level.set_aspect("equal")
    ax_level.set_xlim(-1.15, 1.15)
    ax_level.set_ylim(-1.15, 1.15)
    ax_level.axis("off")

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
    aircraft_lines = [ax3d.plot([], [], [], linewidth=3.0, color="#1f77b4")[0] for _ in segments]
    axis_lines = [
        ax3d.plot([], [], [], linewidth=2.0, color="#d62728")[0],
        ax3d.plot([], [], [], linewidth=2.0, color="#2ca02c")[0],
        ax3d.plot([], [], [], linewidth=2.0, color="#ff7f0e")[0],
    ]
    world_axis_lines = [
        ax3d.plot([0.0, 0.8], [0.0, 0.0], [0.0, 0.0], linestyle="--", linewidth=1.5, color="#d62728", alpha=0.45)[0],
        ax3d.plot([0.0, 0.0], [0.0, 0.8], [0.0, 0.0], linestyle="--", linewidth=1.5, color="#2ca02c", alpha=0.45)[0],
        ax3d.plot([0.0, 0.0], [0.0, 0.0], [0.0, 0.8], linestyle="--", linewidth=1.5, color="#ff7f0e", alpha=0.45)[0],
    ]
    reference_lines = [ax3d.plot([], [], [], linewidth=2.0, linestyle=":", color="#7f7f7f", alpha=0.8)[0] for _ in segments]
    ax3d.text(args.radius, 0.0, 0.0, "X", color="#d62728")
    ax3d.text(0.0, args.radius, 0.0, "Y", color="#2ca02c")
    ax3d.text(0.0, 0.0, args.radius, "Z", color="#ff7f0e")

    circle = plt.Circle((0.0, 0.0), 1.0, fill=False, linewidth=2.0, color="#444444")
    ax_compass.add_patch(circle)
    ax_compass.plot([0.0, 0.0], [-1.0, 1.0], linestyle="--", linewidth=1.0, color="#cccccc")
    ax_compass.plot([-1.0, 1.0], [0.0, 0.0], linestyle="--", linewidth=1.0, color="#cccccc")
    ax_compass.text(0.0, 1.08, "N", ha="center", va="center", fontsize=16, color="#d62728", weight="bold")
    ax_compass.text(1.08, 0.0, "E", ha="center", va="center", fontsize=14)
    ax_compass.text(0.0, -1.08, "S", ha="center", va="center", fontsize=14)
    ax_compass.text(-1.08, 0.0, "W", ha="center", va="center", fontsize=14)
    heading_arrow = ax_compass.plot([], [], linewidth=4.0, color="#1f77b4")[0]
    heading_relative_arrow = ax_compass.plot([], [], linewidth=2.0, linestyle=":", color="#7f7f7f", alpha=0.9)[0]
    heading_center = ax_compass.plot([0.0], [0.0], marker="o", markersize=8, color="#1f77b4")[0]

    outer = plt.Circle((0.0, 0.0), 1.0, fill=False, linewidth=2.2, color="#444444")
    threshold_radius = min(1.0, args.level_threshold / max(args.max_angle, 0.1))
    inner = plt.Circle((0.0, 0.0), threshold_radius, fill=False, linewidth=1.2, color="#8bc34a")
    ax_level.add_patch(outer)
    ax_level.add_patch(inner)
    ax_level.plot([0.0, 0.0], [-1.0, 1.0], linestyle="--", linewidth=1.0, color="#cccccc")
    ax_level.plot([-1.0, 1.0], [0.0, 0.0], linestyle="--", linewidth=1.0, color="#cccccc")
    ax_level.text(0.0, 1.08, "+pitch", ha="center", va="center", fontsize=11)
    ax_level.text(0.0, -1.08, "-pitch", ha="center", va="center", fontsize=11)
    ax_level.text(1.08, 0.0, "+roll", ha="center", va="center", fontsize=11)
    ax_level.text(-1.08, 0.0, "-roll", ha="center", va="center", fontsize=11)
    bubble = ax_level.plot([0.0], [0.0], marker="o", markersize=18, color="#1f77b4")[0]
    bubble_shadow = ax_level.plot([0.0], [0.0], marker="o", markersize=26, alpha=0.15, color="#1f77b4")[0]
    center_mark = ax_level.plot([0.0], [0.0], marker="+", markersize=16, mew=2, color="#666666")[0]

    panel_header = fig.text(0.5, 0.125, "waiting for BNO08x samples...", ha="center", fontsize=13)

    panel_font = {"fontsize": 11, "family": "monospace"}
    value_font = {"fontsize": 11, "family": "monospace", "weight": "bold"}

    row1_y = 0.088
    row2_y = 0.064
    row3_y = 0.040
    row4_y = 0.016

    labels = {
        "heading": fig.text(0.06, row1_y, "Heading:", ha="left", **panel_font),
        "roll": fig.text(0.28, row1_y, "Roll:", ha="left", **panel_font),
        "pitch": fig.text(0.43, row1_y, "Pitch:", ha="left", **panel_font),
        "yaw": fig.text(0.58, row1_y, "Yaw:", ha="left", **panel_font),
        "turn_rate": fig.text(0.72, row1_y, "Turn:", ha="left", **panel_font),
        "state": fig.text(0.06, row2_y, "State:", ha="left", **panel_font),
        "move": fig.text(0.40, row2_y, "Move:", ha="left", **panel_font),
        "gyro": fig.text(0.06, row3_y, "Gyro:", ha="left", **panel_font),
        "accel": fig.text(0.40, row3_y, "Accel:", ha="left", **panel_font),
        "mag": fig.text(0.74, row3_y, "Mag:", ha="left", **panel_font),
        "gravity": fig.text(0.06, row4_y, "Gravity:", ha="left", **panel_font),
        "linear": fig.text(0.40, row4_y, "Linear:", ha="left", **panel_font),
        "calib": fig.text(0.74, row4_y, "Calib:", ha="left", **panel_font),
    }
    _ = labels

    heading_value = fig.text(0.14, row1_y, "--", ha="left", **value_font)
    roll_value = fig.text(0.34, row1_y, "--", ha="left", **value_font)
    pitch_value = fig.text(0.50, row1_y, "--", ha="left", **value_font)
    yaw_value = fig.text(0.64, row1_y, "--", ha="left", **value_font)
    turn_rate_value = fig.text(0.78, row1_y, "--", ha="left", **value_font)
    state_value = fig.text(0.14, row2_y, "--", ha="left", **value_font)
    move_value = fig.text(0.48, row2_y, "--", ha="left", **value_font)

    gyro_value = fig.text(0.13, row3_y, "--", ha="left", fontsize=10, family="monospace")
    accel_value = fig.text(0.48, row3_y, "--", ha="left", fontsize=10, family="monospace")
    mag_value = fig.text(0.80, row3_y, "--", ha="left", fontsize=10, family="monospace")
    gravity_value = fig.text(0.16, row4_y, "--", ha="left", fontsize=10, family="monospace")
    linear_value = fig.text(0.48, row4_y, "--", ha="left", fontsize=10, family="monospace")
    calib_value = fig.text(0.82, row4_y, "--", ha="left", fontsize=10, family="monospace", weight="bold")

    reference_matrix = None
    first_heading = None
    zero_roll = None
    zero_pitch = None

    def _update(_frame):
        nonlocal reference_matrix, first_heading, zero_roll, zero_pitch
        snapshot = tracker.snapshot()
        quaternion = snapshot["quat"]
        accel = snapshot["accel"]
        gyro = snapshot["gyro"]
        mag = snapshot["mag"]
        gravity = snapshot["gravity"]
        linear_accel = snapshot["linear_accel"]
        calibration = snapshot["calibration"]
        euler = snapshot["euler"]
        matrix = _quat_to_matrix(quaternion)

        if matrix is None or euler is None:
            message = f"sensor read error: {snapshot['error']}" if snapshot["error"] else "waiting for heading / level / attitude..."
            panel_header.set_text(message)
            heading_value.set_text("--")
            roll_value.set_text("--")
            pitch_value.set_text("--")
            yaw_value.set_text("--")
            turn_rate_value.set_text("--")
            state_value.set_text("--")
            move_value.set_text("--")
            gyro_value.set_text("--")
            accel_value.set_text("--")
            mag_value.set_text("--")
            gravity_value.set_text("--")
            linear_value.set_text("--")
            calib_value.set_text("--")
            return (
                *aircraft_lines,
                *axis_lines,
                *world_axis_lines,
                *reference_lines,
                heading_arrow,
                heading_relative_arrow,
                heading_center,
                bubble,
                bubble_shadow,
                center_mark,
                panel_header,
                heading_value,
                roll_value,
                pitch_value,
                yaw_value,
                turn_rate_value,
                state_value,
                move_value,
                gyro_value,
                accel_value,
                mag_value,
                gravity_value,
                linear_value,
                calib_value,
            )

        raw_roll, raw_pitch, yaw = euler
        if args.zero_on_start and zero_roll is None:
            zero_roll = raw_roll
            zero_pitch = raw_pitch

        roll = raw_roll - (zero_roll if zero_roll is not None else 0.0) - args.roll_offset
        pitch = raw_pitch - (zero_pitch if zero_pitch is not None else 0.0) - args.pitch_offset

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

        world_forward = _apply_matrix(matrix, body_forward)
        heading = _heading_from_vector_xy(world_forward)
        relative_heading = None
        if heading is not None:
            heading = (heading + args.heading_offset + args.declination) % 360.0
            if first_heading is None:
                first_heading = heading
            relative_heading = (heading - first_heading) % 360.0

            theta = math.radians(90.0 - heading)
            heading_arrow.set_data([0.0, 0.85 * math.cos(theta)], [0.0, 0.85 * math.sin(theta)])

            rel_theta = math.radians(90.0 - relative_heading)
            heading_relative_arrow.set_data([0.0, 0.65 * math.cos(rel_theta)], [0.0, 0.65 * math.sin(rel_theta)])

        normalized_x = _clamp(roll / max(args.max_angle, 0.1), -1.0, 1.0)
        normalized_y = _clamp(pitch / max(args.max_angle, 0.1), -1.0, 1.0)
        bubble.set_data([normalized_x], [normalized_y])
        bubble_shadow.set_data([normalized_x], [normalized_y])
        is_level = abs(roll) <= args.level_threshold and abs(pitch) <= args.level_threshold
        bubble_color = "#2ca02c" if is_level else "#1f77b4"
        bubble.set_color(bubble_color)
        bubble_shadow.set_color(bubble_color)

        turn_rate = _vector_magnitude(gyro)
        level_status = "LEVEL" if is_level else "TILTED"
        heading_text = (
            f"{heading:05.1f} deg {_heading_to_cardinal(heading)}"
            if heading is not None else
            "heading n/a"
        )
        accel_mag = _vector_magnitude(accel)
        mag_mag = _vector_magnitude(mag)
        gravity_mag = _vector_magnitude(gravity)
        linear_mag = _vector_magnitude(linear_accel)
        move_text = _movement_hint(linear_accel, body_forward, args.move_threshold, args.vertical_threshold)

        header_parts = []
        if relative_heading is not None:
            header_parts.append(f"relative={relative_heading: .1f} deg")
        if args.zero_on_start:
            header_parts.append(
                f"zero_ref=({(zero_roll if zero_roll is not None else 0.0): .1f}, {(zero_pitch if zero_pitch is not None else 0.0): .1f})"
            )
        if accel_mag is not None:
            header_parts.append(f"|a|={accel_mag:.2f} m/s²")
        if mag_mag is not None:
            header_parts.append(f"|B|={mag_mag:.1f} uT")
        if gravity_mag is not None:
            header_parts.append(f"|g|={gravity_mag:.2f} m/s²")
        if linear_mag is not None:
            header_parts.append(f"|lin|={linear_mag:.2f} m/s²")
        panel_header.set_text("   ".join(header_parts) if header_parts else "BNO08x telemetry")

        heading_value.set_text(heading_text)
        roll_value.set_text(f"{roll: .1f} deg")
        pitch_value.set_text(f"{pitch: .1f} deg")
        yaw_value.set_text(f"{yaw: .1f} deg")
        turn_rate_value.set_text(f"{turn_rate: .2f} rad/s" if turn_rate is not None else "--")
        state_value.set_text(level_status)
        move_value.set_text(move_text)
        gyro_value.set_text(
            f"({gyro[0]: .3f}, {gyro[1]: .3f}, {gyro[2]: .3f})" if gyro is not None else "--"
        )
        accel_value.set_text(
            f"({accel[0]: .3f}, {accel[1]: .3f}, {accel[2]: .3f})" if accel is not None else "--"
        )
        mag_value.set_text(
            f"({mag[0]: .3f}, {mag[1]: .3f}, {mag[2]: .3f})" if mag is not None else "--"
        )
        gravity_value.set_text(
            f"({gravity[0]: .3f}, {gravity[1]: .3f}, {gravity[2]: .3f})" if gravity is not None else "--"
        )
        linear_value.set_text(
            f"({linear_accel[0]: .3f}, {linear_accel[1]: .3f}, {linear_accel[2]: .3f})"
            if linear_accel is not None else "--"
        )
        if calibration is None:
            calib_value.set_text("--")
        else:
            calib_label = _calibration_label(calibration, REPORT_ACCURACY_STATUS)
            calib_value.set_text(f"{calibration} {calib_label}")

        return (
            *aircraft_lines,
            *axis_lines,
            *world_axis_lines,
            *reference_lines,
            heading_arrow,
            heading_relative_arrow,
            heading_center,
            bubble,
            bubble_shadow,
            center_mark,
            panel_header,
            heading_value,
            roll_value,
            pitch_value,
            yaw_value,
            turn_rate_value,
            state_value,
            move_value,
            gyro_value,
            accel_value,
            mag_value,
            gravity_value,
            linear_value,
            calib_value,
        )

    interval_ms = int(1000.0 / max(args.rate, 0.1))
    animation = FuncAnimation(fig, _update, interval=interval_ms, blit=False, cache_frame_data=False)

    try:
        plt.tight_layout(rect=(0.0, 0.16, 1.0, 0.95))
        plt.show()
    finally:
        tracker.stop()
        _ = animation
    return 0


if __name__ == "__main__":
    sys.exit(main())
