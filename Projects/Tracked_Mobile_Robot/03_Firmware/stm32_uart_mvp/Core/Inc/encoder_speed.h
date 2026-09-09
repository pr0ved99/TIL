#ifndef ENCODER_SPEED_H
#define ENCODER_SPEED_H

#include <stdbool.h>
#include <stdint.h>

typedef enum{
    ENCODER_COUNTER_WIDTH_16 = 16U,
    ENCODER_COUNTER_WIDTH_32 = 32U
} encoder_counter_width_t;

typedef struct{
    uint32_t previous_raw;
    uint32_t last_sample_ms;
    uint32_t sample_period_ms;

    int64_t accumulated_count;
    int64_t delta_count;
    int64_t counts_per_second;

    encoder_counter_width_t counter_width;
    bool initialized;
} encoder_speed_t;

bool encoder_speed_init(
    encoder_speed_t *state,
    encoder_counter_width_t counter_width,
    uint32_t initial_raw,
    uint32_t now_ms,
    uint32_t sample_period_ms
);

bool encoder_speed_update(
    encoder_speed_t *state,
    uint32_t current_raw,
    uint32_t now_ms
);

bool encoder_speed_cps_to_millirpm(
    int64_t counts_per_second,
    uint32_t counts_per_revolution,
    int32_t *millirpm
);

#endif