# Motor Driver and H-Bridge Control Decision

## Purpose

This document defines the first motor-driver decision for the tracked mobile
robot project and explains how the selected driver should be controlled from
STM32.

The goal is to connect the drivetrain decision to the previous MCU analysis,
pin-allocation work, power-safety design, and control-loop plan:

- STM32 owns deterministic low-level motor control.
- The motor driver handles high-current DC motor power.
- Firmware enforces safe H-bridge control rules.
- The selected driver interface drives the first pin allocation and validation
  sequence.

## Decision Summary

Use one Cytron MDD10A dual-channel DC motor driver for the first drivetrain
MVP.

Initial decision:

- One MDD10A board drives the left and right brushed DC motors.
- Each motor uses one `PWM` signal and one `DIR` signal.
- The initial control mode is sign-magnitude PWM.
- STM32 keeps ownership of motor output, command timeout, and the safety gate.
- Logic-only tests and low-duty no-load motor tests come before chassis motion.

Excluded from the first MVP:

- Using BTS7960 dual-PWM modules as the first drivetrain driver.
- Using TB6612FNG as the main tracked-drivetrain driver.
- Driving motors directly from MCU GPIO.
- CAN-based motor control.
- ESP32-S3 as the primary motor controller.

## Sources

Project sources:

- `00_Project_Charter/02_Component_Inventory.md`
- `00_Project_Charter/03_Initial_Purchase_and_Safety.md`
- `01_System_Architecture/04_MCU_Timers_and_Watchdogs.md`
- `01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md`
- `01_System_Architecture/07_ESP32S3_Features_and_Project_Role_ko.md`
- `01_System_Architecture/20_Motor_Driver_Selection_Comparison.md`

Manufacturer references:

- Cytron MDD10A product page: `https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels`
- Cytron MDD10A user's manual V2.0 mirror: `https://cdn.robotshop.com/media/c/cyt/rb-cyt-153/pdf/rb-cyt-153_-_mdd10a_users_manual_v2.0_-_2017-06.pdf`

Local WHEELTEC reference material:

- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../2._Smart_Robot_Car_Chassis_Development_Reference_Programs/4.STM32F407VET6_L150Pro_Robot_Car_Standard_Library_Version_2023.07.28.zip`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/1._Servo_DC_Motor_Development_Notes/5._DC_Motor_Control_and_TB6612FNG.pdf`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/2._Motor_Control_Basics_Video_Tutorial_and_Source_Code/1._PID_Basics_Intro_DC_Motor_and_TB6612/TB6612_Motor_Driver_Included_Materials/3.TB6612FNG_Module_Schematic.pdf`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/7._Common_Chip_Datasheets_Datasheet/`

## 1. Motor Driver Requirement

The motor driver bridges logic-level MCU signals and high-current motor power.

STM32 can provide:

- PWM logic signals
- Direction logic
- Control-loop timing
- Command timeout and safety-gate decisions
- Encoder feedback processing

STM32 cannot provide:

- Motor current
- Motor voltage directly from GPIO
- Inductive-load protection by itself
- Power-stage heat dissipation

The driver must therefore handle:

- 3S LiPo motor voltage range
- Motor start-up current
- Load spikes from tracked drivetrain friction
- Stall or near-stall events long enough for fuse and safety behavior to act
- A logic-level interface that works with STM32 3.3 V GPIO

## 2. H-Bridge Control Concept

An H-bridge is a switching circuit that can apply motor voltage in either
polarity.

Project meaning:

- Forward rotation is made by driving current through the motor one way.
- Reverse rotation is made by driving current through the motor the opposite
  way.
- Speed is controlled by PWM duty ratio.
- The MCU does not drive the motor directly; it commands the H-bridge.

MDD10A uses a sign-magnitude interface for the first MVP:

| Signal | Role |
| --- | --- |
| `PWM` | Speed duty control |
| `DIR` | Direction selection |

Generic model:

| Motor command | `PWM` | `DIR` | Meaning |
| --- | --- | --- | --- |
| Stop/coast candidate | 0 | don't care | No active drive |
| Forward | duty | forward polarity | Drive one direction |
| Reverse | duty | reverse polarity | Drive the opposite direction |

Firmware rule:

```text
Before changing direction, ramp PWM to zero, change DIR, then raise PWM again.
```

## 3. WHEELTEC Reference Finding

The local WHEELTEC material contains STM32 robot reference code and motor-driver
learning material.

Relevant findings:

- L130 reference programs target `STM32F103C8T6`.
- L150Pro reference programs target `STM32F407VET6`.
- The L150Pro program supports `Tank_Car`, which maps to a tracked vehicle
  mode.
- The program description says the programs are adapted for Hall encoder
  motors.
- The L150Pro standard-library source uses two PWM outputs per motor.

Project interpretation:

- WHEELTEC is useful as a drivetrain, encoder, and control-loop reference.
- The user's first board and driver do not need to follow the WHEELTEC
  dual-PWM output topology.
- With MDD10A, the high-level signed motor abstraction remains useful while the
  low-level output mapping becomes `PWM + DIR`.
- TB6612FNG is useful learning material, but it is too small to be the main
  driver for this tracked platform.

## 4. MDD10A Fit

MDD10A is the most practical first-driver choice for this project.

Key manufacturer-facing characteristics:

| Item | Value |
| --- | --- |
| Motor type | Two brushed DC motors |
| Motor voltage | 5 V to 30 V DC, Rev2.0 reference |
| Current | 10 A continuous per channel, 30 A peak for up to 10 seconds |
| Logic input | 3.3 V / 5 V logic input support |
| PWM mode | Sign-magnitude and locked-antiphase support |
| PWM frequency | Up to 20 kHz |

MDD10A input connector:

| Pin | Role |
| --- | --- |
| `GND` | Logic signal ground |
| `PWM2` | Motor 2 speed control |
| `DIR2` | Motor 2 direction |
| `PWM1` | Motor 1 speed control |
| `DIR1` | Motor 1 direction |

Motor and power terminal:

| Pin | Role |
| --- | --- |
| `M1A`, `M1B` | Motor 1 output |
| `POWER+`, `POWER-` | Motor power input |
| `M2A`, `M2B` | Motor 2 output |

Control mapping:

| State | `PWMx` | `DIRx` |
| --- | --- | --- |
| Unsafe / disarmed | 0 | don't care |
| Stop command | 0 | keep last or default |
| Forward | duty | forward mapping |
| Reverse | duty | reverse mapping |

Notes:

- MDD10A `PWM` is not RC receiver servo PWM.
- For inductive motor loads, design around battery operation.
- A switching power supply alone can be unsafe with regenerative current.
- MDD10A does not provide reverse-polarity protection on the motor supply, so
  power polarity must be checked before every early test.

## 5. Driver Option Comparison

| Driver | Interface style | Project fit |
| --- | --- | --- |
| TB6612FNG | PWM + direction pins, small DC motor driver | Good learning reference, too small for the main tracked drivetrain |
| BTS7960 module | Dual-PWM H-bridge style, usually one module per motor | Reasonable early candidate, now superseded by MDD10A for the first MVP |
| MDD10A | Two motors on one board, `PWM + DIR` per motor | Selected for the first drivetrain MVP |
| MDD20A | `PWM + DIR`, higher-current dual-channel driver | Follow-up candidate if measured MDD10A margin is not enough |

Why BTS7960 was considered:

- It is useful for H-bridge and dual-PWM learning.
- It offers more margin than a small TB6612FNG-class driver.
- It resembles the dual-PWM structure in the local WHEELTEC reference code.

Why MDD10A is selected:

- One board drives both motors.
- Two PWM outputs are enough for a two-motor drivetrain.
- The existing PB6/PB7 PWM and PC8/PC9 DIR candidate map stays practical.
- The validation path is simpler: MDD10A inspection, power bring-up,
  PWM/DIR logic test, then no-load motor test.
- The official logic input support fits STM32 3.3 V GPIO more directly.

Detailed comparison is recorded in
`20_Motor_Driver_Selection_Comparison.md`.

## 6. Electrical Interface Candidate

MDD10A first wiring contract:

```text
STM32 PWM_L -> MDD10A PWM1
STM32 DIR_L -> MDD10A DIR1
STM32 PWM_R -> MDD10A PWM2
STM32 DIR_R -> MDD10A DIR2
STM32 GND   -> MDD10A GND

3S LiPo +   -> fuse -> switch -> MDD10A POWER+
3S LiPo -   -> MDD10A POWER-

Left motor  -> MDD10A M1A / M1B
Right motor -> MDD10A M2A / M2B
```

Initial wiring rules:

- STM32 and MDD10A logic GND share a common reference.
- Motor current must not flow through perfboard copper traces.
- STM32 PWM pins must default to low or zero-duty during reset.
- DIR state alone must not create motor output while PWM is zero.
- If a separate hardware power gate or brake is added later, design it in the
  power path or external gate circuit rather than assuming an MDD10A enable pin.

Voltage compatibility:

- STM32 GPIO output is 3.3 V logic.
- MDD10A supports 3.3 V logic input.
- Still run a logic-only PWM/DIR test before connecting motor power.

## 7. Pin Allocation Impact

The first `06_MCU_Pin_Allocation_Candidate_ko.md` map fits MDD10A well.

MDD10A requirements:

- Left motor: `PWM1` + `DIR1`
- Right motor: `PWM2` + `DIR2`
- Two-motor drivetrain: two PWM-capable outputs plus two GPIO outputs

Candidate concept:

| Robot function | Candidate peripheral |
| --- | --- |
| Left motor PWM | `TIM4_CH1` / PB6 |
| Right motor PWM | `TIM4_CH2` / PB7 |
| Left motor DIR | GPIO / PC8 |
| Right motor DIR | GPIO / PC9 |
| Optional power gate or brake | Only if a separate circuit is added, candidate GPIO PC6/PC5 |

This is not the final pinout. Required checks:

- NUCLEO-F446RE header access
- CubeMX alternate-function mapping
- SWD pin preservation
- Encoder timer preservation
- I2C pins for BNO08x if practical
- Reset-safe output defaults

## 8. Firmware Control Rules

Firmware must treat motor-driver output as safety-critical.

Required rules:

1. Initialize all motor PWM compare values to zero.
2. Keep motor output at PWM zero during startup.
3. Allow nonzero PWM only after firmware initialization and arm checks pass.
4. Clamp motor commands to the configured PWM limit.
5. Apply acceleration and deceleration ramp limits.
6. Before changing direction, ramp PWM to zero, change `DIR`, then raise PWM.
7. Stop motors on command timeout.
8. Stop motors on low-voltage stop.
9. Stop motors before watchdog reset or fault handling if possible.
10. Force PWM zero and disarmed state on emergency stop.

Recommended motor command shape:

```c
void motor_set(int command)
{
    int duty = clamp_abs(command, PWM_LIMIT);

    if (!motor_output_allowed()) {
        pwm_set(0);
        return;
    }

    if (command == 0) {
        pwm_set(0);
        return;
    }

    if (direction_change_required(command)) {
        pwm_set(0);
        dir_set(command > 0 ? MOTOR_FORWARD : MOTOR_REVERSE);
    }

    pwm_set(duty);
}
```

Implementation notes:

- Change `DIR` only after PWM reaches zero.
- Handle sudden forward/reverse requests through a ramp-to-zero sequence.
- Final `DIR` mapping is confirmed after actual motor wiring and encoder sign
  tests.

## 9. Power and Safety Rules

Choosing MDD10A does not remove the need for power protection.

Required power path:

```text
3S LiPo
-> XT60
-> AWG14 fuse holder
-> blade fuse
-> DC-rated main switch
-> power distribution
   -> MDD10A motor power
   -> buck converters
```

Safety rules:

- Start bench tests with a 10 A or 15 A fuse.
- Increase fuse rating only after current measurements.
- Keep the 3S LiPo low-voltage alarm connected during LiPo operation.
- Disconnect the battery after every test.
- Do not route high-current motor power through perfboard traces.
- Keep motor power wiring away from encoder, I2C, and UART signal wires.
- Check MDD10A and motor temperature during every early test.
- Verify MDD10A POWER polarity before applying power.

Main switch requirement:

- The main switch must be DC-rated.
- Its current rating should be at least the planned fuse rating.
- A 12 V or 24 V DC switch around 30 A is the minimum practical target.
- A 40 A to 50 A DC-rated switch gives better margin for this tracked platform.

## 10. Validation Plan

### Stage 1: Logic-Only Test

- Disconnect motor power.
- Connect STM32 and MDD10A logic GND.
- Confirm PWM pins output the intended duty.
- Confirm DIR pins change for forward/reverse requests.
- Confirm DIR changes alone create no motor output while PWM is zero.

### Stage 2: No-Load Motor Test

- Connect one motor to one MDD10A channel.
- Start with low duty, such as 5% to 10%.
- Test forward, stop, and reverse.
- Confirm motor direction and encoder sign.
- Check board and motor temperature.

### Stage 3: Dual-Motor Bench Test

- Test left and right motors with wheels or tracks lifted.
- Confirm motor directions match robot convention.
- Confirm encoder signs match command signs.
- Test timeout stop and emergency stop.

### Stage 4: Low-Speed Chassis Test

- Place the robot on the floor.
- Use a low PWM limit.
- Test forward and backward first.
- Test turn-in-place last because tracked vehicles can draw high current while
  rotating.

### Stage 5: Closed-Loop Test

- Add encoder speed estimation.
- Add PI speed control.
- Add command timeout.
- Add voltage monitoring.
- Record current, heat, and motor response.

## 11. Open Questions

These items must be checked before final firmware implementation:

- Actual MDD10A revision and terminal labeling.
- Whether `PWM1/DIR1` maps to left or right.
- Final STM32 timer channel selection.
- Final PWM frequency.
- Motor stall current or measured worst-case current.
- Encoder voltage and signal quality.
- Whether MG540, JGB37-520, or another motor becomes the first drivetrain motor.
- Whether measured MDD10A current and heat margin are enough, or whether an
  MDD20A-class upgrade is needed.

## Architecture Decision

For the first drivetrain MVP, MDD10A is the active motor-driver path.

This decision replaces the earlier BTS7960 dual-PWM assumption with a
per-motor `PWM + DIR` interface. BTS7960 remains in the documentation as a
superseded alternative and design-evolution record, not as the current wiring
or firmware contract.

The next practical tasks are to validate the STM32 pin allocation in CubeMX,
run the MDD10A logic-only test, and complete the one-motor hardware validation
before testing the full tracked chassis.
