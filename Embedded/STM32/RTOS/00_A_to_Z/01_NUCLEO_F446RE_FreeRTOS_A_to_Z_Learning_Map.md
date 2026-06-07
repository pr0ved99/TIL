# NUCLEO-F446RE FreeRTOS A-to-Z Learning Map

## 목적

이 문서는 NUCLEO-F446RE에서 FreeRTOS를 학습하고, tracked mobile robot 하부제어 firmware를 task 기반 구조로 바꾸기 위한 A-to-Z 학습 지도다.

목표 흐름:

```text
bare-metal baseline
-> FreeRTOS task 기본
-> delay/timing
-> queue/semaphore/mutex
-> ISR to task handoff
-> priority/stack/heap
-> motor control task
-> safety task
-> communication task
-> telemetry task
-> CAN RX queue integration
```

## 기준 보드와 전제

- Board: `NUCLEO-F446RE`
- MCU: `STM32F446RE`
- IDE: STM32CubeIDE 또는 STM32 VS Code 확장 + CubeMX
- RTOS: FreeRTOS
- 초기 API: CMSIS-RTOS2 또는 FreeRTOS native API 중 하나로 통일
- 첫 적용 시점: bare-metal motor/encoder/safety baseline이 동작한 뒤

FreeRTOS는 bring-up 문제를 숨기는 도구가 아니다. 이미 동작하는 firmware를 task ownership 기준으로 정리하는 도구다.

## 실습 태그 인덱스

본문의 `[Rxx]` 태그는 아래 실습 문서로 연결된다.

| 태그 | 실습 경로 | 목적 |
| --- | --- | --- |
| `[R00]` | [`Practice/P00_CubeMX_FreeRTOS_Setup`](../Practice/P00_CubeMX_FreeRTOS_Setup/README.md) | CubeMX에서 FreeRTOS 프로젝트 생성 |
| `[R01]` | [`Practice/P01_LED_Task_Timing`](../Practice/P01_LED_Task_Timing/README.md) | LED task와 `vTaskDelayUntil()` timing |
| `[R02]` | [`Practice/P02_Button_ISR_Queue`](../Practice/P02_Button_ISR_Queue/README.md) | 버튼 ISR에서 queue로 task에 event 전달 |
| `[R03]` | [`Practice/P03_Task_Priority_Stack`](../Practice/P03_Task_Priority_Stack/README.md) | priority, stack, heap 점검 |
| `[R04]` | [`Practice/P04_UART_Log_Mutex`](../Practice/P04_UART_Log_Mutex/README.md) | 여러 task의 UART log 충돌 방지 |
| `[R05]` | [`Practice/P05_Motor_Control_Task_Skeleton`](../Practice/P05_Motor_Control_Task_Skeleton/README.md) | motor control/safety/telemetry task skeleton |
| `[R06]` | [`Practice/P06_CAN_RX_Queue_Integration`](../Practice/P06_CAN_RX_Queue_Integration/README.md) | CAN RX ISR에서 queue로 parser task 전달 |

## 전체 학습 순서

```text
0. Bare-metal baseline 고정
1. FreeRTOS가 필요한 이유
2. Task와 scheduler
3. Periodic timing
4. Queue와 ISR handoff
5. Semaphore와 mutex
6. Priority, stack, heap
7. STM32 HAL과 FreeRTOS 주의점
8. Robot firmware task architecture
9. Motor control task
10. Safety task
11. Communication task
12. Telemetry task
13. CAN + FreeRTOS integration
14. Debugging and verification
```

## 0. Bare-metal baseline 먼저

### 0.1 FreeRTOS 도입 전 완료 조건

FreeRTOS는 다음 조건이 만족된 뒤 도입한다.

- NUCLEO-F446RE에서 LED, button, UART log가 동작한다.
- PWM 출력이 정상이다.
- encoder count를 읽을 수 있다.
- battery ADC path가 정의되어 있다.
- MDD10A PWM/DIR output을 안전하게 제어할 수 있다.
- command timeout으로 motor output을 0으로 만들 수 있다.
- boot 직후 motor PWM이 zero 상태다.

이 전제가 없으면 RTOS 문제가 아니라 전기, peripheral, pin 설정 문제를 디버깅하게 된다.

## 1. FreeRTOS가 필요한 이유

### 1.1 while loop의 한계

bare-metal `while (1)`에 모든 일을 넣으면 다음 문제가 생긴다.

- UART parsing이 길어지면 motor control timing이 흔들린다.
- telemetry 출력이 길어지면 safety check가 늦어진다.
- sensor read가 blocking되면 command timeout이 늦어진다.
- 코드 ownership이 불분명해진다.

### 1.2 프로젝트에서 FreeRTOS가 해결할 문제

FreeRTOS는 기능별 job을 task로 나누고, data path를 queue로 명확히 만드는 데 사용한다.

프로젝트 기준 task:

```text
motor_control_task
safety_task
comm_task
battery_task
telemetry_task
optional imu_task
optional can_tx_task
optional can_parser_task
```

## 2. Task와 Scheduler

### 2.1 Task

Task는 독립적으로 실행되는 함수다.

기본 형태:

```c
void MotorControlTask(void *argument)
{
    for (;;)
    {
        // read command/state
        // compute output
        // update PWM through safety gate
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

### 2.2 Scheduler

Scheduler는 ready 상태인 task 중 priority가 높은 task를 실행한다.

핵심:

- 높은 priority task가 계속 실행되면 낮은 priority task는 굶을 수 있다.
- task는 적절히 block 또는 delay해야 한다.
- busy-wait loop는 피한다.

연결 실습: `[R01]`, `[R03]`

## 3. Periodic Timing

### 3.1 `vTaskDelay()`와 `vTaskDelayUntil()`

주기 task에는 `vTaskDelayUntil()`이 더 적합하다.

```c
void MotorControlTask(void *argument)
{
    TickType_t last_wake = xTaskGetTickCount();

    for (;;)
    {
        run_motor_control_once();
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(10));
    }
}
```

이렇게 하면 100 Hz loop를 더 일정하게 유지할 수 있다.

연결 실습: `[R01]`

### 3.2 프로젝트 timing target

| Loop | Target | 이유 |
| --- | --- | --- |
| Motor control | 100 Hz | 저속 motor control과 encoder speed estimate |
| Safety check | 50-100 Hz | timeout, voltage, motor output gate |
| Battery sample | 10 Hz | voltage 변화는 상대적으로 느림 |
| Telemetry | 10 Hz | 사람이 보기 쉽고 serial/CAN 부담이 낮음 |
| IMU sample | 50-100 Hz | yaw-rate 보정 후보 |
| CAN parser | event-driven | frame 도착 시 처리 |

## 4. Queue와 ISR Handoff

### 4.1 Queue

Queue는 task 사이에서 데이터를 안전하게 전달한다.

예:

```text
comm_task -> command_queue -> motor_control_task
safety_task -> fault_queue -> telemetry_task
CAN RX ISR -> can_rx_queue -> can_parser_task
```

### 4.2 ISR에서 queue 사용

ISR 안에서는 blocking API를 쓰면 안 된다. ISR용 API를 사용한다.

```c
BaseType_t higher_priority_task_woken = pdFALSE;
xQueueSendFromISR(can_rx_queue, &frame, &higher_priority_task_woken);
portYIELD_FROM_ISR(higher_priority_task_woken);
```

연결 실습: `[R02]`, `[R06]`

## 5. Semaphore와 Mutex

### 5.1 Semaphore

Semaphore는 event notification에 적합하다.

예:

- button interrupt 발생
- ADC conversion complete
- DMA receive complete
- CAN RX pending

### 5.2 Mutex

Mutex는 공유 자원을 보호한다.

대표 공유 자원:

- UART log output
- shared debug buffer
- I2C bus

주의:

- motor control loop에서 mutex를 오래 잡지 않는다.
- ISR에서는 mutex를 사용하지 않는다.
- 가능하면 shared variable write owner를 하나로 만든다.

연결 실습: `[R04]`

## 6. Priority, Stack, Heap

### 6.1 Priority 모델

프로젝트 권장 priority:

```text
highest  safety_task
         motor_control_task
         comm_task / can_parser_task
         battery_task / imu_task
         telemetry_task
lowest   diagnostic_task
```

기준:

- safety는 motor output을 멈출 수 있어야 한다.
- motor control은 timing이 흔들리면 안 된다.
- communication은 motor control을 block하면 안 된다.
- telemetry는 중요하지만 safety-critical하지 않다.

연결 실습: `[R03]`

### 6.2 Stack

각 task는 자기 stack을 가진다.

Stack 부족 증상:

- HardFault
- task가 갑자기 멈춤
- 지역변수 값 깨짐
- 불규칙한 reset

확인할 것:

- stack high water mark
- printf 사용 여부
- 큰 local array 사용 여부
- 재귀 호출 여부

### 6.3 Heap

FreeRTOS object 생성에는 heap이 필요할 수 있다.

확인할 것:

- `configTOTAL_HEAP_SIZE`
- queue 개수와 크기
- task stack 크기
- dynamic allocation 사용 여부

## 7. STM32 HAL과 FreeRTOS 주의점

### 7.1 `HAL_Delay()` 남용 금지

FreeRTOS task 안에서는 `HAL_Delay()`보다 `vTaskDelay()` 또는 `osDelay()`를 사용한다.

### 7.2 Interrupt priority

FreeRTOS API를 ISR에서 호출하려면 NVIC priority 설정이 중요하다.

주의:

- 모든 ISR에서 FreeRTOS API를 호출할 수 있는 것은 아니다.
- `FromISR` 계열 API를 사용해야 한다.
- CubeMX의 interrupt priority와 FreeRTOS config를 함께 확인한다.

### 7.3 printf와 UART

`printf`는 느릴 수 있고, 여러 task에서 동시에 쓰면 로그가 섞인다.

초기 전략:

- log task 하나가 출력한다.
- 다른 task는 queue로 log event를 보낸다.
- 간단한 실습에서는 UART mutex를 사용한다.

연결 실습: `[R04]`

## 8. Robot Firmware Task Architecture

### 8.1 전체 구조

```text
UART / CAN RX
    |
    v
comm_task / can_parser_task
    |
    v
command_queue
    |
    v
motor_control_task
    |
    v
safety gate
    |
    v
MDD10A PWM + DIR

battery_task -> safety_task
encoder read -> motor_control_task
safety_task -> telemetry_task
telemetry_task -> UART/CAN status
```

연결 실습: `[R05]`

### 8.2 Data ownership

| Data | Writer | Reader |
| --- | --- | --- |
| parsed command | `comm_task` | `motor_control_task`, `safety_task` |
| PWM request | `motor_control_task` | PWM update path |
| actual PWM register | `motor_control_task` only | debug read only |
| safety state | `safety_task` | motor, telemetry |
| battery voltage | `battery_task` | safety, telemetry |
| encoder count/speed | timer / motor task | telemetry, odometry |
| fault code | `safety_task` | telemetry, comm response |

규칙:

```text
여러 task가 같은 control variable을 동시에 write하지 않게 한다.
```

## 9. Motor Control Task

### 9.1 책임

`motor_control_task`가 담당할 것:

- 최신 command 읽기
- encoder delta 읽기
- wheel/track speed estimate
- acceleration limit
- PWM duty 계산
- safety state 확인
- PWM register update

하지 말아야 할 것:

- UART parsing
- CAN frame parsing
- 긴 telemetry 출력
- blocking sensor read

### 9.2 초기 skeleton

```c
void MotorControlTask(void *argument)
{
    TickType_t last_wake = xTaskGetTickCount();

    for (;;)
    {
        motion_command_t cmd = get_latest_command_or_zero();
        measured_state_t state = read_measured_state_snapshot();
        safety_state_t safety = get_safety_state();

        motor_output_t output = compute_motor_output(cmd, state);

        if (!safety.motor_output_allowed) {
            output.left_pwm = 0;
            output.right_pwm = 0;
        }

        apply_motor_output(output);
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(10));
    }
}
```

연결 실습: `[R05]`

## 10. Safety Task

### 10.1 책임

`safety_task`가 담당할 것:

- command timeout
- heartbeat timeout
- low battery
- overcurrent 후보
- motor output permission state
- emergency stop latch
- fault code update

Safety task는 communication task보다 우선순위가 높아야 한다.

### 10.2 Safety gate

motor output은 마지막에 safety gate를 통과해야 한다.

```text
requested output
-> safety gate
-> actual PWM
```

Communication task가 직접 PWM을 쓰는 구조는 금지한다.

## 11. Communication Task

### 11.1 UART 먼저

첫 RTOS comm task는 UART command parsing부터 시작한다.

이유:

- PC에서 디버깅이 쉽다.
- wire 수가 적다.
- CAN 도입 전 command format을 안정화할 수 있다.

### 11.2 CAN 확장

CAN은 통신 transport만 바꾼다.

```text
UART parser -> internal command structure
CAN parser  -> internal command structure
```

두 parser는 같은 `motion_command_t`로 변환해야 한다.

연결 실습: `[R06]`

## 12. Telemetry Task

### 12.1 책임

`telemetry_task`가 담당할 것:

- firmware state publish
- fault flags publish
- battery voltage publish
- wheel speed publish
- encoder count publish
- command age publish
- debug counters publish

출력 경로:

- UART log
- CAN telemetry frame
- 나중에 ROS 2 bridge

### 12.2 주기

초기에는 10 Hz로 충분하다.

너무 빠른 telemetry는 UART/CAN bandwidth를 차지하고, motor control timing을 방해할 수 있다.

## 13. CAN + FreeRTOS 통합

### 13.1 권장 구조

```text
CAN RX interrupt
-> can_rx_queue
-> can_parser_task
-> command_queue or state update

telemetry_task
-> can_tx_queue
-> can_tx_task
-> HAL_CAN_AddTxMessage()
```

연결 실습: `[R06]`

### 13.2 ISR 규칙

CAN RX ISR에서는 다음만 수행한다.

- CAN frame 읽기
- 작은 struct에 copy
- queue로 전달
- 바로 return

ISR에서 하지 말 것:

- printf
- long parsing
- PWM update
- blocking wait
- memory allocation

## 14. Debugging과 검증

### 14.1 확인 명령과 방법

STM32에서는 다음을 UART log 또는 debugger로 확인한다.

- task alive counter
- stack high water mark
- queue overflow count
- control loop jitter 후보
- fault state
- command age
- CAN RX/TX count

### 14.2 완료 기준

RTOS architecture가 성공했다고 볼 수 있는 기준:

- motor control task가 일정 주기로 돈다.
- telemetry 출력이 motor timing을 방해하지 않는다.
- command timeout이 RTOS 구조에서도 동작한다.
- safety task가 communication과 독립적으로 motor를 멈출 수 있다.
- CAN RX ISR이 frame을 queue로 넘기고 parser task가 처리한다.
- queue overflow나 stack overflow가 기록된다.

## 마일스톤

| Milestone | 목표 | 완료 기준 |
| --- | --- | --- |
| R0 | CubeMX FreeRTOS 프로젝트 | build, flash, 기본 task 실행 |
| R1 | Periodic task | LED task가 `vTaskDelayUntil()`으로 주기 실행 |
| R2 | ISR to task | button ISR event가 queue로 task에 전달 |
| R3 | Priority/stack | task priority와 stack usage를 확인 |
| R4 | UART log 보호 | 여러 task 로그가 충돌하지 않음 |
| R5 | Robot skeleton | motor/safety/comm/telemetry task 분리 |
| R6 | CAN queue integration | CAN RX ISR에서 parser task로 frame 전달 |

## 다음에 쌓을 세부 문서

- `01_FreeRTOS_Task_Queue_Basics.md`
- `02_FreeRTOS_Interrupt_Priority_On_STM32.md`
- `03_Motor_Control_Task_Architecture.md`
- `04_Safety_Task_And_Fault_State.md`
- `05_CAN_FreeRTOS_Queue_Integration.md`
