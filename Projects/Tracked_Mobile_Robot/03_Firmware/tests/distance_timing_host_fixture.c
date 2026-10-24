/* Appended to the existing saved-C drive profile fixture in the PC runner. */
#include "encoder_speed.h"

static bool host_async;
static HAL_StatusTypeDef host_it_status = HAL_OK;
static const uint8_t *host_inflight;
static uint16_t host_inflight_len;
static uint8_t host_inflight_copy[512];
static unsigned host_blocking_calls;
static encoder_speed_t s_encoder_tim3, s_encoder_tim5;
static TIM_HandleTypeDef htim3, htim5;
static uint32_t s_encoder_last_publish_ms;
#define ENCODER_COUNT_SAMPLE_PERIOD_MS 5U
#define __HAL_TIM_GET_COUNTER(timer) ((timer)->compare[0])

HAL_StatusTypeDef HAL_UART_Transmit_IT(UART_HandleTypeDef *uart,
                                      const uint8_t *data, uint16_t size)
{
    assert(uart == &host_uart && size > 0 && size < sizeof(host_inflight_copy));
    if (host_it_status != HAL_OK) return host_it_status;
    if (host_async) {
        assert(host_inflight == NULL);
        host_inflight = data;
        host_inflight_len = size;
        memcpy(host_inflight_copy, data, size);
    } else {
        assert(host_tx_len + size < sizeof(host_tx));
        memcpy(host_tx + host_tx_len, data, size);
        host_tx_len += size;
        host_tx[host_tx_len] = 0;
        uart_mvp_on_tx_complete(uart);
    }
    return HAL_OK;
}

static void complete_tx(void)
{
    assert(host_inflight != NULL);
    assert(memcmp(host_inflight, host_inflight_copy, host_inflight_len) == 0);
    assert(host_tx_len + host_inflight_len < sizeof(host_tx));
    memcpy(host_tx + host_tx_len, host_inflight, host_inflight_len);
    host_tx_len += host_inflight_len;
    host_tx[host_tx_len] = 0;
    host_inflight = NULL;
    uart_mvp_on_tx_complete(&host_uart);
}

/* Simulates a board reset, including terminating the mock peripheral transfer. */
static void fresh(void)
{
    host_ms = 0;
    host_estop = GPIO_PIN_RESET;
    host_inflight = NULL;
    host_tx_len = 0; host_tx[0] = 0;
    host_it_status = HAL_OK;
    host_async = true;
    motor_output_stop_all();
    uart_mvp_init(&host_uart);
    uart_mvp_start_rx();
}

static void drive_on(void)
{
    s_state = ROBOT_ARMED;
    s_last_cmd_ms = host_ms;
    s_cmd_timeout_ms = 300;
    assert(motor_output_set_signed(144, 150) == HAL_OK);
}

/* The runner inserts the actual candidate main.c sampling functions here. */
/* INSERT_MAIN_SAMPLE */

int main(void)
{
    unsigned i;
    int64_t value;
    encoder_speed_t enc;
    encoder_speed_t original;
    UART_HandleTypeDef other_uart;
    assert(profile_main() == 0);
    assert(host_blocking_calls == 0);

    assert(encoder_speed_init(&enc, ENCODER_COUNTER_WIDTH_16, 65530, 0, 100));
    original = enc;
    assert(encoder_speed_snapshot(&enc, 5, &value) && value == 11);
    assert(enc.previous_raw == original.previous_raw &&
           enc.last_sample_ms == 0 && enc.accumulated_count == 0);
    assert(encoder_speed_update(&enc, 5, 100));
    assert(enc.accumulated_count == 11 && enc.counts_per_second == 110);
    assert(encoder_speed_snapshot(&enc, 10, &value) && value == 16);
    assert(encoder_speed_snapshot(&enc, 0, &value) && value == 6);
    assert(encoder_speed_init(&enc, ENCODER_COUNTER_WIDTH_32, 0xFFFFFFFAU, 0, 100));
    assert(encoder_speed_snapshot(&enc, 5, &value) && value == 11);
    assert(!encoder_speed_snapshot(NULL, 0, &value) && value == 0);
    assert(!encoder_speed_snapshot(&enc, 0, NULL));
    enc.initialized = false;
    assert(!encoder_speed_snapshot(&enc, 0, &value));
    enc.initialized = true; enc.previous_raw = 0;
    enc.accumulated_count = INT64_MAX;
    assert(!encoder_speed_snapshot(&enc, 1, &value) && value == 0);
    enc.accumulated_count = INT64_MIN;
    assert(!encoder_speed_snapshot(&enc, UINT32_MAX, &value) && value == 0);
    puts("PASS snapshot: 16/32-bit wrap, reverse, no CPS-window mutation, null/overflow rejection");

    fresh();
    s_encoder_last_publish_ms = 0;
    assert(encoder_speed_init(&s_encoder_tim3, ENCODER_COUNTER_WIDTH_16, 65530, 0, 100));
    assert(encoder_speed_init(&s_encoder_tim5, ENCODER_COUNTER_WIDTH_32, 0xFFFFFFFAU, 0, 100));
    for (i = 5; i <= 200; i += 5) {
        host_ms = i;
        htim3.compare[0] = (65530U - i) & 0xFFFFU;
        htim5.compare[0] = 0xFFFFFFFAU + i;
        encoder_speed_log_process();
        assert(s_encoder_sample.valid && s_encoder_sample.sample_ms == i);
        assert(s_encoder_sample.left_count == i && s_encoder_sample.right_count == i);
        assert(s_left_cps == (i < 100 ? 0 : 1000));
        assert(s_right_cps == (i < 100 ? 0 : 1000));
        assert(s_encoder_tim3.last_sample_ms == i / 100 * 100);
    }
    assert(host_blocking_calls == 0);
    /* Left normalization cannot negate INT64_MIN. */
    s_encoder_tim3.accumulated_count = INT64_MIN;
    host_ms = 205;
    encoder_speed_log_process();
    assert(!s_encoder_sample.valid && s_encoder_sample.left_count == 0);
    puts("PASS main sampling: count every5ms, CPS every100ms, TIM3 sign, invalid normalization, no USB wait");

    fresh(); host_async = false; s_encoder_last_publish_ms = 0;
    assert(encoder_speed_init(&s_encoder_tim3, ENCODER_COUNTER_WIDTH_16, 65530, 0, 100));
    assert(encoder_speed_init(&s_encoder_tim5, ENCODER_COUNTER_WIDTH_32, 0, 0, 100));
    htim3.compare[0] = 65529; htim5.compare[0] = 2;
    host_ms = 5; encoder_speed_log_process();
    feed("ARM,seq=42\n"); assert(!s_encoder_sample.valid);
    host_ms = 10; encoder_speed_log_process();
    assert(s_encoder_sample.valid && s_encoder_sample.arm_valid &&
           s_encoder_sample.arm_seq == 42 && s_encoder_sample.sample_ms == 10);
    assert(s_encoder_sample.left_count == 1 && s_encoder_sample.right_count == 2);
    feed("ARM,seq=43\n"); assert(!s_encoder_sample.valid);
    host_ms = 15; encoder_speed_log_process();
    assert(s_encoder_sample.arm_seq == 43 && s_encoder_sample.left_count == 1 &&
           s_encoder_sample.right_count == 2);
    send_tel(); uart_tx_poll();
    assert(strstr(host_tx, "left_count=1,right_count=2,"));
    assert(strstr(host_tx, "encoder_arm_valid=1,encoder_arm_seq=43,"));
    puts("PASS ARM/re-ARM: wait for post-ARM5ms snapshot, preserve accumulated counts and numeric TEL contract");

    fresh();
    uart_sendf("TEL,old\n"); uart_tx_poll();
    assert(host_inflight != NULL && host_ms == 0);
    uart_sendf("TEL,replaced\n");
    uart_sendf("TEL,new\n");
    send_ack(1, "CMD"); send_ack(2, "CMD");
    assert(host_inflight_len == 8 && memcmp(host_inflight, "TEL,old\n", 8) == 0);
    uart_mvp_on_tx_complete(&other_uart);
    assert(s_tx_completed == 0);
    complete_tx(); uart_tx_poll();
    assert(memcmp(host_inflight, "ACK,seq=1,", 10) == 0);
    complete_tx(); uart_tx_poll();
    assert(memcmp(host_inflight, "ACK,seq=2,", 10) == 0);
    complete_tx(); uart_tx_poll();
    assert(host_inflight_len == 8 && memcmp(host_inflight, "TEL,new\n", 8) == 0);
    complete_tx(); uart_tx_poll();
    assert(host_inflight == NULL && !strstr(host_tx, "replaced"));
    puts("PASS async TX: frame buffer lifetime, wrong-UART callback, FIFO ACK priority, latest pending TEL");

    fresh();
    drive_on();
    uart_sendf("TEL,active\n"); uart_tx_poll();
    for (i = 0; i < UART_TX_RESPONSE_SLOTS; ++i) send_ack(i, "CMD");
    send_ack(99, "CMD");
    assert(s_tx_fault && s_state == ROBOT_DISARMED);
    output(0, 0);
    assert(memcmp(host_inflight, host_inflight_copy, host_inflight_len) == 0);
    feed("ARM,seq=200\n"); feed("CMD,seq=201,vx_mmps=100,w_mradps=0,timeout_ms=300\n");
    output(0, 0); assert(s_state == ROBOT_DISARMED);
    puts("PASS critical queue overflow: stop and latch rearm refusal; active memory remains intact");

    fresh(); drive_on();
    uart_sendf("TEL,stuck\n"); uart_tx_poll();
    host_ms = s_tx_started_ms + 99; uart_mvp_process(); output(144, 150);
    host_ms = s_tx_started_ms + 100; uart_mvp_process(); output(0, 0);
    assert(s_tx_fault && s_reason == ROBOT_REASON_OUTPUT_ERROR);
    puts("PASS TX missing completion: deadline100ms stops and latches");

    for (i = 0; i < 2; ++i) {
        fresh(); drive_on();
        host_it_status = i ? HAL_BUSY : HAL_ERROR;
        send_ack(1, "CMD"); uart_tx_poll();
        assert(s_tx_fault); output(0, 0);
    }
    puts("PASS HAL TX ERROR/BUSY: immediate latched stop");

    fresh(); drive_on();
    host_ms = 250; uart_sendf("TEL,still-inflight\n"); uart_tx_poll();
    host_ms = 300; uart_mvp_process(); output(0, 0);
    assert(!s_tx_fault && s_reason == ROBOT_REASON_CMD_TIMEOUT);
    assert(memcmp(host_inflight, host_inflight_copy, host_inflight_len) == 0);
    fresh(); drive_on();
    uart_sendf("TEL,still-inflight\n"); uart_tx_poll();
    host_ms = 10; host_estop = GPIO_PIN_SET; uart_mvp_process();
    output(0, 0); assert(s_estop_latched && s_state == ROBOT_FAULT);
    host_ms = s_tx_started_ms + 100; uart_mvp_process();
    assert(s_tx_fault && s_reason == ROBOT_REASON_ESTOP_ACTIVE);
    puts("PASS command timeout and E-stop enforced while wire transfer is active; E-stop reason preserved");

    fresh(); uart_sendf("TEL,expired\n");
    host_ms = 51; uart_tx_poll();
    assert(host_inflight == NULL && s_tx_tel_len == 0);
    fresh();
    for (i = 0; i < 100; ++i) {
        *host_rx = 'x'; uart_mvp_on_rx_complete(&host_uart);
    }
    uart_mvp_process(); assert(s_line_len == 64);
    uart_mvp_process(); assert(s_line_len == 100);
    assert(host_blocking_calls == 0);
    puts("PASS old pending TEL discarded; RX processing bounded64bytes per poll; no runtime blocking TX");
    puts("PASS timing candidate: synthetic PC execution only, no MCU build or motion");
    return 0;
}
