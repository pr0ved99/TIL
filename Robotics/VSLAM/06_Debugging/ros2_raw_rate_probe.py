#!/usr/bin/env python3

import math
import sys
from typing import List

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image


class RawRateProbe(Node):
    def __init__(self) -> None:
        super().__init__("raw_rate_probe")

        self.declare_parameter("topic", "")
        self.declare_parameter("duration_sec", 5.0)
        self.declare_parameter("msg_kind", "image")

        topic = str(self.get_parameter("topic").value).strip()
        self.duration_sec = float(self.get_parameter("duration_sec").value)
        msg_kind = str(self.get_parameter("msg_kind").value).strip().lower()

        if not topic:
            raise ValueError("topic parameter is required")
        if msg_kind not in {"image", "camera_info"}:
            raise ValueError("msg_kind must be one of: image, camera_info")

        self.topic = topic
        self.msg_kind = msg_kind
        self.arrival_times: List[float] = []
        self.start_time = self.get_clock().now().nanoseconds / 1e9

        msg_type = Image if self.msg_kind == "image" else CameraInfo

        # raw=True avoids Python deserialization cost and measures arrival cadence.
        self.subscription = self.create_subscription(
            msg_type,
            self.topic,
            self._callback,
            qos_profile_sensor_data,
            raw=True,
        )
        self.timer = self.create_timer(0.1, self._maybe_finish)

        self.get_logger().info(
            f"Probing topic={self.topic} msg_kind={self.msg_kind} "
            f"for {self.duration_sec:.1f}s with raw subscription"
        )

    def _callback(self, _raw_msg: bytes) -> None:
        now_sec = self.get_clock().now().nanoseconds / 1e9
        self.arrival_times.append(now_sec)

    def _maybe_finish(self) -> None:
        now_sec = self.get_clock().now().nanoseconds / 1e9
        if now_sec - self.start_time < self.duration_sec:
            return

        count = len(self.arrival_times)
        if count < 2:
            self.get_logger().error(
                f"Not enough messages received on {self.topic}: count={count}"
            )
            rclpy.shutdown()
            return

        deltas = [
            self.arrival_times[i] - self.arrival_times[i - 1]
            for i in range(1, count)
        ]
        avg_delta = sum(deltas) / len(deltas)
        avg_rate = 1.0 / avg_delta if avg_delta > 0.0 else math.inf
        min_delta = min(deltas)
        max_delta = max(deltas)

        self.get_logger().info(
            f"topic={self.topic} count={count} avg_rate={avg_rate:.3f}Hz "
            f"min_dt={min_delta:.6f}s max_dt={max_delta:.6f}s"
        )
        rclpy.shutdown()


def main(argv: List[str] | None = None) -> int:
    rclpy.init(args=argv)
    try:
        node = RawRateProbe()
    except Exception as exc:  # pragma: no cover - startup validation
        print(f"[raw_rate_probe] startup failed: {exc}", file=sys.stderr)
        rclpy.shutdown()
        return 1

    rclpy.spin(node)
    node.destroy_node()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
