# ESP32 단계별 예제 학습

`esp32_wifi_link` 코드를 이해하기 위한 단계별 예제 모음입니다.

## 학습 순서 — 2026-10-06

| 단계 | 폴더 | 핵심 개념 | wifi_link 코드와의 연결 | 상태 |
|------|------|-----------|------------------------|------|
| 01 | `01_hello_world` | ESP_LOGI, app_main 구조 | 로그 출력, 초기화 패턴 | ✅ 빌드 성공 |
| 02 | `02_freertos_task` | vTaskDelay, Task 생성·Mutex | `app_main` 루프, 이후 전송 작업 예약 | ✅ 실행 확인 기록 / 10/4 저장본 검토 |
| 03 | `03_wifi_sta` | Wi-Fi 이벤트 핸들러 | `wifi_event`, `server_start/stop` | ✅ 실행 확인 기록 |
| 04 | `04_http_server` | HTTP URI 핸들러 | `page_get`, `status_get` | ✅ 10/6 사용자 `/hello` 응답 확인 |
| 05 | `05_websocket` | WebSocket 브로드캐스트 | 실제 앱의 상태 전송으로 확장 | ✅ 10/6 사용자 탭 A→B 기본 전달 확인 |

01~05 모두 소스·CMake와 `GUIDE.md`가 있다. 01의 빌드 성공과 02/03 실행 확인은 기존 README 기록이며, 04/05의 오늘 결과는 사용자 대화 보고다. 원본 실행 로그·바이너리 해시는 이번 문서 정리에서 확인하지 않았다.

현재 `esp32_wifi_link`는 HTTP 폴링이다. 05의 `broadcast_text()`는 예제의 메시지 전달이며 실제 앱의 WebSocket·STM TEL·무선 명령 완료가 아니다. [오늘 기록](../../docs/progress/2026-10-06_progress.md)과 [W4 재개 계획](../../docs/plans/2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md)을 따른다.

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

## 다음 할 일 — 실제 앱으로 연결

1. `esp32_wifi_link`에 ESP 단독 WebSocket 상태 전송을 적용한다.
2. 집에서 STM/ESP의 현재 앱·UART·전원 조건을 확인하고 실제 TEL을 snapshot과 화면에 연결한다.
3. 수신 중단·stale·재접속을 확인한 뒤 W5 무선 명령으로 진행한다.

TAG의 역할, `vTaskDelay`의 대기, `ESP_LOGI`와 `ESP_LOGE`, Wi-Fi 이벤트·HTTP handler·브로드캐스트의 호출 흐름은 각 GUIDE로 복습한다. 이미 확인한 04/05 기본 실행을 다시 필수 시험으로 요구하지 않는다.

## 남은 보완

- 03~05에는 `.gitignore`가 있다. 01/02의 생성 파일 제외와 이미 추적된 01 `build` 정리는 별도 Git 작업으로 남아 있다.
- `sdkconfig.defaults` 등으로 target·콘솔 설정을 재현할 기본 설정을 남긴다. 현재 예제에서 이 파일은 확인되지 않았다.
- `ESP_LOGE` 호출 자체는 프로그램을 중단시키지 않는다는 점과 `app_main()`이 FreeRTOS 태스크 안에서 실행된다는 점을 이해한다.

[10/3 검토 이력](../../docs/progress/2026-10-03_progress.md)과 [타이밍·모의 데이터 설명](../../07_Embedded_Learning_Notes/01_Concept_Notes/10_ESP32_WiFi_WebSocket_Timing_and_W4_Dataflow_ko.md)을 참고한다.
