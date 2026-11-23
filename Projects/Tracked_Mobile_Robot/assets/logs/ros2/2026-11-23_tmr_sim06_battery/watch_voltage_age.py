"""Report freshness transitions for the SIM-06 battery voltage sample."""

import rclpy
from diagnostic_msgs.msg import DiagnosticArray
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time


class VoltageAgeMonitor(Node):
    STALE_AFTER_NS = 1_500_000_000

    def __init__(self):
        super().__init__("tmr_voltage_age_monitor")
        self.latest_stamp_ns = None
        self.last_state = None
        self.create_subscription(
            DiagnosticArray, "/tmr/sim/battery_voltage", self.receive_sample, 1
        )
        self.create_timer(0.1, self.check_age)
        self.check_age()

    def receive_sample(self, msg):
        if not any(status.name == "tmr/battery_voltage" for status in msg.status):
            return
        stamp_ns = Time.from_msg(msg.header.stamp).nanoseconds
        if 0 < stamp_ns <= self.get_clock().now().nanoseconds:
            if self.latest_stamp_ns is None or stamp_ns > self.latest_stamp_ns:
                self.latest_stamp_ns = stamp_ns

    def check_age(self):
        now_ns = self.get_clock().now().nanoseconds
        if self.latest_stamp_ns is None or now_ns < self.latest_stamp_ns:
            self.latest_stamp_ns = None
            state = "WAITING"
            detail = ""
        else:
            age_ns = now_ns - self.latest_stamp_ns
            state = "STALE" if age_ns >= self.STALE_AFTER_NS else "FRESH"
            detail = f"  age={age_ns / 1_000_000_000:.3f} s"

        if state != self.last_state:
            print(state + detail, flush=True)
            self.last_state = state


if __name__ == "__main__":
    rclpy.init()
    monitor = VoltageAgeMonitor()
    try:
        rclpy.spin(monitor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        monitor.destroy_node()
        rclpy.try_shutdown()
