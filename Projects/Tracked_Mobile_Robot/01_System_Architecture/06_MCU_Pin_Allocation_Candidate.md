# STM32F446RE Pin Allocation Candidate

## Purpose

This document proposes the first pin allocation candidate for the NUCLEO-F446RE
tracked mobile robot MVP.

This is not the final pinout. It is a pre-CubeMX candidate based on:

- STM32F446xC/E datasheet
- UM1724 STM32 Nucleo-64 boards user manual
- Previous MCU peripheral analysis documents

The final pinout must be validated in CubeMX and against the actual
NUCLEO-F446RE schematic before firmware implementation.

## Design Targets

The pin allocation must support:

- Left/right motor PWM
- Left/right motor direction and enable/brake GPIO
- Left/right quadrature encoder A/B inputs
- PC command/debug serial link
- Optional ESP32-S3 serial link
- BNO08x IMU through I2C
- 3S LiPo battery voltage monitoring through ADC
- Future CAN expansion
- SWD debugging preservation

## Sources Used

| Source | Used for |
| --- | --- |
| `assets/stm32f446mc.pdf` | STM32F446RE package pins and alternate functions. |
| `UM1724 STM32 Nucleo-64 boards user manual` | Arduino connector and ST morpho connector mapping for NUCLEO-F446RE. |

Important UM1724 facts used:

- NUCLEO-F446RE uses STM32F446RET6 in LQFP64 package.
- Arduino D1/D0 map to PA2/PA3 and USART2_TX/USART2_RX.
- Arduino D15/D14 map to PB8/PB9 and I2C1_SCL/I2C1_SDA.
- Arduino A0/A1/A2/A3 map to PA0/PA1/PA4/PB0 ADC-capable pins.
- PA13 and PA14 share SWD signals connected to ST-LINK, so they should be
  preserved during development.

## Allocation Strategy

The first allocation uses these principles:

1. Keep PA13/PA14 reserved for SWD.
2. Use USART2 PA2/PA3 for the first PC serial link.
3. Use I2C1 PB8/PB9 for the BNO08x IMU.
4. Use hardware timer encoder mode for both motor encoders.
5. Use timer PWM outputs for motor speed control.
6. Use ADC through a resistor divider for LiPo voltage.
7. Avoid using the same timer for PWM and encoder if a cleaner split is
   available.
8. Prefer pins exposed on Arduino or ST morpho headers.

## First Pin Candidate Table

| Robot function | MCU pin | Peripheral/function | Board access | Status |
| --- | --- | --- | --- | --- |
| PC serial TX | PA2 | USART2_TX | Arduino D1 / ST morpho CN10 pin 35 | Primary |
| PC serial RX | PA3 | USART2_RX | Arduino D0 / ST morpho CN10 pin 37 | Primary |
| IMU I2C SCL | PB8 | I2C1_SCL | Arduino D15 / ST morpho CN10 pin 3 | Primary |
| IMU I2C SDA | PB9 | I2C1_SDA | Arduino D14 / ST morpho CN10 pin 5 | Primary |
| Left motor PWM | PB6 | TIM4_CH1 | Arduino D10 / ST morpho CN10 pin 17 | Candidate |
| Right motor PWM | PB7 | TIM4_CH2 | ST morpho CN7 pin 21 | Candidate |
| Left encoder A | PB4 | TIM3_CH1 | Arduino D5 / ST morpho CN10 pin 27 | Candidate |
| Left encoder B | PB5 | TIM3_CH2 | Arduino D4 / ST morpho CN10 pin 29 | Candidate |
| Right encoder A | PA0 | TIM5_CH1 | Arduino A0 / ST morpho CN7 pin 28 | Candidate |
| Right encoder B | PA1 | TIM5_CH2 | Arduino A1 / ST morpho CN7 pin 30 | Candidate |
| Battery voltage ADC | PA4 | ADC12_IN4 | Arduino A2 / ST morpho CN7 pin 32 | Candidate |
| Left motor direction | PC8 | GPIO output | ST morpho CN10 pin 2 | Candidate |
| Right motor direction | PC9 | GPIO output | ST morpho CN10 pin 1 | Candidate |
| Left motor enable/brake | PC6 | GPIO output | ST morpho CN10 pin 4 | Candidate |
| Right motor enable/brake | PC5 | GPIO output | ST morpho CN10 pin 6 | Candidate |
| Optional ESP32 TX | PA9 | USART1_TX | Arduino D8 / ST morpho CN10 pin 21 | Reserve |
| Optional ESP32 RX | PA10 | USART1_RX | Arduino D2 / ST morpho CN10 pin 33 | Reserve |
| Future CAN RX | PA11 | CAN1_RX | ST morpho CN10 pin 14 | Reserve |
| Future CAN TX | PA12 | CAN1_TX | ST morpho CN10 pin 12 | Reserve |
| SWDIO | PA13 | SWDIO | ST-LINK / ST morpho CN7 pin 13 | Preserve |
| SWCLK | PA14 | SWCLK | ST-LINK / ST morpho CN7 pin 15 | Preserve |

## Rationale by Subsystem

### PC Serial Link

PA2 and PA3 are assigned to USART2 because UM1724 maps them to Arduino D1/D0
and USART2_TX/USART2_RX.

Use:

- PC command input
- Debug log output
- Early serial protocol validation

Risk:

- Depending on solder bridge configuration and ST-LINK virtual COM routing,
  USART2 may already be connected to the onboard ST-LINK path.

Check:

- Confirm USART2 PA2/PA3 behavior with a simple UART echo test.

### IMU I2C

PB8/PB9 are assigned to I2C1_SCL/I2C1_SDA because UM1724 maps them to Arduino
D15/D14, the common Arduino I2C pins.

Use:

- BNO08x IMU first interface candidate

Risk:

- I2C can be sensitive to wiring length and motor noise.

Check:

- Confirm pull-up voltage and I2C bus stability at 100 kHz or 400 kHz.

### Motor PWM

PB6/PB7 are assigned to TIM4_CH1/TIM4_CH2.

Reason:

- Both are channels from the same timer.
- This makes it easier to configure matching PWM frequency and resolution for
  left/right motors.
- PB6 is available on Arduino D10 and ST morpho.
- PB7 is available on ST morpho.

Risk:

- PB6 is also an I2C1 candidate on many STM32 designs, but this allocation uses
  PB8/PB9 for I2C, so PB6 can stay with TIM4.

Check:

- Verify TIM4_CH1 and TIM4_CH2 are conflict-free in CubeMX.

### Encoders

The left encoder uses TIM3_CH1/TIM3_CH2 on PB4/PB5.

The right encoder uses TIM5_CH1/TIM5_CH2 on PA0/PA1.

Reason:

- Encoder mode typically needs CH1 and CH2 of the same timer.
- TIM3 and TIM5 are full-featured general-purpose timers.
- TIM5 is 32-bit, which is useful for encoder counting.
- PB4/PB5 and PA0/PA1 are accessible on board headers.

Risk:

- PB4 and PB5 may have debug/JTAG-related alternate history on some STM32
  configurations. SWD itself mainly uses PA13/PA14, but CubeMX must still be
  checked.
- PA0/PA1 are also convenient ADC pins; assigning them to encoder input moves
  battery voltage monitoring to PA4.

Check:

- Confirm TIM3 encoder mode on PB4/PB5.
- Confirm TIM5 encoder mode on PA0/PA1.
- Verify encoder signal voltage before connecting to STM32 pins.

### Battery Voltage ADC

PA4 is assigned to ADC12_IN4.

Reason:

- PA0/PA1 are reserved for the right encoder candidate.
- PA4 is available as Arduino A2 and ADC-capable.

Critical rule:

- 3S LiPo must never be connected directly to PA4.
- A resistor divider is mandatory.

Check:

- Choose divider values so maximum battery voltage stays below ADC input range.
- Measure divided voltage with a multimeter before connecting to STM32.

### Motor Direction and Enable GPIO

PC8, PC9, PC6, and PC5 are assigned as GPIO outputs.

Reason:

- These pins are accessible on ST morpho.
- They avoid the first serial, I2C, encoder, PWM, ADC, and SWD assignments.

Safety requirement:

- Motor enable/brake pins must default to a safe disabled state during reset.
- Use external pull-down or pull-up resistors as required by the motor driver.

Check:

- Verify motor driver input logic level.
- Verify motor outputs remain disabled while STM32 resets or boots.

### Optional ESP32 Serial

PA9/PA10 are reserved for USART1_TX/USART1_RX.

Reason:

- USART1 is a clean optional serial link.
- It can connect to ESP32-S3 after the PC serial MVP works.

Check:

- Confirm 3.3 V UART logic compatibility between STM32 and ESP32-S3.
- Add common ground.

### Future CAN

PA11/PA12 are reserved as CAN1_RX/CAN1_TX candidates.

Reason:

- They provide a future CAN path without disturbing the first UART/I2C/PWM/ADC
  allocation.

Important:

- A CAN transceiver is required.
- CAN bus termination must be designed separately.

## Conflict Review

| Resource | Conflict status |
| --- | --- |
| USART2 PA2/PA3 | Conflicts with TIM2/TIM5 CH3/CH4 alternatives, but not used in this allocation. |
| I2C1 PB8/PB9 | Shares with TIM4_CH3/CH4 alternatives, but TIM4_CH1/CH2 are used for PWM. |
| TIM4 PB6/PB7 PWM | PB6 can also be I2C1_SCL or USART1_TX, but those are not used here. |
| TIM3 PB4/PB5 encoder | Must be checked in CubeMX; likely usable when SWD is kept on PA13/PA14. |
| TIM5 PA0/PA1 encoder | Consumes A0/A1 ADC-capable pins. |
| PA4 ADC | Also supports USART2_CK/SPI functions, but not needed here. |
| PA13/PA14 | Reserved for SWD and not assigned to robot functions. |

## Validation Checklist

Before firmware implementation:

1. Create a CubeMX project for STM32F446RETx.
2. Enable USART2 on PA2/PA3.
3. Enable I2C1 on PB8/PB9.
4. Enable TIM4 PWM on PB6/PB7.
5. Enable TIM3 encoder mode on PB4/PB5.
6. Enable TIM5 encoder mode on PA0/PA1.
7. Enable ADC on PA4.
8. Configure PC8, PC9, PC6, PC5 as GPIO outputs.
9. Keep SWD enabled on PA13/PA14.
10. Check all warnings and pin conflicts.
11. Generate a `.ioc` file and commit it after validation.

Bench validation order:

1. GPIO output toggle test.
2. USART2 echo test.
3. I2C scan or BNO08x identity read.
4. PWM output measurement.
5. Encoder count test by hand rotation.
6. ADC divider measurement with bench voltage first, battery later.
7. Motor driver enable safety test with motor power disconnected first.

## First Decision

This candidate is suitable for the first CubeMX validation pass.

The most important design choices are:

- USART2 PA2/PA3 for PC serial.
- I2C1 PB8/PB9 for IMU.
- TIM4 PB6/PB7 for left/right PWM.
- TIM3 PB4/PB5 and TIM5 PA0/PA1 for encoders.
- PA4 for battery voltage ADC.
- PA13/PA14 preserved for SWD.

## Next Stage

The next step is not more datasheet reading. The next step is validation:

1. Create a CubeMX `.ioc` pinout based on this candidate.
2. Export screenshots or notes from CubeMX.
3. Update this document with the validated pinout.
4. Move rejected candidates into a decision log.
