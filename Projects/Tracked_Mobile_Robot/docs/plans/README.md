# 실행 계획

이 폴더는 전체 로드맵과 날짜별 작업 계획을 보관한다. 실제 수행 결과는 진행 기록과 시험 보고서를 따른다.

## 현재 시작점 — 2026-10-13

zero-only ARM/CMD의 모듈·main·브라우저 연결과 사용자 빌드/플래시·일부 보드 관측까지 진행했다. 최신 main C42·PAGE JS46 PC PASS와 증거 한계는 [10/13 기록](../progress/2026-10-13_progress.md), 재개점은 [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md)를 따른다. 전체 AC-B/S·nonzero 구동·전체 안전/주행은 미완료다.

학습은 [STM·ESP 교과서](../../07_Embedded_Learning_Notes/06_STM32_ESP32_Firmware_Textbook/README.md)로 이어간다. 아래 입력 안내와 표의 후보/미입력/검사 수는 해당 작성 시점 이력이다. 10/13 main 입력 안내 이후 ticket 시간 여유·수동 ARM 준비 대기·버튼 표시 보완이 있어 최신 소스의 대체본으로 사용하지 않는다.

## Index

| Date range | File | Scope |
| --- | --- | --- |
| 2026-10-13 / 저장본 C42·JS27·ESP 빌드 확인 | [main·브라우저 전체 교체 안내](2026-10-13_WiFi_ARM_CMD_Main_Integration_Code_Guide_ko.md) | HTTP/ticket·UART/seq·ACK/TEL·기한/취소·zero-only UI. 실제 main 저장/PC 검사·ESP 빌드 확인, 새 플래시/보드 시험 대기 |
| 2026-10-12 / 후보PC17 PASS | [UART executor 입력 안내](2026-10-12_WiFi_ARM_CMD_Executor_Code_Guide_ko.md) | ticket 접수·한 슬롯·송신 계획·취소/우선 DISARM·결과. 사용자 파일/ESP 빌드·main 연결은 미실행 |
| 2026-10-12 / 수정 대기 | [ARM/CMD state 일괄 수정 안내](2026-10-12_WiFi_ARM_CMD_State_Corrections_ko.md) | 최초 실제 저장본 컴파일 실패 0 tests/ERROR1. 정확한 위치·이유·header/source 완성본, CMake 유지 |
| 2026-10-11 / 후보 PC27 PASS | [ARM/CMD state 코드 안내](2026-10-11_WiFi_ARM_CMD_State_Code_Guide_ko.md) | phase·기한·ACK/TEL·취소/정지 판단. 사용자 파일 미입력·실제 저장본/전체 ESP 빌드·실행 adapter 미검증 |
| 2026-10-11 / PC·빌드 확인 완료 | [ARM/CMD owner 코드 안내](2026-10-11_WiFi_ARM_CMD_Owner_Code_Guide_ko.md) | 한 연결 예약·control ID·대조/취소. 실제PC9 PASS, ESP 전체 빌드 성공 사용자 확인. FSM/기한·UART 미연결 |
| 2026-10-10 작성 / 10/11 빌드 확인 | [ARM/CMD ticket 코드 안내](2026-10-10_WiFi_ARM_CMD_Ticket_Code_Guide_ko.md) | 연결/용도·150ms·한 번 소비·번호 소진. 실제PC12 PASS, ESP 전체 빌드 성공 사용자 확인 |
| 2026-10-10 / parser 확인 완료 | [ARM/CMD parser 코드 안내](2026-10-10_WiFi_ARM_CMD_Parser_Code_Guide_ko.md) | 새 header/source·CMake, 실제PC15 PASS·ESP 빌드 성공 사용자 확인. UART 미연결 |
| 2026-10-10 작성 / 10/11 갱신 | [Wi-Fi ARM/CMD 제어 계약](2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md) | 지속 소유권·ticket·기한·priority DISARM·zero-only, AC-H/B/S 기준. 기초 모듈PC15/12/9 PASS·ESP 빌드 성공 사용자 확인, 제어 실행 경로 미연결 |
| 2026-10-08 계획 / 10/10 마감 | [두 보드 W5 PING/DISARM 계획](2026-10-08_W5_Two_Board_PING_DISARM_Plan_ko.md) | 당시 준비/실행 순서 보존, 완료 근거는 report34의 비구동 범위 |
| 2026-10-06 작성 / 10/11 갱신 | [ESP 학습·W4·W5 통합 계획](2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md) | W4/W5 완료와 ARM/CMD 기초 모듈 이후 상태/기한·실행 연결의 경계 |
| 2026-10-02 / 코드 입력 | [ESP 단독 WebSocket 안내](2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md) | 실제 앱 적용 후보, HTTP 작업 예약·버퍼 수명·재접속·WS-1~4 |
| 2026-10-01 / 작업 범위 | [노트북·ESP 작업 계획](2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md) | ESP 단독 Wi-Fi, ADC/CAN PCB 설계 범위, 문서 수정과 코드 이해 |
| 2026-10-01 / 코드 입력 | [ESP 단독 Wi-Fi·HTTP 코드](2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md) | AP/STA 설정, 앱 전문·이벤트/HTTP 설명, 사용자 입력·검토·빌드 순서 |
| 2026-09-30 / 완료 시험의 입력 이력 | [M1 active DISARM 안내](2026-09-30_M1_Active_DISARM_Console_Code_Guide_ko.md) | 당시 입력 블록. 실제 관측은 report32, 현재 앱의 대체 소스나 재실행 지시가 아님 |
| 2026-09-30 / 완료 시험의 입력 이력 | [M1 물리 S0 정지 안내](2026-09-30_M1_Physical_S0_Stop_Console_Code_Guide_ko.md) | 당시 S0 관측 절차. report32 범위와 정식 T-ESTOP-007 BLOCKED 구분 |
| 2026-09-30 / 완료 시험의 입력 이력 | [M1 3초 구동 안내](2026-09-30_M1_Three_Second_Run_Console_Code_Guide_ko.md) | A/B 제한 구동의 시작 코드 이력. 현재 UART bridge의 M2_RUN 소스 상태와 구분 |
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
