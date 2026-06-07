# C01 CAN Loopback Mode

## 목표

외부 CAN transceiver 없이 STM32 bxCAN 내부 loopback으로 CAN 송수신 기본 동작을 확인한다.

## CubeMX 설정

```text
Board: NUCLEO-F446RE
Connectivity -> CAN1 -> Activated
CAN mode -> Loopback
Pins -> PA11 CAN1_RX, PA12 CAN1_TX
NVIC -> CAN RX0 interrupt enable
```

초기 filter는 all-pass로 둔다.

## 구현 흐름

```c
HAL_CAN_Start(&hcan1);
HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
HAL_CAN_AddTxMessage(&hcan1, &tx_header, tx_data, &tx_mailbox);
```

수신 callback에서 `HAL_CAN_GetRxMessage()`로 frame을 읽고 UART 또는 debugger로 확인한다.

## 확인 기준

- 송신한 Standard ID가 수신된다.
- payload 8 byte가 그대로 들어온다.
- Rx callback이 실행된다.
- Tx mailbox가 계속 막히지 않는다.

## 기록할 것

- CAN bitrate 설정값
- prescaler/time segment 값
- 송신 ID와 payload
- 수신 로그
