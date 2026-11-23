"""Record Gazebo Harmonic robot contact pairs and count obstacle encounters by model."""
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from threading import Lock

from gz.msgs10.contacts_pb2 import Contacts

NSEC = 1_000_000_000
GROUND = 'ground_plane::ground::collision'

def to_ns(stamp):
    return stamp.sec * NSEC + stamp.nsec

def classify(first, second, robot):
    if any('::' not in name for name in (first, second)):
        return 'unknown', ''
    a, b = (name.split('::', 1)[0] for name in (first, second))
    if a == robot and b == robot:
        return 'self', robot
    if a != robot and b != robot:
        return 'unknown', ''
    other = second if a == robot else first
    if other == GROUND:
        return 'ground', 'ground_plane'
    return 'obstacle', other.split('::', 1)[0]

class ContactRecorder:
    def __init__(self, node, manifest, robot='tmr'):
        self.node = node
        self.robot = robot
        self.topics = list(manifest)
        if not self.topics:
            raise ValueError('Contact topic manifest is empty')
        self.pairs = {}
        self.rows = []
        self.lock = Lock()
        for i, topic in enumerate(self.topics):
            if not node.subscribe(Contacts, topic, self.callback(i)):
                raise RuntimeError(f'Could not subscribe to {topic}')

    def callback(self, i):
        def record(msg):
            with self.lock:
                for hit in msg.contact:
                    names = tuple(sorted((hit.collision1.name, hit.collision2.name)))
                    if names not in self.pairs:
                        self.pairs[names] = len(self.pairs)
                    self.rows.append((to_ns(hit.header.stamp), i, self.pairs[names]))
        return record

    def all_advertised(self):
        return set(self.topics).issubset(self.node.topic_list())

    def latest_stamp(self):
        with self.lock:
            return max((row[0] for row in self.rows[-100:]), default=0)

    def snapshot(self, start_ns, end_ns):
        with self.lock:
            rows = sorted(row for row in self.rows if start_ns <= row[0] <= end_ns)
            pairs = sorted(self.pairs, key=self.pairs.get)
        return {'robot': self.robot, 'topics': self.topics, 'start_ns': start_ns, 'end_ns': end_ns,
                'pairs': pairs, 'row_columns': ['sim_ns','topic_index','pair_index'], 'rows': rows}

def summarize(raw, release_ns=100_000_000):
    """Merge contact across shapes per obstacle until a gap longer than release_ns."""
    counts = Counter()
    by_obstacle = defaultdict(set)
    by_pair = Counter()
    ground_ticks = set()
    seen = set()
    for tick, topic, idx in raw['rows']:
        first, second = raw['pairs'][idx]
        kind, model = classify(first, second, raw['robot'])
        counts[kind] += 1
        by_pair[(first, second)] += 1
        seen.add(topic)
        if kind == 'ground':
            ground_ticks.add(tick)
        elif kind == 'obstacle':
            by_obstacle[model].add(tick)
    episodes = []
    for model, ticks in sorted(by_obstacle.items()):
        previous = None
        for tick in sorted(ticks):
            if previous is None or tick - previous > release_ns:
                episodes.append({'model': model, 'first_ns': tick, 'last_ns': tick, 'physics_stamps': 1})
            else:
                episodes[-1]['last_ns'] = tick
                episodes[-1]['physics_stamps'] += 1
            previous = tick
    ground_times = [raw['start_ns'], *sorted(ground_ticks), raw['end_ns']]
    return {'duration_s':(raw['end_ns']-raw['start_ns'])/NSEC, 'records':dict(counts),
            'observed_pairs':[{'pair':list(pair),'records':n} for pair,n in sorted(by_pair.items())],
            'active_sensor_topics':[raw['topics'][i] for i in sorted(seen)],
            'ground_physics_stamps':len(ground_ticks),
            'max_ground_gap_ms':max((b-a)/1e6 for a,b in zip(ground_times,ground_times[1:])),
            'release_gap_ms':release_ns/1e6, 'obstacle_episodes':episodes}

def save_raw(path, raw):
    Path(path).write_bytes(gzip.compress((json.dumps(raw,separators=(',',':'))+'\n').encode(),mtime=0))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Summarize a recorded Gazebo contact window.')
    parser.add_argument('recording', type=Path)
    args = parser.parse_args()
    with gzip.open(args.recording, 'rt', encoding='utf-8') as source:
        print(json.dumps(summarize(json.load(source)), indent=2))
