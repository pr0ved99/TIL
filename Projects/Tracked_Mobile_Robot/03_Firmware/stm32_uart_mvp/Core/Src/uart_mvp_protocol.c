#include "uart_mvp_protocol.h"

#include "ring_buffer.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CMD_TIMEOUT_DEFAULT_MS 300u
#define CMD_TIMEOUT_MIN_MS      50u
#define CMD_TIMEOUT_MAX_MS     500u

#define VX_MIN_MMPS -100
#define VX_MAX_MMPS  100
#define W_MIN_MRADPS -500
#define W_MAX_MRADPS  500

#define UART_LINE_MAX 128u
#define TEL_PERIOD_MS 100u

typedef enum{
    ROBOT_DISARMED = 0,
    ROBOT_ARMED,
    ROBOT_FAULT
} robot_state_t;

static UART_HandleTypeDef *s_uart;
static uint8_t s_rx_byte;
static ring_buffer_t s_rx_rb;

static char s_line[UART_LINE_MAX];
static uint16_t s_line_len;
static uint8_t s_line_overflow;

static robot_state_t s_state = ROBOT_DISARMED;
static int32_t s_last_seq;
static int32_t s_vx_mmps;
static int32_t s_w_mradps;
static uint32_t s_cmd_timeout_ms;
static uint32_t s_last_cmd_ms;
static uint32_t s_last_tel_ms;
static uint32_t s_error_count;

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
    char tx[160];
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

static int parse_seq(const char *line, int32_t *seq){
    const char *p;

    if(line == NULL || seq == NULL){
        return 0;
    }

    p = strstr(line, "seq=");
    if(p == NULL){
        return 0;
    }

    p += 4;

    *seq = (int32_t)strtol(p, NULL, 10);

    return 1;
}

static int parse_i32_field(const char *line, const char *key, int32_t *value){
    const char *p;

    if(line == NULL || key == NULL || value == NULL){
        return 0;
    }

    p = strstr(line, key);
    if(p == NULL){
        return 0;
    }

    p += strlen(key);

    *value = (int32_t)strtol(p, NULL, 10);

    return 1;
}

static int parse_u32_field(const char *line, const char *key, uint32_t *value){
    const char *p;

    if(line == NULL || key == NULL || value == NULL){
        return 0;
    }

    p = strstr(line, key);
    if(p == NULL){
        return 0;
    }

    p += strlen(key);

    *value = (uint32_t)strtoul(p, NULL, 10);
    return 1;
}

static void send_ack(int32_t seq, const char *type){
    uart_sendf("ACK,seq=%ld,type=%s,t_ms=%lu\n",
                (long)seq,
                type,
                (unsigned long)HAL_GetTick());
}

static void send_err(int32_t seq, const char *type, const char *code){
    s_error_count++;

    uart_sendf("ERR,seq=%ld,type=%s,code=%s,t_ms=%lu\n",
                (long)seq,
                type,
                code,
                (unsigned long)HAL_GetTick());
}

static void send_tel(void){
    uart_sendf("TEL,t_ms=%lu,state=%s,last_seq=%ld,"
                "vx_mmps=%ld,w_mradps=%ld,"
                "left_pwm=0,right_pwm=0,"
                "left_cps=0,right_cps=0,"
                "batt_mv=0,drop=%lu,err=%lu\n",
                (unsigned long)HAL_GetTick(),
                state_name(s_state),
                (long)s_last_seq,
                (long)s_vx_mmps,
                (long)s_w_mradps,
                (unsigned long)ring_buffer_dropped(&s_rx_rb),
                (unsigned long)s_error_count);
}

static void handle_cmd(const char *line){
    int32_t seq = 0;
    int32_t vx_mmps = 0;
    int32_t w_mradps = 0;
    uint32_t timeout_ms = 0u;

    if(!parse_seq(line, &seq)){
        send_err(0, "CMD", "MISSING_SEQ");
        return;
    }

    if(!parse_i32_field(line, "vx_mmps=", &vx_mmps) ||
       !parse_i32_field(line, "w_mradps=", &w_mradps) ||
       !parse_u32_field(line, "timeout_ms=", &timeout_ms)){
        send_err(seq, "CMD", "MISSING_FIELD");
        return;
    }

    if(vx_mmps < VX_MIN_MMPS || vx_mmps > VX_MAX_MMPS ||
       w_mradps < W_MIN_MRADPS || w_mradps > W_MAX_MRADPS){
        send_err(seq, "CMD", "OUT_OF_RANGE");
        return;
    }

    if(timeout_ms < CMD_TIMEOUT_MIN_MS || timeout_ms > CMD_TIMEOUT_MAX_MS){
        send_err(seq, "CMD", "TIMEOUT_OUT_OF_RANGE");
        return;
    }

    if(s_state != ROBOT_ARMED){
        send_err(seq, "CMD", "NOT_ARMED");
        return;
    }

    s_last_seq = seq;
    s_vx_mmps = vx_mmps;
    s_w_mradps = w_mradps;
    s_cmd_timeout_ms = timeout_ms;
    s_last_cmd_ms = HAL_GetTick();

    send_ack(seq, "CMD");
}

static void handle_line(const char *line){
    int32_t seq = 0;

    if(line == NULL){
        return;
    }

    if(strncmp(line, "PING", 4) == 0){
        if(!parse_seq(line, &seq)){
            send_err(0, "PING", "MISSING_SEQ");
            return;
        }

        s_last_seq = seq;
        uart_sendf("PONG,seq=%ld,t_ms=%lu\n",
                    (long)seq,
                    (unsigned long)HAL_GetTick());
        return;
    }

    if(strncmp(line, "DISARM", 6) == 0){
        if(!parse_seq(line, &seq)){
            send_err(0, "DISARM", "MISSING_SEQ");
            return;
        }

        s_state = ROBOT_DISARMED;
        s_last_seq = seq;
        send_ack(seq, "DISARM");
        return;
    }

    if(strncmp(line, "ARM", 3) == 0){
        if(!parse_seq(line, &seq)){
            send_err(0, "ARM", "MISSING_SEQ");
            return;
        }

        s_state = ROBOT_ARMED;
        s_last_seq = seq;
        send_ack(seq, "ARM");
        return;
    }

    if(strncmp(line, "CMD", 3) == 0){
        handle_cmd(line);
        return;
    }

    send_err(0, "UNKNOWN", "BAD_TYPE");
}

void uart_mvp_init(UART_HandleTypeDef *huart){
    s_uart = huart;
    s_rx_byte = 0u;

    ring_buffer_init(&s_rx_rb);

    s_line_len = 0u;
    s_line_overflow = 0u;

    s_state = ROBOT_DISARMED;
    s_last_seq = 0;
    s_last_tel_ms = 0u;
    s_error_count = 0u;

    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
    s_last_cmd_ms = 0u;
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
    }
    HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
}

void uart_mvp_on_uart_error(UART_HandleTypeDef *huart){
    if(huart != s_uart){
        return;
    }

    s_error_count++;

    HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1);
}

void uart_mvp_process(void){
    uint8_t byte;

    while(ring_buffer_pop(&s_rx_rb, &byte)){
        if(byte == '\r'){
            continue;
        }

        if(byte == '\n'){
            s_line[s_line_len] = '\0';

            if(s_line_overflow){
                s_error_count++;
                uart_sendf("ERR,seq=0,type=RX,code=LINE_OVERFLOW\n");
            }
            else if(s_line_len > 0u){
                handle_line(s_line);
            }

            s_line_len = 0u;
            s_line_overflow = 0u;
            continue;
        }

        if(s_line_len < (UART_LINE_MAX - 1u)){
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
        s_vx_mmps = 0;
        s_w_mradps = 0;
    }

    if((HAL_GetTick() - s_last_tel_ms) >= TEL_PERIOD_MS){
        s_last_tel_ms = HAL_GetTick();
        send_tel();
    }
}
