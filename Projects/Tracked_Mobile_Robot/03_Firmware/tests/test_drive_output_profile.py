"""Saved STM C on native PC with HAL mocks. No board build, flash or I/O."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from reproduce_uart_reconnect import HAL, STM

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    names = ('uart_mvp_protocol', 'uart_frame_parser', 'ring_buffer',
             'drive_command_mapper', 'motor_output')
    paths = [STM / folder / (name + ext) for name in names
             for folder, ext in (('Src', '.c'), ('Inc', '.h'))]
    fixture = HERE / 'drive_output_profile_host_fixture.c'
    inputs = {p: p.read_bytes() for p in [*paths, fixture]}
    source = inputs[STM / 'Src/uart_mvp_protocol.c'].decode('utf-8')
    flags = re.findall(r'^#define\s+UART_MVP_\w*TEST_ENABLED\s+(\d+)U', source, re.M)
    assert flags and all(flag == '0' for flag in flags), 'Expected normal STM image'
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
        with tempfile.TemporaryDirectory(prefix='drive-profile-') as tmp:
            work = Path(tmp)
            for path, raw in inputs.items():
                (work / path.name).write_bytes(raw)
            (work / 'main.h').write_text(hal, encoding='utf-8')
            program = work / 'profile.exe'
            commands = [[args.cc, '-Wall', '-Werror', '-I', str(work),
                         str(work / fixture.name),
                         *[str(work / (name + '.c')) for name in names[1:]],
                         '-o', str(program)], [str(program)]]
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                log.append(result.stdout + result.stderr)
                assert result.returncode == 0, log[-1]
    finally:
        assert all(path.read_bytes() == raw for path, raw in inputs.items()), 'Source changed'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix('.txt').write_text(''.join(log), encoding='utf-8')
    args.output.write_text(json.dumps({'status': 'PASS', 'scope': __doc__,
        'checks': ''.join(log).strip().splitlines(), 'firmware_unchanged': True,
        'inputs': {str(p): hashlib.sha256(raw).hexdigest() for p, raw in inputs.items()}},
        indent=2) + '\n', encoding='utf-8')
    print(''.join(log), end='')


if __name__ == '__main__':
    main()
