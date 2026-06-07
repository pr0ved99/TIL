# C05 CAN Error And Bus-off Debug

## 목표

CAN normal mode에서 흔히 발생하는 물리 계층과 protocol 오류를 분리한다.

## 대표 증상

- `cansend`가 실패한다.
- `candump`에 아무것도 안 보인다.
- STM32 Tx mailbox가 비지 않는다.
- Rx callback이 호출되지 않는다.
- CAN error counter가 증가한다.
- bus-off 상태에 들어간다.

## 점검 순서

1. CANH/CANL이 뒤집히지 않았는가
2. GND를 공유했는가
3. transceiver 전원이 맞는가
4. STM32 PA11/PA12 alternate function이 CAN1인가
5. PC와 STM32 bitrate가 같은가
6. 종단저항이 bus 양 끝에 있는가
7. ACK를 줄 다른 CAN node가 있는가
8. filter가 너무 좁지 않은가

## PC 상태 확인

```bash
ip -details link show can0
```

필요하면 can0를 재시작한다.

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000 restart-ms 100
```

## 완료 기준

- ACK error와 wiring error를 구분할 수 있다.
- bitrate mismatch를 의도적으로 만들고 증상을 확인했다.
- bus-off 이후 recovery 방법을 기록했다.
