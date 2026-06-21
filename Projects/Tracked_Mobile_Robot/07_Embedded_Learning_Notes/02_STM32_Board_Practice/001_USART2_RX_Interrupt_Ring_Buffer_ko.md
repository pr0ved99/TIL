# 001 USART2 RX Interrupt and Ring Buffer

## Status

Planned

## Purpose

USART2 수신 interrupt와 ring buffer 구조를 NUCLEO-F446RE에서 확인한다.

이 실습은 PC serial command path의 가장 작은 단위다.

## Hardware

| Item | Value |
| --- | --- |
| Board | NUCLEO-F446RE |
| USART | USART2 |
| TX | PA2 |
| RX | PA3 |
| Baud | 115200 |
| Format | 8N1 |

## Learning Points

- `.ioc` pin mapping이 HAL 초기화 코드로 어떻게 생성되는지 확인한다.
- `RXNE` interrupt와 HAL callback 흐름을 확인한다.
- ISR/callback에서는 byte 저장만 수행한다.
- parser는 main loop 또는 task에서 수행한다.
- overflow count를 관찰한다.

## Minimal Test

1. CubeMX에서 USART2 asynchronous mode를 활성화한다.
2. NVIC에서 USART2 global interrupt를 활성화한다.
3. `HAL_UART_Receive_IT(&huart2, &rx_byte, 1)`로 첫 수신을 건다.
4. callback에서 `rx_byte`를 ring buffer에 넣고 다음 수신을 다시 건다.
5. main loop에서 ring buffer를 읽어 echo 또는 line parser를 수행한다.

## Evidence To Capture

- CubeMX pin screenshot 또는 `.ioc` diff
- serial terminal 송수신 log
- `rx_count`, `parse_count`, `drop_count`
- invalid frame 입력 시 active command가 바뀌지 않는 증거

## Follow-Up

- DMA circular RX와 비교한다.
- UART command/telemetry protocol로 확장한다.
- FreeRTOS `comm_task`로 이동한다.
