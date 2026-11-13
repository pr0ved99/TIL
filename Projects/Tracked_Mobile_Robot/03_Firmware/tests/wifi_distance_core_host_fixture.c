/* Native PC only: parse -> ticket/owner/state -> exact STM wire bytes. */
#define main executor_baseline_main
#include "wifi_control_executor_host_fixture.c"
#undef main

static void parse_status(const char *text, wifi_control_parse_status_t expected)
{
    wifi_control_request_t out, before;
    memset(&out, 0xa5, sizeof(out));
    memcpy(&before, &out, sizeof(out));
    CHECK(wifi_control_parse(text, strlen(text), &out) == expected);
    if (expected != WIFI_CONTROL_PARSE_OK) {
        CHECK(memcmp(&out, &before, sizeof(out)) == 0);
    }
}

static void distance_request(uint32_t goal, uint64_t now)
{
    char text[WIFI_CONTROL_MAX_FRAME_SIZE + 1U];
    issue(WIFI_CONTROL_CMD, now);
    const int n = snprintf(text, sizeof(text),
        "CMD,boot_id=42,request_id=%u,control_id=%u,ticket=%u,"
        "vx_mmps=100,w_mradps=0,distance_mm=%u",
        (unsigned)r.request_id, (unsigned)r.control_id,
        (unsigned)r.ticket, (unsigned)goal);
    CHECK(n > 0 && (size_t)n < sizeof(text));
    CHECK(wifi_control_parse(text, (size_t)n, &r) == WIFI_CONTROL_PARSE_OK);
    CHECK(r.distance_mm == goal && r.accepted_ms == 0U && r.expires_ms == 0U);
    r.ws_session_id = 7U;
}

static void finish_cmd(uint32_t seq, uint64_t now)
{
    CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, now));
    CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_CMD, seq, true,
                                    (uint32_t)(900U + now), now));
    CHECK(wifi_control_executor_take_result(&e, &answer));
    CHECK(answer.request.distance_mm == r.distance_mm);
}

static void parsing(void)
{
    const char *prefix = "CMD,boot_id=42,request_id=1,control_id=1,ticket=1,vx_mmps=100,w_mradps=0";
    char text[180];
    const char *bad[] = {"", "-50", "+50", "4294967296", "1.5", "50x",
                        "50,distance_mm=100", "50,timeout_ms=300", "50\n"};
    for (size_t i = 0U; i < sizeof(bad) / sizeof(bad[0]); ++i) {
        snprintf(text, sizeof(text), "%s,distance_mm=%s", prefix, bad[i]);
        parse_status(text, WIFI_CONTROL_PARSE_BAD_FORMAT);
    }
    const uint32_t goals[] = {0U, 1U, 49U, 51U, 99U, 101U, 149U, 151U, 199U, 201U, UINT32_MAX};
    for (size_t i = 0U; i < sizeof(goals) / sizeof(goals[0]); ++i) {
        snprintf(text, sizeof(text), "%s,distance_mm=%u", prefix, (unsigned)goals[i]);
        parse_status(text, WIFI_CONTROL_PARSE_OUT_OF_RANGE);
    }
    parse_status("ARM,boot_id=42,request_id=1,ticket=1,distance_mm=50", WIFI_CONTROL_PARSE_BAD_FORMAT);
    parse_status("CMD,boot_id=42,request_id=1,control_id=1,ticket=1,vx_mmps=0,w_mradps=0,distance_mm=50", WIFI_CONTROL_PARSE_OUT_OF_RANGE);
    parse_status("CMD,boot_id=42,request_id=1,control_id=1,ticket=1,vx_mmps=-100,w_mradps=0,distance_mm=50", WIFI_CONTROL_PARSE_OUT_OF_RANGE);
    parse_status("CMD,boot_id=42,request_id=1,control_id=1,ticket=1,vx_mmps=100,w_mradps=1,distance_mm=50", WIFI_CONTROL_PARSE_OUT_OF_RANGE);
    parse_status("CMD,boot_id=42,request_id=1,control_id=1,ticket=1,distance_mm=50,vx_mmps=100,w_mradps=0", WIFI_CONTROL_PARSE_BAD_FORMAT);
    const char *max = "CMD,boot_id=4294967295,request_id=4294967295,control_id=4294967295,ticket=4294967295,vx_mmps=100,w_mradps=0,distance_mm=200";
    CHECK(strlen(max) == 123U && strlen(max) <= WIFI_CONTROL_MAX_FRAME_SIZE);
    parse_status(max, WIFI_CONTROL_PARSE_OK);
    wifi_control_request_t ordinary;
    CHECK(wifi_control_parse(prefix, strlen(prefix), &ordinary) == WIFI_CONTROL_PARSE_OK);
    CHECK(ordinary.distance_mm == 0U);
}

static void policy(void)
{
    wifi_control_request_t v = {.type=WIFI_CONTROL_CMD, .vx_mmps=100, .distance_mm=50U};
    CHECK(wifi_control_request_allows(&v) == (WIFI_CONTROL_ZERO_ONLY == 0U));
    CHECK(!wifi_control_zero_only_allows(&v));
    v.vx_mmps = 0;
    CHECK(!wifi_control_request_allows(&v) && !wifi_control_zero_only_allows(&v));
    v.type = WIFI_CONTROL_ARM;
    CHECK(!wifi_control_request_allows(&v) && !wifi_control_zero_only_allows(&v));
    v.distance_mm = 0U;
    CHECK(wifi_control_request_allows(&v) && wifi_control_zero_only_allows(&v));
    v.type = WIFI_CONTROL_CMD; v.vx_mmps = 100; v.distance_mm = 201U;
    CHECK(!wifi_control_request_allows(&v));
}

static void round_trip(void)
{
    const uint32_t goals[] = {50U,100U,150U,200U};
    for (size_t i = 0U; i < 4U; ++i) {
        active(); distance_request(goals[i], 140U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) == WIFI_EXEC_ACCEPTED);
        CHECK(!ticket.valid && e.request.distance_mm == goals[i]);
        CHECK(wifi_control_executor_take_tx(&e, UINT32_MAX, 141U, &tx));
        char expected[WIFI_CONTROL_UART_FRAME_SIZE];
        snprintf(expected, sizeof(expected), "CMD,seq=4294967295,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=%u\n", (unsigned)goals[i]);
        CHECK(strcmp(tx.bytes, expected) == 0 && tx.length == strlen(expected));
        CHECK(tx.length < WIFI_CONTROL_UART_FRAME_SIZE);
        finish_cmd(UINT32_MAX, 142U);
        tel(145U, WIFI_CONTROL_STM_ARMED, UINT32_MAX);
        CHECK(e.state.phase == WIFI_CONTROL_ACTIVE);
        /* A repeat keeps its goal, then explicit zero omits the suffix. */
        distance_request(goals[i], 150U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 150U) == WIFI_EXEC_ACCEPTED);
        CHECK(wifi_control_executor_take_tx(&e, 14U, 151U, &tx));
        CHECK(strstr(tx.bytes, ",distance_mm=") != NULL);
        finish_cmd(14U, 152U);
        tel(155U, WIFI_CONTROL_STM_ARMED, 14U);
        issue(WIFI_CONTROL_CMD, 160U);
        CHECK(r.distance_mm == 0U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 160U) == WIFI_EXEC_ACCEPTED);
        CHECK(wifi_control_executor_take_tx(&e, 15U, 161U, &tx));
        CHECK(strcmp(tx.bytes, "CMD,seq=15,vx_mmps=0,w_mradps=0,timeout_ms=300\n") == 0);
    }
}

static void distance_admission(const char *name)
{
    if (strcmp(name, "first_zero") == 0) {
        arm_ack(true); distance_request(50U, 116U);
    } else {
        active(); distance_request(50U, 140U);
    }
    uint64_t now = strcmp(name, "first_zero") == 0 ? 116U : 140U;
    if (strcmp(name, "other_owner") == 0) r.ws_session_id = 8U;
    if (strcmp(name, "other_boot") == 0) r.expected_boot_id = 41U;
    if (strcmp(name, "bad_ticket") == 0) ++r.ticket;
    if (strcmp(name, "expired_ticket") == 0) now += WIFI_CONTROL_TICKET_VALID_MS;
    if (strcmp(name, "bad_goal") == 0) r.distance_mm = 51U;
    if (strcmp(name, "other_control") == 0) ++r.control_id;
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, now) != WIFI_EXEC_ACCEPTED);
    CHECK(!e.queued && !e.waiting && !e.prepared);
    if (strcmp(name, "other_owner") == 0 || strcmp(name, "other_boot") == 0 ||
        strcmp(name, "other_control") == 0) CHECK(e.state.phase == WIFI_CONTROL_ACTIVE);
}

static void interruption(const char *name)
{
    active(); distance_request(50U, 140U);
    CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) == WIFI_EXEC_ACCEPTED);
    if (strcmp(name, "queue_expired") == 0) {
        CHECK(!wifi_control_executor_take_tx(&e, 13U, 190U, &tx));
    } else if (strcmp(name, "owner_closed") == 0) {
        wifi_control_executor_owner_closed(&e, 7U, 141U);
    } else {
        CHECK(wifi_control_executor_take_tx(&e, 13U, 141U, &tx));
        if (strcmp(name, "short_tx") == 0) {
            CHECK(!wifi_control_executor_tx_complete(&e, (int)tx.length - 1, 142U));
        } else {
            CHECK(wifi_control_executor_tx_complete(&e, (int)tx.length, 142U));
            if (strcmp(name, "stm_err") == 0) {
                CHECK(wifi_control_executor_reply(&e, WIFI_CONTROL_OP_CMD, 13U, false, 1043U, 143U));
            } else {
                CHECK(strcmp(name, "ack_timeout") == 0);
                wifi_control_executor_poll(&e, true, 291U);
            }
        }
    }
    CHECK(e.state.phase == WIFI_CONTROL_STOPPING && !e.queued && !e.waiting);
    wifi_control_executor_inputs_cleared(&e);
    const uint64_t stop_now = strcmp(name, "ack_timeout") == 0 ? 292U :
        strcmp(name, "queue_expired") == 0 ? 191U : 144U;
    CHECK(wifi_control_executor_take_tx(&e, 14U, stop_now, &tx));
    CHECK(strcmp(tx.bytes, "\x18\nDISARM,seq=14\n") == 0);
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    const char *name = argv[1];
    if (strcmp(name, "parsing") == 0) parsing();
    else if (strcmp(name, "distance_policy") == 0) policy();
    else if (WIFI_CONTROL_ZERO_ONLY != 0U) {
        active(); distance_request(50U, 140U);
        CHECK(wifi_control_executor_submit(&e, &r, &ticket, true, true, 140U) != WIFI_EXEC_ACCEPTED);
        CHECK(!e.queued && !e.waiting);
    } else if (strcmp(name, "distance_round_trip") == 0) round_trip();
    else if (strcmp(name, "queue_expired") == 0 || strcmp(name, "owner_closed") == 0 ||
             strcmp(name, "short_tx") == 0 || strcmp(name, "stm_err") == 0 || strcmp(name, "ack_timeout") == 0) interruption(name);
    else distance_admission(name);
    printf("PASS %s\n", name);
    return 0;
}
