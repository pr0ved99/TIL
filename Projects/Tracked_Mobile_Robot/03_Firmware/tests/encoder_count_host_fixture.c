/* Appended to drive_output_profile_host_fixture.c with simulated HAL only. */
static void encoder_reset_host(void)
{
    host_ms = 0U;
    host_estop = GPIO_PIN_RESET;
    assert(motor_output_init(&host_timer) == HAL_OK);
    uart_mvp_init(&host_uart);
    uart_mvp_start_rx();
}

int main(void)
{
    assert(profile_main() == 0);
    encoder_reset_host();
    assert(!s_encoder_sample.valid && !s_encoder_sample.arm_valid);
    assert(!s_encoder_arm_valid);
    assert(s_encoder_sample.left_count == 0 && s_encoder_sample.right_count == 0);
    puts("PASS boot: no encoder sample or accepted ARM interval");

    s_encoder_tim3 = (host_encoder_t){.accumulated_count = -1560, .counts_per_second = -260};
    s_encoder_tim5 = (host_encoder_t){.accumulated_count = 3120, .counts_per_second = 520};
    host_publish_sample(100U);
    assert(s_encoder_sample.valid && !s_encoder_sample.arm_valid);
    assert(s_encoder_sample.left_count == 1560 && s_encoder_sample.right_count == 3120);
    assert(s_left_cps == 260 && s_right_cps == 520);
    puts("PASS actual main publish block: TIM3 sign inverted, TIM5 kept, CPS paired with count");

    feed("ARM,seq=0\n");
    assert(strstr(host_tx, "ACK,seq=0,type=ARM,"));
    assert(s_encoder_arm_valid && s_encoder_arm_seq == 0U);
    assert(!s_encoder_sample.valid && !s_encoder_sample.arm_valid);
    assert(s_encoder_sample.left_count == 1560);
    puts("PASS accepted ARM: old sample invalidated without resetting accumulated count");

    host_publish_sample(120U);
    assert(s_encoder_sample.valid && s_encoder_sample.arm_valid);
    assert(s_encoder_sample.arm_seq == 0U);
    host_ms = 200U;
    host_tx_len = 0U;
    send_tel();
    assert(strstr(host_tx, "TEL,t_ms=200,"));
    assert(strstr(host_tx, "encoder_valid=1,encoder_t_ms=120,"));
    assert(strstr(host_tx, "left_count=1560,right_count=3120,"));
    assert(strstr(host_tx, "encoder_arm_valid=1,encoder_arm_seq=0,"));
    unsigned commas = 0U;
    for (const char *p = host_tx; *p; ++p) commas += *p == ',';
    assert(commas == 20U && host_tx[host_tx_len - 1U] == '\n');
    puts("PASS TEL: 20 fields, sample time distinct from send time, seq zero is a valid ARM");

    feed("CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300\n");
    output(144, 150);
    feed("DISARM,seq=2\n");
    output(0, 0);
    host_publish_sample(220U);
    assert(s_encoder_sample.valid && s_encoder_sample.arm_valid && s_encoder_sample.arm_seq == 0U);
    assert(s_encoder_sample.left_count == 1560);
    puts("PASS DISARM: output zero and stopped endpoint retains the measurement interval");

    s_encoder_tim3.accumulated_count = 1560;
    s_encoder_tim5.accumulated_count = -1560;
    host_publish_sample(240U);
    assert(s_encoder_sample.valid && s_encoder_sample.left_count == -1560);
    assert(s_encoder_sample.right_count == -1560 && s_encoder_sample.arm_seq == 0U);
    puts("PASS reverse: decreasing/negative count stays valid in the same interval");

    feed("ARM,seq=99\n");
    assert(!s_encoder_sample.valid && !s_encoder_sample.arm_valid);
    host_publish_sample(260U);
    assert(s_encoder_sample.valid && s_encoder_sample.arm_valid && s_encoder_sample.arm_seq == 99U);
    assert(s_encoder_sample.left_count == -1560 && s_encoder_sample.right_count == -1560);
    puts("PASS next ARM: a new interval label, same raw cumulative count");

    host_estop = GPIO_PIN_SET;
    feed("ARM,seq=100\n");
    output(0, 0);
    assert(strstr(host_tx, "ESTOP_LATCHED"));
    assert(s_encoder_arm_seq == 99U);
    puts("PASS rejected ARM: ESTOP stops and does not relabel the interval");

    uart_mvp_set_encoder_sample(1, -1, INT64_MAX, INT64_MIN, UINT32_MAX, true);
    host_tx_len = 0U;
    send_tel();
    assert(strstr(host_tx, "left_count=9223372036854775807,right_count=-9223372036854775808,"));
    assert(strstr(host_tx, "encoder_t_ms=4294967295,"));
    assert(host_tx_len < UART_TX_BUFFER_SIZE && host_tx[host_tx_len - 1U] == '\n');
    puts("PASS int64 endpoints: exact decimal serialization, uint32 sample tick and complete LF");

    s_encoder_tim3.accumulated_count = INT64_MIN;
    host_publish_sample(280U);
    assert(!s_encoder_sample.valid);
    assert(s_encoder_sample.left_count == 0 && s_encoder_sample.right_count == 0);
    assert(s_left_cps == 260 && s_right_cps == 520);
    puts("PASS non-negatable left raw count: invalid measurement, CPS control input preserved");

    const uint32_t prior_sample_ms = s_encoder_sample.sample_ms;
    encoder_reset_host();
    s_encoder_tim3 = (host_encoder_t){0};
    s_encoder_tim5 = (host_encoder_t){0};
    host_publish_sample(prior_sample_ms + 1000U);
    assert(s_encoder_sample.valid && !s_encoder_sample.arm_valid);
    assert(!s_encoder_arm_valid && s_encoder_sample.sample_ms > prior_sample_ms);
    puts("PASS STM init: prior interval cleared, even when new sample time is greater than old time");
    return 0;
}
