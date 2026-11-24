#!/usr/bin/python3
"""Publish the three SIM-06 fixtures at 2 Hz, omitting temperature after six samples."""

from pathlib import Path

import rclpy
import yaml
from diagnostic_msgs.msg import DiagnosticArray
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rosidl_runtime_py.set_message import set_message_fields


class TemperatureGapDemo(Node):
    def __init__(self):
        super().__init__("tmr_sim_temperature_gap_demo")
        root = Path(__file__).resolve().parents[1]
        inputs = {
            "voltage": "2026-11-23_tmr_sim06_battery",
            "current": "2026-11-24_tmr_sim06_current",
            "temperature": "2026-11-24_tmr_sim06_temperature",
        }
        self.channels = {}
        for label, folder in inputs.items():
            fixture = yaml.safe_load((root / folder / "sample.yaml").read_text())
            msg = DiagnosticArray()
            set_message_fields(msg, {"status": fixture["status"]})
            channel = msg.status[0].name.removeprefix("tmr/")
            pub = self.create_publisher(DiagnosticArray, f"/tmr/sim/{channel}", 10)
            self.channels[label] = (pub, msg)
        self.ticks = 0
        self.create_timer(0.5, self.publish_samples)
        print("세 토픽의 구독자를 기다리는 중", flush=True)

    def publish_samples(self):
        if self.ticks == 0:
            if any(pub.get_subscription_count() == 0 for pub, _ in self.channels.values()):
                return
            print("전압·전류·온도 발행 시작 (2 Hz)", flush=True)
        if self.ticks == 6:
            print("온도 6회 발행 완료. 전압·전류는 계속 발행 중 (Ctrl+C로 종료)", flush=True)
        stamp = self.get_clock().now().to_msg()
        for label, (pub, msg) in self.channels.items():
            if label == "temperature" and self.ticks >= 6:
                continue
            msg.header.stamp = stamp
            pub.publish(msg)
        self.ticks += 1


if __name__ == "__main__":
    rclpy.init()
    demo = TemperatureGapDemo()
    try:
        rclpy.spin(demo)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        demo.destroy_node()
        rclpy.try_shutdown()
