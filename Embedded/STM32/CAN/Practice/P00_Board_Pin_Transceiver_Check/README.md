# C00 Board, Pin, Transceiver Check

## 목표

NUCLEO-F446RE에서 CAN 실습 전에 필요한 하드웨어 전제를 확인한다.

## 확인 항목

- Board: NUCLEO-F446RE
- MCU: STM32F446RE
- CAN controller: bxCAN
- CAN1 RX 후보: PA11
- CAN1 TX 후보: PA12
- 외부 CAN transceiver 필요
- CANH/CANL 종단저항 필요
- USB-CAN adapter 필요 또는 두 번째 CAN node 필요

## 배선 기준

```text
PA12 / CAN1_TX -> transceiver TXD
PA11 / CAN1_RX <- transceiver RXD
GND            <-> transceiver GND
CANH           <-> CANH bus
CANL           <-> CANL bus
```

## 완료 기준

- 사용할 transceiver 모듈의 전원 전압과 logic-level compatibility를 확인했다.
- CANH/CANL을 STM32 pin에 직접 연결하지 않는다는 점을 확인했다.
- 120 ohm 종단저항 위치를 정했다.
- USB-CAN adapter 또는 두 번째 CAN node를 준비했다.
