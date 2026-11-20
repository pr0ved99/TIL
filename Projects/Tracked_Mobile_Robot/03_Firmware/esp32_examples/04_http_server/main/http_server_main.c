#include <stdint.h>
#include <string.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "esp_http_server.h" // HTTP 서버 라이브러리 추가

#include "wifi_config.h"

#define MAX_RETRY 5U
#define STATUS_PERIOD_MS 5000U

static const char *TAG = "http_server";
static unsigned s_retry_count;

/* 웹 서버를 제어하기 위한 핸들(조종기). 
 * 나중에 서버를 끄거나 설정을 바꿀 때 이 핸들이 필요합니다. */
static httpd_handle_t server = NULL; 

/* =========================================================================
 * [웹 서버 핵심 1] URI 핸들러 함수
 * =========================================================================
 * 사용자가 브라우저 주소창에 "http://IP주소/hello"를 입력하고 엔터를 치면
 * 웹 서버가 이 함수를 찾아내어 실행시킵니다.
 */
static esp_err_t hello_get_handler(httpd_req_t *req)
{
    /* 클라이언트(브라우저)에게 보낼 문자열입니다. */
    const char* resp_str = "Hello! I am ESP32-S3 Web Server!";
    
    /* httpd_resp_send: 준비된 문자열을 클라이언트에게 HTTP 응답으로 쏴줍니다. 
     * HTTPD_RESP_USE_STRLEN은 문자열의 끝(NULL)까지 알아서 계산해서 보내라는 뜻입니다. */
    httpd_resp_send(req, resp_str, HTTPD_RESP_USE_STRLEN);
    
    ESP_LOGI(TAG, "Sent response to /hello");
    return ESP_OK;
}

/* =========================================================================
 * [웹 서버 핵심 2] 서버 시작 및 주소(URI) 등록 함수
 * =========================================================================
 * 이 함수는 Wi-Fi가 연결되고 IP를 발급받은 직후에 딱 한 번 호출됩니다.
 */
static httpd_handle_t start_webserver(void)
{
    httpd_handle_t server = NULL;
    
    /* 서버 기본 설정 가져오기 (포트 번호 80 등) */
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();

    ESP_LOGI(TAG, "Starting server on port: '%d'", config.server_port);
    
    /* 서버 엔진 가동! (실패하면 ESP_OK가 아닌 값이 나옴) */
    if (httpd_start(&server, &config) == ESP_OK) {
        
        /* 서버가 켜졌으니, "어떤 주소로 들어올 때 어떤 함수를 실행할지" 명함(URI)을 만듭니다. */
        httpd_uri_t hello_uri = {
            .uri       = "/hello",            // 접속할 주소 (URI 경로)
            .method    = HTTP_GET,            // 통신 방식 (브라우저 주소창 입력은 무조건 GET)
            .handler   = hello_get_handler,   // 이 주소로 들어오면 실행할 위쪽의 콜백 함수!
            .user_ctx  = NULL                 // 추가로 넘겨줄 데이터 (여기선 없음)
        };
        
        /* 만든 명함을 서버에 등록(Register)합니다. 
         * 이제부터 누군가 /hello 로 들어오면 서버가 알아서 hello_get_handler를 부릅니다. */
        httpd_register_uri_handler(server, &hello_uri);
        
        ESP_LOGI(TAG, "URI handler '/hello' registered.");
        return server; // 성공적으로 켜진 서버의 조종기 반환
    }

    ESP_LOGI(TAG, "Error starting server!");
    return NULL;
}

/* =========================================================================
 * Wi-Fi 및 IP 이벤트 핸들러 (03 예제와 거의 동일)
 * =========================================================================
 */
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
        
        /* 
         * [매우 중요한 시점] 
         * 인터넷 세상으로 나갈 수 있는 통행증(IP)을 방금 발급받았습니다.
         * IP가 없는 상태에서 서버를 켜봐야 접속할 방법이 없으므로,
         * 반드시 'IP_EVENT_STA_GOT_IP' 이벤트가 터진 이 시점에 서버를 가동해야 합니다. 
         */
        if (server == NULL) {
            server = start_webserver();
        }
    }
}

/* =========================================================================
 * 메인 함수 (Wi-Fi 켜는 과정은 03 예제와 100% 동일하므로 주석 생략)
 * =========================================================================
 */
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
