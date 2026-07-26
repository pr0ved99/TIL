#include "motor_output.h"

#define MOTOR_OUTPUT_DUTY_SCALE_PERMILLE 1000U
#define MOTOR_OUTPUT_MAX_DUTY_PERMILLE   100U
#define MOTOR_OUTPUT_DIR_SETTLE_MS       1U

static TIM_HandleTypeDef *motor_timer = NULL;

static uint16_t motor_left_duty_permille;
static uint16_t motor_right_duty_permille;

static GPIO_PinState motor_left_dir_level = GPIO_PIN_RESET;
static GPIO_PinState motor_right_dir_level = GPIO_PIN_RESET;

static uint32_t motor_output_permille_to_compare(
    uint16_t duty_permille
){
    uint32_t period_counts;

    period_counts =
        __HAL_TIM_GET_AUTORELOAD(motor_timer) + 1U;

    return (
        period_counts * (uint32_t)duty_permille
    ) / MOTOR_OUTPUT_DUTY_SCALE_PERMILLE;
}

void motor_output_stop_all(void){
    if (motor_timer != NULL){
        __HAL_TIM_SET_COMPARE(motor_timer, TIM_CHANNEL_1, 0U);
        __HAL_TIM_SET_COMPARE(motor_timer, TIM_CHANNEL_2, 0U);
    }

    HAL_GPIO_WritePin(
        MOTOR_LEFT_DIR_GPIO_Port,
        MOTOR_LEFT_DIR_Pin,
        GPIO_PIN_RESET
    );
    HAL_GPIO_WritePin(
        MOTOR_RIGHT_DIR_GPIO_Port,
        MOTOR_RIGHT_DIR_Pin,
        GPIO_PIN_RESET
    );

    motor_left_duty_permille = 0U;
    motor_right_duty_permille = 0U;

    motor_left_dir_level = GPIO_PIN_RESET;
    motor_right_dir_level = GPIO_PIN_RESET;
}

HAL_StatusTypeDef motor_output_set_raw(
    uint16_t left_duty_permille,
    GPIO_PinState left_dir_level,
    uint16_t right_duty_permille,
    GPIO_PinState right_dir_level
){
    uint32_t left_compare;
    uint32_t right_compare;
    uint8_t direction_change_while_active;


    if (motor_timer == NULL) {
        return HAL_ERROR;
    }

    if (
        left_duty_permille > MOTOR_OUTPUT_MAX_DUTY_PERMILLE ||
        right_duty_permille > MOTOR_OUTPUT_MAX_DUTY_PERMILLE
    ){
        motor_output_stop_all();
        return HAL_ERROR;
    }

    if (
        (
            left_dir_level != GPIO_PIN_RESET &&
            left_dir_level != GPIO_PIN_SET
        ) ||
        (
            right_dir_level != GPIO_PIN_RESET &&
            right_dir_level != GPIO_PIN_SET
        )
    ){
        motor_output_stop_all();
        return HAL_ERROR;
    }

    left_compare = motor_output_permille_to_compare(left_duty_permille);
    right_compare = motor_output_permille_to_compare(right_duty_permille);

    direction_change_while_active =
    (
        motor_left_duty_permille > 0U &&
        left_dir_level != motor_left_dir_level
    ) ||
    (
        motor_right_duty_permille > 0U &&
        right_dir_level != motor_right_dir_level
    );

    if (direction_change_while_active != 0U){
        __HAL_TIM_SET_COMPARE(
            motor_timer,
            TIM_CHANNEL_1,
            0U
        );
        __HAL_TIM_SET_COMPARE(
            motor_timer,
            TIM_CHANNEL_2,
            0U
        );

        HAL_Delay(MOTOR_OUTPUT_DIR_SETTLE_MS);
    }
    HAL_GPIO_WritePin(
        MOTOR_LEFT_DIR_GPIO_Port,
        MOTOR_LEFT_DIR_Pin,
        left_dir_level
    );
    HAL_GPIO_WritePin(
        MOTOR_RIGHT_DIR_GPIO_Port,
        MOTOR_RIGHT_DIR_Pin,
        right_dir_level
    );

    __HAL_TIM_SET_COMPARE(
        motor_timer,
        TIM_CHANNEL_1,
        left_compare
    );
    __HAL_TIM_SET_COMPARE(
        motor_timer,
        TIM_CHANNEL_2,
        right_compare
    );

    motor_left_duty_permille = left_duty_permille;
    motor_right_duty_permille = right_duty_permille;

    motor_left_dir_level = left_dir_level;
    motor_right_dir_level = right_dir_level;

    return HAL_OK;
}

HAL_StatusTypeDef motor_output_init(TIM_HandleTypeDef *htim){
    HAL_StatusTypeDef status;

    if ((htim == NULL) || (htim->Instance != TIM4)){
        return HAL_ERROR;
    }

    motor_timer = htim;
    motor_output_stop_all();

    status = HAL_TIM_PWM_Start(motor_timer, TIM_CHANNEL_1);
    if (status != HAL_OK){
        motor_output_stop_all();
        motor_timer = NULL;
        return status;
    }

    status = HAL_TIM_PWM_Start(motor_timer, TIM_CHANNEL_2);
    if (status != HAL_OK){
        motor_output_stop_all();
        (void)HAL_TIM_PWM_Stop(motor_timer, TIM_CHANNEL_1);
        motor_timer = NULL;
        return status;
    }

    return HAL_OK;
}
