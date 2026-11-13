/**
 * Step 01 - Hello World
 *
 * 목표:
 *   - ESP-IDF 프로젝트 구조 이해
 *   - ESP_LOGI / ESP_LOGW / ESP_LOGE 로그 레벨 사용법
 *   - app_main() 진입점 이해
 *
 * wifi_link 코드와의 연결:
 *   - wifi_link_main.c 곳곳의 ESP_LOGI / ESP_LOGW / ESP_LOGE 가
 *     바로 이 패턴입니다.
 */

#include <stdio.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* TAG: 시리얼 모니터에서 어느 파일의 로그인지 구분하는 문자열 */
static const char *TAG = "hello";

void app_main(void)
{
    /* INFO: 정상 동작 정보 */
    ESP_LOGI(TAG, "안녕하세요, ESP32!");

    /* WARNING: 주의가 필요한 상황 */
    ESP_LOGW(TAG, "이건 경고 메시지입니다");

    /* ERROR: 심각한 문제 */
    ESP_LOGE(TAG, "이건 에러 메시지입니다");

    /* 부팅 후 1초마다 카운터 출력 */
    int count = 0;
    for (;;) {
        ESP_LOGI(TAG, "카운트: %d", count);
        count++;
        vTaskDelay(pdMS_TO_TICKS(1000)); /* 1000ms 대기 */
    }
}
