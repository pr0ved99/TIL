/* Saved main adapter and control modules, native PC mocks only. */
static void non_owner_arm_case(unsigned mode)
{
    setup();
    wifi_ws_session_t *other=wifi_ws_session_get(&second);
    CHECK(other!=NULL && other->id!=client->id);
    char json[320],input[128];
    CHECK(wifi_control_snapshot(other,json,sizeof(json))>0 && other->ticket.valid);
    const uint32_t old_ticket=other->ticket.id;
    const uint64_t expiry=other->ticket.expires_ms;
    offer();wifi_command_request_t r=request(WIFI_COMMAND_ARM,1);
    CHECK(admit(client,&r)==NULL);wifi_control_step();
    mock_now_ms+=20;ack("ARM",102);offer();r=request(WIFI_COMMAND_CMD,2);
    CHECK(admit(client,&r)==NULL);wifi_control_step();
    mock_now_ms+=20;ack("CMD",103);
    mock_now_ms+=20;tel_at(WIFI_CONTROL_STM_ARMED,103,40);
    CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
    CHECK(wifi_control_snapshot(other,json,sizeof(json))>0);
    CHECK(strstr(json,"\"purpose\":\"NONE\"") && !other->ticket.valid);
    if(mode==1)mock_now_ms+=100;
    CHECK(mode==1 ? mock_now_ms>=expiry : mock_now_ms<expiry);
    mock_now_ms+=20;tel_at(WIFI_CONTROL_STM_ARMED,103,60);offer();
    wifi_command_request_t next=request(WIFI_COMMAND_CMD,3);
    if(mode==2)CHECK(admit(client,&next)==NULL);
    const unsigned writes=mock_write_count;
    const uint32_t owner_control=s_control.state.owner.control_id;
    snprintf(input,sizeof(input),"ARM,boot_id=%" PRIu32 ",request_id=1,ticket=%" PRIu32,s_boot_id,old_ticket);
    mock_ws_input=input;CHECK(ws_receive(&second)==0);
    CHECK(strstr(mock_ws_output,"\"stage\":\"REJECTED\""));
    CHECK(strstr(mock_ws_output,mode==2?"BUSY":"TICKET_REJECTED"));
    CHECK(mock_write_count==writes && other->last_request_id==0);
    CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
    CHECK(s_control.state.owner.ws_session_id==client->id && s_control.state.owner.control_id==owner_control);
    if(mode!=2)CHECK(admit(client,&next)==NULL);
    wifi_control_step();CHECK(mock_write_count==writes+1 && strncmp(mock_uart_line,"CMD,seq=104,",12)==0);
    mock_now_ms+=20;ack("CMD",104);result_is(2,"OK",3,client->id,104);
    mock_now_ms+=20;tel_at(WIFI_CONTROL_STM_ARMED,104,20);
    CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
    wifi_ws_session_free(other);second.sess_ctx=NULL;
    CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
}
int main(void)
{
    non_owner_arm_case(0);puts("PASS B ARM with revoked but not yet expired IDLE ticket: UART ARM TX0, A owner/CMD preserved");
    non_owner_arm_case(1);puts("PASS B ARM with expired/revoked IDLE ticket: UART ARM TX0, A owner/CMD preserved");
    non_owner_arm_case(2);puts("PASS B ARM while A queued CMD: BUSY, A queued CMD preserved; not ticket-specific evidence");
    return 0;
}
