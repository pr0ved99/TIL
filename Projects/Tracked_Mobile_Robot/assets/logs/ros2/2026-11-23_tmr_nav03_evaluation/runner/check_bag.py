"""Read the representative MCAP and match its terminal action UUID to the CSV."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path

from rclpy.serialization import deserialize_message
from rosbag2_py import ConverterOptions, SequentialReader, StorageOptions
from rosidl_runtime_py.utilities import get_message
import yaml

from run_series import TOPICS

ROOT = Path(__file__).resolve().parents[1]


def main():
    name = yaml.safe_load((ROOT/'protocol.yaml').read_text())['representative_bag']
    route,seed = name.split('-')
    with (ROOT/'results.csv').open() as f:
        row, = [r for r in csv.DictReader(f) if r['route']==route and r['seed']==seed]
    reader = SequentialReader()
    reader.open(StorageOptions(uri=str(ROOT/f'{name}_bag'),storage_id='mcap'),ConverterOptions('', ''))
    types = {t.name:get_message(t.type) for t in reader.get_all_topics_and_types()}
    counts = Counter()
    action_states = defaultdict(list)
    grid = None
    final_command = None
    first = last = None
    while reader.has_next():
        topic, payload, stamp = reader.read_next()
        counts[topic] += 1
        if first is None: first = stamp
        last = stamp
        if topic.endswith('/_action/status'):
            for s in deserialize_message(payload,types[topic]).status_list:
                statuses = action_states[bytes(s.goal_info.goal_id.uuid).hex()]
                if not statuses or statuses[-1]!=s.status:
                    statuses.append(s.status)
        elif topic=='/map':
            info = deserialize_message(payload,types[topic]).info
            grid = [info.width,info.height]
        elif topic=='/cmd_vel':
            m = deserialize_message(payload,types[topic])
            final_command = [m.linear.x,m.linear.y,m.linear.z,m.angular.x,m.angular.y,m.angular.z]
    assert all(counts[t] for t in TOPICS), counts
    assert grid == yaml.safe_load((ROOT/'protocol.yaml').read_text())['map']['size_pixels']
    expected = {'SUCCEEDED':4,'CANCELED':5,'ABORTED':6}[row['status']]
    assert action_states[row['goal_uuid']][-1] == expected
    assert max(map(abs,final_command)) <= .001
    check = dict(trial=name,counts=dict(sorted(counts.items())),bag_duration_s=(last-first)/1e9,
                 map_size=grid,goal_uuid=row['goal_uuid'],action_states=action_states[row['goal_uuid']],final_cmd=final_command)
    (ROOT/'bag_check.json').write_text(json.dumps(check,indent=2)+'\n')


if __name__ == '__main__':
    main()
