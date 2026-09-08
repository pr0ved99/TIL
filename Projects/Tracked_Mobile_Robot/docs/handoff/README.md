# Handoff Notes

이 폴더는 `Tracked_Mobile_Robot` 프로젝트를 다른 Codex 세션이나 사람이 이어받을 때 필요한 인수인계 문서를 저장한다.

## How To Use

새 대화창에서는 작은 현재상태 문서에서 시작한다.

1. [`CURRENT_SESSION_CONTEXT.md`](CURRENT_SESSION_CONTEXT.md)
2. [`../progress/README.md`](../progress/README.md)와 최신 progress 1개
3. 현재 gate에 직접 필요한 plan/report/source 1개

`PROJECT_MEMORY.md`, 이 전체 index, 과거 handoff/progress와 architecture tree는 현재 문서로
해결되지 않는 사실이나 충돌이 있을 때만 읽는다. 복사용 프롬프트는
[`NEXT_SESSION_START_PROMPT.md`](NEXT_SESSION_START_PROMPT.md)다.
세션과 외부 대화 아카이브 운용은 [`CODEX_CONTEXT_WORKFLOW.md`](CODEX_CONTEXT_WORKFLOW.md)를 따른다.

ChatGPT Pro에서 Plus로 전환할 때만 [`2026-07-29_codex_plus_transition_handoff.md`](2026-07-29_codex_plus_transition_handoff.md)를 사용한다. 일반 프로젝트 세션의 필수 읽기 문서에는 포함하지 않는다.

## Current Continuation Sources

| Date | File | Use |
| --- | --- | --- |
| Current | [`CURRENT_SESSION_CONTEXT.md`](CURRENT_SESSION_CONTEXT.md) | **First read**: 완료 기준선, 다음 `T-ESTOP-004`, 이후 critical path와 작업 방식 |
| Current | [`CODEX_CONTEXT_WORKFLOW.md`](CODEX_CONTEXT_WORKFLOW.md) | 작은 컨텍스트, bench 한 단계 진행, closeout와 D: archive lookup 규칙 |
| 2026-09-08 | [`../progress/2026-09-08_progress.md`](../progress/2026-09-08_progress.md) | **Current result baseline**: wire-open, XL4015 #1/#2 power와 conditioned sense 기능 subset PASS; T004 NOT RUN |
| 2026-09-08 | [report 25](../verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md) | **Current powered evidence**: bounded logic-power/conditioned-sense result와 미완료 evidence |
| 2026-09-07 | [`2026-09-07_session_recovery_handoff.md`](2026-09-07_session_recovery_handoff.md) | Recovery checkpoint: 중단된 문서/Git 작업 복원과 9/8 결과로 이어지는 기준 |
| 2026-09-07 | [`../progress/2026-09-07_progress.md`](../progress/2026-09-07_progress.md) | 문서 상태·artifact hash 정정과 host/static 29/29 재확인; 새 hardware evidence 없음 |
| 2026-09-05 | [`../plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md`](../plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md) | **Current bench runbook**: remaining explicit wire-open, conditioned PC7, firmware/PWM and direct downstream-rail gates |
| 2026-09-05 | [`../progress/2026-09-05_progress.md`](../progress/2026-09-05_progress.md) | Previous control-only baseline: RevC/6P/K1 assembly, K2 polarity correction and 12.24 V subset |
| 2026-09-05 | [`../verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md`](../verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md) | Previous control-only Physical E-stop evidence and full-gate exclusions |
| 2026-09-03 | [`../plans/2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md`](../plans/2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md) | Historical RevC local unpowered runbook; K2 bottom-view erratum added |
| 2026-09-03 | [`../progress/2026-09-03_progress.md`](../progress/2026-09-03_progress.md) | Historical partial-assembly rail/U1/K2 unpowered checkpoint |
| 2026-09-01 | [`../progress/2026-09-01_progress.md`](../progress/2026-09-01_progress.md) | Previous RevC FINAL/PDF and partial-solder baseline; actual continuity/isolation remained OPEN |
| 2026-08-30 | [`../progress/2026-08-30_progress.md`](../progress/2026-08-30_progress.md) | **Previous continuation**: P-04B default-`0U` reset harness, current `29/29`과 ESP isolated build PASS; reset target runtime OPEN; crimp tool user-reported arrived/unverified, 6P unassembled |
| 2026-08-29 | [`../progress/2026-08-29_progress.md`](../progress/2026-08-29_progress.md) | **Previous firmware checkpoint**: P-04A COMPLETE, P-04B reason/command-age PARTIAL, historical `28/28`와 hook-0 isolated build PASS, reset/target reflash-runtime OPEN |
| 2026-08-29 | [`../verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md`](../verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md) | **Current firmware evidence**: reason/age와 direct-PC7 active/latch UART subset 및 hook-0 isolated build; reset 및 target reflash/runtime 경계 |
| 2026-08-29 | [`../verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md`](../verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md) | **Previous firmware baseline**: positive symmetric/zero-state applied-output telemetry와 measured-output boundary |
| 2026-08-28 | [`../progress/2026-08-28_progress.md`](../progress/2026-08-28_progress.md) | Historical P-03/REQ-SAFE-004 runtime, incoming-screen and 6P/tooling checkpoint |
| 2026-08-28 | [`../verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md`](../verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md) | **Current incoming evidence**: received component-level unpowered PASS와 powered/integrated NOT PASS 경계 |
| 2026-08-27 | [`../progress/2026-08-27_progress.md`](../progress/2026-08-27_progress.md) | Historical P-02B~P-02C-2와 P-03A/P-03B source/static/full-build completion and partial-arrival transition |
| 2026-08-26 | [`../progress/2026-08-26_progress.md`](../progress/2026-08-26_progress.md) | Previous schedule baseline: P-01/P-02A completion, received-plate correction and evidence boundary |
| 2026-08-26 | [`../plans/2026-08-26_Pre_Arrival_Schedule_ko.md`](../plans/2026-08-26_Pre_Arrival_Schedule_ko.md) | Historical dated schedule: P-01~P-09 milestones and buffers |
| 2026-08-25 | [`../progress/2026-08-25_progress.md`](../progress/2026-08-25_progress.md) | Current scope baseline: final remaining-work audit, evidence boundary and `005A/005B` split |
| 2026-08-25 | [`../plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](../plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md) | **Authoritative scope/sequence**: final critical path, pre-arrival `P-01~P-09`, post-arrival gates and stop rules |
| 2026-08-24 | [`../progress/2026-08-24_progress.md`](../progress/2026-08-24_progress.md) | Historical direct-PC7 runtime, F1/K2 incoming precheck and initial `FM-ESTOP-014` finding |
| 2026-08-24 | [`../verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md`](../verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md) | Historical direct-PC7 firmware/runtime and F1/K2/resistor unpowered subset; 전체 Physical E-stop은 NOT PASS |
| 2026-08-18 | [`2026-08-18_k1_order_and_physical_estop_continuation_ko.md`](2026-08-18_k1_order_and_physical_estop_continuation_ko.md) | Historical K1 order/F1 planning handoff; 2026-08-25 progress/plan이 supersede |
| 2026-08-18 | [`../progress/2026-08-18_progress.md`](../progress/2026-08-18_progress.md) | Historical MG540 vendor data, final perfboard 19 kHz/safe restore, K1 catalog numerical PASS와 주문 |
| 2026-08-18 | [`../verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md`](../verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md) | Final perfboard MDD10A-input active DIR/PWM, direction margin, hook-0 all-LOW report |
| 2026-08-16 | [`../plans/2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md`](../plans/2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md) | Completed runbook: final perfboard active DIR/PWM 6-step, hook-`0U` restore와 all-LOW closeout |
| 2026-08-13 | [`2026-08-13_power_and_physical_estop_session_ko.md`](2026-08-13_power_and_physical_estop_session_ko.md) | Historical RevB/permanent `10 kΩ` pull-down, board power/back-power와 초기 Physical E-stop baseline; 2026-08-18 handoff가 supersede |
| 2026-08-13 | [`2026-08-13_motor_output_safety_and_perfboard_planning_session_ko.md`](2026-08-13_motor_output_safety_and_perfboard_planning_session_ko.md) | Completed historical runbook; required timeout/fault/reset scope PASS, optional perfboard work deferred |
| 2026-08-12 | [`../progress/2026-08-12_progress.md`](../progress/2026-08-12_progress.md) | UART Gate C와 motor-disconnected MCU low-level chapter PASS; external 10 kΩ 결정과 다음 power/E-stop gate |
| 2026-08-12 | [`../verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`](../verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md) | Timeout/fault/reset FAIL→10 kΩ PASS, raw hashes, evidence boundary와 final safe restore 정본 |
| 2026-08-12 | [`../verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md`](../verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md) | T-BRIDGE-008A remaining response vectors, T-BRIDGE-008B 8-vector와 safe closeout 판정·evidence boundary |
| 2026-08-12 | [`2026-08-12_focused_uart_gate_c_session_plan_ko.md`](2026-08-12_focused_uart_gate_c_session_plan_ko.md) | Completed historical runbook; current 작업 지시로 사용하지 않음 |
| 2026-08-11 | [`../progress/2026-08-11_progress.md`](../progress/2026-08-11_progress.md) | Partial-frame-name까지 4개 T-BRIDGE-008A subvector PASS, all-hooks-`0U`/`15/15`/safe full-build/flash와 post-READY TEL 164 회귀; invalid terminator/control next |
| 2026-08-11 | [`../verification/14_ESP32_Partial_Frame_Name_ACK_Recovery_Test_Report_2026-08-11_ko.md`](../verification/14_ESP32_Partial_Frame_Name_ACK_Recovery_Test_Report_2026-08-11_ko.md) | T-BRIDGE-008A partial-frame-name rejection/recovery와 current safe closeout report |
| 2026-08-07 | [`../progress/2026-08-07_progress.md`](../progress/2026-08-07_progress.md) | Required-`seq` uint32-overflow까지 3개 T-BRIDGE-008A subvector PASS, all-hooks-`0U`/`15/15`/protocol recompile+relink `0/0`/safe flash와 READY 후 14.43 s/TEL 145 회귀; partial frame-name vector next |
| 2026-08-07 | [`../verification/13_ESP32_Required_Seq_Uint32_Overflow_ACK_Recovery_Test_Report_2026-08-07_ko.md`](../verification/13_ESP32_Required_Seq_Uint32_Overflow_ACK_Recovery_Test_Report_2026-08-07_ko.md) | T-BRIDGE-008A required-`seq` uint32-overflow rejection/recovery와 current safe restore report |
| 2026-08-07 | [`../verification/12_ESP32_Trailing_Comma_ACK_Recovery_Test_Report_2026-08-07_ko.md`](../verification/12_ESP32_Trailing_Comma_ACK_Recovery_Test_Report_2026-08-07_ko.md) | T-BRIDGE-008A trailing-comma rejection/recovery와 historical post-trailing safe full-build/artifact reproduction report |
| 2026-08-06 | [`2026-08-06_safe_uart_baseline_handoff.md`](2026-08-06_safe_uart_baseline_handoff.md) | Historical pre-partial-name checkpoint; 2026-08-11 progress/report가 current continuation |
| 2026-08-06 | [`../progress/2026-08-06_progress.md`](../progress/2026-08-06_progress.md) | Duplicate-seq subvector PASS (008A overall PARTIAL), all-hooks-`0U`/`15/15`/safe build와 session-observed flash verify, READY 후 14.42 s/TEL 150 회귀 및 provenance 한계 |
| 2026-08-06 | [`../verification/11_ESP32_Duplicate_Required_Seq_ACK_Recovery_Test_Report_2026-08-06_ko.md`](../verification/11_ESP32_Duplicate_Required_Seq_ACK_Recovery_Test_Report_2026-08-06_ko.md) | T-BRIDGE-008A duplicate required `seq` rejection/recovery subvector와 safe restore report |
| 2026-08-04 | [`2026-08-04_uart_runtime_and_active_disarm_handoff.md`](2026-08-04_uart_runtime_and_active_disarm_handoff.md) | Historical controlled-test checkpoint; current 작업 지시로 사용하지 않음 |
| 2026-08-04 | [`../progress/2026-08-04_progress.md`](../progress/2026-08-04_progress.md) | Historical Gate A/B, active DISARM과 wrong-ACK controlled-test progress |
| 2026-08-04 | [`../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md`](../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md) | UART RX end to PWM last-edge MCU-pin first baseline과 scope limit |
| 2026-08-03 | [`../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`](../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md) | Gate A/B raw runtime 판정, wrong ACK type와 physical provenance gap |
| 2026-08-03 | [`2026-08-03_uart_response_gated_startup_implementation_handoff.md`](2026-08-03_uart_response_gated_startup_implementation_handoff.md) | Historical implementation checkpoint; current 작업 지시로 사용하지 않음 |
| 2026-08-03 | [`2026-08-03_uart_strict_parser_regression_handoff.md`](2026-08-03_uart_strict_parser_regression_handoff.md) | 구현 전 strict-parser 정상 시퀀스 PASS와 startup 문제를 남긴 역사 baseline; 현재 작업 지시로 사용하지 않음 |
| 2026-08-03 | [`../verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md`](../verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md) | PING/PONG부터 final DISARMED까지 current parser controlled-run 결과, 근거와 release 범위 제한 |
| 2026-08-03 | [`../progress/2026-08-03_progress.md`](../progress/2026-08-03_progress.md) | USART1 decode, dual PWM/direction timing PASS와 current UART normal-sequence PASS; 남은 startup/malformed·active safety gate |
| 2026-08-03 | [`../verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md`](../verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md) | Raw capture에 연결된 PWM/DIR 측정 보고서, 계측 범위와 안전 gate 판정 |
| 2026-07-31 | [`../progress/2026-07-31_progress.md`](../progress/2026-07-31_progress.md) | Strict UART parser fail-closed/recovery와 startup PING/desynchronization 한계 |
| 2026-07-30 | [`../progress/2026-07-30_progress.md`](../progress/2026-07-30_progress.md) | 50회전 `1560 counts/output rev` 확정과 signed CPS-to-mRPM self-test·dynamic log PASS; next physical sign/powered-noise/safety gates |
| 2026-07-29 | [`../progress/2026-07-29_progress.md`](../progress/2026-07-29_progress.md) | Dual encoder production TEL -> ESP32 CW/CCW PASS, direction regression와 active timeout/DISARM LED functional PASS; next physical sign/powered-noise/safety gates |
| 2026-07-29 | [`2026-07-29_codex_plus_transition_handoff.md`](2026-07-29_codex_plus_transition_handoff.md) | Pro 종료 후 Plus용 Codex 설정, 사용량 절약 규칙, smoke test와 rollback 절차 |
| 2026-07-28 | [`2026-07-28_kicad_reva_wiring_handoff.md`](2026-07-28_kicad_reva_wiring_handoff.md) | RevA wiring baseline, verified/TBD boundary, safety constraints and exact next work |
| 2026-07-28 | [`../progress/2026-07-28_progress.md`](../progress/2026-07-28_progress.md) | KiCad RevA functional wiring draft, dated ERC/PDF evidence and verified/TBD boundary |
| 2026-07-28 | [`../../09_Electrical_Design/README.md`](../../09_Electrical_Design/README.md) | Electrical source/evidence index and permanent-wiring release blockers |
| 2026-07-27 | [`../progress/2026-07-27_progress.md`](../progress/2026-07-27_progress.md) | TIM3/TIM5 dual motor-off independent hand-count and next speed-module work |
| 2026-07-27 | [`../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md`](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md) | Encoder pin map, conditioning, TIM3/TIM5 count evidence and powered-noise gate |
| 2026-07-26 | [`../progress/2026-07-26_progress.md`](../progress/2026-07-26_progress.md) | STM32/MDD10A static routing, direction-sequence open item와 MG540 TIM3 motor-power-off encoder 결과 |
| 2026-07-24 | [`../progress/2026-07-24_progress.md`](../progress/2026-07-24_progress.md) | 아크릴 3T 어댑터 플레이트 Rev A 제조 파일 검증, 업체 서버 업로드 차단 상태와 다음 주문 작업 |
| 2026-07-24 | [`../../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](../../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md) | 주문 정본, 치수·벡터 검증 결과와 제작 전 확인 항목 |
| 2026-07-20 | [`2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md`](2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md) | ESP32 scripted command와 timeout-zero까지 PASS한 bridge closeout 및 MDD10A logic test 시작점 |

## Historical Handoff

| Date | File | Note |
| --- | --- | --- |
| 2026-07-14 | [`2026-07-14_esp32_stm32_uart_bridge_handoff.md`](2026-07-14_esp32_stm32_uart_bridge_handoff.md) | structured TEL parser 이전의 UART bridge handoff |
| 2026-06-22 | [`2026-06-22_tracked_mobile_robot_handoff.md`](2026-06-22_tracked_mobile_robot_handoff.md) | STM32CubeMX-first UART MVP 구현 전후 상태 |
| 2026-06-04 | [`2026-06-04_tracked_mobile_robot_handoff.md`](2026-06-04_tracked_mobile_robot_handoff.md) | 초기 프로젝트 상태, 현재와 다른 결정이 포함될 수 있음 |

## Rules For Future Handoff

- 새 handoff는 날짜 prefix를 붙인다: `YYYY-MM-DD_topic_handoff.md`.
- 최신 handoff는 이 README의 `Current Continuation Sources`에 추가한다.
- handoff에는 반드시 다음을 포함한다.
  - 현재 목표
  - 완료된 것
  - 다음 작업
  - 건드리면 안 되는 파일/결정
  - hardware wiring safety
  - evidence 위치
  - 첫 번째로 실행할 확인 명령
- 새 세션은 `git status --short Projects/Tracked_Mobile_Robot`를 먼저 실행한 뒤 작업한다.
