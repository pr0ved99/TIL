#include "wifi_control_executor.h"

#include <inttypes.h>
#include <stdio.h>

static bool live(const wifi_control_executor_t *e)
{
    return e != NULL && e->state.initialized;
}

static const char *cancel_status(const wifi_control_state_t *s, bool queued)
{
    switch (s->reason) {
    case WIFI_CONTROL_REASON_OWNER_CLOSED: return "CONNECTION_CLOSED";
    case WIFI_CONTROL_REASON_INPUT_EXPIRED: return queued ? "QUEUE_EXPIRED" : "TIMEOUT";
    case WIFI_CONTROL_REASON_ACK_TIMEOUT:
    case WIFI_CONTROL_REASON_FIRST_CMD_TIMEOUT:
    case WIFI_CONTROL_REASON_SOURCE_TIMEOUT: return "TIMEOUT";
    case WIFI_CONTROL_REASON_STM_ERR: return "STM_ERROR";
    case WIFI_CONTROL_REASON_TX_FAILED: return "TX_ERROR";
    default: return "CANCELLED";
    }
}

static void result(wifi_control_executor_t *e, const char *status)
{
    e->result = (wifi_control_executor_result_t) {
        .request = e->request, .seq = e->request_seq,
        .has_seq = e->waiting, .status = status
    };
    e->have_result = true;
    e->queued = false;
    e->waiting = false;
}

static void reconcile(wifi_control_executor_t *e)
{
    const wifi_control_phase_t phase = e->state.phase;
    if (phase == WIFI_CONTROL_STOPPING || phase == WIFI_CONTROL_BLOCKED) {
        if (phase != e->observed_phase) {
            e->inputs_cleared = false;
        }
        if (e->queued || e->waiting) {
            result(e, cancel_status(&e->state, e->queued));
        }
    }
    e->observed_phase = phase;
}

static wifi_control_submit_status_t reject(
    wifi_control_executor_t *e, const wifi_control_request_t *r,
    wifi_control_submit_status_t status, wifi_control_reason_t reason,
    uint64_t now)
{
    /* An old generation/other connection cannot cancel a newer owner. */
    if (r->expected_boot_id == e->state.owner.boot_id &&
        r->ws_session_id != 0U && r->ws_session_id == e->state.owner.ws_session_id &&
        (r->control_id == e->state.owner.control_id ||
         (r->type == WIFI_CONTROL_ARM && r->control_id == 0U))) {
        wifi_control_state_stop(&e->state, reason, now);
        reconcile(e);
    }
    return status;
}

void wifi_control_executor_init(wifi_control_executor_t *e, uint32_t boot_id)
{
    if (e != NULL) {
        *e = (wifi_control_executor_t) {0};
        wifi_control_state_init(&e->state, boot_id);
        e->observed_phase = WIFI_CONTROL_IDLE;
    }
}

void wifi_control_executor_poll(
    wifi_control_executor_t *e, bool startup_ready, uint64_t now)
{
    if (live(e)) {
        wifi_control_state_poll(&e->state, startup_ready, now);
        reconcile(e);
    }
}

wifi_control_submit_status_t wifi_control_executor_submit(
    wifi_control_executor_t *e, const wifi_control_request_t *r,
    wifi_control_ticket_t *ticket, bool startup_ready, bool uart_idle,
    uint64_t now)
{
    if (!live(e) || r == NULL || ticket == NULL) {
        return WIFI_EXEC_BAD_INPUT;
    }
    wifi_control_executor_poll(e, startup_ready, now);
    if (r->expected_boot_id != e->state.owner.boot_id) {
        return WIFI_EXEC_BOOT_MISMATCH;
    }
    if (r->request_id == 0U || r->ws_session_id == 0U ||
        (r->type != WIFI_CONTROL_ARM && r->type != WIFI_CONTROL_CMD) ||
        !wifi_control_zero_only_allows(r)) {
        return reject(e, r, WIFI_EXEC_BAD_INPUT, WIFI_CONTROL_REASON_BAD_INPUT, now);
    }
    if (e->queued || e->waiting || e->prepared) {
        return WIFI_EXEC_BUSY;
    }
    if (e->have_result) {
        return WIFI_EXEC_OUTPUT_PENDING;
    }
    wifi_control_ticket_t checked = *ticket;
    wifi_control_request_t accepted = *r;
    accepted.accepted_ms = now;
    accepted.expires_ms = checked.expires_ms;
    const wifi_control_ticket_status_t ticket_status =
        wifi_control_ticket_consume(&checked, &accepted, now);
    if (ticket_status != WIFI_TICKET_OK) {
        if (ticket_status == WIFI_TICKET_EXPIRED) {
            *ticket = checked;
        }
        return reject(e, r, WIFI_EXEC_TICKET_REJECTED,
            ticket_status == WIFI_TICKET_EXPIRED ? WIFI_CONTROL_REASON_INPUT_EXPIRED :
                WIFI_CONTROL_REASON_BAD_INPUT, now);
    }
    if (accepted.type == WIFI_CONTROL_ARM) {
        uint32_t id;
        if (!wifi_control_state_begin_arm(
                &e->state, &accepted, startup_ready, uart_idle, now, &id)) {
            return reject(e, r, WIFI_EXEC_NOT_READY, WIFI_CONTROL_REASON_BAD_INPUT, now);
        }
        accepted.control_id = id;
    } else if (!uart_idle ||
        (e->state.phase != WIFI_CONTROL_ZERO_PENDING && e->state.phase != WIFI_CONTROL_ACTIVE) ||
        !wifi_control_owner_matches(&e->state.owner, accepted.expected_boot_id,
                                   accepted.ws_session_id, accepted.control_id)) {
        return reject(e, r, WIFI_EXEC_NOT_READY, WIFI_CONTROL_REASON_BAD_INPUT, now);
    }
    /* Queue reservation and ticket consumption are one serialized operation. */
    *ticket = checked;
    e->request = accepted;
    e->request_seq = 0U;
    e->queued = true;
    reconcile(e);
    return WIFI_EXEC_ACCEPTED;
}

bool wifi_control_executor_needs_invalidation(const wifi_control_executor_t *e)
{
    return live(e) &&
        (e->state.phase == WIFI_CONTROL_STOPPING || e->state.phase == WIFI_CONTROL_BLOCKED) &&
        !e->inputs_cleared;
}

void wifi_control_executor_inputs_cleared(wifi_control_executor_t *e)
{
    if (wifi_control_executor_needs_invalidation(e)) {
        e->inputs_cleared = true;
    }
}

bool wifi_control_executor_take_tx(
    wifi_control_executor_t *e, uint32_t seq, uint64_t now, wifi_control_tx_t *out)
{
    if (!live(e) || out == NULL) {
        return false;
    }
    wifi_control_executor_poll(e, e->state.startup_ready, now);
    if (e->prepared) {
        return false;
    }
    wifi_control_op_t op;
    if (e->state.phase == WIFI_CONTROL_STOPPING && e->state.need_disarm) {
        if (!e->inputs_cleared) {
            return false;
        }
        op = WIFI_CONTROL_OP_DISARM;
    } else if (e->queued) {
        op = e->request.type == WIFI_CONTROL_ARM ? WIFI_CONTROL_OP_ARM : WIFI_CONTROL_OP_CMD;
    } else {
        return false;
    }
    wifi_control_tx_t tx = {.op = op, .seq = seq};
    int n;
    if (op == WIFI_CONTROL_OP_CMD) {
        n = snprintf(tx.bytes, sizeof(tx.bytes),
            "CMD,seq=%" PRIu32 ",vx_mmps=0,w_mradps=0,timeout_ms=300\n", seq);
    } else {
        n = snprintf(tx.bytes, sizeof(tx.bytes), "%s%s,seq=%" PRIu32 "\n",
            op == WIFI_CONTROL_OP_DISARM && e->need_line_sync ? "\n" : "",
            op == WIFI_CONTROL_OP_ARM ? "ARM" : "DISARM", seq);
    }
    if (n <= 0 || (size_t)n >= sizeof(tx.bytes)) {
        wifi_control_state_stop(&e->state, WIFI_CONTROL_REASON_TX_FAILED, now);
        reconcile(e);
        return false;
    }
    const bool allowed = op == WIFI_CONTROL_OP_ARM ?
        wifi_control_state_arm_sent(&e->state, e->request.ws_session_id,
                                    e->request.control_id, seq, now) :
        op == WIFI_CONTROL_OP_CMD ? wifi_control_state_cmd_sent(&e->state, &e->request, seq, now) :
        wifi_control_state_disarm_sent(&e->state, seq, now);
    reconcile(e);
    if (!allowed) {
        return false;
    }
    tx.length = (size_t)n;
    e->prepared = true;
    e->prepared_op = op;
    e->prepared_seq = seq;
    e->prepared_length = tx.length;
    if (op != WIFI_CONTROL_OP_DISARM) {
        e->queued = false;
        e->waiting = true;
        e->request_seq = seq;
    }
    *out = tx;
    return true;
}

bool wifi_control_executor_tx_complete(wifi_control_executor_t *e, int written, uint64_t now)
{
    if (!live(e) || !e->prepared) {
        return false;
    }
    const bool full = written >= 0 && (size_t)written == e->prepared_length;
    e->prepared = false;
    if (!full) {
        e->need_line_sync = true;
        /* An intervening cancel already revoked an old ARM/CMD pending. */
        if (e->state.pending == e->prepared_op && e->state.pending_seq == e->prepared_seq) {
            wifi_control_state_tx_failed(&e->state, now);
        }
    } else if (e->prepared_op == WIFI_CONTROL_OP_DISARM) {
        e->need_line_sync = false;
    }
    wifi_control_state_poll(&e->state, e->state.startup_ready, now);
    reconcile(e);
    return full;
}

bool wifi_control_executor_reply(
    wifi_control_executor_t *e, wifi_control_op_t op,
    uint32_t seq, bool ok, uint32_t stm_t_ms, uint64_t now)
{
    if (!live(e) || e->prepared) {
        return false;
    }
    const bool matched = wifi_control_state_reply(&e->state, op, seq, ok, stm_t_ms, now);
    if (matched && op != WIFI_CONTROL_OP_DISARM && e->waiting) {
        result(e, ok ? "OK" : "STM_ERROR");
    }
    reconcile(e);
    return matched;
}

void wifi_control_executor_tel(
    wifi_control_executor_t *e, const wifi_control_tel_t *tel, uint64_t now)
{
    if (live(e)) {
        wifi_control_state_tel(&e->state, tel, now);
        reconcile(e);
    }
}

void wifi_control_executor_stop(
    wifi_control_executor_t *e, wifi_control_reason_t reason, uint64_t now)
{
    if (live(e)) {
        wifi_control_state_stop(&e->state, reason, now);
        reconcile(e);
    }
}

void wifi_control_executor_owner_closed(
    wifi_control_executor_t *e, uint32_t session, uint64_t now)
{
    if (live(e)) {
        wifi_control_state_owner_closed(&e->state, session, now);
        reconcile(e);
    }
}

bool wifi_control_executor_take_result(
    wifi_control_executor_t *e, wifi_control_executor_result_t *out)
{
    if (!live(e) || out == NULL || !e->have_result) {
        return false;
    }
    *out = e->result;
    e->have_result = false;
    return true;
}

bool wifi_control_executor_allows_ping(const wifi_control_executor_t *e)
{
    return live(e) && !e->queued && !e->waiting && !e->prepared &&
        e->state.pending == WIFI_CONTROL_OP_NONE &&
        (e->state.phase == WIFI_CONTROL_IDLE || e->state.phase == WIFI_CONTROL_BLOCKED);
}
