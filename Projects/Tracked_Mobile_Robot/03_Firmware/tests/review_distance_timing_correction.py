"""Review a correction to the 10/21 typed timing files in memory; no Core writes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from distance_timing_candidate import CORE, MAIN_SAMPLE, SNAPSHOT
import test_distance_timing_candidate as runner


def corrections():
    result = {}
    changes = []

    def edit(relative, before, after, label):
        p = CORE / relative
        text = result.get(p, p.read_text(encoding='utf-8'))
        assert text.count(before) == 1, label
        result[p] = text.replace(before, after, 1)
        changes.append((relative, label, before, after))

    edit('Inc/uart_mvp_protocol.h',
         'void uart_mvp_on_tx_complete(UART_HandelTypeDef *huart);',
         'void uart_mvp_on_tx_complete(UART_HandleTypeDef *huart);',
         'TX 완료 함수 선언 한 줄을 교체한다')
    enc = (CORE / 'Src/encoder_speed.c').read_text(encoding='utf-8')
    start = enc.index('bool encoder_speed_snapshot(')
    end = enc.index('bool encoder_speed_cps_to_millirpm(', start)
    edit('Src/encoder_speed.c', enc[start:end], SNAPSHOT,
         'encoder_speed_snapshot 정의 전체를 교체한다; 다음 encoder_speed_cps_to_millirpm 직전까지')
    edit('Src/main.c', '''static encoder_speed_t s_encoder_tim3;
static encoder_speed_t s_encoder_tim5;
static uint32_t s_encoder_last_publishh_ms;''', '''static encoder_speed_t s_encoder_tim3;
static encoder_speed_t s_encoder_tim5;
static uint32_t s_encoder_last_publish_ms;''', 'USER CODE PV의 엔코더 상태 선언 세 줄을 교체한다')
    main = result[CORE / 'Src/main.c']
    start = main.index('static int32_t encoder_cps_to_i32(')
    end = main.index('static void motor_output_pin_test_process(void){', start)
    edit('Src/main.c', main[start:end], MAIN_SAMPLE + '\n',
         '첫 번째 encoder_cps_to_i32부터 motor_output_pin_test_process 직전까지 모두 교체한다')
    return result, changes


def write_guide(path, changes):
    text = '''# 빠른 count와 비동기 UART 저장본 교정

현재 저장본은 구조 검사 FAIL이다. 아래4개 교정 블록을3개 파일에 함께 적용한다. 펌웨어는 자동 수정하지 않았다. 모든 교정을 적용한 메모리상의 후보는 `corrected_candidate.json`의 native 검사를 통과했다. 후보 PASS를 현재 저장본 PASS로 해석하지 않는다.

| 파일 | 발견한 문제 | 영향 |
| --- | --- | --- |
| encoder_speed.c | snapshot의 if 조건 닫는 괄호 하나 누락 | 컴파일 오류 |
| uart_mvp_protocol.h | UART_HandelTypeDef | HAL 타입명 오타로 컴파일 오류 |
| main.c | s_encoder_last_publishh_ms 선언 | 사용하는 변수명과 달라 컴파일 오류 |
| main.c | CPS 상한 비교가 cps < INT32_MAX | 정상 CPS도 INT32_MAX로 반환하는 논리 오류 |
| main.c | left_raw_coutn | 미선언 변수명으로 컴파일 오류 |
| main.c | 기존 helper·로그 함수가 아래쪽에 남음 | 두 함수 중복 정의, 옛 blocking 로그 잔존·삭제된 direction helper 참조 |

아래 코드는 지정 범위를 전체 교체하는 연결된 수정 묶음이다. main.c의 마지막 교체 범위에는 새로 입력한 잘못된 두 함수와 그 아래 남은 기존 두 함수가 **모두 포함**된다. 끝점인 `motor_output_pin_test_process`는 삭제하지 않는다. 그러면 두 함수가 각각 하나만 남고 반복 ENC3/ENC5 송신도 제거된다.

송신 큐·완료 callback·TX fault의 ARM/CMD 차단·초기화·RX 예산은 별도로 읽어 기존 안내와 대조했다. encoder_speed.h는 snapshot 선언이 올바르게 추가돼 있다. 이 부분을 다시 입력할 필요는 없다.

교정 후 입력·저장까지 마치고 저장본 검사를 다시 받는다. 현재 상태에서 보드 빌드/플래시/구동을 진행하지 않는다. 새 경로의 실제 IRQ 주기와 목표 거리/PWM 연결은 이후 단계다.
'''
    for i, (relative, label, before, after) in enumerate(changes, 1):
        text += f'\n## {i}. Core/{relative}\n\n{label}.\n'
        if len(before.splitlines()) <= 3:
            text += '\n찾을 기존 블록:\n\n```c\n' + before.rstrip() + '\n```\n'
        else:
            text += '\n교체 시작 줄: `' + before.splitlines()[0] + '`\n'
        text += '\n교체할 전체 코드:\n\n```c\n' + after.rstrip() + '\n```\n'
    text += '''
## PC 검사 범위

실제 입력본 검사는 `test_distance_timing_candidate.py --saved`이며, 현재는 중복 함수 구조 검사에서 중단했다. `saved_validation.json`과 `saved_failure.txt`에 이 결과를 남겼다. 교정 후보에는 같은 native 검사를 적용하여 snapshot/정수 경계·5ms count/100ms CPS·ARM 기준점·비동기 송신/버퍼·실패/포화 정지·기존 timeout/E-stop 회귀를 확인했다. PC 검사는 MCU build나 실물 정지 근거가 아니다.
'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--guide', type=Path, required=True)
    args = parser.parse_args()
    source, changes = corrections()
    # Run the same native fixture against temporary corrected source copies.
    runner.prepare = lambda: (source, [])
    sys.argv = [str(Path(runner.__file__)), '--cc', args.cc, '--output', str(args.output)]
    runner.main()
    report = json.loads(args.output.read_text(encoding='utf-8'))
    report['mode'] = 'CORRECTED_CANDIDATE'
    report['actual_saved_input_status'] = 'FAIL'
    report['corrections_applied_to_core'] = False
    report['correction_generator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    write_guide(args.guide, changes)


if __name__ == '__main__':
    main()
