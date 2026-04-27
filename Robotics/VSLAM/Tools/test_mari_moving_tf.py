#!/usr/bin/env python3
"""Publish a simple moving TF and odometry stream for Mari RViz checks."""

import argparse
import math
import time

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster


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


class MovingTfPublisher(Node):
    def __init__(self, args):
        super().__init__("mari_moving_tf_test")
        self.args = args
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.odom_publisher = self.create_publisher(Odometry, args.odom_topic, 10)
        self.start_time = time.monotonic()
        self.publish_static_map_to_odom()
        self.timer = self.create_timer(1.0 / args.rate, self.publish_tf)
        self.get_logger().info(
            f"Publishing TF: {args.map_frame} -> {args.odom_frame} -> {args.base_frame}, "
            f"radius={args.radius} m, angular_speed={args.angular_speed} rad/s"
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

    def publish_tf(self):
        elapsed = time.monotonic() - self.start_time
        theta = elapsed * self.args.angular_speed
        stamp = self.get_clock().now().to_msg()
        x = self.args.radius * math.cos(theta)
        y = self.args.radius * math.sin(theta)
        yaw = theta + math.pi / 2.0

        # Keep the robot x-axis roughly tangent to the circular trajectory.
        transform = make_transform(
            self.args.odom_frame,
            self.args.base_frame,
            stamp,
            x,
            y,
            0.0,
            yaw,
        )

        self.tf_broadcaster.sendTransform(transform)
        self.publish_odom(stamp, x, y, yaw)

    def publish_odom(self, stamp, x: float, y: float, yaw: float):
        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self.args.odom_frame
        odom.child_frame_id = self.args.base_frame
        odom.pose.pose.position.x = x
        odom.pose.pose.position.y = y
        odom.pose.pose.position.z = 0.0

        qx, qy, qz, qw = yaw_to_quaternion(yaw)
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        odom.twist.twist.linear.x = self.args.radius * self.args.angular_speed
        odom.twist.twist.angular.z = self.args.angular_speed
        self.odom_publisher.publish(odom)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish map->odom and moving odom->base_footprint TF for RViz checks."
    )
    parser.add_argument("--map-frame", default="map")
    parser.add_argument("--odom-frame", default="odom")
    parser.add_argument("--base-frame", default="base_footprint")
    parser.add_argument("--odom-topic", default="/odom")
    parser.add_argument("--radius", type=float, default=0.5)
    parser.add_argument("--angular-speed", type=float, default=0.35)
    parser.add_argument("--rate", type=float, default=30.0)
    return parser.parse_args()


def main():
    args = parse_args()
    rclpy.init()
    node = MovingTfPublisher(args)
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
