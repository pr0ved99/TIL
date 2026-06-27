# CubeMX 생성 코드와 사용자 코드 경계

## 목적

이 문서는 `stm32_uart_mvp` firmware project에서 CubeMX가 자동 생성한 파일이 무엇이고, 각 파일 안의 코드가 어떤 의미를 가지는지 정리한다.

대상 project:

```text
Projects/Tracked_Mobile_Robot/03_Firmware/stm32_uart_mvp/
```

핵심 구분:

```text
CubeMX 생성 코드 = MCU peripheral을 사용할 수 있는 상태로 초기화하는 코드
사용자 코드 = 그 peripheral 위에서 실제 application protocol과 동작 정책을 구현하는 코드
```

이번 UART MVP에서는 CubeMX가 `USART2`, `PA2/PA3`, `115200 8N1`, `NVIC interrupt`를 설정했고, 사용자는 그 UART 위에 `ring buffer`, `line parser`, `ACK/ERR/TEL`, `ARMED/DISARMED state machine`을 올린다.

## 전체 실행 흐름

전원 또는 reset 이후 실행 흐름은 다음과 같다.

```text
startup_stm32f446retx.s
-> Reset_Handler
-> SystemInit()
-> main()
-> HAL_Init()
-> SystemClock_Config()
-> MX_GPIO_Init()
-> MX_USART2_UART_Init()
-> USER CODE: uart_mvp_init(&huart2)
-> USER CODE: uart_mvp_start_rx()
-> while (1)
   -> USER CODE: uart_mvp_process()
```

UART byte가 들어오는 흐름은 다음과 같다.

```text
PC dashboard TX
-> ST-LINK VCP
-> STM32 USART2 RX pin PA3
-> USART2 interrupt
-> USART2_IRQHandler()
-> HAL_UART_IRQHandler(&huart2)
-> HAL_UART_RxCpltCallback()
-> uart_mvp_on_rx_complete()
-> ring buffer push
-> HAL_UART_Receive_IT() re-arm
```

main loop에서 처리되는 흐름은 다음과 같다.

```text
uart_mvp_process()
-> process_rx_bytes()
-> line frame assembly
-> handle_line()
-> handle_ping / handle_arm / handle_disarm / handle_cmd
-> send_ack / send_err / send_telemetry
```

## Project Root 파일

### `stm32_uart_mvp.ioc`

CubeMX 설정의 원본 파일이다.

여기에 저장되는 내용:

- board 또는 MCU 선택: `NUCLEO-F446RE`, `STM32F446RETx`
- USART2 사용 여부
- PA2를 `USART2_TX`로 사용
- PA3를 `USART2_RX`로 사용
- USART2 mode: asynchronous
- baudrate, word length, parity, stop bit
- USART2 global interrupt enable
- project name, toolchain, code generator 옵션

이 파일은 직접 C 코드를 작성하는 파일은 아니다. CubeMX에서 pin/peripheral을 바꾸면 이 `.ioc`가 바뀌고, `Generate Code`를 누르면 C 코드가 다시 생성된다.

### `.project`, `.cproject`, `.mxproject`

STM32CubeIDE/Eclipse 계열 project metadata다.

의미:

- `.project`: project name, project nature, builder 정보
- `.cproject`: C/C++ build configuration, include path, compiler option
- `.mxproject`: CubeMX와 CubeIDE 연동 정보

일반적으로 직접 수정하지 않는다. IDE가 관리한다.

### `.settings/`

Eclipse/STM32CubeIDE workspace 설정 파일들이 들어간다.

예:

- language setting
- resource encoding
- STM32CubeIDE project preference

역시 직접 수정 대상이 아니다.

### `STM32F446RETX_FLASH.ld`

Flash 실행용 linker script다.

역할:

- code와 read-only data를 flash에 배치
- global/static variable을 RAM에 배치
- stack/heap 크기 정의
- interrupt vector table 위치 결정

이 파일이 있기 때문에 compiler가 만든 object file들이 STM32F446RE의 실제 memory map에 맞게 연결된다.

이번 단계에서는 수정하지 않는다. 나중에 bootloader, external memory, custom section을 다룰 때 학습 대상이 된다.

### `STM32F446RETX_RAM.ld`

RAM 실행용 linker script다.

보통 debug 특수 상황이나 RAM execution이 필요할 때 사용한다. 이번 UART MVP에서는 주로 `FLASH.ld`가 사용된다.

### `stm32_uart_mvp Debug.launch`

STM32CubeIDE debug launch 설정이다.

역할:

- 어떤 `.elf`를 flash/debug할지
- ST-LINK GDB server 설정
- reset mode, SWD 설정
- debug startup 옵션

VS Code의 `launch.json`과 비슷한 성격이지만, CubeIDE용 파일이다.

## `Core/Inc`

### `main.h`

CubeMX가 만든 main header다.

주요 역할:

- 공통 include 제공
- `Error_Handler()` 선언
- pin 이름 define

예:

```c
#define USART_TX_Pin GPIO_PIN_2
#define USART_TX_GPIO_Port GPIOA
#define USART_RX_Pin GPIO_PIN_3
#define USART_RX_GPIO_Port GPIOA
#define LD2_Pin GPIO_PIN_5
#define LD2_GPIO_Port GPIOA
```

의미:

- `USART_TX_Pin`은 실제로 `PA2`
- `USART_RX_Pin`은 실제로 `PA3`
- `LD2_Pin`은 NUCLEO board의 green LED

CubeMX에서 pin label을 바꾸면 이 define도 바뀔 수 있다.

### `usart.h`

USART 초기화 함수와 UART handle을 외부에서 사용할 수 있게 선언한다.

중요 선언:

```c
extern UART_HandleTypeDef huart2;
void MX_USART2_UART_Init(void);
```

의미:

- `huart2`는 USART2를 HAL에서 다루기 위한 handle이다.
- 사용자 코드가 `HAL_UART_Transmit(&huart2, ...)`처럼 USART2를 쓰려면 이 handle이 필요하다.
- `MX_USART2_UART_Init()`는 CubeMX가 만든 USART2 초기화 함수다.

### `gpio.h`

GPIO 초기화 함수 선언이 들어간다.

```c
void MX_GPIO_Init(void);
```

`main.c`에서 이 함수를 호출해 GPIO clock, LED, button 같은 기본 GPIO를 초기화한다.

### `stm32f4xx_it.h`

interrupt handler 함수 선언이 들어간다.

예:

```c
void SysTick_Handler(void);
void USART2_IRQHandler(void);
```

이 선언은 startup vector table과 실제 C handler를 연결하는 데 필요하다.

### `stm32f4xx_hal_conf.h`

HAL driver 설정 파일이다.

역할:

- 어떤 HAL module을 사용할지 enable
- oscillator 기본값
- assert 사용 여부
- HAL include 묶음

예를 들어 UART를 쓰면 `HAL_UART_MODULE_ENABLED`가 켜져 있어야 한다.

일반적으로 CubeMX가 관리한다.

### `ring_buffer.h`

사용자 작성 파일이다.

CubeMX 생성물이 아니다.

역할:

- UART RX byte를 임시 저장할 circular queue API 선언

왜 필요한가:

- UART byte는 interrupt 시점에 비동기적으로 들어온다.
- ISR/callback 안에서 문자열 parser, command 처리, printf 같은 무거운 일을 하면 interrupt latency가 커진다.
- 그래서 callback에서는 byte를 빠르게 ring buffer에 넣고 빠져나온다.
- main loop에서 buffer를 천천히 비우며 frame parsing을 수행한다.

### `uart_mvp_protocol.h`

사용자 작성 파일이다.

CubeMX 생성물이 아니다.

역할:

- UART MVP protocol module의 public API 선언

주요 API:

```c
void uart_mvp_init(UART_HandleTypeDef *huart);
void uart_mvp_start_rx(void);
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart);
void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);
void uart_mvp_process(void);
```

이 header 덕분에 `main.c`는 protocol 내부 구현을 몰라도 다음 흐름만 호출하면 된다.

```c
uart_mvp_init(&huart2);
uart_mvp_start_rx();
uart_mvp_process();
```

## `Core/Src`

### `main.c`

project의 중심 파일이다.

CubeMX가 만든 부분:

```c
HAL_Init();
SystemClock_Config();
MX_GPIO_Init();
MX_USART2_UART_Init();
while (1) { ... }
```

의미:

- `HAL_Init()`: HAL library, SysTick, NVIC 기반 초기화
- `SystemClock_Config()`: system clock tree 설정
- `MX_GPIO_Init()`: CubeMX가 설정한 GPIO 초기화
- `MX_USART2_UART_Init()`: CubeMX가 설정한 USART2 초기화
- `while (1)`: bare-metal foreground loop

사용자가 작성해야 하는 부분은 `USER CODE` block 안에 넣는다.

현재 사용자 코드 연결부:

```c
/* USER CODE BEGIN Includes */
#include "uart_mvp_protocol.h"
/* USER CODE END Includes */
```

의미:

- protocol module의 함수 선언을 가져온다.

```c
/* USER CODE BEGIN 2 */
uart_mvp_init(&huart2);
uart_mvp_start_rx();
/* USER CODE END 2 */
```

의미:

- USART2 초기화가 끝난 뒤 protocol module에 `huart2`를 넘긴다.
- 첫 UART interrupt receive를 시작한다.

```c
/* USER CODE BEGIN 3 */
uart_mvp_process();
/* USER CODE END 3 */
```

의미:

- main loop마다 ring buffer를 확인한다.
- complete line frame이 있으면 parser를 실행한다.
- timeout과 telemetry도 함께 처리한다.

```c
/* USER CODE BEGIN 4 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  uart_mvp_on_rx_complete(huart);
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
  uart_mvp_on_uart_error(huart);
}
/* USER CODE END 4 */
```

의미:

- HAL이 UART 수신 완료 또는 error를 감지했을 때 호출하는 weak callback을 사용자 코드에서 재정의한다.
- 수신 완료 callback에서는 byte를 ring buffer에 넣고 다시 `HAL_UART_Receive_IT()`를 걸어야 한다.

주의:

- `USER CODE` block 바깥에 직접 코드를 쓰면 CubeMX regenerate 시 사라질 수 있다.

### `usart.c`

CubeMX 생성 파일이다.

핵심 함수:

```c
void MX_USART2_UART_Init(void)
```

이 함수는 USART2의 통신 조건을 설정한다.

주요 설정:

```c
huart2.Instance = USART2;
huart2.Init.BaudRate = 115200;
huart2.Init.WordLength = UART_WORDLENGTH_8B;
huart2.Init.StopBits = UART_STOPBITS_1;
huart2.Init.Parity = UART_PARITY_NONE;
huart2.Init.Mode = UART_MODE_TX_RX;
huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
huart2.Init.OverSampling = UART_OVERSAMPLING_16;
HAL_UART_Init(&huart2);
```

의미:

- `Instance = USART2`: 실제 peripheral은 USART2
- `BaudRate = 115200`: PC dashboard와 같은 속도
- `WordLength = 8B`: data bit 8개
- `StopBits = 1`: stop bit 1개
- `Parity = NONE`: parity 없음
- `Mode = TX_RX`: 송신과 수신 모두 사용
- `HwFlowCtl = NONE`: RTS/CTS flow control 미사용
- `OverSampling = 16`: UART sampling을 16배 oversampling으로 수행
- `HAL_UART_Init()`: HAL이 위 설정을 실제 register 값으로 반영

또 다른 핵심 함수:

```c
void HAL_UART_MspInit(UART_HandleTypeDef* uartHandle)
```

이 함수는 UART peripheral 주변 자원을 설정한다.

주요 설정:

```c
__HAL_RCC_USART2_CLK_ENABLE();
__HAL_RCC_GPIOA_CLK_ENABLE();
GPIO_InitStruct.Pin = USART_TX_Pin|USART_RX_Pin;
GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
GPIO_InitStruct.Alternate = GPIO_AF7_USART2;
HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
HAL_NVIC_SetPriority(USART2_IRQn, 0, 0);
HAL_NVIC_EnableIRQ(USART2_IRQn);
```

의미:

- USART2 clock enable
- PA2/PA3가 있는 GPIOA clock enable
- PA2/PA3를 alternate function mode로 설정
- AF7을 선택해서 PA2/PA3를 USART2 기능에 연결
- USART2 interrupt priority 설정
- USART2 interrupt enable

register 관점 대응:

```text
GPIOA clock enable    -> RCC AHB1ENR GPIOAEN
USART2 clock enable   -> RCC APB1ENR USART2EN
PA2/PA3 AF mode       -> GPIOA MODER
AF7 USART2 mapping    -> GPIOA AFRL
USART2 interrupt      -> NVIC ISER / priority register
USART2 baud/format    -> USART BRR / CR1 / CR2 / CR3
```

### `gpio.c`

CubeMX 생성 파일이다.

핵심 함수:

```c
void MX_GPIO_Init(void)
```

역할:

- GPIO port clock enable
- NUCLEO board button B1 설정
- NUCLEO board LED LD2 설정

주요 코드 의미:

```c
__HAL_RCC_GPIOC_CLK_ENABLE();
__HAL_RCC_GPIOH_CLK_ENABLE();
__HAL_RCC_GPIOA_CLK_ENABLE();
__HAL_RCC_GPIOB_CLK_ENABLE();
```

GPIO port를 사용하려면 먼저 clock을 켜야 한다.

```c
HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);
```

LD2 LED의 초기 출력값을 low로 둔다.

```c
GPIO_InitStruct.Pin = B1_Pin;
GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);
```

보드 user button B1을 falling edge interrupt 입력으로 설정한다.

```c
GPIO_InitStruct.Pin = LD2_Pin;
GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);
```

보드 LED LD2를 push-pull output으로 설정한다.

이번 UART MVP에서는 B1/LD2가 핵심 기능은 아니다. NUCLEO board template 때문에 기본으로 생성된 코드에 가깝다.

### `stm32f4xx_it.c`

CubeMX 생성 interrupt handler 파일이다.

핵심 함수:

```c
void USART2_IRQHandler(void)
{
  HAL_UART_IRQHandler(&huart2);
}
```

의미:

- USART2 interrupt가 발생하면 CPU가 이 함수로 들어온다.
- 이 함수 안에서 HAL UART interrupt handler를 호출한다.
- HAL은 RXNE, TC, error flag 등을 확인한다.
- 수신 완료 상태라면 `HAL_UART_RxCpltCallback()`을 호출한다.

중요한 점:

```text
USART2_IRQHandler()는 interrupt 입구다.
HAL_UART_RxCpltCallback()은 사용자 처리로 넘어오는 callback이다.
```

따라서 application logic을 `USART2_IRQHandler()`에 직접 많이 넣기보다, HAL callback에서 가볍게 ring buffer에 넣고 main loop에서 처리하는 구조가 좋다.

### `stm32f4xx_hal_msp.c`

CubeMX 생성 MSP 초기화 파일이다.

핵심 함수:

```c
void HAL_MspInit(void)
```

역할:

- global MSP 초기화
- SYSCFG/PWR clock enable
- NVIC priority grouping 설정

주요 코드:

```c
__HAL_RCC_SYSCFG_CLK_ENABLE();
__HAL_RCC_PWR_CLK_ENABLE();
HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_0);
```

이 파일은 MCU 지원 패키지 초기화에 가까워서 이번 UART MVP application logic과는 거리가 있다.

### `system_stm32f4xx.c`

CMSIS system 파일이다.

역할:

- reset 직후 low-level system 초기화
- `SystemCoreClock` 변수 관리
- `SystemInit()` 제공

CubeMX/HAL project에서 거의 기본으로 들어오는 파일이다.

일반적으로 직접 수정하지 않는다.

### `syscalls.c`, `sysmem.c`

embedded C runtime을 위한 stub 파일이다.

역할:

- `_write`, `_read`, `_sbrk`, `_close` 같은 system call stub 제공
- bare-metal 환경에서 newlib가 link될 수 있게 함

`printf`, `malloc` 같은 C library 기능과 관련이 있다. 이번 MVP에서는 직접 학습 우선순위가 높지 않다.

### `ring_buffer.c`

사용자 작성 파일이다.

CubeMX 생성물이 아니다.

역할:

- UART RX callback에서 들어온 byte를 임시 저장
- main loop가 나중에 byte를 꺼내 처리할 수 있게 함

핵심 개념:

```text
head = 다음에 쓸 위치
tail = 다음에 읽을 위치
empty = head == tail
full = 다음 head가 tail과 같을 때
```

왜 필요한가:

- UART byte는 언제 들어올지 모른다.
- interrupt callback에서 parser까지 전부 처리하면 오래 걸릴 수 있다.
- byte 수신은 빠르게 저장하고, frame parsing은 main loop에서 처리한다.

이 구조는 `single producer / single consumer` 구조다.

```text
producer = UART RX callback
consumer = main loop
```

### `uart_mvp_protocol.c`

사용자 작성 파일이다.

CubeMX 생성물이 아니다.

이번 MVP의 핵심 application logic이다.

담당 기능:

- UART 1 byte interrupt receive 시작
- 수신 완료 callback 처리
- ring buffer에서 byte를 꺼내 line frame으로 조립
- frame type 판별
- `PING`, `ARM`, `DISARM`, `CMD` 처리
- `ACK`, `ERR`, `PONG`, `TEL` 송신
- command timeout 처리
- ARMED/DISARMED state 관리

주요 함수 의미:

```c
void uart_mvp_init(UART_HandleTypeDef *huart)
```

사용할 UART handle을 module 내부에 저장한다. 이번에는 `&huart2`가 들어온다.

```c
void uart_mvp_start_rx(void)
```

`HAL_UART_Receive_IT()`를 호출해서 1 byte interrupt 수신을 시작한다.

```c
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart)
```

수신 완료 callback에서 호출된다.

해야 하는 일:

- callback이 USART2에서 온 것이 맞는지 확인
- 수신 byte를 ring buffer에 넣기
- buffer full이면 drop count 증가
- 다시 `HAL_UART_Receive_IT()` 호출해서 다음 byte 수신 준비

```c
static void process_rx_bytes(void)
```

ring buffer에서 byte를 꺼내 문자열 frame으로 조립한다.

예:

```text
C
M
D
,
s
e
q
=
1
\n
```

이 byte들이 모이면:

```text
CMD,seq=1,...
```

같은 line frame이 된다.

```c
static void handle_line(const char *line)
```

line frame의 첫 토큰을 보고 어떤 명령인지 분기한다.

예:

```text
PING -> handle_ping()
ARM -> handle_arm()
DISARM -> handle_disarm()
CMD -> handle_cmd()
unknown -> ERR
```

```c
static void handle_cmd(const char *line)
```

`CMD` frame의 필수 field를 검사한다.

검사할 것:

- `seq`가 있는가
- `vx_mmps`가 있는가
- `w_mradps`가 있는가
- `timeout_ms`가 있는가
- 현재 `ARMED` 상태인가
- 값이 허용 범위 안인가

정상이라면:

```text
ACK,seq=...,type=CMD
```

문제가 있다면:

```text
ERR,seq=...,type=CMD,code=NOT_ARMED
ERR,seq=...,type=CMD,code=OUT_OF_RANGE
ERR,seq=...,type=CMD,code=MISSING_FIELD
```

같은 응답을 보낸다.

```c
static void send_telemetry(uint32_t now)
```

주기적으로 `TEL` frame을 보낸다.

예:

```text
TEL,t_ms=141600,state=ARMED,last_seq=23,vx_mmps=0,w_mradps=0,left_pwm=0,right_pwm=0,left_cps=0,right_cps=0,batt_mv=0,drop=0,err=2
```

현재는 실제 motor/encoder/battery 값이 연결되지 않았기 때문에 placeholder가 많다.

```c
static void update_timeout(uint32_t now)
```

마지막 CMD 이후 timeout이 지나면 motion command를 0으로 만든다.

의도:

- PC/ESP32 명령이 끊겼을 때 계속 움직이지 않게 함
- timeout 이후 output zero
- 더 긴 대기 후 DISARM fallback

## Debug build output

`Debug/` 폴더는 CubeIDE가 build하면서 만든 output이다.

주요 파일:

| File | Meaning |
| --- | --- |
| `stm32_uart_mvp.elf` | debug symbol이 포함된 firmware binary |
| `stm32_uart_mvp.map` | linker가 만든 memory map |
| `stm32_uart_mvp.list` | disassembly와 source interleave |
| `makefile`, `sources.mk`, `objects.mk` | IDE가 만든 build script |
| `Core/`, `Drivers/` 하위 object | compile 중간 산출물 |

보통 git에는 넣지 않는다. local build output이다.

## 사용자가 건드려야 하는 범위

수정 가능성이 높은 파일:

```text
Core/Src/main.c              단, USER CODE block 안
Core/Inc/ring_buffer.h
Core/Src/ring_buffer.c
Core/Inc/uart_mvp_protocol.h
Core/Src/uart_mvp_protocol.c
```

CubeMX에서 설정을 바꿔야 하는 파일:

```text
stm32_uart_mvp.ioc
```

직접 수정하지 않는 것이 좋은 파일:

```text
Drivers/
Core/Startup/
system_stm32f4xx.c
stm32f4xx_hal_conf.h
.project
.cproject
.mxproject
Debug/
```

## 포트폴리오 설명 문장

이 프로젝트에서 CubeMX/HAL을 사용했다는 것은 단순히 자동 생성 코드에 의존했다는 뜻이 아니다.

좋은 설명은 다음처럼 나눠서 말하는 것이다.

```text
CubeMX로 USART2, PA2/PA3 alternate function, NVIC interrupt, clock 초기화를 생성했고,
사용자 코드에서는 UART RX interrupt callback을 ring buffer에 연결한 뒤,
main loop에서 command frame parser와 ARMED/DISARMED state machine, ACK/ERR/TEL telemetry를 구현했습니다.
```

면접에서 더 짧게 말하면:

```text
하드웨어 초기화는 CubeMX/HAL로 재현 가능하게 관리했고,
실제 제어 로직은 UART protocol parser와 safety state machine으로 분리해서 구현했습니다.
```

## 다음 학습 질문

1. `HAL_UART_Receive_IT()`는 내부적으로 어떤 interrupt flag를 enable하는가?
2. `USART2_IRQHandler()`와 `HAL_UART_RxCpltCallback()`은 어떤 순서로 연결되는가?
3. ring buffer를 쓰지 않고 callback에서 바로 parser를 돌리면 어떤 문제가 생기는가?
4. `CMD` frame field가 빠졌을 때 firmware는 어디에서 `ERR`를 결정하는가?
5. timeout zero output은 motor driver 연결 전에도 왜 먼저 구현해야 하는가?
