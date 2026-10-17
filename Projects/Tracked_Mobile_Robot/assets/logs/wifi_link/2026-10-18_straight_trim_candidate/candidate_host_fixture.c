/* Execute saved protocol/parser/mapper/motor C with simulated HAL only. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "uart_mvp_protocol.c"

static uint32_t host_ms;
static uint8_t *host_rx;
static GPIO_PinState host_estop;
static UART_HandleTypeDef host_uart;
static TIM_HandleTypeDef host_timer = {TIM4, 999U, {0, 0}};
static char host_tx[32768];
static size_t host_tx_len;

uint32_t HAL_GetTick(void) { return host_ms; }
void HAL_Delay(uint32_t delay) { host_ms += delay; }
GPIO_PinState HAL_GPIO_ReadPin(void *port, uint16_t pin)
{ (void)port; (void)pin; return host_estop; }
void HAL_GPIO_WritePin(void *port, uint16_t pin, GPIO_PinState level)
{ (void)port; (void)pin; (void)level; }
HAL_StatusTypeDef HAL_TIM_PWM_Start(TIM_HandleTypeDef *timer, uint32_t channel)
{ (void)timer; (void)channel; return HAL_OK; }
HAL_StatusTypeDef HAL_TIM_PWM_Stop(TIM_HandleTypeDef *timer, uint32_t channel)
{ (void)timer; (void)channel; return HAL_OK; }
HAL_StatusTypeDef HAL_UART_Receive_IT(UART_HandleTypeDef *uart, uint8_t *p, uint16_t n)
{ (void)uart; assert(n == 1); host_rx = p; return HAL_OK; }
HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *uart, uint8_t *p, uint16_t n, uint32_t timeout)
{
    (void)uart; (void)timeout;
    assert(host_tx_len + n < sizeof(host_tx));
    memcpy(host_tx + host_tx_len, p, n); host_tx_len += n; host_tx[host_tx_len] = 0;
    return HAL_OK;
}
static void feed(const char *text)
{
    host_tx_len = 0; host_tx[0] = 0;
    while (*text) { *host_rx = (uint8_t)*text++; uart_mvp_on_rx_complete(&host_uart); uart_mvp_process(); }
}
static void output(int left, int right)
{
    motor_output_applied_t actual = motor_output_get_applied();
    assert(actual.left_signed_permille == left && actual.right_signed_permille == right);
    assert(host_timer.compare[0] == (unsigned)(left < 0 ? -left : left));
    assert(host_timer.compare[1] == (unsigned)(right < 0 ? -right : right));
}
static void command(int vx, int w, int left, int right)
{
    static unsigned seq = 10;
    char frame[128], ack[64]; ++seq;
    snprintf(frame, sizeof(frame), "CMD,seq=%u,vx_mmps=%d,w_mradps=%d,timeout_ms=300\n", seq, vx, w);
    snprintf(ack, sizeof(ack), "ACK,seq=%u,type=CMD,", seq);
    feed(frame); assert(strstr(host_tx, ack)); output(left, right);
}
int main(void)
{
    assert(motor_output_init(&host_timer) == HAL_OK);
    uart_mvp_init(&host_uart); uart_mvp_start_rx(); output(0, 0);
    feed("CMD,seq=1,vx_mmps=0,w_mradps=500,timeout_ms=300\n");
    assert(strstr(host_tx, "NOT_ARMED")); output(0, 0);
    feed("ARM,seq=2\n"); output(0, 0);
    command(0, 0, 0, 0);
    command(100, 0, 144, 150); command(-100, 0, -140, -150);
    command(0, 500, -200, 200); command(0, -500, 200, -200);
    command(0, 250, -100, 100); command(0, -250, 100, -100);
    command(100, 250, 50, 150); command(-100, 250, -150, -50);
    command(0, 0, 0, 0);
    puts("PASS UART -> mapper -> motor: straight +144/+150 and -140/-150; pure-turn200, mixed150, partial turn and zero");
    command(0, 500, -200, 200);
    uint32_t accepted = s_last_cmd_ms;
    host_ms = accepted + 299U; uart_mvp_process(); output(-200, 200);
    host_ms = accepted + 300U; uart_mvp_process(); output(0, 0);
    assert(s_state == ROBOT_DISARMED && s_reason == ROBOT_REASON_CMD_TIMEOUT);
    feed("CMD,seq=100,vx_mmps=0,w_mradps=500,timeout_ms=300\n");
    assert(strstr(host_tx, "NOT_ARMED")); output(0, 0);
    feed("ARM,seq=101\n"); command(0, -500, 200, -200);
    feed("DISARM,seq=102\n"); output(0, 0); assert(s_state == ROBOT_DISARMED);
    feed("ARM,seq=103\n"); command(0, 500, -200, 200);
    host_estop = GPIO_PIN_SET; uart_mvp_process(); output(0, 0);
    puts("PASS 300ms timeout, no CMD-only rearm, DISARM and ESTOP stop at turn200");
    drive_command_request_t r = {77, -88};
    assert(!drive_command_map(0, 500, 201, &r));
    assert(r.left_signed_permille == 0 && r.right_signed_permille == 0);
    const int invalid[][2] = {{201,0},{-201,0},{0,201},{0,-201}};
    for (unsigned i=0; i<4; ++i) {
        assert(motor_output_set_signed(-200, 200) == HAL_OK); output(-200, 200);
        assert(motor_output_set_signed(invalid[i][0], invalid[i][1]) == HAL_ERROR); output(0, 0);
    }
    for (unsigned i=0; i<2; ++i) {
        assert(motor_output_set_signed(200, -200) == HAL_OK);
        assert(motor_output_set_raw(i ? 200 : 201, GPIO_PIN_RESET,
                                   i ? 201 : 200, GPIO_PIN_SET) == HAL_ERROR); output(0, 0);
    }
    puts("PASS mapper cap201 rejected; signed +/-201 and raw201 stop both outputs");
    return 0;
}
