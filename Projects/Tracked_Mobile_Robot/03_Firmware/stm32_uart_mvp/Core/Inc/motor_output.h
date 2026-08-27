#ifndef MOTOR_OUTPUT_H
#define MOTOR_OUTPUT_H

#include "main.h"

HAL_StatusTypeDef motor_output_init(TIM_HandleTypeDef *htim);
HAL_StatusTypeDef motor_output_set_raw(
    uint16_t left_duty_permille,
    GPIO_PinState left_dir_level,
    uint16_t right_duty_permille,
    GPIO_PinState right_dir_level
);

HAL_StatusTypeDef motor_output_set_signed(
    int16_t left_signed_permille,
    int16_t right_signed_permille
);

void motor_output_stop_all(void);

#endif // MOTOR_OUTPUT_H