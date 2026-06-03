# CAN Bus Integration Plan

## Purpose

This document defines how CAN will be introduced into the tracked mobile robot
project.

CAN is a required learning goal, but it is not part of the first motor bring-up
MVP. The first drivetrain MVP uses UART or USB serial because it is easier to
debug. CAN is added later after the command model, telemetry fields, and safety
rules are already proven.

This document answers:

- Why CAN is useful for this robot
- Which hardware is required
- How the STM32 CAN pins connect to a CAN transceiver
- Which CAN IDs and frames will be used first
- How CAN is validated before it is allowed to command motors
- What evidence proves that CAN integration worked

## Architecture Decision

Use STM32 bxCAN as the first real CAN controller.

Initial CAN path:

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

Core decision:

```text
CAN changes the communication transport.
CAN does not change the motor-control or safety owner.
```

STM32 remains responsible for:

- Motor PWM output
- BTS7960 enable control
- Encoder counting
- Battery voltage safety
- Command timeout
- Heartbeat timeout
- Final motor output gating

CAN may request motion, but STM32 decides whether motion is allowed.

## 1. CAN Terms Used in This Project

| Term | Meaning in this project |
| --- | --- |
| CAN controller | MCU peripheral that creates and receives CAN frames. STM32 bxCAN is the controller. |
| CAN transceiver | Electrical interface between MCU logic pins and the CANH/CANL differential bus. |
| CANH / CANL | Differential bus wires. Data is represented by the voltage difference between the two lines. |
| CAN ID | Message identifier. It also controls bus priority. Lower numeric ID has higher priority. |
| Standard ID | 11-bit CAN identifier. This project starts with standard IDs. |
| Extended ID | 29-bit CAN identifier. Not needed for the first integration. |
| DLC | Data length code. Classical CAN supports 0 to 8 data bytes. |
| Termination | 120 ohm resistor at each physical end of the CAN bus. |
| Bus-off | Error state where the CAN controller stops participating because of repeated errors. |
| Heartbeat | Periodic message that proves the command source is alive. |

## 2. Why CAN Is Useful Here

UART is sufficient for the first bring-up, but CAN is better for later robot
integration.

Advantages:

- Differential signaling is more robust around motor noise than single-ended
  UART.
- Multiple nodes can share one bus.
- Message IDs provide built-in arbitration and priority.
- CAN has hardware-level error detection.
- CAN is common in vehicles, mobile robots, industrial equipment, and embedded
  control systems.

Project value:

- Demonstrates real embedded communication experience.
- Gives a stronger portfolio story than only UART.
- Allows future nodes such as motor controllers, sensor modules, or a ROS2
  bridge node to share the same bus.

Limit:

- CAN is not a high-bandwidth sensor stream transport.
- Do not send images, point clouds, or high-rate debug logs over classical CAN.

## 3. Entry Criteria

CAN should not be connected to motor command authority until these conditions
are true:

- UART command and telemetry contract is working.
- Motor output stops on command timeout.
- FreeRTOS or bare-metal command queue ownership is clear.
- Safety gate cannot be bypassed by communication code.
- The robot can run low-duty motor tests without CAN.
- CAN can be tested with motor power disconnected or wheels lifted.

Reason:

CAN debugging should not hide basic drivetrain, encoder, power, or safety
problems.

## 4. Hardware Required

Required hardware:

| Item | Purpose | Notes |
| --- | --- | --- |
| STM32 NUCLEO-F446RE | CAN controller | Uses internal bxCAN peripheral |
| CAN transceiver module | Converts STM32 logic CAN RX/TX to CANH/CANL | Prefer 3.3 V-compatible transceiver for early tests |
| USB-CAN adapter | PC-side CAN node and debugger | SocketCAN-compatible adapter is convenient on Ubuntu |
| 120 ohm resistors | Bus termination | One resistor at each physical bus end |
| Twisted pair wire | CANH/CANL bus wiring | Short bench wires are acceptable first |
| Common ground wire | Reference between nodes | Recommended for bench prototypes |

Recommended transceiver direction:

- Prefer a 3.3 V CAN transceiver module such as SN65HVD230-class modules for
  first STM32 tests.
- Avoid assuming every 5 V CAN module accepts 3.3 V logic safely.
- MCP2515 modules include a separate SPI CAN controller, which is not required
  for STM32 because STM32 already has bxCAN.

## 5. STM32 Pin Candidate

Reserved CAN1 pins from the pin allocation document:

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

Important:

- CANH and CANL must not be swapped.
- STM32 CAN pins are not directly connected to CANH/CANL.
- A transceiver is mandatory for a real CAN bus.
- Verify the transceiver supply voltage and logic-level compatibility before
  connecting it to STM32.

## 6. Initial Bus Setup

Initial configuration:

| Setting | Initial value | Reason |
| --- | --- | --- |
| CAN type | Classical CAN | Supported by STM32 bxCAN |
| Identifier type | Standard 11-bit ID | Simpler and enough for this project |
| Bitrate | 500 kbit/s | Common embedded robot default |
| Data length | Up to 8 bytes | Classical CAN frame limit |
| Termination | 120 ohm at each bus end | Required for signal integrity |
| First topology | PC USB-CAN <-> STM32 node | Simplest two-node test |

If 500 kbit/s is unstable during wiring tests, drop to 250 kbit/s until the
physical bus is verified.

## 7. CAN Message Ownership

CAN messages are split by direction.

```text
Command source -> STM32: command, heartbeat, arm/disarm, stop
STM32 -> Command source: status, telemetry, fault, acknowledgement
```

Rules:

- CAN receive code does not write PWM directly.
- Valid motion commands are converted into the same internal command structure
  used by UART.
- Missing heartbeat or stale command forces safe stop.
- Fault frames report problems; they do not remove the need for local safety
  behavior.

## 8. Initial CAN ID Map

Use standard 11-bit IDs.

Command IDs:

| CAN ID | Name | Direction | Period | Purpose |
| --- | --- | --- | --- | --- |
| `0x100` | `HEARTBEAT` | Controller -> STM32 | 10-20 Hz | Proves command source is alive |
| `0x110` | `MOTION_CMD` | Controller -> STM32 | 10-50 Hz | Requested forward velocity and yaw rate |
| `0x120` | `ARM_CMD` | Controller -> STM32 | Event | Request arm or disarm |
| `0x130` | `ESTOP_CMD` | Controller -> STM32 | Event | Request immediate safe stop |

Telemetry IDs:

| CAN ID | Name | Direction | Period | Purpose |
| --- | --- | --- | --- | --- |
| `0x200` | `STATUS` | STM32 -> Controller | 10 Hz | Safety state, fault, battery, command age |
| `0x210` | `MOTOR_TELEM` | STM32 -> Controller | 10-50 Hz | Wheel speed and PWM duty |
| `0x220` | `ENCODER_COUNT` | STM32 -> Controller | 10 Hz | Left/right encoder count snapshot |
| `0x230` | `IMU_TELEM` | STM32 -> Controller | Optional | Reduced IMU yaw or yaw-rate |
| `0x2F0` | `FAULT_EVENT` | STM32 -> Controller | Event | Latched fault event |

Priority rule:

- Emergency and heartbeat-related frames use lower IDs than routine telemetry.
- Telemetry should not block command and safety-related messages.

## 9. Frame Definitions

All multi-byte values use little-endian byte order.

### `0x100 HEARTBEAT`

Direction: Controller -> STM32

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `seq` | `uint16_t` | count |
| 2 | `source_id` | `uint8_t` | enum |
| 3 | `flags` | `uint8_t` | bitfield |
| 4-5 | `timeout_ms` | `uint16_t` | ms |
| 6-7 | reserved | `uint16_t` | - |

Rule:

- If heartbeat is missing longer than the configured timeout, STM32 enters a
  safe stop state.

### `0x110 MOTION_CMD`

Direction: Controller -> STM32

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `seq` | `uint16_t` | count |
| 2-3 | `vx_mmps` | `int16_t` | mm/s |
| 4-5 | `w_mradps` | `int16_t` | millirad/s |
| 6-7 | `timeout_ms` | `uint16_t` | ms |

Rule:

- STM32 clamps velocity, yaw rate, and timeout.
- Invalid or stale commands do not change motor output.

### `0x120 ARM_CMD`

Direction: Controller -> STM32

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `seq` | `uint16_t` | count |
| 2 | `request` | `uint8_t` | `0=disarm`, `1=arm` |
| 3 | `reason` | `uint8_t` | enum |
| 4-7 | reserved | bytes | - |

Rule:

- Arm request is not automatically accepted.
- STM32 may reject arm if safety preconditions are not satisfied.

### `0x130 ESTOP_CMD`

Direction: Controller -> STM32

| Byte | Field | Type | Unit |
| --- | --- | --- | --- |
| 0-1 | `seq` | `uint16_t` | count |
| 2 | `reason` | `uint8_t` | enum |
| 3-7 | reserved | bytes | - |

Rule:

- Emergency stop request forces PWM zero and driver disable.
- Recovery requires an explicit disarm or reset procedure defined by the state
  machine document.

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

Purpose:

Validate STM32 bxCAN configuration without external wiring.

Scope:

- Configure CAN1 in internal loopback mode.
- Transmit test frames.
- Confirm receive callback or polling path sees the same frames.
- Confirm filters accept intended IDs.

Exit criteria:

- STM32 firmware can transmit and receive a known test frame internally.

### Phase B: Physical Bus Bring-Up

Purpose:

Validate the transceiver, wiring, termination, and USB-CAN adapter.

Scope:

- Connect STM32 CAN1 to transceiver.
- Connect transceiver to USB-CAN adapter through CANH/CANL.
- Add termination.
- Keep motor power disconnected.
- Send a known frame from STM32 and observe it on PC.
- Send a known frame from PC and observe it on STM32.

Exit criteria:

- PC and STM32 exchange CAN frames at the selected bitrate.
- No repeated bus-off or error-passive behavior occurs.

### Phase C: Protocol Validation Without Motors

Purpose:

Validate command parsing and telemetry without allowing motion.

Scope:

- Send `HEARTBEAT`, `MOTION_CMD`, `ARM_CMD`, and `ESTOP_CMD`.
- Keep safety state disarmed.
- Confirm STM32 parses commands and reports status.
- Confirm invalid DLC, invalid IDs, and stale commands are rejected.

Exit criteria:

- Motion commands enter the internal command path but cannot drive PWM while
  disarmed.

### Phase D: Low-Speed Robot Integration

Purpose:

Allow CAN to request limited low-speed motion only after safety validation.

Scope:

- Lift tracks or keep robot restrained.
- Enable low-duty output only.
- Send low-speed `MOTION_CMD`.
- Verify heartbeat timeout stop.
- Verify `ESTOP_CMD` stop.
- Verify telemetry reports command age, battery, speed, and PWM.

Exit criteria:

- STM32 accepts a low-speed CAN command.
- Missing heartbeat stops motor output.
- Emergency stop request stops motor output.
- UART remains available as debug or fallback.

## 11. Ubuntu SocketCAN Debug Plan

If the USB-CAN adapter supports SocketCAN, use the Linux `can0` interface.

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

- `100#...` means CAN ID `0x100`.
- The bytes after `#` are payload bytes in hexadecimal.
- `2C01` is `300` in little-endian `uint16_t`.

If the adapter does not support SocketCAN, use the vendor tool but still record:

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
| Heartbeat missing | No `HEARTBEAT` within timeout | Safe stop |
| Command stale | `MOTION_CMD` timeout exceeded | Safe stop |
| Invalid DLC | DLC does not match frame definition | Reject frame |
| Invalid value | Command exceeds limit | Clamp or reject |
| Bus-off | CAN controller error state | Safe stop, report fault |
| Wrong bitrate | No frames or error counters increase | Do not enable motors |
| Reversed CANH/CANL | No communication or many errors | Fix wiring before testing |
| Missing termination | Unstable communication | Fix physical bus |
| Transceiver mismatch | Logic or power incompatibility | Stop test, replace module |

Rule:

```text
CAN failure must fail silent with respect to motor output.
```

In other words, communication failure should stop motion, not create
uncontrolled motion.

## 13. Integration With FreeRTOS

CAN can be integrated in two ways:

| Option | Description | When to use |
| --- | --- | --- |
| Extend `comm_task` | UART and CAN are handled by the same communication task | Simpler first integration |
| Add `can_task` | CAN RX/TX has its own task | Better if UART parsing and CAN traffic become complex |

Initial recommendation:

- Start by extending `comm_task`.
- Keep the same internal `command_queue`.
- Keep the same safety state and output gate.
- Add a separate `can_task` only if CAN traffic or diagnostics becomes
  complex.

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

CAN integration should produce portfolio-quality evidence.

| Evidence | What it proves |
| --- | --- |
| CAN wiring photo | Physical bus and transceiver were actually built |
| Termination measurement | Bus electrical setup was checked |
| CubeMX or firmware CAN setting screenshot | bxCAN bitrate and filter setup were configured |
| Loopback test log | STM32 CAN peripheral works before external wiring |
| `candump` or vendor log | PC can observe real CAN frames |
| `cansend` command and STM32 response | PC-to-STM32 command path works |
| Heartbeat timeout test | Communication loss stops motors |
| E-stop frame test | Safety command is enforced |
| Telemetry frame table | Message contract is documented |

Minimum acceptance evidence:

```text
1. STM32 loopback frame confirmed.
2. USB-CAN adapter observes STM32 telemetry frame.
3. STM32 receives a PC-sent command frame.
4. Missing heartbeat forces safe stop.
```

## 15. Decisions To Finalize Later

Open decisions:

- Exact CAN transceiver module
- Exact USB-CAN adapter
- Final bitrate after wiring test
- Whether CAN is integrated before or after FreeRTOS
- Whether ESP32-S3 TWAI is used as a second CAN node later
- Final CAN filter configuration
- Final fault code enum
- Whether ROS2 bridge command path uses CAN directly or goes through ESP32/PC

## Final Decision

CAN is a required follow-up phase, not an initial bring-up dependency.

The project will first validate UART-based command and telemetry, then validate
CAN independently, then integrate CAN into the same command queue and safety
gate used by UART.

The most important rule is:

```text
CAN may request motion, but STM32 safety logic owns motion permission.
```
