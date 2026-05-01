#!/usr/bin/env python3
"""Publish mock cumulative left/right motor encoder ticks."""

import math
import sys

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64MultiArray


class MockMotorEncoderTicks(Node):
    def __init__(self):
        super().__init__("mock_motor_encoder_ticks")

        self.output_topic = self.declare_parameter(
            "output_encoder_topic", "/motor/encoder_ticks"
        ).value
        self.rate_hz = float(self.declare_parameter("rate_hz", 30.0).value)
        self.ticks_per_revolution = float(
            self.declare_parameter("ticks_per_revolution", 1560.0).value
        )
        self.effective_wheel_radius_m = float(
            self.declare_parameter("effective_wheel_radius_m", 0.021).value
        )
        self.track_width_m = float(
            self.declare_parameter("track_width_m", 0.137553).value
        )
        self.linear_velocity_mps = float(
            self.declare_parameter("linear_velocity_mps", 0.10).value
        )
        self.angular_velocity_radps = float(
            self.declare_parameter("angular_velocity_radps", 0.0).value
        )
        self.tick_jump_after_sec = float(
            self.declare_parameter("tick_jump_after_sec", 0.0).value
        )
        self.tick_jump_left = int(self.declare_parameter("tick_jump_left", 0).value)
        self.tick_jump_right = int(
            self.declare_parameter("tick_jump_right", 0).value
        )

        if self.rate_hz <= 0:
            raise ValueError("rate_hz must be positive")
        if self.ticks_per_revolution <= 0:
            raise ValueError("ticks_per_revolution must be positive")
        if self.effective_wheel_radius_m <= 0:
            raise ValueError("effective_wheel_radius_m must be positive")
        if self.track_width_m <= 0:
            raise ValueError("track_width_m must be positive")

        self.meters_per_tick = (
            2.0 * math.pi * self.effective_wheel_radius_m
        ) / self.ticks_per_revolution
        self.left_ticks_float = 0.0
        self.right_ticks_float = 0.0
        self.start_time = self.get_clock().now()
        self.tick_jump_applied = False

        self.publisher = self.create_publisher(Int64MultiArray, self.output_topic, 10)
        self.timer = self.create_timer(1.0 / self.rate_hz, self.timer_callback)

        self.get_logger().info(
            f"Publishing mock cumulative encoder ticks to {self.output_topic} "
            f"at {self.rate_hz:.1f} Hz"
        )
        if self.tick_jump_after_sec > 0.0 and (
            self.tick_jump_left != 0 or self.tick_jump_right != 0
        ):
            self.get_logger().warn(
                "Mock encoder will inject one tick jump after "
                f"{self.tick_jump_after_sec:.2f}s "
                f"(left={self.tick_jump_left}, right={self.tick_jump_right})"
            )

    def timer_callback(self):
        dt = 1.0 / self.rate_hz
        left_velocity = self.linear_velocity_mps - (
            self.angular_velocity_radps * self.track_width_m * 0.5
        )
        right_velocity = self.linear_velocity_mps + (
            self.angular_velocity_radps * self.track_width_m * 0.5
        )

        self.left_ticks_float += (left_velocity * dt) / self.meters_per_tick
        self.right_ticks_float += (right_velocity * dt) / self.meters_per_tick
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9
        if (
            not self.tick_jump_applied
            and self.tick_jump_after_sec > 0.0
            and elapsed >= self.tick_jump_after_sec
        ):
            self.left_ticks_float += self.tick_jump_left
            self.right_ticks_float += self.tick_jump_right
            self.tick_jump_applied = True
            self.get_logger().warn(
                "Injected mock encoder tick jump "
                f"(left={self.tick_jump_left}, right={self.tick_jump_right})"
            )

        msg = Int64MultiArray()
        msg.data = [
            int(round(self.left_ticks_float)),
            int(round(self.right_ticks_float)),
        ]
        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = MockMotorEncoderTicks()
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
