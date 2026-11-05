/* Actual candidate HTTP/dispatch + saved ESP executor + actual STM stream.
 * Only time/RTOS/HTTP/serial/GPIO are mocked; no target build or physical I/O. */
static bool drop_stop_wire, lf_only_stop_wire;
static void bench_wire(const void *data, size_t length)
{
    char bytes[128]; CHECK(length < sizeof(bytes));
    memcpy(bytes, data, length); bytes[length] = 0;
    if (bytes[0] == 0x18 && drop_stop_wire) return;
    host_ms = (uint32_t)mock_now_ms;
    feed(bytes + ((bytes[0] == 0x18 && lf_only_stop_wire) ? 1 : 0));
}
static void bench_setup(void)
{
    setup(); reset_host(); tick((uint32_t)mock_now_ms); clear_tx();
    drop_stop_wire = false; lf_only_stop_wire = false;
    mock_http_offset = 0; mock_http_chunk = 0; mock_http_recv_fail = false;
    mock_http_status[0] = 0; mock_http_response[0] = 0;
}
static esp_err_t post_bytes(const char *body, size_t length)
{
    httpd_req_t req = {.content_len = length};
    mock_http_body = body; mock_http_offset = 0;
    return wifi_uart_test_post(&req);
}
static void post_ok(void)
{
    CHECK(post_bytes("123", 3) == ESP_OK);
    CHECK(strcmp(mock_http_status, "202 Accepted") == 0);
    CHECK(s_uart_test_phase == UART_TEST_QUEUED);
}
static void prefix_start(void)
{
    bench_setup(); post_ok(); CHECK(mock_write_count == 0);
    wifi_uart_test_step(); CHECK(mock_write_count == 1);
    CHECK(strcmp(mock_uart_line, WIFI_UART_PARTIAL_TEST_MODE == 1 ? "CMD,seq=" : "ARM,seq=102") == 0);
    CHECK(s_uart_test_phase == UART_TEST_HOLD && s_uart_test_prefix_full);
    CHECK(s_state == ROBOT_DISARMED && s_last_seq == 0 && s_error_count == 0);
    CHECK(strstr(host_tx, "ACK,") == NULL && strstr(host_tx, "ERR,") == NULL);
}
static void feed_stop_ack(void)
{
    const char *p = strstr(host_tx, "ACK,"); CHECK(p != NULL);
    const char *end = strchr(p, '\n'); CHECK(end != NULL);
    char line[128]; size_t n = (size_t)(end - p);
    if (n && p[n-1] == '\r') --n;
    memcpy(line, p, n); line[n] = 0;
    CHECK(wifi_control_handle_response(line));
}
static void fixed_cases(void)
{
    prefix_start();
    mock_now_ms += 99; wifi_uart_test_step(); wifi_control_step();
    CHECK(mock_write_count == 1 && s_state == ROBOT_DISARMED);
    ++mock_now_ms; wifi_uart_test_step(); wifi_control_step();
    CHECK(mock_write_count == 2);
    CHECK(strcmp(mock_uart_line, "\x18\nDISARM,seq=103\n") == 0);
    CHECK(s_state == ROBOT_DISARMED && s_last_seq == 103 && s_error_count == 0);
    CHECK(strstr(host_tx, "type=ARM,") == NULL && strstr(host_tx, "type=CMD,") == NULL);
    CHECK(strstr(host_tx, "ERR,") == NULL);
    CHECK(host_output.left_signed_permille == 0 && host_output.right_signed_permille == 0);
    feed_stop_ack(); wifi_uart_test_step();
    CHECK(s_control.state.phase == WIFI_CONTROL_STOPPING); /* ACK alone is insufficient. */
    ++mock_now_ms; tel_at(WIFI_CONTROL_STM_DISARMED, 102, UINT32_MAX);
    CHECK(s_control.state.phase == WIFI_CONTROL_STOPPING); /* Wrong seq TEL. */
    ++mock_now_ms; tel_at(WIFI_CONTROL_STM_DISARMED, s_last_seq, UINT32_MAX);
    wifi_uart_test_step(); CHECK(s_control.state.phase == WIFI_CONTROL_IDLE);
    CHECK(s_uart_test_phase == UART_TEST_DONE);
    post_bytes("123", 3); CHECK(strcmp(mock_http_response, "ALREADY_USED") == 0);
    mock_now_ms += 1000; wifi_uart_test_step(); CHECK(mock_write_count == 2);
}
static void input_checks(void)
{
    const char *bad[] = {"", "-1", "+123", "123\n", "123x", "4294967296", "12345678901"};
    for (size_t i=0; i<sizeof(bad)/sizeof(bad[0]); ++i) {
        bench_setup(); post_bytes(bad[i], strlen(bad[i]));
        CHECK(strcmp(mock_http_status, "400 Bad Request") == 0 && mock_write_count == 0);
        CHECK(s_uart_test_phase == UART_TEST_UNUSED);
    }
    bench_setup(); post_bytes("123\0x", 5); CHECK(strcmp(mock_http_status, "400 Bad Request") == 0);
    bench_setup(); post_bytes("124", 3); CHECK(strcmp(mock_http_response, "BOOT_MISMATCH") == 0);
    bench_setup(); mock_http_recv_fail = true;
    CHECK(post_bytes("123",3) == ESP_FAIL && s_uart_test_phase == UART_TEST_UNUSED);
    bench_setup(); mock_http_chunk = 1; post_ok();
    post_bytes("123", 3); CHECK(strcmp(mock_http_response, "ALREADY_USED") == 0);
    CHECK(mock_write_count == 0);
}
static void admission_checks(void)
{
    for (unsigned i=0; i<13; ++i) {
        bench_setup();
        switch(i) {
        case 0: s_stm_startup_status = "SETTLE"; break;
        case 1: s_control.state.have_tel = false; break;
        case 2: mock_now_ms += 250; break;
        case 3: s_control.state.tel.state = WIFI_CONTROL_STM_ARMED; break;
        case 4: s_control.state.tel.state = WIFI_CONTROL_STM_FAULT; break;
        case 5: s_control.state.tel.left_pwm = 1; break;
        case 6: s_control.state.tel.w_mradps = 1; break;
        case 7: s_control.state.phase = WIFI_CONTROL_BLOCKED; break;
        case 8: s_manual_stop_pending = true; break;
        case 9: s_wifi_command_owner_session_id = 1; break;
        case 10: s_control.have_result = true; break;
        case 11: s_control.prepared = true; break;
        case 12: s_control.state.tel_received_ms = mock_now_ms + 1; break;
        }
        post_bytes("123", 3); CHECK(strcmp(mock_http_response, "NOT_READY") == 0);
        wifi_uart_test_step(); CHECK(mock_write_count == 0 && s_uart_test_phase == UART_TEST_UNUSED);
    }
    bench_setup(); mock_now_ms += 249; post_ok(); /* Freshness boundary. */
    bench_setup(); offer(); CHECK(!client->ticket.valid);
    for (unsigned t=0; t<3; ++t) {
        const wifi_command_type_t types[] = {WIFI_COMMAND_PING, WIFI_COMMAND_ARM, WIFI_COMMAND_CMD};
        wifi_command_request_t r = request(types[t], t+1);
        CHECK(strcmp(admit(client, &r), "BUSY") == 0);
    }
    CHECK(mock_write_count == 0);
    bench_setup(); mock_now_ms += 10000; wifi_uart_test_step(); CHECK(mock_write_count == 0);
}
static void dispatch_checks(void)
{
    bench_setup(); post_ok(); mock_now_ms += 50; wifi_uart_test_step();
    CHECK(mock_write_count == 0 && s_uart_test_phase == UART_TEST_ABORTED);
    post_bytes("123", 3); CHECK(strcmp(mock_http_response, "ALREADY_USED") == 0);
    bench_setup(); post_ok(); mock_now_ms += 49; wifi_uart_test_step(); CHECK(mock_write_count == 1);
    bench_setup(); post_ok(); s_control.state.tel.right_pwm = 1; wifi_uart_test_step();
    CHECK(mock_write_count == 0 && s_uart_test_phase == UART_TEST_ABORTED);
    bench_setup(); post_ok(); s_wifi_uart_next_seq = UINT32_MAX; wifi_uart_test_step();
    CHECK(mock_write_count == 0 && s_uart_test_phase == UART_TEST_ABORTED);
    bench_setup(); post_ok(); s_wifi_uart_next_seq = (uint64_t)UINT32_MAX+1; wifi_uart_test_step();
    CHECK(mock_write_count == 0);
    bench_setup(); post_ok(); s_wifi_uart_next_seq = UINT32_MAX-1;
    s_stm_startup.ping_seq = UINT32_MAX; wifi_uart_test_step(); CHECK(mock_write_count == 0);
    bench_setup(); post_ok(); s_wifi_uart_next_seq = UINT32_MAX-1;
    wifi_uart_test_step(); CHECK(mock_write_count == 1);
    mock_now_ms += 100; wifi_uart_test_step(); wifi_control_step();
    CHECK(mock_write_count == 2 && s_last_seq == UINT32_MAX);
}
static void stop_in_write(void)
{
    mock_write_hook = NULL;
    wifi_command_request_t r = request(WIFI_COMMAND_DISARM, 1);
    CHECK(admit(client, &r) == NULL);
}
static void priority_checks(void)
{
    bench_setup(); post_ok(); stop_in_write(); wifi_uart_test_step(); wifi_control_step();
    CHECK(s_uart_test_phase == UART_TEST_ABORTED && mock_write_count == 1);
    CHECK(strncmp(mock_uart_line, "\x18\nDISARM,", 9) == 0);
    bench_setup(); post_ok(); mock_write_hook = stop_in_write; wifi_uart_test_step();
    CHECK(s_uart_test_phase == UART_TEST_STOPPING && mock_write_count == 1);
    wifi_control_step(); CHECK(mock_write_count == 2 && s_state == ROBOT_DISARMED);
    CHECK(strstr(host_tx,"type=ARM,") == NULL && s_error_count == 0);
    bench_setup(); post_ok(); wifi_control_transport_lost(); wifi_uart_test_step();
    CHECK(mock_write_count == 0 && s_uart_test_phase == UART_TEST_ABORTED);
    prefix_start(); wifi_control_transport_lost(); wifi_control_step();
    CHECK(mock_write_count == 2 && s_uart_test_phase == UART_TEST_STOPPING);
}
static void failure_checks(void)
{
    bench_setup(); post_ok(); mock_short_write = true; wifi_uart_test_step();
    CHECK(!s_uart_test_prefix_full && s_uart_test_phase == UART_TEST_STOPPING);
    mock_short_write = false; wifi_control_step();
    CHECK(mock_write_count == 2 && s_last_seq == 103 && s_error_count == 0);
    prefix_start(); mock_now_ms += 250; wifi_uart_test_step(); wifi_control_step();
    CHECK(mock_write_count == 2 && s_uart_test_phase == UART_TEST_STOPPING);
    prefix_start(); mock_now_ms += 100; wifi_uart_test_step(); drop_stop_wire = true; wifi_control_step();
    CHECK(s_last_seq == 0); /* Actual wire loss, not a fake successful ACK. */
    mock_now_ms += 150; wifi_uart_test_step();
    CHECK(s_control.state.phase == WIFI_CONTROL_BLOCKED && s_uart_test_phase == UART_TEST_DONE);
    mock_now_ms += 1000; wifi_uart_test_step(); wifi_control_step(); CHECK(mock_write_count == 2);
    drop_stop_wire = false; stop_in_write(); wifi_control_step();
    CHECK(mock_write_count == 3 && s_last_seq == 104 && s_error_count == 0);
    CHECK(strstr(host_tx,"type=ARM,") == NULL);
}
static void lf_counterexample(void)
{
    if (WIFI_UART_PARTIAL_TEST_MODE != 2U) return;
    prefix_start(); lf_only_stop_wire = true; mock_now_ms += 100;
    wifi_uart_test_step(); wifi_control_step();
    CHECK(strstr(host_tx, "ACK,seq=102,type=ARM,") != NULL);
    CHECK(s_state == ROBOT_DISARMED && s_last_seq == 103);
    puts("NEGATIVE CONTROL detected: LF-only executes old ARM even though final DISARM succeeds");
}
int main(void)
{
    fixed_cases(); input_checks(); admission_checks(); dispatch_checks();
    priority_checks(); failure_checks(); lf_counterexample();
    printf("PASS mode=%u: fixed bytes/STM cancellation, input, admission, deadlines, priority, failures\n",
           (unsigned)WIFI_UART_PARTIAL_TEST_MODE);
    return 0;
}
