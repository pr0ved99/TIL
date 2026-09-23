# 실행 계획

이 폴더는 전체 로드맵과 날짜별 작업 계획을 보관한다. 실제 수행 결과는 진행 기록과 시험 보고서를 따른다.

## 현재 시작점 — 2026-09-23

**다음 작업은 실제 엔코더 케이블 연결과 새 만능기판 경로의 입력 전압·수동 회전 검증이다.**
[현재 작업 현황](../handoff/CURRENT_SESSION_CONTEXT.md) →
[9/23 진행 기록](../progress/2026-09-23_progress.md) →
[엔코더 조정부 보고서의 다음 시작점](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md#7-다음-시작점) 순서로 읽는다.

- 완료: UART/CTRL/ENC/IMU 헤더 배선, T004 conditioned firmware/PWM 시험, 시험 후 ESP 네 hook `0U` 복구.
  당시 정적 검사 **30/30 PASS**, 복구 빌드·플래시는 사용자 수행 결과다.
- 최신 완료: 엔코더 조정부 납땜, 저항 8곳·전원 연결/단락 6곳, JENC_1/2 **+5.05V** 사용자 보고 PASS.
  `...ENC_Conditioning_WIP.vrt`와 동일 이름 PDF 검토 결과는 report 28에 있다.
- 남음: 실제 엔코더 연결 후 LOW/HIGH·수동 회전, 부팅 초기 CPS 튐 확인, T005A 전체 판정과 실모터 시험.
  T005A는 **PARTIAL**이며 MDD B+는 K1 87에 연결된 상태로 기록됐다. 두 모터는 분리 상태다.
- 완료한 검사는 변경·실패 없이 반복하지 않는다. 펌웨어 입력과 두 보드의 빌드·플래시는 사용자가 수행한다.

날짜별 계획의 `next/open/current`는 해당 시점의 표현이다. 아래 완료·이력 문서를 그대로 다음 작업 지시로 사용하지 않는다.

## Index

| Date range | File | Scope |
| --- | --- | --- |
| 2026-09-23 / 현재 재개 | [엔코더 조정부 검사와 다음 작업](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md) | 완료한 저항·도통·전원 검사는 보존; 실제 엔코더 연결부터 진행 |
| 2026-09-22 / 후속 결과 있음 | [전원 경로와 T005A 계획](2026-09-22_Next_Session_Power_Path_and_T_ESTOP_005A_Plan_ko.md) | 실행 결과는 report 27; 전체 T005A는 PARTIAL |
| 2026-09-16 plan / updated through 9/19 | [납땜 체크리스트](2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md) | 당시 배선·무전원 검사·마감 기록; 후속 T004 결과는 report 26 |
| 2026-09-11 plan / updated through 9/19 | [`2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md`](2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md) | UART·측정 헤더 도면 검토 및 제작 이력 |
| 2026-09-08 / T004 완료 이력 | [T004 실행 절차](2026-09-08_T_ESTOP_004_Firmware_PWM_Integration_Runbook_ko.md) | 당시 MDD B+/모터 분리 조건의 절차; 9/22 report 26에 latch/reset/wire-open/PWM/safe restore PASS 기록 |
| 2026-09-05 / Gates 1~4 completed, historical predecessor | [`2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md`](2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md) | Corrected K2 mapping, S0-A/S0-B independence and conditioned PC7 baseline; Gate 5 moved to the 2026-09-08 runbook |
| 2026-09-03 / execution closed, historical | [`2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md`](2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md) | 2026-09-05에 실행 종료; rail/U1 subset과 후속 control-only results는 progress에 보존, K2 frozen coordinate table은 bottom-view 해석 오류로 비정본이며 남은 formal gates는 새 runbook으로 이관 |
| Project-wide / current | [전체 MVP 로드맵](00_Project_Master_Plan_To_Final_MVP_ko.md) | 최신 시작점과 MVP 종료선, 단계별 검증 조건, 날짜가 표시된 과거 계획 |
| 2026-08-26 to 2026-09-15 / historical | [`2026-08-26_Pre_Arrival_Schedule_ko.md`](2026-08-26_Pre_Arrival_Schedule_ko.md) | Historical dated schedule: `P-01~P-09`, received-subset screen, HOME-first checkpoint, milestones and buffers |
| 2026-08-25 / 범위 결정 이력 | [`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md) | 당시 P-01~P-09와 MVP/후속 범위 결정; 완료 상태와 재개 순서는 위 최신 시작점을 따름 |
| Completed 2026-08-18 | [`2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md`](2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md) | Historical completed runbook: final perfboard MDD10A-input active 6-step, hook-0 restore and all-LOW evidence |
| 2026-06-08 to 2026-06-10 | [`2026-06-08_to_2026-06-10_hardware_execution_plan.md`](2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A multimeter inspection, Wednesday parts follow-up |
| 2026-07-10 | [`2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md) | STM32 + ESP32 board-only UART command bridge plan |
