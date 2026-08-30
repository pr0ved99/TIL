# Execution Plans

This folder stores short-term execution plans for hardware sessions.

Use progress logs for what actually happened. Use this folder for the plan that should guide the next bench session.

Current firmware checkpoint is `P-04B PARTIAL`. The 2026-08-29 reason/command-age checkpoint was
`28/28`; the 2026-08-30 default-`0U` reset closeout harness brings current canonical host/static to
`25 + 2 + 2 = 29/29` and its ESP32 isolated build is PASS. The closeout order is active reset rejection
(`ERR ESTOP_ACTIVE` + persistent `TEL reason=ESTOP_ACTIVE`), released explicit-reset success,
then all-hooks-`0U` target reflash and motor/LiPo-disconnected no-command safe runtime before P-05.
The historical hook-0 isolated STM32/ESP32 build and current default-off reset-harness ESP32 isolated
build are PASS; none of these build results substitutes for the still-open target runtime.

## Index

| Date range | File | Scope |
| --- | --- | --- |
| Project-wide / current | [`00_Project_Master_Plan_To_Final_MVP_ko.md`](00_Project_Master_Plan_To_Final_MVP_ko.md) | Four-chapter V-model roadmap; P-04B PARTIAL/current `29/29` default-off reset-harness closeout sequence, nominal E-stop MVP gate and post-MVP single-fault boundary |
| 2026-08-26 to 2026-09-15 / active | [`2026-08-26_Pre_Arrival_Schedule_ko.md`](2026-08-26_Pre_Arrival_Schedule_ko.md) | **Current dated schedule**: `P-01~P-09`, received-subset screen, HOME-first next checkpoint, milestones and buffers |
| 2026-08-25 / active scope | [`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md) | **Authoritative scope/sequence**: P-04B runtime subset와 hook-0 isolated build PASS, active reset reject/released reset success 및 target reflash/runtime closeout order; remaining critical sequence and stop conditions |
| Completed 2026-08-18 | [`2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md`](2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md) | Historical completed runbook: final perfboard MDD10A-input active 6-step, hook-0 restore and all-LOW evidence |
| 2026-06-08 to 2026-06-10 | [`2026-06-08_to_2026-06-10_hardware_execution_plan.md`](2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A multimeter inspection, Wednesday parts follow-up |
| 2026-07-10 | [`2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md) | STM32 + ESP32 board-only UART command bridge plan |
