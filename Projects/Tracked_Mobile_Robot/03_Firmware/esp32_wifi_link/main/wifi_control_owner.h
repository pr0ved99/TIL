#ifndef WIFI_CONTROL_OWNER_H
#define WIFI_CONTROL_OWNER_H

#include "wifi_control_contract.h"

/* ESP 부팅당 하나. 취소 때 next_control_id를 초기화하지 않는다. */
typedef struct {
    uint32_t boot_id;
    uint64_t next_control_id;
    uint32_t ws_session_id;
    uint32_t control_id;
} wifi_control_owner_t;

typedef enum {
    WIFI_OWNER_OK,
    WIFI_OWNER_BAD_ARGUMENT,
    WIFI_OWNER_BUSY,
    WIFI_OWNER_EXHAUSTED
} wifi_control_owner_status_t;

void wifi_control_owner_init(
    wifi_control_owner_t *owner, uint32_t boot_id);

/* 호출자는 IDLE 및 나머지 ARM 접수 조건을 먼저 확인한다. */
wifi_control_owner_status_t wifi_control_owner_reserve(
    wifi_control_owner_t *owner, uint32_t ws_session_id,
    uint32_t *out_control_id);

/* 식별 번호만 대조한다. 제어 상태/시간/출력 허가 검사가 아니다. */
bool wifi_control_owner_matches(
    const wifi_control_owner_t *owner, uint32_t boot_id,
    uint32_t ws_session_id, uint32_t control_id);

void wifi_control_owner_revoke(wifi_control_owner_t *owner);

#endif