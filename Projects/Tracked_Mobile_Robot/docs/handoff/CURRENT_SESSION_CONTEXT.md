# Current Session Context

Last updated: 2026-09-22

## Current Milestone

**2026-09-22 T-ESTOP-004 PASS**, motor-disconnected conditioned S0-B/VO617A/PC7 firmware/PWM scope.
Read [latest progress](../progress/2026-09-22_progress.md) and
[report 26](../verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md) for raw evidence and limits.
All controlled hooks are now **0U**; final static suite **30/30 PASS** and run07 no-command boot PASS.
Do not repeat the completed T004/source-walkthrough/wiring steps.

Next: resolve documented power-distribution/fuse/terminal release items and prepare **T-ESTOP-005A**,
with motors still disconnected. This is not authorization to attach MDD10A B+ or either motor now.
Repository root: `C:\Users\eyh12\workspace\TIL`; branch: `agent/dual-encoder-bringup`.
The user requested a Git checkpoint/push on 9/22. This checkpoint includes the restored ESP hook,
T004 raw/decoded evidence, report/progress and next-session plan. Check live Git status and the latest
commit/remote before resuming; 3c756e5 is the previous checkpoint.

## Completed Baseline To Preserve

- K2 label correction and bounded direct continuity are complete. Do not repeat K2 contact tests.
- S0-A/S0-B baseline, wire-open independence, restoration, and the nominal K2/K1 control-only switch sequence
  are operator-reported PASS.
- XL4015 #1 powers the separate NUCLEO and ESP32 2P branches. Standalone single/dual board power and power-off
  return passed. USB and buck power must not be connected together.
- XL4015 #2 supplies `AUX_5V` to the encoder/E-stop sense input side. Its OUT+ remains separate from both
  XL4015 #1 5 V branches.
- Conditioned `ESTOP_SENSE` measured `0.06 V` released and `3.27 V` pressed/latched or S0-B conductor-open.
  This closes the functional voltage subset of `T-ESTOP-003`; the formal evidence package remains PARTIAL.
- All-hooks-0U static suite passed 30/30 again on 9/22. The earlier seven mutation detections remain historical evidence.
- T004 run03 proved latch/reset/ARM-only-zero/fresh-CMD/DISARM in one boot. run04/05 proved active/open boot.
- run06 wire-open PC7 HIGH to final PWM falling edge = 357.25 us; 13.740 s LOW afterward.
- run07: 25 s PWM HIGH 0, 199 TEL all DISARMED/zero, err/drop0; only DISARM/PING transmitted.

## Current Firmware And Wiring Checkpoint

- STM32 production E-stop/latch/reset code and ESP ACK/ERR parser were not changed.
- The chosen test-only design reuses P-03 and P-04B with
  `DRIVE -> RESET -> POST_RESET -> DONE/FAILED`. PulseView/sigrok D4/D5 decode supplies exact seq/type/code evidence.
- Final ESP source SHA-256: `ECC304898B7F61BA1C28A8F01FA69B2FE9B11EB196BFAF02FB911D003EF000E4`.
  All four ESP hooks and STM output/response-injection hooks are 0U. User changed only T004 1U→0U.
- STM protocol source remains `063F608DE44673649E4FEAFC22A525532CD48552199AF93AECE1EDC3FF1A5127`.
- Test source remains `AC1C7C4D4E7F193F750495BB332B1BFDCDE06CC2F05BD2E059F64EEDD1C0681D`.
- User performed both builds/flashes and explicitly confirmed final STM success. Final ESP ELF hash
  starts `7bc5eca6f`, matching its USB boot log. Artifact hashes/limitations are in report 26.
  Complete flash transcripts/STM flash readback and a controlled ESP BIN backup were not supplied.
- Scheduler correction is complete. Do not re-enter the coordinator or Python validation code.
- Current user-designated drawing is `09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_WIP_CTRL수정본.vrt`,
  At Git closeout the live file is saved 9/19 02:33:28, 160,699 bytes,
  SHA-256 `96f881a54fd5efcd8a3a8456fb3716284d28075944ffd3d8f2bb95f179c36aa9`.
  This differs from the reviewed 9/18 revision (161,191 bytes,
  SHA-256 `251b271958db7ae46055e674bef86913f683b9c5241d12fd48fa47f34cbcb772`).
  On 9/22 the live T004 headers and their STM Net endpoints were checked directly in this file.
  This was not a revalidation of the complete wire graph or latest PDF export.
  The similarly named `...UART_Debug_IMU_WIP.vrt` is the older 9/16 revision; do not use it for current header numbering.
  The 9/18 reviewed drawing had 132 wires/28 checked non-wire parts, zero broken nets and zero detected Net inconsistencies.
- CTRL and ENC each use two 3-pin connectors. CTRL_1 Pins1/2/3 are DIR1/PWM1/DIR2 at C35/R1/2/3;
  CTRL_2 Pins1/2/3 are PWM2/PC7/GND at C35/R5/6/7. **C35/R6 is PC7, not GND.**
  ENC_1 Pins1/2/3 are PB4/PB5/GND at C9/8/7,R37; ENC_2 are PA0/PA1/GND at C5/4/3,R37.
  UART remains C26/27/28,R37 (STM TX/ESP TX/GND); IMU remains C45/R15...R10 (RST/INT/SDA/SCL/NC/GND).
- User reports: all debug GND and UART directions passed on 9/17; CTRL and ENC passed on 9/18;
  IMU signal continuity/isolation and final workmanship/STM-ESP fit passed on 9/19. Record as operator-reported,
  unpowered evidence; numerical resistances and powered waveforms were not provided. Do not repeat completed checks.
- IMU RST=PC4, INT=PB1, SDA=PB9, SCL=PB8. BNO supply/mode/pull-ups remain unfinished, so the module stays removed.
  Encoder raw input connectors/conditioning are still separate pending work. Debug wiring does not close those gates.
  Matching latest component/solder PDF exports are not yet confirmed. The old isolated PC7 pad was cleared in an earlier review.
- Normal runtime uses board USB removed, JP5=E5V, JP1=OPEN, both #1 board plugs and #2 AUX connected.
  Development USB needs OFF/0 V, both #1 plugs removed, JP5=U5V. Never combine USB and buck supply.
- Left encoder PB4/PB5 each retain temporary 15 kΩ to STM GND. Before: TIM3 ±1 count / left CPS ±10;
  after: 414 raw pairs all left delta/CPS0. Do not alter arithmetic to hide floating-input counts.
- Right encoder has one +10 CPS startup report per run02~07; permanent input conditioning and powered
  motor noise/sign checks remain open. Both encoder connectors/conditioning are not fully implemented.
- JESTOP Pin3 wire was used for open-fault tests, then restored; run07 PC7 LOW confirms live sense recovery.
  S0 released, S2 not used, MDD10A B+ and motors disconnected, BNO removed throughout.
- Final operator instruction was S1 OFF/LiPo disconnected. The capture ends before that action; recheck
  physical power state before subsequent work rather than deriving it from a file.
- Evidence: `assets/logs/estop/2026-09-22_t004/manifest.json` and named raw run02~07 captures.
  Named run01 is only 1.25 s; the previous long Session 2 was overwritten by the application. Use run03
  for normal boot. Current Session 2 raw samples match run03, not the historical run01 long capture.

## Next Session Resume Order

The user paused to sleep. Follow the [next-session plan](../plans/2026-09-22_Next_Session_Power_Path_and_T_ESTOP_005A_Plan_ko.md); it is a plan, not completed hardware work. Start with the as-built power hub/fuse/K1 terminal identification.

1. Read latest progress/report 26 only as needed. Preserve completed T004 PASS and default-off hooks.
2. Inspect the currently unresolved power hub, F1/F2, K1 terminal/wire-release facts in existing documents.
3. Prepare the motor-disconnected T-ESTOP-005A plan from those facts. Do not connect power/motors merely
   because the secondary firmware/PWM path passed.
4. Keep user-authored firmware/build/flash and one coherent bench group per turn. Record results once
   at work-block closeout. No subagents unless the user explicitly requests them.

## Remaining Critical Path After `T-ESTOP-004`

1. Resolve the positive/ground distribution hardware and the K1/F1/F2 release blockers: F1 `257` versus
   ordered `287`, K1 14 AWG lead versus the `280756-4` AWG 12~10 range, connector/terminal ratings, and
   voltage-drop/temperature evidence.
2. Run `T-ESTOP-005A` at the actual MDD10A `B+` input with motors disconnected, including rail-off,
   no-auto-restart, back-power, UART-loss, and firmware-reset behavior.
3. Verify fabricated adapter-plate fit, E-stop mounting, labels, fasteners, insulation, and strain relief.
4. Run the lifted first-motor low-duty test and powered encoder-noise/sign checks.
5. Complete battery ADC/low-voltage behavior, odometry/1 m calibration, dual drivetrain testing, final fault
   acceptance, and portfolio packaging.

`T-ESTOP-005B` single-fault tolerance, CAN, FreeRTOS, selected LL migration, IMU integration, and ROS 2/Nav2
remain post-MVP work.

## Interaction Contract

- Firmware is user-authored by default. For connected function/scheduler changes, Codex gives the exact
  replacement range, complete reviewed block and state-flow explanation at once; the user saves it and Codex
  rereads the actual source. Do not return to serial one-character corrections.
- STM32 and ESP32 builds and flashes are user-performed. Python validation code maintenance/execution is
  delegated to Codex; do not require the user to retype the complete test block.
- Bench instructions state the gate and purpose, then give one physical action at a time.
- `통과 다음` closes only the stated subset and advances without retesting completed work.
- Progress and evidence documents are updated once at the end of the work block, unless the user requests an
  immediate update.
