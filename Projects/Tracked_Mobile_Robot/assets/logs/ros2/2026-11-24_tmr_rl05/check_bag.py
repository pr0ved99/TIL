"""Read the recorded P05 bag and match its velocity commands to the policy log."""
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def check(folder):
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=str(folder / "bag"), storage_id="mcap"),
                rosbag2_py.ConverterOptions("", ""))
    types = {t.name: get_message(t.type) for t in reader.get_all_topics_and_types()}
    counts, frames = Counter(), set()
    commands = []
    while reader.has_next():
        topic, data, _ = reader.read_next()
        msg = deserialize_message(data, types[topic])
        counts[topic] += 1
        if topic == "/rl05/cmd_vel":
            commands.append([msg.linear.x, msg.angular.z])
        elif topic == "/rl05/scan":
            assert msg.header.frame_id == "laser_frame" and len(msg.ranges) == 360
        elif topic == "/rl05/odom":
            assert (msg.header.frame_id, msg.child_frame_id) == ("odom", "base_footprint")
        elif topic in ("/tf", "/tf_static"):
            frames.update((t.header.frame_id, t.child_frame_id) for t in msg.transforms)
        elif topic == "/map":
            size = [msg.info.width, msg.info.height]
            assert msg.header.frame_id == "map" and len(msg.data) == size[0] * size[1]
    assert set(counts) == {"/clock", "/rl05/cmd_vel", "/rl05/odom", "/rl05/scan", "/tf", "/tf_static", "/map"}
    assert {("map", "odom"), ("odom", "base_footprint"), ("base_link", "laser_frame")} <= frames
    with (folder / "policy.csv").open() as stream:
        expected = [[float(r["cmd_v"]), float(r["cmd_w"])] for r in csv.DictReader(stream)]
    assert len(commands) > len(expected) and np.array_equal(commands[:len(expected)], expected)
    assert np.any(expected) and not np.any(commands[len(expected):])
    return dict(messages=sum(counts.values()), topics=dict(sorted(counts.items())), map_cells=size,
                transforms=sorted(frames), policy_commands_verified=len(expected),
                trailing_zero_commands=len(commands)-len(expected))


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent / "guided_map_amcl_P05_repeat"
    report = json.dumps(check(folder), indent=2) + "\n"
    (folder / "bag_check.json").write_text(report)
    print(report)
