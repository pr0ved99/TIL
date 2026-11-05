"""Run candidate/saved STM timing C with a simulated UART, encoder and PWM."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from distance_timing_candidate import CORE, HERE, prepare
from reproduce_uart_reconnect import HAL

EXTRA_NAMES = ()
EXTRA_INPUTS = ()
FIXTURE_TAIL = ''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--saved', action='store_true')
    parser.add_argument('--guide', type=Path)
    args = parser.parse_args()
    candidates, changes = ({}, []) if args.saved else prepare()
    names = ('uart_mvp_protocol', 'uart_frame_parser', 'ring_buffer',
             'drive_command_mapper', 'motor_output', 'encoder_speed') + EXTRA_NAMES
    paths = [CORE / folder / (name + ext) for name in names
             for folder, ext in (('Src', '.c'), ('Inc', '.h'))]
    paths += [CORE / 'Src/main.c', HERE / 'distance_timing_candidate.py',
              HERE / 'drive_output_profile_host_fixture.c',
              HERE / 'distance_timing_guide_intro_ko.md',
              HERE / 'distance_timing_host_fixture.c', Path(__file__).resolve()]
    paths += list(EXTRA_INPUTS)
    inputs = {p: p.read_bytes() for p in paths}
    output = args.output.resolve()
    assert output not in {p.resolve() for p in paths}
    if args.guide:
        assert not args.saved and args.guide.resolve() not in {p.resolve() for p in paths}
        assert args.guide.resolve() != output
    source = lambda p: candidates.get(p, inputs[p].decode('utf-8'))
    main_src = source(CORE / 'Src/main.c')
    assert len(re.findall(r'static\s+int32_t\s+encoder_cps_to_i32\s*\(', main_src)) == 1, \
        'encoder_cps_to_i32 must have exactly one definition'
    assert len(re.findall(r'static\s+void\s+encoder_speed_log_process\s*\(', main_src)) == 1, \
        'encoder_speed_log_process must have exactly one definition'
    start = main_src.index('static int32_t encoder_cps_to_i32(')
    end = main_src.index('static void motor_output_pin_test_process(void){', start)
    sample_functions = main_src[start:end]
    assert 'HAL_UART_Transmit' not in sample_functions
    assert re.search(r'^#define\s+ENCODER_SPEED_SAMPLE_PERIOD_MS\s+100U\s*$', main_src, re.M)
    assert re.search(r'^#define\s+ENCODER_COUNT_SAMPLE_PERIOD_MS\s+5U\s*$', main_src, re.M)
    assert main_src.count('void HAL_UART_TxCpltCallback(') == 1
    assert 'static uint32_t s_encoder_last_publish_ms;' in main_src
    assert re.search(r'void HAL_UART_TxCpltCallback\([^)]*\)\s*\{\s*'
                     r'uart_mvp_on_tx_complete\(huart\);\s*\}', main_src)
    protocol = source(CORE / 'Src/uart_mvp_protocol.c')
    assert 'static volatile uint8_t s_tx_completed;' in protocol
    assert 'static volatile uint8_t s_tx_active;' in protocol
    assert protocol.count('HAL_UART_Transmit_IT(') == 1
    flags = re.findall(r'^#define\s+UART_MVP_\w*TEST_ENABLED\s+(\d+)U', protocol, re.M)
    assert flags and all(value == '0' for value in flags)
    baseline = inputs[HERE / 'drive_output_profile_host_fixture.c'].decode('utf-8')
    baseline = baseline.replace('int main(void)', 'static int profile_main(void)', 1)
    baseline = baseline.replace('static uint32_t host_ms;',
                                'static uint32_t host_ms;\nstatic unsigned host_blocking_calls;')
    baseline = baseline.replace('(void)uart; (void)timeout;',
                                '(void)uart; (void)timeout; host_blocking_calls++;', 1)
    extra = inputs[HERE / 'distance_timing_host_fixture.c'].decode('utf-8')
    if FIXTURE_TAIL:
        extra = extra.replace('int main(void)', 'static int timing_main(void)', 1)
        extra += '\n' + FIXTURE_TAIL
    extra = extra.replace('static unsigned host_blocking_calls;\n', '', 1)
    fixture = baseline + '\n' + extra.replace('/* INSERT_MAIN_SAMPLE */', sample_functions)
    hal = HAL.replace('typedef struct { int unused; } TIM_HandleTypeDef;',
        'typedef struct { void *Instance; uint32_t arr; uint32_t compare[2]; } TIM_HandleTypeDef;')
    hal = hal.replace('typedef enum { HAL_OK, HAL_ERROR }',
                      'typedef enum { HAL_OK, HAL_ERROR, HAL_BUSY }')
    hal = hal.replace('#endif', '''
#define TIM4 ((void *)4)
#define TIM_CHANNEL_1 0
#define TIM_CHANNEL_2 1
#define MOTOR_LEFT_DIR_GPIO_Port ((void *)0)
#define MOTOR_RIGHT_DIR_GPIO_Port ((void *)0)
#define MOTOR_LEFT_DIR_Pin 8
#define MOTOR_RIGHT_DIR_Pin 9
#define __HAL_TIM_GET_AUTORELOAD(t) ((t)->arr)
#define __HAL_TIM_SET_COMPARE(t,c,v) ((t)->compare[c]=(v))
void HAL_Delay(uint32_t);
void HAL_GPIO_WritePin(void *, uint16_t, GPIO_PinState);
HAL_StatusTypeDef HAL_TIM_PWM_Start(TIM_HandleTypeDef *, uint32_t);
HAL_StatusTypeDef HAL_TIM_PWM_Stop(TIM_HandleTypeDef *, uint32_t);
HAL_StatusTypeDef HAL_UART_Transmit_IT(UART_HandleTypeDef *, const uint8_t *, uint16_t);
#endif
''')
    logs = []
    try:
        with tempfile.TemporaryDirectory(prefix='distance-timing-pc-') as temp:
            work = Path(temp)
            for p in paths[:len(names) * 2]:
                (work / p.name).write_text(source(p), encoding='utf-8')
            (work / 'main.h').write_text(hal, encoding='utf-8')
            (work / 'fixture.c').write_text(fixture, encoding='utf-8')
            exe = work / 'timing.exe'
            commands = [[args.cc, '-Wall', '-Werror', '-I', str(work),
                         str(work / 'fixture.c'),
                         *[str(work / (name + '.c')) for name in names[1:]],
                         '-o', str(exe)], [str(exe)]]
            for cmd in commands:
                r = subprocess.run(cmd, capture_output=True, text=True,
                                   encoding='utf-8', errors='replace', timeout=30)
                logs.append(r.stdout + r.stderr)
                if r.returncode:
                    raise RuntimeError(f'{r.returncode}: {logs[-1]}')
    finally:
        assert all(p.read_bytes() == raw for p, raw in inputs.items()), 'Input changed'
    report = dict(status='PASS', mode='SAVED' if args.saved else 'CANDIDATE',
        scope=__doc__, checks=''.join(logs).strip().splitlines(),
        production_sources_unchanged_by_runner=True, compiler=args.cc,
        inputs={str(p.relative_to(HERE.parents[1])): hashlib.sha256(raw).hexdigest()
                for p, raw in inputs.items()},
        candidate_hashes={str(p.relative_to(CORE)): hashlib.sha256(t.encode()).hexdigest()
                          for p,t in candidates.items()},
        limitations=['Host mock does not prove ISR latency, throughput or electrical behavior',
                     'Actual distance command, PWM gating and ESP UI remain to be integrated',
                     'Old blocking host fixtures need an asynchronous HAL adapter for this path'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if args.guide:
        write_guide(args.guide, changes)
    print('\n'.join(report['checks']))


def write_guide(path, changes):
    intro = (HERE / 'distance_timing_guide_intro_ko.md').read_text(encoding='utf-8')
    parts = [intro]
    for i, (relative, label, old, new) in enumerate(changes, 1):
        parts.append(f'\n## {i}. {relative}\n\n{label}.\n')
        if relative in ('Inc/encoder_speed.h', 'Src/encoder_speed.c'):
            parts.append('\n`'+old+'`로 시작하는 기존 선언/정의 바로 앞에 '
                         '다음 전체 블록을 삽입한다. 기존 선언/정의는 유지한다.\n')
            assert new.endswith(old)
            parts.append('\n```c\n'+new[:-len(old)].rstrip()+'\n```\n')
            continue
        if relative.startswith('Inc/') or (len(old.splitlines()) <= 3):
            parts.append('\n찾을 기존 코드:\n\n```c\n'+old.rstrip()+'\n```\n')
        else:
            lines=old.rstrip().splitlines()
            parts.append('\n교체 시작: `'+lines[0]+'`\n\n교체 끝: 위 블록의 마지막 `'+lines[-1]+'`까지.\n')
        parts.append('\n입력할 전체 블록:\n\n```c\n'+new.rstrip()+'\n```\n')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(parts), encoding='utf-8')


if __name__ == '__main__':
    main()
