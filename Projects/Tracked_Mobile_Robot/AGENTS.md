# Tracked Mobile Robot Codex Instructions

Use this file as project-specific working context for `Projects/Tracked_Mobile_Robot`.

## Read First

Before asking the user for project facts, read:

1. `PROJECT_MEMORY.md`
2. `docs/progress/README.md`
3. The latest dated file under `docs/progress/`
4. The latest dated file under `docs/handoff/`
5. `README.md`
6. `01_System_Architecture/20_Motor_Driver_Selection_Comparison_ko.md`
7. Korean canonical architecture docs under `01_System_Architecture/*_ko.md`
8. For learning-oriented work, `07_Embedded_Learning_Notes/README.md`

The Korean `_ko.md` architecture files are the current canonical project contract. English mirror files may be older and should not override the Korean files unless they are intentionally updated.

`07_Embedded_Learning_Notes` is for concept notes and practice logs. Do not treat those notes as canonical architecture decisions until the decision is reflected in `01_System_Architecture`, `PROJECT_MEMORY.md`, or a progress log.

## Do Not Ask Again

Do not ask again for facts already recorded in `PROJECT_MEMORY.md` unless the user says hardware, architecture, or project direction changed.

Current fixed project decisions:

- Main low-level controller: NUCLEO-F446RE.
- Support controller: ESP32-S3 DevKitC.
- First motor driver path: MDD10A dual-channel PWM+DIR driver.
- BTS7960 is superseded for the first drivetrain path and remains only as design-history/comparison context.
- STM32 owns motor output, command timeout, battery safety, encoder reading, and final safety gate.
- UART/USB serial is the first command and telemetry path.
- CAN is a required later phase, not the first bring-up path.
- FreeRTOS is introduced after HAL bare-metal drivetrain validation.
- HAL starts the project; selected LL migration happens later.
- ROS 2 is an upper-layer learning and integration path after low-level safety is validated.

## Progress Logging

For meaningful project work, update `docs/progress/YYYY-MM-DD_progress.md` or create a new dated progress file.

Record:

- What changed
- Why it changed
- Evidence or validation
- Current blockers
- Next concrete actions

Keep progress notes factual and short enough to scan.

## Asking Rule

Ask only when the answer materially changes hardware purchase, wiring, firmware architecture, or safety behavior and the answer is not already in `PROJECT_MEMORY.md` or progress logs.
