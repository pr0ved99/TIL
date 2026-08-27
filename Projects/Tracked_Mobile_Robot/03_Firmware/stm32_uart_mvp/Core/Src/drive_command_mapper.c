#include "drive_command_mapper.h"

#include <stddef.h>

#define DRIVE_COMMAND_NORMALIZED_SCALE  1000
#define DRIVE_COMMAND_VX_MIN_MMPS   -100
#define DRIVE_COMMAND_VX_MAX_MMPS    100
#define DRIVE_COMMAND_W_MIN_MRADPS  -500
#define DRIVE_COMMAND_W_MAX_MRADPS   500
#define DRIVE_COMMAND_MAX_DUTY_PERMILLE 100U

bool drive_command_map(
    int32_t vx_mmps,
    int32_t w_mradps,
    uint16_t duty_cap_permille,
    drive_command_request_t *request
){
    int32_t linear;
    int32_t yaw;
    int32_t raw_left;
    int32_t raw_right;
    int32_t left_abs;
    int32_t right_abs;
    int32_t peak;

    if(request == NULL){
        return false;
    }

    request->left_signed_permille = 0;
    request->right_signed_permille = 0;

    if(
        vx_mmps < DRIVE_COMMAND_VX_MIN_MMPS ||
        vx_mmps > DRIVE_COMMAND_VX_MAX_MMPS ||
        w_mradps < DRIVE_COMMAND_W_MIN_MRADPS ||
        w_mradps > DRIVE_COMMAND_W_MAX_MRADPS ||
        duty_cap_permille > DRIVE_COMMAND_MAX_DUTY_PERMILLE
    ){
        return false;
    }

    linear =
        (vx_mmps * DRIVE_COMMAND_NORMALIZED_SCALE) /
        DRIVE_COMMAND_VX_MAX_MMPS;

    yaw =
        (w_mradps * DRIVE_COMMAND_NORMALIZED_SCALE) /
        DRIVE_COMMAND_W_MAX_MRADPS;

    raw_left = linear - yaw;
    raw_right = linear + yaw;

    left_abs = (raw_left < 0) ? -raw_left : raw_left;
    right_abs = (raw_right < 0) ? -raw_right : raw_right;

    peak = DRIVE_COMMAND_NORMALIZED_SCALE;

    if(left_abs > peak){
        peak = left_abs;
    }

    if(right_abs > peak){
        peak = right_abs;
    }

    request->left_signed_permille = (int16_t)(
        (raw_left * (int32_t)duty_cap_permille) / peak
    );

    request->right_signed_permille = (int16_t)(
        (raw_right * (int32_t)duty_cap_permille) / peak
    );

    return true;
}
