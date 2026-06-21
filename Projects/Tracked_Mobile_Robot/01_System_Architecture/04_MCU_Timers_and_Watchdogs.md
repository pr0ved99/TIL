# STM32F446RE Timers and Watchdogs Analysis

## Purpose

This document analyzes the timer and watchdog part of the STM32F446xC/E
datasheet for the tracked mobile robot project.

Scope:

- Section 3.21: Timers and watchdogs
- Section 3.21.1: Advanced-control timers
- Section 3.21.2: General-purpose timers
- Section 3.21.3: Basic timers
- Section 3.21.4: Independent watchdog
- Section 3.21.5: Window watchdog
- Section 3.21.6: SysTick timer
- Table 6: Timer feature comparison

The goal is to understand which timer resources can support motor PWM, encoder
input, fixed-period control loops, and fail-safe behavior.

## 1. Why Timers Matter in This Robot

Timers are one of the most important MCU peripherals for this project.

Robot functions that depend on timers:

- PWM generation for motor speed control
- Encoder counting for wheel speed estimation
- Fixed-period control loop execution
- Input capture or output compare if needed later
- Periodic ADC sampling or diagnostic timing
- Watchdog reset when firmware becomes unhealthy

If timers are assigned poorly, the robot may still compile and run, but the
control system can become unstable, jittery, or difficult to debug.

## 2. Timer Groups in STM32F446RE

The datasheet classifies timers into these groups:

| Timer group | Timers | Main meaning |
| --- | --- | --- |
| Advanced-control timers | TIM1, TIM8 | High-feature timers intended for motor-control-style PWM. |
| Full-featured general-purpose timers | TIM2, TIM3, TIM4, TIM5 | Flexible timers for PWM, input capture, output compare, and encoder signals. |
| Simpler general-purpose timers | TIM9, TIM10, TIM11, TIM12, TIM13, TIM14 | Useful for simple PWM, output compare, input capture, or time-base tasks. |
| Basic timers | TIM6, TIM7 | Simple 16-bit time-base timers, often used for DAC trigger or periodic events. |
| Watchdog timers | IWDG, WWDG | Safety timers that reset the MCU if firmware fails to refresh them correctly. |
| SysTick | Cortex-M system timer | 24-bit downcounter often used for OS tick or simple periodic interrupt. |

## 3. Table 6 Summary

Table 6 compares the timer feature sets.

Important observations:

- TIM1 and TIM8 are 16-bit advanced-control timers.
- TIM1 and TIM8 support complementary outputs and DMA request generation.
- TIM2 and TIM5 are 32-bit general-purpose timers.
- TIM3 and TIM4 are 16-bit full-featured general-purpose timers.
- TIM2, TIM3, TIM4, and TIM5 each have 4 capture/compare channels.
- TIM2, TIM3, TIM4, and TIM5 can handle quadrature incremental encoder signals.
- TIM6 and TIM7 have no capture/compare channels and are best treated as time-base timers.
- TIM9/TIM12 have 2 channels.
- TIM10/TIM11/TIM13/TIM14 have 1 channel.
- All timer counters can be frozen in debug mode.

## 4. Advanced-Control Timers: TIM1 and TIM8

TIM1 and TIM8 are advanced-control timers.

Datasheet capabilities:

- 16-bit counters
- Up, down, and up/down counting
- 4 independent channels
- Input capture
- Output compare
- PWM generation
- One-pulse mode
- Complementary PWM outputs
- Programmable dead time
- DMA request generation
- Timer link synchronization with other timers

### Project Meaning

TIM1 and TIM8 are strong candidates for motor PWM generation.

For this tracked robot, the motor driver likely needs:

- Left motor PWM
- Right motor PWM
- Left direction GPIO
- Right direction GPIO
- Optional enable/brake GPIO

If the motor driver only needs one PWM per motor, TIM1 or TIM8 can provide more
than enough PWM channels.

### Complementary Output and Dead Time

Complementary PWM means a timer can generate paired outputs, often used for
half-bridge or three-phase motor-control circuits.

Dead time means a short intentional delay between switching complementary
transistors, preventing both high-side and low-side switches from turning on at
the same time.

Project decision:

- If using a complete DC motor driver module, complementary PWM and dead time
  are probably not needed.
- If designing a MOSFET bridge directly later, TIM1/TIM8 become much more
  important.

## 5. Full-Featured General-Purpose Timers: TIM2, TIM3, TIM4, TIM5

These timers are the most important candidates for encoder and general control
tasks.

Datasheet capabilities:

- TIM2 and TIM5: 32-bit counters
- TIM3 and TIM4: 16-bit counters
- 16-bit prescaler
- Up, down, and up/down counting
- 4 independent channels each
- Input capture
- Output compare
- PWM generation
- One-pulse mode
- Timer link synchronization
- DMA request generation
- Quadrature incremental encoder signal handling
- Hall sensor digital output handling

### Project Meaning

For motor encoders, TIM2, TIM3, TIM4, and TIM5 are the primary candidates.

Hardware timer encoder mode is preferred over counting encoder edges using GPIO
interrupts because:

- It reduces CPU interrupt load.
- It handles high edge rates more reliably.
- It gives more deterministic speed estimation.
- It leaves NVIC capacity for communication and safety events.

### 32-bit vs 16-bit Timers

TIM2 and TIM5 are 32-bit. TIM3 and TIM4 are 16-bit.

Simple interpretation:

- 32-bit timers can count much farther before overflowing.
- 16-bit timers overflow sooner and require more careful sampling.

Robot implication:

- TIM2 and TIM5 are attractive for encoder counters.
- TIM3 and TIM4 can also work, especially if the firmware samples encoder count
  differences at a fixed period.
- Final selection depends on available pins, not only timer capability.

## 6. Simpler General-Purpose Timers

TIM9, TIM10, TIM11, TIM12, TIM13, and TIM14 are simpler 16-bit timers.

Capabilities:

- TIM9 and TIM12 have 2 channels.
- TIM10, TIM11, TIM13, and TIM14 have 1 channel.
- They can be used for input capture, output compare, PWM, one-pulse mode, or
  simple time-base tasks depending on the timer.

Project usage candidates:

- Extra PWM output
- Status LED timing
- Periodic diagnostics
- Simple timeout generation
- Non-critical input capture

Initial decision:

- Do not assign these first.
- Reserve them as spare timers after motor PWM, encoder, and control-loop timing
  have been allocated.

## 7. Basic Timers: TIM6 and TIM7

TIM6 and TIM7 are basic 16-bit timers.

Datasheet points:

- Mainly used for DAC trigger and waveform generation
- Can also be used as generic 16-bit time bases
- Support DMA request generation
- No capture/compare channels

Project meaning:

- Good candidates for fixed-period software timing.
- Can be used for the control-loop tick if no capture/compare feature is needed.
- Can be used for periodic battery voltage sampling or diagnostics.

Initial candidate:

- TIM6: fixed-period motor control loop timer
- TIM7: slower diagnostic or ADC sampling time base

This is only a preliminary allocation. The final choice must be checked against
CubeMX, HAL usage, and any library conflicts.

## 8. Watchdogs

Watchdogs are safety peripherals. They reset the MCU if firmware stops behaving
correctly.

### Independent Watchdog: IWDG

The independent watchdog is based on:

- 12-bit downcounter
- 8-bit prescaler
- Independent 32 kHz internal RC clock
- Operation independent from the main system clock
- Can operate in Stop and Standby modes
- Hardware or software configuration through option bytes

Project meaning:

- IWDG is the stronger fail-safe watchdog because it does not depend on the main
  clock.
- If the firmware hangs, the watchdog can reset the MCU.

Important safety note:

- Resetting the MCU is not the same as actively braking the robot.
- MDD10A PWM pins should have safe default states, such as pull-down to keep
  duty at zero during reset.
- The motor power stage should not keep driving motors while the MCU is
  rebooting.

Initial decision:

- Add IWDG after basic motor control is stable.
- Do not enable it too early, because it can make debugging harder.

### Window Watchdog: WWDG

The window watchdog is based on:

- 7-bit downcounter
- Main clock
- Early warning interrupt
- Debug freeze support

Project meaning:

- WWDG can detect timing faults where firmware refreshes the watchdog too early
  or too late.
- It is stricter than a simple timeout watchdog.

Initial decision:

- WWDG is not needed for the initial MVP.
- IWDG is the simpler and more useful first watchdog.

### SysTick Timer

SysTick is a Cortex-M system timer.

Datasheet points:

- 24-bit downcounter
- Autoreload capability
- Maskable interrupt when counter reaches 0
- Programmable clock source
- Often used by RTOS or HAL timing

Project meaning:

- HAL commonly uses SysTick for millisecond timing.
- It can be used for simple delays and scheduling.
- It should not be the main mechanism for high-quality motor-control timing if a
  dedicated hardware timer is available.

Initial decision:

- Leave SysTick for HAL/system tick.
- Use a dedicated TIMx timer for the motor control loop.

## 9. Preliminary Timer Allocation

This allocation is not final. It is a starting point for CubeMX and pinout
validation.

| Robot function | Preferred timer candidate | Reason |
| --- | --- | --- |
| Left/right motor PWM | TIM1 or TIM8 | Advanced-control timers, multiple PWM channels. |
| Left encoder | TIM2 or TIM5 | 32-bit, full-featured, supports quadrature encoder signals. |
| Right encoder | TIM5 or TIM2 | 32-bit, full-featured, supports quadrature encoder signals. |
| Backup encoder option | TIM3 or TIM4 | Full-featured timers, encoder-capable, 16-bit. |
| Fixed-period control loop | TIM6 or TIM7 | Basic timer is enough for a time base. |
| Battery sampling tick | TIM7 or another spare timer | Periodic low-rate task. |
| Additional PWM/debug timing | TIM9-TIM14 | Reserve for secondary features. |
| System millisecond tick | SysTick | Usually used by HAL. |
| Firmware hang recovery | IWDG | Independent watchdog clock. |

## 10. Risks and Checks

### Pin Conflict

Timer capability does not guarantee usable pins.

Required checks:

- Does the chosen timer channel appear on a NUCLEO-accessible pin?
- Does it conflict with ST-LINK, user button, LED, Arduino header, or Morpho
  header usage?
- Can left and right encoder channels each use CH1/CH2 of the same timer?

### PWM Frequency

PWM frequency depends on:

- Timer input clock
- Prescaler
- Auto-reload value
- Counting mode

Required checks:

- Choose PWM frequency suitable for the motor driver.
- Avoid audible motor noise if practical.
- Keep enough timer resolution for duty-cycle control.

### Encoder Overflow

Encoder counters can overflow.

Risk:

- 16-bit timers overflow faster than 32-bit timers.

Mitigation:

- Prefer TIM2/TIM5 for encoders if pins allow.
- If using 16-bit timers, sample count differences frequently and handle
  wraparound correctly.

### Watchdog Reset Safety

Watchdog reset must lead to a safe motor state.

Required checks:

- MDD10A PWM output has a safe default zero state.
- PWM pin reset state does not accidentally drive the motor.
- Firmware initialization disables motors before enabling control.

## 11. First Design Decision

The timer resources of STM32F446RE are sufficient for the tracked robot MVP.

The recommended design direction is:

1. Use a dedicated hardware timer for the fixed-period control loop.
2. Use hardware timer encoder mode for motor encoders.
3. Use TIM1 or TIM8 for PWM if pin mapping allows.
4. Keep SysTick for HAL/system timing.
5. Add IWDG only after basic motor control is stable.
6. Validate all choices in CubeMX and the NUCLEO-F446RE pinout before finalizing
   firmware.

## 12. Next Stage

The next document should analyze communication and I/O peripherals:

- I2C for BNO08x IMU
- USART/UART for PC and ESP32 communication
- bxCAN for deferred expansion
- GPIO for motor driver and safety signals
- ADC for battery voltage monitoring

After communication and I/O are analyzed, the project should create a first
pin-allocation table.
