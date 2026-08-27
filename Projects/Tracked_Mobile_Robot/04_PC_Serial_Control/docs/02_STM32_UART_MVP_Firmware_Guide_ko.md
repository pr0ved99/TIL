# STM32 UART MVP Firmware Guide

## Purpose

이 문서는 PC에서 보내는 UART MVP frame을 STM32 NUCLEO-F446RE가 받아 `ACK`, `ERR`, `TEL`로 응답하도록 만드는 단계별 firmware guide다.

더 세부적인 STM32CubeMX/CubeIDE 클릭 절차, project 생성, CubeIDE import, file-by-file code skeleton은
`06_STM32_UART_MVP_Detailed_Implementation_ko.md`를 기준으로 한다.
CubeMX/CubeIDE 설정 스크린샷과 Web Serial 검증 스크린샷은 `assets/screenshots/uart_mvp/`에 저장하고, 상세 가이드의 `0.5 스크린샷 증거 반영 방식`에 따라 해당 절차 아래에 이미지로 반영한다.

초기 목표는 motor control이 아니다.
이번 firmware는 USB serial 기반 protocol 검증용이다.

> 이 문서는 2026-07-09 PC-first USART2 bench 실습을 보존하는 historical guide다.
> Final MVP production 경로는 ADR-015의 `ESP32 UART1 -> STM32 USART1`이며, USART2는
> production command RX로 사용하지 않는다. 아래 timeout 동작은 ADR-015 기준으로 갱신했다.

```text
PC tool
-> ST-LINK Virtual COM Port
-> STM32 USART2 RX interrupt
-> ring buffer
-> parser
-> safety state machine
-> ACK / ERR / TEL
```

## Hardware Scope

연결:

```text
PC USB <-> NUCLEO-F446RE ST-LINK USB
```

연결하지 않는 것:

- MDD10A
- DC motor
- 3S LiPo
- buck converter
- encoder
- IMU

이번 단계에서 `left_pwm`, `right_pwm`, `left_cps`, `right_cps`, `batt_mv`는 0으로 보낼 수 있다.

## STM32CubeMX / CubeIDE Configuration

### 1. Project

- Board: `NUCLEO-F446RE`
- Project creation: standalone STM32CubeMX 설치/실행 후 Board Selector에서 `NUCLEO-F446RE` 선택, code generation
- Toolchain: STM32CubeIDE 또는 CMake
- Firmware style: HAL baseline

현재 CubeIDE에서 `File -> New -> STM32 Project`가 보이지 않으면 `STM32CubeIDE Empty Project`로 시작하지 않는다.
이 경우 standalone STM32CubeMX에서 `.ioc`와 HAL baseline code를 먼저 생성한 뒤 CubeIDE에서 open/import한다.

### 2. USART2

NUCLEO-F446RE의 ST-LINK Virtual COM Port는 일반적으로 USART2에 연결된다.

설정:

| Item | Value |
| --- | --- |
| Peripheral | USART2 |
| Mode | Asynchronous |
| Baud rate | 115200 |
| Word length | 8 bits |
| Parity | None |
| Stop bits | 1 |
| Hardware flow control | None |
| NVIC | USART2 global interrupt enable |

Pin:

| Function | Pin |
| --- | --- |
| USART2_TX | PA2 |
| USART2_RX | PA3 |

### 3. Timer

이번 MVP에서는 별도 hardware timer 없이 `HAL_GetTick()`으로 `t_ms`, command timeout, telemetry period를 처리해도 된다.

나중에 control loop가 들어가면 TIM 기반 주기 task로 옮긴다.

## Firmware Constants

초기 lab default:

```c
#define UART_RX_RING_SIZE      512u
#define UART_LINE_MAX          128u
#define CMD_TIMEOUT_DEFAULT_MS 300u
#define CMD_TIMEOUT_MIN_MS      50u
#define CMD_TIMEOUT_MAX_MS     500u
#define TEL_PERIOD_MS          100u

#define VX_MIN_MMPS            -100
#define VX_MAX_MMPS             100
#define W_MIN_MRADPS           -500
#define W_MAX_MRADPS            500
```

Timeout은 별도 auto-disarm delay 없이 output/stored command를 zero로 만들고 즉시
`DISARMED`로 전환한다.

## Module Split

처음에는 `main.c` 하나에 넣어도 되지만, 포트폴리오용으로는 다음 분리를 권장한다.

```text
Core/Src/main.c
Core/Src/uart_mvp_protocol.c
Core/Inc/uart_mvp_protocol.h
Core/Src/ring_buffer.c
Core/Inc/ring_buffer.h
```

초기에는 너무 큰 구조보다 다음 책임만 분명하면 된다.

| Module | Responsibility |
| --- | --- |
| `main.c` | HAL init, super loop, periodic telemetry |
| `ring_buffer` | ISR producer, main consumer byte queue |
| `uart_mvp_protocol` | frame parse, command validation, response formatting |
| state machine | `BOOT`, `DISARMED`, `ARMED`, `FAULT` 상태와 timeout 처리 |

## Data Structures

상태:

```c
typedef enum {
    ROBOT_BOOT = 0,
    ROBOT_DISARMED,
    ROBOT_ARMED,
    ROBOT_FAULT
} robot_state_t;
```

Active command:

```c
typedef struct {
    int32_t vx_mmps;
    int32_t w_mradps;
    uint32_t timeout_ms;
    uint32_t last_valid_ms;
    uint32_t seq;
    uint8_t valid;
} active_cmd_t;
```

Runtime counters:

```c
typedef struct {
    uint32_t rx_count;
    uint32_t parse_error_count;
    uint32_t ack_count;
    uint32_t err_count;
    uint32_t last_rx_ms;
    uint32_t last_tel_ms;
} uart_mvp_stats_t;
```

## RX Interrupt Rule

ISR에서는 heavy parsing을 하지 않는다.

ISR 역할:

1. 수신 byte 읽기
2. ring buffer에 push
3. 다음 byte interrupt receive 재등록
4. 즉시 return

HAL callback 형태:

```c
static uint8_t rx_byte;

void uart_rx_start(void)
{
    HAL_UART_Receive_IT(&huart2, &rx_byte, 1);
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2) {
        rb_put(&rx_rb, rx_byte);
        HAL_UART_Receive_IT(&huart2, &rx_byte, 1);
    }
}
```

주의:

- `printf`를 ISR 안에서 하지 않는다.
- `strtok`, `sscanf`, 큰 buffer parsing을 ISR 안에서 하지 않는다.
- overflow가 발생하면 drop counter만 올린다.

## Main Loop Flow

Super loop:

```c
int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();

    uart_rx_start();
    robot_state = ROBOT_DISARMED;

    while (1) {
        uart_mvp_poll_rx();
        uart_mvp_update_safety();
        uart_mvp_send_telemetry_periodic();
    }
}
```

`uart_mvp_poll_rx()`:

1. ring buffer에서 byte를 꺼낸다.
2. `\n`까지 line buffer에 모은다.
3. line이 너무 길면 line buffer를 버리고 `ERR,code=BAD_FRAME` 또는 parse error count 증가.
4. complete line을 parser로 넘긴다.

## Parser Rule

지원 frame:

```text
PING,seq=<u32>
ARM,seq=<u32>
DISARM,seq=<u32>
CMD,seq=<u32>,vx_mmps=<i32>,w_mradps=<i32>,timeout_ms=<u32>
```

응답:

```text
PONG,seq=<u32>,t_ms=<u32>
ACK,seq=<u32>,type=<text>
ERR,seq=<u32>,type=<text>,code=<text>
```

Parser 순서:

1. frame type 확인
2. key-value field 분리
3. required field 존재 확인
4. 숫자 변환 확인
5. range 확인
6. safety state 확인
7. command 적용 또는 reject
8. response transmit

Error priority 권장:

| Priority | Condition | Error |
| --- | --- | --- |
| 1 | frame type 없음 또는 key/value 문법 깨짐 | `BAD_FRAME` |
| 2 | 지원하지 않는 frame type | `UNKNOWN_TYPE` |
| 3 | required field 없음 | `MISSING_FIELD` |
| 4 | 숫자 변환 실패 | `BAD_VALUE` |
| 5 | 범위 초과 | `OUT_OF_RANGE` |
| 6 | `DISARMED` 상태 nonzero `CMD` | `NOT_ARMED` |
| 7 | fault active | `FAULT_ACTIVE` |

## Command Behavior

### PING

Input:

```text
PING,seq=1
```

Output:

```text
PONG,seq=1,t_ms=1234
```

### ARM

초기 parser-only lab에서는 큰 fault가 없으면 accept한다.

Input:

```text
ARM,seq=2
```

State:

```text
DISARMED -> ARMED
```

Output:

```text
ACK,seq=2,type=ARM
```

### DISARM

Valid frame이면 항상 accept한다.

State:

```text
ANY -> DISARMED
left_pwm = 0
right_pwm = 0
active_cmd.valid = 0
```

Output:

```text
ACK,seq=3,type=DISARM
```

### CMD

Valid example:

```text
CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300
```

Accept 조건:

- required field가 모두 있음
- 숫자 변환 성공
- range 안에 있음
- state가 `ARMED`
- fault가 없음

Accept output:

```text
ACK,seq=4,type=CMD
```

Reject example:

```text
ERR,seq=4,type=CMD,code=NOT_ARMED
```

## Timeout Behavior

MVP rule:

1. `ARMED` 상태에서 valid `CMD`가 들어오면 `last_valid_ms`를 갱신한다.
2. `HAL_GetTick() - last_valid_ms > timeout_ms`이면 output을 즉시 0으로 만든다.
3. Stored command를 zero/invalid로 만들고 즉시 `DISARMED`로 전환한다.
4. 재동작에는 new `ARM` 뒤 new `CMD`가 필요하다.

Pseudo:

```c
void uart_mvp_update_safety(void)
{
    uint32_t now = HAL_GetTick();

    if (robot_state == ROBOT_ARMED && active_cmd.valid) {
        if ((now - active_cmd.last_valid_ms) > active_cmd.timeout_ms) {
            left_pwm = 0;
            right_pwm = 0;
            active_cmd.vx_mmps = 0;
            active_cmd.w_mradps = 0;
            active_cmd.valid = 0;
            robot_state = ROBOT_DISARMED;
        }
    }
}
```

## Telemetry

10 Hz로 전송한다.

```text
TEL,t_ms=123456,state=ARMED,batt_mv=0,left_cps=0,right_cps=0,left_pwm=0,right_pwm=0,fault=0
```

Parser-only lab에서는 다음 값을 0으로 둬도 된다.

- `batt_mv`
- `left_cps`
- `right_cps`
- `left_pwm`
- `right_pwm`

State string mapping:

```c
const char *state_to_str(robot_state_t state)
{
    switch (state) {
    case ROBOT_BOOT: return "BOOT";
    case ROBOT_DISARMED: return "DISARMED";
    case ROBOT_ARMED: return "ARMED";
    case ROBOT_FAULT: return "FAULT";
    default: return "FAULT";
    }
}
```

## TX Helper

HAL transmit은 초기 lab에서는 blocking transmit으로 충분하다.

```c
static void uart_send_line(const char *line)
{
    HAL_UART_Transmit(&huart2, (uint8_t *)line, strlen(line), 50);
}
```

응답은 반드시 `\n`으로 끝낸다.

```c
snprintf(tx_buf, sizeof(tx_buf), "ACK,seq=%lu,type=CMD\n", seq);
uart_send_line(tx_buf);
```

## Verification Sequence

PC scripted test에 맞춰 다음을 확인한다.

| Step | PC TX | Expected STM32 behavior |
| --- | --- | --- |
| 1 | `PING,seq=1` | `PONG,seq=1,t_ms=...` |
| 2 | `CMD,seq=2,...` while `DISARMED` | `ERR,seq=2,type=CMD,code=NOT_ARMED` |
| 3 | `ARM,seq=3` | `ACK,seq=3,type=ARM`, state becomes `ARMED` |
| 4 | valid `CMD,seq=4,...` | `ACK,seq=4,type=CMD` |
| 5 | missing field `CMD` | `ERR,code=MISSING_FIELD` |
| 6 | out-of-range `CMD` | `ERR,code=OUT_OF_RANGE` |
| 7 | stop sending valid `CMD` | output zero appears in `TEL` |
| 8 | `DISARM,seq=8` | `ACK,seq=8,type=DISARM`, later `TEL,state=DISARMED` |

## Evidence To Save

PC 쪽:

- `logs/*_raw.log`
- `logs/*_parsed.csv`
- scripted-test terminal screenshot

STM32 쪽:

- CubeMX USART2 configuration screenshot
- main loop/parser code snippet
- timeout handling code snippet

프로젝트 문서에 남길 요약:

```text
STM32 USART2 interrupt receives UART bytes into a ring buffer, main-loop parser validates line-based MVP frames, and STM32 returns ACK/ERR/TEL according to the safety state. PC logs confirm PING/PONG, NOT_ARMED rejection, valid CMD ACK, malformed CMD ERR, timeout zero-output, and DISARMED telemetry.
```

## 이 Historical MVP 이후 상태

1. `[COMPLETED]` 같은 protocol을 ESP32 UART1 <-> STM32 USART1 link로 연결했다.
2. `[COMPLETED — motor-disconnected MDD10A-input scope]` PWM/DIR logic input waveform을 검증했다.
3. `[P-02]` `left_pwm/right_pwm`을 production mapper의 실제 target output으로 연결한다.
4. `[COMPLETED — encoder-side scope]` 실제 encoder CPS를 `left_cps/right_cps` telemetry에 연결했다.
5. `[P-03]` ADR-015 timeout-to-`DISARMED` recovery를 구현·검증하고 actual motor test 전
   command limit과 timeout을 다시 확인한다.

## Detailed Implementation

실제 STM32CubeMX에서 project를 생성하고 CubeIDE에서 파일을 추가해 코드를 나눠 넣는 상세 절차는 다음 문서를 따른다.

- `06_STM32_UART_MVP_Detailed_Implementation_ko.md`
