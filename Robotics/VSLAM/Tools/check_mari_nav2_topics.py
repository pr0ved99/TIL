#!/usr/bin/env python3
"""Check Mari Nav2 smoke-test topics."""

import argparse
import math
import time
from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import OccupancyGrid, Path
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from tf2_msgs.msg import TFMessage


@dataclass(frozen=True)
class TopicSpec:
    label: str
    topic: str
    msg_type: type
    ros_type: str
    required: bool = True


class Nav2TopicProbe(Node):
    def __init__(self, specs):
        super().__init__("mari_nav2_topic_probe")
        self.samples = {
            spec.topic: {
                "count": 0,
                "first_time": None,
                "last_time": None,
                "summary": "no messages",
            }
            for spec in specs
        }
        self.subscriptions_ = []
        for spec in specs:
            self.subscriptions_.append(
                self.create_subscription(
                    spec.msg_type,
                    spec.topic,
                    self._make_callback(spec),
                    qos_for(spec),
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


def qos_for(spec):
    qos = QoSProfile(depth=10)
    qos.reliability = ReliabilityPolicy.BEST_EFFORT
    if spec.msg_type is OccupancyGrid:
        qos.durability = DurabilityPolicy.VOLATILE
    return qos


def summarize_message(msg):
    header = getattr(msg, "header", None)
    frame_id = getattr(header, "frame_id", "") if header is not None else ""

    if isinstance(msg, LaserScan):
        finite_values = [value for value in msg.ranges if math.isfinite(value)]
        finite_ranges = len(finite_values)
        min_finite = min(finite_values) if finite_values else float("nan")
        close_030 = sum(1 for value in finite_values if value < 0.30)
        close_045 = sum(1 for value in finite_values if value < 0.45)
        return (
            f"frame={frame_id or '-'} ranges={len(msg.ranges)} "
            f"finite={finite_ranges} min_range={msg.range_min:.2f} "
            f"max_range={msg.range_max:.2f} min_finite={min_finite:.2f} "
            f"lt0.30={close_030} lt0.45={close_045}"
        )

    if isinstance(msg, OccupancyGrid):
        info = msg.info
        return (
            f"frame={frame_id or '-'} size={info.width}x{info.height} "
            f"resolution={info.resolution:.3f}"
        )

    if isinstance(msg, Path):
        return f"frame={frame_id or '-'} poses={len(msg.poses)}"

    if isinstance(msg, Twist):
        return (
            f"linear_x={msg.linear.x:.3f} linear_y={msg.linear.y:.3f} "
            f"angular_z={msg.angular.z:.3f}"
        )

    if isinstance(msg, TFMessage):
        if not msg.transforms:
            return "transforms=0"
        first = msg.transforms[0]
        return (
            f"transforms={len(msg.transforms)} "
            f"first={first.header.frame_id}->{first.child_frame_id}"
        )

    return f"frame={frame_id or '-'}"


def sample_rate_hz(sample):
    count = sample["count"]
    first_time = sample["first_time"]
    last_time = sample["last_time"]
    if count < 2 or first_time is None or last_time is None or last_time <= first_time:
        return None
    return (count - 1) / (last_time - first_time)


def format_rate(sample):
    rate = sample_rate_hz(sample)
    if rate is None:
        return "n/a"
    return f"{rate:.1f} Hz"


def topic_type_map(node):
    return {
        topic: [name for name in type_names]
        for topic, type_names in node.get_topic_names_and_types()
    }


def make_specs(args):
    specs = [
        TopicSpec("depth scan", args.scan_topic, LaserScan, "sensor_msgs/msg/LaserScan"),
        TopicSpec(
            "rtabmap occupancy map",
            args.map_topic,
            OccupancyGrid,
            "nav_msgs/msg/OccupancyGrid",
            required=args.require_rtabmap_map,
        ),
        TopicSpec(
            "global costmap",
            args.global_costmap_topic,
            OccupancyGrid,
            "nav_msgs/msg/OccupancyGrid",
        ),
        TopicSpec(
            "local costmap",
            args.local_costmap_topic,
            OccupancyGrid,
            "nav_msgs/msg/OccupancyGrid",
        ),
        TopicSpec("tf", "/tf", TFMessage, "tf2_msgs/msg/TFMessage"),
        TopicSpec("nav plan", args.plan_topic, Path, "nav_msgs/msg/Path", required=False),
        TopicSpec("cmd vel", args.cmd_vel_topic, Twist, "geometry_msgs/msg/Twist", required=args.expect_cmd_vel),
    ]
    return specs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", type=float, default=8.0, help="Seconds to observe topics.")
    parser.add_argument("--scan-topic", default="/scan")
    parser.add_argument("--map-topic", default="/rtabmap/map")
    parser.add_argument("--global-costmap-topic", default="/global_costmap/costmap")
    parser.add_argument("--local-costmap-topic", default="/local_costmap/costmap")
    parser.add_argument("--plan-topic", default="/plan")
    parser.add_argument("--cmd-vel-topic", default="/cmd_vel")
    parser.add_argument(
        "--require-rtabmap-map",
        action="store_true",
        help=(
            "Require /rtabmap/map. The default Nav2 training profile uses scan-only "
            "rolling costmaps, so RTAB-Map occupancy is observed but not required."
        ),
    )
    parser.add_argument(
        "--expect-cmd-vel",
        action="store_true",
        help="Require /cmd_vel. Use after sending a Nav2 goal.",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Exit successfully even if required topics are missing. Useful for dry runs.",
    )
    args = parser.parse_args()

    rclpy.init()
    specs = make_specs(args)
    node = Nav2TopicProbe(specs)

    deadline = time.monotonic() + args.duration
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)

    publisher_types = topic_type_map(node)
    print(f"Checked for {args.duration:.1f}s")
    missing_required = []
    warnings = []

    for spec in specs:
        sample = node.samples[spec.topic]
        count = sample["count"]
        observed_types = publisher_types.get(spec.topic, [])
        has_type = spec.ros_type in observed_types
        ok = count > 0 and has_type
        status = "OK" if ok else "MISS" if spec.required else "OBS"
        if spec.required and not ok:
            missing_required.append(spec.topic)
        type_text = ",".join(observed_types) if observed_types else "unknown"
        print(
            f"[{status}] {spec.label}: {spec.topic} type={type_text} "
            f"count={count} rate={format_rate(sample)} {sample['summary']}"
        )
        if spec.msg_type is LaserScan and "optical_frame" in sample["summary"]:
            warnings.append(
                f"{spec.topic} is published in an optical frame. Restart Nav2 with "
                "scan_frame:=camera_link so LaserScan obstacles are projected in "
                "the x-forward/y-left plane."
            )

    if missing_required and not args.allow_missing:
        print("Missing required topics:")
        for topic in missing_required:
            print(f"- {topic}")
        raise SystemExit(1)

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    print("Interpretation:")
    if missing_required:
        print("- Required topics are missing, but --allow-missing was set.")
    else:
        print("- Nav2 smoke-test topics are present.")
        if not args.expect_cmd_vel:
            print("- Run again with --expect-cmd-vel after sending an RViz 2D Goal Pose.")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
