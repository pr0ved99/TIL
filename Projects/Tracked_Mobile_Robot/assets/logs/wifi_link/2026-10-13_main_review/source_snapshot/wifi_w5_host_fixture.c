/* Test-only platform adapters and independent protocol scenarios.
 * The runner inserts current production types/functions at the two markers.
 * No firmware build, real UART, or multithread scheduling occurs here.
 */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* PRODUCTION_TYPES */

typedef int BaseType_t;
typedef void *QueueHandle_t;
typedef void *SemaphoreHandle_t;
#define portMAX_DELAY UINT32_MAX
#define pdPASS 1
#define STM_UART_PORT 1
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #expr); exit(2); \
} } while (0)

static SemaphoreHandle_t s_stm_lock;
static QueueHandle_t s_wifi_command_queue = (void *)1;
static QueueHandle_t s_wifi_command_result_queue = (void *)2;
static uint32_t s_boot_id;
static uint32_t s_wifi_command_owner_session_id;
static stm_startup_t s_stm_startup;
static wifi_uart_pending_t s_wifi_uart_pending;
static uint64_t s_wifi_uart_next_seq;

static uint64_t mock_now_ms;
static wifi_command_request_t mock_request;
static bool mock_request_present;
static wifi_command_result_t mock_results[WIFI_COMMAND_RESULT_QUEUE_LENGTH];
static size_t mock_result_count;
static bool mock_result_queue_full;
static unsigned mock_write_count;
static bool mock_short_write;
static char mock_uart_line[64];

static int64_t esp_timer_get_time(void) { return (int64_t)(mock_now_ms * 1000U); }
static BaseType_t xSemaphoreTake(SemaphoreHandle_t semaphore, uint32_t wait)
{ (void)semaphore; (void)wait; return pdPASS; }
static BaseType_t xSemaphoreGive(SemaphoreHandle_t semaphore)
{ (void)semaphore; return pdPASS; }
static BaseType_t xQueueReceive(QueueHandle_t queue, void *item, uint32_t wait)
{
    CHECK(queue == s_wifi_command_queue && wait == 0U);
    if (!mock_request_present) return 0;
    memcpy(item, &mock_request, sizeof(mock_request));
    mock_request_present = false;
    return pdPASS;
}
static BaseType_t xQueueSend(QueueHandle_t queue, const void *item, uint32_t wait)
{
    CHECK(queue == s_wifi_command_result_queue && wait == 0U);
    if (mock_result_queue_full || mock_result_count >= WIFI_COMMAND_RESULT_QUEUE_LENGTH) return 0;
    memcpy(&mock_results[mock_result_count++], item, sizeof(wifi_command_result_t));
    return pdPASS;
}
static int uart_write_bytes(int port, const void *data, size_t length)
{
    CHECK(port == STM_UART_PORT && length < sizeof(mock_uart_line));
    memcpy(mock_uart_line, data, length);
    mock_uart_line[length] = '\0';
    ++mock_write_count;
    return mock_short_write ? (int)length - 1 : (int)length;
}

/* PRODUCTION_FUNCTIONS */

static void reset_fixture(void)
{
    memset(&s_wifi_uart_pending, 0, sizeof(s_wifi_uart_pending));
    memset(mock_results, 0, sizeof(mock_results));
    s_boot_id = 123U;
    s_wifi_command_owner_session_id = 0U;
    s_stm_startup = (stm_startup_t){ .state = STM_STARTUP_READY, .disarm_seq = 100U, .ping_seq = 101U };
    s_wifi_uart_next_seq = 100U;
    mock_now_ms = 1000U;
    mock_request_present = false;
    mock_result_count = 0U;
    mock_result_queue_full = false;
    mock_write_count = 0U;
    mock_short_write = false;
    mock_uart_line[0] = '\0';
}
static void enqueue(wifi_command_type_t type, uint32_t request_id, uint32_t session_id)
{
    CHECK(!mock_request_present);
    mock_request = (wifi_command_request_t){ .type = type, .request_id = request_id,
        .expected_boot_id = s_boot_id, .ws_session_id = session_id, .accepted_ms = mock_now_ms };
    mock_request_present = true;
    s_wifi_command_owner_session_id = session_id;
}
static void start(wifi_command_type_t type)
{
    reset_fixture();
    enqueue(type, 1U, 7U);
    wifi_command_step();
    CHECK(s_wifi_uart_pending.active && s_wifi_uart_pending.seq == 102U);
    CHECK(mock_write_count == 1U && mock_result_count == 0U);
    CHECK(strcmp(mock_uart_line, type == WIFI_COMMAND_PING ? "PING,seq=102\n" : "DISARM,seq=102\n") == 0);
}
static void result_is(size_t index, const char *status, uint32_t request_id, uint32_t session_id, uint32_t seq)
{
    CHECK(index < mock_result_count);
    CHECK(strcmp(mock_results[index].status, status) == 0);
    CHECK(mock_results[index].request.request_id == request_id);
    CHECK(mock_results[index].request.ws_session_id == session_id);
    CHECK(mock_results[index].request.expected_boot_id == 123U);
    CHECK(mock_results[index].seq == seq);
}

static void ping_before_deadline(void)
{
    start(WIFI_COMMAND_PING); mock_now_ms = 1499U;
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=4294967295"));
    CHECK(mock_result_count == 1U && !s_wifi_uart_pending.active);
    result_is(0U, "OK", 1U, 7U, 102U);
    CHECK(s_wifi_command_owner_session_id == 0U);
}
static void disarm_ack_before_deadline(void)
{
    start(WIFI_COMMAND_DISARM); mock_now_ms = 1499U;
    CHECK(wifi_command_handle_response("ACK,seq=102,type=DISARM,t_ms=42"));
    CHECK(mock_result_count == 1U && !s_wifi_uart_pending.active);
    result_is(0U, "OK", 1U, 7U, 102U);
}
static void wrong_and_startup_sequences(void)
{
    start(WIFI_COMMAND_PING);
    CHECK(wifi_command_handle_response("PONG,seq=101,t_ms=42"));
    CHECK(wifi_command_handle_response("PONG,seq=103,t_ms=42"));
    CHECK(mock_result_count == 0U && s_wifi_uart_pending.active);
    CHECK(s_wifi_uart_pending.seq == 102U);
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    result_is(0U, "OK", 1U, 7U, 102U);
}
static void wrong_response_kind_and_ack_type(void)
{
    start(WIFI_COMMAND_PING);
    CHECK(wifi_command_handle_response("ACK,seq=102,type=PING,t_ms=42"));
    CHECK(wifi_command_handle_response("ACK,seq=102,type=DISARM,t_ms=42"));
    CHECK(mock_result_count == 0U && s_wifi_uart_pending.active);
    start(WIFI_COMMAND_DISARM);
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(wifi_command_handle_response("ACK,seq=102,type=PING,t_ms=42"));
    CHECK(mock_result_count == 0U && s_wifi_uart_pending.active);
    CHECK(wifi_command_handle_response("ACK,seq=102,type=DISARM,t_ms=42"));
    result_is(0U, "OK", 1U, 7U, 102U);
}
static void matching_stm_error_is_failure(void)
{
    start(WIFI_COMMAND_PING);
    CHECK(wifi_command_handle_response("ERR,seq=102,type=PING,code=BAD_STATE,t_ms=42"));
    result_is(0U, "STM_ERROR", 1U, 7U, 102U);
    CHECK(!s_wifi_uart_pending.active);
}
static void nonmatching_error_is_ignored(void)
{
    start(WIFI_COMMAND_PING);
    CHECK(wifi_command_handle_response("ERR,seq=103,type=PING,code=BAD_STATE,t_ms=42"));
    CHECK(wifi_command_handle_response("ERR,seq=102,type=DISARM,code=BAD_STATE,t_ms=42"));
    CHECK(s_wifi_uart_pending.active && mock_result_count == 0U);
}
static void malformed_response_vectors(void)
{
    const char *lines[] = {
        "PONG,seq=102,t_ms=42,", "PONG,seq=102,,t_ms=42", "PONG,seq=102,seq=102",
        "PONG,seq=4294967296,t_ms=42", "PONG,seq=-1,t_ms=42", "PONG,seq=102,t_ms=42x",
        "PONG,seq=102,t_ms=42,extra=1", "PONG,seq=102,t_ms=", "ACK,seq=102,type=,t_ms=42",
        "ACK,seq=102,type=disarm,t_ms=42", "ACK,seq=102,type=DISARM,seq=102",
        "ERR,seq=102,type=PING,code=,t_ms=42", "ERR,seq=102,type=PING,t_ms=42"
    };
    for (size_t i = 0U; i < sizeof(lines) / sizeof(lines[0]); ++i) {
        start(WIFI_COMMAND_PING);
        CHECK(wifi_command_handle_response(lines[i]));
        CHECK(s_wifi_uart_pending.active && mock_result_count == 0U);
    }
}
static void no_pending_and_duplicate_responses(void)
{
    reset_fixture();
    CHECK(!wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(mock_result_count == 0U);
    start(WIFI_COMMAND_PING);
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(!wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(mock_result_count == 1U);
}
static void telemetry_is_not_a_command_response(void)
{
    start(WIFI_COMMAND_PING);
    CHECK(!wifi_command_handle_response("TEL,t_ms=42,state=FAULT"));
    CHECK(mock_result_count == 0U && s_wifi_uart_pending.active);
}
static void response_at_and_after_deadline(void)
{
    for (uint64_t delay = 500U; delay <= 501U; ++delay) {
        start(WIFI_COMMAND_PING); mock_now_ms += delay;
        CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
        CHECK(mock_result_count == 1U && !s_wifi_uart_pending.active);
        result_is(0U, "TIMEOUT", 1U, 7U, 102U);
    }
}
static void late_response_cannot_complete_next_request(void)
{
    start(WIFI_COMMAND_PING); mock_now_ms = 1500U;
    wifi_command_step(); result_is(0U, "TIMEOUT", 1U, 7U, 102U);
    mock_now_ms = 1501U; enqueue(WIFI_COMMAND_PING, 2U, 7U); wifi_command_step();
    CHECK(s_wifi_uart_pending.seq == 103U && mock_write_count == 2U);
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(mock_result_count == 1U && s_wifi_uart_pending.active);
    CHECK(wifi_command_handle_response("PONG,seq=103,t_ms=43"));
    result_is(1U, "OK", 2U, 7U, 103U);
}
static void closed_connection_has_no_result_delivery(void)
{
    start(WIFI_COMMAND_PING); s_wifi_command_owner_session_id = 0U;
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(!s_wifi_uart_pending.active && mock_result_count == 0U);
    CHECK(mock_write_count == 1U);
}
static void old_cleanup_preserves_new_owner(void)
{
    start(WIFI_COMMAND_PING); enqueue(WIFI_COMMAND_PING, 1U, 9U);
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(!s_wifi_uart_pending.active && mock_result_count == 0U);
    CHECK(s_wifi_command_owner_session_id == 9U && mock_request_present);
    wifi_command_step();
    CHECK(s_wifi_uart_pending.seq == 103U && mock_write_count == 2U);
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(mock_result_count == 0U && s_wifi_uart_pending.active);
    CHECK(wifi_command_handle_response("PONG,seq=103,t_ms=43"));
    result_is(0U, "OK", 1U, 9U, 103U);
}
static void orphaned_queued_request_is_not_transmitted(void)
{
    reset_fixture(); enqueue(WIFI_COMMAND_PING, 1U, 7U);
    s_wifi_command_owner_session_id = 0U; wifi_command_step();
    CHECK(mock_write_count == 0U && mock_result_count == 0U && !s_wifi_uart_pending.active);
}
static void expired_queue_request_is_not_transmitted(void)
{
    reset_fixture(); enqueue(WIFI_COMMAND_PING, 1U, 7U); mock_now_ms = 1500U;
    wifi_command_step();
    CHECK(mock_write_count == 0U && mock_result_count == 1U);
    result_is(0U, "QUEUE_EXPIRED", 1U, 7U, 102U);
}
static void startup_gate_and_failed_diagnostics(void)
{
    reset_fixture(); enqueue(WIFI_COMMAND_PING, 1U, 7U); s_stm_startup.state = STM_STARTUP_WAIT_PONG;
    wifi_command_step(); CHECK(mock_write_count == 0U && mock_request_present);
    s_stm_startup.state = STM_STARTUP_FAILED; wifi_command_step();
    CHECK(mock_write_count == 1U && s_wifi_uart_pending.active);
}
static void sequence_exhaustion_never_wraps(void)
{
    reset_fixture(); s_wifi_uart_next_seq = UINT32_MAX; enqueue(WIFI_COMMAND_PING, 1U, 7U);
    wifi_command_step(); CHECK(s_wifi_uart_pending.seq == UINT32_MAX);
    CHECK(wifi_command_handle_response("PONG,seq=4294967295,t_ms=42"));
    result_is(0U, "OK", 1U, 7U, UINT32_MAX);
    enqueue(WIFI_COMMAND_PING, 2U, 7U); wifi_command_step();
    result_is(1U, "SEQ_EXHAUSTED", 2U, 7U, 0U);
    CHECK(mock_write_count == 1U && s_wifi_uart_next_seq > UINT32_MAX);
}
static void full_result_queue_releases_request(void)
{
    start(WIFI_COMMAND_PING); mock_result_queue_full = true;
    CHECK(wifi_command_handle_response("PONG,seq=102,t_ms=42"));
    CHECK(mock_result_count == 0U && !s_wifi_uart_pending.active);
    CHECK(s_wifi_command_owner_session_id == 0U);
}
static void short_uart_write_has_no_retry(void)
{
    reset_fixture(); enqueue(WIFI_COMMAND_PING, 1U, 7U); mock_short_write = true;
    wifi_command_step(); result_is(0U, "TX_ERROR", 1U, 7U, 102U);
    for (unsigned i = 0U; i < 5U; ++i) wifi_command_step();
    CHECK(mock_write_count == 1U && !s_wifi_uart_pending.active);
}
static void wrong_boot_and_unsupported_command(void)
{
    reset_fixture(); enqueue(WIFI_COMMAND_PING, 1U, 7U); ++s_boot_id; wifi_command_step();
    result_is(0U, "BOOT_MISMATCH", 1U, 7U, 0U); CHECK(mock_write_count == 0U);
    reset_fixture(); enqueue((wifi_command_type_t)99, 1U, 7U); wifi_command_step();
    result_is(0U, "UNSUPPORTED", 1U, 7U, 0U); CHECK(mock_write_count == 0U);
}
static void websocket_request_parser_vectors(void)
{
    wifi_command_request_t request;
    CHECK(wifi_command_parse("PING,boot_id=0,request_id=1", 27U, &request));
    CHECK(request.type == WIFI_COMMAND_PING && request.expected_boot_id == 0U && request.request_id == 1U);
    const char *maximum = "DISARM,boot_id=4294967295,request_id=4294967295";
    CHECK(wifi_command_parse(maximum, strlen(maximum), &request));
    CHECK(request.type == WIFI_COMMAND_DISARM && request.expected_boot_id == UINT32_MAX && request.request_id == UINT32_MAX);
    const char *invalid[] = {
        "PING", "ARM,boot_id=123,request_id=1", "CMD,boot_id=123,request_id=1",
        "ESTOP_RESET,boot_id=123,request_id=1", "PING,request_id=1,boot_id=123",
        "PING,boot_id=123,request_id=0", "PING,boot_id=-1,request_id=1",
        "PING,boot_id=123,request_id=4294967296", "PING,boot_id=4294967296,request_id=1",
        "PING,boot_id=123,request_id=1,extra=1", "PING,boot_id=123,request_id=1,request_id=2",
        "PING,boot_id=123,request_id=1\n", "PING,boot_id=123,request_id= 1"
    };
    for (size_t i = 0U; i < sizeof(invalid) / sizeof(invalid[0]); ++i)
        CHECK(!wifi_command_parse(invalid[i], strlen(invalid[i]), &request));
    const char embedded[] = "PING,boot_id=123,request_id=1\0junk";
    CHECK(!wifi_command_parse(embedded, sizeof(embedded) - 1U, &request));
    char oversized[129]; memset(oversized, 'X', sizeof(oversized));
    CHECK(!wifi_command_parse(oversized, sizeof(oversized), &request));
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
#define RUN(name) if (strcmp(argv[1], #name) == 0) { name(); puts("PASS " #name); return 0; }
    RUN(ping_before_deadline)
    RUN(disarm_ack_before_deadline)
    RUN(wrong_and_startup_sequences)
    RUN(wrong_response_kind_and_ack_type)
    RUN(matching_stm_error_is_failure)
    RUN(nonmatching_error_is_ignored)
    RUN(malformed_response_vectors)
    RUN(no_pending_and_duplicate_responses)
    RUN(telemetry_is_not_a_command_response)
    RUN(response_at_and_after_deadline)
    RUN(late_response_cannot_complete_next_request)
    RUN(closed_connection_has_no_result_delivery)
    RUN(old_cleanup_preserves_new_owner)
    RUN(orphaned_queued_request_is_not_transmitted)
    RUN(expired_queue_request_is_not_transmitted)
    RUN(startup_gate_and_failed_diagnostics)
    RUN(sequence_exhaustion_never_wraps)
    RUN(full_result_queue_releases_request)
    RUN(short_uart_write_has_no_retry)
    RUN(wrong_boot_and_unsupported_command)
    RUN(websocket_request_parser_vectors)
#undef RUN
    fprintf(stderr, "Unknown scenario: %s\n", argv[1]);
    return 2;
}
