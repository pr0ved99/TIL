# Tracked Mobile Robot Codex Instructions

Use this file as project-specific working context for `Projects/Tracked_Mobile_Robot`.

## Read First

Before asking the user for project facts, read:

1. `PROJECT_MEMORY.md`
2. `docs/progress/README.md`
3. The latest dated file under `docs/progress/`
4. `docs/handoff/README.md`
5. The current continuation source identified by `docs/handoff/README.md`
6. `README.md`
7. `01_System_Architecture/20_Motor_Driver_Selection_Comparison_ko.md`
8. Korean canonical architecture docs under `01_System_Architecture/*_ko.md`
9. For learning-oriented work, `07_Embedded_Learning_Notes/README.md`

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

## Firmware Learning Workflow

Firmware learning work normally follows this loop:

```text
requirement and safety condition
-> one small code block with an exact insertion location
-> user types and saves it
-> Codex rereads the real file
-> design and structure explanation
-> tests/build
-> board measurement or log evidence
```

Apply these rules:

- The default for learning-target STM32 and ESP32 firmware is that the user types each small block. Do not replace this with a large paste-ready module.
- If the user explicitly says `너가 추가해`, `너가 수정해`, `직접 진행해`, or otherwise clearly delegates the edit, Codex may edit the stated scope directly. Documentation, tests, and repetitive mechanical edits may also be performed directly when they are inside the requested scope.
- When the user says `확인해봐`, reread the actual saved file before judging it. Check the exact text, placement, typos, control flow, compile impact, and relevant safety invariant; do not rely only on the previous chat message.
- After presenting or editing code, explain it in enough detail for the user to reconstruct the reasoning. Cover the problem being solved, why the design was chosen, module/state/data responsibilities, control and data flow, normal path, timeout/error/failure path, safety invariants, alternatives and tradeoffs, and the verification method with explicit PASS criteria.
- When the user is typing, present the code and exact location first, then give the detailed explanation. Keep each typing step independently reviewable.
- A successful static test or build is not board-runtime or electrical evidence. State the evidence boundary explicitly before moving to flash, power, or hardware work.
- Hardware power, rewiring, flashing, and physical measurements are performed by the user. Give the exact preconditions, expected observation, stop conditions, and PASS criteria before asking the user to act.

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
