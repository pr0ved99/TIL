#!/usr/bin/env python3
"""Republish IMU messages with conservative covariance values."""

import sys

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


def diagonal_covariance(value):
    return [
        value,
        0.0,
        0.0,
        0.0,
        value,
        0.0,
        0.0,
        0.0,
        value,
    ]


class ImuCovarianceRepublisher(Node):
    def __init__(self):
        super().__init__("imu_covariance_republisher")

        self.input_topic = self.declare_parameter("input_imu_topic", "/imu/data").value
        self.output_topic = self.declare_parameter(
            "output_imu_topic", "/imu/data_bno08x_like"
        ).value
        self.frame_id = self.declare_parameter("frame_id", "").value
        self.orientation_covariance = float(
            self.declare_parameter("orientation_covariance", 0.01).value
        )
        self.angular_velocity_covariance = float(
            self.declare_parameter("angular_velocity_covariance", 0.001).value
        )
        self.linear_acceleration_covariance = float(
            self.declare_parameter("linear_acceleration_covariance", 0.01).value
        )

        if self.orientation_covariance < 0:
            raise ValueError("orientation_covariance must be >= 0")
        if self.angular_velocity_covariance < 0:
            raise ValueError("angular_velocity_covariance must be >= 0")
        if self.linear_acceleration_covariance < 0:
            raise ValueError("linear_acceleration_covariance must be >= 0")

        self.publisher = self.create_publisher(Imu, self.output_topic, 10)
        self.subscription = self.create_subscription(
            Imu,
            self.input_topic,
            self.imu_callback,
            10,
        )

        self.get_logger().info(
            f"Republishing IMU {self.input_topic} -> {self.output_topic} "
            f"(orientation_cov={self.orientation_covariance:g}, "
            f"angular_velocity_cov={self.angular_velocity_covariance:g}, "
            f"linear_acceleration_cov={self.linear_acceleration_covariance:g})"
        )

    def imu_callback(self, msg):
        out = Imu()
        out.header = msg.header
        if self.frame_id:
            out.header.frame_id = self.frame_id
        out.orientation = msg.orientation
        out.angular_velocity = msg.angular_velocity
        out.linear_acceleration = msg.linear_acceleration
        out.orientation_covariance = diagonal_covariance(self.orientation_covariance)
        out.angular_velocity_covariance = diagonal_covariance(
            self.angular_velocity_covariance
        )
        out.linear_acceleration_covariance = diagonal_covariance(
            self.linear_acceleration_covariance
        )
        self.publisher.publish(out)


def main():
    rclpy.init()
    node = ImuCovarianceRepublisher()
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
