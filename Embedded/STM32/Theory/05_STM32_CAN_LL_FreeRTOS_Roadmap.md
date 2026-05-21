# [STM32] CAN, LL, FreeRTOS 학습 로드맵

## 결론

이 학습의 목표는 **STM32에서 저수준 제어(LL)를 이해하고, FreeRTOS로 작업을 분리한 뒤, CAN 통신을 안정적으로 송수신하는 구조를 직접 구현하는 것**이다.

현재 저장소의 실습 흐름은 `NUCLEO-F446RE` 기준으로 진행되고 있으므로, 이 문서도 우선 **STM32F446RE**를 기준으로 정리한다.

> 주의: STM32F446RE는 `FDCAN`이 아니라 `bxCAN` 계열 CAN 주변장치를 사용한다. 또한 NUCLEO-F446RE 보드에는 CAN 트랜시버가 기본 탑재되어 있지 않으므로, 실제 CAN 통신을 하려면 외부 CAN 트랜시버 모듈과 종단저항 구성이 필요하다.

---

## 1. 학습 범위

이번 학습의 중심축은 세 가지다.

| 주제 | 쉬운 정의 | 학습 목적 |
| --- | --- | --- |
| **LL(Low Layer)** | HAL보다 레지스터에 가까운 저수준 STM32 드라이버 | GPIO, Timer, UART, Interrupt를 가볍고 명확하게 제어 |
| **FreeRTOS** | 여러 작업을 Task 단위로 나눠 실행하는 실시간 OS | CAN 수신, 송신, 로그, 제어 로직을 안전하게 분리 |
| **CAN(Controller Area Network)** | 여러 장치가 같은 2선 버스에서 메시지를 주고받는 통신 방식 | 로봇 내부 MCU, 모터드라이버, 센서와 안정적으로 통신 |

실무적으로는 모든 것을 LL로만 작성하기보다, 다음처럼 나눠 접근하는 것이 현실적이다.

| 영역 | 추천 방식 | 이유 |
| --- | --- | --- |
| GPIO | LL | 단순하고 레지스터 구조를 익히기 좋음 |
| Timer/PWM | LL 또는 HAL+LL 혼용 | 타이밍 제어 원리를 익히기 좋음 |
| UART 로그 | LL 또는 HAL | 디버깅용 출력 확보가 중요 |
| FreeRTOS | CMSIS-RTOS 또는 FreeRTOS Native API | Task/Queue 구조 학습이 핵심 |
| CAN(bxCAN) | HAL 또는 레지스터 직접 제어 | STM32F4 계열은 CAN용 LL API가 제한적이므로 HAL로 시작하는 편이 안전 |

---

## 2. 전체 학습 순서

처음부터 CAN과 FreeRTOS를 같이 붙이면 문제가 생겼을 때 원인을 찾기 어렵다. 따라서 아래 순서로 진행한다.

### 1단계: STM32 기본기 정리

먼저 MCU가 코드를 실행하기 위해 필요한 기본 구조를 이해한다.

- Clock tree: MCU와 주변장치에 클럭을 공급하는 구조
- GPIO: 핀을 입력 또는 출력으로 쓰는 기능
- Timer: 일정한 시간 간격이나 PWM을 만드는 하드웨어
- Interrupt: 특정 이벤트가 발생했을 때 CPU가 즉시 처리하는 방식
- NVIC: Cortex-M에서 인터럽트 우선순위를 관리하는 장치
- UART: PC로 로그를 출력하기 위한 기본 직렬 통신

추천 실습:

```text
STM32/Practice/01_F446RE_Blinky_Tutorial.md
STM32/Practice/02_F446RE_Blinky_LL_Hybrid_Tutorial.md
STM32/Practice/03_F446RE_EXTI_Button_Interrupt.md
STM32/Practice/04_F446RE_PWM_Tutorial.md
```

### 2단계: LL 드라이버 익히기

LL은 HAL보다 코드가 짧고 빠르지만, 개발자가 설정을 더 많이 책임져야 한다.

중점 학습 항목:

- `LL_GPIO_SetOutputPin()`, `LL_GPIO_ResetOutputPin()`
- `LL_GPIO_TogglePin()`
- `LL_APB1_GRP1_EnableClock()`, `LL_AHB1_GRP1_EnableClock()`
- `LL_TIM_EnableCounter()`
- `LL_USART_TransmitData8()`
- `NVIC_SetPriority()`, `NVIC_EnableIRQ()`

확인해야 할 습관:

- CubeMX가 어떤 초기화 코드를 생성했는지 확인한다.
- Reference Manual에서 해당 레지스터가 실제로 어떤 역할인지 찾아본다.
- 디버그 중 Peripheral Registers View로 레지스터 값이 바뀌는지 확인한다.

### 3단계: FreeRTOS 기본 구조 익히기

FreeRTOS는 `while (1)` 안에 모든 코드를 몰아넣지 않고, 기능별로 Task를 나누기 위해 사용한다.

먼저 익힐 개념:

- Task: 독립적으로 실행되는 작업 단위
- Queue: Task끼리 데이터를 안전하게 주고받는 통로
- Semaphore: 이벤트 발생 여부를 알려주는 신호
- Mutex: 공유 자원 충돌을 막는 잠금 장치
- Priority: 어떤 Task를 더 먼저 실행할지 정하는 우선순위
- Stack: 각 Task가 함수 호출과 지역변수 저장에 쓰는 메모리 공간

초기 실습 구조:

```text
LED Task      -> 주기적으로 LED 토글
Log Task      -> UART로 상태 출력
Button ISR    -> 버튼 인터럽트 발생
Event/Queue   -> ISR에서 Task로 이벤트 전달
```

주의할 점:

- ISR 안에서는 오래 걸리는 작업을 하지 않는다.
- ISR에서 Queue를 쓸 때는 `xQueueSendFromISR()` 계열 함수를 사용한다.
- Task 안에서는 `HAL_Delay()` 대신 `vTaskDelay()`를 사용한다.
- Task stack size가 작으면 HardFault나 이상 동작이 발생할 수 있다.

### 4단계: CAN 단독 실습

CAN은 FreeRTOS 없이 먼저 단독으로 송수신을 확인한다. 이 단계에서는 통신 자체가 되는지 확인하는 것이 목표다.

먼저 익힐 개념:

- CAN ID: 메시지 종류를 구분하는 번호
- DLC: CAN 데이터 길이
- Bitrate: CAN 버스 통신 속도
- Filter: 필요한 CAN ID만 받도록 거르는 설정
- Tx Mailbox: 송신 대기 공간
- Rx FIFO: 수신 메시지가 쌓이는 공간
- Bus-off: CAN 오류가 누적되어 노드가 버스에서 빠지는 상태

하드웨어 체크:

- NUCLEO-F446RE에는 CAN 트랜시버가 기본 내장되어 있지 않다.
- STM32 CAN TX/RX 핀과 외부 트랜시버의 TXD/RXD를 연결해야 한다.
- CANH, CANL 라인 양 끝에는 보통 120 ohm 종단저항이 필요하다.
- 모든 CAN 노드는 같은 bitrate를 사용해야 한다.
- GND 기준을 공유해야 한다.

우선 실습 순서:

```text
1. CAN loopback 모드로 보드 내부 송수신 확인
2. Normal 모드에서 두 보드 또는 CAN 어댑터와 통신 확인
3. 특정 CAN ID만 받도록 filter 설정
4. 송신 실패, bus-off, error counter 확인
```

### 5단계: CAN + FreeRTOS 통합

CAN 송수신이 단독으로 안정화되면 FreeRTOS 구조에 붙인다.

추천 구조:

```text
CAN RX Interrupt
    ↓
CAN RX Queue
    ↓
CAN Parser Task
    ↓
State / Control Task
    ↓
CAN TX Queue
    ↓
CAN TX Task
```

역할 분리:

| 구성 | 역할 |
| --- | --- |
| CAN RX Interrupt | CAN 메시지를 빨리 꺼내 Queue에 넣음 |
| CAN RX Queue | ISR과 Parser Task 사이의 안전한 버퍼 |
| CAN Parser Task | CAN ID별로 메시지 해석 |
| Control Task | 해석된 상태를 바탕으로 제어 로직 수행 |
| CAN TX Queue | 송신 요청을 모아둠 |
| CAN TX Task | CAN mailbox 상태를 확인하며 송신 |
| Log Task | UART로 상태, 오류, 통계 출력 |

ISR에서는 최소 작업만 수행한다.

```c
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan)
{
    BaseType_t higher_priority_task_woken = pdFALSE;
    CanFrame_t frame;

    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &frame.header, frame.data);
    xQueueSendFromISR(can_rx_queue, &frame, &higher_priority_task_woken);
    portYIELD_FROM_ISR(higher_priority_task_woken);
}
```

Parser Task에서는 Queue에서 꺼내 처리한다.

```c
void CanParserTask(void *argument)
{
    CanFrame_t frame;

    for (;;)
    {
        if (xQueueReceive(can_rx_queue, &frame, portMAX_DELAY) == pdPASS)
        {
            switch (frame.header.StdId)
            {
            case 0x101:
                // TODO: motor status parsing
                break;
            case 0x201:
                // TODO: sensor data parsing
                break;
            default:
                break;
            }
        }
    }
}
```

---

## 3. 추천 폴더 구성

학습 기록과 실제 프로젝트는 분리한다.

```text
STM32/
├── Theory/
│   ├── 05_STM32_CAN_LL_FreeRTOS_Roadmap.md
│   ├── 06_STM32CubeIDE_for_VSCode_Setup.md
│   ├── 07_FreeRTOS_Basic_Concepts.md
│   ├── 08_CAN_Basic_Concepts.md
│   └── 09_STM32F446RE_bxCAN_Notes.md
├── Practice/
│   ├── 05_F446RE_LL_GPIO_Timer_UART.md
│   ├── 06_F446RE_FreeRTOS_Basic.md
│   ├── 07_F446RE_CAN_Loopback.md
│   ├── 08_F446RE_CAN_Normal_Mode.md
│   └── 09_F446RE_CAN_FreeRTOS_Queue.md
└── STM32_ws/
    ├── F446RE_LL_Basic/
    ├── F446RE_FreeRTOS_Basic/
    ├── F446RE_CAN_Loopback/
    ├── F446RE_CAN_Normal_Mode/
    └── F446RE_CAN_FreeRTOS_Queue/
```

---

## 4. CubeMX / CubeIDE / VS Code 역할

STM32 학습에서는 도구 역할을 분리해서 생각한다.

| 도구 | 역할 |
| --- | --- |
| STM32CubeMX | 핀, 클럭, CAN, FreeRTOS 설정을 생성 |
| STM32CubeIDE | Eclipse 기반 공식 통합 개발 환경 |
| STM32CubeIDE for VS Code | VS Code에서 STM32 프로젝트 빌드, 플래시, 디버그 |
| STM32CubeProgrammer | 펌웨어 다운로드, 메모리 확인, 보드 연결 확인 |

추천 흐름:

```text
CubeMX에서 설정 생성
    ↓
VS Code에서 코드 작성
    ↓
VS Code에서 빌드/디버그
    ↓
보드에서 동작 확인
    ↓
TIL에 Theory/Practice 문서로 정리
```

---

## 5. 실습 마일스톤

### Milestone 1: LL 기본기

목표:

- HAL 없이 GPIO 제어 흐름 이해
- Timer/PWM 동작 원리 이해
- Interrupt와 NVIC 설정 흐름 이해

산출물:

```text
STM32/Practice/05_F446RE_LL_GPIO_Timer_UART.md
STM32/STM32_ws/F446RE_LL_Basic/
```

### Milestone 2: FreeRTOS 기본기

목표:

- Task 여러 개를 생성하고 우선순위 차이를 관찰
- Queue로 Task 간 데이터 전달
- ISR에서 Task로 이벤트 전달

산출물:

```text
STM32/Practice/06_F446RE_FreeRTOS_Basic.md
STM32/STM32_ws/F446RE_FreeRTOS_Basic/
```

### Milestone 3: CAN 단독 통신

목표:

- CAN loopback 모드 송수신 확인
- Normal 모드에서 외부 장치와 통신 확인
- Filter 설정으로 필요한 ID만 수신

산출물:

```text
STM32/Practice/07_F446RE_CAN_Loopback.md
STM32/Practice/08_F446RE_CAN_Normal_Mode.md
STM32/STM32_ws/F446RE_CAN_Loopback/
STM32/STM32_ws/F446RE_CAN_Normal_Mode/
```

### Milestone 4: CAN + FreeRTOS 통합

목표:

- CAN RX interrupt에서 Queue로 메시지 전달
- Parser Task에서 CAN ID별 처리
- TX Task에서 주기 송신
- Log Task에서 error counter, queue usage, task 상태 출력

산출물:

```text
STM32/Practice/09_F446RE_CAN_FreeRTOS_Queue.md
STM32/STM32_ws/F446RE_CAN_FreeRTOS_Queue/
```

---

## 6. 디버깅 체크리스트

CAN, LL, FreeRTOS는 문제 원인이 여러 층에 걸쳐 생기므로 아래 순서로 확인한다.

### 하드웨어

- CAN 트랜시버 전원 전압이 맞는가?
- CANH/CANL이 뒤바뀌지 않았는가?
- 종단저항 120 ohm 구성이 맞는가?
- 모든 장치의 GND가 연결되어 있는가?
- NUCLEO 보드 핀과 CubeMX 핀 설정이 일치하는가?

### Clock / Peripheral

- CAN peripheral clock이 활성화되어 있는가?
- APB clock 기준으로 bitrate 계산이 맞는가?
- GPIO alternate function 설정이 맞는가?
- NVIC에서 CAN RX interrupt가 활성화되어 있는가?

### CAN

- 모든 노드의 bitrate가 같은가?
- Filter가 너무 좁아서 메시지를 버리고 있지 않은가?
- Tx mailbox가 가득 차 있지 않은가?
- Rx FIFO overflow가 발생하지 않는가?
- error counter, bus-off 상태를 확인했는가?

### FreeRTOS

- ISR에서 일반 Queue API를 쓰지 않았는가?
- `xQueueSendFromISR()` 뒤에 context switch 처리를 했는가?
- Task priority가 적절한가?
- Queue 길이가 너무 짧지 않은가?
- Task stack overflow가 발생하지 않는가?

---

## 7. 최종 목표 구조

최종적으로는 아래 구조를 직접 구현하고 설명할 수 있으면 된다.

```text
Sensor / Motor Driver / Other MCU
        ↓ CAN Bus
STM32 bxCAN Peripheral
        ↓ Interrupt
CAN RX Queue
        ↓
CAN Parser Task
        ↓
Robot State / Control Logic
        ↓
CAN TX Queue
        ↓
CAN TX Task
        ↓
CAN Bus
```

핵심은 단순히 CAN 메시지를 보내는 것이 아니라, **인터럽트, Queue, Task를 이용해 통신 처리를 안정적으로 분리하는 것**이다.
