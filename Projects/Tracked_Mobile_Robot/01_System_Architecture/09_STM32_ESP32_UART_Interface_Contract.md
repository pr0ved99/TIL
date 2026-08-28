# STM32-ESP32 UART Interface Contract

## Purpose

This document defines the communication contract between the STM32
NUCLEO-F446RE low-level controller and the ESP32-S3 DevKitC-1 support
controller. ESP32-S3 is the only Final MVP production external command ingress.
A PC serial terminal or Python script used STM32 USART2 only as a historical
bench source; optional interactive control must use `PC -> ESP32 -> STM32`.

The goal is to make the interface safe, testable, and simple enough for the
first tracked drivetrain MVP.

The UART link is not a safety authority. It is a command request and telemetry
transport. STM32 still owns motor control, motor safety, encoder counting,
battery voltage decisions, and MDD10A PWM/DIR output behavior.

## Decision Summary

Use UART as the first STM32-ESP32 interface.

Initial decision:

- Physical interface: 3.3 V UART
- STM32 peripheral: USART1
- STM32 pins: PA9/PA10
- ESP32 UART1 pins: GPIO17/GPIO18
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

This section defines the rules for the ESP32 production ingress and STM32
drivetrain controller. The PC-first lab is protocol evidence, not another
production owner.

### Roles

```text
ESP32 = production command ingress + STM32 bridge; optional PC arbitration/logger/dashboard pending
STM32 = parser, safety gate, drivetrain authority
PC    = optional ESP32 upstream client or historical bench source
```

Rules:

- Historical PC tools and ESP32 use the same application frames.
- Direct PC/ESP32 dual ownership is prohibited.
- If optional PC control is implemented, ESP32 arbitrates and forwards it as the single session owner.
- ESP32, PC, Wi-Fi, and dashboards do not directly own motor output.
- STM32 is the only authority for MDD10A PWM/DIR output and command timeout.

### MVP link

Historical PC-first bench path, not a production motion ingress:

```text
PC serial terminal / Python script
<-> ST-LINK Virtual COM Port
<-> STM32 USART2 candidate PA2/PA3
```

Final MVP production link:

```text
ESP32 UART1 GPIO17/GPIO18
<-> STM32 USART1 PA9/PA10
```

Both paths use the same application frames, but they must not be connected as
simultaneous STM32 command sources. Current command RX/parser binding is
`huart1`; USART2 is an encoder/debug logger.

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
| ESP32 -> STM32 | `PING,seq=<u32>` | Link check |
| STM32 -> ESP32 | `PONG,seq=<u32>,t_ms=<u32>` | Link response |
| ESP32 -> STM32 | `ARM,seq=<u32>` | Request motion-command permission |
| ESP32 -> STM32 | `DISARM,seq=<u32>` | Request motor-output disable |
| ESP32 -> STM32 | `ESTOP_RESET,seq=<u32>` | Request software E-stop latch clear after input recovery |
| ESP32 -> STM32 | `CMD,seq=<u32>,vx_mmps=<i32>,w_mradps=<i32>,timeout_ms=<u32>` | Motion command request |
| STM32 -> ESP32 | `ACK,seq=<u32>,type=<text>` | Command accepted |
| STM32 -> ESP32 | `ERR,seq=<u32>,type=<text>,code=<text>` | Command rejected or parse error |
| STM32 -> ESP32 | `TEL,t_ms=<u32>,state=<text>,reason=<text>,command_age_ms=<u32>,last_seq=<u32>,vx_mmps=<i32>,w_mradps=<i32>,left_pwm=<i32>,right_pwm=<i32>,left_cps=<i32>,right_cps=<i32>,batt_mv=<u32>,drop=<u32>,err=<u32>` | Periodic telemetry |

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
- Overlong frames or embedded CR/control bytes before LF increment the parse
  error count once and discard the complete frame through the next LF.
- Field keys must match exactly at comma-token boundaries; duplicated required
  keys are rejected as ambiguous.
- Integer fields require at least one digit, must end at a comma or frame end,
  and must fit the declared integer type.
- Unknown or unsupported frame types return `ERR,code=BAD_TYPE`.
- Missing required `CMD` fields return `ERR,code=MISSING_FIELD`.
- Numeric conversion, field-order, or extra-data failures return
  `ERR,code=MISSING_FIELD`.
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
- The same timeout handling zeros the stored command and enters `DISARMED`.
- Motion may resume only after an accepted `ARM` followed by a valid `CMD`.
  Timeout handling must not automatically restore the stored pre-timeout
  command, and a `CMD` received while still `DISARMED` is rejected.

ADR-015 fixes this required behavior. P-03A/P-03B checks timeout before
processing RX bytes, zeros output/stored command, and enters `DISARMED`.
Accepted `ARM` starts a fresh first-CMD window using the default 300 ms and the
current tick. The scoped 300 ms and canonical 500 ms target runtime and their
safe restores passed. P-03 does not implement sequence monotonicity, session
freshness, RX queue purging, or cryptographic anti-replay; a queued or replayed
`ARM` + `CMD` pair is outside the proven contract.

Timeout is not an `ERR` response case because no new frame arrived. P-04B now
reports the transition as `state=DISARMED,reason=CMD_TIMEOUT` while keeping the
stored command and applied output at zero. `command_age_ms` is based on a
separate accepted-CMD-only timestamp; it is not the internal first-CMD watchdog
timestamp that `ARM` refreshes.

### MVP telemetry rule

The current MVP keeps this telemetry shape:

```text
TEL,t_ms=123456,state=ARMED,reason=NONE,command_age_ms=85,last_seq=42,vx_mmps=50,w_mradps=0,left_pwm=50,right_pwm=50,left_cps=0,right_cps=0,batt_mv=0,drop=0,err=0\n
```

Rules:

- Current wire-level `state` values are `DISARMED`, `ARMED`, and `FAULT`.
  Boot is represented as `state=DISARMED,reason=BOOT`.
- `reason` is one of `BOOT`, `NONE`, `DISARM`, `CMD_TIMEOUT`, `ESTOP_ACTIVE`,
  `ESTOP_LATCHED`, `ESTOP_RESET`, or `OUTPUT_ERROR`.
- `command_age_ms=4294967295` means no `CMD` has been accepted since MCU boot.
  Only a successfully applied and committed `CMD` resets the age. `ARM`, a
  rejected `CMD`, `DISARM`, timeout, E-stop, and `ESTOP_RESET` do not reset it.
- PC-only parser labs may send `batt_mv`, `left_cps`, and `right_cps` as zero.
- `left_pwm/right_pwm` report the motor-output module's last successfully
  applied software cache in signed permille. `50` means 50 permille, or a 5%
  duty target.
- Stop, DISARM, timeout, and output-error paths report `0/0`.
- These fields are not measured PWM feedback, MDD10A output, or motor motion.
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
- telemetry confirms `DISARMED`, stored `vx/w=0`, and applied PWM `0/0` after
  command timeout
- accepted forward CMD reports `left_pwm=50,right_pwm=50`; ARM-only remains `0/0`
- no accepted CMD reports `command_age_ms=4294967295`; a successful CMD alone
  resets the age, which continues increasing after timeout
- timeout reports `state=DISARMED,reason=CMD_TIMEOUT` with zero stored command
  and applied PWM `0/0`
- direct-PC7 assertion/release reports `FAULT/ESTOP_ACTIVE` followed by
  `FAULT/ESTOP_LATCHED`
- `DISARM` -> `ACK` and later `TEL,state=DISARMED`

P-04B is currently `PARTIAL` in the UART/software-state scope. The boot,
accepted-CMD age, timeout, and direct-PC7 active-to-latched subvectors passed.
The post-test all-hooks-zero isolated STM32/ESP32 builds also passed. Active
reset rejection, released reset success, and target reflash/no-command safe
runtime remain open.

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
| Wi-Fi command source | Receives filtered request | Owns UI and forwarding if implemented |
| Telemetry formatting | Provides core telemetry | Displays/logs/forwards |
| Emergency stop request | Receives and enforces | May request |
| Final safety decision | Owns | Does not own |

Core rule:

```text
ESP32 may request motion.
STM32 decides whether motion is allowed.
```

## 2. Physical Wiring

Current production wiring:

```text
STM32 PA9  / USART1_TX -> ESP32 GPIO18 / UART1_RX
STM32 PA10 / USART1_RX <- ESP32 GPIO17 / UART1_TX
STM32 GND              <-> ESP32 GND
```

Important:

- UART TX and RX must be crossed.
- Grounds must be common.
- Do not connect 5 V logic to either UART pin.
- Keep UART wires away from motor power wires.
- Test UART before motor power is connected.

STM32 production pins from the current pin allocation document:

| Signal | STM32 pin | Function | Board access | Status |
| --- | --- | --- | --- | --- |
| STM32 to ESP32 TX | PA9 | USART1_TX | Arduino D8 / ST morpho CN10 pin 21 | Production / bench-validated |
| ESP32 to STM32 RX | PA10 | USART1_RX | Arduino D2 / ST morpho CN10 pin 33 | Production / bench-validated |

ESP32-S3 UART1 is fixed at GPIO17 TX and GPIO18 RX for this Final MVP board.

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

- STM32 rejects out-of-range `vx_mmps` without changing the active command.
- STM32 rejects out-of-range `w_mradps` without changing the active command.
- STM32 rejects out-of-range `timeout_ms` without changing the active command.
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

### ESTOP_RESET

`ESTOP_RESET` requests a software E-stop latch clear after the physical input
has returned healthy.

Example:

```text
ESTOP_RESET,seq=45\n
```

Rules:

- STM32 forces stored command and motor output to zero before evaluating reset.
- If the E-stop input is still active, STM32 returns
  `ERR,seq=45,type=ESTOP_RESET,code=ESTOP_ACTIVE`; it does not clear the latch or
  create a new persistent reset-rejected reason. TEL remains
  `state=FAULT,reason=ESTOP_ACTIVE`.
- If the input is healthy, STM32 clears the software latch, enters `DISARMED`,
  sets `reason=ESTOP_RESET`, and returns `ACK,seq=45,type=ESTOP_RESET`.
- A successful reset does not arm the robot or restore an old command. Motion
  still requires a new accepted `ARM` followed by a valid `CMD`.

The active-reject and released-success runtime vectors with the new TEL schema
are still open in P-04B.

### PING

`PING` checks that the link is alive.

Example:

```text
PING,seq=46\n
```

STM32 response:

```text
PONG,seq=46,t_ms=123456\n
```

## 7. Telemetry Messages

### TEL

`TEL` carries normal robot telemetry from STM32 to ESP32.

Example:

```text
TEL,t_ms=123456,state=ARMED,reason=NONE,command_age_ms=85,last_seq=42,vx_mmps=50,w_mradps=0,left_pwm=50,right_pwm=50,left_cps=120,right_cps=118,batt_mv=0,drop=0,err=0\n
```

Current telemetry fields:

| Field | Unit | Meaning |
| --- | --- | --- |
| `t_ms` | ms | STM32 uptime |
| `state` | text | Current safety state: `DISARMED`, `ARMED`, or `FAULT` |
| `reason` | text | Current state-transition/stop marker defined below |
| `command_age_ms` | ms | Time since the last successfully accepted CMD, or `UINT32_MAX` if none |
| `last_seq` | count | Last sequence recorded by the current protocol behavior; not the age source |
| `vx_mmps` | mm/s | Stored forward command; zero on stop paths |
| `w_mradps` | millirad/s | Stored yaw command; zero on stop paths |
| `left_pwm` | signed permille | Left software-applied motor target; not measured feedback |
| `right_pwm` | signed permille | Right software-applied motor target; not measured feedback |
| `left_cps` | counts/s | Left encoder count rate |
| `right_cps` | counts/s | Right encoder count rate |
| `batt_mv` | mV | Current P-04B placeholder `0`; actual ADC source is P-05 |
| `drop` | count | RX ring-buffer drop count |
| `err` | count | Protocol/runtime error count |

Telemetry fields should be stable once ESP32 dashboard parsing begins.

Current `reason` values:

| Value | Meaning |
| --- | --- |
| `BOOT` | Initial marker while the current state is `DISARMED` |
| `NONE` | No active software stop reason |
| `DISARM` | A valid `DISARM` was accepted |
| `CMD_TIMEOUT` | Accepted-CMD timeout or ARM first-CMD window expiry |
| `ESTOP_ACTIVE` | E-stop input is active HIGH/open-fault |
| `ESTOP_LATCHED` | Input recovered but the software latch remains set |
| `ESTOP_RESET` | Explicit reset was accepted with a healthy input |
| `OUTPUT_ERROR` | Mapper or motor-output application failed and output was zeroed |

The active-reset rejection is an `ERR` event, not another persistent reason.
It leaves the current telemetry reason as `ESTOP_ACTIVE`.

### STATE

`STATE` is a future event-frame candidate. The current MVP firmware does not
emit a separate `STATE` frame; periodic `TEL` carries `state` and `reason`.

Example:

```text
STATE,t_ms=123500,state=DISARMED,reason=BOOT\n
```

Candidate high-level state names:

- `BOOT`
- `DISARMED`
- `ARMED`
- `FAULT`
- `LOW_BATTERY`

Current P-04B TEL reports command timeout as
`state=DISARMED,reason=CMD_TIMEOUT` with zero stored command. ADR-015 does not
define a separate `TIMEOUT_STOP` state.

### FAULT

`FAULT` is a future event-frame candidate. The current MVP firmware reports
fault state and reason through periodic `TEL` and does not emit this separate
frame.

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
| `MISSING_SEQ` | Missing or invalid `seq` |
| `MISSING_FIELD` | Required field missing |
| `BAD_TYPE` | Empty or unsupported frame type |
| `OUT_OF_RANGE` | Field outside allowed range |
| `NOT_ARMED` | Motion command rejected because robot is disarmed |
| `TIMEOUT_OUT_OF_RANGE` | Requested timeout is outside the accepted range |
| `ESTOP_LATCHED` | ARM or CMD is rejected while the E-stop latch is set |
| `ESTOP_ACTIVE` | `ESTOP_RESET` is rejected while the physical input is active |
| `MAPPER_FAILED` | Drive-command mapping failed before output apply |
| `MOTOR_OUTPUT_FAILED` | Motor-output apply or verification failed |

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

These must be answered before final wiring. ADR-015 already closes command
ownership, production UART routing, and timeout recovery policy.

- Optional `PC -> ESP32` upstream transport and arbitration, if implemented.
- Whether level shifting or buffering is needed for the actual modules.
- Final command and telemetry rate. Current candidate is `CMD 20 Hz`, `TEL 10 Hz`.
- Maximum application frame length and ring buffer size.
- Final fault bitmask definition.
- Whether checksum should be added before Wi-Fi command forwarding.

## Architecture Decision

The STM32-ESP32 link is a 3.3 V UART interface using text messages.

The Final MVP production path is `ESP32 UART1 GPIO17/GPIO18 <-> STM32 USART1
PA9/PA10`. ESP32-S3 is the only external command ingress; USART2 is bench
debug/encoder logging only. STM32 owns all motor safety decisions. Source loss
requires output/stored-command zero, `DISARMED`, and an accepted `ARM` plus a
valid `CMD`. This is a state-machine recovery contract, not proof of transport
freshness or anti-replay.

The P-02C-2 historical checkpoint is `25/25`; P-03 reached `26/26` and passed
the scoped 300/500 ms target timeout/recovery and safe-restore runs. P-04A
connected software-applied signed PWM to STM32 TEL and the ESP32 parser/log at
the historical `27/27` checkpoint. P-04B adds `reason/command_age_ms` actual
sources and required ESP32 parsing. Current host/static discovery passes all
**28/28** tests: firmware source contracts `24/24`, independent mapper vectors
`2/2`, and UART frame vectors `2/2`; all controlled hooks in the current source
are `0U`.

P-04B run02 passed the no-CMD sentinel, accepted-CMD-only age reset, and 500 ms
`CMD_TIMEOUT` subvector. Run04 passed direct-PC7
`ESTOP_ACTIVE -> ESTOP_LATCHED` in the UART/software-state scope. The post-test
hook-zero isolated STM32/ESP32 builds passed. P-04B remains `PARTIAL`: active
reset rejection, released reset success, and target reflash/no-command safe
runtime are open. These UART logs are not measured PWM, conditioned E-stop,
K1 rail-off, exact artifact
linkage, physical setup, or motor evidence. Battery telemetry remains P-05.

CAN remains a required follow-up interface after the UART command and telemetry
contract is validated.
