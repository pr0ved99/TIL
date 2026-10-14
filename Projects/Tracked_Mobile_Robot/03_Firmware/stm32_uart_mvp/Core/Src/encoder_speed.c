#include "encoder_speed.h"

#include <stddef.h>

static bool encoder_counter_width_is_valid(
    encoder_counter_width_t counter_width
){
    return (
        counter_width == ENCODER_COUNTER_WIDTH_16 ||
        counter_width == ENCODER_COUNTER_WIDTH_32
    );
}

static uint32_t encoder_normalize_raw(
    encoder_counter_width_t counter_width,
    uint32_t raw_count
){
    if (counter_width == ENCODER_COUNTER_WIDTH_16){
        return raw_count & 0xFFFFU;
    }

    return raw_count;
}

static int64_t encoder_calculate_delta_16(
    uint32_t current_raw,
    uint32_t previous_raw
){
    uint16_t difference;

    difference = (uint16_t)(
        (uint16_t)current_raw -
        (uint16_t)previous_raw
    );

    if (difference <= 0x7FFFU){
        return (int64_t)difference;
    }

    return (int64_t)difference - 65536LL;
}

static int64_t encoder_calculate_delta_32(
    uint32_t current_raw,
    uint32_t previous_raw
){
    uint32_t difference;

    difference = current_raw - previous_raw;

    if (difference <= 0x7FFFFFFFUL){
        return (int64_t)difference;
    }

    return (int64_t)difference - 4294967296LL;
}

static int64_t encoder_calculate_delta(
    encoder_counter_width_t counter_width,
    uint32_t current_raw,
    uint32_t previous_raw
){
    if (counter_width == ENCODER_COUNTER_WIDTH_16){
        return encoder_calculate_delta_16(
            current_raw,
            previous_raw
        );
    }

    if (counter_width == ENCODER_COUNTER_WIDTH_32){
        return encoder_calculate_delta_32(
            current_raw,
            previous_raw
        );
    }

    return 0;
}

bool encoder_speed_init(
    encoder_speed_t *state,
    encoder_counter_width_t counter_width,
    uint32_t initial_raw,
    uint32_t now_ms,
    uint32_t sample_period_ms
){
    if (state == NULL){
        return false;
    }

    state->initialized = false;

    if (
        !encoder_counter_width_is_valid(counter_width) ||
        sample_period_ms == 0U
    ){
        return false;
    }

    state->previous_raw = encoder_normalize_raw(
        counter_width,
        initial_raw
    );
    state->last_sample_ms = now_ms;
    state->sample_period_ms = sample_period_ms;

    state->accumulated_count = 0;
    state->delta_count = 0;
    state->counts_per_second = 0;

    state->counter_width = counter_width;
    state->initialized = true;

    return true;
}

bool encoder_speed_update(
    encoder_speed_t *state,
    uint32_t current_raw,
    uint32_t now_ms
){
    uint32_t normalized_raw;
    uint32_t elapsed_ms;
    int64_t delta_count;

    if (
        state == NULL ||
        !state->initialized ||
        !encoder_counter_width_is_valid(state->counter_width)
    ){
        return false;
    }

    elapsed_ms = now_ms - state->last_sample_ms;

    if (elapsed_ms < state->sample_period_ms){
        return false;
    }

    normalized_raw = encoder_normalize_raw(
        state->counter_width,
        current_raw
    );

    delta_count = encoder_calculate_delta(
        state->counter_width,
        normalized_raw,
        state->previous_raw
    );

    state->previous_raw = normalized_raw;
    state->last_sample_ms = now_ms;

    state->delta_count = delta_count;
    state->accumulated_count += delta_count;
    state->counts_per_second = (
        delta_count * 1000LL
    ) / (int64_t)elapsed_ms;

    return true;
}

bool encoder_speed_cps_to_millirpm(
    int64_t counts_per_second,
    uint32_t counts_per_revolution,
    int32_t *millirpm
){
    int64_t maximum_cps;
    int64_t minimum_cps;

    if (
        millirpm == NULL ||
        counts_per_revolution == 0U
    ){
        return false;
    }

    maximum_cps = (
        (int64_t)INT32_MAX *
        (int64_t)counts_per_revolution
    ) / 60000LL;

    minimum_cps = (
        (int64_t)INT32_MIN *
        (int64_t)counts_per_revolution
    ) / 60000LL;

    if (
        counts_per_second > maximum_cps ||
        counts_per_second < minimum_cps
    ){
        return false;
    }

    *millirpm = (int32_t)(
        (counts_per_second * 60000LL) /
        (int64_t)counts_per_revolution
    );

    return true;
}
