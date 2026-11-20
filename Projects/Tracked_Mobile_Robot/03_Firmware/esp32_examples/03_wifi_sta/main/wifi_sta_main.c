/**
 * Step 03 - Wi-Fi STA 연결 + 이벤트 핸들러
 *
 * 목표:
 *   - ESP32가 공유기/핫스팟에 접속(STA)하는 초기화 순서 이해
 *   - 이벤트 핸들러가 "누가, 언제" 호출되는지 이해
 *   - 연결 실패 시 reason 코드로 원인 추측하기
 *
 * wifi_link 코드와의 연결 (esp32_wifi_link/main/wifi_link_main.c):
 *   - wifi_event()          <-> 이 파일의 wifi_event_handler()
 *   - STA_START             -> esp_wifi_connect()
 *   - STA_DISCONNECTED      -> 최대 5회 재시도
 *   - IP_EVENT_STA_GOT_IP   -> 원본에서는 여기서 server_start() 호출
 *     (이 예제는 IP만 출력합니다. HTTP 서버는 Step 04에서 붙입니다.)
 *
 * 실행 흐름:
 *   app_main
 *     -> 초기화(nvs, netif, event loop, wifi)
 *     -> esp_wifi_start()
 *          -> [이벤트] STA_START        : connect 요청
 *          -> [이벤트] STA_CONNECTED    : AP와 연결됨 (아직 IP 없음)
 *          -> [이벤트] STA_GOT_IP       : IP 받음 -> 통신 가능
 *          -> [이벤트] STA_DISCONNECTED : 끊김 -> 재시도
 */

#include <stdint.h>
#include <string.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"

#include "wifi_config.h"

#define MAX_RETRY 5U
#define STATUS_PERIOD_MS 5000U

static const char *TAG = "wifi_sta";

/* 이 변수는 이벤트 루프 Task 에서만 읽고 씁니다.
 * (app_main 은 건드리지 않으므로 Mutex 가 필요 없습니다.) */
static unsigned s_retry_count;

/*
 * 이벤트 핸들러: 직접 호출하지 않습니다.
 * esp_event_handler_register 로 등록해 두면, Wi-Fi 스택이 상태가 바뀔 때
 * 시스템 이벤트 Task 에서 이 함수를 대신 호출해 줍니다.
 * (Step 02 에서 본 "등록만 하면 시스템이 불러준다"와 같은 구조입니다.)
 */
static void wifi_event_handler(
    void *arg, esp_event_base_t base, int32_t id, void *event_data)
{
    (void)arg;

    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START)
    {
        ESP_LOGI(TAG, "STA started -> connecting");
        ESP_ERROR_CHECK(esp_wifi_connect());
    }
    else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_CONNECTED)
    {
        ESP_LOGI(TAG, "Associated with AP (waiting for IP)");
    }
    else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED)
    {
        /*
         * reason 코드로 원인을 추측할 수 있습니다.
         *   201 NO_AP_FOUND              : SSID를 못 찾음 (이름 오타 / 5GHz / 범위 밖)
         *   202 AUTH_FAIL                : 인증 실패 (비밀번호 오류 가능)
         *    15 4WAY_HANDSHAKE_TIMEOUT   : 핸드셰이크 실패 (비밀번호 오류 가능)
         *     2 AUTH_EXPIRE              : 인증 만료
         *   205 CONNECTION_FAIL          : 연결 실패
         */
        const wifi_event_sta_disconnected_t *info =
            (const wifi_event_sta_disconnected_t *)event_data;
        ESP_LOGW(TAG, "Disconnected, reason=%u", (unsigned)info->reason);

        if (s_retry_count < MAX_RETRY)
        {
            ++s_retry_count;
            ESP_LOGW(TAG, "Reconnect attempt %u/%u", s_retry_count, MAX_RETRY);
            ESP_ERROR_CHECK(esp_wifi_connect());
        }
        else
        {
            ESP_LOGE(TAG, "Retry limit reached; reset the board to retry");
        }
    }
    else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP)
    {
        const ip_event_got_ip_t *event = (const ip_event_got_ip_t *)event_data;
        s_retry_count = 0U;
        ESP_LOGI(TAG, "Got IP: " IPSTR, IP2STR(&event->ip_info.ip));
        /* wifi_link 에서는 여기서 server_start() 를 호출합니다. */
    }
}

void app_main(void)
{
    /* 1) 설정값 검증: 예제 기본값 그대로면 실행하지 않음 */
    const size_t ssid_length = strlen(WIFI_STA_SSID);
    const size_t password_length = strlen(WIFI_STA_PASSWORD);
    if (ssid_length == 0U || ssid_length > 32U ||
        password_length < 8U || password_length > 63U ||
        strcmp(WIFI_STA_PASSWORD, "CHANGE_ME") == 0)
    {
        ESP_LOGE(TAG, "Set a valid SSID/password in main/wifi_config.h");
        return;
    }

    /* 2) NVS 초기화: Wi-Fi 드라이버가 내부적으로 사용 */
    esp_err_t result = nvs_flash_init();
    if (result == ESP_ERR_NVS_NO_FREE_PAGES ||
        result == ESP_ERR_NVS_NEW_VERSION_FOUND)
    {
        ESP_ERROR_CHECK(nvs_flash_erase());
        result = nvs_flash_init();
    }
    ESP_ERROR_CHECK(result);

    /* 3) 네트워크 스택 + 기본 이벤트 루프 */
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* 4) STA 용 네트워크 인터페이스 생성 */
    esp_netif_t *netif = esp_netif_create_default_wifi_sta();
    if (netif == NULL)
    {
        ESP_LOGE(TAG, "Network interface allocation failed");
        return;
    }

    /* 5) Wi-Fi 드라이버 초기화 */
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));

    /* 6) 이벤트 핸들러 등록: Wi-Fi 이벤트 + IP 이벤트 */
    ESP_ERROR_CHECK(esp_event_handler_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event_handler, NULL));

    /* 7) 접속할 AP 정보 설정 */
    wifi_config_t wifi = {0};
    memcpy(wifi.sta.ssid, WIFI_STA_SSID, ssid_length);
    memcpy(wifi.sta.password, WIFI_STA_PASSWORD, password_length);
    /* 인증 방식: WPA2 이상을 허용합니다. (WPA3 공유기도 접속 대상) */
    wifi.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    /* WPA3(SAE) 공유기 대응:
     *   - sae_pwe_h2e : SAE 비밀번호 변환 방식을 공유기에 맞춰 자동 선택
     *   - pmf_cfg     : 보호된 관리 프레임(PMF) 지원 표시. WPA3 는 PMF 가 필요합니다. */
    wifi.sta.sae_pwe_h2e = WPA3_SAE_PWE_BOTH;
    wifi.sta.pmf_cfg.capable = true;
    wifi.sta.pmf_cfg.required = false;
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi));

    /* 8) 시작: 이 호출 이후의 모든 진행은 이벤트 핸들러로 전달됩니다. */
    ESP_LOGI(TAG, "Connecting to SSID '%s'", WIFI_STA_SSID);
    ESP_ERROR_CHECK(esp_wifi_start());

    /* 9) 상태 점검 루프: 5초마다 연결 상태와 신호 세기를 출력 (heartbeat) */
    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(STATUS_PERIOD_MS));

        wifi_ap_record_t ap;
        if (esp_wifi_sta_get_ap_info(&ap) == ESP_OK)
        {
            ESP_LOGI(TAG, "[main] connected ssid=%s rssi=%d dBm",
                     (const char *)ap.ssid, ap.rssi);
        }
        else
        {
            ESP_LOGW(TAG, "[main] not connected");
        }
    }
}

/*
 * 실험해보기 (한 번에 하나씩)
 *
 *  1) 비밀번호를 일부러 틀리게 쓰면 reason 은 몇 번이 나오나?
 *  2) SSID 를 존재하지 않는 이름으로 바꾸면 reason 은?  (201 이 나와야 정상)
 *  3) 연결된 뒤 공유기/핫스팟을 껐다 켜면 재시도 로그는 어떻게 흐르나?
 *  4) MAX_RETRY 를 1 로 줄이면 어떤 로그에서 멈추나?
 *  5) 연결 후 폰/공유기에서 거리를 두면 rssi 값은 어떻게 변하나?
 */