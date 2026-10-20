# 빠른 count와 비동기 UART 저장본 교정

현재 저장본은 구조 검사 FAIL이다. 아래4개 교정 블록을3개 파일에 함께 적용한다. 펌웨어는 자동 수정하지 않았다. 모든 교정을 적용한 메모리상의 후보는 `corrected_candidate.json`의 native 검사를 통과했다. 후보 PASS를 현재 저장본 PASS로 해석하지 않는다.

| 파일 | 발견한 문제 | 영향 |
| --- | --- | --- |
| encoder_speed.c | snapshot의 if 조건 닫는 괄호 하나 누락 | 컴파일 오류 |
| uart_mvp_protocol.h | UART_HandelTypeDef | HAL 타입명 오타로 컴파일 오류 |
| main.c | s_encoder_last_publishh_ms 선언 | 사용하는 변수명과 달라 컴파일 오류 |
| main.c | CPS 상한 비교가 cps < INT32_MAX | 정상 CPS도 INT32_MAX로 반환하는 논리 오류 |
| main.c | left_raw_coutn | 미선언 변수명으로 컴파일 오류 |
| main.c | 기존 helper·로그 함수가 아래쪽에 남음 | 두 함수 중복 정의, 옛 blocking 로그 잔존·삭제된 direction helper 참조 |

아래 코드는 지정 범위를 전체 교체하는 연결된 수정 묶음이다. main.c의 마지막 교체 범위에는 새로 입력한 잘못된 두 함수와 그 아래 남은 기존 두 함수가 **모두 포함**된다. 끝점인 `motor_output_pin_test_process`는 삭제하지 않는다. 그러면 두 함수가 각각 하나만 남고 반복 ENC3/ENC5 송신도 제거된다.

송신 큐·완료 callback·TX fault의 ARM/CMD 차단·초기화·RX 예산은 별도로 읽어 기존 안내와 대조했다. encoder_speed.h는 snapshot 선언이 올바르게 추가돼 있다. 이 부분을 다시 입력할 필요는 없다.

교정 후 입력·저장까지 마치고 저장본 검사를 다시 받는다. 현재 상태에서 보드 빌드/플래시/구동을 진행하지 않는다. 새 경로의 실제 IRQ 주기와 목표 거리/PWM 연결은 이후 단계다.

## 1. Core/Inc/uart_mvp_protocol.h

TX 완료 함수 선언 한 줄을 교체한다.

찾을 기존 블록:

```c
void uart_mvp_on_tx_complete(UART_HandelTypeDef *huart);
```

교체할 전체 코드:

```c
void uart_mvp_on_tx_complete(UART_HandleTypeDef *huart);
```

## 2. Core/Src/encoder_speed.c

encoder_speed_snapshot 정의 전체를 교체한다; 다음 encoder_speed_cps_to_millirpm 직전까지.

교체 시작 줄: `bool encoder_speed_snapshot(`

교체할 전체 코드:

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

## 3. Core/Src/main.c

USER CODE PV의 엔코더 상태 선언 세 줄을 교체한다.

찾을 기존 블록:

```c
static encoder_speed_t s_encoder_tim3;
static encoder_speed_t s_encoder_tim5;
static uint32_t s_encoder_last_publishh_ms;
```

교체할 전체 코드:

```c
static encoder_speed_t s_encoder_tim3;
static encoder_speed_t s_encoder_tim5;
static uint32_t s_encoder_last_publish_ms;
```

## 4. Core/Src/main.c

첫 번째 encoder_cps_to_i32부터 motor_output_pin_test_process 직전까지 모두 교체한다.

교체 시작 줄: `static int32_t encoder_cps_to_i32(int64_t cps){`

교체할 전체 코드:

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

## PC 검사 범위

실제 입력본 검사는 `test_distance_timing_candidate.py --saved`이며, 현재는 중복 함수 구조 검사에서 중단했다. `saved_validation.json`과 `saved_failure.txt`에 이 결과를 남겼다. 교정 후보에는 같은 native 검사를 적용하여 snapshot/정수 경계·5ms count/100ms CPS·ARM 기준점·비동기 송신/버퍼·실패/포화 정지·기존 timeout/E-stop 회귀를 확인했다. PC 검사는 MCU build나 실물 정지 근거가 아니다.
