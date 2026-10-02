# ESP32 단계별 예제 학습

`esp32_wifi_link` 코드를 이해하기 위한 단계별 예제 모음입니다.

## 학습 순서

| 단계 | 폴더 | 핵심 개념 | wifi_link 코드와의 연결 | 상태 |
|------|------|-----------|------------------------|------|
| 01 | `01_hello_world` | ESP_LOGI, app_main 구조 | 로그 출력, 초기화 패턴 | ✅ 빌드 성공 |
| 02 | `02_freertos_task` | vTaskDelay, Task 생성 | `app_main` 루프, `ws_schedule` | ⬜ 대기 |
| 03 | `03_wifi_sta` | Wi-Fi 이벤트 핸들러 | `wifi_event`, `server_start/stop` | ⬜ 대기 |
| 04 | `04_http_server` | HTTP URI 핸들러 | `page_get`, `status_get` | ⬜ 대기 |
| 05 | `05_websocket` | WebSocket 브로드캐스트 | `ws_receive`, `ws_broadcast` | ⬜ 대기 |

## 환경

- ESP-IDF v6.0.2
- 대상 보드: ESP32-S3

## 다음 할 일 (Step 01 마무리)

1. `idf.py flash monitor` 실행해서 보드에 올리기
2. 시리얼 모니터에서 로그 출력 확인
3. 이해도 체크 3가지 스스로 답해보기:
   - `TAG` 는 왜 선언하나?
   - `vTaskDelay` 없으면 어떻게 되나?
   - `ESP_LOGI` vs `ESP_LOGE` 차이는?
4. Step 02로 넘어가기
