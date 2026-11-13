#include "wifi_control_state.h"

static bool live(const wifi_control_state_t *s)
{
    return s != NULL && s->initialized;
}

static bool controlling(const wifi_control_state_t *s)
{
    return s->phase == WIFI_CONTROL_ARM_PENDING ||
        s->phase == WIFI_CONTROL_ZERO_PENDING ||
        s->phase == WIFI_CONTROL_ACTIVE;
}

static bool within(uint64_t now, uint64_t then, uint32_t budget)
{
    return now >= then && now - then < budget;
}

static bool zero(const wifi_control_tel_t *tel)
{
    return tel->vx_mmps == 0 && tel->w_mradps == 0 &&
        tel->left_pwm == 0 && tel->right_pwm == 0;
}

static bool fresh(const wifi_control_state_t *s, uint64_t now)
{
    return s->have_tel && within(now, s->tel_received_ms, WIFI_CONTROL_TEL_MS);
}

static bool request_live(const wifi_control_request_t *r, uint64_t now)
{
    return r->expires_ms > r->accepted_ms &&
        r->expires_ms - r->accepted_ms <= 150U &&
        now < r->expires_ms && within(now, r->accepted_ms, WIFI_CONTROL_QUEUE_MS);
}

static void blocked(wifi_control_state_t *s, wifi_control_reason_t reason)
{
    wifi_control_owner_revoke(&s->owner);
    s->phase = WIFI_CONTROL_BLOCKED;
    s->reason = reason;
    s->pending = WIFI_CONTROL_OP_NONE;
    s->need_disarm = false;
    s->zero_ack = false;
    s->stop_ack = false;
}

static void stop_now(
    wifi_control_state_t *s, wifi_control_reason_t reason, uint64_t now)
{
    if (s->phase == WIFI_CONTROL_STOPPING ||
        (s->phase == WIFI_CONTROL_BLOCKED &&
         reason != WIFI_CONTROL_REASON_MANUAL_STOP)) {
        return;
    }
    wifi_control_owner_revoke(&s->owner);
    s->phase = WIFI_CONTROL_STOPPING;
    s->reason = reason;
    s->pending = WIFI_CONTROL_OP_NONE;
    s->need_disarm = true;
    s->stop_started_ms = now;
    s->zero_ack = false;
    s->stop_ack = false;
    s->arm_sent = false;
    s->have_cmd = false;
}

static bool clock_accept(wifi_control_state_t *s, uint64_t now)
{
    if (now < s->last_now_ms) {
        if (controlling(s)) {
            stop_now(s, WIFI_CONTROL_REASON_CLOCK_BACKWARD, s->last_now_ms);
        } else if (s->phase == WIFI_CONTROL_STOPPING) {
            blocked(s, WIFI_CONTROL_REASON_CLOCK_BACKWARD);
        }
        return false;
    }
    s->last_now_ms = now;
    return true;
}

static void deadlines(wifi_control_state_t *s, uint64_t now)
{
    if (s->phase == WIFI_CONTROL_STOPPING) {
        if ((s->need_disarm &&
             !within(now, s->stop_started_ms, WIFI_CONTROL_STOP_SEND_MS)) ||
            (s->pending == WIFI_CONTROL_OP_DISARM &&
             !within(now, s->pending_sent_ms, WIFI_CONTROL_ACK_MS)) ||
            (s->stop_ack &&
             !within(now, s->stop_ack_ms, WIFI_CONTROL_STOP_CONFIRM_MS))) {
            blocked(s, WIFI_CONTROL_REASON_STOP_UNCONFIRMED);
        }
        return;
    }
    if (!controlling(s)) {
        return;
    }
    wifi_control_reason_t reason = WIFI_CONTROL_REASON_NONE;
    if (!s->startup_ready) {
        reason = WIFI_CONTROL_REASON_STARTUP;
    } else if (!fresh(s, now)) {
        reason = WIFI_CONTROL_REASON_TEL_STALE;
    } else if (s->phase == WIFI_CONTROL_ARM_PENDING && !s->arm_sent &&
        (now >= s->arm_expires_ms ||
         !within(now, s->arm_accepted_ms, WIFI_CONTROL_QUEUE_MS))) {
        reason = WIFI_CONTROL_REASON_INPUT_EXPIRED;
    } else if (s->pending != WIFI_CONTROL_OP_NONE &&
        !within(now, s->pending_sent_ms, WIFI_CONTROL_ACK_MS)) {
        reason = WIFI_CONTROL_REASON_ACK_TIMEOUT;
    } else if (s->arm_sent && !s->have_cmd &&
        !within(now, s->arm_sent_ms, WIFI_CONTROL_FIRST_CMD_MS)) {
        reason = WIFI_CONTROL_REASON_FIRST_CMD_TIMEOUT;
    } else if (s->have_cmd &&
        !within(now, s->last_cmd_sent_ms, WIFI_CONTROL_SOURCE_MS)) {
        reason = WIFI_CONTROL_REASON_SOURCE_TIMEOUT;
    }
    if (reason != WIFI_CONTROL_REASON_NONE) {
        stop_now(s, reason, now);
    }
}

static bool event_time(wifi_control_state_t *s, uint64_t now)
{
    if (!live(s) || !clock_accept(s, now)) {
        return false;
    }
    deadlines(s, now);
    return true;
}

void wifi_control_state_init(wifi_control_state_t *s, uint32_t boot_id)
{
    if (s != NULL) {
        *s = (wifi_control_state_t) {
            .initialized = true,
            .phase = WIFI_CONTROL_IDLE
        };
        wifi_control_owner_init(&s->owner, boot_id);
    }
}

bool wifi_control_state_begin_arm(
    wifi_control_state_t *s, const wifi_control_request_t *r,
    bool startup_ready, bool uart_idle, uint64_t now,
    uint32_t *out_control_id)
{
    if (!live(s) || r == NULL || out_control_id == NULL) {
        return false;
    }
    s->startup_ready = startup_ready;
    if (!event_time(s, now) || s->phase != WIFI_CONTROL_IDLE ||
        !startup_ready || !uart_idle || !fresh(s, now) ||
        s->tel.state != WIFI_CONTROL_STM_DISARMED || !zero(&s->tel) ||
        r->type != WIFI_CONTROL_ARM || r->expected_boot_id != s->owner.boot_id ||
        r->ws_session_id == 0U || r->control_id != 0U ||
        !request_live(r, now)) {
        return false;
    }
    uint32_t id;
    if (wifi_control_owner_reserve(&s->owner, r->ws_session_id, &id) != WIFI_OWNER_OK) {
        return false;
    }
    s->phase = WIFI_CONTROL_ARM_PENDING;
    s->reason = WIFI_CONTROL_REASON_NONE;
    s->arm_accepted_ms = r->accepted_ms;
    s->arm_expires_ms = r->expires_ms;
    s->arm_sent = false;
    s->have_cmd = false;
    s->zero_ack = false;
    s->stop_ack = false;
    s->need_disarm = false;
    s->pending = WIFI_CONTROL_OP_NONE;
    *out_control_id = id;
    return true;
}

bool wifi_control_state_arm_sent(
    wifi_control_state_t *s, uint32_t session, uint32_t id,
    uint32_t seq, uint64_t now)
{
    if (!event_time(s, now) || s->phase != WIFI_CONTROL_ARM_PENDING ||
        s->arm_sent ||
        !wifi_control_owner_matches(&s->owner, s->owner.boot_id, session, id)) {
        return false;
    }
    if (s->tel.state != WIFI_CONTROL_STM_DISARMED || !zero(&s->tel)) {
        stop_now(s, WIFI_CONTROL_REASON_STM_STATE, now);
        return false;
    }
    s->arm_sent = true;
    s->arm_sent_ms = now;
    s->pending = WIFI_CONTROL_OP_ARM;
    s->pending_seq = seq;
    s->pending_sent_ms = now;
    return true;
}

bool wifi_control_state_cmd_sent(
    wifi_control_state_t *s, const wifi_control_request_t *r,
    uint32_t seq, uint64_t now)
{
    if (r == NULL || !event_time(s, now) ||
        (s->phase != WIFI_CONTROL_ZERO_PENDING && s->phase != WIFI_CONTROL_ACTIVE) ||
        !wifi_control_owner_matches(&s->owner, r->expected_boot_id,
                                    r->ws_session_id, r->control_id)) {
        return false;
    }
    /* Old queue identity cannot cancel a newer owner; a live owner's bad data can. */
    if (r->type != WIFI_CONTROL_CMD || r->vx_mmps != 0 || r->w_mradps != 0) {
        stop_now(s, WIFI_CONTROL_REASON_BAD_INPUT, now);
        return false;
    }
    if (!request_live(r, now)) {
        stop_now(s, WIFI_CONTROL_REASON_INPUT_EXPIRED, now);
        return false;
    }
    if (s->pending != WIFI_CONTROL_OP_NONE) {
        return false;
    }
    s->pending = WIFI_CONTROL_OP_CMD;
    s->pending_seq = seq;
    s->pending_sent_ms = now;
    s->last_cmd_sent_ms = now;
    s->have_cmd = true;
    return true;
}

void wifi_control_state_poll(
    wifi_control_state_t *s, bool startup_ready, uint64_t now)
{
    if (live(s)) {
        s->startup_ready = startup_ready;
        (void)event_time(s, now);
    }
}

void wifi_control_state_stop(
    wifi_control_state_t *s, wifi_control_reason_t reason, uint64_t now)
{
    if (live(s) && clock_accept(s, now)) {
        stop_now(s, reason == WIFI_CONTROL_REASON_NONE ?
                 WIFI_CONTROL_REASON_MANUAL_STOP : reason, now);
    }
}

void wifi_control_state_owner_closed(
    wifi_control_state_t *s, uint32_t session, uint64_t now)
{
    if (live(s) && session != 0U && s->owner.ws_session_id == session) {
        wifi_control_state_stop(s, WIFI_CONTROL_REASON_OWNER_CLOSED, now);
    }
}

bool wifi_control_state_disarm_sent(
    wifi_control_state_t *s, uint32_t seq, uint64_t now)
{
    if (!event_time(s, now) || s->phase != WIFI_CONTROL_STOPPING || !s->need_disarm) {
        return false;
    }
    s->need_disarm = false;
    s->pending = WIFI_CONTROL_OP_DISARM;
    s->pending_seq = seq;
    s->pending_sent_ms = now;
    return true;
}

bool wifi_control_state_reply(
    wifi_control_state_t *s, wifi_control_op_t op,
    uint32_t seq, bool ok, uint32_t stm_t_ms, uint64_t now)
{
    if (!event_time(s, now) || op == WIFI_CONTROL_OP_NONE ||
        op != s->pending || seq != s->pending_seq) {
        return false;
    }
    if (!ok) {
        if (op == WIFI_CONTROL_OP_DISARM) {
            blocked(s, WIFI_CONTROL_REASON_STM_ERR);
        } else {
            stop_now(s, WIFI_CONTROL_REASON_STM_ERR, now);
        }
        return true;
    }
    s->pending = WIFI_CONTROL_OP_NONE;
    if (op == WIFI_CONTROL_OP_ARM) {
        s->phase = WIFI_CONTROL_ZERO_PENDING;
    } else {
        s->confirm_seq = seq;
        s->confirm_stm_ms = stm_t_ms;
        s->confirm_tel_generation = s->tel_generation;
        if (op == WIFI_CONTROL_OP_CMD) {
            s->zero_ack = true;
        } else {
            s->stop_ack = true;
            s->stop_ack_ms = now;
        }
    }
    return true;
}

static bool stm_clock_bad(
    const wifi_control_state_t *s, const wifi_control_tel_t *tel, uint64_t now)
{
    if (!s->have_tel) {
        return false;
    }
    const uint64_t delta = (uint32_t)(tel->t_ms - s->tel.t_ms);
    const uint64_t elapsed = now - s->tel_received_ms;
    const uint64_t difference = delta > elapsed ? delta - elapsed : elapsed - delta;
    return difference > WIFI_CONTROL_STM_CLOCK_SLOP_MS ||
        (delta == 0U && !within(now, s->stm_progress_ms, WIFI_CONTROL_TEL_MS));
}

void wifi_control_state_tel(
    wifi_control_state_t *s, const wifi_control_tel_t *tel, uint64_t now)
{
    if (tel == NULL || !event_time(s, now)) {
        return;
    }
    if (tel->state != WIFI_CONTROL_STM_DISARMED &&
        tel->state != WIFI_CONTROL_STM_ARMED &&
        tel->state != WIFI_CONTROL_STM_FAULT) {
        if (controlling(s)) {
            stop_now(s, WIFI_CONTROL_REASON_STM_STATE, now);
        }
        return;
    }
    const bool bad_clock = stm_clock_bad(s, tel, now);
    if (!s->have_tel || tel->t_ms != s->tel.t_ms) {
        s->stm_progress_ms = now;
    }
    s->have_tel = true;
    s->tel = *tel;
    s->tel_received_ms = now;
    if (s->tel_generation == UINT64_MAX) {
        blocked(s, WIFI_CONTROL_REASON_STM_CLOCK);
        return;
    }
    ++s->tel_generation;
    if (controlling(s)) {
        if (bad_clock) {
            stop_now(s, WIFI_CONTROL_REASON_STM_CLOCK, now);
        } else if (tel->state == WIFI_CONTROL_STM_FAULT) {
            stop_now(s, WIFI_CONTROL_REASON_STM_FAULT, now);
        } else if (!zero(tel) ||
            (s->phase == WIFI_CONTROL_ACTIVE &&
             (tel->state != WIFI_CONTROL_STM_ARMED ||
              tel->command_age_ms >= WIFI_CONTROL_STM_TIMEOUT_MS))) {
            stop_now(s, WIFI_CONTROL_REASON_STM_STATE, now);
        }
    }
    const bool after_ack = s->tel_generation > s->confirm_tel_generation &&
        (uint32_t)(tel->t_ms - s->confirm_stm_ms) < UINT32_C(0x80000000);
    if (s->phase == WIFI_CONTROL_ZERO_PENDING && s->zero_ack && after_ack &&
        tel->last_seq == s->confirm_seq && tel->state == WIFI_CONTROL_STM_ARMED &&
        zero(tel) && tel->command_age_ms < WIFI_CONTROL_STM_TIMEOUT_MS) {
        s->phase = WIFI_CONTROL_ACTIVE;
    } else if (s->phase == WIFI_CONTROL_STOPPING && s->stop_ack && after_ack &&
        tel->last_seq == s->confirm_seq) {
        if (bad_clock || tel->state == WIFI_CONTROL_STM_ARMED || !zero(tel)) {
            blocked(s, WIFI_CONTROL_REASON_STOP_UNCONFIRMED);
        } else {
            s->phase = WIFI_CONTROL_IDLE;
            s->reason = WIFI_CONTROL_REASON_NONE;
            s->stop_ack = false;
            s->zero_ack = false;
        }
    }
}

void wifi_control_state_tx_failed(wifi_control_state_t *s, uint64_t now)
{
    if (!event_time(s, now)) {
        return;
    }
    if (s->phase == WIFI_CONTROL_STOPPING) {
        blocked(s, WIFI_CONTROL_REASON_TX_FAILED);
    } else if (controlling(s)) {
        stop_now(s, WIFI_CONTROL_REASON_TX_FAILED, now);
    }
}

uint32_t wifi_control_state_actions(const wifi_control_state_t *s)
{
    if (!live(s) ||
        (s->phase != WIFI_CONTROL_STOPPING && s->phase != WIFI_CONTROL_BLOCKED)) {
        return 0U;
    }
    return WIFI_CONTROL_ACTION_INVALIDATE_INPUTS |
        (s->need_disarm ? WIFI_CONTROL_ACTION_SEND_DISARM : 0U);
}
