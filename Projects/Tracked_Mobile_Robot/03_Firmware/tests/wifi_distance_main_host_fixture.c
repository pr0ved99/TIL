/* Appended to the extracted real main adapter, native PC mocks only. */
static void dp_receive(httpd_req_t *req, uint32_t id, uint32_t goal)
{
    char text[129];
    const int n=snprintf(text,sizeof(text),"CMD,boot_id=%" PRIu32 ",request_id=%" PRIu32
        ",control_id=%" PRIu32 ",ticket=%" PRIu32 ",vx_mmps=100,w_mradps=0,distance_mm=%" PRIu32,
        s_boot_id,id,s_control.state.owner.control_id,client->ticket.id,goal);
    CHECK(n>0 && (size_t)n<sizeof(text));
    mock_ws_input=text;CHECK(ws_receive(req)==ESP_OK);mock_ws_input=NULL;
}
static void dp_wire(void)
{
    const uint32_t goals[]={50U,100U,150U,200U};
    for(unsigned i=0U;i<4U;++i){
        zero_start();mock_now_ms+=20U;offer();dp_receive(&first,3U,goals[i]);
        if(WIFI_CONTROL_ZERO_ONLY){
            CHECK(strstr(mock_ws_output,"BAD_INPUT")!=NULL);wifi_control_step();
            CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);continue;
        }
        CHECK(strstr(mock_ws_output,"ACCEPTED")!=NULL);
        CHECK(s_control.request.distance_mm==goals[i]);wifi_control_step();
        char expected[96];snprintf(expected,sizeof(expected),
            "CMD,seq=104,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=%" PRIu32 "\n",goals[i]);
        CHECK(strcmp(mock_uart_line,expected)==0);
    }
}
static void dp_first_zero(void)
{
    arm_start();mock_now_ms+=20U;ack("ARM",102);offer();dp_receive(&first,2U,50U);
    CHECK(strstr(mock_ws_output,"REJECTED")!=NULL);wifi_control_step();
    CHECK(strstr(mock_uart_line,"DISARM,")!=NULL);
}
static void dp_other_owner(void)
{
    zero_start();offer();const unsigned n=mock_write_count;
    CHECK(wifi_ws_session_get(&second)!=NULL);dp_receive(&second,1U,50U);
    CHECK(strstr(mock_ws_output,"REJECTED")!=NULL);wifi_control_step();
    CHECK(mock_write_count==n && s_control.state.phase==WIFI_CONTROL_ACTIVE);
}
static void dp_preempt(void)
{
    zero_start();mock_now_ms+=20U;offer();dp_receive(&first,3U,50U);
    const unsigned count=mock_write_count;
    char text[80];snprintf(text,sizeof(text),"DISARM,boot_id=%" PRIu32 ",request_id=4",s_boot_id);
    mock_ws_input=text;CHECK(ws_receive(&first)==ESP_OK);mock_ws_input=NULL;
    wifi_control_step();CHECK(mock_write_count==count+1 && strstr(mock_uart_line,"DISARM,")!=NULL);
    CHECK(!s_control.queued);
}
static void dp_frame_limit(void)
{
    setup();
    const char *text="CMD,boot_id=4294967295,request_id=4294967295,control_id=4294967295,ticket=4294967295,vx_mmps=100,w_mradps=0,distance_mm=200";
    CHECK(strlen(text)==123U);mock_ws_input=text;CHECK(ws_receive(&first)==ESP_OK);mock_ws_input=NULL;
    CHECK(strstr(mock_ws_output,"BOOT_MISMATCH")!=NULL);
}
int main(int argc,char **argv)
{
    CHECK(argc==2);
    struct {const char *name;void (*run)(void);} cases[]={
        {"distance_wire",dp_wire},{"distance_first_zero",dp_first_zero},
        {"distance_other_owner",dp_other_owner},{"distance_preempt",dp_preempt},
        {"distance_frame_limit",dp_frame_limit}};
    for(size_t i=0U;i<sizeof(cases)/sizeof(cases[0]);++i)if(strcmp(argv[1],cases[i].name)==0){
        cases[i].run();printf("PASS %s\n",cases[i].name);return 0;
    }
    return 2;
}
