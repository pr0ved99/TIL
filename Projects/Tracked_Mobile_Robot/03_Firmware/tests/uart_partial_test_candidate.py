"""Prepare the UR-02 manual injection candidate in memory; never edit firmware."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE.parent / 'esp32_wifi_link/main/wifi_link_main.c'

CONFIG = '''/* 0: normal image; 1: partial CMD; 2: ARM without LF.
 * Test images reject normal PING/ARM/CMD for the entire boot.
 * One manual POST per boot; never inject automatically at startup. */
#define WIFI_UART_PARTIAL_TEST_MODE 0U
#if WIFI_UART_PARTIAL_TEST_MODE > 2U
#error "WIFI_UART_PARTIAL_TEST_MODE must be 0, 1 or 2"
#endif
#if WIFI_UART_PARTIAL_TEST_MODE != 0U
#define WIFI_UART_PARTIAL_TEST_BANNER \\
    "<p><strong>UART 부분 명령 시험 이미지</strong> · 일반 PING/ARM/CMD 비활성 · 수동 DISARM 가능</p>"
#else
#define WIFI_UART_PARTIAL_TEST_BANNER ""
#endif

static esp_err_t wifi_uart_test_post(httpd_req_t *req);
static void wifi_uart_test_cancel_locked(void);
'''

BLOCK = r'''/* UART_PARTIAL_TEST_BEGIN: all state is protected by s_stm_lock. */
typedef enum {
    UART_TEST_UNUSED, UART_TEST_QUEUED, UART_TEST_HOLD,
    UART_TEST_STOPPING, UART_TEST_DONE, UART_TEST_ABORTED
} uart_partial_test_phase_t;

static uart_partial_test_phase_t s_uart_test_phase;
static uint64_t s_uart_test_at_ms;
static bool s_uart_test_prefix_full;

static bool wifi_uart_test_ready_locked(uint64_t now)
{
    const wifi_control_state_t *s = &s_control.state;
    return wifi_control_ready_locked() && s->phase == WIFI_CONTROL_IDLE &&
        !s_manual_stop_pending && s_wifi_command_owner_session_id == 0U &&
        !s_control.queued && !s_control.waiting && !s_control.prepared &&
        !s_control.have_result && s->have_tel && now >= s->tel_received_ms &&
        now - s->tel_received_ms < WIFI_CONTROL_TEL_MS &&
        s->tel.state == WIFI_CONTROL_STM_DISARMED &&
        s->tel.vx_mmps == 0 && s->tel.w_mradps == 0 &&
        s->tel.left_pwm == 0 && s->tel.right_pwm == 0;
}

/* Reserve the prefix identity and ensure the next allocator call can still
 * provide a DISARM identity, including skipped startup-reserved values. */
static bool wifi_uart_test_sequence_locked(uint32_t *seq)
{
    if (!wifi_uart_allocate_seq(seq)) return false;
    while (s_wifi_uart_next_seq <= UINT32_MAX &&
        (s_wifi_uart_next_seq == s_stm_startup.disarm_seq ||
         s_wifi_uart_next_seq == s_stm_startup.ping_seq)) {
        ++s_wifi_uart_next_seq;
    }
    return s_wifi_uart_next_seq <= UINT32_MAX;
}

/* Manual stop / transport loss cancels a queued injection. A committed prefix
 * cannot be recalled; request the existing priority DISARM immediately. */
static void wifi_uart_test_cancel_locked(void)
{
    if (s_uart_test_phase == UART_TEST_QUEUED) {
        s_uart_test_phase = UART_TEST_ABORTED;
    } else if (s_uart_test_phase == UART_TEST_HOLD) {
        s_uart_test_phase = UART_TEST_STOPPING;
        wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_MANUAL_STOP,
                                   wifi_control_now());
        wifi_control_cleanup_locked();
    }
}

/* Body: decimal current boot_id only. HTTP queues; it never writes UART.
 * The 202 response means accepted, not prefix delivery or test success. */
static esp_err_t wifi_uart_test_post(httpd_req_t *req)
{
    if (WIFI_UART_PARTIAL_TEST_MODE == 0U) {
        httpd_resp_set_status(req, "404 Not Found");
        return httpd_resp_sendstr(req, "DISABLED");
    }
    char body[11];
    if (req->content_len <= 0 || req->content_len >= sizeof(body)) {
        httpd_resp_set_status(req, "400 Bad Request");
        return httpd_resp_sendstr(req, "BAD_INPUT");
    }
    size_t used = 0U;
    while (used < req->content_len) {
        const int got = httpd_req_recv(req, body + used, req->content_len - used);
        if (got <= 0) return ESP_FAIL; /* No retry, no queued side effect. */
        used += (size_t)got;
    }
    body[used] = '\0';
    uint32_t boot = 0U;
    const char *cursor = body;
    if (memchr(body, '\0', used) != NULL ||
        !wifi_command_parse_u32(&cursor, &boot) || *cursor != '\0') {
        httpd_resp_set_status(req, "400 Bad Request");
        return httpd_resp_sendstr(req, "BAD_INPUT");
    }
    const char *error = NULL;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const uint64_t now = wifi_control_now();
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), now);
    wifi_control_cleanup_locked();
    if (boot != s_boot_id) error = "BOOT_MISMATCH";
    else if (s_uart_test_phase != UART_TEST_UNUSED) error = "ALREADY_USED";
    else if (!wifi_uart_test_ready_locked(now)) error = "NOT_READY";
    else {
        s_uart_test_phase = UART_TEST_QUEUED;
        s_uart_test_at_ms = now;
    }
    xSemaphoreGive(s_stm_lock);
    httpd_resp_set_status(req, error != NULL ? "409 Conflict" : "202 Accepted");
    return httpd_resp_sendstr(req, error != NULL ? error : "QUEUED; check UART log and capture");
}

/* Called only by stm_uart_rx_task, before normal control/command dispatch.
 * Fixed prefix -> 100 ms receive/poll interval -> existing CAN+LF DISARM.
 * No raw input, no LF-only flush, no retry, no new UART writer task. */
static void wifi_uart_test_step(void)
{
    if (WIFI_UART_PARTIAL_TEST_MODE == 0U) return;
    char prefix[32];
    int length = 0;
    uint32_t seq = 0U;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const uint64_t now = wifi_control_now();
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), now);
    wifi_control_cleanup_locked();
    if (s_uart_test_phase == UART_TEST_QUEUED) {
        if (now < s_uart_test_at_ms || now - s_uart_test_at_ms >= WIFI_CONTROL_QUEUE_MS ||
            !wifi_uart_test_ready_locked(now) || !wifi_uart_test_sequence_locked(&seq)) {
            s_uart_test_phase = UART_TEST_ABORTED;
            ESP_LOGW(TAG, "UART TEST: not sent (expired/not ready/sequence exhausted)");
        } else {
            length = WIFI_UART_PARTIAL_TEST_MODE == 1U ?
                snprintf(prefix, sizeof(prefix), "CMD,seq=") :
                snprintf(prefix, sizeof(prefix), "ARM,seq=%" PRIu32, seq);
            /* The fixed strings plus uint32_t always fit prefix[32]. */
            s_uart_test_phase = UART_TEST_HOLD;
            s_uart_test_at_ms = now;
        }
    } else if (s_uart_test_phase == UART_TEST_HOLD) {
        if (!wifi_uart_test_ready_locked(now) || now < s_uart_test_at_ms ||
            now - s_uart_test_at_ms >= 100U) {
            s_uart_test_phase = UART_TEST_STOPPING;
            wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_MANUAL_STOP, now);
            wifi_control_cleanup_locked();
        }
    } else if (s_uart_test_phase == UART_TEST_STOPPING) {
        if (s_control.state.phase == WIFI_CONTROL_IDLE ||
            s_control.state.phase == WIFI_CONTROL_BLOCKED) {
            s_uart_test_phase = UART_TEST_DONE;
            ESP_LOGI(TAG, "UART TEST: end prefix_full=%u stop_confirmed=%u; capture review required",
                     s_uart_test_prefix_full ? 1U : 0U,
                     s_control.state.phase == WIFI_CONTROL_IDLE ? 1U : 0U);
        }
    }
    xSemaphoreGive(s_stm_lock);
    if (length <= 0) return;

    /* Commit point is above, under the lock, just like executor take_tx.
     * A concurrent DISARM may cancel the hold, but cannot retract these bytes. */
    const int written = uart_write_bytes(STM_UART_PORT, prefix, (size_t)length);
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    s_uart_test_prefix_full = written == length;
    if (s_uart_test_phase == UART_TEST_HOLD) {
        s_uart_test_at_ms = wifi_control_now();
        if (!s_uart_test_prefix_full) wifi_uart_test_cancel_locked();
    }
    xSemaphoreGive(s_stm_lock);
    ESP_LOGI(TAG, "UART TEST: mode=%u reserved_seq=%" PRIu32 " prefix=%s written=%d/%d NO_LF",
             (unsigned)WIFI_UART_PARTIAL_TEST_MODE, seq, prefix, written, length);
}
/* UART_PARTIAL_TEST_END */
'''


def prepare():
    source = MAIN.read_text(encoding='utf-8')
    if 'UART_PARTIAL_TEST_BEGIN' in source:
        raise ValueError('Candidate already entered; use --saved to review the real file')

    def replace(old, new):
        nonlocal source
        if source.count(old) != 1:
            raise ValueError('Source changed; review anchor: ' + old[:100])
        source = source.replace(old, new, 1)

    replace('#define STATUS_JSON_SIZE', CONFIG + '\n#define STATUS_JSON_SIZE')
    replace('</h1><p>STM32 UART', '</h1>"\n    WIFI_UART_PARTIAL_TEST_BANNER\n    "<p>STM32 UART')
    replace('    request->ws_session_id = session->id;',
            '    if (WIFI_UART_PARTIAL_TEST_MODE != 0U && request->type != WIFI_COMMAND_DISARM)\n'
            '        return "BUSY"; /* Bench image: normal control stays disabled. */\n'
            '    request->ws_session_id = session->id;')
    replace('        if (s_manual_stop_pending) return "BUSY";\n        s_manual_stop_request',
            '        if (s_manual_stop_pending) return "BUSY";\n'
            '        wifi_uart_test_cancel_locked();\n        s_manual_stop_request')
    replace('    const bool available = !s_manual_stop_pending',
            '    const bool available = WIFI_UART_PARTIAL_TEST_MODE == 0U && !s_manual_stop_pending')
    replace('static void wifi_control_transport_lost(void)\n{\n    xSemaphoreTake(s_stm_lock, portMAX_DELAY);',
            'static void wifi_control_transport_lost(void)\n{\n    xSemaphoreTake(s_stm_lock, portMAX_DELAY);\n'
            '    wifi_uart_test_cancel_locked();')
    replace('static void wifi_control_step(void)', BLOCK + '\nstatic void wifi_control_step(void)')
    replace('    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &ws_uri));',
            '    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &ws_uri));\n'
            '    if (WIFI_UART_PARTIAL_TEST_MODE != 0U) {\n'
            '        const httpd_uri_t test_uri = {\n'
            '            .uri = "/api/uart-partial-test", .method = HTTP_POST,\n'
            '            .handler = wifi_uart_test_post\n'
            '        };\n'
            '        ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &test_uri));\n'
            '        ESP_LOGW(TAG, "UART TEST IMAGE mode=%u: normal PING/ARM/CMD disabled",\n'
            '                 (unsigned)WIFI_UART_PARTIAL_TEST_MODE);\n'
            '    }')
    if source.count('        wifi_control_step();\n        wifi_command_step();') != 2:
        raise ValueError('UART task call sites changed')
    source = source.replace('        wifi_control_step();\n        wifi_command_step();',
                            '        wifi_uart_test_step();\n        wifi_control_step();\n        wifi_command_step();')
    return source
