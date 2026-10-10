#include "wifi_control_owner.h"
#include "wifi_control_ticket.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expression) do { \
    if (!(expression)) { \
        printf("FAIL line=%d: %s\n", __LINE__, #expression); \
        return 1; \
    } \
} while (0)

static int initial_and_binding(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 0U);
    CHECK(owner.boot_id == 0U && owner.next_control_id == 1U);
    CHECK(owner.ws_session_id == 0U && owner.control_id == 0U);
    CHECK(!wifi_control_owner_matches(&owner, 0U, 11U, 1U));
    uint32_t id = 99U;
    CHECK(wifi_control_owner_reserve(&owner, 11U, &id) == WIFI_OWNER_OK);
    CHECK(id == 1U && owner.next_control_id == 2U);
    CHECK(wifi_control_owner_matches(&owner, 0U, 11U, id));
    CHECK(!wifi_control_owner_matches(&owner, 1U, 11U, id));
    CHECK(!wifi_control_owner_matches(&owner, 0U, 12U, id));
    CHECK(!wifi_control_owner_matches(&owner, 0U, 11U, id + 1U));
    CHECK(!wifi_control_owner_matches(&owner, 0U, 0U, id));
    CHECK(!wifi_control_owner_matches(&owner, 0U, 11U, 0U));
    CHECK(!wifi_control_owner_matches(NULL, 0U, 11U, id));
    return 0;
}

static int single_controller(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 7U);
    uint32_t id = 0U;
    CHECK(wifi_control_owner_reserve(&owner, 11U, &id) == WIFI_OWNER_OK);
    uint32_t other = 99U;
    CHECK(wifi_control_owner_reserve(&owner, 12U, &other) == WIFI_OWNER_BUSY);
    CHECK(other == 99U && owner.next_control_id == 2U);
    CHECK(wifi_control_owner_matches(&owner, 7U, 11U, id));
    CHECK(wifi_control_owner_reserve(&owner, 11U, &other) == WIFI_OWNER_BUSY);
    CHECK(other == 99U && owner.next_control_id == 2U);
    CHECK(!wifi_control_owner_matches(&owner, 7U, 12U, id));
    return 0;
}

static int same_session_rearm(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 7U);
    uint32_t old_id = 0U, new_id = 0U;
    CHECK(wifi_control_owner_reserve(&owner, 11U, &old_id) == WIFI_OWNER_OK);
    wifi_control_owner_revoke(&owner);
    CHECK(!wifi_control_owner_matches(&owner, 7U, 11U, old_id));
    CHECK(wifi_control_owner_reserve(&owner, 11U, &new_id) == WIFI_OWNER_OK);
    CHECK(new_id == old_id + 1U);
    CHECK(!wifi_control_owner_matches(&owner, 7U, 11U, old_id));
    CHECK(wifi_control_owner_matches(&owner, 7U, 11U, new_id));
    return 0;
}

static int new_session_rearm(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 7U);
    uint32_t old_id = 0U, new_id = 0U;
    CHECK(wifi_control_owner_reserve(&owner, 11U, &old_id) == WIFI_OWNER_OK);
    wifi_control_owner_revoke(&owner);
    CHECK(wifi_control_owner_reserve(&owner, 12U, &new_id) == WIFI_OWNER_OK);
    CHECK(new_id == 2U);
    CHECK(!wifi_control_owner_matches(&owner, 7U, 11U, old_id));
    CHECK(!wifi_control_owner_matches(&owner, 7U, 11U, new_id));
    CHECK(!wifi_control_owner_matches(&owner, 7U, 12U, old_id));
    CHECK(wifi_control_owner_matches(&owner, 7U, 12U, new_id));
    return 0;
}

static int revoke_preserves_pool(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 7U);
    wifi_control_owner_revoke(&owner);
    CHECK(owner.boot_id == 7U && owner.next_control_id == 1U);
    uint32_t id = 0U;
    CHECK(wifi_control_owner_reserve(&owner, 11U, &id) == WIFI_OWNER_OK);
    wifi_control_owner_revoke(&owner);
    wifi_control_owner_revoke(&owner);
    CHECK(owner.ws_session_id == 0U && owner.control_id == 0U);
    CHECK(owner.boot_id == 7U && owner.next_control_id == 2U);
    CHECK(!wifi_control_owner_matches(&owner, 7U, 11U, id));
    return 0;
}

static int id_sequence(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 7U);
    for (uint32_t i = 1U; i <= 256U; ++i) {
        uint32_t id = 0U;
        const uint32_t session = i % 3U + 1U;
        CHECK(wifi_control_owner_reserve(&owner, session, &id) == WIFI_OWNER_OK);
        CHECK(id == i && wifi_control_owner_matches(&owner, 7U, session, id));
        if (i > 1U) CHECK(!wifi_control_owner_matches(&owner, 7U, session, i - 1U));
        wifi_control_owner_revoke(&owner);
    }
    CHECK(owner.next_control_id == 257U);
    return 0;
}

static int exhaustion(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 7U);
    owner.next_control_id = UINT32_MAX;
    uint32_t id = 0U;
    CHECK(wifi_control_owner_reserve(&owner, 11U, &id) == WIFI_OWNER_OK);
    CHECK(id == UINT32_MAX && owner.next_control_id == (uint64_t)UINT32_MAX + 1U);
    wifi_control_owner_revoke(&owner);
    uint32_t untouched = 99U;
    for (unsigned i = 0U; i < 2U; ++i) {
        CHECK(wifi_control_owner_reserve(&owner, 11U, &untouched) == WIFI_OWNER_EXHAUSTED);
        CHECK(untouched == 99U && owner.next_control_id == (uint64_t)UINT32_MAX + 1U);
        CHECK(owner.ws_session_id == 0U && owner.control_id == 0U);
    }
    owner.next_control_id = 0U;
    CHECK(wifi_control_owner_reserve(&owner, 11U, &untouched) == WIFI_OWNER_EXHAUSTED);
    CHECK(untouched == 99U);
    return 0;
}

static int invalid_arguments(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 7U);
    uint32_t id = 99U;
    CHECK(wifi_control_owner_reserve(NULL, 11U, &id) == WIFI_OWNER_BAD_ARGUMENT);
    CHECK(wifi_control_owner_reserve(&owner, 0U, &id) == WIFI_OWNER_BAD_ARGUMENT);
    CHECK(wifi_control_owner_reserve(&owner, 11U, NULL) == WIFI_OWNER_BAD_ARGUMENT);
    CHECK(id == 99U && owner.next_control_id == 1U);
    CHECK(owner.ws_session_id == 0U && owner.control_id == 0U);
    wifi_control_owner_init(NULL, 7U);
    wifi_control_owner_revoke(NULL);
    CHECK(wifi_control_owner_reserve(&owner, 11U, &id) == WIFI_OWNER_OK);
    CHECK(wifi_control_owner_reserve(&owner, 0U, &id) == WIFI_OWNER_BAD_ARGUMENT);
    CHECK(id == 1U && wifi_control_owner_matches(&owner, 7U, 11U, 1U));
    return 0;
}

static int ticket_consumption_keeps_owner(void)
{
    wifi_control_owner_t owner;
    wifi_control_owner_init(&owner, 7U);
    uint32_t id = 0U;
    CHECK(wifi_control_owner_reserve(&owner, 11U, &id) == WIFI_OWNER_OK);
    wifi_control_ticket_pool_t pool;
    wifi_control_ticket_pool_init(&pool, 7U);
    wifi_control_ticket_t ticket = {0};
    for (uint32_t request_id = 1U; request_id <= 2U; ++request_id) {
        const uint64_t now = 1000U + request_id * 100U;
        CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_CMD,
                                       id, now) == WIFI_TICKET_OK);
        const wifi_control_request_t request = {
            .type = WIFI_CONTROL_CMD, .expected_boot_id = 7U,
            .ws_session_id = 11U, .control_id = id,
            .request_id = request_id, .ticket = ticket.id
        };
        CHECK(wifi_control_owner_matches(&owner, request.expected_boot_id,
                                        request.ws_session_id, request.control_id));
        CHECK(wifi_control_ticket_consume(&ticket, &request, now + 1U) == WIFI_TICKET_OK);
        CHECK(!ticket.valid && owner.next_control_id == 2U);
        CHECK(wifi_control_owner_matches(&owner, 7U, 11U, id));
    }
    CHECK(wifi_control_ticket_issue(&pool, &ticket, 11U, WIFI_CONTROL_CMD,
                                   id, 1300U) == WIFI_TICKET_OK);
    wifi_control_owner_revoke(&owner);
    CHECK(!wifi_control_owner_matches(&owner, 7U, 11U, id));
    CHECK(ticket.valid);
    wifi_control_ticket_invalidate(&ticket);
    CHECK(!ticket.valid);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    static const struct {
        const char *name;
        int (*run)(void);
    } cases[] = {
        {"initial_and_binding", initial_and_binding},
        {"single_controller", single_controller},
        {"same_session_rearm", same_session_rearm},
        {"new_session_rearm", new_session_rearm},
        {"revoke_preserves_pool", revoke_preserves_pool},
        {"id_sequence", id_sequence}, {"exhaustion", exhaustion},
        {"invalid_arguments", invalid_arguments},
        {"ticket_consumption_keeps_owner", ticket_consumption_keeps_owner},
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
