/* Diagnostic harness: real STM stream/parser/mapper + real ESP stop formatter.
 * HAL time, GPIO, UART and motor hardware are mocked. No target firmware build.
 * Reproducing an existing failure is NOT a recovery acceptance PASS.
 */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "uart_mvp_protocol.c"
#include "wifi_control_executor.h"

static uint32_t host_ms;
static uint8_t *host_rx;
static UART_HandleTypeDef host_uart;
static GPIO_PinState host_estop;
static motor_output_applied_t host_output;
static char host_tx[32768];
static size_t host_tx_len;

uint32_t HAL_GetTick(void) { return host_ms; }
GPIO_PinState HAL_GPIO_ReadPin(void *port, uint16_t pin)
{ (void)port; (void)pin; return host_estop; }
HAL_StatusTypeDef HAL_UART_Receive_IT(UART_HandleTypeDef *uart, uint8_t *p, uint16_t n)
{ (void)uart; assert(n == 1); host_rx = p; return HAL_OK; }
HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *uart, uint8_t *p,
                                  uint16_t n, uint32_t timeout)
{
    (void)uart; (void)timeout;
    assert(host_tx_len + n < sizeof(host_tx));
    memcpy(host_tx + host_tx_len, p, n);
    host_tx_len += n;
    host_tx[host_tx_len] = '\0';
    return HAL_OK;
}
void motor_output_stop_all(void) { host_output = (motor_output_applied_t){0}; }
motor_output_applied_t motor_output_get_applied(void) { return host_output; }
HAL_StatusTypeDef motor_output_set_signed(int16_t left, int16_t right)
{
    host_output = (motor_output_applied_t){left, right};
    return HAL_OK;
}
HAL_StatusTypeDef motor_output_set_raw(uint16_t l, GPIO_PinState ld,
                                     uint16_t r, GPIO_PinState rd)
{ (void)l; (void)ld; (void)r; (void)rd; assert(0); return HAL_ERROR; }

static void clear_tx(void) { host_tx_len = 0; host_tx[0] = '\0'; }
static void reset_host(void)
{
    host_ms = 0;
    host_estop = GPIO_PIN_RESET;
    motor_output_stop_all();
    clear_tx();
    uart_mvp_init(&host_uart);
    uart_mvp_start_rx();
}
static void feed(const char *text)
{
    while (*text) {
        *host_rx = (uint8_t)*text++;
        uart_mvp_on_rx_complete(&host_uart);
        uart_mvp_process();
    }
}
static void tick(uint32_t value) { host_ms = value; uart_mvp_process(); }
static wifi_control_tx_t stop_frame(uint32_t seq)
{
    wifi_control_executor_t executor;
    wifi_control_tx_t tx;
    wifi_control_executor_init(&executor, 1);
    wifi_control_executor_stop(&executor, WIFI_CONTROL_REASON_MANUAL_STOP, host_ms);
    wifi_control_executor_inputs_cleared(&executor);
    assert(wifi_control_executor_take_tx(&executor, seq, host_ms, &tx));
    assert(wifi_control_executor_tx_complete(&executor, (int)tx.length, host_ms));
    return tx;
}
static void arm_zero(void)
{
    feed("ARM,seq=1\nCMD,seq=2,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    assert(s_state == ROBOT_ARMED && s_last_seq == 2);
    clear_tx();
}

int main(void)
{
    /* No LF: a frame may span arbitrary receive callbacks/process calls. */
    reset_host();
    feed("ARM,seq="); tick(10); feed("1\r\n");
    assert(s_state == ROBOT_ARMED && strstr(host_tx, "ACK,seq=1,type=ARM,"));
    puts("CHECK fragmented normal frame: ACK only after LF");

    reset_host(); arm_zero();
    feed("CMD,seq="); /* synthetic truncation, NOT a captured bench byte string */
    tick(300); assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_CMD_TIMEOUT);
    tick(10000); assert(s_line_len == strlen("CMD,seq="));
    clear_tx();
    wifi_control_tx_t first = stop_frame(2760658633U);
    printf("OBSERVED ESP first stop length: %zu bytes\n", first.length);
    feed(first.bytes);
    assert(strstr(host_tx, "ERR,seq=0,type=CMD,code=MISSING_SEQ,"));
    assert(!strstr(host_tx, "type=DISARM,"));
    assert(s_last_seq == 2 && s_state == ROBOT_DISARMED);
    puts("REPRODUCED first DISARM absorbed into stale CMD prefix; MISSING_SEQ");
    clear_tx();
    wifi_control_tx_t second = stop_frame(2760658634U);
    feed(second.bytes);
    assert(strstr(host_tx, "ACK,seq=2760658634,type=DISARM,"));
    assert(s_last_seq == 2760658634U && s_reason == ROBOT_REASON_DISARM);
    puts("REPRODUCED second manual DISARM succeeds after first LF clears buffer");

    /* Verify every nonempty proper prefix, not just the chosen error example. */
    const char *cmd = "CMD,seq=2760658631,vx_mmps=0,w_mradps=0,timeout_ms=300\n";
    size_t rejected = 0;
    for (size_t n = 1; n < strlen(cmd); ++n) {
        char prefix[128]; memcpy(prefix, cmd, n); prefix[n] = '\0';
        reset_host(); arm_zero(); feed(prefix); tick(300); clear_tx();
        first = stop_frame(2760658633U); feed(first.bytes);
        assert(!strstr(host_tx, "ACK,seq=2760658633,type=DISARM,"));
        assert(s_state == ROBOT_DISARMED);
        rejected++;
    }
    printf("REPRODUCED lost first stop for %zu/%zu truncated CMD prefixes\n",
           rejected, strlen(cmd) - 1);

    /* A bare LF repair has a counterexample: it can complete an old ARM. */
    reset_host(); feed("ARM,seq=99"); tick(10000); clear_tx(); feed("\n");
    assert(s_state == ROBOT_ARMED && strstr(host_tx, "ACK,seq=99,type=ARM,"));
    puts("COUNTEREXAMPLE bare sync LF executes an old complete ARM lacking LF");

    reset_host(); arm_zero(); tick(299); assert(s_state == ROBOT_ARMED);
    tick(300); assert(s_state == ROBOT_DISARMED); clear_tx();
    feed("CMD,seq=3,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    assert(strstr(host_tx, "ERR,seq=3,type=CMD,code=NOT_ARMED,"));
    assert(s_state == ROBOT_DISARMED && s_last_seq == 2);
    feed("ARM,seq=4\nCMD,seq=5,vx_mmps=0,w_mradps=0,timeout_ms=300\n");
    assert(s_state == ROBOT_ARMED && s_last_seq == 5);
    puts("CHECK timeout at 300 ms rejects CMD alone; new ARM and zero CMD accepted");

    reset_host(); feed("ARM,seq=99");
    uart_mvp_on_uart_error(&host_uart); uart_mvp_process(); clear_tx();
    feed("DISARM,seq=6\n");
    assert(strstr(host_tx, "code=RX_DESYNC") && s_state == ROBOT_DISARMED);
    assert(!strstr(host_tx, "type=ARM,"));
    feed("DISARM,seq=7\n"); assert(s_last_seq == 7);
    puts("CHECK HAL error discards through LF, then accepts next stop");
    puts("DIAGNOSTIC COMPLETE: baseline fault reproduced, no production fix applied");
    return 0;
}
