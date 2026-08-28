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
#include <stdbool.h>

#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_random.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BRIDGE_UART_NUM     UART_NUM_1
#define BRIDGE_UART_TX_GPIO GPIO_NUM_17
#define BRIDGE_UART_RX_GPIO GPIO_NUM_18
#define BRIDGE_UART_BAUD    115200
#define BRIDGE_RX_BUF_SIZE  1024
/* Safety default: never transmit the scripted motion test at bridge boot. */
#define BRIDGE_SCRIPTED_TEST_ENABLED            0U
#define BRIDGE_MALFORMED_COMMAND_TEST_ENABLED   0U

#if BRIDGE_SCRIPTED_TEST_ENABLED && BRIDGE_MALFORMED_COMMAND_TEST_ENABLED
#error "Only one bridge test may be enabled"
#endif
#define TEST_STEP_PERIOD_MS         1000
#define P03_TEST_STEP_PERIOD_MS     100U
#define P03_CMD_TIMEOUT_TARGET_MS   500U
#define LINE_BUF_SIZE               256
#define RX_POLL_MS                  20

#define STARTUP_SETTLE_MS           500U
#define STARTUP_SYNC_WAIT_MS        100U
#define STARTUP_RESPONSE_TIMEOUT_MS 500U
#define STARTUP_MAX_ATTEMPTS        3U


static const char *TAG = "esp32_uart_bridge";

typedef struct {
    uint32_t t_ms;
    char state[16];
    uint32_t last_seq;
    int32_t vx_mmps;
    int32_t w_mradps;
    int32_t left_pwm;
    int32_t right_pwm;
    int32_t left_cps;
    int32_t right_cps;
    uint32_t err;
    bool valid;
} bridge_telemetry_t;

typedef enum {
    BRIDGE_STARTUP_SETTLE = 0,
    BRIDGE_STARTUP_SYNC_WAIT,
    BRIDGE_STARTUP_WAIT_DISARM_ACK,
    BRIDGE_STARTUP_WAIT_PONG,
    BRIDGE_STARTUP_READY,
    BRIDGE_STARTUP_FAILED
} bridge_startup_state_t;

typedef enum {
    BRIDGE_TEST_CMD_BEFORE_ARM = 0,
    BRIDGE_TEST_FIRST_ARM,
    BRIDGE_TEST_FIRST_CMD,
    BRIDGE_TEST_WAIT_CMD_TIMEOUT_1,
    BRIDGE_TEST_WAIT_CMD_TIMEOUT_2,
    BRIDGE_TEST_WAIT_CMD_TIMEOUT_3,
    BRIDGE_TEST_WAIT_CMD_TIMEOUT_4,
    BRIDGE_TEST_WAIT_CMD_TIMEOUT_MARGIN,
    BRIDGE_TEST_CMD_AFTER_TIMEOUT,
    BRIDGE_TEST_ARM_WITHOUT_CMD,
    BRIDGE_TEST_WAIT_ARM_TIMEOUT_1,
    BRIDGE_TEST_WAIT_ARM_TIMEOUT_2,
    BRIDGE_TEST_WAIT_ARM_TIMEOUT_3,
    BRIDGE_TEST_WAIT_ARM_TIMEOUT_4,
    BRIDGE_TEST_CMD_AFTER_ARM_TIMEOUT,
    BRIDGE_TEST_RECOVERY_ARM,
    BRIDGE_TEST_RECOVERY_CMD,
    BRIDGE_TEST_RECOVERY_HOLD,
    BRIDGE_TEST_FINAL_DISARM,
    BRIDGE_TEST_DONE
} bridge_test_step_t;

#if BRIDGE_MALFORMED_COMMAND_TEST_ENABLED
#define MALFORMED_TEST_VECTOR_COUNT 8U
#define MALFORMED_TEST_DONE_STEP    (MALFORMED_TEST_VECTOR_COUNT + 1U)

static const char *const s_malformed_test_frames[
    MALFORMED_TEST_VECTOR_COUNT
] = {
    "PING,seq=9001,extra=1",
    "CMD,seq=9002,w_mradps=0,vx_mmps=0,timeout_ms=300",
    "CMD,seq=9003,vx_mmps=0,vx_mmps=0,w_mradps=0,timeout_ms=300",
    "CMD,seq=9004,vx_mmps=0,w_mradps=0,timeout_ms=4294967296",
    "NOPE,seq=9005",
    NULL,
    "PING,seq=9007\rX",
    "PING,seq=9008" "\x01" "X",
};

static const char *const s_malformed_test_labels[
    MALFORMED_TEST_VECTOR_COUNT
] = {
    "PING_EXTRA_DATA",
    "CMD_BAD_FIELD_ORDER",
    "CMD_DUPLICATE_FIELD",
    "CMD_TIMEOUT_OVERFLOW",
    "UNKNOWN_FRAME",
    "OVERLONG_LINE_180",
    "EMBEDDED_CR",
    "CONTROL_BYTE_0x01",
};
#endif

static uint32_t s_rx_line_count;
static uint32_t s_pong_count;
static uint32_t s_tel_count;
static uint32_t s_ack_count;
static uint32_t s_err_count;
static uint32_t s_parse_error_count;
static uint32_t s_last_pong_seq;
static bool s_last_pong_valid;
static bool s_last_ack_valid;
static uint32_t s_last_ack_seq;
static char s_last_ack_type[16];

static bridge_startup_state_t s_startup_state = BRIDGE_STARTUP_SETTLE;
static TickType_t s_startup_state_tick;
static uint32_t s_startup_attempt_count;
static uint32_t s_startup_disarm_seq;
static uint32_t s_startup_ping_seq;
static uint32_t s_last_tel_ms;
static bridge_telemetry_t s_telemetry;

static char s_rx_line_buf[LINE_BUF_SIZE];
static size_t s_rx_line_len;
static bool s_rx_discard_until_lf;

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

static int bridge_uart_send_frame(const char *frame){
    if(frame == NULL || frame[0] == '\0'){
        ESP_LOGW(TAG, "Cannot send empty UART frame");
        return 0;
    }

    size_t frame_len = strlen(frame);

    if(frame_len >= LINE_BUF_SIZE - 1){
        ESP_LOGW(TAG, "UART TX frame too long");
        return 0;
    }

    char tx_buf[LINE_BUF_SIZE];
    int tx_len = snprintf(tx_buf, sizeof(tx_buf), "%s\n", frame);

    if(tx_len <= 0 || tx_len >= (int)sizeof(tx_buf)){
        ESP_LOGW(TAG, "Failed to terminate UART TX frame");
        return 0;
    }

    int written = uart_write_bytes(BRIDGE_UART_NUM, tx_buf, tx_len);

    if(written != tx_len){
        ESP_LOGW(TAG, "UART TX write failed: %s", frame);
        return 0;
    }

    ESP_LOGI(TAG, "TX UART1: %s", frame);
    return 1;
}

static int bridge_uart_send_ping(uint32_t seq){
    char frame[64];
    int len = snprintf(
        frame,
        sizeof(frame),
        "PING,seq=%" PRIu32,
        seq
    );

    if(len <= 0 || len >= (int)sizeof(frame)){
        ESP_LOGW(TAG, "Failed to build PING frame");
        return 0;
    }

    return bridge_uart_send_frame(frame);
}

static int bridge_uart_send_arm(uint32_t seq){
    char frame[64];
    int len = snprintf(
        frame,
        sizeof(frame),
        "ARM,seq=%" PRIu32,
        seq
    );

    if(len <= 0 || len >= (int)sizeof(frame)){
        ESP_LOGW(TAG, "Failed to build ARM frame");
        return 0;
    }

    return bridge_uart_send_frame(frame);
}

static int bridge_uart_send_disarm(uint32_t seq){
    char frame[64];
    int len = snprintf(
        frame,
        sizeof(frame),
        "DISARM,seq=%" PRIu32,
        seq
    );

    if(len <= 0 || len >= (int)sizeof(frame)){
        ESP_LOGW(TAG, "Failed to build DISARM frame");
        return 0;
    }

    return bridge_uart_send_frame(frame);
}

static int bridge_uart_send_cmd(
    uint32_t seq,
    int32_t vx_mmps,
    int32_t w_mradps,
    uint32_t timeout_ms
){
    char frame[128];
    int len = snprintf(
        frame,
        sizeof(frame),
        "CMD,seq=%" PRIu32
        ",vx_mmps=%" PRId32
        ",w_mradps=%" PRId32
        ",timeout_ms=%" PRIu32,
        seq,
        vx_mmps,
        w_mradps,
        timeout_ms
    );

    if(len <= 0 || len >= (int)sizeof(frame)){
        ESP_LOGW(TAG, "Failed to build CMD frame");
        return 0;
    }

    return bridge_uart_send_frame(frame);
}

static bridge_test_step_t bridge_uart_run_test_step(
    bridge_test_step_t step,
    uint32_t *seq
){
    if(seq == NULL){
        ESP_LOGW(TAG, "Test sequence pointer is NULL");
        return BRIDGE_TEST_DONE;
    }

    switch(step){
        case BRIDGE_TEST_CMD_BEFORE_ARM:
            if(bridge_uart_send_cmd(*seq, 50, 0, P03_CMD_TIMEOUT_TARGET_MS)){
                (*seq)++;
                return BRIDGE_TEST_FIRST_ARM;
            }
            return step;
        case BRIDGE_TEST_FIRST_ARM:
            if(bridge_uart_send_arm(*seq)){
                (*seq)++;
                return BRIDGE_TEST_FIRST_CMD;
            }
            return step;
        case BRIDGE_TEST_FIRST_CMD:
            if(bridge_uart_send_cmd(*seq, 50, 0, P03_CMD_TIMEOUT_TARGET_MS)){
                (*seq)++;
                return BRIDGE_TEST_WAIT_CMD_TIMEOUT_1;
            }
            return step;
        case BRIDGE_TEST_WAIT_CMD_TIMEOUT_1:
            ESP_LOGI(TAG, "P-03: waiting for CMD timeout");
            return BRIDGE_TEST_WAIT_CMD_TIMEOUT_2;

        case BRIDGE_TEST_WAIT_CMD_TIMEOUT_2:
            return BRIDGE_TEST_WAIT_CMD_TIMEOUT_3;

        case BRIDGE_TEST_WAIT_CMD_TIMEOUT_3:
            return BRIDGE_TEST_WAIT_CMD_TIMEOUT_4;

        case BRIDGE_TEST_WAIT_CMD_TIMEOUT_4:
            return BRIDGE_TEST_WAIT_CMD_TIMEOUT_MARGIN;

        case BRIDGE_TEST_WAIT_CMD_TIMEOUT_MARGIN:
            ESP_LOGI(TAG, "REQ-SAFE-004: post-timeout margin");
            return BRIDGE_TEST_CMD_AFTER_TIMEOUT;

        case BRIDGE_TEST_CMD_AFTER_TIMEOUT:
            if(bridge_uart_send_cmd(*seq, 50, 0, P03_CMD_TIMEOUT_TARGET_MS)){
                (*seq)++;
                return BRIDGE_TEST_ARM_WITHOUT_CMD;
            }
            return step;
        case BRIDGE_TEST_ARM_WITHOUT_CMD:
            if(bridge_uart_send_arm(*seq)){
                (*seq)++;
                return BRIDGE_TEST_WAIT_ARM_TIMEOUT_1;
            }
            return step;
        case BRIDGE_TEST_WAIT_ARM_TIMEOUT_1:
            ESP_LOGI(TAG, "P-03: waiting for ARM-only timeout");
            return BRIDGE_TEST_WAIT_ARM_TIMEOUT_2;

        case BRIDGE_TEST_WAIT_ARM_TIMEOUT_2:
            return BRIDGE_TEST_WAIT_ARM_TIMEOUT_3;

        case BRIDGE_TEST_WAIT_ARM_TIMEOUT_3:
            return BRIDGE_TEST_WAIT_ARM_TIMEOUT_4;

        case BRIDGE_TEST_WAIT_ARM_TIMEOUT_4:
            return BRIDGE_TEST_CMD_AFTER_ARM_TIMEOUT;

        case BRIDGE_TEST_CMD_AFTER_ARM_TIMEOUT:
            if(bridge_uart_send_cmd(*seq, 50, 0, P03_CMD_TIMEOUT_TARGET_MS)){
                (*seq)++;
                return BRIDGE_TEST_RECOVERY_ARM;
            }
            return step;

        case BRIDGE_TEST_RECOVERY_ARM:
            if(bridge_uart_send_arm(*seq)){
                (*seq)++;
                return BRIDGE_TEST_RECOVERY_CMD;
            }
            return step;

        case BRIDGE_TEST_RECOVERY_CMD:
            if(bridge_uart_send_cmd(*seq, 50, 0, P03_CMD_TIMEOUT_TARGET_MS)){
                (*seq)++;
                return BRIDGE_TEST_RECOVERY_HOLD;
            }
            return step;

        case BRIDGE_TEST_RECOVERY_HOLD:
            ESP_LOGI(TAG, "P-03: observing recovered output");
            return BRIDGE_TEST_FINAL_DISARM;

        case BRIDGE_TEST_FINAL_DISARM:
            if(bridge_uart_send_disarm(*seq)){
                (*seq)++;
                ESP_LOGI(TAG, "P-03: scripted sequence complete");
                return BRIDGE_TEST_DONE;
            }
            return step;

        case BRIDGE_TEST_DONE:
        default:
            return BRIDGE_TEST_DONE;
    }
}

#if BRIDGE_MALFORMED_COMMAND_TEST_ENABLED
static int bridge_uart_send_labeled_raw_frame(
    const uint8_t *frame,
    size_t frame_len,
    const char *label
){
    int written;

    if(frame == NULL || frame_len == 0U || label == NULL){
        ESP_LOGW(TAG, "Invalid malformed-test frame");
        return 0;
    }

    written = uart_write_bytes(
        BRIDGE_UART_NUM,
        frame,
        frame_len
    );

    if(written != (int)frame_len){
        ESP_LOGW(TAG, "UART TX test payload failed: %s", label);
        return 0;
    }

    written = uart_write_bytes(BRIDGE_UART_NUM, "\n", 1);

    if(written != 1){
        ESP_LOGW(TAG, "UART TX test newline failed: %s", label);
        return 0;
    }

    ESP_LOGI(
        TAG,
        "TX UART1 TEST: %s len=%u",
        label,
        (unsigned int)frame_len
    );
    return 1;
}

static uint8_t bridge_uart_run_malformed_command_test_step(
    uint8_t step
){
    uint8_t overlong_frame[180U];
    const uint8_t *payload;
    size_t payload_len;
    size_t index;
    int prefix_len;

    if(step < MALFORMED_TEST_VECTOR_COUNT){
        if(step == 5U){
            prefix_len = snprintf(
                (char *)overlong_frame,
                sizeof(overlong_frame),
                "PING,seq=9006,"
            );

            if(
                prefix_len <= 0 ||
                prefix_len >= (int)sizeof(overlong_frame)
            ){
                ESP_LOGW(TAG, "Failed to build overlong test frame");
                return step;
            }

            for(
                index = (size_t)prefix_len;
                index < sizeof(overlong_frame);
                index++
            ){
                overlong_frame[index] = (uint8_t)'X';
            }

            payload = overlong_frame;
            payload_len = sizeof(overlong_frame);
        }
        else{
            payload = (const uint8_t *)s_malformed_test_frames[step];
            payload_len = strlen(s_malformed_test_frames[step]);
        }

        if(
            bridge_uart_send_labeled_raw_frame(
                payload,
                payload_len,
                s_malformed_test_labels[step]
            )
        ){
            return step + 1U;
        }
        return step;
    }

    if(step == MALFORMED_TEST_VECTOR_COUNT){
        ESP_LOGI(TAG, "TX UART1 TEST: FINAL_VALID_PING seq=9009");

        if(bridge_uart_send_ping(9009U)){
            return MALFORMED_TEST_DONE_STEP;
        }
    }

    return step;
}
#endif

static const char *find_field_value(const char *line, const char *key){
    if(line == NULL || key == NULL || key[0] == '\0'){
        return NULL;
    }

    size_t key_len = strlen(key);
    const char *field = line;
    const char *value = NULL;

    while(field[0] != '\0'){
        if(strncmp(field, key, key_len) == 0){
            if(value != NULL){
                return NULL;
            }

            value = field + key_len;
        }

        const char *comma = strchr(field, ',');

        if(comma == NULL){
            break;
        }

        field = comma + 1;
    }

    return value;
}

static int parse_u32_field(
    const char *line,
    const char *key,
    uint32_t *out_value
){
    if(out_value == NULL){
        return 0;
    }

    const char *pos = find_field_value(line, key);

    if(pos == NULL || pos[0] < '0' || pos[0] > '9'){
        return 0;
    }

    uint32_t value = 0U;

    while(pos[0] >= '0' && pos[0] <= '9'){
        uint32_t digit = (uint32_t)(pos[0] - '0');

        if(value > (UINT32_MAX - digit) / 10U){
            return 0;
        }

        value = (value * 10U) + digit;
        pos++;
    }

    if(pos[0] != ',' && pos[0] != '\0'){
        return 0;
    }

    *out_value = value;
    return 1;
}

static int parse_i32_field(
    const char *line,
    const char *key,
    int32_t *out_value
){
    if(out_value == NULL){
        return 0;
    }

    const char *pos = find_field_value(line, key);

    if(pos == NULL){
        return 0;
    }

    bool negative = false;

    if(pos[0] == '-'){
        negative = true;
        pos++;
    }

    if(pos[0] < '0' || pos[0] > '9'){
        return 0;
    }

    const uint32_t limit = negative ? 2147483648U : 2147483647U;
    uint32_t magnitude = 0U;

    while(pos[0] >= '0' && pos[0] <= '9'){
        uint32_t digit = (uint32_t)(pos[0] - '0');

        if(magnitude > (limit - digit) / 10U){
            return 0;
        }

        magnitude = (magnitude * 10U) + digit;
        pos++;
    }

    if(pos[0] != ',' && pos[0] != '\0'){
        return 0;
    }

    if(negative){
        *out_value = magnitude == 2147483648U
            ? INT32_MIN
            : -(int32_t)magnitude;
    }
    else {
        *out_value = (int32_t)magnitude;
    }

    return 1;
}

static int parse_string_field(
    const char *line,
    const char *key,
    char *out_value,
    size_t out_size
){
    if(out_value == NULL || out_size == 0){
        return 0;
    }

    const char *pos = find_field_value(line, key);

    if(pos == NULL){
        return 0;
    }

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

    size_t line_length = strlen(line);

    if(line_length == 0U || line[line_length - 1U] == ','){
        s_parse_error_count++;
        ESP_LOGW(TAG, "RX malformed field list: %s", line);
        return;
    }

    if(strncmp(line, "PONG,", 5) == 0){
        uint32_t seq = 0;

        if(parse_u32_field(line, "seq=", &seq)){
            s_pong_count++;

            ESP_LOGI(
                TAG,
                "RX PONG: seq=%" PRIu32 " pong_count=%" PRIu32,
                seq,
                s_pong_count
            );

            if(
                s_startup_state == BRIDGE_STARTUP_WAIT_PONG &&
                seq == s_startup_ping_seq
            ){
                s_last_pong_seq = seq;
                s_last_pong_valid = true;
            }
            else if(s_startup_state != BRIDGE_STARTUP_READY){
                ESP_LOGW(
                    TAG,
                    "STARTUP: ignored non-matching PONG seq=%" PRIu32,
                    seq
                );
            }
        }
        else{
            s_parse_error_count++;
            ESP_LOGW(TAG, "RX PONG parse error: %s", line);
        }

        return;
    }

    if(strncmp(line, "TEL,", 4) == 0){
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
            parse_i32_field(line, "left_pwm=", &parsed.left_pwm) &&
            parse_i32_field(line, "right_pwm=", &parsed.right_pwm) &&
            parse_i32_field(line, "left_cps=", &parsed.left_cps) &&
            parse_i32_field(line, "right_cps=", &parsed.right_cps) &&
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
                " left_pwm=%" PRIi32
                " right_pwm=%" PRIi32
                " left_cps=%" PRIi32
                " right_cps=%" PRIi32
                " err=%" PRIu32
                " tel_count=%" PRIu32,
                s_telemetry.t_ms,
                s_telemetry.state,
                s_telemetry.last_seq,
                s_telemetry.vx_mmps,
                s_telemetry.w_mradps,
                s_telemetry.left_pwm,
                s_telemetry.right_pwm,
                s_telemetry.left_cps,
                s_telemetry.right_cps,
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

    if(strncmp(line, "ACK,", 4) == 0){
        uint32_t seq = 0;
        char type[16] = {0};

        int parse_ok =
            parse_u32_field(line, "seq=", &seq) &&
            parse_string_field(line, "type=", type, sizeof(type));

        if(parse_ok){
            s_ack_count++;
            ESP_LOGI(
                TAG,
                "RX ACK: seq=%" PRIu32
                " type=%s"
                " ack_count=%" PRIu32,
                seq,
                type,
                s_ack_count
            );

            if(
                s_startup_state == BRIDGE_STARTUP_WAIT_DISARM_ACK &&
                seq == s_startup_disarm_seq &&
                strcmp(type, "DISARM") == 0
            ){
                s_last_ack_seq = seq;
                snprintf(
                    s_last_ack_type,
                    sizeof(s_last_ack_type),
                    "%s",
                    type
                );
                s_last_ack_valid = true;
            }
            else if(s_startup_state != BRIDGE_STARTUP_READY){
                ESP_LOGW(
                    TAG,
                    "STARTUP: ignored non-matching ACK seq=%" PRIu32
                    " type=%s",
                    seq,
                    type
                );
            }
        }
        else {
            s_parse_error_count++;
            ESP_LOGW(TAG, "RX ACK parse error: %s", line);
        }

        return;
    }

    if(strncmp(line, "ERR,", 4) == 0){
        s_err_count++;
        ESP_LOGW(TAG, "RX ERR: %s", line);
        return;
    }

    s_parse_error_count++;
    ESP_LOGW(TAG, "RX UNKNOWN: %s", line);
}

static void bridge_uart_handle_rx_byte(uint8_t byte){
    if(byte == '\n'){
        if(s_rx_discard_until_lf){
            s_rx_discard_until_lf = false;
            s_rx_line_len = 0U;
            return;
        }

        if(
            s_rx_line_len > 0U &&
            s_rx_line_buf[s_rx_line_len - 1U] == '\r'
        ){
            s_rx_line_len--;
        }

        s_rx_line_buf[s_rx_line_len] = '\0';

        if(s_rx_line_len > 0U){
            bridge_uart_handle_rx_line(s_rx_line_buf);
        }

        s_rx_line_len = 0U;
        return;
    }

    if(s_rx_discard_until_lf){
        return;
    }

    if(
        s_rx_line_len > 0U &&
        s_rx_line_buf[s_rx_line_len - 1U] == '\r'
    ){
        ESP_LOGW(TAG, "RX embedded CR rejected");
        s_parse_error_count++;
        s_rx_line_len = 0U;
        s_rx_discard_until_lf = true;
        return;
    }

    if((byte < 0x20U && byte != '\r') || byte == 0x7fU){
        ESP_LOGW(TAG, "RX control byte rejected: 0x%02x", byte);
        s_parse_error_count++;
        s_rx_line_len = 0U;
        s_rx_discard_until_lf = true;
        return;
    }

    if(s_rx_line_len < (LINE_BUF_SIZE - 1U)){
        s_rx_line_buf[s_rx_line_len] = (char)byte;
        s_rx_line_len++;
    }
    else {
        ESP_LOGW(TAG, "RX line overflow");
        s_parse_error_count++;
        s_rx_line_len = 0U;
        s_rx_discard_until_lf = true;
    }
}

static void bridge_uart_startup_step(TickType_t now){
    switch(s_startup_state){
        case BRIDGE_STARTUP_SETTLE:
            if(
                now - s_startup_state_tick >=
                pdMS_TO_TICKS(STARTUP_SETTLE_MS)
            ){
                int sync_written = uart_write_bytes(
                    BRIDGE_UART_NUM,
                    "\n",
                    1
                );

                if(sync_written != 1){
                    s_startup_state = BRIDGE_STARTUP_FAILED;
                    ESP_LOGE(TAG, "STARTUP FAILED: line sync TX failed");
                    break;
                }

                ESP_LOGI(TAG, "STARTUP: line sync sent");

                s_startup_state = BRIDGE_STARTUP_SYNC_WAIT;
                s_startup_state_tick = now;
            }
            break;

        case BRIDGE_STARTUP_SYNC_WAIT:
            if(
                now - s_startup_state_tick >=
                pdMS_TO_TICKS(STARTUP_SYNC_WAIT_MS)
            ){
                esp_err_t flush_result = uart_flush_input(BRIDGE_UART_NUM);

                if(flush_result != ESP_OK){
                    s_startup_state = BRIDGE_STARTUP_FAILED;
                    ESP_LOGE(TAG, "STARTUP FAILED: RX flush failed");
                    break;
                }

                s_rx_line_len = 0U;
                s_rx_discard_until_lf = false;
                s_last_ack_valid = false;
                s_startup_attempt_count = 1U;

                if(!bridge_uart_send_disarm(s_startup_disarm_seq)){
                    s_startup_state = BRIDGE_STARTUP_FAILED;
                    ESP_LOGE(TAG, "STARTUP FAILED: DISARM TX failed");
                    break;
                }

                s_startup_state = BRIDGE_STARTUP_WAIT_DISARM_ACK;
                s_startup_state_tick = now;
            }
            break;

        case BRIDGE_STARTUP_WAIT_DISARM_ACK:
            if(
                s_last_ack_valid &&
                s_last_ack_seq == s_startup_disarm_seq &&
                strcmp(s_last_ack_type, "DISARM") == 0
            ){
                ESP_LOGI(TAG, "STARTUP: DISARM acknowledged");

                s_last_pong_valid = false;
                s_startup_attempt_count = 1U;

                if(!bridge_uart_send_ping(s_startup_ping_seq)){
                    s_startup_state = BRIDGE_STARTUP_FAILED;
                    ESP_LOGE(TAG, "STARTUP FAILED: PING TX failed");
                    break;
                }

                s_startup_state = BRIDGE_STARTUP_WAIT_PONG;
                s_startup_state_tick = now;
                break;
            }

            if(
                now - s_startup_state_tick >=
                pdMS_TO_TICKS(STARTUP_RESPONSE_TIMEOUT_MS)
            ){
                if(s_startup_attempt_count < STARTUP_MAX_ATTEMPTS){
                    s_startup_attempt_count++;
                    s_last_ack_valid = false;

                    ESP_LOGW(
                        TAG,
                        "STARTUP: retry DISARM attempt=%" PRIu32,
                        s_startup_attempt_count
                    );

                    if(!bridge_uart_send_disarm(s_startup_disarm_seq)){
                        s_startup_state = BRIDGE_STARTUP_FAILED;
                        ESP_LOGE(
                            TAG,
                            "STARTUP FAILED: DISARM retry TX failed"
                        );
                        break;
                    }
                    s_startup_state_tick = now;
                }
                else {
                    s_startup_state = BRIDGE_STARTUP_FAILED;
                    ESP_LOGE(
                        TAG,
                        "STARTUP FAILED: no matching DISARM ACK"
                    );
                }
            }
            break;

        case BRIDGE_STARTUP_WAIT_PONG:
            if(
                s_last_pong_valid &&
                s_last_pong_seq == s_startup_ping_seq
            ){
                s_startup_state = BRIDGE_STARTUP_READY;

                ESP_LOGI(
                    TAG,
                    "STARTUP READY: DISARM ACK and PONG verified"
                );
                break;
            }

            if(
                now - s_startup_state_tick >=
                pdMS_TO_TICKS(STARTUP_RESPONSE_TIMEOUT_MS)
            ){
                if(s_startup_attempt_count < STARTUP_MAX_ATTEMPTS){
                    s_startup_attempt_count++;
                    s_last_pong_valid = false;

                    ESP_LOGW(
                        TAG,
                        "STARTUP: retry PING attempt=%" PRIu32,
                        s_startup_attempt_count
                    );

                    if(!bridge_uart_send_ping(s_startup_ping_seq)){
                        s_startup_state = BRIDGE_STARTUP_FAILED;
                        ESP_LOGE(
                            TAG,
                            "STARTUP FAILED: PING retry TX failed"
                        );
                        break;
                    }
                    s_startup_state_tick = now;
                }
                else {
                    s_startup_state = BRIDGE_STARTUP_FAILED;
                    ESP_LOGE(
                        TAG,
                        "STARTUP FAILED: no matching PONG"
                    );
                }
            }
            break;

        case BRIDGE_STARTUP_READY:
        case BRIDGE_STARTUP_FAILED:
        default:
            break;
    }
}

void app_main(void){
    ESP_LOGI(TAG, "ESP UART bridge app start");

    bridge_uart_init();
    ESP_LOGI(TAG, "UART1 init done: TX=GPIO%d RX=GPIO%d baud=%d",
        BRIDGE_UART_TX_GPIO,
        BRIDGE_UART_RX_GPIO,
        BRIDGE_UART_BAUD);

    s_startup_disarm_seq = esp_random();
    s_startup_ping_seq = s_startup_disarm_seq + 1U;

    uint32_t test_seq = s_startup_ping_seq + 1U;
    bridge_test_step_t test_step = BRIDGE_TEST_CMD_BEFORE_ARM;

    #if BRIDGE_MALFORMED_COMMAND_TEST_ENABLED
        uint8_t malformed_test_step = 0U;
    #endif

    s_startup_state = BRIDGE_STARTUP_SETTLE;
    s_startup_state_tick = xTaskGetTickCount();
    s_startup_attempt_count = 0U;

    if (BRIDGE_SCRIPTED_TEST_ENABLED == 0U){
        ESP_LOGI(TAG, "Scripted UART safety sequence disabled");
    }
    else {
        ESP_LOGI(TAG, "P-03 target runtime scripted test enabled");
    }

    #if BRIDGE_MALFORMED_COMMAND_TEST_ENABLED
        ESP_LOGW(TAG, "STM32 malformed-command recovery test enabled");
    #endif

    TickType_t last_test_tick = s_startup_state_tick;
    bool startup_ready_seen = false;

    while(1){
        uint8_t rx_byte;
        int rx_len = uart_read_bytes(
            BRIDGE_UART_NUM,
            &rx_byte,
            1,
            pdMS_TO_TICKS(RX_POLL_MS)
        );

        if(rx_len == 1){
            bridge_uart_handle_rx_byte(rx_byte);
        }

        TickType_t now = xTaskGetTickCount();
        bridge_uart_startup_step(now);

        if(
            s_startup_state == BRIDGE_STARTUP_READY &&
            !startup_ready_seen
        ){
            startup_ready_seen = true;
            last_test_tick = now;
        }

        if(
            BRIDGE_SCRIPTED_TEST_ENABLED != 0U &&
            s_startup_state == BRIDGE_STARTUP_READY &&
            test_step != BRIDGE_TEST_DONE &&
            now - last_test_tick >= pdMS_TO_TICKS(P03_TEST_STEP_PERIOD_MS)
        ){
            test_step = bridge_uart_run_test_step(test_step, &test_seq);
            last_test_tick = now;
        }

        #if BRIDGE_MALFORMED_COMMAND_TEST_ENABLED
                if(
                    s_startup_state == BRIDGE_STARTUP_READY &&
                    malformed_test_step < MALFORMED_TEST_DONE_STEP &&
                    now - last_test_tick >= pdMS_TO_TICKS(TEST_STEP_PERIOD_MS)
                ){
                    malformed_test_step =
                        bridge_uart_run_malformed_command_test_step(
                            malformed_test_step
                        );
                    last_test_tick = now;
                }
        #endif
    }
}
