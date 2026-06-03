# STM32F446RE Datasheet Reading Map

## Purpose

This document records how to read the STM32F446xC/E datasheet for the tracked
mobile robot project.

The goal is not to summarize every feature of the MCU. The goal is to extract
engineering evidence for why the NUCLEO-F446RE can be used as the low-level
controller for motor control, encoder reading, battery monitoring, sensor
interface, and PC/ESP32 communication.

## Source

- Datasheet: `assets/stm32f446mc.pdf`
- Device family: STM32F446xC/E
- Project board: NUCLEO-F446RE
- Current reading stage: Contents and List of tables

## How to Read the Datasheet

The datasheet should be read as a reference map, not as a textbook.

For this project, the first pass should answer these questions:

1. Does the MCU have enough timers for PWM and encoder input?
2. Does the MCU have enough communication interfaces for UART, I2C, and future CAN?
3. Can the MCU safely interface with the selected sensors and motor driver signals?
4. Can the ADC be used for LiPo battery voltage monitoring?
5. What electrical limits must be respected to avoid damaging the board?

## Contents Structure

| Section | Meaning | Project relevance |
| --- | --- | --- |
| 1. Introduction | Defines the device family covered by the datasheet. | Check that STM32F446RE belongs to this datasheet scope. |
| 2. Description | Summarizes core, memory, and peripheral availability. | First evidence for MCU suitability. |
| 3. Functional overview | Explains MCU internal blocks and peripherals. | Main section for timer, ADC, UART, I2C, CAN, GPIO, DMA, and watchdog. |
| 4. Pinout and pin description | Lists package pins and alternate functions. | Used to assign motor, encoder, sensor, and communication pins. |
| 5. Memory mapping | Shows address layout for Flash, SRAM, and peripheral registers. | Useful later for low-level debugging and register-level understanding. |
| 6. Electrical characteristics | Defines voltage, current, timing, and operating limits. | Critical for safe wiring and interface design. |
| 7. Package information | Gives physical package dimensions and thermal information. | Low priority while using NUCLEO; important for custom PCB later. |
| 8. Part numbering | Explains STM32 part-name codes. | Helps verify exact MCU variant and Flash/package option. |
| Appendix A | USB application block diagrams. | Low priority for the initial robot MVP. |
| Revision history | Tracks datasheet changes. | Useful only when comparing document versions. |

## Project Priority by Section

### Must Read First

- Section 2: Description
- Section 3: Functional overview
- Section 4: Pinout and pin description
- Section 6: Electrical characteristics

These sections directly affect architecture, wiring, firmware design, and
safety.

### Read When Needed

- Section 5: Memory mapping
- Section 7: Package information
- Section 8: Part numbering
- Appendix A

These are useful, but they are not the first bottleneck for the MVP.

## Functional Overview Targets

Section 3 is large, so the project should focus on the peripherals that map to
real robot functions.

| Datasheet topic | Simple meaning | Robot usage |
| --- | --- | --- |
| Cortex-M4 / FPU | CPU core and floating-point unit. | Runs control loop and math for speed/odometry. |
| Flash / SRAM | Program memory and runtime memory. | Stores firmware and runtime variables. |
| DMA | Hardware data mover. | Later useful for efficient ADC/UART/SPI transfers. |
| NVIC / EXTI | Interrupt controller and external interrupt lines. | Encoder edges, emergency input, timing-sensitive events. |
| Clocks | MCU timing sources and frequency tree. | PWM frequency, UART baud rate, control loop timing. |
| Boot modes | Startup source selection. | Recovery/debugging if firmware upload fails. |
| Timers | Hardware counters and waveform generators. | PWM output, encoder mode, periodic control loop. |
| Watchdogs | Reset mechanism when firmware hangs. | Fail-safe for robot stop/recovery. |
| I2C | Two-wire sensor bus. | BNO08x IMU candidate interface. |
| USART/UART | Serial communication. | PC, ESP32, debug console, command protocol. |
| bxCAN | CAN controller. | Deferred expansion for robust robot bus. |
| GPIO | Digital input/output pins. | Motor driver direction, enable, switches, status inputs. |
| ADC | Analog-to-digital converter. | LiPo voltage monitoring through resistor divider. |
| SWD/JTAG | Debug/programming interface. | ST-LINK debugging and firmware upload. |

## Low Priority Features for the Initial MVP

The following features are valid MCU capabilities, but they are not central to
the first tracked robot MVP:

- FMC, PSRAM, SDRAM, QuadSPI
- I2S, SAI, SPDIF-RX, audio PLL
- HDMI CEC
- SDIO
- USB OTG HS
- DCMI camera interface
- DAC
- RTC calendar features

They can be revisited only if the project scope expands.

## Important Tables

The list of tables is important because design decisions should cite numbers,
not only descriptions.

| Table | Why it matters |
| --- | --- |
| Table 2. STM32F446xC/E features and peripheral counts | Checks number of timers, ADCs, UARTs, I2C, CAN, memory size, and package options. |
| Table 6. Timer feature comparison | Determines which timers can be used for PWM, input capture, output compare, and encoder-related work. |
| Table 7. Comparison of I2C analog and digital filters | Useful when checking I2C robustness for IMU wiring. |
| Table 8. USART feature comparison | Helps choose UART/USART for PC, ESP32, or debug links. |
| Table 10. Pin and ball descriptions | Maps physical pins to available signals. |
| Table 11. Alternate function | Shows which peripheral function can be assigned to each pin. |
| Table 13. Voltage characteristics | Defines voltage limits that must not be exceeded. |
| Table 14. Current characteristics | Defines current limits that must not be exceeded. |
| Table 16. General operating conditions | Defines normal operating voltage and temperature conditions. |
| Table 56. I/O static characteristics | Checks logic-level thresholds and 5 V-tolerant I/O behavior. |
| Table 60. TIMx characteristics | Checks timer-related timing limits. |
| Table 61. I2C characteristics | Checks electrical/timing constraints for I2C devices. |
| Table 63. SPI dynamic characteristics | Useful if an SPI sensor/display/storage device is added later. |
| Table 76. ADC characteristics | Critical for battery voltage measurement accuracy and input constraints. |
| Table 86. VBAT monitoring characteristics | Useful if VBAT-related monitoring becomes relevant later. |

## Reading Result for This Stage

The contents and table list show that the datasheet should be read in a
project-driven order:

1. Start with MCU capability: Section 2 and Table 2.
2. Move to robot-related peripherals: Section 3 and Tables 6, 7, 8.
3. Assign real pins: Section 4 and Tables 10, 11.
4. Validate electrical safety: Section 6 and Tables 13, 14, 16, 56, 60, 61, 76.

This is enough to move to the next reading stage.

## Next Reading Stage

Next target:

- Section 1: Introduction
- Section 2: Description
- Table 2: STM32F446xC/E features and peripheral counts

Questions to answer in the next stage:

1. Is STM32F446RE the correct target part for this board?
2. How much Flash and SRAM are available?
3. Which peripherals are available in enough quantity for this robot?
4. What features are useful now, and what features are deferred?
5. What evidence supports using STM32F446RE as the low-level controller?
