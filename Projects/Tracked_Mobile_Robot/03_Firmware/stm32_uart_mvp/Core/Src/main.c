/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "uart_mvp_protocol.h"
#include "motor_output.h"
#include "encoder_speed.h"
#include <stdio.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* Output-shaft count, calibrated with STM32 quadrature x4 decoding. */
#define ENCODER_COUNTS_PER_OUTPUT_REV       1560U
#define MOTOR_OUTPUT_PIN_TEST_ENABLED       0U
#define MOTOR_FAULT_INJECTION_TEST_ENABLED  0U
#define MOTOR_OUTPUT_PIN_TEST_DUTY_PERMILLE 100U
#define MOTOR_OUTPUT_PIN_TEST_DEBOUNCE_MS   50U
#define ENCODER_SPEED_SAMPLE_PERIOD_MS      100U
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
static uint8_t s_motor_output_test_step;

static GPIO_PinState s_motor_output_test_button_raw = GPIO_PIN_SET;
static GPIO_PinState s_motor_output_test_button_stable = GPIO_PIN_SET;

static uint32_t s_motor_output_test_button_change_ms;

static encoder_speed_t s_encoder_tim3;
static encoder_speed_t s_encoder_tim5;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
static void motor_output_pin_test_process(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
static bool encoder_speed_self_test_case(
  encoder_counter_width_t counter_width,
  uint32_t previous_raw,
  uint32_t current_raw,
  int64_t expected_delta
){
  encoder_speed_t test_state;

  if (!encoder_speed_init(
      &test_state,
      counter_width,
      previous_raw,
      0U,
      100U
  )){
    return false;
  }

  if (!encoder_speed_update(
      &test_state,
      current_raw,
      100U
  )){
    return false;
  }

  return (
    test_state.delta_count == expected_delta &&
    test_state.accumulated_count == expected_delta &&
    test_state.counts_per_second == expected_delta * 10LL
  );
}

static bool encoder_speed_wrap_self_test(void){
  return (
    encoder_speed_self_test_case(
      ENCODER_COUNTER_WIDTH_16,
      65530U,
      5U,
      11LL
    ) &&
    encoder_speed_self_test_case(
      ENCODER_COUNTER_WIDTH_16,
      5U,
      65530U,
      -11LL
    ) &&
    encoder_speed_self_test_case(
      ENCODER_COUNTER_WIDTH_32,
      0xFFFFFFFAUL,
      5U,
      11LL
    ) &&
    encoder_speed_self_test_case(
      ENCODER_COUNTER_WIDTH_32,
      5U,
      0xFFFFFFFAUL,
      -11LL
    )
  );
}

static bool encoder_millirpm_self_test_case(
  int64_t counts_per_second,
  int32_t expected_millirpm
){
  int32_t actual_millirpm;

  if (!encoder_speed_cps_to_millirpm(
    counts_per_second,
    ENCODER_COUNTS_PER_OUTPUT_REV,
    &actual_millirpm
  )){
    return false;
  }

  return actual_millirpm == expected_millirpm;
}

static bool encoder_millirpm_self_test(void){
  int32_t ignored_millirpm;

  return (
    encoder_millirpm_self_test_case(
      0LL,
      0
    ) &&
    encoder_millirpm_self_test_case(
      780LL,
      30000
    ) &&
    encoder_millirpm_self_test_case(
      -780LL,
      -30000
    ) &&
    encoder_millirpm_self_test_case(
      1560LL,
      60000
    ) &&
    encoder_millirpm_self_test_case(
      -1560LL,
      -60000
    ) &&
    !encoder_speed_cps_to_millirpm(
      0LL,
      0U,
      &ignored_millirpm
    ) &&
    !encoder_speed_cps_to_millirpm(
      0LL,
      ENCODER_COUNTS_PER_OUTPUT_REV,
      NULL
    ) &&
    !encoder_speed_cps_to_millirpm(
      INT64_MAX,
      ENCODER_COUNTS_PER_OUTPUT_REV,
      &ignored_millirpm
    ) &&
    !encoder_speed_cps_to_millirpm(
      INT64_MIN,
      ENCODER_COUNTS_PER_OUTPUT_REV,
      &ignored_millirpm
    )
  );
}

static const char *encoder_delta_direction(
  int64_t delta_count
){
  if (delta_count > 0){
    return "POS";
  }

  if (delta_count < 0){
    return "NEG";
  }

  return "STOP";
}

static int32_t encoder_cps_to_i32(int64_t cps){
  if (cps > (int64_t)INT32_MAX){
    return INT32_MAX;
  }

  if (cps < (int64_t)INT32_MIN){
    return INT32_MIN;
  }

  return (int32_t)cps;
}

static void encoder_speed_log_process(void){
  char tx[256];
  uint32_t now_ms;
  uint32_t raw3_count;
  uint32_t raw5_count;
  bool tim3_updated;
  bool tim5_updated;
  int32_t tim3_millirpm;
  int32_t tim5_millirpm;
  int len;

  now_ms = HAL_GetTick();

  raw3_count = __HAL_TIM_GET_COUNTER(&htim3);
  raw5_count = __HAL_TIM_GET_COUNTER(&htim5);

  tim3_updated = encoder_speed_update(
    &s_encoder_tim3,
    raw3_count,
    now_ms
  );

  tim5_updated = encoder_speed_update(
    &s_encoder_tim5,
    raw5_count,
    now_ms
  );

  if (!tim3_updated || !tim5_updated){
      return;
  }

  if (
    !encoder_speed_cps_to_millirpm(
      s_encoder_tim3.counts_per_second,
      ENCODER_COUNTS_PER_OUTPUT_REV,
      &tim3_millirpm
    ) ||
    !encoder_speed_cps_to_millirpm(
      s_encoder_tim5.counts_per_second,
      ENCODER_COUNTS_PER_OUTPUT_REV,
      &tim5_millirpm
    )
  ){
    Error_Handler();
  }

  /* Confirmed vehicle-frame mapping: forward motion is positive.
   * Motor B/left uses TIM3 and requires sign inversion.
   * Motor A/right uses TIM5 and keeps its raw sign.
  */
  uart_mvp_set_encoder_cps(
    encoder_cps_to_i32(-s_encoder_tim3.counts_per_second),
    encoder_cps_to_i32(s_encoder_tim5.counts_per_second)
  );

  len = snprintf(
    tx,
    sizeof(tx),
    "ENC3,raw=%lu,delta=%ld,total=%ld,cps=%ld,mrpm=%ld,dir=%s;"
    "ENC5,raw=%lu,delta=%ld,total=%ld,cps=%ld,mrpm=%ld,dir=%s\r\n",
    (unsigned long)raw3_count,
    (long)s_encoder_tim3.delta_count,
    (long)s_encoder_tim3.accumulated_count,
    (long)s_encoder_tim3.counts_per_second,
    (long)tim3_millirpm,
    encoder_delta_direction(s_encoder_tim3.delta_count),
    (unsigned long)raw5_count,
    (long)s_encoder_tim5.delta_count,
    (long)s_encoder_tim5.accumulated_count,
    (long)s_encoder_tim5.counts_per_second,
    (long)tim5_millirpm,
    encoder_delta_direction(s_encoder_tim5.delta_count)
  );

  if ((len > 0) && (len < (int)sizeof(tx))){
    (void)HAL_UART_Transmit(
      &huart2,
      (uint8_t *)tx,
      (uint16_t)len,
      50U
    );
  }
}
static void motor_output_pin_test_process(void){
    GPIO_PinState button_now;
    uint32_t now_ms;
    HAL_StatusTypeDef status = HAL_OK;

    if (MOTOR_OUTPUT_PIN_TEST_ENABLED == 0U){
        return;
    }

    button_now = HAL_GPIO_ReadPin(B1_GPIO_Port, B1_Pin);
    now_ms = HAL_GetTick();

    if (button_now != s_motor_output_test_button_raw){
        s_motor_output_test_button_raw = button_now;
        s_motor_output_test_button_change_ms = now_ms;
        return;
    }

    if (button_now == s_motor_output_test_button_stable){
        return;
    }

    if (
        (now_ms - s_motor_output_test_button_change_ms) <
        MOTOR_OUTPUT_PIN_TEST_DEBOUNCE_MS
    ){
        return;
    }

    s_motor_output_test_button_stable = button_now;

    if (button_now != GPIO_PIN_RESET){
        return;
    }

    s_motor_output_test_step++;

    switch (s_motor_output_test_step){
        case 1U:
            status = motor_output_set_raw(
                MOTOR_OUTPUT_PIN_TEST_DUTY_PERMILLE,
                GPIO_PIN_RESET,
                (MOTOR_FAULT_INJECTION_TEST_ENABLED != 0U)
                ? MOTOR_OUTPUT_PIN_TEST_DUTY_PERMILLE
                : 0U,
                GPIO_PIN_RESET
            );
            HAL_GPIO_WritePin(
                LD2_GPIO_Port,
                LD2_Pin,
                GPIO_PIN_SET
            );
            break;

        case 2U:
            if (MOTOR_FAULT_INJECTION_TEST_ENABLED != 0U){
              Error_Handler();
            }
            status = motor_output_set_raw(
                MOTOR_OUTPUT_PIN_TEST_DUTY_PERMILLE,
                GPIO_PIN_SET,
                0U,
                GPIO_PIN_RESET
            );
            break;

        case 3U:
            motor_output_stop_all();
            HAL_GPIO_WritePin(
                LD2_GPIO_Port,
                LD2_Pin,
                GPIO_PIN_RESET
            );
            break;

        case 4U:
            status = motor_output_set_raw(
                0U,
                GPIO_PIN_RESET,
                MOTOR_OUTPUT_PIN_TEST_DUTY_PERMILLE,
                GPIO_PIN_RESET
            );
            HAL_GPIO_WritePin(
                LD2_GPIO_Port,
                LD2_Pin,
                GPIO_PIN_SET
            );
            break;

        case 5U:
            status = motor_output_set_raw(
                0U,
                GPIO_PIN_RESET,
                MOTOR_OUTPUT_PIN_TEST_DUTY_PERMILLE,
                GPIO_PIN_SET
            );
            break;

        case 6U:
        default:
            motor_output_stop_all();
            HAL_GPIO_WritePin(
                LD2_GPIO_Port,
                LD2_Pin,
                GPIO_PIN_RESET
            );
            s_motor_output_test_step = 0U;
            break;
    }

    if (status != HAL_OK){
        Error_Handler();
    }
}
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */
  uint32_t encoder_init_ms;
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  MX_USART1_UART_Init();
  MX_TIM4_Init();
  MX_TIM3_Init();
  MX_TIM5_Init();
  /* USER CODE BEGIN 2 */
  if (motor_output_init(&htim4) != HAL_OK){
    Error_Handler();
  }

  __HAL_TIM_SET_COUNTER(&htim3, 32768U);
  __HAL_TIM_SET_COUNTER(&htim5, 0x80000000U);

  if (HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL) != HAL_OK){
    Error_Handler();
  }

  if (HAL_TIM_Encoder_Start(&htim5, TIM_CHANNEL_ALL) != HAL_OK){
    Error_Handler();
  }

  encoder_init_ms = HAL_GetTick();

  if (!encoder_speed_init(
      &s_encoder_tim3,
      ENCODER_COUNTER_WIDTH_16,
      __HAL_TIM_GET_COUNTER(&htim3),
      encoder_init_ms,
      ENCODER_SPEED_SAMPLE_PERIOD_MS
  )){
    Error_Handler();
  }

  if (!encoder_speed_init(
      &s_encoder_tim5,
      ENCODER_COUNTER_WIDTH_32,
      __HAL_TIM_GET_COUNTER(&htim5),
      encoder_init_ms,
      ENCODER_SPEED_SAMPLE_PERIOD_MS
  )){
    Error_Handler();
  }

  if (
    encoder_speed_wrap_self_test() &&
    encoder_millirpm_self_test()
  ){
    static uint8_t pass_message[] =
      "ENC_SELF_TEST,wrap=PASS,millirpm=PASS\r\n";

    (void)HAL_UART_Transmit(
      &huart2,
      pass_message,
      (uint16_t)(sizeof(pass_message) - 1U),
      50U
    );
  } else {
    static uint8_t fail_message[] =
      "ENC_SELF_TEST,wrap_or_millirpm=FAIL\r\n";

    (void)HAL_UART_Transmit(
      &huart2,
      fail_message,
      (uint16_t)(sizeof(fail_message) - 1U),
      50U
    );

    Error_Handler();
  }
  uart_mvp_init(&huart1);
  uart_mvp_start_rx();
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    encoder_speed_log_process();
    motor_output_pin_test_process();
    uart_mvp_process();
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE3);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 16;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 2;
  RCC_OscInitStruct.PLL.PLLR = 2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
  uart_mvp_on_rx_complete(huart);
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart){
  uart_mvp_on_uart_error(huart);
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  motor_output_stop_all();
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
