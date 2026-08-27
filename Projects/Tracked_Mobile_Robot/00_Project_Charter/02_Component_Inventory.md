# Component Inventory

이 문서는 프로젝트에 사용할 부품 목록과 역할을 정리하는 문서다.

## Owned Components

| Category | Component | Role | Notes |
|---|---|---|---|
| MCU | NUCLEO-F446RE | low-level motor controller | STM32 firmware main target |
| MCU | ESP32-S3 DevKitC | support controller | wireless/UI/sensor test candidate |
| Firmware | STM32 HAL / CubeMX | initial bring-up | validate PWM, encoder, ADC, UART first |
| Firmware | FreeRTOS | required later firmware architecture | task, queue, timing, safety separation |
| Firmware | STM32 LL Driver | advanced migration target | timing-critical paths after HAL validation |
| Sensor | BNO08x IMU | yaw rate and attitude sensing | odometry validation candidate |
| Power | 3S LiPo battery | main power source | BMS not used |
| Power | LiPo charger | balance charge / storage mode | iMAX B6 class charger |
| Power | XL4015 x2 | 5V buck converter | MCU/sensor power |
| Protection | AWG14 fuse holder | main power protection | use blade fuses |
| Protection | main power switch | manual power control | DC 20A-30A class target |
| Protection | 3S low-voltage alarm | LiPo over-discharge warning | required in operation |
| Motor | encoder DC motors x2 types | drivetrain candidates | JGB37-520 encoder status must be checked |
| Driver | BTS7960-class module | previous motor-driver candidate | superseded by MDD10A for the first drivetrain path; kept as comparison history |
| Driver | MDD10A | first motor driver path | dual-channel PWM+DIR driver for left/right DC motors |
| Mechanical | tracked chassis | robot base | low-speed test platform |
| Wiring | AWG14/16/18 wires | power wiring | high-current and auxiliary power |
| Wiring | 24AWG wires | signal wiring | encoder/UART/I2C/PWM |
| Build | perfboard, headers, sockets | power/signal hub | do not route motor current through perfboard traces |

## Physical E-stop Procurement Snapshot — 2026-08-27

`USER-REPORTED RECEIVED`는 포장 도착 상태다. Exact part/수량/각인, continuity, polarity,
pin/terminal map, fit과 retention을 확인한 `INCOMING PASS`가 아니다.

| Ref | Component | Qty | Role | Current status |
| --- | --- | ---: | --- | --- |
| K1 | TE `V23134J1052D642` / `1393304-9` | 1 | De-energized-open motor-power high-side cut relay | USER-REPORTED RECEIVED / INCOMING OPEN |
| K1 socket | TE `VCF7-1000` / `1393310-4` | 1 | K1 mounting and terminal housing | USER-REPORTED RECEIVED / INCOMING OPEN |
| K1 terminals | TE `280756-4` main x2, `42281-1` coil x2 | 4 | K1 main/coil wire termination | USER-REPORTED RECEIVED / INCOMING OPEN; `280756-4` is AWG 12~10 |
| S0 | Autonics `SF2ER-E2R2B-A` | 1 | Mechanical-latching emergency-stop, two independent NC paths | USER-REPORTED RECEIVED / INCOMING OPEN |
| S2 | IDEC `ABW110G` | 1 | Deliberate momentary re-enable input | ORDERED / NOT RECEIVED |
| K2 | Panasonic `TX2-12V` | 2 | Low-current seal-in/control relay | RECEIVED / UNPOWERED SCREEN 2/2 PASS; POWERED OPEN |
| U1 | Vishay `VO617A-3` | 1 | Galvanically isolated S0-B sense conditioner for STM32 PC7 | USER-REPORTED RECEIVED / INCOMING OPEN |
| R | measured `670.1 Ω`, `9.97 kΩ` | 1 each selected | Optocoupler LED current limit and PC7 external pull-up candidates | VALUE PRECHECK PASS / INTEGRATION OPEN |
| F2 | Littelfuse `0287001.PXCN` 1 A ATOF | 1 | Control-loop wiring/short protection | USER-REPORTED RECEIVED / INCOMING AND COORDINATION OPEN |
| F2 holder | Littelfuse `FHAC0001ZXJA` | 1 | Inline holder for F2 | USER-REPORTED RECEIVED / INCOMING OPEN |
| D-clamp | Vishay `P6KE16CA-E3/54` | 3 | K1/K2 coil transient clamp candidates | ORDERED / NOT RECEIVED |
| J-ESTOP | 6P waterproof harness + 18 AWG leads | 1 set | Removable S0/S2 operator-panel connection | USER-REPORTED RECEIVED / CAVITY MAP, ISOLATION, RETENTION OPEN |
| F1 | Received Littelfuse holder + fuse marked `257/32V/10` | 1 set | Main-path wiring/short protection prototype | UNPOWERED SCREEN PASS; ORDERED `287` VS ACTUAL `257` IDENTITY AND POWERED TEST OPEN |

Complete Physical E-stop integration, powered K1/K2 coil test와 actual motor energy는 S2/TVS
도착, 모든 incoming check와 motor-disconnected `T-ESTOP-001~004 + T-ESTOP-005A` PASS 전까지
금지한다.

## Purchase Deferred

| Component | Reason |
|---|---|
| BMS | not used with finished RC LiPo pack in this project phase |
| CAN transceiver | UART first, required later CAN phase |
| USB-CAN adapter | required later for CAN debugging |
| LiDAR | drivetrain and odometry first |
| large 5000mAh battery | current 3S LiPo is enough for initial validation |

## Missing Or Optional

| Component | Priority | Reason |
|---|---|---|
| LiPo safety bag or metal storage box | high | safer charging and storage |
