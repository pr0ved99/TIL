# STM CMD ACK 한 번 유실 시험 입력 가이드

UR-03 / AC-S04의 **정상 TEL이 계속되는 동안 CMD ACK 하나만 유실되는 경우**를 확인한다.
기존 늦은 DISARM ACK와 만료 ARM ticket 시험을 반복하지 않는다.
이번에는 수동 ARM 후 정상 zero CMD를 처리하다가 10번째 조건 충족 CMD의 ACK만 생략한다.
ESP가 TEL만으로 성공 처리하지 않고 ACK timeout으로 제어 허가를 취소한 뒤 정지하는 것이 목표다.

현재 단계는 **후보 코드 PC 검사 완료, 사용자 입력 전**이다.
실제 STM/ESP 보드 빌드·플래시와 캡처는 아직 수행하지 않았다.
PC 검사는 실제 STM protocol/parser/mapper와 ESP executor/state를 사용하지만 시간·UART·GPIO·모터는 모의 환경이다.

## 지금 입력할 범위

대상은 [uart_mvp_protocol.c](../../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c) 한 파일이다.
아래 **1~5의 완전한 교체 블록**을 순서대로 입력하고 저장한다.
현재 저장본 기준 위치이며, 앞 블록을 넣으면 뒤쪽 줄 번호는 바뀐다. 함수명과 원문 시작·끝을 기준으로 찾는다.
새 `UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED` 값은 **0U로 저장**한다.
Codex가 실제 저장본을 다시 검사한 뒤 시험 활성화와 빌드를 안내한다.
ESP는 `WIFI_UART_PARTIAL_TEST_MODE 0U`, 다른 STM 시험 스위치는 모두 0U를 유지한다.

## 상태와 데이터 흐름

```text
STM 부팅: used=0, count=0
수동 ARM: count=0, ARM ACK 정상
조건 충족 zero CMD 1~9: 기존 명령 처리 → ACK 정상
10번째: 기존 명령 처리·last_seq/watchdog 갱신 → used=1 → TEST_CMD_ACK_DROP 표식 → ACK 생략
TEL: 계속 ARMED/zero와 10번째 seq를 전달
ESP: ACK 대기 150ms 만료 → TIMEOUT → owner/ticket/대기 입력 취소 → CAN+LF+DISARM
STM: 즉시 DISARM 처리 → ACK 정상 → 새 DISARMED/zero TEL
ESP: 정지 확인 후 IDLE, 자동 ARM/CMD 없음
```

`s_cmd_ack_drop_used`는 부팅당 한 번만 ACK를 생략하도록 한다. ARM 때는 이 값을 지우지 않는다.
`s_cmd_ack_drop_zero_count`는 현재 ARM 이후 조건을 만족한 zero CMD 개수다.
새 ARM 때 0으로 초기화하고, 수락된 CMD의 속도·적용 PWM·CPS 또는 안전 조건이 맞지 않으면 0으로 돌린다.
형식·범위·FAULT 검사에서 거부된 CMD는 이 함수까지 오지 않으므로 계수하지 않는다.

`handle_cmd()`의 기존 검증과 모터 처리, 명령 시간 갱신 뒤 ACK 직전에만 hook을 둔다.
명령 자체를 버리면 TEL의 마지막 seq도 바뀌지 않아 다른 시험이 된다.
ACK만 생략하면 **STM은 명령을 처리했지만 ESP는 응답을 받지 못한 경우**를 만들 수 있다.
10번째를 선택한 이유는 첫 zero ACK/TEL로 ACTIVE에 들어간 뒤 약 1초의 정상 송신을 먼저 관찰하기 위해서다.
실제 도달 시간은 브라우저·무선 지연에 따라 달라진다.

HAL 지연이나 UART 전체 단절을 사용하지 않는다. TEL과 DISARM 응답을 유지해 ACK 유실의 영향을 구분한다.
생략한 ACK를 나중에 송신하는 큐도 없다. 이후 CMD, ARM, PING, DISARM 응답은 정상 경로를 따른다.
기존 STM 300ms watchdog, E-stop latch, CAN 줄 폐기와 ESP의 ACK/TEL 확인 기준은 유지한다.
동시에 다른 fault/output 시험을 켜면 전처리 오류로 빌드를 막는다.

### 1. 시험 설정과 중복 주입 방지

현재 저장본 67~68행. 아래 원문 범위를 새 블록 전체로 교체한다.

기존 범위:

```c
typedef enum{
    ROBOT_DISARMED = 0,
```

새 블록:

```c
/* Bench only: omit the tenth eligible zero CMD ACK once per STM boot. */
#define UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED 0U

#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED > 1U
#error "CMD ACK drop test mode must be 0 or 1"
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED && ( \
    UART_MVP_OUTPUT_TEST_ENABLED || \
    UART_MVP_STALE_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED || \
    UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED || \
    UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED || \
    UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_EMBEDDED_CR_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_CONTROL_BYTE_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_OVERLONG_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_STALE_PONG_ONCE_TEST_ENABLED || \
    UART_MVP_SUPPRESS_PONG_TEST_ENABLED || \
    UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED)
#error "Do not combine CMD ACK drop with another bench fault/output mode"
#endif

typedef enum{
    ROBOT_DISARMED = 0,
```

### 2. 부팅당 사용 여부와 zero CMD 개수

현재 저장본 123~123행. 아래 원문 범위를 새 블록 전체로 교체한다.

기존 범위:

```c
static int32_t s_right_cps;
```

새 블록:

```c
static int32_t s_right_cps;

#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
static uint8_t s_cmd_ack_drop_used;
static uint8_t s_cmd_ack_drop_zero_count;
#endif
```

### 3. ACK 생략 함수와 handle_cmd 전체

현재 저장본 334~427행. 아래 원문 범위를 새 블록 전체로 교체한다.

시작: `static void handle_cmd(const uart_frame_t *frame){`

끝: `handle_cmd()`의 닫는 `}`까지. 뒤의 기존 `delayed_disarm_ack_eligible()` 함수는 포함하지 않는다.

새 블록:

```c
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
static uint8_t drop_cmd_ack_once(uint32_t seq)
{
    const motor_output_applied_t applied = motor_output_get_applied();
    if (s_cmd_ack_drop_used != 0U) {
        return 0U;
    }
    if (s_state != ROBOT_ARMED || s_estop_latched != 0U ||
        estop_input_active() != 0U || s_vx_mmps != 0 || s_w_mradps != 0 ||
        applied.left_signed_permille != 0 || applied.right_signed_permille != 0 ||
        s_left_cps != 0 || s_right_cps != 0) {
        s_cmd_ack_drop_zero_count = 0U;
        return 0U;
    }
    if (++s_cmd_ack_drop_zero_count < 10U) {
        return 0U;
    }
    s_cmd_ack_drop_used = 1U;
    uart_sendf("TEST_CMD_ACK_DROP,seq=%lu,t_ms=%lu,zero_count=%lu\n",
        (unsigned long)seq,
        (unsigned long)HAL_GetTick(),
        (unsigned long)s_cmd_ack_drop_zero_count);
    return 1U;
}
#endif

static void handle_cmd(const uart_frame_t *frame){
    drive_command_request_t request;
    if(frame->vx_mmps < VX_MIN_MMPS || frame->vx_mmps > VX_MAX_MMPS ||
       frame->w_mradps < W_MIN_MRADPS || frame->w_mradps > W_MAX_MRADPS){
        send_err(frame->seq, "CMD", "OUT_OF_RANGE");
        return;
    }

    if(frame->timeout_ms < CMD_TIMEOUT_MIN_MS ||
       frame->timeout_ms > CMD_TIMEOUT_MAX_MS){
        send_err(frame->seq, "CMD", "TIMEOUT_OUT_OF_RANGE");
        return;
    }

    if(s_state != ROBOT_ARMED){
        send_err(frame->seq, "CMD", "NOT_ARMED");
        return;
    }

    if (estop_enforce_latch() != 0U) {
        send_err(frame->seq, "CMD", "ESTOP_LATCHED");
        return;
    }

    if(!drive_command_map(
        frame->vx_mmps,
        frame->w_mradps,
        CMD_OUTPUT_DUTY_CAP_PERMILLE,
        &request
    )){
        motor_output_stop_all();
        s_vx_mmps = 0;
        s_w_mradps = 0;
        s_reason = ROBOT_REASON_OUTPUT_ERROR;
        send_err(frame->seq, "CMD", "MAPPER_FAILED");
        return;
    }

    if (estop_enforce_latch() != 0U) {
        send_err(frame->seq, "CMD", "ESTOP_LATCHED");
        return;
    }

    if(UART_MVP_OUTPUT_TEST_ENABLED != 0U){
        if((frame->vx_mmps == 50) && (frame->w_mradps == 0)){
            if(motor_output_set_raw(
                UART_MVP_OUTPUT_TEST_DUTY_PERMILLE,
                GPIO_PIN_RESET,
                UART_MVP_OUTPUT_TEST_DUTY_PERMILLE,
                GPIO_PIN_RESET
            ) != HAL_OK){
                motor_output_stop_all();
                s_vx_mmps = 0;
                s_w_mradps = 0;
                s_reason = ROBOT_REASON_OUTPUT_ERROR;
                send_err(frame->seq, "CMD", "MOTOR_OUTPUT_FAILED");
                return;
            }
        }
        else{
            motor_output_stop_all();
        }
    }
    else if(motor_output_set_signed(
        request.left_signed_permille,
        request.right_signed_permille
    ) != HAL_OK){
        motor_output_stop_all();
        s_vx_mmps = 0;
        s_w_mradps = 0;
        s_reason = ROBOT_REASON_OUTPUT_ERROR;
        send_err(frame->seq, "CMD", "MOTOR_OUTPUT_FAILED");
        return;
    }

    if (estop_enforce_latch() != 0U) {
        send_err(frame->seq, "CMD", "ESTOP_LATCHED");
        return;
    }
    s_last_seq = frame->seq;
    s_vx_mmps = frame->vx_mmps;
    s_w_mradps = frame->w_mradps;
    s_cmd_timeout_ms = frame->timeout_ms;
    s_last_cmd_ms = HAL_GetTick();
    s_last_accepted_cmd_ms = s_last_cmd_ms;
    s_has_accepted_cmd = 1U;
    s_reason = ROBOT_REASON_NONE;

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    s_delayed_disarm_ack.zero_cmd_seen =
        (uint8_t)(s_vx_mmps == 0 && s_w_mradps == 0);
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    if (drop_cmd_ack_once(frame->seq) != 0U) {
        return;
    }
#endif
    send_ack(frame->seq, "CMD");
}
```

### 4. ARM 분기 전체

현재 저장본 651~665행. 아래 원문 범위를 새 블록 전체로 교체한다.

시작: `case UART_FRAME_TYPE_ARM:`

끝: ARM 분기의 `return;`까지. 다음 `case UART_FRAME_TYPE_ESTOP_RESET:`은 포함하지 않는다.

새 블록:

```c
        case UART_FRAME_TYPE_ARM:
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            s_delayed_disarm_ack.zero_cmd_seen = 0U;
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
            s_cmd_ack_drop_zero_count = 0U;
#endif
            motor_output_stop_all();

            s_vx_mmps = 0;
            s_w_mradps = 0;
            s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
            s_last_cmd_ms = HAL_GetTick();
            s_state = ROBOT_ARMED;
            s_reason = ROBOT_REASON_NONE;
            s_last_seq = frame.seq;
            send_ack(frame.seq, "ARM");
            return;
```

### 5. uart_mvp_init 전체

현재 저장본 700~740행. 아래 원문 범위를 새 블록 전체로 교체한다.

시작: `void uart_mvp_init(UART_HandleTypeDef *huart){`

끝: `uart_mvp_init()`의 닫는 `}`까지. 다음 `uart_mvp_set_encoder_cps()`는 포함하지 않는다.

새 블록:

```c
void uart_mvp_init(UART_HandleTypeDef *huart){
    s_uart = huart;
    s_rx_byte = 0u;

    ring_buffer_init(&s_rx_rb);

    s_line_len = 0u;
    s_line_overflow = 0u;
    s_rx_desync_pending = 0u;
    s_rx_line_mode = UART_RX_COLLECT;

    s_state = ROBOT_DISARMED;
    s_reason = ROBOT_REASON_BOOT;
    s_has_accepted_cmd = 0U;
    s_last_accepted_cmd_ms = 0U;
    s_estop_latched = 0U;
    s_last_seq = 0;
    s_stale_disarm_ack_sent = 0u;
    s_duplicate_disarm_ack_seq_sent = 0u;
    s_trailing_comma_disarm_ack_sent = 0u;
    s_overflow_disarm_ack_seq_sent = 0u;
    s_partial_frame_name_disarm_ack_sent = 0u;
    s_embedded_cr_disarm_ack_sent = 0u;
    s_control_byte_disarm_ack_sent = 0u;
    s_overlong_disarm_ack_sent = 0u;
    s_wrong_disarm_ack_type_sent = 0u;
    s_stale_pong_sent = 0u;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    s_delayed_disarm_ack = (delayed_disarm_ack_t){0};
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    s_cmd_ack_drop_used = 0U;
    s_cmd_ack_drop_zero_count = 0U;
#endif
    s_last_tel_ms = 0u;
    s_error_count = 0u;
    s_left_cps = 0;
    s_right_cps = 0;

    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
    s_last_cmd_ms = 0u;
    (void)estop_enforce_latch();
}
```

## PC 검사 결과와 재검사 방법

- 기본 0U: startup DISARM/PONG, 일반 ARM/CMD/DISARM 응답 유지.
- 시험 1U: 10번째 조건 충족 zero CMD ACK만 생략, 부팅당 1회, 새 ARM으로 중복 주입되지 않음.
- 거부된 CMD·CPS/nonzero/FAULT 조건, ARM·초기화 경계, TEL 지속, STM timeout와 E-stop/CAN 처리 확인.
- 실제 ESP executor: matching seq의 fresh ARMED/zero TEL이 있어도 ACK 없이 성공 처리하지 않음.
  149ms에는 대기, 150ms에는 ACK_TIMEOUT/TIMEOUT과 STOPPING, 입력 취소 후 DISARM 송신.
  정상 DISARM ACK와 새 TEL 뒤 IDLE, 3초 동안 자동 ARM/CMD 없음, 새 수동 ARM/zero만 재허용.
- mode 2와 다른 13개 시험 스위치 각각의 동시 활성화는 컴파일 거부.

[후보 PC 출력](../../assets/logs/wifi_link/2026-10-17_ur03_acs04_cmd_ack_drop_preparation/pc_results.txt),
[입력 식별값](../../assets/logs/wifi_link/2026-10-17_ur03_acs04_cmd_ack_drop_preparation/source_manifest.json).
사용자가 저장한 뒤에는 `test_uart_cmd_ack_drop.py --saved`로 실제 파일을 재검사한다.
보드용 STM/ESP 빌드는 사용자가 수행한다.

## 저장본 검사 후 실물 시험 순서

이 절차는 저장본 검사가 끝난 뒤 한 묶음씩 진행한다. 지금은 위 코드 입력·저장까지다.

1. 새 STM 시험 스위치 하나만 `1U`로 바꾸고 사용자 STM 빌드·플래시·Run.
   ESP는 정상 mode 0을 유지한다. STM 재기동 뒤 ESP가 BLOCKED이면 먼저 정상 수동 DISARM으로 복구하고,
   `READY / IDLE / DISARMED`, fresh TEL·속도/PWM/CPS 0을 확인한다. 준비 단계에서 ARM을 누르지 않는다.
2. 모터 동력 분리 조건을 유지한다: MDD10A B+와 #1 보드용 두 2핀 분리·절연,
   #2 sense 회로 공급, S1 ON/S0 해제, 공통 GND. 기존 D0/PA9·D1/PA10·D4/PB6·D6/PC7·D7/PB7 그대로다.
3. 정상 페이지 Console에서 [수신 전용 관측기](../../assets/logs/wifi_link/2026-10-17_ur03_acs04_cmd_ack_drop_preparation/console_observe.js)를 한 번 설치한다.
   이 코드는 WebSocket 수신 기록만 추가하며 ARM/CMD/DISARM 송신이나 페이지 제어 타이머를 바꾸지 않는다.
4. LA 4MHz, 충분한 길이(권장 200M/50초)로 캡처를 시작하고 페이지의 **ARM · 속도 0을 한 번** 누른다.
   로봇 페이지를 그대로 유지한다. 탭 전환·새로고침·수동 DISARM으로 먼저 정지시키지 않는다.
5. 자동 정지 후 `IDLE / DISARMED`, 출력 0을 3초 이상 관찰한다.
   **CMD 결과 TIMEOUT은 이번 의도한 응답 유실의 예상 결과**다.
   페이지가 추가 DISARM을 요청하면 마지막 결과가 DISARM OK로 바뀔 수 있으므로 수신 기록과 함께 본다.
6. 캡처를 `2026-10-17_UR03_ACS04_CMD_ACK_DROP_PWM_run01.sr`로 저장한다.
   Console에 `copy(ur03AckDrop.report())`를 입력하면 JSON이 클립보드에 복사된다. 복사된 JSON,
   ARM 전부터 정지 후까지의 ESP 로그, 마지막 화면을 전달한다.

### 실물 PASS 기준과 중단 조건

- 시작 ARM과 앞선 zero CMD ACK/TEL 확인 후, 정확히 한 `TEST_CMD_ACK_DROP` 표식과 같은 seq의 CMD를 관찰한다.
  해당 seq의 CMD ACK는 이후 구간에도 없어야 한다.
- ACK 대기 중 정상 TEL이 계속되며 해당 CMD의 last_seq를 반영한다. 수신 기록은 해당 CMD의 TIMEOUT을 보인다.
- 이후 새로운 ARM/CMD 없이 CAN+LF+DISARM, matching DISARM ACK와 새 DISARMED/zero TEL을 확인한다.
  자동 정지의 관측 시간은 UART 구간으로 기록하고 브라우저 타이머나 실제 모터 정지 시간과 혼동하지 않는다.
- D4/D6/D7 LOW, PWM/CPS 0, drop/err 증가 없음. 정지 뒤 3초 이상 자동 ARM/CMD 없음.

표식 전에 ACTIVE가 끝나거나 표식 없이 정지하면 ACK 유실 시험 성공으로 판정하지 않는다.
FAULT, 정지 확인 실패/BLOCKED, 기대하지 않은 출력이 나오면 재ARM하지 않고 로그·캡처를 보존한다.
제어가 멈추지 않으면 수동 DISARM으로 정리하고 그 회차는 미완료로 남긴다. used 값을 지우려고 재부팅·반복하지 않는다.

## 정상 모드 복원

시험 결과 확인 후 새 STM 스위치를 **0U**로 복원하고 사용자 빌드·플래시·Run을 한다.
ESP mode 0·다른 STM 스위치 0U를 확인하고 정상 startup/수동 ARM·zero·DISARM 응답을 짧게 검증한다.
복원까지 확인하면 이번 선택적 CMD ACK 유실 범위를 마무리한다.
zero 출력 시험이므로 nonzero 모터 정지 성능이나 전체 AC-S04 완료를 뜻하지 않는다.
