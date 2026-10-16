#include "uart_mvp_protocol.h"

#include "drive_command_mapper.h"
#include "motor_output.h"
#include "ring_buffer.h"
#include "uart_frame_parser.h"

#include <stdarg.h>
#include <stdio.h>

#define CMD_TIMEOUT_DEFAULT_MS 300u
#define CMD_TIMEOUT_MIN_MS      50u
#define CMD_TIMEOUT_MAX_MS     500u

#define VX_MIN_MMPS  -100
#define VX_MAX_MMPS   100
#define W_MIN_MRADPS -500
#define W_MAX_MRADPS  500

/*
 * 100 permille = 10% initial production output cap.
 * Keep provisional until lifted motor verification.
 */
#define CMD_OUTPUT_DUTY_CAP_PERMILLE    100U
#define UART_FRAME_MAX_LEN              127u
#define UART_LINE_BUFFER_SIZE           (UART_FRAME_MAX_LEN + 2u)
#define UART_TX_BUFFER_SIZE             384u
#define TEL_PERIOD_MS                   100u
#define COMMAND_AGE_INVALID_MS          0xFFFFFFFFu

#define UART_MVP_OUTPUT_TEST_ENABLED                        0U
#define UART_MVP_OUTPUT_TEST_DUTY_PERMILLE                  100U
#define UART_MVP_STALE_DISARM_ACK_ONCE_TEST_ENABLED         0U
#define UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED    0U
#define UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED 0U
#define UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED  0U
#define UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_EMBEDDED_CR_DISARM_ACK_ONCE_TEST_ENABLED   0U
#define UART_MVP_CONTROL_BYTE_DISARM_ACK_ONCE_TEST_ENABLED  0U
#define UART_MVP_OVERLONG_DISARM_ACK_ONCE_TEST_ENABLED  0U
#define UART_MVP_STALE_PONG_ONCE_TEST_ENABLED           0U
#define UART_MVP_SUPPRESS_PONG_TEST_ENABLED             0U

/* Bench only: stop immediately; delay one eligible DISARM ACK. */
#define UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_DELAY_DISARM_ACK_MS             500U

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED > 1U
#error "Delayed DISARM ACK test mode must be 0 or 1"
#endif
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED && ( \
    UART_MVP_OUTPUT_TEST_ENABLED || \
    UART_MVP_STALE_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED || \
    UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED || \
    UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED || \
    UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_EMBEDDED_CR_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_CONTROL_BYTE_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_OVERLONG_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_STALE_PONG_ONCE_TEST_ENABLED || UART_MVP_SUPPRESS_PONG_TEST_ENABLED)
#error "Do not combine delayed ACK with another bench fault/output mode"
#endif

/* Bench only: omit the tenth eligible zero CMD ACK once per STM boot. */
#define UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED 0U

#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED > 1U
#error "CMD ACK drop test mode must be 0 or 1"
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED && ( \
    UART_MVP_OUTPUT_TEST_ENABLED || \
    UART_MVP_STALE_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED || \
    UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED || \
    UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED || \
    UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_EMBEDDED_CR_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_CONTROL_BYTE_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_OVERLONG_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_STALE_PONG_ONCE_TEST_ENABLED || \
    UART_MVP_SUPPRESS_PONG_TEST_ENABLED || \
    UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED)
#error "Do not combine CMD ACK drop with another bench fault/output mode"
#endif

typedef enum{
    ROBOT_DISARMED = 0,
    ROBOT_ARMED,
    ROBOT_FAULT
} robot_state_t;

typedef enum {
    ROBOT_REASON_BOOT = 0,
    ROBOT_REASON_NONE,
    ROBOT_REASON_DISARM,
    ROBOT_REASON_CMD_TIMEOUT,
    ROBOT_REASON_ESTOP_ACTIVE,
    ROBOT_REASON_ESTOP_LATCHED,
    ROBOT_REASON_ESTOP_RESET,
    ROBOT_REASON_OUTPUT_ERROR
} robot_reason_t;

static UART_HandleTypeDef *s_uart;
static uint8_t s_rx_byte;
static ring_buffer_t s_rx_rb;

static char s_line[UART_LINE_BUFFER_SIZE];
static uint16_t s_line_len;
static uint8_t s_line_overflow;
static volatile uint8_t s_rx_desync_pending;
typedef enum {
    UART_RX_COLLECT = 0,
    UART_RX_DISCARD_ERROR,
    UART_RX_DISCARD_CANCEL
} uart_rx_line_mode_t;

static uart_rx_line_mode_t s_rx_line_mode;

static robot_reason_t s_reason = ROBOT_REASON_BOOT;
static uint8_t s_has_accepted_cmd;
static uint32_t s_last_accepted_cmd_ms;
static robot_state_t s_state = ROBOT_DISARMED;
static uint8_t s_estop_latched;
static uint32_t s_last_seq;
static uint8_t s_stale_disarm_ack_sent;
static uint8_t s_duplicate_disarm_ack_seq_sent;
static uint8_t s_trailing_comma_disarm_ack_sent;
static uint8_t s_overflow_disarm_ack_seq_sent;
static uint8_t s_partial_frame_name_disarm_ack_sent;
static uint8_t s_wrong_disarm_ack_type_sent;
static uint8_t s_embedded_cr_disarm_ack_sent;
static uint8_t s_control_byte_disarm_ack_sent;
static uint8_t s_overlong_disarm_ack_sent;
static uint8_t s_stale_pong_sent;
static int32_t s_vx_mmps;
static int32_t s_w_mradps;
static uint32_t s_cmd_timeout_ms;
static uint32_t s_last_cmd_ms;
static uint32_t s_last_tel_ms;
static uint32_t s_error_count;
static int32_t s_left_cps;
static int32_t s_right_cps;

#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
static uint8_t s_cmd_ack_drop_used;
static uint8_t s_cmd_ack_drop_zero_count;
#endif

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
typedef struct {
    uint8_t used;
    uint8_t pending;
    uint8_t zero_cmd_seen;
    uint32_t seq;
    uint32_t processed_ms;
} delayed_disarm_ack_t;

static delayed_disarm_ack_t s_delayed_disarm_ack;
#endif

static const char *state_name(robot_state_t state){
    switch (state){
        case ROBOT_ARMED:
            return "ARMED";

        case ROBOT_FAULT:
            return "FAULT";
        case ROBOT_DISARMED:
        default:
            return "DISARMED";
    }
}

static const char *reason_name(robot_reason_t reason){
    switch (reason){
        case ROBOT_REASON_BOOT:
            return "BOOT";
        case ROBOT_REASON_NONE:
            return "NONE";
        case ROBOT_REASON_DISARM:
            return "DISARM";
        case ROBOT_REASON_CMD_TIMEOUT:
            return "CMD_TIMEOUT";
        case ROBOT_REASON_ESTOP_ACTIVE:
            return "ESTOP_ACTIVE";
        case ROBOT_REASON_ESTOP_LATCHED:
            return "ESTOP_LATCHED";
        case ROBOT_REASON_ESTOP_RESET:
            return "ESTOP_RESET";
        case ROBOT_REASON_OUTPUT_ERROR:
            return "OUTPUT_ERROR";
        default:
            return "UNKNOWN";
    }
}

static uint32_t command_age_ms(uint32_t now_ms){
    if(s_has_accepted_cmd == 0U){
        return COMMAND_AGE_INVALID_MS;
    }

    return now_ms - s_last_accepted_cmd_ms;
}

static void uart_sendf(const char *fmt, ...){
    char tx[UART_TX_BUFFER_SIZE];
    va_list args;
    int len;

    if(s_uart == NULL){
        return;
    }

    va_start(args, fmt);
    len = vsnprintf(tx, sizeof(tx), fmt, args);
    va_end(args);

    if(len <= 0){
        return;
    }

    if((size_t)len >= sizeof(tx)){
        len = (int)sizeof(tx) - 1;
    }

    HAL_UART_Transmit(s_uart, (uint8_t *)tx, (uint16_t)len, 100);
}

static void send_ack(uint32_t seq, const char *type){
    uart_sendf("ACK,seq=%lu,type=%s,t_ms=%lu\n",
                (unsigned long)seq,
                type,
                (unsigned long)HAL_GetTick());
}

static void send_err(uint32_t seq, const char *type, const char *code){
    s_error_count++;

    uart_sendf("ERR,seq=%lu,type=%s,code=%s,t_ms=%lu\n",
                (unsigned long)seq,
                type,
                code,
                (unsigned long)HAL_GetTick());
}

static void send_tel(void){
    uint32_t now_ms = HAL_GetTick();
    motor_output_applied_t applied =
        motor_output_get_applied();

    uart_sendf("TEL,t_ms=%lu,state=%s,reason=%s,"
               "command_age_ms=%lu,last_seq=%lu,"
               "vx_mmps=%ld,w_mradps=%ld,"
               "left_pwm=%ld,right_pwm=%ld,"
               "left_cps=%ld,right_cps=%ld,"
               "batt_mv=0,drop=%lu,err=%lu\n",
                (unsigned long)now_ms,
                state_name(s_state),
                reason_name(s_reason),
                (unsigned long)command_age_ms(now_ms),
                (unsigned long)s_last_seq,
                (long)s_vx_mmps,
                (long)s_w_mradps,
                (long)applied.left_signed_permille,
                (long)applied.right_signed_permille,
                (long)s_left_cps,
                (long)s_right_cps,
                (unsigned long)ring_buffer_dropped(&s_rx_rb),
                (unsigned long)s_error_count);
}

static const char *parse_error_code(uart_frame_parse_result_t result){
    switch(result){
        case UART_FRAME_PARSE_MISSING_SEQ:
        case UART_FRAME_PARSE_INVALID_SEQ:
            return "MISSING_SEQ";

        case UART_FRAME_PARSE_MISSING_FIELD:
        case UART_FRAME_PARSE_BAD_FIELD_ORDER:
        case UART_FRAME_PARSE_INVALID_NUMBER:
        case UART_FRAME_PARSE_EXTRA_DATA:
            return "MISSING_FIELD";

        case UART_FRAME_PARSE_VELOCITY_OUT_OF_RANGE:
            return "OUT_OF_RANGE";

        case UART_FRAME_PARSE_TIMEOUT_OUT_OF_RANGE:
            return "TIMEOUT_OUT_OF_RANGE";

        case UART_FRAME_PARSE_NULL_ARGUMENT:
        case UART_FRAME_PARSE_EMPTY:
        case UART_FRAME_PARSE_BAD_TYPE:
        case UART_FRAME_PARSE_OK:
        default:
            return "BAD_TYPE";
    }
}

static void begin_rx_resynchronization(void){
    uint32_t primask = __get_PRIMASK();

    __disable_irq();
    s_rx_desync_pending = 0u;
    ring_buffer_discard_all(&s_rx_rb);
    __set_PRIMASK(primask);

    s_line_len = 0u;
    s_line_overflow = 0u;
    s_rx_line_mode = UART_RX_DISCARD_ERROR;
}

static uint8_t estop_input_active(void) {
    return (HAL_GPIO_ReadPin(
        ESTOP_SENSE_GPIO_Port,
        ESTOP_SENSE_Pin
        ) == GPIO_PIN_SET) ? 1U : 0U;
}

static void estop_latch_and_force_safe(void) {
    uint8_t input_active = estop_input_active();

    motor_output_stop_all();
    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_estop_latched = 1U;
    s_state = ROBOT_FAULT;
    s_reason = (input_active != 0U)
        ? ROBOT_REASON_ESTOP_ACTIVE
        : ROBOT_REASON_ESTOP_LATCHED;
}

static uint8_t estop_enforce_latch(void) {
    if ((estop_input_active() != 0U) ||
        (s_estop_latched != 0U)) {
        estop_latch_and_force_safe();
        return 1U;
    }

    return 0U;
}

static void command_timeout_enforce(void) {
    if(s_state != ROBOT_ARMED){
        return;
    }

    if((HAL_GetTick() - s_last_cmd_ms) < s_cmd_timeout_ms){
        return;
    }

    motor_output_stop_all();
    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_state = ROBOT_DISARMED;
    s_reason = ROBOT_REASON_CMD_TIMEOUT;
}

#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
static uint8_t drop_cmd_ack_once(uint32_t seq)
{
    const motor_output_applied_t applied = motor_output_get_applied();
    if (s_cmd_ack_drop_used != 0U) {
        return 0U;
    }
    if (s_state != ROBOT_ARMED || s_estop_latched != 0U ||
        estop_input_active() != 0U || s_vx_mmps != 0 || s_w_mradps != 0 ||
        applied.left_signed_permille != 0 || applied.right_signed_permille != 0 ||
        s_left_cps != 0 || s_right_cps != 0) {
        s_cmd_ack_drop_zero_count = 0U;
        return 0U;
    }
    if (++s_cmd_ack_drop_zero_count < 10U) {
        return 0U;
    }
    s_cmd_ack_drop_used = 1U;
    uart_sendf("TEST_CMD_ACK_DROP,seq=%lu,t_ms=%lu,zero_count=%lu\n",
        (unsigned long)seq,
        (unsigned long)HAL_GetTick(),
        (unsigned long)s_cmd_ack_drop_zero_count);
    return 1U;
}
#endif

static void handle_cmd(const uart_frame_t *frame){
    drive_command_request_t request;
    if(frame->vx_mmps < VX_MIN_MMPS || frame->vx_mmps > VX_MAX_MMPS ||
       frame->w_mradps < W_MIN_MRADPS || frame->w_mradps > W_MAX_MRADPS){
        send_err(frame->seq, "CMD", "OUT_OF_RANGE");
        return;
    }

    if(frame->timeout_ms < CMD_TIMEOUT_MIN_MS ||
       frame->timeout_ms > CMD_TIMEOUT_MAX_MS){
        send_err(frame->seq, "CMD", "TIMEOUT_OUT_OF_RANGE");
        return;
    }

    if(s_state != ROBOT_ARMED){
        send_err(frame->seq, "CMD", "NOT_ARMED");
        return;
    }

    if (estop_enforce_latch() != 0U) {
        send_err(frame->seq, "CMD", "ESTOP_LATCHED");
        return;
    }

    if(!drive_command_map(
        frame->vx_mmps,
        frame->w_mradps,
        CMD_OUTPUT_DUTY_CAP_PERMILLE,
        &request
    )){
        motor_output_stop_all();
        s_vx_mmps = 0;
        s_w_mradps = 0;
        s_reason = ROBOT_REASON_OUTPUT_ERROR;
        send_err(frame->seq, "CMD", "MAPPER_FAILED");
        return;
    }

    if (estop_enforce_latch() != 0U) {
        send_err(frame->seq, "CMD", "ESTOP_LATCHED");
        return;
    }

    if(UART_MVP_OUTPUT_TEST_ENABLED != 0U){
        if((frame->vx_mmps == 50) && (frame->w_mradps == 0)){
            if(motor_output_set_raw(
                UART_MVP_OUTPUT_TEST_DUTY_PERMILLE,
                GPIO_PIN_RESET,
                UART_MVP_OUTPUT_TEST_DUTY_PERMILLE,
                GPIO_PIN_RESET
            ) != HAL_OK){
                motor_output_stop_all();
                s_vx_mmps = 0;
                s_w_mradps = 0;
                s_reason = ROBOT_REASON_OUTPUT_ERROR;
                send_err(frame->seq, "CMD", "MOTOR_OUTPUT_FAILED");
                return;
            }
        }
        else{
            motor_output_stop_all();
        }
    }
    else if(motor_output_set_signed(
        request.left_signed_permille,
        request.right_signed_permille
    ) != HAL_OK){
        motor_output_stop_all();
        s_vx_mmps = 0;
        s_w_mradps = 0;
        s_reason = ROBOT_REASON_OUTPUT_ERROR;
        send_err(frame->seq, "CMD", "MOTOR_OUTPUT_FAILED");
        return;
    }

    if (estop_enforce_latch() != 0U) {
        send_err(frame->seq, "CMD", "ESTOP_LATCHED");
        return;
    }
    s_last_seq = frame->seq;
    s_vx_mmps = frame->vx_mmps;
    s_w_mradps = frame->w_mradps;
    s_cmd_timeout_ms = frame->timeout_ms;
    s_last_cmd_ms = HAL_GetTick();
    s_last_accepted_cmd_ms = s_last_cmd_ms;
    s_has_accepted_cmd = 1U;
    s_reason = ROBOT_REASON_NONE;

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    s_delayed_disarm_ack.zero_cmd_seen =
        (uint8_t)(s_vx_mmps == 0 && s_w_mradps == 0);
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    if (drop_cmd_ack_once(frame->seq) != 0U) {
        return;
    }
#endif
    send_ack(frame->seq, "CMD");
}

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
static uint8_t delayed_disarm_ack_eligible(void)
{
    const motor_output_applied_t applied = motor_output_get_applied();
    return (uint8_t)(s_delayed_disarm_ack.used == 0U &&
        s_delayed_disarm_ack.zero_cmd_seen != 0U &&
        s_state == ROBOT_ARMED && s_estop_latched == 0U &&
        estop_input_active() == 0U && s_vx_mmps == 0 && s_w_mradps == 0 &&
        applied.left_signed_permille == 0 && applied.right_signed_permille == 0 &&
        s_left_cps == 0 && s_right_cps == 0);
}

static void delayed_disarm_ack_schedule(uint32_t seq)
{
    s_delayed_disarm_ack.used = 1U;
    s_delayed_disarm_ack.pending = 1U;
    s_delayed_disarm_ack.seq = seq;
    s_delayed_disarm_ack.processed_ms = HAL_GetTick();
    uart_sendf("TEST_ACK_DELAY,seq=%lu,t_ms=%lu,delay_ms=%lu\n",
        (unsigned long)seq,
        (unsigned long)s_delayed_disarm_ack.processed_ms,
        (unsigned long)UART_MVP_DELAY_DISARM_ACK_MS);
}

static void delayed_disarm_ack_poll(void)
{
    if (s_delayed_disarm_ack.pending == 0U ||
        (uint32_t)(HAL_GetTick() - s_delayed_disarm_ack.processed_ms) <
            UART_MVP_DELAY_DISARM_ACK_MS) {
        return;
    }
    s_delayed_disarm_ack.pending = 0U;
    /* Original processing time: this is an old response, not a new stop. */
    uart_sendf("ACK,seq=%lu,type=DISARM,t_ms=%lu\n",
        (unsigned long)s_delayed_disarm_ack.seq,
        (unsigned long)s_delayed_disarm_ack.processed_ms);
}
#endif

static void handle_line(const char *line, size_t line_len){
    uart_frame_t frame;
    uart_frame_parse_result_t parse_result;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    uint8_t delay_disarm_ack;
#endif


    parse_result = uart_frame_parse(line, line_len, &frame);
    if(parse_result != UART_FRAME_PARSE_OK){
        send_err(
            frame.seq,
            uart_frame_type_name(frame.type),
            parse_error_code(parse_result)
        );
        return;
    }

    if(((frame.type == UART_FRAME_TYPE_ARM) ||
        (frame.type == UART_FRAME_TYPE_CMD)) &&
       (estop_enforce_latch() != 0U)) {
        send_err(
            frame.seq,
            uart_frame_type_name(frame.type),
            "ESTOP_LATCHED"
        );
        return;
       }

    switch(frame.type){
        case UART_FRAME_TYPE_PING:
            s_last_seq = frame.seq;

#if UART_MVP_SUPPRESS_PONG_TEST_ENABLED
            return;
#endif

#if UART_MVP_STALE_PONG_ONCE_TEST_ENABLED
            if(s_stale_pong_sent == 0u){
                s_stale_pong_sent = 1u;
                uart_sendf("PONG,seq=%lu,t_ms=%lu\n",
                        (unsigned long)(frame.seq - 1u),
                        (unsigned long)HAL_GetTick());
                return;
            }
#endif

            uart_sendf("PONG,seq=%lu,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick());
            return;

        case UART_FRAME_TYPE_DISARM:
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            delay_disarm_ack = delayed_disarm_ack_eligible();
            s_delayed_disarm_ack.zero_cmd_seen = 0U;
#endif
            motor_output_stop_all();
            s_vx_mmps = 0;
            s_w_mradps = 0;
            if (estop_enforce_latch() == 0U) {
                s_state = ROBOT_DISARMED;
                s_reason = ROBOT_REASON_DISARM;
            }
            s_last_seq = frame.seq;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            if (delay_disarm_ack != 0U && s_state == ROBOT_DISARMED) {
                delayed_disarm_ack_schedule(frame.seq);
                return;
            }
#endif

#if UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED
            if(s_duplicate_disarm_ack_seq_sent == 0u){
                s_duplicate_disarm_ack_seq_sent = 1u;
                uart_sendf(
                    "ACK,seq=%lu,seq=%lu,type=DISARM,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_trailing_comma_disarm_ack_sent == 0u){
                s_trailing_comma_disarm_ack_sent = 1u;
                uart_sendf(
                    "ACK,seq=%lu,type=DISARM,t_ms=%lu,\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED
            if(s_overflow_disarm_ack_seq_sent == 0u){
                s_overflow_disarm_ack_seq_sent = 1u;
                uart_sendf(
                    "ACK,seq=4294967296,type=DISARM,t_ms=%lu\n",
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_partial_frame_name_disarm_ack_sent == 0U){
                s_partial_frame_name_disarm_ack_sent = 1U;
                uart_sendf(
                    "AC,seq=%lu,type=DISARM,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_EMBEDDED_CR_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_embedded_cr_disarm_ack_sent == 0u){
                s_embedded_cr_disarm_ack_sent = 1u;
                uart_sendf(
                    "ACK,seq=%lu,\rtype=DISARM,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_CONTROL_BYTE_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_control_byte_disarm_ack_sent == 0u){
                s_control_byte_disarm_ack_sent = 1u;
                uart_sendf(
                    "ACK,seq=%lu," "\x01" "type=DISARM,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_OVERLONG_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_overlong_disarm_ack_sent == 0u){
                uint8_t overlong_tail[257u];
                size_t i;

                s_overlong_disarm_ack_sent = 1u;

                uart_sendf(
                    "ACK,seq=%lu,type=DISARM,t_ms=%lu,",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );

                for(i = 0U; i < 256U; i++){
                    overlong_tail[i] = (uint8_t)'X';
                }

                overlong_tail[256U] = (uint8_t)'\n';

                (void)HAL_UART_Transmit(
                    s_uart,
                    overlong_tail,
                    (uint16_t)sizeof(overlong_tail),
                    100
                );
                return;
            }
#endif
#if UART_MVP_STALE_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_stale_disarm_ack_sent == 0u){
                s_stale_disarm_ack_sent = 1u;
                send_ack(frame.seq - 1u, "DISARM");
                return;
            }
#endif
#if UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED
            if(s_wrong_disarm_ack_type_sent == 0u){
                s_wrong_disarm_ack_type_sent = 1u;
                send_ack(frame.seq, "ARM");
                return;
            }
#endif
            send_ack(frame.seq, "DISARM");
            return;

        case UART_FRAME_TYPE_ARM:
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            s_delayed_disarm_ack.zero_cmd_seen = 0U;
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
            s_cmd_ack_drop_zero_count = 0U;
#endif
            motor_output_stop_all();

            s_vx_mmps = 0;
            s_w_mradps = 0;
            s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
            s_last_cmd_ms = HAL_GetTick();
            s_state = ROBOT_ARMED;
            s_reason = ROBOT_REASON_NONE;
            s_last_seq = frame.seq;
            send_ack(frame.seq, "ARM");
            return;


        case UART_FRAME_TYPE_ESTOP_RESET:
            motor_output_stop_all();
            s_vx_mmps = 0;
            s_w_mradps = 0;

            if (estop_input_active() != 0U) {
                estop_latch_and_force_safe();
                send_err(
                    frame.seq,
                    "ESTOP_RESET",
                    "ESTOP_ACTIVE"
                );
                return;
            }

            s_estop_latched = 0U;
            s_state = ROBOT_DISARMED;
            s_reason = ROBOT_REASON_ESTOP_RESET;
            s_last_seq = frame.seq;
            send_ack(frame.seq, "ESTOP_RESET");
            return;

        case UART_FRAME_TYPE_CMD:
            handle_cmd(&frame);
            return;

        case UART_FRAME_TYPE_UNKNOWN:
        default:
            send_err(0u, "UNKNOWN", "BAD_TYPE");
            return;
    }
}

void uart_mvp_init(UART_HandleTypeDef *huart){
    s_uart = huart;
    s_rx_byte = 0u;

    ring_buffer_init(&s_rx_rb);

    s_line_len = 0u;
    s_line_overflow = 0u;
    s_rx_desync_pending = 0u;
    s_rx_line_mode = UART_RX_COLLECT;

    s_state = ROBOT_DISARMED;
    s_reason = ROBOT_REASON_BOOT;
    s_has_accepted_cmd = 0U;
    s_last_accepted_cmd_ms = 0U;
    s_estop_latched = 0U;
    s_last_seq = 0;
    s_stale_disarm_ack_sent = 0u;
    s_duplicate_disarm_ack_seq_sent = 0u;
    s_trailing_comma_disarm_ack_sent = 0u;
    s_overflow_disarm_ack_seq_sent = 0u;
    s_partial_frame_name_disarm_ack_sent = 0u;
    s_embedded_cr_disarm_ack_sent = 0u;
    s_control_byte_disarm_ack_sent = 0u;
    s_overlong_disarm_ack_sent = 0u;
    s_wrong_disarm_ack_type_sent = 0u;
    s_stale_pong_sent = 0u;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    s_delayed_disarm_ack = (delayed_disarm_ack_t){0};
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    s_cmd_ack_drop_used = 0U;
    s_cmd_ack_drop_zero_count = 0U;
#endif
    s_last_tel_ms = 0u;
    s_error_count = 0u;
    s_left_cps = 0;
    s_right_cps = 0;

    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
    s_last_cmd_ms = 0u;
    (void)estop_enforce_latch();
}

void uart_mvp_set_encoder_cps(
    int32_t left_cps,
    int32_t right_cps
){
    s_left_cps = left_cps;
    s_right_cps = right_cps;
}

void uart_mvp_start_rx(void){
    if(s_uart == NULL){
        return;
    }

    HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
}

void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart){
    if(huart != s_uart){
        return;
    }
    if(!ring_buffer_push(&s_rx_rb, s_rx_byte)){
        s_error_count++;
        s_rx_desync_pending = 1u;
    }
    HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
}

void uart_mvp_on_uart_error(UART_HandleTypeDef *huart){
    if(huart != s_uart){
        return;
    }

    s_error_count++;
    s_rx_desync_pending = 1u;

    HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
}

void uart_mvp_process(void){
    uint8_t byte;

    for(;;){
        (void)estop_enforce_latch();
        command_timeout_enforce();

        if(s_rx_desync_pending != 0u){
            begin_rx_resynchronization();
        }

        if(!ring_buffer_pop(&s_rx_rb, &byte)){
            break;
        }

        if(s_rx_desync_pending != 0u){
            begin_rx_resynchronization();
            continue;
        }

        /* CAN (0x18) cancels a pending line without executing it. 
         * Keep discarding through LF; preserve a prior hardware-error report. 
         * This changes framing only. DISARM below still owns the stop/ACK. 
         */
        if(byte == 0x18u){
            s_line_len = 0u;
            s_line_overflow = 0u;
            if(s_rx_line_mode == UART_RX_COLLECT){
                s_rx_line_mode = UART_RX_DISCARD_CANCEL;
            }
            continue;
        }

        if(s_rx_line_mode != UART_RX_COLLECT){
            if(byte == '\n'){
                if(s_rx_line_mode == UART_RX_DISCARD_ERROR){
                    uart_sendf("ERR,seq=0,type=RX,code=RX_DESYNC\n");
                }
                s_rx_line_mode = UART_RX_COLLECT;
            }
            continue;
        }

        if(byte == '\n'){
            if(s_line_len > 0u && s_line[s_line_len - 1u] == '\r'){
                s_line_len--;
            }
            if(s_line_len > UART_FRAME_MAX_LEN){
                s_line_overflow = 1u;
            }
            s_line[s_line_len] = '\0';

            if(s_line_overflow){
                s_error_count++;
                uart_sendf("ERR,seq=0,type=RX,code=LINE_OVERFLOW\n");
            }
            else if(s_line_len > 0u){
                handle_line(s_line, (size_t)s_line_len);
            }

            s_line_len = 0u;
            s_line_overflow = 0u;
            continue;
        }

        if(s_line_len < (UART_LINE_BUFFER_SIZE - 1u)){
            s_line[s_line_len] = (char)byte;
            s_line_len++;
        }
        else{
            s_line_overflow = 1u;
        }
    }

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    delayed_disarm_ack_poll();
#endif

    if((HAL_GetTick() - s_last_tel_ms) >= TEL_PERIOD_MS){
        s_last_tel_ms = HAL_GetTick();
        send_tel();
    }
}
