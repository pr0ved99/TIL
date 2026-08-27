#ifndef DRIVE_COMMAND_MAPPER_H
#define DRIVE_COMMAND_MAPPER_H

#include <stdbool.h>
#include <stdint.h>

typedef struct{
    int16_t left_signed_permille;
    int16_t right_signed_permille;
} drive_command_request_t;

bool drive_command_map(
    int32_t vx_mmps,
    int32_t w_mradps,
    uint16_t duty_cap_permille,
    drive_command_request_t *request
);

#endif