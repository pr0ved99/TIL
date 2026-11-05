# A/M1 구동 중 S0 정지 시험 코드 입력 안내

작성: 2026-09-30. 작성 당시에는 **사용자 입력용 제안 코드**였으며 Codex가 실제 ESP 소스에 자동 적용하지 않았다.
이후 사용자가 입력·빌드·플래시하고 단일 모터 시험을 수행했다. 아래 코드는 당시 실행 조건을 보존한다.

## 시험 후 정정 — 사람의 조작 시간과 통신 timeout 구분

**사람이 회전을 보고 S0을 누르는 시간을 500ms로 제한한 시험 설계는 부적절했다.**
통신이 끊겼을 때 정지시키는 CMD timeout과 사람이 조작할 전체 시험 시간을 분리해야 한다.
다음 수동 시험은 통신 timeout을 유지하면서, 유효한 상태·통신을 확인하는 동안에만 CMD를 갱신하고
별도의 수 초 이내 전체 종료 기한을 두는 방식으로 설계한다. 단순히 STM timeout을 늘리는 수정은 아니다.
이 후속 방식은 아직 구현하지 않았다. 아래 500ms 단발 코드를 향후 수동 S0 시험의 기본 절차로 재사용하지 않는다.
이번 캡처는 S0 감지·PWM 차단이 timeout/종료용 DISARM보다 앞섰으므로 이 시간 설정 문제만으로 재시험하지 않는다.
상세 측정 결과는 진행 기록 일괄 정리 때 반영한다.

## 목적과 시험 범위

직전 시험에서는 A/M1 전진 후 DISARM 정지와 B 무동작을 확인했다.
이번에는 A가 회전할 때 사용자가 S0을 눌러, PC7 감지·PWM 차단·엔코더 변화와 실제 정지를 함께 관찰한다.
T-ESTOP-007의 **분리·고정된 단일 모터 기능 확인**을 준비하는 단계다.
이 시험만으로 전체 T-ESTOP-007, rail-off 수용 기준, 주행 중 정지 거리 또는 전체 T005A를 통과 처리하지 않는다.

| 항목 | 이번 설정 |
| --- | --- |
| 콘솔 명령 | `M1_ESTOP` |
| 대상 | A/M1 전진 10%, B/M2 출력 0 |
| 송신 | `CMD(vx=50, w=-250, timeout_ms=500)` 한 번 |
| 회전 감지 뒤 | 자동 DISARM을 보내지 않고 사용자의 S0 입력을 기다림 |
| 제한 | 자동 CMD 갱신·재시도 없음. STM의 500ms 명령 만료 유지 |
| S0 감지 조건 | 해당 CMD의 새 TEL: `FAULT/ESTOP_ACTIVE`, PWM0/0, `command_age_ms < 500` |
| ESP 관찰 기한 | CMD 송신 준비 시각부터 500ms 미만에 위 TEL 수신. 늦으면 불완전 결과로 잠금 |
| 정지 관찰 | S0 감지 확인 후 600ms 미만에 서로 다른 연속 두 TEL의 CPS0/0 확인 |
| 완료·실패·STOP | DISARM 송신 후 FINISHED. 같은 부팅에서 다시 ARM/CMD하지 않음 |
| S0 상태 | 눌러 잠근 상태 유지. 코드에서 ESTOP_RESET이나 S2 복구를 자동 실행하지 않음 |

**500ms는 정상 통신·STM 실행을 전제로 한 명령 유효시간이며 실제 회전 정지시간 상한이 아니다.**
ESP의 기한도 스케줄러가 실행될 때 평가한다. 독립 안전 정격으로 해석하지 않는다.

기존 DISARM 시험은 회전 TEL을 받자마자 출력을 꺼 S0 시험과 섞일 수 있었다.
이번 코드는 정상 시험 중 DISARM을 먼저 보내지 않는다. 통신 오류·예상 밖 출력·기한 초과·STOP에는 종료용 DISARM을 보낸다.
정상 종료용 DISARM은 S0/PWM0 및 정지 TEL 관찰 뒤에 나온다. 실제 선후관계는 캡처로 확인한다.

## 상태 흐름과 역할

```text
IDLE -> WAIT_ARM -> WAIT_ESTOP -> WAIT_STILL -> FINISHED
  \-> WAIT_RESET -> IDLE

기한 초과 / 통신 오류 / 예상 밖 출력 / STOP -> DISARM -> FINISHED
```

- `bridge_bench_command()`: HELP·STOP·RESET_ESTOP·M1_ESTOP 처리.
  구동은 startup READY, 새 TEL, DISARMED, PWM0/0, CPS0/0에서만 ARM 송신.
- `bridge_bench_wait()`: 단계 시작 시각·기대 seq·TEL/통신 오류 카운터 기준 저장.
- `bridge_bench_advance()`: ARM 확인 뒤 CMD를 한 번 보내고 명령과 일치하는 S0 결과 대기.
  CMD 송신 전에 이미 전송 중이던 이전 seq TEL은 기다리되 500ms 기한은 계속 적용.
- `s_bench_saw_motion`: S0 전 TEL에서 `ARMED/left_pwm=100/left_cps>0`을 봤는지 기록.
  TEL은 약 100ms 간격이므로 false여도 캡처에 회전 신호가 있을 수 있음.
  false는 자동 PASS로 처리하지 않고 **회전 미확인**을 출력.
- `s_bench_zero_samples`: 서로 다른 연속 두 TEL의 CPS0/0 확인.
  `s_bench_tel_mark`를 갱신해 같은 TEL의 반복 확인을 두 번으로 세지 않음.
- `bridge_bench_finish()`: DISARM 송신 후 재시도 잠금. 출력 문구는 관측 요약이며 최종 PASS가 아님.
- `bridge_bench_console_init()/poll()`: UART0 콘솔 유지. 한 루프의 문자 처리를 제한해 UART1 수신을 계속 처리.

S0을 너무 일찍 눌러 실제 회전이 없거나 timeout/종료용 DISARM이 먼저 출력을 차단했다면
**구동 중 S0 정지 증거로 사용하지 않는다.**
S0 조작이 늦었다고 펄스를 자동 반복하거나 timeout을 늘리지 않는다.

## 교체 위치

대상: [uart_bridge_main.c](../../03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c).

현재 저장본 **1334행의 `/* Manual bench console:`부터 1689행의 `bridge_bench_console_poll()` 마지막 `}`까지**를
아래 C 블록 전체로 교체한다. **1691행의 `void app_main(void){`부터는 유지한다.**
줄 번호가 변했으면 두 경계 문자열을 기준으로 찾는다.

상태 enum·변수·HELP·명령 분기·advance/init/poll을 한 범위로 제공한다.
사용자는 이 블록을 입력하고 저장한다. STM32 코드와 기존 자동 시험 hook 네 개(0U)는 그대로다.
수동 시험의 `BRIDGE_M1_ESTOP_TEST_ENABLED`만 1U이며 정상 운용 기본값으로 취급하지 않는다.

```c
/* Manual bench console: one attempted M1 physical-S0 test per ESP boot. */
#define BRIDGE_M1_ESTOP_TEST_ENABLED 1U
#define BENCH_RESPONSE_MS 200U
#define BENCH_TELEMETRY_MAX_AGE_MS 250U
#define BENCH_STOP_OBSERVE_MS 600U
#define BENCH_CMD_TIMEOUT_MS 500U

#if BRIDGE_M1_ESTOP_TEST_ENABLED && (BRIDGE_SCRIPTED_TEST_ENABLED || \
BRIDGE_MALFORMED_COMMAND_TEST_ENABLED || BRIDGE_P04B_ESTOP_RESET_TEST_ENABLED || \
BRIDGE_T004_ESTOP_PWM_TEST_ENABLED)
#error "Disable all automatic bridge test hooks for the manual bench console"
#endif

#if BRIDGE_M1_ESTOP_TEST_ENABLED && (!defined(CONFIG_ESP_CONSOLE_UART_NUM) || \
CONFIG_ESP_CONSOLE_UART_NUM != 0)
#error "The manual bench console requires the UART0 console"
#endif

typedef enum {
    BENCH_IDLE = 0,
    BENCH_WAIT_RESET,
    BENCH_WAIT_ARM,
    BENCH_WAIT_ESTOP,
    BENCH_WAIT_STILL,
    BENCH_FINISHED
} bridge_bench_state_t;

static bridge_bench_state_t s_bench_state = BENCH_IDLE;
static uint32_t s_bench_expected_seq;
static uint32_t s_bench_tel_mark;
static uint32_t s_bench_seen_tel_count;
static uint32_t s_bench_err_mark;
static uint32_t s_bench_parse_mark;
static TickType_t s_bench_phase_tick;
static TickType_t s_bench_last_tel_tick;
static bool s_bench_saw_motion;
static uint32_t s_bench_zero_samples;
static char s_bench_line[24];
static size_t s_bench_line_len;
static bool s_bench_discard_line;

static bool bridge_bench_fresh(TickType_t now){
    return s_telemetry.valid &&
        (now - s_bench_last_tel_tick <=
         pdMS_TO_TICKS(BENCH_TELEMETRY_MAX_AGE_MS));
}

static bool bridge_bench_pwm_zero(void){
    return s_telemetry.left_pwm == 0 && s_telemetry.right_pwm == 0;
}

static void bridge_bench_finish(uint32_t *seq, const char *message){
    s_bench_state = BENCH_FINISHED;
    int sent = bridge_uart_send_disarm((*seq)++);
    ESP_LOGW(TAG, "BENCH LOCKED: %s; DISARM TX=%s",
        message, sent ? "OK" : "FAILED");
}

static void bridge_bench_wait(
    bridge_bench_state_t state,
    uint32_t expected_seq,
    TickType_t now
){
    s_bench_state = state;
    s_bench_expected_seq = expected_seq;
    s_bench_tel_mark = s_tel_count;
    s_bench_err_mark = s_err_count;
    s_bench_parse_mark = s_parse_error_count;
    s_bench_phase_tick = now;
}

static void bridge_bench_command(
    const char *command,
    TickType_t now,
    uint32_t *seq
){
    if(strcmp(command, "HELP") == 0){
        ESP_LOGI(TAG,
            "BENCH: RESET_ESTOP, M1_ESTOP, STOP; "
            "M1 positive 10%%; press S0 on motion; 500ms backup; once per boot");
        return;
    }

    if(strcmp(command, "STOP") == 0){
        bridge_bench_finish(seq, "operator STOP");
        return;
    }

    if(strcmp(command, "RESET_ESTOP") != 0 &&
       strcmp(command, "M1_ESTOP") != 0){
        ESP_LOGW(TAG, "BENCH: unknown command; enter HELP");
        return;
    }

    if(s_bench_state != BENCH_IDLE){
        ESP_LOGW(TAG, "BENCH: busy or finished; no command sent");
        return;
    }

    if(s_startup_state != BRIDGE_STARTUP_READY ||
       !bridge_bench_fresh(now) || !bridge_bench_pwm_zero()){
        ESP_LOGW(TAG, "BENCH: need startup READY and fresh PWM=0/0 TEL");
        return;
    }

    if(strcmp(command, "RESET_ESTOP") == 0){
        if(strcmp(s_telemetry.state, "FAULT") != 0 ||
           strcmp(s_telemetry.reason, "ESTOP_LATCHED") != 0){
            ESP_LOGW(TAG, "BENCH: RESET_ESTOP requires FAULT/ESTOP_LATCHED");
            return;
        }

        uint32_t reset_seq = (*seq)++;
        bridge_bench_wait(BENCH_WAIT_RESET, reset_seq, now);
        if(!bridge_uart_send_estop_reset(reset_seq)){
            bridge_bench_finish(seq, "ESTOP_RESET TX failed");
        }
        return;
    }

    if(strcmp(s_telemetry.state, "DISARMED") != 0 ||
       s_telemetry.left_cps != 0 || s_telemetry.right_cps != 0){
        ESP_LOGW(TAG, "BENCH: M1_ESTOP requires DISARMED and CPS=0/0");
        return;
    }

    uint32_t arm_seq = (*seq)++;
    s_bench_saw_motion = false;
    s_bench_zero_samples = 0U;
    bridge_bench_wait(BENCH_WAIT_ARM, arm_seq, now);
    if(!bridge_uart_send_arm(arm_seq)){
        bridge_bench_finish(seq, "ARM TX failed");
    }
}

static void bridge_bench_advance(TickType_t now, uint32_t *seq){
    if(s_bench_state == BENCH_IDLE || s_bench_state == BENCH_FINISHED){
        return;
    }

    if(!bridge_bench_fresh(now) ||
       s_err_count != s_bench_err_mark ||
       s_parse_error_count != s_bench_parse_mark){
        bridge_bench_finish(seq, "stale telemetry or RX error");
        return;
    }

    bool new_tel = s_tel_count != s_bench_tel_mark;
    bool matching_tel = new_tel &&
        s_telemetry.last_seq == s_bench_expected_seq;
    TickType_t elapsed = now - s_bench_phase_tick;

    if(s_bench_state == BENCH_WAIT_RESET){
        if(matching_tel &&
           strcmp(s_telemetry.state, "DISARMED") == 0 &&
           strcmp(s_telemetry.reason, "ESTOP_RESET") == 0 &&
           bridge_bench_pwm_zero()){
            s_bench_state = BENCH_IDLE;
            ESP_LOGI(TAG, "BENCH: reset confirmed; no ARM/CMD sent");
        }
        else if(elapsed >= pdMS_TO_TICKS(BENCH_RESPONSE_MS)){
            bridge_bench_finish(seq, "reset confirmation timeout");
        }
        return;
    }

    if(s_bench_state == BENCH_WAIT_ARM){
        if(strcmp(s_telemetry.state, "FAULT") == 0){
            bridge_bench_finish(seq, "FAULT before CMD; no drive");
            return;
        }

        if(elapsed >= pdMS_TO_TICKS(BENCH_RESPONSE_MS)){
            bridge_bench_finish(seq, "ARM confirmation timeout; no CMD");
            return;
        }

        if(matching_tel && strcmp(s_telemetry.state, "ARMED") == 0){
            if(!bridge_bench_pwm_zero() ||
               s_telemetry.left_cps != 0 || s_telemetry.right_cps != 0){
                bridge_bench_finish(seq, "unexpected output or motion before CMD");
                return;
            }

            uint32_t cmd_seq = (*seq)++;
            bridge_bench_wait(BENCH_WAIT_ESTOP, cmd_seq, now);
            if(!bridge_uart_send_cmd(cmd_seq, 50, -250, BENCH_CMD_TIMEOUT_MS)){
                bridge_bench_finish(seq, "CMD TX failed; no retry");
                return;
            }
            ESP_LOGW(TAG,
                "BENCH: M1 positive 10%% CMD sent; press and hold S0 on motion; "
                "500ms backup timeout, no refresh");
        }
        return;
    }

    if(s_telemetry.right_pwm != 0 || s_telemetry.right_cps != 0 ||
       (s_telemetry.left_pwm != 0 && s_telemetry.left_pwm != 100)){
        bridge_bench_finish(seq, "unexpected PWM or right encoder activity");
        return;
    }

    if(s_bench_state == BENCH_WAIT_ESTOP){
        if(elapsed >= pdMS_TO_TICKS(BENCH_CMD_TIMEOUT_MS)){
            bridge_bench_finish(seq,
                "no in-time S0 confirmation; S0 test incomplete");
            return;
        }

        /* An older TEL may already be in transit when CMD is sent. */
        if(!matching_tel){
            return;
        }

        if(strcmp(s_telemetry.state, "ARMED") == 0){
            if(s_telemetry.left_pwm != 100 ||
               s_telemetry.command_age_ms >= BENCH_CMD_TIMEOUT_MS){
                bridge_bench_finish(seq, "unexpected active sample; incomplete");
                return;
            }

            if(s_telemetry.left_cps > 0){
                s_bench_saw_motion = true;
            }
            return;
        }

        if(strcmp(s_telemetry.state, "FAULT") == 0 &&
           strcmp(s_telemetry.reason, "ESTOP_ACTIVE") == 0 &&
           bridge_bench_pwm_zero() &&
           s_telemetry.command_age_ms < BENCH_CMD_TIMEOUT_MS){
            ESP_LOGI(TAG,
                "BENCH: ESTOP_ACTIVE/PWM0 before 500ms; "
                "prior motion TEL=%s; keep S0 latched",
                s_bench_saw_motion ? "YES" : "NO");
            s_bench_zero_samples = 0U;
            bridge_bench_wait(BENCH_WAIT_STILL, s_bench_expected_seq, now);
            return;
        }

        bridge_bench_finish(seq,
            "drive ended without in-time ESTOP_ACTIVE/PWM0; incomplete");
        return;
    }

    if(s_bench_state == BENCH_WAIT_STILL){
        if(elapsed >= pdMS_TO_TICKS(BENCH_STOP_OBSERVE_MS)){
            bridge_bench_finish(seq,
                "CPS zero not confirmed after S0; inspect motor and trace");
            return;
        }

        if(!bridge_bench_pwm_zero() ||
           strcmp(s_telemetry.state, "FAULT") != 0 ||
           strcmp(s_telemetry.reason, "ESTOP_ACTIVE") != 0){
            bridge_bench_finish(seq,
                "S0 state or output changed during stop observation");
            return;
        }

        if(!new_tel){
            return;
        }

        if(!matching_tel){
            bridge_bench_finish(seq, "unexpected sequence after S0");
            return;
        }

        /* Count separate telemetry frames, not repeated polling of one frame. */
        s_bench_tel_mark = s_tel_count;
        if(s_telemetry.left_cps == 0 && s_telemetry.right_cps == 0){
            s_bench_zero_samples++;
        }
        else{
            s_bench_zero_samples = 0U;
        }

        if(s_bench_zero_samples >= 2U){
            bridge_bench_finish(seq, s_bench_saw_motion
                ? "motion TEL -> S0 zero -> two CPS0 TEL observed; "
                  "inspect trace and actual motor"
                : "S0 zero and two CPS0 TEL observed; prior motion unconfirmed; "
                  "inspect trace and actual motor");
        }
        return;
    }

    bridge_bench_finish(seq, "unexpected bench state");
}

static void bridge_bench_console_init(void){
    if(BRIDGE_M1_ESTOP_TEST_ENABLED == 0U){
        return;
    }

    const uart_config_t config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    ESP_ERROR_CHECK(uart_driver_install(UART_NUM_0, 256, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(UART_NUM_0, &config));
    ESP_LOGI(TAG, "BENCH manual console ready on UART0; enter HELP");
}

static void bridge_bench_console_poll(TickType_t now, uint32_t *seq){
    if(BRIDGE_M1_ESTOP_TEST_ENABLED == 0U || seq == NULL){
        return;
    }

    if(s_bench_seen_tel_count != s_tel_count){
        s_bench_seen_tel_count = s_tel_count;
        s_bench_last_tel_tick = now;
    }

    /* Bound the console work so UART1 telemetry still gets serviced. */
    for(unsigned i = 0U; i < 32U; i++){
        uint8_t ch;
        if(uart_read_bytes(UART_NUM_0, &ch, 1, 0) != 1){
            break;
        }

        if(ch == '\r' || ch == '\n'){
            if(!s_bench_discard_line && s_bench_line_len > 0U){
                s_bench_line[s_bench_line_len] = '\0';
                bridge_bench_command(s_bench_line, now, seq);
            }
            s_bench_line_len = 0U;
            s_bench_discard_line = false;
        }
        else if(!s_bench_discard_line){
            if(ch < 32U || ch > 126U ||
               s_bench_line_len >= sizeof(s_bench_line) - 1U){
                s_bench_discard_line = true;
                s_bench_line_len = 0U;
            }
            else{
                s_bench_line[s_bench_line_len++] = (char)ch;
            }
        }
    }
    bridge_bench_advance(now, seq);
}
```

## 코드 입력 후 확인

1. 저장본을 다시 검토한다. 이전 `M1_DISARM`, `BENCH_WAIT_DISARM`, 중복 함수가 남지 않았는지 확인한다.
2. 사용자가 ESP 빌드를 진행한다. STM 소스는 변경하지 않는다.
3. 전원·플래시 준비는 다음 단계에서 안내한다. 코드 입력과 동시에 모터 시험을 시작하지 않는다.
4. 사용자 플래시 후 HELP는 아래 문구여야 한다.

```text
BENCH: RESET_ESTOP, M1_ESTOP, STOP; M1 positive 10%; press S0 on motion; 500ms backup; once per boot
```

Python 계약 검사는 MCU 빌드나 실제 동작 검증을 대신하지 않는다.
수동 시험 hook=1U는 기존 “모든 bench hook=0” 기본값 검사와 맞지 않는다.
검사를 통과시키기 위해 시험용 예외를 숨기거나 기본값 요구를 삭제하지 않는다.
시험 종료 뒤 정상 운용 복구 시에는 hook=0 확인과 사용자 빌드·플래시가 별도로 필요하다.

## 준비된 계측 경로

사용자는 직전 안내에 “다음”으로 응답해 전원 분리와 아래 추가 연결 완료를 보고했다.
사진 확인이나 새 전압 측정값을 받은 것은 아니다.

| 채널 | 신호·위치 |
| --- | --- |
| D0 | PC7 — JDBG_CTRL_2 Pin2 |
| D1 | PWM1 — JDBG_CTRL_1 Pin2 |
| D2 | PWM2 — JDBG_CTRL_2 Pin1 |
| D4 | STM TX → ESP — JDBG_UART Pin1 |
| D5 | ESP TX → STM — JDBG_UART Pin2 |
| D6 | 왼쪽 엔코더 A/PB4 — JDBG_ENC_1 Pin1, C9/R37 |
| D7 | 왼쪽 엔코더 B/PB5 — JDBG_ENC_1 Pin2, C8/R37 |
| GND | 기존 공통 GND 유지 |

D6/D7은 [엔코더 조정부 보고서](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md)의
1kΩ 직렬저항 뒤 MCU 측 노드다. 로직분석기는 12V 모터 전원 측정에 사용하지 않는다.

## 실행과 판정 기준

실행은 저장본 검토·사용자 빌드/플래시·HELP 확인 후 순서대로 안내한다.
아래는 판정 기준이며 지금 전원을 넣으라는 지시가 아니다.

- 모터는 섀시에서 분리·고정하고 회전축을 비워둔 기존 조건을 유지한다.
- S0 조작을 준비한 뒤 M1_ESTOP을 한 번 실행하며 **실제 A의 회전 시작을 보고 S0을 눌러 잠근다.**
  TEL의 회전 알림을 기다릴 필요는 없다.
- 캡처에서 A의 엔코더 변화와 PWM1 구동이 PC7 상승 전부터 존재하는지 확인한다.
- PC7 상승 시점에도 PWM1이 활성 상태이고 timeout/종료용 DISARM보다 먼저 S0 사건이 발생했는지 확인한다.
- 이후 PWM1/2가 0으로 유지되고 FAULT/ESTOP_ACTIVE와 CPS0/0, A 실제 정지·B 무동작을 함께 확인한다.
- PC7 상승→PWM1 마지막 펄스, PC7 상승→마지막 엔코더 전이를 따로 기록한다.
  엔코더 전이 종료는 센서 분해능 이내 관찰이며 정확한 기계적 정지 시각이나 차체 정지 거리가 아니다.
- 회전 없는 S0, timeout 선행, S0 전 DISARM 선행, 관찰 기한 초과 또는 회전 증거 부족은 불완전 결과로 둔다.
- 예상 밖 모터 동작이나 출력 유지가 보이면 S0 잠금·S1 OFF로 종료한다.
- K1 전후 rail 전압, 정격·열·부하, 주행 조건의 수용은 별도 항목으로 남긴다.

기준은 기존 [S0 안전 요구사항](../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md),
[전체 실행 계획](00_Project_Master_Plan_To_Final_MVP_ko.md)의 남은 항목과 구분해 기록한다.
이번 문서는 코드 입력 안내이며 진행 기록과 검증 결과는 시험 묶음이 끝날 때 정리한다.
