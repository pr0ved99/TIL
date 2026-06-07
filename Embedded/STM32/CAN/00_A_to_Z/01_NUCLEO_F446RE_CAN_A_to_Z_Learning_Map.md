# NUCLEO-F446RE CAN A-to-Z Learning Map

## 목적

이 문서는 NUCLEO-F446RE에서 CAN 통신을 학습하고, tracked mobile robot의 command/telemetry bus로 확장하기 위한 A-to-Z 학습 지도다.

목표 흐름:

```text
CAN 개념
-> NUCLEO-F446RE bxCAN 이해
-> transceiver wiring
-> loopback 검증
-> USB-CAN / SocketCAN 검증
-> normal mode 통신
-> filter / ID map 설계
-> error / bus-off 디버깅
-> robot command / telemetry 통합
```

## 기준 보드와 핵심 주의점

- Board: `NUCLEO-F446RE`
- MCU: `STM32F446RE`
- CAN peripheral: `bxCAN`
- 첫 구현 API: `HAL_CAN`
- NUCLEO-F446RE 보드에는 CAN transceiver가 기본 탑재되어 있지 않다.
- STM32의 CAN TX/RX 핀을 CANH/CANL에 직접 연결하면 안 된다.
- 실제 CAN bus에는 외부 CAN transceiver와 종단저항 구성이 필요하다.

## 실습 태그 인덱스

본문의 `[Cxx]` 태그는 아래 실습 문서로 연결된다.

| 태그 | 실습 경로 | 목적 |
| --- | --- | --- |
| `[C00]` | [`Practice/P00_Board_Pin_Transceiver_Check`](../Practice/P00_Board_Pin_Transceiver_Check/README.md) | 보드, 핀, transceiver, wiring 전제 확인 |
| `[C01]` | [`Practice/P01_CAN_Loopback_Mode`](../Practice/P01_CAN_Loopback_Mode/README.md) | 외부 배선 없이 bxCAN 송수신 기본 확인 |
| `[C02]` | [`Practice/P02_USB_CAN_SocketCAN`](../Practice/P02_USB_CAN_SocketCAN/README.md) | Ubuntu에서 USB-CAN adapter와 SocketCAN 확인 |
| `[C03]` | [`Practice/P03_CAN_Normal_Mode`](../Practice/P03_CAN_Normal_Mode/README.md) | STM32와 외부 CAN node 사이 normal mode 통신 |
| `[C04]` | [`Practice/P04_CAN_ID_Filter_Design`](../Practice/P04_CAN_ID_Filter_Design/README.md) | 11-bit CAN ID map과 filter 설계 |
| `[C05]` | [`Practice/P05_CAN_Error_BusOff_Debug`](../Practice/P05_CAN_Error_BusOff_Debug/README.md) | ACK error, wiring fault, bus-off 분리 |
| `[C06]` | [`Practice/P06_CAN_Robot_Command_Telemetry`](../Practice/P06_CAN_Robot_Command_Telemetry/README.md) | robot command/telemetry frame 설계 |

## 전체 학습 순서

```text
0. CAN을 왜 쓰는지 이해
1. 물리 계층과 transceiver 이해
2. STM32F446RE bxCAN 구조 이해
3. CAN frame 구조 이해
4. CubeMX/HAL CAN 설정
5. Loopback mode 검증
6. USB-CAN/SocketCAN으로 bus 관찰
7. Normal mode 송수신
8. Filter와 ID map 설계
9. Error state와 bus-off 디버깅
10. Robot command/telemetry protocol 설계
11. FreeRTOS queue 기반 CAN task로 확장
```

## 0. CAN을 왜 쓰는가

### 0.1 UART와 CAN의 차이

UART는 첫 motor bring-up에 좋다. 배선이 단순하고 PC에서 로그를 보기 쉽다.

CAN은 로봇 내부 장치가 늘어나는 시점에 가치가 커진다.

| 항목 | UART | CAN |
| --- | --- | --- |
| 배선 | TX/RX point-to-point | CANH/CANL multi-drop bus |
| 노드 수 | 기본적으로 1:1 | 여러 node가 같은 bus 공유 |
| 전기적 특성 | single-ended | differential signaling |
| 우선순위 | 별도 설계 필요 | CAN ID arbitration |
| 오류 검출 | protocol 설계에 의존 | hardware-level error detection |
| 용도 | bring-up, log, 단순 command | 모터/센서/제어기 간 견고한 message bus |

### 0.2 이 프로젝트에서 CAN의 역할

CAN은 motor control owner가 아니다. CAN은 command transport다.

STM32가 계속 소유해야 하는 것:

- PWM output
- BTS7960 enable
- encoder counting
- battery voltage safety
- command timeout
- emergency stop
- final motor output gating

CAN이 담당하는 것:

- 상위 제어기에서 STM32로 command 전달
- STM32에서 상위 제어기로 telemetry 전달
- heartbeat와 fault report
- 향후 sensor/motor module 확장

## 1. CAN 물리 계층

### 1.1 CAN controller와 transceiver

NUCLEO-F446RE의 STM32F446RE 내부에는 CAN controller가 있다. 하지만 CANH/CANL 전기 신호를 직접 만들지는 않는다.

필수 구분:

| 구성 | 역할 |
| --- | --- |
| bxCAN controller | STM32 내부 peripheral. CAN frame 송수신, mailbox, filter, error 처리 |
| CAN transceiver | STM32 logic level TX/RX와 CANH/CANL differential bus 사이 변환 |
| CANH/CANL bus | 실제 통신선 |

### 1.2 NUCLEO-F446RE 배선 후보

프로젝트 기준 CAN1 후보:

| Signal | STM32 pin | Function |
| --- | --- | --- |
| CAN RX | `PA11` | `CAN1_RX` |
| CAN TX | `PA12` | `CAN1_TX` |

기본 배선:

```text
STM32 PA12 / CAN1_TX -> Transceiver TXD
STM32 PA11 / CAN1_RX <- Transceiver RXD
STM32 GND            <-> Transceiver GND
Transceiver CANH     <-> CANH bus
Transceiver CANL     <-> CANL bus
```

연결 실습: `[C00]`

### 1.3 Transceiver 선택 기준

초기에는 3.3 V logic compatible CAN transceiver module을 우선 고려한다.

주의:

- 모든 5 V CAN module이 STM32 3.3 V logic에 안전하다고 가정하지 않는다.
- MCP2515 module은 CAN controller가 포함된 SPI 모듈이다. STM32F446RE에는 bxCAN controller가 있으므로 필수는 아니다.
- SN65HVD230 계열처럼 3.3 V logic과 함께 쓰기 쉬운 transceiver를 먼저 검토한다.

### 1.4 Termination

CAN bus 양 끝에는 보통 120 ohm 종단저항을 둔다.

2-node bench setup:

```text
[USB-CAN] --- CANH/CANL --- [STM32 transceiver]
   120R                      120R
```

짧은 bench wire에서는 우연히 동작할 수 있지만, 종단 없이 통신이 된다고 해서 물리 계층이 검증된 것은 아니다.

## 2. CAN Frame 기본

### 2.1 Classical CAN

STM32F446RE bxCAN은 Classical CAN을 사용한다.

첫 프로젝트에서는 Standard ID를 사용한다.

| 항목 | 기준 |
| --- | --- |
| Identifier | Standard 11-bit ID |
| Data length | 0-8 bytes |
| Bitrate | 초기 500 kbit/s, 불안정하면 250 kbit/s |
| Frame type | Data frame 우선 |
| Remote frame | 초기에는 사용하지 않음 |

### 2.2 CAN ID

CAN ID는 message 종류이면서 bus arbitration priority다. 숫자가 낮은 ID가 더 높은 우선순위를 가진다.

프로젝트 규칙:

- emergency와 heartbeat는 routine telemetry보다 낮은 ID를 준다.
- command와 telemetry ID 범위를 분리한다.
- ID 하나에 의미 하나를 부여한다.
- sensor stream처럼 큰 데이터는 Classical CAN에 싣지 않는다.

### 2.3 DLC와 byte packing

Classical CAN payload는 최대 8 byte다.

규칙:

- multi-byte integer는 little-endian으로 통일한다.
- float를 바로 보내기보다 scale된 integer를 우선 사용한다.
- signed value의 scale을 명확히 적는다.
- frame마다 sequence 또는 counter를 넣을지 검토한다.

예:

```text
vx_mmps   : int16_t
w_mradps : int16_t
flags     : uint8_t
seq       : uint8_t
```

## 3. STM32 bxCAN 구조

### 3.1 핵심 구성

bxCAN에서 먼저 알아야 할 구성:

| 구성 | 의미 |
| --- | --- |
| Tx mailbox | 송신 대기 공간 |
| Rx FIFO0/FIFO1 | 수신 frame이 쌓이는 FIFO |
| Filter bank | 수신할 ID를 거르는 hardware filter |
| Error counters | transmit/receive error 누적 상태 |
| Loopback mode | 외부 bus 없이 내부 송수신 테스트 |
| Silent mode | bus를 방해하지 않고 수신 관찰 |
| Normal mode | 실제 bus 송수신 |

### 3.2 Interrupt 기반 수신

CAN 수신은 polling보다 interrupt 기반으로 시작하는 것이 좋다.

기본 흐름:

```text
CAN RX interrupt
-> HAL_CAN_RxFifo0MsgPendingCallback()
-> HAL_CAN_GetRxMessage()
-> frame copy
-> parser 또는 queue로 전달
```

RTOS 통합 전에는 callback 안에서 간단한 flag만 세우고 main loop에서 처리해도 된다.

RTOS 통합 후에는 callback에서 `xQueueSendFromISR()`로 넘긴다.

## 4. CubeMX/HAL 설정 순서

### 4.1 CAN1 활성화

CubeMX에서:

```text
Connectivity -> CAN1 -> Activated
Mode -> Loopback 또는 Normal
Pins -> PA11(CAN1_RX), PA12(CAN1_TX)
```

초기 검증:

1. Loopback mode
2. Normal mode

연결 실습: `[C01]`, `[C03]`

### 4.2 Bit timing

처음 목표 bitrate는 500 kbit/s로 둔다.

중요한 것은 양쪽 노드의 bitrate가 같아야 한다는 점이다.

불안정할 때 확인:

- APB1 CAN clock
- Prescaler
- Time segment 1
- Time segment 2
- Sync jump width
- USB-CAN adapter bitrate
- physical wiring

### 4.3 HAL 초기 코드

필수 호출 흐름:

```c
HAL_CAN_Start(&hcan1);
HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
```

송신:

```c
HAL_CAN_AddTxMessage(&hcan1, &tx_header, tx_data, &tx_mailbox);
```

수신 callback:

```c
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan)
{
    CAN_RxHeaderTypeDef rx_header;
    uint8_t rx_data[8];

    if (hcan->Instance == CAN1) {
        HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &rx_header, rx_data);
    }
}
```

## 5. Loopback 검증

Loopback은 외부 transceiver나 CANH/CANL 없이 CAN peripheral 내부 송수신을 확인하는 단계다.

이 단계에서 검증하는 것:

- CAN peripheral clock
- HAL CAN init
- Tx mailbox 사용
- Rx callback
- frame header와 data packing
- filter 설정이 너무 좁지 않은지

연결 실습: `[C01]`

완료 기준:

- 송신한 ID와 data가 같은 보드에서 수신된다.
- UART log 또는 debugger로 수신 frame을 확인한다.
- filter를 all-pass로 둔 상태에서 수신된다.

## 6. USB-CAN과 SocketCAN

Ubuntu에서 CAN을 다루려면 SocketCAN-compatible USB-CAN adapter가 가장 편하다.

대표 명령:

```bash
ip link
sudo ip link set can0 up type can bitrate 500000
candump can0
cansend can0 110#6400000001000000
```

필요 도구:

```bash
sudo apt install -y can-utils
```

연결 실습: `[C02]`

## 7. Normal Mode 송수신

Normal mode에서는 실제 bus ACK가 필요하다. 혼자 있는 CAN node가 계속 송신하면 ACK를 받지 못해 error가 쌓일 수 있다.

최소 정상 구성:

```text
STM32 + transceiver <-> USB-CAN adapter
```

확인 순서:

1. USB-CAN adapter가 `can0`로 보이는지 확인
2. `can0` bitrate 설정
3. STM32 CAN1 normal mode 설정
4. STM32에서 주기 frame 송신
5. PC에서 `candump can0`
6. PC에서 `cansend`로 STM32 수신 확인

연결 실습: `[C03]`

## 8. Filter와 ID Map

### 8.1 처음에는 all-pass

초기 bring-up에서는 filter를 너무 좁게 잡지 않는다. 통신 자체가 되는지 먼저 확인한다.

그 다음 ID별 filter로 좁힌다.

연결 실습: `[C04]`

### 8.2 프로젝트 ID map 초안

Command:

| CAN ID | Name | Direction | Period |
| --- | --- | --- | --- |
| `0x100` | `HEARTBEAT` | Controller -> STM32 | 10-20 Hz |
| `0x110` | `MOTION_CMD` | Controller -> STM32 | 10-50 Hz |
| `0x120` | `ARM_CMD` | Controller -> STM32 | Event |
| `0x130` | `ESTOP_CMD` | Controller -> STM32 | Event |

Telemetry:

| CAN ID | Name | Direction | Period |
| --- | --- | --- | --- |
| `0x200` | `STATUS` | STM32 -> Controller | 10 Hz |
| `0x210` | `MOTOR_TELEM` | STM32 -> Controller | 10-50 Hz |
| `0x220` | `ENCODER_COUNT` | STM32 -> Controller | 10 Hz |
| `0x2F0` | `FAULT_EVENT` | STM32 -> Controller | Event |

## 9. Error와 Bus-off 디버깅

CAN은 물리 계층 문제가 software bug처럼 보이기 쉽다.

먼저 볼 것:

- CANH/CANL 뒤바뀜
- GND 공유 안 됨
- bitrate 불일치
- termination 없음
- transceiver 전원 불일치
- STM32 pin alternate function 설정 오류
- USB-CAN adapter가 down 상태
- ACK를 줄 두 번째 node가 없음

연결 실습: `[C05]`

## 10. Robot Command/Telemetry 설계

### 10.1 Motion command

예시 payload:

```text
ID: 0x110 MOTION_CMD
DLC: 8
byte 0-1: vx_mmps, int16 little-endian
byte 2-3: wz_mradps, int16 little-endian
byte 4: enable_flags
byte 5: sequence
byte 6-7: timeout_ms, uint16 little-endian
```

### 10.2 Status telemetry

예시 payload:

```text
ID: 0x200 STATUS
DLC: 8
byte 0: firmware_state
byte 1: fault_flags_low
byte 2: fault_flags_high
byte 3: command_age_10ms
byte 4-5: battery_mv, uint16 little-endian
byte 6: heartbeat_counter
byte 7: reserved
```

### 10.3 안전 규칙

- CAN RX callback은 PWM을 직접 쓰지 않는다.
- valid command는 내부 command queue로만 전달한다.
- heartbeat timeout이면 safe stop이다.
- ESTOP frame은 local safety state를 latch할 수 있다.
- fault report는 안전 동작을 대체하지 않는다.

연결 실습: `[C06]`

## 11. FreeRTOS 통합 방향

CAN 단독 송수신이 안정된 뒤 FreeRTOS에 붙인다.

권장 구조:

```text
CAN RX ISR
-> can_rx_queue
-> can_parser_task
-> command_queue / state update
-> motor_control_task

telemetry_task
-> can_tx_queue
-> can_tx_task
-> CAN Tx mailbox
```

RTOS 연결 실습은 RTOS 문서의 `[R06]`에서 다룬다.

## 마일스톤

| Milestone | 목표 | 완료 기준 |
| --- | --- | --- |
| C0 | 보드/핀/부품 확인 | PA11/PA12, transceiver, termination 계획 존재 |
| C1 | Loopback | 외부 배선 없이 송신 frame을 수신 |
| C2 | SocketCAN | `can0`, `candump`, `cansend` 사용 가능 |
| C3 | Normal mode | STM32 <-> USB-CAN 송수신 |
| C4 | Filter | 필요한 ID만 수신 |
| C5 | Error handling | ACK error, bus-off 원인 분리 가능 |
| C6 | Robot protocol | command/telemetry ID와 payload 정의 |
| C7 | RTOS integration | ISR에서 queue로 넘기고 task에서 parsing |

## 다음에 쌓을 세부 문서

- `01_bxCAN_Bit_Timing_Notes.md`
- `02_CAN_Filter_Bank_Examples.md`
- `03_CAN_Command_Telemetry_Frame_Spec.md`
- `04_CAN_Error_Debugging_Checklist.md`
