#include "uart_mvp_protocol.h"

#include "ring_buffer.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define UART_LINE_MAX 128u

#define CMD_TIMEOUT_DEFAULT_MS 300u
#define CMD_TIMEOUT_MIN_MS      50u
#define CMD_TIMEOUT_MAX_MS     500u
#define AUTO_DISARM_MS        3000u
#define TEL_PERIOD_MS          100u

#define VX_MIN_MMPS            -100
#define VX_MAX_MMPS             100
#define W_MIN_MRADPS           -500
#define W_MAX_MRADPS            500

typedef enum {
  ROBOT_DISARMED = 0,
  ROBOT_ARMED,
  ROBOT_FAULT
} robot_state_t;

static UART_HandleTypeDef *s_uart;
static uint8_t s_rx_byte;
static ring_buffer_t s_rx_rb;

static char s_line[UART_LINE_MAX];
static uint16_t s_line_len;
static uint8_t s_line_overflow;

static robot_state_t s_state = ROBOT_DISARMED;
static int32_t s_last_seq;
static int16_t s_vx_mmps;
static int16_t s_w_mradps;
static uint16_t s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
static uint32_t s_last_cmd_ms;
static uint32_t s_last_tel_ms;
static uint32_t s_drop_count;
static uint32_t s_error_count;

static const char *state_name(robot_state_t state)
{
  switch (state) {
  case ROBOT_ARMED:
    return "ARMED";
  case ROBOT_FAULT:
    return "FAULT";
  case ROBOT_DISARMED:
  default:
    return "DISARMED";
  }
}

static void uart_sendf(const char *fmt, ...)
{
  char tx[160];
  va_list args;
  int len;

  if (s_uart == NULL) {
    return;
  }

  va_start(args, fmt);
  len = vsnprintf(tx, sizeof(tx), fmt, args);
  va_end(args);

  if (len <= 0) {
    return;
  }

  if ((size_t)len >= sizeof(tx)) {
    len = (int)sizeof(tx) - 1;
  }

  (void)HAL_UART_Transmit(s_uart, (uint8_t *)tx, (uint16_t)len, 20u);
}

static int get_i32_field(const char *line, const char *key, int32_t *out)
{
  char pattern[24];
  const char *p;
  char *endp;

  (void)snprintf(pattern, sizeof(pattern), "%s=", key);
  p = strstr(line, pattern);
  if (p == NULL) {
    return 0;
  }

  p += strlen(pattern);
  *out = (int32_t)strtol(p, &endp, 10);
  return endp != p;
}

static void get_frame_type(const char *line, char *type, size_t type_size)
{
  size_t i = 0u;

  while (line[i] != '\0' && line[i] != ',' && i + 1u < type_size) {
    type[i] = line[i];
    i++;
  }
  type[i] = '\0';
}

static void send_ack(int32_t seq, const char *type)
{
  uart_sendf("ACK,seq=%ld,type=%s,t_ms=%lu\n",
             (long)seq, type, (unsigned long)HAL_GetTick());
}

static void send_err(int32_t seq, const char *type, const char *code)
{
  s_error_count++;
  uart_sendf("ERR,seq=%ld,type=%s,code=%s,t_ms=%lu\n",
             (long)seq, type, code, (unsigned long)HAL_GetTick());
}

static void zero_motion_command(void)
{
  s_vx_mmps = 0;
  s_w_mradps = 0;
}

static void handle_ping(const char *line)
{
  int32_t seq = 0;

  if (!get_i32_field(line, "seq", &seq)) {
    send_err(0, "PING", "MISSING_SEQ");
    return;
  }

  s_last_seq = seq;
  uart_sendf("PONG,seq=%ld,t_ms=%lu\n",
             (long)seq, (unsigned long)HAL_GetTick());
}

static void handle_arm(const char *line)
{
  int32_t seq = 0;

  if (!get_i32_field(line, "seq", &seq)) {
    send_err(0, "ARM", "MISSING_SEQ");
    return;
  }

  s_state = ROBOT_ARMED;
  s_last_seq = seq;
  s_last_cmd_ms = HAL_GetTick();
  zero_motion_command();
  send_ack(seq, "ARM");
}

static void handle_disarm(const char *line)
{
  int32_t seq = 0;

  if (!get_i32_field(line, "seq", &seq)) {
    send_err(0, "DISARM", "MISSING_SEQ");
    return;
  }

  s_state = ROBOT_DISARMED;
  s_last_seq = seq;
  zero_motion_command();
  send_ack(seq, "DISARM");
}

static void handle_cmd(const char *line)
{
  int32_t seq = 0;
  int32_t vx = 0;
  int32_t w = 0;
  int32_t timeout_ms = CMD_TIMEOUT_DEFAULT_MS;

  if (!get_i32_field(line, "seq", &seq) ||
      !get_i32_field(line, "vx_mmps", &vx) ||
      !get_i32_field(line, "w_mradps", &w)) {
    send_err(seq, "CMD", "MISSING_FIELD");
    return;
  }

  (void)get_i32_field(line, "timeout_ms", &timeout_ms);

  if (s_state != ROBOT_ARMED) {
    send_err(seq, "CMD", "NOT_ARMED");
    return;
  }

  if (vx < VX_MIN_MMPS || vx > VX_MAX_MMPS ||
      w < W_MIN_MRADPS || w > W_MAX_MRADPS ||
      timeout_ms < CMD_TIMEOUT_MIN_MS || timeout_ms > CMD_TIMEOUT_MAX_MS) {
    send_err(seq, "CMD", "OUT_OF_RANGE");
    return;
  }

  s_last_seq = seq;
  s_vx_mmps = (int16_t)vx;
  s_w_mradps = (int16_t)w;
  s_cmd_timeout_ms = (uint16_t)timeout_ms;
  s_last_cmd_ms = HAL_GetTick();
  send_ack(seq, "CMD");
}

static void handle_line(const char *line)
{
  char type[12];

  get_frame_type(line, type, sizeof(type));

  if (strcmp(type, "PING") == 0) {
    handle_ping(line);
  } else if (strcmp(type, "ARM") == 0) {
    handle_arm(line);
  } else if (strcmp(type, "DISARM") == 0) {
    handle_disarm(line);
  } else if (strcmp(type, "CMD") == 0) {
    handle_cmd(line);
  } else {
    send_err(0, type[0] ? type : "UNKNOWN", "UNKNOWN_TYPE");
  }
}

static void process_rx_bytes(void)
{
  uint8_t byte;

  while (rb_get(&s_rx_rb, &byte)) {
    if (byte == '\r') {
      continue;
    }

    if (byte == '\n') {
      if (s_line_overflow) {
        send_err(0, "RX", "LINE_TOO_LONG");
      } else if (s_line_len > 0u) {
        s_line[s_line_len] = '\0';
        handle_line(s_line);
      }
      s_line_len = 0u;
      s_line_overflow = 0u;
      continue;
    }

    if (s_line_len + 1u >= UART_LINE_MAX) {
      s_line_overflow = 1u;
      continue;
    }

    if (!s_line_overflow) {
      s_line[s_line_len++] = (char)byte;
    }
  }
}

static void update_timeout(uint32_t now)
{
  uint32_t elapsed;

  if (s_state != ROBOT_ARMED) {
    return;
  }

  elapsed = now - s_last_cmd_ms;

  if (elapsed > s_cmd_timeout_ms) {
    zero_motion_command();
  }

  if (elapsed > AUTO_DISARM_MS) {
    s_state = ROBOT_DISARMED;
  }
}

static void send_telemetry(uint32_t now)
{
  if ((now - s_last_tel_ms) < TEL_PERIOD_MS) {
    return;
  }

  s_last_tel_ms = now;
  uart_sendf("TEL,t_ms=%lu,state=%s,last_seq=%ld,vx_mmps=%d,w_mradps=%d,left_pwm=0,right_pwm=0,left_cps=0,right_cps=0,batt_mv=0,drop=%lu,err=%lu\n",
             (unsigned long)now,
             state_name(s_state),
             (long)s_last_seq,
             (int)s_vx_mmps,
             (int)s_w_mradps,
             (unsigned long)s_drop_count,
             (unsigned long)s_error_count);
}

void uart_mvp_init(UART_HandleTypeDef *huart)
{
  s_uart = huart;
  rb_init(&s_rx_rb);
  s_line_len = 0u;
  s_line_overflow = 0u;
  s_state = ROBOT_DISARMED;
  s_last_seq = 0;
  zero_motion_command();
  s_last_cmd_ms = HAL_GetTick();
  s_last_tel_ms = HAL_GetTick();
  s_drop_count = 0u;
  s_error_count = 0u;
}

void uart_mvp_start_rx(void)
{
  if (s_uart != NULL) {
    (void)HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1u);
  }
}

void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart)
{
  if (huart != s_uart) {
    return;
  }

  if (!rb_put(&s_rx_rb, s_rx_byte)) {
    s_drop_count++;
  }

  (void)HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1u);
}

void uart_mvp_on_uart_error(UART_HandleTypeDef *huart)
{
  if (huart == s_uart) {
    (void)HAL_UART_Receive_IT(s_uart, &s_rx_byte, 1u);
  }
}

void uart_mvp_process(void)
{
  uint32_t now = HAL_GetTick();

  process_rx_bytes();
  update_timeout(now);
  send_telemetry(now);
}
