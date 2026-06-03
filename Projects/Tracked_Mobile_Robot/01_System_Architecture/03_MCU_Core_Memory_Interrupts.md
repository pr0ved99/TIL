# STM32F446RE Core, Memory, Interrupt, and Clock Analysis

## Purpose

This document analyzes the first project-relevant part of Section 3 Functional
overview in the STM32F446xC/E datasheet.

Scope:

- Section 3.1: Arm Cortex-M4 with FPU and embedded Flash/SRAM
- Section 3.2: ART Accelerator
- Section 3.3: MPU
- Section 3.4: Embedded Flash memory
- Section 3.5: CRC calculation unit
- Section 3.6: Embedded SRAM
- Section 3.7: Multi-AHB bus matrix
- Section 3.8: DMA controller
- Section 3.9: FMC
- Section 3.10: QuadSPI
- Section 3.11: NVIC
- Section 3.12: EXTI
- Section 3.13: Clocks and startup
- Section 3.14: Boot modes

The goal is to understand the MCU foundation before analyzing motor-control
timers, communication peripherals, GPIO, and ADC.

## 1. Core and Computation

### Cortex-M4 with FPU

The STM32F446RE uses an Arm Cortex-M4 CPU core with a single-precision FPU.

Important datasheet points:

- 32-bit RISC processor
- Designed for embedded systems
- Good interrupt response
- DSP instruction support
- Single-precision floating-point hardware
- Binary compatible with Cortex-M3

Project meaning:

- The CPU is strong enough for the initial low-level robot controller.
- Floating-point math can be used for speed, yaw-rate, PID, and odometry
  calculations.
- DSP support gives future room for filtering and sensor-processing work.

Practical interpretation:

- Use readable floating-point code first.
- Optimize only after measuring real loop time.
- Keep time-critical interrupt handlers short even though the CPU is fast.

### FPU

FPU means Floating Point Unit. It accelerates decimal-number calculations such
as `m/s`, `rad/s`, PID terms, and odometry estimates.

Robot usage:

- Convert encoder ticks to wheel speed.
- Calculate angular velocity.
- Compare IMU yaw rate with encoder-based yaw estimate.
- Implement PID control with readable equations.

Risk:

- FPU helps performance, but it does not remove the need for deterministic
  timing. The control loop should still run at a fixed period.

### DSP Instructions

DSP instructions are CPU instructions optimized for signal-processing patterns
such as multiply-accumulate operations.

Robot usage candidates:

- Encoder speed smoothing
- IMU signal filtering
- Current or voltage measurement filtering
- Future CMSIS-DSP based filtering

Initial decision:

- Do not design around DSP instructions at MVP stage.
- Keep this as future optimization headroom.

### MPU

MPU means Memory Protection Unit. It restricts access to memory regions so that
one task cannot accidentally corrupt another protected region.

Datasheet points:

- Up to 8 protected regions
- Each region can be divided into subregions
- Region sizes can range from 32 bytes to the whole 4 GB address space
- Usually managed by an RTOS
- Optional and can be bypassed

Project decision:

- Low priority for the initial bare-metal or HAL-based MVP.
- Revisit only if the project moves to RTOS-based firmware or stronger safety
  partitioning.

## 2. Program and Data Memory

### Embedded Flash Memory

The datasheet states that the device embeds 512 KB Flash memory for storing
programs and data.

Robot usage:

- Main firmware image
- Control logic
- Serial protocol code
- Calibration constants if stored in Flash

Initial judgment:

- 512 KB is enough for the initial motor-control firmware.
- It should also be enough for UART protocol handling, IMU parsing, and basic
  diagnostic logging code.

### ART Accelerator

ART means Adaptive Real-Time memory accelerator. It reduces the performance
penalty of executing code from Flash at high CPU frequencies.

Datasheet points:

- Optimized for Cortex-M4
- Uses instruction prefetch and branch cache
- Helps the CPU reach high performance from Flash
- The datasheet mentions 225 DMIPS and 0-wait-state-equivalent execution from
  Flash up to 180 MHz based on CoreMark-style performance

Project meaning:

- Firmware can run from internal Flash without treating Flash access as the main
  performance bottleneck.
- This supports a practical design where the control loop is compiled normally
  and executed from Flash.

Practical note:

- ART does not replace timing measurement.
- The control loop period should still be validated with GPIO toggling, timer
  capture, or trace/debug tools.

### Embedded SRAM

The STM32F446xC/E devices include:

- Up to 128 KB system SRAM
- 4 KB backup SRAM
- System SRAM is accessed at CPU clock speed with 0 wait states
- Backup SRAM can be retained in Standby or VBAT modes

Robot usage:

- Runtime variables
- Encoder counters and speed estimates
- UART receive buffers
- ADC sample buffers
- IMU data buffers
- Control state

Initial judgment:

- 128 KB is enough for the initial robot MVP.
- The project should still avoid large unnecessary buffers.
- Backup SRAM is not needed at the beginning.

## 3. Data Integrity and Data Movement

### CRC Calculation Unit

CRC means Cyclic Redundancy Check. It is a compact code used to detect data
corruption.

Datasheet points:

- Generates a CRC from a 32-bit data word and fixed polynomial
- Can verify data transmission or storage integrity
- Can help compute runtime software signatures

Robot usage candidates:

- Verify serial command packets later
- Verify stored calibration data
- Add firmware integrity checks in a more mature safety design

Initial decision:

- Not required for the first motor-control MVP.
- Useful later when the serial protocol becomes structured.

### DMA Controller

DMA means Direct Memory Access. It moves data between memory and peripherals
without the CPU copying every byte.

Datasheet points:

- Two general-purpose dual-port DMAs: DMA1 and DMA2
- Each DMA has 8 streams
- Supports memory-to-memory, peripheral-to-memory, and memory-to-peripheral
  transfers
- Supports circular buffer management
- Supports double buffering
- Can be used with SPI/I2S, I2C, USART, timers, DAC, SDIO, DCMI, ADC, SAI,
  SPDIF, and QuadSPI

Robot usage:

- UART receive buffer without losing bytes
- ADC sampling for battery voltage monitoring
- SPI or I2C sensor transfers if needed
- Timer-related data transfer in more advanced designs

Initial decision:

- Start simple with interrupt-based UART and polling/interrupt ADC if needed.
- Move to DMA when data loss, CPU overhead, or timing jitter becomes measurable.

Important design rule:

- DMA improves efficiency, but it also increases debugging complexity. Use it
  only when the simpler method has a real limitation.

## 4. Internal Bus Architecture

### Multi-AHB Bus Matrix

The multi-AHB bus matrix connects masters such as CPU, DMA, and USB HS to
slaves such as Flash, RAM, QuadSPI, FMC, AHB peripherals, and APB peripherals.

Simple interpretation:

- CPU, DMA, and peripherals share internal roads.
- The bus matrix helps multiple high-speed blocks work at the same time.

Project meaning:

- This is the reason DMA can move data while the CPU continues control logic.
- It matters more when UART, ADC, timers, and sensor interfaces are active
  together.

Initial decision:

- No direct firmware work is needed at this stage.
- Keep it as background knowledge for later performance debugging.

## 5. External Memory Features

### FMC

FMC means Flexible Memory Controller. It interfaces with external memories such
as SRAM, PSRAM, NOR Flash, NAND Flash, and SDRAM.

Project decision:

- Not needed for the initial robot MVP.
- Revisit only if a future design needs external memory or a parallel LCD.

### QuadSPI

QuadSPI is a high-speed interface for external SPI Flash memories. It can also
support memory-mapped external Flash access.

Project decision:

- Not needed for the initial robot MVP.
- Internal Flash is enough for the low-level controller.

## 6. Interrupt and Event Handling

### NVIC

NVIC means Nested Vectored Interrupt Controller. It manages interrupt priorities
and dispatches the CPU to the correct interrupt handler.

Datasheet points:

- 16 priority levels
- Up to 91 maskable interrupt channels
- 16 Cortex-M4 core interrupt lines
- Low-latency interrupt processing
- Supports late-arriving higher-priority interrupts
- Supports tail chaining
- Automatically saves and restores processor state

Robot usage:

- Periodic timer interrupt for the control loop
- USART receive interrupt for command reception
- EXTI interrupt for emergency button or low-rate external signals
- ADC interrupt for voltage monitoring if not using DMA

Design rule:

- Interrupt handlers must be short.
- Do not run long calculations, blocking delays, or heavy printing inside an
  interrupt handler.
- Set flags or push small data into buffers, then process in the main loop or a
  scheduled control task.

### EXTI

EXTI means External Interrupt/Event Controller. It detects edges on external
lines and generates interrupt or event requests.

Datasheet points:

- 23 edge-detector lines
- Rising edge, falling edge, or both-edge trigger selection
- Independent masking
- Pending register for request status
- Up to 114 GPIOs can connect to the 16 external interrupt lines in the full
  device family

Robot usage:

- Emergency stop button
- User button
- Limit switch
- Low-rate fault input from a driver

Encoder note:

- EXTI can count edges, but high-rate motor encoders are usually better handled
  by timer encoder mode.
- Timer encoder mode reduces CPU interrupt load and is more robust for motor
  control.

## 7. Clocks and Startup

### Default Clock

On reset, the 16 MHz internal RC oscillator is selected as the default CPU clock.
The datasheet states that this oscillator is factory-trimmed to 1% accuracy at
25 degrees Celsius.

Project meaning:

- The MCU can start without an external clock.
- Early boot and initial firmware tests can run from the internal oscillator.

### External Clock and PLL

The application can select either:

- Internal RC oscillator
- External 4 MHz to 26 MHz clock source

The clock can be monitored for failure. If failure is detected, the system can
switch back to the internal RC oscillator and generate a software interrupt if
enabled.

The PLL can increase the frequency up to 180 MHz.

Bus frequency limits:

- AHB maximum: 180 MHz
- APB2 maximum: 90 MHz
- APB1 maximum: 45 MHz

Project meaning:

- PWM frequency, UART baud rate, timer tick rate, and control-loop period all
  depend on clock configuration.
- Incorrect clock settings can cause wrong UART baud rate or wrong PWM timing.

Initial decision:

- Use CubeMX-generated clock configuration first.
- Record the actual system clock, APB1, and APB2 frequencies in firmware notes.
- Verify UART baud rate and PWM frequency with real tests.

## 8. Boot Modes

The device can boot from:

1. User Flash
2. System memory
3. Embedded SRAM

The bootloader is located in system memory and can reprogram Flash through
serial communication interfaces:

- UART
- I2C
- CAN
- SPI
- USB

Project meaning:

- Normal firmware boots from user Flash.
- System bootloader is useful for recovery or programming without the normal
  debug path.
- SRAM boot is useful for specialized debugging, but not needed initially.

Initial decision:

- Use the normal NUCLEO ST-LINK programming flow.
- Keep boot modes as recovery knowledge.

## 9. Architecture Impact for This Robot

The Section 3.1 to 3.14 reading supports these early architecture decisions:

1. STM32F446RE has enough computation headroom for low-level control.
2. Floating-point math is acceptable for initial PID and odometry work.
3. Interrupts should coordinate time-sensitive events, but handlers must stay
   short.
4. DMA is useful but should be introduced only when needed.
5. Timer encoder mode should be preferred over EXTI for motor encoder counting.
6. Clock configuration must be recorded because timers and USART depend on it.
7. Bootloader knowledge is useful for recovery, but not central to MVP design.

## 10. Open Questions for the Next Stage

The next analysis should focus on timers and watchdogs.

Questions:

1. Which timers support PWM output?
2. Which timers support encoder mode?
3. Which timer channels are exposed on NUCLEO-F446RE usable pins?
4. Which timer should run the fixed-period control loop?
5. Which watchdog should be used for fail-safe recovery?
6. How should control-loop timing be measured and verified?
