# ESP32-S3 Features and Project Role Analysis

## Purpose

This document summarizes ESP32-S3 features and defines how the ESP32-S3
DevKitC-1 should be used in the tracked mobile robot project.

The goal is not to replace the STM32 low-level controller. The goal is to
identify the engineering role of ESP32-S3 as a support controller for wireless
communication, UI, sensor prototyping, and development utilities.

## Sources

- ESP32-S3 Series Datasheet v2.2: `assets/esp32-s3_datasheet_en.pdf`
- Online reference: https://documentation.espressif.com/esp32-s3_datasheet_en.pdf
- ESP32-S3-DevKitC-1 User Guide v1.1: https://documentation.espressif.com/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html
- Project ESP32-S3 notes: `Embedded/ESP32-S3/README.md`

## Current Project Board

| Item | Current state |
| --- | --- |
| Board | HG ESP32-S3 DevKitC-1 |
| Toolchain | ESP-IDF v5.4.4 |
| USB detection | Espressif USB JTAG/serial debug unit |
| Serial path | `/dev/ttyACM0` and stable by-id path |
| Flash detected in practice | 16 MB |
| RGB LED test | Completed |
| RGB LED GPIO in project test | GPIO38 |

Note:

- ESP32-S3-DevKitC-1 boards exist in multiple revisions.
- The official Espressif documentation notes that RGB LED GPIO differs by board
  revision.
- This project should trust the tested result for the current board: GPIO38.

## 1. ESP32-S3 Feature Summary

### CPU and Runtime

ESP32-S3 is a Wi-Fi and Bluetooth LE MCU built around a dual-core Xtensa LX7
processor.

Project meaning:

- Strong enough for networking, UI, serial parsing, and light sensor processing.
- Runs ESP-IDF and FreeRTOS-based applications.
- Good fit for tasks that benefit from concurrency but do not require hard
  motor-control timing.

Not the primary role:

- It should not replace STM32 for the first low-level motor-control MVP.
- Wi-Fi/BLE tasks can introduce timing variability, so motor PWM and encoder
  counting should remain on STM32.

### Wireless

ESP32-S3 provides:

- 2.4 GHz Wi-Fi
- Bluetooth Low Energy

Project uses:

- Wireless configuration page
- Remote command interface
- Debug telemetry streaming
- Mobile phone or laptop control interface
- Future ROS2-side bridge experiments through Wi-Fi

Initial decision:

- Do not use wireless in the first drivetrain MVP.
- Add Wi-Fi only after STM32 UART control and motor safety are stable.

### USB

ESP32-S3 includes USB-related capabilities such as USB Serial/JTAG and USB OTG
support, depending on board wiring and firmware configuration.

Project uses:

- Flashing and monitoring firmware
- USB serial debug
- JTAG-style development workflow through the built-in USB Serial/JTAG unit

Initial decision:

- Keep ESP32-S3 USB workflow for ESP-IDF practice and debugging.
- Do not make USB host/device behavior part of the first robot MVP.

### GPIO and Digital Peripherals

ESP32-S3 provides many programmable GPIOs and common embedded peripherals such
as UART, I2C, SPI, PWM, RMT, pulse counter, SD/MMC host, and TWAI.

Project uses:

- UART link to STM32
- Optional I2C/SPI sensor prototyping
- Button, LED, status output, and simple UI
- Future CAN-like experiments through TWAI plus external transceiver

Important caution:

- ESP32-S3 GPIO is for logic signals, not motor power.
- GPIO voltage compatibility must be checked before connecting to STM32,
  sensors, or motor drivers.

### ADC and Touch

ESP32-S3 includes ADC and touch sensing capabilities.

Project uses:

- Quick analog experiments
- Simple battery or rail monitoring prototypes
- Touch/button UI experiments

Initial decision:

- Primary battery monitoring remains on STM32 ADC because STM32 owns motor
  safety.
- ESP32 ADC can be used for secondary telemetry only after the main power
  safety path is validated.

### Security and Crypto

ESP32-S3 includes hardware security features such as secure boot, flash
encryption, random number generation, and cryptographic acceleration.

Project uses:

- Not required for the first MVP.
- Useful if the robot later exposes Wi-Fi services or stores credentials.

Initial decision:

- Defer security hardening until wireless features become part of the project.

## 2. ESP32-S3 vs STM32 Role Split

The project should use STM32 and ESP32-S3 for different jobs.

| Responsibility | STM32 NUCLEO-F446RE | ESP32-S3 DevKitC-1 |
| --- | --- | --- |
| Motor PWM | Primary | Avoid for MVP |
| Encoder counting | Primary | Avoid for MVP |
| Motor fail-safe | Primary | Support only |
| Battery low-voltage motor shutdown | Primary | Telemetry only |
| IMU integration | Candidate primary | Good prototype candidate |
| External command ingress | Request validation/execution and final safety authority | Final MVP production ingress owner; optional arbitration/forwarding planned |
| Wireless control | Not suitable | Primary |
| Web UI or mobile UI | Not suitable | Primary |
| Debug telemetry over Wi-Fi | Not suitable | Primary |
| ROS2 bridge experiments | Later through PC | Possible Wi-Fi/serial bridge |
| CAN/TWAI expansion | STM32 bxCAN candidate | ESP32 TWAI candidate, later only |

## 3. Recommended ESP32-S3 Uses in This Project

### Use 1: Wireless Dashboard

ESP32-S3 can host a simple Wi-Fi dashboard after the drivetrain MVP works.

Possible features:

- Robot armed/disarmed state
- Battery voltage telemetry from STM32
- Left/right motor speed
- IMU yaw or yaw rate
- Command buttons for low-speed test modes

Data path:

```text
STM32 -> UART -> ESP32-S3 -> Wi-Fi dashboard
```

Do not allow high-power motor commands from Wi-Fi until safety behavior is
verified.

### Use 2: STM32 Wireless Serial Bridge

ESP32-S3 can act as a bridge between STM32 UART and a PC or phone over Wi-Fi.

Possible data path:

```text
PC/phone -> Wi-Fi -> ESP32-S3 -> UART -> STM32
STM32 -> UART -> ESP32-S3 -> Wi-Fi -> PC/phone
```

Use case:

- Remote telemetry
- Low-speed command testing
- Debugging without a USB cable connected to STM32

Risk:

- Wi-Fi latency and packet loss can occur.
- STM32 must enforce command timeout and motor stop behavior.

### Use 3: IMU Prototype Platform

ESP32-S3 can be used to test the BNO08x IMU before integrating it into STM32.

Reason:

- ESP-IDF development and logging are convenient.
- I2C/SPI sensor experiments can be isolated from motor-control firmware.

Decision:

- Use ESP32-S3 for IMU bring-up only if STM32 integration is blocked or if
  sensor debugging needs a separate environment.
- Final IMU ownership should be decided after drivetrain and odometry tests.

### Use 4: UI and Mode Controller

ESP32-S3 can handle non-safety user-facing functions.

Examples:

- Mode selection
- Start/stop request
- Web-based parameter setting
- LED status pattern
- BLE-based setup

Rule:

- ESP32-S3 may request actions.
- STM32 must decide whether motor action is safe.

### Use 5: Future Communication Experiments

ESP32-S3 has TWAI, which is compatible with CAN 2.0 style controller behavior,
but it still needs an external transceiver to connect to a real CAN bus.

Project decision:

- Do not use TWAI/CAN in the first MVP.
- Keep it as a later communication experiment after UART-based control works.

## 4. What ESP32-S3 Should Not Do First

ESP32-S3 should not own these functions in the first MVP:

- Primary motor PWM generation
- Primary encoder counting
- Primary low-voltage motor shutdown
- Direct motor driver safety logic
- High-priority real-time control loop
- Complex ROS2/Nav2 autonomy role

Reason:

- The project architecture intentionally assigns low-level deterministic motor
  control to STM32.
- ESP32-S3 is better used for wireless, UI, and support tasks.

## 5. STM32-ESP32 Interface Candidate

The initial interface should be UART.

Candidate wiring:

```text
STM32 TX -> ESP32 RX
STM32 RX <- ESP32 TX
GND      <-> GND
```

Important checks:

- Both sides use compatible 3.3 V logic.
- Grounds are connected.
- Baud rate and frame format match.
- STM32 command timeout is implemented.
- ESP32 cannot keep motors running if STM32 stops receiving valid commands.

Initial protocol direction:

- Start with text messages.
- Move to framed binary packets later if needed.

Example early messages:

```text
STM32 -> ESP32:
TEL,batt_mv=11820,left_cps=120,right_cps=118,armed=0

ESP32 -> STM32:
CMD,linear=0.10,angular=0.00,timeout_ms=300
```

## 6. ESP32-S3 Development Path

Recommended learning and validation order:

1. Confirm ESP-IDF environment and board connection.
2. Confirm RGB LED and BOOT button.
3. Create a FreeRTOS two-task example.
4. Test UART loopback.
5. Test ESP32-to-PC serial logging.
6. Test ESP32-to-STM32 UART link.
7. Add Wi-Fi access point or station mode.
8. Add simple telemetry web page.
9. Add command timeout and safety gating.
10. Integrate with STM32 telemetry after STM32 motor tests are stable.

## 7. Architecture Decision

ESP32-S3 is suitable as a support controller, not as the first low-level motor
controller.

Final MVP role:

- Wireless dashboard
- Production external command ingress and UART bridge
- IMU/sensor prototype platform
- UI and development utility controller

The fixed production path is:

```text
optional PC control -> ESP32-S3 -> UART1 GPIO17/GPIO18
                                   <-> STM32 USART1 PA9/PA10
```

The STM32 USART2 PA2/PA3 PC-first path is historical bench evidence only and
does not accept Final MVP production commands. ESP32 owns ingress, while STM32
still owns motor output and safety permission. `PC -> ESP32` forwarding is not
implemented yet.

Deferred role:

- Wi-Fi command interface
- BLE setup
- TWAI/CAN experiment
- Advanced telemetry gateway

Rejected for MVP:

- Primary motor control
- Primary safety shutdown
- Encoder ownership

## 8. Next Stage

ADR-015 fixes the STM32-ESP32 boundary and production ingress. The next
command-path work is the production `CMD(vx,w)` mapper and timeout recovery.

Current reference documents:

- `09_STM32_ESP32_UART_Interface_Contract.md`
- ADR-015 in `19_Architecture_Decision_Record_ko.md`

Follow-up implementation must close:

- Production `CMD(vx,w)` to left/right PWM/DIR mapping
- Output/stored-command zero and `DISARMED` on timeout
- New `ARM` followed by new `CMD` before motion resumes
- Optional `PC -> ESP32` forwarding
