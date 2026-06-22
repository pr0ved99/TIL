# STM32 UART MVP 상세 구현 가이드

## 목적

이 문서는 `NUCLEO-F446RE` 보드에서 PC Web Serial Dashboard 또는 terminal tool과 UART MVP protocol을 검증하기 위한 STM32 firmware 상세 구현 가이드다.

현재 개발 흐름은 다음을 기준으로 한다.

```text
STM32CubeMX
-> NUCLEO-F446RE board selection
-> USART2 / NVIC / code generation
-> STM32CubeIDE import or open
-> user firmware files 추가
-> build / flash / UART 검증
```

예전 STM32CubeIDE 버전처럼 `File -> New -> STM32 Project`가 보이지 않는 환경에서는 `STM32CubeIDE Empty Project`를 선택하지 않는다. 이 프로젝트는 `.ioc`, HAL initialization, pin mapping 자동 생성을 활용해야 하므로 standalone `STM32CubeMX`에서 먼저 project를 생성한다.

기준 목표:

```text
PC
-> ST-LINK Virtual COM Port
-> STM32 USART2 RX interrupt
-> ring buffer
-> line parser
-> command/state machine
-> STM32 PONG / ACK / ERR / TEL
```

## 이번 단계의 범위

이번 단계에서 하는 것:

- STM32CubeMX에서 `NUCLEO-F446RE` board 기반 project 생성
- USART2 115200 8N1 설정
- USART2 global interrupt enable
- RX interrupt 기반 byte 수신
- ring buffer 저장
- `\n` 기준 line 조립
- UART MVP frame parsing
- `PING`, `ARM`, `DISARM`, `CMD` 처리
- `PONG`, `ACK`, `ERR`, `TEL` 송신
- `DISARMED`, `ARMED`, `FAULT` 상태 관리
- command timeout 후 output zero 상태 확인

이번 단계에서 하지 않는 것:

- MDD10A PWM 실제 출력
- DC motor 연결
- LiPo 전원 연결
- encoder 실제 counting
- IMU 연결
- FreeRTOS 도입
- LL/direct register 전환

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

## 0. 준비: STM32CubeMX 설치와 폴더 구조

### 0.1 왜 STM32CubeMX를 따로 쓰는가

현재 설치된 STM32CubeIDE 환경에서는 예전 튜토리얼에서 보던 다음 메뉴가 보이지 않을 수 있다.

```text
File
-> New
-> STM32 Project
```

대신 다음 항목만 보일 수 있다.

```text
STM32CubeIDE Empty Project
C Project
C++ Project
STM32 CMake Project
Import STM32 Project
```

이 경우 `STM32CubeIDE Empty Project`로 시작하지 않는다.
Empty Project는 `.ioc`, board preset, GPIO alternate function, USART init code를 자동 생성하는 흐름이 아니기 때문이다.

이번 실습에서는 다음 흐름을 사용한다.

```text
STM32CubeMX 설치/실행
-> Board Selector에서 NUCLEO-F446RE 선택
-> USART2 / NVIC 설정
-> code generation
-> STM32CubeIDE에서 open 또는 import
```

### 0.2 설치해야 할 도구

필요 도구:

| Tool | Purpose |
| --- | --- |
| STM32CubeMX | board selection, `.ioc`, pin/peripheral 설정, HAL code generation |
| STM32CubeIDE | generated firmware project build, flash, debug |
| ST-LINK driver | NUCLEO-F446RE flash/debug and Virtual COM Port |

권장:

- STM32CubeIDE는 이미 설치되어 있어도 된다.
- STM32CubeMX는 standalone application으로 따로 설치한다.
- STM32CubeIDE 안에 `STM32 Project` 메뉴가 없으면 CubeMX-first workflow를 사용한다.

설치 후 Windows 시작 메뉴에서 다음을 찾는다.

```text
STM32CubeMX
STM32CubeIDE
```

### 0.3 CubeIDE workspace

권장 firmware project 위치:

```text
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware\stm32_uart_mvp
```

PC test tool 위치:

```text
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
```

CubeIDE workspace는 기본 경로를 써도 된다.

```text
C:\Users\eyh12\STM32CubeIDE\workspace_2.1.1
```

CubeIDE workspace는 IDE metadata와 cache 성격이 강하다. Git으로 관리할 실제 firmware source는 `03_Firmware/stm32_uart_mvp` 아래에 둔다.

### 0.4 Git으로 관리할 위치

실제 firmware source는 다음 경로 아래에 만든다.

```text
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware\stm32_uart_mvp
```

CubeMX가 code generation을 하면 이 project 안에 다음 파일들이 생긴다.

```text
stm32_uart_mvp.ioc
Core/
Drivers/
STM32F446RETX_FLASH.ld
startup_stm32f446retx.s
```

이 파일들이 나중에 Git으로 관리할 실제 firmware 산출물이다.

## 1. STM32CubeMX에서 Project 생성

### 1.1 STM32CubeMX 실행

Windows 시작 메뉴에서 `STM32CubeMX`를 실행한다.

시작 화면에서 다음을 선택한다.

```text
ACCESS TO BOARD SELECTOR
```

이번 프로젝트는 ST Nucleo 개발보드를 사용하므로 `MCU Selector`보다 `Board Selector`를 사용한다.

| Selector | 언제 쓰는가 |
| --- | --- |
| Board Selector | NUCLEO-F446RE처럼 ST board 전체를 사용할 때 |
| MCU Selector | 직접 만든 PCB 또는 칩 단품 기준으로 설정할 때 |

`Board Selector`를 쓰는 이유:

- 보드의 MCU가 `STM32F446RE`임을 자동으로 잡는다.
- ST-LINK와 Virtual COM Port 연결 전제를 반영하기 쉽다.
- Nucleo board의 LED, button, debug 관련 기본 pin 정보를 함께 볼 수 있다.
- 이번 실습의 핵심인 `USART2 PA2/PA3` 기반 PC USB serial 검증에 적합하다.

### 1.2 Board 선택

검색창에 입력:

```text
NUCLEO-F446RE
```

`Board Selector` 결과에서 `NUCLEO-F446RE`를 선택한다.

확인할 것:

| Item | Expected |
| --- | --- |
| Board | `NUCLEO-F446RE` |
| MCU | `STM32F446RE` |
| Package | `LQFP64` 계열 |
| Vendor | STMicroelectronics |

선택 후 `Start Project`를 누른다.

`Initialize all peripherals with their default Mode?` 질문이 나오면 기본 peripheral 초기화를 허용해도 된다.

다만 이번 MVP에서 실제로 사용할 peripheral은 USART2와 SysTick 중심이다.

### 1.3 Board 선택 후 바로 확인할 것

project가 열리면 먼저 다음을 확인한다.

```text
Pinout & Configuration
```

확인 포인트:

- board가 `NUCLEO-F446RE`로 열렸는가
- MCU가 `STM32F446RE`로 잡혔는가
- PA2/PA3를 USART2로 설정할 수 있는가
- ST-LINK Virtual COM Port 용도로 USART2를 사용할 계획인지 문서와 일치하는가

이 단계에서 board를 잘못 고르면 나중에 `USART2`, pin mapping, linker script, startup file이 모두 달라질 수 있으므로 여기서 바로 잡는다.

## 2. CubeMX Peripheral 설정

### 2.1 USART2 확인

`Pinout & Configuration` 화면에서 다음을 확인한다.

```text
Connectivity
-> USART2
-> Mode: Asynchronous
```

NUCLEO-F446RE의 ST-LINK Virtual COM Port는 일반적으로 USART2와 연결된다.

설정값:

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

주의:

- PA2/PA3가 다른 peripheral로 잡혀 있으면 USART2로 다시 지정한다.
- USB cable은 Nucleo board의 ST-LINK USB port에 연결한다.
- Windows에서는 ST-LINK Virtual COM Port가 `COMx`로 보인다.

### 2.2 NVIC 설정

다음 설정을 켠다.

```text
System Core
-> NVIC
-> USART2 global interrupt
-> Enabled
```

초기 MVP에서는 interrupt priority 기본값을 사용해도 된다. 나중에 motor control timer, encoder, watchdog이 들어오면 priority를 다시 정리한다.

### 2.3 Clock 설정

이번 UART MVP는 고속 clock tuning이 핵심이 아니다.

우선 다음 중 하나로 진행한다.

| 선택 | 설명 |
| --- | --- |
| CubeMX default clock | 가장 단순한 시작점 |
| Nucleo board default clock | CubeMX가 board preset으로 잡아주는 설정 |

중요한 것은 USART2 baudrate가 `115200`으로 생성되는지 확인하는 것이다.

## 3. Project Manager 설정

### 3.1 Project

`Project Manager -> Project`에서 다음처럼 설정한다.

| Item | Value |
| --- | --- |
| Project Name | `stm32_uart_mvp` |
| Project Location | `C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware` |
| Application Structure | `Basic` |
| Toolchain / IDE | `STM32CubeIDE` 우선 |

생성 후 예상 경로:

```text
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware\stm32_uart_mvp
```

만약 `Toolchain / IDE`에 `STM32CubeIDE`가 보이지 않고 `CMake` 중심으로만 보이면, `CMake`로 생성해도 된다. 다만 이 문서의 코드 배치는 HAL/CubeMX 생성 구조를 기준으로 설명한다.

### 3.2 Code Generator

`Project Manager -> Code Generator`에서 다음을 권장한다.

| Option | Recommendation |
| --- | --- |
| Generate peripheral initialization as a pair of `.c/.h` files per peripheral | Enable |
| Keep User Code when re-generating | Enable |
| Delete previously generated files when not re-generated | Disable |

이렇게 하면 `usart.c/usart.h`, `gpio.c/gpio.h`처럼 peripheral별 파일이 나뉘어 관리된다.

권장 생성 구조:

```text
Core/Inc/main.h
Core/Inc/usart.h
Core/Inc/gpio.h
Core/Src/main.c
Core/Src/usart.c
Core/Src/gpio.c
Core/Src/stm32f4xx_it.c
```

### 3.3 Code Generate

CubeMX 상단의 다음 버튼을 누른다.

```text
GENERATE CODE
```

생성 후 확인할 파일:

| File | Check |
| --- | --- |
| `stm32_uart_mvp.ioc` | CubeMX 설정 파일 |
| `Core/Src/main.c` | `MX_USART2_UART_Init()` 호출 |
| `Core/Src/usart.c` | `UART_HandleTypeDef huart2` 정의 |
| `Core/Inc/usart.h` | `extern UART_HandleTypeDef huart2` 선언 |
| `Core/Src/stm32f4xx_it.c` | `USART2_IRQHandler()` 존재 |

`stm32f4xx_it.c` 안에는 다음 흐름이 있어야 한다.

```c
void USART2_IRQHandler(void)
{
  HAL_UART_IRQHandler(&huart2);
}
```

## 4. STM32CubeIDE로 열기

### 4.1 자동 open

CubeMX에서 code generation 후 다음과 같은 버튼이 보이면 사용한다.

```text
Open Project
```

### 4.2 CubeIDE에서 import

자동으로 열리지 않으면 STM32CubeIDE에서 가져온다.

```text
File
-> Import...
-> General
-> Existing Projects into Workspace
-> Select root directory
-> C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware\stm32_uart_mvp
-> Finish
```

또는 설치 버전에 따라 다음 import 항목을 사용할 수 있다.

```text
File
-> New
-> Other...
-> Import STM32 Project
-> STM32CubeMX/STM32CubeIDE Project
```

중요:

- `STM32CubeIDE Empty Project`로 새로 만들지 않는다.
- CubeMX가 생성한 `.ioc`, `Core`, `Drivers`, startup, linker script가 들어있는 project를 import한다.
- import 시 `Copy projects into workspace`는 체크하지 않는 편이 낫다. 실제 source가 `03_Firmware/stm32_uart_mvp`에 그대로 남아야 Git 관리가 명확하다.

## 5. 생성 직후 Build 확인

사용자 코드를 추가하기 전에 한 번 build한다.

```text
Project
-> Build Project
```

이 단계가 통과해야 이후 UART MVP code 문제와 CubeMX 생성 문제를 분리해서 볼 수 있다.

Build가 실패하면 먼저 다음을 확인한다.

- `STM32Cube_FW_F4` package가 설치되어 있는가
- project path에 한글 또는 특수문자가 들어가지 않았는가
- `Drivers/`, `Core/`, `.ioc`가 같은 project 아래에 있는가
- CubeIDE가 project root를 제대로 import했는가

## 6. 추가할 User 파일

CubeMX가 생성한 파일과 사용자가 직접 관리할 파일을 나눈다.

CubeMX 관리 파일:

```text
Core/Src/main.c
Core/Src/usart.c
Core/Src/gpio.c
Core/Src/stm32f4xx_it.c
Core/Inc/main.h
Core/Inc/usart.h
Core/Inc/gpio.h
```

사용자 추가 파일:

```text
Core/Inc/ring_buffer.h
Core/Src/ring_buffer.c
Core/Inc/uart_mvp_protocol.h
Core/Src/uart_mvp_protocol.c
```

CubeIDE에서 추가:

```text
Core/Inc 우클릭 -> New -> Header File
Core/Src 우클릭 -> New -> Source File
```

주의:

- CubeMX 재생성 시 `USER CODE BEGIN/END` 밖의 generated file 수정은 사라질 수 있다.
- 새로 추가한 `ring_buffer.*`, `uart_mvp_protocol.*` 파일은 CubeMX가 덮어쓰지 않는다.
- `main.c` 수정은 반드시 `USER CODE BEGIN/END` 영역 안에 넣는다.

## 7. Ring Buffer 구현

### 7.1 역할

UART RX interrupt는 byte 단위로 발생한다.
MVP command frame은 line 단위로 처리한다.

따라서 ISR 또는 HAL RX callback에서는 byte만 빠르게 저장하고, main loop에서 parser를 실행한다.

```text
USART2 RX interrupt
-> HAL_UART_RxCpltCallback
-> ring buffer push
-> main loop poll
-> line assembly
-> frame parser
```

### 7.2 `ring_buffer.h`

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

### 7.3 `ring_buffer.c`

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

### 7.4 Lock-free로 충분한 이유

이번 구조는 single producer / single consumer 구조다.

```text
producer: USART2 RX callback
consumer: main loop
```

RX callback은 `head`를 전진시키고, main loop는 `tail`을 전진시킨다.
STM32F4에서 16-bit index read/write는 이 용도에 충분히 단순하다.

주의:

- 여러 interrupt나 task가 동시에 같은 buffer를 만지는 구조가 되면 critical section을 검토한다.
- FreeRTOS queue나 DMA circular buffer를 도입하면 설계가 달라진다.

## 8. Protocol Header 작성

`Core/Inc/uart_mvp_protocol.h`:

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

## 9. Protocol Source 기본 구조

`Core/Src/uart_mvp_protocol.c`:

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

static void handle_frame(const char *frame);
static void handle_ping(const char *frame);
static void handle_arm(const char *frame);
static void handle_disarm(const char *frame);
static void handle_cmd(const char *frame);
```

초기화:

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

RX 시작:

```c
void uart_mvp_start_rx(void)
{
    HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
}
```

RX byte 저장:

```c
void uart_mvp_on_rx_byte(uint8_t b)
{
    rb_put(&s_rx_rb, b);
    s_stats.rx_count++;
    s_stats.last_rx_ms = HAL_GetTick();
}
```

HAL callback 완료 처리:

```c
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart)
{
    if (huart == s_uart) {
        uart_mvp_on_rx_byte(s_rx_byte);
        HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
    }
}
```

## 10. `main.c` 연결

CubeMX가 생성한 `main.c`에서는 `USER CODE` 영역만 수정한다.

### 10.1 Include 추가

```c
/* USER CODE BEGIN Includes */
#include "uart_mvp_protocol.h"
/* USER CODE END Includes */
```

`main.c` 상단에 `usart.h`가 없고 `huart2`를 찾지 못하면 다음도 확인한다.

```c
#include "usart.h"
```

CubeMX에서 peripheral별 `.c/.h` 생성을 켰다면 보통 `main.c`에 이미 포함되어 있다.

### 10.2 초기화 추가

`MX_USART2_UART_Init();` 호출 이후 `USER CODE BEGIN 2`에 넣는다.

```c
/* USER CODE BEGIN 2 */
uart_mvp_init(&huart2);
uart_mvp_start_rx();
/* USER CODE END 2 */
```

초기화 순서:

```text
HAL_Init()
SystemClock_Config()
MX_GPIO_Init()
MX_USART2_UART_Init()
uart_mvp_init(&huart2)
uart_mvp_start_rx()
```

### 10.3 Main loop 추가

```c
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

- `while (1)` 안에 긴 `HAL_Delay(1000)`를 넣지 않는다.
- delay가 길면 parser, timeout, telemetry 반응이 늦어진다.

### 10.4 UART RX callback 추가

`main.c`의 `USER CODE BEGIN 4` 영역에 넣는다.

```c
/* USER CODE BEGIN 4 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    uart_mvp_on_rx_complete(huart);
}
/* USER CODE END 4 */
```

`s_rx_byte`는 `uart_mvp_protocol.c` 안의 static 변수이므로 `main.c`에서 직접 접근하지 않는다.

## 11. TX Helper

`uart_mvp_protocol.c`에 추가한다.

```c
static void send_line(const char *line)
{
    HAL_UART_Transmit(s_uart, (uint8_t *)line, (uint16_t)strlen(line), 50);
}
```

초기 MVP에서는 blocking transmit으로 충분하다.

규칙:

- 모든 response는 `\n`으로 끝낸다.
- ISR 또는 HAL RX callback 안에서 `send_line()`을 호출하지 않는다.
- RX callback은 byte 저장과 receive 재등록만 한다.

Response helper:

```c
static void send_ack(uint32_t seq, const char *type)
{
    char tx[64];
    snprintf(tx, sizeof(tx),
             "ACK,seq=%lu,type=%s\n",
             (unsigned long)seq,
             type);
    send_line(tx);
    s_stats.ack_count++;
}

static void send_err(uint32_t seq, const char *type, const char *code)
{
    char tx[96];
    snprintf(tx, sizeof(tx),
             "ERR,seq=%lu,type=%s,code=%s\n",
             (unsigned long)seq,
             type,
             code);
    send_line(tx);
    s_stats.err_count++;
}

static void send_pong(uint32_t seq)
{
    char tx[64];
    snprintf(tx, sizeof(tx),
             "PONG,seq=%lu,t_ms=%lu\n",
             (unsigned long)seq,
             (unsigned long)HAL_GetTick());
    send_line(tx);
}
```

## 12. Line 조립

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

처리 정책:

- `\r\n` 입력을 고려해 `\r`은 무시한다.
- `\n`이 들어오면 한 frame으로 처리한다.
- line overflow가 나면 해당 line을 버리고 `ERR BAD_FRAME`을 보낸다.
- overflow frame의 `seq`를 알 수 없으므로 MVP에서는 `seq=0`을 사용한다.

## 13. Key-value Parser

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

`atoi()`는 실패 여부를 알기 어렵기 때문에 쓰지 않는다.

## 14. Frame Type 분기

```c
static uint8_t is_type(const char *frame, const char *type)
{
    size_t n = strlen(type);
    return (strncmp(frame, type, n) == 0 &&
            (frame[n] == ',' || frame[n] == '\0'));
}

static void handle_frame(const char *frame)
{
    if (is_type(frame, "PING")) {
        handle_ping(frame);
    } else if (is_type(frame, "ARM")) {
        handle_arm(frame);
    } else if (is_type(frame, "DISARM")) {
        handle_disarm(frame);
    } else if (is_type(frame, "CMD")) {
        handle_cmd(frame);
    } else {
        s_stats.parse_error_count++;
        send_err(0u, "UNKNOWN", "UNKNOWN_TYPE");
    }
}
```

`strncmp(frame, "ARM", 3)`만 사용하면 `ARMED...` 같은 문자열도 `ARM`으로 오인할 수 있으므로 `is_type()`으로 frame type 경계를 확인한다.

## 15. PING 구현

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

## 16. ARM 구현

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

## 17. DISARM 구현

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

## 18. CMD 구현

### 18.1 Parsing

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

### 18.2 Range check

```c
    if (vx < VX_MIN_MMPS || vx > VX_MAX_MMPS ||
        w < W_MIN_MRADPS || w > W_MAX_MRADPS) {
        send_err(seq, "CMD", "OUT_OF_RANGE");
        return;
    }

    if (timeout_ms < CMD_TIMEOUT_MIN_MS ||
        timeout_ms > CMD_TIMEOUT_MAX_MS) {
        send_err(seq, "CMD", "TIMEOUT_OUT_OF_RANGE");
        return;
    }
```

### 18.3 State check

```c
    if (s_state == ROBOT_FAULT) {
        send_err(seq, "CMD", "FAULT_ACTIVE");
        return;
    }

    if (s_state != ROBOT_ARMED) {
        send_err(seq, "CMD", "NOT_ARMED");
        return;
    }
```

첫 MVP에서는 `DISARMED` 상태의 모든 `CMD`를 `NOT_ARMED`로 거부한다. `zero CMD`만 예외 허용하는 정책은 나중에 필요해지면 추가한다.

### 18.4 Active command update

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

이번 단계에서는 valid `CMD`가 들어와도 실제 PWM을 내보내지 않는다.
`left_pwm/right_pwm`은 telemetry field로만 둔다.

## 19. Timeout 구현

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

## 20. Telemetry 구현

State string:

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

Periodic telemetry:

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

MVP에서는 다음 값들을 0으로 둔다.

| Field | MVP value | Later source |
| --- | --- | --- |
| `batt_mv` | `0` | ADC voltage divider |
| `left_cps` | `0` | left encoder timer delta |
| `right_cps` | `0` | right encoder timer delta |
| `left_pwm` | `0` | MDD10A PWM output |
| `right_pwm` | `0` | MDD10A PWM output |

## 21. CubeMX 재생성 규칙

나중에 `.ioc`에서 peripheral 설정을 바꾸고 `GENERATE CODE`를 다시 누를 수 있다.

안전 규칙:

- `main.c` 수정은 `USER CODE BEGIN/END` 안에만 둔다.
- `stm32f4xx_it.c`를 직접 수정하지 않는다.
- `usart.c`의 generated init 코드를 직접 수정하지 않는다.
- `ring_buffer.*`, `uart_mvp_protocol.*`는 사용자 파일이라 재생성으로 덮이지 않는다.
- 새 사용자 source가 build에서 빠지면 CubeIDE Project Explorer에서 excluded 상태를 확인한다.

## 22. Build Error 대응

### 22.1 `huart2` undeclared

원인:

- `main.c`에서 `usart.h` include 누락
- CubeMX가 peripheral별 `.c/.h` 생성을 하지 않았고 `huart2` 선언 위치가 다른 경우

확인:

```c
#include "usart.h"
```

### 22.2 `undefined reference to rb_put`

원인:

- `ring_buffer.c`가 project build에 포함되지 않음

해결:

- `Core/Src/ring_buffer.c`가 실제 source folder에 있는지 확인
- CubeIDE에서 해당 파일이 `Exclude from Build` 상태인지 확인

### 22.3 UART RX callback이 안 불림

확인:

- CubeMX NVIC에서 `USART2 global interrupt`를 enable 했는가
- `uart_mvp_start_rx()`가 init 이후 호출되는가
- `HAL_UART_RxCpltCallback()` 안에서 `uart_mvp_on_rx_complete()`가 호출되는가
- `uart_mvp_on_rx_complete()`에서 다시 `HAL_UART_Receive_IT()`를 재등록하는가
- `stm32f4xx_it.c`의 `USART2_IRQHandler()`가 `HAL_UART_IRQHandler(&huart2)`를 호출하는가

### 22.4 PC에서 COM port가 안 보임

확인:

- Nucleo board의 ST-LINK USB port에 연결했는가
- Windows 장치 관리자에서 ST-LINK Virtual COM Port가 보이는가
- ST-LINK driver가 설치되어 있는가
- 다른 serial terminal이 COM port를 점유하고 있지 않은가

## 23. PC Web Dashboard 검증

### 23.1 서버 실행

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ServeWebDashboard.ps1
```

브라우저:

```text
http://localhost:8765/
```

### 23.2 테스트 순서

1. `Connect`
2. `PING`
3. `CMD` before ARM
4. `ARM`
5. `CMD`
6. `Bad Range`
7. `Keepalive`
8. `DISARM`

### 23.3 기대 로그

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

## 24. Terminal Scripted Test

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

## 25. Evidence 정리

검증 후 남길 것:

```text
04_PC_Serial_Control/logs/*_raw.log
04_PC_Serial_Control/logs/*_parsed.csv
web dashboard screenshot
CubeMX Board Selector screenshot
CubeMX USART2 setting screenshot
CubeMX NVIC setting screenshot
STM32 parser code snippet
```

진행 로그에 적을 요약 예:

```text
STM32CubeMX generated a NUCLEO-F446RE HAL project with USART2 PA2/PA3 at 115200 8N1 and USART2 global interrupt enabled. The STM32 firmware stores RX bytes into a ring buffer, reconstructs newline-delimited UART MVP frames in the main loop, validates required fields and ranges, and returns PONG/ACK/ERR/TEL. PC Web Serial dashboard confirmed PING/PONG, NOT_ARMED rejection, valid CMD ACK, OUT_OF_RANGE rejection, timeout zero-output telemetry, and DISARMED telemetry.
```

## 26. 다음 단계

이 MVP가 통과하면 다음 순서로 확장한다.

1. `left_pwm/right_pwm`을 실제 PWM target variable과 연결한다.
2. MDD10A logic input test에서 PWM waveform을 측정한다.
3. Encoder voltage safety test 후 TIM encoder mode를 연결한다.
4. `left_cps/right_cps`를 실제 encoder delta로 대체한다.
5. Battery ADC가 준비되면 `batt_mv`를 실제 값으로 대체한다.
6. ESP32 USART1 link로 같은 protocol을 옮긴다.
7. CAN version command/telemetry contract를 later phase에서 설계한다.
