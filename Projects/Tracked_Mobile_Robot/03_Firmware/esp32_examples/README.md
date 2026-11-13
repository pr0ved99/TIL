# ESP32 단계별 예제 학습

`esp32_wifi_link` 코드를 이해하기 위한 단계별 예제 모음입니다.

**상태 안내 갱신: 2026-10-11.** 아래 학습 순서와 실행 결과는10/6 당시 기록이다.
실제 앱은 이후 WebSocket·STM TEL의 W4와 비구동 PING/DISARM의 W5를 완료했다.
현재는 ARM/CMD parser·ticket·owner PC15/12/9 PASS·ESP 전체 빌드 성공 사용자 확인 이후 상태·시간 제한 흐름을 준비한다.
[실제 앱 안내](../esp32_wifi_link/README.md)와 [현재 인수인계](../../docs/handoff/CURRENT_SESSION_CONTEXT.md)를 재개 기준으로 사용한다.

## 학습 순서 — 2026-10-06

| 단계 | 폴더 | 핵심 개념 | wifi_link 코드와의 연결 | 상태 |
|------|------|-----------|------------------------|------|
| 01 | `01_hello_world` | ESP_LOGI, app_main 구조 | 로그 출력, 초기화 패턴 | ✅ 빌드 성공 |
| 02 | `02_freertos_task` | vTaskDelay, Task 생성·Mutex | `app_main` 루프, 이후 전송 작업 예약 | ✅ 실행 확인 기록 / 10/4 저장본 검토 |
| 03 | `03_wifi_sta` | Wi-Fi 이벤트 핸들러 | `wifi_event`, `server_start/stop` | ✅ 실행 확인 기록 |
| 04 | `04_http_server` | HTTP URI 핸들러 | `page_get`, `status_get` | ✅ 10/6 사용자 `/hello` 응답 확인 |
| 05 | `05_websocket` | WebSocket 브로드캐스트 | 실제 앱의 상태 전송으로 확장 | ✅ 10/6 사용자 탭 A→B 기본 전달 확인 |

01~05 모두 소스·CMake와 `GUIDE.md`가 있다. 01의 빌드 성공과 02/03 실행 확인은 기존 README 기록이며, 04/05의 오늘 결과는 사용자 대화 보고다. 원본 실행 로그·바이너리 해시는 이번 문서 정리에서 확인하지 않았다.

10/6 당시 `esp32_wifi_link`는 HTTP 폴링이었다. 05의 `broadcast_text()`는 예제의 메시지 전달이며 예제 PASS 자체가 실제 앱의 UART·명령 검증을 증명하지 않는다. 당시 준비 과정은 [10/6 기록](../../docs/progress/2026-10-06_progress.md), 후속 완료 범위는 [W5 보고서34](../../docs/verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md)를 따른다.

## 환경

- ESP-IDF v6.0.2
- 대상 보드: ESP32-S3

## VS Code에서 01 실행하기

1. **`01_hello_world` 폴더**를 ESP-IDF 프로젝트로 연다. `esp32_examples` 전체 폴더에는 최상위 `CMakeLists.txt`가 없다.
2. ESP-IDF v6.0.2와 target `esp32s3`, 연결된 ESP의 실제 COM 포트를 확인한다.
3. 사용자가 Build → Flash → Monitor를 실행한다. 터미널에서는 ESP-IDF 환경이 활성화된 상태로 `01_hello_world` 폴더에서 `idf.py -p COM번호 flash monitor`를 실행한다. `COM번호`는 실제 포트로 바꾼다.
4. 시작 로그 3종 뒤 `카운트: 0`, `카운트: 1`처럼 값이 약 1초마다 증가하는지 확인한다. 재부팅하면 카운트는 다시 0부터 시작한다.

01의 현재 설정은 UART 기본 콘솔·USB Serial/JTAG 보조 콘솔, 115200 baud다.
이 예제를 플래시하면 ESP에서 실행하는 앱이 Hello World로 바뀐다. Wi-Fi 기능을 다시 시험하려면 `esp32_wifi_link`를 별도로 빌드·플래시한다.

## 실제 앱으로 연결한 결과와 다음 작업

1. **완료:** 실제 STM TEL → ESP snapshot → WebSocket, 수신 중단/stale·복구와 부팅 응답 이력 표시(W4).
2. **완료:** 브라우저 PING/DISARM → UART 응답 → 요청자별 결과·버튼, 거부·timeout·재접속 뒤 자동 재전송 없음(W5).
3. **다음:** [ARM/CMD 초기 계약](../../docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md)의 기초 모듈 이후 상태·시간 제한·ACK/TEL·취소/정지 흐름. 큐/UART·브라우저 연결과 새 보드 시험은 남아 있다.

TAG의 역할, `vTaskDelay`의 대기, `ESP_LOGI`와 `ESP_LOGE`, Wi-Fi 이벤트·HTTP handler·브로드캐스트의 호출 흐름은 각 GUIDE로 복습한다. 이미 확인한 04/05 기본 실행을 다시 필수 시험으로 요구하지 않는다.

## 남은 보완

- 03~05에는 `.gitignore`가 있다. 01/02의 생성 파일 제외와 이미 추적된 01 `build` 정리는 별도 Git 작업으로 남아 있다.
- `sdkconfig.defaults` 등으로 target·콘솔 설정을 재현할 기본 설정을 남긴다. 현재 예제에서 이 파일은 확인되지 않았다.
- `ESP_LOGE` 호출 자체는 프로그램을 중단시키지 않는다는 점과 `app_main()`이 FreeRTOS 태스크 안에서 실행된다는 점을 이해한다.

[10/3 검토 이력](../../docs/progress/2026-10-03_progress.md)과 [타이밍·모의 데이터 설명](../../07_Embedded_Learning_Notes/01_Concept_Notes/10_ESP32_WiFi_WebSocket_Timing_and_W4_Dataflow_ko.md)을 참고한다.
