#!/usr/bin/env python3
"""Check Mari Gazebo input topics and RTAB-Map mapping output topics."""

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path as FilesystemPath

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
        self.last_odom = None
        self.last_info = None
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
            if isinstance(msg, Odometry):
                self.last_odom = msg
            elif isinstance(msg, Info):
                self.last_info = msg

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
    rate = sample_rate_hz(sample)
    if rate is None:
        return "n/a"
    return f"{rate:.1f} Hz"


def sample_rate_hz(sample):
    count = sample["count"]
    first_time = sample["first_time"]
    last_time = sample["last_time"]
    if count < 2 or first_time is None or last_time is None or last_time <= first_time:
        return None
    return (count - 1) / (last_time - first_time)


def covariance_summary(covariance):
    labels = ("x", "y", "z", "roll", "pitch", "yaw")
    values = (
        covariance[0],
        covariance[7],
        covariance[14],
        covariance[21],
        covariance[28],
        covariance[35],
    )
    text = " ".join(f"{label}={value:.4g}" for label, value in zip(labels, values))
    all_zero = all(abs(value) < 1e-12 for value in covariance)
    return f"{text} all_zero={str(all_zero).lower()}"


def covariance_dict(covariance):
    return {
        "x": covariance[0],
        "y": covariance[7],
        "z": covariance[14],
        "roll": covariance[21],
        "pitch": covariance[28],
        "yaw": covariance[35],
        "all_zero": all(abs(value) < 1e-12 for value in covariance),
    }


def selected_stats(info, args):
    pairs = list(zip(info.stats_keys, info.stats_values))
    if args.all_stats:
        return pairs[: args.max_stats]

    filters = [
        token.strip()
        for token in args.stats_filter.split(",")
        if token.strip()
    ]
    selected = [
        (key, value)
        for key, value in pairs
        if any(token in key for token in filters)
    ]
    return selected[: args.max_stats]


def make_report(node, args, publisher_types, result_rows, helper_types):
    odom = node.last_odom
    info = node.last_info

    report = {
        "label": args.label,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "duration_sec": args.duration,
        "odom_topic": args.odom_topic,
        "rtabmap_namespace": args.rtabmap_namespace,
        "topics": result_rows,
        "helpers": helper_types,
        "diagnostics": {},
    }

    if odom is not None:
        report["diagnostics"]["odom"] = {
            "frame_id": odom.header.frame_id,
            "child_frame_id": odom.child_frame_id,
            "pose_covariance": covariance_dict(odom.pose.covariance),
            "twist_covariance": covariance_dict(odom.twist.covariance),
            "position": {
                "x": odom.pose.pose.position.x,
                "y": odom.pose.pose.position.y,
                "z": odom.pose.pose.position.z,
            },
            "twist": {
                "linear_x": odom.twist.twist.linear.x,
                "linear_y": odom.twist.twist.linear.y,
                "angular_z": odom.twist.twist.angular.z,
            },
        }

    if info is not None:
        report["diagnostics"]["rtabmap_info"] = {
            "frame_id": info.header.frame_id,
            "ref_id": info.ref_id,
            "loop_closure_id": info.loop_closure_id,
            "proximity_detection_id": info.proximity_detection_id,
            "working_memory_size": len(info.wm_state),
            "local_path_size": len(info.local_path),
            "odom_cache_poses": len(info.odom_cache.poses_id),
            "stats_count": len(info.stats_keys),
            "selected_stats": [
                {"key": key, "value": value}
                for key, value in selected_stats(info, args)
            ],
        }

    return report


def write_json_report(path, report):
    output_path = FilesystemPath(path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Saved JSON report: {output_path}")


def write_markdown_report(path, report):
    output_path = FilesystemPath(path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Mari RTAB-Map Check - {report['label']}",
        "",
        "## Summary",
        "",
        f"- checked_at: `{report['checked_at']}`",
        f"- duration_sec: `{report['duration_sec']}`",
        f"- odom_topic: `{report['odom_topic']}`",
        f"- rtabmap_namespace: `{report['rtabmap_namespace']}`",
        "",
        "## Topics",
        "",
        "| status | label | topic | count | rate_hz | summary |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]

    for row in report["topics"]:
        rate = row["rate_hz"]
        rate_text = "n/a" if rate is None else f"{rate:.2f}"
        lines.append(
            f"| {row['status']} | {row['label']} | `{row['topic']}` | "
            f"{row['count']} | {rate_text} | {row['summary']} |"
        )

    diagnostics = report.get("diagnostics", {})
    rtabmap_info = diagnostics.get("rtabmap_info")
    if rtabmap_info:
        lines.extend(
            [
                "",
                "## RTAB-Map Info",
                "",
                f"- ref_id: `{rtabmap_info['ref_id']}`",
                f"- loop_closure_id: `{rtabmap_info['loop_closure_id']}`",
                f"- proximity_detection_id: `{rtabmap_info['proximity_detection_id']}`",
                f"- working_memory_size: `{rtabmap_info['working_memory_size']}`",
                f"- local_path_size: `{rtabmap_info['local_path_size']}`",
                f"- odom_cache_poses: `{rtabmap_info['odom_cache_poses']}`",
                f"- stats_count: `{rtabmap_info['stats_count']}`",
            ]
        )

        if rtabmap_info["selected_stats"]:
            lines.extend(["", "## Selected Stats", "", "| key | value |", "| --- | ---: |"])
            for stat in rtabmap_info["selected_stats"]:
                lines.append(f"| `{stat['key']}` | {stat['value']:.6g} |")

    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved Markdown report: {output_path}")


def print_diagnostics(node, args):
    print("Diagnostics:")

    odom = node.last_odom
    if odom is None:
        print("- odom covariance: no odom sample")
    else:
        print(f"- odom pose covariance: {covariance_summary(odom.pose.covariance)}")
        print(f"- odom twist covariance: {covariance_summary(odom.twist.covariance)}")

    info = node.last_info
    if info is None:
        print("- rtabmap info: no info sample")
        return

    print(
        "- rtabmap info: "
        f"ref_id={info.ref_id} loop={info.loop_closure_id} "
        f"proximity={info.proximity_detection_id} wm={len(info.wm_state)} "
        f"local_path={len(info.local_path)} odom_cache={len(info.odom_cache.poses_id)} "
        f"stats={len(info.stats_keys)}"
    )

    stats = selected_stats(info, args)
    if not stats:
        print("- rtabmap stats: no matching stats; use --all-stats to print raw keys")
        return

    print("- rtabmap stats:")
    for key, value in stats:
        print(f"  {key}={value:.4g}")


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
    rate_value = sample_rate_hz(sample)
    rate = "n/a" if rate_value is None else f"{rate_value:.1f} Hz"
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
    row = {
        "label": spec.label,
        "topic": spec.topic,
        "required": spec.required,
        "expected_type": spec.ros_type,
        "publisher_types": publisher_types.get(spec.topic, []),
        "type_ok": type_ok,
        "count_ok": count_ok,
        "count": count,
        "rate_hz": rate_value,
        "status": status,
        "ok": ok,
        "summary": sample["summary"],
    }
    return ok, row


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Check Mari Gazebo RGB-D/odom inputs and RTAB-Map mapping outputs."
        )
    )
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--min-count", type=int, default=1)
    parser.add_argument(
        "--label",
        default="mari_rtabmap_check",
        help="Label stored in JSON/Markdown reports.",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional path to save a machine-readable JSON report.",
    )
    parser.add_argument(
        "--output-md",
        default="",
        help="Optional path to save a Markdown report.",
    )
    parser.add_argument("--rtabmap-namespace", default="/rtabmap")
    parser.add_argument("--odom-topic", default="/odom")
    parser.add_argument("--rgb-topic", default="/camera/camera/color/image_raw")
    parser.add_argument(
        "--depth-topic",
        default="/camera/camera/aligned_depth_to_color/image_raw",
    )
    parser.add_argument("--rgb-info-topic", default="/camera/camera/color/camera_info")
    parser.add_argument(
        "--stats-filter",
        default=(
            "Loop,loop,Optimize,optimize,Memory,memory,Timing,timing,"
            "RTAB,rtab,Registration,registration,Inliers,inliers,Update,update"
        ),
        help="Comma-separated substrings used to print selected /rtabmap/info stats.",
    )
    parser.add_argument("--max-stats", type=int, default=20)
    parser.add_argument(
        "--all-stats",
        action="store_true",
        help="Print raw /rtabmap/info stats instead of filtered diagnostic stats.",
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

        publisher_types = publisher_topic_types(node, node.specs)
        print(f"Checked for {args.duration:.1f}s")
        result_rows = []
        results = []
        for spec in node.specs:
            ok, row = print_result(
                spec,
                node.samples[spec.topic],
                publisher_types,
                args.min_count,
            )
            results.append(ok)
            result_rows.append(row)

        print("Graph helpers:")
        helper_types = {}
        for helper in ("/tf_static", "/clock", "/cmd_vel", "/imu/data"):
            infos = node.get_publishers_info_by_topic(helper)
            type_list = sorted({info.topic_type for info in infos})
            helper_types[helper] = type_list
            type_text = ",".join(type_list) or "not published"
            print(f"- {helper}: {type_text}")

        print_diagnostics(node, args)

        if args.output_json or args.output_md:
            report = make_report(node, args, publisher_types, result_rows, helper_types)
            if args.output_json:
                write_json_report(args.output_json, report)
            if args.output_md:
                write_markdown_report(args.output_md, report)

        return 0 if all(results) else 1
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
