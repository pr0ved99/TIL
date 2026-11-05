#include "wifi_control_ticket.h"

void wifi_control_ticket_pool_init(
    wifi_control_ticket_pool_t *pool, uint32_t boot_id)
{
    if (pool != NULL) {
        *pool = (wifi_control_ticket_pool_t) {
            .boot_id = boot_id,
            .next_id = 1U
        };
    }
}

void wifi_control_ticket_invalidate(wifi_control_ticket_t *ticket)
{
    if (ticket != NULL) {
        ticket->valid = false;
    }
}

wifi_control_ticket_status_t wifi_control_ticket_issue(
    wifi_control_ticket_pool_t *pool,
    wifi_control_ticket_t *ticket,
    uint32_t ws_session_id, wifi_control_type_t purpose,
    uint32_t control_id, uint64_t now_ms)
{
    if (pool == NULL || ticket == NULL || ws_session_id == 0U ||
        (purpose != WIFI_CONTROL_ARM && purpose != WIFI_CONTROL_CMD) ||
        (purpose == WIFI_CONTROL_ARM && control_id != 0U) ||
        (purpose == WIFI_CONTROL_CMD && control_id == 0U) ||
        now_ms > UINT64_MAX - WIFI_CONTROL_TICKET_VALID_MS) {
        return WIFI_TICKET_BAD_ARGUMENT;
    }

    if (ticket->valid) {
        if (now_ms < ticket->issued_ms) {
            ticket->valid = false;
            return WIFI_TICKET_EXPIRED;
        }
        if (now_ms < ticket->expires_ms) {
            return WIFI_TICKET_BUSY;
        }
        ticket->valid = false;
    }

    if (pool->next_id == 0U || pool->next_id > UINT32_MAX) {
        return WIFI_TICKET_EXHAUSTED;
    }

    *ticket = (wifi_control_ticket_t){
        .boot_id = pool->boot_id,
        .ws_session_id = ws_session_id,
        .control_id = control_id,
        .purpose = purpose,
        .id = (uint32_t)pool->next_id++,
        .issued_ms = now_ms,
        .expires_ms = now_ms + WIFI_CONTROL_TICKET_VALID_MS,
        .valid = true
    };
    return WIFI_TICKET_OK;
}

wifi_control_ticket_status_t wifi_control_ticket_consume(
    wifi_control_ticket_t *ticket,
    const wifi_control_request_t *request, uint64_t now_ms)
{
    if (ticket == NULL || request == NULL) {
        return WIFI_TICKET_BAD_ARGUMENT;
    }

    if (!ticket->valid || ticket->id == 0U ||
        request->expected_boot_id != ticket->boot_id ||
        request->ws_session_id != ticket->ws_session_id ||
        request->type != ticket->purpose ||
        request->control_id != ticket->control_id ||
        request->ticket != ticket->id) {
        return WIFI_TICKET_MISMATCH;
    }

    if (now_ms < ticket->issued_ms || now_ms >= ticket->expires_ms) {
        ticket->valid = false;
        return WIFI_TICKET_EXPIRED;
    }

    ticket->valid = false;
    return WIFI_TICKET_OK;
}