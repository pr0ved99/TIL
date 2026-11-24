#!/usr/bin/python3
"""Replay three captured SIM-06 measurements and exercise the installed ROS service."""

import csv
import sys
import time
from pathlib import Path

import rclpy
import yaml
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rclpy.node import Node
from std_srvs.srv import Trigger


RECORDINGS = {
    "voltage": "2026-11-23_tmr_sim06_battery/received.yaml",
    "current": "2026-11-24_tmr_sim06_current/user_received.yaml",
    "temperature": "2026-11-24_tmr_sim06_temperature/user_received.yaml",
}


class SensorReplay(Node):
    def __init__(self):
        super().__init__("tmr_sim_sensor_replay")
        self.client = self.create_client(Trigger, "/tmr/sim/check_drive_sensors")
        self.channels = {}
        log_root = Path(__file__).resolve().parents[1]
        for label, filename in RECORDINGS.items():
            with (log_root / filename).open() as stream:
                recording = next(yaml.safe_load_all(stream))
            status, = recording["status"]
            stamp = recording["header"]["stamp"]
            values = {item["key"]: item["value"] for item in status["values"]}
            values["source"] = "REPLAY"
            values["recorded_stamp"] = f"{stamp['sec']}.{stamp['nanosec']:09d}"
            topic = "/tmr/sim/" + status["name"].removeprefix("tmr/")
            publisher = self.create_publisher(DiagnosticArray, topic, 10)
            self.channels[label] = publisher, status, values
        self.writer = csv.writer(sys.stdout, lineterminator="\n")

    def wait_for_monitor(self):
        if not self.client.wait_for_service(timeout_sec=8):
            raise RuntimeError("watch_sensor_states service is unavailable")
        deadline = time.monotonic() + 8
        while any(pub.get_subscription_count() == 0 for pub, _, _ in self.channels.values()):
            if time.monotonic() >= deadline:
                raise RuntimeError("waiting for subscriptions to all three sensor topics")
            rclpy.spin_once(self, timeout_sec=0.05)

    def publish_samples(self, silent, invalid):
        stamp = self.get_clock().now().to_msg()
        for label, (publisher, original, values) in self.channels.items():
            if label in silent:
                continue
            status = DiagnosticStatus(name=original["name"], hardware_id=original["hardware_id"],
                                      message=original["message"])
            fields = values.copy()
            if label == invalid:
                fields["valid"] = "false"
                status.level = DiagnosticStatus.ERROR
                status.message = "simulated_open_circuit"
            status.values = [KeyValue(key=key, value=value) for key, value in fields.items()]
            sample = DiagnosticArray(status=[status])
            sample.header.stamp = stamp
            publisher.publish(sample)

    def check(self, case, silent=(), invalid=None, waiting=False):
        expected = {}
        for label in self.channels:
            if waiting:
                expected[label] = "WAITING"
            else:
                freshness = "STALE" if label in silent else "FRESH"
                flag = "false" if label == invalid else "true"
                expected[label] = f"{freshness} valid={flag}"
        allowed = all(state == "FRESH valid=true" for state in expected.values())
        next_publish = 0
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            now = time.monotonic()
            if not waiting and now >= next_publish:
                self.publish_samples(silent, invalid)
                next_publish = now + 0.5
            future = self.client.call_async(Trigger.Request())
            rclpy.spin_until_future_complete(self, future, timeout_sec=2)
            if not future.done():
                raise TimeoutError(f"{case}: no service response")
            response = future.result()
            states = {}
            for column in response.message.split(" | "):
                label, _, state = column.partition("=")
                states[label] = state.partition(" age=")[0]
            if states == expected:
                self.writer.writerow([case, allowed, response.success, response.message])
                if response.success != allowed:
                    raise AssertionError(f"{case}: incorrect decision")
                return
            time.sleep(0.05)
        raise TimeoutError(f"{case}: {response.message}")

    def run(self):
        self.wait_for_monitor()
        self.writer.writerow(["case", "expected_success", "actual_success", "response"])
        self.check("before_replay", waiting=True)
        self.check("nominal")
        for label in self.channels:
            self.check(f"{label}_open_circuit", invalid=label)
            self.check(f"{label}_valid_again")
            self.check(f"{label}_stopped", silent=(label,))
            self.check(f"{label}_resumed")
        self.check("all_streams_stopped", silent=tuple(self.channels))
        self.check("all_streams_resumed")


if __name__ == "__main__":
    rclpy.init()
    replay = SensorReplay()
    try:
        replay.run()
    finally:
        replay.destroy_node()
        rclpy.try_shutdown()
