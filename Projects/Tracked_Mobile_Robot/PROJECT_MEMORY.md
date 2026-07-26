# Tracked Mobile Robot Project Memory

This file stores stable project facts so future work does not repeat the same questions.

Last updated: 2026-07-26

## Project Identity

- Current local project path on this machine: `C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot`
- Repository-relative project path: `Projects/Tracked_Mobile_Robot`
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
| Chassis source drawing | `08_Mechanical_Design/source/chassis/R3_High_Config_Version_Tracked_Vehicle_Hole_Pattern_Drawing.dwg` |
| Adapter plate Rev A | 174 x 208.93379 mm, acrylic 3T candidate, small mounting holes nominal 3.3 mm |
| Electronics carrier | 150 x 100 mm universal PCB, 55 x 37 hole array |
| CAN controller | STM32 internal bxCAN |
| CAN transceiver | Not selected yet |
| USB-CAN adapter | Not selected yet |
| DC main switch | Available; fused switch path validated 2026-07-10 and MDD10A input check repeated 2026-07-26 |

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

## Current Pin Allocation And Candidates

| Function | Candidate |
| --- | --- |
| PC serial TX/RX | PA2 / PA3, USART2 |
| STM32 ESP bridge UART TX/RX | PA9 / PA10, USART1 |
| ESP32 UART TX/RX candidate | GPIO17 / GPIO18 |
| Firmware motor channel 1 PWM, bench-confirmed | PB6, TIM4_CH1 -> MDD10A PWM1 |
| Firmware motor channel 2 PWM, bench-confirmed | PB7, TIM4_CH2 -> MDD10A PWM2 |
| Firmware motor channel 1 DIR, bench-confirmed | PC8 -> MDD10A DIR1 |
| Firmware motor channel 2 DIR, bench-confirmed | PC9 -> MDD10A DIR2 |
| Optional power gate/brake | PC6 / PC5 only if a separate circuit is added |
| Encoder channel 1 A/B candidate | PB4 / PB5, TIM3 |
| Encoder channel 2 A/B candidate | PA0 / PA1, TIM5 |
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
- `02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md`: 2026-07-26 STM32 pin-only and MDD10A powered/no-motor logic validation record
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
- `04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`: STM32CubeMX-first detailed implementation guide for NUCLEO-F446RE, USART2, ring buffer, parser, state machine, timeout, and telemetry
- `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md`: ESP32 UART1 loopback, STM32 PING/PONG/TEL integration, scripted safety sequence, timeout-zero, and final evidence
- `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/002_ESP32_IDF_Environment_Bringup_ko.md`: ESP32-S3 ESP-IDF v6.0.2 bring-up evidence
- `08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md`: adapter plate and electronics placement baseline, Rev A state, and remaining physical checks
- `08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`: Rev A dimension, A4 1:1, vendor-template PDF, vector-scale, and order-attempt record
- `08_Mechanical_Design/source/chassis/README.md`: preserved original R3 tracked-chassis hole-pattern DWG and SHA-256
- `08_Mechanical_Design/releases/revA/README.md`: Rev A DXF, DWG, SVG, PDF release-file index and SHA-256 values
- `08_Mechanical_Design/references/vendor_templates/README.md`: preserved Multimaker source template, original filename, and SHA-256
- `assets/screenshots/mechanical_layout/README.md`: adapter plate and electronics layout screenshot index
- `docs/progress/2026-07-26_progress.md`: latest progress note for STM32 PWM/DIR, MDD10A powered/no-motor and MG540 encoder loaded-voltage validation
- `docs/progress/2026-07-24_progress.md`: Rev A manufacturing files, 1:1/vector validation, and vendor upload blocker
- `docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md`: 2026-07-26 V-model gate roadmap and current execution order
- `docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`: project-wide requirement, design, test, evidence, and result traceability
- `docs/progress/2026-07-23_progress.md`: adapter plate Draft, electronics placement, and Onshape Version
- `docs/progress/2026-07-20_progress.md`: ESP32 scripted safety sequence, timeout-zero, and bridge MVP PASS
- `docs/handoff/README.md`: handoff folder index and reading order
- `docs/handoff/NEXT_SESSION_START_PROMPT.md`: prompt to paste into a new Codex session
- `docs/handoff/2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md`: historical UART bridge closeout; current continuation is `NEXT_SESSION_START_PROMPT.md` plus the latest progress note

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
- `04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md` is the current detailed STM32 firmware build guide for the UART MVP.
- The STM32 firmware workflow is now STM32CubeMX-first: install/run standalone STM32CubeMX, select `NUCLEO-F446RE` through Board Selector, configure USART2 and NVIC, generate code under `03_Firmware/stm32_uart_mvp`, then open/import in STM32CubeIDE.
- `STM32CubeIDE Empty Project` is not the starting point for the current MVP because the project depends on CubeMX `.ioc` and generated HAL initialization code.
- STM32-side UART MVP firmware guide covers USART2, RX interrupt, ring buffer, parser, ACK/ERR/TEL responses, timeout handling, and telemetry generation.
- WebSocket dashboard and AI-assisted log diagnosis are optional extensions, not MVP scope.
- AI must not be the primary motor safety authority; STM32 deterministic safety remains authoritative.
- MDD10A board is available.
- A dated execution plan exists for 2026-06-08 to 2026-06-10 hardware work.
- PC-first STM32 UART MVP was validated on 2026-07-09 with the Web Serial dashboard, screenshots, CSV log, requirements, verification matrix, and test report.
- MDD10A unpowered inspection and XL4015 #1/#2 no-load 5 V calibration were recorded on 2026-07-10.
- STM32 project now has an ESP bridge path through USART1 `PA9 TX` / `PA10 RX`; verify the `huart1` protocol path before bridge testing.
- ESP32-S3 ESP-IDF v6.0.2 environment bring-up was completed on 2026-07-14 with `hello_world` build, flash, and monitor on `COM4`.
- Current COM map: STM32 ST-LINK VCP is `COM3`; ESP32-S3 serial port is `COM4`.
- ESP32 bring-up screenshots are under `assets/screenshots/esp32_uart_bridge`.
- ESP32 UART1 is fixed for this practice at `GPIO17 TX`, `GPIO18 RX`, `115200 8N1`.
- ESP32 GPIO17/GPIO18 loopback passed on 2026-07-14.
- ESP32 UART1 to STM32 USART1 board-to-board `PING/PONG` passed on 2026-07-14 with TX/RX crossed and common GND.
- STM32 `TEL` telemetry reached the ESP32 monitor, and the ESP32 parser classified `TEL` and `PONG` while tracking `tel_count` and `pong_count`.
- The failed pre-flash symptom was broken RX data and line overflow; running the latest STM32 USART1 firmware resolved it.
- ESP32 structured parsing of `TEL` fields (`state`, `last_seq`, `vx_mmps`, `w_mradps`, `err`) passed on 2026-07-18 with ESP-IDF build/flash and the real STM32 USART1 link.
- ESP32 scripted `CMD before ARM -> ARM -> valid CMD -> invalid CMD -> DISARM` sequence passed on 2026-07-20.
- STM32 returned the expected `NOT_ARMED`, command `ACK`, `OUT_OF_RANGE`, and `DISARM` responses through the ESP32 bridge.
- A one-shot valid CMD produced `vx=50`, then STM32 timeout returned `vx=0`, `w=0` after about 300 ms while remaining `ARMED` until explicit `DISARM`.
- ESP32-STM32 board-only UART bridge MVP is complete.
- STM32 motor-output uses `PB6/TIM4_CH1 -> PWM1`, `PC8 -> DIR1`, `PB7/TIM4_CH2 -> PWM2`, `PC9 -> DIR2` with common GND for the bench mapping.
- STM32 pin-only DMM and MDD10A powered/no-motor static LED sequence passed on 2026-07-26. An initial two-channel PWM/DIR swap was diagnosed from the LED pattern, corrected, and the full sequence was repeated successfully.
- The 2026-07-26 MDD10A power check measured battery 12.36 V and driver input 12.35 V with the motor disconnected and no abnormal heat, smell, noise, or fuse behavior.
- The temporary 10% raw output test was disabled again with `MOTOR_OUTPUT_PIN_TEST_ENABLED 0U`; all MDD10A output LEDs remained off after rebuild/flash.
- Motor-output verification remains `PARTIAL`: actual 20 kHz/10% waveform and active timeout/DISARM/fault output zero have not been instrumented or physically exercised. The current source order is `PWM zero -> 1 ms wait -> DIR write -> immediate PWM restore`; intended post-DIR settle must be corrected before active motor use.
- Two available encoder motors are WHEELTEC `MG540P30_12V`; use bench IDs `MG540-A` and `MG540-B` until physical vehicle left/right assignment is known.
- With the encoder PCB/magnet face toward the viewer and connector at the top, the six connector pads are left-to-right: motor+, encoder GND, encoder B, encoder A, encoder 5 V, motor-.
- XL4015 #2 encoder rail measured 5.06 V before MG540-A and 5.03 V connected; MG540-B connected rail also measured 5.03 V.
- MG540-A raw encoder A/B can idle near 0 V or 5 V depending on shaft position; raw encoder outputs must not be connected directly to STM32.
- A 15 kΩ signal-to-GND load produced exact-recorded HIGH values of 2.96~2.98 V on MG540-A A and MG540-B A/B; MG540-A B behaved similarly but its exact value was not recorded. This load is required for the first limited STM32 hand-rotation count test.
- Loaded measurements are consistent with an approximately 10.3~10.5 kΩ internal 5 V pull-up, but do not prove the exact open-collector/open-drain topology.
- Encoder LOW voltage, pulse shape, A/B phase, count, direction sign and CPR are not yet verified. `PB4/PB5 TIM3` is the first hand-count candidate; `PA0/PA1 TIM5` is the second.
- A roughly 174 x 209 mm adapter plate Draft was created from the tracked-chassis hole-pattern drawing on 2026-07-23.
- A 150 x 100 mm, 55 x 37 universal PCB carries the NUCLEO-F446RE, ESP32-S3, and GY-BNO085 in the Draft assembly.
- XL4015 x2 and MDD10A are placed in the upper power area; ESP32 stays horizontal for USB access and the IMU stays near the vehicle center.
- The CAD checkpoint is preserved under the displayed Onshape Version name `dapter-layout_draft01_2026-07-23`; the intended name starts with `adapter-`.
- Rev A 2D manufacturing baseline is 174 x 208.93379 mm with nominal 3.3 mm small mounting holes; the first fabrication candidate is acrylic 3T.
- The A4 1:1 print was physically compared with the chassis and recorded as `USER-CONFIRMED PASS`.
- The final Multimaker PDF passed a one-page, 39-vector-path, zero-raster, zero-text and source-scale comparison.
- The Multimaker order is not submitted because its WordPress server could not create or write `wp-content/uploads/2026/07`.
- The original chassis input file is preserved at `08_Mechanical_Design/source/chassis/R3_High_Config_Version_Tracked_Vehicle_Hole_Pattern_Drawing.dwg`; verify its SHA-256 against the source README before a Rev B rebase.
- Red reference-instance badges remain in the 3D Assembly Draft, but they are outside the user-approved Rev A 2D order scope; fabricated-plate fit remains `NOT TESTED`.

## Open Decisions

Ask the user or verify from hardware only for these:

- Exact DC motor to use first: MG540, JGB37-520, or another available motor
- Vehicle left/right assignment for MDD10A channel 1/2
- Physical confirmation and final release decision for the configured 20 kHz PWM
- Final CAN transceiver model
- Final USB-CAN adapter model
- Battery voltage divider resistor values
- Encoder counts-per-revolution, count direction and vehicle left/right assignment
- Actual fuse rating after current measurement
- Whether a separate power gate, brake, or emergency-stop circuit will be added
- PC-first UART path: ST-LINK VCP USART2 only, or also external USB-UART
- UART auto-disarm delay after timeout-zero-output state
- UART maximum application frame length and ring buffer size
- UART unknown frame type handling: return `ERR,code=UNKNOWN_TYPE` or ignore
- Whether checksum/CRC stays deferred until Wi-Fi forwarding
- Acrylic color and cast/extruded material choice
- Vendor kerf compensation, minimum hole capability, and manufacturing tolerance
- Mounting screw, nut, washer, and insulating-spacer specifications
- Vehicle-forward direction and CAD coordinate origin for the manufacturing drawing

## Next Concrete Actions

1. Start every new session with `git status --short Projects/Tracked_Mobile_Robot`.
2. Read `docs/progress/2026-07-26_progress.md` and `02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md` before continuing hardware validation.
3. Preserve the validated UART baseline: ESP32 `GPIO17 TX` / `GPIO18 RX`, STM32 `PA10 RX` / `PA9 TX`, common GND, 115200 8N1.
4. Preserve the completed UART bridge baseline and 2026-07-20 screenshot/raw log evidence.
5. Read `08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md` before continuing the order.
6. Contact Multimaker about the server upload error and request KakaoTalk or email file submission.
7. Confirm acrylic 3T material details, kerf, minimum hole capability, tolerance, total quote, and order ID.
8. After delivery, run `02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md` before powered assembly.
9. Read the refreshed V-model roadmap and project-wide verification matrix while the plate order is pending.
10. Preserve the bench-confirmed motor signal mapping and keep `MOTOR_OUTPUT_PIN_TEST_ENABLED 0U` outside an explicit test session.
11. Preserve the 2026-07-26 encoder loaded-voltage evidence; raw A/B direct STM32 connection is prohibited.
12. Configure `PB4/PB5 TIM3` for the first bench encoder and verify hand-rotation count/sign with 15 kΩ signal-to-GND on each channel, common GND and no motor power.
13. After TIM3 passes, repeat the limited hand-count test on `PA0/PA1 TIM5` for the second channel.
14. Before active motor use, correct the current `PWM zero -> 1 ms wait -> DIR -> PWM` code to provide the intended post-DIR settle, then measure actual PWM frequency/duty and timing when equipment is available.
15. Connect the validated UART command state to the 10%-limited motor-output interface.
16. With no motor connected, verify active timeout, DISARM and fault paths at the actual PWM pins and MDD10A LEDs.
17. Continue with board power/back-power, fabricated plate fit and the first lifted/no-load motor only after their safety gates pass.
