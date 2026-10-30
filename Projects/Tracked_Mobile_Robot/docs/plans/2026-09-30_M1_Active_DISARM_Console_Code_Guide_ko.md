# A/M1 구동 중 DISARM 시험 코드 입력 안내

작성: 2026-09-30. **코드 제안 단계**이며 실제 ESP 소스에 자동 적용하지 않았다.
사용자가 입력·저장하면 저장본 검토 → 사용자 빌드 → 전원 조건 확인 → 사용자 플래시·HELP 확인 순서로 진행한다.
아래 코드는 보드에서 빌드·실행한 결과가 아니다.

## 목적과 이전 시험의 차이

직전 A/M1 양수 10%·300ms 시험에서는 사용자가 실제 전진 후 정지, B 무동작을 확인했다.
첨부 로그는 CMD 수락 후 267ms에 처음 양수 CPS를 보고했고, 367ms TEL에서 CMD_TIMEOUT/PWM0을 보였다.
그 결과는 명령 만료에 따른 정지이며, 이번 목표는 **회전 중 별도 DISARM 명령으로 출력을 끄는 것**이다.

| 항목 | 이번 설정과 이유 |
| --- | --- |
| 구동 대상 | A/M1, 양수 10%. B/M2 PWM0 유지 |
| 콘솔 명령 | `M1_DISARM`. 기존 `M1_PULSE`와 구분 |
| CMD | `vx_mmps=50,w_mradps=-250,timeout_ms=500`, 한 번만 송신 |
| 500ms | STM32가 현재 허용하는 timeout 상한. ESP가 DISARM을 보내지 못했을 때의 명령 만료 경로. 300ms에서 늘어나는 부분이며 정상 시험은 회전 감지 후 조기에 DISARM |
| 회전 확인 제한 | CMD 송신을 준비한 ESP 시각부터 350ms 미만, STM TEL의 command_age도 350ms 미만. 넘으면 DISARM을 보내고 불완전 결과로 종료 |
| 회전 조건 | 해당 CMD의 새 TEL에서 ARMED, left_pwm=100, left_cps>0, right_pwm/right_cps=0 |
| 출력 차단 확인 | 해당 DISARM의 새 TEL에서 DISARMED/DISARM, PWM0/0, command_age<500ms |
| 정지 관찰 | 출력 0 확인 후 600ms 안에 새 TEL의 CPS0/0 확인. 이후 안정 유지와 실제 정지는 원본 로그·육안으로 별도 확인 |
| 반복 금지 | 완료·실패·STOP 뒤 잠금. 추가 CMD·자동 refresh·자동 재시도 없음 |

상태 흐름:

```text
IDLE -> WAIT_ARM -> WAIT_ACTIVE -> WAIT_DISARM -> WAIT_STILL -> FINISHED
  \-> WAIT_RESET -> IDLE

시험 중 FAULT / 통신 오류 / stale TEL / 예상 밖 출력 -> DISARM -> FINISHED
회전 미확인·늦은 정지 증거 -> DISARM -> FINISHED (시험 통과 아님)
```

350ms는 ESP가 실행되는 동안 회전 확인을 기다리는 제한이다. ESP 정지·통신 장애까지 항상 이 시간에 멈춘다는 뜻은 아니다.
STM32의 500ms 명령 만료와 기존 물리 S0 차단 경로를 유지한다.
CPS0 한 샘플이나 콘솔 완료 문구만으로 실제 정지 시간·거리 또는 전체 모터 수용을 PASS로 판정하지 않는다.

## 교체 위치와 방법

대상: [uart_bridge_main.c](../../03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c).

현재 저장본 **1334행의 `/* Manual bench console:`부터 1605행의 `bridge_bench_console_poll()` 마지막 닫는 중괄호까지**를 아래 C 블록 전체로 교체한다.
바로 다음 **`void app_main(void){`는 교체 범위에 포함하지 않는다.**
행 번호가 바뀌었으면 두 경계 문자열을 기준으로 찾는다.

이 범위 안에 매크로·상태 enum·HELP·명령 분기·advance/init/poll을 모두 포함했다.
기존 네 자동 시험 hook은 0U, 이 수동 시험 hook만 1U다.
STM32 코드·핀·동력선 변경은 이번 코드 입력에 포함하지 않는다.

```c
/* Manual bench console: one attempted M1 active-DISARM test per ESP boot. */
#define BRIDGE_M1_DISARM_TEST_ENABLED 1U
#define BENCH_RESPONSE_MS 200U
#define BENCH_TELEMETRY_MAX_AGE_MS 250U
#define BENCH_STOP_OBSERVE_MS 600U
#define BENCH_CMD_TIMEOUT_MS 500U
#define BENCH_ACTIVE_WAIT_MS 350U

#if BRIDGE_M1_DISARM_TEST_ENABLED && (BRIDGE_SCRIPTED_TEST_ENABLED || \
BRIDGE_MALFORMED_COMMAND_TEST_ENABLED || BRIDGE_P04B_ESTOP_RESET_TEST_ENABLED || \
BRIDGE_T004_ESTOP_PWM_TEST_ENABLED)
#error "Disable all automatic bridge test hook for the manual bench console"
#endif

#if BRIDGE_M1_DISARM_TEST_ENABLED && (!defined(CONFIG_ESP_CONSOLE_UART_NUM) || \
CONFIG_ESP_CONSOLE_UART_NUM != 0)
#error "The manual bench console requires the UART0 console"
#endif

typedef enum {
    BENCH_IDLE = 0,
    BENCH_WAIT_RESET,
    BENCH_WAIT_ARM,
    BENCH_WAIT_ACTIVE,
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
static TickType_t s_bench_phase_tick;
static TickType_t s_bench_last_tel_tick;
static bool s_bench_saw_output;
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
            "BENCH: RESET_ESTOP, M1_DISARM, STOP; "
            "M1 positive 10%%; DISARM on motion; 500ms backup; once per boot");
        return;
    }

    if(strcmp(command, "STOP") == 0){
        bridge_bench_finish(seq, "operator STOP");
        return;
    }

    if(strcmp(command, "RESET_ESTOP") != 0 &&
       strcmp(command, "M1_DISARM") != 0){
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
        ESP_LOGW(TAG, "BENCH: M1_DISARM requires DISARMED and CPS=0/0");
        return;
    }

    uint32_t arm_seq = (*seq)++;
    s_bench_saw_output = false;
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

    if(strcmp(s_telemetry.state, "FAULT") == 0){
        bridge_bench_finish(seq, "STM32 FAULT; no retry");
        return;
    }

    if(s_bench_state == BENCH_WAIT_ARM){
        if(elapsed >= pdMS_TO_TICKS(BENCH_RESPONSE_MS)){
            bridge_bench_finish(seq, "ARM confirmation timeout; no CMD");
            return;
        }

        if(matching_tel && strcmp(s_telemetry.state, "ARMED") == 0){
            if(!bridge_bench_pwm_zero()){
                bridge_bench_finish(seq, "unexpected PWM before CMD");
                return;
            }

            uint32_t cmd_seq = (*seq)++;
            bridge_bench_wait(BENCH_WAIT_ACTIVE, cmd_seq, now);
            if(!bridge_uart_send_cmd(cmd_seq, 50, -250, BENCH_CMD_TIMEOUT_MS)){
                bridge_bench_finish(seq, "CMD TX failed; no retry");
                return;
            }
            ESP_LOGW(TAG,
                "BENCH: M1 positive 10%% CMD sent; "
                "500ms backup timeout, no refresh");
        }
        return;
    }

    if(s_telemetry.right_pwm != 0 || s_telemetry.right_cps != 0 ||
       (s_telemetry.left_pwm != 0 && s_telemetry.left_pwm != 100)){
        bridge_bench_finish(seq, "unexpected PWM or right encoder activity");
        return;
    }

    if(s_bench_state == BENCH_WAIT_ACTIVE){
        if(elapsed >= pdMS_TO_TICKS(BENCH_ACTIVE_WAIT_MS)){
            bridge_bench_finish(seq,
                "motion confirmation deadline; DISARM test incomplete");
            return;
        }

        if(matching_tel){
            if(strcmp(s_telemetry.state, "ARMED") != 0){
                bridge_bench_finish(seq,
                    "drive ended before test DISARM; result incomplete");
                return;
            }

            if(s_telemetry.left_pwm == 100 && s_telemetry.left_cps > 0){
                if(s_telemetry.command_age_ms >= BENCH_ACTIVE_WAIT_MS){
                    bridge_bench_finish(seq,
                        "active sample too late; DISARM test incomplete");
                    return;
                }

                s_bench_saw_output = true;
                uint32_t disarm_seq = (*seq)++;
                bridge_bench_wait(BENCH_WAIT_DISARM, disarm_seq, now);
                if(!bridge_uart_send_disarm(disarm_seq)){
                    bridge_bench_finish(seq, "test DISARM TX failed");
                    return;
                }
                ESP_LOGW(TAG,
                    "BENCH: active M1 motion observed; "
                    "DISARM seq=%" PRIu32 " sent",
                    disarm_seq);
            }
        }
        return;
    }

    if(s_bench_state == BENCH_WAIT_DISARM){
        if(elapsed >= pdMS_TO_TICKS(BENCH_RESPONSE_MS)){
            bridge_bench_finish(seq,
                "DISARM confirmation missing; check S0");
            return;
        }

        if(matching_tel){
            if(strcmp(s_telemetry.state, "DISARMED") != 0 ||
               strcmp(s_telemetry.reason, "DISARM") != 0 ||
               !bridge_bench_pwm_zero()){
                bridge_bench_finish(seq,
                    "test DISARM did not confirm output zero; check S0");
                return;
            }

            if(s_telemetry.command_age_ms >= BENCH_CMD_TIMEOUT_MS){
                bridge_bench_finish(seq,
                    "zero TEL too late to distinguish timeout; incomplete");
                return;
            }

            ESP_LOGI(TAG,
                "BENCH: DISARM output zero confirmed before 500ms; "
                "waiting for CPS=0/0");
            bridge_bench_wait(
                BENCH_WAIT_STILL, s_bench_expected_seq, now);
        }
        return;
    }

    if(s_bench_state == BENCH_WAIT_STILL){
        if(elapsed >= pdMS_TO_TICKS(BENCH_STOP_OBSERVE_MS)){
            bridge_bench_finish(seq,
                "CPS zero not confirmed after DISARM; check S0");
            return;
        }

        if(!bridge_bench_pwm_zero() ||
           strcmp(s_telemetry.state, "DISARMED") != 0 ||
           strcmp(s_telemetry.reason, "DISARM") != 0){
            bridge_bench_finish(seq,
                "output or state changed after DISARM; check S0");
            return;
        }

        if(matching_tel && s_bench_saw_output &&
           s_telemetry.left_cps == 0 && s_telemetry.right_cps == 0){
            bridge_bench_finish(seq,
                "active M1 -> DISARM zero -> CPS=0/0 observed; "
                "inspect trace and actual motor");
            return;
        }

        return;
    }

    bridge_bench_finish(seq, "unexpected bench state");
}

static void bridge_bench_console_init(void){
    if(BRIDGE_M1_DISARM_TEST_ENABLED == 0U){
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
    if(BRIDGE_M1_DISARM_TEST_ENABLED == 0U || seq == NULL){
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

## 코드를 읽는 순서

1. `bridge_bench_command()`는 HELP/STOP/RESET_ESTOP/M1_DISARM을 구분한다. M1_DISARM은 READY·새 TEL·DISARMED·PWM0·CPS0에서만 ARM을 보낸다.
2. `bridge_bench_wait()`는 단계·기대 명령 번호·TEL 기준 번호·오류 카운터·시각을 함께 기록한다. 같은 단계 전의 오래된 TEL을 새 명령의 결과로 쓰지 않기 위한 기준이다.
3. `WAIT_ACTIVE`는 10% 출력을 요청한 뒤 해당 CMD의 PWM과 양수 CPS를 기다린다. 확인 즉시 새 seq로 DISARM을 전송한다. 회전하지 않으면 자동 재시도하지 않는다.
4. `WAIT_DISARM`은 새 DISARM seq와 상태·이유·출력·command_age를 함께 확인한다. DISARM 처리 뒤에는 마지막 CMD의 age가 유지되는 현재 STM 구현을 사용한다.
5. `WAIT_STILL`은 출력 0 뒤 엔코더 CPS의 0 복귀를 관찰한다. PWM 차단과 기계적 정지를 같은 시각으로 취급하지 않는다.
6. `bridge_bench_finish()`는 완료/실패 상태를 잠그고 보수적으로 DISARM을 한 번 더 보낸다. 파형에서는 구동 중 처음 보낸 시험 DISARM과 종료 시 재전송을 구분한다.

고정된 짧은 시간 후 바로 DISARM을 보내면 직전처럼 회전이 늦게 시작되는 경우 구동 중 정지 증거가 없을 수 있어, 양수 CPS 확인을 조건으로 쓴다.
회전 증거가 제한 시간 안에 나타나지 않으면 시험 불성립으로 남긴다. 이 조건 때문에 엔코더 오류를 물리 회전으로 오인하지 않도록 육안 확인도 필요하다.

## 저장 후 확인과 실제 시험의 범위

- 사용자 저장 후 실제 소스의 명령 이름·매크로 참조·시간 상수·seq/상태 전환을 다시 검토하고 Python 계약 검사를 실행한다.
- 사용자 ESP 빌드 후 HELP에 `M1_DISARM`, `DISARM on motion`, `500ms backup`이 나오는지 확인한다.
- 이 안내만으로 전원을 투입하거나 새 구동 시험을 시작하지 않는다. 현재 작업은 S0 잠금·S1 OFF 후, 사용자 `다음` 응답으로 LiPo/두 USB 분리 및 로직분석기 연결·설정 단계를 진행한 상태다. 개별 연결 사진·측정값은 추가 보고되지 않았다.
- 전력단 T005A의 rail-off 기준·정격 release 미결은 [기존 보고서](../verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md)와 [후속 전력단 기록](../verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md)에 남아 있다. 이 코드 작성은 그 항목의 해소나 구동 시간 확대 승인으로 기록하지 않는다. 통전 시험 범위·조건은 실행 전에 정한다.
- 구동 중 DISARM 확인과 실제 S0 전원 차단은 별도 시험이다. 전체 T-MOTOR-003 / T-ESTOP-007 완료로 확대하지 않는다.

계측 준비는 4MHz/100M samples(25초), D0=PC7, D1=PWM1, D2=PWM2, D4=STM TX, D5=ESP TX다.
UART decoder는 STM 기준 RX=D5/TX=D4, 115200/8N1/LSB first다.
구동 중 시험 DISARM 프레임과 D1 PWM의 마지막 활성 구간을 대조하고, D2의 비활성 유지와 실제 A 정지를 확인한다.
프레임 전에 PWM이 이미 꺼져 있거나 증거가 부족하면 DISARM 정지 지연 PASS로 해석하지 않는다.
