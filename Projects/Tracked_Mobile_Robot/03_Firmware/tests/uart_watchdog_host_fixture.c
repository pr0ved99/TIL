/* Wire both actual parsers and state machines; replace only I/O and time.
 * No success can be inferred from this fixture without the physical capture. */
static char bench_writes[16][128];
static unsigned bench_count;
static bool drop_ack, drop_tel, wrong_probe_ack, drop_stop;
static bool cmd_ack_next_tick;

static void bench_wire(const void *data, size_t length)
{
    CHECK(bench_count < 16 && length < sizeof(bench_writes[0]));
    memcpy(bench_writes[bench_count], data, length);
    bench_writes[bench_count][length] = 0;
    const char *text = bench_writes[bench_count++];
    if (drop_stop && text[0] == 0x18) return;
    host_ms = (uint32_t)mock_now_ms;
    feed(text);
}

static void receive_wire(void)
{
    char copy[32768]; memcpy(copy, host_tx, host_tx_len+1); clear_tx();
    char *p = copy;
    while (*p) {
        char *end = strchr(p, '\n'); CHECK(end != NULL); *end = 0;
        if ((!drop_ack || strncmp(p,"ACK,",4)) && (!drop_tel || strncmp(p,"TEL,",4))) {
            if (wrong_probe_ack && strstr(p,"code=NOT_ARMED")) {
                char fake[100]; snprintf(fake,sizeof(fake),"ACK,seq=%" PRIu32 ",type=CMD,t_ms=%u",
                                         s_watchdog.seq[2],host_ms);
                stm_uart_handle_line(fake);
            } else if (cmd_ack_next_tick && strncmp(p,"ACK,",4)==0 && strstr(p,"type=CMD,")) {
                char shifted[100]; snprintf(shifted,sizeof(shifted),"ACK,seq=%" PRIu32 ",type=CMD,t_ms=%u",
                                            s_watchdog.seq[1],host_ms+1U);
                stm_uart_handle_line(shifted);
            } else stm_uart_handle_line(p);
        }
        p = end+1;
    }
}

static void bench_setup(void)
{
    setup(); reset_host(); memset(&s_watchdog,0,sizeof(s_watchdog));
    memset(&s_stm_telemetry,0,sizeof(s_stm_telemetry)); s_stm_tel_count = 0;
    bench_count = 0; drop_ack = drop_tel = wrong_probe_ack = drop_stop = false;
    cmd_ack_next_tick = false;
    mock_http_offset = mock_http_chunk = 0; mock_http_recv_fail = false;
    mock_http_status[0] = mock_http_response[0] = 0;
    tick((uint32_t)mock_now_ms); receive_wire();
    CHECK(s_stm_telemetry.valid && s_stm_telemetry.last_seq == 0);
}

static void post_test(const char *body)
{
    httpd_req_t req = {.content_len = strlen(body)};
    mock_http_body = body; mock_http_offset = 0;
    CHECK(wifi_uart_test_post(&req) == ESP_OK);
}
static void begin(void)
{
    bench_setup(); post_test("123");
    CHECK(strcmp(mock_http_status,"202 Accepted") == 0 && bench_count == 0);
    wifi_uart_test_step(); CHECK(bench_count == 1 && s_state == ROBOT_ARMED);
    CHECK(strcmp(bench_writes[0],"ARM,seq=102\n") == 0);
    receive_wire();
}
static void advance(unsigned milliseconds)
{
    for (unsigned i=0;i<milliseconds;i+=10) {
        mock_now_ms += 10; tick((uint32_t)mock_now_ms); receive_wire();
        wifi_uart_test_step(); wifi_control_step(); receive_wire();
    }
}
static void stop_now(void)
{
    mock_write_hook = NULL;
    wifi_command_request_t r = request(WIFI_COMMAND_DISARM,1);
    CHECK(admit(client,&r) == NULL);
}

static void happy_path(void)
{
    begin(); advance(200);
    CHECK(bench_count == 2 && s_state == ROBOT_ARMED && s_last_seq == 103);
    CHECK(s_watchdog.phase == WD_TIMEOUT && !s_watchdog.proof);
    CHECK(s_control.state.phase == WIFI_CONTROL_IDLE); /* Isolated test actor owns UART. */
    advance(200);
    CHECK(bench_count == 3 && s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_CMD_TIMEOUT);
    CHECK(s_last_seq == 103 && s_error_count == 1); /* rejected CMD never updates last_seq */
    CHECK(strcmp(bench_writes[2],"CMD,seq=104,vx_mmps=0,w_mradps=0,timeout_ms=300\n") == 0);
    advance(400);
    CHECK(s_watchdog.proof && s_watchdog.stop_confirmed && s_watchdog.problem == NULL && s_uart_test_phase == UART_TEST_DONE);
    CHECK(bench_count == 4 && strcmp(bench_writes[3],"\x18\nDISARM,seq=105\n") == 0);
    CHECK(s_control.state.phase == WIFI_CONTROL_IDLE && s_state == ROBOT_DISARMED && s_last_seq == 105);
    CHECK(host_output.left_signed_permille == 0 && host_output.right_signed_permille == 0);
    post_test("123"); CHECK(strcmp(mock_http_response,"ALREADY_USED") == 0);
    advance(1000); CHECK(bench_count == 4); /* No autonomous rearm. */
    /* STM permits recovery only after a separate fresh ARM and zero CMD. PC only. */
    feed("CMD,seq=200,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    CHECK(s_state == ROBOT_DISARMED && s_last_seq == 105);
    feed("ARM,seq=201\nCMD,seq=202,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    CHECK(s_state == ROBOT_ARMED && s_last_seq == 202);
    feed("DISARM,seq=203\n"); CHECK(s_state == ROBOT_DISARMED);
    begin(); cmd_ack_next_tick=true; advance(800);
    CHECK(s_watchdog.proof && s_watchdog.stop_confirmed && s_watchdog.problem==NULL);
    puts("PASS real wire path: ARM/zero -> CMD_TIMEOUT -> NOT_ARMED unchanged seq -> observed stop -> cleanup; separate rearm");
}

static void admission_cases(void)
{
    const char *bad[] = {"", "-1", "123x", "4294967296"};
    for(unsigned i=0;i<4;++i){bench_setup();post_test(bad[i]);CHECK(s_uart_test_phase==UART_TEST_UNUSED);}
    bench_setup();post_test("124");CHECK(strcmp(mock_http_response,"BOOT_MISMATCH")==0);
    for(unsigned i=0;i<9;++i){
        bench_setup();
        switch(i){
        case 0: s_stm_telemetry.left_cps=1; break;
        case 1: s_stm_telemetry.right_pwm=1; break;
        case 2: s_stm_telemetry.valid=false; break;
        case 3: mock_now_ms+=250; break;
        case 4: s_stm_telemetry.rx_ms=mock_now_ms+1; break;
        case 5: strcpy(s_stm_telemetry.state,"FAULT"); break;
        case 6: s_stm_startup_status="SETTLE"; break;
        case 7: s_manual_stop_pending=true; break;
        case 8: s_control.state.phase=WIFI_CONTROL_BLOCKED; break;
        }
        post_test("123"); CHECK(strcmp(mock_http_response,"NOT_READY")==0 && bench_count==0);
    }
    bench_setup(); offer(); CHECK(!client->ticket.valid);
    const wifi_command_type_t commands[]={WIFI_COMMAND_PING,WIFI_COMMAND_ARM,WIFI_COMMAND_CMD};
    for(unsigned i=0;i<3;++i){wifi_command_request_t r=request(commands[i],i+1);CHECK(strcmp(admit(client,&r),"BUSY")==0);}
    advance(1000); CHECK(bench_count==0); /* Installation never starts. */
    puts("PASS admission: full telemetry, current boot, normal control disabled, no auto start");
}

static void cancellation_cases(void)
{
    bench_setup(); post_test("123"); stop_now(); wifi_uart_test_step(); wifi_control_step();
    CHECK(s_uart_test_phase==UART_TEST_ABORTED && bench_count==1 && bench_writes[0][0]==0x18);
    bench_setup(); post_test("123"); mock_write_hook=stop_now; wifi_uart_test_step();
    CHECK(bench_count==1 && s_uart_test_phase==UART_TEST_STOPPING);
    wifi_control_step(); receive_wire(); advance(200);
    CHECK(bench_count==2 && s_state==ROBOT_DISARMED && !s_watchdog.proof);
    for(unsigned stage=0;stage<4;++stage){
        begin(); advance(stage*100); wifi_control_transport_lost(); wifi_control_step(); receive_wire(); advance(300);
        CHECK(s_uart_test_phase==UART_TEST_DONE && s_watchdog.problem!=NULL && !s_watchdog.proof);
        CHECK(s_state==ROBOT_DISARMED && bench_writes[bench_count-1][0]==0x18);
    }
    puts("PASS cancellation: queued, committed write race, transport loss across phases");
}

static void failure_cases(void)
{
    bench_setup(); post_test("123"); mock_now_ms+=50; wifi_uart_test_step();
    CHECK(s_uart_test_phase==UART_TEST_ABORTED && bench_count==0);
    bench_setup(); post_test("123"); s_wifi_uart_next_seq=UINT32_MAX-2U; wifi_uart_test_step();
    CHECK(s_uart_test_phase==UART_TEST_ABORTED && bench_count==0); /* Reserve all three plus cleanup. */
    bench_setup(); post_test("123"); s_wifi_uart_next_seq=UINT32_MAX-3U; wifi_uart_test_step();
    receive_wire(); advance(800); CHECK(s_watchdog.proof && s_last_seq==UINT32_MAX);
    begin(); drop_tel=true; advance(400); CHECK(!s_watchdog.proof && s_watchdog.problem!=NULL);
    bench_setup(); post_test("123"); drop_ack=true; wifi_uart_test_step(); receive_wire(); advance(150);
    CHECK(!s_watchdog.proof && s_watchdog.problem!=NULL && s_uart_test_phase==UART_TEST_STOPPING);
    begin(); wrong_probe_ack=true; advance(800);
    CHECK(!s_watchdog.proof && strcmp(s_watchdog.problem,"BAD_OR_LATE_REPLY")==0);
    begin(); advance(200); s_cmd_timeout_ms=2000; advance(700);
    CHECK(!s_watchdog.proof && strcmp(s_watchdog.problem,"EXPECTED_CMD_TIMEOUT_MISSING")==0);
    begin(); host_estop=GPIO_PIN_SET; advance(200);
    CHECK(!s_watchdog.proof && s_state==ROBOT_FAULT && s_watchdog.problem!=NULL);
    for(unsigned i=0;i<5;++i){
        begin();
        switch(i){
        case 0: s_stm_telemetry.left_pwm=1; break;
        case 1: s_stm_telemetry.t_ms=1; break;
        case 2: s_stm_telemetry.drop++; break;
        case 3: s_stm_telemetry.err++; break;
        case 4: mock_now_ms--; break;
        }
        wifi_uart_test_step(); CHECK(s_uart_test_phase==UART_TEST_STOPPING && !s_watchdog.proof);
    }
    for(unsigned frame=0;frame<3;++frame){
        bench_setup(); post_test("123");
        if(frame){wifi_uart_test_step();receive_wire();if(frame==2)advance(300);}
        mock_short_write=true;
        if(frame==0)wifi_uart_test_step();else advance(100);
        CHECK(s_watchdog.problem!=NULL && !s_watchdog.proof);
        mock_short_write=false;advance(400);CHECK(s_state==ROBOT_DISARMED);
    }
    begin(); advance(600); CHECK(s_watchdog.phase==WD_OBSERVE);
    advance(100); CHECK(s_uart_test_phase==UART_TEST_STOPPING);
    mock_now_ms+=100;tick((uint32_t)mock_now_ms);receive_wire(); /* Before final test verdict. */
    CHECK(s_control.state.phase==WIFI_CONTROL_IDLE && s_uart_test_phase==UART_TEST_STOPPING);
    s_stm_telemetry.left_cps=1; wifi_uart_test_step();
    CHECK(!s_watchdog.stop_confirmed && strcmp(s_watchdog.problem,"CLEANUP_UNCONFIRMED")==0);
    begin(); drop_stop=true; advance(1100);
    CHECK(s_watchdog.proof && s_control.state.phase==WIFI_CONTROL_BLOCKED);
    CHECK(!s_watchdog.stop_confirmed && strcmp(s_watchdog.problem,"CLEANUP_UNCONFIRMED")==0);
    CHECK(s_uart_test_phase==UART_TEST_DONE); /* end checks_ok must be false despite earlier proof */
    puts("PASS failures: queue expiry, sequence reserve, missing ACK/TEL, wrong probe ACK, missing watchdog, E-stop, outputs/counters/clock, short writes, cleanup loss");
}

int main(void)
{
    happy_path(); admission_cases(); cancellation_cases(); failure_cases();
    return 0;
}
