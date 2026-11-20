#ifndef WIFI_CONTROL_EXECUTOR_H
#define WIFI_CONTROL_EXECUTOR_H

#include "wifi_control_state.h"
#include "wifi_control_ticket.h"

#define WIFI_CONTROL_UART_FRAME_SIZE 96U

typedef enum {
    WIFI_EXEC_ACCEPTED,
    WIFI_EXEC_BAD_INPUT,
    WIFI_EXEC_BOOT_MISMATCH,
    WIFI_EXEC_TICKET_REJECTED,
    WIFI_EXEC_NOT_READY,
    WIFI_EXEC_BUSY,
    WIFI_EXEC_OUTPUT_PENDING
} wifi_control_submit_status_t;

typedef struct {
    wifi_control_op_t op;
    uint32_t seq;
    char bytes[WIFI_CONTROL_UART_FRAME_SIZE];
    size_t length;
} wifi_control_tx_t;

typedef struct {
    wifi_control_request_t request;
    uint32_t seq;
    bool has_seq; /* Assigned UART seq, including valid zero; not physical TX proof. */
    const char *status; /* Static string; no allocation or borrowed input pointer. */
} wifi_control_executor_result_t;

/* One serialized caller. HTTP/FreeRTOS/network synchronization is external. */
typedef struct {
    wifi_control_state_t state;
    wifi_control_phase_t observed_phase;
    wifi_control_request_t request;
    bool queued;
    bool waiting;
    bool prepared;
    bool inputs_cleared;
    bool need_line_sync;
    wifi_control_op_t prepared_op;
    uint32_t prepared_seq;
    size_t prepared_length;
    uint32_t request_seq;
    bool have_result;
    wifi_control_executor_result_t result;
} wifi_control_executor_t;

void wifi_control_executor_init(wifi_control_executor_t *executor, uint32_t boot_id);

/* request-id ordering, rate limit and real session liveness precede this call. */
wifi_control_submit_status_t wifi_control_executor_submit(
    wifi_control_executor_t *executor, const wifi_control_request_t *request,
    wifi_control_ticket_t *ticket, bool startup_ready, bool uart_idle,
    uint64_t now_ms);

/* Outer actor purges all tickets and unsent ingress work before acknowledging. */
bool wifi_control_executor_needs_invalidation(const wifi_control_executor_t *executor);
void wifi_control_executor_inputs_cleared(wifi_control_executor_t *executor);

/* seq is allocated by the SAME UART owner used for startup/W5. Never reuse it. */
bool wifi_control_executor_take_tx(
    wifi_control_executor_t *executor, uint32_t seq, uint64_t now_ms,
    wifi_control_tx_t *out);
/* Write immediately, then report exact uart_write_bytes return before RX/next TX. */
bool wifi_control_executor_tx_complete(
    wifi_control_executor_t *executor, int written, uint64_t now_ms);

bool wifi_control_executor_reply(
    wifi_control_executor_t *executor, wifi_control_op_t op,
    uint32_t seq, bool ok, uint32_t stm_t_ms, uint64_t now_ms);
void wifi_control_executor_tel(
    wifi_control_executor_t *executor, const wifi_control_tel_t *tel,
    uint64_t now_ms);
void wifi_control_executor_poll(
    wifi_control_executor_t *executor, bool startup_ready, uint64_t now_ms);
void wifi_control_executor_stop(
    wifi_control_executor_t *executor, wifi_control_reason_t reason,
    uint64_t now_ms);
void wifi_control_executor_owner_closed(
    wifi_control_executor_t *executor, uint32_t ws_session_id, uint64_t now_ms);
bool wifi_control_executor_take_result(
    wifi_control_executor_t *executor, wifi_control_executor_result_t *out);
bool wifi_control_executor_allows_ping(const wifi_control_executor_t *executor);

#endif
