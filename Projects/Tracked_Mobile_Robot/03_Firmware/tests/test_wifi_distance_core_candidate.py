"""ESP distance contract/executor native review; no production writes or board build."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest import mock

from wifi_distance_core_candidate import HERE, MAIN, prepare
import test_wifi_nonzero_core as baseline

CASES = ('parsing', 'distance_policy', 'distance_round_trip', 'first_zero',
         'other_owner', 'other_boot', 'bad_ticket', 'expired_ticket', 'bad_goal',
         'other_control', 'queue_expired', 'owner_closed', 'short_tx', 'stm_err', 'ack_timeout')


def write_guide(path, changes):
    intro = (HERE / 'wifi_distance_core_guide_intro_ko.md').read_text(encoding='utf-8')
    text = intro
    for i, (name, label, old, new) in enumerate(changes, 1):
        text += f'\n## {i}. `{name}` — {label}\n\n'
        if len(old.splitlines()) < 8:
            text += '찾을 기존 구간:\n\n```c\n' + old.rstrip() + '\n```\n'
        else:
            text += '교체 시작: `' + old.splitlines()[0] + '`\n\n'
            if i == 2:
                text += '기존 정책 주석부터 `wifi_control_request_allows()` 닫는 중괄호까지 교체한다. 마지막 `#endif`는 유지한다.\n'
            else:
                text += '해당 함수의 선언부터 닫는 중괄호까지 전체 교체한다. 다음 함수는 유지한다.\n'
        text += '\n위 기존 구간을 삭제하고 아래 전체 블록으로 교체한다. 추가로 붙이지 않는다.\n\n```c\n'
        text += new.rstrip() + '\n```\n'
    text += '\n## 입력 후 확인\n\n3개 파일의5개 구간을 함께 저장한 뒤 `확인해`라고 알려준다. Codex가 실제 저장본과 `--saved` native 검사를 대조한다. 이 단계에서 ESP/STM 빌드·flash·구동은 진행하지 않는다. 다음 입력 묶음에서 브라우저 거리 선택·정지 대기·누르는 동안만 실행·완료 표시를 연결한다.\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--saved', action='store_true')
    ap.add_argument('--cc', required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--guide', type=Path)
    args = ap.parse_args()
    candidates, changes = ({}, []) if args.saved else prepare()
    assert not (args.saved and args.guide)
    production = {MAIN / n: (MAIN / n).read_bytes() for n in baseline.UNITS}
    selected = {p: candidates[p].encode('utf-8') if p in candidates else raw
                for p, raw in production.items()}
    fixture = HERE / 'wifi_distance_core_host_fixture.c'
    test_paths = [Path(__file__).resolve(), HERE / 'wifi_distance_core_candidate.py',
                  fixture, HERE / 'wifi_distance_core_guide_intro_ko.md',
                  HERE / 'test_wifi_nonzero_core.py', HERE / 'wifi_control_executor_host_fixture.c']
    report = {
        'mode': 'SAVED' if args.saved else 'CANDIDATE',
        'scope': __doc__, 'compiler': args.cc,
        'source_sha256': {str(p): hashlib.sha256(b).hexdigest() for p, b in production.items()},
        'selected_sha256': {str(p): hashlib.sha256(b).hexdigest() for p, b in selected.items()},
        'test_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in test_paths},
        'changes': [{'file': n, 'block': label} for n, label, _, _ in changes],
        'limitations': ['Native PC execution with mocked events, not ESP/STM build or UART/RTOS proof',
                        'Browser distance controls are not connected yet',
                        'STM owns goal latch, cutoff and final stop; ESP ACK is not measured distance completion'],
        'checks': [],
    }
    log = []

    def run(command):
        r = subprocess.run([str(x) for x in command], capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=45)
        log.append(r.stdout + r.stderr)
        assert r.returncode == 0, r.stdout + r.stderr
        return r.stdout

    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='wifi-distance-core-') as tmp:
            work = Path(tmp)
            selected_dir = work / 'selected'; selected_dir.mkdir()
            for p, raw in selected.items():
                (selected_dir / p.name).write_bytes(raw)
            # Reuse ordinary motion/zero-only regression against the selected C.
            regression = work / 'regression.json'
            with mock.patch.object(baseline, 'CANDIDATE', selected_dir), \
                 mock.patch.object(baseline, 'CHANGED', set(baseline.UNITS)), \
                 mock.patch.object(sys, 'argv', [baseline.__file__, '--cc', args.cc, '--output', str(regression)]):
                baseline.main()
            old = json.loads(regression.read_text(encoding='utf-8'))
            report['baseline'] = old
            log.append(regression.with_suffix('.txt').read_text(encoding='utf-8'))
            report['checks'].append('Ordinary parser/state/executor + mode 0/mode 1 regression PASS')
            for mode in (0, 1):
                dest = work / f'mode{mode}'; dest.mkdir()
                for p, raw in selected.items(): (dest / p.name).write_bytes(raw)
                header = dest / 'wifi_control_contract.h'
                text = header.read_text(encoding='utf-8')
                assert len(re.findall(r'^#define WIFI_CONTROL_ZERO_ONLY [01]U$', text, re.M)) == 1
                header.write_text(re.sub(r'^#define WIFI_CONTROL_ZERO_ONLY [01]U$',
                    f'#define WIFI_CONTROL_ZERO_ONLY {mode}U', text, flags=re.M), encoding='utf-8')
                for p in (fixture, HERE / 'wifi_control_executor_host_fixture.c'):
                    (dest / p.name).write_bytes(p.read_bytes())
                exe = dest / 'distance.exe'
                sources = [dest / p.name for p in production if p.suffix == '.c']
                command = [args.cc, '-Wall', '-Werror', '-I', dest, *sources, dest / fixture.name, '-o', exe]
                run(command)
                cases = CASES if mode == 0 else ('parsing', 'distance_policy', 'distance_rejected_zero_only')
                for case in cases:
                    assert run([exe, case]).strip() == 'PASS ' + case
                report['checks'].append(f'Mode {mode} distance vectors: {len(cases)} PASS')
                if mode == 0:
                    # Remove only the new suffix: exact-wire check must catch it.
                    path = dest / 'wifi_control_executor.c'
                    text = path.read_text(encoding='utf-8')
                    needle = '",distance_mm=%" PRIu32 "\\n",'
                    assert text.count(needle) == 1
                    path.write_text(text.replace(needle, '",ignored=%" PRIu32 "\\n",'), encoding='utf-8')
                    run(command)
                    r = subprocess.run([str(exe), 'distance_round_trip'], capture_output=True, timeout=5)
                    assert r.returncode != 0, 'distance suffix mutation escaped'
                    report['checks'].append('Wrong distance wire field negative control detected')
        report['status'] = 'PASS'
        if args.guide:
            write_guide(args.guide, changes)
            # Review copies are artifacts only; production files are untouched.
            folder = args.guide.parent / 'source'; folder.mkdir(exist_ok=True)
            for p, text in candidates.items(): (folder / p.name).write_text(text, encoding='utf-8')
    except Exception as exc:
        report['status'] = 'FAIL'
        report['error'] = str(exc)
        raise
    finally:
        for p, raw in production.items(): assert p.read_bytes() == raw, f'production changed: {p}'
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        args.output.with_suffix('.txt').write_text('\n'.join(log), encoding='utf-8')
    print(report['mode'] + ' PASS: ' + '; '.join(report['checks']))
    print('Firmware unchanged. ESP/browser integration and physical motion remain pending.')


if __name__ == '__main__':
    main()
