# Tracked Mobile Robot Project Memory

This file stores stable project facts so future work does not repeat the same questions.

Last updated: 2026-08-28

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
| Adapter plate | 174 x 208.93379 mm PC 3T order candidate with the supplier minimum-hole response reflected in 8 holes changed to 3.0 mm. The user reported the fabricated custom PC plate received on 2026-08-26. Exact order-source identity, physical dimensions/hole pattern and chassis/module fit remain pending. |
| Electronics carrier | 150 x 100 mm universal PCB, 55 x 37 hole array |
| CAN controller | STM32 internal bxCAN |
| CAN transceiver | Not selected yet |
| USB-CAN adapter | Not selected yet |
| DC main switch | Available; fused switch path validated 2026-07-10 and MDD10A input check repeated 2026-07-26 |

## Fixed Architecture Decisions

- STM32 owns final motor output permission.
- ESP32, PC, CAN, and future ROS 2 can request motion but cannot bypass STM32 safety.
- ADR-015 fixes ESP32-S3 as the only Final MVP production external command ingress. The production path is `ESP32 UART1 GPIO17/GPIO18 <-> STM32 USART1 PA9/PA10`; optional PC control must go through ESP32, and direct PC/ESP32 dual ownership is prohibited.
- MDD10A control model is motor당 `PWM + DIR`.
- Direction changes must ramp or set PWM to zero before changing `DIR`.
- Each MDD10A control signal has a required external reset-safe pull-down: `PC8/DIR1`,
  `PB6/PWM1`, `PC9/DIR2`, `PB7/PWM2` each use `10 kΩ` to GND. Breadboard reset,
  RevB-WIP schematic/ERC/PDF, permanent wiring continuity, power-up/NRST all-LOW and
  powered/no-motor regression passed.
- Board-power policy is fixed: development uses independent dual USB with UART TX/RX/GND only
  and no 5 V rail tie; standalone uses XL4015 #1 5 V to NUCLEO E5V and ESP32 5V with all USB
  removed. NUCLEO uses `JP5=PWR-E5V`, `JP1=open`. USB+buck simultaneous use is prohibited.
- UART/USB serial comes before CAN for first bring-up.
- CAN is still a required later phase.
- FreeRTOS comes after HAL bare-metal drivetrain behavior is validated.
- LL Driver migration comes after a known-good HAL baseline.
- ROS 2 bridge comes after low-level drivetrain safety, timeout, and odometry basics are validated.
- Physical E-stop RevB nominal control path is `F2 -> S0-A NC -> [S2 momentary NO OR K2-HOLD-NO] -> K2 coil`, with K2 pole 2 enabling the K1 coil. K1 opens the MDD10A `POWER+` feed when de-energized, independently of MCU output permission.
- Physical E-stop monitoring uses a separate `5 V -> S0-B NC -> optocoupler LED` loop and 3.3 V pull-up/transistor output to `ESTOP_SENSE`. It does not prove the K1 main contact actually opened.
- With a healthy, released S2 and no S2-pair cross-short, E-stop release does not restore the K1 motor rail by itself. The 2026-08-24 audit identified the open `FM-ESTOP-014` gap: S2 stuck closed or a 6P S2-pair short can energize K2/K1 immediately when S0 is released or control power returns. On 2026-08-25 its verification scope was split: nominal healthy-path/no-auto-motion is MVP `T-ESTOP-005A`; stuck/short single-fault tolerance is post-MVP `T-ESTOP-005B`. The hazard remains a documented residual risk, and no single-fault-tolerant or industrial-safety claim is allowed. Firmware `DISARMED`/PWM zero is an independent layer, not hardware rail-off evidence.
- Current procured/selected Physical E-stop parts are Autonics `SF2ER-E2R2B-A` for S0, IDEC `ABW110G` for S2, Panasonic `TX2-12V` for K2 and Vishay `VO617A-3` for S0-B conditioning. K2 incoming unpowered screening passed. On 2026-08-28 S0 body/contact markings, two independent NC contact states, mechanical latch operation and cross-channel gross-short screen passed; VO617A-3 forward/reverse diode behavior and input-output gross-short screen also passed. S2 then arrived and its terminal `3–4` released-open/pressed-closed/momentary-return truth table passed. These are component-level low-voltage DMM screens, not insulation-withstand, powered or integrated-circuit PASS.
- WHEELTEC technical support confirmed `MG540P30_12V` at 12 V, rated 1.44 A/15 W/280 rpm/2.6 kgf·cm, stall 9 A/10 kgf·cm, 1:30 and PWM 5~20 kHz. Hall encoder is 13-line, 3.3~5 V pulled-up output; STM32 x4 gives `13 x 30 x 4 = 1560 counts/output rev`. Starting current, terminal resistance and thermal/duty-cycle detail remain unavailable.
- WHEELTEC repeated the same motor table in a follow-up support reply. This corroborates the manufacturer-supplied `1.44 A` rated/`9 A` stall values but is not an independent test or formal warranty datasheet.
- Two-motor coordination now uses `2.88 A` rated-total, `18 A` simultaneous stall at 12 V and a conservative `18.9 A` full-charge estimate at 12.6 V. TE Connectivity `V23134J1052D642` / `1393304-9` (12 V, 1 Form A NO) with `VCF7-1000`/`1393310-4` socket, `280756-4` main terminals x2 and `42281-1` coil terminals x2 was ordered on 2026-08-18 and received. On 2026-08-28 the exact parts were matched, coil resistance measured `89.5 ohm` against the official `81~99 ohm` band, the de-energized NO contact was open and the coil-contact low-voltage gross-short screen was open. Catalog ratings still numerically cover the 18.9 A envelope. Socket retention with crimped terminals, suppression, powered pickup/dropout, actual motor-load waveform, voltage-drop/thermal and rail-off bench release remain open. Panasonic `ACA14535` remains a comparison benchmark, not the procured K1.
- Littelfuse `0287010.PXCN` ATOF 10 A/32 VDC remains the provisional F1 prototype candidate for short/harness protection, not a proven locked-rotor protector. The received Littelfuse holder has `GXL 12AWG SCL -LF-` leads; visual inspection, fuse/holder continuity and light-movement continuity passed unpowered. The fuse itself is marked `LITTELFUSE/257/32V/10`, so its identity/time-current curve must be reconciled with the ordered 287 ATOF part before release. Loaded voltage-drop/thermal, interruption and locked-rotor claims remain open. AWG 12 remains the preferred released common harness because TE `280756-4` accepts AWG 12~10; per-motor AWG 16 remains the branch candidate.
- F2 is the ordered Littelfuse `0287001.PXCN` 1 A ATOF with `FHAC0001ZXJA` holder. The received set passed the operator-reported unpowered continuity/movement screen on 2026-08-28, but the exact physical marking was not captured in immutable evidence and its powered time-current, voltage-drop and thermal behavior remain open. The 6P item is a loose male/female waterproof connector kit with terminals, seals and secondary locks plus separate 18 AWG wire, not a preterminated harness; inventory/visual screening passed, while cavity numbering, crimp, 6-by-6 intended-continuity/unintended-open and retention remain open. Three `P6KE16CA-E3/54` coil-clamp candidates arrived; exact `CA` marking, no stripe and both-direction continuity/diode-mode open passed the identity/gross-short screen. Breakdown/clamp energy and actual K1/K2 release behavior remain open.
- A 2026-08-25 source audit found that normal production `CMD(vx,w)` was not mapped to left/right PWM/DIR and TEL motor/battery fields were placeholders. P-02A fixed a normalized, coupled-saturation open-loop mixer and pure-function/vector contract. On 2026-08-27 P-02B HAL-independent mapper source/build and vectors reached the historical `23/23` checkpoint; P-02C-1 added `motor_output_set_signed()` with provisional polarity and fail-safe range/error handling and reached the historical `24/24` checkpoint. P-02C-2 then connected production `handle_cmd()` as validation -> `ARMED` -> E-stop -> mapper at a 100-permille cap -> E-stop -> mutually exclusive controlled-raw or production-signed output -> E-stop -> success-only command/timestamp commit and ACK. Mapper/output failures stop all output, zero stored `vx/w`, send ERR and return. That P-02C-2 checkpoint was `21 + 2 + 2 = 25/25`; its 32-object forced build exited 0 with ELF `text=29216`, `data=172`, `bss=2832`, and nonzero mapper/signed-adapter linkage.
- P-03A/P-03B moved timeout enforcement into a pre-RX helper that stops all output, zeros stored `vx/w` and enters `DISARMED`; accepted `ARM` resets the first-CMD window to the default 300 ms and current tick. Its historical canonical host/static checkpoint is `22 + 2 + 2 = 26/26`; the forced 32-object ARM build exited 0 with no warning/error diagnostics and ELF `text=29268`, `data=172`, `bss=2832`. On 2026-08-28 the motor/LiPo-disconnected 300 ms target run passed timeout-to-`DISARMED`, CMD-only rejection, ARM-only old-command non-restoration, new ARM+CMD recovery and final DISARM. PB6/PB7 produced two expected about 19.06 kHz/5% bursts while PC8/PC9 stayed LOW; all-hooks-`0U` restore then held all four nets LOW for 10 s. A later canonical `REQ-SAFE-004 timeout_ms=500` run03 also passed the same state/recovery contract in one D4/D5 UART+D0~D3 timeline: first PWM active span `498.4085 ms`, about 19.043 kHz/4.99%, timeout-safe transition, three expected CMD-only rejections/expiry checks, fresh ARM+CMD recovery and final 6.545 s no-reactivation. This closes `REQ-SAFE-004` in the motor/LiPo-disconnected UART+MCU control-net scope. Run03 used an operator-reported dual-reset release, but the RST nets were not captured. Post-run run04 then passed source hooks `0U`, host/static `26/26`, script-disabled startup DISARM/PING/READY, ARM/CMD TX 0, about 14.3 s/144 post-READY `DISARMED/zero` TEL and D0~D3 10 s all-LOW. Channel/forward polarity, exact controlled BIN linkage, clean electrical cold-start and actual motor evidence remain open.
- On 2026-08-29 P-04A replaced the STM TEL `left_pwm/right_pwm` placeholders with `motor_output_get_applied()` software-cached signed permille and extended the ESP32 structured parser/log. Its historical canonical host/static checkpoint was `23 + 2 + 2 = 27/27`; the user-run STM32CubeIDE incremental build passed 0 errors/0 warnings with ELF `text=29428`, `data=172`, `bss=2832`, and both boards were reported flashed. Controlled run01 had 49 TEL: all 7 accepted forward-command samples were `50/50`, while 5 ARM-only and 37 DISARMED samples were `0/0`; timeout/reject/expiry/recovery/final-DISARM stale reports were zero. Post-test run02 had script disabled, ARM/CMD TX 0 and all 50 TEL `DISARMED/0/0`, with a 43-TEL/4.2 s post-READY safe tail. This closes P-04A only in the UART/software-cache scope. Reverse/asymmetric sign, same-run physical PWM, exact flashed-binary linkage, battery and actual motor remain open.
- As of 2026-08-28, all selected S2/P6KE electrical parts have arrived and their specified unpowered incoming screens passed. The ordered crimp tooling remains not received, and the loose 6P kit has completed inventory/visual screening only. Complete nominal integration and powered coil tests remain blocked by first-article crimp/cavity/intended-continuity/unintended-open/retention and the remaining powered gates, not by S2/P6KE delivery.
- The downloaded WHEELTEC chassis bundle itself contained no MG540 rating evidence; the values above come from the separate 2026-08-17 manufacturer support reply preserved under `assets/vendor/wheeltec`.
- Step 6 fixed the functional circuit/net architecture, connector/test-point partition and backfeed boundary in `25_Physical_EStop_RevB_Circuit_Architecture_ko.md`.
- MVP K1 actual-off evidence is direct downstream continuity/voltage measurement; K2/control state alone is not proof. Protected PA4/PB0 dual-rail sensing remains a post-MVP automatic diagnostic option.
- PC7 is configured for MVP `ESTOP_SENSE` as an internal-pull-up, active-HIGH/open-fault input. A motor-disconnected direct PC7-to-GND runtime subtest passed healthy boot, asserted/open fault latch, ARM/CMD rejection, reset-while-active rejection, release-with-latch persistence and explicit-reset-to-`DISARMED`; this is firmware/direct-pin evidence only, not VO617A-3/S0-B/K1 proof. PA4 upstream `VBAT_PROTECTED_SENSE` and PB0 downstream `MOTOR_VBAT_SAFE_SENSE` remain post-MVP candidates.
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
| PC bench debug/encoder logger; historical PC-first evidence only | PA2 / PA3, USART2; production command RX disabled |
| STM32 production ESP bridge UART TX/RX | PA9 / PA10, USART1 |
| ESP32 production UART TX/RX | GPIO17 / GPIO18, UART1 |
| Firmware motor channel 1 PWM, bench-confirmed | PB6, TIM4_CH1 -> MDD10A PWM1 |
| Firmware motor channel 2 PWM, bench-confirmed | PB7, TIM4_CH2 -> MDD10A PWM2 |
| Firmware motor channel 1 DIR, bench-confirmed | PC8 -> MDD10A DIR1 |
| Firmware motor channel 2 DIR, bench-confirmed | PC9 -> MDD10A DIR2 |
| Optional power gate/brake | PC6 / PC5 only if a separate circuit is added |
| Encoder channel 1 A/B, motor-off bench-confirmed | PB4 / PB5, TIM3 |
| Encoder channel 2 A/B, motor-off bench-confirmed | PA0 / PA1, TIM5 |
| K1 upstream rail ADC candidate | PA4, ADC12_IN4 -> `VBAT_PROTECTED_SENSE` |
| K1 downstream rail ADC candidate | PB0, ADC12_IN8 -> `MOTOR_VBAT_SAFE_SENSE` |
| Physical E-stop sense, configured/direct-runtime partial | PC7 GPIO input, internal pull-up, active HIGH/open -> `ESTOP_SENSE` |
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
- `04_PC_Serial_Control/docs/02_STM32_UART_MVP_Firmware_Guide_ko.md`: historical PC-first STM32 USART2/ring-buffer/parser implementation guide
- `04_PC_Serial_Control/docs/03_Ubuntu_UART_MVP_Test_Tool_ko.md`: Ubuntu PC-side UART MVP test guide with `/dev/ttyACM0`, `dialout`, and `stty` notes
- `04_PC_Serial_Control/docs/04_Web_Serial_Dashboard_ko.md`: browser Web Serial dashboard guide
- `04_PC_Serial_Control/docs/05_UART_MVP_Runbook_ko.md`: historical PC-first end-to-end UART MVP execution guide for Web dashboard and terminal tools
- `04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`: historical PC-first STM32CubeMX implementation guide for NUCLEO-F446RE, USART2, ring buffer, parser, state machine, timeout, and telemetry
- `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md`: ESP32 UART1 loopback, STM32 PING/PONG/TEL integration, scripted safety sequence, timeout-zero, and final evidence
- `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/002_ESP32_IDF_Environment_Bringup_ko.md`: ESP32-S3 ESP-IDF v6.0.2 bring-up evidence
- `08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md`: adapter plate and electronics placement baseline, Rev A state, and remaining physical checks
- `08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`: Rev A dimension, A4 1:1, vendor-template PDF, vector-scale, and order-attempt record
- `08_Mechanical_Design/source/chassis/README.md`: preserved original R3 tracked-chassis hole-pattern DWG and SHA-256
- `08_Mechanical_Design/releases/revA/README.md`: Rev A DXF, DWG, SVG, PDF release-file index and SHA-256 values
- `08_Mechanical_Design/references/vendor_templates/README.md`: preserved Multimaker source template, original filename, and SHA-256
- `assets/screenshots/mechanical_layout/README.md`: adapter plate and electronics layout screenshot index
- `09_Electrical_Design/README.md`: RevB-WIP current scope, RevA history, verified/TBD boundary and source/evidence index
- `09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevB/Tracked_Mobile_Robot_Wiring_RevB.kicad_sch`: current pull-down-integrated KiCad schematic source
- `09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevB/README.md`: RevB-WIP checkpoint evidence hashes and remaining gate
- `09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_sch`: historical pre-pull-down KiCad schematic source
- `09_Electrical_Design/01_Perfboard_Low_Current_Allocation_Plan_ko.md`: current 150 x 100 mm/55 x 37-hole low-current zone plan; exact part coordinates and soldering remain HOLD
- `09_Electrical_Design/04_RevB_Schematic_Functional_Layout_Learning_and_Rework_Plan_ko.md`: RevB electrical WIP baseline freeze and post-learning portfolio-layout rework gate
- `09_Electrical_Design/05_Perfboard_Photo_Dimension_and_Dry_Placement_Input_Checklist_ko.md`: actual board/part photo, dimension and occupied-hole inputs required before dry placement
- `09_Electrical_Design/06_Perfboard_Photo_Derived_Occupancy_and_Pulldown_Dry_Placement_ko.md`: actual solder joints + Onshape body/removal cross-check, preliminary fixed-hole map and R9~R12 candidate
- `09_Electrical_Design/07_Perfboard_Digital_Layout_Workflow_Decision_ko.md`: adopted pre-solder 1:1 component/solder-side and KiCad-net-to-hole review Gate; VeroRoute 2.40 pilot pending
- The 150 x 100 mm carrier is not blank: NUCLEO-F446RE, ESP32-S3 and BNO085 socket/header positions are user-confirmed permanently soldered. Preserve their removal envelopes and the ESP32 antenna keep-out; the upper-right open area is the first low-current expansion candidate.
- `09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/reports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt`: dated ERC 0/0 evidence
- `09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/exports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_draft.pdf`: RevA human-review export
- `docs/progress/2026-08-29_progress.md`: current continuation state; P-04A COMPLETE, P-04B reason/command-age PARTIAL, canonical `28/28`, hook-0 isolated build and remaining reset/target reflash-runtime boundary
- `docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md`: P-04B reason/accepted-CMD age, timeout and direct-PC7 active/latch UART subset with reset and hook-0 target reflash/runtime limitations
- `assets/logs/firmware_build/2026-08-29_p04b_hook0_isolated_build_pass.md`: current all-hooks-`0U` isolated STM32/ESP32 build run, retained artifact hashes and explicit no-flash/no-runtime boundary
- `docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md`: P-04A positive symmetric/zero-state target UART result, raw evidence hashes and measured-output limitations
- `docs/progress/2026-08-28_progress.md`: historical K1/S0/S2/VO617A-3/P6KE/F2 incoming and P-03/REQ-SAFE-004 target-runtime checkpoint
- `docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md`: K1/S0/S2/VO617A-3/P6KE/F2 unpowered incoming evidence and 6P loose-kit/tooling boundary
- `docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md`: P-03 current-default target UART/PWM recovery, evidence hashes and all-hooks-`0U` safe restore
- `docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md`: canonical 500 ms same-run UART/PWM acceptance and run04 post-test safe restore evidence/hashes
- `docs/progress/2026-08-27_progress.md`: historical P-02B~P-02C-2 and P-03A/P-03B source/static/full-build completion, canonical `26/26` and partial-arrival transition
- `docs/progress/2026-08-26_progress.md`: dated pre-arrival schedule decision and P-01/P-02A baseline; superseded by later progress records
- `docs/plans/2026-08-26_Pre_Arrival_Schedule_ko.md`: historical pre-arrival execution schedule; `P-01~P-09` daily allocation, milestones, buffers and delivery transition rules
- `docs/progress/2026-08-25_progress.md`: current scope baseline; final remaining-work audit, `005A/005B` scope split, evidence boundaries and pre-arrival queue
- `docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`: authoritative final-MVP remaining-work sequence and `P-01~P-09` scope definitions
- `docs/progress/2026-08-24_progress.md`: historical direct-PC7 firmware/runtime evidence, F1/K2 incoming prechecks and initial `FM-ESTOP-014` finding
- `docs/verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md`: motor-disconnected direct-PC7 runtime and unpowered F1/K2/resistor evidence with explicit scope limits
- `docs/progress/2026-08-18_progress.md`: historical final 19 kHz perfboard gate PASS, MG540 manufacturer values, TE K1 order and initial F1/AWG 12/K1 incoming actions
- `docs/handoff/2026-08-18_k1_order_and_physical_estop_continuation_ko.md`: historical continuation source superseded by the 2026-08-25 progress/plan and 2026-08-28 progress/reports 19~20; it is not the current hardware-evidence baseline
- `docs/progress/2026-08-12_progress.md`: historical UART Gate C and motor-disconnected timeout/fault/reset-boot completion state, external `10 kΩ` pull-down decision
- `docs/verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md`: current T-BRIDGE-008A/008B report, artifact metadata and evidence boundaries
- `docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`: command-timeout, software-fault latch, reset FAIL/root cause, `10 kΩ` pull-down PASS and final safe restore report
- `docs/handoff/2026-08-13_power_and_physical_estop_session_ko.md`: historical source for RevB pull-down, board power/back-power and initial Physical E-stop work; superseded by the 2026-08-18 K1 handoff
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
- `03_Firmware/tests/test_firmware_contract.py`, `test_drive_command_mapper_contract.py`, `test_uart_frame_contract.py`, `README.md`: STM32/ESP32 pin, timer, UART, E-stop, encoder sign, mapper, signed output adapter, production caller, timeout-to-`DISARMED`, applied-output and reason/command-age telemetry plus default-off host/static contract preflight; current result is `24 + 2 + 2 = 28/28 PASS`, not a substitute for target electrical evidence
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
- `01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md`: actual S0/S2/K2/opto/F2/K1 selection, 2026-08-28 incoming-screen status, catalog/current-envelope review와 남은 integration closure gates
- `01_System_Architecture/27_Production_Open_Loop_Command_Mapper_ko.md`: P-02A normalized open-loop differential mixer, coupled saturation, HAL-independent interface and exact host vectors
- `docs/progress/2026-07-23_progress.md`: adapter plate Draft, electronics placement, and Onshape Version
- `docs/progress/2026-07-20_progress.md`: ESP32 scripted safety sequence, timeout-zero, and bridge MVP PASS
- `docs/handoff/README.md`: handoff folder index and reading order
- `docs/handoff/NEXT_SESSION_START_PROMPT.md`: prompt to paste into a new Codex session
- `docs/handoff/2026-07-28_kicad_reva_wiring_handoff.md`: latest wiring baseline, safety boundary and next firmware/hardware gate
- `docs/handoff/2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md`: historical UART bridge closeout; current continuation source는 2026-08-25 progress/plan이며 2026-08-24 report 18은 hardware evidence baseline이다.

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
- Historical PC-first tools and ESP32 use the same line-based application frames, but ADR-015 no longer treats them as simultaneous/equivalent production owners. ESP32 is the single production ingress; STM32 remains the parser, safety gate, drivetrain authority, and command-timeout owner.
- First UART MVP uses `ACK` for accepted commands and `ERR` for rejected commands or parse failures. A separate `NACK` frame is not used.
- The pre-ADR-015 timeout candidate kept `ARMED` after output zero. ADR-015 supersedes it with output/stored command zero -> `DISARMED` -> accepted `ARM` + valid `CMD`. P-03A/P-03B source/static/full-build, the 300 ms current-default target run and canonical `REQ-SAFE-004 timeout_ms=500` run03 implement and verify that transition plus a reset 300 ms first-CMD window after `ARM`. It does not implement sequence/session anti-replay; exact controlled artifact linkage, electrically captured reset timing, clean electrical cold-start and actual motor closure remain pending.
- PC telemetry dashboard mock is planned as a fake-telemetry-first tool before real serial integration.
- Historical PC-first UART MVP tooling was added under `04_PC_Serial_Control`. For that bench workflow, the PowerShell tool was the Windows-first path and the Bash tool was the Ubuntu/Linux path for `/dev/ttyACM0` or `/dev/ttyUSB0`. The tools can build frames, send frames over a serial port, run an interactive console, run a scripted MVP smoke test, monitor RX lines, and save raw/parsed logs.
- A browser-based Web Serial dashboard was added under `04_PC_Serial_Control/web_serial_dashboard`. This is not a backend WebSocket bridge; Chrome/Edge directly opens the serial port from `localhost`, keeping the first web UI simple.
- `04_PC_Serial_Control/docs/05_UART_MVP_Runbook_ko.md` is the execution guide for the historical PC-first Web dashboard, terminal tools, and evidence collection.
- `04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md` is the detailed historical PC-first STM32 UART MVP build guide. Its USART2 command path is not the Final MVP production contract after ADR-015.
- The historical PC-first STM32 firmware workflow was STM32CubeMX-first: install/run standalone STM32CubeMX, select `NUCLEO-F446RE` through Board Selector, configure USART2 and NVIC, generate code under `03_Firmware/stm32_uart_mvp`, then open/import in STM32CubeIDE.
- `STM32CubeIDE Empty Project` is not the starting point for the current MVP because the project depends on CubeMX `.ioc` and generated HAL initialization code.
- The historical STM32-side UART MVP guide covers USART2, RX interrupt, ring buffer, parser, ACK/ERR/TEL responses, timeout handling, and telemetry generation. The current production protocol binding is USART1 under ADR-015.
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
- Motor-output verification is `PASS — motor-disconnected MCU-pin scope`; permanent pull-down and powered/no-motor regression also passed. MDD10A power-stage timing, Physical E-stop and actual motor stop remain unverified, so the overall drivetrain release is still `PARTIAL`.
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
- On 2026-08-16, RevB R9~R12 permanent pull-downs and the STM32-MDD10A 5-Net interface passed resistance/continuity, 5 s power-up, NRST-held/cycle all-LOW and powered/no-motor regression.
- On 2026-08-16, XL4015 #1 was approved for STM32/ESP32 buck-only logic power. Board-connected values were 5.00~5.01 V with NUCLEO 3.30 V and ESP32 3.27 V; supply-off values were all 0 V.
- On 2026-08-18, WHEELTEC support confirmed rated 1.44 A, stall 9 A and PWM 5~20 kHz for `MG540P30_12V`. Because the nominal 20 kHz baseline remeasured about 20.054 kHz, TIM4 period was changed to `4420` for nominal 19 kHz with upper-limit margin.
- On 2026-08-18, final perfboard MDD10A-input active 6-step passed. CH1/CH2 measured `19.049/19.058 kHz`, about 10% duty, pre/post-DIR zero about 2 ms, inactive channels LOW and planned MDD10A LED order. After restore all controlled hooks were `0U`, contract `15/15`, user-observed build/flash/run passed and final 5 s D0~D3 capture had zero HIGH samples/transitions.
- On 2026-08-24, current host/static discovery passed `test_firmware_contract.py` 18 tests and `test_uart_frame_contract.py` 2 tests (`20/20`). Both controlled ESP32 hooks are `0U`. This is source/host evidence, while the separate direct-PC7 board run is target runtime evidence.
- On 2026-08-26, ADR-015 was accepted and the Korean/English pin, ESP32-role, UART, block-map, FreeRTOS, state-machine and fault documents plus historical PC-first/protocol learning guides were synchronized. Target timeout-only states and direct PC/ESP32 dual-ingress wording were removed or retained only as explicit superseded history. Source inspection found only `uart_mvp_init(&huart1)`, no USART2 `HAL_UART_Receive*`, and three USART2 logger TX call sites; host/static discovery re-passed the then-current `20/20`. This closes P-01 ownership/documentation. P-02A fixed the open-loop mapper design/vectors, P-02B reached the dated `23/23 PASS` checkpoint, P-02C-1 signed adapter reached `24/24`, and P-02C-2 production caller integration reached `25/25`. P-03A/P-03B timeout recovery then reached the historical `26/26` checkpoint, passed a 32-object forced ARM build and, on 2026-08-28, passed both the 300 ms scoped target UART/PWM recovery with its safe restore and the canonical 500 ms `REQ-SAFE-004` same-run UART/PWM acceptance. Run04 closed the post-run03 safe source/static/build/flash/UART/all-LOW restore. P-04A subsequently connected the left/right software-applied TEL fields and reached the historical `27/27` checkpoint.
- On 2026-08-29, P-04B added STM32 TEL `reason/command_age_ms` and the matching ESP32 required strict parser/log path; canonical host/static discovery reached current `28/28 PASS`. Controlled run02 verified the no-CMD sentinel, successful-CMD-only age reset, 500 ms `CMD_TIMEOUT`, ARM-only timeout and fresh-CMD recovery. Independent direct-PC7 run03 verified `ESTOP_ACTIVE`; run04 verified `ESTOP_ACTIVE -> ESTOP_LATCHED`, with software-cached PWM `0/0` throughout FAULT. The authoritative report is `docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md`, with raw logs under `assets/logs/esp32_uart_bridge/2026-08-29_p04b_*.txt`. Active reset reject and released reset success were not run in the new schema. Current source/static has every controlled hook restored to `0U`; isolated build run `20260829043337-25400-bc21` passed STM32 `0 errors / 0 warnings` and ESP32-S3 image generation, with hashes recorded in `assets/logs/firmware_build/2026-08-29_p04b_hook0_isolated_build_pass.md`. Those hook-0 images have not been reflashed or checked in a no-command board runtime, so P-04B remains `PARTIAL`. Optional `PC -> ESP32` forwarding and battery remain pending.
- The motor-disconnected direct-PC7 run passed active-HIGH/open-fault behavior: open/HIGH entered and retained `FAULT`, ARM/CMD and active reset were rejected, DISARM did not clear the latch, restoring LOW did not clear it, and an explicit `ESTOP_RESET` returned the system to `DISARMED` with zero telemetry. This does not test VO617A-3, S0, K1 rail interruption, active-output assertion timing or an actual motor.
- Incoming K2 `TX2-12V` samples measured `1.025 kΩ` and `1.035 kΩ` against the official `1.028 kΩ ±10%` coil value. De-energized `3-4`/`10-9` NC continuity, `4-5`/`9-8` NO-open state and coil-to-contact low-voltage gross-short screen passed on both samples. Powered pickup/dropout waits for the clamp and controlled supply path.
- The received F1 holder/fuse passed unpowered visual and continuity screening: Littelfuse holder, `GXL 12AWG SCL -LF-` leads, fuse markings `LITTELFUSE/257/32V/10`, open holder without fuse, fuse continuity and stable installed continuity. Loaded milliohm/voltage-drop/thermal and interruption behavior remain unverified. The selected S0-B resistors measured `670.1 Ω` and `9.97 kΩ`.
- On 2026-08-28 K1 exact-part matching, `89.5 ohm` coil, de-energized-NO and coil-contact gross-short screens passed; S0 two-channel NC/latch states, S2 `3–4` momentary-NO action, VO617A-3 diode/input-output gross-short, P6KE16CA x3 identity/gross-short and F2 operator-reported continuity/movement passed. These are unpowered low-voltage screens, not insulation-withstand, powered integration or rail-off evidence. The 6P item is a loose connector kit and separate 18 AWG wire; only inventory/visual screening is complete.
- A `VH-30J` interchangeable-die crimper set was ordered with seller-listed `WX-35WF (10~35 mm2)`, `WX-03B (0.5~6 mm2)`, `WS-25WF (2x0.5~2x6 mm2)` and `WS-692 (1.5~6 mm2)` dies for 18 AWG connector first-article work and later AWG 12 K1 terminal work. It is not received, and printed wire-range coverage is not proof of the required open-barrel crimp geometry or pull/retention quality. Use spare 6P terminals for first-article validation; do not practice on the only two K1 main terminals.
- The dated ERC report records 0 errors and 0 warnings under its listed ignored-check policy. This does not verify physical wiring, current capacity, noise, footprints, perfboard layout or manufacturing readiness.
- A roughly 174 x 209 mm adapter plate Draft was created from the tracked-chassis hole-pattern drawing on 2026-07-23.
- A 150 x 100 mm, 55 x 37 universal PCB carries the NUCLEO-F446RE, ESP32-S3, and GY-BNO085 in the Draft assembly.
- XL4015 x2 and MDD10A are placed in the upper power area; ESP32 stays horizontal for USB access and the IMU stays near the vehicle center.
- The CAD checkpoint is preserved under the displayed Onshape Version name `dapter-layout_draft01_2026-07-23`; the intended name starts with `adapter-`.
- Rev A 2D manufacturing baseline is 174 x 208.93379 mm. Direct DXF audit found 21 x diameter 3.3 mm and 8 x diameter 2.2 mm small holes; the first fabrication candidate was acrylic 3T.
- The A4 1:1 print was physically compared with the chassis and recorded as `USER-CONFIRMED PASS`.
- The final Multimaker PDF passed a one-page, 39-vector-path, zero-raster, zero-text and source-scale comparison.
- The 2026-07 RevA Multimaker attempt was not submitted because its WordPress server could not create or write `wp-content/uploads/2026/07`; this is historical and does not describe the later PC plate order.
- A later PC plate order was recorded as placed on 2026-08-18, and the user reported the fabricated custom PC plate received on 2026-08-26. The repository still needs the actual order artifact or physical measurements/photos to link that plate to the RevB DWG/DXF and close fit evidence.
- The original chassis input file is preserved at `08_Mechanical_Design/source/chassis/R3_High_Config_Version_Tracked_Vehicle_Hole_Pattern_Drawing.dwg`; verify its SHA-256 against the source README before a Rev B rebase.
- Red reference-instance badges remain in the 3D Assembly Draft, but they are outside the user-approved Rev A 2D order scope; fabricated-plate fit remains `NOT TESTED`.

## Open Decisions

Ask the user or verify from hardware only for these:

- Vehicle left/right assignment for MDD10A channel 1/2
- Final CAN transceiver model
- Final USB-CAN adapter model
- Battery voltage divider resistor values
- External-tachometer RPM accuracy and wheel-speed scale; the current firmware output-shaft count constant is 1560
- Final F1 release after loaded start-waveform, voltage-drop/thermal and protection-coordination evidence; 10 A ATOF remains the prototype candidate
- BNO085 power and I2C final wiring
- Physical connector, footprint, perfboard and harness release; 6P cavity mapping, first-article crimp and 18 AWG terminal/seal retention remain pending
- K1 powered/assembled bench release and remaining Physical E-stop component integration; its unpowered incoming screen is complete
- Post-MVP disposition/mitigation for `FM-ESTOP-014`: `T-ESTOP-005B` covers S2 stuck closed and 6P S2-pair short; until closed, document the residual risk and make no single-fault-tolerant/industrial-safety claim
- Optional `PC -> ESP32` forwarding transport/arbitration, if that feature is implemented
- UART maximum application frame length and ring buffer size
- Whether checksum/CRC stays deferred until Wi-Fi forwarding
- Acrylic color and cast/extruded material choice
- Vendor kerf compensation, minimum hole capability, and manufacturing tolerance
- Mounting screw, nut, washer, and insulating-spacer specifications
- CAD coordinate origin for the manufacturing drawing

## Next Concrete Actions

1. Start every new session with `git status --short -- Projects/Tracked_Mobile_Robot`.
2. Read `docs/progress/2026-08-29_progress.md`, report 23, report 22, then reports 19~21 and the authoritative scope plan `docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md` first. Treat the 2026-08-26 pre-arrival schedule, report 18 and the 2026-08-18 handoff as history.
3. Preserve the fixed power policy: dual USB uses UART TX/RX/GND only; buck-only uses XL4015 #1 with all USB removed; never combine USB and buck. Keep actual motor power disconnected until the E-stop gate passes.
4. Preserve the all-hooks-`0U` current source, its isolated STM32/ESP32 build PASS, TIM4 period `4420`, current host/static `28/28`, P-04A hook-0 50-TEL safe UART run, P-04B controlled reason/age and direct-PC7 active/latch subset, final perfboard 5 s all-LOW, P-03 historical safe-restore 10 s all-LOW, canonical 500 ms run03 and post-run03 safe run04 UART/D0~D3 evidence. Earlier UART-safe artifact hashes and `15/15`, `20/20`, `23/23`, `24/24`, `25/25`, `26/26`, `27/27` checkpoints remain historical. The current P-04B hook-0 target reflash/runtime restore is still open; host/static/build PASS does not replace board or electrical evidence.
5. Treat T-BRIDGE-008A/008B required runtime scope as complete and preserve report 15 plus all 2026-08-12 raw logs; do not repeat these controlled vectors unless firmware behavior changes.
6. Preserve Gate A/B, T-BRIDGE-007/008, active DISARM 23.50 us and report 16 timeout/fault/reset raw evidence; do not repeat unless firmware or wiring changes.
7. Preserve the completed RevB-WIP four-`10 kΩ` schematic/ERC/PDF, `55 x 37` layout/1:1 comparison, permanent wiring continuity, power-up/NRST all-LOW and powered/no-motor regression evidence.
8. Preserve A=right/TIM5, B=left/TIM3, forward-positive CPS, `1560 counts/output rev`; treat 20.1005 kHz as historical and final 19.049/19.058 kHz perfboard captures as the current PWM baseline.
9. `P-01` is complete through Accepted ADR-015. `P-02A~P-02C-2`, the 300 ms-scoped `P-03` target runtime and canonical 500 ms `REQ-SAFE-004` target acceptance are complete in their stated motor/LiPo-disconnected scope. Preserve reports 20/21 and their evidence.
10. Preserve run04 as the P-03/REQ-SAFE-004 safe board baseline, report 22 as the P-04A applied-output/hook-0 UART baseline, and report 23 plus the hook-0 isolated build summary as the P-04B reason/age, direct-PC7 active/latch and build subset. Finish P-04B with active reset rejection, released reset success, then all-hooks-`0U` target reflash/no-command safe runtime. Only then continue battery sensing/low-voltage behavior (`P-05`) and wheel-distance/odometry (`P-06`). Plate identification/dry fit remains a separate home `H-01` checkpoint.
11. Complete received-plate identification, fit and mechanical/harness preflight (`P-07`) without assuming the plate matches the RevB source, reconcile received F1 `257` versus ordered `287` identity and S1 DC basis (`P-08`), and prepare incoming/test capture sheets (`P-09`).
12. Preserve report 19's completed K1/S0/S2/VO617A-3/P6KE/F2 unpowered screens. Confirm the 6P mating-face cavity numbers/orientation, then after the ordered crimper arrives qualify one spare 18 AWG terminal/seal first article by visual, pull and housing-retention checks. Remove the temporary direct PC7-to-GND jumper before connecting the optocoupler path.
13. Execute `T-ESTOP-001~004` and then nominal healthy-path `T-ESTOP-005A`. Keep the direct-PC7 result as a partial subtest, not full conditioned-path PASS. Do not apply actual motor energy before all five MVP gates pass.
14. Only after `T-ESTOP-001~004 + T-ESTOP-005A` pass, run lifted/no-load actual motor at 5~10%, record current/heat/smell/noise/powered encoder noise, then execute `T-ESTOP-007` actual-stop/no-auto-motion evidence.
15. Continue with dual drivetrain mapping, low-speed ground motion, low-voltage behavior, 1 m odometry and final documentation/evidence audit.
16. Keep `FM-ESTOP-014`/`T-ESTOP-005B`, PA4/PB0 dual-rail plausibility, discrepancy fault injection and precision rail transient `T-ESTOP-006` as explicit post-MVP V-cycles.
17. Preserve the KiCad `RevA DRAFT` history and `RevB-WIP` verified/TBD boundary; do not treat the incomplete RevC workspace as released. Perform schematic-to-hardware continuity review before permanent wiring is accepted.
