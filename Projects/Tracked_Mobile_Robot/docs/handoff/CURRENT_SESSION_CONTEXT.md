# Current Session Context

Last updated: 2026-09-19

## Current Milestone

Finish the motor-disconnected integrated Physical E-stop gate before reconnecting MDD10A `B+` or either
motor. The `T-ESTOP-004` scheduler correction and static-test update are complete. The user has now
completed UART/CTRL/ENC/IMU wiring, the instructed unpowered continuity/isolation checks, and final
workmanship/STM32-ESP32 fit checks. Resume with **BUILD-01: user builds both firmwares with board power
disconnected**. PRE-01/DEV-01 precede USB connection and flashing. Powered communication/T004 remain untested.
The [soldering checklist](../plans/2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md) is the current
bench record. The [UART/debug-header plan](../plans/2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md)
preserves drawing history. The [9/19 progress](../progress/2026-09-19_progress.md) records this work-block closeout.

Repository root is `C:\Users\eyh12\workspace\TIL`, project path is
`Projects\Tracked_Mobile_Robot`, and the working branch is `agent/dual-encoder-bringup`. Check Git status and
the latest commit at session start; do not assume this file proves the live electrical state.

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
- The modified firmware's all-hooks-0U host/static baseline passed `30/30`; seven in-memory regression
  mutations were caught. Current source has T004 `1U` and the other three ESP hooks `0U`.

## Current Firmware And Wiring Checkpoint

- STM32 production E-stop/latch/reset code and ESP ACK/ERR parser were not changed.
- The chosen test-only design reuses P-03 and P-04B with
  `DRIVE -> RESET -> POST_RESET -> DONE/FAILED`. Saleae D4/D5 remains the exact UART oracle.
- Current ESP source SHA-256:
  `C7582EB895B0955C434CD17DCB9AE7CD767AA01CE7506415021476680D334201`.
- Restoring only the T004 define to 0U in memory reproduces the prior 30/30 source hash
  `ECC304898B7F61BA1C28A8F01FA69B2FE9B11EB196BFAF02FB911D003EF000E4` exactly. No source was changed
  during this 9/10 comparison. Firmware `git diff --check` passes.
- Test file SHA-256: `AC1C7C4D4E7F193F750495BB332B1BFDCDE06CC2F05BD2E059F64EEDD1C0681D`.
- The wrong runner, RESET/POST_RESET completion condition and FAILED assignment are corrected. Do not ask
  the user to re-enter the scheduler or Python tests.
- User build/flash/runtime results are not yet reported; source hook state does not establish board state.
- Current user-designated drawing is `09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_WIP_CTRL수정본.vrt`,
  At Git closeout the live file is saved 9/19 02:33:28, 160,699 bytes,
  SHA-256 `96f881a54fd5efcd8a3a8456fb3716284d28075944ffd3d8f2bb95f179c36aa9`.
  This differs from the reviewed 9/18 revision (161,191 bytes,
  SHA-256 `251b271958db7ae46055e674bef86913f683b9c5241d12fd48fa47f34cbcb772`).
  The latest file is preserved without review in this Git-only closeout; compare its changes before using drawing endpoints.
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
- On 9/19 the live ESP, STM protocol and Python test hashes match the recorded baseline. ESP T004=1U,
  the other ESP hooks=0U, and STM output/response-injection hooks=0U. No new build or static rerun was performed.
- T004 needs PC7, PB6/PB7, UART PA10/PA9 and LOGIC_GND. DIR access remains useful for later gates.
  IMU signal/owner integration and additional S2 software interlocks remain outside this gate.

Use the soldering checklist for 9/17-19 bench results and the 9/10 progress for the preserved firmware
baseline. The 9/9 progress is an earlier paused checkpoint. The original T004 runbook still supplies runtime
and safe-restore procedures. The user paused before BUILD-01; the 9/19 progress consolidates this work block.

## Next Session Resume Order

1. Read the current soldering checklist and T004 runbook. Do not restart completed wiring or scheduler work.
2. BUILD-01: the user builds STM32 `stm32_uart_mvp` and ESP32 `esp32_uart_bridge` without powering boards.
   Review build results and identify artifacts. Codex does not build/flash unless explicitly delegated.
3. PRE-01/DEV-01: check motor-energy boundaries and development dual-USB configuration before USB connection.
   Keep BNO removed; XL4015 #1's two board plugs must be removed for USB power.
4. The user flashes the identified images, then changes to the standalone runtime setup through OFF/0 V.
5. Capture startup UART and the motor-disconnected T004 sequence with analyzer connections ready before
   startup. The controlled image sends ARM/CMD automatically after READY.
6. After testing, the user restores every controlled hook to 0U, runs the required build/reflash and confirms
   no-command safe runtime; Codex may run the canonical Python suite and prepare the closeout.

Do not start `T-ESTOP-005A` merely because part of `T-ESTOP-004` passes. Close the whole test and its evidence
first. If the work block is short, completing the source walkthrough and exact capture plan is still useful.

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
