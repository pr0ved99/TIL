/* Encoder target cutoff logic; no HAL, UART or motor writes. */
#include "distance_move.h"

#include <stddef.h>

static void abort_move(distance_move_t *move, distance_move_reason_t reason)
{
    move->phase = DISTANCE_MOVE_ABORTED;
    move->reason = reason;
}

static bool sample_is_usable(
    distance_move_t *move,
    const distance_move_sample_t *sample,
    uint32_t now_ms
)
{
    if (sample == NULL || !sample->valid) {
        abort_move(move, DISTANCE_MOVE_REASON_BAD_SAMPLE);
        return false;
    }
    if ((uint32_t)(now_ms - sample->sample_ms) >
        DISTANCE_MOVE_MAX_SAMPLE_AGE_MS) {
        abort_move(move, DISTANCE_MOVE_REASON_STALE_SAMPLE);
        return false;
    }
    return true;
}

void distance_move_init(distance_move_t *move)
{
    if (move != NULL) {
        *move = (distance_move_t){0};
    }
}

bool distance_move_target_counts(uint32_t distance_mm, uint32_t *counts)
{
    if (counts == NULL) {
        return false;
    }
    *counts = 0U;
    if (distance_mm != 50U && distance_mm != 100U &&
        distance_mm != 150U && distance_mm != 200U) {
        return false;
    }
    /* Round to nearest count; maximum product here is only 3,900,000. */
    *counts = (distance_mm * DISTANCE_MOVE_MM_DENOMINATOR +
        DISTANCE_MOVE_MM_NUMERATOR / 2U) / DISTANCE_MOVE_MM_NUMERATOR;
    return true;
}

bool distance_move_start(
    distance_move_t *move,
    uint32_t distance_mm,
    const distance_move_sample_t *sample,
    uint32_t now_ms,
    bool motion_permitted
)
{
    uint32_t target;
    if (move == NULL || move->phase != DISTANCE_MOVE_IDLE) {
        return false;
    }
    if (!motion_permitted) {
        abort_move(move, DISTANCE_MOVE_REASON_NOT_PERMITTED);
        return false;
    }
    if (!distance_move_target_counts(distance_mm, &target)) {
        abort_move(move, DISTANCE_MOVE_REASON_BAD_TARGET);
        return false;
    }
    if (!sample_is_usable(move, sample, now_ms)) {
        return false;
    }
    move->target_counts = target;
    move->start_left = move->last_left = sample->left_count;
    move->start_right = move->last_right = sample->right_count;
    move->started_ms = move->last_poll_ms = now_ms;
    move->last_sample_ms = sample->sample_ms;
    move->left_progress_ms = move->right_progress_ms = now_ms;
    move->left_reached = false;
    move->right_reached = false;
    move->reason = DISTANCE_MOVE_REASON_NONE;
    move->phase = DISTANCE_MOVE_RUNNING;
    return true;
}

void distance_move_update(
    distance_move_t *move,
    const distance_move_sample_t *sample,
    uint32_t now_ms,
    bool motion_permitted
)
{
    uint32_t sample_step;
    uint64_t left_delta;
    uint64_t right_delta;
    if (move == NULL || move->phase != DISTANCE_MOVE_RUNNING) {
        return;
    }
    if (!motion_permitted) {
        abort_move(move, DISTANCE_MOVE_REASON_NOT_PERMITTED);
        return;
    }
    if (!sample_is_usable(move, sample, now_ms)) {
        return;
    }
    if ((uint32_t)(now_ms - move->last_poll_ms) >
        DISTANCE_MOVE_MAX_POLL_GAP_MS) {
        abort_move(move, DISTANCE_MOVE_REASON_POLL_GAP);
        return;
    }
    if ((uint32_t)(now_ms - move->started_ms) >= DISTANCE_MOVE_MAX_RUN_MS) {
        abort_move(move, DISTANCE_MOVE_REASON_RUN_TIMEOUT);
        return;
    }
    move->last_poll_ms = now_ms;
    sample_step = sample->sample_ms - move->last_sample_ms;
    if (sample_step >= 0x80000000U ||
        (sample_step == 0U &&
         (sample->left_count != move->last_left ||
          sample->right_count != move->last_right))) {
        abort_move(move, DISTANCE_MOVE_REASON_BAD_SAMPLE);
        return;
    }
    if (sample->left_count < move->last_left ||
        sample->right_count < move->last_right) {
        abort_move(move, DISTANCE_MOVE_REASON_COUNT_REVERSED);
        return;
    }
    /* Unsigned subtraction avoids signed overflow even across zero. */
    left_delta = (uint64_t)sample->left_count - (uint64_t)move->start_left;
    right_delta = (uint64_t)sample->right_count - (uint64_t)move->start_right;
    if (left_delta > (uint64_t)INT32_MAX ||
        right_delta > (uint64_t)INT32_MAX) {
        abort_move(move, DISTANCE_MOVE_REASON_COUNT_RANGE);
        return;
    }
    if (sample->left_count > move->last_left) {
        move->left_progress_ms = now_ms;
    }
    if (sample->right_count > move->last_right) {
        move->right_progress_ms = now_ms;
    }
    move->last_left = sample->left_count;
    move->last_right = sample->right_count;
    move->last_sample_ms = sample->sample_ms;

    /* Each cutoff is latched. Continued input cannot enable that side again. */
    move->left_reached = move->left_reached ||
        left_delta >= move->target_counts;
    move->right_reached = move->right_reached ||
        right_delta >= move->target_counts;
    if (move->left_reached && move->right_reached) {
        move->phase = DISTANCE_MOVE_TARGET_REACHED;
        return;
    }
    if ((!move->left_reached &&
         (uint32_t)(now_ms - move->left_progress_ms) >=
             DISTANCE_MOVE_NO_PROGRESS_MS) ||
        (!move->right_reached &&
         (uint32_t)(now_ms - move->right_progress_ms) >=
             DISTANCE_MOVE_NO_PROGRESS_MS)) {
        abort_move(move, DISTANCE_MOVE_REASON_NO_PROGRESS);
    }
}

void distance_move_cancel(distance_move_t *move)
{
    if (move != NULL && move->phase == DISTANCE_MOVE_RUNNING) {
        abort_move(move, DISTANCE_MOVE_REASON_CANCELLED);
    }
}

distance_move_output_t distance_move_output(const distance_move_t *move)
{
    distance_move_output_t output = {false, false};
    if (move != NULL && move->phase == DISTANCE_MOVE_RUNNING) {
        output.left_run = !move->left_reached;
        output.right_run = !move->right_reached;
    }
    return output;
}
