"""Prepare the UART cancellation candidate in memory; never edit firmware files.

The old/new blocks also supply the user's code guide. Production input stays
unchanged until the user types the reviewed changes.
"""
from pathlib import Path

FIRMWARE = Path(__file__).resolve().parent.parent
STM = "stm32_uart_mvp/Core/Src/uart_mvp_protocol.c"
HEADER = "esp32_wifi_link/main/wifi_control_executor.h"
EXECUTOR = "esp32_wifi_link/main/wifi_control_executor.c"
MAIN = "esp32_wifi_link/main/wifi_link_main.c"

CHANGES = [
    (STM, "수신 줄 상태 선언", "static uint8_t s_rx_discard_until_lf;", """typedef enum {
    UART_RX_COLLECT = 0,
    UART_RX_DISCARD_ERROR,
    UART_RX_DISCARD_CANCEL
} uart_rx_line_mode_t;

static uart_rx_line_mode_t s_rx_line_mode;"""),
    (STM, "begin_rx_resynchronization 내부", "    s_rx_discard_until_lf = 1u;",
     "    s_rx_line_mode = UART_RX_DISCARD_ERROR;"),
    (STM, "uart_mvp_init 내부", "    s_rx_desync_pending = 0u;\n    s_rx_discard_until_lf = 0u;",
     "    s_rx_desync_pending = 0u;\n    s_rx_line_mode = UART_RX_COLLECT;"),
    (STM, "uart_mvp_process의 LF 폐기 분기 전체", """        if(s_rx_discard_until_lf != 0u){
            if(byte == '\\n'){
                s_rx_discard_until_lf = 0u;
                uart_sendf("ERR,seq=0,type=RX,code=RX_DESYNC\\n");
            }
            continue;
        }""", """        /* CAN (0x18) cancels a pending line without executing it.
         * Keep discarding through LF; preserve a prior hardware-error report.
         * This changes framing only. DISARM below still owns the stop/ACK.
         */
        if(byte == 0x18u){
            s_line_len = 0u;
            s_line_overflow = 0u;
            if(s_rx_line_mode == UART_RX_COLLECT){
                s_rx_line_mode = UART_RX_DISCARD_CANCEL;
            }
            continue;
        }

        if(s_rx_line_mode != UART_RX_COLLECT){
            if(byte == '\\n'){
                if(s_rx_line_mode == UART_RX_DISCARD_ERROR){
                    uart_sendf("ERR,seq=0,type=RX,code=RX_DESYNC\\n");
                }
                s_rx_line_mode = UART_RX_COLLECT;
            }
            continue;
        }"""),
    (HEADER, "UART 프레임 크기 정의 바로 아래", "#define WIFI_CONTROL_UART_FRAME_SIZE 96U",
     """#define WIFI_CONTROL_UART_FRAME_SIZE 96U
/* ASCII CAN + LF: discard the pending STM line before a new stop command. */
#define WIFI_CONTROL_UART_CANCEL "\\x18\\n"
""".rstrip()),
    (HEADER, "executor 구조체의 폐기된 조건 플래그", "    bool need_line_sync;\n", ""),
    (EXECUTOR, "take_tx의 ARM DISARM 포맷 분기", """    } else {
        n = snprintf(tx.bytes, sizeof(tx.bytes), "%s%s,seq=%" PRIu32 "\\n",
            op == WIFI_CONTROL_OP_DISARM && e->need_line_sync ? "\\n" : "",
            op == WIFI_CONTROL_OP_ARM ? "ARM" : "DISARM", seq);
    }""", """    } else {
        /* Full UART writes do not prove that STM received every byte. */
        n = snprintf(tx.bytes, sizeof(tx.bytes), "%s%s,seq=%" PRIu32 "\\n",
            op == WIFI_CONTROL_OP_DISARM ? WIFI_CONTROL_UART_CANCEL : "",
            op == WIFI_CONTROL_OP_ARM ? "ARM" : "DISARM", seq);
    }"""),
    (EXECUTOR, "tx_complete의 short write 처리", """    if (!full) {
        e->need_line_sync = true;
        /* An intervening cancel already revoked an old ARM/CMD pending. */
        if (e->state.pending == e->prepared_op && e->state.pending_seq == e->prepared_seq) {
            wifi_control_state_tx_failed(&e->state, now);
        }
    } else if (e->prepared_op == WIFI_CONTROL_OP_DISARM) {
        e->need_line_sync = false;
    }""", """    if (!full) {
        /* Every DISARM now cancels a partial line, including after short TX. */
        if (e->state.pending == e->prepared_op && e->state.pending_seq == e->prepared_seq) {
            wifi_control_state_tx_failed(&e->state, now);
        }
    }"""),
    (MAIN, "stm_startup_send_request의 snprintf", """        frame, sizeof(frame),
        "%s,seq=%" PRIu32 "\\n", command, seq);""", """        frame, sizeof(frame),
        "%s%s,seq=%" PRIu32 "\\n",
        ping ? "" : WIFI_CONTROL_UART_CANCEL, command, seq);"""),
    (MAIN, "stm_startup_step SETTLE의 단독 LF 송신", """        if (uart_write_bytes(STM_UART_PORT, "\\n", 1) != 1) {
            stm_startup_fail("line sync TX failed");
            break;
        }

        ESP_LOGI(TAG, "STARTUP: line sync sent");""", """        if (uart_write_bytes(STM_UART_PORT, WIFI_CONTROL_UART_CANCEL, 2) != 2) {
            stm_startup_fail("line cancel TX failed");
            break;
        }

        ESP_LOGI(TAG, "STARTUP: line cancel sent");"""),
    (MAIN, "wifi_command_step의 PING DISARM 포맷", """        line, sizeof(line),
        "%s,seq=%" PRIu32 "\\n", command, s_wifi_uart_pending.seq);""", """        line, sizeof(line),
        "%s%s,seq=%" PRIu32 "\\n",
        request.type == WIFI_COMMAND_DISARM ? WIFI_CONTROL_UART_CANCEL : "",
        command, s_wifi_uart_pending.seq);"""),
    (MAIN, "wifi_command_step의 TX_ERROR 분기", """    } else if (written != length) {
        xSemaphoreTake(s_stm_lock, portMAX_DELAY);
        s_control.need_line_sync = true;
        xSemaphoreGive(s_stm_lock);
        wifi_command_finish("TX_ERROR");""", """    } else if (written != length) {
        wifi_command_finish("TX_ERROR");"""),
]


def prepare():
    paths = dict.fromkeys(path for path, *_ in CHANGES)
    units = {path: (FIRMWARE / path).read_text(encoding="utf-8") for path in paths}
    for path, label, old, new in CHANGES:
        if units[path].count(old) != 1:
            raise ValueError(f"Candidate base changed: {path}: {label}")
        units[path] = units[path].replace(old, new, 1)
    return units
