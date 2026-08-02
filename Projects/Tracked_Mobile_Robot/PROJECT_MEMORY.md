# Tracked Mobile Robot Project Memory

This file stores stable project facts so future work does not repeat the same questions.

Last updated: 2026-08-03

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
| Encoder channel 1 A/B, motor-off bench-confirmed | PB4 / PB5, TIM3 |
| Encoder channel 2 A/B, motor-off bench-confirmed | PA0 / PA1, TIM5 |
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
- `09_Electrical_Design/README.md`: RevA functional wiring scope, verified/TBD boundary and source/evidence index
- `09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_sch`: current KiCad schematic source
- `09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/reports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt`: dated ERC 0/0 evidence
- `09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/exports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_draft.pdf`: RevA human-review export
- `docs/progress/2026-08-03_progress.md`: latest progress note for logic-analyzer PWM/direction timing evidence, safe-source restoration and remaining safety gates
- `03_Firmware/tests/test_firmware_contract.py`, `README.md`: STM32/ESP32 pin, timer, UART, encoder sign and default-off safety contract preflight
- `03_Firmware/tools/Build-Firmware.ps1`, `README.md`: repository build trees를 건드리지 않는 isolated STM32/ESP32 build workflow
- `assets/logs/firmware_build/2026-07-30_laptop_firmware_preflight.md`: contract test, isolated clean-build result, artifact hashes and laptop-only evidence boundary
- `02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md`: logic-analyzer channel map and exact PWM/direction/shutdown timing procedure
- `03_Firmware/stm32_uart_mvp/Core/Inc/encoder_speed.h`, `Core/Src/encoder_speed.c`: TIM3/TIM5 modular delta, int64 accumulation and counts/s module
- `assets/logs/encoder/2026-07-29_encoder_speed_stationary_pass.txt`: stationary dual-encoder speed-log evidence
- `assets/logs/encoder/2026-07-29_dual_encoder_speed_hand_rotation_pass.txt`: dynamic dual hand-rotation delta/counts/s evidence
- `assets/logs/encoder/2026-07-29_dual_encoder_cps_uart_telemetry_verification.md`: STM32 production TEL -> ESP32 dual-CPS end-to-end verification summary
- `assets/logs/encoder/2026-07-29_dual_encoder_cps_tel_cw_pass.txt`, `2026-07-29_dual_encoder_cps_tel_ccw_pass.txt`: independent clockwise/counter-clockwise raw TEL evidence
- `assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md`: direction-by-direction 50-revolution calibration and mRPM audit summary
- `assets/logs/encoder/2026-07-30_dual_encoder_millirpm_hand_rotation_pass.txt`: dual hand-rotation CPS/mRPM raw evidence
- `assets/logs/encoder/2026-07-30_vehicle_frame_encoder_sign_verification.md`: A=right/TIM5, B=left/TIM3 and forward-positive production sign record
- `assets/logs/motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md`: motor-disconnected software fault output-zero/latch DMM and operator record
- `docs/progress/2026-07-28_progress.md`: KiCad RevA functional wiring baseline progress note
- `docs/progress/2026-07-27_progress.md`: TIM5 configuration and TIM3/TIM5 dual motor-off independent hand-count validation
- `assets/logs/encoder/README.md`: encoder bench-log conditions, separately reported one-revolution results and remaining limitations
- `docs/progress/2026-07-24_progress.md`: Rev A manufacturing files, 1:1/vector validation, and vendor upload blocker
- `docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md`: refreshed V-model gate roadmap and current execution order
- `docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`: project-wide requirement, design, test, evidence, and result traceability
- `docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`: NC hardware motor-energy cut, auxiliary sense, latch/reset requirements and staged E-stop verification
- `01_System_Architecture/21_Physical_EStop_Architecture_ko.md`: two-path Physical E-stop architecture and component-selection boundary
- `docs/progress/2026-07-23_progress.md`: adapter plate Draft, electronics placement, and Onshape Version
- `docs/progress/2026-07-20_progress.md`: ESP32 scripted safety sequence, timeout-zero, and bridge MVP PASS
- `docs/handoff/README.md`: handoff folder index and reading order
- `docs/handoff/NEXT_SESSION_START_PROMPT.md`: prompt to paste into a new Codex session
- `docs/handoff/2026-07-28_kicad_reva_wiring_handoff.md`: latest wiring baseline, safety boundary and next firmware/hardware gate
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
- ESP32 structured parsing of production `left_cps/right_cps` passed on 2026-07-29 with real STM32 USART1 telemetry and independent dual-encoder clockwise/counter-clockwise hand rotation.
- ESP32 scripted `CMD before ARM -> ARM -> valid CMD -> invalid CMD -> DISARM` sequence passed on 2026-07-20.
- STM32 returned the expected `NOT_ARMED`, command `ACK`, `OUT_OF_RANGE`, and `DISARM` responses through the ESP32 bridge.
- A one-shot valid CMD produced `vx=50`, then STM32 timeout returned `vx=0`, `w=0` after about 300 ms while remaining `ARMED` until explicit `DISARM`.
- The 2026-07-20 historical ESP32-STM32 board-only UART bridge baseline is complete. The current strict-parser release still requires startup-handshake and malformed-frame board regression.
- On 2026-07-30, ESP32 automatic boot traffic was disabled by default with `BRIDGE_SCRIPTED_TEST_ENABLED 0U`. The 2026-07-20 scripted sequence remains historical controlled-bench evidence, not normal boot behavior.
- The STM32 CubeMX `.ioc` init ordering explicitly retains `MX_TIM5_Init` so TIM5 encoder initialization is not silently lost after regeneration.
- Twelve static firmware safety contract tests passed, followed by isolated clean STM32 Debug and ESP32-S3 builds. This laptop-only gate did not flash or run either board.
- STM32 motor-output uses `PB6/TIM4_CH1 -> PWM1`, `PC8 -> DIR1`, `PB7/TIM4_CH2 -> PWM2`, `PC9 -> DIR2` with common GND for the bench mapping.
- STM32 pin-only DMM and MDD10A powered/no-motor static LED sequence passed on 2026-07-26. An initial two-channel PWM/DIR swap was diagnosed from the LED pattern, corrected, and the full sequence was repeated successfully.
- The 2026-07-26 MDD10A power check measured battery 12.36 V and driver input 12.35 V with the motor disconnected and no abnormal heat, smell, noise, or fuse behavior.
- The temporary 10% raw output test was disabled again with `MOTOR_OUTPUT_PIN_TEST_ENABLED 0U`; all MDD10A output LEDs remained off after rebuild/flash.
- Motor-output direction logic now uses `PWM zero -> 1 ms PWM-zero settle -> DIR write -> 1 ms post-DIR settle -> PWM restore`. The 2026-07-29 powered/no-motor 6-step MDD10A LED regression passed. A temporary default-off 10% UART hook also produced active M1A/M2A indication and both command timeout and a separate active `DISARM` made the output LEDs all-off. The hook was restored to `0U`, both boards were rebuilt/flashed and the default script remained all-off.
- On 2026-07-30 a temporary dual-channel 10% button hook injected `Error_Handler()` after M1A/M2A became active. All motor LEDs turned off, PB6/PB7/PC8/PC9 measured 0 V to STM32 GND, and further B1 input could not reactivate output before reset. Both button-test macros were restored to `0U` and B1 no-output regression passed.
- On 2026-08-03 the motor-disconnected B1 six-step logic-analyzer capture measured both PWM channels at `49.75 us = 20.1005 kHz`, high time `5.00 us` and duty about `10.05%`. Direction-change PWM-zero intervals were channel 1 pre/post `1.994/2.03875 ms` and channel 2 pre/post `1.54725/about 2.040 ms`, so the waveform/direction timing sub-gate is `PASS`.
- Overall motor-output verification remains `PARTIAL`. The sampled initial inactive interval is scoped evidence only because it has no external reset marker. Active DISARM, command-timeout and software-fault event-to-PWM-zero latency, safe-image board reflash plus reset-marker boot regression, Physical E-stop and actual motor stop remain unverified.
- Two available encoder motors are WHEELTEC `MG540P30_12V`; the encoder-side mapping is MG540-A/motor A = vehicle right/TIM5 and MG540-B/motor B = vehicle left/TIM3. MDD10A powered channel 1/2 to physical side remains TBD.
- With the encoder PCB/magnet face toward the viewer and connector at the top, the six connector pads are left-to-right: motor+, encoder GND, encoder B, encoder A, encoder 5 V, motor-.
- XL4015 #2 encoder rail measured 5.06 V before MG540-A and 5.03 V connected; MG540-B connected rail also measured 5.03 V.
- MG540-A raw encoder A/B can idle near 0 V or 5 V depending on shaft position; raw encoder outputs must not be connected directly to STM32.
- The final motor-off input conditioning is per channel: encoder A/B -> 1 kΩ series -> STM32 input node, with 15 kΩ from that MCU-side node to common GND. STM32 GND, encoder GND and XL4015 OUT- are common.
- With PB4/PB5 disconnected, conditioned HIGH measured 3.06 V on MG540-A A/B and 3.06~3.07 V on MG540-B A/B.
- Loaded measurements are consistent with an approximately 10.3~10.5 kΩ internal 5 V pull-up, but do not prove the exact open-collector/open-drain topology.
- `PB4/PB5 TIM3` encoder mode passed the motor-off hand-rotation test with both motors connected sequentially. Output-shaft-end view raw signs were CW positive and CCW negative.
- Separately reported one-output-shaft-turn results were MG540-A `+1560 / -1560~-1570` and MG540-B `+1562 / -1560`; use `1560 counts/output rev` only as a provisional scale.
- Exact 360-degree hand rotation was not mechanically indexed. Manual start/end alignment and gearbox backlash limit single-revolution accuracy; final calibration requires a marked reference and a repeated multi-revolution average.
- On 2026-07-30, the marked output shaft was hand-rotated 50 revolutions per direction. Operator-reported absolute totals were MG540-A `77,998 / 78,001` and MG540-B `78,000 / 78,000`, yielding `1559.96~1560.02 counts/output rev`. This supersedes the provisional-scale gap and fixes the current firmware constant at `1560 counts/output rev`.
- The 2026-07-26 preserved raw log contains only a partial bidirectional capture assigned to MG540-A, not the full-turn results or MG540-B trace.
- On 2026-07-27, both encoders were connected concurrently to `PB4/PB5 TIM3` and `PA0/PA1 TIM5`. The dual raw log shows ENC5 `0 -> +1557 -> -6` while ENC3 stayed `0`, then ENC3 `0 -> +1561 -> +7` while ENC5 stayed `-6`. Motor ID to ENC3/ENC5 mapping was not recorded, so keep timer names until physical left/right assignment.
- TIM3/TIM5 dual motor-off independent count/sign is `PASS`.
- On 2026-07-29, `encoder_speed` implemented TIM3 16-bit and TIM5 32-bit modular delta, int64 accumulated count and nominal 100 ms counts/s. Synthetic forward/reverse wrap cases, stationary logging and dual hand-rotation logging passed.
- A later 2026-07-29 operator-identified end-to-end retest established MG540-A -> TIM5 -> `right_cps` and MG540-B -> TIM3 -> `left_cps`; both were clockwise positive and counter-clockwise negative in output-shaft-end view. These are logical telemetry fields, not final vehicle-side assignments.
- On 2026-07-30, signed CPS-to-mRPM conversion, invalid-input/range checks and boot self-test were added. `ENC_SELF_TEST,wrap=PASS,millirpm=PASS` and a 305-row dual hand-rotation log passed with 0/610 formula mismatch, direction mismatch 0 and stop-to-zero.
- On 2026-07-30 the encoder-side installed mapping was confirmed as A=right/TIM5 and B=left/TIM3. Right/A clockwise and left/B counter-clockwise are physical forward, so production TIM3/left CPS is inverted while TIM5/right keeps its raw sign. Operator manual forward-sign regression passed; powered actuator channel mapping did not form part of this test.
- USART2 remains a parallel bench logger and carries raw-sign mRPM diagnostics. CPS is fed into production UART `TEL` and parsed by ESP32; the production contract remains forward-positive `left_cps/right_cps`. Powered-motor noise, exact LOW, A/B phase timing, external-tachometer RPM accuracy and wheel-speed scale remain unverified.
- On 2026-07-28, a KiCad 10.0 `RevA DRAFT` functional wiring schematic captured the battery/fuse/switch distribution, MDD10A power/logic/output, dual encoder 1 kΩ + 15 kΩ conditioning, XL4015 #2 encoder rail and STM32–ESP32 UART.
- XL4015 #1 output remains a candidate and is not connected to STM32 or ESP32 until its destination and USB backfeed policy are verified.
- The dated ERC report records 0 errors and 0 warnings under its listed ignored-check policy. This does not verify physical wiring, current capacity, noise, footprints, perfboard layout or manufacturing readiness.
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
- External-tachometer RPM accuracy and wheel-speed scale; the current firmware output-shaft count constant is 1560
- Actual fuse rating after current measurement
- XL4015 #1 final 5 V destination and STM32/ESP32 USB backfeed policy
- BNO085 power and I2C final wiring
- Physical connector, footprint, perfboard and harness release
- Whether a separate power gate, brake, or emergency-stop circuit will be added
- PC-first UART path: ST-LINK VCP USART2 only, or also external USB-UART
- UART auto-disarm delay after timeout-zero-output state
- UART maximum application frame length and ring buffer size
- UART unknown frame type handling: return `ERR,code=UNKNOWN_TYPE` or ignore
- Whether checksum/CRC stays deferred until Wi-Fi forwarding
- Acrylic color and cast/extruded material choice
- Vendor kerf compensation, minimum hole capability, and manufacturing tolerance
- Mounting screw, nut, washer, and insulating-spacer specifications
- CAD coordinate origin for the manufacturing drawing

## Next Concrete Actions

1. Start every new session with `git status --short Projects/Tracked_Mobile_Robot`.
2. Read `docs/progress/2026-08-03_progress.md`, `docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md` and `02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md` before continuing.
3. Preserve the KiCad `RevA DRAFT` verified/TBD boundary. Do not connect XL4015 #1 candidate output to either MCU before the USB backfeed policy is decided.
4. Preserve the validated UART baseline: ESP32 `GPIO17 TX` / `GPIO18 RX`, STM32 `PA10 RX` / `PA9 TX`, common GND, 115200 8N1.
5. Preserve the encoder conditioning, TIM3/TIM5 firmware, modular-delta module and dated raw-log evidence; raw A/B direct STM32 connection is prohibited.
6. Preserve the 2026-07-29 timeout/DISARM and 2026-07-30 software fault output-zero/latch functional PASS evidence. Do not treat them as exact PWM transition/shutdown-latency, physical E-stop or motor-stop proof. Keep both button-test macros and the UART output hook at `0U` by default.
7. Keep `BRIDGE_SCRIPTED_TEST_ENABLED 0U` during normal operation. After CubeMX regeneration, run the firmware contract tests and isolated build before flashing, and confirm that TIM5 init remains present.
8. Preserve A=right/TIM5, B=left/TIM3 and forward-positive production `left_cps/right_cps` as the encoder-side vehicle mapping regression baseline; USART2 `ENC3/ENC5` remains raw-sign diagnostics. Verify MDD10A powered channel-to-side mapping separately.
9. Preserve the 50-revolution `1560 counts/output rev` evidence and mRPM regression baseline; separately validate absolute RPM with an external tachometer and measure the sprocket/track travel scale before wheel-speed conversion.
10. Preserve the 2026-08-03 actual `20.1005 kHz`/about `10.05%` PWM and direction pre/post zero `>= 1 ms` evidence as a passed sub-gate; do not repeat it unless firmware, timer configuration or wiring changes.
11. Before applying MDD10A or motor power in the next session, confirm the four test-hook macros are `0U` and flash/run the current STM32 safe source to remove the possibility that the temporary B1 six-step image remains on the board. This is a bench-safety prerequisite, not the final release regression.
12. With the motor disconnected and output limited to 10%, capture active `DISARM` frame-completion to PB6/PB7 last-active-edge shutdown latency.
13. Under the same limit, capture last valid CMD completion through configured command timeout to PB6/PB7 last-active-edge shutdown latency.
14. Capture software-fault event-to-PWM-zero latency with a dedicated marker or debounced event, recording button debounce separately from firmware latency.
15. Restore STM32 `MOTOR_OUTPUT_PIN_TEST_ENABLED`, `MOTOR_FAULT_INJECTION_TEST_ENABLED`, `UART_MVP_OUTPUT_TEST_ENABLED` and ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED` to `0U`. Run contract tests and clean builds, reflash both safe images, and capture PB6/PC8/PB7/PC9 boot no-output with an external reset reference marker.
16. Close board power/back-power prerequisites, then execute `T-ESTOP-001~006` from the Physical E-stop architecture and verification plan: NC hardware motor-energy cut and 3.3 V auxiliary sense remain separate, release never auto-rearms, and continuity/sense/latch/reset-reject/no-auto-restart/motor-disconnected timing must pass.
17. Only after actions 12~16 pass, run the first lifted/no-load actual motor test at 5~10% and record current, heat, smell, noise, timeout/DISARM actual stop and powered encoder false counts/noise.
18. Perform a schematic-to-hardware continuity review before permanent perfboard or harness construction.
19. Read `08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md` before continuing the plate order.
20. Contact Multimaker about the server upload error and confirm material, kerf, minimum hole capability, tolerance, total quote and order ID.
20. After delivery, run `02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md` before powered assembly.
