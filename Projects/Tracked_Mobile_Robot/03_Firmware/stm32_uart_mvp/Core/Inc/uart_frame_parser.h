#ifndef UART_FRAME_PARSER_H
#define UART_FRAME_PARSER_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    UART_FRAME_TYPE_UNKNOWN = 0,
    UART_FRAME_TYPE_PING,
    UART_FRAME_TYPE_ARM,
    UART_FRAME_TYPE_DISARM,
    UART_FRAME_TYPE_CMD,
    UART_FRAME_TYPE_ESTOP_RESET
} uart_frame_type_t;

typedef enum {
    UART_FRAME_PARSE_OK = 0,
    UART_FRAME_PARSE_NULL_ARGUMENT,
    UART_FRAME_PARSE_EMPTY,
    UART_FRAME_PARSE_BAD_TYPE,
    UART_FRAME_PARSE_MISSING_SEQ,
    UART_FRAME_PARSE_INVALID_SEQ,
    UART_FRAME_PARSE_MISSING_FIELD,
    UART_FRAME_PARSE_BAD_FIELD_ORDER,
    UART_FRAME_PARSE_INVALID_NUMBER,
    UART_FRAME_PARSE_VELOCITY_OUT_OF_RANGE,
    UART_FRAME_PARSE_TIMEOUT_OUT_OF_RANGE,
    UART_FRAME_PARSE_EXTRA_DATA
} uart_frame_parse_result_t;

typedef struct {
    uart_frame_type_t type;
    uint32_t seq;
    int32_t vx_mmps;
    int32_t w_mradps;
    uint32_t timeout_ms;
} uart_frame_t;

/*
 * Parse exactly line_len bytes as one UART command frame.
 * The caller must remove the trailing CR/LF before calling this function.
 * frame is initialized to safe defaults before parsing.
 */
uart_frame_parse_result_t uart_frame_parse(
    const char *line,
    size_t line_len,
    uart_frame_t *frame
);

const char *uart_frame_type_name(uart_frame_type_t type);

#endif // UART_FRAME_PARSER_H
