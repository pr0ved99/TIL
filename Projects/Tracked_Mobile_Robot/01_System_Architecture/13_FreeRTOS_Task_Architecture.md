# FreeRTOS Task Architecture

> Status: Superseded English draft. After the 2026-06-08 MDD10A decision, use
> `13_FreeRTOS_Task_Architecture_ko.md` as the canonical RTOS architecture
> contract. Do not use stale BTS7960 enable-pin references in this file for new
> firmware work.

## Purpose

This document defines the FreeRTOS task architecture for the tracked mobile
robot low-level controller.

FreeRTOS is a required learning and architecture goal, but it is not the first
bring-up step. The project first validates PWM, encoder, ADC, UART, and basic
motor safety using a HAL bare-metal firmware. After that baseline works, the
firmware is restructured into tasks.

This document answers:

- Which jobs become FreeRTOS tasks
- Which task owns motor output
- How commands move from communication code to motor control code
- How safety state gates every motor command
- How battery, IMU, telemetry, UART, and future CAN are separated
- What evidence proves that the RTOS architecture is working

## Architecture Decision

Use FreeRTOS after the HAL bare-metal drivetrain MVP is working.

The architecture will move from:

```text
single bare-metal loop
```

to:

```text
communication task
sensor/battery tasks
safety task
motor control task
telemetry task
```

Core decision:

```text
Only the motor control task writes PWM outputs.
Only the safety logic can allow or block motor output.
Communication tasks may request motion, but they do not directly drive motors.
```

## 1. FreeRTOS Terms Used in This Project

| Term | Project meaning |
| --- | --- |
| Task | A firmware job that runs independently, such as motor control or telemetry |
| Priority | Scheduler importance; higher-priority ready tasks run first |
| Period | How often a periodic task should run |
| Queue | Safe message passing between tasks |
| Mutex | Protection for shared resources, used sparingly |
| Semaphore | Event signal, often from ISR to task |
| ISR | Interrupt service routine; should be short and non-blocking |
| Tick | FreeRTOS scheduler time base |

The project should use these concepts only where they reduce real complexity.
The first RTOS version should stay simple and measurable.

## 2. Entry Criteria

FreeRTOS should not be introduced until the HAL bare-metal baseline satisfies
these conditions:

- One motor spins forward and reverse under STM32 control.
- Both left and right motor PWM outputs are validated at low duty.
- Encoder direction and count rate are confirmed.
- Battery voltage ADC path is at least defined and safe.
- UART or USB command input can request stop and low-speed motion.
- Command timeout can stop motor output.
- BTS7960 enable pins are controlled by STM32.
- Boot behavior leaves motor outputs disabled.

Reason:

FreeRTOS should restructure a known-working firmware. It should not hide basic
electrical, pin, timer, or driver problems.

## 3. Task Overview

Initial task architecture:

```text
                 UART / future CAN RX
                         |
                         v
                    comm_task
                         |
                         v
                    command_queue
                         |
                         v
                 motor_control_task
                         |
                         v
                PWM + BTS7960 enable

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
The motor control task computes desired output.
The safety state decides whether output is allowed.
```

## 4. Task List

| Task | Initial period | Priority | Responsibility |
| --- | --- | --- | --- |
| `motor_control_task` | 100 Hz | High | Read latest command/state, estimate speed, update PWM |
| `safety_task` | 50-100 Hz | High | Fault checks, low-voltage stop, timeout stop, enable gating |
| `comm_task` | Event-driven or 100 Hz | Medium | UART receive, command parsing, later CAN receive |
| `battery_task` | 10 Hz | Medium | ADC sampling, voltage filtering, low-voltage input to safety |
| `imu_task` | 50-100 Hz | Medium | BNO08x sampling, yaw/attitude update |
| `telemetry_task` | 10 Hz | Low | Publish state, fault, voltage, speed, command status |
| `diagnostic_task` | 1-2 Hz | Low | Optional debug counters and health summary |

The first RTOS implementation may omit `imu_task` and `diagnostic_task` until
the drivetrain is stable.

## 5. Priority Model

Recommended priority order:

```text
highest  safety_task
         motor_control_task
         comm_task
         battery_task / imu_task
         telemetry_task
lowest   diagnostic_task
```

Rationale:

- Safety must be able to stop motor output independently.
- Motor control must run with stable timing.
- Communication must not block motor control.
- Telemetry is useful but not safety-critical.
- Diagnostics should never disturb control timing.

Important:

If `safety_task` and `motor_control_task` share the same high priority, their
periods and blocking behavior must be carefully controlled.

## 6. Timing Model

Initial timing targets:

| Loop | Target | Notes |
| --- | --- | --- |
| Motor control | 10 ms / 100 Hz | Enough for initial low-speed drivetrain control |
| Safety check | 10-20 ms / 50-100 Hz | Fast enough for timeout and voltage decisions |
| Command timeout | 300 ms initial | Matches UART interface contract |
| Battery sampling | 100 ms / 10 Hz | Voltage changes slowly compared to PWM |
| IMU sampling | 10-20 ms / 50-100 Hz | Useful for yaw-rate and odometry experiments |
| Telemetry | 100 ms / 10 Hz | Human-readable and serial-friendly |

Implementation rule:

- Periodic tasks should use `vTaskDelayUntil()`.
- Long `HAL_Delay()` calls should not be used inside tasks.
- A task should not busy-wait for a peripheral.
- Blocking waits must have timeouts.

## 7. Data Ownership

Each data item should have one writer.

| Data | Writer | Readers |
| --- | --- | --- |
| Latest valid motion command | `comm_task` via queue | `motor_control_task`, `safety_task` |
| Motor PWM duty request | `motor_control_task` | PWM update code |
| Actual PWM hardware registers | `motor_control_task` only | debug read only |
| Encoder counts | timer hardware / encoder read function | `motor_control_task`, telemetry |
| Estimated wheel speed | `motor_control_task` | telemetry, odometry later |
| Battery voltage | `battery_task` | `safety_task`, telemetry |
| IMU yaw/attitude | `imu_task` | odometry later, telemetry |
| Safety state | `safety_task` | `motor_control_task`, telemetry |
| Fault code | `safety_task` | telemetry, communication response |

Rule:

```text
Do not allow multiple tasks to write the same control variable.
```

## 8. Message and Queue Model

Initial queues:

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

Minimal safety state:

```c
typedef enum {
    SAFETY_BOOT = 0,
    SAFETY_DISARMED,
    SAFETY_ARMED,
    SAFETY_TIMEOUT,
    SAFETY_LOW_VOLTAGE,
    SAFETY_FAULT
} safety_state_t;
```

Rules:

- Command queues should keep only the latest command if old commands become
  stale.
- If the queue is full, old motion commands should not block safety behavior.
- Telemetry loss must not affect motor control.
- Fault events should be retained long enough to be reported.

## 9. Safety Gate

Every motor output update must pass through safety gating.

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
    +-- unsafe -> PWM = 0, driver enable = disabled
    |
    +-- safe   -> apply limited PWM command
```

Safety conditions that block output:

- Boot not complete
- Disarmed state
- Command timeout
- Low-voltage stop
- Emergency stop request
- Encoder or motor fault if configured
- Firmware internal fault

Rule:

```text
Safety gating is not optional and cannot be bypassed by UART, CAN, ESP32, or ROS2.
```

## 10. ISR Rules

Interrupt service routines must stay short.

Allowed ISR behavior:

- Capture a timestamp
- Read or clear a hardware flag
- Push a small event to a queue from ISR
- Give a semaphore from ISR
- Increment a simple counter if needed

Avoid in ISR:

- Text parsing
- `printf`
- Long I2C transactions
- Blocking HAL calls
- Direct complex motor control logic
- Heap allocation

Preferred pattern:

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

`comm_task` owns command parsing.

Initial responsibilities:

- Receive UART bytes or lines.
- Parse newline-terminated ASCII command frames.
- Validate required fields.
- Clamp obviously invalid values before queueing.
- Update last command receive time.
- Send valid command requests to `command_queue`.
- Ignore unknown message types safely.

Deferred responsibilities:

- CAN receive handling
- Binary packet parsing
- CRC validation
- ROS2 bridge integration

Important rule:

```text
comm_task never writes PWM or driver enable pins directly.
```

## 12. Motor Control Task

`motor_control_task` owns deterministic drivetrain output.

Responsibilities:

- Run at a fixed period.
- Read the latest command request.
- Read encoder counters.
- Estimate left/right wheel speed.
- Apply ramp limits.
- Apply initial open-loop or closed-loop control.
- Convert motion request to left/right motor command.
- Apply safety gate result.
- Update BTS7960 PWM and enable outputs.

Initial control mode:

- Start with low-duty open-loop output.
- Add speed estimation after encoder validation.
- Add P or PID speed control only after encoder readings are stable.

Rule:

```text
The motor loop must not wait for communication, telemetry, or IMU reads.
```

## 13. Safety Task

`safety_task` owns safety state updates.

Responsibilities:

- Check command timeout.
- Check battery voltage state.
- Check disarm/arm state.
- Check startup delay.
- Check emergency stop request.
- Check firmware fault flags.
- Publish safety state and fault code.

Safety output:

- `SAFETY_ARMED` allows limited motor output.
- Any unsafe state forces PWM zero and driver disable through the motor-control
  output path.

Important:

The exact state machine is defined in
`16_Control_Loop_and_State_Machine.md`. This document only defines the RTOS task
ownership.

## 14. Battery Task

`battery_task` owns battery ADC sampling and filtering.

Responsibilities:

- Trigger or read ADC value.
- Convert ADC count to pack voltage.
- Apply simple filtering.
- Compare voltage with warning and stop thresholds.
- Provide battery state to `safety_task`.
- Provide voltage telemetry.

Rules:

- ADC conversion must not block motor control.
- Low-voltage decisions should be debounced or filtered enough to avoid false
  stops from one noisy sample.
- The LiPo alarm remains independent of firmware.

## 15. IMU Task

`imu_task` is introduced after basic motor control and UART telemetry are stable.

Responsibilities:

- Read BNO08x data.
- Track IMU health.
- Provide yaw/attitude or yaw-rate data.
- Publish reduced telemetry.
- Later support odometry fusion experiments.

Rules:

- I2C reads must not block the motor-control loop.
- IMU failure must not directly cause uncontrolled motor output.
- If IMU data is required for a mode, safety or mode logic must handle missing
  IMU data explicitly.

## 16. Telemetry Task

`telemetry_task` owns status output.

Initial telemetry fields:

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

Rule:

```text
Telemetry is allowed to drop data.
Motor control is not allowed to wait for telemetry.
```

## 17. Future CAN Extension

CAN should reuse the same task architecture.

Future options:

| Option | Description |
| --- | --- |
| Extend `comm_task` | UART and CAN both produce motion commands into the same queue |
| Add `can_task` | CAN RX/TX separated from UART parsing |

Initial recommendation:

- Start with UART in `comm_task`.
- Validate CAN standalone later.
- When integrating CAN, either extend `comm_task` or add `can_task`, but keep
  the same `command_queue` and safety gate.

Rule:

```text
CAN changes the transport, not the motor safety owner.
```

## 18. Debug and Measurement Plan

FreeRTOS evidence targets:

| Evidence | Purpose |
| --- | --- |
| Task table | Shows ownership and timing design |
| Runtime counters | Confirms tasks are alive |
| Loop period log | Confirms motor loop timing |
| Command timeout test | Confirms communication does not own safety |
| Low-voltage simulated test | Confirms safety can stop motor output |
| Queue overflow test | Confirms stale commands do not block safety |
| Telemetry under motor load | Confirms logging does not break control |

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

Before enabling FreeRTOS, preserve the HAL bare-metal version as a known-good
baseline.

### Step 2: Move Command Parsing

Move UART parsing into `comm_task`, but keep motor output logic simple.

### Step 3: Move Motor Loop

Move periodic motor update into `motor_control_task` using `vTaskDelayUntil()`.

### Step 4: Add Safety Task

Move timeout, disarm, and low-voltage decisions into `safety_task`.

### Step 5: Add Battery and Telemetry Tasks

Separate slow monitoring and logging from motor control.

### Step 6: Add IMU Task

Add IMU only after motor and telemetry timing are stable.

### Step 7: Prepare CAN Integration

Keep the command queue and safety gate transport-independent so CAN can be
added without rewriting the drivetrain logic.

## 20. Exit Criteria

The FreeRTOS architecture is accepted when:

- `motor_control_task` runs at a stable enough period for low-speed control.
- `comm_task` cannot directly write PWM outputs.
- Command parsing does not block motor output updates.
- Command timeout stops the motors.
- `safety_task` can stop motor output independently.
- `telemetry_task` can be slowed or disabled without breaking motor control.
- Battery voltage state reaches safety logic.
- Task responsibilities are documented.
- A timing or runtime log exists.

## Final Decision

FreeRTOS is introduced after the bare-metal drivetrain baseline works.

The RTOS architecture is built around one principle: communication, telemetry,
and sensor processing may provide data, but STM32 safety logic and the motor
control task remain the only path to motor output.
