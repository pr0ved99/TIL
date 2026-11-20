#ifndef UART_MVP_PROTOCOL_H
#define UART_MVP_PROTOCOL_H

#include "main.h"
#include <stdbool.h>
#include <stdint.h>

void uart_mvp_init(UART_HandleTypeDef *huart);
void uart_mvp_start_rx(void);
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart);
void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);
void uart_mvp_on_tx_complete(UART_HandleTypeDef *huart);
void uart_mvp_set_encoder_sample(
    int32_t left_cps,
    int32_t right_cps,
    int64_t left_count,
    int64_t right_count,
    uint32_t sample_ms,
    bool valid
);
void uart_mvp_process(void);

#endif // UART_MVP_PROTOCOL_H