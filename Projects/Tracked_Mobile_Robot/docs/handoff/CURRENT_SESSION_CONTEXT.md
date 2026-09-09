# Current Session Context

Last updated: 2026-09-08

## Current Milestone

Finish the motor-disconnected integrated Physical E-stop gate before reconnecting MDD10A `B+` or either
motor. The next uncompleted test is `T-ESTOP-004` conditioned `ESTOP_SENSE` to firmware latch/PWM behavior.

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
- Firmware host/static checks are `29/29`. Controlled hooks are currently `0U`. P-04B active reset reject,
  released reset success, and the final hook-0 target runtime remain open.

The authoritative detailed result is `docs/progress/2026-09-08_progress.md`. The current bench procedure is
`docs/plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md`, starting at Gate 5.

## Recommended Work For The Next Bench Block

Use the existing firmware as learning material and proceed in three bounded parts:

1. Review the existing STM32 E-stop latch/reset path and ESP32 P-04B reset harness. Codex identifies one small
   block and its role; the user reads or types any required change and saves it; Codex rereads the real file.
2. With MDD10A `B+` and both motors disconnected, capture conditioned PC7 plus PB6/PB7 while checking active
   reset rejection, released explicit reset, PWM-zero latch, and no stale-command replay. Do not merge the
   no-ARM/CMD reset check with the limited-output PWM check without stating which subtest is running.
3. Restore every controlled hook to `0U`, rebuild/reflash both boards, and record the no-command safe runtime.

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

- Firmware is user-authored by default: exact location and one small block first, user saves, Codex rereads,
  then explanation/build/flash/measurement.
- Bench instructions state the gate and purpose, then give one physical action at a time.
- `통과 다음` closes only the stated subset and advances without retesting completed work.
- Progress and evidence documents are updated once at the end of the work block, unless the user requests an
  immediate update.
