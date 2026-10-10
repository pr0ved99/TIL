#ifndef WIFI_CONTROL_TICKET_H
#define WIFI_CONTROL_TICKET_H

#include "wifi_control_contract.h"

#define WIFI_CONTROL_TICKET_VALID_MS 150U

/* ESP 부팅 전체에서 공유한다. 연결 종료 떄 초기화하지 않는다. */
typedef struct {
    uint32_t boot_id;
    uint64_t next_id;
} wifi_control_ticket_pool_t;

/* 연결마다 하나 보관한다. 초기값은 {0}이다. */
typedef struct {
    uint32_t boot_id;
    uint32_t ws_session_id;
    uint32_t control_id;
    wifi_control_type_t purpose;
    uint32_t id;
    uint64_t issued_ms;
    uint64_t expires_ms;
    bool valid;
} wifi_control_ticket_t;

typedef enum {
    WIFI_TICKET_OK,
    WIFI_TICKET_BAD_ARGUMENT,
    WIFI_TICKET_BUSY,
    WIFI_TICKET_EXHAUSTED,
    WIFI_TICKET_MISMATCH,
    WIFI_TICKET_EXPIRED
} wifi_control_ticket_status_t;

void wifi_control_ticket_pool_init(
    wifi_control_ticket_pool_t *pool, uint32_t boot_id);

wifi_control_ticket_status_t wifi_control_ticket_issue(
    wifi_control_ticket_pool_t *pool,
    wifi_control_ticket_t *ticket,
    uint32_t ws_session_id, wifi_control_type_t purpose,
    uint32_t control_id, uint64_t now_ms);

/* 호출자는 parser 성공과 나머지 접수 조건을 먼저 검사한다. */
wifi_control_ticket_status_t wifi_control_ticket_consume(
    wifi_control_ticket_t *ticket,
    const wifi_control_request_t *request, uint64_t now_ms);

void wifi_control_ticket_invalidate(wifi_control_ticket_t *ticket);

#endif