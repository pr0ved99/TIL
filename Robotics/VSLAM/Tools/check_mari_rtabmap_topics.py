#!/usr/bin/env python3
"""Check Mari Gazebo input topics and RTAB-Map mapping output topics."""

import argparse
import sys
import time
from dataclasses import dataclass

import rclpy
from nav_msgs.msg import OccupancyGrid, Odometry, Path
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rtabmap_msgs.msg import Info, MapData, MapGraph
from sensor_msgs.msg import CameraInfo, Image, PointCloud2
from tf2_msgs.msg import TFMessage


@dataclass(frozen=True)
class TopicSpec:
    label: str
    topic: str
    msg_type: type
    ros_type: str
    required: bool = True


class TopicProbe(Node):
    def __init__(self, specs):
        super().__init__("mari_rtabmap_topic_probe")
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

    if isinstance(msg, Odometry):
        return (
            f"frame={frame_id or '-'} child={msg.child_frame_id or '-'} "
            f"x={msg.pose.pose.position.x:.3f} y={msg.pose.pose.position.y:.3f}"
        )

    if isinstance(msg, PointCloud2):
        return (
            f"frame={frame_id or '-'} size={msg.width}x{msg.height} "
            f"points={msg.width * msg.height}"
        )

    if isinstance(msg, Info):
        return (
            f"frame={frame_id or '-'} ref_id={msg.ref_id} "
            f"loop={msg.loop_closure_id} wm={len(msg.wm_state)} "
            f"stats={len(msg.stats_keys)}"
        )

    if isinstance(msg, MapData):
        return (
            f"frame={frame_id or '-'} nodes={len(msg.nodes)} "
            f"poses={len(msg.graph.poses_id)} links={len(msg.graph.links)}"
        )

    if isinstance(msg, MapGraph):
        return (
            f"frame={frame_id or '-'} poses={len(msg.poses_id)} "
            f"links={len(msg.links)}"
        )

    if isinstance(msg, Path):
        return f"frame={frame_id or '-'} poses={len(msg.poses)}"

    if isinstance(msg, OccupancyGrid):
        info = msg.info
        return (
            f"frame={frame_id or '-'} size={info.width}x{info.height} "
            f"resolution={info.resolution:.3f}"
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


def format_rate(sample):
    count = sample["count"]
    first_time = sample["first_time"]
    last_time = sample["last_time"]
    if count < 2 or first_time is None or last_time is None or last_time <= first_time:
        return "n/a"
    return f"{(count - 1) / (last_time - first_time):.1f} Hz"


def namespace_topic(namespace, name):
    clean_namespace = namespace.strip("/")
    clean_name = name.strip("/")
    if not clean_namespace:
        return f"/{clean_name}"
    return f"/{clean_namespace}/{clean_name}"


def expected_specs(args):
    ns = args.rtabmap_namespace
    return [
        TopicSpec("odom input", args.odom_topic, Odometry, "nav_msgs/msg/Odometry"),
        TopicSpec("rgb image input", args.rgb_topic, Image, "sensor_msgs/msg/Image"),
        TopicSpec("depth image input", args.depth_topic, Image, "sensor_msgs/msg/Image"),
        TopicSpec(
            "rgb camera info input",
            args.rgb_info_topic,
            CameraInfo,
            "sensor_msgs/msg/CameraInfo",
        ),
        TopicSpec(
            "rtabmap info output",
            namespace_topic(ns, "info"),
            Info,
            "rtabmap_msgs/msg/Info",
        ),
        TopicSpec(
            "rtabmap map data output",
            namespace_topic(ns, "mapData"),
            MapData,
            "rtabmap_msgs/msg/MapData",
        ),
        TopicSpec(
            "rtabmap cloud map output",
            namespace_topic(ns, "cloud_map"),
            PointCloud2,
            "sensor_msgs/msg/PointCloud2",
        ),
        TopicSpec(
            "rtabmap map graph output",
            namespace_topic(ns, "mapGraph"),
            MapGraph,
            "rtabmap_msgs/msg/MapGraph",
            required=False,
        ),
        TopicSpec(
            "rtabmap path output",
            namespace_topic(ns, "mapPath"),
            Path,
            "nav_msgs/msg/Path",
            required=False,
        ),
        TopicSpec(
            "rtabmap occupancy map output",
            namespace_topic(ns, "map"),
            OccupancyGrid,
            "nav_msgs/msg/OccupancyGrid",
            required=False,
        ),
        TopicSpec("tf", "/tf", TFMessage, "tf2_msgs/msg/TFMessage", required=False),
    ]


def publisher_topic_types(node, specs):
    topic_types = {}
    for spec in specs:
        infos = node.get_publishers_info_by_topic(spec.topic)
        topic_types[spec.topic] = sorted({info.topic_type for info in infos})
    return topic_types


def print_result(spec, sample, publisher_types, min_count):
    count = sample["count"]
    rate = format_rate(sample)
    publisher_type_text = ",".join(publisher_types.get(spec.topic, [])) or "not published"
    type_ok = spec.ros_type in publisher_types.get(spec.topic, [])
    count_ok = count >= min_count

    if spec.required:
        ok = count_ok and type_ok
        status = "OK" if ok else "FAIL"
    else:
        ok = True
        status = "OBS" if count_ok and type_ok else "MISS"

    print(
        f"[{status}] {spec.label}: {spec.topic} "
        f"type={publisher_type_text} count={count} rate={rate} {sample['summary']}"
    )
    return ok


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Check Mari Gazebo RGB-D/odom inputs and RTAB-Map mapping outputs."
        )
    )
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--min-count", type=int, default=1)
    parser.add_argument("--rtabmap-namespace", default="/rtabmap")
    parser.add_argument("--odom-topic", default="/odom")
    parser.add_argument("--rgb-topic", default="/camera/camera/color/image_raw")
    parser.add_argument(
        "--depth-topic",
        default="/camera/camera/aligned_depth_to_color/image_raw",
    )
    parser.add_argument("--rgb-info-topic", default="/camera/camera/color/camera_info")
    return parser.parse_args()


def main():
    args = parse_args()

    rclpy.init()
    node = TopicProbe(expected_specs(args))
    deadline = time.monotonic() + args.duration

    try:
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)

        publisher_types = publisher_topic_types(node, node.specs)
        print(f"Checked for {args.duration:.1f}s")
        results = [
            print_result(spec, node.samples[spec.topic], publisher_types, args.min_count)
            for spec in node.specs
        ]

        print("Graph helpers:")
        for helper in ("/tf_static", "/clock", "/cmd_vel", "/imu/data"):
            infos = node.get_publishers_info_by_topic(helper)
            types = ",".join(sorted({info.topic_type for info in infos})) or "not published"
            print(f"- {helper}: {types}")

        return 0 if all(results) else 1
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
