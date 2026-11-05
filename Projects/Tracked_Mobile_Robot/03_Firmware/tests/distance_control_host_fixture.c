/* Runs after the timing/transport regressions in the same native PC program. */
static void distance_publish(uint32_t time_ms, int64_t left, int64_t right,
                             bool valid)
{
    host_ms = time_ms;
    uart_mvp_set_encoder_sample(0, 0, left, right, time_ms, valid);
    uart_mvp_process();
}

static void distance_command(unsigned seq, unsigned mm)
{
    char frame[128];
    snprintf(frame, sizeof(frame),
        "CMD,seq=%u,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=%u\n", seq, mm);
    feed(frame);
}

static void distance_ready(void)
{
    unsigned t;
    fresh(); host_async = false;
    feed("ARM,seq=1001\n");
    for (t = 5; t <= 110; t += 5) distance_publish(t, 1000, 2000, true);
    assert(s_distance_mm == 0 && s_state == ROBOT_ARMED);
    output(0, 0);
}

static void begin_target(unsigned mm)
{
    distance_ready();
    distance_command(1002, mm);
    assert(strstr(host_tx, "ACK,seq=1002,type=CMD,"));
    assert(s_distance_move.phase == DISTANCE_MOVE_RUNNING);
    assert(s_distance_move.start_left == 1000 && s_distance_move.start_right == 2000);
    output(144, 150);
}

int main(void)
{
    unsigned i, t;
    uart_frame_t frame;
    assert(timing_main() == 0);
    const unsigned distances[] = {50, 100, 150, 200};
    const unsigned counts[] = {578, 1156, 1734, 2312};
    const char *invalid[] = {
        "CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=0",
        "CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=51",
        "CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=-50",
        "CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=4294967296",
        "CMD,seq=1,vx_mmps=0,w_mradps=0,timeout_ms=300,distance_mm=50",
        "CMD,seq=1,vx_mmps=-100,w_mradps=0,timeout_ms=300,distance_mm=50",
        "CMD,seq=1,vx_mmps=100,w_mradps=1,timeout_ms=300,distance_mm=50",
        "CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=50,",
        "CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=50x",
        "CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=50,distance_mm=50",
        "ARM,seq=1,distance_mm=50"
    };
    const char *ordinary = "CMD,seq=1,vx_mmps=100,w_mradps=0,timeout_ms=300";
    assert(uart_frame_parse(ordinary, strlen(ordinary), &frame) == UART_FRAME_PARSE_OK);
    assert(frame.distance_mm == 0);
    for (i = 0; i < sizeof(invalid)/sizeof(invalid[0]); ++i) {
        assert(uart_frame_parse(invalid[i], strlen(invalid[i]), &frame) != UART_FRAME_PARSE_OK);
    }
    puts("PASS optional distance suffix: ordinary CMD unchanged; malformed/range/direction/order rejected");

    for (i = 0; i < 4; ++i) {
        begin_target(distances[i]);
        assert(s_distance_move.target_counts == counts[i]);
        distance_command(1003, distances[i]);
        assert(s_distance_move.started_ms == 110 && s_distance_move.start_left == 1000);
        distance_publish(115, 1000 + counts[i], 2000 + counts[i] - 1, true);
        output(0, 150);
        assert(s_distance_move.phase == DISTANCE_MOVE_RUNNING);
        distance_publish(120, 1002 + counts[i], 2000 + counts[i], true);
        output(0, 0);
        assert(s_state == ROBOT_ARMED && s_reason == ROBOT_REASON_DISTANCE_REACHED);
        assert(s_vx_mmps == 0 && s_w_mradps == 0);
        distance_command(1004, distances[i]); output(0, 0);
        assert(s_distance_move.started_ms == 110);
        send_tel(); uart_tx_poll();
        assert(strstr(host_tx, "reason=DISTANCE_REACHED,"));
    }
    puts("PASS all four targets: independent cutoff, relative baseline, immutable goal, no restart after reached");

    begin_target(50);
    distance_publish(115, 1200, 2578, true); output(144, 0);
    distance_publish(120, 1578, 2578, true); output(0, 0);
    assert(s_reason == ROBOT_REASON_DISTANCE_REACHED);
    puts("PASS right reaches first: right cutoff held while left finishes");

    distance_ready();
    /* Stationarity clock is reset by count movement even when cached CPS is0. */
    distance_publish(115, 1001, 2000, true);
    distance_command(1002, 50); output(0, 0);
    assert(strstr(host_tx, "DISTANCE_NOT_STILL"));
    distance_ready(); command(100, 0, 144, 150);
    distance_command(1002, 50); output(0, 0);
    assert(s_state == ROBOT_DISARMED && strstr(host_tx, "DISTANCE_NOT_STILL"));
    assert(s_distance_mm == 0);
    fresh(); host_async = false;
    feed("ARM,seq=1001\n"); distance_publish(5, 1000, 2000, true);
    distance_command(1002, 50); output(0, 0);
    assert(strstr(host_tx, "DISTANCE_NOT_STILL"));
    puts("PASS first target requires fresh post-ARM100ms stationary baseline");

    begin_target(50);
    command(0, 0, 0, 0); uart_mvp_process(); output(0, 0);
    assert(s_state == ROBOT_ARMED && s_distance_move.phase == DISTANCE_MOVE_ABORTED);
    assert(s_distance_move.reason == DISTANCE_MOVE_REASON_CANCELLED);
    distance_command(1003, 50); output(0, 0);
    assert(strstr(host_tx, "DISTANCE_REARM_REQUIRED") && s_state == ROBOT_DISARMED);
    puts("PASS release/zero cancels without autonomous resume; new nonzero command requires rearm");

    begin_target(50); distance_command(1003, 100); output(0, 0);
    assert(s_state == ROBOT_DISARMED && strstr(host_tx, "DISTANCE_LOCKED"));
    begin_target(50);
    feed("CMD,seq=1003,vx_mmps=0,w_mradps=500,timeout_ms=300\n"); output(0, 0);
    assert(s_state == ROBOT_DISARMED && strstr(host_tx, "DISTANCE_LOCKED"));
    begin_target(50);
    feed("ARM,seq=1001\n"); output(0, 0);
    assert(s_state == ROBOT_DISARMED && strstr(host_tx, "DISTANCE_DUPLICATE_ARM"));
    feed("ARM,seq=2000\n"); output(0, 0);
    assert(s_state == ROBOT_ARMED && s_distance_mm == 0);
    puts("PASS changed goal/manual PWM cannot bypass distance latch; duplicate ARM cannot rewind; new ARM resets idle");

    begin_target(50); distance_publish(115, 1000, 2000, false); output(0, 0);
    assert(s_state == ROBOT_DISARMED && s_distance_move.reason == DISTANCE_MOVE_REASON_BAD_SAMPLE);
    begin_target(50); host_ms = 131; uart_mvp_process(); output(0, 0);
    assert(s_distance_move.reason == DISTANCE_MOVE_REASON_STALE_SAMPLE);
    send_tel(); uart_tx_poll();
    assert(strstr(host_tx, "reason=DISTANCE_STALE_SAMPLE,"));
    begin_target(50); distance_publish(140, 1001, 2001, true); output(0, 0);
    assert(s_distance_move.reason == DISTANCE_MOVE_REASON_POLL_GAP);
    begin_target(50); distance_publish(115, 999, 2000, true); output(0, 0);
    assert(s_distance_move.reason == DISTANCE_MOVE_REASON_COUNT_REVERSED);
    begin_target(50); s_encoder_sample.arm_seq++;
    uart_mvp_process(); output(0, 0);
    assert(s_distance_move.reason == DISTANCE_MOVE_REASON_BAD_SAMPLE);
    puts("PASS invalid/stale/gapped/reversed/wrong-ARM sample cuts both outputs and disarms");

    begin_target(200);
    for (t = 115; t <= 610; t += 5) {
        distance_publish(t, 1000, 2000, true);
        if ((t - 110) % 80 == 0) distance_command(1003 + t, 200);
    }
    output(0, 0);
    assert(s_state == ROBOT_DISARMED && s_distance_move.reason == DISTANCE_MOVE_REASON_NO_PROGRESS);
    begin_target(200);
    for (t = 115; t <= 3110; t += 5) {
        distance_publish(t, 1000 + (t - 110)/5, 2000 + (t - 110)/5, true);
        if ((t - 110) % 80 == 0) distance_command(1003 + t, 200);
    }
    output(0, 0);
    assert(s_state == ROBOT_DISARMED && s_distance_move.reason == DISTANCE_MOVE_REASON_RUN_TIMEOUT);
    puts("PASS keepalive cannot extend500ms no-progress or3000ms total-run deadline");

    begin_target(200);
    for (t = 115; t <= 410; t += 5)
        distance_publish(t, 1000 + (t - 110)/5, 2000 + (t - 110)/5, true);
    output(0, 0);
    assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_CMD_TIMEOUT);
    begin_target(50); host_estop = GPIO_PIN_SET; uart_mvp_process(); output(0, 0);
    assert(s_state == ROBOT_FAULT && s_reason == ROBOT_REASON_ESTOP_ACTIVE);
    begin_target(50); feed("DISARM,seq=1010\n"); uart_mvp_process(); output(0, 0);
    assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_DISARM);
    puts("PASS distance run preserves timeout/E-stop/DISARM immediate stop and original reasons");

    begin_target(50); host_async = true;
    uart_sendf("TEL,held\n"); uart_tx_poll();
    for (i = 0; i <= UART_TX_RESPONSE_SLOTS; ++i) send_ack(i, "CMD");
    output(0, 0);
    assert(s_tx_fault && s_distance_move.phase == DISTANCE_MOVE_ABORTED);
    assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_OUTPUT_ERROR);
    puts("PASS transport fault cancels distance immediately without bypassing TX rearm latch");
    puts("PASS STM distance integration candidate only; ESP/browser and board motion remain pending");
    return 0;
}
