#include "wifi_control_state.h"
#include <stdio.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { \
    fprintf(stderr, "line %d: %s\n", __LINE__, #x); return 1; \
} } while (0)

static wifi_control_request_t request(wifi_control_type_t type, uint64_t now)
{
    return (wifi_control_request_t) {
        .type = type, .expected_boot_id = 7U, .request_id = 1U,
        .ws_session_id = 11U, .ticket = 9U,
        .accepted_ms = now, .expires_ms = now + 150U
    };
}

static wifi_control_tel_t telemetry(wifi_control_stm_state_t state, uint64_t now)
{
    return (wifi_control_tel_t) {
        .state = state, .t_ms = (uint32_t)(1000U + now),
        .command_age_ms = state == WIFI_CONTROL_STM_ARMED ? 10U : UINT32_MAX
    };
}

static void baseline(wifi_control_state_t *s)
{
    wifi_control_state_init(s, 7U);
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_DISARMED, 100U);
    wifi_control_state_tel(s, &tel, 100U);
}

static int arm_pending(wifi_control_state_t *s)
{
    baseline(s);
    wifi_control_request_t r = request(WIFI_CONTROL_ARM, 100U);
    uint32_t id = 0U;
    CHECK(wifi_control_state_begin_arm(s, &r, true, true, 100U, &id));
    CHECK(id == 1U && s->phase == WIFI_CONTROL_ARM_PENDING);
    CHECK(wifi_control_state_arm_sent(s, 11U, id, 10U, 110U));
    return 0;
}

static int zero_pending(wifi_control_state_t *s)
{
    CHECK(arm_pending(s) == 0);
    CHECK(wifi_control_state_reply(s, WIFI_CONTROL_OP_ARM, 10U, true, 1120U, 120U));
    CHECK(s->phase == WIFI_CONTROL_ZERO_PENDING);
    return 0;
}

static int active(wifi_control_state_t *s)
{
    CHECK(zero_pending(s) == 0);
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 130U);
    r.control_id = 1U;
    CHECK(wifi_control_state_cmd_sent(s, &r, 20U, 130U));
    CHECK(wifi_control_state_reply(s, WIFI_CONTROL_OP_CMD, 20U, true, 1140U, 140U));
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_ARMED, 150U);
    tel.last_seq = 20U;
    wifi_control_state_tel(s, &tel, 150U);
    CHECK(s->phase == WIFI_CONTROL_ACTIVE);
    return 0;
}

static int initial_arguments(void)
{
    wifi_control_state_t s = {0};
    wifi_control_request_t r = request(WIFI_CONTROL_ARM, 100U);
    uint32_t out = 77U;
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 100U, &out));
    CHECK(!wifi_control_state_begin_arm(NULL, &r, true, true, 100U, &out));
    wifi_control_state_init(NULL, 7U);
    baseline(&s);
    CHECK(!wifi_control_state_begin_arm(&s, NULL, true, true, 100U, &out));
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 100U, NULL));
    CHECK(out == 77U && s.phase == WIFI_CONTROL_IDLE);
    CHECK(!wifi_control_state_arm_sent(NULL, 11U, 1U, 1U, 100U));
    CHECK(!wifi_control_state_cmd_sent(NULL, &r, 1U, 100U));
    CHECK(!wifi_control_state_disarm_sent(NULL, 1U, 100U));
    CHECK(!wifi_control_state_reply(NULL, WIFI_CONTROL_OP_ARM, 1U, true, 0U, 100U));
    wifi_control_state_tel(NULL, NULL, 100U);
    wifi_control_state_poll(NULL, true, 100U);
    wifi_control_state_stop(NULL, WIFI_CONTROL_REASON_MANUAL_STOP, 100U);
    wifi_control_state_tx_failed(NULL, 100U);
    CHECK(wifi_control_state_actions(NULL) == 0U);
    return 0;
}

static int arm_gates(void)
{
    wifi_control_state_t s;
    wifi_control_request_t r = request(WIFI_CONTROL_ARM, 100U);
    uint32_t out = 77U;
    wifi_control_state_init(&s, 7U);
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 100U, &out));
    baseline(&s);
    CHECK(!wifi_control_state_begin_arm(&s, &r, false, true, 100U, &out));
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, false, 100U, &out));
    s.tel.state = WIFI_CONTROL_STM_FAULT;
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 100U, &out));
    s.tel.state = WIFI_CONTROL_STM_ARMED;
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 100U, &out));
    s.tel.state = WIFI_CONTROL_STM_DISARMED;
    s.tel.left_pwm = 1;
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 100U, &out));
    s.tel.left_pwm = 0;
    r.expected_boot_id = 8U;
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 100U, &out));
    CHECK(out == 77U && s.owner.next_control_id == 1U);
    return 0;
}

static int arm_queue_boundary(void)
{
    wifi_control_state_t s;
    baseline(&s);
    wifi_control_request_t r = request(WIFI_CONTROL_ARM, 100U);
    uint32_t id;
    CHECK(wifi_control_state_begin_arm(&s, &r, true, true, 100U, &id));
    CHECK(wifi_control_state_arm_sent(&s, 11U, id, 10U, 149U));
    baseline(&s);
    CHECK(wifi_control_state_begin_arm(&s, &r, true, true, 100U, &id));
    CHECK(!wifi_control_state_arm_sent(&s, 11U, id, 10U, 150U));
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_INPUT_EXPIRED);
    baseline(&s);
    r.expires_ms = 125U;
    CHECK(wifi_control_state_begin_arm(&s, &r, true, true, 100U, &id));
    CHECK(!wifi_control_state_arm_sent(&s, 11U, id, 10U, 125U));
    return 0;
}

static int ack_boundary(void)
{
    wifi_control_state_t s;
    CHECK(arm_pending(&s) == 0);
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 10U, true, 1259U, 259U));
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING);
    CHECK(arm_pending(&s) == 0);
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 10U, true, 1260U, 260U));
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.owner.control_id == 0U);
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 10U, true, 1270U, 270U));
    return 0;
}

static int reply_identity(void)
{
    wifi_control_state_t s;
    CHECK(arm_pending(&s) == 0);
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 9U, true, 1120U, 120U));
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_CMD, 10U, true, 1120U, 120U));
    CHECK(s.phase == WIFI_CONTROL_ARM_PENDING && s.pending == WIFI_CONTROL_OP_ARM);
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 10U, true, 1130U, 130U));
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 10U, true, 1130U, 130U));
    return 0;
}

static int cmd_before_arm_ack(void)
{
    wifi_control_state_t s;
    CHECK(arm_pending(&s) == 0);
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 120U);
    r.control_id = 1U;
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 20U, 120U));
    CHECK(s.pending_seq == 10U && !s.have_cmd);
    return 0;
}

static int zero_ack_tel_order(void)
{
    wifi_control_state_t s;
    CHECK(zero_pending(&s) == 0);
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 130U); r.control_id = 1U;
    CHECK(wifi_control_state_cmd_sent(&s, &r, 20U, 130U));
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_ARMED, 135U); tel.last_seq = 20U;
    wifi_control_state_tel(&s, &tel, 135U);
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING);
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_CMD, 20U, true, 1140U, 140U));
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING);
    wifi_control_state_tel(&s, &tel, 145U); /* buffered pre-ACK STM sample */
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING);
    tel = telemetry(WIFI_CONTROL_STM_ARMED, 150U); tel.last_seq = 19U;
    wifi_control_state_tel(&s, &tel, 150U);
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING);
    tel = telemetry(WIFI_CONTROL_STM_ARMED, 160U); tel.last_seq = 20U;
    wifi_control_state_tel(&s, &tel, 160U);
    CHECK(s.phase == WIFI_CONTROL_ACTIVE && s.owner.control_id == 1U);
    return 0;
}

static int zero_telemetry_guards(void)
{
    wifi_control_state_t s;
    CHECK(zero_pending(&s) == 0);
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_DISARMED, 125U);
    wifi_control_state_tel(&s, &tel, 125U);
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING); /* pre-ARM telemetry tolerated */
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 130U); r.control_id = 1U;
    CHECK(wifi_control_state_cmd_sent(&s, &r, 20U, 130U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_CMD, 20U, true, 1140U, 140U));
    tel = telemetry(WIFI_CONTROL_STM_ARMED, 150U); tel.last_seq = 20U; tel.command_age_ms = 300U;
    wifi_control_state_tel(&s, &tel, 150U);
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING);
    tel = telemetry(WIFI_CONTROL_STM_ARMED, 160U); tel.last_seq = 20U; tel.right_pwm = 1;
    wifi_control_state_tel(&s, &tel, 160U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING);
    return 0;
}

static int first_cmd_boundary(void)
{
    wifi_control_state_t s;
    CHECK(zero_pending(&s) == 0);
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_ARMED, 330U);
    wifi_control_state_tel(&s, &tel, 330U);
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 359U); r.control_id = 1U;
    CHECK(wifi_control_state_cmd_sent(&s, &r, 20U, 359U));
    CHECK(zero_pending(&s) == 0);
    wifi_control_state_tel(&s, &tel, 330U);
    r = request(WIFI_CONTROL_CMD, 360U); r.control_id = 1U;
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 20U, 360U));
    CHECK(s.reason == WIFI_CONTROL_REASON_FIRST_CMD_TIMEOUT);
    return 0;
}

static int source_deadline_not_telemetry(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_ARMED, 300U); tel.last_seq = 20U;
    wifi_control_state_tel(&s, &tel, 300U);
    wifi_control_state_poll(&s, true, 329U);
    CHECK(s.phase == WIFI_CONTROL_ACTIVE && s.last_cmd_sent_ms == 130U);
    wifi_control_state_poll(&s, true, 330U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_SOURCE_TIMEOUT);
    return 0;
}

static int tel_boundary(void)
{
    wifi_control_state_t s; CHECK(zero_pending(&s) == 0);
    wifi_control_state_poll(&s, true, 349U);
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING);
    wifi_control_state_poll(&s, true, 350U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_TEL_STALE);
    return 0;
}

static int cmd_binding(void)
{
    wifi_control_state_t s; CHECK(zero_pending(&s) == 0);
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 130U); r.control_id = 1U;
    r.ws_session_id = 12U;
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 20U, 130U));
    r.ws_session_id = 11U; r.expected_boot_id = 8U;
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 20U, 130U));
    r.expected_boot_id = 7U; r.control_id = 2U;
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 20U, 130U));
    CHECK(s.phase == WIFI_CONTROL_ZERO_PENDING && !s.have_cmd && s.owner.control_id == 1U);
    return 0;
}

static int cmd_queue_boundary(void)
{
    wifi_control_state_t s; CHECK(zero_pending(&s) == 0);
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 130U); r.control_id = 1U;
    CHECK(wifi_control_state_cmd_sent(&s, &r, 20U, 179U));
    CHECK(zero_pending(&s) == 0);
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 20U, 180U));
    CHECK(s.reason == WIFI_CONTROL_REASON_INPUT_EXPIRED);
    CHECK(zero_pending(&s) == 0);
    r.expires_ms = 140U;
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 20U, 140U));
    CHECK(s.phase == WIFI_CONTROL_STOPPING);
    return 0;
}

static int zero_only_and_single_pending(void)
{
    wifi_control_state_t s; CHECK(zero_pending(&s) == 0);
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 130U); r.control_id = 1U;
    CHECK(wifi_control_state_cmd_sent(&s, &r, 20U, 130U));
    r = request(WIFI_CONTROL_CMD, 140U); r.control_id = 1U;
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 21U, 140U));
    CHECK(s.pending_seq == 20U && s.last_cmd_sent_ms == 130U);
    CHECK(zero_pending(&s) == 0);
    r.vx_mmps = 1;
    CHECK(!wifi_control_state_cmd_sent(&s, &r, 20U, 140U));
    CHECK(s.reason == WIFI_CONTROL_REASON_BAD_INPUT && s.owner.control_id == 0U);
    return 0;
}

static int owner_close_and_late_ack(void)
{
    wifi_control_state_t s; CHECK(arm_pending(&s) == 0);
    wifi_control_state_owner_closed(&s, 12U, 120U);
    CHECK(s.phase == WIFI_CONTROL_ARM_PENDING);
    wifi_control_state_owner_closed(&s, 11U, 120U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.owner.control_id == 0U);
    CHECK(wifi_control_state_actions(&s) == 3U);
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 10U, true, 1125U, 125U));
    CHECK(wifi_control_state_disarm_sent(&s, 10U, 130U)); /* same seq, wrong type still rejected */
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 10U, true, 1135U, 135U));
    CHECK(wifi_control_state_actions(&s) == 1U);
    return 0;
}

static int stop_order_and_rearm(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 170U));
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_DISARMED, 175U); tel.last_seq = 30U;
    wifi_control_state_tel(&s, &tel, 175U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING);
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_DISARM, 30U, true, 1180U, 180U));
    CHECK(s.phase == WIFI_CONTROL_STOPPING);
    wifi_control_state_tel(&s, &tel, 185U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING);
    tel = telemetry(WIFI_CONTROL_STM_DISARMED, 190U); tel.last_seq = 30U;
    wifi_control_state_tel(&s, &tel, 190U);
    CHECK(s.phase == WIFI_CONTROL_IDLE && s.owner.next_control_id == 2U);
    wifi_control_request_t r = request(WIFI_CONTROL_ARM, 200U); uint32_t id;
    CHECK(wifi_control_state_begin_arm(&s, &r, true, true, 200U, &id));
    CHECK(id == 2U);
    CHECK(!wifi_control_state_arm_sent(&s, 11U, 1U, 40U, 201U));
    return 0;
}

static int fault_can_confirm_stop(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 170U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_DISARM, 30U, true, 1180U, 180U));
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_FAULT, 190U); tel.last_seq = 30U;
    wifi_control_state_tel(&s, &tel, 190U);
    CHECK(s.phase == WIFI_CONTROL_IDLE);
    wifi_control_request_t r = request(WIFI_CONTROL_ARM, 200U); uint32_t out = 77U;
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 200U, &out));
    CHECK(out == 77U);
    return 0;
}

static int stop_send_boundary(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_OWNER_CLOSED, 200U);
    CHECK(s.stop_started_ms == 160U);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 309U));
    CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    CHECK(!wifi_control_state_disarm_sent(&s, 30U, 310U));
    CHECK(s.phase == WIFI_CONTROL_BLOCKED && wifi_control_state_actions(&s) == 1U);
    return 0;
}

static int stop_ack_boundary(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 170U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_DISARM, 30U, true, 1319U, 319U));
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.stop_ack);
    CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 170U));
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_DISARM, 30U, true, 1320U, 320U));
    CHECK(s.phase == WIFI_CONTROL_BLOCKED);
    return 0;
}

static int stop_confirm_boundary(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 170U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_DISARM, 30U, true, 1180U, 180U));
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_DISARMED, 479U); tel.last_seq = 30U;
    wifi_control_state_tel(&s, &tel, 479U);
    CHECK(s.phase == WIFI_CONTROL_IDLE);
    CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 170U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_DISARM, 30U, true, 1180U, 180U));
    tel = telemetry(WIFI_CONTROL_STM_DISARMED, 480U); tel.last_seq = 30U;
    wifi_control_state_tel(&s, &tel, 480U);
    CHECK(s.phase == WIFI_CONTROL_BLOCKED);
    return 0;
}

static int blocked_manual_recovery(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    wifi_control_state_poll(&s, true, 310U);
    CHECK(s.phase == WIFI_CONTROL_BLOCKED);
    wifi_control_request_t r = request(WIFI_CONTROL_ARM, 320U); uint32_t out = 77U;
    CHECK(!wifi_control_state_begin_arm(&s, &r, true, true, 320U, &out));
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_OWNER_CLOSED, 330U);
    CHECK(s.phase == WIFI_CONTROL_BLOCKED);
    wifi_control_state_stop(&s, WIFI_CONTROL_REASON_MANUAL_STOP, 340U);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 350U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_DISARM, 30U, true, 1360U, 360U));
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_DISARMED, 370U); tel.last_seq = 30U;
    wifi_control_state_tel(&s, &tel, 370U);
    CHECK(s.phase == WIFI_CONTROL_IDLE && s.owner.next_control_id == 2U);
    return 0;
}

static int active_fault_state_age(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_FAULT, 160U);
    wifi_control_state_tel(&s, &tel, 160U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_STM_FAULT);
    CHECK(active(&s) == 0);
    tel = telemetry(WIFI_CONTROL_STM_DISARMED, 160U);
    wifi_control_state_tel(&s, &tel, 160U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING);
    CHECK(active(&s) == 0);
    tel = telemetry(WIFI_CONTROL_STM_ARMED, 160U); tel.command_age_ms = 300U;
    wifi_control_state_tel(&s, &tel, 160U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING);
    CHECK(active(&s) == 0);
    tel = telemetry(WIFI_CONTROL_STM_ARMED, 160U); tel.vx_mmps = 1;
    wifi_control_state_tel(&s, &tel, 160U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING);
    return 0;
}

static int stm_wrap_and_reset(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    s.tel.t_ms = UINT32_MAX - 20U;
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_ARMED, 180U); tel.t_ms = 9U;
    wifi_control_state_tel(&s, &tel, 180U);
    CHECK(s.phase == WIFI_CONTROL_ACTIVE);
    tel = telemetry(WIFI_CONTROL_STM_ARMED, 190U); tel.t_ms = 1U;
    wifi_control_state_tel(&s, &tel, 190U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_STM_CLOCK);
    return 0;
}

static int frozen_stm_clock(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    const uint32_t frozen = s.tel.t_ms;
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_ARMED, 200U); tel.t_ms = frozen;
    wifi_control_state_tel(&s, &tel, 200U);
    wifi_control_request_t r = request(WIFI_CONTROL_CMD, 230U); r.control_id = 1U;
    CHECK(wifi_control_state_cmd_sent(&s, &r, 21U, 230U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_CMD, 21U, true, frozen, 240U));
    wifi_control_state_tel(&s, &tel, 300U);
    r = request(WIFI_CONTROL_CMD, 330U); r.control_id = 1U;
    CHECK(wifi_control_state_cmd_sent(&s, &r, 22U, 330U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_CMD, 22U, true, frozen, 340U));
    wifi_control_state_tel(&s, &tel, 400U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_STM_CLOCK);
    return 0;
}

static int clock_backward_and_startup(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_state_poll(&s, true, 149U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_CLOCK_BACKWARD);
    CHECK(active(&s) == 0);
    wifi_control_state_poll(&s, false, 160U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_STARTUP);
    return 0;
}

static int err_and_tx_failure(void)
{
    wifi_control_state_t s; CHECK(arm_pending(&s) == 0);
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_ARM, 10U, false, 1120U, 120U));
    CHECK(s.phase == WIFI_CONTROL_STOPPING && s.reason == WIFI_CONTROL_REASON_STM_ERR);
    CHECK(wifi_control_state_disarm_sent(&s, 30U, 130U));
    CHECK(wifi_control_state_reply(&s, WIFI_CONTROL_OP_DISARM, 30U, false, 1140U, 140U));
    CHECK(s.phase == WIFI_CONTROL_BLOCKED);
    CHECK(active(&s) == 0);
    wifi_control_state_tx_failed(&s, 160U);
    CHECK(s.phase == WIFI_CONTROL_STOPPING && wifi_control_state_actions(&s) == 3U);
    wifi_control_state_tx_failed(&s, 170U);
    CHECK(s.phase == WIFI_CONTROL_BLOCKED && wifi_control_state_actions(&s) == 1U);
    return 0;
}

static int no_automatic_resume(void)
{
    wifi_control_state_t s; CHECK(active(&s) == 0);
    wifi_control_state_owner_closed(&s, 11U, 160U);
    wifi_control_state_poll(&s, true, 310U);
    CHECK(s.phase == WIFI_CONTROL_BLOCKED);
    wifi_control_tel_t tel = telemetry(WIFI_CONTROL_STM_DISARMED, 320U); tel.last_seq = 20U;
    wifi_control_state_tel(&s, &tel, 320U);
    CHECK(s.phase == WIFI_CONTROL_BLOCKED && s.owner.control_id == 0U);
    CHECK(!wifi_control_state_reply(&s, WIFI_CONTROL_OP_CMD, 20U, true, 1330U, 330U));
    CHECK(s.phase == WIFI_CONTROL_BLOCKED);
    return 0;
}

struct test_case { const char *name; int (*run)(void); };
static const struct test_case cases[] = {
    {"initial_arguments", initial_arguments}, {"arm_gates", arm_gates},
    {"arm_queue_boundary", arm_queue_boundary}, {"ack_boundary", ack_boundary},
    {"reply_identity", reply_identity}, {"cmd_before_arm_ack", cmd_before_arm_ack},
    {"zero_ack_tel_order", zero_ack_tel_order}, {"zero_telemetry_guards", zero_telemetry_guards},
    {"first_cmd_boundary", first_cmd_boundary}, {"source_deadline_not_telemetry", source_deadline_not_telemetry},
    {"tel_boundary", tel_boundary}, {"cmd_binding", cmd_binding},
    {"cmd_queue_boundary", cmd_queue_boundary}, {"zero_only_and_single_pending", zero_only_and_single_pending},
    {"owner_close_and_late_ack", owner_close_and_late_ack}, {"stop_order_and_rearm", stop_order_and_rearm},
    {"fault_can_confirm_stop", fault_can_confirm_stop}, {"stop_send_boundary", stop_send_boundary},
    {"stop_ack_boundary", stop_ack_boundary}, {"stop_confirm_boundary", stop_confirm_boundary},
    {"blocked_manual_recovery", blocked_manual_recovery}, {"active_fault_state_age", active_fault_state_age},
    {"stm_wrap_and_reset", stm_wrap_and_reset}, {"frozen_stm_clock", frozen_stm_clock},
    {"clock_backward_and_startup", clock_backward_and_startup}, {"err_and_tx_failure", err_and_tx_failure},
    {"no_automatic_resume", no_automatic_resume}
};

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    for (size_t i = 0U; i < sizeof(cases) / sizeof(cases[0]); ++i) {
        if (strcmp(argv[1], cases[i].name) == 0) {
            const int result = cases[i].run();
            if (result == 0) printf("PASS %s\n", cases[i].name);
            return result;
        }
    }
    return 2;
}
