#ifndef UART_MVP_PROTOCOL_H
#define UART_MVP_PROTOCOL_H

#include "main.h"

void uart_mvp_init(UART_HandleTypeDef *huart);
void uart_mvp_start_rx(void);
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart);
void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);
void uart_mvp_set_encoder_cps(
    int32_t left_cps,
    int32_t right_cps
);
void uart_mvp_process(void);

#endif // UART_MVP_PROTOCOL_H