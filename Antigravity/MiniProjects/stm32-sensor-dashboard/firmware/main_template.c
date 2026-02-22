/**
 * @file main_template.c
 * @brief STM32 Dashboard Firmware Template (Pseudo-code / Skeleton)
 * 
 * This file provides a template for sending sensor data via UART in JSON format
 * to the Python backend dashboard.
 * 
 * Target Baudrate: 115200
 * Transmission Frequency: 1 Hz (1000ms)
 * JSON Format Example:
 * {"sensor_id": "sensor_01", "value": 24.5, "unit": "Celsius", "timestamp": 1708123456}
 */

#include "main.h"
#include <stdio.h>
#include <string.h>

// Assume huart2 is initialized and connected to the PC (ST-Link Virtual COM Port)
extern UART_HandleTypeDef huart2;

// Retarget printf to UART
#ifdef __GNUC__
int __io_putchar(int ch) {
    HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, 0xFFFF);
    return ch;
}
#else
int fputc(int ch, FILE *f) {
    HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, 0xFFFF);
    return ch;
}
#endif

// Global dummy timestamp counter (in real project use RTC or system ticks)
uint32_t current_timestamp = 1708123000;

float read_temperature_sensor(void) {
    // TODO: Implement actual I2C/SPI/ADC sensor reading here
    // For now, return a fake floating point value
    static float temp = 25.0f;
    temp += 0.5f;
    if (temp > 35.0f) temp = 20.0f;
    return temp;
}

int main(void) {
    // HAL MCU Initialization...
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();
    // MX_I2C1_Init(); // Example for sensor

    // Application buffer
    char json_buffer[128];

    while (1) {
        // 1. Read sensor data
        float temp_value = read_temperature_sensor();
        current_timestamp++; // Increment 1 sec

        // 2. Format JSON string exactly matching backend expectations
        // NOTE: Make sure float formatting is enabled in your STM32 linker settings!
        // (usually by adding -u _printf_float in GCC flags)
        snprintf(json_buffer, sizeof(json_buffer), 
                 "{\"sensor_id\": \"stm32_sensor_1\", \"value\": %.2f, \"unit\": \"Celsius\", \"timestamp\": %lu}\r\n",
                 temp_value, 
                 current_timestamp);

        // 3. Transmit UART using printf or HAL_UART_Transmit directly
        printf("%s", json_buffer);

        // 4. Delay for 0.1 second (100 ms)
        HAL_Delay(100);
    }
}
