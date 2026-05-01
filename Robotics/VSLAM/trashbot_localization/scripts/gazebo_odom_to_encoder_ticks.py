#!/usr/bin/env python3
"""Convert Gazebo odometry twist into mock cumulative motor encoder ticks."""

import math
import sys

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import Int64MultiArray


def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def quaternion_to_yaw(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class GazeboOdomToEncoderTicks(Node):
    def __init__(self):
        super().__init__("gazebo_odom_to_encoder_ticks")

        self.input_odom_topic = self.declare_parameter(
            "input_odom_topic", "/odom"
        ).value
        self.output_encoder_topic = self.declare_parameter(
            "output_encoder_topic", "/motor/encoder_ticks"
        ).value
        self.ticks_per_revolution = float(
            self.declare_parameter("ticks_per_revolution", 1560.0).value
        )
        self.effective_wheel_radius_m = float(
            self.declare_parameter("effective_wheel_radius_m", 0.021).value
        )
        self.track_width_m = float(
            self.declare_parameter("track_width_m", 0.137553).value
        )
        self.left_ticks_sign = float(
            self.declare_parameter("left_ticks_sign", 1.0).value
        )
        self.right_ticks_sign = float(
            self.declare_parameter("right_ticks_sign", 1.0).value
        )
        self.integration_source = self.declare_parameter(
            "integration_source", "pose"
        ).value

        if self.ticks_per_revolution <= 0:
            raise ValueError("ticks_per_revolution must be positive")
        if self.effective_wheel_radius_m <= 0:
            raise ValueError("effective_wheel_radius_m must be positive")
        if self.track_width_m <= 0:
            raise ValueError("track_width_m must be positive")
        if self.integration_source not in ("pose", "twist"):
            raise ValueError("integration_source must be 'pose' or 'twist'")

        self.meters_per_tick = (
            2.0 * math.pi * self.effective_wheel_radius_m
        ) / self.ticks_per_revolution
        self.left_ticks_float = 0.0
        self.right_ticks_float = 0.0
        self.prev_stamp_sec = None
        self.prev_x = None
        self.prev_y = None
        self.prev_yaw = None
        self.publish_count = 0

        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT

        self.publisher = self.create_publisher(
            Int64MultiArray, self.output_encoder_topic, 10
        )
        self.subscription = self.create_subscription(
            Odometry,
            self.input_odom_topic,
            self.odom_callback,
            qos,
        )

        self.get_logger().info(
            "Converting Gazebo odom twist to mock encoder ticks "
            f"{self.input_odom_topic} -> {self.output_encoder_topic} "
            f"(ticks_per_rev={self.ticks_per_revolution:.1f}, "
            f"radius={self.effective_wheel_radius_m:.4f} m, "
            f"track_width={self.track_width_m:.4f} m, "
            f"integration_source={self.integration_source})"
        )

    def odom_callback(self, msg):
        stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        pose_x = msg.pose.pose.position.x
        pose_y = msg.pose.pose.position.y
        pose_yaw = quaternion_to_yaw(msg.pose.pose.orientation)

        if self.prev_stamp_sec is None:
            self.prev_stamp_sec = stamp_sec
            self.prev_x = pose_x
            self.prev_y = pose_y
            self.prev_yaw = pose_yaw
            self.publish_ticks()
            return

        dt = stamp_sec - self.prev_stamp_sec
        self.prev_stamp_sec = stamp_sec
        if dt <= 0.0:
            return

        if self.integration_source == "pose":
            left_distance, right_distance = self.pose_delta_to_track_distances(
                pose_x, pose_y, pose_yaw
            )
        else:
            linear_x = msg.twist.twist.linear.x
            angular_z = msg.twist.twist.angular.z
            left_velocity = linear_x - angular_z * self.track_width_m * 0.5
            right_velocity = linear_x + angular_z * self.track_width_m * 0.5
            left_distance = left_velocity * dt
            right_distance = right_velocity * dt

        self.left_ticks_float += (
            left_distance / self.meters_per_tick
        ) * self.left_ticks_sign
        self.right_ticks_float += (
            right_distance / self.meters_per_tick
        ) * self.right_ticks_sign

        self.prev_x = pose_x
        self.prev_y = pose_y
        self.prev_yaw = pose_yaw
        self.publish_ticks()

    def pose_delta_to_track_distances(self, pose_x, pose_y, pose_yaw):
        delta_x = pose_x - self.prev_x
        delta_y = pose_y - self.prev_y
        delta_yaw = normalize_angle(pose_yaw - self.prev_yaw)

        mid_yaw = self.prev_yaw + 0.5 * delta_yaw
        center_distance = delta_x * math.cos(mid_yaw) + delta_y * math.sin(mid_yaw)

        half_yaw_distance = delta_yaw * self.track_width_m * 0.5
        left_distance = center_distance - half_yaw_distance
        right_distance = center_distance + half_yaw_distance
        return left_distance, right_distance

    def publish_ticks(self):
        msg = Int64MultiArray()
        msg.data = [
            int(round(self.left_ticks_float)),
            int(round(self.right_ticks_float)),
        ]
        self.publisher.publish(msg)

        self.publish_count += 1
        if self.publish_count == 1:
            self.get_logger().info(
                f"First mock encoder ticks published to {self.output_encoder_topic}"
            )


def main():
    rclpy.init()
    node = GazeboOdomToEncoderTicks()
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
