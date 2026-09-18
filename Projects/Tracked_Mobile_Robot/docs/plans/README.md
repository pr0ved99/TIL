# Execution Plans

This folder stores short-term execution plans for hardware sessions.

Use progress logs for what actually happened. Use this folder for the plan that should guide the next bench session.

Current bench record is the
[soldering checklist](2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md).
UART/CTRL/ENC/IMU wiring, instructed unpowered checks and final fit/workmanship passed by user report
through 9/19. Resume at **BUILD-01: user builds both firmwares with boards unpowered**.
See [9/19 progress](../progress/2026-09-19_progress.md) for the closeout and remaining boundaries.
The detailed runtime procedure remains the
[`2026-09-08 T-ESTOP-004 firmware/PWM integration runbook`](2026-09-08_T_ESTOP_004_Firmware_PWM_Integration_Runbook_ko.md).
It records each logical result while preserving the completed K2, wire-open, board-power and
conditioned-sense baseline. Connected firmware edits use a complete replacement range and reviewed block.
MDD10A B+ and both motors remain disconnected throughout T-ESTOP-004.

The scheduler correction and static-test update are complete: the all-hooks-0U baseline passed **30/30**
tests and seven in-memory regression mutations were caught. Current ESP source has only T004 enabled at
`1U`; build/flash/runtime results have not been reported. Do not repeat the completed scheduler replacement.
The user performs both STM32 and ESP32 builds and flashes. Latest matching PDF exports remain unconfirmed;
powered communication, IMU integration and T004 runtime are not established by the wiring checks.

## Index

| Date range | File | Scope |
| --- | --- | --- |
| 2026-09-16 plan / updated through 9/19 | [납땜 체크리스트](2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md) | 배선·무전원 검사·마감 완료; T004 사용자 빌드부터 재개 |
| 2026-09-11 plan / updated through 9/19 | [`2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md`](2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md) | UART·측정 헤더 도면 검토 및 제작 이력 |
| 2026-09-08 / current T-ESTOP-004 runtime procedure | [`2026-09-08_T_ESTOP_004_Firmware_PWM_Integration_Runbook_ko.md`](2026-09-08_T_ESTOP_004_Firmware_PWM_Integration_Runbook_ko.md) | Scheduler/static work complete; same-boot active/reset/post-reset capture, wire-open and all-hooks-0U safe restore remain; MDD10A B+/motors disconnected |
| 2026-09-05 / Gates 1~4 completed, historical predecessor | [`2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md`](2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md) | Corrected K2 mapping, S0-A/S0-B independence and conditioned PC7 baseline; Gate 5 moved to the 2026-09-08 runbook |
| 2026-09-03 / execution closed, historical | [`2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md`](2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md) | 2026-09-05에 실행 종료; rail/U1 subset과 후속 control-only results는 progress에 보존, K2 frozen coordinate table은 bottom-view 해석 오류로 비정본이며 남은 formal gates는 새 runbook으로 이관 |
| Project-wide / current | [`00_Project_Master_Plan_To_Final_MVP_ko.md`](00_Project_Master_Plan_To_Final_MVP_ko.md) | Four-chapter V-model roadmap; P-04B PARTIAL/current `29/29` default-off reset-harness closeout sequence, nominal E-stop MVP gate and post-MVP single-fault boundary |
| 2026-08-26 to 2026-09-15 / historical | [`2026-08-26_Pre_Arrival_Schedule_ko.md`](2026-08-26_Pre_Arrival_Schedule_ko.md) | Historical dated schedule: `P-01~P-09`, received-subset screen, HOME-first checkpoint, milestones and buffers |
| 2026-08-25 / active scope | [`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md) | **Authoritative scope/sequence**: P-04B runtime subset와 hook-0 isolated build PASS, active reset reject/released reset success 및 target reflash/runtime closeout order; remaining critical sequence and stop conditions |
| Completed 2026-08-18 | [`2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md`](2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md) | Historical completed runbook: final perfboard MDD10A-input active 6-step, hook-0 restore and all-LOW evidence |
| 2026-06-08 to 2026-06-10 | [`2026-06-08_to_2026-06-10_hardware_execution_plan.md`](2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A multimeter inspection, Wednesday parts follow-up |
| 2026-07-10 | [`2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md) | STM32 + ESP32 board-only UART command bridge plan |
