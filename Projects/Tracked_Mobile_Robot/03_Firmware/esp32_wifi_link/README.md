# ESP32 Wi-Fi · STM UART 상태와 PING/DISARM

STM32의 실제 UART TEL을 ESP32-S3가 브라우저에 전달하고, WebSocket PING/DISARM 요청을 UART 응답과 연결하는 ESP-IDF 프로젝트다.

## 현재 상태 — 2026-10-10

**W4 상태 전달·W5 비구동 PING/DISARM PASS.** 실제 요청/응답, 입력 거부, 요청자별 결과·버튼,
timeout/복구와 재접속 후 자동 재전송 없음을 확인했다.
[W5 보고서34](../../docs/verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md)와
[마감 기록](../../docs/progress/2026-10-10_progress.md)이 시험 조건과 증거의 기준이다.

현재 `/ws`는 상태 전달과 PING/DISARM 입력·notice/result를 처리한다. 브라우저 ARM/CMD 입력은 미구현이다.
부팅 때 UART로 보내는 DISARM/PING은 별도 응답 확인 순서이며 자동 구동하지 않는다.
READY/FAILED는 **이번 ESP 부팅의 응답 확인 이력**이다. 현재 STM 연결·구동 허가는 TEL freshness와 별도로 판단해야 한다.

## 데이터 흐름과 조건

```text
STM UART TEL → ESP RX 줄 조립/파싱 → mutex snapshot
→ HTTP 서버 작업에서 JSON 전송 → WebSocket → 브라우저

브라우저 PING/DISARM → HTTP 입력 검사·요청 큐
→ UART 태스크의 송신·seq/응답 대응 → 결과 큐
→ HTTP 서버 작업 → 요청한 WS session의 브라우저
```

- ESP GPIO17 TX→STM PA10 RX, STM PA9 TX→ESP GPIO18 RX, 공통 GND, 115200/8N1.
- 마감 시험: 두 보드 각각 USB 전원, LiPo 미연결. STM PA10 내부 pull-up 유지. 종료 후 두 USB 분리 사용자 확인.
- STM TEL100ms / WebSocket 상태100ms / TEL stale500ms / 브라우저 무응답4000ms.
- 유효 TEL을 받은 ESP 시각으로 age를 계산한다. ACK/PONG은 TEL freshness를 갱신하지 않는다.
- `batt_mv=null`, `battery_available=false`: 배터리 ADC 미구현. CPS는 counts/s이며 RPM과 다르다.
- 마지막 화면은 재접속 후 수동 PING1 OK, READY·fresh·FAULT/ESTOP_ACTIVE·PWM/CPS0·drop/err0이었다. err는 누적 오류이며 특정 하드웨어 오류 코드가 아니다.

## 경로와 설정

| 경로 | 용도 |
| --- | --- |
| GET `/` | 로봇 상태·PING/DISARM 버튼·명령 접수/거부/완료 표시 |
| GET `/api/status` | 같은 상태 JSON의 개별 조회. 화면 반복 갱신은 WebSocket |
| `/ws` | 상태 JSON·command_notice/result 수신, final TEXT PING/DISARM 요청 송신 |

명령은 `PING,boot_id=<u32>,request_id=<positive u32>` 또는 `DISARM,...`이다.
최대128byte·같은 연결 간격500ms·전체 진행1개·UART 응답500ms·자동 retry 없음.
부팅 확인 진행 중 사용자 명령은 거부한다. 접수(ACCEPTED)는 STM 성공(OK)이 아니다.
브라우저 추가 결과 대기3000ms 만료는 ‘결과 확인 불가’이며 STM TIMEOUT과 구분한다.

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
실제 PAGE JS57 PASS·실제 C 일부 함수 PC21 PASS와 보드 실행은 별도 증거다.
[검사 안내](../tests/README.md)와 [다음 인수인계](../../docs/handoff/CURRENT_SESSION_CONTEXT.md)를 따른다.

## 이전 단계와 남은 범위

- [단계별 학습 예제](../esp32_examples/README.md): 10/6 HTTP·두 탭 WebSocket 실행 확인 뒤 실제 앱으로 전환했다.
- [10/1 AP HTTP 기록](../../docs/progress/2026-10-01_progress.md), [10/2 최초 STA 연결](../../docs/progress/2026-10-02_progress.md): 당시 학습·접속 이력.
- [HTTP 입력 안내](../../docs/plans/2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md)와 [ESP 단독 WS 입력 안내](../../docs/plans/2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)는 이전 단계 코드다. 현재 실행 소스의 대체본으로 사용하지 않는다.
- [기존 UART bridge](../esp32_uart_bridge/README.md)는 별도 프로젝트다. 그 수동 모터 시험 hook을 이 앱의 실행 상태로 해석하지 않는다.

다음은 [전체 학습·통합 계획](../../docs/plans/2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md)의
ARM/CMD 세션·명령 유효시간·TEL freshness·명시적 재허가 계약 설계다. PING/DISARM의 비구동 PASS를 구동 허가로 쓰지 않는다.
리셋 순간 UART err 증가의 완전한 전기 원인, 실제 구동 중 통신 유실 안전, 배터리 ADC·전류·열·주행은 미완료다.
