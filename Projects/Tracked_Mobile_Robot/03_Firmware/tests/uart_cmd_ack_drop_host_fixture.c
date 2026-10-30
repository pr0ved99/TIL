/* Actual STM protocol/parser/mapper and ESP executor; hardware/time mocked. */
#define main baseline_diagnostic_main
#include "stm_uart_stream_host_fixture.c"
#undef main

static unsigned tests;
#define RUN(test) do { test(); tests++; puts("PASS " #test); } while (0)

static void zero_cmd(uint32_t seq, uint32_t now)
{
    char text[96];
    tick(now); clear_tx();
    snprintf(text, sizeof(text), "CMD,seq=%lu,vx_mmps=0,w_mradps=0,timeout_ms=300\n",
             (unsigned long)seq);
    feed(text);
}

static void startup_and_normal_stop(void)
{
    reset_host(); feed("DISARM,seq=90\nPING,seq=91\n");
    assert(strstr(host_tx, "ACK,seq=90,type=DISARM,"));
    assert(strstr(host_tx, "PONG,seq=91,"));
    feed("ARM,seq=92\nDISARM,seq=93\n");
    assert(strstr(host_tx, "ACK,seq=92,type=ARM,"));
    assert(strstr(host_tx, "ACK,seq=93,type=DISARM,"));
    assert(!strstr(host_tx, "TEST_CMD_ACK_DROP"));
    assert(s_state == ROBOT_DISARMED);
}

static void tenth_only_and_restore_path(void)
{
    reset_host(); feed("ARM,seq=1\n");
    for (uint32_t i = 1; i <= 12; ++i) {
        zero_cmd(i + 1, i * 100);
        assert(s_state == ROBOT_ARMED && s_last_seq == i + 1);
        assert(host_output.left_signed_permille == 0 && host_output.right_signed_permille == 0);
        assert(s_last_accepted_cmd_ms == i * 100 && s_error_count == 0);
        if (UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED && i == 10) {
            assert(!strstr(host_tx, "ACK,"));
            assert(strstr(host_tx, "TEST_CMD_ACK_DROP,seq=11,t_ms=1000,zero_count=10\n"));
        } else {
            assert(strstr(host_tx, "type=CMD,"));
            assert(!strstr(host_tx, "TEST_CMD_ACK_DROP"));
        }
    }
    feed("\x18\nDISARM,seq=14\n");
    assert(strstr(host_tx, "ACK,seq=14,type=DISARM,"));
    assert(s_state == ROBOT_DISARMED);
    clear_tx(); tick(1300);
    assert(strstr(host_tx, "state=DISARMED,reason=DISARM,"));
    assert(!strstr(host_tx, "ACK,"));
    feed("ARM,seq=15\n");
    for (uint32_t i = 1; i <= 11; ++i) {
        zero_cmd(i + 15, 1300 + i * 100);
        assert(strstr(host_tx, "type=CMD,"));
        assert(!strstr(host_tx, "TEST_CMD_ACK_DROP"));
    }
}

#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
static void reset_and_ineligible_commands(void)
{
    reset_host(); feed("CMD,seq=1,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    assert(strstr(host_tx, "code=NOT_ARMED,"));
    assert(s_cmd_ack_drop_zero_count == 0 && !s_cmd_ack_drop_used);
    feed("ARM,seq=2\n");
    for (uint32_t i = 1; i <= 9; ++i) zero_cmd(i + 2, i * 100);
    feed("CMD,seq=12,vx_mmps=0,w_mradps=0,timeout_ms=0\n");
    assert(strstr(host_tx, "code=TIMEOUT_OUT_OF_RANGE,"));
    assert(s_cmd_ack_drop_zero_count == 9 && !s_cmd_ack_drop_used);
    feed("ARM,seq=13\n");
    assert(s_cmd_ack_drop_zero_count == 0);
    zero_cmd(14, 1000); assert(strstr(host_tx, "type=CMD,"));
    uart_mvp_set_encoder_cps(1, 0);
    zero_cmd(15, 1100); assert(s_cmd_ack_drop_zero_count == 0 && !s_cmd_ack_drop_used);
    uart_mvp_set_encoder_cps(0, -1);
    zero_cmd(16, 1200); assert(s_cmd_ack_drop_zero_count == 0 && !s_cmd_ack_drop_used);
    uart_mvp_set_encoder_cps(0, 0);
    feed("CMD,seq=17,vx_mmps=50,w_mradps=0,timeout_ms=300\n");
    assert(strstr(host_tx, "ACK,seq=17,type=CMD,"));
    assert(s_cmd_ack_drop_zero_count == 0 && !s_cmd_ack_drop_used);
    for (uint32_t i = 1; i <= 10; ++i) zero_cmd(i + 17, 1200 + i * 100);
    assert(s_cmd_ack_drop_used && strstr(host_tx, "TEST_CMD_ACK_DROP,"));
    reset_host(); assert(!s_cmd_ack_drop_used && s_cmd_ack_drop_zero_count == 0);
}

static void physical_state_dimensions(void)
{
    /* Independently check dimensions that handle_cmd normally overwrites. */
    for (unsigned i = 0; i < 8; ++i) {
        reset_host(); arm_zero(); s_cmd_ack_drop_zero_count = 9;
        switch (i) {
        case 0: host_output.left_signed_permille = 1; break;
        case 1: host_output.right_signed_permille = -1; break;
        case 2: s_vx_mmps = 1; break;
        case 3: s_w_mradps = 1; break;
        case 4: s_state = ROBOT_DISARMED; break;
        case 5: s_estop_latched = 1; break;
        case 6: host_estop = GPIO_PIN_SET; break;
        default: s_state = ROBOT_FAULT; break;
        }
        assert(!drop_cmd_ack_once(3));
        assert(!s_cmd_ack_drop_used && s_cmd_ack_drop_zero_count == 0);
    }
}

static void watchdog_estop_and_cancel_remain_live(void)
{
    reset_host(); feed("ARM,seq=1\n");
    for (uint32_t i = 1; i <= 10; ++i) zero_cmd(i + 1, i * 100);
    clear_tx(); tick(1100);
    assert(strstr(host_tx, "TEL,t_ms=1100,state=ARMED,reason=NONE,"));
    assert(strstr(host_tx, "command_age_ms=100,last_seq=11,"));
    assert(!strstr(host_tx, "ACK,"));
    tick(1299); assert(s_state == ROBOT_ARMED);
    tick(1300); assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_CMD_TIMEOUT);
    assert(!strstr(host_tx, "ACK,"));
    feed("CMD,seq=12,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    assert(strstr(host_tx, "ERR,seq=12,type=CMD,code=NOT_ARMED,"));
    feed("ARM,seq=99\x18\nDISARM,seq=13\n");
    assert(!strstr(host_tx, "ACK,seq=99,"));
    assert(strstr(host_tx, "ACK,seq=13,type=DISARM,"));
    reset_host(); feed("ARM,seq=1\n");
    for (uint32_t i = 1; i <= 9; ++i) zero_cmd(i + 1, i * 100);
    host_estop = GPIO_PIN_SET; zero_cmd(11, 1000);
    assert(s_state == ROBOT_FAULT && s_estop_latched && !s_cmd_ack_drop_used);
    host_estop = GPIO_PIN_RESET; tick(1100);
    assert(s_state == ROBOT_FAULT && s_reason == ROBOT_REASON_ESTOP_LATCHED);
    assert(host_output.left_signed_permille == 0 && host_output.right_signed_permille == 0);
}

static wifi_control_executor_t exec;
static wifi_control_ticket_pool_t pool;
static wifi_control_tx_t frame;

static void relay_tel(uint32_t now)
{
    tick(now);
    wifi_control_tel_t t = {.state = s_state == ROBOT_ARMED ? WIFI_CONTROL_STM_ARMED : WIFI_CONTROL_STM_DISARMED,
        .t_ms = now, .last_seq = s_last_seq, .command_age_ms = now - s_last_accepted_cmd_ms,
        .vx_mmps = s_vx_mmps, .w_mradps = s_w_mradps,
        .left_pwm = host_output.left_signed_permille, .right_pwm = host_output.right_signed_permille};
    wifi_control_executor_tel(&exec, &t, now);
}

static void send_request(wifi_control_type_t type, uint32_t seq, uint32_t now)
{
    relay_tel(now);
    wifi_control_ticket_t ticket = {0};
    uint32_t id = type == WIFI_CONTROL_ARM ? 0 : exec.state.owner.control_id;
    assert(wifi_control_ticket_issue(&pool, &ticket, 7, type, id, now) == WIFI_TICKET_OK);
    wifi_control_request_t r = {.type = type, .expected_boot_id = 42,
        .request_id = ticket.id, .ws_session_id = 7, .control_id = id, .ticket = ticket.id};
    assert(wifi_control_executor_submit(&exec, &r, &ticket, true, true, now) == WIFI_EXEC_ACCEPTED);
    assert(wifi_control_executor_take_tx(&exec, seq, now, &frame));
    assert(wifi_control_executor_tx_complete(&exec, (int)frame.length, now));
    clear_tx(); feed(frame.bytes);
}

static void accept_reply(uint32_t seq, wifi_control_op_t op, uint32_t now)
{
    unsigned long actual, processed; char type[16];
    const char *a = strstr(host_tx, "ACK,");
    assert(a && sscanf(a, "ACK,seq=%lu,type=%15[^,],t_ms=%lu", &actual, type, &processed) == 3);
    assert(actual == seq);
    assert(strcmp(type, op == WIFI_CONTROL_OP_ARM ? "ARM" : op == WIFI_CONTROL_OP_CMD ? "CMD" : "DISARM") == 0);
    assert(wifi_control_executor_reply(&exec, op, seq, true, (uint32_t)processed, now));
    wifi_control_executor_result_t result;
    while (wifi_control_executor_take_result(&exec, &result)) assert(strcmp(result.status, "OK") == 0);
}

static void esp_requires_ack_despite_fresh_tel(void)
{
    reset_host(); wifi_control_executor_init(&exec, 42); wifi_control_ticket_pool_init(&pool, 42);
    send_request(WIFI_CONTROL_ARM, 100, 1000); accept_reply(100, WIFI_CONTROL_OP_ARM, 1000);
    for (uint32_t i = 1; i <= 10; ++i) {
        uint32_t now = 1000 + i * 100;
        send_request(WIFI_CONTROL_CMD, 100 + i, now);
        if (i < 10) {
            accept_reply(100 + i, WIFI_CONTROL_OP_CMD, now);
            relay_tel(now + 1); assert(exec.state.phase == WIFI_CONTROL_ACTIVE);
        }
    }
    assert(strstr(host_tx, "TEST_CMD_ACK_DROP,seq=110,"));
    assert(!strstr(host_tx, "ACK,"));
    relay_tel(2100);
    assert(exec.state.phase == WIFI_CONTROL_ACTIVE && exec.waiting);
    assert(exec.state.pending == WIFI_CONTROL_OP_CMD && exec.state.tel.last_seq == 110);
    wifi_control_executor_poll(&exec, true, 2149);
    assert(exec.state.phase == WIFI_CONTROL_ACTIVE);
    wifi_control_executor_poll(&exec, true, 2150);
    assert(exec.state.phase == WIFI_CONTROL_STOPPING && exec.state.reason == WIFI_CONTROL_REASON_ACK_TIMEOUT);
    assert(exec.state.owner.ws_session_id == 0 && exec.state.owner.control_id == 0);
    wifi_control_executor_result_t result;
    assert(wifi_control_executor_take_result(&exec, &result));
    assert(result.seq == 110 && result.has_seq && strcmp(result.status, "TIMEOUT") == 0);
    assert(!exec.queued && !exec.waiting && wifi_control_executor_needs_invalidation(&exec));
    assert(!wifi_control_executor_take_tx(&exec, 111, 2150, &frame));
    wifi_control_executor_inputs_cleared(&exec);
    assert(wifi_control_executor_take_tx(&exec, 111, 2150, &frame));
    assert(frame.op == WIFI_CONTROL_OP_DISARM && strstr(frame.bytes, "\x18\nDISARM,seq=111\n"));
    assert(wifi_control_executor_tx_complete(&exec, (int)frame.length, 2150));
    tick(2150); clear_tx(); feed(frame.bytes);
    assert(s_state == ROBOT_DISARMED); accept_reply(111, WIFI_CONTROL_OP_DISARM, 2150);
    assert(exec.state.phase == WIFI_CONTROL_STOPPING); /* New TEL still required. */
    relay_tel(2151); assert(exec.state.phase == WIFI_CONTROL_IDLE);
    clear_tx();
    for (uint32_t now = 2251; now <= 5251; now += 100) {
        relay_tel(now); wifi_control_executor_poll(&exec, true, now);
        assert(exec.state.phase == WIFI_CONTROL_IDLE && s_state == ROBOT_DISARMED);
        assert(!wifi_control_executor_take_tx(&exec, 112, now, &frame));
    }
    assert(!strstr(host_tx, "ACK,")); /* The omitted ACK is never released later. */
    send_request(WIFI_CONTROL_ARM, 112, 5300); accept_reply(112, WIFI_CONTROL_OP_ARM, 5300);
    send_request(WIFI_CONTROL_CMD, 113, 5400); accept_reply(113, WIFI_CONTROL_OP_CMD, 5400);
    relay_tel(5401); assert(exec.state.phase == WIFI_CONTROL_ACTIVE);
}
#endif

int main(void)
{
    RUN(startup_and_normal_stop);
    RUN(tenth_only_and_restore_path);
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    RUN(reset_and_ineligible_commands);
    RUN(physical_state_dimensions);
    RUN(watchdog_estop_and_cancel_remain_live);
    RUN(esp_requires_ack_despite_fresh_tel);
#endif
    printf("PASS mode=%u: %u native case groups; no board evidence\n",
           UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED, tests);
    return 0;
}
