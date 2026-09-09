# FreeRTOS Task Architecture

## 목적

이 문서는 궤도형 모바일 로봇 low-level controller의 FreeRTOS task architecture를 정의한다.

FreeRTOS는 필수 학습 목표이자 architecture 목표지만, 첫 bring-up 단계는 아니다. 프로젝트는 먼저
HAL bare-metal firmware로 PWM, encoder, ADC, UART, 기본 motor safety를 검증한다. 이 baseline이
동작한 뒤 firmware를 task 기반 구조로 재구성한다.

이 문서는 다음 질문에 답한다.

- 어떤 job을 FreeRTOS task로 분리할 것인가
- 어떤 task가 motor output을 소유하는가
- Communication code에서 motor control code로 command가 어떻게 전달되는가
- Safety state가 모든 motor command를 어떻게 gate하는가
- Battery, IMU, telemetry, UART, future CAN을 어떻게 분리하는가
- RTOS architecture가 동작한다고 볼 수 있는 증거는 무엇인가

## Architecture Decision

HAL bare-metal drivetrain MVP가 동작한 뒤 FreeRTOS를 적용한다.

Firmware는 다음 구조에서:

```text
single bare-metal loop
```

다음 구조로 이동한다.

```text
communication task
sensor/battery tasks
safety task
motor control task
telemetry task
```

핵심 결정:

```text
PWM output은 motor control task만 쓴다.
Motor output 허용/차단은 safety logic이 결정한다.
Communication task는 motion을 요청할 수 있지만 motor를 직접 구동하지 않는다.
```

### 최신 학습 경로

이 문서는 프로젝트의 task ownership과 architecture contract를 정의한다. 실제 학습과 실습은 아래 문서를 기준으로 진행한다.

- [`../../../Embedded/STM32/RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md`](../../../Embedded/STM32/RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md): NUCLEO-F446RE FreeRTOS A-to-Z
- [`../../../Embedded/STM32/RTOS/Practice/README.md`](../../../Embedded/STM32/RTOS/Practice/README.md): `[R00]`부터 `[R06]`까지의 실습 경로

## 1. 이 프로젝트에서 쓰는 FreeRTOS 용어

| Term | Project meaning |
| --- | --- |
| Task | Motor control, telemetry처럼 독립적으로 실행되는 firmware job |
| Priority | Scheduler 중요도. Ready 상태의 높은 priority task가 먼저 실행됨 |
| Period | 주기 task가 얼마나 자주 실행되어야 하는지 |
| Queue | Task 사이의 안전한 message passing |
| Mutex | Shared resource 보호용. 가능한 적게 사용 |
| Semaphore | Event signal. 보통 ISR에서 task로 알림을 줄 때 사용 |
| ISR | Interrupt service routine. 짧고 non-blocking이어야 함 |
| Tick | FreeRTOS scheduler time base |

이 개념들은 실제 복잡도를 줄일 때만 사용한다. 첫 RTOS version은 단순하고 측정 가능해야 한다.

## 2. Entry Criteria

FreeRTOS는 HAL bare-metal baseline이 다음 조건을 만족하기 전에는 도입하지 않는다.

- Motor 1개가 STM32 제어로 forward/reverse 회전한다.
- Left/right motor PWM output이 low duty에서 검증된다.
- Encoder direction과 count rate가 확인된다.
- Battery voltage ADC path가 최소한 안전하게 정의되어 있다.
- UART 또는 USB command input으로 stop과 low-speed motion을 요청할 수 있다.
- Command timeout으로 motor output을 stop할 수 있다.
- MDD10A PWM/DIR output을 STM32가 제어한다.
- Boot behavior에서 motor output이 disabled 상태다.

이유:

FreeRTOS는 이미 동작하는 firmware를 구조화하는 도구다. 기본 전기, pin, timer, driver 문제를
가리는 용도로 쓰면 안 된다.

## 3. Task Overview

초기 task architecture:

```text
                 UART / CAN RX after standalone validation
                         |
                         v
              comm_task or can_parser_task
                         |
                         v
                    command_queue
                         |
                         v
                 motor_control_task
                         |
                         v
                MDD10A PWM + DIR

encoder timer counters ----+
                           |
battery_task --------------+--> shared measured state
                           |
imu_task ------------------+

safety_task ---------------> global safety gate

telemetry_task ------------> UART / future CAN telemetry
```

Safety rule:

```text
Motor control task는 원하는 output을 계산한다.
Safety state는 output 허용 여부를 결정한다.
```

## 4. Task List

| Task | Initial period | Priority | Responsibility |
| --- | --- | --- | --- |
| `motor_control_task` | 100 Hz | High | 최신 command/state 읽기, speed estimate, PWM update |
| `safety_task` | 50-100 Hz | High | Fault check, low-voltage stop, timeout stop, motor output gating |
| `comm_task` | Event-driven 또는 100 Hz | Medium | UART receive, command parsing, 나중에 CAN receive |
| `battery_task` | 10 Hz | Medium | ADC sampling, voltage filtering, low-voltage input to safety |
| `imu_task` | 50-100 Hz | Medium | BNO08x sampling, yaw/attitude update |
| `telemetry_task` | 10 Hz | Low | State, fault, voltage, speed, command status publish |
| `diagnostic_task` | 1-2 Hz | Low | Optional debug counter와 health summary |

첫 RTOS 구현에서는 drivetrain이 안정될 때까지 `imu_task`와 `diagnostic_task`를 생략할 수 있다.

## 5. Priority Model

권장 priority order:

```text
highest  safety_task
         motor_control_task
         comm_task
         battery_task / imu_task
         telemetry_task
lowest   diagnostic_task
```

근거:

- Safety는 motor output을 독립적으로 멈출 수 있어야 한다.
- Motor control은 안정적인 timing으로 실행되어야 한다.
- Communication은 motor control을 block하면 안 된다.
- Telemetry는 유용하지만 safety-critical하지 않다.
- Diagnostics는 control timing을 방해하면 안 된다.

중요:

`safety_task`와 `motor_control_task`를 같은 high priority로 둔다면, 각 task의 period와 blocking
behavior를 더 조심해서 통제해야 한다.

## 6. Timing Model

초기 timing target:

| Loop | Target | Notes |
| --- | --- | --- |
| Motor control | 10 ms / 100 Hz | 초기 저속 drivetrain control에 충분 |
| Safety check | 10-20 ms / 50-100 Hz | Timeout과 voltage decision에 충분히 빠름 |
| Command timeout | 초기 300 ms | UART interface contract와 일치 |
| Battery sampling | 100 ms / 10 Hz | Voltage는 PWM보다 느리게 변함 |
| IMU sampling | 10-20 ms / 50-100 Hz | Yaw-rate와 odometry 실험에 유용 |
| Telemetry | 100 ms / 10 Hz | 사람이 읽기 쉽고 serial에도 부담이 낮음 |

Implementation rule:

- Periodic task는 `vTaskDelayUntil()`을 사용한다.
- Task 안에서 긴 `HAL_Delay()`를 사용하지 않는다.
- Peripheral을 기다리며 busy-wait하지 않는다.
- Blocking wait에는 timeout이 있어야 한다.

## 7. Data Ownership

각 data item은 writer가 하나여야 한다.

| Data | Writer | Readers |
| --- | --- | --- |
| Latest valid motion command | `comm_task` via queue | `motor_control_task`, `safety_task` |
| Motor PWM duty request | `motor_control_task` | PWM update code |
| Actual PWM hardware registers | `motor_control_task` only | debug read only |
| Encoder counts | timer hardware / encoder read function | `motor_control_task`, telemetry |
| Estimated wheel speed | `motor_control_task` | telemetry, later odometry |
| Battery voltage | `battery_task` | `safety_task`, telemetry |
| IMU yaw/attitude | `imu_task` | later odometry, telemetry |
| Safety state | `safety_task` | `motor_control_task`, telemetry |
| Fault code | `safety_task` | telemetry, communication response |

규칙:

```text
여러 task가 같은 control variable을 write하지 않게 한다.
```

## 8. Message and Queue Model

초기 queue:

| Queue | Producer | Consumer | Payload |
| --- | --- | --- | --- |
| `command_queue` | `comm_task` | `motor_control_task` | Parsed command request |
| `fault_queue` | `safety_task` | `telemetry_task` | Fault events |
| `telemetry_queue` | control/sensor tasks | `telemetry_task` | Optional status snapshots |

Minimal command message:

```c
typedef struct {
    uint32_t seq;
    int32_t vx_mmps;
    int32_t w_mradps;
    uint32_t timeout_ms;
    uint32_t rx_time_ms;
} motion_command_t;
```

FreeRTOS version에서도 safety state는 `16_Control_Loop_and_State_Machine_ko.md`의 enum을 재사용한다.

```c
typedef enum {
    SAFETY_BOOT = 0,
    SAFETY_DISARMED,
    SAFETY_ARMING_CHECK,
    SAFETY_ARMED_IDLE,
    SAFETY_ARMED_ACTIVE,
    SAFETY_LOW_VOLTAGE_STOP,
    SAFETY_ESTOP_LATCHED,
    SAFETY_FAULT_LATCHED
} safety_state_t;
```

ADR-015 기준으로 command timeout은 output/stored command zero 뒤 즉시
`SAFETY_DISARMED`로 전환한다. `SAFETY_TIMEOUT_STOP`은 과거 후보이므로 FreeRTOS
target enum에 포함하지 않으며 재동작에는 new `ARM` 뒤 new `CMD`가 필요하다.

Rules:

- Command queue는 오래된 command가 stale해질 수 있으므로 최신 command 중심으로 운용한다.
- Queue가 full이어도 오래된 motion command 때문에 safety behavior가 block되면 안 된다.
- Telemetry loss는 motor control에 영향을 주면 안 된다.
- Fault event는 report될 수 있을 만큼 유지한다.

## 9. Safety Gate

모든 motor output update는 safety gate를 통과해야 한다.

Control flow:

```text
motion command
    |
    v
clamp velocity and acceleration
    |
    v
compute left/right motor request
    |
    v
check safety state
    |
    +-- unsafe -> PWM = 0, nonzero motor output blocked
    |
    +-- safe   -> apply limited PWM command
```

Output을 차단해야 하는 safety condition:

- Boot not complete
- Disarmed state
- Command timeout
- Low-voltage stop
- Emergency stop request
- 설정된 경우 encoder 또는 motor fault
- Firmware internal fault

규칙:

```text
Safety gating은 선택사항이 아니며 UART, CAN, ESP32, ROS2가 우회할 수 없다.
```

## 10. ISR Rules

Interrupt service routine은 짧게 유지해야 한다.

ISR에서 허용되는 동작:

- Timestamp capture
- Hardware flag read/clear
- ISR-safe queue에 작은 event push
- ISR-safe semaphore give
- 필요한 경우 단순 counter 증가

ISR에서 피해야 하는 동작:

- Text parsing
- `printf`
- 긴 I2C transaction
- Blocking HAL call
- 복잡한 motor control logic 직접 실행
- Heap allocation

권장 pattern:

```text
ISR detects event
    |
    v
notify task or push event
    |
    v
task performs heavier work
```

## 11. Communication Task

`comm_task`는 command parsing을 소유한다.

초기 책임:

- UART byte 또는 line receive.
- Newline-terminated ASCII command frame parse.
- Required field validate.
- 명백히 잘못된 값을 queueing 전에 clamp.
- Last command receive time update.
- Valid command request를 `command_queue`로 전달.
- Unknown message type은 안전하게 ignore.

Deferred responsibilities:

- CAN receive handling
- Binary packet parsing
- CRC validation
- ROS2 bridge integration

중요 규칙:

```text
comm_task는 PWM 또는 DIR pin을 직접 쓰지 않는다.
```

## 12. Motor Control Task

`motor_control_task`는 deterministic drivetrain output을 소유한다.

Responsibilities:

- Fixed period로 실행.
- 최신 command request 읽기.
- Encoder counter 읽기.
- Left/right wheel speed estimate.
- Ramp limit 적용.
- 초기 open-loop 또는 closed-loop control 적용.
- Motion request를 left/right motor command로 변환.
- Safety gate result 적용.
- MDD10A PWM과 DIR output update.

초기 control mode:

- Low-duty open-loop output으로 시작한다.
- Encoder validation 이후 speed estimation을 추가한다.
- Encoder reading이 안정된 뒤 P 또는 PID speed control을 추가한다.

규칙:

```text
Motor loop는 communication, telemetry, IMU read를 기다리면 안 된다.
```

## 13. Safety Task

`safety_task`는 safety state update를 소유한다.

Responsibilities:

- Command timeout 확인.
- Battery voltage state 확인.
- Disarm/arm state 확인.
- Startup delay 확인.
- Emergency stop request 확인.
- Firmware fault flag 확인.
- Safety state와 fault code publish.

Safety output:

- `SAFETY_ARMED_ACTIVE`일 때만 nonzero motor output이 허용되고,
  `SAFETY_ARMED_IDLE`은 output zero를 유지한다.
- Unsafe state는 motor-control output path를 통해 PWM zero와 driver disable을 강제한다.

중요:

정확한 state machine은 `16_Control_Loop_and_State_Machine_ko.md`에서 정의한다. 이 문서는 RTOS task
ownership만 정의한다.

## 14. Battery Task

`battery_task`는 battery ADC sampling과 filtering을 소유한다.

Responsibilities:

- ADC value trigger 또는 read.
- ADC count를 pack voltage로 변환.
- Simple filtering 적용.
- Warning/stop threshold와 비교.
- Battery state를 `safety_task`에 제공.
- Voltage telemetry 제공.

Rules:

- ADC conversion이 motor control을 block하면 안 된다.
- Low-voltage decision은 noisy sample 하나로 false stop이 발생하지 않도록 debounce 또는 filtering이
  필요하다.
- LiPo alarm은 firmware와 독립적으로 유지한다.

## 15. IMU Task

`imu_task`는 basic motor control과 UART telemetry가 안정된 뒤 도입한다.

Responsibilities:

- BNO08x data read.
- IMU health tracking.
- Yaw/attitude 또는 yaw-rate data 제공.
- Reduced telemetry publish.
- 추후 odometry fusion experiment 지원.

Rules:

- I2C read가 motor-control loop를 block하면 안 된다.
- IMU failure가 motor output을 uncontrolled 상태로 만들면 안 된다.
- 어떤 mode가 IMU data를 필수로 요구한다면, safety 또는 mode logic이 missing IMU data를 명시적으로
  처리해야 한다.

## 16. Telemetry Task

`telemetry_task`는 status output을 소유한다.

초기 telemetry fields:

- firmware uptime
- safety state
- fault code
- latest command sequence
- command age
- left/right encoder count
- left/right estimated speed
- battery voltage
- motor PWM duty
- optional IMU yaw/attitude

규칙:

```text
Telemetry는 data를 drop해도 된다.
Motor control은 telemetry를 기다리면 안 된다.
```

## 17. Future CAN Extension

CAN은 같은 task architecture를 재사용해야 한다.

Future options:

| Option | Description |
| --- | --- |
| Extend `comm_task` | UART와 CAN이 같은 queue로 motion command를 생산 |
| Add `can_task` | CAN RX/TX를 UART parsing과 분리 |

초기 권장:

- UART를 `comm_task`에서 먼저 시작한다.
- CAN은 이후 standalone으로 검증한다.
- CAN 통합 시 `comm_task` 확장 또는 `can_task` 추가 중 하나를 선택하되, 같은 `command_queue`와
  safety gate를 유지한다.
- CAN RX ISR에서 queue로 parser task에 넘기는 실습은 [`../../../Embedded/STM32/RTOS/Practice/P06_CAN_RX_Queue_Integration/README.md`](../../../Embedded/STM32/RTOS/Practice/P06_CAN_RX_Queue_Integration/README.md)에 둔다.

규칙:

```text
CAN은 transport를 바꾸는 것이지 motor safety owner를 바꾸는 것이 아니다.
```

## 18. Debug and Measurement Plan

FreeRTOS evidence targets:

| Evidence | Purpose |
| --- | --- |
| Task table | Ownership과 timing design 제시 |
| Runtime counters | Task가 살아 있는지 확인 |
| Loop period log | Motor loop timing 확인 |
| Command timeout test | Communication이 safety를 소유하지 않음을 확인 |
| Low-voltage simulated test | Safety가 motor output을 stop할 수 있음을 확인 |
| Queue overflow test | Stale command가 safety를 block하지 않음을 확인 |
| Telemetry under motor load | Logging이 control을 깨지 않음을 확인 |

Useful debug fields:

```text
uptime_ms
task_counter_motor
task_counter_safety
task_counter_comm
task_counter_telemetry
last_command_age_ms
safety_state
fault_code
motor_loop_max_dt_ms
```

## 19. Migration Plan

### Step 1: Keep Bare-Metal Firmware Working

FreeRTOS를 켜기 전에 HAL bare-metal version을 known-good baseline으로 보존한다.

### Step 2: Move Command Parsing

UART parsing을 `comm_task`로 옮기되 motor output logic은 단순하게 유지한다.

### Step 3: Move Motor Loop

Periodic motor update를 `vTaskDelayUntil()` 기반 `motor_control_task`로 옮긴다.

### Step 4: Add Safety Task

Timeout, disarm, low-voltage decision을 `safety_task`로 옮긴다.

### Step 5: Add Battery and Telemetry Tasks

느린 monitoring과 logging을 motor control에서 분리한다.

### Step 6: Add IMU Task

Motor와 telemetry timing이 안정된 뒤 IMU를 추가한다.

### Step 7: Prepare CAN Integration

CAN을 추가해도 drivetrain logic을 다시 쓰지 않도록 command queue와 safety gate를 transport-independent하게
유지한다.

## 20. Exit Criteria

FreeRTOS architecture는 다음 조건을 만족하면 accepted로 본다.

- `motor_control_task`가 low-speed control에 충분히 안정적인 period로 동작한다.
- `comm_task`가 PWM output을 직접 쓸 수 없다.
- Command parsing이 motor output update를 block하지 않는다.
- Command timeout이 motor를 stop한다.
- `safety_task`가 motor output을 독립적으로 stop할 수 있다.
- `telemetry_task`를 느리게 하거나 꺼도 motor control이 깨지지 않는다.
- Battery voltage state가 safety logic에 도달한다.
- Task responsibility가 문서화되어 있다.
- Timing 또는 runtime log가 존재한다.

## Final Decision

FreeRTOS는 bare-metal drivetrain baseline이 동작한 뒤 도입한다.

RTOS architecture의 핵심 원칙은 하나다. Communication, telemetry, sensor processing은 data를
제공할 수 있지만, STM32 safety logic과 motor control task만 motor output으로 이어지는 경로가 된다.
