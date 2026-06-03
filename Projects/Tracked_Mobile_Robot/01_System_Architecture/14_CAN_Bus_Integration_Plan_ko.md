# CAN Bus Integration Plan

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트에 CAN을 어떻게 도입할지 정의한다.

CAN은 필수 학습 목표지만 첫 motor bring-up MVP에는 포함하지 않는다. 첫 drivetrain MVP는 UART 또는 USB
serial을 사용한다. 이유는 디버깅이 쉽기 때문이다. CAN은 command model, telemetry fields, safety
rules가 먼저 검증된 뒤 추가한다.

이 문서는 다음 질문에 답한다.

- 이 로봇에서 CAN이 왜 유용한가
- 어떤 hardware가 필요한가
- STM32 CAN pin을 CAN transceiver에 어떻게 연결하는가
- 첫 CAN ID와 frame은 어떻게 설계하는가
- CAN이 motor command 권한을 갖기 전에 어떻게 검증하는가
- CAN 통합이 성공했다는 증거는 무엇인가

## Architecture Decision

첫 실제 CAN controller는 STM32 bxCAN을 사용한다.

초기 CAN path:

```text
PC / USB-CAN adapter
        |
        v
CANH / CANL bus
        |
        v
CAN transceiver
        |
        v
STM32 CAN1 RX/TX
        |
        v
STM32 command queue and safety gate
```

핵심 결정:

```text
CAN은 communication transport를 바꾼다.
CAN은 motor-control owner나 safety owner를 바꾸지 않는다.
```

STM32는 계속 다음 책임을 가진다.

- Motor PWM output
- BTS7960 enable control
- Encoder counting
- Battery voltage safety
- Command timeout
- Heartbeat timeout
- Final motor output gating

CAN은 motion을 요청할 수 있지만, motion 허용 여부는 STM32가 결정한다.

## 1. 이 프로젝트에서 쓰는 CAN 용어

| Term | 이 프로젝트에서의 의미 |
| --- | --- |
| CAN controller | CAN frame을 만들고 받는 MCU peripheral. STM32 bxCAN이 controller다. |
| CAN transceiver | MCU logic pin과 CANH/CANL differential bus 사이의 전기적 interface. |
| CANH / CANL | Differential bus wire. 두 선의 전압 차이로 data를 표현한다. |
| CAN ID | Message identifier. Bus priority도 결정한다. 숫자가 낮을수록 우선순위가 높다. |
| Standard ID | 11-bit CAN identifier. 이 프로젝트는 standard ID부터 사용한다. |
| Extended ID | 29-bit CAN identifier. 첫 통합에는 필요하지 않다. |
| DLC | Data length code. Classical CAN은 0-8 data byte를 지원한다. |
| Termination | CAN bus 양 끝에 들어가는 120 ohm 저항. |
| Bus-off | 반복 error 때문에 CAN controller가 bus 참여를 중단하는 error state. |
| Heartbeat | Command source가 살아 있음을 증명하는 주기 message. |

## 2. 여기서 CAN이 유용한 이유

UART는 첫 bring-up에는 충분하지만, 이후 robot integration에서는 CAN이 더 적합하다.

장점:

- Differential signaling이라 motor noise 주변에서 single-ended UART보다 견고하다.
- 여러 node가 하나의 bus를 공유할 수 있다.
- Message ID 기반 arbitration과 priority가 있다.
- Hardware-level error detection이 있다.
- 차량, 모바일 로봇, 산업 장비, embedded control system에서 자주 쓰인다.

Project value:

- 실제 embedded communication 경험을 보여준다.
- UART만 사용한 프로젝트보다 portfolio 설명력이 강하다.
- 향후 motor controller, sensor module, ROS2 bridge node가 같은 bus를 공유할 수 있다.

한계:

- CAN은 고대역폭 sensor stream용 transport가 아니다.
- Image, point cloud, high-rate debug log는 classical CAN으로 보내지 않는다.

## 3. Entry Criteria

CAN을 motor command 권한에 연결하기 전에 다음 조건이 만족되어야 한다.

- UART command and telemetry contract가 동작한다.
- Command timeout으로 motor output이 정지한다.
- FreeRTOS 또는 bare-metal command queue ownership이 명확하다.
- Safety gate를 communication code가 우회할 수 없다.
- CAN 없이 low-duty motor test가 가능하다.
- CAN은 motor power를 끊거나 track을 들어 올린 상태에서 테스트할 수 있다.

이유:

CAN debugging이 기본 drivetrain, encoder, power, safety 문제를 가리면 안 된다.

## 4. 필요한 Hardware

Required hardware:

| Item | Purpose | Notes |
| --- | --- | --- |
| STM32 NUCLEO-F446RE | CAN controller | 내부 bxCAN peripheral 사용 |
| CAN transceiver module | STM32 logic CAN RX/TX를 CANH/CANL로 변환 | 초기 STM32 test에는 3.3 V-compatible transceiver 권장 |
| USB-CAN adapter | PC-side CAN node와 debugger | Ubuntu에서는 SocketCAN-compatible adapter가 편리 |
| 120 ohm resistors | Bus termination | 물리적 bus 양 끝에 하나씩 |
| Twisted pair wire | CANH/CANL bus wiring | 첫 bench test는 짧은 배선도 가능 |
| Common ground wire | Node 사이 기준 전위 | Bench prototype에서는 권장 |

권장 transceiver 방향:

- 첫 STM32 test에는 SN65HVD230 계열처럼 3.3 V CAN transceiver module을 우선 고려한다.
- 모든 5 V CAN module이 3.3 V logic을 안전하게 받는다고 가정하지 않는다.
- MCP2515 module은 별도 SPI CAN controller를 포함한다. STM32에는 이미 bxCAN이 있으므로 필수는 아니다.

## 5. STM32 Pin Candidate

Pin allocation 문서에서 reserve한 CAN1 pin:

| Signal | STM32 pin | Function | Board access | Status |
| --- | --- | --- | --- | --- |
| CAN RX | PA11 | CAN1_RX | ST morpho CN10 pin 14 | Reserved |
| CAN TX | PA12 | CAN1_TX | ST morpho CN10 pin 12 | Reserved |

Physical connection:

```text
STM32 PA12 / CAN1_TX -> Transceiver TXD
STM32 PA11 / CAN1_RX <- Transceiver RXD
STM32 GND            <-> Transceiver GND
Transceiver CANH     <-> CANH bus
Transceiver CANL     <-> CANL bus
```

중요:

- CANH와 CANL을 바꾸어 연결하면 안 된다.
- STM32 CAN pin은 CANH/CANL에 직접 연결하지 않는다.
- 실제 CAN bus에는 transceiver가 필수다.
- STM32에 연결하기 전에 transceiver supply voltage와 logic-level compatibility를 확인한다.

## 6. 초기 Bus Setup

Initial configuration:

| Setting | Initial value | Reason |
| --- | --- | --- |
| CAN type | Classical CAN | STM32 bxCAN 지원 |
| Identifier type | Standard 11-bit ID | 단순하고 이 프로젝트에 충분 |
| Bitrate | 500 kbit/s | Embedded robot에서 흔한 기본값 |
| Data length | Up to 8 bytes | Classical CAN frame limit |
| Termination | Bus 양 끝 120 ohm | Signal integrity에 필요 |
| First topology | PC USB-CAN <-> STM32 node | 가장 단순한 two-node test |

500 kbit/s가 wiring test에서 불안정하면 physical bus가 검증될 때까지 250 kbit/s로 낮춘다.

## 7. CAN Message Ownership

CAN message는 방향별로 분리한다.

```text
Command source -> STM32: command, heartbeat, arm/disarm, stop
STM32 -> Command source: status, telemetry, fault, acknowledgement
```

규칙:

- CAN receive code는 PWM을 직접 쓰지 않는다.
- Valid motion command는 UART가 쓰는 것과 같은 internal command structure로 변환한다.
- Heartbeat 누락 또는 stale command는 safe stop을 강제한다.
- Fault frame은 문제를 report한다. Local safety behavior를 대체하지 않는다.

## 8. 초기 CAN ID Map

Standard 11-bit ID를 사용한다.

Command IDs:

| CAN ID | Name | Direction | Period | Purpose |
| --- | --- | --- | --- | --- |
| `0x100` | `HEARTBEAT` | Controller -> STM32 | 10-20 Hz | Command source가 살아 있음을 증명 |
| `0x110` | `MOTION_CMD` | Controller -> STM32 | 10-50 Hz | Forward velocity와 yaw rate 요청 |
| `0x120` | `ARM_CMD` | Controller -> STM32 | Event | Arm 또는 disarm 요청 |
| `0x130` | `ESTOP_CMD` | Controller -> STM32 | Event | Immediate safe stop 요청 |

Telemetry IDs:

| CAN ID | Name | Direction | Period | Purpose |
| --- | --- | --- | --- | --- |
| `0x200` | `STATUS` | STM32 -> Controller | 10 Hz | Safety state, fault, battery, command age |
| `0x210` | `MOTOR_TELEM` | STM32 -> Controller | 10-50 Hz | Wheel speed와 PWM duty |
| `0x220` | `ENCODER_COUNT` | STM32 -> Controller | 10 Hz | Left/right encoder count snapshot |
| `0x230` | `IMU_TELEM` | STM32 -> Controller | Optional | Reduced IMU yaw 또는 yaw-rate |
| `0x2F0` | `FAULT_EVENT` | STM32 -> Controller | Event | Latched fault event |

Priority rule:

- Emergency와 heartbeat 관련 frame은 routine telemetry보다 낮은 ID를 사용한다.
- Telemetry가 command와 safety-related message를 막으면 안 된다.

## 9. Frame Definitions

Multi-byte value는 모두 little-endian byte order를 사용한다.

### `0x100 HEARTBEAT`

Direction: Controller -> STM32

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `seq` | `uint16_t` | count |
| 2 | `source_id` | `uint8_t` | enum |
| 3 | `flags` | `uint8_t` | bitfield |
| 4-5 | `timeout_ms` | `uint16_t` | ms |
| 6-7 | reserved | `uint16_t` | - |

규칙:

- Heartbeat가 설정된 timeout보다 오래 누락되면 STM32는 safe stop state로 들어간다.

### `0x110 MOTION_CMD`

Direction: Controller -> STM32

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `seq` | `uint16_t` | count |
| 2-3 | `vx_mmps` | `int16_t` | mm/s |
| 4-5 | `w_mradps` | `int16_t` | millirad/s |
| 6-7 | `timeout_ms` | `uint16_t` | ms |

규칙:

- STM32가 velocity, yaw rate, timeout을 clamp한다.
- Invalid 또는 stale command는 motor output을 바꾸지 않는다.

### `0x120 ARM_CMD`

Direction: Controller -> STM32

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `seq` | `uint16_t` | count |
| 2 | `request` | `uint8_t` | `0=disarm`, `1=arm` |
| 3 | `reason` | `uint8_t` | enum |
| 4-7 | reserved | bytes | - |

규칙:

- Arm request는 자동으로 accept되지 않는다.
- Safety precondition이 만족되지 않으면 STM32가 arm을 거부할 수 있다.

### `0x130 ESTOP_CMD`

Direction: Controller -> STM32

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `seq` | `uint16_t` | count |
| 2 | `reason` | `uint8_t` | enum |
| 3-7 | reserved | bytes | - |

규칙:

- Emergency stop request는 PWM zero와 driver disable을 강제한다.
- Recovery는 state machine 문서에서 정의한 explicit disarm 또는 reset procedure를 요구한다.

### `0x200 STATUS`

Direction: STM32 -> Controller

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0 | `safety_state` | `uint8_t` | enum |
| 1 | `fault_code` | `uint8_t` | enum |
| 2-3 | `battery_mv` | `uint16_t` | mV |
| 4-5 | `cmd_age_ms` | `uint16_t` | ms |
| 6-7 | `uptime_100ms` | `uint16_t` | 100 ms ticks |

### `0x210 MOTOR_TELEM`

Direction: STM32 -> Controller

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `left_cps` | `int16_t` | counts/s |
| 2-3 | `right_cps` | `int16_t` | counts/s |
| 4-5 | `left_pwm` | `int16_t` | signed duty |
| 6-7 | `right_pwm` | `int16_t` | signed duty |

### `0x220 ENCODER_COUNT`

Direction: STM32 -> Controller

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-3 | `left_count` | `int32_t` | counts |
| 4-7 | `right_count` | `int32_t` | counts |

### `0x2F0 FAULT_EVENT`

Direction: STM32 -> Controller

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `event_seq` | `uint16_t` | count |
| 2 | `fault_code` | `uint8_t` | enum |
| 3 | `safety_state` | `uint8_t` | enum |
| 4-5 | `detail` | `uint16_t` | fault-specific |
| 6-7 | `uptime_100ms` | `uint16_t` | 100 ms ticks |

## 10. Validation Phases

### Phase A: bxCAN Loopback

목적:

외부 wiring 없이 STM32 bxCAN 설정을 검증한다.

Scope:

- CAN1을 internal loopback mode로 설정.
- Test frame transmit.
- Receive callback 또는 polling path가 같은 frame을 보는지 확인.
- Filter가 의도한 ID를 accept하는지 확인.

Exit criteria:

- STM32 firmware가 내부적으로 known test frame을 송수신할 수 있다.

### Phase B: Physical Bus Bring-Up

목적:

Transceiver, wiring, termination, USB-CAN adapter를 검증한다.

Scope:

- STM32 CAN1을 transceiver에 연결.
- Transceiver를 CANH/CANL로 USB-CAN adapter에 연결.
- Termination 추가.
- Motor power는 disconnected 상태 유지.
- STM32에서 known frame을 보내고 PC에서 관찰.
- PC에서 known frame을 보내고 STM32에서 관찰.

Exit criteria:

- PC와 STM32가 선택한 bitrate에서 CAN frame을 교환한다.
- 반복 bus-off 또는 error-passive 동작이 발생하지 않는다.

### Phase C: Protocol Validation Without Motors

목적:

Motion 허용 없이 command parsing과 telemetry를 검증한다.

Scope:

- `HEARTBEAT`, `MOTION_CMD`, `ARM_CMD`, `ESTOP_CMD` 전송.
- Safety state는 disarmed로 유지.
- STM32가 command를 parse하고 status를 report하는지 확인.
- Invalid DLC, invalid ID, stale command가 reject되는지 확인.

Exit criteria:

- Motion command가 internal command path에는 들어가지만 disarmed 상태에서는 PWM을 구동하지 못한다.

### Phase D: Low-Speed Robot Integration

목적:

Safety validation 이후 CAN이 제한된 low-speed motion을 요청하도록 허용한다.

Scope:

- Track을 들어 올리거나 robot을 고정한다.
- Low-duty output만 허용한다.
- Low-speed `MOTION_CMD` 전송.
- Heartbeat timeout stop 확인.
- `ESTOP_CMD` stop 확인.
- Telemetry가 command age, battery, speed, PWM을 report하는지 확인.

Exit criteria:

- STM32가 low-speed CAN command를 수신한다.
- Heartbeat가 끊기면 motor output이 정지한다.
- Emergency stop request가 motor output을 정지한다.
- UART는 debug 또는 fallback path로 유지된다.

## 11. Ubuntu SocketCAN Debug Plan

USB-CAN adapter가 SocketCAN을 지원한다면 Linux `can0` interface를 사용한다.

Example commands:

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000
ip -details link show can0
candump can0
```

Example transmit:

```bash
cansend can0 100#010001002C010000
cansend can0 110#0200500000002C01
```

Notes:

- `100#...`는 CAN ID `0x100`을 의미한다.
- `#` 뒤의 byte들은 payload byte를 hexadecimal로 적은 것이다.
- `2C01`은 little-endian `uint16_t` 기준 `300`이다.

Adapter가 SocketCAN을 지원하지 않으면 vendor tool을 사용하되 다음 항목은 기록한다.

- Bitrate
- CAN ID
- Payload
- Timestamp
- Direction
- Error state if available

## 12. Fault Handling

CAN-related fault cases:

| Fault | Detection | Required response |
| --- | --- | --- |
| Heartbeat missing | Timeout 내 `HEARTBEAT` 없음 | Safe stop |
| Command stale | `MOTION_CMD` timeout 초과 | Safe stop |
| Invalid DLC | DLC가 frame definition과 다름 | Frame reject |
| Invalid value | Command가 limit 초과 | Clamp 또는 reject |
| Bus-off | CAN controller error state | Safe stop, fault report |
| Wrong bitrate | Frame 없음 또는 error counter 증가 | Motor enable 금지 |
| Reversed CANH/CANL | Communication 없음 또는 error 다수 | Test 중지 후 wiring 수정 |
| Missing termination | Communication 불안정 | Physical bus 수정 |
| Transceiver mismatch | Logic 또는 power incompatibility | Test 중지, module 교체 |

규칙:

```text
CAN failure는 motor output 관점에서 fail silent 해야 한다.
```

즉, communication failure는 uncontrolled motion이 아니라 motion stop으로 이어져야 한다.

## 13. FreeRTOS와의 통합

CAN은 두 가지 방식으로 통합할 수 있다.

| Option | Description | When to use |
| --- | --- | --- |
| Extend `comm_task` | UART와 CAN을 같은 communication task에서 처리 | 첫 통합에 단순함 |
| Add `can_task` | CAN RX/TX를 별도 task로 분리 | UART parsing과 CAN traffic이 복잡해질 때 |

초기 권장:

- 먼저 `comm_task`를 확장한다.
- 같은 internal `command_queue`를 유지한다.
- 같은 safety state와 output gate를 유지한다.
- CAN traffic 또는 diagnostics가 복잡해질 때만 별도 `can_task`를 추가한다.

Internal flow:

```text
CAN RX interrupt
        |
        v
small event / FIFO read
        |
        v
comm_task or can_task
        |
        v
validate frame
        |
        v
command_queue
        |
        v
motor_control_task + safety gate
```

## 14. Evidence Targets

CAN 통합은 portfolio-quality evidence를 남겨야 한다.

| Evidence | What it proves |
| --- | --- |
| CAN wiring photo | 실제 bus와 transceiver를 구성했음 |
| Termination measurement | Bus electrical setup을 확인했음 |
| CubeMX 또는 firmware CAN setting screenshot | bxCAN bitrate와 filter setup을 설정했음 |
| Loopback test log | 외부 wiring 전 STM32 CAN peripheral이 동작함 |
| `candump` 또는 vendor log | PC가 실제 CAN frame을 관찰할 수 있음 |
| `cansend` command and STM32 response | PC-to-STM32 command path가 동작함 |
| Heartbeat timeout test | Communication loss가 motor를 정지시킴 |
| E-stop frame test | Safety command가 강제됨 |
| Telemetry frame table | Message contract가 문서화됨 |

Minimum acceptance evidence:

```text
1. STM32 loopback frame confirmed.
2. USB-CAN adapter observes STM32 telemetry frame.
3. STM32 receives a PC-sent command frame.
4. Missing heartbeat forces safe stop.
```

## 15. Later Finalization Items

나중에 확정할 항목:

- 정확한 CAN transceiver module
- 정확한 USB-CAN adapter
- Wiring test 이후 final bitrate
- CAN을 FreeRTOS 이전에 통합할지 이후에 통합할지
- ESP32-S3 TWAI를 나중에 second CAN node로 사용할지
- Final CAN filter configuration
- Final fault code enum
- ROS2 bridge command path가 CAN을 직접 쓸지 ESP32/PC를 거칠지

## Final Decision

CAN은 필수 후속 phase지만 초기 bring-up dependency는 아니다.

프로젝트는 먼저 UART 기반 command와 telemetry를 검증하고, CAN을 독립적으로 검증한 뒤, UART와 같은
command queue와 safety gate에 CAN을 통합한다.

가장 중요한 규칙은 다음과 같다.

```text
CAN은 motion을 요청할 수 있지만, motion permission은 STM32 safety logic이 소유한다.
```
