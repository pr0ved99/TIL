"""Prepare STM encoder telemetry typing blocks without editing firmware."""
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent / "stm32_uart_mvp/Core"
HEADER = """#ifndef UART_MVP_PROTOCOL_H
#define UART_MVP_PROTOCOL_H

#include "main.h"
#include <stdbool.h>
#include <stdint.h>

void uart_mvp_init(UART_HandleTypeDef *huart);
void uart_mvp_start_rx(void);
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart);
void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);
void uart_mvp_set_encoder_sample(
    int32_t left_cps,
    int32_t right_cps,
    int64_t left_count,
    int64_t right_count,
    uint32_t sample_ms,
    bool valid
);
void uart_mvp_process(void);

#endif // UART_MVP_PROTOCOL_H
"""

STATE = """static int32_t s_left_cps;
static int32_t s_right_cps;

typedef struct {
    int64_t left_count;
    int64_t right_count;
    uint32_t sample_ms;
    uint32_t arm_seq;
    bool valid;
    bool arm_valid;
} encoder_sample_t;

static encoder_sample_t s_encoder_sample;
static uint32_t s_encoder_arm_seq;
static bool s_encoder_arm_valid;"""

SETTER = """void uart_mvp_set_encoder_sample(
    int32_t left_cps,
    int32_t right_cps,
    int64_t left_count,
    int64_t right_count,
    uint32_t sample_ms,
    bool valid
){
    /* Both paths run in the main loop, not in the UART RX interrupt. */
    s_left_cps = left_cps;
    s_right_cps = right_cps;

    s_encoder_sample = (encoder_sample_t){
        .left_count = valid ? left_count : 0,
        .right_count = valid ? right_count : 0,
        .sample_ms = sample_ms,
        .arm_seq = s_encoder_arm_valid ? s_encoder_arm_seq : 0U,
        .valid = valid,
        .arm_valid = s_encoder_arm_valid
    };
}"""

PUBLISH = """  /* Vehicle-forward count uses the same sign as production CPS. */
  const bool encoder_sample_valid =
    s_encoder_tim3.accumulated_count != INT64_MIN;

  uart_mvp_set_encoder_sample(
    encoder_cps_to_i32(-s_encoder_tim3.counts_per_second),
    encoder_cps_to_i32(s_encoder_tim5.counts_per_second),
    encoder_sample_valid ? -s_encoder_tim3.accumulated_count : 0,
    s_encoder_tim5.accumulated_count,
    now_ms,
    encoder_sample_valid
  );"""


def between(text, start, end):
    a = text.index(start)
    b = text.index(end, a)
    return text[a:b].rstrip()


def changes():
    """Each entry is one exact, reviewable block in the user's saved source."""
    header = CORE / "Inc/uart_mvp_protocol.h"
    protocol = CORE / "Src/uart_mvp_protocol.c"
    main = CORE / "Src/main.c"
    p = protocol.read_text(encoding="utf-8")
    m = main.read_text(encoding="utf-8")
    old_tel = between(p, "static void send_tel(void){", "\nstatic const char *parse_error_code(")
    tel = old_tel.replace(
        '               "batt_mv=0,drop=%lu,err=%lu\\n",',
        '               "encoder_valid=%u,encoder_t_ms=%lu,"\n'
        '               "left_count=%" PRId64 ",right_count=%" PRId64 ","\n'
        '               "encoder_arm_valid=%u,encoder_arm_seq=%lu,"\n'
        '               "batt_mv=0,drop=%lu,err=%lu\\n",')
    tel = tel.replace("                (long)s_right_cps,", """                (long)s_right_cps,
                s_encoder_sample.valid ? 1U : 0U,
                (unsigned long)s_encoder_sample.sample_ms,
                s_encoder_sample.left_count,
                s_encoder_sample.right_count,
                s_encoder_sample.arm_valid ? 1U : 0U,
                (unsigned long)s_encoder_sample.arm_seq,"""
    )
    old_arm = between(p, "        case UART_FRAME_TYPE_ARM:", "\n        case UART_FRAME_TYPE_ESTOP_RESET:")
    arm = old_arm.replace('            send_ack(frame.seq, "ARM");', """            /* New measurement interval; wait for a post-ARM sample. */
            s_encoder_arm_seq = frame.seq;
            s_encoder_arm_valid = true;
            s_encoder_sample.valid = false;
            s_encoder_sample.arm_valid = false;
            s_encoder_sample.arm_seq = 0U;
            send_ack(frame.seq, "ARM");"""
    )
    old_init = between(p, "void uart_mvp_init(UART_HandleTypeDef *huart){", "\nvoid uart_mvp_set_encoder_cps(")
    init = old_init.replace("    s_right_cps = 0;", """    s_right_cps = 0;
    s_encoder_sample = (encoder_sample_t){0};
    s_encoder_arm_seq = 0U;
    s_encoder_arm_valid = false;"""
    )
    old_setter = between(p, "void uart_mvp_set_encoder_cps(", "\nvoid uart_mvp_start_rx(")
    old_main = between(m, "static void encoder_speed_log_process(void){", "\nstatic void motor_output_pin_test_process(")
    old_publish = between(old_main, "  uart_mvp_set_encoder_cps(", "\n\n  len = snprintf(")
    new_main = old_main.replace(old_publish, PUBLISH)
    return [
        (header, "1. uart_mvp_protocol.h 전체", header.read_text(encoding="utf-8").rstrip(), HEADER.rstrip()),
        (protocol, "2. 표준 헤더 두 줄", "#include <stdarg.h>\n#include <stdio.h>", "#include <inttypes.h>\n#include <stdarg.h>\n#include <stdio.h>"),
        (protocol, "3. STM TX 버퍼 정의", "#define UART_TX_BUFFER_SIZE             384u", "#define UART_TX_BUFFER_SIZE             512u"),
        (protocol, "4. CPS 상태 두 줄과 sample 상태", "static int32_t s_left_cps;\nstatic int32_t s_right_cps;", STATE),
        (protocol, "5. send_tel() 전체", old_tel, tel),
        (protocol, "6. ARM case 전체: 다음 ESTOP_RESET case 직전까지", old_arm, arm),
        (protocol, "7. uart_mvp_init() 전체", old_init, init),
        (protocol, "8. 기존 uart_mvp_set_encoder_cps() 전체", old_setter, SETTER),
        (main, "9. encoder_speed_log_process() 전체", old_main, new_main),
    ]


def prepare():
    result = {}
    for path, label, old, new in changes():
        source = result.get(path, path.read_text(encoding="utf-8"))
        if source.count(old) != 1 or old == new:
            raise ValueError("Replacement anchor changed: " + label)
        result[path] = source.replace(old, new, 1)
    return result


def guide():
    lines = ["### STM 누적 count 입력 묶음 — 2026-10-19", "",
        "상태: **입력 대기 / 후보 PC 검사 대상**. 아래 블록은 사용자가 입력한다. 실제 STM/ESP 저장 소스·보드 이미지는 아직 바뀌지 않았다.", "",
        "목적은 기존 encoder 갱신의 차량 기준 count/CPS/시각을 같은 main-loop 샘플로 보관하고 확장 TEL로 내보내는 것이다. 현재 ESP14필드 parser는 새 TEL20필드를 거부하므로 **지금은 저장까지 진행하고 두 보드 빌드/플래시는 ESP 변경과 저장본 PC 검사가 끝난 뒤** 진행한다.", "",
        "- 부팅: sample/ARM 유효성 false. 첫 encoder 갱신 뒤 sample은 유효하지만 ARM 구간은 아직 없음.",
        "- ARM 성공: UART seq를 구간 기준으로 보관하고 이전 sample을 무효화. 다음 encoder 갱신부터 새 ARM seq와 count를 연결. ARM이 count를0으로 리셋하지 않음.",
        "- DISARM/timeout/FAULT: 제어의 기존 정지 동작을 유지하고 마지막 ARM 기준/count는 정지 후 샘플에도 보존. FAULT 또는 관측 단절이 낀 구간은 거리 수용에서 제외.",
        "- STM 재시작: sample/ARM 유효성 초기화. 새 ARM은 현재 ESP 단일 UART allocator가 재사용하지 않는 seq를 받음. 거리 구간은 `(ESP boot_id, encoder_arm_seq)`가 같고 ACK된 ARM seq와 일치해야 한다. 이 값은 전역 STM boot ID나 보안 nonce가 아니다.",
        "- 원시 count가 감소하는 것은 후진일 수 있으므로 reset 판정으로 사용하지 않음. 측정 시각 역행/wrap 또는 통신 단절은 구간을 종료하고 사용자 새 기준점부터 측정. 원시 로그는 보존.",
        "- TIM3 raw count가 INT64_MIN이면 부호 반전할 수 없어 sample.valid=false로 전달. CPS는 기존 제어 경로에 계속 갱신. 이 방어는 기존 int64 누적기 자체의 영구 overflow 문제를 해결하지 않음.", "",
        "아래 번호 순서로 교체한다. 같은 이름의 호출부 대신 **선언 / 함수 정의 / switch case**를 구분한다. 함수/case는 아래 완결 블록 전체를 사용한다.", ""]
    for path, label, old, new in changes():
        lines += [f"**{label}** — `{path.relative_to(CORE).as_posix()}`", "",
            "기존 범위: `" + old.splitlines()[0] + "`부터 해당 블록 끝까지.", "", "```c", new, "```", ""]
    lines += ["입력 후 확인 기준: 이전 setter 이름0건, 새 setter 선언/정의/호출 각1건, 새 TEL20필드·개행/버퍼 여유, 초기/ARM後/DISARM/reset 구간과 실제 제어 회귀 PC 검사. ESP의 i64 parser·JSON 문자열·유효성/ACK 연계·관찰 로그는 다음 입력 묶음이다. native HAL 모의 결과는 보드 실행 근거가 아니다.", ""]
    return "\n".join(lines)
