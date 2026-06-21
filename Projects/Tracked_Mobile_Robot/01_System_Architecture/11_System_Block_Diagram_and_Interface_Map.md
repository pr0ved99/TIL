# System Block Diagram and Interface Map

## Purpose

This document defines the first complete hardware/software interface map for
the tracked mobile robot project.

It connects the previous architecture documents into one system view:

- STM32 owns low-level drivetrain control and safety.
- MDD10A converts STM32 PWM/DIR commands into motor power.
- Encoders, IMU, and battery sensing provide feedback to STM32.
- ESP32-S3 is a support controller for telemetry, wireless UI, and later
  bridging.
- UART is the first STM32-ESP32 interface.
- CAN, FreeRTOS, LL Driver migration, ROS2, LiDAR, and SLAM are later
  expansion phases.

This document is not the detailed wiring diagram. It is the interface boundary
document that later wiring, firmware, and test documents should reference.

## 1. System Boundary

The first project boundary is a low-speed tracked drivetrain platform.

Inside the first MVP:

- 3S LiPo power input
- fuse and main switch
- buck converters for logic power
- STM32 NUCLEO-F446RE low-level controller
- one MDD10A dual-channel motor driver
- two DC geared motors with encoders
- BNO08x IMU
- ESP32-S3 DevKitC support controller
- UART command and telemetry link

Outside the first MVP:

- CAN bus robot command interface
- ROS2 bridge
- LiDAR
- SLAM/Nav2
- full autonomy stack
- custom PCB

Rule:

```text
The first MVP proves the robot can move safely and be measured.
It does not need to be autonomous yet.
```

## 2. Top-Level Block Diagram

```text
                       Future expansion
        +---------------------------------------------+
        | PC / Jetson / ROS2 / LiDAR / SLAM / Nav2    |
        | Deferred from first drivetrain MVP          |
        +----------------------+----------------------+
                               |
                         future bridge
                               |
+------------------------------v-------------------------------+
|                         ESP32-S3                              |
|  Wireless UI / telemetry display / command forwarding         |
|  Does not directly own motor outputs or safety decisions       |
+------------------------------+-------------------------------+
                               |
                         UART 3.3 V
                   115200 8N1 text protocol
                               |
+------------------------------v-------------------------------+
|                    STM32 NUCLEO-F446RE                        |
|  Low-level controller and safety owner                         |
|                                                               |
|  - command validation                                          |
|  - motor output safety gate                                    |
|  - PWM generation                                              |
|  - encoder counting                                            |
|  - speed estimation                                            |
|  - battery voltage decision                                    |
|  - IMU sampling candidate                                      |
|  - timeout stop and fault state                                |
+------+----------+----------+----------+----------+-------------+
       |          |          |          |          |
   PWM/DIR L  PWM/DIR R  Encoder L  Encoder R    I2C / ADC
       |          |          |          |          |
+------v----------------+ +--v-----+ +--v-----+ +--v------------+
| MDD10A dual-channel   | | Left   | | Right  | | BNO08x IMU / |
| motor driver          | | encoder| | encoder| | battery ADC  |
+-----+-----------+-----+ +--------+ +--------+ +---------------+
      |           |
      v           v
 Left DC     Right DC
 motor       motor
```

## 3. Power Block Diagram

The detailed power architecture is handled in
`12_Power_Distribution_and_Safety_Architecture.md`. This document records only
the interface-level power model.

```text
3S LiPo battery
    |
    +-- XT60 main connector
    |
    +-- blade fuse holder
    |
    +-- main power switch
    |
    +-- motor power rail --------------------+
    |                                        |
    |                                  MDD10A POWER+
    |
    +-- buck converter input
             |
             +-- 5 V logic/aux rail candidate
             |
             +-- STM32 / ESP32 / sensor supply path
```

Common rules:

- Use a fuse in the main battery path.
- Use a DC-rated main switch.
- Do not route motor current through perfboard traces.
- Keep motor power wiring and logic signal wiring physically separated where
  practical.
- STM32, ESP32, sensors, and motor-driver logic must share a common reference
  ground for signals to work.
- BMS is not used in this project phase.
- LiPo balance charging and low-voltage alarm remain required.

## 4. Controller Ownership Map

| Function | Owner | Notes |
| --- | --- | --- |
| Motor PWM/DIR output | STM32 | Two PWM outputs and two DIR GPIO outputs for MDD10A |
| Motor output safety gate | STM32 | Must force PWM zero during boot, disarm, timeout, and fault |
| Encoder counting | STM32 | Required for RPM and odometry |
| Battery voltage safety | STM32 | ESP32 may display the value but does not decide safety |
| Command timeout | STM32 | Motion stops if valid commands stop arriving |
| Emergency stop behavior | STM32 | ESP32 or PC may request stop, but STM32 enforces it |
| Wireless dashboard | ESP32-S3 | Deferred until UART telemetry is stable |
| Wi-Fi command forwarding | ESP32-S3 | Requests only, not final motor authority |
| USB serial debug | STM32 and ESP32 | Used during bring-up |
| CAN command interface | STM32 later | Deferred until UART model is proven |
| ROS2 bridge | Future upper layer | Must not bypass STM32 safety rules |

Core rule:

```text
External systems may request motion.
STM32 decides whether motion is allowed.
```

## 5. STM32 Interface Map

Candidate STM32 interfaces for the first MVP:

| Interface | Direction | Connected block | Purpose | Status |
| --- | --- | --- | --- | --- |
| Timer PWM x2 | STM32 -> MDD10A | Left/right motor driver channels | Motor duty control | Required |
| GPIO DIR x2 | STM32 -> MDD10A | Left/right motor driver channels | Motor direction control | Required |
| Timer encoder input | Motor encoder -> STM32 | Left encoder A/B | Count and direction | Required |
| Timer encoder input | Motor encoder -> STM32 | Right encoder A/B | Count and direction | Required |
| ADC input | Battery divider -> STM32 | Main battery monitor | Low-voltage decision | Required |
| I2C | STM32 <-> BNO08x | IMU | Yaw/attitude candidate | Required after motor bring-up |
| USART1 | STM32 <-> ESP32 | Support controller | Command/telemetry | Required |
| USB serial | STM32 <-> PC | Development PC | Debug and manual command | Required |
| bxCAN | STM32 <-> CAN transceiver | Future CAN bus | Later command/telemetry path | Deferred |

Pin allocation is not finalized in this document.

The current architecture keeps the pin plan close to PB6/PB7 PWM plus PC8/PC9
DIR, pending CubeMX and header-access validation.

## 6. ESP32-S3 Interface Map

Candidate ESP32-S3 responsibilities:

| Interface | Direction | Connected block | Purpose | Status |
| --- | --- | --- | --- | --- |
| UART | ESP32 <-> STM32 | Low-level controller | Command forwarding and telemetry | First interface |
| USB Serial/JTAG | ESP32 <-> PC | Development PC | Flashing and debug | Required |
| Wi-Fi | ESP32 <-> PC/phone | Dashboard or log bridge | Later |
| GPIO/RGB LED | ESP32 local | Board test | Already validated in earlier ESP32 practice | Optional |

ESP32 does not connect directly to motor-driver inputs in the first
architecture.

## 7. Motor Driver Interface Map

Use one MDD10A board for both motors.

For each MDD10A channel:

| Signal | Direction | Owner | Purpose |
| --- | --- | --- | --- |
| `PWMx` | STM32 -> MDD10A | STM32 PWM timer | Motor speed duty control |
| `DIRx` | STM32 -> MDD10A | STM32 GPIO | Motor direction selection |
| `GND` | common ground | power system | Signal reference |
| `POWER+`, `POWER-` | battery rail -> MDD10A | power system | Motor power input |
| `M1A/M1B`, `M2A/M2B` | MDD10A -> motor | MDD10A | Motor output |

Firmware safety rule:

```text
Before changing direction, ramp PWM to zero, change DIR, then raise PWM again.
```

## 8. Sensor Interface Map

| Sensor | Interface | Owner | First use |
| --- | --- | --- | --- |
| Left motor encoder | Timer encoder mode or interrupt counting | STM32 | RPM and direction validation |
| Right motor encoder | Timer encoder mode or interrupt counting | STM32 | RPM and direction validation |
| BNO08x IMU | I2C candidate | STM32 initially | Yaw/attitude logging and odometry support |
| Battery voltage divider | ADC | STM32 | Low-voltage monitoring |
| 3S LiPo low-voltage alarm | Direct battery balance lead | Human/operator | Independent audible warning |

Sensor data ownership:

- Raw encoder count belongs to STM32.
- Raw battery voltage belongs to STM32.
- Raw IMU data should initially be consumed by STM32 for odometry experiments.
- ESP32 may receive reduced telemetry over UART.

## 9. Communication Interface Map

### Initial Path

```text
PC serial terminal or ESP32
        |
        v
UART command request
        |
        v
STM32 command parser
        |
        v
safety gate + command clamp
        |
        v
motor control output
```

### Telemetry Path

```text
STM32 sensor/control state
        |
        v
UART telemetry frame
        |
        v
ESP32 display/log/forwarding
```

Initial UART contract:

- 3.3 V UART
- 115200 baud
- 8 data bits, no parity, 1 stop bit
- newline-terminated ASCII messages
- command timeout enforced by STM32

### Future CAN Path

```text
Upper controller / USB-CAN / future node
        |
        v
CAN transceiver
        |
        v
STM32 bxCAN
        |
        v
same STM32 safety gate
```

CAN must reuse the same safety ownership model as UART.

## 10. Software Block Map

### Phase 1: Bare-Metal HAL MVP

```text
main loop
  |
  +-- read UART command
  +-- validate command timeout
  +-- read encoder counters
  +-- estimate speed
  +-- read battery ADC
  +-- update safety state
  +-- update PWM outputs
  +-- print telemetry
```

### Phase 2: FreeRTOS Architecture

```text
comm_task
    |
    v
command queue
    |
    v
motor_control_task <---- sensor/battery state
    |
    v
PWM output

safety_task
    |
    v
global safety gate

telemetry_task
    |
    v
UART/CAN status publishing
```

Rule:

- Communication code does not directly write PWM.
- Safety state gates every motor command.
- Motor control timing must remain stable.

## 11. Interface Risk Register

| Risk | Affected interface | Mitigation |
| --- | --- | --- |
| Motor noise resets MCU | power/GND/PWM | separate power routing, common ground, short signal wires, staged tests |
| MDD10A PWM/DIR input wiring error | STM32 -> MDD10A logic | logic-only PWM/DIR bench test, record channel mapping |
| Encoder output exceeds STM32 input tolerance | encoder -> STM32 | measure encoder output before connection, use level shifting if needed |
| UART wires pick up motor noise | STM32 <-> ESP32 | short wires, GND reference, test before motor power |
| Buck converter misadjusted | logic power | adjust without MCU connected, verify with multimeter |
| Command source freezes | UART/CAN command | STM32 command timeout stop |
| Software task blocks motor loop | firmware architecture | defer FreeRTOS until HAL baseline exists, use queues and priorities |
| CAN wiring/debug complexity delays motor bring-up | CAN bus | validate drivetrain first, test CAN standalone later |

## 12. Exit Criteria for This Architecture Map

This document is complete enough when:

- Each physical block has an owner.
- Each safety decision has an owner.
- Initial UART path is separated from future CAN path.
- Motor driver signal requirements are clear.
- Sensor data ownership is clear.
- Future ROS2/autonomy expansion cannot bypass STM32 safety logic.

## Final Decision

The first tracked robot architecture is STM32-centered.

ESP32, PC, future CAN nodes, and future ROS2 bridges may request or display
robot motion, but the STM32 remains the low-level authority for motor output,
sensor feedback, command timeout, and safety gating.
