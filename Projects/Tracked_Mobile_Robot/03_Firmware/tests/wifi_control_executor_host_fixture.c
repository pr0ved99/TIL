#include "wifi_control_executor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Keep the saved baseline runnable while the user types the new protocol. */
#ifdef WIFI_CONTROL_UART_CANCEL
#define EXPECT_STOP_PREFIX "\x18\n"
#define EXPECT_SHORT_TX_PREFIX "\x18\n"
#else
#define EXPECT_STOP_PREFIX ""
#define EXPECT_SHORT_TX_PREFIX "\n"
#endif

#define CHECK(v) do { if (!(v)) { fprintf(stderr, "line %d: %s\n", __LINE__, #v); exit(1); } } while (0)
static wifi_control_executor_t e;
static wifi_control_ticket_pool_t pool;
static wifi_control_ticket_t ticket;
static wifi_control_request_t r;
static wifi_control_tx_t tx;
static wifi_control_executor_result_t answer;

static void tel(uint64_t now, wifi_control_stm_state_t state, uint32_t seq)
{
    wifi_control_tel_t t = {
        .state = state, .t_ms = (uint32_t)(900U + now),
        .last_seq = seq, .command_age_ms = 10U
    };
    wifi_control_executor_tel(&e, &t, now);
}

static void setup(void)
{
    wifi_control_executor_init(&e, 42U);
    wifi_control_ticket_pool_init(&pool, 42U);
    ticket = (wifi_control_ticket_t) {0};
    r = (wifi_control_request_t) {0};
    tel(100U, WIFI_CONTROL_STM_DISARMED, 0U);
}

static void issue(wifi_control_type_t type, uint64_t now)
{
    const uint32_t id = type == WIFI_CONTROL_ARM ? 0U : e.state.owner.control_id;
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 7U, type, id, now) == WIFI_TICKET_OK);
    r = (wifi_control_request_t) {
        .type = type, .expected_boot_id = 42U, .request_id = ticket.id,
        .ws_session_id = 7U, .control_id = id, .ticket = ticket.id
    };
}

static void queue_arm(void)
{
    setup();
    issue(WIFI_CONTROL_ARM, 100U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 100U) == WIFI_EXEC_ACCEPTED);
    CHECK(!ticket.valid && e.queued && e.state.owner.control_id == 1U);
}

static void arm_ack(bool drain)
{
    queue_arm();
    CHECK(wifi_control_executor_take_tx(&e, 11U, 110U, &tx));
    CHECK(strcmp(tx.bytes, "ARM,seq=11\n") == 0 && tx.length == strlen(tx.bytes));
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 111U));
    CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_ARM, 11U, true, 1015U, 115U));
    CHECK(e.state.phase == WIFI_CONTROL_ZERO_PENDING && e.state.owner.ws_session_id == 7U);
    if (drain) {
        CHECK(wifi_control_executor_take_result(&e, &answer));
        CHECK(strcmp(answer.status, "OK") == 0 && answer.seq == 11U);
    }
}

static void active(void)
{
    arm_ack(true);
    issue(WIFI_CONTROL_CMD, 116U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 116U) == WIFI_EXEC_ACCEPTED);
    CHECK(wifi_control_executor_take_tx(&e, 12U, 120U, &tx));
    CHECK(strcmp(tx.bytes, "CMD,seq=12,vx_mmps=0,w_mradps=0,timeout_ms=300\n") == 0);
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 121U));
    CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_CMD, 12U, true, 1025U, 125U));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(e.state.phase == WIFI_CONTROL_ZERO_PENDING);
    tel(130U, WIFI_CONTROL_STM_ARMED, 12U);
    CHECK(e.state.phase == WIFI_CONTROL_ACTIVE);
}

static void normal(void)
{
    active();
    CHECK(!wifi_control_executor_allows_ping(&e));
    wifi_control_executor_stop(&e, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    CHECK(wifi_control_executor_needs_invalidation(&e));
    CHECK(!wifi_control_executor_take_tx(&e, 13U, 161U, &tx));
    wifi_control_executor_inputs_cleared(&e);
    CHECK(wifi_control_executor_take_tx(&e, 13U, 162U, &tx));
    CHECK(strcmp(tx.bytes, EXPECT_STOP_PREFIX "DISARM,seq=13\n") == 0);
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 163U));
    CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_DISARM, 13U, true, 1065U, 165U));
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
    tel(170U, WIFI_CONTROL_STM_DISARMED, 13U);
    CHECK(e.state.phase == WIFI_CONTROL_IDLE && wifi_control_executor_allows_ping(&e));
    CHECK(!wifi_control_executor_take_tx(&e, 14U, 171U, &tx));
}

static void admission(void)
{
    setup(); issue(WIFI_CONTROL_ARM, 100U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, false, true, 100U) == WIFI_EXEC_NOT_READY);
    CHECK(ticket.valid && !e.queued);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, false, 100U) == WIFI_EXEC_NOT_READY);
    tel(101U, WIFI_CONTROL_STM_FAULT, 0U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 101U) == WIFI_EXEC_NOT_READY);
    CHECK(!wifi_control_executor_take_tx(&e, 11U, 102U, &tx));
    CHECK(e.state.owner.ws_session_id == 0U && ticket.valid);
}

static void ticket_expiry(void)
{
    setup(); issue(WIFI_CONTROL_ARM, 100U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 250U) == WIFI_EXEC_TICKET_REJECTED);
    CHECK(!ticket.valid && !e.queued);
    CHECK(!wifi_control_executor_take_tx(&e, 11U, 250U, &tx));
}

static void queue_expiry(void)
{
    queue_arm();
    CHECK(!wifi_control_executor_take_tx(&e, 11U, 150U, &tx));
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING && !e.queued);
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(!answer.has_seq && strcmp(answer.status, "QUEUE_EXPIRED") == 0);
}

static void cancel_order(void)
{
    queue_arm();
    wifi_control_executor_stop(&e, WIFI_CONTROL_REASON_MANUAL_STOP, 101U);
    CHECK(!wifi_control_executor_take_tx(&e, 11U, 102U, &tx));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(!answer.has_seq && strcmp(answer.status, "CANCELLED") == 0);
    wifi_control_executor_inputs_cleared(&e);
    CHECK(wifi_control_executor_take_tx(&e, 12U, 103U, &tx));
    CHECK(tx.op == WIFI_CONTROL_OP_DISARM);
    CHECK(!wifi_control_executor_take_tx(&e, 13U, 103U, &tx));
}

static void connection_identity(void)
{
    queue_arm();
    wifi_control_executor_owner_closed(&e, 99U, 101U);
    CHECK(e.queued && e.state.owner.ws_session_id == 7U);
    wifi_control_executor_owner_closed(&e, 7U, 102U);
    CHECK(!e.queued && e.state.owner.ws_session_id == 0U);
    CHECK(!wifi_control_executor_take_tx(&e, 11U, 103U, &tx));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(strcmp(answer.status, "CONNECTION_CLOSED") == 0);
}

static void cancel_during_tx(void)
{
    queue_arm();
    CHECK(wifi_control_executor_take_tx(&e, 11U, 110U, &tx));
    wifi_control_executor_owner_closed(&e, 7U, 111U);
    wifi_control_executor_inputs_cleared(&e);
    CHECK(!wifi_control_executor_take_tx(&e, 12U, 111U, &tx));
    CHECK(!wifi_control_executor_tx_complete(&e, -1, 112U));
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
    CHECK(wifi_control_executor_take_tx(&e, 12U, 113U, &tx));
    CHECK(strcmp(tx.bytes, EXPECT_SHORT_TX_PREFIX "DISARM,seq=12\n") == 0);
}

static void partial_tx(void)
{
    queue_arm();
    CHECK(wifi_control_executor_take_tx(&e, 11U, 110U, &tx));
    CHECK(!wifi_control_executor_tx_complete(&e, 3, 111U));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(strcmp(answer.status, "TX_ERROR") == 0);
    wifi_control_executor_inputs_cleared(&e);
    CHECK(wifi_control_executor_take_tx(&e, 12U, 112U, &tx));
    CHECK(strcmp(tx.bytes, EXPECT_SHORT_TX_PREFIX "DISARM,seq=12\n") == 0);
    CHECK(!wifi_control_executor_tx_complete(&e, -1, 113U));
    CHECK(e.state.phase == WIFI_CONTROL_BLOCKED);
}

static void response_identity(void)
{
    queue_arm();
    CHECK(wifi_control_executor_take_tx(&e, 11U, 110U, &tx));
    CHECK(!wifi_control_executor_reply(&e, WIFI_CONTROL_OP_ARM, 11U, true, 1011U, 111U));
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 111U));
    CHECK(!wifi_control_executor_reply(&e, WIFI_CONTROL_OP_CMD, 11U, true, 1012U, 112U));
    CHECK(!wifi_control_executor_reply(&e, WIFI_CONTROL_OP_ARM, 99U, true, 1013U, 113U));
    CHECK(!e.have_result && e.waiting);
    CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_ARM, 11U, false, 1014U, 114U));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(strcmp(answer.status, "STM_ERROR") == 0 && e.state.phase == WIFI_CONTROL_STOPPING);
}

static void ack_deadline(void)
{
    queue_arm();
    CHECK(wifi_control_executor_take_tx(&e, 11U, 110U, &tx));
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 111U));
    CHECK(!wifi_control_executor_reply(&e, WIFI_CONTROL_OP_ARM, 11U, true, 1160U, 260U));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(strcmp(answer.status, "TIMEOUT") == 0 && e.state.phase == WIFI_CONTROL_STOPPING);
}

static void output_and_copy(void)
{
    arm_ack(false);
    issue(WIFI_CONTROL_CMD, 116U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 116U) == WIFI_EXEC_OUTPUT_PENDING);
    CHECK(ticket.valid && wifi_control_executor_take_result(&e, &answer));
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 117U) == WIFI_EXEC_ACCEPTED);
    r.vx_mmps = 100; r.ws_session_id = 99U;
    CHECK(wifi_control_executor_take_tx(&e, 12U, 120U, &tx));
    CHECK(strcmp(tx.bytes, "CMD,seq=12,vx_mmps=0,w_mradps=0,timeout_ms=300\n") == 0);
}

static void zero_only_and_old_owner(void)
{
    active();
    issue(WIFI_CONTROL_CMD, 140U);
    r.control_id = 2U;
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) == WIFI_EXEC_TICKET_REJECTED);
    CHECK(e.state.phase == WIFI_CONTROL_ACTIVE && ticket.valid);
    r.control_id = 1U; r.w_mradps = 1;
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 141U) == WIFI_EXEC_BAD_INPUT);
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING && !e.queued);
}

static void cmd_queue_expiry(void)
{
    active(); issue(WIFI_CONTROL_CMD, 150U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 150U) == WIFI_EXEC_ACCEPTED);
    CHECK(!wifi_control_executor_take_tx(&e, 13U, 200U, &tx));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(answer.seq == 0U && strcmp(answer.status, "QUEUE_EXPIRED") == 0);
}

static void source_and_blocked(void)
{
    active();
    wifi_control_executor_poll(&e, true, 320U);
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING && e.state.reason == WIFI_CONTROL_REASON_SOURCE_TIMEOUT);
    wifi_control_executor_poll(&e, true, 470U);
    CHECK(e.state.phase == WIFI_CONTROL_BLOCKED && wifi_control_executor_allows_ping(&e));
    CHECK(!wifi_control_executor_take_tx(&e, 13U, 471U, &tx));
    wifi_control_executor_stop(&e, WIFI_CONTROL_REASON_MANUAL_STOP, 472U);
    CHECK(wifi_control_executor_needs_invalidation(&e));
    wifi_control_executor_inputs_cleared(&e);
    CHECK(wifi_control_executor_take_tx(&e, 14U, 473U, &tx));
    CHECK(tx.op == WIFI_CONTROL_OP_DISARM);
}

static void ticket_reuse_and_startup(void)
{
    arm_ack(true);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 116U) == WIFI_EXEC_TICKET_REJECTED);
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
    active();
    wifi_control_executor_poll(&e, false, 140U);
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING && e.state.reason == WIFI_CONTROL_REASON_STARTUP);
}

static void long_tx_completion(void)
{
    queue_arm();
    CHECK(wifi_control_executor_take_tx(&e, 11U, 110U, &tx));
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 260U));
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING);
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(strcmp(answer.status, "TIMEOUT") == 0);
}

static void seq_zero(void)
{
    queue_arm();
    CHECK(wifi_control_executor_take_tx(&e, 0U, 110U, &tx));
    CHECK(strcmp(tx.bytes, "ARM,seq=0\n") == 0);
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 111U));
    CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_ARM, 0U, true, 1015U, 115U));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(answer.has_seq && answer.seq == 0U && strcmp(answer.status, "OK") == 0);
}

int main(int argc, char **argv)
{
    static const struct { const char *name; void (*run)(void); } cases[] = {
        {"normal", normal}, {"admission", admission}, {"ticket_expiry", ticket_expiry},
        {"queue_expiry", queue_expiry}, {"cancel_order", cancel_order},
        {"connection_identity", connection_identity}, {"cancel_during_tx", cancel_during_tx},
        {"partial_tx", partial_tx}, {"response_identity", response_identity},
        {"ack_deadline", ack_deadline}, {"output_and_copy", output_and_copy},
        {"zero_only_and_old_owner", zero_only_and_old_owner}, {"cmd_queue_expiry", cmd_queue_expiry},
        {"source_and_blocked", source_and_blocked}, {"ticket_reuse_and_startup", ticket_reuse_and_startup},
        {"long_tx_completion", long_tx_completion}, {"seq_zero", seq_zero}
    };
    if (argc != 2) return 2;
    for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i) {
        if (strcmp(argv[1], cases[i].name) == 0) {
            cases[i].run(); printf("PASS %s\n", cases[i].name); return 0;
        }
    }
    return 2;
}
