# ESP32 단독 Wi-Fi Link

ESP32-S3와 노트북만으로 PC↔ESP의 Wi-Fi/HTTP 경로를 검증하는 학습용 ESP-IDF 프로젝트다.
실제 STM UART 통합·모터 명령은 구현하지 않는다.

## 현재 상태 — 2026-10-03

사용자가 앱과 개인 설정 header를 작성·수정하고 ESP-IDF 6.0.2에서 빌드·플래시했다.
**AP 접속·HTTP 상태 수신(W1), 자동 갱신(W2), 연결 해제 표시·재접속 복구(W3)를 확인했다.**
재플래시로 boot_id가 바뀌었으며 이후 연결 해제·재접속에서는 유지됐다. 10/2에는 STA 설정으로 변경하고 사용자가 공유기 연결 완료를 보고했다. STA 로그/IP와 재접속 시험은 별도 미확인이다.
근거와 관측 범위는 [10/1 진행 기록](../../docs/progress/2026-10-01_progress.md#wi-fi-ap-실측--w1w2w3-결과)을 따른다.
현재 코드는 HTTP 폴링이며 WebSocket·STM UART 통합·무선 명령은 미구현이다.

WebSocket 서버 지원 설정(`CONFIG_HTTPD_WS_SUPPORT=y`)은 활성화됐고 `sdkconfig.defaults`와 CMake 의존성 선언도 확인했다.
현재 앱 소스는 HTTP 폴링이며 WebSocket 전환 코드의 빌드·보드 검증은 미실행이다.
안내 코드의 브라우저 모의 검사 11개 PASS는 실제 ESP 실행 결과와 구분한다.

현재는 [단계별 예제](../esp32_examples/README.md)로 로그 → 태스크 → STA 이벤트 → HTTP → WebSocket을 학습한다.
작성된 것은 01 Hello World이며 02~05는 준비 단계다. 기초 학습 뒤 [WebSocket 전체 코드 입력 안내](../../docs/plans/2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)를 따른다.
최근 저장본 검토 결과와 남은 작업은 [10/3 진행 기록](../../docs/progress/2026-10-03_progress.md)을 참고한다.
USB 표기 포트 사용 시 현재 COM4와 USB 보조 콘솔 출력을 확인했다. 실제 연결 기록은 [10/2 진행 기록](../../docs/progress/2026-10-02_progress.md#공유기-sta-연결-확인)을 따른다.

[코드 전문·입력 위치·함수 설명·시험 기준](../../docs/plans/2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md)을 따른다.
AP와 STA는 개인 설정으로 선택한다. 실제 wifi_link_config.h는 .gitignore로 제외한다.

## 경로

- GET /: ESP 상태 화면.
- GET /api/status: ESP uptime·heap·부팅 식별값.
- STM 연결은 미구현이므로 stm_connected=false, state/PWM/CPS=null.

[기존 UART bridge](../esp32_uart_bridge/README.md)는 별도 프로젝트로 보존했다.
