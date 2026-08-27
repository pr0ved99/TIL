# Control Loop and State Machine

## Purpose

This document defines the low-level drivetrain control loop and safety state
machine for the tracked mobile robot.

The goal is to make motor output deterministic and safe regardless of whether
commands arrive from USB/UART, ESP32, CAN, or a future ROS2 bridge.

This document answers:

- Which states the robot controller can enter
- Which events cause state transitions
- When motor output is allowed
- How command timeout, low voltage, and emergency stop affect motion
- How the motor control loop applies commands to the MDD10A driver

## Architecture Decision

STM32 owns the final motor output state.

Core rule:

```text
Communication code may request motion.
The state machine decides whether motion is allowed.
The motor control loop is the only code path that writes PWM outputs.
```

This rule must remain true for UART, CAN, ESP32, and future ROS2 integration.

## 1. Terms

| Term | Meaning in this project |
| --- | --- |
| State machine | Explicit list of controller states and allowed transitions |
| Safety gate | Logic that allows or blocks motor output |
| Control loop | Periodic firmware loop that reads state, estimates speed, and updates PWM |
| Command timeout | Condition where no valid command has arrived within the allowed time |
| Arm | Allow limited motor output if all safety preconditions are satisfied |
| Disarm | Disable motor output intentionally |
| E-stop | Emergency stop request that latches a safe stop state |
| Fault | Abnormal condition that must block motor output |

## 2. State List

Initial safety state enum:

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
| `SAFETY_BOOT` | Disabled | Startup, output must remain safe |
| `SAFETY_DISARMED` | Disabled | Normal safe idle state |
| `SAFETY_ARMING_CHECK` | Disabled | Checking whether arm is allowed |
| `SAFETY_ARMED_IDLE` | Enabled but zero command | Armed, no active motion command |
| `SAFETY_ARMED_ACTIVE` | Limited output allowed | Valid command is being applied |
| `SAFETY_LOW_VOLTAGE_STOP` | Disabled | Battery below stop threshold |
| `SAFETY_ESTOP_LATCHED` | Disabled | Emergency stop requested |
| `SAFETY_FAULT_LATCHED` | Disabled | Firmware, sensor, encoder, driver, or internal fault |

`SAFETY_TIMEOUT_STOP` was an earlier candidate. ADR-015 makes Final MVP command
source loss converge directly to `SAFETY_DISARMED`, so it is not in the target
state list.

## 3. Events

Events that affect state:

| Event | Source | Notes |
| --- | --- | --- |
| `boot_complete` | firmware init | All outputs initialized safe |
| `arm_request` | UART/CAN/ESP32 | Request only, not authority |
| `disarm_request` | UART/CAN/ESP32/operator | Always allowed |
| `valid_motion_command` | command parser | Must pass field validation |
| `command_timeout` | safety task or loop | No fresh command |
| `heartbeat_timeout` | CAN or future bridge | Command source missing |
| `low_voltage_warning` | battery task | Warn only |
| `low_voltage_stop` | battery task | Blocks output |
| `estop_request` | operator/command | Latches stop |
| `fault_detected` | firmware checks | Latches fault |
| `fault_clear_request` | operator/debug | Accepted only if condition is gone |

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

Timeout and recovery rules:

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

The controller must not replay the pre-timeout command or accept motion without
a new `ARM`.

## 5. Arm Preconditions

Arm request is accepted only if:

- Boot initialization is complete.
- Battery voltage is above stop threshold.
- No E-stop is latched.
- No active fault is latched.
- Motor PWM output is currently zero.
- PWM compare values are zero.
- The selected Final MVP production ingress is the ESP32 single owner and the session is not stale.
- Optional: robot is physically safe for the current test stage.

If any condition fails, the controller stays disarmed or enters a latched fault
state.

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
    +-- unsafe -> PWM = 0, motor output blocked
    |
    +-- safe   -> apply limited MDD10A PWM + DIR output
```

Rules:

- The loop must not block waiting for UART, CAN, IMU, or telemetry.
- The loop must ramp PWM to zero before changing motor direction.
- The loop must update PWM duty and DIR state inside the same control-loop
  ownership boundary.

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
| `vx_mmps` | Reject values outside `-100..100`; do not change the active command |
| `w_mradps` | Reject values outside `-500..500`; do not change the active command |
| `timeout_ms` | Reject values outside `50..500`; initial default is 300 ms |
| `seq` | Used for telemetry and stale command inspection |

Invalid command behavior:

- Do not update the active command.
- Report invalid command count if telemetry supports it.
- Do not change motor output directly from parser code.

## 8. MDD10A Output Mapping

Each motor uses sign-magnitude `PWM + DIR`.

| Signed command | `PWMx` | `DIRx` | Motor output |
| --- | --- | --- | --- |
| Unsafe state | 0 | don't care | blocked by zero PWM |
| Zero command | 0 | keep last or default | stop |
| Positive command | duty | forward mapping | forward |
| Negative command | duty | reverse mapping | reverse |
| Forbidden | duty | duty | Not allowed |

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

Initial fault code enum:

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

Not every fault must be implemented in the first firmware. The enum defines
the expected growth path.

## 10. Low-Voltage Behavior

Voltage states:

| State | Behavior |
| --- | --- |
| Normal | Operation allowed if no other fault exists |
| Warning | Telemetry warning, motion may continue during early tests |
| Stop | Motor output disabled |

Rules:

- Firmware low-voltage stop does not replace the physical LiPo alarm.
- Low-voltage decision should use filtering or debounce.
- If low voltage stop triggers, recovery requires operator action.

## 11. Startup and Reset Behavior

Startup requirements:

- Configure PWM outputs to zero.
- MDD10A has no separate enable pin, so PWM zero is the basic output block.
- Initialize state to `SAFETY_BOOT`.
- Verify basic initialization.
- Transition to `SAFETY_DISARMED`.

Watchdog or reset behavior:

- Hardware reset must leave motor output safe.
- External pull-downs on PWM lines or a separate power gate circuit should be
  considered.
- Firmware should not arm automatically after reset.

## 12. Telemetry Fields

Telemetry should expose state-machine behavior.

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

These fields make timeout, safety, and output behavior testable.

## 13. Validation Tests

| Test | Expected result |
| --- | --- |
| Boot without command | State becomes `SAFETY_DISARMED`, PWM zero |
| Arm with safe conditions | State becomes `SAFETY_ARMED_IDLE` |
| Motion command while armed | State becomes `SAFETY_ARMED_ACTIVE`, limited PWM output |
| Stop command | PWM zero, state returns to idle or disarmed |
| Command timeout | Output/stored command zero, state becomes `SAFETY_DISARMED`; stale `CMD` is rejected and a new `ARM` then new `CMD` is required |
| E-stop command | State becomes `SAFETY_ESTOP_LATCHED`, output disabled |
| Low-voltage simulated | State becomes `SAFETY_LOW_VOLTAGE_STOP`, output disabled |
| Fault injected | State becomes `SAFETY_FAULT_LATCHED`, output disabled |

## Final Decision

The controller uses an explicit safety state machine.

Only `SAFETY_ARMED_IDLE` and `SAFETY_ARMED_ACTIVE` can allow motor output
permission, and only `SAFETY_ARMED_ACTIVE` can apply nonzero PWM.

All other states force:

```text
PWM = 0
nonzero motor output blocked
```

This is the ADR-015 required model. Current firmware still remains `ARMED`
after timeout, so `P-03` implementation and target runtime evidence are pending.
