# ESP32 Wi-Fi · STM UART 상태와 zero-only 제어

STM32의 UART TEL을 브라우저에 전달하고 PING/DISARM 및 속도 0 전용 ARM/CMD를 UART 응답·새 TEL과 연결하는 ESP-IDF 프로젝트다.

## 현재 상태 — 2026-10-17

UR-02 부분 CMD/ARM 폐기·첫 DISARM 복구와 UR-03 AC-S01~08의 선택한 zero-only 실물 시나리오를 마감했다. 모터 동력 차단 상태에서 UART·실제 PWM·PC7을 대조했다. 전체 오류 분기·nonzero 구동·전력/기계 안전·주행 수용은 별도다. [보고서37](../../docs/verification/37_Zero_Only_ACS_Bench_Closeout_2026-10-17_ko.md)과 [진행 기록](../../docs/progress/2026-10-17_progress.md)을 따른다.

부팅 및 모든 DISARM 앞의 ASCII CAN+LF는 STM 잔여 줄을 실행 없이 폐기한다. ESP 시험 mode1/2/3은 부분 CMD/ARM·timeout 검증용이며 현재 WIFI_UART_PARTIAL_TEST_MODE=0U로 비활성이다. 사용자 정상 이미지 복원과 수동 ARM/zero/DISARM을 확인했다.

READY/FAILED는 이번 ESP 부팅의 응답 확인 이력이다. 현재 TEL freshness와 제어 조건은 별도로 판단한다. 새 연결·포커스 복귀는 자동 ARM하지 않으며 B는 한 페이지의 내부 WebSocket으로 시험할 수 있다. 공개 소스 hash는 플래시 바이너리 readback을 대신하지 않는다.

## 데이터 흐름과 조건

```text
STM UART TEL → ESP RX 파싱 → mutex snapshot → HTTP 작업 → WebSocket → 브라우저
PING → 요청 큐 → UART 태스크 → PONG → 요청자별 결과
ARM/CMD → 형식·ticket·owner·상태 검사 → executor → UART 태스크 → ACK/TEL
DISARM/취소 → 제어 허가와 미송신 입력 폐기 → DISARM → ACK와 새 정지 TEL
```

- ESP GPIO17 TX→STM PA10 RX, STM PA9 TX→ESP GPIO18 RX, 공통 GND, 115200/8N1.
- STM TEL/WS 상태 목표100ms, 제어 처리 목표20ms. 표시 stale500ms와 제어용 TEL age250ms는 구분한다.
- zero-only ARM→zero CMD ACK와 새 일치 TEL→ACTIVE. ticket150ms·큐50ms·ACK150ms·source200ms 등 서로 다른 기한을 검사한다.
- 브라우저는 ticket 전송 여유50ms와 수동 ARM의 미송신 준비 대기 최대200ms를 사용한다. blur/hidden/끊김은 준비 대기·제어 의도를 취소한다.
- `batt_mv=null`, `battery_available=false`: 배터리 ADC 미구현. CPS는 counts/s다.
- 현재 물리 조건은 [인수인계](../../docs/handoff/CURRENT_SESSION_CONTEXT.md)를 확인한다. W5 종료 때 USB 분리 조건을 이후 시험의 현재 조건으로 사용하지 않는다.

## 경로와 설정

| 경로 | 용도 |
| --- | --- |
| GET `/` | 로봇 상태·PING/ARM 속도0/DISARM 버튼·결과·제어 상태 |
| GET `/api/status` | STM 상태 JSON 개별 조회 |
| `/ws` | 상태·notice/result·control_state 수신, HELLO 및 명령 입력 |

HELLO는 연결 등록이며 UART 명령이 아니다. PING/DISARM은 boot_id·request_id를 사용하고, ARM은 ticket, CMD는 control_id·ticket·속도0 필드를 추가한다. 접수 성공은 실행 완료가 아니다. DISARM OK는 ACK뿐 아니라 새 비무장/출력0 TEL까지 확인한 결과다.

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
최신 저장본 C42·PAGE46 PC 결과와 사용자 보드 관측은 별도 증거다.
모듈별 PC 검사·사용자 빌드 성공을 전체 구동 안전으로 확대하지 않는다.
[검사 안내](../tests/README.md)와 [다음 인수인계](../../docs/handoff/CURRENT_SESSION_CONTEXT.md)를 따른다.
새 시험의 원본 로그·화면·빌드/플래시 식별값은 [증거 보존 절차](../../docs/verification/EVIDENCE_CAPTURE_GUIDE_ko.md)를 따른다.

## 이전 단계와 남은 범위

- [단계별 학습 예제](../esp32_examples/README.md): 10/6 HTTP·두 탭 WebSocket 실행 확인 뒤 실제 앱으로 전환했다.
- [10/1 AP HTTP 기록](../../docs/progress/2026-10-01_progress.md), [10/2 최초 STA 연결](../../docs/progress/2026-10-02_progress.md): 당시 학습·접속 이력.
- [HTTP 입력 안내](../../docs/plans/2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md)와 [ESP 단독 WS 입력 안내](../../docs/plans/2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)는 이전 단계 코드다. 현재 실행 소스의 대체본으로 사용하지 않는다.
- [기존 UART bridge](../esp32_uart_bridge/README.md)는 별도 프로젝트다. 그 수동 모터 시험 hook을 이 앱의 실행 상태로 해석하지 않는다.

ARM/CMD zero-only 실행 연결은 구현됐고 일부 보드 관측을 마쳤다. [초기 계약](../../docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md)의
전체 AC-H/B/S 수용은 PC·보드·출력 근거를 나누어 미완료 항목만 이어간다.
PING/DISARM의 비구동 PASS와 모듈 PC 검사·빌드 성공을 구동 허가로 쓰지 않는다.
리셋 순간 UART err 증가의 완전한 전기 원인, 실제 구동 중 통신 유실 안전, 배터리 ADC·전류·열·주행은 미완료다.
