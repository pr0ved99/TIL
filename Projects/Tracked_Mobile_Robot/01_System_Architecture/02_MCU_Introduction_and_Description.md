# STM32F446RE Introduction and Description Analysis

## Purpose

This document analyzes the following parts of the STM32F446xC/E datasheet and
records the first suitability check for using the NUCLEO-F446RE as the
low-level controller of the tracked mobile robot.

- Section 1: Introduction
- Section 2: Description
- Table 2: STM32F446xC/E features and peripheral counts

## 1. What the Introduction Confirms

The Introduction is short, but it gives an important premise.

The STM32F446xC/E datasheet describes an Arm Cortex-M4 based device family.
However, the datasheet alone is not enough to implement firmware. The datasheet
mainly provides specifications, pins, package information, and electrical
limits. The actual behavior and register-level configuration of each peripheral
must be checked in separate documents.

The relevant documents have different roles.

| Document | Role | Project use |
| --- | --- | --- |
| Datasheet | Provides chip features, pins, electrical limits, and package information. | MCU suitability check, pin selection, voltage/current limit checks. |
| RM0390 Reference Manual | Explains peripheral registers and behavior for timers, ADC, UART, and other blocks. | STM32 firmware design and debugging. |
| PM0214 Cortex-M4 Programming Manual | Explains the Cortex-M4 core, instructions, exceptions, and interrupt behavior. | Interrupts, SysTick, and low-level debugging. |

### Interpretation

This project does not need to read the entire reference manual from the start.
However, once Timer, ADC, UART, I2C, or CAN is actually used, the datasheet is
not enough. RM0390 must be checked together with the datasheet.

## 2. Key Summary from the Description

The STM32F446xC/E family is based on an Arm Cortex-M4 32-bit MCU core operating
up to 180 MHz. The STM32F446RE used on the NUCLEO-F446RE belongs to this family.

The Description section lists the following project-relevant features:

- Up to 180 MHz Cortex-M4 CPU
- Single-precision FPU
- DSP instructions
- MPU
- Flash memory up to 512 KB
- SRAM up to 128 KB
- Backup SRAM 4 KB
- Three 12-bit ADCs
- Twelve general-purpose 16-bit timers
- Two PWM timers for motor control
- Two general-purpose 32-bit timers
- Up to four I2C interfaces
- Four USARTs plus two UARTs
- Two CAN interfaces
- Operating voltage should generally be treated as 1.8 V to 3.6 V

## Key Terms

### Cortex-M4

Cortex-M4 is an MCU CPU core designed by Arm. In simple terms, it is the central
processing unit inside the STM32 that executes firmware instructions.

Project meaning:

- Runs the periodic PWM control loop.
- Reads encoder values and estimates speed.
- Runs PID control, odometry calculation, and IMU data processing.

### FPU

FPU means Floating Point Unit. It is hardware that accelerates floating-point
math.

Project meaning:

- Useful when calculating physical values such as `m/s` and `rad/s`.
- Makes PID calculation, IMU yaw-rate handling, and odometry calculation easier.

Notes:

- Having an FPU does not mean every calculation should blindly use `float`.
- For very short control periods, fixed-point or integer-based computation can
  still be more deterministic.
- A practical approach is to start with readable floating-point code, then
  optimize only if performance becomes a real issue.

### DSP Instructions

DSP instructions are CPU instructions optimized for signal-processing style
operations such as multiply-accumulate and saturation arithmetic.

Project meaning:

- Useful for filtering, sensor data handling, and control algorithms.
- For example, they can help with moving-average filtering of encoder speed or
  IMU signal processing.

The initial MVP will probably not use DSP instructions directly. However, if a
library such as CMSIS-DSP is used later, these instructions can become useful.

### MPU

MPU means Memory Protection Unit. It can restrict access permissions for memory
regions.

Project meaning:

- Rarely used in an initial bare-metal or HAL-based firmware project.
- Becomes more relevant if the firmware grows into an RTOS-based or
  safety-oriented structure.

Current judgment:

- Low priority for the initial MVP.

### APB, AHB, and Multi-AHB Bus Matrix

APB and AHB are internal MCU buses that allow the CPU, memory, and peripherals
to exchange data.

Simple view:

- AHB: a high-speed internal road
- APB: a road toward peripherals such as timers, UART, and I2C
- Multi-AHB bus matrix: an internal interconnect that allows multiple masters
  and peripherals to access the bus structure efficiently

Project meaning:

- These buses form the foundation for how Timer, ADC, UART, and DMA communicate
  with the CPU.
- CubeMX and HAL hide most of this complexity at the beginning.
- This becomes more important when DMA, high-rate ADC, or multiple UART streams
  are used at the same time.

## 3. F446RE-Specific Extraction from Table 2

The NUCLEO-F446RE should be treated as an STM32F446RE target. Based on Table 2,
the key STM32F446RE specifications are:

| Item | STM32F446RE value | Project judgment |
| --- | --- | --- |
| Flash | 512 KB | Enough for low-level control firmware, UART protocol handling, and IMU processing. |
| System SRAM | 128 KB, structured as 112 KB + 16 KB | Enough for motor control, encoder handling, ADC processing, and IMU buffers. |
| Backup SRAM | 4 KB | Not important for the initial MVP. |
| General-purpose timers | 10 | Enough for PWM, encoder-related timing, and periodic control tasks. |
| Advanced-control timers | 2 | Suitable for motor-control-oriented PWM. |
| Basic timers | 2 | Can be used for periodic events or DAC triggers. |
| SPI / I2S | 4 SPI / 3 I2S | SPI expansion is available; I2S is not needed initially. |
| I2C | 4, including 1 FMP+ | Enough for a BNO08x IMU connection. |
| USART / UART | 4 USART + 2 UART | PC, ESP32, and debug communication can be separated. |
| USB OTG FS | Supported | Must be distinguished from the ST-LINK virtual COM port on the NUCLEO board. |
| USB OTG HS | Supported | Low priority for the initial MVP. |
| CAN | 2 | CAN can be deferred while keeping future expansion possible. |
| SDIO | Supported | Not needed initially. |
| QuadSPI | Limited feature support in LQFP64 | Not needed initially. |
| Camera interface | Supported | Not needed initially. |
| GPIO | About 50 pins for the F446RE package | Likely enough for motors, encoders, UART, I2C, and ADC, but pin conflicts must be checked. |
| 12-bit ADC | 3 ADCs, 16 channels for the F446RE package | Enough for battery voltage and optional analog sensing. |
| 12-bit DAC | 2 channels | Not needed for the initial MVP. |
| Maximum CPU frequency | 180 MHz | Sufficient headroom for a low-level controller. |
| Operating voltage | 1.8 V to 3.6 V | The actual board design should be treated as a 3.3 V logic system. |
| Package | LQFP64 | Pin-count limitations must be considered. |

## 4. Matching Against Robot Requirements

### Motor PWM Control

Requirements:

- Left/right motor PWM outputs
- Direction-control GPIO
- Enable or brake-control GPIO

Judgment from Table 2:

- The MCU has 2 advanced-control timers and 10 general-purpose timers, so PWM
  resources are sufficient in principle.
- Actual usability must be checked with Table 11, the alternate function table,
  and the NUCLEO board pinout.

### Encoder Input

Requirements:

- Left/right motor encoder A/B channels
- Preferably use hardware timer encoder mode

Judgment from Table 2:

- The timer count is sufficient.
- Whether a specific timer supports encoder mode must be checked in Table 6 and
  RM0390.
- Pin mapping must confirm that `TIMx_CH1` and `TIMx_CH2` for the same timer are
  available on usable board pins.

### Battery Voltage Monitoring

Requirements:

- Measure 3S LiPo voltage through a resistor divider and ADC input
- Limit motor output or stop the robot when low-voltage threshold is reached

Judgment from Table 2:

- Three 12-bit ADCs and 16 ADC channels for the F446RE package are sufficient.
- 3S LiPo voltage must never be connected directly to an MCU pin.
- The voltage must be divided down below the ADC input limit, normally below
  the 3.3 V logic range.
- The detailed ADC input conditions must be checked in Table 76 and Section 6
  electrical characteristics.

### BNO08x IMU Connection

Requirements:

- Candidate connection through I2C, UART, or SPI

Judgment from Table 2:

- Four I2C interfaces provide enough room for an I2C-based IMU connection.
- Four SPI interfaces also make SPI possible.
- I2C is simpler for initial wiring, but SPI can be considered if I2C stability
  becomes a problem.

### PC / ESP32 Communication

Requirements:

- Receive velocity commands from a PC
- Allow possible communication with ESP32-S3
- Output debug logs

Judgment from Table 2:

- Four USARTs plus two UARTs are sufficient.
- PC debug, ESP32 link, and an external serial module can be separated if
  needed.
- The actual UART choice must be checked against the NUCLEO schematic and
  board pinout.

### CAN Expansion

Requirements:

- Excluded from the initial MVP
- Considered later as a more robust internal robot bus

Judgment from Table 2:

- The MCU has two CAN controllers, so future CAN expansion is supported.
- The STM32 CAN controller cannot be connected directly to the CAN bus.
- A separate CAN transceiver is required for real CAN communication.

## 5. Important Notes

### 1. MCU Operating Voltage and Board Power Must Be Separated

Table 2 lists the operating voltage as 1.8 V to 3.6 V. In practice, the NUCLEO
board and ordinary STM32 GPIO design should be treated as a 3.3 V system.

Warnings:

- Do not connect 3S LiPo directly to the STM32.
- A 5 V signal is not safe for every pin.
- 5 V-tolerant behavior must be checked per pin using Table 10, Table 11, and
  Section 6.

### 2. F446RE Has Fewer Pins Than Larger F446 Packages

The F446RE uses an LQFP64 package. It has fewer GPIO pins and fewer exposed ADC
channels than larger F446 variants.

Meaning:

- The MCU may have enough internal peripherals, but not every peripheral signal
  is available on external pins.
- CubeMX may report peripheral conflicts.
- PWM, encoder, UART, I2C, and ADC pin allocation must be checked together.

### 3. The Datasheet Is Not a Sufficient Condition

The fact that Table 2 lists enough timers does not automatically prove that
encoder input will work.

Additional checks:

- Does the selected timer support encoder mode?
- Are the required channels available as `CH1` and `CH2` of the same timer?
- Are those pins actually available on the NUCLEO board?
- Do they conflict with ST-LINK, Arduino headers, or Morpho headers?

## 6. First Suitability Judgment

STM32F446RE is suitable as the initial low-level controller for this project.

Evidence:

1. The 180 MHz Cortex-M4 with FPU is enough for motor control and basic odometry
   calculation.
2. 512 KB Flash and 128 KB SRAM are sufficient for the initial firmware size.
3. The timer count is enough for PWM, encoder-related timing, and periodic
   control tasks.
4. Three 12-bit ADCs and multiple ADC channels allow battery voltage monitoring.
5. USART/UART resources are enough to separate PC, ESP32, and debug
   communication.
6. I2C and SPI are both available for BNO08x IMU connection choices.
7. Two CAN controllers provide future expansion room.

However, this suitability judgment is not final until the following items are
validated:

- PWM, encoder, UART, I2C, and ADC can be assigned without pin conflicts on the
  NUCLEO-F446RE.
- Motor driver input voltage is compatible with STM32 GPIO output voltage.
- Encoder output voltage does not exceed STM32 input limits.
- The ADC battery measurement circuit satisfies electrical limits.

## Next Stage

Next, read the project-relevant parts of Section 3 Functional overview in this
order:

1. Cortex-M4 / FPU / Flash / SRAM
2. DMA
3. NVIC / EXTI
4. Clocks and startup
5. Timers and watchdogs
6. I2C
7. USART/UART
8. bxCAN
9. GPIO
10. ADC

After that, use Table 6, Table 10, and Table 11 to create real pin allocation
candidates.
