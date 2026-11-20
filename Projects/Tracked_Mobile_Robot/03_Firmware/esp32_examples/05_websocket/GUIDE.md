# 05 WebSocket 수신·브로드캐스트 — 코드 가이드

대상 소스: [`main/websocket_main.c`](main/websocket_main.c), 설정: `main/wifi_config.h`

갱신일: **2026-10-06**. 04의 HTTP 서버에 `/ws` WebSocket 엔드포인트를 추가한 예제입니다. 처음의 1:1 Echo에서 확장해, 현재는 클라이언트가 보낸 텍스트를 로그로 출력하고 연결된 WebSocket 클라이언트들에게 전달합니다.

사용자는 두 브라우저 탭의 기본 메시지 전달을 확인했습니다. 실제 앱의 STM 연동(W4)은 다음 단계이며 [오늘 진행 기록](../../../docs/progress/2026-10-06_progress.md)과 [W4 계획](../../../docs/plans/2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md)을 따릅니다.

> **빌드 전 필수**: `sdkconfig`에서 `CONFIG_HTTPD_WS_SUPPORT=y`를 켜야 합니다. `menuconfig`에서 `Component config → HTTP Server → WebSocket server support`를 체크하고 저장합니다. 꺼져 있으면 `httpd_ws_*` 관련 코드가 컴파일되지 않습니다.

## 전체 구조

```text
app_main → Wi-Fi 초기화/시작
 → (이벤트) GOT_IP → start_webserver()
        └─ httpd_start → "/ws" 를 WebSocket URI로 등록
 → 클라이언트가 ws://<ESP IP>/ws 접속
        ├─ 최초 GET(핸드셰이크) → websocket_handler: 로그 후 반환
        └─ 이후 메시지마다 websocket_handler: 수신 → 로그 → broadcast_text()
              → 연결 목록 → WebSocket fd만 선택 → 각 클라이언트에 송신
```

## 1. 상단 정의

| 항목 | 역할 |
|------|------|
| `esp_http_server.h` | HTTP 서버와 WebSocket API |
| `MAX_RETRY`, `STATUS_PERIOD_MS` | 재접속 횟수와 메인 루프 주기 |
| `s_retry_count` | 재시도 횟수 |
| `server` | 서버 핸들. `NULL`이면 서버 미실행 |

### `broadcast_text()` — 수신 메시지를 여러 화면에 전달

현재 저장본 27행에서 시작합니다.

1. 서버 핸들이 `NULL`이면 반환합니다.
2. 문자열 포인터·`strlen()` 길이·TEXT 타입을 `httpd_ws_frame_t`에 담습니다.
3. `httpd_get_client_list()`로 최대 16개 fd를 얻습니다. 이 배열 크기가 실제 서버 동시 접속 수 보장은 아닙니다.
4. `httpd_ws_get_fd_info()`로 WebSocket 연결을 골라 `httpd_ws_send_frame_async()`를 호출합니다.

현재는 클라이언트별 전송 반환값을 처리하지 않습니다. UART task에서 이 함수를 호출해도 서버 작업의 동기화·payload 수명·서버 종료가 자동으로 해결되는 것은 아닙니다. 본 작업의 예약·동기화는 별도로 설계합니다.

## 2. `websocket_handler()` — 핵심 함수

`/ws`에 요청이 올 때마다 서버가 호출합니다.

### 2-1. 핸드셰이크 구분
- WebSocket 연결은 처음에 **HTTP GET 요청**으로 시작합니다. `req->method == HTTP_GET`이면 연결이 열린 순간입니다.
- 이때는 로그만 남기고 `ESP_OK`를 반환합니다. 업그레이드 응답은 `esp_http_server`가 처리합니다.

### 2-2. 프레임 준비
- `httpd_ws_frame_t ws_pkt`를 0으로 초기화합니다.
- 128바이트 스택 버퍼 `buf`를 `ws_pkt.payload`로 연결하고, 타입을 `HTTPD_WS_TYPE_TEXT`로 지정합니다.
- **역할**: 수신할 데이터를 담을 그릇을 만드는 단계입니다.

### 2-3. 수신
- `httpd_ws_recv_frame(req, &ws_pkt, 128)`: 최대 128바이트를 `buf`로 읽어옵니다.
- 실패하면 에러 로그를 남기고 에러 코드를 반환합니다.

### 2-4. 출력
- `%s`로 payload를 문자열 출력합니다.
- 주의: 128바이트를 가득 채워 받으면 널 종결이 없어 `%s`와 `broadcast_text()`의 `strlen()`이 버퍼 밖을 읽을 수 있습니다. 길이·타입 검사와 NUL 종료가 본 작업 전 검토 항목입니다. 이번 문서 정리에서 소스는 수정하지 않았습니다.

### 2-5. 브로드캐스트 호출
- `broadcast_text((const char *)ws_pkt.payload)`로 수신 문자열을 전달합니다.
- 이후 핸들러는 `ESP_OK`를 반환합니다. 현재 모든 클라이언트 전송의 성공을 확인한 결과는 아닙니다.

## 3. `start_webserver()` — 서버 시작과 WebSocket 등록

1. `HTTPD_DEFAULT_CONFIG()`로 기본 설정(포트 80)을 만듭니다.
2. `httpd_start()`로 서버를 시작합니다.
3. `httpd_uri_t`를 채워 `/ws`를 등록합니다.

| 필드 | 값 | 의미 |
|------|----|------|
| `.uri` | `"/ws"` | WebSocket 접속 경로 |
| `.method` | `HTTP_GET` | 핸드셰이크는 GET으로 시작 |
| `.handler` | `websocket_handler` | 호출할 함수 |
| `.is_websocket` | `true` | **핵심.** 이 URI를 WebSocket으로 업그레이드해 처리 |

- 04와의 가장 큰 차이가 `.is_websocket = true`입니다.
- 함수 안의 지역 변수 `server`가 전역 `server`를 가립니다(섀도잉). 반환값을 전역에 대입하므로 동작은 정상입니다.

## 4. `wifi_event_handler()`

| 이벤트 | 동작 |
|--------|------|
| `STA_START` | `esp_wifi_connect()`로 접속 시작 |
| `STA_DISCONNECTED` | 5회까지 재접속 (이후에는 시도 안 함) |
| `GOT_IP` | 카운터 리셋, IP 로그, `server == NULL`이면 `start_webserver()` 호출 |

- **IP를 받은 뒤 서버를 켜는 이유**: 클라이언트가 접속할 주소가 있어야 하기 때문입니다.
- 03과 달리 끊김 reason 로그는 없고, 재시도 한도 초과 시 별도 경고도 없습니다.

## 5. `app_main()`

03·04와 같은 초기화 순서입니다.
1. NVS 초기화 (필요하면 지우고 재초기화)
2. `esp_netif_init`, 기본 이벤트 루프, STA 인터페이스 생성
3. `esp_wifi_init`, 저장소를 RAM으로 설정
4. 이벤트 핸들러 등록(Wi-Fi 이벤트 전체, IP 획득 이벤트)
5. SSID/비밀번호, WPA2 이상, WPA3(SAE)와 PMF 설정
6. `set_mode(STA)` → `set_config` → `esp_wifi_start()`
7. `for (;;) vTaskDelay(...)`로 메인 태스크 유지

## 6. 알려진 한계 (학습용 예제 범위)
- 수신 버퍼가 128바이트로 고정이며, 그보다 큰 메시지는 에러로 처리됩니다.
- 보통은 먼저 길이를 얻은 뒤(`max_len = 0`으로 호출) 그 크기만큼 버퍼를 준비해 받습니다.
- 연결 유실이나 입력 타임아웃 처리가 없습니다. 이 입력을 모터 명령에 연결하려면 STM 쪽의 명령 타임아웃과 안전 게이트 설계가 먼저 필요합니다.

## 기본 동작 확인 방법과 10/6 결과
- 빌드 에러가 없습니다(`CONFIG_HTTPD_WS_SUPPORT=y` 확인).
- 로그에 `Got IP`, `Starting server on port: '80'`, `WebSocket handler '/ws' registered.`가 나옵니다.
- 같은 네트워크의 브라우저 탭 두 개에서 각각 다음 연결 코드를 실행합니다. 연결 완료 후 탭 A에서 `ws.send("DOWN")`을 입력하면 양쪽 콘솔에서 해당 문자열을 확인할 수 있습니다. 따옴표 없는 `DOWN`은 JavaScript 변수로 해석됩니다.

```javascript
const ws = new WebSocket("ws://<ESP IP>/ws");
ws.onopen    = () => console.log("connected");
ws.onmessage = (e) => console.log("broadcast:", e.data);
```

> 10/6 상태: 사용자가 브라우저 입력 오류 해결과 탭 A→B 기본 메시지 수신을 확인했습니다. 원본 실행 로그·바이너리 해시는 이번 정리에서 확인하지 않았습니다. 이 완료 결과를 유지하며 UART·실제 앱 상태 전송·재접속·장시간 동작의 PASS로 확대하지 않습니다.
