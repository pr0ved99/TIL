"""Review/saved core checks in both modes, without modifying firmware inputs."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

TESTS = Path(__file__).resolve().parent
PROJECT = TESTS.parents[1]
MAIN = TESTS.parent / 'esp32_wifi_link/main'
CANDIDATE = PROJECT / 'assets/logs/wifi_link/2026-10-17_nonzero_core_candidate/source'
UNITS = ('wifi_control_contract.h', 'wifi_control_contract.c',
         'wifi_control_owner.h', 'wifi_control_owner.c',
         'wifi_control_ticket.h', 'wifi_control_ticket.c',
         'wifi_control_state.h', 'wifi_control_state.c',
         'wifi_control_executor.h', 'wifi_control_executor.c')
CHANGED = {'wifi_control_contract.h', 'wifi_control_state.c', 'wifi_control_executor.c'}
CASES = ('policy', 'first_motion_admission', 'first_motion_at_tx', 'round_trip',
         'queue_expired_motion', 'old_owner', 'ack_timeout', 'source_timeout',
         'owner_close', 'partial_motion_tx', 'bad_motion_tel', 'zero_command_pwm',
         'motion_cannot_confirm_stop')


def run(command):
    p = subprocess.run([str(x) for x in command], capture_output=True, text=True, timeout=45)
    if p.returncode:
        raise AssertionError('command failed:\n' + p.stdout + p.stderr)
    return p.stdout + p.stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved', action='store_true', help='test user-saved core, not review copies')
    parser.add_argument('--cc', help='native PC compiler; never an ESP/STM cross compiler')
    parser.add_argument('--output', type=Path, help='JSON evidence output')
    args = parser.parse_args()
    cc = args.cc or os.environ.get('WIFI_CONTROL_HOST_CC') or shutil.which('tcc') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('NOT RUN: pass --cc with a native PC compiler')
    selection = MAIN if args.saved else CANDIDATE
    inputs = {}
    for name in UNITS:
        path = selection / name if name in CHANGED else MAIN / name
        inputs[path] = path.read_bytes()
    fixture = TESTS / 'wifi_nonzero_core_host_fixture.c'
    fixture_inputs = {p: p.read_bytes() for p in (
        fixture, TESTS / 'wifi_control_executor_host_fixture.c',
        TESTS / 'wifi_control_state_host_fixture.c', TESTS / 'wifi_control_parser_host_fixture.c')}
    evidence = {'mode': 'SAVED CORE' if args.saved else 'CANDIDATE CORE',
                'scope': 'Native PC copies in both modes; legacy baseline forced to mode 1; no firmware build/flash or hardware acceptance',
                'compiler': cc,
                'inputs': {str(p): hashlib.sha256(raw).hexdigest() for p, raw in inputs.items()},
                'fixtures': {str(p): hashlib.sha256(raw).hexdigest() for p, raw in fixture_inputs.items()},
                'checks': []}
    transcript = io.StringIO()
    previous_cc = os.environ.get('WIFI_CONTROL_HOST_CC')
    guide_vars = ('WIFI_CONTROL_INPUT_GUIDE', 'WIFI_CONTROL_STATE_GUIDE', 'WIFI_CONTROL_EXECUTOR_GUIDE')
    previous_guides = {name: os.environ.pop(name, None) for name in guide_vars}
    os.environ['WIFI_CONTROL_HOST_CC'] = cc
    try:
        with tempfile.TemporaryDirectory(prefix='wifi-nonzero-core-') as tmp:
            work = Path(tmp)
            default = work / 'default'
            default.mkdir()
            for path, raw in inputs.items():
                (default / path.name).write_bytes(raw)
            for path, raw in fixture_inputs.items():
                (default / path.name).write_bytes(raw)
            header = (default / 'wifi_control_contract.h').read_text(encoding='utf-8')
            mode_pattern = r'^#define WIFI_CONTROL_ZERO_ONLY ([01])U$'
            modes = re.findall(mode_pattern, header, re.M)
            assert len(modes) == 1, 'expected one valid mode definition'
            input_mode = int(modes[0])
            evidence['input_zero_only'] = input_mode
            # The older regression suite intentionally expects zero-only policy.
            if input_mode != 1:
                (default / 'wifi_control_contract.h').write_text(re.sub(
                    mode_pattern, '#define WIFI_CONTROL_ZERO_ONLY 1U', header, flags=re.M), encoding='utf-8')
            with contextlib.redirect_stdout(transcript):
                for stem in ('parser', 'state', 'executor'):
                    path = TESTS / f'test_wifi_control_{stem}.py'
                    spec = importlib.util.spec_from_file_location('nonzero_baseline_' + stem, path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    module.MAIN = default
                    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
                    result = unittest.TextTestRunner(stream=transcript, verbosity=1).run(suite)
                    assert result.wasSuccessful() and not result.skipped, transcript.getvalue()
                    evidence['checks'].append({'name': f'baseline_mode_1_{stem}', 'passed': result.testsRun})
            for mode in (1, 0):
                dest = work / f'mode{mode}'
                dest.mkdir()
                for path in default.iterdir():
                    if path.is_file():
                        shutil.copyfile(path, dest / path.name)
                header_path = dest / 'wifi_control_contract.h'
                if mode == input_mode:
                    # Compile the selected configuration byte-for-byte as saved.
                    header_path.write_bytes(inputs[selection / 'wifi_control_contract.h'])
                else:
                    header_path.write_text(re.sub(mode_pattern,
                        f'#define WIFI_CONTROL_ZERO_ONLY {mode}U', header, flags=re.M), encoding='utf-8')
                program = dest / 'core.exe'
                sources = [dest / name for name in UNITS if name.endswith('.c')]
                transcript.write(run([cc, '-Wall', '-Werror', '-I', dest, *sources,
                                      dest / fixture.name, '-o', program]))
                cases = CASES if mode == 0 else ('policy', 'first_motion_admission', 'first_motion_at_tx')
                for case in cases:
                    output = run([program, case])
                    assert output.strip() == 'PASS ' + case, output
                    transcript.write(f'mode={mode} {output}')
                evidence['checks'].append({'name': f'mode_{mode}_new_vectors', 'passed': len(cases)})
            # Prove that the round-trip vector detects the original zero-value TX bug.
            broken = work / 'mode0'
            path = broken / 'wifi_control_executor.c'
            text = path.read_text(encoding='utf-8')
            assert text.count('seq, e->request.vx_mmps, e->request.w_mradps,') == 1
            path.write_text(text.replace('seq, e->request.vx_mmps, e->request.w_mradps,',
                                         'seq, (int32_t)0, (int32_t)0,'), encoding='utf-8')
            program = broken / 'mutated.exe'
            run([cc, '-Wall', '-Werror', '-I', broken,
                 *[broken / name for name in UNITS if name.endswith('.c')],
                 broken / fixture.name, '-o', program])
            p = subprocess.run([str(program), 'round_trip'], capture_output=True, text=True, timeout=5)
            assert p.returncode != 0, 'negative control failed: zero TX mutation escaped'
            evidence['checks'].append({'name': 'zero_tx_negative_control_detected', 'passed': 1})
    finally:
        if previous_cc is None:
            os.environ.pop('WIFI_CONTROL_HOST_CC', None)
        else:
            os.environ['WIFI_CONTROL_HOST_CC'] = previous_cc
        for name, value in previous_guides.items():
            if value is not None:
                os.environ[name] = value
        for path, raw in {**inputs, **fixture_inputs}.items():
            assert path.read_bytes() == raw, f'input changed: {path}'
    evidence['status'] = 'PASS'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
        args.output.with_suffix('.txt').write_text(transcript.getvalue(), encoding='utf-8')
    print(evidence['mode'] + ': ' + ', '.join(f"{v['name']}={v['passed']}" for v in evidence['checks']))
    print('PASS. Inputs unchanged; board build/flash and actual UART/PWM remain unverified.')


if __name__ == '__main__':
    main()
