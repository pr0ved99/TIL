"""STM distance-command integration candidate. Changes stay in memory."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / 'stm32_uart_mvp/Core'

CONTROL = '''static distance_move_sample_t distance_sample_now(void){
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

'''


def prepare():
    result = {}
    changes = []

    def edit(relative, old, new, label):
        p = CORE / relative
        text = result.get(p, p.read_text(encoding='utf-8'))
        assert text.count(old) == 1, (relative, label, text.count(old))
        result[p] = text.replace(old, new, 1)
        changes.append((relative, label, old, new))

    edit('Inc/uart_frame_parser.h', '    UART_FRAME_PARSE_EXTRA_DATA\n',
         '    UART_FRAME_PARSE_EXTRA_DATA,\n    UART_FRAME_PARSE_DISTANCE_OUT_OF_RANGE\n',
         'parse result enum 끝 두 줄 교체')
    edit('Inc/uart_frame_parser.h', '    uint32_t timeout_ms;\n',
         '    uint32_t timeout_ms;\n    uint32_t distance_mm; /* 0: ordinary CMD, optional suffix absent. */\n',
         'uart_frame_t의 timeout 필드 뒤 distance 필드 추가')
    edit('Src/uart_frame_parser.c', '    frame->timeout_ms = 0u;\n',
         '    frame->timeout_ms = 0u;\n    frame->distance_mm = 0u;\n',
         'parse 시작의 safe default 추가')
    old = '''    if(cursor.position != cursor.length){
        return UART_FRAME_PARSE_EXTRA_DATA;
    }

    return UART_FRAME_PARSE_OK;'''
    new = '''    if(cursor.position != cursor.length){
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

    return UART_FRAME_PARSE_OK;'''
    edit('Src/uart_frame_parser.c', old, new, 'parse 끝 optional distance suffix 블록 교체')
    edit('Src/uart_mvp_protocol.c', '#include "drive_command_mapper.h"',
         '#include "drive_command_mapper.h"\n#include "distance_move.h"', 'distance 모듈 include 추가')
    edit('Src/uart_mvp_protocol.c', '    ROBOT_REASON_OUTPUT_ERROR\n',
         '    ROBOT_REASON_OUTPUT_ERROR,\n    ROBOT_REASON_DISTANCE_RUNNING,\n'
         '    ROBOT_REASON_DISTANCE_REACHED,\n    ROBOT_REASON_DISTANCE_ABORTED\n',
         'robot reason enum 끝 확장')
    edit('Src/uart_mvp_protocol.c', 'static bool s_encoder_arm_valid;\n',
         'static bool s_encoder_arm_valid;\nstatic distance_move_t s_distance_move;\n'
         'static uint32_t s_distance_mm;\nstatic uint32_t s_distance_still_since_ms;\n',
         'distance 실행 상태 선언 추가')
    distance_abort_name = '''static const char *distance_abort_name(void){
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

'''
    edit('Src/uart_mvp_protocol.c', 'static const char *reason_name(robot_reason_t reason){',
         distance_abort_name + 'static const char *reason_name(robot_reason_t reason){',
         'reason_name 바로 앞에 거리 중단 이유 helper 삽입')
    edit('Src/uart_mvp_protocol.c', '''        case ROBOT_REASON_OUTPUT_ERROR:
            return "OUTPUT_ERROR";''', '''        case ROBOT_REASON_OUTPUT_ERROR:
            return "OUTPUT_ERROR";
        case ROBOT_REASON_DISTANCE_RUNNING:
            return "DISTANCE_RUNNING";
        case ROBOT_REASON_DISTANCE_REACHED:
            return "DISTANCE_REACHED";
        case ROBOT_REASON_DISTANCE_ABORTED:
            return distance_abort_name();''', 'reason_name 출력 확장')
    edit('Src/uart_mvp_protocol.c', '''        case UART_FRAME_PARSE_TIMEOUT_OUT_OF_RANGE:
            return "TIMEOUT_OUT_OF_RANGE";''', '''        case UART_FRAME_PARSE_TIMEOUT_OUT_OF_RANGE:
            return "TIMEOUT_OUT_OF_RANGE";
        case UART_FRAME_PARSE_DISTANCE_OUT_OF_RANGE:
            return "DISTANCE_OUT_OF_RANGE";''', 'parse error 문자열 확장')
    for begin, end, label in [
        ('static void uart_tx_force_safe(void){', 'void uart_mvp_on_tx_complete(', 'TX fault 시 distance 취소 추가'),
        ('static void estop_latch_and_force_safe(void)', 'static uint8_t estop_enforce_latch(', 'E-stop 시 distance 취소 추가'),
        ('static void command_timeout_enforce(void)', '#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED', 'CMD timeout 시 distance 취소 추가')]:
        p = CORE / 'Src/uart_mvp_protocol.c'
        text = result[p]
        start = text.index(begin)
        stop = text.index(end, start)
        old = text[start:stop]
        assert old.count('    motor_output_stop_all();') == 1
        new = old.replace('    motor_output_stop_all();',
                          '    distance_move_cancel(&s_distance_move);\n    motor_output_stop_all();', 1)
        edit('Src/uart_mvp_protocol.c', old, new, label+'; 함수 전체 교체')
    edit('Src/uart_mvp_protocol.c', 'static void handle_cmd(const uart_frame_t *frame){',
         CONTROL + 'static void handle_cmd(const uart_frame_t *frame){',
         'handle_cmd 바로 앞에 distance 전용 처리 함수 묶음 삽입')
    edit('Src/uart_mvp_protocol.c', '    const uint16_t duty_cap_permille =\n', '''    if (frame->distance_mm != 0U || s_distance_mm != 0U){
        handle_distance_cmd(frame);
        return;
    }

    const uint16_t duty_cap_permille =
''', 'handle_cmd의 검증 후 ordinary PWM 경로 앞에 거리 소유권 분기 추가')
    # A DISARM cancels but does not clear the used-target latch until a new ARM.
    p = CORE / 'Src/uart_mvp_protocol.c'
    text = result[p]
    start = text.index('        case UART_FRAME_TYPE_DISARM:')
    end = text.index('        case UART_FRAME_TYPE_ARM:', start)
    old = text[start:end]
    new = old.replace('            motor_output_stop_all();',
                      '            distance_move_cancel(&s_distance_move);\n            motor_output_stop_all();', 1)
    edit('Src/uart_mvp_protocol.c', old, new, 'DISARM case 전체 교체')
    text = result[p]
    start = text.index('        case UART_FRAME_TYPE_ARM:')
    end = text.index('        case UART_FRAME_TYPE_ESTOP_RESET:', start)
    old = text[start:end]
    new = old.replace('            motor_output_stop_all();', '''            if (s_distance_mm != 0U && frame.seq == s_encoder_arm_seq){
                distance_abort_output();
                send_err(frame.seq, "ARM", "DISTANCE_DUPLICATE_ARM");
                return;
            }
            distance_move_init(&s_distance_move);
            s_distance_mm = 0U;
            s_distance_still_since_ms = HAL_GetTick();
            motor_output_stop_all();''', 1)
    edit('Src/uart_mvp_protocol.c', old, new, 'ARM case 전체 교체; 새 ARM에서만 거리 기준 초기화')
    edit('Src/uart_mvp_protocol.c', '    s_encoder_arm_valid = false;\n',
         '    s_encoder_arm_valid = false;\n    distance_move_init(&s_distance_move);\n'
         '    s_distance_mm = 0U;\n    s_distance_still_since_ms = HAL_GetTick();\n',
         'uart_mvp_init의 거리 상태 초기화 추가')
    edit('Src/uart_mvp_protocol.c', '''    /* Both paths run in the main loop, not in the UART RX interrupt. */
    s_left_cps = left_cps;''', '''    /* Count must remain still for100ms after a fresh post-ARM baseline. */
    if (!valid || !s_encoder_sample.valid || left_cps != 0 || right_cps != 0 ||
        left_count != s_encoder_sample.left_count ||
        right_count != s_encoder_sample.right_count ||
        (uint32_t)(sample_ms - s_encoder_sample.sample_ms) > DISTANCE_MOVE_MAX_SAMPLE_AGE_MS){
        s_distance_still_since_ms = sample_ms;
    }
    /* Both paths run in the main loop, not in the UART RX interrupt. */
    s_left_cps = left_cps;''', 'sample setter의 정지 기준점 추적 추가')
    edit('Src/uart_mvp_protocol.c', '''        command_timeout_enforce();
''', '''        command_timeout_enforce();
        distance_motion_enforce();
''', 'uart_mvp_process의 매 poll 안전 검사 뒤 거리 판정 추가')
    return result, changes
