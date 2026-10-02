# ESP32 단계별 예제 학습

`esp32_wifi_link` 코드를 이해하기 위한 단계별 예제 모음입니다.

## 학습 순서 — 2026-10-03

| 단계 | 폴더 | 핵심 개념 | wifi_link 코드와의 연결 | 상태 |
|------|------|-----------|------------------------|------|
| 01 | `01_hello_world` | ESP_LOGI, app_main 구조 | 로그 출력, 초기화 패턴 | ✅ 빌드 성공 |
| 02 | `02_freertos_task` | vTaskDelay, Task 생성 | `app_main` 루프, `ws_schedule` | ⬜ 대기 |
| 03 | `03_wifi_sta` | Wi-Fi 이벤트 핸들러 | `wifi_event`, `server_start/stop` | ⬜ 대기 |
| 04 | `04_http_server` | HTTP URI 핸들러 | `page_get`, `status_get` | ⬜ 대기 |
| 05 | `05_websocket` | WebSocket 브로드캐스트 | `ws_receive`, `ws_broadcast` | ⬜ 대기 |

실제 소스·CMake가 있는 것은 01뿐이고 02~05는 폴더만 준비돼 있다.
01의 빌드 성공 기록과 보드 실행 검증은 구분한다. 실행 로그는 아직 이 검토에서 확인하지 않았다.
현재 `esp32_wifi_link`는 HTTP 폴링이며 표의 WebSocket 함수들은 이후 구현할 학습 대상이다.

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

## 다음 할 일 (Step 01 마무리)

1. `idf.py flash monitor` 실행해서 보드에 올리기
2. 시리얼 모니터에서 로그 출력 확인
3. 이해도 체크 3가지 스스로 답해보기:
   - `TAG` 는 왜 선언하나?
   - `vTaskDelay` 없으면 어떻게 되나?
   - `ESP_LOGI` vs `ESP_LOGE` 차이는?
4. Step 02로 넘어가기

## 남은 보완

- 예제용 `.gitignore`로 `build` 등 생성 파일을 제외한다. 10/3 검토 당시 빌드 파일들이 Git 미추적 후보에 포함돼 있었다.
- `sdkconfig.defaults` 등으로 target·콘솔 설정을 재현할 기본 설정을 남긴다. 현재 이 파일은 없다.
- `ESP_LOGE` 호출 자체는 프로그램을 중단시키지 않는다는 점과 `app_main()`이 FreeRTOS 태스크 안에서 실행된다는 점을 이해한다.

[검토 결과와 다음 작업](../../docs/progress/2026-10-03_progress.md)을 참고한다.
