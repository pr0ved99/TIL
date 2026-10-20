"""Prepare reviewable STM timing edits in memory only; never write Core files."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "stm32_uart_mvp/Core"

SNAPSHOT_DECL = '''/* Read current accumulated count without changing the 100ms CPS window. */
bool encoder_speed_snapshot(
    const encoder_speed_t *state,
    uint32_t current_raw,
    int64_t *count
);

'''

SNAPSHOT = '''bool encoder_speed_snapshot(
    const encoder_speed_t *state,
    uint32_t current_raw,
    int64_t *count
){
    int64_t delta;
    if (count == NULL){
        return false;
    }
    *count = 0;
    if (state == NULL || !state->initialized ||
        !encoder_counter_width_is_valid(state->counter_width)){
        return false;
    }
    delta = encoder_calculate_delta(state->counter_width,
        encoder_normalize_raw(state->counter_width, current_raw),
        state->previous_raw);
    if ((delta > 0 && state->accumulated_count > INT64_MAX - delta) ||
        (delta < 0 && state->accumulated_count < INT64_MIN - delta)){
        return false;
    }
    *count = state->accumulated_count + delta;
    return true;
}

'''

MAIN_SAMPLE = '''static int32_t encoder_cps_to_i32(int64_t cps){
    if (cps > (int64_t)INT32_MAX){
        return INT32_MAX;
    }
    if (cps < (int64_t)INT32_MIN){
        return INT32_MIN;
    }
    return (int32_t)cps;
}

static void encoder_speed_log_process(void){
    uint32_t now_ms = HAL_GetTick();
    uint32_t raw3;
    uint32_t raw5;
    int64_t left_raw_count;
    int64_t right_count;
    bool valid;

    /* Name retained for the existing loop call; runtime USB logging removed. */
    if ((uint32_t)(now_ms - s_encoder_last_publish_ms) <
        ENCODER_COUNT_SAMPLE_PERIOD_MS){
        return;
    }
    s_encoder_last_publish_ms = now_ms;
    raw3 = __HAL_TIM_GET_COUNTER(&htim3);
    raw5 = __HAL_TIM_GET_COUNTER(&htim5);
    (void)encoder_speed_update(&s_encoder_tim3, raw3, now_ms);
    (void)encoder_speed_update(&s_encoder_tim5, raw5, now_ms);

    valid = encoder_speed_snapshot(&s_encoder_tim3, raw3, &left_raw_count) &&
        encoder_speed_snapshot(&s_encoder_tim5, raw5, &right_count) &&
        left_raw_count != INT64_MIN;
    uart_mvp_set_encoder_sample(
        encoder_cps_to_i32(-s_encoder_tim3.counts_per_second),
        encoder_cps_to_i32(s_encoder_tim5.counts_per_second),
        valid ? -left_raw_count : 0,
        valid ? right_count : 0,
        now_ms,
        valid
    );
}
'''

TRANSPORT = '''/* One in-flight frame, four FIFO responses, one coalesced pending TEL. */
#define UART_TX_RESPONSE_SLOTS 4U
#define UART_TX_DEADLINE_MS 100U
#define UART_RX_POLL_BYTE_BUDGET 64U
static uint8_t s_tx_frame[UART_TX_BUFFER_SIZE];
static uint8_t s_tx_responses[UART_TX_RESPONSE_SLOTS][UART_TX_BUFFER_SIZE];
static uint16_t s_tx_response_len[UART_TX_RESPONSE_SLOTS];
static uint8_t s_tx_head;
static uint8_t s_tx_count;
static uint8_t s_tx_tel[UART_TX_BUFFER_SIZE];
static uint16_t s_tx_tel_len;
static uint32_t s_tx_tel_ms;
static uint32_t s_tx_started_ms;
static volatile uint8_t s_tx_active;
static uint8_t s_tx_fault;
static volatile uint8_t s_tx_completed;

static void uart_tx_force_safe(void){
    if (s_tx_fault == 0U){
        s_error_count++;
    }
    s_tx_fault = 1U;
    motor_output_stop_all();
    s_vx_mmps = 0;
    s_w_mradps = 0;
    if (s_estop_latched == 0U){
        s_state = ROBOT_DISARMED;
        s_reason = ROBOT_REASON_OUTPUT_ERROR;
    }
}

void uart_mvp_on_tx_complete(UART_HandleTypeDef *huart){
    if (huart == s_uart && s_tx_active != 0U){
        /* ISR only publishes completion; queue and motor state belong to main. */
        s_tx_completed = 1U;
    }
}

static void uart_tx_enqueue(const uint8_t *data, uint16_t length, bool telemetry){
    uint8_t slot;
    if (s_tx_fault != 0U){
        uart_tx_force_safe();
        return;
    }
    if (data == NULL || length == 0U || length >= UART_TX_BUFFER_SIZE){
        uart_tx_force_safe();
        return;
    }
    if (telemetry){
        memcpy(s_tx_tel, data, length);
        s_tx_tel_len = length;
        s_tx_tel_ms = HAL_GetTick();
        return;
    }
    if (s_tx_count >= UART_TX_RESPONSE_SLOTS){
        /* A missing control response must not leave motion enabled. */
        uart_tx_force_safe();
        return;
    }
    slot = (uint8_t)((s_tx_head + s_tx_count) % UART_TX_RESPONSE_SLOTS);
    memcpy(s_tx_responses[slot], data, length);
    s_tx_response_len[slot] = length;
    s_tx_count++;
}

static void uart_tx_poll(void){
    uint16_t length;
    uint32_t now_ms = HAL_GetTick();
    if (s_tx_fault != 0U){
        uart_tx_force_safe();
        return;
    }
    if (s_tx_active != 0U){
        if (s_tx_completed == 0U){
            if ((uint32_t)(now_ms - s_tx_started_ms) >= UART_TX_DEADLINE_MS){
                uart_tx_force_safe();
            }
            return;
        }
        s_tx_active = 0U;
        s_tx_completed = 0U;
    }
    if (s_tx_count != 0U){
        length = s_tx_response_len[s_tx_head];
        memcpy(s_tx_frame, s_tx_responses[s_tx_head], length);
        s_tx_head = (uint8_t)((s_tx_head + 1U) % UART_TX_RESPONSE_SLOTS);
        s_tx_count--;
    }
    else if (s_tx_tel_len != 0U){
        length = s_tx_tel_len;
        s_tx_tel_len = 0U;
        /* Do not transmit a TEL that aged behind a response burst. */
        if ((uint32_t)(now_ms - s_tx_tel_ms) > 50U){
            return;
        }
        memcpy(s_tx_frame, s_tx_tel, length);
    }
    else{
        return;
    }
    s_tx_started_ms = now_ms;
    s_tx_completed = 0U;
    s_tx_active = 1U;
    if (HAL_UART_Transmit_IT(s_uart, s_tx_frame, length) != HAL_OK){
        uart_tx_force_safe();
    }
}

static void uart_sendf(const char *fmt, ...){
    char tx[UART_TX_BUFFER_SIZE];
    va_list args;
    int len;
    if (s_uart == NULL){
        return;
    }
    va_start(args, fmt);
    len = vsnprintf(tx, sizeof(tx), fmt, args);
    va_end(args);
    if (len <= 0 || (size_t)len >= sizeof(tx)){
        uart_tx_force_safe();
        return;
    }
    uart_tx_enqueue((const uint8_t *)tx, (uint16_t)len,
        strncmp(tx, "TEL,", 4U) == 0);
}
'''

def prepare():
    changes = []
    result = {}

    def replace(relative, old, new, label):
        path = CORE / relative
        text = result.get(path, path.read_text(encoding="utf-8"))
        assert text.count(old) == 1, (label, text.count(old))
        result[path] = text.replace(old, new, 1)
        changes.append((relative, label, old, new))

    replace("Inc/encoder_speed.h", "bool encoder_speed_cps_to_millirpm(",
            SNAPSHOT_DECL + "bool encoder_speed_cps_to_millirpm(",
            "encoder_speed_cps_to_millirpm 선언 바로 앞에 snapshot 선언 추가")
    replace("Src/encoder_speed.c", "bool encoder_speed_cps_to_millirpm(",
            SNAPSHOT + "bool encoder_speed_cps_to_millirpm(",
            "encoder_speed_cps_to_millirpm 정의 바로 앞에 snapshot 정의 추가")
    replace("Src/main.c", "#define ENCODER_SPEED_SAMPLE_PERIOD_MS      100U",
            "#define ENCODER_SPEED_SAMPLE_PERIOD_MS      100U\n"
            "#define ENCODER_COUNT_SAMPLE_PERIOD_MS        5U",
            "CPS 주기100ms 유지, count 주기5ms 상수 추가")
    replace("Src/main.c", "static encoder_speed_t s_encoder_tim5;",
            "static encoder_speed_t s_encoder_tim5;\nstatic uint32_t s_encoder_last_publish_ms;",
            "엔코더 상태 선언 뒤 count 발행 시각 추가")
    main = result[CORE / "Src/main.c"]
    start = main.index("static const char *encoder_delta_direction(")
    end = main.index("static void motor_output_pin_test_process(void){", start)
    replace("Src/main.c", main[start:end], MAIN_SAMPLE + "\n",
            "encoder_delta_direction 시작부터 motor_output_pin_test_process 직전까지 교체")
    callback = '''void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
  uart_mvp_on_rx_complete(huart);
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart){
  uart_mvp_on_uart_error(huart);
}'''
    replace("Src/main.c", callback, callback + '''

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart){
  uart_mvp_on_tx_complete(huart);
}''', "USER CODE 4의 UART 콜백 묶음 교체")
    replace("Inc/uart_mvp_protocol.h", "void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);",
            "void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);\n"
            "void uart_mvp_on_tx_complete(UART_HandleTypeDef *huart);",
            "TX 완료 콜백 진입점 선언 추가")
    replace("Src/uart_mvp_protocol.c", "#include <stdio.h>",
            "#include <stdio.h>\n#include <string.h>", "memcpy/strncmp 헤더 추가")
    protocol = result[CORE / "Src/uart_mvp_protocol.c"]
    start = protocol.index("static void uart_sendf(")
    end = protocol.index("static void send_ack(", start)
    replace("Src/uart_mvp_protocol.c", protocol[start:end], TRANSPORT + "\n",
            "uart_sendf 전체를 TX 버퍼/큐/완료/송신 함수 묶음으로 교체")
    protocol = result[CORE / "Src/uart_mvp_protocol.c"]
    start = protocol.index("    if(((frame.type == UART_FRAME_TYPE_ARM)")
    end = protocol.index("    switch(frame.type){", start)
    old = protocol[start:end]
    guard = '''    if (s_tx_fault != 0U &&
        (frame.type == UART_FRAME_TYPE_ARM || frame.type == UART_FRAME_TYPE_CMD)){
        uart_tx_force_safe();
        return;
    }

'''
    replace("Src/uart_mvp_protocol.c", old, guard + old,
            "handle_line의 switch 직전 ARM/CMD 안전 검사 묶음 교체")
    protocol = result[CORE / "Src/uart_mvp_protocol.c"]
    start = protocol.index("void uart_mvp_init(")
    end = protocol.index("void uart_mvp_set_encoder_sample(", start)
    old = protocol[start:end]
    new = old.replace("    s_rx_byte = 0u;", '''    s_rx_byte = 0u;
    s_tx_head = 0U;
    s_tx_count = 0U;
    s_tx_tel_len = 0U;
    s_tx_active = 0U;
    s_tx_completed = 0U;
    s_tx_fault = 0U;''')
    replace("Src/uart_mvp_protocol.c", old, new, "uart_mvp_init 전체 교체")
    protocol = result[CORE / "Src/uart_mvp_protocol.c"]
    start = protocol.index("void uart_mvp_process(void){")
    old = protocol[start:]
    assert old.rstrip().endswith("}")
    new = old.replace("    uint8_t byte;\n\n    for(;;){", '''    uint8_t byte;
    uint32_t budget = UART_RX_POLL_BYTE_BUDGET;

    uart_tx_poll();
    for(; budget != 0U; budget--){''', 1)
    assert new != old
    pos = new.rfind("\n}")
    new = new[:pos] + "\n    uart_tx_poll();" + new[pos:]
    replace("Src/uart_mvp_protocol.c", old, new, "파일 끝 uart_mvp_process 전체 교체")
    return result, changes
