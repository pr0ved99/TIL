"""Send a planar velocity for two seconds of simulation time, then stop."""

from time import monotonic

import rclpy
from geometry_msgs.msg import Twist
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.signals import SignalHandlerOptions


def run_drive_step(node_name, *, linear_x=0.0, angular_z=0.0):
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = Node(node_name, parameter_overrides=[Parameter('use_sim_time', value=True)])
    pub = node.create_publisher(Twist, '/cmd_vel', 1)
    clock = node.get_clock()
    drive_started = False
    try:
        deadline = monotonic() + 10
        start = clock.now()
        while clock.now() <= start or not pub.get_subscription_count():
            if monotonic() >= deadline:
                raise SystemExit('Waiting for a running simulation and a /cmd_vel subscriber timed out.')
            rclpy.spin_once(node, timeout_sec=0.1)

        command = Twist()
        command.linear.x = linear_x
        command.angular.z = angular_z
        start = clock.now()
        finish = start + Duration(seconds=2)
        next_publish = start
        deadline = monotonic() + 15
        node.get_logger().info(f'linear.x = {linear_x:+.2f} m/s, angular.z = {angular_z:+.3f} rad/s for 2 s of simulation time.')
        while clock.now() < finish:
            now = clock.now()
            if monotonic() >= deadline or now < start:
                raise SystemExit('Simulation clock stalled or reset during the drive.')
            if now >= next_publish:
                drive_started = True
                pub.publish(command)
                next_publish = now + Duration(seconds=0.1)
            rclpy.spin_once(node, timeout_sec=0.05)
    finally:
        if drive_started:
            pub.publish(Twist())
            pub.wait_for_all_acked(Duration(seconds=1))
            node.get_logger().info('Sent zero velocity.')
        node.destroy_node()
        rclpy.shutdown()
