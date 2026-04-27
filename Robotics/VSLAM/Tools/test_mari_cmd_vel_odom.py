#!/usr/bin/env python3
"""Convert /cmd_vel into a simple odom->base_footprint TF for Mari RViz checks."""

import argparse
import math
import time

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_to_quaternion(yaw: float):
    half = yaw * 0.5
    return 0.0, 0.0, math.sin(half), math.cos(half)


def make_transform(parent_frame: str, child_frame: str, stamp, x: float, y: float, z: float, yaw: float):
    transform = TransformStamped()
    transform.header.stamp = stamp
    transform.header.frame_id = parent_frame
    transform.child_frame_id = child_frame
    transform.transform.translation.x = x
    transform.transform.translation.y = y
    transform.transform.translation.z = z

    qx, qy, qz, qw = yaw_to_quaternion(yaw)
    transform.transform.rotation.x = qx
    transform.transform.rotation.y = qy
    transform.transform.rotation.z = qz
    transform.transform.rotation.w = qw
    return transform


class CmdVelOdomPublisher(Node):
    def __init__(self, args):
        super().__init__("mari_cmd_vel_odom_test")
        self.args = args
        self.x = args.initial_x
        self.y = args.initial_y
        self.yaw = args.initial_yaw
        self.last_cmd = Twist()
        self.last_cmd_time = time.monotonic()
        self.last_update_time = time.monotonic()

        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.odom_publisher = self.create_publisher(Odometry, args.odom_topic, 10)
        self.cmd_subscriber = self.create_subscription(Twist, args.cmd_vel_topic, self.on_cmd_vel, 10)
        self.publish_static_map_to_odom()
        self.timer = self.create_timer(1.0 / args.rate, self.update)

        self.get_logger().info(
            f"Listening {args.cmd_vel_topic}, publishing {args.odom_topic} and "
            f"TF {args.map_frame} -> {args.odom_frame} -> {args.base_frame}"
        )
        self.get_logger().info(
            f"Limits: |linear.x| <= {args.max_linear_x} m/s, "
            f"|angular.z| <= {args.max_angular_z} rad/s, timeout={args.cmd_timeout}s"
        )

    def publish_static_map_to_odom(self):
        stamp = self.get_clock().now().to_msg()
        transform = make_transform(
            self.args.map_frame,
            self.args.odom_frame,
            stamp,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        self.static_tf_broadcaster.sendTransform(transform)

    def on_cmd_vel(self, msg: Twist):
        self.last_cmd.linear.x = clamp(msg.linear.x, -self.args.max_linear_x, self.args.max_linear_x)
        self.last_cmd.angular.z = clamp(msg.angular.z, -self.args.max_angular_z, self.args.max_angular_z)
        self.last_cmd_time = time.monotonic()

    def current_cmd(self):
        if time.monotonic() - self.last_cmd_time > self.args.cmd_timeout:
            return 0.0, 0.0
        return self.last_cmd.linear.x, self.last_cmd.angular.z

    def update(self):
        now = time.monotonic()
        dt = now - self.last_update_time
        self.last_update_time = now

        linear_x, angular_z = self.current_cmd()
        self.x += linear_x * math.cos(self.yaw) * dt
        self.y += linear_x * math.sin(self.yaw) * dt
        self.yaw = normalize_angle(self.yaw + angular_z * dt)

        stamp = self.get_clock().now().to_msg()
        transform = make_transform(
            self.args.odom_frame,
            self.args.base_frame,
            stamp,
            self.x,
            self.y,
            0.0,
            self.yaw,
        )
        self.tf_broadcaster.sendTransform(transform)
        self.publish_odom(stamp, linear_x, angular_z)

    def publish_odom(self, stamp, linear_x: float, angular_z: float):
        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self.args.odom_frame
        odom.child_frame_id = self.args.base_frame
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
        odom.pose.covariance[0] = 0.02
        odom.pose.covariance[7] = 0.02
        odom.pose.covariance[35] = 0.05
        odom.twist.covariance[0] = 0.02
        odom.twist.covariance[35] = 0.05
        self.odom_publisher.publish(odom)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Subscribe to /cmd_vel and publish a simple odom stream for Mari RViz checks."
    )
    parser.add_argument("--map-frame", default="map")
    parser.add_argument("--odom-frame", default="odom")
    parser.add_argument("--base-frame", default="base_footprint")
    parser.add_argument("--cmd-vel-topic", default="/cmd_vel")
    parser.add_argument("--odom-topic", default="/odom")
    parser.add_argument("--initial-x", type=float, default=0.0)
    parser.add_argument("--initial-y", type=float, default=0.0)
    parser.add_argument("--initial-yaw", type=float, default=0.0)
    parser.add_argument("--max-linear-x", type=float, default=0.35)
    parser.add_argument("--max-angular-z", type=float, default=1.2)
    parser.add_argument("--cmd-timeout", type=float, default=0.5)
    parser.add_argument("--rate", type=float, default=50.0)
    return parser.parse_args()


def main():
    args = parse_args()
    rclpy.init()
    node = CmdVelOdomPublisher(args)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
