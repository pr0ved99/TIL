#include "uart_mvp_protocol.h"

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

#define UART_FRAME_MAX_LEN    127u
#define UART_LINE_BUFFER_SIZE (UART_FRAME_MAX_LEN + 2u)
#define TEL_PERIOD_MS         100u

#define UART_MVP_OUTPUT_TEST_ENABLED       0U
#define UART_MVP_OUTPUT_TEST_DUTY_PERMILLE 100U
#define UART_MVP_STALE_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED 0U
#define UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED 0U
#define UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED 0U
#define UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_EMBEDDED_CR_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_CONTROL_BYTE_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_OVERLONG_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_STALE_PONG_ONCE_TEST_ENABLED       0U
#define UART_MVP_SUPPRESS_PONG_TEST_ENABLED         0U

typedef enum{
    ROBOT_DISARMED = 0,
    ROBOT_ARMED,
    ROBOT_FAULT
} robot_state_t;

static UART_HandleTypeDef *s_uart;
static uint8_t s_rx_byte;
static ring_buffer_t s_rx_rb;

static char s_line[UART_LINE_BUFFER_SIZE];
static uint16_t s_line_len;
static uint8_t s_line_overflow;
static volatile uint8_t s_rx_desync_pending;
static uint8_t s_rx_discard_until_lf;

static robot_state_t s_state = ROBOT_DISARMED;
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

static void uart_sendf(const char *fmt, ...){
    char tx[256];
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
    uart_sendf("TEL,t_ms=%lu,state=%s,last_seq=%lu,"
               "vx_mmps=%ld,w_mradps=%ld,"
               "left_pwm=0,right_pwm=0,"
               "left_cps=%ld,right_cps=%ld,"
               "batt_mv=0,drop=%lu,err=%lu\n",
               (unsigned long)HAL_GetTick(),
               state_name(s_state),
               (unsigned long)s_last_seq,
               (long)s_vx_mmps,
               (long)s_w_mradps,
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
    s_rx_discard_until_lf = 1u;
}

static void handle_cmd(const uart_frame_t *frame){
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

    if(UART_MVP_OUTPUT_TEST_ENABLED != 0U){
        if((frame->vx_mmps == 50) && (frame->w_mradps == 0)){
            if(motor_output_set_raw(
                UART_MVP_OUTPUT_TEST_DUTY_PERMILLE,
                GPIO_PIN_RESET,
                UART_MVP_OUTPUT_TEST_DUTY_PERMILLE,
                GPIO_PIN_RESET
            ) != HAL_OK){
                motor_output_stop_all();
                send_err(frame->seq, "CMD", "MOTOR_OUTPUT_FAILED");
                return;
            }
        }
        else{
            motor_output_stop_all();
        }
    }

    s_last_seq = frame->seq;
    s_vx_mmps = frame->vx_mmps;
    s_w_mradps = frame->w_mradps;
    s_cmd_timeout_ms = frame->timeout_ms;
    s_last_cmd_ms = HAL_GetTick();

    send_ack(frame->seq, "CMD");
}

static void handle_line(const char *line, size_t line_len){
    uart_frame_t frame;
    uart_frame_parse_result_t parse_result;

    parse_result = uart_frame_parse(line, line_len, &frame);
    if(parse_result != UART_FRAME_PARSE_OK){
        send_err(
            frame.seq,
            uart_frame_type_name(frame.type),
            parse_error_code(parse_result)
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
            motor_output_stop_all();
            s_vx_mmps = 0;
            s_w_mradps = 0;
            s_state = ROBOT_DISARMED;
            s_last_seq = frame.seq;
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
            motor_output_stop_all();
            s_vx_mmps = 0;
            s_w_mradps = 0;
            s_state = ROBOT_ARMED;
            s_last_seq = frame.seq;
            send_ack(frame.seq, "ARM");
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
    s_rx_discard_until_lf = 0u;

    s_state = ROBOT_DISARMED;
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
    s_last_tel_ms = 0u;
    s_error_count = 0u;
    s_left_cps = 0;
    s_right_cps = 0;

    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
    s_last_cmd_ms = 0u;
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

        if(s_rx_discard_until_lf != 0u){
            if(byte == '\n'){
                s_rx_discard_until_lf = 0u;
                uart_sendf("ERR,seq=0,type=RX,code=RX_DESYNC\n");
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

    /* Force command velocity to zero when no fresh CMD arrives in time. */
    if(s_state == ROBOT_ARMED &&
       (HAL_GetTick() - s_last_cmd_ms) >= s_cmd_timeout_ms){
        motor_output_stop_all();
        s_vx_mmps = 0;
        s_w_mradps = 0;
    }

    if((HAL_GetTick() - s_last_tel_ms) >= TEL_PERIOD_MS){
        s_last_tel_ms = HAL_GetTick();
        send_tel();
    }
}
