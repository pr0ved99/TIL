/* Appended to the existing host adapter fixture; actual saved C, mocked IO. */
static void other_session_stop_case(unsigned pending_mode)
{
    zero_start();
    wifi_ws_session_t *other=wifi_ws_session_get(&second);
    CHECK(other!=NULL && other->id!=client->id);
    char json[320];
    CHECK(wifi_control_snapshot(other,json,sizeof(json))>0);
    CHECK(strstr(json,"\"phase\":\"ACTIVE\"")!=NULL);
    CHECK(strstr(json,"\"purpose\":\"NONE\"")!=NULL);
    CHECK(!other->ticket.valid);
    CHECK(s_control.state.owner.ws_session_id==client->id);
    unsigned result_index=2;
    uint32_t stop_seq=104;
    if(pending_mode!=0) {
        mock_now_ms+=20;offer();
        wifi_command_request_t cmd=request(WIFI_COMMAND_CMD,3);
        CHECK(admit(client,&cmd)==NULL);
        if(pending_mode==2) {
            wifi_control_step();CHECK(strstr(mock_uart_line,"CMD,seq=104,")!=NULL);
            stop_seq=105;
        }
        result_index=3;
    }
    wifi_command_request_t stop={.type=WIFI_COMMAND_DISARM,.request_id=1,.expected_boot_id=s_boot_id};
    CHECK(admit(other,&stop)==NULL);
    CHECK(s_control.state.owner.ws_session_id==0 && !client->ticket.valid);
    CHECK(s_control.state.phase==WIFI_CONTROL_STOPPING);
    wifi_control_step();
    char expected[64];snprintf(expected,sizeof(expected),EXPECT_STOP_PREFIX "DISARM,seq=%" PRIu32 "\n",stop_seq);
    CHECK(strcmp(mock_uart_line,expected)==0);
    if(pending_mode!=0) result_is(2,"CANCELLED",3,client->id,pending_mode==2?104:0);
    mock_now_ms+=20;ack("DISARM",stop_seq);
    CHECK(s_manual_stop_pending); /* ACK alone is insufficient. */
    mock_now_ms+=20;tel_at(WIFI_CONTROL_STM_DISARMED,stop_seq,UINT32_MAX);
    wifi_control_step();
    CHECK(!s_manual_stop_pending && s_control.state.phase==WIFI_CONTROL_IDLE);
    result_is(result_index,"OK",1,other->id,stop_seq);
    const unsigned writes=mock_write_count;
    for(unsigned i=0;i<31;++i) {
        mock_now_ms+=100;tel_at(WIFI_CONTROL_STM_DISARMED,stop_seq,UINT32_MAX);wifi_control_step();
        CHECK(mock_write_count==writes && s_control.state.phase==WIFI_CONTROL_IDLE);
    }
    wifi_ws_session_free(other);second.sess_ctx=NULL;
    CHECK(s_control.state.phase==WIFI_CONTROL_IDLE);
}
int main(void)
{
    other_session_stop_case(0);puts("PASS other-session DISARM from ACTIVE; result routed to B; ACK plus TEL required");
    other_session_stop_case(1);puts("PASS other-session DISARM cancels A queued CMD before UART");
    other_session_stop_case(2);puts("PASS other-session DISARM cancels A pending ACK and follows in-flight CMD");
    puts("PASS no automatic ARM/CMD during 3.1 seconds after each confirmed stop");
    return 0;
}
