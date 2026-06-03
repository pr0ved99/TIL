# STM32F446RE Communication and I/O Peripheral Analysis

## Purpose

This document analyzes the communication, GPIO, ADC, and debug-related
peripherals in the STM32F446xC/E datasheet for the tracked mobile robot project.

Scope:

- Section 3.22: I2C
- Section 3.23: USART/UART
- Section 3.24: SPI
- Section 3.32: bxCAN
- Section 3.36: GPIO
- Section 3.37: ADC
- Section 3.40: SWJ-DP

The goal is to decide how STM32F446RE can interface with the BNO08x IMU, PC,
ESP32-S3, motor driver, battery monitor circuit, and future CAN expansion.

## 1. Project I/O Requirements

The initial tracked robot MVP needs the following MCU interfaces:

| Robot function | Likely MCU peripheral |
| --- | --- |
| PC command and debug log | USART/UART, or ST-LINK virtual COM port path |
| ESP32-S3 support controller link | USART/UART |
| BNO08x IMU | I2C first, SPI/UART as alternatives |
| Motor driver direction/enable/brake | GPIO |
| Motor speed command | Timer PWM, assigned in the timer document |
| Encoder input | Timer encoder mode, assigned in the timer document |
| 3S LiPo voltage monitoring | ADC through resistor divider |
| Future robust robot bus | bxCAN plus external CAN transceiver |
| Firmware flashing/debugging | SWD through ST-LINK |

## 2. I2C

I2C is a two-wire serial bus using SCL and SDA. It is commonly used for sensors.

Datasheet points:

- Four I2C bus interfaces
- Multimaster and slave modes
- Three I2C interfaces support standard mode up to 100 kHz and fast mode up to
  400 kHz
- One I2C interface supports standard mode, fast mode, and fast mode plus up to
  1 MHz
- 7-bit and 10-bit addressing support
- 7-bit dual addressing support in slave mode
- Hardware CRC generation/verification
- DMA support
- SMBus 2.0 / PMBus support
- Programmable analog and digital noise filters

### Project Use

The first candidate use is the BNO08x IMU.

Advantages:

- Simple wiring: SCL, SDA, power, ground
- Enough interface count for one IMU
- Noise filtering support can help with practical wiring robustness

Risks:

- I2C is sensitive to pull-up resistance, cable length, capacitance, and noise.
- Motor wiring and switching noise can disturb sensor communication.
- I2C is a shared bus, so one unstable device can affect the bus.

Design notes:

- Keep I2C wires short.
- Route I2C away from motor power wires.
- Use proper pull-ups to the correct logic voltage.
- Start at 100 kHz or 400 kHz before trying faster modes.

Initial decision:

- Use I2C as the first BNO08x interface candidate.
- Keep SPI or UART as fallback options if I2C reliability becomes a problem.

## 3. USART / UART

USART means Universal Synchronous/Asynchronous Receiver Transmitter. UART means
Universal Asynchronous Receiver Transmitter.

Simple distinction:

- UART supports asynchronous serial communication.
- USART supports asynchronous serial communication and can also support
  synchronous modes.
- In this project, USART peripherals will mostly be used in UART-style TX/RX
  mode.

Datasheet points:

- Six serial interfaces are listed in Table 8:
  - USART1
  - USART2
  - USART3
  - UART4
  - UART5
  - USART6
- USART1 and USART6 can reach higher maximum baud rates because they are mapped
  to APB2.
- USART2, USART3, UART4, and UART5 are mapped to APB1.
- All interfaces support asynchronous communication.
- Features include IrDA, multiprocessor communication, single-wire half-duplex,
  LIN, and DMA support.
- USART1, USART2, USART3, and USART6 also support CTS/RTS, Smart Card mode, and
  SPI-like communication.

### Project Use

Main uses:

- PC velocity command input
- Debug log output
- ESP32-S3 communication
- Future serial bridge to ROS2 or a PC-side tool

Recommended early use:

- Start with one serial channel for PC command and debug.
- Add a second serial channel for ESP32-S3 only when the need is clear.

Typical initial configuration:

- 115200 baud
- 8 data bits
- No parity
- 1 stop bit
- No flow control

This is commonly written as `115200 8N1`.

### Design Notes

Do not confuse logic-level UART with RS-232.

- STM32 UART pins are logic-level signals, typically 3.3 V.
- RS-232 voltage levels must not be connected directly to STM32 pins.
- USB-to-serial adapters must be checked for 3.3 V logic compatibility.

Use interrupts first:

- Interrupt-based receive is simpler than DMA.
- DMA receive can be added later if the serial protocol becomes high-rate or if
  bytes are lost.

Protocol recommendation:

- Start with a simple text command protocol.
- Move to binary packets with CRC only after basic motion tests work.

## 4. SPI

SPI is a synchronous serial interface using a clock line, data lines, and a chip
select signal.

Datasheet points:

- Up to four SPI peripherals
- Master and slave modes
- Full-duplex and simplex communication
- SPI1 and SPI4 up to 45 Mbit/s
- SPI2 and SPI3 up to 22.5 Mbit/s
- 8-bit or 16-bit frame format
- Hardware CRC generation/verification
- DMA support

### Project Use

SPI is not required for the first MVP, but it is useful as an alternative sensor
interface.

Candidate uses:

- BNO08x IMU fallback interface if supported by the module
- Future high-rate sensor
- Display or external storage

I2C vs SPI:

- I2C uses fewer wires and is simpler for low-rate sensors.
- SPI uses more wires but can be faster and more robust for some modules.

Initial decision:

- Do not use SPI first unless the IMU breakout or sensor module makes SPI easier
  than I2C.
- Reserve SPI as an expansion interface.

## 5. bxCAN

bxCAN is the STM32 CAN controller. CAN is a differential, multi-node bus often
used in vehicles and industrial systems.

Datasheet points:

- Two CAN controllers
- CAN 2.0A and 2.0B active support
- Bitrate up to 1 Mbit/s
- Standard 11-bit identifiers
- Extended 29-bit identifiers
- Three transmit mailboxes per CAN
- Two receive FIFOs with 3 stages
- 28 shared scalable filter banks
- 256 bytes SRAM allocated for each CAN

### Project Use

CAN is explicitly deferred for the MVP, but the MCU supports future expansion.

Possible future uses:

- Robust link between STM32 and another controller
- Distributed motor controller or sensor nodes
- Cleaner wiring for multi-node robot electronics

Important hardware note:

- The STM32 contains a CAN controller, not a complete physical CAN interface.
- A CAN transceiver is required to connect to a real CAN bus.
- Proper bus termination is required for real CAN wiring.

Initial decision:

- Do not use CAN in the first MVP.
- Keep CAN in the architecture as a future expansion path.

## 6. GPIO

GPIO means General-Purpose Input/Output. These pins can be configured as digital
input, digital output, analog input, or peripheral alternate function.

Datasheet points:

- Output modes: push-pull or open-drain
- Optional pull-up or pull-down
- Input modes: floating or pull-up/pull-down
- Alternate function mode for peripherals
- Many GPIOs are shared with digital or analog alternate functions
- GPIO speed selection is available
- I/O configuration can be locked
- Fast I/O toggling up to 90 MHz

### Project Use

GPIO is needed for:

- Motor driver direction pins
- Motor driver enable or brake pins
- Fault input from driver, if available
- User button or emergency-stop signal
- Status LED
- Chip-select signals for SPI devices
- Optional power control signals

Important warning:

- GPIO being high-current-capable does not mean it can drive motors.
- STM32 GPIO pins are for logic signals, not motor power.
- Motors must be driven through a motor driver or power stage.

### Safe Motor Driver Control

Motor-related GPIO should be designed with safe default states.

Recommended approach:

- Motor enable pin defaults to disabled during reset.
- Use pull-down or pull-up resistors as needed.
- Firmware should explicitly disable motor outputs during startup.
- PWM should be started only after direction and enable pins are in known states.

## 7. ADC

ADC means Analog-to-Digital Converter. It converts an analog voltage into a
digital value.

Datasheet points:

- Three 12-bit ADCs
- Each ADC shares up to 16 external channels
- Single-shot or scan mode
- Automatic scan conversion for selected input groups
- Simultaneous sample and hold
- Interleaved sample and hold
- DMA support
- Analog watchdog support
- ADC interrupt when converted voltage is outside programmed thresholds
- ADC conversion can be triggered by TIM1, TIM2, TIM3, TIM4, TIM5, or TIM8

### Project Use

The first ADC use is 3S LiPo voltage monitoring.

Important rule:

- 3S LiPo voltage must never be connected directly to an STM32 ADC pin.
- A resistor divider is required to scale battery voltage below the ADC input
  range.

Possible ADC inputs:

- Battery pack voltage
- Motor driver current sense, if available
- Regulated 5 V rail monitor through divider
- Temperature or other analog diagnostics

### Analog Watchdog

The analog watchdog can generate an interrupt when an ADC value goes outside a
configured threshold range.

Project use:

- Detect low battery voltage
- Trigger a warning state
- Reduce PWM or stop motors

Initial decision:

- Start with periodic ADC sampling and software threshold checks.
- Use analog watchdog later if the battery monitoring logic needs more hardware
  support.

### Timer-Triggered ADC

The ADC can be triggered by timers.

Project use:

- Sample battery voltage at a fixed rate.
- Avoid irregular sampling caused by main-loop timing variation.

Initial decision:

- For MVP, software-triggered or simple periodic sampling is enough.
- Timer-triggered ADC can be added when the control loop and telemetry become
  more structured.

## 8. SWJ-DP: SWD/JTAG Debug Port

SWJ-DP combines Serial Wire Debug and JTAG debug access.

Datasheet points:

- Supports SWD and JTAG
- SWD uses fewer pins than JTAG
- Debug can be performed using only SWDIO and SWCLK
- JTAG pins can be reused as GPIO with alternate function when appropriate

### Project Use

The NUCLEO board uses ST-LINK, which relies on the debug interface for firmware
upload and debugging.

Project decision:

- Keep SWD pins available for debugging.
- Avoid assigning SWD pins to robot functions during early development.
- Debug access is more valuable than saving a small number of pins at MVP stage.

## 9. Low-Priority Peripherals for MVP

These peripherals are useful in general, but not central to the first robot MVP:

- I2S / SAI / SPDIF-RX: audio interfaces
- HDMI-CEC: consumer electronics control
- SDIO: SD/MMC card interface
- USB OTG FS/HS: useful, but ST-LINK virtual COM and UART are simpler first
- DCMI: camera parallel interface
- DAC: analog output

Decision:

- Do not include these in the first pin allocation.
- Revisit only when a specific feature requires them.

## 10. Preliminary Peripheral Allocation

This is not a final pinout. It is a functional allocation before checking Table
10, Table 11, the NUCLEO schematic, and CubeMX.

| Robot function | Peripheral candidate | First decision |
| --- | --- | --- |
| PC command/debug | USART/UART | Use one simple serial link first. |
| ESP32-S3 link | USART/UART | Add after PC serial control works. |
| BNO08x IMU | I2C first, SPI/UART fallback | Start simple with I2C. |
| Motor driver direction | GPIO | Use safe default states. |
| Motor driver enable/brake | GPIO | Default to disabled on reset. |
| Battery voltage monitor | ADC | Use resistor divider and software threshold first. |
| Future CAN bus | bxCAN + transceiver | Defer until UART MVP works. |
| Firmware debug | SWD through ST-LINK | Preserve during development. |

## 11. Risks and Checks

### Voltage Compatibility

Required checks:

- Motor driver logic input threshold
- Encoder output voltage
- IMU logic voltage
- ESP32-S3 UART voltage
- ADC input maximum voltage

### Pin Conflict

Required checks:

- USART pins do not conflict with PWM/encoder pins.
- I2C pins are available and have proper pull-ups.
- ADC pin is not already needed for a timer or communication function.
- SWD pins remain available.

### Noise

Motor systems are noisy.

Mitigation:

- Keep motor power wires away from I2C and UART wires.
- Use a common ground reference intentionally.
- Add filtering or shielding only after measuring or observing actual problems.
- Keep ADC divider impedance and filtering reasonable.

## 12. First Design Decision

STM32F446RE has sufficient communication and I/O resources for the initial
tracked robot MVP.

Recommended direction:

1. Use one USART/UART path for PC command and debug.
2. Use I2C as the first BNO08x IMU interface candidate.
3. Use GPIO for motor direction and enable/brake with safe default states.
4. Use ADC for LiPo voltage monitoring through a resistor divider.
5. Preserve SWD for debugging.
6. Defer CAN until the UART-based MVP is validated.

## 13. Next Stage

The next architecture document should build the first pin allocation candidate.

Inputs needed:

- Table 10: Pin and ball descriptions
- Table 11: Alternate function
- NUCLEO-F446RE user manual and schematic
- CubeMX pinout conflict check

The pin allocation must cover:

- Left/right motor PWM
- Left/right encoder A/B
- Motor direction and enable GPIO
- UART for PC
- Optional UART for ESP32-S3
- I2C for IMU
- ADC for battery voltage
- SWD debug preservation
