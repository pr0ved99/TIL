# ESP32 Wi-Fi · STM UART 상태 전달

STM32의 실제 UART TEL을 ESP32-S3가 받아 Wi-Fi/WebSocket으로 브라우저에 전달하는 ESP-IDF 프로젝트다.

## 현재 상태 — 2026-10-08

**W4 읽기 전용 상태 전달 PASS.** 실제 TEL 표시, STM 수신 중단/복구, WebSocket 재접속,
부팅 DISARM ACK→PING/PONG→READY와 응답 누락 시 제한 실패를 확인했다.
[W4 보고서33](../../docs/verification/33_W4_STM_UART_WebSocket_and_Startup_Status_2026-10-08_ko.md)와
[마감 기록](../../docs/progress/2026-10-08_progress.md)이 시험 조건과 증거의 기준이다.

현재 `/ws`는 상태 전달용이다. 브라우저의 PING/DISARM·ARM/CMD 입력은 W5 미구현 범위다.
부팅 때 UART로 보내는 DISARM/PING은 별도 응답 확인 순서이며 자동 구동하지 않는다.
READY/FAILED는 **이번 ESP 부팅의 응답 확인 이력**이다. 현재 STM 연결·구동 허가는 TEL freshness와 별도로 판단해야 한다.

## 데이터 흐름과 조건

```text
STM UART TEL → ESP RX 줄 조립/파싱 → mutex snapshot
→ HTTP 서버 작업에서 JSON 전송 → WebSocket → 브라우저
```

- ESP GPIO17 TX→STM PA10 RX, STM PA9 TX→ESP GPIO18 RX, 공통 GND, 115200/8N1.
- 마감 시험: 두 보드 만능기판 장착·각각 USB 전원, LiPo 미연결. STM PA10 내부 pull-up 유지.
- STM TEL100ms / WebSocket 상태1000ms / TEL stale500ms / 브라우저 무응답4000ms.
- 유효 TEL을 받은 ESP 시각으로 age를 계산한다. ACK/PONG은 TEL freshness를 갱신하지 않는다.
- `batt_mv=null`, `battery_available=false`: 배터리 ADC 미구현. CPS는 counts/s이며 RPM과 다르다.
- 마지막 화면은 READY·fresh·FAULT/ESTOP_ACTIVE·PWM/CPS0·drop0·err1이었다. err는 누적 오류이며 특정 하드웨어 오류 코드가 아니다.

## 경로와 설정

| 경로 | 용도 |
| --- | --- |
| GET `/` | 로봇 상태 화면·WebSocket 연결 |
| GET `/api/status` | 같은 상태 JSON의 개별 조회. 화면 반복 갱신은 WebSocket |
| `/ws` | 상태 JSON 수신. 브라우저 명령 입력은 아직 없음 |

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
실제 저장본의 브라우저 모의 검사25 PASS와 보드 실행은 별도 증거다.
[검사 안내](../tests/README.md)와 [다음 인수인계](../../docs/handoff/CURRENT_SESSION_CONTEXT.md)를 따른다.

## 이전 단계와 남은 범위

- [단계별 학습 예제](../esp32_examples/README.md): 10/6 HTTP·두 탭 WebSocket 실행 확인 뒤 실제 앱으로 전환했다.
- [10/1 AP HTTP 기록](../../docs/progress/2026-10-01_progress.md), [10/2 최초 STA 연결](../../docs/progress/2026-10-02_progress.md): 당시 학습·접속 이력.
- [HTTP 입력 안내](../../docs/plans/2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md)와 [ESP 단독 WS 입력 안내](../../docs/plans/2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)는 이전 단계 코드다. 현재 실행 소스의 대체본으로 사용하지 않는다.
- [기존 UART bridge](../esp32_uart_bridge/README.md)는 별도 프로젝트다. 그 수동 모터 시험 hook을 이 앱의 실행 상태로 해석하지 않는다.

다음은 [W5 계획](../../docs/plans/2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md)의
입력·세션·단일 UART 송신 소유자·seq/응답 계약을 정하고, 모터 전원 없이 PING/DISARM부터 검증하는 작업이다.
리셋 순간 UART err 증가의 완전한 전기 원인, 실제 구동 중 통신 유실 안전, 배터리 ADC·전류·열·주행은 미완료다.
