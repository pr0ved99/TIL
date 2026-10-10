#include "wifi_control_contract.h"

#include <string.h>

/* 일치한 문자열만큼 currsor를 이동한다. */
static bool control_take_literal(
    const char **cursor, const char *literal)
{
    const size_t length = strlen(literal);

    if (strncmp(*cursor, literal, length) != 0) {
        return false;
    }

    *cursor += length;
    return true;
}

/* u32 overflow를 곱셈 전에 검사한다. */
static bool control_read_u32(const char **cursor, uint32_t *out)
{
    const char *pos = *cursor;
    uint32_t value = 0U;

    if (*pos < '0' || *pos > '9') {
        return false;
    }

    while (*pos >= '0' && *pos <= '9') {
        const uint32_t digit = (uint32_t)(*pos - '0');

        if (value > (UINT32_MAX - digit) / 10U) {
            return false;
        }

        value = value *10U + digit;
        ++pos;
    }

    *cursor = pos;
    *out = value;
    return true;
}

/* 부호와 magnitude를 따로 읽어 INT32_MIN도 안전하게 처리한다. */
static bool control_read_i32(const char **cursor, int32_t *out)
{
    const char *pos = *cursor;
    const bool negative = *pos == '-';
    uint32_t magnitude = 0U;

    if (negative) {
        ++pos;
    }

    if (!control_read_u32(&pos, &magnitude)) {
        return false;
    }

    const uint32_t limit = negative
        ? (uint32_t)INT32_MAX + 1U
        : (uint32_t)INT32_MAX;
    
    if (magnitude > limit) {
        return false;
    }

    int32_t value;

    if (negative && magnitude == limit) {
        value = INT32_MIN;
    } else if (negative) {
        value = -(int32_t)magnitude;
    } else {
        value = (int32_t)magnitude;
    }

    *cursor = pos;
    *out = value;
    return true;
}

wifi_control_parse_status_t wifi_control_parse(
    const char *text, size_t length,
    wifi_control_request_t *out)
{
    if (text == NULL || out == NULL || length == 0U ||
        length > WIFI_CONTROL_MAX_FRAME_SIZE) {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    /* 공백, 개행, 중간, NUL, 비ASCII를 복사 전에 거부한다. */
    for (size_t i = 0U; i < length; ++i) {
        const uint8_t byte = (uint8_t)text[i];

        if (byte < 0x21U || byte > 0x7eU) {
            return WIFI_CONTROL_PARSE_BAD_FORMAT;
        }
    }

    char buffer[WIFI_CONTROL_MAX_FRAME_SIZE + 1U];
    memcpy(buffer, text, length);
    buffer[length] = '\0';

    const char *cursor = buffer;
    wifi_control_request_t parsed = {0};

    if (control_take_literal(&cursor, "ARM,")) {
        parsed.type = WIFI_CONTROL_ARM;
    } else if (control_take_literal(&cursor, "CMD,")) {
        parsed.type = WIFI_CONTROL_CMD;
    } else {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    if (!control_take_literal(&cursor, "boot_id=") ||
        !control_read_u32(&cursor, &parsed.expected_boot_id) ||
        !control_take_literal(&cursor, ",request_id=") ||
        !control_read_u32(&cursor, &parsed.request_id) ||
        parsed.request_id == 0U) {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    if (parsed.type == WIFI_CONTROL_CMD) {
        if (!control_take_literal(&cursor, ",control_id=") ||
            !control_read_u32(&cursor, &parsed.control_id) ||
            parsed.control_id == 0U) {
            return WIFI_CONTROL_PARSE_BAD_FORMAT;
        }
    }

    if (!control_take_literal(&cursor, ",ticket=") ||
        !control_read_u32(&cursor, &parsed.ticket) ||
        parsed.ticket == 0U) {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    if (parsed.type == WIFI_CONTROL_CMD) {
        if (!control_take_literal(&cursor, ",vx_mmps=") ||
            !control_read_i32(&cursor, &parsed.vx_mmps) ||
            !control_take_literal(&cursor, ",w_mradps=") ||
            !control_read_i32(&cursor, &parsed.w_mradps)) {
            return WIFI_CONTROL_PARSE_BAD_FORMAT;
        }
    }

    if (*cursor != '\0') {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    if (parsed.vx_mmps < WIFI_CONTROL_VX_MIN_MMPS ||
        parsed.vx_mmps > WIFI_CONTROL_VX_MAX_MMPS ||
        parsed.w_mradps < WIFI_CONTROL_W_MIN_MRADPS ||
        parsed.w_mradps > WIFI_CONTROL_W_MAX_MRADPS) {
        return WIFI_CONTROL_PARSE_OUT_OF_RANGE;
    }

    *out = parsed;
    return WIFI_CONTROL_PARSE_OK;
}

bool wifi_control_zero_only_allows(
    const wifi_control_request_t *request)
{
    return request != NULL &&
        (request->type == WIFI_CONTROL_ARM ||
            request->type == WIFI_CONTROL_CMD) &&
        request->vx_mmps == 0 && request->w_mradps == 0;
}