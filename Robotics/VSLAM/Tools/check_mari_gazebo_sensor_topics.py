#!/usr/bin/env python3
"""Check that Mari Gazebo baseline sensor topics are being published."""

import argparse
import sys
import time
from dataclasses import dataclass

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CameraInfo, Image, Imu


@dataclass(frozen=True)
class TopicSpec:
    label: str
    topic: str
    msg_type: type
    ros_type: str


class TopicProbe(Node):
    def __init__(self, specs):
        super().__init__("mari_gazebo_sensor_topic_probe")
        self.specs = specs
        self.samples = {
            spec.topic: {
                "count": 0,
                "first_time": None,
                "last_time": None,
                "summary": "no messages",
            }
            for spec in specs
        }

        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT

        self.subscriptions_ = []
        for spec in specs:
            self.subscriptions_.append(
                self.create_subscription(
                    spec.msg_type,
                    spec.topic,
                    self._make_callback(spec),
                    qos,
                )
            )

    def _make_callback(self, spec):
        def callback(msg):
            now = time.monotonic()
            sample = self.samples[spec.topic]
            if sample["first_time"] is None:
                sample["first_time"] = now
            sample["last_time"] = now
            sample["count"] += 1
            sample["summary"] = summarize_message(msg)

        return callback


def summarize_message(msg):
    header = getattr(msg, "header", None)
    frame_id = getattr(header, "frame_id", "") if header is not None else ""

    if isinstance(msg, Image):
        return (
            f"frame={frame_id or '-'} size={msg.width}x{msg.height} "
            f"encoding={msg.encoding}"
        )

    if isinstance(msg, CameraInfo):
        return f"frame={frame_id or '-'} size={msg.width}x{msg.height}"

    if isinstance(msg, Imu):
        return (
            f"frame={frame_id or '-'} "
            f"angular_z={msg.angular_velocity.z:.5f} "
            f"linear_z={msg.linear_acceleration.z:.5f}"
        )

    if isinstance(msg, Odometry):
        return (
            f"frame={frame_id or '-'} child={msg.child_frame_id or '-'} "
            f"x={msg.pose.pose.position.x:.3f} "
            f"y={msg.pose.pose.position.y:.3f}"
        )

    return f"frame={frame_id or '-'}"


def format_rate(sample):
    count = sample["count"]
    first_time = sample["first_time"]
    last_time = sample["last_time"]
    if count < 2 or first_time is None or last_time is None or last_time <= first_time:
        return "n/a"
    return f"{(count - 1) / (last_time - first_time):.1f} Hz"


def expected_specs(args):
    return [
        TopicSpec("odom", args.odom_topic, Odometry, "nav_msgs/msg/Odometry"),
        TopicSpec("imu", args.imu_topic, Imu, "sensor_msgs/msg/Imu"),
        TopicSpec("rgb image", args.rgb_topic, Image, "sensor_msgs/msg/Image"),
        TopicSpec("depth image", args.depth_topic, Image, "sensor_msgs/msg/Image"),
        TopicSpec(
            "rgb camera info",
            args.rgb_info_topic,
            CameraInfo,
            "sensor_msgs/msg/CameraInfo",
        ),
        TopicSpec(
            "depth camera info",
            args.depth_info_topic,
            CameraInfo,
            "sensor_msgs/msg/CameraInfo",
        ),
    ]


def graph_topic_types(node):
    return {name: sorted(types) for name, types in node.get_topic_names_and_types()}


def print_result(spec, sample, graph_types, min_count):
    count = sample["count"]
    rate = format_rate(sample)
    graph_type_text = ",".join(graph_types.get(spec.topic, [])) or "not in graph"
    ok = count >= min_count and spec.ros_type in graph_types.get(spec.topic, [spec.ros_type])
    status = "OK" if ok else "FAIL"
    print(
        f"[{status}] {spec.label}: {spec.topic} "
        f"type={graph_type_text} count={count} rate={rate} {sample['summary']}"
    )
    return ok


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check Mari Gazebo odom, IMU, RGB image, depth image, and camera_info topics."
    )
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--min-count", type=int, default=1)
    parser.add_argument("--odom-topic", default="/odom")
    parser.add_argument("--imu-topic", default="/imu/data")
    parser.add_argument("--rgb-topic", default="/camera/camera/color/image_raw")
    parser.add_argument(
        "--depth-topic",
        default="/camera/camera/aligned_depth_to_color/image_raw",
    )
    parser.add_argument("--rgb-info-topic", default="/camera/camera/color/camera_info")
    parser.add_argument(
        "--depth-info-topic",
        default="/camera/camera/aligned_depth_to_color/camera_info",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    rclpy.init()
    node = TopicProbe(expected_specs(args))
    deadline = time.monotonic() + args.duration

    try:
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)

        graph_types = graph_topic_types(node)
        print(f"Checked for {args.duration:.1f}s")
        results = [
            print_result(spec, node.samples[spec.topic], graph_types, args.min_count)
            for spec in node.specs
        ]

        print("Graph helpers:")
        for helper in ("/tf", "/tf_static", "/clock", "/cmd_vel"):
            types = ",".join(graph_types.get(helper, [])) or "not in graph"
            print(f"- {helper}: {types}")

        return 0 if all(results) else 1
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
