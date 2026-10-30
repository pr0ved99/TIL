# ESP32 Wi-Fi · STM UART 상태와 방향 제어

STM32의 UART TEL을 브라우저에 전달하고 PING/DISARM 및 ARM과 방향 CMD를 UART 응답·새 TEL과 연결하는 ESP-IDF 프로젝트다.

## 현재 상태 — 2026-10-24

**후속 적용 확인:** 사용자 ESP 플래시 성공, 새 UI ARM0→DISARM 정상·배터리 단독 보고를 받았다. [새 화면/실물 영상](../../assets/logs/wifi_link/2026-10-24_demo_run01/README.md)에서6개 구동 구간과 마지막 DISARM1512 OK·IDLE/DISARMED/출력0을 확인했다. 아래 보드 적용 대기는 구현 당시 이력이다. 이번 실행 이미지 해시/원본 TEL 로그는 미확보다.

**로컬 UI 보완·보드 적용 대기:** [실제 PAGE 표시 재점검](../../assets/logs/wifi_link/2026-10-24_browser_dashboard_review/README.md)으로 좌우 PWM%/CPS/count 요약, 십자 방향 버튼, 큰 DISARM, 지연·FAULT 표시와 접이식 JSON을 추가했다. PC105검사와 Chrome4너비 검사 PASS. 기존 제어 코드/제한은 동일하며 새 빌드·플래시는 사용자 수행 대기다. 아래 통신 시간/해시와 “새 펌웨어 없음”은 UI 수정 전 관측 이력이다.

[운용·재현 절차](../../docs/handoff/CURRENT_MVP_OPERATION_RUNBOOK_ko.md)에 배터리 단독 전원·UART/구동 연결·펌웨어 기준과 시작~종료/복구 순서를 모았다. v5.2 실제 IDLE/속도0/전진 계측은 [3조건 비교](../../assets/logs/wifi_link/2026-10-24_handler_timing_air_forward_run01/README.md)에 완료했다. 원인OPEN/전체 인수 미완료, 새 펌웨어/빌드·플래시는 없다. 아래10/23 전원 관측은 이전 회차이며 새 전압/종료 전원 분리는 미보고다.

지상1m 실제/추정·오차 기록 범위 PASS. run03/04 사용자 실측1002mm에 평균1002.640333/1000.953333mm, 종료 DISARM OK·IDLE·정지 TEL을 확인했다. PC 관찰기v5.1은 재접속/실제 송신/수동 클릭/focus loss를 추적하며 MCU코드/빌드·플래시 변경은 없다. run02의 간헐 DISARM/UI 원인은 OPEN, 전체 인수는 미완료다. [최신 판정](../../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#2026-10-23-지상-1m-결과와-잔여-인수-대조), [관찰기](../../assets/logs/wifi_link/2026-10-23_ground_distance_preparation/console_encoder_observe_1m.js). 기존k/cap/gain 유지, 외부 온도는 후속 미실시다.

**최신 전원 재설정 후 관측:** 전원 재설정 후 두 보드 연결 전압5.02V, 로봇 최종 실측 중량3.25kg(사용자 보고). 새 로그153.124초/전·후진·좌우회전16개 비영 명령 구간에서 집중·버튼 유지 중 지연성 DISARM0건, TEL 최대126.3ms(비영 명령120ms), 제어 상태 최대80.1ms다. 이전 전진/좌회전 정지 근처 TEL287.9/219.2ms보다 긴 공백이 줄었지만 재부팅도 동반되어 전압 인과관계는 OPEN이다. MCU 소스/제한값·빌드/플래시 변경 없음. 전체 인수와 별개다.

### 10/21 공중 거리 — 당시 이력

10/21 공중 목표 거리5·10·15cm의 단일 회차 실측을 마감했다. 좌/우 실측은5cm=52/52mm, 10cm=102/101~102mm, 15cm=151~152/151~152mm다. 10·15cm JSON에서 목표 도달→DISARMED·요청/PWM/CPS0·drop/err0과 정지 후 count 유지를 확인했다. 20cm는 사용자 요청으로 미실시다. 현재 k=1687/19500mm/count와 출력/gain을 유지한다. 반복 정밀도·지상 차체 거리/직진성·외부 온도·전체 MVP 수용은 미완료다. 10/20 공중 UART 단절/timeout 정지·복구 기능 근거는 보존하며, 이번 거리 변경 후 실행 이미지 신원/변경 영향은 별도로 연결한다. [10/21 기록](../../docs/progress/2026-10-21_progress.md).

PAGE는 넓은 화면2열/900px 이하1열이며 전체 거리 JSON 복사와 HTTP 대체 복사·수동 선택을 지원한다. 기록은 페이지 메모리에 있어 새로고침 전에 보관한다. 거리 버튼은 hold-to-run이고 ARM 전 목표 선택·post-ARM 정지 기준점·좌우 독립 출력 차단·도달 후 DISARM을 사용한다. 20cm 입력/PC 검사는 유지하지만 이번 실물 회차는 미실시다.

### 10/18 기본 주행 이력

배터리 단독 지상에서 브라우저→ESP→STM 경로의 전·후진·양방향 회전·놓음/DISARM 정지를 확인했다. 현재 ZERO_ONLY=0U·UART 시험 mode0, 일반 PWM cap150‰/순수 회전200‰, STM 직진 왼쪽 gain960/930이다. [최종 주행 회차](../../assets/logs/wifi_link/2026-10-18_ground_combined_trim_run01/observations.json), [진행 기록](../../docs/progress/2026-10-18_progress.md). 전체 MVP·정밀 속도/거리·모든 오류/물리 안전 수용은 별도다.

현재 WS 상태50ms·브라우저 CMD80ms(새 ticket/ACK 등 조건 충족 시), STA WIFI_PS_NONE으로 동작한다. 과거 간헐 정지에는 TEL freshness/SOURCE timeout과 구 ESP±150 이미지가 ±200을 거부한 별개 사례가 있었다. 후속 비재현 회차로 영구 신뢰성을 주장하지 않는다. 제어 TEL250ms·SOURCE200ms·STM300ms 제한은 유지했다.

## 데이터 흐름과 조건

```text
STM UART TEL → ESP RX 파싱 → mutex snapshot → HTTP 작업 → WebSocket → 브라우저
PING → 요청 큐 → UART 태스크 → PONG → 요청자별 결과
ARM/CMD → 형식·ticket·owner·상태 검사 → executor → UART 태스크 → ACK/TEL
DISARM/취소 → 제어 허가와 미송신 입력 폐기 → DISARM → ACK와 새 정지 TEL
```

- ESP GPIO17 TX→STM PA10 RX, STM PA9 TX→ESP GPIO18 RX, 공통 GND, 115200/8N1.
- STM TEL 목표100ms·WS 상태 목표50ms, 제어 처리 목표20ms. 표시 stale500ms와 제어용 TEL age250ms는 구분한다.
- ARM→zero CMD ACK와 새 일치 TEL→ACTIVE→현재 방향 CMD. ticket150ms·큐50ms·ACK150ms·source200ms 등 서로 다른 기한을 검사한다.
- 브라우저는 ticket 전송 여유50ms와 수동 ARM의 미송신 준비 대기 최대200ms를 사용한다. blur/hidden/끊김은 준비 대기·제어 의도를 취소한다.
- `batt_mv=null`, `battery_available=false`: 배터리 ADC 미구현. CPS는 counts/s다.
- 현재 물리 조건은 [인수인계](../../docs/handoff/CURRENT_SESSION_CONTEXT.md)를 확인한다. W5 종료 때 USB 분리 조건을 이후 시험의 현재 조건으로 사용하지 않는다.

## 경로와 설정

| 경로 | 용도 |
| --- | --- |
| GET `/` | 로봇 상태·PING/ARM 속도0/DISARM 버튼·결과·제어 상태 |
| GET `/api/status` | STM 상태 JSON 개별 조회 |
| `/ws` | 상태·notice/result·control_state 수신, HELLO 및 명령 입력 |

HELLO는 연결 등록이며 UART 명령이 아니다. PING/DISARM은 boot_id·request_id를 사용하고, ARM은 ticket, CMD는 control_id·ticket·vx_mmps/w_mradps 필드를 추가한다. 접수 성공은 실행 완료가 아니다. DISARM OK는 ACK뿐 아니라 새 비무장/출력0 TEL까지 확인한 결과다.

정확한 형식·타이밍·취소 경계는 [실제 main](main/wifi_link_main.c), [검사 안내](../tests/README.md), [교과서](../../07_Embedded_Learning_Notes/06_STM32_ESP32_Firmware_Textbook/README.md)를 참조한다.

`main/wifi_link_config.h`에서 AP/STA를 선택한다. 개인 header는 Git에서 제외하며
[설정 예시](main/wifi_link_config.h.example)를 참고한다. 공유기 STA 주소는 DHCP 할당 로그로 확인한다.

`sdkconfig.defaults`의 `CONFIG_HTTPD_WS_SUPPORT=y`와 `main/CMakeLists.txt`의
`esp_driver_uart`를 포함한 의존성 선언이 필요하다. 기존 `sdkconfig`에도 WS 옵션이 적용돼 있어야 한다.
USB 보조 콘솔 설정을 사용하며 USB 포트/COM 번호는 실제 장치에 맞춘다.

## 빌드·검사

VS Code에서 **이 폴더 `esp32_wifi_link`**를 ESP-IDF 프로젝트로 열고 ESP32-S3 target으로 빌드한다.
ESP-IDF 환경이 활성화된 터미널에서는 이 폴더에서 실행한다.

```powershell
idf.py build
idf.py -p COM번호 flash monitor
```

`COM번호`는 실제 장치 포트로 바꾼다. 코드 입력·보드 빌드·플래시는 사용자가 수행한다.
마감 PC 검사는 mode0 core14·mode1 추가3·기존 회귀59, adapter 각6·기존 C42, PAGE67과 C 초기화/반례 검사를 구분한다. [현재 검사 근거](../../assets/logs/wifi_link/2026-10-18_manual_drive_closeout_pc_review/esp_main.json)와 사용자 보드 관측은 별도 증거다.
모듈별 PC 검사·사용자 빌드 성공을 전체 구동 안전으로 확대하지 않는다.
[검사 안내](../tests/README.md)와 [다음 인수인계](../../docs/handoff/CURRENT_SESSION_CONTEXT.md)를 따른다.
새 시험의 원본 로그·화면·빌드/플래시 식별값은 [증거 보존 절차](../../docs/verification/EVIDENCE_CAPTURE_GUIDE_ko.md)를 따른다.

## 이전 단계와 남은 범위

- [단계별 학습 예제](../esp32_examples/README.md): 10/6 HTTP·두 탭 WebSocket 실행 확인 뒤 실제 앱으로 전환했다.
- [10/1 AP HTTP 기록](../../docs/progress/2026-10-01_progress.md), [10/2 최초 STA 연결](../../docs/progress/2026-10-02_progress.md): 당시 학습·접속 이력.
- [HTTP 입력 안내](../../docs/plans/2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md)와 [ESP 단독 WS 입력 안내](../../docs/plans/2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)는 이전 단계 코드다. 현재 실행 소스의 대체본으로 사용하지 않는다.
- [기존 UART bridge](../esp32_uart_bridge/README.md)는 별도 프로젝트다. 그 수동 모터 시험 hook을 이 앱의 실행 상태로 해석하지 않는다.

ARM/CMD nonzero 통합과 NZ-01~04 모터 분리 검증을 마쳤다. [초기 계약](../../docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md)의
전체 AC-H/B/S 수용은 PC·보드·출력 근거를 나누어 미완료 항목만 이어간다.
PING/DISARM의 비구동 PASS와 모듈 PC 검사·빌드 성공을 구동 허가로 쓰지 않는다.
리셋 순간 UART err 증가의 전기 원인·간헐 통신 지연/UI 원인은OPEN이다.10/20 전용 통신 유실/timeout 정지·복구와10/23 지상1m 거리 기록은 해당 기능 범위 완료다. 외부 온도는 후속 DEFERRED/NOT_RUN, 정량 전류/전압 ADC와 자동 저전압 정지도 후속이다. 전체 인수 판정과 구분한다.
