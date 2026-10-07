# 실행 계획

이 폴더는 전체 로드맵과 날짜별 작업 계획을 보관한다. 실제 수행 결과는 진행 기록과 시험 보고서를 따른다.

## 현재 시작점 — 2026-10-08

[현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md) → [10/8 마감 기록](../progress/2026-10-08_progress.md) → [Wi-Fi 계획](2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md)의 W5 순서로 읽는다.
**실제 W4 읽기 전용 TEL·WS·stale/복구·재접속·STARTUP 분리 표시는 완료했다.** 다음은 두 보드 USB·LiPo 미연결에서 PING/DISARM 입력·단일 UART 송신·seq/응답·세션 설계다.
ARM/CMD·전류/열·전체 안전 수용·주행·새 PCB CAD는 별도 미완료다. 이전 학습/납땜/모터 시험을 변경 없이 반복하지 않는다.
상세 근거는 [보고서33](../verification/33_W4_STM_UART_WebSocket_and_Startup_Status_2026-10-08_ko.md), 기존 단일 모터 범위는 [report32](../verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)를 따른다.

## Index

| Date range | File | Scope |
| --- | --- | --- |
| 2026-10-06 작성 / 10/8 갱신 | [ESP 학습·W4·W5 통합 계획](2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md) | W4 완료 근거와 W5 비구동 명령·세션·안전 계약 시작점 |
| 2026-10-02 / 코드 입력 | [ESP 단독 WebSocket 안내](2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md) | 실제 앱 적용 후보, HTTP 작업 예약·버퍼 수명·재접속·WS-1~4 |
| 2026-10-01 / 작업 범위 | [노트북·ESP 작업 계획](2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md) | ESP 단독 Wi-Fi, ADC/CAN PCB 설계 범위, 문서 수정과 코드 이해 |
| 2026-10-01 / 코드 입력 | [ESP 단독 Wi-Fi·HTTP 코드](2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md) | AP/STA 설정, 앱 전문·이벤트/HTTP 설명, 사용자 입력·검토·빌드 순서 |
| 2026-09-29 / 당시 재개 계획 | [휴식 후 방향 확인 계획](2026-09-29_Next_Session_M1_Direction_and_Bench_Closeout_ko.md) | 당시 M2 역방향 이미지와 A 방향 확인 계획. 후속 완료 결과는 report32 |
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
