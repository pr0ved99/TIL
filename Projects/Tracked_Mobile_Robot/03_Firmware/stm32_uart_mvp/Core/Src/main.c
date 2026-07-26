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
#include <stdio.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define MOTOR_OUTPUT_PIN_TEST_ENABLED       0U
#define MOTOR_OUTPUT_PIN_TEST_DUTY_PERMILLE 100U
#define MOTOR_OUTPUT_PIN_TEST_DEBOUNCE_MS   50U
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
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
static void Board_Hardware_Init(void);
static void motor_output_pin_test_process(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
static void encoder_hand_test_log_process(void){
  static uint32_t last_log_ms;
  char tx[80];
  uint32_t now_ms;
  uint16_t raw_count;
  int32_t centered_count;
  int len;

  now_ms = HAL_GetTick();

  if ((now_ms - last_log_ms) < 250U){
    return;
  }

  last_log_ms = now_ms;
  raw_count = (uint16_t)__HAL_TIM_GET_COUNTER(&htim3);
  centered_count = (int32_t)raw_count - 32768L;

  len = snprintf(
    tx,
    sizeof(tx),
    "ENC3,raw=%u,count=%ld,dir=%s\r\n",
    (unsigned int)raw_count,
    (long)centered_count,
    __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim3) ? "DOWN" : "UP"
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
                0U,
                GPIO_PIN_RESET
            );
            HAL_GPIO_WritePin(
                LD2_GPIO_Port,
                LD2_Pin,
                GPIO_PIN_SET
            );
            break;

        case 2U:
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
  /* USER CODE BEGIN 2 */
  if (motor_output_init(&htim4) != HAL_OK){
    Error_Handler();
  }

  __HAL_TIM_SET_COUNTER(&htim3, 32768U);

  if (HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL) != HAL_OK){
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
    encoder_hand_test_log_process();
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
static void Board_Hardware_Init(void)
{
  MX_GPIO_Init();
  MX_USART2_UART_Init();
}

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
