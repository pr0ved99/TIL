#include "wifi_control_owner.h"

void wifi_control_owner_init(
    wifi_control_owner_t *owner, uint32_t boot_id)
{
    if (owner != NULL) {
        *owner = (wifi_control_owner_t) {
            .boot_id = boot_id,
            .next_control_id = 1U
        };
    }
}

wifi_control_owner_status_t wifi_control_owner_reserve(
    wifi_control_owner_t *owner, uint32_t ws_session_id,
    uint32_t *out_control_id)
{
    if (owner == NULL || ws_session_id == 0U || out_control_id == NULL) {
        return WIFI_OWNER_BAD_ARGUMENT;
    }

    if (owner->ws_session_id != 0U || owner->control_id != 0U) {
        return WIFI_OWNER_BUSY;
    }

    if (owner->next_control_id == 0U || owner->next_control_id > UINT32_MAX) {
        return WIFI_OWNER_EXHAUSTED;
    }

    owner->ws_session_id = ws_session_id;
    owner->control_id = (uint32_t)owner->next_control_id++;
    *out_control_id = owner->control_id;
    return WIFI_OWNER_OK;
}

bool wifi_control_owner_matches(
    const wifi_control_owner_t *owner, uint32_t boot_id,
    uint32_t ws_session_id, uint32_t control_id)
{
    return owner != NULL && ws_session_id != 0U && control_id != 0U &&
        owner->boot_id == boot_id &&
        owner->ws_session_id == ws_session_id &&
        owner->control_id == control_id;
}

void wifi_control_owner_revoke(wifi_control_owner_t *owner)
{
    if (owner != NULL) {
        owner->ws_session_id = 0U;
        owner->control_id = 0U;
    }
}