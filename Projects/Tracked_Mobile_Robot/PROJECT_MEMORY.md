# Tracked Mobile Robot Project Memory

This file stores stable project facts so future work does not repeat the same questions.

Last updated: 2026-08-12

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
- Each MDD10A control signal has a required external reset-safe pull-down: `PC8/DIR1`,
  `PB6/PWM1`, `PC9/DIR2`, `PB7/PWM2` each use `10 kΩ` to GND. The breadboard
  reset capture passed; RevB/permanent wiring and continuity remain required.
- UART/USB serial comes before CAN for first bring-up.
- CAN is still a required later phase.
- FreeRTOS comes after HAL bare-metal drivetrain behavior is validated.
- LL Driver migration comes after a known-good HAL baseline.
- ROS 2 bridge comes after low-level drivetrain safety, timeout, and odometry basics are validated.
- Physical E-stop RevB uses an MCU-independent `S0-A NC -> K1 DC power relay` control path; K1 opens the MDD10A `POWER+` feed when de-energized.
- Physical E-stop monitoring uses a separate `5 V -> S0-B NC -> optocoupler LED` loop and 3.3 V pull-up/transistor output to `ESTOP_SENSE`. It does not prove the K1 main contact actually opened.
- E-stop release never restores motion authority or K1 motor rail by itself. Step 7 corrected the three-wire path to `F2 -> S0-A NC -> [S2 momentary NO OR K2-HOLD-NO] -> K2 coil`, with a second K2 NO contact enabling K1 coil. A K1 high-current pole is not used below its official minimum switching load.
- Step 7 preferred candidates are Omron `A22NE-M-PD02-N` for S0, Schneider `ZB5AA3 + ZB5AZ009 + ZBE1016` low-power assembly for S2, Panasonic `TX2-12V` for K2 and Vishay `VO617A-3` for S0-B conditioning. They remain conditional until minimum-load, received-part and bench gates close.
- K1/F1/main wire/connectors remain blocked by missing MG540P30_12V motor current data. F2 is only a preliminary 0.5 A time-delay candidate; coil clamps and ADC values remain open.
- Step 6 fixed the functional circuit/net architecture, connector/test-point partition and backfeed boundary in `25_Physical_EStop_RevB_Circuit_Architecture_ko.md`.
- MVP K1 actual-off evidence is direct downstream continuity/voltage measurement; K2/control state alone is not proof. Protected PA4/PB0 dual-rail sensing remains a post-MVP automatic diagnostic option.
- Step 6 target pin is PC7 for MVP `ESTOP_SENSE`; PA4 upstream `VBAT_PROTECTED_SENSE` and PB0 downstream `MOTOR_VBAT_SAFE_SENSE` are post-MVP candidates. None is configured or bench-tested.
- Step 5 baselined `REQ-ESTOP-001~020`: 15 MUST, 5 SHOULD. `REQ-ESTOP-012~015` and precision `T-ESTOP-006` are post-MVP; MVP-linked TBR items still close before their powered-test gates.

## Fixed Engineering Process Decisions

- Project planning and verification use a tailored systems-engineering lifecycle and lightweight Vee traceability.
- `docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md` is the canonical Engineering Basis ID and standards-claim boundary.
- Work completed before 2026-08-10 is treated as `RETROSPECTIVE ALIGNMENT` unless its original decision record cites the source. New requirements, ADRs and tests use the selected Basis ID as an `ADOPTED FORWARD BASIS` before the decision.
- Basis ID linkage does not claim full standard conformance, certification, ISO 13849 PL, SIL, EMC/IP rating or MISRA compliance.
- New requirements and major design decisions should connect at least one Basis ID and one Test ID.

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
| K1 upstream rail ADC candidate | PA4, ADC12_IN4 -> `VBAT_PROTECTED_SENSE` |
| K1 downstream rail ADC candidate | PB0, ADC12_IN8 -> `MOTOR_VBAT_SAFE_SENSE` |
| Physical E-stop sense candidate | PC7 GPIO/EXTI -> `ESTOP_SENSE` |
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

- `docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md`: Engineering Basis ID catalog, past/future application timing and standards-claim boundary
- `docs/progress/2026-08-10_progress.md`: Engineering Basis adoption and final MVP matrix linkage record
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
- `docs/progress/2026-08-12_progress.md`: current UART Gate C and motor-disconnected timeout/fault/reset-boot completion state, external `10 kΩ` pull-down decision and next power/E-stop gate
- `docs/verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md`: current T-BRIDGE-008A/008B report, artifact metadata and evidence boundaries
- `docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`: command-timeout, software-fault latch, reset FAIL/root cause, `10 kΩ` pull-down PASS and final safe restore report
- `docs/handoff/2026-08-13_power_and_physical_estop_session_ko.md`: current continuation source for RevB pull-down, board power/back-power and Physical E-stop work
- `docs/handoff/2026-08-12_focused_uart_gate_c_session_plan_ko.md`: completed historical Gate C execution runbook; not the current next-work instruction
- `docs/progress/2026-08-11_progress.md`: historical partial-frame-name checkpoint before Gate C completion
- `docs/verification/14_ESP32_Partial_Frame_Name_ACK_Recovery_Test_Report_2026-08-11_ko.md`: historical partial-frame-name report
- `docs/progress/2026-08-07_progress.md`: historical trailing-comma and required-`seq` uint32-overflow subvector PASS checkpoint
- `docs/handoff/2026-08-06_safe_uart_baseline_handoff.md`: historical pre-partial-name continuation checkpoint
- `docs/progress/2026-08-06_progress.md`: historical duplicate-seq subvector PASS and post-test 14.42 s safe UART checkpoint
- `docs/progress/2026-08-04_progress.md`: historical Gate A/B, wrong-ACK and active DISARM 23.50 us checkpoint
- `docs/handoff/2026-08-04_uart_runtime_and_active_disarm_handoff.md`: historical controlled-test handoff superseded by the 2026-08-06 handoff
- `docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`: Gate A exact startup, Gate B bounded loss/stale response/reset recovery and evidence limits
- `docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md`: active DISARM UART RX end to PWM last-edge MCU-pin first baseline
- `docs/verification/11_ESP32_Duplicate_Required_Seq_ACK_Recovery_Test_Report_2026-08-06_ko.md`: T-BRIDGE-008A duplicate required `seq` ACK rejection/recovery and post-test safe restore report
- `docs/verification/12_ESP32_Trailing_Comma_ACK_Recovery_Test_Report_2026-08-07_ko.md`: T-BRIDGE-008A trailing-comma ACK rejection/recovery, current safe restore, full-build `0/0` and artifact reproduction report
- `docs/verification/13_ESP32_Required_Seq_Uint32_Overflow_ACK_Recovery_Test_Report_2026-08-07_ko.md`: T-BRIDGE-008A required-`seq` uint32 overflow ACK rejection/recovery and post-test safe restore report
- `assets/logs/firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt`: retained post-Clean full-build console proving 31-object recompilation, link and `0 errors / 0 warnings`
- `assets/logs/firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md`: controlled/safe artifact hashes, builds and session-observed flash evidence for the overflow subvector
- `docs/progress/2026-08-03_progress.md`: historical logic-analyzer PWM/direction, fixed-delay normal sequence and response-gated source/build checkpoint
- `docs/handoff/2026-08-03_uart_response_gated_startup_implementation_handoff.md`: historical implementation checkpoint, superseded by 2026-08-04 handoff
- `docs/handoff/2026-08-03_uart_strict_parser_regression_handoff.md`: response-gated implementation 이전의 historical strict-parser baseline
- `docs/verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md`: current strict-parser controlled normal-sequence result and scope limit
- `assets/logs/esp32_uart_bridge/2026-08-03_strict_parser_normal_sequence_pass.txt`: raw ESP32 monitor evidence for the 2026-08-03 controlled normal sequence
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
- `docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`: K1 relay motor-energy cut, auxiliary sense, latch/reset requirements and staged E-stop verification
- `01_System_Architecture/21_Physical_EStop_Architecture_ko.md`: Physical E-stop safety goal, RevA/RevB boundary, K1 relay energy path and independent sense path
- `01_System_Architecture/22_Physical_EStop_Hazard_Analysis_ko.md`: 12-hazard initial screening, foreseeable misuse, risk-reduction mapping and FMEA inputs
- `01_System_Architecture/23_Physical_EStop_FMEA_ko.md`: 23 failure modes, action priorities, three-wire re-enable and downstream rail-sense decisions
- `01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md`: 20 shall/should requirements, acceptance criteria, TBR registry and requirement-to-test mapping
- `01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md`: MVP K1 high-side cut, three-wire re-enable, S0-B sense, connector/test-point and backfeed circuit baseline; dual-rail sense is post-MVP
- `01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md`: S0/S2/K2/opto candidates, official minimum-load review, K1/F1/main-current blockers and Step 7 closure gates
- `docs/progress/2026-07-23_progress.md`: adapter plate Draft, electronics placement, and Onshape Version
- `docs/progress/2026-07-20_progress.md`: ESP32 scripted safety sequence, timeout-zero, and bridge MVP PASS
- `docs/handoff/README.md`: handoff folder index and reading order
- `docs/handoff/NEXT_SESSION_START_PROMPT.md`: prompt to paste into a new Codex session
- `docs/handoff/2026-07-28_kicad_reva_wiring_handoff.md`: latest wiring baseline, safety boundary and next firmware/hardware gate
- `docs/handoff/2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md`: historical UART bridge closeout; current continuation is `NEXT_SESSION_START_PROMPT.md` plus `2026-08-06_safe_uart_baseline_handoff.md`

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
- The 2026-07-20 historical ESP32-STM32 board-only UART bridge baseline is complete. On 2026-08-03, a controlled `500 ms settle -> LF -> 100 ms -> PING` preamble and the current strict-parser normal safety sequence passed again, including PING/PONG, NOT_ARMED, ARM/valid CMD, timeout-zero, OUT_OF_RANGE and final DISARMED.
- ESP32 source now contains a non-blocking response-gated startup state machine: `500 ms settle -> LF boundary sync -> per-boot DISARM/matching ACK -> next-seq PING/matching PONG -> READY`, with a 500 ms response timeout, at most three attempts per response stage and `FAILED` fail-closed state. Startup sequence is seeded with `esp_random()` on every boot; responses latch only in the matching wait state. ACK `seq/type` and PONG `seq` are parsed and matched explicitly, and scripted ARM/CMD steps are gated on `READY`.
- TX is emitted as one newline-terminated write and any TX or startup RX-flush failure enters `FAILED`. Duplicate required fields, integer overflow, trailing commas and non-exact frame prefixes are rejected. RX overflow or embedded control/CR marks the whole frame invalid and discards bytes through the next LF, preventing an overflow tail from being reparsed as a command.
- The 2026-08-03 safe-source contract passed `15/15` and ESP32-S3 build passed with binary `0x2b210`, `83%` partition free. Actual response-gated board logs then passed Gate A exact ACK/PONG/READY, Gate B DISARM-ACK/PONG loss bounded failure, stale ACK/PONG sequence rejection and controlled reset/new-startup recovery. The reset segment does not contain the preceding failure, so post-failure session linkage remains operator-labeled. A 2026-08-04 controlled run also passed matching-seq/wrong-ACK-type rejection, exact 500 ms same-seq DISARM retry and exact-response-only READY. On 2026-08-06~12 T-BRIDGE-008A passed duplicate-required-`seq`, trailing-comma, required-`seq` uint32-overflow, partial-frame-name, embedded-CR, control-byte and overlong-line rejection/recovery. On 2026-08-12 T-BRIDGE-008B also passed eight malformed/unknown STM32 command rejections, TEL 200/200 safe and final matching PING/PONG recovery. Gate C required runtime scope is closed; the strict-parser release remains `PARTIAL` only for exact artifact linkage, external cold-start marker and log-embedded physical setup provenance.
- The 2026-08-04 safe-image UART runtime behavior passed with about 11.24 s after READY and TEL 118/118 safe; the following wrong-ACK controlled run also passed and is historical evidence.
- On 2026-08-06 the wrong-ACK hook was restored to `0U`; every ESP32/STM32 test hook was `0U`. Firmware contract discovery passed `15/15`, and the user-observed STM32CubeIDE build reported `0 errors / 0 warnings`. That pre-008A historical ELF was `1,239,972 bytes` with SHA-256 `71EF2C275A5DD5CFAB34995D1CF33A76B4DC4593661842BD6E379D6DBEFACBAF`.
- The first final 2026-08-06 safe board log passed exact ACK/PONG/READY and then 11.35 s with TEL 120/120 `DISARMED/zero/error 0`, ARM/CMD 0 and parser/startup errors 0. It remains the pre-008A historical baseline.
- T-BRIDGE-008A duplicate-required-`seq` controlled runtime then passed: one malformed ACK parser rejection, no early gate opening, exactly 500 ms same-seq DISARM retry, first exact ACK count 1, matching PONG then READY, TEL 150/150 safe and ARM/CMD/failure 0. The controlled ELF SHA-256 was `9565A1405FF97BE75BC1D30F87DEBD1CE32ED05D8E16525D2205231AD74CCA61`, and the malformed ACK branch string was confirmed present before a verified flash.
- After that vector the duplicate hook and every other controlled hook were restored to `0U`. Contract discovery passed `15/15`; safe STM32 build and flash verify passed; the then-current `1,240,148-byte` ELF SHA-256 was `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`, with the controlled branch string absent. The post-test safe log passed exact startup without retry/parser errors, 14.42 s after READY, TEL 150/150 safe and ARM/CMD/failure 0. This remains the historical post-duplicate checkpoint.
- The trailing-comma controlled runtime then passed: one `RX malformed field list`, no early gate opening, exactly 500 ms same-seq DISARM retry, first exact ACK count 1, matching PONG then READY, TEL 150/150 safe and ARM/CMD/failure 0. Its retained controlled ELF is `1,240,348 bytes`, SHA-256 `5791C9B1E5A8F2ED942B8A8A0BDD8599C2A775EDB5D59022E60CE900C52B406E`.
- After the trailing-comma vector every controlled hook was restored to `0U`. Contract discovery passed `15/15`; restored artifacts were regenerated, the controlled string was absent from object/ELF/map/list, and safe flash verify passed. A later post-Clean full build recompiled all 31 objects, including `uart_mvp_protocol.c`, linked with `0 errors / 0 warnings` and reproduced every retained safe artifact hash. That historical `1,240,328-byte` ELF SHA-256 is `3526206C7E2043634029B15B7D41F9C80B136904FCA72FB46D8CA24F4119DEE4`. The safe log passed exact startup without warnings/retry/parser errors, 15.51 s after READY, TEL 160/160 safe and ARM/CMD/failure 0.
- The required-`seq` uint32-overflow controlled runtime then passed: one exact overflow ACK parse rejection, no early gate opening, exactly 500 ms same-seq DISARM retry, first exact ACK count 1, matching PONG then READY, post-READY TEL 140/140 safe and ARM/CMD/failure 0. Its retained controlled ELF is `1,240,520 bytes`, SHA-256 `747F32E3BDFBF0D4130E2F136145806AE88FF4F94BBC8948C7FFB554BE0A3701`.
- After the overflow vector every controlled hook was restored to `0U`. Contract discovery passed `15/15`; the restored protocol source recompiled and relinked with `0 errors / 0 warnings`, the controlled string was absent from object/ELF/map/list, and safe flash verify passed. That historical `1,240,504-byte` safe ELF SHA-256 is `244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`; its safe log passed exact startup, post-READY TEL 145/145 safe and ARM/CMD/failure 0.
- The 2026-08-11 partial-frame-name controlled runtime passed: `AC,...` was classified UNKNOWN once, no early gate opened, the same DISARM seq retried exactly 500 ms later, and only exact ACK/PONG opened READY. Visible TEL 165/165 and post-READY TEL 159/159 were safe. The controlled ELF was `1,240,712 bytes`, SHA-256 `FDEF89BFA9420D35BDACA582CD4C7CD19D7973F804BC39D312F7B4BF64A6B818`.
- After the partial-name vector all hooks were restored to `0U`; contract `15/15`, a full STM32 build `0 errors / 0 warnings`, partial controlled literal absence, NUCLEO-F446RE flash verify and safe runtime passed. That historical safe ELF was `1,240,692 bytes`, SHA-256 `3567C9266C2D46DD920C8DAD6DE29656EBBC0BA73AB35CF1D55CC9368EABF4CA`. Safe runtime had exact startup once, retry/parser error/unknown/failure 0, visible TEL 169/169 and post-READY TEL 164/164 safe over about 16.27 s, ARM/CMD 0. UART logs did not embed the ELF hash or physical metadata; no battery, MDD10A B+/B- or actual motor power was permitted for the then-remaining Gate C vectors.
- On 2026-08-12 the remaining T-BRIDGE-008A response vectors passed. Embedded CR and control byte `0x01` were each rejected once before an exact 500 ms same-seq retry; overlong line produced one RX overflow before a 510 ms same-seq retry. All three reached READY only after exact ACK/PONG and kept ARM/CMD at zero. The first embedded-CR attempt was invalid because the STM32 one-shot hook had already been consumed; it is retained as excluded evidence.
- On 2026-08-12 T-BRIDGE-008B passed all eight scripted STM32 malformed/unknown command vectors. Each produced the expected ERR, TEL 200/200 remained DISARMED/zero, accumulated `err=8` was expected, and final `PING,seq=9009` received matching PONG followed by 106 safe TEL over about 10.5 s.
- Final source has all ESP32 and STM32 controlled hooks `0U`; contract discovery passed `15/15`. The safe STM32 ELF is `1,241,204 bytes`, SHA-256 `46A80919B8ECE0521CBFA0861D74446F51904F7D9967517DCDC63118EA73B98A`. The safe ESP32 BIN is `176,656 bytes`, SHA-256 `4321B4BF2811590167EB7DCEF58CA84ABE5C0C7EEC67656E20D0EFD787A2724D`, with controlled 008B markers absent. Final safe runtime had exact startup once, retry/test/parser error/ARM/CMD/failure 0, visible TEL 128/128 and post-READY TEL 123/123 safe over about 12.2 s. Physical no-power was operator-confirmed but not log-embedded, and the raw UART log does not embed artifact hashes.
- The STM32 CubeMX `.ioc` init ordering explicitly retains `MX_TIM5_Init` so TIM5 encoder initialization is not silently lost after regeneration.
- Fifteen firmware preflight tests passed again after the 2026-08-04 safe-source restore. The suite combines source/configuration checks with host parser vectors; it does not replace target runtime or electrical evidence. Isolated clean build PASS likewise does not prove the restored images are running on either board.
- STM32 motor-output uses `PB6/TIM4_CH1 -> PWM1`, `PC8 -> DIR1`, `PB7/TIM4_CH2 -> PWM2`, `PC9 -> DIR2` with common GND for the bench mapping.
- STM32 pin-only DMM and MDD10A powered/no-motor static LED sequence passed on 2026-07-26. An initial two-channel PWM/DIR swap was diagnosed from the LED pattern, corrected, and the full sequence was repeated successfully.
- The 2026-07-26 MDD10A power check measured battery 12.36 V and driver input 12.35 V with the motor disconnected and no abnormal heat, smell, noise, or fuse behavior.
- The temporary 10% raw output test was disabled again with `MOTOR_OUTPUT_PIN_TEST_ENABLED 0U`; all MDD10A output LEDs remained off after rebuild/flash.
- Motor-output direction logic now uses `PWM zero -> 1 ms PWM-zero settle -> DIR write -> 1 ms post-DIR settle -> PWM restore`. The 2026-07-29 powered/no-motor 6-step MDD10A LED regression passed. A temporary default-off 10% UART hook also produced active M1A/M2A indication and both command timeout and a separate active `DISARM` made the output LEDs all-off. The hook was restored to `0U`, both boards were rebuilt/flashed and the default script remained all-off.
- On 2026-07-30 a temporary dual-channel 10% button hook injected `Error_Handler()` after M1A/M2A became active. All motor LEDs turned off, PB6/PB7/PC8/PC9 measured 0 V to STM32 GND, and further B1 input could not reactivate output before reset. Both button-test macros were restored to `0U` and B1 no-output regression passed.
- On 2026-08-03 the motor-disconnected B1 six-step logic-analyzer capture measured both PWM channels at `49.75 us = 20.1005 kHz`, high time `5.00 us` and duty about `10.05%`. Direction-change PWM-zero intervals were channel 1 pre/post `1.994/2.03875 ms` and channel 2 pre/post `1.54725/about 2.040 ms`, so the waveform/direction timing sub-gate is `PASS`.
- On 2026-08-04 the 4 MHz raw capture measured active DISARM final LF stop-bit end to both PWM last-active falling edges at `23.50 us`; PWM stopped `62.75 us` before ACK and did not restart for the remaining about 2.712088 s. This is an MCU-pin first baseline only.
- On 2026-08-12 the 300 ms command-timeout capture produced a UART-calibrated frame-end-to-last-PWM-edge value of about `299.690 ms`, followed by about `8.939 s` without reactivation. This is a scoped baseline that explicitly allows the 1 ms `HAL_GetTick()` phase and analyzer-clock tolerance.
- The 2026-08-12 software-fault capture proved expected-next-pulse suppression and about `2.052 s` no-reactivation latch. The last PWM fall was `5.25 us` before the PA5 marker because injection occurred during PWM LOW, so that value is not reported as fault latency.
- The first external-reset capture without pull-downs failed: all four motor control signals appeared HIGH for about `159 ms` during NRST LOW. After adding an external `10 kΩ` pull-down from each `PC8/PB6/PC9/PB7` signal to GND, a 5 s/20 M-sample retest observed zero transitions and zero HIGH samples on all four signals.
- Motor-output verification is now `PASS — motor-disconnected MCU-pin scope`. MDD10A power-stage timing, RevB/permanent pull-down continuity, Physical E-stop and actual motor stop remain unverified, so the overall drivetrain release is still `PARTIAL`.
- After the motor-output safety tests all controlled hooks were restored to `0U`; contract discovery passed `15/15`. The safe STM32 ELF was `1,241,208 bytes`, SHA-256 `3B80E7A6A465545A0324AA7CD83503C95E387DE203374548BCA368FDC7DA831B`; the safe ESP32 BIN was `176,656 bytes`, SHA-256 `8F46810367A370A080781A09E52B04F3DF348CF9F3430ABA536686DFFEF033C3`. Final runtime had exact DISARM ACK/PING/PONG/READY and post-READY TEL 155/155 safe over 15.4 s. Raw flash-console and embedded artifact identity remain missing provenance.
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

1. Start every new session with `git status --short -- Projects/Tracked_Mobile_Robot`.
2. Read `docs/progress/2026-08-10_progress.md` and `docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md` for the adopted process; use `docs/progress/2026-08-12_progress.md` plus verification reports 15 and 16 as the current UART/motor-output baseline.
3. Keep LiPo, MDD10A B+/B- and actual motor power disconnected. If both boards are USB-powered, never connect their 5 V/VBUS/VIN rails.
4. Preserve the all-hooks-`0U` current source, contract `15/15`, post-motor-safety safe STM32 ELF SHA-256 `3B80E7A6A465545A0324AA7CD83503C95E387DE203374548BCA368FDC7DA831B`, safe ESP32 BIN SHA-256 `8F46810367A370A080781A09E52B04F3DF348CF9F3430ABA536686DFFEF033C3` and 15.4 s/post-READY TEL 155 final UART regression. Exact linkage and log-embedded physical provenance remain pending.
5. Treat T-BRIDGE-008A/008B required runtime scope as complete and preserve report 15 plus all 2026-08-12 raw logs; do not repeat these controlled vectors unless firmware behavior changes.
6. Preserve Gate A/B, T-BRIDGE-007/008, active DISARM 23.50 us and report 16 timeout/fault/reset raw evidence; do not repeat unless firmware or wiring changes.
7. Add the four external `10 kΩ` pull-downs to RevB/permanent wiring and verify continuity before motor energy is enabled.
8. Preserve A=right/TIM5, B=left/TIM3, forward-positive CPS, `1560 counts/output rev`, 20.1005 kHz/about 10.05% PWM and direction settle evidence.
9. Close board power/back-power prerequisites and execute Physical E-stop MVP `T-ESTOP-001~005` before any actual motor test.
10. Only after all preceding safety gates pass, run lifted/no-load actual motor at 5~10%, record current/heat/smell/noise/powered encoder noise, then execute `T-ESTOP-007` actual-stop/no-auto-restart evidence.
11. Keep PA4/PB0 dual-rail plausibility, discrepancy fault injection and precision rail-transient `T-ESTOP-006` as a post-MVP diagnostic V-cycle.
12. Preserve the KiCad `RevA DRAFT` verified/TBD boundary and perform schematic-to-hardware continuity review before permanent wiring.
13. Read the adapter-plate preflight before order work, record vendor terms/order ID, and run fit check after delivery.
