#ifndef WIFI_CONTROL_STATE_H
#define WIFI_CONTROL_STATE_H

#include "wifi_control_owner.h"

#define WIFI_CONTROL_QUEUE_MS 50U
#define WIFI_CONTROL_ACK_MS 150U
#define WIFI_CONTROL_FIRST_CMD_MS 250U
#define WIFI_CONTROL_SOURCE_MS 200U
#define WIFI_CONTROL_TEL_MS 250U
#define WIFI_CONTROL_STM_TIMEOUT_MS 300U
#define WIFI_CONTROL_STOP_SEND_MS 150U
#define WIFI_CONTROL_STOP_CONFIRM_MS 300U
#define WIFI_CONTROL_STM_CLOCK_SLOP_MS 250U

typedef enum {
    WIFI_CONTROL_IDLE,
    WIFI_CONTROL_ARM_PENDING,
    WIFI_CONTROL_ZERO_PENDING,
    WIFI_CONTROL_ACTIVE,
    WIFI_CONTROL_STOPPING,
    WIFI_CONTROL_BLOCKED
} wifi_control_phase_t;

typedef enum {
    WIFI_CONTROL_OP_NONE,
    WIFI_CONTROL_OP_ARM,
    WIFI_CONTROL_OP_CMD,
    WIFI_CONTROL_OP_DISARM
} wifi_control_op_t;

typedef enum {
    WIFI_CONTROL_REASON_NONE,
    WIFI_CONTROL_REASON_MANUAL_STOP,
    WIFI_CONTROL_REASON_OWNER_CLOSED,
    WIFI_CONTROL_REASON_INPUT_EXPIRED,
    WIFI_CONTROL_REASON_BAD_INPUT,
    WIFI_CONTROL_REASON_STARTUP,
    WIFI_CONTROL_REASON_TEL_STALE,
    WIFI_CONTROL_REASON_STM_FAULT,
    WIFI_CONTROL_REASON_STM_STATE,
    WIFI_CONTROL_REASON_STM_CLOCK,
    WIFI_CONTROL_REASON_CLOCK_BACKWARD,
    WIFI_CONTROL_REASON_ACK_TIMEOUT,
    WIFI_CONTROL_REASON_FIRST_CMD_TIMEOUT,
    WIFI_CONTROL_REASON_SOURCE_TIMEOUT,
    WIFI_CONTROL_REASON_STM_ERR,
    WIFI_CONTROL_REASON_TX_FAILED,
    WIFI_CONTROL_REASON_STOP_UNCONFIRMED
} wifi_control_reason_t;

typedef enum {
    WIFI_CONTROL_STM_DISARMED,
    WIFI_CONTROL_STM_ARMED,
    WIFI_CONTROL_STM_FAULT
} wifi_control_stm_state_t;

/* Validated TEL field. CPS is not an output-stop confirmation. */
typedef struct {
    wifi_control_stm_state_t state;
    uint32_t t_ms;
    uint32_t last_seq;
    uint32_t command_age_ms;
    int32_t vx_mmps;
    int32_t w_mradps;
    int32_t left_pwm;
    int32_t right_pwm;
} wifi_control_tel_t;

#define WIFI_CONTROL_ACTION_INVALIDATE_INPUTS 1U
#define WIFI_CONTROL_ACTION_SEND_DISARM 2U

/* One instance per ESP boot; one serialized caller, no internal locks. */
typedef struct {
    bool initialized;
    bool startup_ready;
    wifi_control_owner_t owner;
    wifi_control_phase_t phase;
    wifi_control_reason_t reason;
    wifi_control_op_t pending;
    uint32_t pending_seq;
    uint64_t last_now_ms;
    uint64_t pending_sent_ms;
    uint64_t arm_accepted_ms;
    uint64_t arm_expires_ms;
    uint64_t arm_sent_ms;
    uint64_t last_cmd_sent_ms;
    uint64_t stop_started_ms;
    uint64_t stop_ack_ms;
    bool arm_sent;
    bool have_cmd;
    bool zero_ack;
    bool stop_ack;
    bool need_disarm;
    uint32_t confirm_seq;
    uint64_t confirm_stm_ms;
    uint32_t confirm_tel_generation;
    bool have_tel;
    wifi_control_tel_t tel;
    uint64_t tel_received_ms;
    uint64_t tel_generation;
    uint64_t stm_progress_ms;
} wifi_control_state_t;

void wifi_control_state_init(wifi_control_state_t *state, uint32_t boot_id);

/* Parser/ticket/request-id checks precede admission. out changes on success only. */
bool wifi_control_state_begin_arm(
    wifi_control_state_t *state, const wifi_control_request_t *request,
    bool startup_ready, bool uart_idle, uint64_t now_ms,
    uint32_t *out_control_id);

/* Immediately before TX; caller also checks live connection/ticket queue data. */
bool wifi_control_state_arm_sent(
    wifi_control_state_t *state, uint32_t ws_session_id,
    uint32_t control_id, uint32_t seq, uint64_t now_ms);
bool wifi_control_state_cmd_sent(
    wifi_control_state_t *state, const wifi_control_request_t *request,
    uint32_t seq, uint64_t now_ms);
bool wifi_control_state_disarm_sent(
    wifi_control_state_t *state, uint32_t seq, uint64_t now_ms);

/* Use receive time, never a browser timestamp. reply t_ms comes from STM. */
bool wifi_control_state_reply(
    wifi_control_state_t *state, wifi_control_op_t op,
    uint32_t seq, bool ok, uint32_t stm_t_ms, uint64_t now_ms);
void wifi_control_state_tel(
    wifi_control_state_t *state, const wifi_control_tel_t *tel,
    uint64_t now_ms);
void wifi_control_state_poll(
    wifi_control_state_t *state, bool startup_ready, uint64_t now_ms);
void wifi_control_state_stop(
    wifi_control_state_t *state, wifi_control_reason_t reason,
    uint64_t now_ms);
void wifi_control_state_owner_closed(
    wifi_control_state_t *state, uint32_t ws_session_id, uint64_t now_ms);
void wifi_control_state_tx_failed(wifi_control_state_t *state, uint64_t now_ms);

/* Level flags: revoke inputs first, then dispatch one DISARM. No automatic retry. */
uint32_t wifi_control_state_actions(const wifi_control_state_t *state);

#endif