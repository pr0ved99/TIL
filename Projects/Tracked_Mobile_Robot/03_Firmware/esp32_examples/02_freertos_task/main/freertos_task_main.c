/**
 * Step 02 - FreeRTOS Task + Mutex
 *
 * 목표:
 *   - xTaskCreate 로 여러 Task를 동시에 실행하기
 *   - vTaskDelay 로 CPU를 양보하는 이유 이해하기
 *   - 여러 Task가 같은 변수를 건드릴 때 Mutex가 필요한 이유 이해하기
 *
 * wifi_link 코드와의 연결:
 *   - app_main 마지막의 for(;;) { vTaskDelay(...); ws_schedule(); }
 *   - s_server_lock = xSemaphoreCreateMutex()
 *   - xSemaphoreTake(s_server_lock, portMAX_DELAY) / xSemaphoreGive(...)
 *   (Wi-Fi 이벤트 Task, HTTP 서버 Task, app_main Task가 s_server 를
 *    함께 쓰기 때문에 Mutex로 보호합니다.)
 */

#include <inttypes.h>
#include <stdint.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

static const char *TAG = "rtos";

/* 여러 Task가 함께 쓰는 공유 변수 + 이를 보호하는 Mutex */
static uint32_t s_shared_counter;
static SemaphoreHandle_t s_lock;

/* Task마다 다른 이름과 주기를 주기 위한 설정 */
typedef struct {
    const char *name;
    uint32_t period_ms;
} task_config_t;

static const task_config_t FAST_TASK = {.name = "fast", .period_ms = 100};
static const task_config_t SLOW_TASK = {.name = "slow", .period_ms = 2000};

/* Task 함수: 반환하면 안 되고, 무한 루프여야 합니다. */
static void counter_task(void *arg)
{
    const task_config_t *config = (const task_config_t *)arg;

    for (;;) {
        /* 임계 구역: 공유 변수는 Mutex를 잡은 동안에만 읽고 쓴다. */
        xSemaphoreTake(s_lock, portMAX_DELAY);
        s_shared_counter++;
        const uint32_t value = s_shared_counter;
        xSemaphoreGive(s_lock);

        ESP_LOGI(TAG, "[%s] shared_counter=%" PRIu32, config->name, value);

        /* 이 줄이 없으면 이 Task가 CPU를 계속 잡아 다른 Task가 굶습니다. */
        vTaskDelay(pdMS_TO_TICKS(config->period_ms));
    }
}

void app_main(void)
{
    s_lock = xSemaphoreCreateMutex();
    if (s_lock == NULL) {
        ESP_LOGE(TAG, "Mutex allocation failed");
        return;
    }

    /* xTaskCreate(함수, 이름, 스택 바이트, 인자, 우선순위, 핸들) */
    const BaseType_t fast_ok = xTaskCreate(
        counter_task, "fast_task", 3072, (void *)&FAST_TASK, 5, NULL);
    const BaseType_t slow_ok = xTaskCreate(
        counter_task, "slow_task", 3072, (void *)&SLOW_TASK, 5, NULL);

    if (fast_ok != pdPASS || slow_ok != pdPASS) {
        ESP_LOGE(TAG, "Task creation failed");
        return;
    }

    /* app_main 자체도 하나의 Task 입니다. 5초마다 상태를 점검합니다. */
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(5000));

        xSemaphoreTake(s_lock, portMAX_DELAY);
        const uint32_t value = s_shared_counter;
        xSemaphoreGive(s_lock);

        ESP_LOGW(TAG, "[main] heartbeat, shared_counter=%" PRIu32, value);
    }
}

/*
 * 실험해보기 (한 번에 하나씩 바꾸고 로그 차이를 관찰하세요)
 *
 *  1) FAST_TASK 의 period_ms 를 100 으로 줄이면 로그 비율이 어떻게 변하나?
 *  2) counter_task 의 vTaskDelay 줄을 주석 처리하면 어떻게 되나?
 *     (다른 Task 로그가 사라지거나 워치독 경고가 뜰 수 있습니다.)
 *  3) 한 Task의 우선순위를 5 -> 10 으로 바꾸면 달라지는 점은?
 *  4) xTaskCreate 의 스택 크기를 3072 -> 512 로 줄이면 어떤 에러가 나나?
 */
