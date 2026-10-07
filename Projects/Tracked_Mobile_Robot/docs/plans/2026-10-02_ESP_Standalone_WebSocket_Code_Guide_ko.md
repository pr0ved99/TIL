# ESP 단독 WebSocket 상태 전송 코드 입력 안내

작성일: 2026-10-02. 상태: **입력용 기준 코드 준비. 실제 C 소스 반영·빌드·플래시·보드 검증 전**.

기준은 현재 `03_Firmware/esp32_wifi_link`와 설치된 ESP-IDF 6.0.2다.
공유기 STA 연결은 사용자 확인 완료이며, 이번 목표는 동일한 네트워크에서 ESP 자체 상태를 WebSocket으로 받는 것이다.
사용자가 코드를 입력하고 Codex가 저장 파일을 검토한 다음 사용자가 빌드·플래시한다.
개인 설정의 SSID/비밀번호와 `WIFI_LINK_USE_AP=0`은 그대로 유지한다.

## 1. 먼저 이해할 흐름

현재는 브라우저가 `/api/status`를 반복 요청한다. 이번에는 첫 화면을 HTTP로 받은 뒤 `/ws` 연결을 유지하고 ESP가 약 1초 주기로 상태를 보낸다.
AP/STA는 Wi-Fi 접속 방식이고, HTTP/WebSocket은 연결된 네트워크 위에서 데이터를 주고받는 방식이다.
기존 `/api/status`는 직접 조회용으로 남기며 새 화면은 HTTP 폴링을 하지 않는다.

```text
브라우저 -- GET / --> page_get(): 화면 전달
브라우저 -- /ws 접속 --> HTTP 서버: WebSocket 연결 수립

app_main(): 1초 대기 → ws_schedule()
                         ↓ httpd_queue_work()
HTTP 서버 task: ws_broadcast() → status_json() → 연결된 브라우저에 TEXT 전송
브라우저: JSON 확인 → 화면/수신 시각 갱신 → 수신 제한시간 재설정
```

| 함수/데이터 | 책임 |
| --- | --- |
| `status_json()` | ESP uptime·boot ID·메모리 상태를 공통 JSON으로 작성 |
| `status_get()` | 직접 `/api/status`를 열었을 때 같은 JSON 응답 |
| `ws_receive()` | 수신 제어 프레임 중 PONG을 소비하고 앱 데이터 입력은 거절 |
| `ws_schedule()` | 서버가 살아 있고 앞선 전송 작업이 없을 때만 전송 예약 |
| `ws_broadcast()` | HTTP 서버 task 안에서 연결 목록을 확인하고 상태를 전송 |
| `s_server_lock` | 예약 중 서버 핸들이 종료·해제되지 않도록 보호 |
| `s_ws_work_pending` | 미완료 전송 예약을 최대 하나로 제한하는 원자적 플래그 |
| `server_stop()` | 새 예약을 차단한 다음 HTTP 서버 종료 완료를 기다림 |
| 브라우저 `connect()/disconnect()` | 상태 수신·4초 무응답 판정·1초 뒤 재접속·오래된 연결의 이벤트 무시 |

서버 API는 모두 자동으로 thread-safe인 것이 아니다. 연결 목록 조회와 프레임 전송을 HTTP 서버 task에 모은다.
서버 시작/종료는 기존 Wi-Fi 이벤트 task가 담당한다. `server_stop()`은 mutex를 풀고 `httpd_stop()`을 호출하며, HTTP 작업은 이 mutex를 기다리지 않는다.
서버가 종료돼도 정적 플래그는 존재하고, 다음 서버 시작에서 예약 상태를 초기화한다. 생성한 JSON 버퍼는 HTTP 작업 안의 실제 전송이 끝날 때까지 살아 있다.
ESP는 이미 ESP-IDF/FreeRTOS 환경이며, 이번 작업은 STM의 FreeRTOS 전환과 무관하다.

## 2. WebSocket 기능 켜기

VS Code에서 **esp32_wifi_link 폴더**를 연 상태로 진행한다.

1. `Ctrl+Shift+P` → `ESP-IDF: SDK Configuration Editor (menuconfig)`.
2. `HTTPD_WS_SUPPORT` 또는 `WebSocket server support`를 검색해 활성화하고 저장한다.
   메뉴 위치는 `Component config → HTTP Server → WebSocket server support`다.
3. 아래 `sdkconfig.defaults` 전문도 입력한다. 기존 sdkconfig에는 menuconfig의 선택이 적용되므로 defaults 수정만으로 현재 설정이 바뀌었다고 가정하지 않는다.

대상: `03_Firmware/esp32_wifi_link/sdkconfig.defaults` 전체.

```ini
CONFIG_ESP_CONSOLE_UART_DEFAULT=y
CONFIG_ESP_CONSOLE_UART_BAUDRATE=115200
CONFIG_ESP_CONSOLE_SECONDARY_USB_SERIAL_JTAG=y
CONFIG_HTTPD_WS_SUPPORT=y
```

대상: `03_Firmware/esp32_wifi_link/main/CMakeLists.txt` 전체. 직접 사용하는 FreeRTOS 의존성을 명시한다.

```cmake
idf_component_register(
    SRCS "wifi_link_main.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_wifi esp_event esp_netif esp_http_server
        esp_timer esp_system esp_hw_support nvs_flash freertos
)
```

## 3. 앱 코드 전문

대상: `03_Firmware/esp32_wifi_link/main/wifi_link_main.c` **첫 include부터 마지막 `}`까지 전체 교체**.
`wifi_link_config.h`는 교체하지 않는다. 아래 코드는 입력용 기준이며 Codex가 실제 C 파일에 적용한 것은 아니다.

```c
#include <inttypes.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

#include "esp_event.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_random.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "nvs_flash.h"

#include "wifi_link_config.h"

#if WIFI_LINK_USE_AP != 0 && WIFI_LINK_USE_AP != 1
#error "WIFI_LINK_USE_AP must be 0 or 1"
#endif

#if !CONFIG_HTTPD_WS_SUPPORT
#error "Enable HTTPD_WS_SUPPORT in menuconfig"
#endif

#if WIFI_LINK_USE_AP
#define WIFI_LINK_MODE_NAME "AP"
#else
#define WIFI_LINK_MODE_NAME "STA"
static unsigned s_retry_count;
#endif

#define STATUS_JSON_SIZE 384U
#define WS_MAX_CLIENTS 4U
#define WS_PERIOD_MS 1000U

static const char *TAG = "wifi_link";
static httpd_handle_t s_server;
static esp_netif_t *s_netif;
static uint32_t s_boot_id;
static SemaphoreHandle_t s_server_lock;
static atomic_bool s_ws_work_pending = ATOMIC_VAR_INIT(false);

static const char PAGE[] =
    "<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>ESP Wi-Fi Link</title></head><body>"
    "<h1>ESP Wi-Fi 상태</h1><p>ESP 단독 시험 · STM 미연결</p>"
    "<p id='link'>연결 확인 중</p><pre id='data'></pre><script>"
    "const link=document.getElementById('link');"
    "const data=document.getElementById('data');"
    "let socket=null;"
    "let retryTimer=null;"
    "let watchdog=null;"
    "function scheduleReconnect(){"
    " if(retryTimer!==null)return;"
    " retryTimer=setTimeout(()=>{retryTimer=null;connect();},1000);"
    "}"
    "function disconnect(ws,reason){"
    " if(socket!==ws)return;"
    " socket=null;clearTimeout(watchdog);watchdog=null;"
    " link.textContent=reason+' · 아래 값은 마지막 수신 데이터';"
    " ws.close();scheduleReconnect();"
    "}"
    "function armWatchdog(ws){"
    " clearTimeout(watchdog);"
    " watchdog=setTimeout(()=>disconnect(ws,'상태 수신 시간 초과'),4000);"
    "}"
    "function connect(){"
    " if(socket!==null)return;"
    " link.textContent='연결 중 · 기존 표시값은 마지막 수신 데이터';"
    " const ws=new WebSocket('ws://'+location.host+'/ws');"
    " socket=ws;armWatchdog(ws);"
    " ws.onopen=()=>{"
    "  if(socket!==ws)return;"
    "  link.textContent='연결됨 · 새 상태 수신 대기';armWatchdog(ws);"
    " };"
    " ws.onmessage=(event)=>{"
    "  if(socket!==ws)return;"
    "  try{"
    "   const status=JSON.parse(event.data);"
    "   if(status.source!=='ESP_ONLY'||"
    "      !Number.isFinite(status.uptime_ms)||status.uptime_ms<0||"
    "      !Number.isInteger(status.boot_id)||status.boot_id<0||"
    "      status.boot_id>4294967295)throw new Error('invalid status');"
    "   data.textContent=JSON.stringify(status,null,2);"
    "   link.textContent='WebSocket 수신 정상 · '+new Date().toLocaleTimeString();"
    "   armWatchdog(ws);"
    "  }catch(error){disconnect(ws,'잘못된 상태 응답');}"
    " };"
    " ws.onerror=()=>disconnect(ws,'WebSocket 오류');"
    " ws.onclose=()=>disconnect(ws,'연결 끊김');"
    "}"
    "window.addEventListener('offline',()=>{"
    " if(socket!==null)disconnect(socket,'네트워크 연결 끊김');"
    "});"
    "window.addEventListener('online',()=>{"
    " clearTimeout(retryTimer);retryTimer=null;connect();"
    "});"
    "connect();</script></body></html>";

static int status_json(char *json, size_t capacity)
{
    const uint64_t uptime_ms = (uint64_t)esp_timer_get_time() / 1000U;
    const int length = snprintf(
        json, capacity,
        "{\"source\":\"ESP_ONLY\",\"mode\":\"%s\","
        "\"boot_id\":%" PRIu32 ",\"uptime_ms\":%" PRIu64 ","
        "\"free_heap_bytes\":%" PRIu32 ",\"stm_connected\":false,"
        "\"state\":null,\"reason\":null,\"left_pwm\":null,"
        "\"right_pwm\":null,\"left_cps\":null,\"right_cps\":null}",
        WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms, esp_get_free_heap_size());

    if (length < 0 || (size_t)length >= capacity) {
        return -1;
    }
    return length;
}

static esp_err_t page_get(httpd_req_t *req)
{
    ESP_ERROR_CHECK(httpd_resp_set_type(req, "text/html; charset=utf-8"));
    ESP_ERROR_CHECK(httpd_resp_set_hdr(req, "Cache-Control", "no-store"));
    return httpd_resp_send(req, PAGE, HTTPD_RESP_USE_STRLEN);
}

static esp_err_t status_get(httpd_req_t *req)
{
    char json[STATUS_JSON_SIZE];
    const int length = status_json(json, sizeof(json));
    if (length < 0) {
        return httpd_resp_send_err(
            req, HTTPD_500_INTERNAL_SERVER_ERROR, "Status buffer error");
    }

    ESP_ERROR_CHECK(httpd_resp_set_type(req, "application/json"));
    ESP_ERROR_CHECK(httpd_resp_set_hdr(req, "Cache-Control", "no-store"));
    return httpd_resp_send(req, json, length);
}

static esp_err_t ws_receive(httpd_req_t *req)
{
    /* ESP-IDF 6.0.2 handles the handshake, PING and CLOSE internally. */
    httpd_ws_frame_t frame = {0};
    esp_err_t result = httpd_ws_recv_frame(req, &frame, 0);
    if (result != ESP_OK) {
        return result;
    }

    /* This endpoint publishes status only. No application commands. */
    if (frame.type != HTTPD_WS_TYPE_PONG || frame.len > 125U) {
        return ESP_FAIL;
    }
    uint8_t payload[125];
    frame.payload = payload;
    return frame.len == 0U ? ESP_OK :
        httpd_ws_recv_frame(req, &frame, sizeof(payload));
}

static void ws_broadcast(void *arg)
{
    const httpd_handle_t server = (httpd_handle_t)arg;
    char json[STATUS_JSON_SIZE];
    const int length = status_json(json, sizeof(json));
    int clients[WS_MAX_CLIENTS];
    size_t count = WS_MAX_CLIENTS;

    if (length >= 0 &&
        httpd_get_client_list(server, &count, clients) == ESP_OK) {
        httpd_ws_frame_t frame = {
            .type = HTTPD_WS_TYPE_TEXT,
            .payload = (uint8_t *)json,
            .len = (size_t)length
        };
        for (size_t i = 0; i < count; ++i) {
            if (httpd_ws_get_fd_info(server, clients[i]) !=
                HTTPD_WS_CLIENT_WEBSOCKET) {
                continue;
            }
            if (httpd_ws_send_frame_async(server, clients[i], &frame) != ESP_OK) {
                ESP_LOGW(TAG, "WS send failed; closing fd=%d", clients[i]);
                (void)httpd_sess_trigger_close(server, clients[i]);
            }
        }
    }
    atomic_store(&s_ws_work_pending, false);
}

static void ws_schedule(void)
{
    xSemaphoreTake(s_server_lock, portMAX_DELAY);
    if (s_server != NULL && !atomic_load(&s_ws_work_pending)) {
        atomic_store(&s_ws_work_pending, true);
        if (httpd_queue_work(s_server, ws_broadcast, s_server) != ESP_OK) {
            atomic_store(&s_ws_work_pending, false);
            ESP_LOGW(TAG, "WS work queue failed");
        }
    }
    xSemaphoreGive(s_server_lock);
}

static void server_stop(void)
{
    xSemaphoreTake(s_server_lock, portMAX_DELAY);
    const httpd_handle_t server = s_server;
    s_server = NULL;
    xSemaphoreGive(s_server_lock);

    if (server != NULL) {
        ESP_ERROR_CHECK(httpd_stop(server));
        ESP_LOGI(TAG, "HTTP/WS server stopped");
    }
}

static void server_start(void)
{
    xSemaphoreTake(s_server_lock, portMAX_DELAY);
    if (s_server != NULL) {
        xSemaphoreGive(s_server_lock);
        return;
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.max_open_sockets = WS_MAX_CLIENTS;
    config.lru_purge_enable = true;
    config.recv_wait_timeout = 1;
    config.send_wait_timeout = 1;
    ESP_ERROR_CHECK(httpd_start(&s_server, &config));

    const httpd_uri_t page_uri = {
        .uri = "/",
        .method = HTTP_GET,
        .handler = page_get
    };
    const httpd_uri_t status_uri = {
        .uri = "/api/status",
        .method = HTTP_GET,
        .handler = status_get
    };
    const httpd_uri_t ws_uri = {
        .uri = "/ws",
        .method = HTTP_GET,
        .handler = ws_receive,
        .is_websocket = true,
        .handle_ws_control_frames = false
    };
    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &page_uri));
    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &status_uri));
    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &ws_uri));
    atomic_store(&s_ws_work_pending, false);
    xSemaphoreGive(s_server_lock);

    esp_netif_ip_info_t info;
    ESP_ERROR_CHECK(esp_netif_get_ip_info(s_netif, &info));
    ESP_LOGI(TAG, "Open http://" IPSTR "/", IP2STR(&info.ip));
    ESP_LOGI(TAG, "WebSocket status: /ws, period=%u ms", WS_PERIOD_MS);
}

static void wifi_event(
    void *arg, esp_event_base_t base, int32_t id, void *event_data)
{
    (void)arg;
    (void)event_data;

#if WIFI_LINK_USE_AP
    if (base == WIFI_EVENT && id == WIFI_EVENT_AP_START) {
        server_start();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_AP_STOP) {
        server_stop();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_AP_STACONNECTED) {
        ESP_LOGI(TAG, "AP client connected");
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_AP_STADISCONNECTED) {
        ESP_LOGI(TAG, "AP client disconnected");
    }
#else
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        ESP_ERROR_CHECK(esp_wifi_connect());
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        server_stop();
        if (s_retry_count < 5U) {
            ++s_retry_count;
            ESP_LOGW(TAG, "STA reconnect attempt %u/5", s_retry_count);
            ESP_ERROR_CHECK(esp_wifi_connect());
        } else {
            ESP_LOGE(TAG, "STA retry limit reached; reboot to retry");
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        s_retry_count = 0U;
        server_start();
    }
#endif
}

void app_main(void)
{
    const size_t ssid_length = strlen(WIFI_LINK_SSID);
    const size_t password_length = strlen(WIFI_LINK_PASSWORD);

    if (ssid_length == 0U || ssid_length > 32U ||
        password_length < 8U || password_length > 63U ||
        strcmp(WIFI_LINK_PASSWORD, "CHANGE_ME") == 0) {
        ESP_LOGE(TAG, "Set a valid private SSID/password in wifi_link_config.h");
        return;
    }

    s_server_lock = xSemaphoreCreateMutex();
    if (s_server_lock == NULL) {
        ESP_LOGE(TAG, "Server mutex allocation failed");
        return;
    }

    esp_err_t result = nvs_flash_init();
    if (result == ESP_ERR_NVS_NO_FREE_PAGES ||
        result == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        result = nvs_flash_init();
    }
    ESP_ERROR_CHECK(result);

    s_boot_id = esp_random();
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

#if WIFI_LINK_USE_AP
    s_netif = esp_netif_create_default_wifi_ap();
#else
    s_netif = esp_netif_create_default_wifi_sta();
#endif
    if (s_netif == NULL) {
        ESP_LOGE(TAG, "Network interface allocation failed");
        return;
    }

    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_event_handler_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event, NULL));

    wifi_config_t wifi = {0};
#if WIFI_LINK_USE_AP
    memcpy(wifi.ap.ssid, WIFI_LINK_SSID, ssid_length);
    memcpy(wifi.ap.password, WIFI_LINK_PASSWORD, password_length);
    wifi.ap.ssid_len = (uint8_t)ssid_length;
    wifi.ap.channel = 6;
    wifi.ap.max_connection = 2;
    wifi.ap.authmode = WIFI_AUTH_WPA2_PSK;
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi));
#else
    memcpy(wifi.sta.ssid, WIFI_LINK_SSID, ssid_length);
    memcpy(wifi.sta.password, WIFI_LINK_PASSWORD, password_length);
    wifi.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    ESP_ERROR_CHECK(esp_event_handler_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi));
#endif

    ESP_LOGI(TAG, "ESP-only Wi-Fi test: mode=%s boot_id=%" PRIu32,
             WIFI_LINK_MODE_NAME, s_boot_id);
    ESP_ERROR_CHECK(esp_wifi_start());

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(WS_PERIOD_MS));
        ws_schedule();
    }
}
```

## 4. 정상 경로와 실패 경로

- 정상: STA IP 확보 → 서버 시작 → 페이지/WS 접속 → 1초마다 ESP 상태 생성·전송 → 화면 갱신. 같은 부팅에서 boot_id는 유지한다.
- 브라우저: 열려 있는 것처럼 보이는 연결이라도 유효한 상태가 4초 동안 없으면 마지막 값에 시간 초과 표시를 붙이고 연결을 닫는다. 그 뒤 1초 후 재접속한다. 이 수치는 브라우저 전경 실행 기준의 설계값이며 정밀 실시간 보장은 아니다.
- 오래된 연결: `socket!==ws`이면 뒤늦게 온 메시지·close·error를 무시해 새 연결의 화면/타이머를 바꾸지 않는다. 연결 성공만으로 마지막 데이터를 최신으로 표시하지 않는다.
- ESP: 실패한 소켓은 닫고 다른 클라이언트를 계속 처리한다. 앞선 전송 작업이 끝나지 않았으면 새 작업을 쌓지 않는다. 샘플 전송 주기는 부하에 따라 지연될 수 있다.
- 공유기 연결 유실: 기존 STA 로직은 최대 5회 재시도 후 멈춘다. **브라우저의 자동 재접속과 ESP의 공유기 재접속 정책은 별개**다. 5회 소진 후에는 공유기 복구 뒤 ESP를 재부팅해야 한다. 무제한 STA 복구를 이번 코드의 성과로 주장하지 않는다.
- 재부팅: boot_id가 새로 생성된다. DHCP로 IP가 바뀌면 모니터에 나온 새 주소로 페이지를 열어야 한다.

HTTP 폴링도 현재 상태 조회에는 사용할 수 있다. 이번 WebSocket 확장은 연결 수명과 서버 주도 전송을 학습하고, 이후 실제 STM 상태 전달에 적용할 목적이다. 이번에 성능 향상을 계측했다고 주장하지 않는다.
현재 `/ws`는 상태 전송 전용이다. STM UART·ARM·구동 명령을 추가하지 않고, 미연결 STM 값은 null로 유지한다. 무선 명령은 별도 W5의 유효시간·세션·연결 유실 검증 대상으로 남긴다.

## 5. 입력 후 검토와 보드 검증

먼저 위 세 파일을 입력·저장하고 Codex에 검토를 요청한다. Codex는 실제 저장 파일을 다시 확인한다.
사용자 빌드 성공과 보드 실행 결과가 나오기 전에는 구현 완료/PASS로 기록하지 않는다.

저장 검토가 끝나면 사용자가 기존 COM4, UART/esptool 설정으로 Build → Flash → Monitor를 진행한다.
ESP 단독 USB 전원 조건이며 기존 로봇 전원/모터 시험을 동시에 재개하지 않는다.

| 확인 | 완료 기준 |
| --- | --- |
| WS-1 연결·전송 | 모니터에 `/ws, period=1000 ms`; 화면 `WebSocket 수신 정상`, mode=STA, uptime 반복 증가 |
| WS-2 전송 경로 | 브라우저 개발자도구 Network의 WS에서 `/ws`와 연속 수신 메시지 확인. 반복 `/api/status` 요청 없음 |
| WS-3 연결만 재수립 | 브라우저 콘솔에서 `socket.close()` 실행 → 자동 재접속·수신 재개, ESP 재부팅 없이 boot_id 유지 |
| WS-4 무응답·전원 복구 | ESP 단독 USB 전원을 분리하면 기존 값 보존 + 연결 끊김/시간 초과 표시. 전원 복구 뒤 같은 IP라면 자동 수신 재개; boot_id 변경은 정상 |
| 직접 HTTP 조회 | 같은 ESP 주소의 `/api/status`를 직접 열면 유효한 JSON 반환 |

WS-4는 ESP 전원 재인가 시험이며 공유기 STA 재시도 한계 검증을 대신하지 않는다. 실제 실행 시 한 시험씩 진행하고 결과를 기다린다.

## 6. 사전 검토 범위

- ESP-IDF 6.0.2의 `esp_http_server.h`, `httpd_main.c`, `httpd_ws.c`, `httpd_uri.c`, `httpd_parse.c` 및 `ws_echo_server`를 확인했다.
- 이 버전의 WebSocket handshake는 URI handler를 호출하지 않고 SDK에서 완료한다. PING/CLOSE 자동 처리와 PONG handler 전달을 실제 소스에서 확인했다. 이전 버전의 GET 분기 예제를 그대로 적용하지 않는다.
- [브라우저 모의 검사](../../03_Firmware/tests/test_wifi_websocket_page.js) **11개 PASS**. 이 문서의 C 문자열에서 JavaScript를 추출해 Node.js 22.22.0에서 실행했다. 정상 표시, 무응답, 중복 재접속, 이전 연결 이벤트, 잘못된 JSON/상태, 재부팅 ID 변경을 확인했다.
- 설치된 header에서 사용한 HTTP 서버 API 13개 선언을 대조했다. 이는 컴파일 검사를 대신하지 않는다. 실제 C 파일은 기존 HTTP 폴링 상태이며 C 컴파일·실제 Wi-Fi/WebSocket·전원 복구 검증은 사용자 입력 후 진행한다.

근거: [ESP-IDF 6.0.2 HTTP/WebSocket 서버](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/api-reference/protocols/esp_http_server.html), [현재 STA 연결 기록](../progress/2026-10-02_progress.md#공유기-sta-연결-확인).
