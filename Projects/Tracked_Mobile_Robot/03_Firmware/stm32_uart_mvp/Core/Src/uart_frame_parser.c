#include "uart_frame_parser.h"

#include <stdint.h>

typedef struct {
    const char *data;
    size_t length;
    size_t position;
} parser_cursor_t;

typedef enum {
    NUMBER_PARSE_OK = 0,
    NUMBER_PARSE_EMPTY,
    NUMBER_PARSE_INVALID,
    NUMBER_PARSE_OUT_OF_RANGE
} number_parse_result_t;

/* Compare a bounded token with a NUL-terminated expected literal. */
static int token_equals(
    const char *token,
    size_t token_len,
    const char *expected
) {
    size_t index = 0u;

    while (expected[index] != '\0') {
        if (index >= token_len || token[index] != expected[index]) {
            return 0;
        }
        index++;
    }

    return index == token_len;
}

/* Consume a literal at the current cursor position without reading past the frame. */
static int consume_literal(parser_cursor_t *cursor, const char *literal) {
    size_t index = 0u;
    size_t remaining;

    if (cursor->position > cursor->length) {
        return 0;
    }

    remaining = cursor->length - cursor->position;

    while (literal[index] != '\0') {
        if (index >= remaining ||
            cursor->data[cursor->position + index] != literal[index]) {
            return 0;
        }
        index++;
    }

    cursor->position += index;
    return 1;
}

static int is_decimal_digit(char value) {
    return value >= '0' && value <= '9';
}

/* Parse an unsigned 32-bit decimal value without requiring NUL termination. */
static number_parse_result_t parse_u32_value(
    parser_cursor_t *cursor,
    uint32_t *value
) {
    uint32_t parsed = 0u;

    if (cursor->position >= cursor->length) {
        return NUMBER_PARSE_EMPTY;
    }
    if (!is_decimal_digit(cursor->data[cursor->position])) {
        return NUMBER_PARSE_INVALID;
    }

    while (cursor->position < cursor->length &&
            is_decimal_digit(cursor->data[cursor->position])) {
        uint32_t digit =
             (uint32_t)(cursor->data[cursor->position] - '0');

        if (parsed > (UINT32_MAX - digit) / 10u) {
            return NUMBER_PARSE_OUT_OF_RANGE;
        }

        parsed = (parsed * 10u) + digit;
        cursor->position++;
    }

    *value = parsed;
    return NUMBER_PARSE_OK;
}

/* Parse a signed 32-bit decimal value without requiring NUL termination. */
static number_parse_result_t parse_i32_value(
    parser_cursor_t *cursor,
    int32_t *value
) {
    uint32_t magnitude = 0u;
    uint32_t limit = 2147483647u;
    int negative = 0;

    if (cursor->position >= cursor->length) {
        return NUMBER_PARSE_EMPTY;
    }

    if (cursor->data[cursor->position] == '-') {
        negative = 1;
        limit = 2147483648u;
        cursor->position++;
    }

    if (cursor->position >= cursor->length ||
        !is_decimal_digit(cursor->data[cursor->position])) {
        return NUMBER_PARSE_INVALID;
    }

    while (cursor->position < cursor->length &&
           is_decimal_digit(cursor->data[cursor->position])) {
        uint32_t digit =
            (uint32_t)(cursor->data[cursor->position] - '0');

        if (magnitude > (limit - digit) / 10u) {
            return NUMBER_PARSE_OUT_OF_RANGE;
        }

        magnitude = (magnitude * 10u) + digit;
        cursor->position++;
    }

    if (negative != 0) {
        if (magnitude == 2147483648u) {
            *value = (-2147483647 - 1);
        } else {
            *value = -(int32_t)magnitude;
        }
    } else {
        *value = (int32_t)magnitude;
    }

    return NUMBER_PARSE_OK;
}

/* Map an exact command token to its internal frame type. */
static uart_frame_type_t parse_type(
    const char *line,
    size_t token_len
) {
    if (token_equals(line, token_len, "PING")) {
        return UART_FRAME_TYPE_PING;
    }
    if (token_equals(line, token_len, "ARM")) {
        return UART_FRAME_TYPE_ARM;
    }
    if (token_equals(line, token_len, "DISARM")) {
        return UART_FRAME_TYPE_DISARM;
    }
    if (token_equals(line, token_len, "CMD")) {
        return UART_FRAME_TYPE_CMD;
    }

    return UART_FRAME_TYPE_UNKNOWN;
}

uart_frame_parse_result_t uart_frame_parse(
    const char *line,
    size_t line_len,
    uart_frame_t *frame
){
    parser_cursor_t cursor;
    size_t type_length = 0u;
    number_parse_result_t number_result;
    uint32_t parsed_seq = 0u;

    if(frame == NULL){
        return UART_FRAME_PARSE_NULL_ARGUMENT;
    }

    frame->type = UART_FRAME_TYPE_UNKNOWN;
    frame->seq = 0u;
    frame->vx_mmps = 0;
    frame->w_mradps = 0;
    frame->timeout_ms = 0u;

    if(line == NULL){
        return UART_FRAME_PARSE_NULL_ARGUMENT;
    }
    if(line_len == 0u){
        return UART_FRAME_PARSE_EMPTY;
    }

    while(type_length < line_len && line[type_length] != ','){
        type_length++;
    }

    frame->type = parse_type(line, type_length);
    if(frame->type == UART_FRAME_TYPE_UNKNOWN){
        return UART_FRAME_PARSE_BAD_TYPE;
    }
    if(type_length == line_len){
        return UART_FRAME_PARSE_MISSING_SEQ;
    }

    cursor.data = line;
    cursor.length = line_len;
    cursor.position = type_length;

    if(!consume_literal(&cursor, ",seq=")){
        return UART_FRAME_PARSE_MISSING_SEQ;
    }

    number_result = parse_u32_value(&cursor, &parsed_seq);
    if(number_result != NUMBER_PARSE_OK){
        return UART_FRAME_PARSE_INVALID_SEQ;
    }

    if(frame->type != UART_FRAME_TYPE_CMD){
        if(cursor.position == cursor.length){
            frame->seq = parsed_seq;
            return UART_FRAME_PARSE_OK;
        }
        if(cursor.data[cursor.position] == ','){
            frame->seq = parsed_seq;
            return UART_FRAME_PARSE_EXTRA_DATA;
        }
        return UART_FRAME_PARSE_INVALID_SEQ;
    }

    if(cursor.position < cursor.length && cursor.data[cursor.position] != ','){
        return UART_FRAME_PARSE_INVALID_SEQ;
    }

    frame->seq = parsed_seq;

    if(cursor.position >= cursor.length){
        return UART_FRAME_PARSE_MISSING_FIELD;
    }
    if(!consume_literal(&cursor, ",vx_mmps=")){
        return UART_FRAME_PARSE_BAD_FIELD_ORDER;
    }

    number_result = parse_i32_value(&cursor, &frame->vx_mmps);
    if(number_result == NUMBER_PARSE_OUT_OF_RANGE){
        return UART_FRAME_PARSE_VELOCITY_OUT_OF_RANGE;
    }
    if(number_result != NUMBER_PARSE_OK){
        return UART_FRAME_PARSE_INVALID_NUMBER;
    }
    if(!consume_literal(&cursor, ",w_mradps=")){
        return UART_FRAME_PARSE_BAD_FIELD_ORDER;
    }

    number_result = parse_i32_value(&cursor, &frame->w_mradps);
    if(number_result == NUMBER_PARSE_OUT_OF_RANGE){
        return UART_FRAME_PARSE_VELOCITY_OUT_OF_RANGE;
    }
    if(number_result != NUMBER_PARSE_OK){
        return UART_FRAME_PARSE_INVALID_NUMBER;
    }
    if(!consume_literal(&cursor, ",timeout_ms=")){
        return UART_FRAME_PARSE_BAD_FIELD_ORDER;
    }

    number_result = parse_u32_value(&cursor, &frame->timeout_ms);
    if(number_result == NUMBER_PARSE_OUT_OF_RANGE){
        return UART_FRAME_PARSE_TIMEOUT_OUT_OF_RANGE;
    }
    if(number_result != NUMBER_PARSE_OK){
        return UART_FRAME_PARSE_INVALID_NUMBER;
    }
    if(cursor.position != cursor.length){
        return UART_FRAME_PARSE_EXTRA_DATA;
    }

    return UART_FRAME_PARSE_OK;
}

const char *uart_frame_type_name(uart_frame_type_t type){
    switch(type){
        case UART_FRAME_TYPE_PING:
            return "PING";
        case UART_FRAME_TYPE_ARM:
            return "ARM";
        case UART_FRAME_TYPE_DISARM:
            return "DISARM";
        case UART_FRAME_TYPE_CMD:
            return "CMD";
        case UART_FRAME_TYPE_UNKNOWN:
        default:
            return "UNKNOWN";
    }
}
