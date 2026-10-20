# STM 목표 거리 명령과 PWM 차단 입력

`TK-MVP-03-06`의 세 번째 입력 묶음이다. 앞 단계의 `distance_move.h/.c`와5ms count·비동기 UART 저장본은 PC 검사를 통과했다. 이번에는 **UART 목표 명령 → STM 거리 상태 → 좌우 PWM 차단**을 연결한다.

수정 대상은 `Core/Inc/uart_frame_parser.h`, `Core/Src/uart_frame_parser.c`, `Core/Src/uart_mvp_protocol.c` 세 파일이다. 아래 각 항목에서 **교체**로 표시한 기존 블록을 삭제한 뒤 새 블록을 넣는다. **삽입**으로 표시한 helper 묶음만 기존 함수 앞에 추가한다. 같은 이름의 기존 함수/case를 남겨 두고 새 정의를 덧붙이지 않는다. 이번에는 모든 블록을 입력·저장한 뒤 실제 저장본 검사를 받는다.

## 목표 명령과 단위

기존 CMD에 마지막 선택 필드를 추가한다. 다음은 형식 설명이며 지금 보드로 보내라는 지시가 아니다.

```text
CMD,seq=123,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=50
```

| 목표 링크 이동량 | distance_mm | 상대 목표 count |
| --- | --- | --- |
| 5cm | 50 | 578 |
| 10cm | 100 | 1156 |
| 15cm | 150 | 1734 |
| 20cm | 200 | 2312 |

거리 필드가 없으면 기존 일반 CMD다. 명시한 거리0·음수·그 외 값, 중복/잘못된 순서/추가 데이터, 전진100·회전0 이외의 목표 명령은 거부한다. `vx_mmps=100`은 현재 mapper의 전진 출력 요청이며 실제100mm/s를 보장하지 않는다. ACK/ERR의 type은 기존 CMD를 유지한다.

거리 계수는 기하 초기값 `1687/19500 mm/count`다. 수동 측정으로 회귀 보정한 계수가 아니며 실제 오차를 이번 시험에서 확인한다. 한쪽이 목표에 도달한 순간 그쪽 출력을0으로 유지하고, 다른 쪽은 자기 목표까지 구동한다. 이 개별 차단은 공중 링크 이동 시험용이며 지상 직진 궤적 제어로 바로 사용하지 않는다.

## 시작점과 출력 소유권

첫 목표 전에 성공한 ARM의 유효 sample,20ms 이내 count, 요청/PWM/CPS0과100ms 이상 정지한 count가 필요하다. ARM 이후 처음 발행한 sample부터 정지 시간을 새로 확인한다. 정지 기준이 부족한 요청은 출력을 끄고 DISARMED로 종료한다. 오래된 CPS0만 보고 움직이는 궤도를 정지 상태로 오인하지 않도록 count 변화도 확인한다.

```text
새 ARM → post-ARM 정지 기준점100ms → 첫 목표 CMD
                                  ↓
                        RUNNING: 좌/우144/150‰
                        ├─ 왼쪽 도달 → 좌0, 우 계속
                        ├─ 오른쪽 도달 → 우0, 좌 계속
                        ├─ 양쪽 도달 → 양PWM0 / DISTANCE_REACHED
                        └─ 오류·취소 → 양PWM0 / 중단 이유
```

거리 목표를 처음 수락하면 그 ARM 구간의 출력 경로는 거리 처리기가 맡는다. 같은 거리의 다음 CMD는 keepalive이며 시작점·시작 시각을 바꾸지 않는다. 도달 뒤 같은 목표를 계속 보내도 다시 움직이지 않는다. 다른 목표나 일반 비영점 CMD가 들어오면 즉시 중단해 일반 PWM 경로가 차단을 우회하지 못하게 한다.

놓음/포커스 이탈은 기존처럼 거리 필드 없는 CMD0으로 취소한다. 목표 중 취소는 ARMED/PWM0을 유지하지만 그 ARM 구간에서는 다시 출발할 수 없다. 중간 취소나 완료 뒤 새 회차는 DISARM→새 ARM→새 정지 기준점으로 시작한다. 같은 ARM seq를 재전송해 진행량을 초기화하는 요청도 거부한다. 새 ARM 자체가 모터를 구동하지는 않는다.

## 실패와 정지 우선순위

- E-stop·CMD timeout·TX fault·수동 DISARM은 distance 상태와 함께 취소하고 즉시 기존 `motor_output_stop_all()`을 호출한다. 해당 E-stop/timeout/TX/DISARM 이유를 보존한다.
- 실행 중 매 UART poll에서 거리 판정을 호출한다. keepalive 수신 때만 검사하는 방식이 아니다. 새 CMD가 없어도 count 도달과 잘못된 sample을 판정한다.
- 무효/오래된 sample·20ms 초과 poll 간격·count 역행·ARM 불일치·개별 무진행500ms·전체3000ms 초과는 양쪽을 끄고 DISARMED로 종료한다. keepalive가 전체 실행 기한이나 무진행 기한을 늘리지 않는다.
- 기존 TEL20개 필드는 유지하고 reason에 `DISTANCE_RUNNING`, `DISTANCE_REACHED`, `DISTANCE_STALE_SAMPLE`, `DISTANCE_POLL_GAP`, `DISTANCE_NO_PROGRESS` 등의 이유를 보낸다. 새 목표는 ARM 구간으로 식별하며 원시 count는 계속 전송한다.

PWM0 이후 관성 이동이 남을 수 있다. `DISTANCE_REACHED`는 출력 차단 조건이며 정확한 물리 정지나 거리 PASS가 아니다. 실제 시험에서는 궤도가 완전히 멈춘 뒤 좌우 링크의 최종 이동량과 최종 count를 측정한다. 초기 버전은 감속/위치 PID 없이 그 오차부터 관측한다.

## 검증과 다음 단계

[후보 native 검사](validation.json)는 실제 parser·protocol·distance·mapper·motor C를 mock HAL에서 실행했다. 네 목표/좌우 순서/반복 keepalive·취소·목표 변경/일반 CMD 우회 차단·중복 ARM·stationary 기준·invalid/stale/gap/reverse/ARM 오류·무진행/전체 기한·기존 E-stop/timeout/TX fault 정지를 검사했다. 앞선 비동기 UART·5ms count 회귀도 함께 실행했다.

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_distance_control_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
```

입력 후에는 `--saved`로 실제 저장본을 검사한다. PC 검사는 STM 보드 빌드나 실제 정지 지연/거리 오차 근거가 아니다.

ESP의 request parser/executor와 브라우저에는 아직 거리 필드와 거리 버튼을 연결하지 않았다. 이번 입력을 마친 뒤 그 경로에서 기존 ticket/owner/hold-to-run을 유지하면서 거리 필드를 전달하고, 정지 기준점 대기와 완료 상태를 표시한다. 그다음 사용자 두 보드 빌드/flash와 공중5cm 첫 회차로 진행한다. 이번 블록만으로 브라우저에서 거리 명령을 실행할 수 있는 것은 아니다.

## 1. Core/Inc/uart_frame_parser.h

parse result enum 끝 두 줄 교체.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
    UART_FRAME_PARSE_EXTRA_DATA
```

교체할 전체 블록:

```c
    UART_FRAME_PARSE_EXTRA_DATA,
    UART_FRAME_PARSE_DISTANCE_OUT_OF_RANGE
```

## 2. Core/Inc/uart_frame_parser.h

uart_frame_t의 timeout 필드 뒤 distance 필드 추가.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
    uint32_t timeout_ms;
```

교체할 전체 블록:

```c
    uint32_t timeout_ms;
    uint32_t distance_mm; /* 0: ordinary CMD, optional suffix absent. */
```

## 3. Core/Src/uart_frame_parser.c

parse 시작의 safe default 추가.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
    frame->timeout_ms = 0u;
```

교체할 전체 블록:

```c
    frame->timeout_ms = 0u;
    frame->distance_mm = 0u;
```

## 4. Core/Src/uart_frame_parser.c

parse 끝 optional distance suffix 블록 교체.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
    if(cursor.position != cursor.length){
        return UART_FRAME_PARSE_EXTRA_DATA;
    }

    return UART_FRAME_PARSE_OK;
```

교체할 전체 블록:

```c
    if(cursor.position != cursor.length){
        if(!consume_literal(&cursor, ",distance_mm=")){
            return UART_FRAME_PARSE_EXTRA_DATA;
        }
        number_result = parse_u32_value(&cursor, &frame->distance_mm);
        if(number_result == NUMBER_PARSE_OUT_OF_RANGE){
            return UART_FRAME_PARSE_DISTANCE_OUT_OF_RANGE;
        }
        if(number_result != NUMBER_PARSE_OK){
            return UART_FRAME_PARSE_INVALID_NUMBER;
        }
        if(cursor.position != cursor.length){
            return UART_FRAME_PARSE_EXTRA_DATA;
        }
        if(frame->distance_mm != 50U && frame->distance_mm != 100U &&
            frame->distance_mm != 150U && frame->distance_mm != 200U){
            return UART_FRAME_PARSE_DISTANCE_OUT_OF_RANGE;
        }
        if(frame->vx_mmps != 100 || frame->w_mradps != 0){
            return UART_FRAME_PARSE_VELOCITY_OUT_OF_RANGE;
        }
    }

    return UART_FRAME_PARSE_OK;
```

## 5. Core/Src/uart_mvp_protocol.c

distance 모듈 include 추가.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
#include "drive_command_mapper.h"
```

교체할 전체 블록:

```c
#include "drive_command_mapper.h"
#include "distance_move.h"
```

## 6. Core/Src/uart_mvp_protocol.c

robot reason enum 끝 확장.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
    ROBOT_REASON_OUTPUT_ERROR
```

교체할 전체 블록:

```c
    ROBOT_REASON_OUTPUT_ERROR,
    ROBOT_REASON_DISTANCE_RUNNING,
    ROBOT_REASON_DISTANCE_REACHED,
    ROBOT_REASON_DISTANCE_ABORTED
```

## 7. Core/Src/uart_mvp_protocol.c

distance 실행 상태 선언 추가.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
static bool s_encoder_arm_valid;
```

교체할 전체 블록:

```c
static bool s_encoder_arm_valid;
static distance_move_t s_distance_move;
static uint32_t s_distance_mm;
static uint32_t s_distance_still_since_ms;
```

## 8. Core/Src/uart_mvp_protocol.c

reason_name 바로 앞에 거리 중단 이유 helper 삽입.

`static const char *reason_name(robot_reason_t reason){`로 시작하는 기존 함수 바로 앞에 아래 전체 함수를 삽입한다. 기존 함수는 유지한다.

```c
static const char *distance_abort_name(void){
    switch (s_distance_move.reason){
        case DISTANCE_MOVE_REASON_CANCELLED: return "DISTANCE_CANCELLED";
        case DISTANCE_MOVE_REASON_NOT_PERMITTED: return "DISTANCE_NOT_PERMITTED";
        case DISTANCE_MOVE_REASON_BAD_SAMPLE: return "DISTANCE_BAD_SAMPLE";
        case DISTANCE_MOVE_REASON_STALE_SAMPLE: return "DISTANCE_STALE_SAMPLE";
        case DISTANCE_MOVE_REASON_POLL_GAP: return "DISTANCE_POLL_GAP";
        case DISTANCE_MOVE_REASON_COUNT_REVERSED: return "DISTANCE_REVERSED";
        case DISTANCE_MOVE_REASON_COUNT_RANGE: return "DISTANCE_COUNT_RANGE";
        case DISTANCE_MOVE_REASON_RUN_TIMEOUT: return "DISTANCE_RUN_TIMEOUT";
        case DISTANCE_MOVE_REASON_NO_PROGRESS: return "DISTANCE_NO_PROGRESS";
        case DISTANCE_MOVE_REASON_BAD_TARGET: return "DISTANCE_BAD_TARGET";
        case DISTANCE_MOVE_REASON_NONE:
        default: return "DISTANCE_ABORTED";
    }
}
```

## 9. Core/Src/uart_mvp_protocol.c

reason_name 출력 확장.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
        case ROBOT_REASON_OUTPUT_ERROR:
            return "OUTPUT_ERROR";
```

교체할 전체 블록:

```c
        case ROBOT_REASON_OUTPUT_ERROR:
            return "OUTPUT_ERROR";
        case ROBOT_REASON_DISTANCE_RUNNING:
            return "DISTANCE_RUNNING";
        case ROBOT_REASON_DISTANCE_REACHED:
            return "DISTANCE_REACHED";
        case ROBOT_REASON_DISTANCE_ABORTED:
            return distance_abort_name();
```

## 10. Core/Src/uart_mvp_protocol.c

parse error 문자열 확장.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
        case UART_FRAME_PARSE_TIMEOUT_OUT_OF_RANGE:
            return "TIMEOUT_OUT_OF_RANGE";
```

교체할 전체 블록:

```c
        case UART_FRAME_PARSE_TIMEOUT_OUT_OF_RANGE:
            return "TIMEOUT_OUT_OF_RANGE";
        case UART_FRAME_PARSE_DISTANCE_OUT_OF_RANGE:
            return "DISTANCE_OUT_OF_RANGE";
```

## 11. Core/Src/uart_mvp_protocol.c

TX fault 시 distance 취소 추가; 함수 전체 교체.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

교체 시작: `static void uart_tx_force_safe(void){`

해당 함수 또는 case 전체를 교체한다. 다음 함수/case는 유지한다.

교체할 전체 블록:

```c
static void uart_tx_force_safe(void){
    if (s_tx_fault == 0U){
        s_error_count++;
    }
    s_tx_fault = 1U;
    distance_move_cancel(&s_distance_move);
    motor_output_stop_all();
    s_vx_mmps = 0;
    s_w_mradps = 0;
    if (s_estop_latched == 0U){
        s_state = ROBOT_DISARMED;
        s_reason = ROBOT_REASON_OUTPUT_ERROR;
    }
}
```

## 12. Core/Src/uart_mvp_protocol.c

E-stop 시 distance 취소 추가; 함수 전체 교체.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

교체 시작: `static void estop_latch_and_force_safe(void) {`

해당 함수 또는 case 전체를 교체한다. 다음 함수/case는 유지한다.

교체할 전체 블록:

```c
static void estop_latch_and_force_safe(void) {
    uint8_t input_active = estop_input_active();

    distance_move_cancel(&s_distance_move);
    motor_output_stop_all();
    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_estop_latched = 1U;
    s_state = ROBOT_FAULT;
    s_reason = (input_active != 0U)
        ? ROBOT_REASON_ESTOP_ACTIVE
        : ROBOT_REASON_ESTOP_LATCHED;
}
```

## 13. Core/Src/uart_mvp_protocol.c

CMD timeout 시 distance 취소 추가; 함수 전체 교체.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

교체 시작: `static void command_timeout_enforce(void) {`

해당 함수 또는 case 전체를 교체한다. 다음 함수/case는 유지한다.

교체할 전체 블록:

```c
static void command_timeout_enforce(void) {
    if(s_state != ROBOT_ARMED){
        return;
    }

    if((HAL_GetTick() - s_last_cmd_ms) < s_cmd_timeout_ms){
        return;
    }

    distance_move_cancel(&s_distance_move);
    motor_output_stop_all();
    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_state = ROBOT_DISARMED;
    s_reason = ROBOT_REASON_CMD_TIMEOUT;
}
```

## 14. Core/Src/uart_mvp_protocol.c

handle_cmd 바로 앞에 distance 전용 처리 함수 묶음 삽입.

`static void handle_cmd(const uart_frame_t *frame){`로 시작하는 기존 함수 바로 앞에 아래 전체 함수를 삽입한다. 기존 함수는 유지한다.

```c
static distance_move_sample_t distance_sample_now(void){
    distance_move_sample_t sample = {
        .left_count = s_encoder_sample.left_count,
        .right_count = s_encoder_sample.right_count,
        .sample_ms = s_encoder_sample.sample_ms,
        .valid = s_encoder_sample.valid && s_encoder_sample.arm_valid &&
            s_encoder_arm_valid && s_encoder_sample.arm_seq == s_encoder_arm_seq
    };
    return sample;
}

static void distance_abort_output(void){
    distance_move_cancel(&s_distance_move);
    motor_output_stop_all();
    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_state = ROBOT_DISARMED;
    s_reason = ROBOT_REASON_DISTANCE_ABORTED;
}

static void distance_motion_enforce(void){
    drive_command_request_t request;
    distance_move_sample_t sample;
    distance_move_output_t gate;
    uint32_t now_ms;
    if (s_distance_mm == 0U){
        return;
    }
    /* Preserve the E-stop/timeout/transport reason after their immediate stop. */
    if (s_state != ROBOT_ARMED || s_estop_latched != 0U || s_tx_fault != 0U){
        distance_move_cancel(&s_distance_move);
        motor_output_stop_all();
        return;
    }
    now_ms = HAL_GetTick();
    sample = distance_sample_now();
    distance_move_update(&s_distance_move, &sample, now_ms,
        (uint32_t)(now_ms - s_last_cmd_ms) < s_cmd_timeout_ms);
    if (s_distance_move.phase == DISTANCE_MOVE_ABORTED){
        if (s_distance_move.reason == DISTANCE_MOVE_REASON_CANCELLED){
            motor_output_stop_all();
            s_vx_mmps = 0;
            s_w_mradps = 0;
            s_reason = ROBOT_REASON_DISTANCE_ABORTED;
            return;
        }
        distance_abort_output();
        return;
    }
    if (s_distance_move.phase == DISTANCE_MOVE_TARGET_REACHED){
        motor_output_stop_all();
        s_vx_mmps = 0;
        s_w_mradps = 0;
        s_reason = ROBOT_REASON_DISTANCE_REACHED;
        return;
    }
    if (s_distance_move.phase != DISTANCE_MOVE_RUNNING ||
        !drive_command_map(100, 0, CMD_OUTPUT_DUTY_CAP_PERMILLE, &request)){
        distance_abort_output();
        return;
    }
    gate = distance_move_output(&s_distance_move);
    if (!gate.left_run){ request.left_signed_permille = 0; }
    if (!gate.right_run){ request.right_signed_permille = 0; }
    if (estop_enforce_latch() != 0U){
        return;
    }
    const motor_output_applied_t applied = motor_output_get_applied();
    if ((applied.left_signed_permille != request.left_signed_permille ||
         applied.right_signed_permille != request.right_signed_permille) &&
        motor_output_set_signed(request.left_signed_permille,
                                request.right_signed_permille) != HAL_OK){
        distance_abort_output();
        s_reason = ROBOT_REASON_OUTPUT_ERROR;
        return;
    }
    if (estop_enforce_latch() != 0U){
        return;
    }
    s_vx_mmps = 100;
    s_w_mradps = 0;
    s_reason = ROBOT_REASON_DISTANCE_RUNNING;
}

/* handle_cmd already checked ranges, ARM and E-stop before entering here. */
static void handle_distance_cmd(const uart_frame_t *frame){
    const uint32_t now_ms = HAL_GetTick();
    const bool zero = frame->vx_mmps == 0 && frame->w_mradps == 0;
    distance_move_sample_t sample = distance_sample_now();
    if (UART_MVP_OUTPUT_TEST_ENABLED != 0U){
        distance_abort_output();
        send_err(frame->seq, "CMD", "DISTANCE_TEST_MODE");
        return;
    }
    if (s_distance_mm != 0U && zero && frame->distance_mm == 0U){
        distance_move_cancel(&s_distance_move);
        motor_output_stop_all();
        s_vx_mmps = 0;
        s_w_mradps = 0;
        s_reason = s_distance_move.phase == DISTANCE_MOVE_TARGET_REACHED
            ? ROBOT_REASON_DISTANCE_REACHED : ROBOT_REASON_DISTANCE_ABORTED;
        /* Keep ARM for the stop ACK; nonzero commands stay locked this epoch. */
    }
    else{
        if (frame->distance_mm == 0U || frame->vx_mmps != 100 ||
            frame->w_mradps != 0 ||
            (s_distance_mm != 0U && frame->distance_mm != s_distance_mm)){
            distance_abort_output();
            send_err(frame->seq, "CMD", "DISTANCE_LOCKED");
            return;
        }
        if (s_distance_mm == 0U){
            const motor_output_applied_t applied = motor_output_get_applied();
            if (!sample.valid ||
                (uint32_t)(now_ms - sample.sample_ms) > DISTANCE_MOVE_MAX_SAMPLE_AGE_MS ||
                (uint32_t)(now_ms - s_distance_still_since_ms) < 100U ||
                s_left_cps != 0 || s_right_cps != 0 ||
                s_vx_mmps != 0 || s_w_mradps != 0 ||
                applied.left_signed_permille != 0 || applied.right_signed_permille != 0){
                distance_abort_output();
                send_err(frame->seq, "CMD", "DISTANCE_NOT_STILL");
                return;
            }
            s_distance_mm = frame->distance_mm;
            if (!distance_move_start(&s_distance_move, frame->distance_mm,
                                     &sample, now_ms, true)){
                distance_abort_output();
                send_err(frame->seq, "CMD", "DISTANCE_START_FAILED");
                return;
            }
        }
        else if (s_distance_move.phase == DISTANCE_MOVE_ABORTED){
            distance_abort_output();
            send_err(frame->seq, "CMD", "DISTANCE_REARM_REQUIRED");
            return;
        }
    }
    s_last_seq = frame->seq;
    s_cmd_timeout_ms = frame->timeout_ms;
    s_last_cmd_ms = now_ms;
    s_last_accepted_cmd_ms = now_ms;
    s_has_accepted_cmd = 1U;
    if (s_distance_move.phase != DISTANCE_MOVE_ABORTED){
        distance_motion_enforce();
    }
    if (s_state != ROBOT_ARMED){
        send_err(frame->seq, "CMD", "DISTANCE_STOPPED");
        return;
    }
    send_ack(frame->seq, "CMD");
}
```

## 15. Core/Src/uart_mvp_protocol.c

handle_cmd의 검증 후 ordinary PWM 경로 앞에 거리 소유권 분기 추가.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
    const uint16_t duty_cap_permille =
```

교체할 전체 블록:

```c
    if (frame->distance_mm != 0U || s_distance_mm != 0U){
        handle_distance_cmd(frame);
        return;
    }

    const uint16_t duty_cap_permille =
```

## 16. Core/Src/uart_mvp_protocol.c

DISARM case 전체 교체.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

교체 시작: `        case UART_FRAME_TYPE_DISARM:`

해당 함수 또는 case 전체를 교체한다. 다음 함수/case는 유지한다.

교체할 전체 블록:

```c
        case UART_FRAME_TYPE_DISARM:
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            delay_disarm_ack = delayed_disarm_ack_eligible();
            s_delayed_disarm_ack.zero_cmd_seen = 0U;
#endif
            distance_move_cancel(&s_distance_move);
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
#endif

#if UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED
            if(s_duplicate_disarm_ack_seq_sent == 0u){
                s_duplicate_disarm_ack_seq_sent = 1u;
                uart_sendf(
                    "ACK,seq=%lu,seq=%lu,type=DISARM,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_trailing_comma_disarm_ack_sent == 0u){
                s_trailing_comma_disarm_ack_sent = 1u;
                uart_sendf(
                    "ACK,seq=%lu,type=DISARM,t_ms=%lu,\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED
            if(s_overflow_disarm_ack_seq_sent == 0u){
                s_overflow_disarm_ack_seq_sent = 1u;
                uart_sendf(
                    "ACK,seq=4294967296,type=DISARM,t_ms=%lu\n",
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_partial_frame_name_disarm_ack_sent == 0U){
                s_partial_frame_name_disarm_ack_sent = 1U;
                uart_sendf(
                    "AC,seq=%lu,type=DISARM,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_EMBEDDED_CR_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_embedded_cr_disarm_ack_sent == 0u){
                s_embedded_cr_disarm_ack_sent = 1u;
                uart_sendf(
                    "ACK,seq=%lu,\rtype=DISARM,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_CONTROL_BYTE_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_control_byte_disarm_ack_sent == 0u){
                s_control_byte_disarm_ack_sent = 1u;
                uart_sendf(
                    "ACK,seq=%lu," "\x01" "type=DISARM,t_ms=%lu\n",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );
                return;
            }
#endif
#if UART_MVP_OVERLONG_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_overlong_disarm_ack_sent == 0u){
                uint8_t overlong_tail[257u];
                size_t i;

                s_overlong_disarm_ack_sent = 1u;

                uart_sendf(
                    "ACK,seq=%lu,type=DISARM,t_ms=%lu,",
                    (unsigned long)frame.seq,
                    (unsigned long)HAL_GetTick()
                );

                for(i = 0U; i < 256U; i++){
                    overlong_tail[i] = (uint8_t)'X';
                }

                overlong_tail[256U] = (uint8_t)'\n';

                (void)HAL_UART_Transmit(
                    s_uart,
                    overlong_tail,
                    (uint16_t)sizeof(overlong_tail),
                    100
                );
                return;
            }
#endif
#if UART_MVP_STALE_DISARM_ACK_ONCE_TEST_ENABLED
            if(s_stale_disarm_ack_sent == 0u){
                s_stale_disarm_ack_sent = 1u;
                send_ack(frame.seq - 1u, "DISARM");
                return;
            }
#endif
#if UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED
            if(s_wrong_disarm_ack_type_sent == 0u){
                s_wrong_disarm_ack_type_sent = 1u;
                send_ack(frame.seq, "ARM");
                return;
            }
#endif
            send_ack(frame.seq, "DISARM");
            return;
```

## 17. Core/Src/uart_mvp_protocol.c

ARM case 전체 교체; 새 ARM에서만 거리 기준 초기화.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

교체 시작: `        case UART_FRAME_TYPE_ARM:`

해당 함수 또는 case 전체를 교체한다. 다음 함수/case는 유지한다.

교체할 전체 블록:

```c
        case UART_FRAME_TYPE_ARM:
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            s_delayed_disarm_ack.zero_cmd_seen = 0U;
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
            s_cmd_ack_drop_zero_count = 0U;
#endif
            if (s_distance_mm != 0U && frame.seq == s_encoder_arm_seq){
                distance_abort_output();
                send_err(frame.seq, "ARM", "DISTANCE_DUPLICATE_ARM");
                return;
            }
            distance_move_init(&s_distance_move);
            s_distance_mm = 0U;
            s_distance_still_since_ms = HAL_GetTick();
            motor_output_stop_all();

            s_vx_mmps = 0;
            s_w_mradps = 0;
            s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
            s_last_cmd_ms = HAL_GetTick();
            s_state = ROBOT_ARMED;
            s_reason = ROBOT_REASON_NONE;
            s_last_seq = frame.seq;
            /* New measurement interval; wait for a post-ARM sample. */
            s_encoder_arm_seq = frame.seq;
            s_encoder_arm_valid = true;
            s_encoder_sample.valid = false;
            s_encoder_sample.arm_valid = false;
            s_encoder_sample.arm_seq = 0U;
            send_ack(frame.seq, "ARM");
            return;
```

## 18. Core/Src/uart_mvp_protocol.c

uart_mvp_init의 거리 상태 초기화 추가.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
    s_encoder_arm_valid = false;
```

교체할 전체 블록:

```c
    s_encoder_arm_valid = false;
    distance_move_init(&s_distance_move);
    s_distance_mm = 0U;
    s_distance_still_since_ms = HAL_GetTick();
```

## 19. Core/Src/uart_mvp_protocol.c

sample setter의 정지 기준점 추적 추가.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
    /* Both paths run in the main loop, not in the UART RX interrupt. */
    s_left_cps = left_cps;
```

교체할 전체 블록:

```c
    /* Count must remain still for100ms after a fresh post-ARM baseline. */
    if (!valid || !s_encoder_sample.valid || left_cps != 0 || right_cps != 0 ||
        left_count != s_encoder_sample.left_count ||
        right_count != s_encoder_sample.right_count ||
        (uint32_t)(sample_ms - s_encoder_sample.sample_ms) > DISTANCE_MOVE_MAX_SAMPLE_AGE_MS){
        s_distance_still_since_ms = sample_ms;
    }
    /* Both paths run in the main loop, not in the UART RX interrupt. */
    s_left_cps = left_cps;
```

## 20. Core/Src/uart_mvp_protocol.c

uart_mvp_process의 매 poll 안전 검사 뒤 거리 판정 추가.

**기존 범위를 삭제하고 다음 전체 블록으로 교체한다. 추가로 붙이지 않는다.**

찾을 기존 블록:

```c
        command_timeout_enforce();
```

교체할 전체 블록:

```c
        command_timeout_enforce();
        distance_motion_enforce();
```
