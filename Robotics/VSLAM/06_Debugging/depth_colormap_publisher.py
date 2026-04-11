#!/usr/bin/env python3

import math

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


COLORMAP_LOOKUP = {
    "autumn": cv2.COLORMAP_AUTUMN,
    "bone": cv2.COLORMAP_BONE,
    "jet": cv2.COLORMAP_JET,
    "winter": cv2.COLORMAP_WINTER,
    "rainbow": cv2.COLORMAP_RAINBOW,
    "ocean": cv2.COLORMAP_OCEAN,
    "summer": cv2.COLORMAP_SUMMER,
    "spring": cv2.COLORMAP_SPRING,
    "cool": cv2.COLORMAP_COOL,
    "hsv": cv2.COLORMAP_HSV,
    "pink": cv2.COLORMAP_PINK,
    "hot": cv2.COLORMAP_HOT,
    "parula": cv2.COLORMAP_PARULA,
    "magma": cv2.COLORMAP_MAGMA,
    "inferno": cv2.COLORMAP_INFERNO,
    "plasma": cv2.COLORMAP_PLASMA,
    "viridis": cv2.COLORMAP_VIRIDIS,
    "cividis": cv2.COLORMAP_CIVIDIS,
    "turbo": cv2.COLORMAP_TURBO,
}


class DepthColormapPublisher(Node):
    def __init__(self) -> None:
        super().__init__("depth_colormap_publisher")

        self.declare_parameter(
            "input_topic", "/camera/camera/depth/image_rect_raw"
        )
        self.declare_parameter(
            "output_topic", "/camera/camera/depth/image_colormap"
        )
        self.declare_parameter("min_depth_m", 0.3)
        self.declare_parameter("max_depth_m", 5.0)
        self.declare_parameter("colormap", "turbo")
        self.declare_parameter("invert", True)
        self.declare_parameter("show_window", False)

        self.input_topic = (
            self.get_parameter("input_topic").get_parameter_value().string_value
        )
        self.output_topic = (
            self.get_parameter("output_topic").get_parameter_value().string_value
        )
        self.min_depth_m = (
            self.get_parameter("min_depth_m").get_parameter_value().double_value
        )
        self.max_depth_m = (
            self.get_parameter("max_depth_m").get_parameter_value().double_value
        )
        self.colormap_name = (
            self.get_parameter("colormap").get_parameter_value().string_value.lower()
        )
        self.invert = (
            self.get_parameter("invert").get_parameter_value().bool_value
        )
        self.show_window = (
            self.get_parameter("show_window").get_parameter_value().bool_value
        )

        self.colormap = COLORMAP_LOOKUP.get(
            self.colormap_name, cv2.COLORMAP_TURBO
        )
        self.bridge = CvBridge()
        self.publisher = self.create_publisher(
            Image, self.output_topic, qos_profile_sensor_data
        )
        self.subscription = self.create_subscription(
            Image,
            self.input_topic,
            self.depth_callback,
            qos_profile_sensor_data,
        )

        self.get_logger().info(
            "Depth colormap publisher started: "
            f"{self.input_topic} -> {self.output_topic}, "
            f"range={self.min_depth_m:.2f}m~{self.max_depth_m:.2f}m, "
            f"colormap={self.colormap_name}, invert={self.invert}"
        )

    def _depth_to_meters(self, msg: Image) -> np.ndarray:
        if msg.encoding == "16UC1":
            depth_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            return depth_raw.astype(np.float32) / 1000.0
        if msg.encoding == "32FC1":
            depth_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            return depth_raw.astype(np.float32)
        raise ValueError(f"Unsupported depth encoding: {msg.encoding}")

    def depth_callback(self, msg: Image) -> None:
        try:
            depth_m = self._depth_to_meters(msg)
        except Exception as exc:
            self.get_logger().error(str(exc))
            return

        valid_mask = np.isfinite(depth_m) & (depth_m > 0.0)
        range_mask = valid_mask & (depth_m >= self.min_depth_m) & (
            depth_m <= self.max_depth_m
        )

        normalized = np.zeros(depth_m.shape, dtype=np.float32)
        if np.any(range_mask):
            clipped = np.clip(depth_m[range_mask], self.min_depth_m, self.max_depth_m)
            normalized_values = (
                clipped - self.min_depth_m
            ) / max(self.max_depth_m - self.min_depth_m, 1e-6)
            if self.invert:
                normalized_values = 1.0 - normalized_values
            normalized[range_mask] = normalized_values

        image_8u = (normalized * 255.0).astype(np.uint8)
        colorized = cv2.applyColorMap(image_8u, self.colormap)
        colorized[~range_mask] = (0, 0, 0)

        output_msg = self.bridge.cv2_to_imgmsg(colorized, encoding="bgr8")
        output_msg.header = msg.header
        self.publisher.publish(output_msg)

        if self.show_window:
            cv2.imshow("depth_colormap", colorized)
            cv2.waitKey(1)


def main() -> None:
    rclpy.init()
    node = DepthColormapPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.show_window:
            cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
