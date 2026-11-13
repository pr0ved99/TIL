/* Encoder target cutoff for short forward track-distance tests. */
#ifndef DISTANCE_MOVE_H
#define DISTANCE_MOVE_H

#include <stdbool.h>
#include <stdint.h>

/* Initial geometry: 14 teeth * 9.64 mm / 1560 counts = 1687/19500. */
#define DISTANCE_MOVE_MM_NUMERATOR       1687U
#define DISTANCE_MOVE_MM_DENOMINATOR    19500U

/* Software bounds for the proposed short airborne test, not motor ratings. */
#define DISTANCE_MOVE_MAX_SAMPLE_AGE_MS    20U
#define DISTANCE_MOVE_MAX_POLL_GAP_MS      20U
#define DISTANCE_MOVE_MAX_RUN_MS        3000U
#define DISTANCE_MOVE_NO_PROGRESS_MS     500U

typedef enum {
    DISTANCE_MOVE_IDLE = 0,
    DISTANCE_MOVE_RUNNING,
    DISTANCE_MOVE_TARGET_REACHED,
    DISTANCE_MOVE_ABORTED
} distance_move_phase_t;

typedef enum {
    DISTANCE_MOVE_REASON_NONE = 0,
    DISTANCE_MOVE_REASON_BAD_TARGET,
    DISTANCE_MOVE_REASON_NOT_PERMITTED,
    DISTANCE_MOVE_REASON_BAD_SAMPLE,
    DISTANCE_MOVE_REASON_STALE_SAMPLE,
    DISTANCE_MOVE_REASON_POLL_GAP,
    DISTANCE_MOVE_REASON_COUNT_REVERSED,
    DISTANCE_MOVE_REASON_COUNT_RANGE,
    DISTANCE_MOVE_REASON_RUN_TIMEOUT,
    DISTANCE_MOVE_REASON_NO_PROGRESS,
    DISTANCE_MOVE_REASON_CANCELLED
} distance_move_reason_t;

typedef struct {
    int64_t left_count;
    int64_t right_count;
    uint32_t sample_ms;
    bool valid;
} distance_move_sample_t;

typedef struct {
    distance_move_phase_t phase;
    distance_move_reason_t reason;
    uint32_t target_counts;
    int64_t start_left;
    int64_t start_right;
    int64_t last_left;
    int64_t last_right;
    uint32_t started_ms;
    uint32_t last_poll_ms;
    uint32_t last_sample_ms;
    uint32_t left_progress_ms;
    uint32_t right_progress_ms;
    bool left_reached;
    bool right_reached;
} distance_move_t;

typedef struct {
    bool left_run;
    bool right_run;
} distance_move_output_t;

/* Caller may reset only at boot or a new explicitly authorized stopped run. */
void distance_move_init(distance_move_t *move);
bool distance_move_target_counts(uint32_t distance_mm, uint32_t *counts);

/* Start requires a stationary baseline and the caller's current safety permit. */
bool distance_move_start(
    distance_move_t *move,
    uint32_t distance_mm,
    const distance_move_sample_t *sample,
    uint32_t now_ms,
    bool motion_permitted
);

/* Call even between new samples so stale/stall/deadline checks still run. */
void distance_move_update(
    distance_move_t *move,
    const distance_move_sample_t *sample,
    uint32_t now_ms,
    bool motion_permitted
);
void distance_move_cancel(distance_move_t *move);
distance_move_output_t distance_move_output(const distance_move_t *move);

#endif
