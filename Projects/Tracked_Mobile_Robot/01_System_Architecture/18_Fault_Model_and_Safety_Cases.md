# Fault Model and Safety Cases

## Purpose

This document defines the expected fault cases for the tracked mobile robot and
the required safe response for each case.

The project uses a 3S LiPo battery, high-current DC motors, an MDD10A motor
driver, STM32 firmware, ESP32 support logic, and later CAN/ROS2 integration.
Fault handling must therefore cover both electrical and software failures.

This document answers:

- What can fail
- How the firmware or operator can detect it
- What the robot must do immediately
- What evidence should be captured during validation

## Safety Principle

The robot must fail toward no motion.

Core rule:

```text
When the controller is uncertain, motor output goes to zero and nonzero output is blocked.
```

This applies to UART, CAN, ESP32, ROS2, encoder, battery, and firmware faults.

## 1. Fault Severity Levels

| Level | Meaning | Motor response |
| --- | --- | --- |
| Info | Useful diagnostic condition | No automatic stop |
| Warning | Abnormal but not immediately dangerous | Limit or prepare stop |
| Stop | Motion must stop, recovery may be simple | PWM zero, driver disabled |
| Latched fault | Motion must stop until explicit reset | PWM zero, driver disabled |
| Hardware emergency | Operator must remove power | Use switch, disconnect battery if safe |

## 2. Fault Categories

| Category | Examples |
| --- | --- |
| Power faults | Low voltage, buck overvoltage, reverse polarity, fuse trip |
| Motor driver faults | MDD10A heat, wrong PWM/DIR mapping, unsafe direction reversal |
| Command faults | UART timeout, CAN heartbeat timeout, invalid command |
| Sensor faults | Encoder stuck, encoder sign mismatch, IMU missing |
| Firmware faults | Assertion failure, loop timing overrun, watchdog reset |
| Wiring faults | Loose ground, swapped CANH/CANL, encoder 5 V into unsafe pin |
| Mechanical faults | Track jam, high friction, chassis collision |
| Operator faults | Wrong connector polarity, wrong fuse, unsafe battery handling |

## 3. Fault Response Table

| Fault | Detection method | Immediate response | Recovery |
| --- | --- | --- | --- |
| Boot not complete | Startup state | Keep PWM zero | Complete init then disarmed |
| Command timeout | Command age exceeds timeout | Zero motor output/stored command, enter `DISARMED` | Accepted `ARM` then valid `CMD`; transport anti-replay separate |
| CAN heartbeat timeout | Missing heartbeat | Stop motors | Reconnect bus, disarm/arm |
| E-stop request | Command or physical input | Latch stop | Explicit operator reset |
| Low-voltage warning | ADC or LiPo alarm | Warn, reduce test scope | Recharge or stop soon |
| Low-voltage stop | ADC below stop threshold | Stop motors | Recharge, operator reset |
| Buck output wrong | Multimeter check | Do not connect electronics | Adjust/replace converter |
| Encoder stuck | Commanded motion but no count change | Stop or limit motion | Inspect wiring/mechanics |
| Encoder direction mismatch | Sign check fails | Do not enter closed-loop mode | Fix sign mapping |
| Direction change while PWM active | Firmware assertion or output audit | Force PWM zero | Fix motor output code |
| Motor overheat | Operator touch/IR thermometer | Stop test | Cool down, reduce load |
| MDD10A overheat | Operator check | Stop test | Cool down, reduce load, recheck current margin |
| Fuse blows | Loss of motor/robot power | Stop test | Find root cause before replacing |
| Watchdog reset | Reset cause register/log | Remain disarmed after reboot | Inspect loop blocking |
| CAN bus-off | CAN error state | Stop motors, report fault | Fix bus, reset CAN |
| UART parse storm | Invalid frames repeated | Ignore, maintain timeout rules | Fix sender |
| IMU missing | No data or bus error | Disable IMU-dependent modes | Check wiring/I2C |

## 4. Power Safety Cases

### Case P1: Buck Converter Output Too High

Risk:

- STM32, ESP32, sensors, or encoder logic can be damaged.

Detection:

- Measure buck output before connecting boards.

Required response:

- Do not connect load.
- Adjust output to target voltage.
- Re-measure under light load.

Evidence:

- Multimeter photo or recorded voltage table.

### Case P2: LiPo Low Voltage

Risk:

- LiPo cell damage, voltage sag, unreliable electronics.

Detection:

- 3S LiPo alarm.
- STM32 ADC voltage monitor after implemented.

Required response:

- Warning threshold: reduce or stop test.
- Stop threshold: disable motor output.

Evidence:

- ADC raw value, converted pack voltage, threshold used.

### Case P3: Fuse Trip

Risk:

- Short circuit, wiring fault, stall current, wrong fuse.

Detection:

- Robot loses switched battery power.
- Fuse continuity check fails.

Required response:

- Disconnect battery.
- Inspect wiring before replacing fuse.

Evidence:

- Fault log and physical inspection note.

## 5. Motor Driver Safety Cases

### Case M1: Both Direction PWM Inputs Active

Risk:

- Undefined driver behavior, heating, shoot-through-like stress depending on
  module design.

Detection:

- Firmware output audit.
- Logic analyzer or oscilloscope during validation.

Required response:

- Set PWM to zero.
- Keep motor output disarmed.

Rule:

```text
Set inactive PWM channel to zero before applying the active channel.
```

### Case M2: Track Jam or Stall

Risk:

- High motor current, driver heat, fuse trip, battery sag.

Detection:

- Motor command present but encoder count does not change.
- Current measurement if available.
- Voltage sag or heat.

Required response:

- Stop motor output.
- Require operator inspection.

### Case M3: Driver Enable Unsafe During Reset

Risk:

- Motor may move while firmware is not ready.

Detection:

- Bench boot test with motor power disconnected.

Required response:

- Add external pull-down or revise wiring.
- Do not connect motor power until safe reset behavior is confirmed.

## 6. Communication Safety Cases

### Case C1: UART Command Timeout

Detection:

- `last_command_age_ms >= timeout_ms`.

Required response:

- PWM and stored command zero.
- Enter `DISARMED` immediately.
- Do not automatically restore the stored pre-timeout command.
- Resume only after an accepted `ARM` followed by a valid `CMD`.
- Current telemetry shows `DISARMED` and zero command values; an explicit
  timeout reason is pending P-04.

ADR-015 supersedes the earlier timeout-stop/armed-idle candidate. P-03A/P-03B
source/static/full-build now passes the pre-RX timeout stop/zero/`DISARMED`
response and starts a fresh default 300 ms first-CMD window on `ARM`. Target
runtime evidence remains open.
P-03 does not implement sequence monotonicity, session freshness, RX queue
purging, or cryptographic anti-replay. It proves CMD-only rejection while
`DISARMED`, not rejection of a queued or replayed `ARM` + `CMD` pair.

### Case C2: CAN Heartbeat Timeout

Detection:

- No `HEARTBEAT` frame within configured window.

Required response:

- Safe stop.
- Report `FAULT_HEARTBEAT_TIMEOUT`.

### Case C3: Invalid Command Frame

Detection:

- Missing required fields.
- Invalid DLC.
- Out-of-range values.

Required response:

- Reject frame.
- Do not update active command.
- Keep timeout logic active.

## 7. Sensor Safety Cases

### Case S1: Encoder Direction Mismatch

Detection:

- Forward command causes one side to count negative.

Required response:

- Do not enter closed-loop speed control.
- Fix sign in wiring or firmware mapping.

### Case S2: Encoder Stuck

Detection:

- Nonzero PWM command but no count change for a configured window.

Required response:

- During early open-loop tests: warn and stop test manually.
- During closed-loop operation: stop or limit motion.

### Case S3: IMU Missing

Detection:

- I2C read failure or no valid BNO08x report.

Required response:

- Do not use IMU-dependent mode.
- Encoder-only mode may continue if explicitly allowed.

## 8. Firmware Safety Cases

### Case F1: Control Loop Overrun

Detection:

- `loop_dt_us` exceeds maximum allowed period.

Required response:

- Record diagnostic counter.
- If repeated, enter fault or safe stop.

### Case F2: Watchdog Reset

Detection:

- Reset cause register or boot counter.

Required response:

- Boot into disarmed state.
- Do not resume motion automatically.

### Case F3: Internal Assertion Failure

Detection:

- Firmware detects impossible state, invalid enum, or unsafe output request.

Required response:

- Force PWM zero.
- Keep motor output disarmed.
- Latch fault.

## 9. Operator Safety Cases

Operator rules:

- Keep the robot lifted for first motor tests.
- Use the lowest practical fuse during early tests.
- Keep a clear way to disconnect the battery.
- Do not charge LiPo unattended.
- Do not use damaged or swollen LiPo packs.
- Do not increase fuse rating to hide a mechanical or wiring problem.
- Do not connect STM32 pins to unknown encoder voltage without measurement.

## 10. Fault Telemetry

Minimum fields:

```text
safety_state
fault_code
last_fault_time_ms
command_age_ms
battery_mv
left_pwm
right_pwm
left_encoder_count
right_encoder_count
loop_dt_max_us
reset_cause
```

Fault logs should include:

- What command was active
- What state the robot was in
- What safety response was applied
- Whether physical power was removed

## 11. Validation Matrix

| Validation | Method | Pass condition |
| --- | --- | --- |
| Boot safe output | Power logic only, motor disconnected | PWM zero |
| Command timeout | Stop sending commands | Motor output/stored command zero, `DISARMED`, CMD-only rejected, accepted `ARM` then valid `CMD` required; transport anti-replay pending |
| E-stop | Send E-stop frame or command | Fault latched, output disabled |
| Low voltage simulated | Inject low ADC equivalent | Output disabled |
| Encoder sign | Lifted motor test | Forward command produces expected signs |
| CAN timeout | Stop heartbeat | Output disabled |
| Watchdog recovery | Force reset during safe test | Reboot remains disarmed |
| Fuse stage | Use low fuse first | Fuse choice documented |

## Final Decision

The fault model is part of the architecture, not an afterthought.

Every command path must share the same fail-safe behavior:

```text
invalid, detected-stale, missing, or unsafe input -> PWM zero and driver disabled
```

Final MVP command-source loss additionally requires stored-command zero and a
`DISARMED` transition. Motion needs an accepted `ARM` followed by a valid `CMD`.
The current P-03 implementation does not itself detect transport/session
freshness; anti-replay remains a separate pending control.

Recovery from latched safety faults requires explicit operator action.
