"""Review proposed/saved STM C on native PC only; no board build or I/O."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from encoder_count_candidate import CORE, PUBLISH, between, guide, prepare
from reproduce_uart_reconnect import HAL

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--saved', action='store_true')
    parser.add_argument('--guide', type=Path, help='Optional typing-guide destination')
    args = parser.parse_args()
    names = ('uart_mvp_protocol', 'uart_frame_parser', 'ring_buffer',
             'drive_command_mapper', 'motor_output')
    paths = [CORE / folder / (name + ext) for name in names
             for folder, ext in (('Src', '.c'), ('Inc', '.h'))]
    main_path = CORE / 'Src/main.c'
    support = [HERE / name for name in ('drive_output_profile_host_fixture.c',
        'encoder_count_host_fixture.c', 'encoder_count_candidate.py')]
    inputs = {p: p.read_bytes() for p in [*paths, main_path, *support]}
    candidate = {} if args.saved else prepare()
    source = candidate.get(CORE / 'Src/uart_mvp_protocol.c',
        inputs[CORE / 'Src/uart_mvp_protocol.c'].decode('utf-8'))
    main_source = candidate.get(main_path, inputs[main_path].decode('utf-8'))
    header = candidate.get(CORE / 'Inc/uart_mvp_protocol.h',
        inputs[CORE / 'Inc/uart_mvp_protocol.h'].decode('utf-8'))
    assert 'uart_mvp_set_encoder_cps' not in source + main_source + header
    assert all(text.count('uart_mvp_set_encoder_sample(') == 1
               for text in (source, main_source, header))
    flags = re.findall(r'^#define\s+UART_MVP_\w*TEST_ENABLED\s+(\d+)U', source, re.M)
    assert flags and all(x == '0' for x in flags)
    publish_start = main_source.index('  /* Vehicle-forward count uses the same sign')
    publish_end = re.search(r'^\s*len\s*=\s*snprintf\s*\(',
        main_source[publish_start:], re.M)
    assert publish_end is not None, 'encoder diagnostic snprintf missing'
    sample = main_source[publish_start:publish_start + publish_end.start()].rstrip()
    cps = between(main_source, 'static int32_t encoder_cps_to_i32(', '\nstatic void encoder_speed_log_process(')
    baseline = inputs[HERE / 'drive_output_profile_host_fixture.c'].decode('utf-8')
    baseline = baseline.replace('int main(void)', 'static int profile_main(void)', 1)
    fixture = baseline + '\n' + '''
typedef struct { int64_t accumulated_count, counts_per_second; } host_encoder_t;
static host_encoder_t s_encoder_tim3, s_encoder_tim5;
''' + cps + '\nstatic void host_publish_sample(uint32_t now_ms) {\n' + sample + '\n}\n'
    fixture += inputs[HERE / 'encoder_count_host_fixture.c'].decode('utf-8')
    hal = HAL.replace('typedef struct { int unused; } TIM_HandleTypeDef;',
        'typedef struct { void *Instance; uint32_t arr; uint32_t compare[2]; } TIM_HandleTypeDef;')
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
#endif
''')
    log = []
    try:
        with tempfile.TemporaryDirectory(prefix='encoder-count-pc-') as tmp:
            work = Path(tmp)
            for p in paths:
                (work / p.name).write_text(candidate.get(p, inputs[p].decode('utf-8')), encoding='utf-8')
            (work / 'main.h').write_text(hal, encoding='utf-8')
            (work / 'fixture.c').write_text(fixture, encoding='utf-8')
            program = work / 'encoder.exe'
            commands = [[args.cc, '-Wall', '-Werror', '-I', str(work), str(work / 'fixture.c'),
                *[str(work / (name + '.c')) for name in names[1:]], '-o', str(program)], [str(program)]]
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
                log.append(result.stdout + result.stderr)
                assert result.returncode == 0, log[-1]
    finally:
        assert all(p.read_bytes() == raw for p, raw in inputs.items()), 'An input file changed'
    fields = [('t_ms','4294967295'), ('state','DISARMED'), ('reason','R'*31),
        ('command_age_ms','4294967295'), ('last_seq','4294967295'),
        *[(k,'-2147483648') for k in ('vx_mmps','w_mradps')],
        *[(k,'-1000') for k in ('left_pwm','right_pwm')],
        *[(k,'-2147483648') for k in ('left_cps','right_cps')],
        ('encoder_valid','1'), ('encoder_t_ms','4294967295'),
        *[(k,'-9223372036854775808') for k in ('left_count','right_count')],
        ('encoder_arm_valid','1'), ('encoder_arm_seq','4294967295'),
        ('batt_mv','0'), ('drop','4294967295'), ('err','4294967295')]
    wire = 'TEL,' + ','.join(k+'='+v for k,v in fields) + '\n'
    assert len(fields) == 20 and len(wire)+1 <= 512
    report = {'status':'PASS', 'mode':'SAVED' if args.saved else 'CANDIDATE',
        'scope':__doc__, 'compiler':args.cc, 'firmware_unchanged':True,
        'checks': ''.join(log).strip().splitlines(), 'wire_bound_bytes_including_lf':len(wire),
        'buffer_bound_including_nul':len(wire)+1, 'uart_8n1_115200_bound_ms':len(wire)*10/115200*1000,
        'inputs':{str(p):hashlib.sha256(raw).hexdigest() for p,raw in inputs.items()},
        'candidate_hashes':{str(p):hashlib.sha256(text.encode('utf-8')).hexdigest() for p,text in candidate.items()}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if args.guide:
        assert not args.saved
        args.guide.write_text(guide(), encoding='utf-8')
    print('\n'.join(report['checks']))
    print('PASS wire bound:', report['buffer_bound_including_nul'], 'bytes including NUL')


if __name__ == '__main__':
    main()
