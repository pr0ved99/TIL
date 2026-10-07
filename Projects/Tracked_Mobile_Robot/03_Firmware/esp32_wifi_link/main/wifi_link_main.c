#include <inttypes.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "driver/uart.h"

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

#define STATUS_JSON_SIZE 1024U
#define WS_MAX_CLIENTS 4U
#define WS_PERIOD_MS 1000U
#define STM_TEL_STALE_MS 500U

static const char *TAG = "wifi_link";
static httpd_handle_t s_server;
static esp_netif_t *s_netif;
static uint32_t s_boot_id;
static SemaphoreHandle_t s_server_lock;
static atomic_bool s_ws_work_pending = ATOMIC_VAR_INIT(false);

typedef struct {
    uint32_t t_ms;
    char state[16];
    char reason[32];
    uint32_t command_age_ms;
    uint32_t last_seq;
    int32_t vx_mmps;
    int32_t w_mradps;
    int32_t left_pwm;
    int32_t right_pwm;
    int32_t left_cps;
    int32_t right_cps;
    uint32_t batt_mv;
    uint32_t drop;
    uint32_t err;

    uint64_t rx_ms;
    bool valid;
} stm_telemetry_t;

static SemaphoreHandle_t s_stm_lock;
static stm_telemetry_t s_stm_telemetry;
static uint32_t s_stm_tel_count;
/* RX task publishes a static string; s_stm_lock protects the pointer. */
static const char *s_stm_startup_status = "SETTLE";

static const char PAGE[] =
    "<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>ESP Wi-Fi Link</title></head><body>"
    "<h1>로봇 상태</h1><p>STM32 UART → ESP32 Wi-Fi → 브라우저</p>"
    "<p id='link'>연결 확인 중</p>"
    "<p id='stm'>STM TEL 수신 대기</p>"
    "<p id='startup'>부팅 응답 새 상태 확인 대기</p>"
    "<p>READY는 이번 ESP 부팅 때 응답 확인을 마쳤다는 뜻입니다. "
    "현재 통신 상태는 TEL 표시에서 확인하세요.</p>"
    "<pre id='data'></pre><script>"
    "const link=document.getElementById('link');"
    "const stm=document.getElementById('stm');"
    "const startup=document.getElementById('startup');"
    "const data=document.getElementById('data');"
    "let socket=null;"
    "let retryTimer=null;"
    "let watchdog=null;"
    "const startupLabels={"
    " SETTLE:'초기 안정 대기',SYNC_WAIT:'UART 줄 동기화 대기',"
    " WAIT_DISARM_ACK:'DISARM 응답 대기',WAIT_PONG:'PING 응답 대기',"
    " READY:'완료 (READY)',FAILED:'실패 (FAILED)'"
    "};"
    "function validStatus(s){"
    " const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;"
    " const i32=v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647;"
    " const ms=v=>Number.isSafeInteger(v)&&v>=0;"
    " if(!s||typeof s!=='object'||Array.isArray(s)||"
    "    !['ESP_ONLY','STM_UART'].includes(s.source)||"
    "    !['AP','STA'].includes(s.mode)||"
    "    !['SETTLE','SYNC_WAIT','WAIT_DISARM_ACK',"
    "      'WAIT_PONG','READY','FAILED'].includes(s.startup_state)||"
    "    !u32(s.boot_id)||!ms(s.uptime_ms)||!u32(s.free_heap_bytes)||"
    "    !u32(s.tel_count)||!u32(s.stm_age_limit_ms)||s.stm_age_limit_ms===0||"
    "    typeof s.stm_connected!=='boolean'||typeof s.stm_stale!=='boolean'||"
    "    s.batt_mv!==null||s.battery_available!==false)return false;"
    " if(s.source==='ESP_ONLY'){"
    "  return !s.stm_connected&&!s.stm_stale&&s.stm_age_ms===null&&"
    "   s.tel_count===0&&['stm_t_ms','state','reason','command_age_ms',"
    "   'last_seq','vx_mmps','w_mradps','left_pwm','right_pwm',"
    "   'left_cps','right_cps','drop','err'].every(k=>s[k]===null);"
    " }"
    " return ms(s.stm_age_ms)&&"
    "  s.stm_connected===(s.stm_age_ms<=s.stm_age_limit_ms)&&"
    "  s.stm_stale===!s.stm_connected&&u32(s.stm_t_ms)&&"
    "  ['DISARMED','ARMED','FAULT'].includes(s.state)&&"
    "  typeof s.reason==='string'&&/^[A-Z0-9_]{1,31}$/.test(s.reason)&&"
    "  ['command_age_ms','last_seq','drop','err'].every(k=>u32(s[k]))&&"
    "  ['vx_mmps','w_mradps','left_pwm','right_pwm',"
    "   'left_cps','right_cps'].every(k=>i32(s[k]))&&"
    "  Math.abs(s.left_pwm)<=1000&&Math.abs(s.right_pwm)<=1000;"
    "}"
    "function scheduleReconnect(){"
    " if(retryTimer!==null)return;"
    " retryTimer=setTimeout(()=>{retryTimer=null;connect();},1000);"
    "}"
    "function disconnect(ws,reason){"
    " if(socket!==ws)return;"
    " socket=null;clearTimeout(watchdog);watchdog=null;"
    " link.textContent=reason+' · 아래 값은 마지막 수신 데이터';"
    " stm.textContent='STM 상태 확인 불가 · 아래 STM 값은 마지막 수신 데이터';"
    " startup.textContent='부팅 응답 확인 불가 · 아래 값은 마지막 수신 데이터';"
    " ws.close();scheduleReconnect();"
    "}"
    "function armWatchdog(ws){"
    " clearTimeout(watchdog);"
    " watchdog=setTimeout(()=>disconnect(ws,'상태 수신 시간 초과'),4000);"
    "}"
    "function connect(){"
    " if(socket!==null)return;"
    " link.textContent='연결 중 · 기존 표시값은 마지막 수신 데이터';"
    " stm.textContent='STM 새 상태 확인 대기 · 기존 값은 마지막 수신 데이터';"
    " startup.textContent='부팅 응답 새 상태 확인 대기 · 기존 값은 마지막 수신 데이터';"
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
    "   if(!validStatus(status))throw new Error('invalid status');"
    "   data.textContent=JSON.stringify(status,null,2);"
    "   link.textContent='WebSocket 수신 정상 · '+new Date().toLocaleTimeString();"
    "   startup.textContent='이번 ESP 부팅의 응답 확인: '+startupLabels[status.startup_state];"
    "   if(status.source==='ESP_ONLY'){"
    "    stm.textContent='STM TEL 아직 수신 없음';"
    "   }else if(status.stm_stale){"
    "    stm.textContent='STM TEL 수신 중단 · '+status.stm_age_ms+"
    "     ' ms · 아래 STM 값은 마지막 정상 TEL';"
    "   }else{"
    "    stm.textContent='STM TEL 수신 정상 · '+status.state+' / '+status.reason;"
    "   }"
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
    stm_telemetry_t tel;
    uint32_t tel_count;
    const char *startup_state;

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    tel = s_stm_telemetry;
    tel_count = s_stm_tel_count;
    startup_state = s_stm_startup_status;
    xSemaphoreGive(s_stm_lock);

    /* Snapshot을 복사한 뒤 시각을 읽어 rx_ms보다 앞서지 않게 한다. */
    const uint64_t uptime_ms = (uint64_t)esp_timer_get_time() / 1000U;
    const uint64_t age_ms = tel.valid ? uptime_ms - tel.rx_ms : 0U;
    const bool fresh = tel.valid && age_ms <= STM_TEL_STALE_MS;
    int length;

    if (!tel.valid) {
        length = snprintf(
            json, capacity,
            "{\"source\":\"ESP_ONLY\",\"mode\":\"%s\","
            "\"boot_id\":%" PRIu32 ",\"uptime_ms\":%" PRIu64 ","
            "\"free_heap_bytes\":%" PRIu32 ","
            "\"startup_state\":\"%s\","
            "\"stm_connected\":false,\"stm_stale\":false,"
            "\"stm_age_ms\":null,\"stm_age_limit_ms\":%u,"
            "\"tel_count\":0,\"stm_t_ms\":null,"
            "\"state\":null,\"reason\":null,"
            "\"command_age_ms\":null,\"last_seq\":null,"
            "\"vx_mmps\":null,\"w_mradps\":null,"
            "\"left_pwm\":null,\"right_pwm\":null,"
            "\"left_cps\":null,\"right_cps\":null,"
            "\"batt_mv\":null,\"battery_available\":false,"
            "\"drop\":null,\"err\":null}",
            WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms,
            esp_get_free_heap_size(), startup_state, STM_TEL_STALE_MS);
    } else {
        length = snprintf(
            json, capacity,
            "{\"source\":\"STM_UART\",\"mode\":\"%s\","
            "\"boot_id\":%" PRIu32 ",\"uptime_ms\":%" PRIu64 ","
            "\"free_heap_bytes\":%" PRIu32 ","
            "\"startup_state\":\"%s\","
            "\"stm_connected\":%s,\"stm_stale\":%s,"
            "\"stm_age_ms\":%" PRIu64 ",\"stm_age_limit_ms\":%u,"
            "\"tel_count\":%" PRIu32 ",\"stm_t_ms\":%" PRIu32 ","
            "\"state\":\"%s\",\"reason\":\"%s\","
            "\"command_age_ms\":%" PRIu32 ",\"last_seq\":%" PRIu32 ","
            "\"vx_mmps\":%" PRIi32 ",\"w_mradps\":%" PRIi32 ","
            "\"left_pwm\":%" PRIi32 ",\"right_pwm\":%" PRIi32 ","
            "\"left_cps\":%" PRIi32 ",\"right_cps\":%" PRIi32 ","
            "\"batt_mv\":null,\"battery_available\":false,"
            "\"drop\":%" PRIu32 ",\"err\":%" PRIu32 "}",
            WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms,
            esp_get_free_heap_size(), startup_state,
            fresh ? "true" : "false", fresh ? "false" : "true",
            age_ms, STM_TEL_STALE_MS, tel_count, tel.t_ms,
            tel.state, tel.reason, tel.command_age_ms, tel.last_seq,
            tel.vx_mmps, tel.w_mradps, tel.left_pwm, tel.right_pwm,
            tel.left_cps, tel.right_cps, tel.drop, tel.err);
    }

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
            for (size_t i = 0;i < count; ++i) {
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
    config.recv_wait_timeout = 2;
    config.send_wait_timeout = 2;
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

#define STM_UART_PORT UART_NUM_1
#define STM_UART_TX_PIN 17
#define STM_UART_RX_PIN 18
#define STM_UART_RX_BUFFER_SIZE 1024
#define STM_UART_LINE_SIZE 384U

/* 이 수신 상태는 stm_uart_rx_task만 사용한다. */
static char s_stm_rx_line[STM_UART_LINE_SIZE];
static size_t s_stm_rx_length;

/* 수신 시작 시 이미 전송 중인 첫 줄은 버린다. */
static bool s_stm_discard_until_lf = true;

static void stm_uart_init(void)
{
    const uart_config_t config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT
    };

    ESP_ERROR_CHECK(uart_driver_install(
        STM_UART_PORT, STM_UART_RX_BUFFER_SIZE,
        0, 0, NULL, 0));
    
    ESP_ERROR_CHECK(uart_param_config(STM_UART_PORT, &config));

    ESP_ERROR_CHECK(uart_set_pin(
        STM_UART_PORT,
        STM_UART_TX_PIN, STM_UART_RX_PIN,
        UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));

    ESP_LOGI(TAG, "STM UART RX ready: TX=GPIO17 RX=GPIO18 115200/8N1");
}

static const char *stm_find_field_value(
    const char *line, const char *key)
{
    const size_t key_length = strlen(key);
    const char *field = line;
    const char *value = NULL;

    while (*field != '\0') {
        if (strncmp(field, key, key_length) == 0) {
            if (value != NULL) {
                return NULL;
            }
            value = field + key_length;
        }

        const char *comma = strchr(field, ',');
        if (comma == NULL) {
            break;
        }
        field = comma + 1;
    }

    return value;
}

static bool stm_parse_u32_field(
    const char *line, const char *key, uint32_t *out)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL || *pos < '0' || *pos > '9') {
        return false;
    }

    uint32_t value = 0U;

    while (*pos >= '0' && *pos <= '9') {
        const uint32_t digit = (uint32_t)(*pos - '0');
        if (value > (UINT32_MAX - digit) / 10U) {
            return false;
        }
        value = value * 10U + digit;
        ++pos;
    }

    if (*pos != ',' && *pos != '\0') {
        return false;
    }

    *out = value;
    return true;
}

static bool stm_parse_i32_field(
    const char *line, const char *key, int32_t *out)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL) {
        return false;
    }

    const bool negative = *pos == '-';
    if (negative) {
        ++pos;
    }
    if (*pos < '0' || *pos > '9') {
        return false;
    }

    const uint32_t limit =
        negative ? 2147483648U : 2147483647U;
    uint32_t magnitude = 0U;

    while (*pos >= '0' && *pos <= '9') {
        const uint32_t digit = (uint32_t)(*pos - '0');
        if (magnitude > (limit - digit) / 10U) {
            return false;
        }
        magnitude = magnitude * 10U + digit;
        ++pos;
    }

    if (*pos != ',' && *pos != '\0') {
        return false;
    }

    if (negative) {
        *out = magnitude == 2147483648U
            ? INT32_MIN : -(int32_t)magnitude;
    } else {
        *out = (int32_t)magnitude;
    }

    return true;
}

static bool stm_parse_text_field(
    const char *line, const char *key,
    char *out, size_t capacity)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL) {
        return false;
    }

    const size_t length = strcspn(pos, ",");
    if (length == 0U || length >= capacity) {
        return false;
    }

    for (size_t i = 0U; i < length; ++i) {
        const char c = pos[i];
        if (!((c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || c == '_')) {
            return false;
        }
    }

    memcpy(out, pos, length);
    out[length] = '\0';
    return true;
}

static bool stm_parse_tel(
    const char *line, stm_telemetry_t *out)
{
    if (line == NULL || out == NULL ||
        strncmp(line, "TEL,", 4) != 0) {
        return false;
    }

    const size_t length = strlen(line);
    if (line[length - 1U] == ',' ||
        strstr(line, ",,") != NULL) {
        return false;
    }

    /* 현재 TEL 계약은 14개 필드다. */
    size_t field_count = 0U;
    for (const char *pos = line; *pos != '\0'; ++pos) {
        if (*pos == ',') {
            ++field_count;
        }
    }
    if (field_count != 14U) {
        return false;
    }

    const bool fields_ok =
        stm_parse_u32_field(line, "t_ms=", &out->t_ms) &&
        stm_parse_text_field(
            line, "state=", out->state, sizeof(out->state)) &&
        stm_parse_text_field(
            line, "reason=", out->reason, sizeof(out->reason)) &&
        stm_parse_u32_field(
            line, "command_age_ms=", &out->command_age_ms) &&
        stm_parse_u32_field(line, "last_seq=", &out->last_seq) &&
        stm_parse_i32_field(line, "vx_mmps=", &out->vx_mmps) &&
        stm_parse_i32_field(line, "w_mradps=", &out->w_mradps) &&
        stm_parse_i32_field(line, "left_pwm=", &out->left_pwm) &&
        stm_parse_i32_field(line, "right_pwm=", &out->right_pwm) &&
        stm_parse_i32_field(line, "left_cps=", &out->left_cps) &&
        stm_parse_i32_field(line, "right_cps=", &out->right_cps) &&
        stm_parse_u32_field(line, "batt_mv=", &out->batt_mv) &&
        stm_parse_u32_field(line, "drop=", &out->drop) &&
        stm_parse_u32_field(line, "err=", &out->err);

    if (!fields_ok) {
        return false;
    }

    const bool state_ok =
        strcmp(out->state, "DISARMED") == 0 ||
        strcmp(out->state, "ARMED") == 0 ||
        strcmp(out->state, "FAULT") == 0;

    return state_ok &&
        out->left_pwm >= -1000 && out->left_pwm <= 1000 &&
        out->right_pwm >= -1000 && out->right_pwm <= 1000;
}

#define STM_STARTUP_SETTLE_MS 500U
#define STM_STARTUP_SYNC_WAIT_MS 100U
#define STM_STARTUP_RESPONSE_MS 500U
#define STM_STARTUP_MAX_ATTEMPTS 3U

typedef enum {
    STM_STARTUP_SETTLE,
    STM_STARTUP_SYNC_WAIT,
    STM_STARTUP_WAIT_DISARM_ACK,
    STM_STARTUP_WAIT_PONG,
    STM_STARTUP_READY,
    STM_STARTUP_FAILED
} stm_startup_state_t;

/* 아래 상태는 stm_uart_rx_task만 읽고 변경한다. */
typedef struct {
    stm_startup_state_t state;
    uint64_t phase_ms;
    uint32_t disarm_seq;
    uint32_t ping_seq;
    unsigned attempts;
    bool disarm_ack;
    bool pong;
} stm_startup_t;

static stm_startup_t s_stm_startup;

static void stm_startup_fail(const char *reason)
{
    if (s_stm_startup.state == STM_STARTUP_FAILED) {
        return;
    }

    s_stm_startup.state = STM_STARTUP_FAILED;
    ESP_LOGE(TAG, "STARTUP FAILED: %s", reason);
}

static void stm_startup_begin(void)
{
    const uint32_t seq = esp_random();

    s_stm_startup = (stm_startup_t) {
        .state = STM_STARTUP_SETTLE,
        .phase_ms = (uint64_t)esp_timer_get_time() / 1000U,
        .disarm_seq = seq,
        .ping_seq = seq + 1U
    };

    ESP_LOGI(
        TAG,
        "STARTUP: settle; DISARM seq=%" PRIu32
        " PING seq=%" PRIu32,
        s_stm_startup.disarm_seq,
        s_stm_startup.ping_seq);
}

static void stm_startup_send_request(bool ping, uint64_t now_ms)
{
    const char *command = ping ? "PING" : "DISARM";
    const uint32_t seq = ping
        ? s_stm_startup.ping_seq
        : s_stm_startup.disarm_seq;

    char frame[48];
    const int length = snprintf(
        frame, sizeof(frame),
        "%s,seq=%" PRIu32 "\n", command, seq);

    if (length <= 0 || (size_t)length >= sizeof(frame)) {
        stm_startup_fail("request formatting failed");
        return;
    }

    if (uart_write_bytes(
            STM_UART_PORT, frame, (size_t)length) != length) {
        stm_startup_fail("request TX failed");
        return;
    }

    s_stm_startup.state = ping
        ? STM_STARTUP_WAIT_PONG
        : STM_STARTUP_WAIT_DISARM_ACK;
    s_stm_startup.phase_ms = now_ms;
    s_stm_startup.disarm_ack = false;
    s_stm_startup.pong = false;

    ESP_LOGI(
        TAG,
        "TX UART1: %s,seq=%" PRIu32 " attempt=%u",
        command, seq, s_stm_startup.attempts);
}

static void stm_startup_retry(bool ping, uint64_t now_ms)
{
    if (now_ms - s_stm_startup.phase_ms <
        STM_STARTUP_RESPONSE_MS) {
        return;
    }

    if (s_stm_startup.attempts >= STM_STARTUP_MAX_ATTEMPTS) {
        stm_startup_fail(
            ping ? "no matching PONG" : "no matching DISARM ACK");
        return;
    }

    ++s_stm_startup.attempts;

    ESP_LOGW(
        TAG, "STARTUP: retry %s attempt=%u",
        ping ? "PING" : "DISARM",
        s_stm_startup.attempts);

    stm_startup_send_request(ping, now_ms);
}

static void stm_startup_step(uint64_t now_ms)
{
    switch (s_stm_startup.state) {
    case STM_STARTUP_SETTLE:
        if (now_ms - s_stm_startup.phase_ms <
            STM_STARTUP_SETTLE_MS) {
            break;
        }

        if (uart_write_bytes(STM_UART_PORT, "\n", 1) != 1) {
            stm_startup_fail("line sync TX failed");
            break;
        }

        ESP_LOGI(TAG, "STARTUP: line sync sent");
        s_stm_startup.state = STM_STARTUP_SYNC_WAIT;
        s_stm_startup.phase_ms = now_ms;
        break;

    case STM_STARTUP_SYNC_WAIT:
        if (now_ms - s_stm_startup.phase_ms <
            STM_STARTUP_SYNC_WAIT_MS) {
            break;
        }

        if (uart_flush_input(STM_UART_PORT) != ESP_OK) {
            stm_startup_fail("RX flush failed");
            break;
        }

        s_stm_rx_length = 0U;
        s_stm_discard_until_lf = false;
        s_stm_startup.attempts = 1U;
        stm_startup_send_request(false, now_ms);
        break;

    case STM_STARTUP_WAIT_DISARM_ACK:
        if (s_stm_startup.disarm_ack) {
            ESP_LOGI(TAG, "STARTUP: DISARM acknowledged");
            s_stm_startup.attempts = 1U;
            stm_startup_send_request(true, now_ms);
        } else {
            stm_startup_retry(false, now_ms);
        }
        break;

    case STM_STARTUP_WAIT_PONG:
        if (s_stm_startup.pong) {
            s_stm_startup.state = STM_STARTUP_READY;
            ESP_LOGI(
                TAG,
                "STARTUP READY: DISARM ACK and PONG verified");
        } else {
            stm_startup_retry(true, now_ms);
        }
        break;

    case STM_STARTUP_READY:
    case STM_STARTUP_FAILED:
    default:
        break;
    }
}

/* ACK/PONG이면 처리 후 true, 다른 프레임이면 false를 반환한다. */
static bool stm_startup_handle_response(const char *line)
{
    const bool ack = strncmp(line, "ACK,", 4) == 0;
    const bool pong = strncmp(line, "PONG,", 5) == 0;

    if (!ack && !pong) {
        return false;
    }

    const size_t length = strlen(line);
    if (line[length - 1U] == ',' ||
        strstr(line, ",,") != NULL) {
        ESP_LOGW(TAG, "STARTUP: malformed response: %s", line);
        return true;
    }

    uint32_t seq;
    char type[16];

    if (!stm_parse_u32_field(line, "seq=", &seq) ||
        (ack && !stm_parse_text_field(
            line, "type=", type, sizeof(type)))) {
        ESP_LOGW(TAG, "STARTUP: response parse rejected: %s", line);
        return true;
    }

    if (ack) {
        ESP_LOGI(
            TAG, "RX ACK: seq=%" PRIu32 " type=%s",
            seq, type);

        if (s_stm_startup.state == STM_STARTUP_WAIT_DISARM_ACK &&
            seq == s_stm_startup.disarm_seq &&
            strcmp(type, "DISARM") == 0) {
            s_stm_startup.disarm_ack = true;
        } else {
            ESP_LOGW(TAG, "STARTUP: ignored non-matching ACK");
        }
    } else {
        ESP_LOGI(TAG, "RX PONG: seq=%" PRIu32, seq);

        if (s_stm_startup.state == STM_STARTUP_WAIT_PONG &&
            seq == s_stm_startup.ping_seq) {
            s_stm_startup.pong = true;
        } else {
            ESP_LOGW(TAG, "STARTUP: ignored non-matching PONG");
        }
    }

    return true;
}

static void stm_uart_handle_line(const char *line)
{
    if (stm_startup_handle_response(line)) {
        return;
    }

    if (strncmp(line, "TEL,", 4) != 0) {
        ESP_LOGI(TAG, "STM RX: %s", line);
        return;
    }

    stm_telemetry_t parsed = {0};

    if (!stm_parse_tel(line, &parsed)) {
        ESP_LOGW(TAG, "STM TEL rejected: %s", line);
        return;
    }

    parsed.rx_ms = (uint64_t)esp_timer_get_time() / 1000U;
    parsed.valid = true;

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    s_stm_telemetry = parsed;
    const uint32_t count = ++s_stm_tel_count;
    xSemaphoreGive(s_stm_lock);

    ESP_LOGI(
        TAG,
        "STM TEL #%" PRIu32 " t_ms=%" PRIu32
        " state=%s reason=%s"
        " pwm=%" PRIi32 "/%" PRIi32
        " cps=%" PRIi32 "/%" PRIi32
        " drop=%" PRIu32 " err=%" PRIu32,
        count, parsed.t_ms, parsed.state, parsed.reason,
        parsed.left_pwm, parsed.right_pwm,
        parsed.left_cps, parsed.right_cps,
        parsed.drop, parsed.err);
}

static void stm_uart_handle_byte(uint8_t byte)
{
    if (byte == '\n') {
        if (s_stm_discard_until_lf) {
            s_stm_discard_until_lf = false;
            s_stm_rx_length = 0U;
            return;
        }

        /* CRLF 형식이면 마지막 CR을 제거한다. */
        if (s_stm_rx_length > 0U &&
            s_stm_rx_line[s_stm_rx_length - 1U] == '\r') {
            --s_stm_rx_length;
        }

        s_stm_rx_line[s_stm_rx_length] = '\0';

        if (s_stm_rx_length > 0U) {
            stm_uart_handle_line(s_stm_rx_line);
        }

        s_stm_rx_length = 0U;
        return;
    }

    if (s_stm_discard_until_lf) {
        return;
    }

    const bool embedded_cr =
        s_stm_rx_length > 0U &&
        s_stm_rx_line[s_stm_rx_length - 1U] == '\r';
    
    const bool invalid_byte =
        (byte < 0x20U && byte != '\r') || byte > 0x7eU;

    if (embedded_cr || invalid_byte) {
        ESP_LOGW(TAG, "STM RX invalid line; discard until LF");
        s_stm_rx_length = 0U;
        s_stm_discard_until_lf = true;
        return;
    }

    if (s_stm_rx_length >= sizeof(s_stm_rx_line) - 1U) {
        ESP_LOGW(TAG, "STM RX line overflow; discard until LF");
        s_stm_rx_length = 0U;
        s_stm_discard_until_lf = true;
        return;
    }

    s_stm_rx_line[s_stm_rx_length++] = (char)byte;
}

static void stm_startup_publish_status(void)
{
    const char *status = "FAILED";

    switch (s_stm_startup.state) {
    case STM_STARTUP_SETTLE:
        status = "SETTLE";
        break;
    case STM_STARTUP_SYNC_WAIT:
        status = "SYNC_WAIT";
        break;
    case STM_STARTUP_WAIT_DISARM_ACK:
        status = "WAIT_DISARM_ACK";
        break;
    case STM_STARTUP_WAIT_PONG:
        status = "WAIT_PONG";
        break;
    case STM_STARTUP_READY:
        status = "READY";
        break;
    case STM_STARTUP_FAILED:
    default:
        break;
    }

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    s_stm_startup_status = status;
    xSemaphoreGive(s_stm_lock);
}

static void stm_uart_rx_task(void *arg)
{
    (void)arg;
    uint8_t bytes[64];

    stm_startup_begin();
    stm_startup_publish_status();

    for (;;) {
        stm_startup_step(
            (uint64_t)esp_timer_get_time() / 1000U);

        const int count = uart_read_bytes(
            STM_UART_PORT, bytes, sizeof(bytes),
            pdMS_TO_TICKS(20));

        if (count < 0) {
            stm_startup_fail("UART read failed");
            stm_startup_publish_status();
            s_stm_rx_length = 0U;
            s_stm_discard_until_lf = true;
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        for (int i = 0; i < count; ++i) {
            stm_uart_handle_byte(bytes[i]);
        }

        stm_startup_step(
            (uint64_t)esp_timer_get_time() / 1000U);
        stm_startup_publish_status();
    }
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
    s_stm_lock = xSemaphoreCreateMutex();

    if (s_server_lock == NULL || s_stm_lock == NULL) {
        ESP_LOGE(TAG, "Mutex allocation failed");
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
    
    stm_uart_init();

    if (xTaskCreate(
            stm_uart_rx_task, "stm_uart_rx",
            4096, NULL, 5, NULL) != pdPASS) {
        ESP_LOGE(TAG, "STM UART RX task allocation failed");
        return;
    }

    ESP_LOGI(TAG, "Wi-Fi + STM UART RX: mode=%s boot_id=%" PRIu32,
             WIFI_LINK_MODE_NAME, s_boot_id);
    ESP_ERROR_CHECK(esp_wifi_start());

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(WS_PERIOD_MS));
        ws_schedule();
    }
}