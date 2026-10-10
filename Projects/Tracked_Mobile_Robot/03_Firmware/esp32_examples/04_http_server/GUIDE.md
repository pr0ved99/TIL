# 04 HTTP 서버 — 코드 가이드

대상 소스: [`main/http_server_main.c`](main/http_server_main.c), 설정: `main/wifi_config.h`

03의 Wi-Fi 접속 코드에, IP를 받으면 HTTP 서버를 시작하고 `/hello` 주소에 응답하는 기능을 더한 예제입니다.

## 전체 구조

```text
app_main → Wi-Fi 초기화/시작
 → (이벤트) STA_START → connect
 → (이벤트) GOT_IP → start_webserver()
        └─ httpd_start → "/hello" 핸들러 등록
 → 브라우저가 http://<ESP IP>/hello 요청 → hello_get_handler → 문자열 응답
```

## 1. 상단 정의 (1~20행)

| 항목 | 역할 |
|------|------|
| `esp_http_server.h` | HTTP 서버 API 헤더 |
| `MAX_RETRY`, `STATUS_PERIOD_MS` | 재접속 횟수와 메인 루프 주기 (03과 동일) |
| `s_retry_count` | 재시도 횟수 |
| `server` (전역 `httpd_handle_t`) | 실행 중인 서버 핸들. `NULL`이면 서버 미실행 → 중복 시작 방지에 사용 |

- 이 프로젝트의 `main/CMakeLists.txt`에서 `esp_http_server` 컴포넌트를 `PRIV_REQUIRES`로 요구합니다.

## 2. `hello_get_handler()` (23~30행) — URI 핸들러

- **역할**: 클라이언트가 `GET /hello`를 요청하면 실행됩니다.
- `httpd_resp_send(req, resp_str, HTTPD_RESP_USE_STRLEN)`: 문자열을 응답으로 보냅니다. 길이 인자에 `HTTPD_RESP_USE_STRLEN`을 주면 `strlen`으로 길이를 계산합니다.
- 반환값 `ESP_OK`는 처리 성공을 뜻합니다.
- 핸들러는 서버가 만든 태스크에서 실행됩니다. 직접 호출하는 코드는 없습니다.

## 3. `start_webserver()` (33~55행) — 서버 시작과 URI 등록

1. `HTTPD_DEFAULT_CONFIG()`로 기본 설정을 만듭니다. 기본 포트는 80입니다.
2. `httpd_start(&server, &config)`로 서버를 시작합니다.
3. 성공하면 `httpd_uri_t`로 라우팅 정보를 만들고 등록합니다.

| 필드 | 값 | 의미 |
|------|----|------|
| `.uri` | `"/hello"` | 경로 |
| `.method` | `HTTP_GET` | 허용하는 메서드 |
| `.handler` | `hello_get_handler` | 호출할 함수 |
| `.user_ctx` | `NULL` | 핸들러에 넘길 사용자 데이터(미사용) |

- 실패하면 `NULL`을 반환합니다.
- 함수 안의 지역 변수 `server`가 전역 `server`를 가립니다(섀도잉). 반환값을 전역에 대입하므로 동작은 정상입니다.

## 4. `wifi_event_handler()` (57~78행)

03과 같은 구조이며 차이는 다음과 같습니다.
- 03에 있던 reason 로그, `STA_CONNECTED` 처리, 재시도 한도 초과 에러 로그가 없습니다.
- **`IP_EVENT_STA_GOT_IP`에서** 재시도 카운터를 0으로 리셋하고 IP를 출력한 뒤, `server == NULL`이면 `start_webserver()`를 호출합니다.
- **왜 IP를 받은 뒤에 서버를 켜는가**: IP가 없으면 클라이언트가 접속할 주소가 없고, 네트워크 스택도 준비되지 않았기 때문입니다.
- 끊김 후 재접속에 성공해 `GOT_IP`가 다시 와도 `server != NULL`이면 서버를 다시 만들지 않습니다.

## 5. `app_main()` (80~118행)

03과 같은 초기화 순서(NVS → netif/이벤트 루프 → Wi-Fi 초기화 → 핸들러 등록 → 설정 → 시작)입니다. 차이는 다음과 같습니다.
- SSID/비밀번호 검증 코드가 없습니다(길이만 계산).
- 마지막 `for (;;)` 루프는 5초마다 `vTaskDelay`만 하고 상태 출력은 하지 않습니다. `app_main` 태스크를 유지하는 역할입니다.

## 확인 기준 (PASS)
- 로그에 `Got IP`, `Starting server on port: '80'`, `URI handler '/hello' registered.`가 나옵니다.
- PC나 폰이 같은 네트워크에서 `http://<ESP IP>/hello`를 열면 `Hello! I am ESP32-S3 Web Server!`가 보이고, ESP 로그에 `Sent response to /hello`가 나옵니다.
- 등록하지 않은 경로(예: `/abc`)는 404가 응답됩니다.

> 상태: 예제 README 기준 아직 실행 확인 전입니다.

## 다음 단계
- 05는 같은 서버에 `is_websocket = true`인 URI를 등록해 양방향 통신을 추가합니다.
