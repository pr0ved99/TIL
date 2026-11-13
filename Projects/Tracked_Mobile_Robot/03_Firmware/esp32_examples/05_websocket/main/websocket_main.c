#include <stdint.h>
#include <string.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "esp_http_server.h" 

#include "wifi_config.h"

#define MAX_RETRY 5U
#define STATUS_PERIOD_MS 5000U

static const char *TAG = "websocket";
static unsigned s_retry_count;
static httpd_handle_t server = NULL;

/* =========================================================================
 * [추가된 기능] Broadcast (전체 메시지 전송)
 * =========================================================================
 * 접속된 모든 클라이언트(스마트폰, 태블릿 등)를 찾아서 동일한 메시지를 보냅니다.
 */
static void broadcast_text(const char *msg)
{
    if (server == NULL) return;

    httpd_ws_frame_t ws_pkt;
    memset(&ws_pkt, 0, sizeof(httpd_ws_frame_t));
    ws_pkt.payload = (uint8_t*)msg;
    ws_pkt.len = strlen(msg);
    ws_pkt.type = HTTPD_WS_TYPE_TEXT;

    size_t max_clients = 16;
    int fds[16];
    
    // 1. 현재 서버에 접속 중인 모든 클라이언트 번호(fd) 목록을 가져옵니다.
    esp_err_t ret = httpd_get_client_list(server, &max_clients, fds);
    if (ret != ESP_OK) return;

    // 2. 접속자 수만큼 반복문을 돌면서
    for (size_t i = 0; i < max_clients; i++) {
        // 3. 해당 접속자가 웹소켓 접속자인지 확인하고
        httpd_ws_client_info_t client_info = httpd_ws_get_fd_info(server, fds[i]);
        if (client_info == HTTPD_WS_CLIENT_WEBSOCKET) {
            // 4. 비동기(Async) 전송 방식으로 메시지를 개별 전송합니다. (이게 모이면 Broadcast)
            httpd_ws_send_frame_async(server, fds[i], &ws_pkt);
        }
    }
}

/* 
 * 1. 웹소켓 프레임 핸들러 함수
 * 클라이언트가 스마트폰 조이스틱 앱 등에서 "/ws" 로 데이터를 보내면 이 함수가 실행됩니다.
 */
static esp_err_t websocket_handler(httpd_req_t *req)
{
    if (req->method == HTTP_GET) {
        ESP_LOGI(TAG, "Handshake done, the new connection was opened");
        return ESP_OK;
    }
    
    // 데이터 패킷(프레임) 구조체 설정
    httpd_ws_frame_t ws_pkt;
    uint8_t buf[128] = { 0 };
    memset(&ws_pkt, 0, sizeof(httpd_ws_frame_t));
    ws_pkt.payload = buf;
    ws_pkt.type = HTTPD_WS_TYPE_TEXT;

    // 들어온 데이터를 버퍼(buf)로 읽어옵니다.
    esp_err_t ret = httpd_ws_recv_frame(req, &ws_pkt, 128);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "httpd_ws_recv_frame failed with %d", ret);
        return ret;
    }
    
    // 읽어온 조이스틱 데이터를 출력합니다! (예: "UP", "DOWN")
    ESP_LOGI(TAG, "Got packet with message: %s", ws_pkt.payload);

    // [수정됨] 1:1 메아리가 아니라, 연결된 모두에게 브로드캐스트(Broadcast) 합니다!
    broadcast_text((const char*)ws_pkt.payload);

    return ESP_OK;
}

/* 2. 서버 및 웹소켓 URI 등록 함수 */
static httpd_handle_t start_webserver(void)
{
    httpd_handle_t server = NULL;
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();

    ESP_LOGI(TAG, "Starting server on port: '%d'", config.server_port);
    if (httpd_start(&server, &config) == ESP_OK) {
        
        // "/ws" 라는 주소를 웹소켓 전용으로 뚫어줍니다.
        httpd_uri_t ws_uri = {
            .uri        = "/ws",
            .method     = HTTP_GET,
            .handler    = websocket_handler,
            .user_ctx   = NULL,
            .is_websocket = true // ★ 핵심! 단순 HTTP가 아니라 웹소켓이라는 뜻입니다.
        };
        
        httpd_register_uri_handler(server, &ws_uri);
        ESP_LOGI(TAG, "WebSocket handler '/ws' registered.");
        return server;
    }

    ESP_LOGI(TAG, "Error starting server!");
    return NULL;
}

static void wifi_event_handler(
    void *arg, esp_event_base_t base, int32_t id, void *event_data)
{
    (void)arg;
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        ESP_ERROR_CHECK(esp_wifi_connect());
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_retry_count < MAX_RETRY) {
            ++s_retry_count;
            ESP_ERROR_CHECK(esp_wifi_connect());
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        const ip_event_got_ip_t *event = (const ip_event_got_ip_t *)event_data;
        s_retry_count = 0U;
        ESP_LOGI(TAG, "Got IP: " IPSTR, IP2STR(&event->ip_info.ip));
        
        /* IP를 무사히 받으면 웹소켓 서버를 가동합니다. */
        if (server == NULL) {
            server = start_webserver();
        }
    }
}

void app_main(void)
{
    const size_t ssid_length = strlen(WIFI_STA_SSID);
    const size_t password_length = strlen(WIFI_STA_PASSWORD);

    esp_err_t result = nvs_flash_init();
    if (result == ESP_ERR_NVS_NO_FREE_PAGES || result == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        result = nvs_flash_init();
    }
    ESP_ERROR_CHECK(result);

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));

    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event_handler, NULL));

    wifi_config_t wifi = {0};
    memcpy(wifi.sta.ssid, WIFI_STA_SSID, ssid_length);
    memcpy(wifi.sta.password, WIFI_STA_PASSWORD, password_length);
    wifi.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    wifi.sta.sae_pwe_h2e = WPA3_SAE_PWE_BOTH;
    wifi.sta.pmf_cfg.capable = true;
    wifi.sta.pmf_cfg.required = false;
    
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi));
    ESP_ERROR_CHECK(esp_wifi_start());

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(STATUS_PERIOD_MS));
    }
}
