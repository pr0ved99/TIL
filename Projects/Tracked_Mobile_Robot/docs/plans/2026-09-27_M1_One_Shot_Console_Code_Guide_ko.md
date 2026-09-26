# M1 수동 1회 펄스 시험 코드 입력 안내

상태: **2026-09-27 사용자 입력 도중 중단한 WIP**. 아래는 완성 목표 블록이며 실제 파일은 일부만 입력됐다.
ESP-IDF v6.0.2의 로컬 UART API와 현재 프로젝트 설정을 기준으로 작성했다.
펌웨어 빌드·플래시·보드 동작은 아직 검증하지 않았다. 사용자가 입력한 실제 파일을 다시 검토한 뒤 진행한다.

## 휴식 후 재개 위치

실제 [hello_world_main.c](../../03_Firmware/esp32_uart_bridge/main/hello_world_main.c)는
`bridge_bench_command()`까지 입력했고 아래 세 함수는 선언된 빈 몸체 상태다.

- `bridge_bench_advance()`
- `bridge_bench_console_init()`
- `bridge_bench_console_poll()`

`app_main()`의 init/poll 호출 두 곳도 아직 추가하지 않았다. 입력한 앞부분에서는 다음을 함께 고친다.

| 현재 저장 내용 | 완성 블록의 내용·수정 이유 |
| --- | --- |
| `#if` 조건 두 곳을 여러 줄로 나누고 줄 연속 처리를 생략 | 아래처럼 각각 한 줄로 입력하거나 줄 끝에 역슬래시를 넣어 이어야 함 |
| `BRIDGE_SCRIPED_TEST_ENABLED` | `BRIDGE_SCRIPTED_TEST_ENABLED`: 기존 자동 시험 매크로의 정확한 이름 |
| `bridge_bench_finished(...)` | `bridge_bench_finish(...)`: 위에서 정의한 함수 이름 |
| 로그의 `enter HLEP` | `enter HELP` |

미완성 파일은 현재 빌드·플래시 대상으로 보지 않는다. Codex는 중단한 코드를 대신 완성하지 않고 보존했다.
설명은 목적·전체 흐름·시간 상수·enum과 `s_bench_state`까지 진행했다.
**다음 설명은 `s_bench_expected_seq`, `s_bench_tel_mark` 등 나머지 상태 변수부터** 이어간다.
작성 위치와 설명 위치가 다르므로 이미 입력한 부분을 처음부터 다시 타이핑하지 않는다.
이번 문서의 목표는 HELP 입력 확인까지이며 실제 회전 시험은 별도 단계다.

## 이번에 만드는 기능

모니터에서 명령 한 줄을 입력하면 ESP가 기존 UART1으로 STM32에 제한된 시험 명령을 전송한다.
STM32의 상태 머신·E-stop·출력 제한·명령 타임아웃을 그대로 통과한다.
기존 ESP의 startup DISARM/PING/PONG 절차와 TEL parser도 유지한다.

| 명령 | 역할 |
| --- | --- |
| `HELP` | 입력 경로 확인과 명령 안내. STM32에 명령을 보내지 않음 |
| `RESET_ESTOP` | S0 해제 후 남아 있는 ESTOP_LATCHED를 수동 해제. ARM/CMD는 보내지 않음 |
| `M1_PULSE` | 최신 DISARMED·PWM0·CPS0에서 ARM 전송 → 해당 ARM의 새 TEL 확인 → M1 5% CMD 한 번 전송 |
| `STOP` | DISARM 전송, 이번 시험을 종료 상태로 잠금 |

`M1_PULSE`가 시작 조건을 통과해 ARM 전송 단계에 들어가면 이번 ESP 실행 중 재시도하지 않는다. STOP·시험 중 실패·완료 후에도 같다.
시작 조건 미충족으로 거부된 입력은 IDLE을 유지한다.
재부팅 후에도 자동 구동하지 않으며 새 수동 입력이 있어야 한다.

현재 매핑은 A=왼쪽/M1/JENC_1/TIM3/left다. B는 오른쪽/JENC_2/TIM5/right이고 동력선은 분리한다.
이 시험에서 양의 출력 명령이 실제 차량 전진인지 처음 확인한다. 손회전으로 확인한 엔코더 부호와
전동 구동의 DIR 극성은 별개다. 실제 방향이 반대이면 먼저 정지한 뒤 출력 DIR 설정을 검토한다.

## 듀티와 시간의 근거

현재 STM32 mapper에서 `vx_mmps=25`, `w_mradps=-125`, duty cap=100 permille이면:

```text
linear = 250, yaw = -250
left = (250 - (-250)) * 100 / 1000 = 50 permille = 5%
right = (250 + (-250)) * 100 / 1000 = 0
```

이 값은 현재 open-loop mapper의 시험 입력이다. 실제 25 mm/s를 보장하는 속도 제어가 아니다.
CMD는 한 번만 보내며 `timeout_ms=300`이다. STM32가 약 300ms 뒤 PWM을 차단한다.
모터 축의 기계적 정지 시간이 300ms라는 뜻은 아니다.
ESP가 멈추거나 UART가 끊겨도 CMD를 갱신하지 않으므로 STM32 타임아웃이 남는다.
ESP는 응답·통신 이상에서 DISARM을 추가로 보내지만, 통신이 끊기면 그 전달은 보장되지 않는다.

## 입력 전 상태

- S0 잠금, S1 OFF, LiPo는 로봇에서 분리한다. 보드 USB는 유지해도 된다.
- USB 시험 구성: XL4015 #1의 보드용 2P 두 개 분리, STM32 JP5=U5V/JP1=OPEN.
- ESP는 **UART라고 표시된 USB 커넥터**를 사용한다. 아래 입력 코드는 UART0을 읽는다.
  native USB 커넥터의 보조 로그 표시와 UART0 입력은 서로 다르다. COM 번호는 고정하지 않는다.
- 기존 네 ESP 시험 hook과 STM32 출력 시험 hook은 모두 0U를 유지한다.

## 1. 연결된 코드 블록 전체 추가

대상: `03_Firmware/esp32_uart_bridge/main/hello_world_main.c`.
기존 `bridge_uart_startup_step()` 함수가 끝난 뒤, **`void app_main(void){` 바로 앞**에 다음 블록 전체를 추가한다.
기존 함수들은 지우지 않는다. 기존 include와 CMake 의존성으로 사용하는 API가 이미 제공된다.

새 매크로의 1U는 수동 콘솔 기능을 켠다는 뜻이다. 부팅 시 ARM/CMD를 자동 전송하지 않는다.
기존 네 자동 시험 hook 중 하나라도 켜져 있으면 빌드를 막는다.

```c
/* Manual bench console: one attempted M1 pulse per ESP boot. */
#define BRIDGE_M1_PULSE_TEST_ENABLED 1U
#define BENCH_RESPONSE_MS 200U
#define BENCH_TELEMETRY_MAX_AGE_MS 250U
#define BENCH_STOP_OBSERVE_MS 600U

#if BRIDGE_M1_PULSE_TEST_ENABLED && (BRIDGE_SCRIPTED_TEST_ENABLED || BRIDGE_MALFORMED_COMMAND_TEST_ENABLED || BRIDGE_P04B_ESTOP_RESET_TEST_ENABLED || BRIDGE_T004_ESTOP_PWM_TEST_ENABLED)
#error "Disable all automatic bridge test hooks for the manual bench console"
#endif

#if BRIDGE_M1_PULSE_TEST_ENABLED && (!defined(CONFIG_ESP_CONSOLE_UART_NUM) || CONFIG_ESP_CONSOLE_UART_NUM != 0)
#error "The manual bench console requires the UART0 console"
#endif

typedef enum {
    BENCH_IDLE = 0,
    BENCH_WAIT_RESET,
    BENCH_WAIT_ARM,
    BENCH_WAIT_STOP,
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
            "BENCH: RESET_ESTOP, M1_PULSE, STOP; "
            "one M1 5%% / 300ms timeout pulse per boot");
        return;
    }

    if(strcmp(command, "STOP") == 0){
        bridge_bench_finish(seq, "operator STOP");
        return;
    }

    if(strcmp(command, "RESET_ESTOP") != 0 &&
       strcmp(command, "M1_PULSE") != 0){
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
        ESP_LOGW(TAG, "BENCH: M1_PULSE requires DISARMED and CPS=0/0");
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
            bridge_bench_wait(BENCH_WAIT_STOP, cmd_seq, now);
            if(!bridge_uart_send_cmd(cmd_seq, 25, -125, 300U)){
                bridge_bench_finish(seq, "CMD TX failed; no retry");
                return;
            }
            ESP_LOGW(TAG, "BENCH: single M1 5%% CMD sent; no refresh");
        }
        return;
    }

    if(s_telemetry.right_pwm != 0 ||
       (s_telemetry.left_pwm != 0 && s_telemetry.left_pwm != 50)){
        bridge_bench_finish(seq, "unexpected applied PWM");
        return;
    }

    if(matching_tel && strcmp(s_telemetry.state, "ARMED") == 0 &&
       s_telemetry.left_pwm == 50){
        s_bench_saw_output = true;
    }

    if(matching_tel && strcmp(s_telemetry.state, "DISARMED") == 0 &&
       strcmp(s_telemetry.reason, "CMD_TIMEOUT") == 0 &&
       bridge_bench_pwm_zero()){
        bridge_bench_finish(seq, s_bench_saw_output
            ? "PWM 50/0 then CMD_TIMEOUT 0/0 observed; inspect actual motor"
            : "timeout observed, active PWM TEL missing; result incomplete");
        return;
    }

    if(elapsed >= pdMS_TO_TICKS(BENCH_STOP_OBSERVE_MS)){
        bridge_bench_finish(seq, "stop confirmation missing; check S0");
    }
}

static void bridge_bench_console_init(void){
    if(BRIDGE_M1_PULSE_TEST_ENABLED == 0U){
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
    if(BRIDGE_M1_PULSE_TEST_ENABLED == 0U || seq == NULL){
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
            else {
                s_bench_line[s_bench_line_len++] = (char)ch;
            }
        }
    }

    bridge_bench_advance(now, seq);
}
```

## 2. app_main에 연결하는 두 곳

같은 파일에서 `app_main()` 시작 부분의 다음 두 줄:

```c
    bridge_uart_init();
    ESP_LOGI(TAG, "UART1 init done: TX=GPIO%d RX=GPIO%d baud=%d",
```

사이에 초기화 호출을 추가한다. 아래처럼 되어야 한다. 뒤의 기존 로그 인수는 유지한다.

```c
    bridge_uart_init();
    bridge_bench_console_init();
    ESP_LOGI(TAG, "UART1 init done: TX=GPIO%d RX=GPIO%d baud=%d",
```

`while(1)` 안의 다음 두 줄:

```c
        TickType_t now = xTaskGetTickCount();
        bridge_uart_startup_step(now);
```

바로 다음에 poll을 추가한다. 전체 묶음은 다음과 같다.

```c
        TickType_t now = xTaskGetTickCount();
        bridge_uart_startup_step(now);
        bridge_bench_console_poll(now, &test_seq);
```

## 코드의 흐름과 변수

```text
부팅 -> 기존 startup -> IDLE (아무 명령도 자동 전송하지 않음)
RESET_ESTOP 입력 -> WAIT_RESET -> 같은 seq의 새 DISARMED/ESTOP_RESET TEL -> IDLE
M1_PULSE 입력 -> WAIT_ARM -> 같은 seq의 새 ARMED/PWM0 TEL
             -> CMD 한 번 -> WAIT_STOP -> CMD_TIMEOUT/PWM0 TEL -> FINISHED
STOP / 통신 오류 / 확인 시간 초과 -> DISARM 시도 -> FINISHED
```

여기서 “자동 명령 없음”은 새 bench 기능의 ARM/CMD를 뜻한다. 기존 startup DISARM/PING은 유지한다.
Reset 해제와 구동 시작을 별도 사용자 명령으로 구분했다. S0 해제만으로 ARM/CMD를 보내지 않는다.
UART ACK를 출력하는 기존 코드는 유지한다. 이 새 기능의 단계 전환 근거는 **해당 seq와 일치하는 새 TEL**이다.

| 변수 | 의미 |
| --- | --- |
| `s_bench_state` | 시험이 어느 단계인지. FINISHED에서 재구동하지 않음 |
| `s_bench_expected_seq` | 지금 기다리는 요청 번호. 이전 요청 응답으로 진행하지 않음 |
| `s_bench_tel_mark` | 요청할 때의 TEL 수. 요청 이전 TEL을 새 결과로 재사용하지 않음 |
| `s_bench_last_tel_tick` | ESP가 새 TEL을 받은 시각. STM의 t_ms와 섞어서 비교하지 않음 |
| `s_bench_phase_tick` | 현재 단계 시작 시각. 응답 대기/정지 확인 제한에 사용 |
| `s_bench_err_mark`, `s_bench_parse_mark` | 단계 중 ERR 또는 파싱 오류가 추가되면 중단 |
| `s_bench_saw_output` | PWM 50/0 TEL을 실제 받았는지. 못 받으면 결과 불충분으로 표시 |
| `s_bench_line*` | 콘솔 입력을 줄 단위로 조립. 긴 줄·제어문자가 섞인 줄은 버림 |

200ms는 ARM 응답을 기다리는 상한이며 STM32의 300ms ARM-only timeout보다 짧다.
250ms는 ESP가 허용하는 TEL 수신 공백, 600ms는 명령 뒤 정지 상태 관측을 기다리는 상한이다.
600ms 동안 모터에 계속 명령을 보낸다는 뜻은 아니다. CMD는 1개이고 STM32는 300ms로 차단한다.
S0/K1은 별도의 물리 차단 경로로 유지한다.

## 입력 후 이번 단계의 종료 조건

1. 저장 후 Codex가 실제 파일을 재검토한다. 이 문서만 보고 바로 LiPo를 연결하지 않는다.
2. 그 뒤 사용자가 ESP를 빌드·플래시한다. STM32는 기능 변경이 없으므로 이번 기능에 STM 재플래시는 필요하지 않다.
3. **LiPo 분리 상태에서 `HELP`만 입력**해 콘솔 수신을 검증한다.
   모니터 입력에 에코가 없어도 Enter 후 `BENCH: RESET_ESTOP, M1_PULSE, STOP` 안내가 나오면 입력 경로는 확인된다.
4. 이 단계의 PASS는 부팅 후 자동 ARM/CMD 없음과 HELP 응답이다. 실제 PWM·모터 구동 PASS가 아니다.

전력단을 켜고 RESET_ESTOP/M1_PULSE를 사용하는 실제 회전 시험은 소스·빌드·입력 경로 검토 이후 별도 안내한다.
부팅마다 구동하거나 기존 T004 CMD 반복 시험을 사용하는 방식은 이번 수동 시작·1회 종료 요구와 맞지 않는다.
시험 종료 후에는 `BRIDGE_M1_PULSE_TEST_ENABLED`를 0U로 되돌리고 사용자 빌드·플래시로 복구한다.

참고: [Espressif UART API](https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32s3/api-reference/peripherals/uart.html).
실제 선언 확인은 설치된 `C:/esp/v6.0.2/esp-idf/components/esp_driver_uart/include/driver/uart.h`를 사용했다.
