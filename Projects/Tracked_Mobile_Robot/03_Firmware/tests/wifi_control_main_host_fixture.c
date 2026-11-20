/* Adapter scenarios use real candidate functions and saved modules. */
static httpd_req_t first, second;
static wifi_ws_session_t *client;

static void tel_at(wifi_control_stm_state_t state, uint32_t seq, uint32_t age)
{
    wifi_control_tel_t tel = {.state=state, .t_ms=(uint32_t)mock_now_ms,
        .last_seq=seq, .command_age_ms=age};
    wifi_control_executor_tel(&s_control,&tel,mock_now_ms);
}
static void setup(void)
{
    reset_fixture(); first=(httpd_req_t){0}; second=(httpd_req_t){0};
    client=wifi_ws_session_get(&first); CHECK(client != NULL);
    tel_at(WIFI_CONTROL_STM_DISARMED,0,UINT32_MAX);
}
static wifi_command_request_t request(wifi_command_type_t type, uint32_t id)
{
    wifi_command_request_t r={.type=type,.request_id=id,.expected_boot_id=s_boot_id};
    r.control=(wifi_control_request_t){.type=type==WIFI_COMMAND_ARM?WIFI_CONTROL_ARM:WIFI_CONTROL_CMD,
        .expected_boot_id=s_boot_id,.request_id=id,.ticket=client->ticket.id,
        .control_id=type==WIFI_COMMAND_CMD?s_control.state.owner.control_id:0};
    return r;
}
static const char *admit(wifi_ws_session_t *session,wifi_command_request_t *r)
{
    xSemaphoreTake(s_stm_lock,portMAX_DELAY);
    const char *error=wifi_command_admit_locked(session,r);
    xSemaphoreGive(s_stm_lock); return error;
}
static void offer(void)
{
    char json[320];CHECK(wifi_control_snapshot(client,json,sizeof(json))>0);
}
static void arm_start(void)
{
    setup(); offer(); CHECK(client->ticket.valid);
    wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);
    CHECK(admit(client,&r)==NULL); wifi_control_step();
    CHECK(strcmp(mock_uart_line,"ARM,seq=102\n")==0);
    CHECK(s_control.state.phase==WIFI_CONTROL_ARM_PENDING);
}
static void ack(const char *type,uint32_t seq)
{
    char line[96]; snprintf(line,sizeof(line),"ACK,seq=%" PRIu32 ",type=%s,t_ms=%" PRIu64,seq,type,mock_now_ms);
    CHECK(wifi_control_handle_response(line));
}
static void zero_start(void)
{
    arm_start();mock_now_ms+=20;ack("ARM",102);
    CHECK(s_control.state.phase==WIFI_CONTROL_ZERO_PENDING);
    offer();wifi_command_request_t r=request(WIFI_COMMAND_CMD,2);
    CHECK(admit(client,&r)==NULL);wifi_control_step();
    CHECK(strstr(mock_uart_line,"vx_mmps=0,w_mradps=0,timeout_ms=300")!=NULL);
    mock_now_ms+=20;ack("CMD",103);
    CHECK(s_control.state.phase==WIFI_CONTROL_ZERO_PENDING);
    mock_now_ms+=20;tel_at(WIFI_CONTROL_STM_ARMED,103,40);
    CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
}
static void adapter_normal_and_stop(void)
{
    zero_start();CHECK(mock_results[0].control_id==1 && mock_results[1].control_id==1);
    wifi_command_request_t r=request(WIFI_COMMAND_DISARM,3);
    CHECK(admit(client,&r)==NULL);CHECK(!client->ticket.valid);
    wifi_control_step();CHECK(strcmp(mock_uart_line,EXPECT_STOP_PREFIX "DISARM,seq=104\n")==0);
    mock_now_ms+=20;ack("DISARM",104);CHECK(s_manual_stop_pending);
    CHECK(mock_result_count==2);mock_now_ms+=20;tel_at(WIFI_CONTROL_STM_DISARMED,104,UINT32_MAX);
    wifi_control_step();CHECK(!s_manual_stop_pending && s_control.state.phase==WIFI_CONTROL_IDLE);
    result_is(2,"OK",3,client->id,104);
}
static void adapter_closed_queued(void)
{
    setup();offer();wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);CHECK(admit(client,&r)==NULL);
    const uint32_t old=client->id;wifi_ws_session_free(client);first.sess_ctx=NULL;
    wifi_control_step();CHECK(mock_write_count==1);CHECK(strncmp(mock_uart_line,"ARM,",4)!=0);
    CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);CHECK(s_control.state.owner.ws_session_id==0);
    client=wifi_ws_session_get(&first);CHECK(client->id!=old);CHECK(!client->ticket.valid);
}
static void adapter_expired_queue(void)
{
    setup();offer();wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);CHECK(admit(client,&r)==NULL);
    mock_now_ms+=50;wifi_control_step();CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);
    result_is(0,"QUEUE_EXPIRED",1,client->id,0);CHECK(!client->ticket.valid);
}
static void adapter_expired_ticket(void)
{
    setup();offer();wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);
    mock_now_ms+=150;CHECK(strcmp(admit(client,&r),"TICKET_REJECTED")==0);
    wifi_control_step();CHECK(mock_write_count==0 && client->last_request_id==0);
}
static void adapter_priority_stop(void)
{
    setup();wifi_command_request_t p=request(WIFI_COMMAND_PING,1);CHECK(admit(client,&p)==NULL);
    wifi_command_request_t d=request(WIFI_COMMAND_DISARM,2);CHECK(admit(client,&d)==NULL);
    CHECK(!mock_request_present && s_wifi_command_owner_session_id==0);
    wifi_control_step();wifi_command_step();CHECK(mock_write_count==1 && strstr(mock_uart_line,"DISARM,")!=NULL);
    CHECK(strcmp(admit(client,&d),"DUPLICATE")==0);
}
static void adapter_response_identity(void)
{
    arm_start();CHECK(!wifi_control_handle_response("ACK,seq=103,type=ARM,t_ms=1001"));
    CHECK(!wifi_control_handle_response("ACK,seq=102,type=CMD,t_ms=1001"));
    CHECK(!wifi_control_handle_response("ACK,seq=102,type=ARM,t_ms=1001,extra=1"));
    CHECK(!wifi_control_handle_response("ACK,seq=102,type=ARM,seq=102"));
    CHECK(mock_result_count==0);mock_now_ms+=20;ack("ARM",102);CHECK(mock_result_count==1);
    CHECK(!wifi_control_handle_response("ACK,seq=102,type=ARM,t_ms=1020"));
}
static void adapter_source_timeout(void)
{
    zero_start();mock_now_ms=1220;tel_at(WIFI_CONTROL_STM_ARMED,103,200);wifi_control_step();
    CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING && s_control.state.owner.ws_session_id==0);
    CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);CHECK(!client->ticket.valid);
}
static void adapter_unrelated_close(void)
{
    zero_start();wifi_ws_session_t *other=wifi_ws_session_get(&second);CHECK(other!=NULL);
    wifi_ws_session_free(other);CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
    wifi_control_transport_lost();CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING);
    wifi_control_step();CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);
}
static void adapter_output_backpressure(void)
{
    arm_start();mock_result_queue_full=true;mock_now_ms+=20;ack("ARM",102);
    CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING);wifi_control_step();
    CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);
}
static void close_during_write(void){mock_write_hook=NULL;wifi_control_closed(client->id);}
static void adapter_commit_boundary(void)
{
    setup();offer();wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);CHECK(admit(client,&r)==NULL);
    mock_write_hook=close_during_write;wifi_control_step();CHECK(strstr(mock_uart_line,"ARM,")!=NULL);
    CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING);wifi_control_step();
    CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);CHECK(mock_write_count==2 && mock_lock_depth==0);
}
static void adapter_partial_write(void)
{
    setup();offer();wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);CHECK(admit(client,&r)==NULL);
    mock_short_write=true;wifi_control_step();CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING);
    mock_short_write=false;wifi_control_step();
    CHECK(strncmp(mock_uart_line,EXPECT_SHORT_TX_PREFIX,strlen(EXPECT_SHORT_TX_PREFIX))==0);
    CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);result_is(0,"TX_ERROR",1,client->id,102);
}
static void adapter_fault_stale_and_zero(void)
{
    setup();tel_at(WIFI_CONTROL_STM_FAULT,0,UINT32_MAX);offer();CHECK(!client->ticket.valid);
    mock_now_ms+=1;tel_at(WIFI_CONTROL_STM_DISARMED,0,UINT32_MAX);offer();CHECK(client->ticket.valid);
    mock_now_ms+=250;offer();CHECK(!client->ticket.valid);
    mock_now_ms+=1;tel_at(WIFI_CONTROL_STM_DISARMED,0,UINT32_MAX);offer();
    wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);CHECK(admit(client,&r)==NULL);wifi_control_step();
    mock_now_ms+=20;ack("ARM",102);offer();r=request(WIFI_COMMAND_CMD,2);r.control.vx_mmps=1;
    CHECK(strcmp(admit(client,&r),"BAD_INPUT")==0);CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING);
}
static void adapter_rate_boot_and_session(void)
{
    zero_start();offer();wifi_command_request_t r=request(WIFI_COMMAND_CMD,3);
    CHECK(strcmp(admit(client,&r),"RATE_LIMIT")==0);CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
    mock_now_ms+=20;r.expected_boot_id=456;CHECK(strcmp(admit(client,&r),"BOOT_MISMATCH")==0);
    CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
    wifi_ws_session_t *other=wifi_ws_session_get(&second);r.expected_boot_id=123;
    CHECK(admit(other,&r)!=NULL);CHECK(s_control.state.owner.ws_session_id==client->id);
}
static void adapter_stop_unconfirmed(void)
{
    setup();wifi_command_request_t r=request(WIFI_COMMAND_DISARM,1);CHECK(admit(client,&r)==NULL);wifi_control_step();
    mock_now_ms+=150;wifi_control_step();CHECK(s_control.state.phase==WIFI_CONTROL_BLOCKED);
    result_is(0,"STOP_UNCONFIRMED",1,client->id,102);CHECK(mock_write_count==1);
    mock_now_ms+=1000;wifi_control_step();CHECK(mock_write_count==1);
}
static void adapter_sequence_exhaustion(void)
{
    setup();s_wifi_uart_next_seq=0;offer();wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);
    CHECK(admit(client,&r)==NULL);wifi_control_step();CHECK(strstr(mock_uart_line,"seq=0\n")!=NULL);
    setup();s_wifi_uart_next_seq=(uint64_t)UINT32_MAX+1U;offer();r=request(WIFI_COMMAND_ARM,1);
    CHECK(admit(client,&r)==NULL);wifi_control_step();CHECK(mock_write_count==0);
    mock_now_ms+=150;wifi_control_step();CHECK(s_control.state.phase==WIFI_CONTROL_BLOCKED);
}
static void adapter_http_hello_and_arm(void)
{
    setup();mock_ws_input="HELLO";CHECK(ws_receive(&first)==0);CHECK(mock_write_count==0 && !mock_request_present);
    offer();char input[128];snprintf(input,sizeof(input),"ARM,boot_id=123,request_id=1,ticket=%" PRIu32,client->ticket.id);
    mock_ws_input=input;CHECK(ws_receive(&first)==0);CHECK(strstr(mock_ws_output,"ACCEPTED")!=NULL);
    CHECK(mock_write_count==0);wifi_control_step();CHECK(strcmp(mock_uart_line,"ARM,seq=102\n")==0);
    mock_now_ms+=20;ack("ARM",102);mock_network_count=0;ws_command_results(NULL);
    CHECK(mock_network_count==1 && strstr(mock_ws_output,"\"control_id\":1")!=NULL);
    CHECK(strstr(mock_ws_output,"\"status\":\"OK\"")!=NULL);
}
static void adapter_http_bad_and_boot(void)
{
    zero_start();mock_ws_input="ARM,boot_id=999,request_id=3,ticket=99";CHECK(ws_receive(&first)==0);
    CHECK(strstr(mock_ws_output,"BOOT_MISMATCH")!=NULL && s_control.state.phase==WIFI_CONTROL_ACTIVE);
    mock_ws_input="PING";CHECK(ws_receive(&first)==0);CHECK(strstr(mock_ws_output,"BAD_FORMAT")!=NULL);
    CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING);wifi_control_step();CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);
}
static void adapter_http_send_failure(void)
{
    setup();offer();char input[128];snprintf(input,sizeof(input),"ARM,boot_id=123,request_id=1,ticket=%" PRIu32,client->ticket.id);
    mock_ws_input=input;mock_ws_send_fail=true;CHECK(ws_receive(&first)==-1);
    CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING);wifi_control_step();CHECK(strncmp(mock_uart_line,"ARM,",4)!=0);
}
static void adapter_http_result_target(void)
{
    arm_start();mock_now_ms+=20;ack("ARM",102);
    wifi_ws_session_free(client);first.sess_ctx=NULL;client=wifi_ws_session_get(&first);
    mock_network_count=0;ws_command_results(NULL);CHECK(mock_network_count==0);
}
static void adapter_http_unsupported(void)
{
    setup();mock_ws_input="HELLO";mock_ws_final=false;CHECK(ws_receive(&first)==-1);
    mock_ws_final=true;mock_ws_type=2;CHECK(ws_receive(&first)==-1);
    char large[130];memset(large,'X',129);large[129]=0;mock_ws_input=large;mock_ws_type=HTTPD_WS_TYPE_TEXT;
    CHECK(ws_receive(&first)==-1);CHECK(mock_write_count==0 && mock_network_count==0);
}
static void adapter_late_manual_stop(void)
{
    arm_start();wifi_control_closed(client->id);wifi_control_step();mock_now_ms+=20;ack("DISARM",103);
    CHECK(s_control.state.stop_ack);wifi_command_request_t r=request(WIFI_COMMAND_DISARM,2);CHECK(admit(client,&r)==NULL);
    CHECK(s_manual_stop_seq==103);mock_now_ms+=20;tel_at(WIFI_CONTROL_STM_DISARMED,103,UINT32_MAX);
    wifi_control_step();result_is(1,"OK",2,client->id,103);
}
int main(int argc,char **argv)
{
    struct {const char *name;void (*run)(void);} cases[]={
        {"adapter_normal_and_stop",adapter_normal_and_stop},
        {"adapter_closed_queued",adapter_closed_queued},
        {"adapter_expired_queue",adapter_expired_queue},
        {"adapter_expired_ticket",adapter_expired_ticket},
        {"adapter_priority_stop",adapter_priority_stop},
        {"adapter_response_identity",adapter_response_identity},
        {"adapter_source_timeout",adapter_source_timeout},
        {"adapter_unrelated_close",adapter_unrelated_close},
        {"adapter_output_backpressure",adapter_output_backpressure},
        {"adapter_commit_boundary",adapter_commit_boundary},
        {"adapter_partial_write",adapter_partial_write},
        {"adapter_fault_stale_and_zero",adapter_fault_stale_and_zero},
        {"adapter_rate_boot_and_session",adapter_rate_boot_and_session},
        {"adapter_stop_unconfirmed",adapter_stop_unconfirmed},
        {"adapter_sequence_exhaustion",adapter_sequence_exhaustion},
        {"adapter_http_hello_and_arm",adapter_http_hello_and_arm},
        {"adapter_http_bad_and_boot",adapter_http_bad_and_boot},
        {"adapter_http_send_failure",adapter_http_send_failure},
        {"adapter_http_result_target",adapter_http_result_target},
        {"adapter_http_unsupported",adapter_http_unsupported},
        {"adapter_late_manual_stop",adapter_late_manual_stop}
    };
    CHECK(argc==2);
    for(size_t i=0;i<sizeof(cases)/sizeof(cases[0]);++i) if(strcmp(argv[1],cases[i].name)==0){
        cases[i].run();printf("PASS %s\n",cases[i].name);return 0;
    }
    return w5_main(argc,argv);
}
