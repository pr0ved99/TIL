# Architecture Decision Record

## Purpose

This document summarizes the major architecture decisions made for the tracked
mobile robot project.

The goal is not only to record what was selected, but also to record why it was
selected and what was intentionally deferred. This is important for portfolio
quality because embedded robotics projects are judged by design reasoning, not
only by whether a motor spins.

## Project Direction

Build a tracked mobile robot low-level platform that can later expand toward
ROS2, LiDAR, SLAM, CAN, FreeRTOS, and LL Driver work.

Initial focus:

```text
power safety
-> STM32 motor control
-> encoder validation
-> UART command and telemetry
-> low-speed tracked chassis motion
```

Deferred but required learning goals:

```text
FreeRTOS
CAN
HAL-to-LL migration
odometry
ROS2 integration
```

## Decision Status Terms

| Status | Meaning |
| --- | --- |
| Accepted | Current project decision |
| Deferred | Not in first MVP, but kept as later scope |
| Rejected | Not used for this project phase |
| Open | Requires measurement, purchase, or firmware validation |

## ADR-001: Build Low-Level Platform Before Full Autonomy

Status: Accepted

Decision:

- First build a reliable STM32-based drivetrain platform.
- Do not start with full ROS2 autonomy.

Reason:

- Motor, encoder, power, and safety behavior must be trustworthy before higher
  autonomy is meaningful.
- A stable low-level base gives stronger engineering evidence.

Consequence:

- ROS2, LiDAR, SLAM, and Nav2 are later expansion phases.

## ADR-002: Use STM32 NUCLEO-F446RE as Low-Level Controller

Status: Accepted

Decision:

- STM32 owns motor PWM, encoder counting, battery voltage safety, and final
  motor output permission.

Reason:

- STM32F446RE has enough timers, UART, I2C, ADC, and bxCAN resources.
- Deterministic low-level control belongs on the MCU.

Consequence:

- ESP32, PC, CAN, and ROS2 are command or telemetry sources, not final safety
  authorities.

## ADR-003: Use ESP32-S3 as Support Controller, Not Motor Controller

Status: Accepted

Decision:

- ESP32-S3 handles support roles such as Wi-Fi dashboard, wireless forwarding,
  telemetry display, or future bridge experiments.
- ESP32 does not own motor PWM or final safety.

Reason:

- STM32 is better suited for deterministic low-level motor timing.
- Separating support logic from motor safety reduces risk.

Consequence:

- STM32-ESP32 communication starts through UART.

## ADR-004: Use UART First

Status: Accepted

Decision:

- Use 3.3 V UART as the first STM32-ESP32 or PC command interface.

Reason:

- UART is simple, observable, and easy to debug.
- ASCII frames are appropriate for first bring-up.

Consequence:

- CAN is deferred from initial bring-up but remains a required phase.

## ADR-005: CAN Is Required Later

Status: Accepted

Decision:

- CAN will be added after UART command and telemetry are proven.

Reason:

- CAN provides robust multi-node communication experience.
- It is relevant to vehicles, robots, and embedded control systems.
- CAN should not block first motor bring-up.

Consequence:

- PA11/PA12 are reserved for CAN1.
- CAN transceiver and USB-CAN adapter are required later.
- CAN command frames must reuse the same safety gate as UART.

## ADR-006: Use FreeRTOS After Bare-Metal Baseline

Status: Accepted

Decision:

- Do not start with FreeRTOS.
- Introduce FreeRTOS after PWM, encoder, ADC, UART, timeout, and safety basics
  are working.

Reason:

- RTOS should structure working behavior, not hide bring-up problems.
- Task ownership becomes meaningful when there are multiple periodic jobs.

Consequence:

- First firmware can be HAL bare-metal.
- Later firmware separates motor, safety, communication, battery, IMU, and
  telemetry tasks.

## ADR-007: Start With HAL, Migrate Selected Paths to LL Later

Status: Accepted

Decision:

- Use CubeMX/HAL for initial peripheral bring-up.
- Migrate selected timing-critical paths to LL after baseline validation.

Reason:

- HAL lowers initial risk.
- LL provides engineering depth after the system works.

Consequence:

- LL migration targets are MDD10A DIR GPIO, PWM compare update, encoder read,
  control-loop timer, and optional ADC/CAN.

## ADR-008: Use MDD10A Dual-Channel Motor Driver First

Status: Accepted

Decision:

- Use one MDD10A board to drive the left and right brushed DC motors.
- Control each motor using sign-magnitude `PWM + DIR`.

Reason:

- Better current margin than small TB6612FNG-class modules.
- One board handles both drivetrain motors, reducing wiring and bench setup.
- The interface matches the current STM32 pin candidate: two PWM outputs and
  two DIR GPIO outputs.
- MDD10A supports 3.3 V logic input, so it fits NUCLEO-F446RE GPIO better for
  first bring-up.
- Compared with a two-module BTS7960 path, it reduces PWM-channel pressure and
  removes the need for BTS7960-style `RPWM`/`LPWM` mutual exclusion.

Consequence:

- The pin allocation must support two PWM outputs and two DIR GPIO outputs.
- Firmware must ramp PWM to zero before changing `DIR`.
- BTS7960 remains documented as a superseded alternative and design-history
  comparison, not as the active wiring or firmware contract.

## ADR-009: Use Fuse, Main Switch, and LiPo Alarm

Status: Accepted

Decision:

- Use a blade fuse holder near the battery positive side.
- Use a DC-rated main switch after the fuse.
- Use a 3S LiPo low-voltage alarm during tests.

Reason:

- Firmware cannot be the only safety layer.
- LiPo and motor current faults need physical protection and operator warning.

Consequence:

- Power validation is required before MCU connection.
- Fuse rating starts low and increases only after current behavior is known.

## ADR-010: Do Not Use a BMS for Finished RC LiPo Pack in This Phase

Status: Accepted

Decision:

- Do not insert a generic BMS board into the finished RC LiPo pack path for the
  current project phase.

Reason:

- RC LiPo packs are charged with balance chargers.
- Discharge-side protection is handled through fuse, switch, LiPo alarm,
  firmware voltage monitoring, and operator procedure.
- A mismatched BMS can add wiring and failure risk.

Consequence:

- Low-voltage handling must be documented and tested.

## ADR-011: Use Differential-Drive Approximation for Tracked Kinematics

Status: Accepted

Decision:

- Model the tracked drivetrain as a differential-drive robot for first control
  and odometry.

Reason:

- Left/right track speed controls forward motion and yaw.
- The model is simple enough for first encoder odometry.

Consequence:

- Slip and track deformation must be treated as known limitations.
- IMU correction is added only after encoder scale and signs are validated.

## ADR-012: Keep Motor Safety on STM32 Through Every Expansion

Status: Accepted

Decision:

- STM32 remains final safety authority even after ESP32, CAN, or ROS2
  integration.

Reason:

- Communication links can freeze, delay, disconnect, or send invalid commands.
- Motor output safety must be local and deterministic.

Consequence:

- Every command path goes through command validation, timeout, state machine,
  and safety gate.

## Rejected or Deferred Alternatives

| Alternative | Status | Reason |
| --- | --- | --- |
| Direct motor drive from MCU GPIO | Rejected | MCU cannot supply motor current |
| TB6612FNG as main drivetrain driver | Rejected for main drivetrain | Too small for tracked platform current risk |
| BTS7960 as first drivetrain driver | Superseded | Reasonable early dual-PWM candidate, but MDD10A reduces board count, PWM-channel demand, and validation complexity |
| ESP32 as primary motor controller | Rejected | STM32 is better for deterministic low-level control |
| CAN in first bring-up | Deferred | Adds wiring and debug complexity too early |
| FreeRTOS from day one | Deferred | Can hide peripheral bring-up problems |
| LL Driver from day one | Deferred | HAL baseline is needed for comparison |
| Full ROS2 autonomy first | Deferred | Low-level drivetrain and safety must be validated first |
| Generic LiPo BMS board | Rejected for this phase | Balance charger, fuse, alarm, firmware monitor, and procedure are preferred |

## Open Decisions

| Topic | Open question |
| --- | --- |
| Final PWM/DIR pins | Do PB6/PB7 PWM and PC8/PC9 DIR work without conflict after CubeMX validation? |
| Encoder source quality | Which motors have working encoders and correct counts per revolution? |
| CAN hardware | Which CAN transceiver and USB-CAN adapter will be purchased? |
| Battery voltage divider | Exact resistor values and ADC calibration |
| PWM frequency | Final MDD10A-safe and motor-friendly frequency |
| Motor current measurement | Whether a current sensor is added or current is measured externally |
| ROS2 bridge path | UART, CAN, ESP32, or PC bridge for future ROS2 commands |
| Odometry calibration | Effective track width and distance-per-count values |

## Evidence Roadmap

| Decision area | Evidence to collect |
| --- | --- |
| Power safety | Wiring photo, fuse rating, buck voltage measurements |
| Motor driver | PWM waveform, low-duty motor test, heat observation |
| Encoder | Direction test, count-rate log, speed plot |
| UART | Command/telemetry logs, timeout test |
| FreeRTOS | Task table, timing counters, queue behavior |
| CAN | Loopback log, `candump`, heartbeat timeout |
| LL migration | Before/after timing and regression checklist |
| Odometry | Straight and rotation test plots |

## Final Architecture Summary

Current architecture direction:

```text
3S LiPo + fuse + switch
        |
        +-- MDD10A motor power
        |
        +-- buck converters
                |
                +-- STM32 low-level controller
                +-- ESP32 support controller
                +-- sensors

STM32
    +-- PWM/DIR -> MDD10A
    +-- timer encoder mode -> motor encoders
    +-- ADC -> battery monitor
    +-- UART -> PC/ESP32 first command path
    +-- bxCAN -> future CAN command path
    +-- FreeRTOS -> later task structure
    +-- LL Driver -> later timing-critical migration
```

Final rule:

```text
The robot may receive commands from many places, but motor permission belongs to STM32.
```
