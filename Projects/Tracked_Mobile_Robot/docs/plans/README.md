# 실행 계획

이 폴더는 전체 로드맵과 날짜별 작업 계획을 보관한다. 실제 수행 결과는 진행 기록과 시험 보고서를 따른다.

## 현재 시작점 — 2026-09-30

**현재는 노트북에서 문서 개편 4단계를 마친 상태다.**
[전체 실행 계획](00_Project_Master_Plan_To_Final_MVP_ko.md)·[프로젝트 README](../../README.md)·진행 기록 형식의 정리는 [9/30 기록](../progress/2026-09-30_progress.md)에 마감했다.

**하드웨어 재개 목표는 A/M1 양수 명령의 실제 전진 방향 확인이다.**
[현재 작업 현황](../handoff/CURRENT_SESSION_CONTEXT.md) →
[9/29 진행 기록](../progress/2026-09-29_progress.md) →
[휴식 후 계획](2026-09-29_Next_Session_M1_Direction_and_Bench_Closeout_ko.md) 순서로 읽는다.

- A/M1 ±10% 회전·CPS 부호·정지, B/M2 DIR 보정 후 실제 양방향 회전·CPS 부호·정지를 확인했다.
  두 모터 동력선은 원래 A/M1·B/M2 연결로 복원했다. A의 양수 전진 방향 육안 확인만 별도로 남았다.
- 현재 ESP는 M2 역방향10%/300ms 시험1U 이미지다. 다음 M1 시험 전에 소스·HELP·검사 조건을 함께 변경한다.
- T004 기존 PASS와 T005A 전체 PARTIAL 유지. 현재 정적31개 중30 PASS, 시험hook=0 요구1개 FAIL이다.
- 완료한 검사는 변경·실패 없이 반복하지 않는다. 펌웨어 입력과 두 보드의 빌드·플래시는 사용자가 수행한다.

날짜별 계획의 `next/open/current`는 해당 시점의 표현이다. 아래 이력 문서를 현재 작업 지시로 사용하지 않는다.

## Index

| Date range | File | Scope |
| --- | --- | --- |
| 2026-09-29 / 현재 재개 | [휴식 후 방향 확인 계획](2026-09-29_Next_Session_M1_Direction_and_Bench_Closeout_ko.md) | 현재 M2 역방향 이미지, A/M1 실제 전진 방향, err 관측과 후속 gate |
| 2026-09-27 / 입력 이력 | [M1 수동 1회 시험 코드](2026-09-27_M1_One_Shot_Console_Code_Guide_ko.md) | 당시 WIP와 최초5% 안내. 최신 실행 설정은 현재 인수인계를 따름 |
| 2026-09-23 / 검사 이력 | [엔코더 조정부 검사와 다음 작업](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md) | 당시 저항·도통·전원 PASS; 후속 실제 엔코더 결과는 reports 29/30 |
| 2026-09-22 / 후속 결과 있음 | [전원 경로와 T005A 계획](2026-09-22_Next_Session_Power_Path_and_T_ESTOP_005A_Plan_ko.md) | 실행 결과는 report 27; 전체 T005A는 PARTIAL |
| 2026-09-16 plan / updated through 9/19 | [납땜 체크리스트](2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md) | 당시 배선·무전원 검사·마감 기록; 후속 T004 결과는 report 26 |
| 2026-09-11 plan / updated through 9/19 | [`2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md`](2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md) | UART·측정 헤더 도면 검토 및 제작 이력 |
| 2026-09-08 / T004 완료 이력 | [T004 실행 절차](2026-09-08_T_ESTOP_004_Firmware_PWM_Integration_Runbook_ko.md) | 당시 MDD B+/모터 분리 조건의 절차; 9/22 report 26에 latch/reset/wire-open/PWM/safe restore PASS 기록 |
| 2026-09-05 / Gates 1~4 completed, historical predecessor | [`2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md`](2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md) | Corrected K2 mapping, S0-A/S0-B independence and conditioned PC7 baseline; Gate 5 moved to the 2026-09-08 runbook |
| 2026-09-03 / execution closed, historical | [`2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md`](2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md) | 2026-09-05에 실행 종료; rail/U1 subset과 후속 control-only results는 progress에 보존, K2 frozen coordinate table은 bottom-view 해석 오류로 비정본이며 남은 formal gates는 새 runbook으로 이관 |
| Project-wide / current | [전체 MVP 로드맵](00_Project_Master_Plan_To_Final_MVP_ko.md) | 현재 단계·작업별 완료 조건·MVP 종료선, 펼쳐 읽는 상세 Gate와 과거 계획 |
| 2026-08-26 to 2026-09-15 / historical | [`2026-08-26_Pre_Arrival_Schedule_ko.md`](2026-08-26_Pre_Arrival_Schedule_ko.md) | Historical dated schedule: `P-01~P-09`, received-subset screen, HOME-first checkpoint, milestones and buffers |
| 2026-08-25 / 범위 결정 이력 | [`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md) | 당시 P-01~P-09와 MVP/후속 범위 결정; 완료 상태와 재개 순서는 위 최신 시작점을 따름 |
| Completed 2026-08-18 | [`2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md`](2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md) | Historical completed runbook: final perfboard MDD10A-input active 6-step, hook-0 restore and all-LOW evidence |
| 2026-06-08 to 2026-06-10 | [`2026-06-08_to_2026-06-10_hardware_execution_plan.md`](2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A multimeter inspection, Wednesday parts follow-up |
| 2026-07-10 | [`2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md) | STM32 + ESP32 board-only UART command bridge plan |
