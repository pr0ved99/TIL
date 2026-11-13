# ESP 단독 Wi-Fi·HTTP 상태 페이지 코드 입력 안내

작성일: 2026-10-01. 단계: **사용자 빌드·플래시 성공, AP W1/W2 및 W3 연결 해제·복구 통과**.
설치된 ESP-IDF 6.0.2의 softAP/station/HTTP server 예제와 관련 header를 대조했다.
실제 결과는 [10/1 진행 기록](../progress/2026-10-01_progress.md#wi-fi-ap-실측--w1w2w3-결과)을 따른다. STA·WebSocket·STM 통합은 미검증이다.
아래 기준 코드의 브라우저 script 모의 검사5개는 별도 사전 검사다. 실제 보드의 HTTP500·시간 초과 주입 시험으로 확대하지 않는다.
8번의 오타·누락 목록은 수정 전 검토 이력이다. 사용자가 반영하고 빌드했으므로 같은 수정을 다시 요구하지 않는다.

## 이번 단계의 목적

노트북 브라우저가 USB 콘솔 대신 Wi-Fi로 ESP에 요청하고 ESP의 실제 동작 시간을 받는다.
STM32와 모터가 없어도 이 경로를 검증할 수 있다. STM의 상태·PWM·CPS는 연결하지 않은 데이터이므로 null이다.

```text
노트북 브라우저 → Wi-Fi → ESP HTTP 요청 handler
                         → ESP 동작 시간/메모리 읽기 → JSON 응답
노트북 브라우저 ← Wi-Fi ← 상태 응답

기존 로봇 경로: ESP UART1 ↔ STM USART1
이번 단독 프로젝트: 위 UART를 초기화하거나 모터 명령을 보내지 않음
```

접속 방식은 설정으로 바꾼다. 최초 예시 설정은 AP이며, 공유기/노트북 핫스폿은 같은 코드의 STA 설정을 사용한다.
AP에 접속하면 노트북의 기존 Wi-Fi 인터넷 연결이 끊길 수 있다. 코드 입력·검토·빌드 후 실제 접속 단계에서 사용할 방식을 선택한다.

## 1. 입력할 위치

프로젝트 폴더: `Projects/Tracked_Mobile_Robot/03_Firmware/esp32_wifi_link`.

```text
esp32_wifi_link/
  CMakeLists.txt                 준비됨
  sdkconfig.defaults             준비됨
  .gitignore                     준비됨
  main/
    CMakeLists.txt               준비됨
    wifi_link_config.h.example   준비됨
    wifi_link_config.h           사용자가 새로 작성
    wifi_link_main.c             사용자가 새로 작성
```

VS Code에서 **esp32_wifi_link 폴더를 새 창으로 열어** 입력한다.
기존 esp32_uart_bridge의 uart_bridge_main.c를 대체하지 않는다.
빌드/플래시 전에 아래 두 파일을 작성하고 저장한 뒤 실제 파일을 검토한다.

## 2. 개인 설정 파일 전문

새 `main/wifi_link_config.h`에 다음을 입력한다.
`CHANGE_ME`는 실제 사용할 8~63바이트 비밀번호로 바꾼다. 이 자리표시자가 그대로면 앱은 Wi-Fi 시작 전에 오류를 기록하고 멈춘다.
실제 비밀번호는 대화에 보내지 않는다. 이 파일은 프로젝트 .gitignore로 제외했다.

```c
#pragma once

// 1: ESP creates an AP. 0: ESP joins a router or laptop hotspot.
#define WIFI_LINK_USE_AP 1

// Local settings only. Do not commit the actual wifi_link_config.h.
#define WIFI_LINK_SSID "TMR-ESP32"
#define WIFI_LINK_PASSWORD "CHANGE_ME"
```

| 항목 | AP: ESP가 Wi-Fi 생성 | STA: 공유기·노트북 핫스폿 접속 |
| --- | --- | --- |
| WIFI_LINK_USE_AP | 1 | 0 |
| WIFI_LINK_SSID | ESP가 만들 Wi-Fi 이름 | 접속할 기존 Wi-Fi 이름 |
| WIFI_LINK_PASSWORD | 새 AP의 비밀번호 | 기존 Wi-Fi 비밀번호 |

첫 STA 시험은 2.4 GHz 개인용 WPA2 네트워크를 기준으로 한다. 기업 인증/캡티브 포털·다른 인증 구성은 이번 코드의 검증 범위가 아니다.
SSID는 1~32바이트다. 한글은 문자 수와 UTF-8 바이트 수가 다를 수 있다.

## 3. 앱 소스 전문

새 `main/wifi_link_main.c`의 **전체 내용**으로 아래 블록을 입력한다.
하나의 앱이 초기화→접속 이벤트→HTTP 응답까지 이어지는 완결된 블록이다.

```c
#include <inttypes.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

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

#if WIFI_LINK_USE_AP
#define WIFI_LINK_MODE_NAME "AP"
#else
#define WIFI_LINK_MODE_NAME "STA"
static unsigned s_retry_count;
#endif

static const char *TAG = "wifi_link";
static httpd_handle_t s_server;
static esp_netif_t *s_netif;
static uint32_t s_boot_id;

static const char PAGE[] =
    "<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>ESP Wi-Fi Link</title></head><body>"
    "<h1>ESP Wi-Fi 상태</h1><p>ESP 단독 시험 · STM 미연결</p>"
    "<p id='link'>연결 확인 중</p><pre id='data'></pre><script>"
    "const link=document.getElementById('link');"
    "const data=document.getElementById('data');"
    "async function poll(){"
    "const controller=new AbortController();"
    "const timer=setTimeout(()=>controller.abort(),2000);"
    "try{"
    "const response=await fetch('/api/status',"
    "{cache:'no-store',signal:controller.signal});"
    "if(!response.ok)throw new Error('HTTP '+response.status);"
    "const status=await response.json();"
    "data.textContent=JSON.stringify(status,null,2);"
    "link.textContent='수신 정상 · '+new Date().toLocaleTimeString();"
    "}catch(error){"
    "link.textContent='응답 없음 · 아래 값은 마지막 수신 데이터';"
    "}finally{clearTimeout(timer);setTimeout(poll,1000);}"
    "}poll();</script></body></html>";

static esp_err_t page_get(httpd_req_t *req)
{
    ESP_ERROR_CHECK(httpd_resp_set_type(req, "text/html; charset=utf-8"));
    ESP_ERROR_CHECK(httpd_resp_set_hdr(req, "Cache-Control", "no-store"));
    return httpd_resp_send(req, PAGE, HTTPD_RESP_USE_STRLEN);
}

static esp_err_t status_get(httpd_req_t *req)
{
    char json[384];
    const uint64_t uptime_ms = (uint64_t)esp_timer_get_time() / 1000U;
    const int length = snprintf(
        json, sizeof(json),
        "{\"source\":\"ESP_ONLY\",\"mode\":\"%s\","
        "\"boot_id\":%" PRIu32 ",\"uptime_ms\":%" PRIu64 ","
        "\"free_heap_bytes\":%" PRIu32 ",\"stm_connected\":false,"
        "\"state\":null,\"reason\":null,\"left_pwm\":null,"
        "\"right_pwm\":null,\"left_cps\":null,\"right_cps\":null}",
        WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms, esp_get_free_heap_size());

    if (length < 0 || (size_t)length >= sizeof(json)) {
        return httpd_resp_send_err(
            req, HTTPD_500_INTERNAL_SERVER_ERROR, "Status buffer error");
    }

    ESP_ERROR_CHECK(httpd_resp_set_type(req, "application/json"));
    ESP_ERROR_CHECK(httpd_resp_set_hdr(req, "Cache-Control", "no-store"));
    return httpd_resp_send(req, json, length);
}

static void server_stop(void)
{
    if (s_server != NULL) {
        ESP_ERROR_CHECK(httpd_stop(s_server));
        s_server = NULL;
        ESP_LOGI(TAG, "HTTP server stopped");
    }
}

static void server_start(void)
{
    if (s_server != NULL) {
        return;
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
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
    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &page_uri));
    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &status_uri));

    esp_netif_ip_info_t info;
    ESP_ERROR_CHECK(esp_netif_get_ip_info(s_netif, &info));
    ESP_LOGI(TAG, "Open http://" IPSTR "/", IP2STR(&info.ip));
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
}
```

## 4. 코드가 실행되는 순서

```text
app_main
  → 개인 설정 길이/자리표시자 검사
  → NVS 준비
  → 부팅 식별값 설정
  → esp_netif: IP 네트워크 인터페이스 준비
  → default event loop: 접속 이벤트 전달 경로 준비
  → AP 또는 STA 인터페이스 생성
  → Wi-Fi driver 초기화와 event handler 등록
  → 설정 적용, esp_wifi_start
  → app_main 반환

AP: WIFI_EVENT_AP_START → server_start
STA: WIFI_EVENT_STA_START → 접속 요청
     IP_EVENT_STA_GOT_IP → server_start

브라우저 GET / → page_get → 화면·JavaScript 전달
브라우저 GET /api/status → status_get → 실제 ESP 값 JSON 전달
```

**app_main이 반환돼도 Wi-Fi와 HTTP 서버는 계속 동작한다.** ESP-IDF가 만든 task들이 이벤트와 요청을 처리하기 때문이다.
기존 UART bridge의 while 반복문과 달리 이 앱은 이벤트/요청이 들어올 때 callback으로 처리한다.
이것은 STM에 FreeRTOS를 도입했다는 뜻이 아니다.

| 이름 | 의미·책임 |
| --- | --- |
| s_netif | 현재 AP 또는 STA의 IP 네트워크 인터페이스 |
| s_server | 실행 중인 HTTP 서버 handle. NULL은 서버 없음 |
| s_boot_id | 이번 부팅을 구분하는 32비트 난수. 보안 인증값이나 절대 고유번호가 아님 |
| wifi_event | Wi-Fi 시작/접속 유실/IP 획득에 따른 처리 |
| server_start/stop | HTTP 서버 생성·경로 등록·종료 |
| page_get | 브라우저가 처음 열 화면을 제공 |
| status_get | 요청할 때의 uptime/heap으로 JSON 생성 |
| PAGE의 poll | 응답 후 1초 뒤 다시 요청. 요청은 2초 뒤 취소하며 중첩 요청은 만들지 않음 |

JSON의 `mode`는 설정 모드, `source=ESP_ONLY`는 데이터 출처다.
`stm_connected=false`는 이 앱이 STM 연결을 구현하지 않았다는 표시이며 UART를 검사한 결과는 아니다.
`state/reason/PWM/CPS=null`은 데이터 없음이다. 모터 정지를 의미하는 0과 구분한다.
동작 시간과 heap은 요청 시 SDK API로 읽고, boot_id는 Wi-Fi 시작 전에 한 번 설정한다.
이번 앱은 STM 공유 데이터가 없어 snapshot mutex가 필요하지 않지만, 기존 bridge 통합 때는 task 간 동기화를 설계한다.

## 5. 정상·실패·재접속

- AP는 시작 이벤트에서 서버를 연다. 클라이언트가 끊겨도 AP 서버는 유지하므로 다시 접속할 수 있다.
- STA는 IP 획득 뒤 서버를 열고 접속 유실 시 닫는다. 최초 접속 뒤 최대5회 재시도한다.
  IP를 얻으면 재시도 횟수를 초기화한다. 한 번의 연결 실패 묶음에서5회를 모두 소진하면 재부팅으로 다시 시도한다.
  횟수를 제한했으며 전체 재시도 시간을 정확히 보장하는 코드가 아니다.
- 잘못된 설정/미수정 비밀번호는 Wi-Fi 시작 전에 반환한다.
- SDK 초기화/서버 API 실패는 ESP_ERROR_CHECK 오류 로그·panic 경로로 간다. 성공으로 표시하지 않는다.
  이는 단독 학습 앱의 오류 처리이며 추후 운영 복구 정책은 별도 검토한다.
- JSON 버퍼가 부족하면 HTTP500으로 응답한다.
- 브라우저 응답 실패/시간 초과는 “응답 없음”을 표시하며 마지막 데이터는 보존한다. 오래된 값을 현재 값으로 안내하지 않는다.
- STA 재접속으로 IP가 바뀌면 새 로그의 URL로 접속한다. AP/STA 자동 전환과 이전 명령 재생은 없다.
- Wi-Fi 비밀번호는 로그에 출력하지 않는다. 드라이버 설정은 RAM에 적용하며 다음 부팅에도 header 설정을 사용한다.

서버 시작/종료는 Wi-Fi event loop에서 수행하는 작은 단독 시험 구조다.
STM bridge와 통합할 때는 HTTP 대기·종료 처리가 UART safety 흐름을 막지 않도록 실행 구조를 다시 검토한다.

## 6. 검토 뒤 사용자 빌드

**지금은 입력본의 오타/누락을 수정하는 단계다(8번).** 수정 파일 검토 뒤 사용자가 ESP-IDF 환경에서 진행한다.

```powershell
idf.py set-target esp32s3
idf.py build
```

VS Code도 새 프로젝트 폴더를 대상으로 빌드해야 한다. 설치된 ESP-IDF6.0.2 환경을 그대로 사용한다.
COM 포트는 그때 실제 연결된 ESP 포트를 선택한다. 기존 COM4/COM5를 새 프로젝트에 고정하지 않았다.
USB는 이전에 사용했던 UART 표기 포트 하나로 전원·플래시·로그를 사용할 수 있다.

빌드 성공은 문법·링크 결과다. 무선 접속/상태 표시 PASS는 실제 시험 후 따로 기록한다.
플래시는 ESP의 실행 앱을 이 단독 시험으로 바꾸며 이전 로봇 앱 복원도 나중에 사용자 build/flash로 진행한다.

## 7. 다음 실제 시험 기준

현재 두 파일의 입력본은 오타/누락 수정 대기이며 아래 시험은 **미실행**이다. 수정·검토·빌드 후 한 단계씩 확인한다.

| 단계 | PASS 기준 |
| --- | --- |
| W1 접속 | 모니터에 실제 HTTP URL, 노트북에서 /api/status HTTP200과 올바른 JSON |
| W2 표시 | 브라우저 uptime이 반복 증가, boot_id는 동일 부팅에서 유지, STM 필드 false/null |
| W3 유실 | 접속 해제 후 이미 열린 화면이 응답 없음을 표시하고 마지막 값을 유지 |
| W3 복구 | 접속 복구 뒤 새 값 갱신. ESP 재부팅 때 uptime 초기화/부팅 식별값 관찰 |

다음 응답에서는 먼저 사용자가 저장한 두 파일을 확인한다. 설정 검토 시 비밀번호 값 자체는 출력하지 않는다.
입력 중 이해할 핵심은 “초기화 함수가 task를 만들고, 이후 사건을 callback으로 처리한다”는 실행 구조다.

## 참고

- [전체 작업 계획](2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md).
- [ESP-IDF6.0.2 HTTP 서버](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/api-reference/protocols/esp_http_server.html).
- 로컬 `C:/esp/v6.0.2/esp-idf/examples/wifi/getting_started/softAP`·`station`, `examples/protocols/http_server/simple` 및 `esp_wifi.h`·`esp_http_server.h` API와 대조했다.

## 8. 저장된 입력본 검토 — 2026-10-01

사용자가 저장한 앱198줄과 개인 설정 header를 읽었다. 현재는 아래 오타와 누락으로 빌드 전 수정이 필요하다.
이 표의 행 번호는 **이번에 읽은 수정 전 파일** 기준이며, 행을 추가하면 뒤 번호가 달라진다.
이번 검토에서는 사용자 C/header 파일을 직접 수정하거나 빌드하지 않았다.

### 개인 설정 header

- 1행을 `#pragma once`로 맞춘다.
- 6행의 매크로 이름 `WIFI_LINK_PASSWARD`를 `WIFI_LINK_PASSWORD`로 수정한다.
- SSID와 비밀번호 문자열은 사용자의 값을 유지한다. 비밀번호 내용은 출력·기록하지 않았다.
- 현재 선택은 AP=1이다. 이름이 틀렸으므로 올바른 PASSWORD 값의 길이/자리표시자 검사는 수정 후 다시 확인한다.

### 앱의 오타와 누락

| 수정 전 행 | 현재 입력 | 수정 |
| --- | --- | --- |
| 2 | stdint.g | stdint.h |
| 12 | esp_sustem.h | esp_system.h |
| 23 | #if WIFI_LINK_USE AP | #if WIFI_LINK_USE_AP |
| 30 | TAG 선언 끝 세미콜론 없음 | `static const char *TAG = "wifi_link";` |
| 45 | controller.about() | controller.abort() |
| 47 | getch(...) | fetch(...) |
| 49 | `'HTTP 'response.status` | `'HTTP '+response.status` |
| 55 | cleatTimeout(timer) | clearTimeout(timer) |
| 65 | ststic void | static void |
| 107 | WIFI_EVENT+AP_START | WIFI_EVENT_AP_START |
| 160 | eps_netif_create_default_wifi_ap | esp_netif_create_default_wifi_ap |

`status_get()` 함수 전체가 빠져 있다. `page_get()` 뒤, `server_stop()` 앞에 3번 전문의 해당 함수 전체를 넣는다.
현재94행 `.handler = status_get`는 정의되지 않은 함수를 참조하므로 빌드할 수 없다.

`server_start()` 끝에는 IP 조회·접속 주소 로그3줄도 빠져 있다.
두 URI 등록 직후, 함수 마지막 닫는 중괄호 전에 복구한다.

```c
    esp_netif_ip_info_t info;
    ESP_ERROR_CHECK(esp_netif_get_ip_info(s_netif, &info));
    ESP_LOGI(TAG, "Open http://" IPSTR "/", IP2STR(&info.ip));
```

한 번에 전체 대조할 기준은 **3번의 앱 소스 전문225줄**이다.
현재 앱 전체1~198행을 그 완결된 블록과 맞추면 된다. 화면 문구의 가운데 점 유무는 동작 오류가 아니다.
PAGE 안의 JavaScript는 C 입장에서는 문자열이므로 C 빌드 성공만으로 검증되지 않는다.
현재49행은 JavaScript 문법 오류이며 나머지 함수명 오타도 화면 갱신/시간 초과 처리를 방해한다.
현재 입력본은 HTTP 폴링 버전이며 WebSocket으로 전환된 코드는 아니다.

### 수정 후 빌드할 폴더

빌드 기준은 아래 **프로젝트 루트**다. main 하위 폴더나 기존 STM bringup/ESP UART bridge 폴더에서 실행하지 않는다.

```text
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware\esp32_wifi_link
```

**VS Code 빌드**

1. 위 폴더를 새 창으로 연다.
2. 필요하면 `ESP-IDF: Select Current ESP-IDF Version`에서 설치된6.0.2를 선택한다.
3. 최초 한 번 `ESP-IDF: Set Espressif Device Target` → `esp32s3`.
4. `ESP-IDF: Build your Project`를 실행한다.

**터미널 빌드**

VS Code 명령 팔레트에서 `ESP-IDF: Open ESP-IDF Terminal`을 열면 도구/파이썬 환경이 설정된다.
아래는 PowerShell 문법이다.

```powershell
Set-Location 'C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware\esp32_wifi_link'
idf.py set-target esp32s3
idf.py build
```

`set-target`은 새 프로젝트 최초 설정 또는 대상 변경 때만 수행하고, 이후 수정 빌드는 `idf.py build`만 실행한다.
일반 PowerShell에서 idf.py를 찾지 못하면 ESP-IDF 환경이 준비되지 않은 것이므로 위 ESP-IDF Terminal을 사용한다.
VS Code 밖에서는 ESP-IDF Installation Manager에서6.0.2의 Open IDF Terminal을 사용할 수 있다.
빌드에는 보드 연결·COM 선택이 필요하지 않다. 플래시·모니터는 빌드 성공 후 별도 단계다.

[공식 빌드 안내](https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/buildproject.html),
[ESP-IDF Terminal](https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/additionalfeatures/esp-terminal.html).
