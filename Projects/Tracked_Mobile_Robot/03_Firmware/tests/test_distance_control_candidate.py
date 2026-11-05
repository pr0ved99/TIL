"""Run STM goal/PWM integration candidate or saved source on a native PC."""
import argparse
import json
from pathlib import Path
import sys

from distance_control_candidate import HERE, prepare
import test_distance_timing_candidate as runner


def write_guide(path, changes):
    text = (HERE / 'distance_control_guide_intro_ko.md').read_text(encoding='utf-8')
    for i, (relative, label, old, new) in enumerate(changes, 1):
        text += f'\n## {i}. Core/{relative}\n\n{label}.\n'
        if label.endswith('삽입'):
            assert new.endswith(old)
            text += '\n`' + old + '`로 시작하는 기존 함수 바로 앞에 아래 전체 함수를 삽입한다. 기존 함수는 유지한다.\n'
            text += '\n```c\n' + new[:-len(old)].rstrip() + '\n```\n'
            continue
        text += '\n**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**\n'
        if len(old.splitlines()) <= 12:
            text += '\n찾을 기존 블록:\n\n```c\n' + old.rstrip() + '\n```\n'
        else:
            text += '\n교체 시작: `' + old.splitlines()[0] + '`\n'
            text += '\n해당 함수 또는 case 전체를 교체한다. 다음 함수/case는 유지한다.\n'
        text += '\n교체할 전체 블록:\n\n```c\n' + new.rstrip() + '\n```\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--saved', action='store_true')
    parser.add_argument('--guide', type=Path)
    args = parser.parse_args()
    candidate, changes = ({}, []) if args.saved else prepare()
    fixture = HERE / 'distance_control_host_fixture.c'
    intro = HERE / 'distance_control_guide_intro_ko.md'
    runner.prepare = lambda: (candidate, [])
    runner.EXTRA_NAMES = ('distance_move',)
    runner.EXTRA_INPUTS = (HERE / 'distance_control_candidate.py', fixture,
                           Path(__file__).resolve()) + ((intro,) if intro.exists() else ())
    runner.FIXTURE_TAIL = fixture.read_text(encoding='utf-8')
    sys.argv = [runner.__file__, '--cc', args.cc, '--output', str(args.output)]
    if args.saved:
        sys.argv.append('--saved')
    runner.main()
    report = json.loads(args.output.read_text(encoding='utf-8'))
    report['scope'] = __doc__
    report['limitations'] = [
        'Host execution, not an STM board build or measured stop-time/distance result',
        'ESP request parser/executor and browser distance controls not wired yet',
        'Goal-reached means cutoff; coasting counts and actual link travel must be measured',
    ]
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if args.guide:
        assert not args.saved
        write_guide(args.guide, changes)


if __name__ == '__main__':
    main()
