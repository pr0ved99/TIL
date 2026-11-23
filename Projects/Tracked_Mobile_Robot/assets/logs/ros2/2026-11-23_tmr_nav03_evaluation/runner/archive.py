"""Collect observations, including setup failures, retaining the original action UUIDs."""
from pathlib import Path
import shutil
import sys
import tarfile

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = Path(sys.argv[1])
    config = yaml.safe_load((ROOT/'protocol.yaml').read_text())
    trials = [f'{r}-{s}' for r in config['goals'] for s in config['gazebo_seeds']]
    trials += ['aux-'+case for case in config['auxiliary']['cases']]
    with tarfile.open(ROOT/'runs.tar.gz.tmp','w:gz',compresslevel=6) as archive:
        for name in trials:
            attempts = sorted((source/name).glob('attempt-*'))
            completed = [a for a in attempts if (a/'dispatch.json').is_file()]
            if len(completed)!=1:
                raise RuntimeError(f'{name}: expected exactly one dispatch, found {len(completed)}')
            current = completed[0]
            for f in ['dispatch.json','result.json','contacts.json.gz','trace.json.gz','trial.log','stack.log','scan.log']:
                archive.add(current/f,arcname=f'{name}/{f}')
            if (current/'bag.log').is_file():
                archive.add(current/'bag.log',arcname=f'{name}/bag.log')
            for a in attempts:
                if a!=current:
                    for f in a.glob('*.log'):
                        archive.add(f,arcname=f'{name}/pre-dispatch/{a.name}/{f.name}')
    (ROOT/'runs.tar.gz.tmp').replace(ROOT/'runs.tar.gz')
    rep = config['representative_bag']
    bag, = (source/rep).glob('attempt-*/bag/metadata.yaml')
    shutil.copytree(bag.parent,ROOT/f'{rep}_bag',dirs_exist_ok=True)


if __name__ == '__main__':
    main()
