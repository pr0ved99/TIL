#!/usr/bin/env python3
"""Keyboard teleoperation for Mari through geometry_msgs/Twist."""

import argparse
import select
import sys
import termios
import time
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


MOVE_BINDINGS = {
    "w": (1.0, 0.0),
    "\x1b[A": (1.0, 0.0),
    "s": (-1.0, 0.0),
    "\x1b[B": (-1.0, 0.0),
    "a": (0.0, 1.0),
    "\x1b[D": (0.0, 1.0),
    "d": (0.0, -1.0),
    "\x1b[C": (0.0, -1.0),
    "q": (1.0, 1.0),
    "e": (1.0, -1.0),
    "z": (-1.0, -1.0),
    "c": (-1.0, 1.0),
}

STOP_KEYS = {" ", "x", "k"}


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def ramp_toward(current: float, target: float, max_delta: float) -> float:
    if max_delta <= 0.0:
        return target
    if current < target:
        return min(current + max_delta, target)
    if current > target:
        return max(current - max_delta, target)
    return current


def read_key(timeout: float):
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if not ready:
        return None

    key = sys.stdin.read(1)
    if key != "\x1b":
        return key

    # Arrow keys arrive as escape sequences such as ESC [ A.
    sequence = key
    for _ in range(2):
        ready, _, _ = select.select([sys.stdin], [], [], 0.0)
        if not ready:
            break
        sequence += sys.stdin.read(1)
    return sequence


def make_twist(linear_x: float, angular_z: float) -> Twist:
    msg = Twist()
    msg.linear.x = linear_x
    msg.angular.z = angular_z
    return msg


class MariKeyboardTeleop(Node):
    def __init__(self, args):
        super().__init__("mari_keyboard_teleop")
        self.args = args
        self.publisher = self.create_publisher(Twist, args.cmd_vel_topic, 10)
        self.linear_speed = args.linear_speed
        self.angular_speed = args.angular_speed
        self.target_linear_scale = 0.0
        self.target_angular_scale = 0.0
        self.current_linear_x = 0.0
        self.current_angular_z = 0.0
        self.last_motion_key_time = 0.0
        self.last_update_time = time.monotonic()

        self.get_logger().info(
            f"Publishing Twist to {args.cmd_vel_topic} at {args.rate:.1f} Hz "
            f"(linear={self.linear_speed:.2f} m/s, angular={self.angular_speed:.2f} rad/s, "
            f"linear_accel={self.args.linear_accel:.2f} m/s^2, "
            f"angular_accel={self.args.angular_accel:.2f} rad/s^2)"
        )

    def set_motion(self, linear_scale: float, angular_scale: float):
        self.target_linear_scale = linear_scale
        self.target_angular_scale = angular_scale
        self.last_motion_key_time = time.monotonic()

    def stop(self):
        self.target_linear_scale = 0.0
        self.target_angular_scale = 0.0
        self.current_linear_x = 0.0
        self.current_angular_z = 0.0
        self.last_update_time = time.monotonic()
        try:
            if self.context.ok():
                self.publisher.publish(make_twist(0.0, 0.0))
        except Exception:
            if self.context.ok():
                raise

    def handle_key(self, key: str) -> bool:
        if key in MOVE_BINDINGS:
            linear_scale, angular_scale = MOVE_BINDINGS[key]
            self.set_motion(linear_scale, angular_scale)
            return True

        if key in STOP_KEYS:
            self.stop()
            return True

        if key == "r":
            self.linear_speed = clamp(
                self.linear_speed + self.args.linear_step,
                0.0,
                self.args.max_linear_speed,
            )
            self.print_speed()
            return True

        if key == "f":
            self.linear_speed = clamp(
                self.linear_speed - self.args.linear_step,
                0.0,
                self.args.max_linear_speed,
            )
            self.print_speed()
            return True

        if key == "t":
            self.angular_speed = clamp(
                self.angular_speed + self.args.angular_step,
                0.0,
                self.args.max_angular_speed,
            )
            self.print_speed()
            return True

        if key == "g":
            self.angular_speed = clamp(
                self.angular_speed - self.args.angular_step,
                0.0,
                self.args.max_angular_speed,
            )
            self.print_speed()
            return True

        if key == "h":
            print_help(self.args)
            self.print_speed()
            return True

        if key == "\x03" or key == "\x1b":
            return False

        return True

    def current_twist(self) -> Twist:
        if time.monotonic() - self.last_motion_key_time > self.args.key_timeout:
            self.stop()
            return make_twist(0.0, 0.0)

        now = time.monotonic()
        dt = max(0.0, now - self.last_update_time)
        self.last_update_time = now

        target_linear_x = self.target_linear_scale * self.linear_speed
        target_angular_z = self.target_angular_scale * self.angular_speed

        if self.args.no_smoothing:
            self.current_linear_x = target_linear_x
            self.current_angular_z = target_angular_z
        else:
            self.current_linear_x = ramp_toward(
                self.current_linear_x,
                target_linear_x,
                self.args.linear_accel * dt,
            )
            self.current_angular_z = ramp_toward(
                self.current_angular_z,
                target_angular_z,
                self.args.angular_accel * dt,
            )

        return make_twist(self.current_linear_x, self.current_angular_z)

    def publish_current(self):
        self.publisher.publish(self.current_twist())

    def print_speed(self):
        print(
            f"speed: linear={self.linear_speed:.2f} m/s, "
            f"angular={self.angular_speed:.2f} rad/s"
        )


def print_help(args):
    print(
        f"""
Mari keyboard teleoperation

Movement:
  w / up        forward
  s / down      backward
  a / left      rotate left in place
  d / right     rotate right in place
  q, e          forward arc left/right
  z, c          backward arc right/left
  space, x, k   stop

Speed:
  r / f         linear speed up/down
  t / g         angular speed up/down

Other:
  h             show this help
  Ctrl-C, Esc   stop and exit

Topic:
  {args.cmd_vel_topic}

Safety:
  If no movement key is received for {args.key_timeout:.2f}s, the command is reset to zero.

Smoothing:
  Velocity commands are ramped with linear_accel={args.linear_accel:.2f} m/s^2 and
  angular_accel={args.angular_accel:.2f} rad/s^2. Use --no-smoothing for step commands.
"""
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish /cmd_vel from keyboard input for Mari Gazebo manual driving."
    )
    parser.add_argument("--cmd-vel-topic", default="/cmd_vel")
    parser.add_argument("--linear-speed", type=float, default=0.12)
    parser.add_argument("--angular-speed", type=float, default=0.5)
    parser.add_argument("--linear-step", type=float, default=0.02)
    parser.add_argument("--angular-step", type=float, default=0.1)
    parser.add_argument("--max-linear-speed", type=float, default=0.35)
    parser.add_argument("--max-angular-speed", type=float, default=1.2)
    parser.add_argument("--key-timeout", type=float, default=0.7)
    parser.add_argument("--rate", type=float, default=50.0)
    parser.add_argument("--linear-accel", type=float, default=0.30)
    parser.add_argument("--angular-accel", type=float, default=1.00)
    parser.add_argument("--no-smoothing", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if not sys.stdin.isatty():
        print("teleop_mari_keyboard.py must be run from an interactive terminal.", file=sys.stderr)
        return 2

    rclpy.init()
    node = MariKeyboardTeleop(args)
    terminal_settings = termios.tcgetattr(sys.stdin)
    period = 1.0 / args.rate
    next_publish_time = time.monotonic()

    try:
        print_help(args)
        node.print_speed()
        tty.setcbreak(sys.stdin.fileno())

        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.0)
            key = read_key(min(period, 0.05))
            if key is not None and not node.handle_key(key):
                break

            now = time.monotonic()
            if now >= next_publish_time:
                node.publish_current()
                next_publish_time = now + period

    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.stop()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, terminal_settings)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    return 0


if __name__ == "__main__":
    sys.exit(main())
