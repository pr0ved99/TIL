# C03 CAN Normal Mode

## 목표

STM32 CAN1 normal mode와 USB-CAN adapter 사이에서 실제 CAN frame을 송수신한다.

## 하드웨어 구성

```text
NUCLEO-F446RE PA12 -> transceiver TXD
NUCLEO-F446RE PA11 <- transceiver RXD
NUCLEO-F446RE GND  <-> transceiver GND
transceiver CANH   <-> USB-CAN CANH
transceiver CANL   <-> USB-CAN CANL
```

종단저항:

```text
bus 양 끝 120 ohm
```

## STM32 설정

```text
CAN1 mode -> Normal
Standard ID
Bitrate -> 500 kbit/s
RX0 interrupt enable
Filter -> all-pass initially
```

## PC 확인

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000
candump can0
```

## STM32 -> PC 확인

STM32에서 주기적으로 `0x200` frame을 보낸다.

PC에서:

```bash
candump can0
```

## PC -> STM32 확인

```bash
cansend can0 110#6400000001000000
```

STM32 수신 callback에서 ID `0x110`과 data를 확인한다.

## 완료 기준

- PC에서 STM32 송신 frame이 보인다.
- STM32에서 PC 송신 frame을 받는다.
- bitrate를 바꾸면 통신이 깨진다는 것을 확인한다.
