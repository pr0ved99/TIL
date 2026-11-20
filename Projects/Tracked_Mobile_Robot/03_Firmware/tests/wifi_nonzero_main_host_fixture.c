/* Appended to the existing real-main adapter host translation unit. */
static void nz_snapshot(void)
{
    setup(); char json[320];
    CHECK(wifi_control_snapshot(client,json,sizeof(json))>0);
    CHECK(strstr(json,WIFI_CONTROL_ZERO_ONLY?"\"zero_only\":true":"\"zero_only\":false")!=NULL);
}
static void nz_receive(httpd_req_t *req,uint32_t id,uint32_t ticket,int32_t vx,int32_t w)
{
    char text[128];
    snprintf(text,sizeof(text),"CMD,boot_id=%" PRIu32 ",request_id=%" PRIu32
        ",control_id=%" PRIu32 ",ticket=%" PRIu32 ",vx_mmps=%" PRIi32 ",w_mradps=%" PRIi32,
        s_boot_id,id,s_control.state.owner.control_id,ticket,vx,w);
    mock_ws_input=text;CHECK(ws_receive(req)==ESP_OK);mock_ws_input=NULL;
}
static void nz_first_zero(void)
{
    arm_start();mock_now_ms+=20;ack("ARM",102);offer();
    nz_receive(&first,2,client->ticket.id,50,0);
    CHECK(strstr(mock_ws_output,"REJECTED")!=NULL);
    wifi_control_step();CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);
}
static void nz_wire(void)
{
    zero_start();mock_now_ms+=20;offer();nz_receive(&first,3,client->ticket.id,50,-250);
    if(WIFI_CONTROL_ZERO_ONLY){
        CHECK(strstr(mock_ws_output,"BAD_INPUT")!=NULL);wifi_control_step();
        CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);return;
    }
    CHECK(strstr(mock_ws_output,"ACCEPTED")!=NULL);
    CHECK(s_control.request.vx_mmps==50 && s_control.request.w_mradps==-250);
    wifi_control_step();CHECK(strcmp(mock_uart_line,"CMD,seq=104,vx_mmps=50,w_mradps=-250,timeout_ms=300\n")==0);
    mock_now_ms+=20;ack("CMD",104);mock_now_ms+=20;
    wifi_control_tel_t t={.state=WIFI_CONTROL_STM_ARMED,.t_ms=(uint32_t)mock_now_ms,
        .last_seq=104,.command_age_ms=40,.vx_mmps=50,.w_mradps=-250,.left_pwm=100,.right_pwm=-50};
    wifi_control_executor_tel(&s_control,&t,mock_now_ms);
    CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
    mock_now_ms+=20;offer();nz_receive(&first,4,client->ticket.id,0,0);wifi_control_step();
    CHECK(strcmp(mock_uart_line,"CMD,seq=105,vx_mmps=0,w_mradps=0,timeout_ms=300\n")==0);
    mock_now_ms+=20;ack("CMD",105);mock_now_ms+=20;tel_at(WIFI_CONTROL_STM_ARMED,105,40);
    CHECK(s_control.state.phase==WIFI_CONTROL_ACTIVE);
}
static void nz_expired_ticket(void)
{
    zero_start();offer();const uint32_t ticket=client->ticket.id;
    const unsigned count=mock_write_count;mock_now_ms+=150;
    nz_receive(&first,3,ticket,50,0);
    CHECK(strstr(mock_ws_output,"REJECTED")!=NULL);wifi_control_step();
    CHECK(mock_write_count==count || strstr(mock_uart_line,"DISARM,")!=NULL);
}
static void nz_nonowner(void)
{
    zero_start();offer();const unsigned count=mock_write_count;
    CHECK(wifi_ws_session_get(&second)!=NULL);
    nz_receive(&second,1,client->ticket.id,50,0);
    CHECK(strstr(mock_ws_output,"REJECTED")!=NULL);wifi_control_step();
    CHECK(mock_write_count==count && s_control.state.phase==WIFI_CONTROL_ACTIVE);
}
static void nz_preempt(void)
{
    zero_start();mock_now_ms+=20;offer();nz_receive(&first,3,client->ticket.id,50,0);
    const unsigned count=mock_write_count;
    char text[80];snprintf(text,sizeof(text),"DISARM,boot_id=%" PRIu32 ",request_id=4",s_boot_id);
    mock_ws_input=text;CHECK(ws_receive(&first)==ESP_OK);mock_ws_input=NULL;
    wifi_control_step();CHECK(mock_write_count==count+1 && strstr(mock_uart_line,"DISARM,")!=NULL);
    CHECK(!s_control.queued && s_control.state.owner.ws_session_id==0);
}
int main(int argc,char **argv)
{
    CHECK(argc==2);
    struct {const char *name;void (*run)(void);} cases[]={
        {"nz_snapshot",nz_snapshot},{"nz_first_zero",nz_first_zero},{"nz_wire",nz_wire},
        {"nz_expired_ticket",nz_expired_ticket},{"nz_nonowner",nz_nonowner},{"nz_preempt",nz_preempt}};
    for(size_t i=0;i<sizeof(cases)/sizeof(cases[0]);++i)if(strcmp(argv[1],cases[i].name)==0){
        cases[i].run();printf("PASS %s\n",cases[i].name);return 0;
    }
    return baseline_main(argc,argv);
}
