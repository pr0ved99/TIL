#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
import sys
import threading
import time


def _print_missing_dependency(exc: Exception) -> None:
    print(f"missing dependency: {exc}")
    print()
    print("install steps:")
    print("  source /opt/ros/humble/setup.bash")
    print("  sudo apt update")
    print("  sudo apt install -y python3-matplotlib")


def _quat_norm(quat):
    return math.sqrt(sum(v * v for v in quat))


def _quat_normalize(quat):
    norm = _quat_norm(quat)
    if math.isclose(norm, 0.0):
        return None
    return tuple(v / norm for v in quat)


def _quat_conjugate(quat):
    x, y, z, w = quat
    return (-x, -y, -z, w)


def _quat_multiply(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def _euler_to_quat(roll, pitch, yaw):
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


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
    quat = _quat_normalize(quat)
    if quat is None:
        return None

    x, y, z, w = quat
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
    return math.sqrt(sum(v * v for v in value))


def _accel_to_roll_pitch(accel):
    ax, ay, az = accel
    roll = math.atan2(ay, az)
    pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))
    return roll, pitch


class ImuTracker:
    def __init__(self, node, alpha):
        self.node = node
        self.alpha = alpha
        self.subscription = None
        self._lock = threading.Lock()
        self.last_stamp = None
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.initialized = False
        self.latest_quat = None
        self.latest_accel = None
        self.latest_gyro = None
        self.latest_mode = "waiting"
        self.latest_frame_id = ""
        self.latest_update = None

    @staticmethod
    def _imu_msg_type():
        from sensor_msgs.msg import Imu

        return Imu

    def subscribe(self, topic):
        from rclpy.qos import qos_profile_sensor_data

        if self.subscription is not None:
            self.node.destroy_subscription(self.subscription)
        self.subscription = self.node.create_subscription(
            self._imu_msg_type(),
            topic,
            self._on_imu,
            qos_profile_sensor_data,
        )

    def _stamp_to_sec(self, msg):
        if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
            return time.monotonic()
        return float(msg.header.stamp.sec) + float(msg.header.stamp.nanosec) * 1e-9

    def _orientation_from_message(self, msg):
        quat = (
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w,
        )
        if msg.orientation_covariance[0] < 0.0:
            return None
        quat = _quat_normalize(quat)
        if quat is None:
            return None
        if _quat_norm(quat) < 0.5:
            return None
        return quat

    def _on_imu(self, msg):
        stamp = self._stamp_to_sec(msg)
        accel = (
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z,
        )
        gyro = (
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z,
        )

        with self._lock:
            self.latest_accel = accel
            self.latest_gyro = gyro
            self.latest_frame_id = msg.header.frame_id or ""
            self.latest_update = time.time()

            quat_from_msg = self._orientation_from_message(msg)
            if quat_from_msg is not None:
                self.latest_quat = quat_from_msg
                self.latest_mode = "message_quaternion"
                self.last_stamp = stamp
                self.initialized = True
                return

            if not self.initialized:
                self.roll, self.pitch = _accel_to_roll_pitch(accel)
                self.yaw = 0.0
                self.initialized = True
                self.last_stamp = stamp
            else:
                dt = 0.0 if self.last_stamp is None else stamp - self.last_stamp
                self.last_stamp = stamp
                if dt < 0.0 or dt > 0.5:
                    dt = 0.0

                self.roll += gyro[0] * dt
                self.pitch += gyro[1] * dt
                self.yaw += gyro[2] * dt

                accel_mag = _vector_magnitude(accel)
                if accel_mag > 1e-6:
                    accel_roll, accel_pitch = _accel_to_roll_pitch(accel)
                    self.roll = self.alpha * self.roll + (1.0 - self.alpha) * accel_roll
                    self.pitch = self.alpha * self.pitch + (1.0 - self.alpha) * accel_pitch

            self.latest_quat = _quat_normalize(_euler_to_quat(self.roll, self.pitch, self.yaw))
            self.latest_mode = "estimated_from_gyro_accel"

    def snapshot(self):
        with self._lock:
            return {
                "quat": self.latest_quat,
                "accel": self.latest_accel,
                "gyro": self.latest_gyro,
                "mode": self.latest_mode,
                "frame_id": self.latest_frame_id,
                "update": self.latest_update,
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Visualize a ROS2 IMU topic with an aircraft viewer.")
    parser.add_argument("--topic", default="/camera/camera/imu", help="ROS2 IMU topic name")
    parser.add_argument("--rate", type=float, default=20.0, help="Viewer redraw rate in Hz")
    parser.add_argument("--radius", type=float, default=1.2, help="View radius for the 3D scene")
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.98,
        help="Complementary filter weight for gyro when orientation is estimated from accel+gyro",
    )
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        import rclpy
        from rclpy.executors import SingleThreadedExecutor
        from rclpy.node import Node
    except ModuleNotFoundError as exc:
        _print_missing_dependency(exc)
        return 1

    rclpy.init(args=None)
    node = Node("ros2_imu_aircraft_viewer")
    tracker = ImuTracker(node, alpha=args.alpha)
    tracker.subscribe(args.topic)
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    fig.suptitle(f"ROS2 IMU Aircraft Viewer ({args.topic})")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.view_init(elev=20, azim=35)
    ax.set_xlim(-args.radius, args.radius)
    ax.set_ylim(-args.radius, args.radius)
    ax.set_zlim(-args.radius, args.radius)
    ax.set_box_aspect((1.0, 1.0, 1.0))
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
    world_axis_lines = [
        ax.plot([0.0, 0.8], [0.0, 0.0], [0.0, 0.0], linestyle="--", linewidth=1.5, color="#d62728", alpha=0.45)[0],
        ax.plot([0.0, 0.0], [0.0, 0.8], [0.0, 0.0], linestyle="--", linewidth=1.5, color="#2ca02c", alpha=0.45)[0],
        ax.plot([0.0, 0.0], [0.0, 0.0], [0.0, 0.8], linestyle="--", linewidth=1.5, color="#ff7f0e", alpha=0.45)[0],
    ]
    reference_lines = [ax.plot([], [], [], linewidth=2.0, linestyle=":", color="#7f7f7f", alpha=0.8)[0] for _ in segments]

    ax.text(args.radius, 0.0, 0.0, "X", color="#d62728")
    ax.text(0.0, args.radius, 0.0, "Y", color="#2ca02c")
    ax.text(0.0, 0.0, args.radius, "Z", color="#ff7f0e")

    info_text = fig.text(0.02, 0.02, "waiting for IMU messages...", fontsize=10)
    reference_quat = None
    first_message_printed = False

    def _update(_frame):
        nonlocal reference_quat, first_message_printed
        snapshot = tracker.snapshot()
        quat = snapshot["quat"]
        if quat is None:
            info_text.set_text(f"waiting for IMU on {args.topic} ...")
            return (*aircraft_lines, *axis_lines, *world_axis_lines, *reference_lines, info_text)

        if reference_quat is None:
            reference_quat = quat

        relative_quat = _quat_multiply(_quat_conjugate(reference_quat), quat)
        matrix = _quat_to_matrix(relative_quat)
        if matrix is None:
            info_text.set_text("IMU quaternion is not ready yet")
            return (*aircraft_lines, *axis_lines, *world_axis_lines, *reference_lines, info_text)

        transformed = {name: _apply_matrix(matrix, point) for name, point in body_points.items()}
        for line, (start_name, end_name) in zip(aircraft_lines, segments):
            start = transformed[start_name]
            end = transformed[end_name]
            line.set_data([start[0], end[0]], [start[1], end[1]])
            line.set_3d_properties([start[2], end[2]])

        basis = (
            ((0.0, 0.0, 0.0), _apply_matrix(matrix, (0.8, 0.0, 0.0))),
            ((0.0, 0.0, 0.0), _apply_matrix(matrix, (0.0, 0.8, 0.0))),
            ((0.0, 0.0, 0.0), _apply_matrix(matrix, (0.0, 0.0, 0.8))),
        )
        for line, (start, end) in zip(axis_lines, basis):
            line.set_data([start[0], end[0]], [start[1], end[1]])
            line.set_3d_properties([start[2], end[2]])

        for line, (start_name, end_name) in zip(reference_lines, segments):
            start = body_points[start_name]
            end = body_points[end_name]
            line.set_data([start[0], end[0]], [start[1], end[1]])
            line.set_3d_properties([start[2], end[2]])

        euler = _quat_to_euler_deg(relative_quat)
        if euler is not None:
            roll, pitch, yaw = euler
            info_text.set_text(
                f"mode={snapshot['mode']}   frame={snapshot['frame_id'] or '-'}   "
                f"roll={roll: .1f} deg   pitch={pitch: .1f} deg   yaw={yaw: .1f} deg   "
                "body: +X nose / +Y left wing / +Z up"
            )

        if not first_message_printed:
            print(
                "first imu message:",
                f"topic={args.topic}",
                f"mode={snapshot['mode']}",
                f"frame_id={snapshot['frame_id']}",
                f"accel={snapshot['accel']}",
                f"gyro={snapshot['gyro']}",
                f"quat={snapshot['quat']}",
            )
            first_message_printed = True

        return (*aircraft_lines, *axis_lines, *world_axis_lines, *reference_lines, info_text)

    interval_ms = int(1000.0 / max(args.rate, 0.1))
    animation = FuncAnimation(fig, _update, interval=interval_ms, blit=False, cache_frame_data=False)

    try:
        plt.tight_layout()
        plt.show()
    finally:
        _ = animation
        executor.shutdown()
        spin_thread.join(timeout=1.0)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
