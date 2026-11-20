"""In-memory STM late-DISARM-ACK candidate; never writes production firmware.

CHANGES also supplies exact old/new blocks for the learning code guide.
"""
from pathlib import Path

FIRMWARE = Path(__file__).resolve().parent.parent
STM = FIRMWARE / "stm32_uart_mvp/Core/Src/uart_mvp_protocol.c"
MODE = "UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED"

CONFIG = r"""/* Bench only: stop immediately; delay one eligible DISARM ACK. */
#define UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_DELAY_DISARM_ACK_MS             500U

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED > 1U
#error "Delayed DISARM ACK test mode must be 0 or 1"
#endif
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED && ( \
    UART_MVP_OUTPUT_TEST_ENABLED || \
    UART_MVP_STALE_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED || \
    UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED || \
    UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED || \
    UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_EMBEDDED_CR_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_CONTROL_BYTE_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_OVERLONG_DISARM_ACK_ONCE_TEST_ENABLED || \
    UART_MVP_STALE_PONG_ONCE_TEST_ENABLED || UART_MVP_SUPPRESS_PONG_TEST_ENABLED)
#error "Do not combine delayed ACK with another bench fault/output mode"
#endif"""

STATE = """#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
typedef struct {
    uint8_t used;
    uint8_t pending;
    uint8_t zero_cmd_seen;
    uint32_t seq;
    uint32_t processed_ms;
} delayed_disarm_ack_t;

static delayed_disarm_ack_t s_delayed_disarm_ack;
#endif"""

HELPERS = r"""#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
static uint8_t delayed_disarm_ack_eligible(void)
{
    const motor_output_applied_t applied = motor_output_get_applied();
    return (uint8_t)(s_delayed_disarm_ack.used == 0U &&
        s_delayed_disarm_ack.zero_cmd_seen != 0U &&
        s_state == ROBOT_ARMED && s_estop_latched == 0U &&
        estop_input_active() == 0U && s_vx_mmps == 0 && s_w_mradps == 0 &&
        applied.left_signed_permille == 0 && applied.right_signed_permille == 0 &&
        s_left_cps == 0 && s_right_cps == 0);
}

static void delayed_disarm_ack_schedule(uint32_t seq)
{
    s_delayed_disarm_ack.used = 1U;
    s_delayed_disarm_ack.pending = 1U;
    s_delayed_disarm_ack.seq = seq;
    s_delayed_disarm_ack.processed_ms = HAL_GetTick();
    uart_sendf("TEST_ACK_DELAY,seq=%lu,t_ms=%lu,delay_ms=%lu\n",
        (unsigned long)seq,
        (unsigned long)s_delayed_disarm_ack.processed_ms,
        (unsigned long)UART_MVP_DELAY_DISARM_ACK_MS);
}

static void delayed_disarm_ack_poll(void)
{
    if (s_delayed_disarm_ack.pending == 0U ||
        (uint32_t)(HAL_GetTick() - s_delayed_disarm_ack.processed_ms) <
            UART_MVP_DELAY_DISARM_ACK_MS) {
        return;
    }
    s_delayed_disarm_ack.pending = 0U;
    /* Original processing time: this is an old response, not a new stop. */
    uart_sendf("ACK,seq=%lu,type=DISARM,t_ms=%lu\n",
        (unsigned long)s_delayed_disarm_ack.seq,
        (unsigned long)s_delayed_disarm_ack.processed_ms);
}
#endif

"""

DISARM_OLD = """        case UART_FRAME_TYPE_DISARM:
            motor_output_stop_all();
            s_vx_mmps = 0;
            s_w_mradps = 0;
            if (estop_enforce_latch() == 0U) {
                s_state = ROBOT_DISARMED;
                s_reason = ROBOT_REASON_DISARM;
            }
            s_last_seq = frame.seq;"""
DISARM_NEW = """        case UART_FRAME_TYPE_DISARM:
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            delay_disarm_ack = delayed_disarm_ack_eligible();
            s_delayed_disarm_ack.zero_cmd_seen = 0U;
#endif
            motor_output_stop_all();
            s_vx_mmps = 0;
            s_w_mradps = 0;
            if (estop_enforce_latch() == 0U) {
                s_state = ROBOT_DISARMED;
                s_reason = ROBOT_REASON_DISARM;
            }
            s_last_seq = frame.seq;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            if (delay_disarm_ack != 0U && s_state == ROBOT_DISARMED) {
                delayed_disarm_ack_schedule(frame.seq);
                return;
            }
#endif"""

CHANGES = [
    ("시험 설정과 중복 주입 방지", "#define UART_MVP_SUPPRESS_PONG_TEST_ENABLED             0U",
     "#define UART_MVP_SUPPRESS_PONG_TEST_ENABLED             0U\n\n" + CONFIG),
    ("지연 응답 저장 공간", "static int32_t s_right_cps;",
     "static int32_t s_right_cps;\n\n" + STATE),
    ("이번 ARM 이후 수락한 zero CMD 표시", '    send_ack(frame->seq, "CMD");',
     """#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    s_delayed_disarm_ack.zero_cmd_seen =
        (uint8_t)(s_vx_mmps == 0 && s_w_mradps == 0);
#endif
    send_ack(frame->seq, "CMD");"""),
    ("지연 응답 함수와 handle_line 지역 변수",
     """static void handle_line(const char *line, size_t line_len){
    uart_frame_t frame;
    uart_frame_parse_result_t parse_result;""",
     HELPERS + """static void handle_line(const char *line, size_t line_len){
    uart_frame_t frame;
    uart_frame_parse_result_t parse_result;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    uint8_t delay_disarm_ack;
#endif"""),
    ("DISARM 처리 앞부분 전체", DISARM_OLD, DISARM_NEW),
    ("ARM마다 zero CMD 관측 초기화", "        case UART_FRAME_TYPE_ARM:\n            motor_output_stop_all();",
     """        case UART_FRAME_TYPE_ARM:
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            s_delayed_disarm_ack.zero_cmd_seen = 0U;
#endif
            motor_output_stop_all();"""),
    ("부팅/초기화 시 지연 응답 폐기", "    s_stale_pong_sent = 0u;",
     """    s_stale_pong_sent = 0u;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    s_delayed_disarm_ack = (delayed_disarm_ack_t){0};
#endif"""),
    ("수신/안전 처리 후 ACK 송신 시각 검사",
     "    if((HAL_GetTick() - s_last_tel_ms) >= TEL_PERIOD_MS){",
     """#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    delayed_disarm_ack_poll();
#endif

    if((HAL_GetTick() - s_last_tel_ms) >= TEL_PERIOD_MS){"""),
]


def prepare():
    text = STM.read_text(encoding="utf-8")
    if MODE in text:
        raise ValueError("Candidate already present; use --saved to review the user's file")
    for label, old, new in CHANGES:
        if text.count(old) != 1:
            raise ValueError(f"Exact replacement range changed: {label}")
        text = text.replace(old, new, 1)
    return text
