/* PC lesson: real ESP pure-C modules driven by a synthetic clock.
 * Printed UART frames are never sent to a device. One serialized caller. */
#include "wifi_control_executor.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static wifi_control_executor_t executor;
static wifi_control_ticket_pool_t pool;
static wifi_control_ticket_t ticket;

static void show(unsigned now, const char *event)
{
    static const char *const names[] = {
        "IDLE", "ARM_PENDING", "ZERO_PENDING", "ACTIVE", "STOPPING", "BLOCKED"
    };
    printf("%3u ms %-24s -> %s\n", now, event, names[executor.state.phase]);
}

static void telemetry(unsigned now, wifi_control_stm_state_t state, uint32_t seq)
{
    wifi_control_tel_t tel = {
        .state = state, .t_ms = 900U + now,
        .last_seq = seq, .command_age_ms = 10U
    };
    wifi_control_executor_tel(&executor, &tel, now);
}

static void setup(void)
{
    wifi_control_executor_init(&executor, 42U);
    wifi_control_ticket_pool_init(&pool, 42U);
    ticket = (wifi_control_ticket_t){0};
    telemetry(100U, WIFI_CONTROL_STM_DISARMED, 0U);
}

static void submit(wifi_control_type_t type, unsigned now)
{
    uint32_t control = type == WIFI_CONTROL_ARM ? 0U : executor.state.owner.control_id;
    assert(wifi_control_ticket_issue(&pool, &ticket, 7U, type, control, now) == WIFI_TICKET_OK);
    char text[128];
    int n = type == WIFI_CONTROL_ARM ?
        snprintf(text, sizeof(text), "ARM,boot_id=42,request_id=1,ticket=%lu",
                 (unsigned long)ticket.id) :
        snprintf(text, sizeof(text),
                 "CMD,boot_id=42,request_id=2,control_id=%lu,ticket=%lu,vx_mmps=0,w_mradps=0",
                 (unsigned long)control, (unsigned long)ticket.id);
    assert(n > 0 && (size_t)n < sizeof(text));
    wifi_control_request_t request;
    assert(wifi_control_parse(text, (size_t)n, &request) == WIFI_CONTROL_PARSE_OK);
    /* Real HTTP adapter supplies the live session; it is not parsed from text. */
    request.ws_session_id = 7U;
    assert(wifi_control_executor_submit(&executor, &request, &ticket, true, true, now)
           == WIFI_EXEC_ACCEPTED);
    assert(!ticket.valid);
}

static void write_frame(unsigned now, uint32_t seq)
{
    wifi_control_tx_t tx;
    assert(wifi_control_executor_take_tx(&executor, seq, now, &tx));
    printf("  simulated TX only: %s", tx.bytes);
    /* Simulated successful driver return, not physical transmission evidence. */
    assert(wifi_control_executor_tx_complete(&executor, (int)tx.length, now + 1U));
}

static void reply(unsigned now, wifi_control_op_t op, uint32_t seq)
{
    assert(wifi_control_executor_reply(&executor, op, seq, true, 900U + now, now));
    if (op != WIFI_CONTROL_OP_DISARM) {
        wifi_control_executor_result_t result;
        assert(wifi_control_executor_take_result(&executor, &result));
        assert(strcmp(result.status, "OK") == 0);
    }
}

static void invalidate_inputs(void)
{
    /* Real main invalidates EVERY session ticket and clears ingress work. */
    wifi_control_ticket_invalidate(&ticket);
    wifi_control_executor_inputs_cleared(&executor);
}

int main(void)
{
    setup();
    submit(WIFI_CONTROL_ARM, 100U); show(100, "ARM accepted");
    write_frame(110U, 11U);
    reply(115U, WIFI_CONTROL_OP_ARM, 11U); show(115, "ARM ACK");
    assert(executor.state.phase == WIFI_CONTROL_ZERO_PENDING);
    submit(WIFI_CONTROL_CMD, 116U);
    write_frame(120U, 12U);
    reply(125U, WIFI_CONTROL_OP_CMD, 12U); show(125, "CMD ACK only");
    assert(executor.state.phase == WIFI_CONTROL_ZERO_PENDING);
    telemetry(130U, WIFI_CONTROL_STM_ARMED, 12U); show(130, "fresh matching TEL");
    assert(executor.state.phase == WIFI_CONTROL_ACTIVE);

    wifi_control_executor_stop(&executor, WIFI_CONTROL_REASON_MANUAL_STOP, 160U);
    show(160, "manual stop");
    wifi_control_tx_t tx;
    assert(!wifi_control_executor_take_tx(&executor, 13U, 161U, &tx));
    invalidate_inputs();
    write_frame(162U, 13U);
    reply(165U, WIFI_CONTROL_OP_DISARM, 13U); show(165, "DISARM ACK only");
    assert(executor.state.phase == WIFI_CONTROL_STOPPING);
    telemetry(170U, WIFI_CONTROL_STM_DISARMED, 13U); show(170, "fresh stopped TEL");
    assert(executor.state.phase == WIFI_CONTROL_IDLE);
    assert(!wifi_control_executor_take_tx(&executor, 14U, 171U, &tx));

    puts("\nExpiry lesson:");
    assert(wifi_control_ticket_issue(&pool, &ticket, 7U, WIFI_CONTROL_ARM, 0U, 1000U) == WIFI_TICKET_OK);
    wifi_control_request_t request = {
        .type = WIFI_CONTROL_ARM, .expected_boot_id = 42U,
        .request_id = 3U, .ws_session_id = 7U, .ticket = ticket.id
    };
    wifi_control_ticket_t early = ticket;
    assert(wifi_control_ticket_consume(&early, &request, 1149U) == WIFI_TICKET_OK);
    assert(wifi_control_ticket_consume(&ticket, &request, 1150U) == WIFI_TICKET_EXPIRED);
    puts("issued=1000 expires=1150: at 1149 OK, at 1150 EXPIRED");

    puts("\nMissing stop ACK lesson:");
    setup();
    wifi_control_executor_stop(&executor, WIFI_CONTROL_REASON_MANUAL_STOP, 110U);
    invalidate_inputs();
    write_frame(120U, 21U);
    wifi_control_executor_poll(&executor, true, 270U);
    show(270, "150 ms without ACK");
    assert(executor.state.phase == WIFI_CONTROL_BLOCKED);
    assert(!wifi_control_executor_reply(&executor, WIFI_CONTROL_OP_DISARM, 21U, true, 1171U, 271U));
    assert(executor.state.phase == WIFI_CONTROL_BLOCKED);
    puts("late ACK does not restore IDLE");
    puts("PASS 04: real modules, simulated clock/transport/TEL");
    return 0;
}
