/*
 * SPDX-FileCopyrightText: 2010-2022 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: CC0-1.0
 */
#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BRIDGE_UART_NUM     UART_NUM_1
#define BRIDGE_UART_TX_GPIO GPIO_NUM_17
#define BRIDGE_UART_RX_GPIO GPIO_NUM_18
#define BRIDGE_UART_BAUD    115200
#define BRIDGE_RX_BUF_SIZE  1024
#define PING_PERIOD_MS      1000
#define LINE_BUF_SIZE       256
#define RX_POLL_MS          20


static const char *TAG = "esp32_uart_bridge";

typedef struct {
    uint32_t t_ms;
    char state[16];
    uint32_t last_seq;
    int32_t vx_mmps;
    int32_t w_mradps;
    uint32_t err;
    bool valid;
} bridge_telemetry_t;
static uint32_t s_rx_line_count;
static uint32_t s_pong_count;
static uint32_t s_tel_count;
static uint32_t s_ack_count;
static uint32_t s_err_count;
static uint32_t s_parse_error_count;
static uint32_t s_last_pong_seq;
static uint32_t s_last_tel_ms;
static bridge_telemetry_t s_telemetry;

static void bridge_uart_init(void){
    const uart_config_t uart_config = {
        .baud_rate = BRIDGE_UART_BAUD,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    ESP_ERROR_CHECK(uart_driver_install(BRIDGE_UART_NUM, BRIDGE_RX_BUF_SIZE, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(BRIDGE_UART_NUM, &uart_config));
    ESP_ERROR_CHECK(uart_set_pin(
        BRIDGE_UART_NUM,
        BRIDGE_UART_TX_GPIO,
        BRIDGE_UART_RX_GPIO,
        UART_PIN_NO_CHANGE,
        UART_PIN_NO_CHANGE));
}

static void bridge_uart_send_ping(uint32_t seq){
    char frame[64];

    int len = snprintf(frame, sizeof(frame), "PING,seq=%" PRIu32 "\n", seq);

    if(len > 0 && len < (int)sizeof(frame)){
        uart_write_bytes(BRIDGE_UART_NUM, frame, len);
        ESP_LOGI(TAG, "TX UART1: PING,seq=%" PRIu32, seq);
    }
    else {
        ESP_LOGW(TAG, "Failed to build PING frame");
    }
}

static int parse_u32_field(const char *line, const char *key, uint32_t  *out_value){
    const char *pos = strstr(line, key);

    if(pos == NULL || out_value == NULL){
        return 0;
    }

    pos += strlen(key);

    char *end_ptr = NULL;
    unsigned long value = strtoul(pos, &end_ptr, 10);

    if(end_ptr == pos){
        return 0;
    }

    *out_value = (uint32_t)value;
    return 1;
}

static int parse_i32_field(
    const char *line,
    const char *key,
    int32_t *out_value
){
    const char *pos = strstr(line, key);

    if(pos == NULL || out_value == NULL){
        return 0;
    }

    pos += strlen(key);

    char *end_ptr = NULL;
    long value = strtol(pos, &end_ptr, 10);

    if(end_ptr == pos){
        return 0;
    }

    *out_value = (int32_t)value;
    return 1;
}

static int parse_string_field(
    const char *line,
    const char *key,
    char *out_value,
    size_t out_size
){
    const char *pos = strstr(line, key);

    if(pos == NULL || out_value == NULL || out_size == 0){
        return 0;
    }

    pos += strlen(key);

    const char *end = strchr(pos, ',');
    if(end == NULL){
        end = pos + strlen(pos);
    }

    size_t value_len = (size_t)(end - pos);

    if(value_len == 0 || value_len >= out_size){
        return 0;
    }

    memcpy(out_value, pos, value_len);
    out_value[value_len] = '\0';
    return 1;
}

static void bridge_uart_handle_rx_line(const char *line){
    s_rx_line_count++;

    if(strncmp(line, "PONG", 4) == 0){
        uint32_t seq = 0;

        if(parse_u32_field(line, "seq=", &seq)){
            s_pong_count++;
            s_last_pong_seq = seq;
            ESP_LOGI(TAG, "RX PONG: seq=%" PRIu32 " pong_count=%" PRIu32,
            seq,
            s_pong_count);
        }
        else{
            s_parse_error_count++;
            ESP_LOGW(TAG, "RX PONG parse error: %s", line);
        }

        return;
    }

    if(strncmp(line, "TEL", 3) == 0){
        bridge_telemetry_t parsed = {0};

        int parse_ok =
            parse_u32_field(line, "t_ms=", &parsed.t_ms) &&
            parse_string_field(
                line,
                "state=",
                parsed.state,
                sizeof(parsed.state)) &&
            parse_u32_field(line, "last_seq=", &parsed.last_seq) &&
            parse_i32_field(line, "vx_mmps=", &parsed.vx_mmps) &&
            parse_i32_field(line, "w_mradps=", &parsed.w_mradps) &&
            parse_u32_field(line, "err=", &parsed.err);

        if(parse_ok){
            parsed.valid = true;
            s_telemetry = parsed;
            s_tel_count++;
            s_last_tel_ms = parsed.t_ms;

            ESP_LOGI(
                TAG,
                "RX TEL: t_ms=%" PRIu32
                " state=%s"
                " last_seq=%" PRIu32
                " vx=%" PRIi32
                " w=%" PRIi32
                " err=%" PRIu32
                " tel_count=%" PRIu32,
                s_telemetry.t_ms,
                s_telemetry.state,
                s_telemetry.last_seq,
                s_telemetry.vx_mmps,
                s_telemetry.w_mradps,
                s_telemetry.err,
                s_tel_count
            );
        }
        else {
            s_parse_error_count++;
            ESP_LOGW(TAG, "RX TEL parse error: %s", line);
        }

        return;
    }

    if(strncmp(line, "ACK", 3) == 0){
        s_ack_count++;
        ESP_LOGI(TAG, "RX ACK: %s", line);
        return;
    }

    if(strncmp(line, "ERR", 3) == 0){
        s_err_count++;
        ESP_LOGW(TAG, "RX ERR: %s", line);
        return;
    }

    s_parse_error_count++;
    ESP_LOGW(TAG, "RX UNKNOWN: %s", line);
}

static void bridge_uart_handle_rx_byte(uint8_t byte){
    static char line_buf[LINE_BUF_SIZE];
    static size_t line_len;

    if(byte == '\r'){
        return;
    }

    if(byte == '\n'){
        line_buf[line_len] = '\0';

        if(line_len > 0){
            bridge_uart_handle_rx_line(line_buf);
        }

        line_len = 0;
        return;
    }

    if(line_len < (LINE_BUF_SIZE- 1)){
        line_buf[line_len] = (char)byte;
        line_len++;
    }
    else {
        ESP_LOGW(TAG, "RX line overflow");
        line_len =0;
    }
}

void app_main(void){
    ESP_LOGI(TAG, "ESP UART bridge app start");

    bridge_uart_init();
    ESP_LOGI(TAG, "UART1 init done: TX=GPIO%d RX=GPIO%d baud=%d",
        BRIDGE_UART_TX_GPIO,
        BRIDGE_UART_RX_GPIO,
        BRIDGE_UART_BAUD);

    uint32_t seq = 1;
    TickType_t last_ping_tick = 0;

    while(1){
        TickType_t now = xTaskGetTickCount();

        if(now - last_ping_tick >= PING_PERIOD_MS / portTICK_PERIOD_MS){
            bridge_uart_send_ping(seq);
            last_ping_tick = now;
            seq++;
        }

        uint8_t rx_byte;
        int rx_len = uart_read_bytes(
            BRIDGE_UART_NUM,
            &rx_byte,
            1,
            pdMS_TO_TICKS(RX_POLL_MS));

        if (rx_len == 1){
            bridge_uart_handle_rx_byte(rx_byte);
        }
    }
}
