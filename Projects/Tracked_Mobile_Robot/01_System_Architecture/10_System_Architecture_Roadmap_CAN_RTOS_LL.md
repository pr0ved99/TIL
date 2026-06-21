# System Architecture Roadmap: CAN, RTOS, and LL Driver

## Purpose

This document updates the project architecture roadmap based on three required
learning goals:

1. CAN communication experience
2. RTOS-based firmware architecture experience
3. HAL-to-LL Driver migration experience

These goals are not part of the first motor bring-up MVP, but they are required
project outcomes. The architecture must therefore leave clear expansion points
for FreeRTOS, CAN, and LL Driver migration from the beginning.

## Architecture Decision

The project will not start with CAN, RTOS, or LL Driver.

The project will start with a simple HAL-based bare-metal bring-up, then
progressively add:

```text
HAL bare-metal drivetrain
-> FreeRTOS task architecture
-> CAN standalone validation
-> CAN command/telemetry integration
-> LL Driver migration for timing-critical paths
```

Reason:

- Motor and encoder behavior must be verified before adding scheduling and bus
  communication complexity.
- FreeRTOS is valuable after the firmware has multiple periodic jobs.
- CAN is valuable after the command and telemetry model is clear.
- LL Driver migration is meaningful only after there is a working HAL baseline
  to compare against.

## 1. Required Learning Goals

### Goal 1: CAN Communication

CAN must be handled as a real project phase, not a vague future option.

Expected experience:

- CAN frame structure
- CAN ID design
- CAN transceiver wiring
- Bus termination
- STM32 bxCAN configuration
- USB-CAN adapter debugging
- Command and telemetry message mapping
- Fault behavior when CAN messages stop arriving

Initial scope:

- Validate CAN in isolation before using it to command motors.
- Keep UART as the first control interface.
- Move command/telemetry concepts from UART to CAN after UART is proven.

### Goal 2: RTOS Experience

FreeRTOS should be introduced after bare-metal motor and encoder validation.

Expected experience:

- Task creation
- Periodic task timing
- Priority assignment
- Queue or stream-buffer communication
- Shared state ownership
- Command timeout handling
- Safety task separation

Initial task candidates:

| Task | Period | Priority | Responsibility |
| --- | --- | --- | --- |
| `motor_control_task` | 100 Hz | High | Speed control, PWM update, ramp limiting |
| `safety_task` | 50-100 Hz | High | Fault checks, low-voltage stop, output gating |
| `comm_task` | Event-driven or 100 Hz | Medium | UART/CAN receive and command parsing |
| `telemetry_task` | 10 Hz | Low | Status publishing |
| `battery_task` | 10 Hz | Medium | ADC sampling and voltage filtering |
| `imu_task` | 50-100 Hz | Medium | BNO08x sampling and yaw-rate handling |

Rule:

- The motor control loop must remain deterministic.
- Communication tasks must not directly write PWM outputs.
- Safety state must gate every motor command.

### Goal 3: LL Driver Migration

LL Driver migration is a later engineering-depth goal.

The first firmware should use HAL and CubeMX to reduce bring-up risk. After the
system works, timing-critical paths can be migrated to LL.

Recommended migration targets:

| Target | Reason |
| --- | --- |
| Timer PWM compare update | High-frequency duty update path |
| Encoder counter read/reset | Frequent control-loop read path |
| MDD10A DIR GPIO | Direction output path; migrate after HAL baseline |
| Control-loop timer interrupt | Timing determinism and jitter inspection |
| CAN RX/TX handling | Optional later optimization |
| ADC sampling trigger/read | Optional after voltage monitoring is stable |

Not recommended for first LL migration:

- I2C IMU bring-up
- USB/printf debug
- ESP32-side Wi-Fi features
- Early text protocol parsing

## 2. Phase Plan

### Phase 0: Architecture and Bench Preparation

Output:

- Project charter
- Component inventory
- Power safety plan
- MCU datasheet reading notes
- Motor driver decision
- UART interface contract
- This roadmap

Exit criteria:

- First wiring plan exists.
- Power safety rules exist.
- MDD10A PWM/DIR control model is documented.
- CAN/RTOS/LL are recorded as required later outcomes.

### Phase 1: HAL Bare-Metal Drivetrain MVP

Purpose:

Validate the physical drivetrain and basic MCU peripheral use without RTOS or
CAN complexity.

Scope:

- PWM/DIR output to MDD10A
- Encoder A/B input counting
- Battery voltage ADC through resistor divider
- Basic UART/USB command
- Low-speed motor test
- Emergency stop and timeout stop

Exit criteria:

- One motor spins forward and reverse under STM32 control.
- Encoder direction and count rate are confirmed.
- Left/right motors can be driven at low duty.
- Motor output stops on command timeout.
- Low-voltage threshold behavior is defined.

### Phase 2: FreeRTOS Firmware Restructure

Purpose:

Turn a working bare-metal firmware into a task-based firmware architecture.

Scope:

- Motor control task
- Safety task
- Communication task
- Telemetry task
- Battery task
- Optional IMU task

Exit criteria:

- Control loop period is stable enough for low-speed motor control.
- Command parsing no longer blocks the motor loop.
- Safety task can stop the motors independently of command source.
- Task responsibilities are documented.

### Phase 3: CAN Standalone Validation

Purpose:

Learn CAN without risking drivetrain safety.

Scope:

- STM32 bxCAN loopback mode
- STM32 + CAN transceiver
- USB-CAN adapter receive/transmit test
- 120 ohm termination check
- CAN ID and frame design draft

Exit criteria:

- STM32 can transmit and receive CAN frames.
- USB-CAN adapter can observe the bus.
- Termination and wiring rules are documented.
- CAN message IDs are defined for command and telemetry.

### Phase 4: CAN Robot Integration

Purpose:

Move command and telemetry concepts from UART into CAN messages.

Scope:

- CAN command frame
- CAN telemetry frame
- CAN heartbeat
- CAN timeout stop
- Fault report frame

Exit criteria:

- STM32 accepts a low-speed command over CAN.
- STM32 publishes telemetry over CAN.
- Missing CAN heartbeat causes motor stop.
- UART remains available as debug or fallback path.

### Phase 5: HAL-to-LL Migration

Purpose:

Improve engineering depth and understand STM32 peripherals closer to register
level.

Scope:

- Convert PWM duty update path to LL.
- Convert encoder read/reset path to LL if useful.
- Convert MDD10A DIR GPIO path to LL if useful.
- Measure or reason about latency and jitter before and after migration.

Exit criteria:

- HAL baseline and LL version both work.
- The reason for each LL migration is documented.
- No safety behavior regresses after migration.

### Phase 6: Higher-Level Expansion

Purpose:

Use the validated low-level platform as a base for autonomy.

Scope:

- ESP32 dashboard
- ROS2 bridge
- LiDAR
- SLAM/Nav2
- More complete odometry evaluation

Exit criteria:

- Low-level firmware remains stable while higher-level features are added.

## 3. Interface Evolution

The project should evolve the command path in this order:

```text
PC USB/UART command
-> ESP32 UART bridge command
-> CAN command
-> ROS2 bridge command
```

The motor-control safety rules must remain on STM32 through every stage.

## 4. Documentation Impact

The system architecture section should now include these remaining documents:

| Document | Purpose |
| --- | --- |
| `11_System_Block_Diagram_and_Interface_Map.md` | Full hardware/software interface map |
| `12_Power_Distribution_and_Safety_Architecture.md` | Power path, fuse, switch, buck converter, GND, low-voltage safety |
| `13_FreeRTOS_Task_Architecture.md` | Task model, priority, timing, shared state |
| `14_CAN_Bus_Integration_Plan.md` | CAN hardware, IDs, frames, validation |
| `15_HAL_to_LL_Driver_Migration_Strategy.md` | Migration target and validation rules |
| `16_Control_Loop_and_State_Machine.md` | Boot, disarmed, armed, fault, timeout stop |
| `17_Drivetrain_Kinematics_and_Odometry_Plan.md` | Tracked drivetrain equations and encoder/IMU odometry plan |
| `18_Fault_Model_and_Safety_Cases.md` | Fault scenarios and responses |
| `19_Architecture_Decision_Record.md` | Final design decisions and rejected alternatives |

## 5. Portfolio Evidence Targets

The project should produce evidence for each learning goal.

| Goal | Evidence |
| --- | --- |
| Motor control | PWM screenshots, motor test logs, encoder plots |
| Power safety | fuse plan, voltage measurements, shutdown behavior |
| FreeRTOS | task diagram, priority table, timing measurements |
| CAN | CAN frame table, USB-CAN logs, bus wiring photos |
| LL Driver | before/after code, timing comparison, regression checklist |
| Odometry | straight-line and turn test records |
| Architecture | block diagrams, interface contracts, decision records |

## 6. Current Position

Current state:

- Project charter exists.
- STM32 MCU feature analysis exists.
- Timer, communication, and pin allocation notes exist.
- ESP32-S3 role decision exists.
- MDD10A motor-driver decision exists.
- STM32-ESP32 UART contract exists.

Immediate next action:

1. Verify the STM32 pin allocation for MDD10A PWM/DIR output.
2. Create the system block diagram and interface map.
3. Create the power distribution and safety architecture.
4. Then prepare the HAL bare-metal firmware bring-up plan.

## Final Roadmap Decision

CAN, FreeRTOS, and LL Driver migration are required project learning outcomes.

They are deferred only from the first motor bring-up, not from the project.
