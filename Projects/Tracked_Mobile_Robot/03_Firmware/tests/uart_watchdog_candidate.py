"""Prepare AC-S06 in memory. Never overwrite the learning-target firmware."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE.parent / 'esp32_wifi_link/main/wifi_link_main.c'
ROOT = HERE.parent.parent
OUT = ROOT / 'assets/logs/wifi_link/2026-10-16_ur03_acs06_cmd_timeout_preparation'


def changes(source):
    config_start = source.index('/* 0: normal image; 1: partial CMD;')
    config_end = source.index('#define WS_MAX_CLIENTS', config_start)
    old_config = source[config_start:config_end].rstrip()
    new_config = old_config.replace('2: ARM without LF.', '2: ARM without LF; 3: CMD_TIMEOUT / NOT_ARMED.')
    new_config = new_config.replace('> 2U', '> 3U').replace('must be 0, 1 or 2', 'must be 0, 1, 2 or 3')
    new_config = new_config.replace('#if WIFI_UART_PARTIAL_TEST_MODE != 0U', '''#if WIFI_UART_PARTIAL_TEST_MODE == 3U
#define WIFI_UART_PARTIAL_TEST_BANNER \\
    "<p><strong>AC-S06 시간초과 시험 이미지</strong> · 제어 IDLE과 별도로 시험 UART 동작 · 일반 PING/ARM/CMD 비활성 · 수동 DISARM 가능</p>"
#elif WIFI_UART_PARTIAL_TEST_MODE != 0U''')
    start = source.index('/* UART_PARTIAL_TEST_BEGIN')
    end = source.index('/* UART_PARTIAL_TEST_END */', start) + len('/* UART_PARTIAL_TEST_END */')
    old_block = source[start:end]
    extra = (HERE/'uart_watchdog_test_block.c').read_text(encoding='utf-8')
    declarations, functions = extra.split('/* WATCHDOG_FUNCTIONS */', 1)
    new_block = old_block.replace('static bool s_uart_test_prefix_full;',
        'static bool s_uart_test_prefix_full;\n\n'+declarations.rstrip())
    new_block = new_block.replace('s->tel.left_pwm == 0 && s->tel.right_pwm == 0;',
        's->tel.left_pwm == 0 && s->tel.right_pwm == 0 &&\n'
        '        (WIFI_UART_PARTIAL_TEST_MODE != 3U || wifi_watchdog_zero_locked(now));')
    new_block = new_block.replace('} else if (s_uart_test_phase == UART_TEST_HOLD) {',
        '} else if (s_uart_test_phase == UART_TEST_HOLD) {\n'
        '        if (WIFI_UART_PARTIAL_TEST_MODE == 3U && s_watchdog.problem == NULL)\n'
        '            s_watchdog.problem = "CANCELLED";', 1)
    marker = '/* Called only by stm_uart_rx_task, before normal control/command dispatch.'
    new_block = new_block.replace(marker, functions.strip()+'\n\n'+marker)
    new_block = new_block.replace('    if (WIFI_UART_PARTIAL_TEST_MODE == 0U) return;\n    char prefix',
        '    if (WIFI_UART_PARTIAL_TEST_MODE == 0U) return;\n'
        '    if (WIFI_UART_PARTIAL_TEST_MODE == 3U) { wifi_watchdog_step(); return; }\n    char prefix')
    old_reply = '    const bool matched = wifi_control_executor_reply(&s_control, op, seq, ack, t_ms, wifi_control_now());'
    new_reply = '''    const bool test_matched = wifi_watchdog_reply_locked(op, seq, ack,
        ack ? NULL : code, t_ms, wifi_control_now());
    const bool matched = test_matched ||
        wifi_control_executor_reply(&s_control, op, seq, ack, t_ms, wifi_control_now());'''
    return [('시험 설정 전체', old_config, new_config),
            ('UART_PARTIAL_TEST_BEGIN부터 UART_PARTIAL_TEST_END까지 전체', old_block, new_block),
            ('wifi_control_handle_response 안의 matched 선언 한 줄', old_reply, new_reply)]


def prepare():
    source = MAIN.read_text(encoding='utf-8')
    assert 'wifi_watchdog_step' not in source, 'Use --saved after entry'
    for _, old, new in changes(source):
        assert source.count(old) == 1
        source = source.replace(old, new)
    return source
