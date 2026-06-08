# Tracked Mobile Robot Project Memory

This file stores stable project facts so future work does not repeat the same questions.

Last updated: 2026-06-08

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
- `11_System_Block_Diagram_and_Interface_Map_ko.md`: full hardware/software interface map
- `14_CAN_Bus_Integration_Plan_ko.md`: CAN ID and frame plan
- `16_Control_Loop_and_State_Machine_ko.md`: safety state machine and motor output rules
- `19_Architecture_Decision_Record_ko.md`: accepted, deferred, superseded decisions
- `02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md`: first MDD10A logic validation plan

## Current Progress Snapshot

- ROS 2 Humble, RViz2, and Gazebo classic 11 were installed and basic execution was verified on the laptop.
- ROS 2 A-to-Z learning map and practice paths were added.
- NUCLEO-F446RE CAN A-to-Z learning map and practice paths were added.
- NUCLEO-F446RE FreeRTOS A-to-Z learning map and practice paths were added.
- System architecture was updated to make MDD10A the first motor driver path.
- MDD10A logic validation replaced BTS7960 logic validation.
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
