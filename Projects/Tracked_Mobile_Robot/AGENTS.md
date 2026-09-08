# Tracked Mobile Robot Codex Instructions

Use this file as project-specific working context for `Projects/Tracked_Mobile_Robot`.

## Read First

Use the smallest current context that can answer the task:

1. `docs/handoff/CURRENT_SESSION_CONTEXT.md`
2. `docs/progress/README.md` and only the latest dated progress file
3. The one plan, verification report, design file, or firmware source directly needed for the task

Read `PROJECT_MEMORY.md`, `docs/handoff/README.md`, the main `README.md`, older progress/handoff files,
or the architecture tree only when the small current context does not settle a fact or a conflict must be
audited. Do not load the entire project history at the start of every conversation.

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

## Bench Workflow

- At the start of a bench gate, state the final purpose, the current Test ID/gate, and why the next action is needed.
- Give one physical action or one logically inseparable measurement group at a time. Wait for the user's result before advancing.
- Treat `통과 다음`, `전부 통과 다음`, and equivalent wording as an instruction to record that bounded result and move on. Do not repeat a completed test unless wiring/code changed, a result failed, or the user asks to repeat it.
- Before naming probe points, verify that both endpoints exist in the current physical topology. Do not ask for continuity to an unconnected module.
- Keep observed values, units, meter mode, probe endpoints, and the interpretation separate. Never assign a value to an unreported endpoint.
- Do not expand one reported PASS into a larger gate, safety rating, or evidence claim.

## Progress Logging

For meaningful project work, update `docs/progress/YYYY-MM-DD_progress.md` or create a new dated progress file.

Record:

- What changed
- Why it changed
- Evidence or validation
- Current blockers
- Next concrete actions

Keep progress notes factual and short enough to scan.

During an active bench sequence, collect results in the conversation and update progress documents once when
the user ends the work block or explicitly requests documentation. Update immediately only when a wrong live
instruction or safety-critical project fact must be corrected before continuing.

## Context And Resource Discipline

- Use one conversation for one gate or one tightly connected milestone. After a major milestone, update
  `CURRENT_SESSION_CONTEXT.md` and start the next milestone in a new conversation.
- Do not use subagents unless the user explicitly requests them. Past subagent/session snapshots consumed most
  of the local conversation storage.
- Save useful logs, captures, and drawings as repository artifacts and refer to their paths. Do not paste or
  reattach the same large output repeatedly.
- Inspect long logs with targeted searches and bounded excerpts. Do not load full logs or all historical
  conversations when the current documents already preserve the decision.
- Follow `docs/handoff/CODEX_CONTEXT_WORKFLOW.md` for session closeout, archive lookup, and new-thread startup.

## Asking Rule

Ask only when the answer materially changes hardware purchase, wiring, firmware architecture, or safety behavior and the answer is not already in `PROJECT_MEMORY.md` or progress logs.
