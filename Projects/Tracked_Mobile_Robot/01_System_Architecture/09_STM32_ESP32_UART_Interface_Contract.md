# STM32-ESP32 UART Interface Contract

## Purpose

This document defines the first communication contract between the STM32
NUCLEO-F446RE low-level controller and the ESP32-S3 DevKitC-1 support
controller. During the first lab, a PC serial terminal or Python script is
treated as the same kind of command source as the ESP32.

The goal is to make the interface safe, testable, and simple enough for the
first tracked drivetrain MVP.

The UART link is not a safety authority. It is a command request and telemetry
transport. STM32 still owns motor control, motor safety, encoder counting,
battery voltage decisions, and MDD10A PWM/DIR output behavior.

## Decision Summary

Use UART as the first STM32-ESP32 interface.

Initial decision:

- Physical interface: 3.3 V UART
- STM32 candidate peripheral: USART1
- STM32 candidate pins: PA9/PA10
- Frame format: 115200 baud, 8 data bits, no parity, 1 stop bit
- Initial protocol: newline-terminated ASCII text messages
- Initial command timeout: 300 ms
- Safety owner: STM32
- Wireless owner: ESP32-S3

Deferred from the first UART MVP:

- CAN
- USB host/device transport
- Binary packet protocol
- ROS2 integration over Wi-Fi
- Direct wireless high-power control

Note:

- CAN is deferred only from the initial UART bring-up.
- CAN remains a required later learning and integration phase.

## MVP Rule Set

This section defines the rules that the first PC/ESP32-to-STM32 UART MVP must
follow.

### Roles

```text
PC/ESP32 = command source, logger, dashboard
STM32    = parser, safety gate, drivetrain authority
```

Rules:

- PC and ESP32 use the same application frames.
- PC can replace ESP32 as a test source during the first lab.
- ESP32, PC, Wi-Fi, and dashboards do not directly own motor output.
- STM32 is the only authority for MDD10A PWM/DIR output and command timeout.

### MVP link

Initial PC lab:

```text
PC serial terminal / Python script
<-> ST-LINK Virtual COM Port
<-> STM32 USART2 candidate PA2/PA3
```

Initial ESP32 integration:

```text
ESP32 UART
<-> STM32 USART1 candidate PA9/PA10
```

Both paths use the same application protocol.

### MVP UART settings

| Item | Value |
| --- | --- |
| Baud rate | 115200 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |
| Frame delimiter | `\n` |
| Encoding | ASCII text |

### MVP frame set

| Direction | Frame | Purpose |
| --- | --- | --- |
| PC/ESP32 -> STM32 | `PING,seq=<u32>` | Link check |
| STM32 -> PC/ESP32 | `PONG,seq=<u32>,t_ms=<u32>` | Link response |
| PC/ESP32 -> STM32 | `ARM,seq=<u32>` | Request motion-command permission |
| PC/ESP32 -> STM32 | `DISARM,seq=<u32>` | Request motor-output disable |
| PC/ESP32 -> STM32 | `CMD,seq=<u32>,vx_mmps=<i32>,w_mradps=<i32>,timeout_ms=<u32>` | Motion command request |
| STM32 -> PC/ESP32 | `ACK,seq=<u32>,type=<text>` | Command accepted |
| STM32 -> PC/ESP32 | `ERR,seq=<u32>,type=<text>,code=<text>` | Command rejected or parse error |
| STM32 -> PC/ESP32 | `TEL,t_ms=<u32>,state=<text>,batt_mv=<u32>,left_cps=<i32>,right_cps=<i32>,left_pwm=<i32>,right_pwm=<i32>,fault=<u32>` | Periodic telemetry |

Do not add a separate `NACK` frame in the first MVP. Use `ERR` for negative
acknowledgement behavior.

### MVP command range

| Field | Range | MVP rule |
| --- | --- | --- |
| `seq` | `0` to `4294967295` | ACK/ERR matching and log analysis |
| `vx_mmps` | `-100` to `100` | Initial low-speed drive range |
| `w_mradps` | `-500` to `500` | Initial low-speed turn range |
| `timeout_ms` | `50` to `500` | Default `300` |

Reject out-of-range `CMD` frames with `ERR,code=OUT_OF_RANGE` instead of
clamping them. Tune actual motor output limits after MDD10A no-load and chassis
tests.

### MVP parser and response rule

- UART RX ISR only pushes bytes into the ring buffer and exits.
- The parser runs in the main loop or task context and assembles frames by `\n`.
- Overlong frames are dropped and the parse error count is incremented.
- Unknown frame types are handled as `ERR,code=UNKNOWN_TYPE` or ignored.
- Missing required `CMD` fields return `ERR,code=MISSING_FIELD`.
- Numeric conversion failures return `ERR,code=BAD_VALUE`.
- Range violations return `ERR,code=OUT_OF_RANGE`.
- Nonzero `CMD` frames in `DISARMED` return `ERR,code=NOT_ARMED`.
- Invalid `CMD` frames must not update the active command.

### MVP safety and timeout rule

Initial state:

```text
Boot -> DISARMED
PWM output -> 0
```

After `ARM` is accepted:

- Active commands are kept only while `CMD` frames arrive at about 20 Hz.
- A stopped-but-armed robot still receives repeated zero commands such as
  `CMD,seq=N,vx_mmps=0,w_mradps=0,timeout_ms=300`.
- If no new valid `CMD` arrives within `timeout_ms`, STM32 immediately sets
  motor output to zero.
- Right after timeout, keep the system armed with zero output instead of
  immediately entering `DISARMED`.
- The later auto-disarm delay is an open MVP decision.

Timeout is not an `ERR` response case because no new frame arrived. Report it
through `TEL` using `state`, `left_pwm`, `right_pwm`, `fault`, or a future
`warn` field.

### MVP telemetry rule

The first MVP keeps this telemetry shape:

```text
TEL,t_ms=123456,state=ARMED,batt_mv=0,left_cps=0,right_cps=0,left_pwm=0,right_pwm=0,fault=0\n
```

Rules:

- `state` uses at least `BOOT`, `DISARMED`, `ARMED`, and `FAULT`.
- PC-only parser labs may send `batt_mv`, `left_cps`, and `right_cps` as zero.
- UART-only labs without motor power keep `left_pwm` and `right_pwm` at zero.
- Telemetry does not replace safety decisions. STM32's internal state machine
  owns safety.
- Initial telemetry rate is 10 Hz.

### MVP evidence

The first UART MVP passes when these logs are captured:

- `PING` -> `PONG`
- `ARM` -> `ACK`
- valid `CMD` -> `ACK`
- missing-field `CMD` -> `ERR,code=MISSING_FIELD`
- out-of-range `CMD` -> `ERR,code=OUT_OF_RANGE`
- nonzero `CMD` while `DISARMED` -> `ERR,code=NOT_ARMED`
- telemetry confirms zero output after command timeout
- `DISARM` -> `ACK` and later `TEL,state=DISARMED`

## Sources

Project sources:

- `01_System_Architecture/06_MCU_Pin_Allocation_Candidate.md`
- `01_System_Architecture/07_ESP32S3_Features_and_Project_Role.md`
- `01_System_Architecture/08_Motor_Driver_and_HBridge_Control.md`
- `00_Project_Charter/03_Initial_Purchase_and_Safety.md`

## 1. Interface Boundary

The UART link connects two controllers with different responsibilities.

| Responsibility | STM32 NUCLEO-F446RE | ESP32-S3 DevKitC-1 |
| --- | --- | --- |
| Motor PWM | Owns | Does not own |
| MDD10A PWM/DIR output | Owns | Does not own |
| Encoder counting | Owns | Does not own |
| Motor speed estimation | Owns | Displays or forwards |
| Battery voltage safety | Owns | Displays telemetry |
| Command timeout | Owns | Sends requested timeout value only |
| Wireless dashboard | Does not own | Owns |
| Wi-Fi command source | Receives filtered request | Owns UI and forwarding |
| Telemetry formatting | Provides core telemetry | Displays/logs/forwards |
| Emergency stop request | Receives and enforces | May request |
| Final safety decision | Owns | Does not own |

Core rule:

```text
ESP32 may request motion.
STM32 decides whether motion is allowed.
```

## 2. Physical Wiring

Candidate wiring:

```text
STM32 PA9  / USART1_TX -> ESP32 UART_RX
STM32 PA10 / USART1_RX <- ESP32 UART_TX
STM32 GND              <-> ESP32 GND
```

Important:

- UART TX and RX must be crossed.
- Grounds must be common.
- Do not connect 5 V logic to either UART pin.
- Keep UART wires away from motor power wires.
- Test UART before motor power is connected.

STM32 candidate pins from the current pin allocation document:

| Signal | STM32 pin | Function | Board access | Status |
| --- | --- | --- | --- | --- |
| STM32 to ESP32 TX | PA9 | USART1_TX | Arduino D8 / ST morpho CN10 pin 21 | Reserve |
| ESP32 to STM32 RX | PA10 | USART1_RX | Arduino D2 / ST morpho CN10 pin 33 | Reserve |

ESP32-S3 pin assignment is not finalized in this document.

Selection rule for ESP32 pins:

- Use two exposed GPIOs that are safe for UART.
- Avoid USB Serial/JTAG pins.
- Avoid BOOT/strapping-sensitive pins unless the board manual confirms safe use.
- Avoid the current RGB LED pin used in project tests, GPIO38.
- Record the final ESP32 pin numbers after checking the exact DevKitC-1 board
  pinout and ESP-IDF UART mapping.

## 3. Electrical Rules

Both STM32F446RE and ESP32-S3 are 3.3 V logic devices.

Rules:

- Connect only 3.3 V UART signals.
- Connect common GND before UART signal testing.
- Do not use the 3S LiPo rail for logic signal testing.
- Do not power one board through the other board's UART pins.
- If either board is unpowered, avoid driving its UART input from the other
  board until the board's input behavior is confirmed.

Optional protection for early prototypes:

- 100 ohm to 330 ohm series resistor on TX lines
- Clearly labeled connector polarity
- JST/KF connector keying or color-coded wiring

## 4. UART Settings

Initial settings:

| Setting | Value |
| --- | --- |
| Baud rate | 115200 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |
| Line ending | `\n` |
| Encoding | ASCII UTF-8-safe subset |

Reason:

- 115200 baud is slow enough for reliable bring-up.
- ASCII messages are easier to debug with a serial monitor.
- The first goal is correctness and safety, not maximum bandwidth.

Later upgrade candidates:

- 230400 or 921600 baud after wiring is stable.
- Binary packets after the message fields stop changing.
- CRC after wireless command forwarding becomes active.

## 5. Protocol Direction

The link is bidirectional.

```text
ESP32 -> STM32: command requests, arm/disarm requests, heartbeat
STM32 -> ESP32: telemetry, state, faults, acknowledgements
```

The first protocol should be line-based text.

Message format:

```text
TYPE,key=value,key=value,...\n
```

Parsing rule:

- Unknown message types are ignored.
- Unknown fields are ignored.
- Required fields missing from a command make the command invalid.
- Invalid commands must not change motor output.

## 6. Command Messages

### CMD

`CMD` requests robot motion.

Example:

```text
CMD,seq=42,vx_mmps=80,w_mradps=0,timeout_ms=300\n
```

Fields:

| Field | Unit | Required | Meaning |
| --- | --- | --- | --- |
| `seq` | count | Yes | Monotonic command sequence number |
| `vx_mmps` | mm/s | Yes | Requested forward velocity |
| `w_mradps` | millirad/s | Yes | Requested yaw rate |
| `timeout_ms` | ms | Yes | Requested command validity window |

Initial limits:

- `vx_mmps` is clamped by STM32.
- `w_mradps` is clamped by STM32.
- `timeout_ms` is clamped by STM32.
- STM32 may ignore a command even if ESP32 sends it correctly.

Why integer units:

- Integer parsing is simpler and safer on MCU firmware.
- It avoids early floating-point text parsing errors.
- Units are explicit in field names.

### ARM

`ARM` requests that STM32 enter an armed state.

Example:

```text
ARM,seq=43\n
```

STM32 may reject this request if:

- Battery voltage is too low.
- MDD10A output safety self-check failed.
- Encoder test is required but not completed.
- Emergency stop or fault state is active.
- Firmware is still in startup delay.

### DISARM

`DISARM` requests motor output disable.

Example:

```text
DISARM,seq=44\n
```

Rule:

- `DISARM` should always be accepted if the frame is valid.
- After disarm, PWM outputs go to zero and nonzero motor output is blocked.

### PING

`PING` checks that the link is alive.

Example:

```text
PING,seq=45\n
```

STM32 response:

```text
PONG,seq=45,uptime_ms=123456\n
```

## 7. Telemetry Messages

### TEL

`TEL` carries normal robot telemetry from STM32 to ESP32.

Example:

```text
TEL,t_ms=123456,state=ARMED,batt_mv=11820,left_cps=120,right_cps=118,left_pwm=420,right_pwm=415,fault=0\n
```

Recommended initial telemetry fields:

| Field | Unit | Meaning |
| --- | --- | --- |
| `t_ms` | ms | STM32 uptime |
| `batt_mv` | mV | Measured battery voltage after ADC conversion |
| `left_cps` | counts/s | Left encoder count rate |
| `right_cps` | counts/s | Right encoder count rate |
| `left_mmps` | mm/s | Left track speed estimate, optional after calibration |
| `right_mmps` | mm/s | Right track speed estimate, optional after calibration |
| `left_pwm` | timer counts or percent-scaled value | Left motor command output |
| `right_pwm` | timer counts or percent-scaled value | Right motor command output |
| `state` | text | Safety state such as `BOOT`, `DISARMED`, `ARMED`, or `FAULT` |
| `motor_allowed` | 0/1 | Whether STM32 safety gate allows nonzero motor output. Optional in the MVP |
| `fault` | bitmask | Active fault flags |

Telemetry fields should be stable once ESP32 dashboard parsing begins.

### STATE

`STATE` reports high-level controller state changes.

Example:

```text
STATE,t_ms=123500,state=DISARMED,reason=BOOT\n
```

Candidate states:

- `BOOT`
- `DISARMED`
- `ARMED`
- `FAULT`
- `LOW_BATTERY`
- `TIMEOUT_STOP`

### FAULT

`FAULT` reports a fault event.

Example:

```text
FAULT,t_ms=124000,code=LOW_BATTERY,batt_mv=9600\n
```

The ESP32 displays and logs faults. It does not clear safety faults by itself.

## 8. Acknowledgement and Error Handling

STM32 should acknowledge important command messages.

Valid command response:

```text
ACK,seq=42,type=CMD\n
```

Rejected command response:

```text
ERR,seq=42,type=CMD,code=NOT_ARMED\n
```

Possible error codes:

| Code | Meaning |
| --- | --- |
| `BAD_FRAME` | Message could not be parsed |
| `UNKNOWN_TYPE` | Unsupported frame type |
| `MISSING_FIELD` | Required field missing |
| `BAD_VALUE` | Numeric conversion failure or malformed field value |
| `OUT_OF_RANGE` | Field outside allowed range |
| `NOT_ARMED` | Motion command rejected because robot is disarmed |
| `LOW_BATTERY` | Motion command rejected by battery safety |
| `FAULT_ACTIVE` | Fault state active |
| `TIMEOUT_TOO_LONG` | Requested timeout exceeds STM32 limit |

Minimum safe behavior:

- Malformed messages are ignored.
- Invalid `CMD` does not change the current command.
- If valid commands stop arriving, STM32 stops the motors.
- ESP32 reset or Wi-Fi failure must naturally cause STM32 timeout stop.

## 9. Timing Contract

Initial timing:

| Item | Value |
| --- | --- |
| ESP32 command send rate | 20 Hz while actively commanding |
| STM32 telemetry send rate | 10 Hz initially |
| Command timeout | 300 ms |
| PING interval | 1 s when idle |
| Startup motor-disabled delay | STM32-defined |

Rules:

- STM32 must stop motors if no valid `CMD` arrives within the active timeout.
- ESP32 must not keep replaying stale commands.
- A new command replaces the previous command only after it is parsed as valid.
- Telemetry may be dropped without affecting safety.

## 10. Safety Contract

STM32 must enforce:

- Motor output disabled during boot.
- MDD10A PWM output zero during boot.
- Command timeout stop.
- Low-voltage stop.
- PWM clamp.
- Acceleration and deceleration limit.
- MDD10A PWM zero before direction change.
- Emergency disarm.

ESP32 must enforce:

- Do not send high-speed commands from Wi-Fi UI during bring-up.
- Do not hide STM32 fault states.
- Do not automatically re-arm after STM32 fault or reset.
- Stop sending `CMD` when UI command source disconnects.
- Send `DISARM` when the user presses stop.

Shared rule:

```text
Safety is enforced at the lowest layer that can stop the motor.
```

For this project, that layer is STM32 plus MDD10A PWM/DIR output control.

## 11. Bring-Up Plan

### Stage 1: UART Loopback

- Test STM32 USART1 TX/RX loopback.
- Test ESP32 UART TX/RX loopback.
- Confirm baud rate and newline handling.

### Stage 2: Cross-Board Link Without Motor Power

- Connect STM32 PA9 to ESP32 RX.
- Connect ESP32 TX to STM32 PA10.
- Connect common GND.
- Keep motor battery disconnected.
- Send `PING` and confirm `PONG`.

### Stage 3: Telemetry Only

- STM32 sends `TEL`.
- ESP32 prints telemetry to USB serial monitor.
- No motor command is accepted yet.

### Stage 4: Command Parsing Without Motor Enable

- ESP32 sends `CMD`.
- STM32 parses and acknowledges.
- STM32 updates internal target variables.
- Motor PWM stays zero and nonzero MDD10A output stays blocked.

### Stage 5: Low-Power Motor Command Test

- Enable motor output only after MDD10A single-channel motor validation.
- Clamp command to a low PWM limit.
- Confirm timeout stop by unplugging ESP32 TX or stopping commands.

### Stage 6: Dashboard Integration

- ESP32 displays STM32 telemetry.
- ESP32 sends low-speed command requests from UI.
- STM32 remains the final safety gate.

## 12. Logging and Debugging

During early development:

- Keep STM32 USART2 or ST-LINK virtual COM for PC debug if available.
- Keep ESP32 USB Serial/JTAG monitor for ESP-side logs.
- Do not depend only on the STM32-ESP32 UART for debugging both boards.

Recommended logs:

STM32:

- Received command count
- Last valid command time
- Parse error count
- Current safety state
- Fault code
- PWM command values

ESP32:

- UART receive count
- UART parse error count
- Last telemetry time
- Wi-Fi client state
- Last command sent

## 13. Open Questions

These must be answered before final wiring:

- Whether the PC-first lab uses only ST-LINK VCP USART2 or also allows an external USB-UART adapter.
- Final ESP32-S3 UART GPIO pair.
- Whether STM32 USART1 PA9/PA10 remain conflict-free after MDD10A PWM/DIR pin validation.
- Whether level shifting or buffering is needed for the actual modules.
- Final command and telemetry rate. Current candidate is `CMD 20 Hz`, `TEL 10 Hz`.
- `auto_disarm_ms` after timeout-zero-output state.
- Maximum application frame length and ring buffer size.
- Whether unknown frame types return `ERR,code=UNKNOWN_TYPE` or are silently ignored.
- Final fault bitmask definition.
- Whether checksum should be added before Wi-Fi command forwarding.

## Architecture Decision

The first STM32-ESP32 link will be a 3.3 V UART interface using text messages.

STM32 owns all motor safety decisions. ESP32-S3 acts as a dashboard, command
request source, and telemetry bridge.

The next practical task is to validate UART on both boards without motor power,
then verify that MDD10A PWM/DIR outputs, encoders, ADC, I2C, USART2 debug, and
USART1 ESP32 link can coexist.

CAN remains a required follow-up interface after the UART command and telemetry
contract is validated.
