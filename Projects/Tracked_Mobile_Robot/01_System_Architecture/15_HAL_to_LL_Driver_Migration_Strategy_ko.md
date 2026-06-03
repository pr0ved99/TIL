# HAL to LL Driver Migration Strategy

## 목적

이 문서는 drivetrain이 이미 동작한 뒤 STM32 firmware의 일부 경로를 HAL에서 LL Driver로 전환하는 전략을
정의한다.

LL 전환은 필수 engineering-depth 목표지만, 첫 bring-up 단계는 아니다. 첫 firmware는 CubeMX와 HAL을
사용해 wiring, clock, timer, peripheral 설정 위험을 줄인다. LL은 나중에 timing clarity, register-level
이해, control-loop determinism을 개선할 수 있는 부분에만 도입한다.

이 문서는 다음 질문에 답한다.

- 왜 프로젝트를 HAL로 시작하는가
- 어떤 code path가 좋은 LL migration target인가
- 어떤 code path는 처음에 HAL로 남겨야 하는가
- 이미 동작하는 motor controller를 망가뜨리지 않고 어떻게 전환하는가
- LL 전환이 유용했다는 증거는 무엇인가

## Architecture Decision

HAL로 시작하고, 안정적인 project interface 뒤에서 timing-critical path만 LL로 전환한다.

Migration direction:

```text
HAL bare-metal MVP
    -> HAL + FreeRTOS baseline
    -> LL for selected GPIO/PWM/encoder/timer paths
    -> optional LL for ADC and CAN paths
```

핵심 결정:

```text
HAL은 bring-up 안정성을 위해 사용한다.
LL은 timing-critical 및 safety-relevant path에 나중에 사용한다.
```

프로젝트 전체를 LL로 다시 작성하는 것은 목표가 아니다.

## 1. HAL과 LL 용어

| Term | 이 프로젝트에서의 의미 |
| --- | --- |
| HAL | CubeMX와 함께 쉽게 생성/사용하는 STM32 high-level driver layer |
| LL Driver | Peripheral register에 더 가까운 lower-level STM32 driver layer |
| Register | MCU hardware 설정 또는 data field가 memory에 mapping된 것 |
| Migration | 동작하는 HAL path를 같은 behavior를 유지하며 LL path로 교체하는 일 |
| Baseline | 비교 기준이 되는 known-good HAL behavior |
| Regression | 이전에는 되던 behavior가 migration 이후 깨지는 것 |
| Jitter | Loop period 또는 signal timing의 흔들림 |

## 2. HAL로 시작하는 이유

이 프로젝트의 첫 단계는 HAL이 맞다.

이유:

- CubeMX가 pin, clock, alternate-function 설정 실수를 줄여준다.
- HAL example은 검색, debug, 수정이 쉽다.
- UART, ADC, I2C, CAN, timer bring-up이 빠르다.
- 초기 문제는 HAL overhead보다 wiring, power, pin, driver 문제일 가능성이 높다.
- 동작하는 HAL version이 있어야 LL 변경의 비교 기준이 생긴다.

규칙:

```text
HAL version이 검증되지 않은 peripheral은 LL로 전환하지 않는다.
```

## 3. 일부 경로를 LL로 전환하는 이유

LL은 다음 상황에서 유용하다.

- Timer와 GPIO behavior를 더 직접적으로 이해하고 싶을 때
- 반복되는 high-rate operation의 overhead를 줄이고 싶을 때
- Interrupt timing을 명확히 통제하고 싶을 때
- Timing inspection을 쉽게 만들고 싶을 때
- Embedded portfolio evidence를 강화하고 싶을 때

좋은 LL migration은 모든 line을 빠르게 만드는 작업이 아니다. Firmware에서 어떤 부분이
timing-critical인지 알고, 그 변경을 검증할 수 있음을 보여주는 작업이다.

## 4. Entry Criteria

LL migration은 다음 조건 이후에 시작한다.

- Motor 1개가 HAL 제어로 forward/reverse 동작한다.
- Left/right BTS7960 PWM output이 low duty에서 검증된다.
- Encoder counting이 HAL 설정으로 동작한다.
- Command timeout이 motor output을 정지시킨다.
- Safety gate가 PWM zero와 driver disable을 강제한다.
- Known-good HAL firmware commit 또는 branch가 존재한다.
- Basic telemetry가 loop timing, command age, PWM, encoder 값을 보여준다.

이 조건이 아니면 LL migration은 전문성을 높이는 게 아니라 debug를 어렵게 만든다.

## 5. Migration Principles

규칙:

1. High-level application logic은 유지한다.
2. Peripheral access를 project-local function 뒤에 숨긴다.
3. 한 번에 하나의 peripheral path만 전환한다.
4. HAL version을 비교용으로 유지한다.
5. Migration 전후 behavior를 측정하거나 log로 남긴다.
6. Migration마다 regression checklist를 실행한다.
7. Safety-critical output은 safe default test 없이 전환하지 않는다.

Project-local wrapper 예시:

```c
void motor_pwm_set_left(int16_t duty);
void motor_pwm_set_right(int16_t duty);
int32_t encoder_get_left_count(void);
int32_t encoder_get_right_count(void);
void driver_enable_set(bool enabled);
uint16_t battery_adc_read_raw(void);
```

Application code는 HAL 또는 LL을 직접 호출하지 않고 이 wrapper를 호출한다.

## 6. 권장 Migration Targets

| Target | Initial HAL path | LL migration reason | Priority |
| --- | --- | --- | --- |
| BTS7960 enable GPIO | `HAL_GPIO_WritePin()` | 작고 쉬운 첫 LL migration, safety output clarity | High |
| PWM compare update | `__HAL_TIM_SET_COMPARE()` 또는 HAL PWM helper | High-rate motor duty update path | High |
| Encoder count read | `__HAL_TIM_GET_COUNTER()` | Frequent control-loop read path | High |
| Control-loop timer interrupt | HAL timer callback | Loop timing과 ISR ownership clarity | Medium |
| ADC raw read | HAL ADC polling 또는 interrupt | Battery monitor path 안정화 이후 | Medium |
| CAN RX/TX | HAL CAN callbacks | CAN baseline 이후 선택 | Low to medium |

## 7. 첫 LL Migration으로 권장하지 않는 경로

처음에는 다음 경로를 피한다.

| Path | Reason |
| --- | --- |
| UART command text parsing | Parsing logic 비중이 크고 LL 이점이 작다 |
| Debug `printf` path | Debug 편의성이 optimization보다 중요하다 |
| BNO08x I2C bring-up | Sensor protocol debug 자체가 이미 복잡하다 |
| ESP32 Wi-Fi 또는 dashboard logic | STM32 timing-critical path가 아니다 |
| Full CAN protocol stack | HAL CAN을 먼저 검증한 뒤 결정한다 |
| FreeRTOS kernel internals | 프로젝트 migration 대상이 아니다 |

규칙:

```text
Application architecture 전체가 아니라 peripheral access를 전환한다.
```

## 8. Layering Model

권장 firmware layering:

```text
Application / control logic
        |
        v
Project driver interface
        |
        v
HAL implementation or LL implementation
        |
        v
STM32 peripheral registers
```

예시:

```text
motor_control_task
        |
        v
motor_pwm_set_left()
        |
        +-- HAL implementation in baseline
        |
        +-- LL implementation after migration
```

이 구조는 control loop를 driver layer와 분리한다.

## 9. Migration Plan

### Step 0: HAL Baseline 보존

변경 전:

- HAL baseline을 commit 또는 tag로 남긴다.
- PWM frequency, control-loop rate, encoder behavior, safety test를 기록한다.
- 작은 test log를 저장한다.

Exit criteria:

- HAL version을 다시 build하고 flash할 수 있다.

### Step 1: Driver Wrapper 생성

직접 HAL 호출을 project-local function 뒤로 옮긴다.

예시:

- `motor_pwm_set_*()`
- `encoder_get_*()`
- `driver_enable_set()`
- `battery_adc_read_raw()`

Exit criteria:

- Firmware behavior는 그대로이고 HAL call 위치만 localized된다.

### Step 2: Driver Enable GPIO 전환

Enable GPIO write를 먼저 전환한다. 작고 테스트가 쉽기 때문이다.

Validation:

- Boot에서 enable disabled.
- Disarm이 driver를 disable.
- E-stop이 driver를 disable.
- Arm은 safety state가 허용할 때만 driver를 enable.

### Step 3: PWM Compare Update 전환

PWM compare update path를 LL로 교체한다.

Validation:

- Boot에서 PWM duty zero.
- Forward command는 motor당 BTS7960 PWM input 하나만 active.
- Reverse command는 반대 PWM input만 active.
- `RPWM`과 `LPWM`이 동시에 active되지 않는다.
- Duty clamp가 유지된다.

### Step 4: Encoder Count Read 전환

Encoder counter read와 필요 시 reset path를 LL로 교체한다.

Validation:

- Count가 기대 방향으로 증가한다.
- Left/right encoder sign이 motor command sign과 일치한다.
- Speed estimate가 HAL baseline과 허용 오차 안에서 일치한다.

### Step 5: Control-Loop Timer Path 전환

Motor와 encoder path가 안정된 뒤 loop timer 또는 ISR path 전환을 검토한다.

Validation:

- Motor loop period가 target에 가깝게 유지된다.
- Worst-case loop delay가 기록된다.
- ISR 내부에 blocking work가 추가되지 않는다.

### Step 6: Optional ADC 또는 CAN LL Migration

ADC 또는 CAN LL migration은 해당 feature가 HAL로 동작한 뒤 진행한다.

ADC validation:

- Raw ADC count가 voltage divider 측정값과 일치한다.
- Pack voltage estimate가 safety threshold에 사용할 만큼 안정적이다.

CAN validation:

- Loopback이 계속 동작한다.
- USB-CAN이 telemetry를 관찰한다.
- Heartbeat timeout이 motor output을 정지시킨다.

## 10. Measurement Plan

Migration 전후 값을 기록한다.

| Measurement | Purpose |
| --- | --- |
| Motor loop period average | 기대 control frequency 확인 |
| Motor loop max period | Jitter 또는 blocking 감지 |
| PWM output frequency | Timer 설정이 의도치 않게 바뀌지 않았는지 확인 |
| PWM duty command vs output | Compare update correctness 확인 |
| Encoder count direction | Timer mode와 sign 확인 |
| Command timeout behavior | Safety behavior regression 확인 |
| Boot output state | Reset 시 motor disabled 확인 |

Useful debug fields:

```text
loop_count
loop_dt_us
loop_dt_max_us
left_pwm_cmd
right_pwm_cmd
left_encoder_count
right_encoder_count
safety_state
fault_code
```

## 11. Regression Checklist

LL migration마다 실행한다.

- Firmware가 clean build된다.
- Board flashing이 성공한다.
- Boot state에서 PWM zero.
- Driver enable은 arm 조건 전까지 disabled.
- Stop command가 PWM zero를 강제한다.
- Command timeout이 PWM zero를 강제한다.
- Simulated low-voltage condition이 motor output을 block한다.
- Encoder count direction이 변하지 않았다.
- Telemetry가 safety state와 motor data를 계속 report한다.
- UART 또는 CAN command path가 safety gate를 우회할 수 없다.

## 12. Risks

| Risk | Mitigation |
| --- | --- |
| LL code가 CubeMX assumption을 우회 | Generated init code 유지, access function부터 전환 |
| Register 실수로 motor가 예상치 않게 구동 | Motor power disconnected 또는 track lifted 상태에서 테스트 |
| HAL과 LL이 같은 peripheral을 inconsistent하게 접근 | Wrapper file에서 ownership 중앙화 |
| Timing은 좋아졌지만 behavior가 깨짐 | Timing number만 보지 말고 regression checklist 사용 |
| Debugging이 어려워짐 | HAL baseline branch 유지, migration마다 문서화 |

## 13. Portfolio Evidence

LL migration은 code만이 아니라 evidence를 남겨야 한다.

Evidence targets:

- Before/after architecture note
- HAL baseline commit reference
- LL migration commit reference
- PWM 또는 timing measurement screenshot
- Wrapper isolation을 보여주는 code diff
- Regression checklist result
- 왜 해당 path를 migration했는지 짧은 설명

강한 portfolio 문장:

```text
Validated HAL baseline 이후 STM32 motor output timing-critical path를 LL로 전환하고,
safety behavior와 motor output timing이 regression되지 않았음을 확인했다.
```

## Final Decision

프로젝트는 LL Driver로 시작하지 않는다.

먼저 동작하는 HAL baseline을 만들고, 이후 다음 순서로 선택적 LL migration을 진행한다.

```text
GPIO enable
-> PWM compare update
-> encoder count read
-> control-loop timer path
-> optional ADC/CAN path
```

모든 LL migration은 HAL baseline과 같은 safety behavior를 유지해야 한다.
