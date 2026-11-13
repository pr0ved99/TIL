/* Real STM stream/parser/mapper + ESP executor/state; HAL/time/motors mocked. */
#define main baseline_diagnostic_main
#include "stm_uart_stream_host_fixture.c"
#undef main

static unsigned tests;
#define RUN(test) do { test(); tests++; puts("PASS " #test); } while (0)

static void stopped(uint32_t seq)
{
    assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_DISARM);
    assert(s_last_seq == seq && s_vx_mmps == 0 && s_w_mradps == 0);
    assert(host_output.left_signed_permille == 0 && host_output.right_signed_permille == 0);
}

static void startup_immediate(void)
{
    reset_host();
    feed("DISARM,seq=10\nPING,seq=11\n");
    assert(strstr(host_tx, "ACK,seq=10,type=DISARM,t_ms=0\n"));
    assert(strstr(host_tx, "PONG,seq=11,t_ms=0\n"));
    assert(!strstr(host_tx, "TEST_ACK_DELAY"));
    feed("ARM,seq=12\nDISARM,seq=13\n"); /* No accepted CMD in this ARM. */
    assert(strstr(host_tx, "ACK,seq=13,type=DISARM,t_ms=0\n"));
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    assert(!s_delayed_disarm_ack.used);
#endif
}

static void timeout_and_cancel(void)
{
    reset_host(); arm_zero();
    tick(299); assert(s_state == ROBOT_ARMED);
    tick(300); assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_CMD_TIMEOUT);
    clear_tx(); feed("CMD,seq=3,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    assert(strstr(host_tx, "ERR,seq=3,type=CMD,code=NOT_ARMED,"));
    clear_tx(); feed("ARM,seq=99\x18\nDISARM,seq=4\n");
    assert(!strstr(host_tx, "type=ARM,"));
    assert(strstr(host_tx, "ACK,seq=4,type=DISARM,"));
    stopped(4);
}

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
static void delayed_once(void)
{
    reset_host(); arm_zero(); tick(10); clear_tx();
    feed("DISARM,seq=3\n"); stopped(3);
    assert(strstr(host_tx, "TEST_ACK_DELAY,seq=3,t_ms=10,delay_ms=500\n"));
    assert(!strstr(host_tx, "ACK,seq=3,"));
    tick(110); tick(210); tick(310); tick(410); tick(509);
    assert(!strstr(host_tx, "ACK,seq=3,"));
    assert(strstr(host_tx, "TEL,t_ms=110,state=DISARMED,reason=DISARM,"));
    clear_tx(); tick(510);
    assert(strstr(host_tx, "ACK,seq=3,type=DISARM,t_ms=10\n"));
    stopped(3); clear_tx(); tick(610);
    assert(!strstr(host_tx, "ACK,"));
    feed("ARM,seq=4\nCMD,seq=5,vx_mmps=0,w_mradps=0,timeout_ms=300\nDISARM,seq=6\n");
    assert(strstr(host_tx, "ACK,seq=6,type=DISARM,t_ms=610\n"));
    assert(!strstr(host_tx, "TEST_ACK_DELAY"));
}

static void eligibility(void)
{
    /* Each nonzero state dimension prevents injection, never prevents stop. */
    for (unsigned i = 0; i < 6; i++) {
        reset_host(); arm_zero();
        switch (i) {
        case 0: s_vx_mmps = 1; break;
        case 1: s_w_mradps = 1; break;
        case 2: host_output.left_signed_permille = 1; break;
        case 3: host_output.right_signed_permille = -1; break;
        case 4: uart_mvp_set_encoder_cps(1, 0); break;
        default: uart_mvp_set_encoder_cps(0, -1); break;
        }
        feed("DISARM,seq=3\n"); stopped(3);
        assert(strstr(host_tx, "ACK,seq=3,type=DISARM,"));
        assert(!s_delayed_disarm_ack.used && !strstr(host_tx, "TEST_ACK_DELAY"));
    }
    reset_host(); arm_zero(); feed("ARM,seq=3\nDISARM,seq=4\n");
    assert(strstr(host_tx, "ACK,seq=4,type=DISARM,"));
    assert(!s_delayed_disarm_ack.used); /* Previous ARM's CMD is insufficient. */
    reset_host(); arm_zero(); host_estop = GPIO_PIN_SET;
    feed("DISARM,seq=3\n");
    assert(s_state == ROBOT_FAULT && s_estop_latched && !s_delayed_disarm_ack.used);
    assert(strstr(host_tx, "ACK,seq=3,type=DISARM,"));
}

static void safety_during_wait(void)
{
    reset_host(); arm_zero(); feed("DISARM,seq=3\n");
    host_estop = GPIO_PIN_SET; tick(1);
    assert(s_state == ROBOT_FAULT && s_estop_latched);
    host_estop = GPIO_PIN_RESET; tick(500);
    assert(s_state == ROBOT_FAULT && s_estop_latched && s_last_seq == 3);
    assert(host_output.left_signed_permille == 0 && host_output.right_signed_permille == 0);
    assert(strstr(host_tx, "ACK,seq=3,type=DISARM,t_ms=0\n"));
    assert(strstr(host_tx, "state=FAULT,reason=ESTOP_LATCHED,"));
}

static void newer_command_not_overwritten(void)
{
    reset_host(); arm_zero(); feed("DISARM,seq=3\n");
    tick(20); clear_tx(); feed("DISARM,seq=4\n"); stopped(4);
    assert(strstr(host_tx, "ACK,seq=4,type=DISARM,t_ms=20\n"));
    clear_tx(); tick(500); stopped(4);
    assert(strstr(host_tx, "ACK,seq=3,type=DISARM,t_ms=0\n"));
    /* RX and watchdog must still execute while the old response is pending. */
    reset_host(); arm_zero(); feed("DISARM,seq=3\n");
    tick(10); feed("ARM,seq=4\nCMD,seq=5,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    tick(309); assert(s_state == ROBOT_ARMED);
    tick(310); assert(s_reason == ROBOT_REASON_CMD_TIMEOUT);
    clear_tx(); tick(500);
    assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_CMD_TIMEOUT && s_last_seq == 5);
    assert(strstr(host_tx, "ACK,seq=3,type=DISARM,t_ms=0\n"));
}

static void reset_discards_and_tick_wrap(void)
{
    reset_host(); arm_zero(); feed("DISARM,seq=3\n");
    reset_host(); tick(1000);
    assert(!strstr(host_tx, "ACK,") && !s_delayed_disarm_ack.used);
    reset_host(); tick(UINT32_MAX - 99U); arm_zero(); feed("DISARM,seq=3\n");
    clear_tx(); tick(399U); assert(!strstr(host_tx, "ACK,"));
    tick(400U); assert(strstr(host_tx, "ACK,seq=3,type=DISARM,t_ms=4294967196\n"));
    stopped(3);
}

static wifi_control_executor_t late_e;
static wifi_control_ticket_pool_t late_pool;
static wifi_control_tx_t late_tx;

static void relay_tel(uint32_t now)
{
    tick(now);
    wifi_control_tel_t t = {.state = s_state == ROBOT_ARMED ? WIFI_CONTROL_STM_ARMED :
        s_state == ROBOT_FAULT ? WIFI_CONTROL_STM_FAULT : WIFI_CONTROL_STM_DISARMED,
        .t_ms = now, .last_seq = s_last_seq, .command_age_ms = now - s_last_accepted_cmd_ms,
        .vx_mmps = s_vx_mmps, .w_mradps = s_w_mradps,
        .left_pwm = host_output.left_signed_permille, .right_pwm = host_output.right_signed_permille};
    wifi_control_executor_tel(&late_e, &t, now);
}

static wifi_control_submit_status_t submit(wifi_control_type_t type, uint32_t now)
{
    wifi_control_ticket_t ticket = {0};
    uint32_t id = type == WIFI_CONTROL_ARM ? 0U : late_e.state.owner.control_id;
    assert(wifi_control_ticket_issue(&late_pool, &ticket, 7U, type, id, now) == WIFI_TICKET_OK);
    wifi_control_request_t r = {.type = type, .expected_boot_id = 42U,
        .request_id = ticket.id, .ws_session_id = 7U, .control_id = id, .ticket = ticket.id};
    return wifi_control_executor_submit(&late_e, &r, &ticket, true, true, now);
}

static void relay_tx(uint32_t seq, uint32_t now)
{
    tick(now); clear_tx();
    assert(wifi_control_executor_take_tx(&late_e, seq, now, &late_tx));
    assert(wifi_control_executor_tx_complete(&late_e, (int)late_tx.length, now));
    feed(late_tx.bytes);
}

static bool relay_ack(uint32_t expected_seq, wifi_control_op_t op, uint32_t now)
{
    const char *ack = strstr(host_tx, "ACK,");
    unsigned long seq, processed;
    char type[16];
    assert(ack && sscanf(ack, "ACK,seq=%lu,type=%15[^,],t_ms=%lu", &seq, type, &processed) == 3);
    assert(seq == expected_seq);
    assert(strcmp(type, op == WIFI_CONTROL_OP_ARM ? "ARM" : op == WIFI_CONTROL_OP_CMD ? "CMD" : "DISARM") == 0);
    bool accepted = wifi_control_executor_reply(&late_e, op, (uint32_t)seq, true, (uint32_t)processed, now);
    wifi_control_executor_result_t result;
    while (wifi_control_executor_take_result(&late_e, &result)) { }
    return accepted;
}

static void esp_blocked_late_ack_manual_recovery(void)
{
    reset_host(); wifi_control_executor_init(&late_e, 42U);
    wifi_control_ticket_pool_init(&late_pool, 42U); relay_tel(1000);
    assert(submit(WIFI_CONTROL_ARM, 1000) == WIFI_EXEC_ACCEPTED);
    relay_tx(11, 1010); assert(relay_ack(11, WIFI_CONTROL_OP_ARM, 1010));
    assert(submit(WIFI_CONTROL_CMD, 1015) == WIFI_EXEC_ACCEPTED);
    relay_tx(12, 1020); assert(relay_ack(12, WIFI_CONTROL_OP_CMD, 1020));
    relay_tel(1021); assert(late_e.state.phase == WIFI_CONTROL_ACTIVE);
    wifi_control_executor_stop(&late_e, WIFI_CONTROL_REASON_MANUAL_STOP, 1050);
    wifi_control_executor_inputs_cleared(&late_e); relay_tx(13, 1050); stopped(13);
    assert(!strstr(host_tx, "ACK,"));
    relay_tel(1150); assert(late_e.state.phase == WIFI_CONTROL_STOPPING);
    wifi_control_executor_poll(&late_e, true, 1199); assert(late_e.state.phase == WIFI_CONTROL_STOPPING);
    wifi_control_executor_poll(&late_e, true, 1200); assert(late_e.state.phase == WIFI_CONTROL_BLOCKED);
    relay_tel(1250); relay_tel(1350); relay_tel(1450);
    assert(late_e.state.phase == WIFI_CONTROL_BLOCKED);
    clear_tx(); tick(1550);
    assert(!relay_ack(13, WIFI_CONTROL_OP_DISARM, 1550));
    relay_tel(1551); assert(late_e.state.phase == WIFI_CONTROL_BLOCKED);
    assert(submit(WIFI_CONTROL_ARM, 1552) == WIFI_EXEC_NOT_READY);
    wifi_control_executor_inputs_cleared(&late_e);
    assert(!wifi_control_executor_take_tx(&late_e, 14, 1553, &late_tx));
    wifi_control_executor_stop(&late_e, WIFI_CONTROL_REASON_MANUAL_STOP, 1600);
    wifi_control_executor_inputs_cleared(&late_e); relay_tx(14, 1600); stopped(14);
    assert(relay_ack(14, WIFI_CONTROL_OP_DISARM, 1600));
    assert(late_e.state.phase == WIFI_CONTROL_STOPPING);
    relay_tel(1601); assert(late_e.state.phase == WIFI_CONTROL_IDLE);
}
#else
static void mode_zero_immediate(void)
{
    reset_host(); arm_zero(); feed("DISARM,seq=3\n"); stopped(3);
    assert(strstr(host_tx, "ACK,seq=3,type=DISARM,t_ms=0\n"));
    assert(!strstr(host_tx, "TEST_ACK_DELAY"));
    clear_tx(); tick(500); assert(!strstr(host_tx, "ACK,"));
}
#endif

int main(void)
{
    RUN(startup_immediate);
    RUN(timeout_and_cancel);
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    RUN(delayed_once);
    RUN(eligibility);
    RUN(safety_during_wait);
    RUN(newer_command_not_overwritten);
    RUN(reset_discards_and_tick_wrap);
    RUN(esp_blocked_late_ack_manual_recovery);
#else
    RUN(mode_zero_immediate);
#endif
    printf("PASS mode=%u: %u native case groups; no board evidence\n",
        UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED, tests);
    return 0;
}
