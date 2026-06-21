# Tracked Mobile Robot Project Memory

This file stores stable project facts so future work does not repeat the same questions.

Last updated: 2026-06-21

## Project Identity

- Project path: `/home/proved/my_ws/github/pr0ved99/TIL/Projects/Tracked_Mobile_Robot`
- Goal: build a reliable STM32-based tracked mobile robot lower-control platform that can later expand to CAN, FreeRTOS, LL Driver, ROS 2, LiDAR, SLAM, and Nav2.
- First MVP is not full autonomy. The first MVP is safe low-speed drivetrain control with encoder feedback and command timeout.

## Fixed Hardware Context

| Area | Current decision |
| --- | --- |
| Low-level controller | NUCLEO-F446RE |
| Support controller | ESP32-S3 DevKitC |
| Motor driver | MDD10A dual-channel DC motor driver |
| Previous motor driver path | BTS7960 is superseded for the first drivetrain path |
| Battery | 3S LiPo |
| Power safety | Fuse, DC-rated main switch, LiPo alarm, measured buck converter output |
| IMU candidate | BNO08x |
| CAN controller | STM32 internal bxCAN |
| CAN transceiver | Not selected yet |
| USB-CAN adapter | Not selected yet |
| DC main switch | Not arrived as of 2026-06-08 |

## Fixed Architecture Decisions

- STM32 owns final motor output permission.
- ESP32, PC, CAN, and future ROS 2 can request motion but cannot bypass STM32 safety.
- MDD10A control model is motor당 `PWM + DIR`.
- Direction changes must ramp or set PWM to zero before changing `DIR`.
- UART/USB serial comes before CAN for first bring-up.
- CAN is still a required later phase.
- FreeRTOS comes after HAL bare-metal drivetrain behavior is validated.
- LL Driver migration comes after a known-good HAL baseline.
- ROS 2 bridge comes after low-level drivetrain safety, timeout, and odometry basics are validated.

## Current Pin Candidate

| Function | Candidate |
| --- | --- |
| PC serial TX/RX | PA2 / PA3, USART2 |
| ESP32 UART TX/RX | PA9 / PA10, USART1 |
| Left motor PWM | PB6, TIM4_CH1 |
| Right motor PWM | PB7, TIM4_CH2 |
| Left motor DIR | PC8 |
| Right motor DIR | PC9 |
| Optional power gate/brake | PC6 / PC5 only if a separate circuit is added |
| Left encoder A/B | PB4 / PB5, TIM3 |
| Right encoder A/B | PA0 / PA1, TIM5 |
| Battery ADC | PA4 |
| IMU I2C | PB8 / PB9, I2C1 |
| CAN RX/TX | PA11 / PA12, CAN1 |
| SWD | PA13 / PA14 preserved |

## CAN Parts Needed Later

Minimum CAN bring-up parts:

- 3.3 V CAN transceiver module, SN65HVD230-class preferred for first STM32 test
- SocketCAN-compatible USB-CAN adapter
- 120 ohm termination resistor x2
- Twisted pair wire for CANH/CANL
- Common GND wire for bench prototype
- Jumper wires or small breadboard/prototype connector

Avoid MCP2515 as the first STM32 path because STM32F446RE already has bxCAN. MCP2515 is an external SPI CAN controller and is unnecessary for this project unless there is a specific later reason.

## Current Documentation State

The current canonical architecture docs are under `01_System_Architecture/*_ko.md`.

Important docs:

- `08_Motor_Driver_and_HBridge_Control_ko.md`: MDD10A decision and PWM+DIR control contract
- `20_Motor_Driver_Selection_Comparison_ko.md`: BTS7960 to MDD10A decision history and comparison
- `11_System_Block_Diagram_and_Interface_Map_ko.md`: full hardware/software interface map
- `14_CAN_Bus_Integration_Plan_ko.md`: CAN ID and frame plan
- `16_Control_Loop_and_State_Machine_ko.md`: safety state machine and motor output rules
- `19_Architecture_Decision_Record_ko.md`: accepted, deferred, superseded decisions
- `02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md`: first MDD10A logic validation plan
- `07_Embedded_Learning_Notes/README.md`: embedded learning note structure, concept notes, board practice logs, protocol labs, measurement logs
- `07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/001_UART_Command_Telemetry_Protocol_ko.md`: UART command/telemetry protocol learning note
- `07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/002_PC_Telemetry_Dashboard_Mock_ko.md`: PC-side dashboard mock plan
- `07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/003_Optional_WebSocket_AI_Log_Diagnosis_ko.md`: optional WebSocket and AI-assisted log diagnosis plan
- `04_PC_Serial_Control/tools/UartMvpTool.ps1`: Windows PowerShell PC-side UART MVP frame builder, sender, monitor, scripted smoke test, and raw/parsed logger
- `04_PC_Serial_Control/tools/uart_mvp_tool.sh`: Ubuntu/Linux Bash PC-side UART MVP frame builder, sender, monitor, scripted smoke test, and raw/parsed logger
- `04_PC_Serial_Control/tools/uart_mvp_tool.py`: Python PC-side UART MVP frame builder, sender, monitor, scripted smoke test, and raw/parsed logger
- `04_PC_Serial_Control/web_serial_dashboard`: browser Web Serial UART MVP dashboard
- `04_PC_Serial_Control/tools/ServeWebDashboard.ps1`: Windows localhost static server for Web Serial dashboard
- `04_PC_Serial_Control/tools/serve_web_dashboard.sh`: Ubuntu/Linux localhost static server for Web Serial dashboard
- `04_PC_Serial_Control/docs/01_PC_UART_MVP_Test_Tool_ko.md`: PC-side UART MVP test guide
- `04_PC_Serial_Control/docs/02_STM32_UART_MVP_Firmware_Guide_ko.md`: STM32 USART2/ring-buffer/parser implementation guide
- `04_PC_Serial_Control/docs/03_Ubuntu_UART_MVP_Test_Tool_ko.md`: Ubuntu PC-side UART MVP test guide with `/dev/ttyACM0`, `dialout`, and `stty` notes
- `04_PC_Serial_Control/docs/04_Web_Serial_Dashboard_ko.md`: browser Web Serial dashboard guide
- `04_PC_Serial_Control/docs/05_UART_MVP_Runbook_ko.md`: end-to-end UART MVP execution guide for Web dashboard and terminal tools
- `04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`: detailed CubeIDE implementation guide for USART2, ring buffer, parser, state machine, timeout, and telemetry

## Current Progress Snapshot

- ROS 2 Humble, RViz2, and Gazebo classic 11 were installed and basic execution was verified on the laptop.
- ROS 2 A-to-Z learning map and practice paths were added.
- NUCLEO-F446RE CAN A-to-Z learning map and practice paths were added.
- NUCLEO-F446RE FreeRTOS A-to-Z learning map and practice paths were added.
- System architecture was updated to make MDD10A the first motor driver path.
- MDD10A logic validation replaced BTS7960 logic validation.
- BTS7960 is preserved as a superseded design alternative and comparison point, not the active wiring or firmware contract.
- English mirror architecture docs were updated to remove stale active BTS7960/RPWM/LPWM assumptions.
- Embedded learning notes were split into concept notes, STM32/ESP32 practice logs, protocol practice, and measurement/debugging records under `07_Embedded_Learning_Notes`.
- UART protocol learning note now explains frame vs field, sequence number, telemetry, CMD required fields, ACK/ERR, DISARM/DISARMED, and zero CMD keepalive behavior while armed.
- Official UART MVP rule now treats PC and ESP32 as equivalent command sources that use the same line-based frames. STM32 remains the parser, safety gate, drivetrain authority, and command-timeout owner.
- First UART MVP uses `ACK` for accepted commands and `ERR` for rejected commands or parse failures. A separate `NACK` frame is not used.
- Timeout policy candidate: timeout immediately forces motor output zero while staying armed first; later auto-disarm delay still needs confirmation.
- PC telemetry dashboard mock is planned as a fake-telemetry-first tool before real serial integration.
- PC-first UART MVP tooling was added under `04_PC_Serial_Control`. The PowerShell tool is the current Windows-first path because this machine does not currently expose a working Python launcher. The Bash tool is the Ubuntu/Linux path for `/dev/ttyACM0` or `/dev/ttyUSB0`. The tools can build frames, send frames over a serial port, run an interactive console, run a scripted MVP smoke test, monitor RX lines, and save raw/parsed logs.
- A browser-based Web Serial dashboard was added under `04_PC_Serial_Control/web_serial_dashboard`. This is not a backend WebSocket bridge; Chrome/Edge directly opens the serial port from `localhost`, keeping the first web UI simple.
- `04_PC_Serial_Control/docs/05_UART_MVP_Runbook_ko.md` is the primary execution guide for running the Web dashboard, Windows terminal tool, Ubuntu terminal tool, and collecting MVP evidence.
- `04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md` is the detailed STM32 firmware build guide for the UART MVP.
- STM32-side UART MVP firmware guide was added for USART2, RX interrupt, ring buffer, parser, ACK/ERR/TEL responses, timeout handling, and telemetry generation.
- WebSocket dashboard and AI-assisted log diagnosis are optional extensions, not MVP scope.
- AI must not be the primary motor safety authority; STM32 deterministic safety remains authoritative.
- MDD10A board is available.
- A dated execution plan exists for 2026-06-08 to 2026-06-10 hardware work.
- Today's allowed hardware work is fuse soldering and unpowered MDD10A visual/DMM inspection only.
- Latest pushed commit at the time this memory was created: `bc50ec7 docs(robot): update tracked robot architecture`.

## Open Decisions

Ask the user or verify from hardware only for these:

- Exact DC motor to use first: MG540, JGB37-520, or another available motor
- MDD10A channel mapping: `PWM1/DIR1` left or right
- Final PWM frequency
- Final CAN transceiver model
- Final USB-CAN adapter model
- Battery voltage divider resistor values
- Encoder voltage and counts-per-revolution
- Actual fuse rating after current measurement
- Whether a separate power gate, brake, or emergency-stop circuit will be added
- PC-first UART path: ST-LINK VCP USART2 only, or also external USB-UART
- UART auto-disarm delay after timeout-zero-output state
- UART maximum application frame length and ring buffer size
- UART unknown frame type handling: return `ERR,code=UNKNOWN_TYPE` or ignore
- Whether checksum/CRC stays deferred until Wi-Fi forwarding

## Next Concrete Actions

1. Execute `docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md`.
2. Solder and insulate only the fuse-holder path with LiPo disconnected.
3. Run `02_Hardware_Validation/00_MDD10A_Visual_and_Multimeter_Inspection.md`.
4. After the DC-rated main switch arrives, install the switch/fuse path and run `02_Hardware_Validation/01_Power_Bringup_Checklist.md`.
5. Run `02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md` before connecting STM32, ESP32, or sensors to buck output.
6. Run `02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md`.
7. Check encoder voltage before connecting encoder signals to STM32.
8. Do one-channel MDD10A no-load motor test at low duty.
9. Later, confirm or purchase CAN transceiver, USB-CAN adapter, 120 ohm resistors, and CAN wiring.
10. For the PC-first UART MVP, run `tools/UartMvpTool.ps1 -Mode ListPorts`, then run `Interactive` or `ScriptedTest` against the ST-LINK Virtual COM Port.
11. On Ubuntu, run `bash tools/uart_mvp_tool.sh list-ports`, then use `/dev/ttyACM0` with `interactive` or `scripted-test`. If permission is denied, add the user to the `dialout` group and log in again.
12. For the browser dashboard on Windows, run `tools/ServeWebDashboard.ps1` and open `http://localhost:8765/` in Chrome or Edge.
13. For the browser dashboard on Ubuntu, run `bash tools/serve_web_dashboard.sh` and open `http://localhost:8765/` in Chrome or Edge.
