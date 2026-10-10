# 시스템 아키텍처 문서 안내

상태 대조일: **2026-10-11**. 코드·기존 시험 증거에 맞춘 문서 정리이며 새 하드웨어 시험 결과가 아니다.

이 폴더는 **현재 설계 계약과 그 결정 근거**를 관리한다. 한국어 `_ko.md`가 정본이고 영문은 보조 참고본이다.
초기 후보·과거 시험 기록·향후 계획은 해당 시점과 범위를 표시해 보존한다.
파일명에 Candidate/Plan이 있거나 작성일이 오래됐다는 이유만으로 폐기된 설계로 취급하지 않는다.

## 현재 구현과 검증 범위

| 영역 | 현재 기준 | 아직 완료하지 않은 범위 |
| --- | --- | --- |
| 제어 책임 | STM32가 출력·명령 timeout·최종 안전 판단을 소유. ESP32가 production 명령 진입점 | 일반 PC forwarding, CAN transport, STM32 FreeRTOS/LL 전환 |
| 통신 | ESP GPIO17/18 ↔ STM USART1 PA9/10. USART2 PA2/3는 bench logger | 전체 UART/bridge release의 잔여 증거·시험 |
| Wi-Fi·제어 준비 | W4 실제 TEL/WS·W5 비구동 PING/DISARM PASS. ARM/CMD parser·ticket·owner 실제 PC15/12/9 PASS, ESP 전체 빌드 성공 사용자 확인 | 상태·기한·ACK/TEL·취소/정지 흐름, main·큐/UART·브라우저 연결과 AC-H 전체·AC-B/S. 새 모듈 보드 실행 미확인 |
| 상태·TEL | 현재 코드 state=`DISARMED/ARMED/FAULT`, 원인은 별도 `reason`. 적용 PWM·command age·CPS 보고 | 확장 상태머신·저전압 입력/정지·IMU 통합. TEL PWM은 소프트웨어 적용값이며 실측 출력 피드백이 아님 |
| 모터 매핑 | A=왼쪽/M1/JENC_1/TIM3, B=오른쪽/M2/JENC_2/TIM5.9/30 두 동력선 연결 시험과 A 양수 실제 전진 확인 | 최종 기구 장착·양쪽 동시 구동·실주행 방향/거리 검증 |
| PWM/DIR | PB6/PC8=M1, PB7/PC9=M2. B DIR HIGH=전진/LOW=후진 보정 뒤 양방향 단발 확인, A active DISARM과 A/B 각각10%·3초 구동 관측 | 부하·전류·온도·노이즈·반복 기동 및 전체 T-MOTOR-003 수용 조건 |
| 엔코더 | PB4/PB5 및 PA0/PA1, 입력별 1 kΩ 직렬+15 kΩ 풀다운 실장. 손회전·단발 구동 CPS 관측 | 구동 중 파형/노이즈와 외부 기준 속도 검증. 1560 counts/rev는 현재 변환 기준이며 실주행 보정과 별개 |
| 비상정지 | PC7은 `GPIO_Input`이며 EXTI 구현이 아님. conditioned sense/latch/reset/PWM의 모터 분리 T004 PASS, A 구동 중 S0/PWM/CPS 정지 관측 | 전체 T005A PARTIAL·정식 T-ESTOP-007 BLOCKED. 기계 정지 시간/거리·rail 동시 계측과 전력단 잔여 수용 조건 |
| 전원 | F1→S1→+버스바에서 K1·두 XL4015·F2 제어 분기. K1 87→MDD B+, MDD B−→GND 버스바 | 전류·열·단자 편차·rail-off 수용 기준. 현재 관측을 정격 release로 확대하지 않음 |
| IMU | PB8/PB9 I2C, PB1 INT, PC4 RST 배선·무전원 검사 완료 | CubeMX 설정·센서 전원/모드·풀업·실제 통신과 센서값 |
| CAN | PA11 RX/PA12 TX 예약, 사용자 보유 SN65HVD230 MCU-230 모듈 | 모듈 상세·전원·종단·버스·펌웨어 검증. 모듈 보유는 CAN 동작 검증이 아님 |
| ADC·적층 | PA4/PB0 진단 후보. 기존 최상층·새 하층 확장 및 분리형 하네스 검토 | 회로 값·보호·핀 순서·실장·구매 미확정. 기본 저전압 경고/정지는 첫 주행 전 준비 |

**마지막 보드 실행:** ESP `esp32_wifi_link`의 W5 비구동 시험이다. 각 보드 USB 공급·LiPo 미연결로 실행했고 두 USB 분리 완료는 사용자 확인이다.
STM PA10 pull-up·PONG 시험 hook0U 유지.10/11 새 기초 모듈은 CMake 등록·사용자 빌드 확인 상태이며 새 플래시/보드 실행은 미확인이다.

**9/30 로봇 시험 이력:** 당시 ESP는 기판 밖에 두고 GPIO17·18·GND를 연장했다. 두 보드 USB 공급과 XL4015 #1 보드용2P 분리·절연은 최종 로봇 전원 구조와 구분한다.
별도 `esp32_uart_bridge`의 M2_RUN 수동 hook1U·기존 자동 hook4개0U, 정적30 PASS/1 FAIL(default-off)은 해당 앱의 마지막 시험 소스 이력이다. 현재 Wi-Fi 플래시 앱의 설정이 아니다.
과거 all-hooks0U 복구 기록을 이 별도 앱의 복구 완료로 해석하지 않는다. 실제 재개 조건은 [현재 인수인계](../docs/handoff/CURRENT_SESSION_CONTEXT.md), 앱/모듈 구분은 [펌웨어 목차](../03_Firmware/README.md)를 따른다.

## 무엇을 읽을까

| 목적 | 문서 | 읽는 방법 |
| --- | --- | --- |
| MCU 원리 복습 | [01 자료 읽기](01_MCU_Datasheet_Reading_Map_ko.md), [02 개요](02_MCU_Introduction_and_Description_ko.md), [03 코어](03_MCU_Core_Memory_Interrupts_ko.md), [04 타이머](04_MCU_Timers_and_Watchdogs_ko.md), [05 통신·I/O](05_MCU_Communication_and_IO_Peripherals_ko.md) | 개념과 초기 후보를 학습. 실제 배정은 06 기준 |
| 핀·역할·연결 이해 | [06 핀 배정](06_MCU_Pin_Allocation_Candidate_ko.md), [07 ESP 역할](07_ESP32S3_Features_and_Project_Role_ko.md), [11 블록도](11_System_Block_Diagram_and_Interface_Map_ko.md) | 설정·배선·동작 검증을 구분 |
| 출력·통신 계약 | [08 드라이버](08_Motor_Driver_and_HBridge_Control_ko.md), [09 UART](09_STM32_ESP32_UART_Interface_Contract_ko.md), [16 상태·제어](16_Control_Loop_and_State_Machine_ko.md), [27 명령 변환](27_Production_Open_Loop_Command_Mapper_ko.md) | 현재 구현 계약과 향후 확장 모델을 구분 |
| 무선 제어 다음 구현 | [ARM/CMD 초기 계약](../docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md), [모듈 역할](../03_Firmware/README.md#armcmd-모듈과-실행-경로) | 기초 모듈 검사와 미연결인 제어 실행 경로, AC-H/B/S 조건을 구분 |
| 향후 확장 | [10 로드맵](10_System_Architecture_Roadmap_CAN_RTOS_LL_ko.md), [13 FreeRTOS](13_FreeRTOS_Task_Architecture_ko.md), [14 CAN](14_CAN_Bus_Integration_Plan_ko.md), [15 LL](15_HAL_to_LL_Driver_Migration_Strategy_ko.md), [17 주행·오도메트리](17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md) | 목표·진입 조건이며 구현 완료 목록이 아님 |
| 전원·고장·선택 이유 | [12 전원](12_Power_Distribution_and_Safety_Architecture_ko.md), [18 고장 정책](18_Fault_Model_and_Safety_Cases_ko.md), [19 ADR](19_Architecture_Decision_Record_ko.md), [20 드라이버 비교](20_Motor_Driver_Selection_Comparison_ko.md) | 정책과 구현 여부, 당시 선택 이력을 구분 |
| 물리 비상정지 | [21 구조](21_Physical_EStop_Architecture_ko.md), [22 위험 분석](22_Physical_EStop_Hazard_Analysis_ko.md), [23 FMEA](23_Physical_EStop_FMEA_ko.md), [24 요구사항](24_Physical_EStop_Safety_Requirements_ko.md), [25 회로](25_Physical_EStop_RevB_Circuit_Architecture_ko.md), [26 부품](26_Physical_EStop_Component_and_Rating_Selection_ko.md) | 각 Step 종료 기록은 당시 상태. 최신 시험 범위는 아래 근거와 대조 |

## 근거와 문서별 역할

- **설계 계약:** 이 폴더의 한국어 문서. 역할·인터페이스·안전 정책·CAN 프레임 등 변경 시 해당 본문을 갱신한다.
- **현재 판정:** [최종 검증 매트릭스](../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md). 이 안내의 요약과 충돌하면 시험 범위·기준 시점을 먼저 대조한다.
- **실제 관측:** [25 전원·감지](../docs/verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md), [26 T004](../docs/verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md), [27 T005A](../docs/verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md), [28 엔코더 조정부](../docs/verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md), [29 좌우 정정](../docs/verification/29_Vehicle_Side_Mapping_Correction_and_Hand_Rotation_Check_2026-09-26_ko.md), [30 전력단·엔코더](../docs/verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md), [31 단일 모터](../docs/verification/31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md).
- **다음 작업과 완료 조건:** [전체 실행 계획](../docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md). 이미 완료한 기능 검사를 옛 문서의 ‘다음 단계’만 보고 반복하지 않는다.
- **후속 완료 범위:** [32 단일 모터 DISARM/S0·3초 구동](../docs/verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md), [33 W4](../docs/verification/33_W4_STM_UART_WebSocket_and_Startup_Status_2026-10-08_ko.md), [34 W5](../docs/verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md), [10/11 모듈·빌드 기록](../docs/progress/2026-10-11_progress.md). 실제 모터·비구동 통신·PC 검사·사용자 빌드의 증거 범위를 합치지 않는다.
- **재개 연결·이미지:** [현재 인수인계](../docs/handoff/CURRENT_SESSION_CONTEXT.md). `PROJECT_MEMORY`는 안정적인 사실과 요약을 보조하며 이 폴더의 설계 계약을 폐기하지 않는다.
- **미확정 배치 제안:** [2층 확장·층간 연결](../09_Electrical_Design/13_Two_Deck_Perfboard_Expansion_Feasibility_2026-09-30_ko.md). 제안 단계이며 현행 VRT나 실장 완료 상태를 바꾸지 않는다.

## 갱신 원칙

1. 현재 설계나 구현이 바뀌면 관련 본문의 상태·표·다음 행동도 함께 수정한다. 앞에 최신 문단만 추가하고 뒤의 현재형 오류를 남기지 않는다.
2. 시험 당시 수치·로그·해시·검사 개수는 날짜가 있는 이력으로 보존한다. 새 결과를 과거 시험에 소급 적용하지 않는다.
3. `선정`, `배선 완료`, `설정 완료`, `제한 조건 검증`, `전체 수용`을 구분한다. 모터가 회전했다는 사실만으로 전체 선행 Gate를 PASS로 바꾸지 않는다.
4. 영문은 대응 한국어 정본과 이 안내로 연결한다. 영문 본문의 과거 checkpoint는 해당 날짜의 기록이며 현재 배선 지시로 사용하지 않는다.
5. ADR·Hazard/FMEA의 과거 근거는 유지하고 변경 결정·조치 결과를 덧붙인다. 제안 중인 확장안을 Accepted 또는 실장 완료로 기록하지 않는다.
