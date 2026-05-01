#!/usr/bin/env python3
"""Republish Gazebo odom as a mock wheel odometry input."""

import sys

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy


class GazeboOdomToWheelOdom(Node):
    def __init__(self):
        super().__init__("gazebo_odom_to_wheel_odom")
        self.input_topic = self.declare_parameter(
            "input_odom_topic", "/odom"
        ).value
        self.output_topic = self.declare_parameter(
            "output_wheel_odom_topic", "/wheel/odometry"
        ).value
        self.override_child_frame_id = self.declare_parameter(
            "override_child_frame_id", ""
        ).value

        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT

        self.publisher = self.create_publisher(Odometry, self.output_topic, qos)
        self.subscription = self.create_subscription(
            Odometry,
            self.input_topic,
            self.odom_callback,
            qos,
        )
        self.count = 0
        self.get_logger().info(
            f"Republishing {self.input_topic} to {self.output_topic} as mock wheel odom"
        )

    def odom_callback(self, msg):
        out = Odometry()
        out.header = msg.header
        out.child_frame_id = self.override_child_frame_id or msg.child_frame_id
        out.pose = msg.pose
        out.twist = msg.twist
        self.publisher.publish(out)

        self.count += 1
        if self.count == 1:
            self.get_logger().info(
                "First mock wheel odom published: "
                f"frame={out.header.frame_id or '-'} child={out.child_frame_id or '-'}"
            )


def main():
    rclpy.init()
    node = GazeboOdomToWheelOdom()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
