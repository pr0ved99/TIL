#ifndef WIFI_CONTROL_CONTRACT_H
#define WIFI_CONTROL_CONTRACT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define WIFI_CONTROL_MAX_FRAME_SIZE 128U
#define WIFI_CONTROL_ZERO_ONLY 1U
#define WIFI_CONTROL_VX_MIN_MMPS (-100)
#define WIFI_CONTROL_VX_MAX_MMPS 100
#define WIFI_CONTROL_W_MIN_MRADPS (-500)
#define WIFI_CONTROL_W_MAX_MRADPS 500

typedef enum {
    WIFI_CONTROL_ARM,
    WIFI_CONTROL_CMD
} wifi_control_type_t;

typedef enum {
    WIFI_CONTROL_PARSE_OK,
    WIFI_CONTROL_PARSE_BAD_FORMAT,
    WIFI_CONTROL_PARSE_OUT_OF_RANGE
} wifi_control_parse_status_t;

typedef struct {
    wifi_control_type_t type;
    uint32_t expected_boot_id;
    uint32_t request_id;
    uint32_t control_id;
    uint32_t ticket;
    int32_t vx_mmps;
    int32_t w_mradps;

    /* ESP가 나중에 채울 값. 브라우저 문자열에서 읽지 않는다. */
    uint32_t ws_session_id;
    uint64_t accepted_ms;
    uint64_t expires_ms;
} wifi_control_request_t;

/* 성공할 때만 out에 복사한다. 실패하면 이전 out을 사용하지 않는다. */
wifi_control_parse_status_t wifi_control_parse(
    const char *text, size_t length,
    wifi_control_request_t *out);

/* 파실 성공 요청의 zero-only 적합성만 확인한다. 제어 허가가 아니다. */
bool wifi_control_zero_only_allows(
    const wifi_control_request_t *request);

#endif