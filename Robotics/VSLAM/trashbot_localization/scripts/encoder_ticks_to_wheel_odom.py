#!/usr/bin/env python3
"""Convert cumulative left/right motor encoder ticks into wheel odometry."""

import math
import sys

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Int64MultiArray


def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_to_quaternion(yaw):
    half = yaw * 0.5
    return 0.0, 0.0, math.sin(half), math.cos(half)


class EncoderTicksToWheelOdom(Node):
    def __init__(self):
        super().__init__("encoder_ticks_to_wheel_odom")

        self.input_topic = self.declare_parameter(
            "input_encoder_topic", "/motor/encoder_ticks"
        ).value
        self.output_topic = self.declare_parameter(
            "output_odom_topic", "/wheel/odometry"
        ).value
        self.frame_id = self.declare_parameter("frame_id", "odom").value
        self.child_frame_id = self.declare_parameter(
            "child_frame_id", "base_footprint"
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
        self.left_distance_scale = float(
            self.declare_parameter("left_distance_scale", 1.0).value
        )
        self.right_distance_scale = float(
            self.declare_parameter("right_distance_scale", 1.0).value
        )
        self.reject_outlier_samples = bool(
            self.declare_parameter("reject_outlier_samples", True).value
        )
        self.max_tick_delta = int(
            self.declare_parameter("max_tick_delta", 2000).value
        )
        self.max_linear_velocity_mps = float(
            self.declare_parameter("max_linear_velocity_mps", 0.8).value
        )
        self.max_angular_velocity_radps = float(
            self.declare_parameter("max_angular_velocity_radps", 3.0).value
        )
        self.max_encoder_gap_sec = float(
            self.declare_parameter("max_encoder_gap_sec", 0.5).value
        )

        self.pose_covariance_x = float(
            self.declare_parameter("pose_covariance_x", 0.02).value
        )
        self.pose_covariance_y = float(
            self.declare_parameter("pose_covariance_y", 0.02).value
        )
        self.pose_covariance_yaw = float(
            self.declare_parameter("pose_covariance_yaw", 0.05).value
        )
        self.twist_covariance_x = float(
            self.declare_parameter("twist_covariance_x", 0.02).value
        )
        self.twist_covariance_yaw = float(
            self.declare_parameter("twist_covariance_yaw", 0.05).value
        )

        if self.ticks_per_revolution <= 0:
            raise ValueError("ticks_per_revolution must be positive")
        if self.effective_wheel_radius_m <= 0:
            raise ValueError("effective_wheel_radius_m must be positive")
        if self.track_width_m <= 0:
            raise ValueError("track_width_m must be positive")
        if self.left_distance_scale <= 0:
            raise ValueError("left_distance_scale must be positive")
        if self.right_distance_scale <= 0:
            raise ValueError("right_distance_scale must be positive")
        if self.max_tick_delta < 0:
            raise ValueError("max_tick_delta must be >= 0")
        if self.max_linear_velocity_mps <= 0:
            raise ValueError("max_linear_velocity_mps must be positive")
        if self.max_angular_velocity_radps <= 0:
            raise ValueError("max_angular_velocity_radps must be positive")
        if self.max_encoder_gap_sec <= 0:
            raise ValueError("max_encoder_gap_sec must be positive")

        self.meters_per_tick = (
            2.0 * math.pi * self.effective_wheel_radius_m
        ) / self.ticks_per_revolution

        self.prev_left_ticks = None
        self.prev_right_ticks = None
        self.prev_time = None
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.rejected_samples = 0

        self.publisher = self.create_publisher(Odometry, self.output_topic, 10)
        self.subscription = self.create_subscription(
            Int64MultiArray,
            self.input_topic,
            self.encoder_callback,
            10,
        )

        self.get_logger().info(
            "Converting cumulative encoder ticks "
            f"{self.input_topic} -> {self.output_topic} "
            f"(ticks_per_rev={self.ticks_per_revolution:.1f}, "
            f"radius={self.effective_wheel_radius_m:.4f} m, "
            f"track_width={self.track_width_m:.4f} m, "
            f"left_scale={self.left_distance_scale:.4f}, "
            f"right_scale={self.right_distance_scale:.4f}, "
            f"max_tick_delta={self.max_tick_delta}, "
            f"max_v={self.max_linear_velocity_mps:.2f} m/s, "
            f"max_w={self.max_angular_velocity_radps:.2f} rad/s)"
        )

    def encoder_callback(self, msg):
        if len(msg.data) < 2:
            self.get_logger().warn(
                f"{self.input_topic} must contain [left_ticks, right_ticks]"
            )
            return

        now = self.get_clock().now()
        left_ticks = int(msg.data[0])
        right_ticks = int(msg.data[1])

        if self.prev_left_ticks is None:
            self.prev_left_ticks = left_ticks
            self.prev_right_ticks = right_ticks
            self.prev_time = now
            self.publish_odom(now, 0.0, 0.0)
            return

        dt = (now - self.prev_time).nanoseconds * 1e-9
        if dt <= 0.0:
            return
        if self.reject_outlier_samples and dt > self.max_encoder_gap_sec:
            self.reject_sample(
                now,
                left_ticks,
                right_ticks,
                (
                    f"encoder gap {dt:.3f}s exceeded "
                    f"max_encoder_gap_sec={self.max_encoder_gap_sec:.3f}s"
                ),
            )
            return

        delta_left_ticks = (left_ticks - self.prev_left_ticks) * self.left_ticks_sign
        delta_right_ticks = (
            right_ticks - self.prev_right_ticks
        ) * self.right_ticks_sign
        if (
            self.reject_outlier_samples
            and self.max_tick_delta > 0
            and (
                abs(delta_left_ticks) > self.max_tick_delta
                or abs(delta_right_ticks) > self.max_tick_delta
            )
        ):
            self.reject_sample(
                now,
                left_ticks,
                right_ticks,
                (
                    "encoder tick jump exceeded limit "
                    f"(left_delta={delta_left_ticks:.0f}, "
                    f"right_delta={delta_right_ticks:.0f}, "
                    f"max_tick_delta={self.max_tick_delta})"
                ),
            )
            return

        left_distance = (
            delta_left_ticks * self.meters_per_tick * self.left_distance_scale
        )
        right_distance = (
            delta_right_ticks * self.meters_per_tick * self.right_distance_scale
        )
        center_distance = 0.5 * (left_distance + right_distance)
        delta_yaw = (right_distance - left_distance) / self.track_width_m
        linear_x = center_distance / dt
        angular_z = delta_yaw / dt
        if (
            self.reject_outlier_samples
            and (
                abs(linear_x) > self.max_linear_velocity_mps
                or abs(angular_z) > self.max_angular_velocity_radps
            )
        ):
            self.reject_sample(
                now,
                left_ticks,
                right_ticks,
                (
                    "encoder-derived velocity exceeded limit "
                    f"(vx={linear_x:.3f} m/s, wz={angular_z:.3f} rad/s, "
                    f"max_v={self.max_linear_velocity_mps:.3f}, "
                    f"max_w={self.max_angular_velocity_radps:.3f})"
                ),
            )
            return

        mid_yaw = self.yaw + 0.5 * delta_yaw
        self.x += center_distance * math.cos(mid_yaw)
        self.y += center_distance * math.sin(mid_yaw)
        self.yaw = normalize_angle(self.yaw + delta_yaw)

        self.prev_left_ticks = left_ticks
        self.prev_right_ticks = right_ticks
        self.prev_time = now
        self.publish_odom(now, linear_x, angular_z)

    def reject_sample(self, stamp, left_ticks, right_ticks, reason):
        self.rejected_samples += 1
        if self.rejected_samples <= 5 or self.rejected_samples % 20 == 0:
            self.get_logger().warn(
                f"Rejected encoder sample #{self.rejected_samples}: {reason}. "
                "Resetting encoder baseline and publishing zero velocity."
            )

        self.prev_left_ticks = left_ticks
        self.prev_right_ticks = right_ticks
        self.prev_time = stamp
        self.publish_odom(stamp, 0.0, 0.0)

    def publish_odom(self, stamp, linear_x, angular_z):
        odom = Odometry()
        odom.header.stamp = stamp.to_msg()
        odom.header.frame_id = self.frame_id
        odom.child_frame_id = self.child_frame_id
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        qx, qy, qz, qw = yaw_to_quaternion(self.yaw)
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = linear_x
        odom.twist.twist.angular.z = angular_z

        odom.pose.covariance[0] = self.pose_covariance_x
        odom.pose.covariance[7] = self.pose_covariance_y
        odom.pose.covariance[35] = self.pose_covariance_yaw
        odom.twist.covariance[0] = self.twist_covariance_x
        odom.twist.covariance[35] = self.twist_covariance_yaw

        self.publisher.publish(odom)


def main():
    rclpy.init()
    node = EncoderTicksToWheelOdom()
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
