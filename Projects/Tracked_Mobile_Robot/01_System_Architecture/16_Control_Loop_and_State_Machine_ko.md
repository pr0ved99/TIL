# Control Loop and State Machine

## 목적

이 문서는 궤도형 모바일 로봇의 low-level drivetrain control loop와 safety state machine을 정의한다.

목표는 command가 USB/UART, ESP32, CAN, future ROS2 bridge 중 어디에서 오더라도 motor output을
deterministic하고 safe하게 만드는 것이다.

이 문서는 다음 질문에 답한다.

- Robot controller가 어떤 state에 들어갈 수 있는가
- 어떤 event가 state transition을 일으키는가
- 언제 motor output이 허용되는가
- Command timeout, low voltage, emergency stop이 motion에 어떤 영향을 주는가
- Motor control loop가 command를 MDD10A driver에 어떻게 적용하는가

## Architecture Decision

STM32가 final motor output state를 소유한다.

핵심 규칙:

```text
Communication code는 motion을 요청할 수 있다.
State machine은 motion 허용 여부를 결정한다.
Motor control loop만 PWM output을 쓴다.
```

이 규칙은 UART, CAN, ESP32, future ROS2 integration에서도 유지되어야 한다.

## 1. 용어

| Term | 이 프로젝트에서의 의미 |
| --- | --- |
| State machine | Controller state와 허용 transition을 명시한 구조 |
| Safety gate | Motor output을 허용하거나 차단하는 logic |
| Control loop | State를 읽고, speed를 추정하고, PWM을 update하는 주기 firmware loop |
| Command timeout | 허용 시간 내 valid command가 도착하지 않은 상태 |
| Arm | Safety precondition이 만족될 때 제한된 motor output 허용 |
| Disarm | Motor output을 의도적으로 disable |
| E-stop | Safe stop state를 latch하는 emergency stop request |
| Fault | Motor output을 block해야 하는 abnormal condition |

## 2. State List

초기 safety state enum:

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

State meaning:

| State | Motor output | Meaning |
| --- | --- | --- |
| `SAFETY_BOOT` | Disabled | Startup, output은 반드시 safe |
| `SAFETY_DISARMED` | Disabled | 일반 safe idle state |
| `SAFETY_ARMING_CHECK` | Disabled | Arm 가능 여부 확인 중 |
| `SAFETY_ARMED_IDLE` | Enabled but zero command | Armed, active motion command 없음 |
| `SAFETY_ARMED_ACTIVE` | Limited output allowed | Valid command가 적용 중 |
| `SAFETY_LOW_VOLTAGE_STOP` | Disabled | Battery가 stop threshold 아래 |
| `SAFETY_ESTOP_LATCHED` | Disabled | Emergency stop request 발생 |
| `SAFETY_FAULT_LATCHED` | Disabled | Firmware, sensor, encoder, driver, internal fault |

`SAFETY_TIMEOUT_STOP`은 과거 후보 상태였으나 ADR-015에서 Final MVP command-source loss를
즉시 `SAFETY_DISARMED`로 귀결하도록 확정했으므로 현재 목표 state list에서는 사용하지 않는다.

## 3. Events

State에 영향을 주는 event:

| Event | Source | Notes |
| --- | --- | --- |
| `boot_complete` | firmware init | 모든 output이 safe로 초기화됨 |
| `arm_request` | UART/CAN/ESP32 | 권한이 아니라 요청 |
| `disarm_request` | UART/CAN/ESP32/operator | 항상 허용 |
| `valid_motion_command` | command parser | Field validation 통과 필요 |
| `command_timeout` | safety task 또는 loop | Fresh command 없음 |
| `heartbeat_timeout` | CAN 또는 future bridge | Command source missing |
| `low_voltage_warning` | battery task | Warning only |
| `low_voltage_stop` | battery task | Output block |
| `estop_request` | operator/command | Stop latch |
| `fault_detected` | firmware checks | Fault latch |
| `fault_clear_request` | operator/debug | 조건이 사라진 경우에만 accept |

## 4. State Transition Overview

```text
SAFETY_BOOT
    |
    +-- boot_complete -----------------> SAFETY_DISARMED

SAFETY_DISARMED
    |
    +-- arm_request -------------------> SAFETY_ARMING_CHECK
    +-- fault_detected ----------------> SAFETY_FAULT_LATCHED
    +-- low_voltage_stop --------------> SAFETY_LOW_VOLTAGE_STOP

SAFETY_ARMING_CHECK
    |
    +-- checks_pass -------------------> SAFETY_ARMED_IDLE
    +-- checks_fail -------------------> SAFETY_DISARMED or FAULT

SAFETY_ARMED_IDLE
    |
    +-- valid_motion_command ----------> SAFETY_ARMED_ACTIVE
    +-- disarm_request ----------------> SAFETY_DISARMED
    +-- command_timeout ---------------> SAFETY_DISARMED
    +-- low_voltage_stop --------------> SAFETY_LOW_VOLTAGE_STOP
    +-- estop_request -----------------> SAFETY_ESTOP_LATCHED
    +-- fault_detected ----------------> SAFETY_FAULT_LATCHED

SAFETY_ARMED_ACTIVE
    |
    +-- command becomes zero ----------> SAFETY_ARMED_IDLE
    +-- command_timeout ---------------> SAFETY_DISARMED
    +-- disarm_request ----------------> SAFETY_DISARMED
    +-- low_voltage_stop --------------> SAFETY_LOW_VOLTAGE_STOP
    +-- estop_request -----------------> SAFETY_ESTOP_LATCHED
    +-- fault_detected ----------------> SAFETY_FAULT_LATCHED
```

Timeout과 recovery 규칙:

```text
command_timeout
    -> motor output zero
    -> stored command zero
    -> SAFETY_DISARMED
    -> new ARM
    -> new CMD

SAFETY_LOW_VOLTAGE_STOP
    +-- voltage recovered + operator reset -> SAFETY_DISARMED

SAFETY_ESTOP_LATCHED
    +-- explicit reset after operator check -> SAFETY_DISARMED

SAFETY_FAULT_LATCHED
    +-- fault cleared + explicit reset -> SAFETY_DISARMED
```

Timeout 시 이전 stored command를 zero로 만들고 자동 재적용하지 않는다. `DISARMED`에서
수신한 `CMD`는 `ARM`이 수락될 때까지 거부한다. P-03은 transport/session freshness를
판별하지 않으므로 queue에 남았거나 replay된 `ARM` + `CMD` 쌍의 차단은 구현 범위가 아니다.

## 5. Arm Preconditions

Arm request는 다음 조건에서만 accept된다.

- Boot initialization complete.
- Battery voltage가 stop threshold보다 높다.
- E-stop이 latch되어 있지 않다.
- Active fault가 latch되어 있지 않다.
- Motor PWM output이 현재 zero.
- PWM compare 값이 zero.
- Final MVP production ingress가 ESP32 단일 owner로 선택되어 있다.
- Target anti-replay 단계에서는 session freshness도 확인해야 하지만 P-03에는 이 검사가 없다.
- Optional: 현재 test stage에서 robot이 물리적으로 safe.

하나라도 실패하면 controller는 disarmed에 남거나 latched fault state로 들어간다.

## 6. Motor Control Loop

Initial target period:

```text
10 ms / 100 Hz
```

Control loop flow:

```text
read latest command request
    |
    v
read safety state
    |
    v
read encoder counters
    |
    v
estimate left/right wheel speed
    |
    v
apply command timeout and ramp limits
    |
    v
convert command to left/right motor request
    |
    v
apply safety gate
    |
    +-- unsafe -> PWM = 0, motor output disabled
    |
    +-- safe   -> apply limited MDD10A PWM + DIR output
```

Rules:

- Loop는 UART, CAN, IMU, telemetry를 기다리며 block하면 안 된다.
- Loop는 방향 전환 전에 해당 motor PWM을 0까지 낮춰야 한다.
- Loop는 PWM duty와 DIR state를 같은 control-loop ownership 안에서 갱신해야 한다.

## 7. Command Model

Internal motion command:

```c
typedef struct {
    uint32_t seq;
    int32_t vx_mmps;
    int32_t w_mradps;
    uint32_t timeout_ms;
    uint32_t rx_time_ms;
} motion_command_t;
```

Initial command limits:

| Field | Initial handling |
| --- | --- |
| `vx_mmps` | `-100~100` 범위 밖이면 거부; active command를 바꾸지 않음 |
| `w_mradps` | `-500~500` 범위 밖이면 거부; active command를 바꾸지 않음 |
| `timeout_ms` | `50~500` 범위 밖이면 거부; 초기 기본값 300 ms |
| `seq` | Response/telemetry correlation에 사용하며 P-03은 sequence freshness로 command를 거부하지 않음 |

Invalid command behavior:

- Active command를 update하지 않는다.
- Telemetry가 지원하면 invalid command count를 report한다.
- Parser code가 motor output을 직접 바꾸지 않는다.

## 8. MDD10A Output Mapping

각 motor는 sign-magnitude 방식의 `PWM + DIR`을 사용한다.

| Signed command | `PWMx` | `DIRx` | Motor output |
| --- | --- | --- | --- |
| Unsafe state | 0 | don't care | disabled by zero PWM |
| Zero command | 0 | keep last or default | stop |
| Positive command | duty | forward mapping | forward |
| Negative command | duty | reverse mapping | reverse |

Safe update order:

```text
if unsafe:
    set PWM = 0
else if direction must change:
    ramp PWM to 0
    set DIR
    set limited PWM
else:
    set limited PWM
```

## 9. Fault Codes

초기 fault code enum:

```c
typedef enum {
    FAULT_NONE = 0,
    FAULT_COMMAND_TIMEOUT,
    FAULT_HEARTBEAT_TIMEOUT,
    FAULT_LOW_VOLTAGE,
    FAULT_ESTOP,
    FAULT_ENCODER_STUCK,
    FAULT_ENCODER_DIRECTION,
    FAULT_MOTOR_OUTPUT,
    FAULT_CAN_BUS_OFF,
    FAULT_INTERNAL_ASSERT
} fault_code_t;
```

첫 firmware에서 모든 fault를 구현할 필요는 없다. 이 enum은 성장 방향을 정의한다.

## 10. Low-Voltage Behavior

Voltage states:

| State | Behavior |
| --- | --- |
| Normal | 다른 fault가 없으면 operation allowed |
| Warning | Telemetry warning, 초기 test에서는 motion 지속 가능 |
| Stop | Motor output disabled |

Rules:

- Firmware low-voltage stop은 물리 LiPo alarm을 대체하지 않는다.
- Low-voltage decision은 filtering 또는 debounce가 필요하다.
- Low-voltage stop이 trigger되면 recovery는 operator action을 요구한다.

## 11. Startup and Reset Behavior

Startup requirements:

- PWM output을 zero로 설정한다.
- MDD10A에는 별도 enable pin이 없으므로 기본 차단 수단은 PWM zero다.
- State를 `SAFETY_BOOT`로 초기화한다.
- 기본 initialization을 확인한다.
- `SAFETY_DISARMED`로 transition한다.

Watchdog 또는 reset behavior:

- Hardware reset은 motor output safe 상태를 만들어야 한다.
- PWM line external pull-down 또는 별도 power gate 회로를 검토한다.
- Firmware는 reset 이후 자동 arm하면 안 된다.

## 12. Telemetry Fields

Telemetry는 state-machine behavior를 보여줘야 한다.

Recommended fields:

```text
uptime_ms
safety_state
fault_code
last_command_seq
last_command_age_ms
left_pwm
right_pwm
left_encoder_count
right_encoder_count
battery_mv
loop_dt_max_us
```

이 field들은 timeout, safety, output behavior를 testable하게 만든다.

## 13. Validation Tests

| Test | Expected result |
| --- | --- |
| Boot without command | State가 `SAFETY_DISARMED`, PWM zero |
| Arm with safe conditions | State가 `SAFETY_ARMED_IDLE` |
| Motion command while armed | State가 `SAFETY_ARMED_ACTIVE`, limited PWM output |
| Stop command | PWM zero, state가 idle 또는 disarmed로 복귀 |
| Command timeout | PWM/stored command zero, state가 `SAFETY_DISARMED`; CMD-only 거부 뒤 accepted `ARM`과 valid `CMD`로 복구, transport anti-replay는 pending |
| E-stop command | State가 `SAFETY_ESTOP_LATCHED`, PWM zero |
| Low-voltage simulated | State가 `SAFETY_LOW_VOLTAGE_STOP`, PWM zero |
| Fault injected | State가 `SAFETY_FAULT_LATCHED`, PWM zero |

## Final Decision

Controller는 explicit safety state machine을 사용한다.

`SAFETY_ARMED_IDLE`과 `SAFETY_ARMED_ACTIVE`만 motor output permission을 허용할 수 있고,
nonzero PWM은 `SAFETY_ARMED_ACTIVE`에서만 적용된다.

다른 모든 state는 다음을 강제한다.

```text
PWM = 0
nonzero motor output blocked
```

이 항목은 ADR-015의 required state model이다. P-03A/P-03B source/static/full-build는 pre-RX
timeout에서 output/stored command zero와 `DISARMED` 전이를 강제하고, `ARM`에서 default
300 ms first-CMD window를 다시 시작하는 계약을 PASS했다. Flash/board/PWM target runtime
검증 전에는 이 state transition의 실기 PASS를 주장하지 않는다.
