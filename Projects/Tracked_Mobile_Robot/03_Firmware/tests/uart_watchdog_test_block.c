/* Inserted inside UART_PARTIAL_TEST_BEGIN. Native tests compile these exact functions. */
typedef enum { WD_ARM, WD_ZERO, WD_TIMEOUT, WD_PROBE, WD_OBSERVE } uart_watchdog_phase_t;
static struct {
    uart_watchdog_phase_t phase;
    uint32_t seq[3], baseline_seq, drop, err, last_t_ms, ack_t_ms, cmd_t_ms, tel_floor;
    uint64_t started_ms, sent_ms, observed_ms;
    bool replied, proof, stop_confirmed;
    const char *problem;
} s_watchdog;

static bool wifi_watchdog_zero_locked(uint64_t now)
{
    const stm_telemetry_t *t = &s_stm_telemetry;
    return t->valid && now >= t->rx_ms && now - t->rx_ms < WIFI_CONTROL_TEL_MS &&
        (strcmp(t->state, "DISARMED") == 0 || strcmp(t->state, "ARMED") == 0) &&
        t->vx_mmps == 0 && t->w_mradps == 0 && t->left_pwm == 0 && t->right_pwm == 0 &&
        t->left_cps == 0 && t->right_cps == 0;
}

/* WATCHDOG_FUNCTIONS */
static void wifi_watchdog_stop_locked(const char *problem, uint64_t now)
{
    if (problem != NULL && s_watchdog.problem == NULL) s_watchdog.problem = problem;
    s_uart_test_phase = UART_TEST_STOPPING;
    wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_MANUAL_STOP, now);
    wifi_control_cleanup_locked();
    ESP_LOGI(TAG, "AC-S06: cleanup proof=%u problem=%s", s_watchdog.proof ? 1U : 0U,
             s_watchdog.problem != NULL ? s_watchdog.problem : "NONE");
}

static bool wifi_watchdog_reply_locked(wifi_control_op_t op, uint32_t seq,
    bool ack, const char *code, uint32_t t_ms, uint64_t now)
{
    if (WIFI_UART_PARTIAL_TEST_MODE != 3U || s_uart_test_phase != UART_TEST_HOLD ||
        (s_watchdog.phase != WD_ARM && s_watchdog.phase != WD_ZERO &&
         s_watchdog.phase != WD_PROBE)) return false;
    const unsigned index = s_watchdog.phase == WD_ARM ? 0U :
                           s_watchdog.phase == WD_ZERO ? 1U : 2U;
    if (seq != s_watchdog.seq[index]) return false;
    const bool expected = op == (index == 0U ? WIFI_CONTROL_OP_ARM : WIFI_CONTROL_OP_CMD) &&
        (index < 2U ? ack : (!ack && code != NULL && strcmp(code, "NOT_ARMED") == 0));
    if (!expected || s_watchdog.replied || now < s_watchdog.sent_ms ||
        now - s_watchdog.sent_ms >= WIFI_CONTROL_ACK_MS || t_ms < s_watchdog.last_t_ms) {
        wifi_watchdog_stop_locked("BAD_OR_LATE_REPLY", now);
    } else {
        s_watchdog.replied = true;
        s_watchdog.ack_t_ms = t_ms;
        if (index == 1U) s_watchdog.cmd_t_ms = t_ms;
        ESP_LOGI(TAG, "AC-S06: reply step=%u seq=%" PRIu32 " %s t_ms=%" PRIu32,
                 index, seq, ack ? "ACK" : "NOT_ARMED", t_ms);
    }
    return true;
}

/* Same UART task as production, fixed zero frames only, no retries or auto re-arm.
 * The production owner remains IDLE: its early source-loss DISARM would otherwise
 * preempt the STM's 300 ms watchdog. Normal ingress/tickets stay disabled in mode 3. */
static void wifi_watchdog_step(void)
{
    char frame[WIFI_CONTROL_UART_FRAME_SIZE];
    int length = 0, index = -1;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const uint64_t now = wifi_control_now();
    const stm_telemetry_t *t = &s_stm_telemetry;
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), now);
    wifi_control_cleanup_locked();
    if (s_uart_test_phase == UART_TEST_QUEUED) {
        if (now < s_uart_test_at_ms || now - s_uart_test_at_ms >= WIFI_CONTROL_QUEUE_MS ||
            !wifi_uart_test_ready_locked(now) || strcmp(t->state, "DISARMED") != 0 ||
            t->err == UINT32_MAX || t->t_ms > UINT32_MAX - 2000U) {
            s_uart_test_phase = UART_TEST_ABORTED;
            ESP_LOGW(TAG, "AC-S06: not sent (expired/not ready/counter boundary)");
        } else {
            memset(&s_watchdog, 0, sizeof(s_watchdog));
            bool allocated = true;
            for (unsigned i = 0U; i < 3U && allocated; ++i)
                allocated = wifi_uart_test_sequence_locked(&s_watchdog.seq[i]);
            if (!allocated) {
                s_uart_test_phase = UART_TEST_ABORTED;
                ESP_LOGW(TAG, "AC-S06: not sent (sequence exhausted)");
            } else {
                s_watchdog.started_ms = now;
                s_watchdog.baseline_seq = t->last_seq;
                s_watchdog.drop = t->drop; s_watchdog.err = t->err;
                s_watchdog.last_t_ms = t->t_ms;
                s_uart_test_phase = UART_TEST_HOLD;
                index = 0;
            }
        }
    } else if (s_uart_test_phase == UART_TEST_HOLD) {
        const bool armed = strcmp(t->state, "ARMED") == 0;
        const bool timed_out = strcmp(t->state, "DISARMED") == 0 &&
            strcmp(t->reason, "CMD_TIMEOUT") == 0 && t->last_seq == s_watchdog.seq[1] &&
            t->t_ms >= s_watchdog.cmd_t_ms &&
            t->command_age_ms >= 300U && t->command_age_ms != UINT32_MAX;
        /* command_age_ms is measured from CMD acceptance. ACK t_ms can be a
         * later HAL tick; subtracting it would falsely reject the 300 ms edge. */
        const bool probing = s_watchdog.phase == WD_PROBE || s_watchdog.phase == WD_OBSERVE;
        if (!wifi_control_ready_locked() || s_control.state.phase != WIFI_CONTROL_IDLE ||
            s_manual_stop_pending || s_wifi_command_owner_session_id != 0U ||
            s_control.queued || s_control.waiting || s_control.prepared || s_control.have_result ||
            !wifi_watchdog_zero_locked(now) || now < s_watchdog.started_ms ||
            now - s_watchdog.started_ms >= 2000U || t->t_ms < s_watchdog.last_t_ms ||
            t->drop != s_watchdog.drop ||
            (t->err != s_watchdog.err && (!probing || t->err != s_watchdog.err + 1U))) {
            wifi_watchdog_stop_locked("STATE_FRESHNESS_OUTPUT_OR_COUNTER", now);
        } else {
            s_watchdog.last_t_ms = t->t_ms;
            const bool tel_after_tx = s_stm_tel_count != s_watchdog.tel_floor &&
                t->rx_ms >= s_watchdog.sent_ms && t->t_ms >= s_watchdog.ack_t_ms;
            if ((s_watchdog.phase == WD_ARM || s_watchdog.phase == WD_ZERO ||
                 s_watchdog.phase == WD_PROBE) && !s_watchdog.replied &&
                now - s_watchdog.sent_ms >= WIFI_CONTROL_ACK_MS) {
                wifi_watchdog_stop_locked("REPLY_TIMEOUT", now);
            } else if (s_watchdog.phase == WD_ARM) {
                if ((armed && (t->last_seq != s_watchdog.seq[0] || strcmp(t->reason, "NONE") != 0)) ||
                    (!armed && t->last_seq != s_watchdog.baseline_seq))
                    wifi_watchdog_stop_locked("ARM_STATE_MISMATCH", now);
                else if (s_watchdog.replied && tel_after_tx && armed) index = 1;
                else if (now - s_watchdog.sent_ms >= 250U)
                    wifi_watchdog_stop_locked("ARM_TEL_TIMEOUT", now);
            } else if (s_watchdog.phase == WD_ZERO) {
                if (!armed || strcmp(t->reason, "NONE") != 0 ||
                    (t->last_seq != s_watchdog.seq[0] && t->last_seq != s_watchdog.seq[1]))
                    wifi_watchdog_stop_locked("ZERO_STATE_MISMATCH", now);
                else if (s_watchdog.replied && tel_after_tx && t->last_seq == s_watchdog.seq[1] &&
                         t->command_age_ms < 300U) {
                    s_watchdog.phase = WD_TIMEOUT;
                    ESP_LOGI(TAG, "AC-S06: zero accepted; waiting CMD_TIMEOUT seq=%" PRIu32, t->last_seq);
                } else if (now - s_watchdog.sent_ms >= 250U)
                    wifi_watchdog_stop_locked("ZERO_TEL_TIMEOUT", now);
            } else if (s_watchdog.phase == WD_TIMEOUT) {
                if (timed_out) {
                    ESP_LOGI(TAG, "AC-S06: CMD_TIMEOUT seq=%" PRIu32 " age=%" PRIu32,
                             t->last_seq, t->command_age_ms);
                    index = 2;
                } else if (!armed || t->last_seq != s_watchdog.seq[1] ||
                           strcmp(t->reason, "NONE") != 0 || t->command_age_ms >= 300U ||
                           now - s_watchdog.sent_ms >= 700U)
                    wifi_watchdog_stop_locked("EXPECTED_CMD_TIMEOUT_MISSING", now);
            } else if (probing) {
                if (!timed_out) wifi_watchdog_stop_locked("CMD_REARMED_OR_STATE_CHANGED", now);
                else if (s_watchdog.phase == WD_PROBE && s_watchdog.replied && tel_after_tx &&
                         t->err == s_watchdog.err + 1U) {
                    s_watchdog.phase = WD_OBSERVE;
                    s_watchdog.observed_ms = now;
                    s_watchdog.tel_floor = s_stm_tel_count;
                } else if (s_watchdog.phase == WD_PROBE && now - s_watchdog.sent_ms >= 250U)
                    wifi_watchdog_stop_locked("REJECTION_TEL_TIMEOUT", now);
                else if (s_watchdog.phase == WD_OBSERVE && t->err != s_watchdog.err + 1U)
                    wifi_watchdog_stop_locked("ERROR_COUNTER_CHANGED", now);
                else if (s_watchdog.phase == WD_OBSERVE && now - s_watchdog.observed_ms >= 200U &&
                         s_stm_tel_count - s_watchdog.tel_floor >= 2U) {
                    s_watchdog.proof = true;
                    wifi_watchdog_stop_locked(NULL, now);
                }
            }
        }
    } else if (s_uart_test_phase == UART_TEST_STOPPING &&
               (s_control.state.phase == WIFI_CONTROL_IDLE || s_control.state.phase == WIFI_CONTROL_BLOCKED)) {
        const bool stopped = s_control.state.phase == WIFI_CONTROL_IDLE &&
            wifi_watchdog_zero_locked(now) && strcmp(t->state, "DISARMED") == 0 &&
            strcmp(t->reason, "DISARM") == 0 && t->last_seq == s_control.state.confirm_seq &&
            t->t_ms >= s_watchdog.last_t_ms && t->drop == s_watchdog.drop &&
            t->err == s_watchdog.err + 1U;
        s_watchdog.stop_confirmed = stopped;
        if (!stopped && s_watchdog.problem == NULL) s_watchdog.problem = "CLEANUP_UNCONFIRMED";
        s_uart_test_phase = UART_TEST_DONE;
        ESP_LOGI(TAG, "AC-S06: end checks_ok=%u stop_confirmed=%u problem=%s; capture and manual re-arm review required",
            s_watchdog.proof && s_watchdog.problem == NULL && stopped ? 1U : 0U,
            stopped ? 1U : 0U, s_watchdog.problem != NULL ? s_watchdog.problem : "NONE");
    }
    if (index >= 0 && s_uart_test_phase == UART_TEST_HOLD) {
        s_watchdog.phase = index == 0 ? WD_ARM : index == 1 ? WD_ZERO : WD_PROBE;
        s_watchdog.replied = false; s_watchdog.ack_t_ms = 0U;
        s_watchdog.sent_ms = now; s_watchdog.tel_floor = s_stm_tel_count;
        length = index == 0 ? snprintf(frame, sizeof(frame), "ARM,seq=%" PRIu32 "\n", s_watchdog.seq[index]) :
            snprintf(frame, sizeof(frame), "CMD,seq=%" PRIu32 ",vx_mmps=0,w_mradps=0,timeout_ms=300\n", s_watchdog.seq[index]);
        if (length <= 0 || (size_t)length >= sizeof(frame)) {
            length = 0; wifi_watchdog_stop_locked("FORMAT_FAILED", now);
        }
    }
    xSemaphoreGive(s_stm_lock);
    if (length <= 0) return;
    /* A concurrent manual stop cannot retract this committed frame. The existing
     * priority CAN+LF/DISARM follows; no subsequent test frame is committed. */
    const int written = uart_write_bytes(STM_UART_PORT, frame, (size_t)length);
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    if (written != length && s_uart_test_phase == UART_TEST_HOLD)
        wifi_watchdog_stop_locked("SHORT_WRITE", wifi_control_now());
    xSemaphoreGive(s_stm_lock);
    ESP_LOGI(TAG, "AC-S06: TX step=%d seq=%" PRIu32 " written=%d/%d", index,
             s_watchdog.seq[index], written, length);
}
