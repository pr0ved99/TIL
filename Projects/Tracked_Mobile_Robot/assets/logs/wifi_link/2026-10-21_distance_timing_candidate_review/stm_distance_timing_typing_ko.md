# 목표 거리 정지를 위한 엔코더 주기와 UART 송신 입력

`TK-MVP-03-06`의 두 번째 입력 묶음이다. 사용자가 저장한 `distance_move.h/.c`는 독립 모듈 PC 검사를 통과했다. 이번에는 그 모듈이 사용할 **5ms count 발행과 대기 없는 USART1 송신 경로**를 함께 준비한다.

아래 항목을 같은 입력 묶음으로 적용하고 저장한다. 삽입으로 명시한 항목은 기존 선언/정의 앞에 추가하고, 교체 항목은 지정된 기존 범위를 전체 블록으로 바꾼다. 일부 항목은 기존 한 줄을 포함한 블록에 새 선언을 추가하는 형태다. 경로는 모두 `stm32_uart_mvp/Core` 기준이다. 생산 파일 자동 수정은 하지 않았으며, 입력 후 실제 저장본을 다시 검사한다. 이번에는 입력·저장까지만 진행한다.

## count와 CPS의 시간을 나누는 이유

기존 누적 count와 CPS는100ms에 한 번 갱신된다. 그 중간 시점의 count를 얻기 위해 `encoder_speed_snapshot()`을 추가한다. 기존 누적값에 최근 기준 raw counter부터 현재 raw counter까지의 증가량을 더해 현재 count를 계산한다. 이 함수는 기준 counter·누적값·CPS 시간창을 수정하지 않는다. 원래 `encoder_speed_update()`가100ms에 도달하면 같은 증가량을 기준 누적값에 반영하며, snapshot은 새 기준을 사용하므로 이중 누적하지 않는다.

`main.c`에서는5ms 목표 주기로 TIM3/TIM5 raw counter를 읽고 snapshot을 TEL 저장소에 발행한다. 왼쪽은 기존대로 전진 양수로 부호를 바꾼다. CPS는100ms 시간창의 값으로 유지한다. `encoder_t_ms`는 새 count를 읽은 시각이며 CPS가5ms 속도 추정값으로 바뀌는 것은 아니다.

기존 `encoder_speed_log_process()` 이름과 메인 루프 호출은 유지하되, 함수 내부의 반복 `ENC3/ENC5` USB 문자열 출력은 제거한다. 부팅 때의 encoder 자체 검사와 성공/실패 출력은 유지한다. 반복 로그 때문에 구동 중 루프가 UART 송신을 기다리지 않도록 하는 선택이다.

## USART1 송신 흐름과 버퍼 수명

```text
ACK/PONG/ERR → 응답 FIFO 최대4개 ─┐
TEL → 최신 대기 프레임1개 ────────┼→ 고정 송신 버퍼 → HAL_UART_Transmit_IT
                                │                         │
                         응답을 먼저 선택          USART1 IRQ / TX 완료
                                │                         │
                                └──── 다음 main poll ← 완료 flag
```

`HAL_UART_Transmit_IT()`는 데이터를 끝까지 보내고 돌아오는 함수가 아니다. 그래서 stack의 지역 배열을 넘기지 않고, 전송이 끝날 때까지 변경하지 않는 static 송신 버퍼를 사용한다. `uart_sendf()`의 지역 문자열은 먼저 대기 버퍼로 복사한다. 이미 전송 중인 프레임은 중간에 끊거나 섞지 않으며, 다음 프레임부터 응답 FIFO를 TEL보다 먼저 선택한다. 대기 중인 TEL은 최신값 하나로 합치고, 응답 뒤에서50ms 넘게 기다린 TEL은 버린다. 이는 STM 원시 encoder sample 유실이나 RX ring의 drop과 다른 송신 대기 정책이다.

`HAL_UART_TxCpltCallback()`은 완료 flag만 바꾼다. 큐 변경과 출력 상태 변경은 main loop에서 수행한다. 현재 보드에는 USART1 IRQ/NVIC와 `HAL_UART_IRQHandler(&huart1)`가 이미 있으므로 DMA·새 IRQ 설정은 필요하지 않다. 로컬 STM32 HAL 소스에서 `HAL_UART_Transmit_IT()`가 버퍼 포인터를 보관하고, 최종 TC 처리 후 gState를 READY로 바꾸어 callback을 부르는 것을 확인했다.

## 송신 오류와 기존 정지 경로

송신 시작이 HAL_ERROR/HAL_BUSY로 실패하거나, TX 완료가100ms 동안 오지 않거나, 중요한 응답 FIFO가 포화되면 즉시 `motor_output_stop_all()`을 호출하고 속도 요청을0으로 만든다. E-stop latch가 없다면 DISARMED/OUTPUT_ERROR로 표시한다. TX fault는 재부팅까지 유지하며 ARM/CMD로 다시 구동하지 못한다. DISARM이나 ESTOP_RESET이 TX fault를 해제하지 않는다. 전송 중 버퍼는 오류가 나도 재사용하지 않는다. `uart_mvp_init()`은 지금처럼 부팅 시 한 번 호출하는 용도다.

100ms는511byte 이하 프레임의115200baud/8N1 이상적 전송 시간 약44.4ms보다 긴 소프트웨어 감시값이다. 이론 전송 시간이나 PC 검사가 보드의 ISR 지연·정지 지연을 보장하지는 않는다.

수신은 한 번의 `uart_mvp_process()`에서 최대64byte를 처리하고 메인 루프로 돌아온다. 그 안에서도 기존 E-stop과300ms 명령 timeout 검사를 유지한다. TX fault 검사나 TX 완료가 명령 timeout을 갱신하지 않는다. 기존15% 직진·20% 회전 제한과 좌측960/930 gain도 유지한다.

## PC 검사와 실제 검증의 경계

[검사 결과](validation.json)는 실제 후보 C를 native PC에서 실행한 것이다. 기존 mapper→motor 출력/timeout/E-stop, snapshot의16/32bit wrap·역방향·정수 경계,5ms count/100ms CPS 분리, 비동기 버퍼 수명·FIFO·TEL 합치기, 잘못된 UART callback, 응답 포화/전송 실패/완료 누락 시 정지, TX 중 timeout/E-stop, RX64byte 예산을 확인했다.

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_distance_timing_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
```

사용자 입력본은 같은 명령에 `--saved`를 추가한다. 기존 동기 `HAL_UART_Transmit()` mock만 있는 host 검사는 새 비동기 경로를 재현하지 못하므로 이 검사의 adapter로 먼저 확인한다. 동작 자체를 건너뛰거나 옛 PASS를 새 저장본 PASS로 사용하지 않는다.

이번 블록을 저장해도 아직 `distance_move_update()`와 PWM 차단은 호출되지 않는다. 다음 연결 단계에서 목표 명령·정지 기준점·안전 supervisor·출력 소유권·ESP UI를 묶어야 한다. 그 단계에서5ms 호출을 실제 보드에서 유지하는지와 최대 지연, 변경된 UART 응답/텔레메트리,5cm 첫 정지의 실제 잔여 이동량을 확인한다. PC 검사 PASS를 실제 거리 오차 PASS로 확대하지 않는다.

## 입력 순서

아래5개 파일의 지정 범위를 모두 입력한 후 저장한다. 이미 검토한 `distance_move.h/.c`는 그대로 사용한다.

- `Inc/encoder_speed.h`, `Src/encoder_speed.c`
- `Src/main.c`
- `Inc/uart_mvp_protocol.h`, `Src/uart_mvp_protocol.c`

main.c 안의 상수·상태·함수·callback을 포함하여 아래 번호 순서대로 적용하면 된다.


## 1. Inc/encoder_speed.h

encoder_speed_cps_to_millirpm 선언 바로 앞에 snapshot 선언 추가.


`bool encoder_speed_cps_to_millirpm(`로 시작하는 기존 선언/정의 바로 앞에 다음 전체 블록을 삽입한다. 기존 선언/정의는 유지한다.


```c
/* Read current accumulated count without changing the 100ms CPS window. */
bool encoder_speed_snapshot(
    const encoder_speed_t *state,
    uint32_t current_raw,
    int64_t *count
);
```


## 2. Src/encoder_speed.c

encoder_speed_cps_to_millirpm 정의 바로 앞에 snapshot 정의 추가.


`bool encoder_speed_cps_to_millirpm(`로 시작하는 기존 선언/정의 바로 앞에 다음 전체 블록을 삽입한다. 기존 선언/정의는 유지한다.


```c
bool encoder_speed_snapshot(
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
```


## 3. Src/main.c

CPS 주기100ms 유지, count 주기5ms 상수 추가.


찾을 기존 코드:

```c
#define ENCODER_SPEED_SAMPLE_PERIOD_MS      100U
```


입력할 전체 블록:

```c
#define ENCODER_SPEED_SAMPLE_PERIOD_MS      100U
#define ENCODER_COUNT_SAMPLE_PERIOD_MS        5U
```


## 4. Src/main.c

엔코더 상태 선언 뒤 count 발행 시각 추가.


찾을 기존 코드:

```c
static encoder_speed_t s_encoder_tim5;
```


입력할 전체 블록:

```c
static encoder_speed_t s_encoder_tim5;
static uint32_t s_encoder_last_publish_ms;
```


## 5. Src/main.c

encoder_delta_direction 시작부터 motor_output_pin_test_process 직전까지 교체.


교체 시작: `static const char *encoder_delta_direction(`

교체 끝: 위 블록의 마지막 `}`까지.


입력할 전체 블록:

```c
static int32_t encoder_cps_to_i32(int64_t cps){
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
```


## 6. Src/main.c

USER CODE 4의 UART 콜백 묶음 교체.


교체 시작: `void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){`

교체 끝: 위 블록의 마지막 `}`까지.


입력할 전체 블록:

```c
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
  uart_mvp_on_rx_complete(huart);
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart){
  uart_mvp_on_uart_error(huart);
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart){
  uart_mvp_on_tx_complete(huart);
}
```


## 7. Inc/uart_mvp_protocol.h

TX 완료 콜백 진입점 선언 추가.


찾을 기존 코드:

```c
void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);
```


입력할 전체 블록:

```c
void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);
void uart_mvp_on_tx_complete(UART_HandleTypeDef *huart);
```


## 8. Src/uart_mvp_protocol.c

memcpy/strncmp 헤더 추가.


찾을 기존 코드:

```c
#include <stdio.h>
```


입력할 전체 블록:

```c
#include <stdio.h>
#include <string.h>
```


## 9. Src/uart_mvp_protocol.c

uart_sendf 전체를 TX 버퍼/큐/완료/송신 함수 묶음으로 교체.


교체 시작: `static void uart_sendf(const char *fmt, ...){`

교체 끝: 위 블록의 마지막 `}`까지.


입력할 전체 블록:

```c
/* One in-flight frame, four FIFO responses, one coalesced pending TEL. */
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
```


## 10. Src/uart_mvp_protocol.c

handle_line의 switch 직전 ARM/CMD 안전 검사 묶음 교체.


교체 시작: `    if(((frame.type == UART_FRAME_TYPE_ARM) ||`

교체 끝: 위 블록의 마지막 `       }`까지.


입력할 전체 블록:

```c
    if (s_tx_fault != 0U &&
        (frame.type == UART_FRAME_TYPE_ARM || frame.type == UART_FRAME_TYPE_CMD)){
        uart_tx_force_safe();
        return;
    }

    if(((frame.type == UART_FRAME_TYPE_ARM) ||
        (frame.type == UART_FRAME_TYPE_CMD)) &&
       (estop_enforce_latch() != 0U)) {
        send_err(
            frame.seq,
            uart_frame_type_name(frame.type),
            "ESTOP_LATCHED"
        );
        return;
       }
```


## 11. Src/uart_mvp_protocol.c

uart_mvp_init 전체 교체.


교체 시작: `void uart_mvp_init(UART_HandleTypeDef *huart){`

교체 끝: 위 블록의 마지막 `}`까지.


입력할 전체 블록:

```c
void uart_mvp_init(UART_HandleTypeDef *huart){
    s_uart = huart;
    s_rx_byte = 0u;
    s_tx_head = 0U;
    s_tx_count = 0U;
    s_tx_tel_len = 0U;
    s_tx_active = 0U;
    s_tx_completed = 0U;
    s_tx_fault = 0U;

    ring_buffer_init(&s_rx_rb);

    s_line_len = 0u;
    s_line_overflow = 0u;
    s_rx_desync_pending = 0u;
    s_rx_line_mode = UART_RX_COLLECT;

    s_state = ROBOT_DISARMED;
    s_reason = ROBOT_REASON_BOOT;
    s_has_accepted_cmd = 0U;
    s_last_accepted_cmd_ms = 0U;
    s_estop_latched = 0U;
    s_last_seq = 0;
    s_stale_disarm_ack_sent = 0u;
    s_duplicate_disarm_ack_seq_sent = 0u;
    s_trailing_comma_disarm_ack_sent = 0u;
    s_overflow_disarm_ack_seq_sent = 0u;
    s_partial_frame_name_disarm_ack_sent = 0u;
    s_embedded_cr_disarm_ack_sent = 0u;
    s_control_byte_disarm_ack_sent = 0u;
    s_overlong_disarm_ack_sent = 0u;
    s_wrong_disarm_ack_type_sent = 0u;
    s_stale_pong_sent = 0u;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    s_delayed_disarm_ack = (delayed_disarm_ack_t){0};
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    s_cmd_ack_drop_used = 0U;
    s_cmd_ack_drop_zero_count = 0U;
#endif
    s_last_tel_ms = 0u;
    s_error_count = 0u;
    s_left_cps = 0;
    s_right_cps = 0;
    s_encoder_sample = (encoder_sample_t){0};
    s_encoder_arm_seq = 0U;
    s_encoder_arm_valid = false;

    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
    s_last_cmd_ms = 0u;
    (void)estop_enforce_latch();
}
```


## 12. Src/uart_mvp_protocol.c

파일 끝 uart_mvp_process 전체 교체.


교체 시작: `void uart_mvp_process(void){`

교체 끝: 위 블록의 마지막 `}`까지.


입력할 전체 블록:

```c
void uart_mvp_process(void){
    uint8_t byte;
    uint32_t budget = UART_RX_POLL_BYTE_BUDGET;

    uart_tx_poll();
    for(; budget != 0U; budget--){
        (void)estop_enforce_latch();
        command_timeout_enforce();

        if(s_rx_desync_pending != 0u){
            begin_rx_resynchronization();
        }

        if(!ring_buffer_pop(&s_rx_rb, &byte)){
            break;
        }

        if(s_rx_desync_pending != 0u){
            begin_rx_resynchronization();
            continue;
        }

        /* CAN (0x18) cancels a pending line without executing it. 
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
            if(byte == '\n'){
                if(s_rx_line_mode == UART_RX_DISCARD_ERROR){
                    uart_sendf("ERR,seq=0,type=RX,code=RX_DESYNC\n");
                }
                s_rx_line_mode = UART_RX_COLLECT;
            }
            continue;
        }

        if(byte == '\n'){
            if(s_line_len > 0u && s_line[s_line_len - 1u] == '\r'){
                s_line_len--;
            }
            if(s_line_len > UART_FRAME_MAX_LEN){
                s_line_overflow = 1u;
            }
            s_line[s_line_len] = '\0';

            if(s_line_overflow){
                s_error_count++;
                uart_sendf("ERR,seq=0,type=RX,code=LINE_OVERFLOW\n");
            }
            else if(s_line_len > 0u){
                handle_line(s_line, (size_t)s_line_len);
            }

            s_line_len = 0u;
            s_line_overflow = 0u;
            continue;
        }

        if(s_line_len < (UART_LINE_BUFFER_SIZE - 1u)){
            s_line[s_line_len] = (char)byte;
            s_line_len++;
        }
        else{
            s_line_overflow = 1u;
        }
    }

#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    delayed_disarm_ack_poll();
#endif

    if((HAL_GetTick() - s_last_tel_ms) >= TEL_PERIOD_MS){
        s_last_tel_ms = HAL_GetTick();
        send_tel();
    }
    uart_tx_poll();
}
```
