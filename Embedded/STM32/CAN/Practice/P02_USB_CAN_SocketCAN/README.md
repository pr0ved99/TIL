# C02 USB-CAN And SocketCAN

## 목표

Ubuntu에서 USB-CAN adapter를 `can0`로 올리고 `candump`, `cansend`를 사용할 수 있게 한다.

## 설치

```bash
sudo apt install -y can-utils
```

## 확인

USB-CAN adapter 연결 후:

```bash
ip link
```

`can0`가 보이면 bitrate를 설정한다.

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000
ip -details link show can0
```

수신 대기:

```bash
candump can0
```

송신:

```bash
cansend can0 110#0100640000002C01
```

## 확인 기준

- `can0` interface가 up 상태다.
- `candump can0`가 실행된다.
- `cansend` 명령이 오류 없이 실행된다.

## 주의

CAN bus에 ACK를 줄 다른 node가 없으면 송신 error가 날 수 있다. normal mode 테스트에서는 STM32 node 또는 다른 CAN node가 bus에 있어야 한다.
