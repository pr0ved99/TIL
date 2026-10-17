/* Reuse baseline setup helpers; all code here runs on a native PC only. */
#define main baseline_fixture_main
#include "wifi_control_executor_host_fixture.c"
#undef main

static void motion(uint64_t now)
{
    issue(WIFI_CONTROL_CMD, now);
    r.vx_mmps = 50;
    r.w_mradps = -250;
}

static void motion_sent(void)
{
    active();
    motion(140U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) == WIFI_EXEC_ACCEPTED);
    CHECK(wifi_control_executor_take_tx(&e, 13U, 141U, &tx));
    CHECK(strcmp(tx.bytes, "CMD,seq=13,vx_mmps=50,w_mradps=-250,timeout_ms=300\n") == 0);
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 142U));
}

static void motion_ack(void)
{
    motion_sent();
    CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_CMD, 13U, true, 1045U, 145U));
    CHECK(wifi_control_executor_take_result(&e, &answer));
}

static wifi_control_tel_t moving_tel(uint64_t now)
{
    return (wifi_control_tel_t){
        .state = WIFI_CONTROL_STM_ARMED, .t_ms = (uint32_t)(900U + now),
        .last_seq = 13U, .command_age_ms = 10U,
        .vx_mmps = 50, .w_mradps = -250, .left_pwm = 100, .right_pwm = 0
    };
}

static void policy(void)
{
    wifi_control_request_t v = {.type = WIFI_CONTROL_CMD};
    CHECK(wifi_control_request_allows(&v));
    CHECK(!wifi_control_request_allows(NULL));
    const int32_t vx[] = {-100, 100, -101, 101, INT32_MIN, INT32_MAX};
    for (unsigned i = 0; i < sizeof(vx) / sizeof(vx[0]); ++i) {
        v.vx_mmps = vx[i];
        CHECK(wifi_control_request_allows(&v) == (WIFI_CONTROL_ZERO_ONLY == 0U && i < 2U));
    }
    v.vx_mmps = 0;
    const int32_t w[] = {-500, 500, -501, 501, INT32_MIN, INT32_MAX};
    for (unsigned i = 0; i < sizeof(w) / sizeof(w[0]); ++i) {
        v.w_mradps = w[i];
        CHECK(wifi_control_request_allows(&v) == (WIFI_CONTROL_ZERO_ONLY == 0U && i < 2U));
    }
    v = (wifi_control_request_t){.type = WIFI_CONTROL_ARM};
    CHECK(wifi_control_request_allows(&v));
    v.vx_mmps = 1;
    CHECK(!wifi_control_request_allows(&v));
    v.type = (wifi_control_type_t)99;
    CHECK(!wifi_control_request_allows(&v));
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    const char *name = argv[1];
    if (strcmp(name, "policy") == 0) {
        policy();
    } else if (strcmp(name, "first_motion_admission") == 0) {
        arm_ack(true);
        motion(140U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) != WIFI_EXEC_ACCEPTED);
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING && !e.queued);
    } else if (strcmp(name, "first_motion_at_tx") == 0) {
        arm_ack(true);
        motion(140U);
        r.accepted_ms = 140U;
        r.expires_ms = 290U;
        CHECK(!wifi_control_state_cmd_sent(&e.state, &r, 13U, 140U));
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
    } else if (strcmp(name, "round_trip") == 0) {
        motion_ack();
        wifi_control_tel_t t = moving_tel(150U);
        wifi_control_executor_tel(&e, &t, 150U);
        CHECK(e.state.phase == WIFI_CONTROL_ACTIVE);
        issue(WIFI_CONTROL_CMD, 160U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 160U) == WIFI_EXEC_ACCEPTED);
        CHECK(wifi_control_executor_take_tx(&e, 14U, 161U, &tx));
        CHECK(strcmp(tx.bytes, "CMD,seq=14,vx_mmps=0,w_mradps=0,timeout_ms=300\n") == 0);
        CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 162U));
        CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_CMD, 14U, true, 1065U, 165U));
        CHECK(wifi_control_executor_take_result(&e, &answer));
        tel(170U, WIFI_CONTROL_STM_ARMED, 14U);
        CHECK(e.state.phase == WIFI_CONTROL_ACTIVE);
    } else if (strcmp(name, "queue_expired_motion") == 0) {
        active(); motion(140U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) == WIFI_EXEC_ACCEPTED);
        CHECK(!wifi_control_executor_take_tx(&e, 13U, 190U, &tx));
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING && !e.queued);
    } else if (strcmp(name, "old_owner") == 0) {
        active(); motion(140U); r.ws_session_id = 8U;
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) != WIFI_EXEC_ACCEPTED);
        CHECK(e.state.phase == WIFI_CONTROL_ACTIVE && e.state.owner.ws_session_id == 7U);
    } else if (strcmp(name, "ack_timeout") == 0) {
        motion_sent();
        wifi_control_executor_poll(&e, true, 291U);
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
        CHECK(!wifi_control_executor_reply(&e, WIFI_CONTROL_OP_CMD, 13U, true, 1192U, 292U));
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
    } else if (strcmp(name, "source_timeout") == 0) {
        motion_ack();
        tel(200U, WIFI_CONTROL_STM_ARMED, 13U);
        tel(300U, WIFI_CONTROL_STM_ARMED, 13U);
        wifi_control_executor_poll(&e, true, 341U);
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING && e.state.reason == WIFI_CONTROL_REASON_SOURCE_TIMEOUT);
    } else if (strcmp(name, "owner_close") == 0) {
        active(); motion(140U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) == WIFI_EXEC_ACCEPTED);
        wifi_control_executor_owner_closed(&e, 7U, 141U);
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING && !e.queued);
        CHECK(!wifi_control_executor_take_tx(&e, 13U, 142U, &tx));
        wifi_control_executor_inputs_cleared(&e);
        CHECK(wifi_control_executor_take_tx(&e, 14U, 143U, &tx));
        CHECK(strcmp(tx.bytes, "\x18\nDISARM,seq=14\n") == 0);
    } else if (strcmp(name, "partial_motion_tx") == 0) {
        active(); motion(140U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) == WIFI_EXEC_ACCEPTED);
        CHECK(wifi_control_executor_take_tx(&e, 13U, 141U, &tx));
        CHECK(!wifi_control_executor_tx_complete(&e, (int)tx.length - 1, 142U));
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
        wifi_control_executor_inputs_cleared(&e);
        CHECK(wifi_control_executor_take_tx(&e, 14U, 143U, &tx));
        CHECK(strcmp(tx.bytes, "\x18\nDISARM,seq=14\n") == 0);
    } else if (strcmp(name, "bad_motion_tel") == 0 || strcmp(name, "zero_command_pwm") == 0) {
        motion_ack();
        wifi_control_tel_t t = moving_tel(150U);
        if (strcmp(name, "zero_command_pwm") == 0) { t.vx_mmps = 0; t.w_mradps = 0; }
        else { t.left_pwm = 101; }
        wifi_control_executor_tel(&e, &t, 150U);
        CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
    } else if (strcmp(name, "motion_cannot_confirm_stop") == 0) {
        motion_ack();
        wifi_control_executor_stop(&e, WIFI_CONTROL_REASON_MANUAL_STOP, 150U);
        wifi_control_executor_inputs_cleared(&e);
        CHECK(wifi_control_executor_take_tx(&e, 14U, 151U, &tx));
        CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 152U));
        CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_DISARM, 14U, true, 1055U, 155U));
        wifi_control_tel_t t = moving_tel(160U); t.last_seq = 14U;
        wifi_control_executor_tel(&e, &t, 160U);
        CHECK(e.state.phase == WIFI_CONTROL_BLOCKED);
    } else {
        fprintf(stderr, "unknown case: %s\n", name); return 2;
    }
    printf("PASS %s\n", name);
    return 0;
}
