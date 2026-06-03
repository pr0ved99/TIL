# Motor Driver and H-Bridge Control Decision

## Purpose

This document defines the first motor-driver decision for the tracked mobile
robot project and explains how the selected driver should be controlled from
STM32.

The goal is to connect the drivetrain decision to the previous MCU analysis:

- STM32 owns deterministic low-level motor control.
- The motor driver must handle high-current DC motor power.
- Firmware must enforce safe H-bridge control rules.
- The initial pin allocation must be revised for the selected driver interface.

## Decision Summary

Use BTS7960-class H-bridge motor driver modules for the first drivetrain MVP.

Initial decision:

- Use one BTS7960 module per DC motor.
- Use two modules for left/right tracked drivetrain.
- Control each motor with dual PWM inputs: `RPWM` and `LPWM`.
- Keep enable lines under STM32 control instead of tying them permanently high.
- Start with low-duty bench tests before chassis testing.

Rejected for the first MVP:

- TB6612FNG as the main drivetrain driver.
- Direct motor drive from MCU GPIO.
- CAN-based motor control.
- ESP32-S3 as the primary motor controller.

## Sources

Project sources:

- `00_Project_Charter/02_Component_Inventory.md`
- `00_Project_Charter/03_Initial_Purchase_and_Safety.md`
- `01_System_Architecture/04_MCU_Timers_and_Watchdogs.md`
- `01_System_Architecture/06_MCU_Pin_Allocation_Candidate.md`
- `01_System_Architecture/07_ESP32S3_Features_and_Project_Role.md`

Local WHEELTEC reference material:

- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../2._Smart_Robot_Car_Chassis_Development_Reference_Programs/4.STM32F407VET6_L150Pro_Robot_Car_Standard_Library_Version_2023.07.28.zip`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/1._Servo_DC_Motor_Development_Notes/5._DC_Motor_Control_and_TB6612FNG.pdf`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/2._Motor_Control_Basics_Video_Tutorial_and_Source_Code/1._PID_Basics_Intro_DC_Motor_and_TB6612/TB6612_Motor_Driver_Included_Materials/3.TB6612FNG_Module_Schematic.pdf`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/7._Common_Chip_Datasheets_Datasheet/`

## 1. Motor Driver Requirement

The motor driver must bridge the gap between logic-level MCU signals and
high-current motor power.

STM32 can provide:

- PWM logic signals
- Enable or disable GPIO signals
- Direction logic
- Control-loop timing

STM32 cannot provide:

- Motor current
- Motor voltage directly from GPIO
- Inductive load protection by itself
- Power-stage heat dissipation

The driver must therefore handle:

- 3S LiPo motor voltage range
- Motor start-up current
- Load spikes from tracked drivetrain friction
- Motor stall or near-stall conditions long enough for fuse/safety behavior
- Logic-level interface from STM32

## 2. H-Bridge Control Concept

An H-bridge is a switching circuit that can apply motor voltage in either
polarity.

Project meaning:

- Forward rotation is made by driving current through the motor one way.
- Reverse rotation is made by driving current through the motor the opposite
  way.
- Speed is controlled by PWM duty ratio.
- The MCU does not drive the motor directly; it only commands the H-bridge.

For a dual-PWM H-bridge interface, each motor is controlled by two PWM-capable
logic inputs.

Generic model:

| Motor command | Input A | Input B | Meaning |
| --- | --- | --- | --- |
| Stop/coast candidate | 0 | 0 | No active drive |
| Forward | PWM duty | 0 | Drive in one direction |
| Reverse | 0 | PWM duty | Drive in opposite direction |
| Forbidden for MVP | PWM duty | PWM duty | Avoid simultaneous drive commands |

The final electrical behavior depends on the driver module, but the firmware
rule for this project is simple:

```text
Never command both direction PWM inputs active at the same time.
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

The L150Pro motor source defines four motors, each with two PWM channels:

| Motor | PWM input 1 | PWM input 2 |
| --- | --- | --- |
| A | `PB8 / TIM10_CH1` | `PB9 / TIM11_CH1` |
| B | `PE5 / TIM9_CH1` | `PE6 / TIM9_CH2` |
| C | `PE11 / TIM1_CH2` | `PE9 / TIM1_CH1` |
| D | `PE14 / TIM1_CH4` | `PE13 / TIM1_CH3` |

The source code applies opposite-side PWM depending on motor command sign.

Project interpretation:

- The WHEELTEC architecture is close to a dual-PWM H-bridge control model.
- It is useful as a control architecture reference.
- It does not prove that the user's R3 chassis uses MG540 motors.
- It does not prove the exact driver IC on the WHEELTEC main board from source
  alone.
- TB6612FNG material exists, but TB6612FNG is not suitable as the main driver
  for this project's heavier tracked drivetrain.

## 4. BTS7960 Fit

BTS7960-class modules are a practical fit for the current project direction.

Typical BTS7960 module interface:

| Pin | Role |
| --- | --- |
| `RPWM` | PWM input for one motor direction |
| `LPWM` | PWM input for the opposite motor direction |
| `R_EN` | Enable input for one side |
| `L_EN` | Enable input for the other side |
| `VCC` | Logic supply |
| `GND` | Logic and power reference |
| `B+`, `B-` | Motor power input |
| `M+`, `M-` | Motor output |

Control mapping:

| Motion state | `RPWM` | `LPWM` | `R_EN` / `L_EN` |
| --- | --- | --- | --- |
| Disabled | 0 | 0 | 0 |
| Stop/coast candidate | 0 | 0 | 1 |
| Forward | duty | 0 | 1 |
| Reverse | 0 | duty | 1 |
| Emergency stop | 0 | 0 | 0 |

This is similar to the WHEELTEC dual-PWM idea:

```text
positive command -> PWM channel A active, PWM channel B off
negative command -> PWM channel A off, PWM channel B active
zero command     -> both PWM channels off
```

## 5. Driver Option Comparison

| Driver | Interface style | Project fit |
| --- | --- | --- |
| TB6612FNG | PWM + direction pins, small DC motor driver | Good learning reference, too small for the main tracked drivetrain |
| BTS7960 module | Dual PWM H-bridge style | Selected for first drivetrain MVP |
| MDD10A | PWM + DIR, integrated dual-channel driver | Clean option, but interface differs from WHEELTEC dual-PWM style |
| MDD20A | PWM + DIR, higher-current dual-channel driver | Strong option if cost/space are acceptable, but not selected for the first BTS-based path |

Decision:

- Use BTS7960 first because it matches the dual-PWM H-bridge learning path and
  provides more practical current margin than TB6612FNG-class modules.
- Keep MDD20A as a future replacement option if BTS7960 module quality, heat,
  or wiring complexity becomes a problem.

## 6. Electrical Interface Candidate

For each motor:

```text
STM32 PWM_CH_A -> BTS7960 RPWM
STM32 PWM_CH_B -> BTS7960 LPWM
STM32 GPIO     -> BTS7960 R_EN and L_EN
STM32 GND      -> BTS7960 GND
3S LiPo +      -> fuse -> switch -> BTS7960 B+
3S LiPo -      -> BTS7960 B-
Motor leads    -> BTS7960 M+ / M-
```

Recommended initial wiring rule:

- Use one enable GPIO per BTS7960 module.
- Tie `R_EN` and `L_EN` together only if the module documentation and bench
  test confirm this is acceptable.
- Add an external pull-down on enable so the driver remains disabled while STM32
  resets.
- Keep motor current wiring off perfboard copper traces.
- Use common ground between STM32 and BTS7960 logic ground.

Voltage compatibility check:

- STM32 GPIO outputs are 3.3 V logic.
- Confirm the actual BTS7960 module recognizes 3.3 V logic reliably.
- If not, add a level shifter or transistor buffer.

## 7. Pin Allocation Impact

The previous pin allocation candidate assumed one PWM signal plus direction and
enable GPIO per motor.

BTS7960 changes the requirement:

- Left motor needs `RPWM` and `LPWM`.
- Right motor needs `RPWM` and `LPWM`.
- Therefore the two-motor drivetrain needs four PWM-capable outputs.

Preferred STM32 timer direction:

- Use four channels from one timer if practical.
- A strong candidate is `TIM8_CH1` through `TIM8_CH4`, if CubeMX and board pin
  access confirm availability.

Candidate concept:

| Robot function | Candidate peripheral |
| --- | --- |
| Left motor RPWM | `TIM8_CH1` |
| Left motor LPWM | `TIM8_CH2` |
| Right motor RPWM | `TIM8_CH3` |
| Right motor LPWM | `TIM8_CH4` |
| Left BTS7960 enable | GPIO with external pull-down |
| Right BTS7960 enable | GPIO with external pull-down |

This is not final pinout.

Checks required:

- Confirm NUCLEO-F446RE board header access.
- Confirm CubeMX alternate-function mapping.
- Preserve SWD pins.
- Preserve encoder timers.
- Preserve I2C pins for BNO08x if possible.
- Confirm reset default states are safe.

## 8. Firmware Control Rules

The firmware must treat the motor driver as a safety-critical output.

Required rules:

1. Initialize all motor PWM compare values to zero.
2. Keep driver enable low during startup.
3. Enable the driver only after firmware initialization passes.
4. Clamp motor command to a configured PWM limit.
5. Apply acceleration and deceleration ramp limits.
6. Never make `RPWM` and `LPWM` active at the same time.
7. Stop motors if command timeout occurs.
8. Stop motors if low-voltage condition is detected.
9. Stop motors before watchdog reset or fault handling if possible.
10. Disable driver enable on emergency stop.

Recommended motor command function:

```c
void motor_set(int command)
{
    int duty = clamp_abs(command, PWM_LIMIT);

    if (!motor_output_allowed()) {
        rpwm_set(0);
        lpwm_set(0);
        enable_set(0);
        return;
    }

    enable_set(1);

    if (command > 0) {
        rpwm_set(duty);
        lpwm_set(0);
    } else if (command < 0) {
        rpwm_set(0);
        lpwm_set(duty);
    } else {
        rpwm_set(0);
        lpwm_set(0);
    }
}
```

Implementation note:

- Set the inactive PWM channel to zero before increasing the active PWM channel.
- For direction changes, ramp to zero first, then switch direction.

## 9. Power and Safety Rules

The BTS7960 decision does not remove the need for power protection.

Required power path:

```text
3S LiPo
-> XT60
-> AWG14 fuse holder
-> blade fuse
-> DC-rated main switch
-> power distribution
   -> BTS7960 motor power
   -> buck converters
```

Safety rules:

- Start bench tests with 10A or 15A fuse.
- Increase fuse rating only after current measurements.
- Keep low-voltage alarm connected during LiPo operation.
- Disconnect battery after every test.
- Do not run high-current motor power through perfboard traces.
- Keep motor power wires away from encoder, I2C, and UART signal wires.
- Check BTS7960 heat during every early test.

Main switch requirement:

- The main power switch should be DC-rated.
- Its current rating should be at least equal to the planned fuse rating.
- A 12 V or 24 V DC switch rated around 30 A is the minimum practical target.
- A 40 A to 50 A DC-rated switch gives better margin for this tracked platform.

## 10. Validation Plan

### Stage 1: Logic-Only Test

- Disconnect motor power.
- Power only STM32 and BTS7960 logic side if needed.
- Confirm enable defaults to disabled.
- Confirm PWM pins output expected duty.
- Confirm `RPWM` and `LPWM` are never active together.

### Stage 2: No-Load Motor Test

- Connect one motor and one BTS7960.
- Use low bench duty, such as 5% to 10%.
- Test forward, stop, reverse.
- Confirm motor direction and encoder sign.
- Check module temperature.

### Stage 3: Dual-Motor Bench Test

- Test left and right motors with wheels or tracks lifted.
- Confirm both motor directions match robot convention.
- Confirm encoder signs match command signs.
- Test emergency stop.

### Stage 4: Low-Speed Chassis Test

- Place the robot on the floor.
- Use low PWM limits.
- Test forward/backward.
- Test turn-in-place last because tracked vehicles can draw high current during
  rotation.

### Stage 5: Closed-Loop Test

- Add encoder speed estimation.
- Add PI speed control.
- Add command timeout.
- Add voltage monitoring.
- Record current, heat, and motor response.

## 11. Open Questions

These items must be checked before final firmware implementation:

- Exact BTS7960 module logic input threshold.
- Whether `R_EN` and `L_EN` should be tied or controlled separately.
- Final STM32 timer channel selection.
- Final PWM frequency.
- Motor stall current or measured worst-case current.
- Encoder voltage and signal quality.
- Whether MG540 or JGB37-520 becomes the first drivetrain motor.

## Architecture Decision

For the first drivetrain MVP, BTS7960 is selected as the motor driver path.

This decision changes the motor control interface from the earlier one-PWM plus
direction assumption to a dual-PWM H-bridge interface.

The next architecture task is to revise the STM32 pin allocation and then build
the hardware validation plan around one BTS7960 module and one motor before
testing the full tracked chassis.
