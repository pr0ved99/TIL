# STM32 UART MVP 상세 구현 가이드

## 목적

이 문서는 STM32CubeIDE에서 NUCLEO-F446RE firmware를 실제로 작성해 PC Web Serial Dashboard 또는 terminal tool과 UART MVP protocol을 검증하기 위한 상세 구현 가이드다.

기준 목표:

```text
PC -> USART2 RX interrupt -> ring buffer -> line parser -> state machine
STM32 -> PONG / ACK / ERR / TEL
```

이번 단계에서 하지 않는 것:

- MDD10A PWM 실제 출력
- DC motor 연결
- LiPo 전원 연결
- encoder 실제 counting
- IMU 연결
- FreeRTOS 도입
- LL/direct register 전환

이번 단계에서 하는 것:

- USART2 115200 8N1 설정
- RX interrupt 기반 byte 수신
- ring buffer 저장
- `\n` 기준 line 조립
- MVP frame parsing
- `ACK`, `ERR`, `PONG`, `TEL` 송신
- `DISARMED`, `ARMED`, `FAULT` 상태 관리
- command timeout 후 output zero 상태 확인

## 완료 기준

PC dashboard 또는 terminal tool에서 다음이 확인되면 완료로 본다.

| PC TX | STM32 RX 처리 | STM32 TX |
| --- | --- | --- |
| `PING,seq=1` | link check | `PONG,seq=1,t_ms=...` |
| `CMD,seq=2,vx_mmps=80,w_mradps=0,timeout_ms=300` before ARM | motion command reject | `ERR,seq=2,type=CMD,code=NOT_ARMED` |
| `ARM,seq=3` | state transition | `ACK,seq=3,type=ARM` |
| valid `CMD,seq=4,...` | active command update | `ACK,seq=4,type=CMD` |
| missing field `CMD` | parser reject | `ERR,code=MISSING_FIELD` |
| out-of-range `CMD` | range reject | `ERR,code=OUT_OF_RANGE` |
| no valid CMD after timeout | output zero | periodic `TEL`에서 `left_pwm=0,right_pwm=0` |
| `DISARM,seq=8` | state transition | `ACK,seq=8,type=DISARM` and later `TEL,state=DISARMED` |

## 0. 작업 폴더 권장

CubeIDE project는 다음 위치를 권장한다.

```text
Projects/Tracked_Mobile_Robot/03_Firmware/stm32_uart_mvp/
```

아직 실제 firmware project가 없다면 CubeIDE에서 새 STM32 project를 만들 때 위 경로를 workspace 또는 project location으로 사용할 수 있다.

문서와 PC 도구 위치:

```text
Projects/Tracked_Mobile_Robot/04_PC_Serial_Control/
```

## 1. CubeIDE 프로젝트 생성

### 1.1 Board 선택

STM32CubeIDE:

```text
File
-> New
-> STM32 Project
-> Board Selector
-> NUCLEO-F446RE
```

Project name 예:

```text
stm32_uart_mvp
```

### 1.2 초기 peripheral 설정

이번 MVP에서 필요한 peripheral:

| Peripheral | Purpose |
| --- | --- |
| USART2 | ST-LINK Virtual COM Port over USB |
| SysTick | `HAL_GetTick()` time base |
| GPIO | 기본 board init |

필요 없는 것:

- TIM PWM
- encoder timer
- ADC
- I2C
- CAN
- FreeRTOS

## 2. CubeMX 설정

### 2.1 USART2 설정

CubeMX `.ioc` 화면에서 USART2를 설정한다.

```text
Connectivity
-> USART2
-> Mode: Asynchronous
```

Parameter settings:

| Item | Value |
| --- | --- |
| Baud Rate | `115200 Bits/s` |
| Word Length | `8 Bits` |
| Parity | `None` |
| Stop Bits | `1` |
| Data Direction | `Receive and Transmit` |
| Hardware Flow Control | `None` |
| Oversampling | `16 Samples` |

Pin:

| Signal | Pin |
| --- | --- |
| USART2_TX | PA2 |
| USART2_RX | PA3 |

NUCLEO-F446RE에서는 USART2가 ST-LINK Virtual COM Port와 연결되어 PC에서 COM port로 보인다.

### 2.2 NVIC 설정

```text
System Core
-> NVIC
-> USART2 global interrupt
-> Enabled
```

우선순위는 기본값이어도 된다. 나중에 motor control timer가 들어오면 interrupt priority를 다시 정리한다.

### 2.3 Code generation

```text
Project
-> Generate Code
```

생성 후 확인할 것:

| File | Check |
| --- | --- |
| `Core/Src/main.c` | `MX_USART2_UART_Init()` 존재 |
| `Core/Src/stm32f4xx_it.c` | `USART2_IRQHandler()` 존재 |
| `Core/Src/usart.c` 또는 `main.c` | `UART_HandleTypeDef huart2` 존재 |

프로젝트 구조는 CubeIDE 설정에 따라 `usart.c`가 생길 수도 있고, `main.c` 안에 init 함수가 있을 수도 있다.

## 3. 추가할 파일

권장 파일:

```text
Core/Inc/ring_buffer.h
Core/Src/ring_buffer.c
Core/Inc/uart_mvp_protocol.h
Core/Src/uart_mvp_protocol.c
```

CubeIDE에서:

```text
Core/Inc 우클릭 -> New -> Header File
Core/Src 우클릭 -> New -> Source File
```

## 4. Ring Buffer 구현

### 4.1 역할

UART RX interrupt는 byte 단위로 들어온다.
Application frame은 한 줄 단위다.

따라서 ISR에서는 byte만 빠르게 저장하고, main loop에서 줄 단위 parser를 실행한다.

```text
ISR: rx_byte -> ring buffer
main loop: ring buffer -> line buffer -> parser
```

### 4.2 `ring_buffer.h`

```c
#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>

#define RB_SIZE 512u

typedef struct {
    volatile uint8_t buf[RB_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
    volatile uint32_t drop_count;
} ring_buffer_t;

void rb_init(ring_buffer_t *rb);
uint8_t rb_put(ring_buffer_t *rb, uint8_t b);
uint8_t rb_get(ring_buffer_t *rb, uint8_t *out);
uint16_t rb_count(const ring_buffer_t *rb);

#endif
```

### 4.3 `ring_buffer.c`

```c
#include "ring_buffer.h"

static uint16_t rb_next(uint16_t index)
{
    return (uint16_t)((index + 1u) % RB_SIZE);
}

void rb_init(ring_buffer_t *rb)
{
    rb->head = 0u;
    rb->tail = 0u;
    rb->drop_count = 0u;
}

uint8_t rb_put(ring_buffer_t *rb, uint8_t b)
{
    uint16_t next = rb_next(rb->head);
    if (next == rb->tail) {
        rb->drop_count++;
        return 0u;
    }

    rb->buf[rb->head] = b;
    rb->head = next;
    return 1u;
}

uint8_t rb_get(ring_buffer_t *rb, uint8_t *out)
{
    if (rb->head == rb->tail) {
        return 0u;
    }

    *out = rb->buf[rb->tail];
    rb->tail = rb_next(rb->tail);
    return 1u;
}

uint16_t rb_count(const ring_buffer_t *rb)
{
    if (rb->head >= rb->tail) {
        return (uint16_t)(rb->head - rb->tail);
    }
    return (uint16_t)(RB_SIZE - rb->tail + rb->head);
}
```

### 4.4 왜 interrupt disable 없이 동작하는가

이번 구조는 single producer / single consumer 구조다.

```text
producer: USART2 RX callback
consumer: main loop
```

ISR은 `head`를 전진시키고, main loop는 `tail`을 전진시킨다.
각자가 주로 다른 index를 쓰기 때문에 짧은 byte queue 용도로는 간단하게 사용할 수 있다.

주의:

- 16-bit index read/write는 STM32F4에서 자연스럽게 처리 가능하다.
- 복잡한 multi-producer 구조가 되면 critical section이 필요하다.
- DMA circular buffer로 바꾸면 설계가 달라진다.

## 5. Protocol Header 작성

### 5.1 `uart_mvp_protocol.h`

```c
#ifndef UART_MVP_PROTOCOL_H
#define UART_MVP_PROTOCOL_H

#include "main.h"
#include "ring_buffer.h"
#include <stdint.h>

#define UART_LINE_MAX 128u

#define CMD_TIMEOUT_DEFAULT_MS 300u
#define CMD_TIMEOUT_MIN_MS      50u
#define CMD_TIMEOUT_MAX_MS     500u
#define AUTO_DISARM_MS        3000u
#define TEL_PERIOD_MS          100u

#define VX_MIN_MMPS            -100
#define VX_MAX_MMPS             100
#define W_MIN_MRADPS           -500
#define W_MAX_MRADPS            500

typedef enum {
    ROBOT_BOOT = 0,
    ROBOT_DISARMED,
    ROBOT_ARMED,
    ROBOT_FAULT
} robot_state_t;

typedef struct {
    int32_t vx_mmps;
    int32_t w_mradps;
    uint32_t timeout_ms;
    uint32_t last_valid_ms;
    uint32_t seq;
    uint8_t valid;
} active_cmd_t;

typedef struct {
    uint32_t rx_count;
    uint32_t parse_error_count;
    uint32_t ack_count;
    uint32_t err_count;
    uint32_t last_rx_ms;
    uint32_t last_tel_ms;
    uint32_t timeout_started_ms;
} uart_mvp_stats_t;

void uart_mvp_init(UART_HandleTypeDef *huart);
void uart_mvp_start_rx(void);
void uart_mvp_on_rx_byte(uint8_t b);
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart);
void uart_mvp_poll(void);
void uart_mvp_update_safety(void);
void uart_mvp_send_telemetry_periodic(void);

#endif
```

## 6. Protocol Source 기본 구조

### 6.1 include와 static 변수

`uart_mvp_protocol.c`:

```c
#include "uart_mvp_protocol.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static UART_HandleTypeDef *s_uart;
static ring_buffer_t s_rx_rb;
static uint8_t s_rx_byte;

static char s_line[UART_LINE_MAX];
static uint16_t s_line_len;

static robot_state_t s_state;
static active_cmd_t s_cmd;
static uart_mvp_stats_t s_stats;

static int32_t s_left_pwm;
static int32_t s_right_pwm;
static uint32_t s_fault;
```

### 6.2 초기화

```c
void uart_mvp_init(UART_HandleTypeDef *huart)
{
    s_uart = huart;
    rb_init(&s_rx_rb);

    s_line_len = 0u;
    s_state = ROBOT_DISARMED;
    memset(&s_cmd, 0, sizeof(s_cmd));
    memset(&s_stats, 0, sizeof(s_stats));

    s_left_pwm = 0;
    s_right_pwm = 0;
    s_fault = 0u;
}
```

### 6.3 RX 시작

```c
void uart_mvp_start_rx(void)
{
    HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
}
```

### 6.4 RX byte callback에서 호출할 함수

```c
void uart_mvp_on_rx_byte(uint8_t b)
{
    rb_put(&s_rx_rb, b);
    s_stats.rx_count++;
    s_stats.last_rx_ms = HAL_GetTick();
}
```

## 7. `main.c` 연결

### 7.1 include 추가

`main.c`의 USER CODE include 영역:

```c
/* USER CODE BEGIN Includes */
#include "uart_mvp_protocol.h"
/* USER CODE END Includes */
```

### 7.2 초기화 위치

`MX_USART2_UART_Init();` 이후:

```c
/* USER CODE BEGIN 2 */
uart_mvp_init(&huart2);
uart_mvp_start_rx();
/* USER CODE END 2 */
```

만약 `huart2`가 `usart.c`에 있고 `main.c`에서 보이지 않는다면 `usart.h`가 include되어 있는지 확인한다.

### 7.3 while loop

```c
/* Infinite loop */
/* USER CODE BEGIN WHILE */
while (1)
{
    uart_mvp_poll();
    uart_mvp_update_safety();
    uart_mvp_send_telemetry_periodic();

    /* USER CODE END WHILE */
    /* USER CODE BEGIN 3 */
}
/* USER CODE END 3 */
```

주의:

- `HAL_Delay(1000)` 같은 긴 delay를 while loop에 넣지 않는다.
- delay가 길면 ring buffer는 쌓이지만 parser와 timeout 반응이 늦어진다.

## 8. RX callback 연결

`main.c` 또는 별도 source file에 HAL callback을 추가한다.

핵심은 `s_rx_byte`를 `main.c`에서 직접 만지지 않는 것이다.
`s_rx_byte`는 `uart_mvp_protocol.c` 내부 static 변수로 유지하고, HAL callback은 protocol module에 완료 이벤트만 전달한다.

`uart_mvp_protocol.h`:

```c
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart);
```

`uart_mvp_protocol.c`:

```c
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart)
{
    if (huart == s_uart) {
        uart_mvp_on_rx_byte(s_rx_byte);
        HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
    }
}
```

`main.c`:

```c
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    uart_mvp_on_rx_complete(huart);
}
```

이렇게 하면 `rx_byte` 저장 위치가 protocol module 안에 유지된다.

## 9. TX helper

`uart_mvp_protocol.c`:

```c
static void send_line(const char *line)
{
    HAL_UART_Transmit(s_uart, (uint8_t *)line, (uint16_t)strlen(line), 50);
}
```

초기 MVP에서는 blocking transmit으로 충분하다.

주의:

- response 문자열은 항상 `\n`으로 끝낸다.
- 너무 큰 TX buffer를 만들지 않는다.
- ISR 안에서 `send_line()`을 호출하지 않는다.

## 10. Response helper

```c
static void send_ack(uint32_t seq, const char *type)
{
    char tx[64];
    snprintf(tx, sizeof(tx), "ACK,seq=%lu,type=%s\n", seq, type);
    send_line(tx);
    s_stats.ack_count++;
}

static void send_err(uint32_t seq, const char *type, const char *code)
{
    char tx[96];
    snprintf(tx, sizeof(tx), "ERR,seq=%lu,type=%s,code=%s\n", seq, type, code);
    send_line(tx);
    s_stats.err_count++;
}

static void send_pong(uint32_t seq)
{
    char tx[64];
    snprintf(tx, sizeof(tx), "PONG,seq=%lu,t_ms=%lu\n", seq, HAL_GetTick());
    send_line(tx);
}
```

`%lu` warning이 나면 cast를 명시한다.

```c
(unsigned long)seq
```

STM32 GCC에서 `uint32_t`가 `unsigned long` 또는 `unsigned int`로 잡히는 경우가 있어 format warning이 날 수 있다.

## 11. Line 조립

`uart_mvp_poll()`:

```c
void uart_mvp_poll(void)
{
    uint8_t b;

    while (rb_get(&s_rx_rb, &b)) {
        if (b == '\r') {
            continue;
        }

        if (b == '\n') {
            s_line[s_line_len] = '\0';
            if (s_line_len > 0u) {
                handle_frame(s_line);
            }
            s_line_len = 0u;
            continue;
        }

        if (s_line_len >= (UART_LINE_MAX - 1u)) {
            s_line_len = 0u;
            s_stats.parse_error_count++;
            send_err(0u, "UNKNOWN", "BAD_FRAME");
            continue;
        }

        s_line[s_line_len++] = (char)b;
    }
}
```

주의:

- `\r\n`으로 들어와도 처리되도록 `\r`은 무시한다.
- line overflow가 나면 기존 line을 버린다.
- overflow frame의 seq는 알 수 없으므로 `seq=0` 또는 생략 정책을 선택해야 한다. 현재 MVP에서는 `seq=0`으로 충분하다.

## 12. 간단한 key-value parser

처음에는 복잡한 일반 parser보다 MVP field만 찾는 helper가 낫다.

```c
static uint8_t find_field(const char *frame, const char *key, char *out, size_t out_len)
{
    size_t key_len = strlen(key);
    const char *p = frame;

    while (*p != '\0') {
        const char *token_start = p;
        const char *token_end = strchr(token_start, ',');
        size_t token_len = token_end ? (size_t)(token_end - token_start) : strlen(token_start);

        if (token_len > key_len + 1u &&
            strncmp(token_start, key, key_len) == 0 &&
            token_start[key_len] == '=') {
            size_t value_len = token_len - key_len - 1u;
            if (value_len >= out_len) {
                value_len = out_len - 1u;
            }
            memcpy(out, token_start + key_len + 1u, value_len);
            out[value_len] = '\0';
            return 1u;
        }

        if (token_end == NULL) {
            break;
        }
        p = token_end + 1;
    }

    return 0u;
}
```

숫자 변환:

```c
static uint8_t parse_i32(const char *text, int32_t *out)
{
    char *end = NULL;
    long value = strtol(text, &end, 10);
    if (end == text || *end != '\0') {
        return 0u;
    }
    *out = (int32_t)value;
    return 1u;
}

static uint8_t parse_u32(const char *text, uint32_t *out)
{
    char *end = NULL;
    unsigned long value = strtoul(text, &end, 10);
    if (end == text || *end != '\0') {
        return 0u;
    }
    *out = (uint32_t)value;
    return 1u;
}
```

주의:

- `atoi()`는 실패 여부를 알기 어렵다.
- `strtol()`, `strtoul()`로 변환 실패를 확인한다.

## 13. Frame type 분기

```c
static void handle_frame(const char *frame)
{
    if (strncmp(frame, "PING", 4) == 0) {
        handle_ping(frame);
    } else if (strncmp(frame, "ARM", 3) == 0) {
        handle_arm(frame);
    } else if (strncmp(frame, "DISARM", 6) == 0) {
        handle_disarm(frame);
    } else if (strncmp(frame, "CMD", 3) == 0) {
        handle_cmd(frame);
    } else {
        s_stats.parse_error_count++;
        send_err(0u, "UNKNOWN", "UNKNOWN_TYPE");
    }
}
```

더 엄밀히 하려면 `frame type` 다음 문자가 `,` 또는 `\0`인지 확인한다.

```c
static uint8_t is_type(const char *frame, const char *type)
{
    size_t n = strlen(type);
    return strncmp(frame, type, n) == 0 && (frame[n] == ',' || frame[n] == '\0');
}
```

## 14. PING 구현

```c
static void handle_ping(const char *frame)
{
    char seq_text[16];
    uint32_t seq;

    if (!find_field(frame, "seq", seq_text, sizeof(seq_text))) {
        send_err(0u, "PING", "MISSING_FIELD");
        return;
    }

    if (!parse_u32(seq_text, &seq)) {
        send_err(0u, "PING", "BAD_VALUE");
        return;
    }

    send_pong(seq);
}
```

## 15. ARM 구현

```c
static void handle_arm(const char *frame)
{
    char seq_text[16];
    uint32_t seq;

    if (!find_field(frame, "seq", seq_text, sizeof(seq_text))) {
        send_err(0u, "ARM", "MISSING_FIELD");
        return;
    }
    if (!parse_u32(seq_text, &seq)) {
        send_err(0u, "ARM", "BAD_VALUE");
        return;
    }

    if (s_state == ROBOT_FAULT) {
        send_err(seq, "ARM", "FAULT_ACTIVE");
        return;
    }

    s_state = ROBOT_ARMED;
    s_cmd.valid = 0u;
    s_stats.timeout_started_ms = 0u;
    send_ack(seq, "ARM");
}
```

## 16. DISARM 구현

```c
static void handle_disarm(const char *frame)
{
    char seq_text[16];
    uint32_t seq;

    if (!find_field(frame, "seq", seq_text, sizeof(seq_text))) {
        send_err(0u, "DISARM", "MISSING_FIELD");
        return;
    }
    if (!parse_u32(seq_text, &seq)) {
        send_err(0u, "DISARM", "BAD_VALUE");
        return;
    }

    s_left_pwm = 0;
    s_right_pwm = 0;
    s_cmd.valid = 0u;
    s_state = ROBOT_DISARMED;
    s_stats.timeout_started_ms = 0u;

    send_ack(seq, "DISARM");
}
```

## 17. CMD 구현

### 17.1 parsing

```c
static void handle_cmd(const char *frame)
{
    char seq_text[16];
    char vx_text[16];
    char w_text[16];
    char timeout_text[16];

    uint32_t seq;
    int32_t vx;
    int32_t w;
    uint32_t timeout_ms;

    if (!find_field(frame, "seq", seq_text, sizeof(seq_text)) ||
        !find_field(frame, "vx_mmps", vx_text, sizeof(vx_text)) ||
        !find_field(frame, "w_mradps", w_text, sizeof(w_text)) ||
        !find_field(frame, "timeout_ms", timeout_text, sizeof(timeout_text))) {
        send_err(0u, "CMD", "MISSING_FIELD");
        return;
    }

    if (!parse_u32(seq_text, &seq) ||
        !parse_i32(vx_text, &vx) ||
        !parse_i32(w_text, &w) ||
        !parse_u32(timeout_text, &timeout_ms)) {
        send_err(0u, "CMD", "BAD_VALUE");
        return;
    }
```

### 17.2 range check

```c
    if (vx < VX_MIN_MMPS || vx > VX_MAX_MMPS ||
        w < W_MIN_MRADPS || w > W_MAX_MRADPS) {
        send_err(seq, "CMD", "OUT_OF_RANGE");
        return;
    }

    if (timeout_ms < CMD_TIMEOUT_MIN_MS ||
        timeout_ms > CMD_TIMEOUT_MAX_MS) {
        send_err(seq, "CMD", "TIMEOUT_TOO_LONG");
        return;
    }
```

### 17.3 state check

```c
    if (s_state == ROBOT_FAULT) {
        send_err(seq, "CMD", "FAULT_ACTIVE");
        return;
    }

    if (s_state != ROBOT_ARMED) {
        if (vx != 0 || w != 0) {
            send_err(seq, "CMD", "NOT_ARMED");
            return;
        }
    }
```

여기서 정책 선택지가 있다.

| 상황 | 추천 |
| --- | --- |
| `DISARMED` + nonzero CMD | `NOT_ARMED` |
| `DISARMED` + zero CMD | ignore 또는 `NOT_ARMED` |

첫 MVP에서는 단순하게 `DISARMED`에서 모든 `CMD`를 `NOT_ARMED`로 거부해도 된다.
대시보드 검증이 더 명확해진다.

### 17.4 active command update

```c
    s_cmd.seq = seq;
    s_cmd.vx_mmps = vx;
    s_cmd.w_mradps = w;
    s_cmd.timeout_ms = timeout_ms;
    s_cmd.last_valid_ms = HAL_GetTick();
    s_cmd.valid = 1u;
    s_stats.timeout_started_ms = 0u;

    /* Motor power is not connected in this MVP.
       Keep actual PWM output zero. */
    s_left_pwm = 0;
    s_right_pwm = 0;

    send_ack(seq, "CMD");
}
```

중요:

- 이번 단계에서는 valid CMD가 들어와도 실제 PWM을 내보내지 않는다.
- `left_pwm/right_pwm`은 telemetry field로만 둔다.
- MDD10A 연결 전까지 motor output은 0이다.

## 18. Timeout 구현

```c
void uart_mvp_update_safety(void)
{
    uint32_t now = HAL_GetTick();

    if (s_state == ROBOT_ARMED && s_cmd.valid) {
        if ((now - s_cmd.last_valid_ms) > s_cmd.timeout_ms) {
            s_left_pwm = 0;
            s_right_pwm = 0;
            s_cmd.valid = 0u;
            s_stats.timeout_started_ms = now;
        }
    }

    if (s_state == ROBOT_ARMED && !s_cmd.valid) {
        if (s_stats.timeout_started_ms != 0u &&
            (now - s_stats.timeout_started_ms) > AUTO_DISARM_MS) {
            s_state = ROBOT_DISARMED;
            s_stats.timeout_started_ms = 0u;
        }
    }
}
```

해석:

```text
valid CMD 끊김
-> timeout_ms 후 output zero
-> ARMED 유지
-> AUTO_DISARM_MS 후 DISARMED 전환
```

현재 `AUTO_DISARM_MS=3000`은 lab default다.
나중에 공식 정책으로 확정되면 architecture contract에도 반영한다.

## 19. Telemetry 구현

### 19.1 state string

```c
static const char *state_to_str(robot_state_t state)
{
    switch (state) {
    case ROBOT_BOOT:
        return "BOOT";
    case ROBOT_DISARMED:
        return "DISARMED";
    case ROBOT_ARMED:
        return "ARMED";
    case ROBOT_FAULT:
        return "FAULT";
    default:
        return "FAULT";
    }
}
```

### 19.2 periodic telemetry

```c
void uart_mvp_send_telemetry_periodic(void)
{
    uint32_t now = HAL_GetTick();
    if ((now - s_stats.last_tel_ms) < TEL_PERIOD_MS) {
        return;
    }
    s_stats.last_tel_ms = now;

    char tx[160];
    snprintf(tx, sizeof(tx),
             "TEL,t_ms=%lu,state=%s,batt_mv=0,left_cps=0,right_cps=0,left_pwm=%ld,right_pwm=%ld,fault=%lu\n",
             (unsigned long)now,
             state_to_str(s_state),
             (long)s_left_pwm,
             (long)s_right_pwm,
             (unsigned long)s_fault);
    send_line(tx);
}
```

MVP에서는 `batt_mv`, `left_cps`, `right_cps`를 0으로 둔다.

나중에 연결:

| Field | Later source |
| --- | --- |
| `batt_mv` | ADC voltage divider |
| `left_cps` | TIM3 encoder count delta |
| `right_cps` | TIM5 encoder count delta |
| `left_pwm` | motor command output |
| `right_pwm` | motor command output |

## 20. Build error 대응

### 20.1 `huart2` undeclared

원인:

- `usart.h` include 누락
- CubeMX 설정에서 peripheral source split 여부 차이

해결:

`main.c`:

```c
#include "usart.h"
```

또는 `huart2`가 선언된 파일 위치를 확인한다.

### 20.2 `undefined reference to rb_put`

원인:

- `ring_buffer.c`가 project build에 포함되지 않음

해결:

- `Core/Src/ring_buffer.c`가 실제 source folder에 있는지 확인
- CubeIDE Project Explorer에서 excluded 상태가 아닌지 확인

### 20.3 format warning

예:

```text
format '%lu' expects argument of type 'long unsigned int'
```

해결:

```c
(unsigned long)seq
```

처럼 cast한다.

### 20.4 UART interrupt callback이 안 불림

확인:

- NVIC에서 USART2 global interrupt enable
- `HAL_UART_Receive_IT()`를 init 이후 한 번 호출했는지
- callback에서 다시 `HAL_UART_Receive_IT()`를 재등록했는지
- `USART2_IRQHandler()` 안에 `HAL_UART_IRQHandler(&huart2)`가 있는지

`stm32f4xx_it.c` 예:

```c
void USART2_IRQHandler(void)
{
    HAL_UART_IRQHandler(&huart2);
}
```

## 21. PC Web Dashboard 검증

### 21.1 서버 실행

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ServeWebDashboard.ps1
```

브라우저:

```text
http://localhost:8765/
```

### 21.2 테스트 순서

1. `Connect`
2. `PING`
3. `CMD` before ARM
4. `ARM`
5. `CMD`
6. `Bad Range`
7. `Keepalive`
8. `DISARM`

### 21.3 기대 로그

```text
TX PING,seq=1
RX PONG,seq=1,t_ms=...

TX CMD,seq=2,vx_mmps=80,w_mradps=0,timeout_ms=300
RX ERR,seq=2,type=CMD,code=NOT_ARMED

TX ARM,seq=3
RX ACK,seq=3,type=ARM
RX TEL,t_ms=...,state=ARMED,...

TX CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300
RX ACK,seq=4,type=CMD

TX CMD,seq=5,vx_mmps=9999,w_mradps=0,timeout_ms=300
RX ERR,seq=5,type=CMD,code=OUT_OF_RANGE

TX DISARM,seq=6
RX ACK,seq=6,type=DISARM
RX TEL,t_ms=...,state=DISARMED,...
```

## 22. Terminal scripted test

Windows:

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode ScriptedTest -Port COM5
```

Ubuntu:

```bash
cd ~/workspace/TIL/Projects/Tracked_Mobile_Robot/04_PC_Serial_Control
bash tools/uart_mvp_tool.sh scripted-test --port /dev/ttyACM0
```

## 23. Evidence 정리

검증 후 남길 것:

```text
04_PC_Serial_Control/logs/*_raw.log
04_PC_Serial_Control/logs/*_parsed.csv
web dashboard screenshot
CubeMX USART2 setting screenshot
STM32 parser code snippet
```

진행 로그에 적을 요약 예:

```text
USART2 RX interrupt stores incoming bytes into a ring buffer. The main-loop parser reconstructs newline-delimited UART MVP frames, validates required fields and ranges, and returns PONG/ACK/ERR/TEL. PC Web Serial dashboard confirmed PING/PONG, NOT_ARMED rejection, valid CMD ACK, OUT_OF_RANGE rejection, timeout zero-output telemetry, and DISARMED telemetry.
```

## 24. 다음 단계

이 MVP가 통과하면 다음 순서로 확장한다.

1. `left_pwm/right_pwm`을 실제 PWM target variable과 연결한다.
2. MDD10A logic input test에서 PWM waveform을 측정한다.
3. Encoder voltage safety test 후 TIM encoder mode를 연결한다.
4. `left_cps/right_cps`를 실제 encoder delta로 대체한다.
5. Battery ADC가 준비되면 `batt_mv`를 실제 값으로 대체한다.
6. ESP32 USART1 link로 같은 protocol을 옮긴다.
7. CAN version command/telemetry contract를 later phase에서 설계한다.
