"""One-shot CMD ACK omission candidate; never edits production firmware."""
from pathlib import Path
import re

STM = Path(__file__).resolve().parent.parent / "stm32_uart_mvp/Core/Src/uart_mvp_protocol.c"
MODE = "UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED"

CONFIG = r"""/* Bench only: omit the tenth eligible zero CMD ACK once per STM boot. */
#define UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED 0U

#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED > 1U
#error "CMD ACK drop test mode must be 0 or 1"
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED && ( \
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
    UART_MVP_STALE_PONG_ONCE_TEST_ENABLED || \
    UART_MVP_SUPPRESS_PONG_TEST_ENABLED || \
    UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED)
#error "Do not combine CMD ACK drop with another bench fault/output mode"
#endif"""

STATE = """#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
static uint8_t s_cmd_ack_drop_used;
static uint8_t s_cmd_ack_drop_zero_count;
#endif"""

HELPER = r"""#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
static uint8_t drop_cmd_ack_once(uint32_t seq)
{
    const motor_output_applied_t applied = motor_output_get_applied();
    if (s_cmd_ack_drop_used != 0U) {
        return 0U;
    }
    if (s_state != ROBOT_ARMED || s_estop_latched != 0U ||
        estop_input_active() != 0U || s_vx_mmps != 0 || s_w_mradps != 0 ||
        applied.left_signed_permille != 0 || applied.right_signed_permille != 0 ||
        s_left_cps != 0 || s_right_cps != 0) {
        s_cmd_ack_drop_zero_count = 0U;
        return 0U;
    }
    if (++s_cmd_ack_drop_zero_count < 10U) {
        return 0U;
    }
    s_cmd_ack_drop_used = 1U;
    uart_sendf("TEST_CMD_ACK_DROP,seq=%lu,t_ms=%lu,zero_count=%lu\n",
        (unsigned long)seq,
        (unsigned long)HAL_GetTick(),
        (unsigned long)s_cmd_ack_drop_zero_count);
    return 1U;
}
#endif

"""


def changes(source):
    """Complete function/case blocks and unique declaration anchors for typing."""
    start = source.index("static void handle_cmd(const uart_frame_t *frame){")
    end = source.index("\n#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED\nstatic uint8_t delayed_disarm_ack_eligible", start)
    old_cmd = source[start:end].rstrip()
    new_cmd = old_cmd.replace('    send_ack(frame->seq, "CMD");', '''#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    if (drop_cmd_ack_once(frame->seq) != 0U) {
        return;
    }
#endif
    send_ack(frame->seq, "CMD");''')
    start = source.index("        case UART_FRAME_TYPE_ARM:")
    end = source.index("\n        case UART_FRAME_TYPE_ESTOP_RESET:", start)
    old_arm = source[start:end].rstrip()
    new_arm = old_arm.replace("            motor_output_stop_all();", """#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
            s_cmd_ack_drop_zero_count = 0U;
#endif
            motor_output_stop_all();""", 1)
    start = source.index("void uart_mvp_init(UART_HandleTypeDef *huart){")
    end = source.index("\nvoid uart_mvp_set_encoder_cps(", start)
    old_init = source[start:end].rstrip()
    new_init = old_init.replace("    s_last_tel_ms = 0u;", """#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    s_cmd_ack_drop_used = 0U;
    s_cmd_ack_drop_zero_count = 0U;
#endif
    s_last_tel_ms = 0u;""", 1)
    return [
        ("시험 설정과 중복 주입 방지", "typedef enum{\n    ROBOT_DISARMED = 0,",
         CONFIG + "\n\ntypedef enum{\n    ROBOT_DISARMED = 0,"),
        ("부팅당 사용 여부와 zero CMD 개수", "static int32_t s_right_cps;",
         "static int32_t s_right_cps;\n\n" + STATE),
        ("ACK 생략 함수와 handle_cmd 전체", old_cmd, HELPER + new_cmd),
        ("ARM 분기 전체", old_arm, new_arm),
        ("uart_mvp_init 전체", old_init, new_init),
    ]


def prepare():
    source = STM.read_text(encoding="utf-8")
    if re.search(r"(?m)^#define\s+" + MODE + r"\s+", source):
        raise ValueError("Candidate already present; use --saved")
    for label, old, new in changes(source):
        if source.count(old) != 1:
            raise ValueError("Exact replacement range changed: " + label)
        source = source.replace(old, new, 1)
    return source
