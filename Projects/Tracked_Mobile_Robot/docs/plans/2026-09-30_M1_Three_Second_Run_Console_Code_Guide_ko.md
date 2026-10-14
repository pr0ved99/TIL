# A/M1 3초 구동 콘솔 코드 입력 안내

작성: 2026-09-30. **사용자 입력용 제안이며 실제 펌웨어 소스에는 적용하지 않았다.**
사용자가 입력·저장한 뒤 Codex가 저장본을 검토하고, 사용자 빌드·플래시·계측 순서로 진행한다.

## 이번에 하는 일

A/M1의 방향·단발 timeout·구동 중 DISARM·S0 정지는 이번 대화에서 확인했다.
이번 목표는 **A를 10%로 약 3초 유지했을 때 엔코더 신호와 CPS가 계속 정상인지** 관찰하는 것이다.
B는 정지한다. 이미 완료한 방향·S0 반응 시험을 다시 시작하지 않는다.

사용자는 XL830L만 가지고 있으며 전류 측정선을 고정할 절연 악어클립/연결선은 없다고 답했다.
따라서 지금은 전류계를 동력선에 연결하지 않는다. 기존 K1 87→MDD10A B+ 배선을 유지한다.
전류·정량 발열 시험은 미완료로 남긴다. 이번 3초 관찰을 열적 안정성이나 전체 T-MOTOR-003 PASS로 확대하지 않는다.

이 문서는 **코드 준비** 단계다. 현재 전력단·전체 T005A의 미완료 조건은 유지하며
코드 입력 자체가 장시간·양쪽 모터·차량 주행의 실행 승인을 뜻하지 않는다.

## 두 시간을 분리하는 이유

이전 500ms 단발 설정은 사람이 회전을 보고 S0을 누르기에 지나치게 짧았다.
이번에는 버튼 조작으로 정상 시험을 끝낼 필요가 없다. 정상 동작이면 ESP가 약 3초에 DISARM을 보낸다.

| 시간 | 역할 |
| --- | --- |
| `BENCH_RUN_MS=3000` | 첫 CMD 송신 준비 시각부터 전체 구동 시간을 제한. CMD 갱신으로 연장하지 않음 |
| `BENCH_REFRESH_MS=100` | 직전 CMD의 정상 적용 TEL을 받은 경우에만, 직전 송신에서 최소 100ms 간격으로 새 CMD 송신 |
| `BENCH_CMD_TIMEOUT_MS=500` | STM에서 마지막으로 수락한 CMD의 유효시간. 통신 단절 때 유지되는 기존 정지 조건 |
| `BENCH_RESPONSE_MS=200` | ARM/CMD/DISARM의 해당 seq TEL을 기다리는 제한 |
| `BENCH_TELEMETRY_MAX_AGE_MS=250` | 새 TEL이 없으면 종료하는 ESP 측 수신 제한 |
| `BENCH_MOTION_GAP_MS=500` | 시작 후 또는 마지막 양수 CPS 관찰 뒤 500ms 동안 회전 근거가 없으면 종료 |
| `BENCH_STOP_OBSERVE_MS=600` | DISARM/PWM0 확인 후 연속 두 TEL에서 CPS0/0을 기다리는 제한 |

3초는 **정상 ESP 루프에서 DISARM을 송신하는 목표 시각**이다.
DISARM 손실·ESP 정지 시에는 마지막 수락 CMD의 500ms 만료가 별도로 작동한다.
ESP/STM 스케줄링·전송·실제 관성 정지까지 포함해 정확히 3.000초에 기계적으로 정지한다는 뜻은 아니다.
이 구현을 MCU 고장까지 감시하는 독립 하드웨어 watchdog으로 표현하지 않는다.

## 상태·데이터 흐름

```text
IDLE -> WAIT_ARM -> RUN -> WAIT_DISARM -> WAIT_STILL -> FINISHED
  \-> WAIT_RESET -> IDLE

RUN:
첫 CMD -> 해당 seq의 정상 TEL -> 100ms 이후 다음 CMD
첫 CMD 기준 3초 도달 -> 갱신 중단 -> DISARM
S0/FAULT, STOP, 통신 오류, 회전 근거 유실, 예상 밖 출력 -> DISARM -> FINISHED
```

- `bridge_bench_command()`: HELP/STOP/RESET_ESTOP/M1_RUN 처리.
  구동 전 READY·새 TEL·DISARMED·PWM0/0·CPS0/0을 요구한다.
- `bridge_bench_wait()`: 단계 시작 시각·기대 seq·수신 카운터와 STM err 기준을 저장한다.
  이미 누적된 err가 0이 아니라는 이유로 실패시키지 않고 **시험 도중 증가/변경**을 감지한다.
- `bridge_bench_send_run_cmd()`: CMD마다 새 seq를 배정하고 확인 대기와 최근 송신 시각을 갱신한다.
  **전체 RUN 시작 시각인 `s_bench_phase_tick`는 건드리지 않는다.**
- `s_bench_cmd_confirmed`: ACK만으로 열지 않는다.
  해당 CMD의 새 TEL이 ARMED/NONE, PWM100/0, vx=50/w=-250, 유효 age인지 확인한 뒤 갱신을 허용한다.
- `s_bench_last_motion_tick`: 새 matching TEL의 양수 left_cps로만 갱신한다.
  같은 TEL을 매 루프 다시 읽는 것으로 회전 관찰 시간을 연장하지 않는다.
- `bridge_bench_advance()`: 전체 3초 제한을 CMD 갱신보다 먼저 확인한다.
  정상 종료는 해당 DISARM의 DISARMED/DISARM·PWM0과 연속 두 새 TEL의 CPS0/0으로 확인한다.
- `bridge_bench_finish()`: 종료용 DISARM 후 잠금. 같은 부팅에서는 자동 재시도·재ARM·다음 구동이 없다.
- `console_init()/poll()`: 기존 UART0 콘솔을 유지하고 한 루프의 문자 처리를 제한한다.

200ms 이내 matching TEL이 없으면 CMD를 반복해서 밀어 넣지 않고 종료한다.
새 TEL은 약 100ms 주기이므로 갱신 간격은 수신/스케줄링에 따라 100ms보다 길어질 수 있다.
S0는 언제든 조기 종료 수단이며, 이번에 다시 정해진 순간에 누르라는 절차는 없다.

## 교체 범위

대상: [uart_bridge_main.c](../../03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c).

현재 저장본 **1334행 `/* Manual bench console:`부터 1682행 `bridge_bench_console_poll()`의 마지막 `}`까지**를
아래 C 블록 전체로 교체한다.
**1685행의 `void app_main(void){`부터는 유지한다.** 줄 번호가 달라지면 두 경계 문자열로 찾는다.

STM 소스와 기존 자동 hook 네 개(0U)는 그대로다.
이번 수동 hook `BRIDGE_M1_RUN_TEST_ENABLED`만 1U다.

```c
/* Manual bench console: one bounded M1 run per ESP boot. */
#define BRIDGE_M1_RUN_TEST_ENABLED 1U
#define BENCH_RESPONSE_MS 200U
#define BENCH_TELEMETRY_MAX_AGE_MS 250U
#define BENCH_STOP_OBSERVE_MS 600U
#define BENCH_CMD_TIMEOUT_MS 500U
#define BENCH_RUN_MS 3000U
#define BENCH_REFRESH_MS 100U
#define BENCH_MOTION_GAP_MS 500U

#if BRIDGE_M1_RUN_TEST_ENABLED && (BRIDGE_SCRIPTED_TEST_ENABLED || \
BRIDGE_MALFORMED_COMMAND_TEST_ENABLED || BRIDGE_P04B_ESTOP_RESET_TEST_ENABLED || \
BRIDGE_T004_ESTOP_PWM_TEST_ENABLED)
#error "Disable all automatic bridge test hooks for the manual bench console"
#endif

#if BRIDGE_M1_RUN_TEST_ENABLED && (!defined(CONFIG_ESP_CONSOLE_UART_NUM) || \
CONFIG_ESP_CONSOLE_UART_NUM != 0)
#error "The manual bench console requires the UART0 console"
#endif

typedef enum {
    BENCH_IDLE = 0,
    BENCH_WAIT_RESET,
    BENCH_WAIT_ARM,
    BENCH_RUN,
    BENCH_WAIT_DISARM,
    BENCH_WAIT_STILL,
    BENCH_FINISHED
} bridge_bench_state_t;

static bridge_bench_state_t s_bench_state = BENCH_IDLE;
static uint32_t s_bench_expected_seq;
static uint32_t s_bench_tel_mark;
static uint32_t s_bench_seen_tel_count;
static uint32_t s_bench_err_mark;
static uint32_t s_bench_parse_mark;
static uint32_t s_bench_stm_err_mark;
static TickType_t s_bench_phase_tick;
static TickType_t s_bench_last_tel_tick;
static TickType_t s_bench_cmd_tick;
static TickType_t s_bench_last_motion_tick;
static bool s_bench_cmd_confirmed;
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
    s_bench_stm_err_mark = s_telemetry.err;
    s_bench_phase_tick = now;
}

static void bridge_bench_command(
    const char *command,
    TickType_t now,
    uint32_t *seq
){
    if(strcmp(command, "HELP") == 0){
        ESP_LOGI(TAG,
            "BENCH: RESET_ESTOP, M1_RUN, STOP; "
            "M1 positive 10%% / 3s auto-DISARM; 100ms refresh, 500ms timeout; once per boot");
        return;
    }

    if(strcmp(command, "STOP") == 0){
        bridge_bench_finish(seq, "operator STOP");
        return;
    }

    if(strcmp(command, "RESET_ESTOP") != 0 &&
       strcmp(command, "M1_RUN") != 0){
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
        ESP_LOGW(TAG, "BENCH: M1_RUN requires DISARMED and CPS=0/0");
        return;
    }

    uint32_t arm_seq = (*seq)++;
    s_bench_cmd_confirmed = false;
    s_bench_saw_motion = false;
    s_bench_zero_samples = 0U;
    bridge_bench_wait(BENCH_WAIT_ARM, arm_seq, now);
    if(!bridge_uart_send_arm(arm_seq)){
        bridge_bench_finish(seq, "ARM TX failed");
    }
}

static bool bridge_bench_send_run_cmd(TickType_t now, uint32_t *seq){
    s_bench_expected_seq = (*seq)++;
    s_bench_tel_mark = s_tel_count;
    s_bench_cmd_tick = now;
    s_bench_cmd_confirmed = false;

    /* Do not change s_bench_phase_tick: it is the absolute run deadline base. */
    if(!bridge_uart_send_cmd(
        s_bench_expected_seq, 50, -250, BENCH_CMD_TIMEOUT_MS)){
        bridge_bench_finish(seq, "CMD TX failed; no retry");
        return false;
    }
    return true;
}

static void bridge_bench_advance(TickType_t now, uint32_t *seq){
    if(s_bench_state == BENCH_IDLE || s_bench_state == BENCH_FINISHED){
        return;
    }

    if(!bridge_bench_fresh(now) ||
       s_err_count != s_bench_err_mark ||
       s_parse_error_count != s_bench_parse_mark ||
       s_telemetry.err != s_bench_stm_err_mark){
        bridge_bench_finish(seq, "stale telemetry or new communication error");
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

    if(strcmp(s_telemetry.state, "FAULT") == 0){
        bridge_bench_finish(seq, "STM32 FAULT; no refresh or retry");
        return;
    }

    if(s_bench_state == BENCH_WAIT_ARM){
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

            bridge_bench_wait(BENCH_RUN, *seq, now);
            s_bench_last_motion_tick = now;
            if(bridge_bench_send_run_cmd(now, seq)){
                ESP_LOGW(TAG,
                    "BENCH: M1 10%% run started; auto-DISARM at 3s; "
                    "STOP or physical S0 may end it earlier");
            }
        }
        return;
    }

    if(s_telemetry.right_pwm != 0 || s_telemetry.right_cps != 0 ||
       (s_telemetry.left_pwm != 0 && s_telemetry.left_pwm != 100)){
        bridge_bench_finish(seq, "unexpected PWM or right encoder activity");
        return;
    }

    if(s_bench_state == BENCH_RUN){
        /* Check total duration before considering any CMD refresh. */
        if(elapsed >= pdMS_TO_TICKS(BENCH_RUN_MS)){
            uint32_t disarm_seq = (*seq)++;
            bridge_bench_wait(BENCH_WAIT_DISARM, disarm_seq, now);
            if(!bridge_uart_send_disarm(disarm_seq)){
                bridge_bench_finish(seq, "scheduled DISARM TX failed");
            }
            else{
                ESP_LOGI(TAG, "BENCH: 3s deadline; DISARM sent, refresh stopped");
            }
            return;
        }

        if(strcmp(s_telemetry.state, "ARMED") != 0){
            bridge_bench_finish(seq, "run left ARMED; no re-arm");
            return;
        }

        TickType_t cmd_elapsed = now - s_bench_cmd_tick;
        if(!s_bench_cmd_confirmed &&
           cmd_elapsed >= pdMS_TO_TICKS(BENCH_RESPONSE_MS)){
            bridge_bench_finish(seq, "CMD telemetry confirmation timeout");
            return;
        }

        if(matching_tel){
            if(strcmp(s_telemetry.reason, "NONE") != 0 ||
               s_telemetry.left_pwm != 100 ||
               s_telemetry.vx_mmps != 50 || s_telemetry.w_mradps != -250 ||
               s_telemetry.command_age_ms >= BENCH_CMD_TIMEOUT_MS ||
               s_telemetry.left_cps < 0){
                bridge_bench_finish(seq, "unexpected active M1 telemetry");
                return;
            }

            /* A matching TEL confirms the preceding CMD before another is sent. */
            s_bench_cmd_confirmed = true;
            s_bench_tel_mark = s_tel_count;
            if(s_telemetry.left_cps > 0){
                s_bench_saw_motion = true;
                s_bench_last_motion_tick = now;
            }
        }

        if(now - s_bench_last_motion_tick >=
           pdMS_TO_TICKS(BENCH_MOTION_GAP_MS)){
            bridge_bench_finish(seq, "no recent forward motion; run incomplete");
            return;
        }

        if(s_bench_cmd_confirmed &&
           cmd_elapsed >= pdMS_TO_TICKS(BENCH_REFRESH_MS)){
            (void)bridge_bench_send_run_cmd(now, seq);
        }
        return;
    }

    if(s_bench_state == BENCH_WAIT_DISARM){
        if(elapsed >= pdMS_TO_TICKS(BENCH_RESPONSE_MS)){
            bridge_bench_finish(seq, "DISARM zero confirmation missing");
            return;
        }

        if(matching_tel){
            if(strcmp(s_telemetry.state, "DISARMED") != 0 ||
               strcmp(s_telemetry.reason, "DISARM") != 0 ||
               !bridge_bench_pwm_zero()){
                bridge_bench_finish(seq, "unexpected result after DISARM");
                return;
            }

            s_bench_zero_samples = 0U;
            bridge_bench_wait(BENCH_WAIT_STILL, s_bench_expected_seq, now);
            ESP_LOGI(TAG, "BENCH: DISARM/PWM0 confirmed; waiting for CPS0");
        }
        return;
    }

    if(s_bench_state == BENCH_WAIT_STILL){
        if(elapsed >= pdMS_TO_TICKS(BENCH_STOP_OBSERVE_MS)){
            bridge_bench_finish(seq, "CPS zero not confirmed after DISARM");
            return;
        }

        if(!bridge_bench_pwm_zero() ||
           strcmp(s_telemetry.state, "DISARMED") != 0 ||
           strcmp(s_telemetry.reason, "DISARM") != 0){
            bridge_bench_finish(seq, "state or output changed during stop");
            return;
        }

        if(!new_tel){
            return;
        }

        if(!matching_tel){
            bridge_bench_finish(seq, "unexpected sequence after DISARM");
            return;
        }

        s_bench_tel_mark = s_tel_count;
        if(s_telemetry.left_cps == 0 && s_telemetry.right_cps == 0){
            s_bench_zero_samples++;
        }
        else{
            s_bench_zero_samples = 0U;
        }

        if(s_bench_zero_samples >= 2U){
            bridge_bench_finish(seq, s_bench_saw_motion
                ? "bounded M1 run -> DISARM zero -> two CPS0 TEL observed; "
                  "inspect trace and actual motor"
                : "run ended without forward motion evidence; incomplete");
        }
        return;
    }

    bridge_bench_finish(seq, "unexpected bench state");
}

static void bridge_bench_console_init(void){
    if(BRIDGE_M1_RUN_TEST_ENABLED == 0U){
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
    if(BRIDGE_M1_RUN_TEST_ENABLED == 0U || seq == NULL){
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

## 저장본 검토·빌드

1. 사용자가 위 블록 전체를 입력하고 저장한다.
2. Codex가 실제 저장본의 오타·중복·상태 흐름과 관련 Python 계약 검사를 확인한다.
3. 사용자가 ESP를 빌드한다. 코드 안내만으로 빌드 성공이나 보드 동작을 주장하지 않는다.
4. 플래시·HELP·실제 구동은 별도 단계로 안내한다. 현재 전류계는 회로에서 분리해 둔다.

예상 HELP:

```text
BENCH: RESET_ESTOP, M1_RUN, STOP; M1 positive 10% / 3s auto-DISARM; 100ms refresh, 500ms timeout; once per boot
```

기존 모든 bench hook=0 검사는 수동 hook=1U를 검출한다.
이 상태를 정상 모드 복구 PASS로 바꾸거나 검사를 약화하지 않는다.

## 검토한 분기와 남은 실제 검증

아래는 제안 코드의 제어 흐름을 대조한 항목이며 보드 시험 결과가 아니다.

| 조건 | 코드가 취하는 동작 |
| --- | --- |
| 첫 정상 CMD의 TEL 수신 | 정상 적용을 확인한 뒤 다음 갱신 허용 |
| 같은 TEL을 반복 polling | TEL 카운터 기준이 바뀌어 회전 시간/정지 샘플 중복 갱신 안 함 |
| matching CMD TEL 미수신 | 200ms 기한에 DISARM·잠금 |
| RUN 중 통신 오류/STM err 변경 | DISARM·잠금 |
| RUN 중 S0/FAULT 또는 B 출력·CPS 발생 | 갱신 중단, DISARM·잠금 |
| 시작 후 회전 없음/이후 양수 CPS 유실 | 500ms 제한에서 종료. 재기동하지 않음 |
| 전체 3초 도달과 갱신 시각이 겹침 | 전체 제한을 먼저 처리해 추가 CMD 없이 DISARM |
| CMD 갱신 반복 | 전체 시작 시각 불변. 3초 제한이 계속 뒤로 밀리지 않음 |
| 정상 종료 후 재입력 | FINISHED에서 구동/RESET_ESTOP 거부; HELP/STOP만 처리 |

실제 실행에서는 다음 범위를 확인한다.

- A 실제 전진·B 무동작, A encoder의 지속적인 유효 전이와 대응하는 양수 CPS.
- 여러 CMD를 갱신하더라도 PWM1은 약 10%로 유지되고 전체 약 3초 뒤 종료되는지.
- 최종 DISARM/PWM0/CPS0 유지와 새 err/drop 발생 여부.
- 로직 캡처에서 PWM 갱신 때 뜻하지 않은 출력 공백, 양 상 동시 변화나 지속적인 역전이가 생기는지.
- CPS의 최솟값·최댓값·안정 구간을 기록하되 무부하 개방루프 속도 편차의 합격 수치는 임의로 만들지 않는다.
- 기동/감속의 변화와 안정 구간의 이상을 구분한다.
- 전류·권선 전류·기동 피크·온도·주행 부하 합격을 이 결과에 덧붙이지 않는다.

이번 안내는 손으로 전류 프로브를 잡고 시험하라는 지시가 아니다.
전류 측정은 고정 가능한 적합한 리드와 계측 조건을 확보한 뒤 별도로 준비한다.

