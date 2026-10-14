#include "wifi_control_ticket.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expression) do { \
    if (!(expression)) { \
        printf("FAIL line=%d: %s\n", __LINE__, #expression); \
        return 1; \
    } \
} while (0)

static wifi_control_request_t request_for(const wifi_control_ticket_t *ticket)
{
    return (wifi_control_request_t){
        .type = ticket->purpose,
        .expected_boot_id = ticket->boot_id,
        .request_id = 1U,
        .control_id = ticket->control_id,
        .ticket = ticket->id,
        .ws_session_id = ticket->ws_session_id
    };
}

static int issue_bindings(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t arm = {0}, cmd = {0};
    CHECK(wifi_control_ticket_issue(&pool, &arm, 11U, WIFI_CONTROL_ARM,
                                   0U, 1000U) == WIFI_TICKET_OK);
    CHECK(arm.boot_id == 7U && arm.ws_session_id == 11U);
    CHECK(arm.purpose == WIFI_CONTROL_ARM && arm.control_id == 0U);
    CHECK(arm.id == 1U && arm.issued_ms == 1000U && arm.expires_ms == 1150U);
    CHECK(wifi_control_ticket_issue(&pool, &cmd, 12U, WIFI_CONTROL_CMD,
                                   3U, 1001U) == WIFI_TICKET_OK);
    CHECK(cmd.purpose == WIFI_CONTROL_CMD && cmd.control_id == 3U);
    CHECK(cmd.id == 2U && cmd.ws_session_id == 12U && pool.next_id == 3U);
    return 0;
}

static int valid_window(void)
{
    const uint64_t ages[] = {0U, 149U, 150U, 151U};
    for (size_t i = 0U; i < sizeof(ages) / sizeof(ages[0]); ++i) {
        wifi_control_ticket_pool_t pool;
        wifi_control_ticket_pool_init(&pool, 7U);
        wifi_control_ticket_t ticket = {0};
        CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                       0U, 1000U) == WIFI_TICKET_OK);
        const wifi_control_request_t request = request_for(&ticket);
        const wifi_control_ticket_status_t expected = ages[i] < 150U
            ? WIFI_TICKET_OK : WIFI_TICKET_EXPIRED;
        CHECK(wifi_control_ticket_consume(&ticket, &request, 1000U + ages[i]) == expected);
        CHECK(!ticket.valid);
    }
    return 0;
}

static int single_use(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_CMD,
                                   3U, 1000U) == WIFI_TICKET_OK);
    const wifi_control_request_t request = request_for(&ticket);
    CHECK(wifi_control_ticket_consume(&ticket, &request, 1001U) == WIFI_TICKET_OK);
    CHECK(wifi_control_ticket_consume(&ticket, &request, 1002U) == WIFI_TICKET_MISMATCH);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_CMD,
                                   3U, 1003U) == WIFI_TICKET_OK);
    CHECK(ticket.id == 2U);
    CHECK(wifi_control_ticket_consume(&ticket, &request, 1004U) == WIFI_TICKET_MISMATCH);
    CHECK(ticket.valid);
    return 0;
}

static int wrong_binding(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_CMD,
                                   3U, 1000U) == WIFI_TICKET_OK);
    const wifi_control_request_t correct = request_for(&ticket);
    for (unsigned i = 0U; i < 5U; ++i) {
        wifi_control_request_t wrong = correct;
        switch (i) {
        case 0: ++wrong.expected_boot_id; break;
        case 1: ++wrong.ws_session_id; break;
        case 2: wrong.type = WIFI_CONTROL_ARM; break;
        case 3: ++wrong.control_id; break;
        default: ++wrong.ticket; break;
        }
        CHECK(wifi_control_ticket_consume(&ticket, &wrong, 1001U) == WIFI_TICKET_MISMATCH);
        CHECK(ticket.valid && pool.next_id == 2U);
    }
    CHECK(wifi_control_ticket_consume(&ticket, &correct, 1002U) == WIFI_TICKET_OK);
    return 0;
}

static int live_ticket_preserved(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1000U) == WIFI_TICKET_OK);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 12U, WIFI_CONTROL_CMD,
                                   3U, 1149U) == WIFI_TICKET_BUSY);
    CHECK(ticket.valid && ticket.id == 1U && ticket.ws_session_id == 11U);
    CHECK(ticket.expires_ms == 1150U && pool.next_id == 2U);
    const wifi_control_request_t request = request_for(&ticket);
    CHECK(wifi_control_ticket_consume(&ticket, &request, 1149U) == WIFI_TICKET_OK);
    return 0;
}

static int expired_replacement(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1000U) == WIFI_TICKET_OK);
    const wifi_control_request_t old = request_for(&ticket);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1150U) == WIFI_TICKET_OK);
    CHECK(ticket.id == 2U && ticket.expires_ms == 1300U);
    CHECK(wifi_control_ticket_consume(&ticket, &old, 1151U) == WIFI_TICKET_MISMATCH);
    CHECK(ticket.valid);
    return 0;
}

static int invalidate(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1000U) == WIFI_TICKET_OK);
    const wifi_control_request_t old = request_for(&ticket);
    wifi_control_ticket_invalidate(&ticket);
    wifi_control_ticket_invalidate(&ticket);
    CHECK(wifi_control_ticket_consume(&ticket, &old, 1001U) == WIFI_TICKET_MISMATCH);
    CHECK(pool.next_id == 2U);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 12U, WIFI_CONTROL_ARM,
                                   0U, 1002U) == WIFI_TICKET_OK);
    CHECK(ticket.id == 2U && ticket.ws_session_id == 12U);
    CHECK(wifi_control_ticket_consume(&ticket, &old, 1003U) == WIFI_TICKET_MISMATCH);
    return 0;
}

static int counter_exhaustion(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    pool.next_id = UINT32_MAX;
    wifi_control_ticket_t ticket = {0};
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1000U) == WIFI_TICKET_OK);
    CHECK(ticket.id == UINT32_MAX && pool.next_id == (uint64_t)UINT32_MAX + 1U);
    wifi_control_ticket_invalidate(&ticket);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1001U) == WIFI_TICKET_EXHAUSTED);
    CHECK(!ticket.valid && pool.next_id == (uint64_t)UINT32_MAX + 1U);
    pool.next_id = 0U;
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1002U) == WIFI_TICKET_EXHAUSTED);
    return 0;
}

static int clock_rollback(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1000U) == WIFI_TICKET_OK);
    const wifi_control_request_t request = request_for(&ticket);
    CHECK(wifi_control_ticket_consume(&ticket, &request, 999U) == WIFI_TICKET_EXPIRED);
    CHECK(!ticket.valid);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 1000U) == WIFI_TICKET_OK);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 999U) == WIFI_TICKET_EXPIRED);
    CHECK(!ticket.valid && pool.next_id == 3U);
    return 0;
}

static int time_overflow(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    const uint64_t last_issued = UINT64_MAX - 150U;
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, last_issued + 1U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(!ticket.valid && pool.next_id == 1U);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, last_issued) == WIFI_TICKET_OK);
    CHECK(ticket.expires_ms == UINT64_MAX);
    wifi_control_request_t request = request_for(&ticket);
    CHECK(wifi_control_ticket_consume(&ticket, &request, UINT64_MAX - 1U) == WIFI_TICKET_OK);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, last_issued) == WIFI_TICKET_OK);
    request = request_for(&ticket);
    CHECK(wifi_control_ticket_consume(&ticket, &request, UINT64_MAX) == WIFI_TICKET_EXPIRED);
    return 0;
}

static int invalid_arguments(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    wifi_control_request_t request = {0};
    CHECK(wifi_control_ticket_issue(NULL, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 0U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(wifi_control_ticket_issue(&pool, NULL, 11U, WIFI_CONTROL_ARM,
                                   0U, 0U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 0U, WIFI_CONTROL_ARM,
                                   0U, 0U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   1U, 0U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_CMD,
                                   0U, 0U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, (wifi_control_type_t)99,
                                   0U, 0U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(wifi_control_ticket_consume(NULL, &request, 0U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(wifi_control_ticket_consume(&ticket, NULL, 0U) == WIFI_TICKET_BAD_ARGUMENT);
    CHECK(wifi_control_ticket_consume(&ticket, &request, 0U) == WIFI_TICKET_MISMATCH);
    wifi_control_ticket_pool_init(NULL, 7U);
    wifi_control_ticket_invalidate(NULL);
    CHECK(!ticket.valid && pool.next_id == 1U);
    return 0;
}

static int boot_zero(void)
{
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 0U);
    wifi_control_ticket_t ticket = {0};
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_ARM,
                                   0U, 0U) == WIFI_TICKET_OK);
    const wifi_control_request_t request = request_for(&ticket);
    CHECK(wifi_control_ticket_consume(&ticket, &request, 1U) == WIFI_TICKET_OK);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    static const struct {
        const char *name;
        int (*run)(void);
    } cases[] = {
        {"issue_bindings", issue_bindings}, {"valid_window", valid_window},
        {"single_use", single_use}, {"wrong_binding", wrong_binding},
        {"live_ticket_preserved", live_ticket_preserved},
        {"expired_replacement", expired_replacement}, {"invalidate", invalidate},
        {"counter_exhaustion", counter_exhaustion}, {"clock_rollback", clock_rollback},
        {"time_overflow", time_overflow}, {"invalid_arguments", invalid_arguments},
        {"boot_zero", boot_zero}
    };
    for (size_t i = 0U; i < sizeof(cases) / sizeof(cases[0]); ++i) {
        if (strcmp(argv[1], cases[i].name) == 0) {
            const int result = cases[i].run();
            if (result == 0) printf("PASS %s\n", cases[i].name);
            return result;
        }
    }
    return 2;
}
