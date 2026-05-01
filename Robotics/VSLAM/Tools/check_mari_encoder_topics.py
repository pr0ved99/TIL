#!/usr/bin/env python3
"""Discover likely Mari wheel encoder or wheel odometry topics."""

import argparse
import math
import sys
import time
from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import Twist, TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState
from std_msgs.msg import (
    Float32,
    Float32MultiArray,
    Float64,
    Float64MultiArray,
    Int32,
    Int32MultiArray,
    Int64,
    Int64MultiArray,
)


SUPPORTED_TYPES = {
    "nav_msgs/msg/Odometry": Odometry,
    "sensor_msgs/msg/JointState": JointState,
    "std_msgs/msg/Int32": Int32,
    "std_msgs/msg/Int64": Int64,
    "std_msgs/msg/Float32": Float32,
    "std_msgs/msg/Float64": Float64,
    "std_msgs/msg/Int32MultiArray": Int32MultiArray,
    "std_msgs/msg/Int64MultiArray": Int64MultiArray,
    "std_msgs/msg/Float32MultiArray": Float32MultiArray,
    "std_msgs/msg/Float64MultiArray": Float64MultiArray,
    "geometry_msgs/msg/Twist": Twist,
    "geometry_msgs/msg/TwistStamped": TwistStamped,
}


@dataclass(frozen=True)
class Candidate:
    topic: str
    ros_type: str
    supported: bool


class EncoderTopicProbe(Node):
    def __init__(self, args):
        super().__init__("mari_encoder_topic_probe")
        self.args = args
        self.candidates = []
        self.samples = {}
        self.subscriptions_ = []

        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT
        self.qos = qos

    def discover(self):
        topic_names_and_types = self.get_topic_names_and_types()
        include_tokens = split_tokens(self.args.include)
        exclude_tokens = split_tokens(self.args.exclude)

        candidates = []
        for topic, ros_types in sorted(topic_names_and_types):
            if not self.args.all_topics and not is_candidate(
                topic, ros_types, include_tokens, exclude_tokens
            ):
                continue

            for ros_type in ros_types:
                candidates.append(
                    Candidate(
                        topic=topic,
                        ros_type=ros_type,
                        supported=ros_type in SUPPORTED_TYPES,
                    )
                )

        self.candidates = candidates

        for candidate in self.candidates:
            self.samples[(candidate.topic, candidate.ros_type)] = {
                "count": 0,
                "first_time": None,
                "last_time": None,
                "summary": "no messages",
            }
            if not candidate.supported:
                continue

            msg_type = SUPPORTED_TYPES[candidate.ros_type]
            self.subscriptions_.append(
                self.create_subscription(
                    msg_type,
                    candidate.topic,
                    self._make_callback(candidate),
                    self.qos,
                )
            )

    def _make_callback(self, candidate):
        def callback(msg):
            now = time.monotonic()
            sample = self.samples[(candidate.topic, candidate.ros_type)]
            if sample["first_time"] is None:
                sample["first_time"] = now
            sample["last_time"] = now
            sample["count"] += 1
            sample["summary"] = summarize_message(msg)

        return callback


def split_tokens(text):
    return [token.strip().lower() for token in text.split(",") if token.strip()]


def is_candidate(topic, ros_types, include_tokens, exclude_tokens):
    topic_lower = topic.lower()
    haystack = f"{topic_lower} {' '.join(ros_types).lower()}"
    if any(token and token in topic_lower for token in exclude_tokens):
        return False
    return any(token and token in haystack for token in include_tokens)


def quaternion_to_yaw(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def summarize_sequence(values, max_items=4):
    shown = list(values[:max_items])
    text = ", ".join(format_number(value) for value in shown)
    if len(values) > max_items:
        text += ", ..."
    return text


def format_number(value):
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def summarize_message(msg):
    if isinstance(msg, Odometry):
        pose = msg.pose.pose
        twist = msg.twist.twist
        yaw = quaternion_to_yaw(pose.orientation)
        return (
            f"frame={msg.header.frame_id or '-'} child={msg.child_frame_id or '-'} "
            f"x={pose.position.x:.3f} y={pose.position.y:.3f} yaw={yaw:.3f} "
            f"vx={twist.linear.x:.3f} wz={twist.angular.z:.3f}"
        )

    if isinstance(msg, JointState):
        names = list(msg.name[:4])
        name_text = ",".join(names) if names else "-"
        pos_text = summarize_sequence(msg.position) if msg.position else "-"
        vel_text = summarize_sequence(msg.velocity) if msg.velocity else "-"
        return f"names={name_text} pos=[{pos_text}] vel=[{vel_text}]"

    if isinstance(msg, (Int32, Int64, Float32, Float64)):
        return f"data={format_number(msg.data)}"

    if isinstance(
        msg,
        (Int32MultiArray, Int64MultiArray, Float32MultiArray, Float64MultiArray),
    ):
        return f"len={len(msg.data)} data=[{summarize_sequence(msg.data)}]"

    if isinstance(msg, Twist):
        return f"vx={msg.linear.x:.3f} wz={msg.angular.z:.3f}"

    if isinstance(msg, TwistStamped):
        return (
            f"frame={msg.header.frame_id or '-'} "
            f"vx={msg.twist.linear.x:.3f} wz={msg.twist.angular.z:.3f}"
        )

    return "message received"


def format_rate(sample):
    count = sample["count"]
    first_time = sample["first_time"]
    last_time = sample["last_time"]
    if count < 2 or first_time is None or last_time is None or last_time <= first_time:
        return "n/a"
    return f"{(count - 1) / (last_time - first_time):.1f} Hz"


def print_results(node, args):
    print(f"Checked for {args.duration:.1f}s")
    if not node.candidates:
        print("[WARN] No likely encoder/wheel/motor topics were discovered.")
        print("Hint: retry with --all-topics or adjust --include tokens.")
        return

    for candidate in node.candidates:
        sample = node.samples[(candidate.topic, candidate.ros_type)]
        status = "OK" if candidate.supported and sample["count"] > 0 else "OBS"
        if not candidate.supported:
            status = "UNSUPPORTED"
        print(
            f"[{status}] {candidate.topic} type={candidate.ros_type} "
            f"count={sample['count']} rate={format_rate(sample)} "
            f"{sample['summary']}"
        )

    wheel_odom = [
        candidate
        for candidate in node.candidates
        if candidate.topic == args.expected_wheel_odom
        and candidate.ros_type == "nav_msgs/msg/Odometry"
    ]
    joint_states = [
        candidate
        for candidate in node.candidates
        if candidate.ros_type == "sensor_msgs/msg/JointState"
    ]
    raw_encoder = [
        candidate
        for candidate in node.candidates
        if "encoder" in candidate.topic.lower()
        or "tick" in candidate.topic.lower()
        or "count" in candidate.topic.lower()
    ]

    print("Interpretation:")
    if wheel_odom:
        print(
            f"- {args.expected_wheel_odom} already exists as nav_msgs/Odometry; "
            "this can become the local EKF wheel input."
        )
    elif joint_states:
        print(
            "- JointState data exists; if wheel joint positions/velocities change, "
            "an adapter can convert it to /wheel/odometry."
        )
    elif raw_encoder:
        print(
            "- Raw encoder-like topics exist; next step is converting ticks/counts "
            "to distance with ticks_per_rev, effective_radius, and track_width."
        )
    else:
        print(
            "- No direct wheel odometry or encoder topic was found yet. Check the "
            "motor driver node and topic names first."
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Discover likely Mari wheel encoder or wheel odometry topics."
    )
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--discovery-timeout", type=float, default=1.0)
    parser.add_argument(
        "--include",
        default="encoder,wheel,motor,joint,odom,tick,count,rpm",
        help="Comma-separated candidate name/type tokens.",
    )
    parser.add_argument(
        "--exclude",
        default="camera,imu,gps,rtabmap,tf,clock,cmd_vel,rosout,parameter_events",
        help="Comma-separated topic-name tokens to ignore.",
    )
    parser.add_argument("--all-topics", action="store_true")
    parser.add_argument("--expected-wheel-odom", default="/wheel/odometry")
    return parser.parse_args()


def main():
    args = parse_args()

    rclpy.init()
    node = EncoderTopicProbe(args)
    try:
        discovery_deadline = time.monotonic() + args.discovery_timeout
        while rclpy.ok() and time.monotonic() < discovery_deadline:
            rclpy.spin_once(node, timeout_sec=0.1)

        node.discover()
        deadline = time.monotonic() + args.duration
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)

        print_results(node, args)
        return 0
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
