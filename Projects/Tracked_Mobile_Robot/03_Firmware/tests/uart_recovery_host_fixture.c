/* PC-only recovery acceptance tests. HAL/IRQ/motor/UART are mocks.
 * Rename the diagnostic entry point to reuse its actual STM adapter helpers.
 */
#define main baseline_diagnostic_main
#include "stm_uart_stream_host_fixture.c"
#undef main
#include <inttypes.h>

static char startup_wire[96];
static int startup_short_write;
static unsigned startup_writes;
static int uart_write_bytes(int port, const void *data, size_t length)
{
    (void)port;
    assert(length < sizeof(startup_wire));
    ++startup_writes;
    memcpy(startup_wire, data, length);
    startup_wire[length] = 0;
    if (startup_short_write) return -1;
    feed(startup_wire);
    return (int)length;
}
static int uart_flush_input(int port) { (void)port; return 0; }
static void host_log(const char *fmt, ...) { (void)fmt; }
#define STM_UART_PORT 1
#define ESP_OK 0
#define TAG "host"
#define ESP_LOGI(tag, ...) host_log(__VA_ARGS__)
#define ESP_LOGW(tag, ...) host_log(__VA_ARGS__)
#define ESP_LOGE(tag, ...) host_log(__VA_ARGS__)
static size_t s_stm_rx_length;
static bool s_stm_discard_until_lf;
#include "startup_functions.h"

static void stop_ok(uint32_t seq)
{
    char expected[80];
    wifi_control_tx_t tx = stop_frame(seq);
    assert(tx.length == strlen(tx.bytes));
    assert((unsigned char)tx.bytes[0] == 0x18 && tx.bytes[1] == '\n');
    feed(tx.bytes);
    snprintf(expected, sizeof(expected), "ACK,seq=%" PRIu32 ",type=DISARM,", seq);
    assert(strstr(host_tx, expected));
    assert(s_state == ROBOT_DISARMED && s_last_seq == seq);
    assert(host_output.left_signed_permille == 0 && host_output.right_signed_permille == 0);
}

static size_t prefixes(void)
{
    const char *frames[] = {
        "CMD,seq=2760658631,vx_mmps=0,w_mradps=0,timeout_ms=300\n",
        "CMD,seq=99,vx_mmps=50,w_mradps=0,timeout_ms=300\n",
        "ARM,seq=99\n", "ARM,seq=99\r\n", "DISARM,seq=99\n",
        "PING,seq=99\n", "ESTOP_RESET,seq=99\n"
    };
    size_t checked = 0;
    for (size_t f=0; f<sizeof(frames)/sizeof(frames[0]); ++f) {
        for (size_t n=0; n<strlen(frames[f]); ++n) {
            for (unsigned mode=0; mode<3; ++mode) {
                char prefix[128]; memcpy(prefix, frames[f], n); prefix[n]=0;
                reset_host();
                if (mode != 0) arm_zero();
                feed(prefix);
                tick(mode == 2 ? 10000U : 10U);
                clear_tx();
                stop_ok(2760658633U);
                assert(!strstr(host_tx, "seq=99,"));
                assert(!strstr(host_tx, "type=ARM,") && !strstr(host_tx, "type=CMD,"));
                assert(!strstr(host_tx, "ERR,") && s_error_count == 0);
                ++checked;
            }
        }
    }
    return checked;
}

static void framing(void)
{
    reset_host(); feed("ARM,seq="); tick(10); feed("1\r\n");
    assert(s_state == ROBOT_ARMED && s_last_seq == 1);
    clear_tx(); feed("CMD,seq=9,vx_mmps=50,w_mradps=0,timeout_ms=300");
    feed("\x18"); /* Discard is not a motor command or permission grant. */
    assert(!strstr(host_tx, "type=CMD,"));
    feed("ARM,seq=99\x18\r"); tick(11); feed("\n");
    assert(!strstr(host_tx, "seq=99,"));
    stop_ok(10); assert(s_error_count == 0);

    /* Prefix and cancellation can be queued together, rather than byte-fed. */
    reset_host();
    const char *queued = "ARM,seq=99\x18\nDISARM,seq=10\n";
    for (size_t i=0; queued[i]; ++i) {
        *host_rx=(uint8_t)queued[i]; uart_mvp_on_rx_complete(&host_uart);
    }
    uart_mvp_process();
    assert(s_state == ROBOT_DISARMED && s_last_seq == 10);
    assert(!strstr(host_tx,"type=ARM,"));

    reset_host();
    for (unsigned i=0; i<100; ++i) feed("PING,seq=1\n"); /* Ring wraps. */
    feed("ARM,seq=99"); clear_tx(); stop_ok(10);
    assert(!strstr(host_tx,"type=ARM,"));
}

static void lengths_and_errors(void)
{
    char line[132];
    reset_host();
    memset(line, '0', 127); memcpy(line,"ARM,seq=",8);
    line[126]='1'; line[127]='\r'; line[128]='\n'; line[129]=0;
    feed(line); assert(s_last_seq==1 && s_state==ROBOT_ARMED);
    reset_host();
    memset(line, 'X', 128); line[128]='\n'; line[129]=0;
    feed(line); assert(strstr(host_tx,"LINE_OVERFLOW") && s_state==ROBOT_DISARMED);
    clear_tx(); stop_ok(10);
    reset_host();
    for(unsigned i=0;i<300;++i) feed("X");
    clear_tx(); stop_ok(10); assert(!strstr(host_tx,"ERR,"));

    reset_host(); feed("ARM,seq=99");
    uart_mvp_on_uart_error(&host_uart); uart_mvp_process(); clear_tx();
    stop_ok(10);
    assert(strstr(host_tx,"RX_DESYNC") && !strstr(host_tx,"type=ARM,"));

    reset_host(); feed("ARM,seq=99\x18");
    uart_mvp_on_uart_error(&host_uart); uart_mvp_process(); clear_tx();
    stop_ok(10); assert(strstr(host_tx,"RX_DESYNC"));

    reset_host();
    for(unsigned i=0;i<300;++i) {
        *host_rx='X'; uart_mvp_on_rx_complete(&host_uart);
    }
    assert(ring_buffer_dropped(&s_rx_rb)>0);
    uart_mvp_process(); clear_tx(); stop_ok(10);
    assert(strstr(host_tx,"RX_DESYNC"));
}

static void safety_gates(void)
{
    reset_host(); arm_zero(); tick(299); assert(s_state==ROBOT_ARMED);
    tick(300); assert(s_state==ROBOT_DISARMED); clear_tx(); stop_ok(10);
    feed("CMD,seq=11,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    assert(strstr(host_tx,"NOT_ARMED") && s_state==ROBOT_DISARMED && s_last_seq==10);
    feed("ARM,seq=12\nCMD,seq=13,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    assert(s_state==ROBOT_ARMED && s_last_seq==13);

    reset_host(); host_estop=GPIO_PIN_SET; uart_mvp_process();
    feed("ESTOP_RESET,seq=99");
    wifi_control_tx_t tx=stop_frame(10); feed(tx.bytes);
    assert(s_state==ROBOT_FAULT && s_estop_latched && s_last_seq==10);
    assert(!strstr(host_tx,"type=ESTOP_RESET,"));
    host_estop=GPIO_PIN_RESET; uart_mvp_process();
    feed(tx.bytes); assert(s_state==ROBOT_FAULT && s_estop_latched);
}

static void executor_confirmation(void)
{
    wifi_control_executor_t e;
    wifi_control_tx_t tx;
    reset_host();
    wifi_control_executor_init(&e,1);
    wifi_control_executor_stop(&e,WIFI_CONTROL_REASON_MANUAL_STOP,0);
    wifi_control_executor_inputs_cleared(&e);
    assert(wifi_control_executor_take_tx(&e,10,0,&tx));
    assert(wifi_control_executor_tx_complete(&e,(int)tx.length,1));
    feed(tx.bytes); assert(strstr(host_tx,"ACK,seq=10,type=DISARM,"));
    wifi_control_tel_t t={.state=WIFI_CONTROL_STM_DISARMED,.last_seq=10,.t_ms=1};
    wifi_control_executor_tel(&e,&t,2); /* TEL alone cannot confirm stop. */
    assert(e.state.phase==WIFI_CONTROL_STOPPING);
    assert(!wifi_control_executor_reply(&e,WIFI_CONTROL_OP_DISARM,9,true,2,3));
    assert(wifi_control_executor_reply(&e,WIFI_CONTROL_OP_DISARM,10,true,2,3));
    wifi_control_executor_tel(&e,&t,4); /* pre-ACK STM time */
    assert(e.state.phase==WIFI_CONTROL_STOPPING);
    t.t_ms=3; wifi_control_executor_tel(&e,&t,5);
    assert(e.state.phase==WIFI_CONTROL_IDLE);
    assert(!wifi_control_executor_take_tx(&e,11,6,&tx));

    /* If the recovery itself is truncated, remain blocked; no auto retry. */
    wifi_control_executor_stop(&e,WIFI_CONTROL_REASON_MANUAL_STOP,10);
    wifi_control_executor_inputs_cleared(&e);
    assert(wifi_control_executor_take_tx(&e,12,11,&tx));
    assert(!wifi_control_executor_tx_complete(&e,1,12));
    assert(e.state.phase==WIFI_CONTROL_BLOCKED);
    assert(!wifi_control_executor_take_tx(&e,13,13,&tx));
    wifi_control_executor_stop(&e,WIFI_CONTROL_REASON_MANUAL_STOP,14);
    wifi_control_executor_inputs_cleared(&e);
    assert(wifi_control_executor_take_tx(&e,14,15,&tx));
    assert((unsigned char)tx.bytes[0]==0x18 && tx.bytes[1]=='\n');
}

static void startup(void)
{
    reset_host(); feed("ARM,seq=99"); clear_tx();
    startup_short_write=0; startup_writes=0;
    s_stm_startup=(stm_startup_t){.state=STM_STARTUP_SETTLE,.disarm_seq=10,.ping_seq=11};
    stm_startup_step(500);
    assert(strcmp(startup_wire,"\x18\n")==0 && startup_writes==1);
    assert(s_state==ROBOT_DISARMED && !strstr(host_tx,"type=ARM,"));
    stm_startup_step(600);
    assert(strcmp(startup_wire,"\x18\nDISARM,seq=10\n")==0);
    assert(strstr(host_tx,"ACK,seq=10,type=DISARM,"));
    clear_tx(); s_stm_startup.disarm_ack=true; stm_startup_step(601);
    assert(strcmp(startup_wire,"PING,seq=11\n")==0);
    assert(strstr(host_tx,"PONG,seq=11,"));
    s_stm_startup.pong=true; stm_startup_step(602);
    assert(s_stm_startup.state==STM_STARTUP_READY);

    reset_host(); feed("ARM,seq=99"); clear_tx();
    s_stm_startup=(stm_startup_t){.state=STM_STARTUP_WAIT_DISARM_ACK,.disarm_seq=10,.attempts=1};
    stm_startup_retry(false,500);
    assert(strcmp(startup_wire,"\x18\nDISARM,seq=10\n")==0);
    assert(!strstr(host_tx,"type=ARM,"));
    s_stm_startup=(stm_startup_t){.state=STM_STARTUP_SETTLE};
    startup_short_write=1; stm_startup_step(500);
    assert(s_stm_startup.state==STM_STARTUP_FAILED);
}

int main(void)
{
    size_t n=prefixes(); printf("PASS %zu prefix/state combinations\n",n);
    framing(); puts("PASS fragmented, queued, repeated cancellation and ring wrap");
    lengths_and_errors(); puts("PASS max-length CRLF, overflow and HAL error recovery");
    safety_gates(); puts("PASS timeout, CMD-only rejection and E-stop latch preservation");
    executor_confirmation(); puts("PASS exact ACK plus fresh TEL; failed TX stays BLOCKED");
    startup(); puts("PASS real startup cancellation, retry, PING and TX failure");
    return 0;
}
