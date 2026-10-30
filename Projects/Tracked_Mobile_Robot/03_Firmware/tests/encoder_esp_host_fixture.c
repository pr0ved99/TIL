static const char *sample =
    "TEL,t_ms=100,state=DISARMED,reason=DISARM,command_age_ms=10,last_seq=7,"
    "vx_mmps=0,w_mradps=0,left_pwm=0,right_pwm=0,left_cps=0,right_cps=0,"
    "encoder_valid=1,encoder_t_ms=90,left_count=9007199254740993,right_count=-9007199254740993,"
    "encoder_arm_valid=1,encoder_arm_seq=0,batt_mv=0,drop=0,err=0";

static bool replaced_parse(const char *old, const char *replacement)
{
    char frame[1024];
    const char *p = strstr(sample, old);
    assert(p != NULL);
    snprintf(frame, sizeof(frame), "%.*s%s%s", (int)(p - sample), sample,
             replacement, p + strlen(old));
    stm_telemetry_t tel = {0};
    return stm_parse_tel(frame, &tel);
}

int main(void)
{
    stm_telemetry_t tel = {0};
    assert(stm_parse_tel(sample, &tel));
    assert(tel.left_count == INT64_C(9007199254740993));
    assert(tel.right_count == -INT64_C(9007199254740993));
    assert(tel.encoder_valid && tel.encoder_arm_valid && tel.encoder_arm_seq == 0U);
    assert(tel.t_ms == 100U && tel.encoder_t_ms == 90U);
    puts("PASS parse20: exact count beyond JS safe integer, separate sample tick, valid ARM seq0");

    int64_t value;
    assert(stm_parse_i64_field("x=9223372036854775807", "x=", &value) && value == INT64_MAX);
    assert(stm_parse_i64_field("x=-9223372036854775808", "x=", &value) && value == INT64_MIN);
    assert(stm_parse_i64_field("x=-0", "x=", &value) && value == 0);
    const char *invalid[] = {"x=9223372036854775808", "x=-9223372036854775809",
        "x=18446744073709551616", "x=+1", "x=", "x=-", "x= 1", "x=1 ",
        "x=1.0", "x=1e1", "x=1,x=2", "other=1", "x=--1"};
    for (unsigned i = 0U; i < sizeof(invalid)/sizeof(invalid[0]); ++i)
        assert(!stm_parse_i64_field(invalid[i], "x=", &value));
    puts("PASS i64 grammar and range: both endpoints accepted, overflow/duplicates/junk rejected");

    assert(!replaced_parse("encoder_valid=1", "encoder_valid=2"));
    assert(!replaced_parse("encoder_arm_valid=1", "encoder_arm_valid=2"));
    assert(!replaced_parse("encoder_valid=1", "encoder_valid=-1"));
    assert(!replaced_parse("encoder_t_ms=90", "encoder_t_ms=4294967296"));
    assert(!replaced_parse("encoder_arm_seq=0", "encoder_arm_seq=4294967296"));
    assert(!replaced_parse("right_count=-9007199254740993", "left_count=1"));
    assert(!replaced_parse("right_count=-9007199254740993", "unknown=1"));
    assert(!replaced_parse("encoder_valid=1,encoder_t_ms=90,left_count=9007199254740993,right_count=-9007199254740993,encoder_arm_valid=1,encoder_arm_seq=0,", ""));
    assert(!replaced_parse("drop=0", "drop=0,"));
    puts("PASS whole TEL: flag/time/seq bounds, duplicate/missing/unknown fields and old14 rejected");

    assert(replaced_parse("encoder_valid=1", "encoder_valid=0"));
    assert(replaced_parse("encoder_arm_valid=1", "encoder_arm_valid=0"));
    puts("PASS false measurement flags remain valid control telemetry");

    char json[STATUS_JSON_SIZE];
    assert(status_json(json, sizeof(json)) > 0);
    assert(strstr(json, "\"source\":\"ESP_ONLY\""));
    assert(strstr(json, "\"encoder_valid\":null,\"encoder_t_ms\":null,"));
    assert(strstr(json, "\"left_count\":null,\"right_count\":null,"));
    printf("JSON %s\n", json);
    puts("PASS ESP_ONLY JSON: encoder metadata is null before first valid STM TEL");

    tel.valid = true;
    tel.rx_ms = 900U;
    s_stm_telemetry = tel;
    s_stm_tel_count = 1U;
    assert(status_json(json, sizeof(json)) > 0);
    assert(strstr(json, "\"left_count\":\"9007199254740993\""));
    assert(strstr(json, "\"right_count\":\"-9007199254740993\""));
    assert(strstr(json, "\"encoder_valid\":true"));
    printf("JSON %s\n", json);
    puts("PASS STM JSON: exact decimal strings and boolean metadata");

    s_stm_telemetry.encoder_valid = false;
    s_stm_telemetry.encoder_arm_valid = false;
    assert(status_json(json, sizeof(json)) > 0);
    assert(strstr(json, "\"stm_connected\":true"));
    assert(strstr(json, "\"encoder_valid\":false"));
    printf("JSON %s\n", json);
    puts("PASS JSON flags false: transport connected and count snapshot preserved");

    mock_us = 2000000U;
    assert(status_json(json, sizeof(json)) > 0);
    assert(strstr(json, "\"stm_stale\":true"));
    assert(strstr(json, "\"left_count\":\"9007199254740993\""));
    printf("JSON %s\n", json);
    puts("PASS stale JSON: existing freshness policy and last count retained");

    s_stm_telemetry.left_count = INT64_MIN;
    s_stm_telemetry.right_count = INT64_MIN;
    s_stm_telemetry.t_ms = UINT32_MAX;
    s_stm_telemetry.encoder_t_ms = UINT32_MAX;
    s_stm_telemetry.encoder_arm_seq = UINT32_MAX;
    s_stm_telemetry.command_age_ms = UINT32_MAX;
    s_stm_telemetry.last_seq = UINT32_MAX;
    s_stm_telemetry.drop = UINT32_MAX;
    s_stm_telemetry.err = UINT32_MAX;
    s_stm_telemetry.vx_mmps = INT32_MIN;
    s_stm_telemetry.w_mradps = INT32_MIN;
    s_stm_telemetry.left_cps = INT32_MIN;
    s_stm_telemetry.right_cps = INT32_MIN;
    s_stm_telemetry.left_pwm = -1000;
    s_stm_telemetry.right_pwm = -1000;
    memset(s_stm_telemetry.reason, 'R', 31);
    s_stm_telemetry.reason[31] = 0;
    s_stm_tel_count = UINT32_MAX;
    s_boot_id = UINT32_MAX;
    s_stm_telemetry.rx_ms = 0U;
    mock_us = UINT64_C(9007199254740991) * 1000U;
    s_stm_startup_status = "WAIT_DISARM_ACK";
    const int length = status_json(json, sizeof(json));
    assert(length > 0 && (size_t)length < sizeof(json));
    printf("JSON %s\n", json);
    printf("MAX_JSON_BYTES %d\n", length);
    assert(status_json(json, 8U) == -1);
    puts("PASS JSON capacity: all count/numeric/text bounds fit, short buffer rejected");
    return 0;
}
