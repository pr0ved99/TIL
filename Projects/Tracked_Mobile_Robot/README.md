# Tracked Mobile Robot

STM32와 ESP32-S3를 기반으로 **궤도형 모바일 로봇의 하위 구동 플랫폼**을 개발하는 프로젝트다.
UART 명령 처리, PWM/DIR 출력, 엔코더 피드백과 물리 비상정지 회로를 단계적으로 구현·검증한다.
목표는 저속 주행과 정지 동작을 검증하고, 이후 ROS 2 기반 상위 시스템으로 확장하는 것이다.

- **담당:** 이영현 (`pr0ved99`) — 요구사항·인터페이스 설계, STM32/ESP32 펌웨어 구현,
  전장·기구 배치, 배선·납땜, 보드 빌드·플래시와 실측 검증.
- **작업 방식:** 설계·코드 검토와 로그 해석에 Codex를 활용하며, Python 검증 코드와 문서 정리에 지원을 받는다.
- **최근 거리 결과 · 2026-10-23:** 지상1m 실제/추정 거리와 오차 기록 완료. run03/04 사용자 실측1002mm에 대해 엔코더 평균1002.640333/1000.953333mm, 오차+0.640333/−1.046667mm다. ARM/종료 ACK와 정지 TEL·count가 보존됐고 drop/err0이다. `MVP-011 / REQ-ODO-001 / T-ODO-001`은 기록 범위 PASS이며 정밀도·직진성 보증은 아니다. [원본·판정·한계](docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#2026-10-23-지상-1m-결과와-잔여-인수-대조), [진행 기록](docs/progress/2026-10-23_progress.md).
- **현재 범위:** 기본 무선 주행/정지·엔코더 거리 비교의 선택 기능 근거를 확보했다. 전체 MUST 인수는 미완료이며 기존 PARTIAL/OPEN을 검증표에 남긴다.10/23 사용자 결정으로 외부 온도는 후속 DEFERRED / NOT_RUN, 정량 전류·ADC·자동 저전압·IMU/PID/STM 스케줄링/CAN/ROS2도 후속이다. ESP는 이미 FreeRTOS 태스크·큐를 사용한다. 기존 출력·정지·셀 알람 운영은 유지한다.
- **기준 설정:** 초기 공통k=1687/19500mm/count, 일반 cap150‰·회전200‰, 왼쪽 gain전진960‰/후진930‰. 지상 비교 후 계수나 출력을 바꾸지 않았다. 현재 ESP 앱은 `esp32_wifi_link`이며 두 MCU의 코드 입력·빌드/플래시와 실물 조작은 사용자가 수행한다.
- **계측 준비:** 103JT-025×2·Pololu#5241×2·GM1312·UT210E 구매/배송 대기, Vishay100nF10개 구매·수령 미확인이라는 마지막 보고를 유지한다. 장비 수령을 거리/MVP 선행으로 요구하지 않는다. [후속 모니터링 계획](docs/plans/2026-10-22_Motor_Current_Temperature_Monitoring_and_Procurement_ko.md).
- **학습 자료:** [STM32·ESP32 펌웨어 교과서](07_Embedded_Learning_Notes/06_STM32_ESP32_Firmware_Textbook/README.md) — 기초 C부터 현재 구현까지, 예제 5개와 12개 학습 단위.
- **모니터링 실습 · 10/29 마감:** 전류 RC AC/TRAN·NTC25/50°C 상당 OP/AC·전압 분압12.6/16V OP와 AC의 사용자 GUI 실습 및 PNG/CSV 저장을 완료했다. 전압 fc404.942Hz·저주파−15.7157dB·차단점−18.7260dB, NTC VDD(CN7-5) 공급 기본안은 실제 쉴드 미반영이다. [학습 노트20](07_Embedded_Learning_Notes/01_Concept_Notes/20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md) · [설계 판단24](09_Electrical_Design/24_Monitoring_Input_Simulation_and_Design_Review_2026-10-28_ko.md) · [진행 기록](docs/progress/2026-10-29_progress.md). 다음은전압오차예산·보호조건,실물/전체MVP완료아님.
- **이전 모니터링 설계 · 10/28 첫 마감:** [전류 검증 명세](09_Electrical_Design/22_Current_Channel_Verification_Spec_2026-10-27_ko.md)·[온도 검증 명세](09_Electrical_Design/23_Temperature_Channel_Verification_Spec_2026-10-27_ko.md)에 시험용 오차 배분·보정/독립점·장비 경계·절차를 정했다. 센서 단독/입력계/전체계 범위를 구분하며 실물 NOT_RUN이다. 다음은 전원/보호 미결과 전압2채널 설계. [마감 기록](docs/progress/2026-10-28_progress.md), [학습 목차](07_Embedded_Learning_Notes/01_Concept_Notes/README.md). AI 후속안은 문서화만 완료했다.

**통합 시연 완성 · 2026-10-24:** [2분29초 MP4](assets/videos/wifi_mvp/2026-10-24/final/TMR_MVP_Final_2026-10-24.mp4)는 기존65초 탁상 편집본과 카펫 주행·S0/래치/ARM 차단·S2·STM 리셋·재주행을 연결한다.1080p30·무음, 전체4470프레임 디코딩 오류0·21개 표본 검토·원본 해시 보존. [편집 근거와 한계](assets/logs/wifi_link/2026-10-24_carpet_s0_demo_run01/README.md). 사용자 동기 지적을 반영해 카펫 화면을 기존 대비1.2667초 상대 지연했다(화면=카메라−0.7667초). 원본9구간18전이·출력5구간10전이를 대조한 편집 정렬이며 정지 지연/거리 정확도 계측이 아니다. 영상 제작 완료와 전체 MUST 인수 미완료를 구분한다.

**브라우저 적용:** PAGE 요약판·십자 조작·DISARM·지연 표시의 PC105검사와 Chrome4너비 검증을 완료했다. 사용자 ESP 플래시 성공·새 UI 정상·배터리 단독 확인 및 제출 영상은 [판독](assets/logs/wifi_link/2026-10-24_demo_run01/README.md)에 기록했다. 보드 이미지 readback과 새 UI 처리 비용 계측은 미확인이다.

**관측·운용:** [v5.2 세 조건 분석](assets/logs/wifi_link/2026-10-24_handler_timing_air_forward_run01/README.md), [운용 절차](docs/handoff/CURRENT_MVP_OPERATION_RUNBOOK_ko.md), [잔여 인수 대조41](docs/verification/41_MVP_Acceptance_Disposition_2026-10-24_ko.md)을 보존한다. 과거 통신/UI 원인은OPEN, T005A PARTIAL/T007 BLOCKED를 유지하며 완료 시험·제외 조사를 자동 반복하지 않는다.

**바로 보기:** [STM32 펌웨어](03_Firmware/stm32_uart_mvp/Core/Src/) ·
[현재 ESP Wi-Fi 앱](03_Firmware/esp32_wifi_link/main/wifi_link_main.c) · [운용·재현 절차](docs/handoff/CURRENT_MVP_OPERATION_RUNBOOK_ko.md) ·
[Python 검증 코드](03_Firmware/tests/) · [대표 계측 보고서](docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md) ·
[완료 범위와 근거](docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md) · [전체 실행 계획](docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md)

## 1. 프로젝트 목표와 범위

첫 MVP는 UART 명령으로 전진·후진·제자리 회전하는 저속 궤도형 플랫폼이다.
명령 유실과 비상정지 상황에서 출력을 차단하고, 엔코더 기반 속도·거리 추정 결과를 실제 움직임과 비교한다.

| 첫 MVP에 포함 | 완료 판단 기준 |
| --- | --- |
| 좌우 구동과 엔코더 | 두 모터 제어, 방향·속도 추정, 전동 구동 중 신호 검증 |
| 명령 처리와 정지 | timeout 뒤 출력·저장 명령 초기화, 명시적인 재허가와 새 명령으로만 복구 |
| 전원과 물리 비상정지 | 모터 에너지 차단, 해제만으로 자동 재시작하지 않는 동작, 첫 주행 전 저전압 경고·정지 기준 검증 |
| 기구 통합과 주행 | 제작 플레이트 장착, 저속 주행, 1 m 직진의 실제·엔코더 거리 오차 기록 |

완료 여부는 [MVP 요구사항·검증 매트릭스](docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)에서 추적한다.

## 2. 하드웨어와 시스템 구조

<img src="assets/photos/perfboard/2026-08-14_04_perfboard_component_side_modules_installed_scale_grid_top.jpg" alt="2026년 8월 14일 만능기판 위 NUCLEO-F446RE, BNO085, ESP32-S3 모듈 배치" width="640">

*2026-08-14 모듈 배치 확인 단계. 당시 NUCLEO·BNO085·ESP32-S3의 위치를 보여준다.
9월의 비상정지·측정 헤더 배선 개정 전 사진이며, IMU 동작 검증을 의미하지 않는다.*

아래는 시스템의 핵심 연결 관계다. 실선은 명령·감지·피드백, 점선은 전력·모터 구동 경로다.
연결 여부와 검증 완료 여부를 구분하기 위해, 남은 검증 범위를 각 경로에 표시했다.

```mermaid
flowchart LR
    ESP["ESP32-S3<br/>UART 명령 전달 · 상태 수신"] <-->|UART| STM["STM32 NUCLEO-F446RE<br/>명령 검증 · 출력 허용 판단"]
    ESP <-->|Wi-Fi / WebSocket · 상태와 ARM/CMD/DISARM| WEB["브라우저<br/>방향 입력·놓음 정지·지상 주행 확인"]
    STM -->|PWM / DIR| DRIVER["MDD10A<br/>2채널 모터 드라이버"]
    DRIVER -.->|일반15%·회전20% 저속 주행 확인| MOTOR["좌우 궤도 모터"]
    MOTOR -->|축 회전 피드백| ENC["엔코더<br/>신호 조정 회로"]
    ENC -->|A/B 펄스| STM
    BAT["3S LiPo · 퓨즈 · 메인 스위치"] -.-> STOP["물리 비상정지 회로<br/>모터 전원 차단"]
    STOP -.->|전력단 연결·관측 완료 · 전체 수용 미완료| DRIVER
    STOP -->|감지·펌웨어/PWM 결합 PASS| STM
```

### 핵심 설계 판단

| 판단 | 이유와 구현 방향 |
| --- | --- |
| **최종 출력 허용 판단은 STM32가 담당** | 외부 명령이 들어와도 명령 유효성, 제어 상태, timeout과 비상정지 조건을 STM32에서 확인한 뒤 출력한다. ESP32는 명령 전달과 상태 수신을 맡는다. |
| **명령 유실 뒤 이전 주행 명령을 자동 복원하지 않음** | 통신 복구만으로 예기치 않게 다시 움직이지 않도록 출력과 저장 명령을 0으로 만들고 `DISARMED`로 전환한다. 새 `ARM`과 유효한 `CMD`를 모두 받아야 출력할 수 있다. |
| **물리 전원 차단과 펌웨어 상태 감지를 함께 사용** | MCU 소프트웨어와 독립된 모터 에너지 차단 경로를 두고, STM32도 비상정지 상태를 감지·유지해 재허가 조건을 검사한다. 두 경로를 결합한 전체 검증은 진행 중이다. |

세부 계약: [UART 인터페이스](01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md) ·
[상태 머신](01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md) ·
[물리 비상정지 설계](01_System_Architecture/21_Physical_EStop_Architecture_ko.md)

## 3. 대표 구현과 검증 성과

각 결과는 아래에 명시한 시험 조건의 결과다. 코드 검사, 로직 핀 계측, 실제 모터 정지를 구분한다.

| 대표 결과 | 확인한 내용 | 시험 범위·근거 |
| --- | --- | --- |
| 실제 UART↔무선 상태·비구동 명령 | **W4 상태 전달·W5 PING/DISARM PASS**: 요청자별 결과·입력 거부·timeout/복구·재접속 후 자동 재전송 없음 | [두 보드 USB·LiPo 미연결](docs/verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md). 당시 STM TEL/WS100ms·stale500ms; 현재 WS50ms·STA 절전 해제. PC JS57·C21은 별도 검사. nonzero 명령·모터 분리 검증은 보고서38 참조 |
| DISARM → PWM 차단 | **23.50 μs** | [STM32 로직 핀 계측](docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md). 실제 모터 정지 시간이 아님 |
| 영구 배선의 PWM/DIR | **19.049 / 19.058 kHz**, 약 **10%**, 방향 전환 전후 약 **2 ms PWM 0** | [모터 분리 MDD10A 입력](docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md) |
| 명령 유실과 복구 | **500 ms timeout** 후 출력·저장 명령 0, 새 ARM+CMD에서만 복구 | [모터·LiPo 분리 UART/제어 신호](docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md) |
| 엔코더 환산 | **1,560 counts/rev**, 610개 채널 샘플의 mRPM 환산 불일치 **0건** | [손회전 보정·계산 검증](assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md). 절대 속도·주행 거리 검증은 별도 |
| 실제 모터 방향 보정 | B/M2 **±10%·300 ms** 단발 명령에서 실제 양방향 회전·CPS 부호·정지 확인 | [섀시 분리 단일 모터](docs/verification/31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md). A 실제 전진도9/30 확인. 10/18 궤도 지상 주행은 별도 최신 근거로 추가; 전체 안전 수용은 별도 |
| 지상1m 거리 기록 | 실측1002mm 두 회차, 평균 추정1002.640333/1000.953333mm | [run03/04 비교](assets/logs/wifi_link/2026-10-23_ground_1m_run04/repeat_comparison.json). 실측 불확도 미제공, sub-mm 정확도/직진성 보증 아님 |
| 수동 DISARM 관찰 | 클릭→방향 비활성→DISARM OK→IDLE/정지 TEL | [정지 상태 회차](assets/logs/wifi_link/2026-10-23_disarm_stationary_run01/observations.json), [지상run04](assets/logs/wifi_link/2026-10-23_ground_1m_run04/observations.json). 이전run02 간헐 UI 원인은 미해결 |

<details>
<summary>각 결과의 검증 문제·방법·관측 한계 펼치기</summary>

### 3.1 DISARM 명령에 따른 PWM 출력 차단

- **검증 문제:** 상태 로그만으로 알기 어려운 실제 PWM 차단 시점을 확인한다.
- **방법:** 유효한 `DISARM` 프레임 수신 완료와 두 PWM의 마지막 active edge를 같은 4 MHz 로직 캡처에서 비교했다.
- **결과:** 두 PWM 출력이 비활성화되기까지 **23.50 μs**를 측정했다.
- **범위:** STM32 MCU 로직 핀 계측 결과다. 실제 모터 정지 시간은 측정하지 않았으며,
  당시 전원·모터 분리 상태의 증거 보완은 보고서에 남아 있다.

[시험 조건·파형·원본 캡처](docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)

### 3.2 영구 배선을 통한 PWM/DIR 전달

- **검증 문제:** 만능기판의 pull-down과 하네스를 거쳐도 제어 신호가 드라이버 입력에 전달되는지 확인한다.
- **방법:** 모터를 분리하고 MDD10A 입력에서 두 채널의 PWM과 방향 전환 구간을 계측했다.
- **결과:** PWM **19.049 / 19.058 kHz**, 약 **10% 듀티**, DIR 전환 전후 약 **2 ms의 PWM 0 구간**을 확인했다.
  시험 설정 복구 후 5초 동안 모든 제어 신호가 LOW인 상태도 확인했다.
- **범위:** 이 시험은 MDD10A 로직 입력까지의 결과다. 이후 실제 회전·방향 관측은 아래 3.5에서 구분해 기록한다.

[시험 보고서와 원본 자료](docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md)

### 3.3 명령 유실 후 정지와 명시적 복구

- **검증 문제:** 명령이 끊긴 뒤 과거 명령이나 `ARM`만으로 출력이 되살아나는 것을 막는다.
- **방법:** 모터·LiPo 분리 조건에서 `timeout_ms=500`인 명령을 사용하고 UART와 PWM/DIR을 같은 캡처로 비교했다.
- **결과:** timeout 뒤 출력·저장 명령 0과 `DISARMED` 전환, `CMD` 단독 거부,
  `ARM`만으로 이전 출력이 복원되지 않음, **새 `ARM` + 새 `CMD`에 의한 복구**를 확인했다.
- **범위:** 보드의 UART·제어 신호·상태 복구 검증이며, 실제 모터나 물리 비상정지 시험은 포함하지 않는다.

[500 ms timeout·복구 시험](docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md)

### 3.4 수동 회전 기반 엔코더 환산 검증

- **검증 문제:** 모터 출력축 회전량과 펌웨어의 카운트·속도 환산을 연결한다.
- **방법:** 두 모터의 출력축을 방향별 50회전시킨 관찰 기록과 별도의 수동 회전 로그를 사용했다.
- **결과:** 출력축 기준 **1,560 counts/rev**로 보정했다.
  별도 로그의 **610개 채널 샘플**에서 카운트/초(CPS) → 0.001 rpm 단위(mRPM) 환산 불일치는 0건이었다.
- **범위:** 수동 회전 기반 기능 검증이다. 전동 구동 중 노이즈, 외부 회전계 비교와 실제 주행 거리 검증은 남아 있다.

[50회전 관찰 기록·환산 검증·로그](assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md)

### 3.5 실제 단일 모터 구동과 방향 보정

- **검증 문제:** 명령 부호와 실제 모터 방향·엔코더 피드백이 일치하는지 확인한다.
- **방법·결과:** 보정 전 B/M2의 양수 명령에서 실제 역회전과 음수 CPS가 함께 관측됐다.
  두 모터를 교차 연결해 회전을 확인한 뒤, 손회전으로 확인한 엔코더 부호를 유지하고 오른쪽 DIR을 HIGH=전진/LOW=후진으로 보정했다.
  B/M2는 정방향·역방향 각각 **10%·300 ms 단발 명령**에서 회전·CPS 부호·timeout 후 0 복귀를 로그와 육안으로 확인했다.
- **범위:** 섀시 분리 단일 모터 시험이다. A/M1 양수 실제 전진은9/30 추가 확인했으며 부하·주행 검증은 남아 있다.

[시험 결과·관측 한계·원본 로그](docs/verification/31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md)

</details>

## 4. 현재 검증 범위와 남은 작업

**상태 대조: 2026-10-24.** 선택 기능/거리 기록의 완료와 전체 전력단·비상정지 인수를 구분한다. [최신 잔여 대조](docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#현재-완료-범위와-남은-판단)가 현재 판정의 정본이다.

| 분야 | 확인된 범위 | 남은 경계 |
| --- | --- | --- |
| 통신·펌웨어 | Wi-Fi ARM/CMD/DISARM·선택 AC-S/nonzero,10/20 UART 명령선 단절/timeout 실제 정지·수동 복구 | 전체 UART release PARTIAL. run02 DISARM/UI 간헐 현상 원인 OPEN; 후속 정상 회차와 구분 |
| 보드 전원·운영 | 실제 STM/ESP 공급·USB/standalone 분리 규칙·BX100 설정/표시·과거 주행 중 저전압 경고음→작업자 전원 차단 USER-REPORTED PASS | 감독하 경고 대응 운영 범위 완료. 최종 정격/부하 미수용, 기존 제외 조사 재개 없음 |
| 구동·거리 | 지상 네 방향/놓음/DISARM,10/23 1m 실제/추정·오차 기록 PASS | 계수 지상 보정·정밀 속도/직진성·슬립·장시간/정격 수용 아님. 전류/온도는 후속 |
| 물리 비상정지 | T004 감지/latch/reset/PWM PASS, 전력단 일부·A 구동 S0 관측 | 전체 T005A PARTIAL·정식 T-ESTOP-007 BLOCKED. 기존 사용자 제외와 정식 전체 안전 수용 사이 OPEN 경계 보존 |
| 엔코더·기구 | 입력 전압·손회전/구동 count·정지, 장착/간격/배선 접근 사용자 확인 | 파형/출력형식/노이즈·전체 제작 identity/치수 미기록을 오늘 거리 결과로 소급 통과시키지 않음 |

추가 근거: [보드 전원](docs/verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md) ·
[T004 감지·PWM](docs/verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md) ·
[T005A 전력단 관측](docs/verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md) ·
[실제 엔코더·전력단](docs/verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md).

다음 작업은 잔여 운영 근거와 기존 제외 범위의 최종 인수 처리, 공개할 증거 묶음 정리다. 완료한 거리/단절·복구·공중5/10/15cm를 자동 반복하지 않으며20cm는 사용자 요청으로 미실시다. 전체 MVP 완료나 Git/외부 앱 게시 완료를 의미하지 않는다.

작업 순서·완료 조건은 [전체 실행 계획](docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md),
현재 전원·배선·시험 이미지와 재개 절차는 [현재 작업 현황](docs/handoff/CURRENT_SESSION_CONTEXT.md),
일자별 결과는 [진행 기록](docs/progress/README.md)에서 관리한다.
### 저장된 지상1m 결과 재현

[run03](assets/logs/wifi_link/2026-10-23_ground_1m_run03/), [run04](assets/logs/wifi_link/2026-10-23_ground_1m_run04/)의 `browser_report.json`은 원본, `source_manifest.json`은 출처/해시, `observations.json`은 사용자 실측·해석, `encoder_analysis.json`은 계산 결과다. 저장소 루트에서 아래 명령으로 새 출력 파일에 계산을 재현할 수 있다. 보드 연결/송신·빌드/플래시를 수행하지 않는다.

```powershell
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/analyze_encoder_distance.py Projects/Tracked_Mobile_Robot/assets/logs/wifi_link/2026-10-23_ground_1m_run04/browser_report.json --output ground_run04_recheck.json --actual-distance-mm 1002 --boot-id 1339414435 --arm-seq 2670355801 --measurement-note "10/23 사용자 보고1002mm; 측정 불확도 미제공"
```

기대 결과는 유효 구간1개·거부0개, 평균1000.953333mm·부호 있는 오차−1.046667mm다. 분석 성공은 실측 정확도 보증이나 전체 MVP 자동 PASS가 아니다. run02의 누락 구간은 같은 정책에서 거부된 원본 그대로 보존한다. [측정 방법/해석 양식](docs/plans/templates/distance_1m_session_template_ko.md)과 [관찰기 PC검사](assets/logs/wifi_link/2026-10-23_ground_distance_preparation/observer_reconnect_check.json)를 함께 볼 수 있다. 새 시연 영상은 이번 기록에 추가하지 않았다.

## 5. 코드와 문서 안내

### 구현 코드

| 살펴볼 내용 | 진입점 |
| --- | --- |
| STM32 초기화·주기 처리 | [main.c](03_Firmware/stm32_uart_mvp/Core/Src/main.c) · [CubeMX 설정](03_Firmware/stm32_uart_mvp/stm32_uart_mvp.ioc) |
| 명령 검증·상태 전이·timeout | [UART 프로토콜](03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c) |
| 좌우 명령 변환·출력·엔코더 | [명령 변환](03_Firmware/stm32_uart_mvp/Core/Src/drive_command_mapper.c) · [PWM/DIR](03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c) · [엔코더](03_Firmware/stm32_uart_mvp/Core/Src/encoder_speed.c) |
| ESP32 UART 브리지 | [프로젝트 안내](03_Firmware/esp32_uart_bridge/README.md) · [구현 코드](03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c) |
| 현재 ESP Wi-Fi 앱 | [프로젝트 안내](03_Firmware/esp32_wifi_link/README.md) · [구현 코드](03_Firmware/esp32_wifi_link/main/wifi_link_main.c) |
| ARM/CMD 독립 기초 모듈 | [역할·구현 상태](03_Firmware/README.md#armcmd-모듈과-실행-경로) · [초기 계약](docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md) |
| PC 검사 | [검증 코드](03_Firmware/tests/) · [종류·선택·실행 방법](03_Firmware/tests/README.md#검사-종류와-선택) |

PC 검사는 정적 소스/참조 모델, 실제 C 함수·모듈 실행, PAGE JavaScript 모의 실행으로 구분한다. 보드 빌드·실행이나 전기적 계측을 대신하지 않는다.
현재 검사 범위와 별도 UART bridge의 과거 hook 기록은 [검사 안내](03_Firmware/tests/README.md#검사-종류와-선택)를 확인한다.
시험용 설정과 빌드·실행 전제는 [현재 현황](docs/handoff/CURRENT_SESSION_CONTEXT.md)과 해당 런북을 따른다.

### 빌드·검사 시작점

- **STM32:** STM32CubeIDE에서 [stm32_uart_mvp 프로젝트](03_Firmware/stm32_uart_mvp/)를 가져와 빌드한다. `.project`와 `.ioc`를 포함한다.
- **ESP32 현재 Wi-Fi 앱:** ESP-IDF 환경에서 [esp32_wifi_link 빌드 안내](03_Firmware/esp32_wifi_link/README.md#빌드검사)를 따른다. 별도 [UART bridge 빌드 안내](03_Firmware/esp32_uart_bridge/README.md#build)와 프로젝트 폴더를 혼동하지 않는다. 포트 번호는 연결한 PC에서 확인한다.
- **호스트 검사:** 보드 연결 없이 [검사 종류와 선택](03_Firmware/tests/README.md#검사-종류와-선택)을 먼저 읽고 해당 Python/C 또는 Node.js 검사를 실행한다. 빌드·계측 결과와 구분한다.
- **시험 기록:** [증거 보존 절차](docs/verification/EVIDENCE_CAPTURE_GUIDE_ko.md)에 따라 원본 로그·화면·빌드/플래시 식별값과 관측 범위를 연결한다.

펌웨어 앱별 역할·빌드 폴더·마지막 실행과 새 모듈 준비 상태는 [펌웨어 목차](03_Firmware/README.md)를 따른다.
별도 UART bridge 진입 파일은 `uart_bridge_main.c`로 이름을 바꿨다. 이름 변경 후 해당 앱의 보드 빌드는 아직 확인하지 않았으며 Wi-Fi 앱 빌드 성공과 구분한다.

### 설계·검증·학습 자료

| 읽는 목적 | 문서 |
| --- | --- |
| 전체 구조와 설계 결정 | [시스템 인터페이스 맵](01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md) · [설계 결정 기록](01_System_Architecture/19_Architecture_Decision_Record_ko.md) |
| 전기·기구 설계 확인 | [VeroRoute](09_Electrical_Design/VeroRoute/README.md) · [KiCad](09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevB/README.md) · [기구 설계](08_Mechanical_Design/README.md) |
| 요구사항과 근거 추적 | [검증 문서](docs/verification/README.md) · [하드웨어 검증 절차](02_Hardware_Validation/README.md) |
| PC 시험 도구와 초기 UART MVP | [PC Serial 도구](04_PC_Serial_Control/README.md) · [Web Serial 대시보드](04_PC_Serial_Control/web_serial_dashboard/README.md) |
| 학습 과정과 전체 자료 탐색 | [임베디드 학습 노트](07_Embedded_Learning_Notes/README.md) · [분야별 전체 문서 색인](docs/README.md) |

PC–STM32 직접 연결 대시보드는 초기 UART MVP의 시험 도구다.
현재 MVP의 외부 명령 경로는 ESP32 → STM32이며, STM32 USART2는 벤치 진단용으로 구분한다.

## 6. MVP 이후 확장 계획

| 확장 | 목적 |
| --- | --- |
| IMU | 센서 통신·자세 데이터 검증과 엔코더 정보 결합. 현재 헤더 배치·GND 검토와 구분해 진행 |
| CAN | UART로 확인한 명령·상태 계약을 CAN 인터페이스로 확장 |
| STM32 FreeRTOS | 검증된 STM32 bare-metal 동작을 태스크·주기·큐 구조로 옮기고 동작 유지 확인. ESP-IDF의 기존 FreeRTOS 환경과 구분 |
| 선택적 LL 전환 | 계측으로 필요성이 확인된 타이밍 경로의 구현과 성능 비교 |
| ROS 2 · LiDAR · SLAM/Nav2 | 하위 구동 플랫폼과 상위 명령·상태 연결 후 자율주행으로 확장 |

단계별 범위와 완료 기준은 [프로젝트 마스터 플랜](docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md)을 따른다.
