# STM32 CAN Practice

CAN A-to-Z 학습 문서와 연결되는 실습 경로다.

## 실습 목록

| 태그 | 경로 | 주제 |
| --- | --- | --- |
| `[C00]` | [`P00_Board_Pin_Transceiver_Check`](./P00_Board_Pin_Transceiver_Check/README.md) | 보드, 핀, transceiver 확인 |
| `[C01]` | [`P01_CAN_Loopback_Mode`](./P01_CAN_Loopback_Mode/README.md) | CAN loopback |
| `[C02]` | [`P02_USB_CAN_SocketCAN`](./P02_USB_CAN_SocketCAN/README.md) | USB-CAN과 SocketCAN |
| `[C03]` | [`P03_CAN_Normal_Mode`](./P03_CAN_Normal_Mode/README.md) | normal mode 송수신 |
| `[C04]` | [`P04_CAN_ID_Filter_Design`](./P04_CAN_ID_Filter_Design/README.md) | ID map과 filter |
| `[C05]` | [`P05_CAN_Error_BusOff_Debug`](./P05_CAN_Error_BusOff_Debug/README.md) | error와 bus-off |
| `[C06]` | [`P06_CAN_Robot_Command_Telemetry`](./P06_CAN_Robot_Command_Telemetry/README.md) | robot protocol |

## 권장 STM32CubeIDE workspace

```text
/home/proved/my_ws/github/pr0ved99/TIL/Embedded/STM32/STM32_ws
```

실습 프로젝트 후보:

```text
F446RE_CAN_Loopback
F446RE_CAN_Normal_Mode
F446RE_CAN_Robot_Protocol
```
