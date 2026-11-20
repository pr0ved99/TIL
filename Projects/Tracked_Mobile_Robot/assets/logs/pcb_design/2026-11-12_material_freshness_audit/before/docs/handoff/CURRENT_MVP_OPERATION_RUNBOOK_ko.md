# 현재 MVP 운용·재현 절차

기준일: **2026-10-24** · `TK-MVP-05-03/04` 문서 산출물. 기본 무선 주행·정지·거리 기록을 확인한 현재 구성의 설명서다. 전체 MVP 인수나 새 실물 시험 완료 선언은 아니다. 이 문서 작성으로 로봇을 조작하지 않았다.

판정 정본은 [요구사항·검증표](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md), 최신 시연은 [149초 통합본·S0 복구 관측](../../assets/logs/wifi_link/2026-10-24_carpet_s0_demo_run01/README.md), UI 변경 전 원시 통신 계측은 [v5.2 전진·3조건 비교](../../assets/logs/wifi_link/2026-10-24_handler_timing_air_forward_run01/README.md)다. 영상의 S2→리셋 순서는 시연 관측이며 아래 표준 복구 절차를 대체하지 않는다. 아래 운용 순서는 다음에 실제 사용할 때 참고하며, 완료한 관측을 다시 수행하라는 목록이 아니다.

## 1. 현재 구성과 연결

| 구분 | 현재 기준 | 근거 |
| --- | --- | --- |
| 제어기 | NUCLEO-F446RE가 최종 출력·timeout·엔코더 처리, ESP32-S3 DevKitC가 Wi-Fi/UART 전달 | [STM 프로토콜](../../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c), [현재 ESP 앱](../../03_Firmware/esp32_wifi_link/main/wifi_link_main.c) |
| 구동 | MDD10A, MG540P30_12V, A=왼쪽/M1, B=오른쪽/M2 | [배터리 단독·지상 주행 기록](../progress/2026-10-18_progress.md) |
| UART | STM PA9 TX → ESP GPIO18 RX, ESP GPIO17 TX → STM PA10 RX, 공통 GND, 115200/8N1 | [ESP 연결 계약](../../03_Firmware/esp32_wifi_link/README.md#데이터-흐름과-조건) |
| PWM/DIR | 왼쪽 PB6 TIM4_CH1 / PC8, 오른쪽 PB7 TIM4_CH2 / PC9 | [main.h](../../03_Firmware/stm32_uart_mvp/Core/Inc/main.h), [핀 배정](../../01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md) |
| 엔코더 | JENC1 → PB4/PB5 TIM3, 부호 반전. JENC2 → PA0/PA1 TIM5, 정상 부호. 기존 신호 조정부 경유 | [엔코더 구현](../../03_Firmware/stm32_uart_mvp/Core/Src/encoder_speed.c), [기존 입력 검사](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md) |
| 물리 정지 | S0/K2/K1 전력 경로와 PC7 감지·STM 래치는 별도 경로. S2는 모터 전원 수동 재인가 | [RevB 회로 계약](../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md) |
| 기구·거리 | 양 궤도 한 링크씩 단축한 구성. 사용자 최종 중량3.25kg, 중심 간격 약233mm. 초기 k=1687/19500mm/count | [10/18 구성](../progress/2026-10-18_progress.md), [거리 기록/한계](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#2026-10-23-지상-1m-결과와-잔여-인수-대조) |

배선/커넥터를 새로 조립할 때는 위 신호표만으로 핀 순서를 추측하지 않고 연결된 도면과 기존 하네스 표시를 대조한다. IMU는 기존 만능기판에 배치돼 있으나 현재 주행 제어에 사용하지 않는다. CAN·확장 PCB·전류/온도/전압 ADC도 현재 실행 구성에 포함하지 않는다.

### 전원 기준

```text
3S LiPo + → F1 → S1 → +busbar
                       ├→ K1 30→87 → MDD10A B+
                       ├→ XL4015 #1 → STM/ESP 보드용 5V 2P 두 개
                       ├→ XL4015 #2 → AUX5V (엔코더·S0-B 감지)
                       └→ F2 → S0/S2/K2/K1 제어
LiPo − → GND busbar → MDD B− / 두 buck / 공통 신호 GND
```

- 현재 무선 운용 기준은 **배터리 단독, 보드용 2P 연결, STM JP5=E5V, 두 보드 USB 전원 분리**다. 10/18 복원 보고와 이후 운용 기록을 따른다.
- 과거 USB 벤치는 #1 보드용 2P 두 개를 분리·절연한 별도 구성이다. USB 모드 전환·플래시는 현재 전원 구성을 그대로 둔 채 USB를 추가하는 절차가 아니다. 변경 시 해당 보드 전원 절차를 별도로 확인한다.
- K1은 모터 경로만 끊으므로 S0를 눌러도 #1/#2와 보드가 살아 있을 수 있다. S2와 브라우저 ARM도 서로 다른 허가다. #1/#2 OUT+는 서로 연결하지 않는다.
- 이전 전원 조정 후 보드 연결5.02V는 사용자 보고값이다. 이번10/24 공급 전압·순간 강하·3.3V·정확한 CC 설정을 측정한 값이 아니다. [전원 비교 기록](../../assets/logs/wifi_link/2026-10-23_power_adjusted_drive_run01/comparison_ko.md).
- BX100 셀 알람과 작업자 감독·경고 시 수동 종료를 사용한다. 현재 `batt_mv=null`, `battery_available=false`는 정상적인 미구현 표시이며 자동 저전압 차단은 없다. [알람 판정](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#2026-10-23-리포-알람-경고음-확인-추가).

## 2. 펌웨어·설정 기준점

**10/24 후속 사용자 적용 확인:** ESP 플래시 성공·새 UI ARM0→DISARM 정상·두 USB 분리/배터리 단독을 보고했다. [새 화면·실물 영상 표본](../../assets/logs/wifi_link/2026-10-24_demo_run01/README.md)을 확인했다. 로컬 빌드 로그/보드 해시 readback은 아직 없으며 아래 “사용자 적용 대기”는 당시 이력이다. 기존 제한/STM 코드를 바꿨다는 보고는 없다.

**10/24 UI 수정 후 현재:** [브라우저 보완](../../assets/logs/wifi_link/2026-10-24_browser_dashboard_review/README.md)으로 로컬 ESP main의 PAGE가 변경됐다. PC105검사와 Chrome 배치 검증만 완료했고 사용자 빌드/플래시·보드 적용은 아직이다. 아래 해시 일치는 UI 수정 전 기록이며 현재 main/보드 이미지가 같다는 뜻이 아니다. 기존 제어 로직/제한과 STM 소스는 유지했다.

**10/24 UI 수정 전 로컬 대조: 10/22 manifest의 소스13개·빌드 산출물6개가 모두 SHA-256 일치.** [이번 manifest](../../assets/logs/wifi_link/2026-10-24_mvp_operation_documentation/baseline_manifest.json)는 비교 기준, 실제 파일 해시, 추가 참조 파일을 구분한다. 이 결과는 로컬 파일의 동일성이다. 보드 flash readback이나 실행 이미지 해시 확인, 새 빌드/플래시는 수행하지 않았다. Git HEAD만으로 미커밋 자료까지 식별하지 않는다.

| 항목 | 기준 |
| --- | --- |
| STM 앱 | `03_Firmware/stm32_uart_mvp`, HAL bare-metal. CubeIDE 프로젝트/`.ioc` 포함 |
| ESP 앱 | `03_Firmware/esp32_wifi_link`, ESP32-S3. 로컬 SDK 검토 기준 ESP-IDF v6.0.2. `esp32_uart_bridge`는 과거 별도 앱 |
| 실행 설정 | ESP `WIFI_CONTROL_ZERO_ONLY=0`, UART 시험mode0. STM 출력/오류 주입 hook0 |
| 출력 | 일반 cap150‰, 순수 회전200‰, 왼쪽 직진 gain 전진960‰/후진930‰ |
| 브라우저 입력 | 전·후진 요청±100mm/s, 회전±500mrad/s. 현재 open-loop 요청값이며 실측 속도가 아님 |
| 주기와 정지 조건 | CMD 목표80ms, control freshness200ms, 제어용 TEL age250ms, STM 명령 timeout300ms. 표시용 stale500ms와 구분 |
| 관측 데이터 | signed64 누적 count를 문자열로 전달. encoder sample 시각·ARM seq·boot/session을 함께 보존 |

현재 설정의 근거: [명령 변환](../../03_Firmware/stm32_uart_mvp/Core/Src/drive_command_mapper.c), [ESP 계약](../../03_Firmware/esp32_wifi_link/main/wifi_control_contract.h), [PAGE](../../03_Firmware/esp32_wifi_link/main/wifi_link_main.c). 실제 CMD 간격은 ACK/ticket 조건 때문에80ms와 다를 수 있다. 과거500ms timeout 시험 보고서를 현재 설정으로 읽지 않는다.

새 환경에서 펌웨어를 준비할 때는 [STM 프로젝트](../../03_Firmware/stm32_uart_mvp/)와 [ESP 빌드 안내](../../03_Firmware/esp32_wifi_link/README.md#빌드검사)를 따른다. Wi-Fi 개인 설정은 Git에 없는 `wifi_link_config.h`이며 [예시](../../03_Firmware/esp32_wifi_link/main/wifi_link_config.h.example)로 AP/STA·접속 정보를 로컬 설정한다. 비밀번호를 기록/게시하지 않는다. 두 MCU 빌드·플래시는 사용자 수행이며, 새 이미지의 구동 수용을 이 문서로 대신하지 않는다.

## 3. 시작 → 연결 → 운전 → 종료

현재 배선이 유지된 감독하 저속 운용에 대한 순서다. 실제 작업에서는 한 단계의 예상 상태를 확인한 뒤 다음 단계로 진행한다. 배선·점퍼 변경은 전원을 분리한 상태에서 수행한다.

| 단계 | 작업 | 다음 단계로 넘어갈 상태 / 중단 조건 |
| --- | --- | --- |
| 1. 시작 조건 | S1 OFF, 이전 제어 의도 없음. USB 전원 분리·2P/JP5 기준 확인. 궤도 주변 공간과 S0 접근, 셀 알람 연결/표시 확인 | 기존 지상/공중 조건 중 사용할 조건을 기록. 미확인 전원 조합·경고음·배선 손상이 있으면 통전/구동 진행하지 않음 |
| 2. 로직 전원 | LiPo 연결 후 S1 ON. S2는 아직 누르지 않음 | 보드 기동, 실제 궤도 무동작. K1 재인가 전 상태를 확인 |
| 3. 브라우저 연결 | 노트북을 로봇과 같은 STA 네트워크에 연결하고 현재 ESP IP의 HTTP `/` 열기. 기존 주소가 바뀌었으면 공유기 DHCP 목록 등으로 확인 | WebSocket 정상, 새 STM TEL, `startup_state=READY`, `stm_connected=true`, `stm_stale=false`. READY는 이번 ESP 부팅의 응답 확인이지 지속 통신 보장이 아님 |
| 4. 정지 상태 확보 | `DISARMED`·ESP `IDLE`, 요청/PWM/CPS0, 실제 정지를 확인. S0가 눌려 있으면 정지 원인을 확인한 뒤 해제 | S0 해제만으로 STM 래치가 풀리거나 모터가 움직여서는 안 됨. `ESTOP_ACTIVE/LATCHED`면 아래 복구 분기로 이동 |
| 5. 모터 전원 | 위 정지 상태와 S0 해제를 확인한 뒤 S2로 K1 수동 재인가 | **궤도 무동작**, DISARMED/출력0 유지. S2 조작만으로 움직이면 S0로 정지하고 중단 |
| 6. ARM 속도0 | 로봇 페이지에 포커스를 둔 채 ARM 클릭 | ARM/zero CMD 확인 후 `ACTIVE`, STM `ARMED`, 요청/PWM/CPS0. 방향 버튼 활성. READY만 보고 방향 입력을 시작하지 않음 |
| 7. 방향 입력 | 원하는 방향 버튼을 누르는 동안만 조작 | 해당 요청·PWM·CPS/count 변화와 실제 방향을 함께 확인. 예상 밖 움직임/정지 실패는 S0, 링크 오류·경고음은 작업 중단 |
| 8. 일반 정지 | 방향 버튼 해제 → 실제 정지/출력0 확인 → DISARM | 해제는 속도0 요청이며 ARM은 유지될 수 있음. DISARM 결과OK, ESP IDLE·STM DISARMED, PWM/CPS0·count 고정을 확인. 화면 숫자만으로 물리 정지를 대신하지 않음 |
| 9. 기록·종료 | 정지 후 필요한 로그를 내보내고 S1 OFF, LiPo 주 전원과 알람 연결을 분리 | 전원 분리 여부를 별도로 기록. DISARM은 전원 분리가 아니다. 종료 전압은 실제 측정한 경우에만 기록 |

시작 분기 근거는 [10/18 통전/배터리 전환](../progress/2026-10-18_progress.md), [10/20 래치·리셋·S2 관측](../progress/2026-10-20_progress.md)다. 위 순서 전체를 새로 통과한 cold-start 시험으로 기록하지 않는다. 현재 저장 로그의 마지막은 IDLE/DISARMED·count53336/53856 고정7.121초이며 **그 뒤 실제 전원 분리는 미보고**다.

### ESTOP 래치·통신 단절 때

- `ESTOP_ACTIVE`는 S0뿐 아니라 AUX5V 감지 전원 상실에서도 나타날 수 있다. S0 잠금으로 단정하지 않고 전원/감지 상태를 먼저 확인한다.
- `ESTOP_LATCHED`는 S0 해제 뒤에도 남을 수 있다. **S2는 K1 전원 재인가이며 STM fault reset 명령이 아니다.** 현재 브라우저에는 `ESTOP_RESET` 버튼이 없다.
- 기존10/20에서는 S2 미조작·궤도 공중·출력0 조건에서 감지 전원을 복구한 뒤 **STM 보드 RESET**으로 DISARMED/BOOT를 확인했고, 이후 S2를 눌러도 무동작이었다. 같은 시작 분기를 사용할 때도 S0 해제·감지 정상과 모터 전원 미인가를 먼저 확인한다. RESET 뒤에도 FAULT면 반복 ARM/S2로 진행하지 않는다. 운전 중 보드 RESET으로 문제를 덮지 않는다.
- 화면 전환/포커스 이탈·연결 끊김은 제어 의도를 취소한다. 복구 후 이전 방향을 자동 재개하지 않으며 정상 정지 상태에서 새 수동 ARM이 필요하다. 신선도 제한을 늘리거나 버튼을 강제로 활성화하지 않는다.
- 응답이 없을 때는 실제 정지를 확인한다. 위험한 움직임 또는 정지 실패는 브라우저 응답을 기다리지 않고 S0를 사용한다. 이미 완료한 [UART 단절→timeout 정지·복구](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#2026-10-20-명령선-단절timeout-정지와-복구)를 매번 재현할 필요는 없다.

## 4. 단계별 검증 근거

| 운용 기능 | 기존 근거 | 주장할 수 있는 범위 |
| --- | --- | --- |
| 배터리 단독·4방향·해제/정지 | [10/18 지상 최종 회차](../../assets/logs/wifi_link/2026-10-18_ground_combined_trim_run01/observations.json) | 선택 저속 기능. 전체 부하/정격 수용 아님 |
| ARM 속도0·수동 DISARM | [10/24 속도0](../../assets/logs/wifi_link/2026-10-24_handler_timing_armed_zero_run01/README.md) | ACTIVE→DISARM 송신36.522초, 명령381개 모두OK |
| 방향 입력·해제·수동 종료 | [10/24 전진](../../assets/logs/wifi_link/2026-10-24_handler_timing_air_forward_run01/README.md) | 첫 전진 송신→capture 해제49.225초, 명령500개 모두OK. 물리 정지시간 계측 아님 |
| 브라우저 처리 시간 | [IDLE](../../assets/logs/wifi_link/2026-10-24_handler_timing_idle_run01/README.md)·위 속도0·전진 | 각 해당 구간 앱 최대0.6/0.6/0.8ms. 과거 긴 지연 미재현; 전체 브라우저/네트워크 원인 배제 아님 |
| 명령 유실·복구 | [10/20 단절](../../assets/logs/wifi_link/2026-10-20_uart_tx_disconnect_timeout_air_run01/observations.json)·[복구](../../assets/logs/wifi_link/2026-10-20_uart_tx_reconnect_recovery_air_run01/observations.json) | 실제 정지·재연결 뒤 자동 재시작 없음. 전체 UART release와 구분 |
| 지상1m 기록 | [run03](../../assets/logs/wifi_link/2026-10-23_ground_1m_run03/encoder_analysis.json)·[run04](../../assets/logs/wifi_link/2026-10-23_ground_1m_run04/encoder_analysis.json) | 실측1002mm, 평균 추정1002.640333/1000.953333mm. 정확도/직진성/자동1m 정지 보증 아님 |
| 물리 E-stop | [T004](../verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md)·[A 구동 S0](../verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md) | 확인한 감지/래치/PWM·제한 구동 범위. T005A 전체 PARTIAL·T007 정식 수용 BLOCKED 유지 |

공중 거리 버튼은5/10/15/20cm의 별도 기능이다.5/10/15cm는 기존 제한 회차 근거가 있고20cm는 사용자 요청 미실시다. 지상1m 기록을 이 버튼의 자동1m 정지로 소개하지 않는다.

## 5. 저장 로그 재현과 기록 방법

실물 없이 지상 결과를 재계산하는 명령은 [README의 저장 결과 재현](../../README.md#저장된-지상1m-결과-재현)을 따른다. v5.2 세 폴더에는 `browser_report.json.gz`, 원본 해시/출처 manifest, `analyze.py`, `summary.json`이 있다. 저장소 루트에서 다음 명령은 해당 저장 로그만 분석하며 `summary.json`을 다시 생성한다.

```powershell
python Projects/Tracked_Mobile_Robot/assets/logs/wifi_link/2026-10-24_handler_timing_air_forward_run01/analyze.py
```

앞선 IDLE/속도0 폴더도 같은 저장소에 있어야 한다. 재현 결과의 `checks`가 모두true이고 명령500개OK·최종count53336/53856인지 대조한다. 현재 문서 작업에서는 이미 완료한 분석/PC 시험을 다시 실행하지 않았다.

새로 로그를 수집할 필요가 생긴 회차에만 [v5.2 관측기](../../assets/logs/wifi_link/2026-10-24_browser_handler_timing_preparation/console_encoder_observe_1m_v5_2.js)를 DISARMED/IDLE에서 설치한다. 일반 운전의 필수 설치물이 아니다. 설치 후 페이지에 포커스를 돌리고, 끝나면 정지·DISARM 확인 뒤 개발자 콘솔에서 아래 명령으로 내보낸다. 새로고침하면 메모리 기록은 사라진다.

```javascript
copy(g6StopObserve.report())
```

회차에는 전원 모드, 공중/지상, 실제 조작/포커스 전환, 측정한 값과 사용자 관찰, 종료 상태를 함께 적는다. 마지막 raw·SHA-256·분석 결과를 보존하고 boot/session/ARM seq가 다른 구간을 임의로 이어붙이지 않는다. 계측기의 `trace_errors`, 삭제/overwrite·짝 누락을 먼저 확인한다.

## 6. 인수·시연에 남은 범위

- ACC-COM-01 지연 원인, ACC-UI-01 과거 수동 DISARM/UI 현상은 OPEN이다. 이번 정상3조건 표본으로 해결 처리하지 않는다. [경로 검토40](../verification/40_WS_Delivery_Path_and_Minimal_Observation_2026-10-23_ko.md)의 ESP 추가 계측B는 미구현이며 자동 착수하지 않는다.
- ACC-REL/PWR/MOT/ENC/ESTOP는 [보고서39](../verification/39_Home_Communication_Observation_and_MVP_Acceptance_Review_2026-10-23_ko.md#3-잔여-항목-확정)의 기존 PARTIAL/BLOCKED 경계다. 정지 과도기 오른쪽count -1도 원인 미확정이다. 사용자 제외한 정격/도면 조사를 새 숙제로 복원하지 않으며, 제외가 정식 수용 PASS를 뜻하지도 않는다.
- 이번에 운용·증거 연결 문서와 [시연 구성안](../plans/2026-10-24_MVP_Demo_Outline_ko.md)을 작성했다. [판정41](../verification/41_MVP_Acceptance_Disposition_2026-10-24_ko.md)에 따라 `MVP-012`의 로컬 README 정보 요구사항은 PASS다. `T-DOC-001`, `TK-MVP-05-03/04/05` 전체는 미완료다. 새 시연 영상·실행 이미지 readback·최종 인수 판정·공개 묶음은 추가하지 않았다.
- [판정41 후속 정정](../verification/41_MVP_Acceptance_Disposition_2026-10-24_ko.md#5-기준-검토-결과와-중복-재개-정정)에 따라10/17 이미 수행·후속 제외한 rail-off 기준 조사를 다음 필수 단계에서 취소했다. 수치 기준/인수 판정 변경 없음. 다음은 [기존 원본2개 재생 검토와 시연 편집](../plans/2026-10-24_MVP_Demo_Outline_ko.md)이다. 전체 MUST/정식 인수는 미완료이며 온도/전류·ADC·IMU/CAN/PCB는 후속이다.
