# Component Inventory

이 문서는 프로젝트에 사용할 부품 목록과 역할을 정리하는 문서다.

## Owned Components

| Category | Component | Role | Notes |
|---|---|---|---|
| MCU | NUCLEO-F446RE | low-level motor controller | STM32 firmware main target |
| MCU | ESP32-S3 DevKitC | support controller | wireless/UI/sensor test candidate |
| Sensor | BNO08x IMU | yaw rate and attitude sensing | odometry validation candidate |
| Power | 3S LiPo battery | main power source | BMS not used |
| Power | LiPo charger | balance charge / storage mode | iMAX B6 class charger |
| Power | XL4015 x2 | 5V buck converter | MCU/sensor power |
| Power | XL4016 | higher-current buck converter | servo/high-current auxiliary candidate |
| Protection | AWG14 fuse holder | main power protection | use blade fuses |
| Protection | main power switch | manual power control | DC 20A-30A class target |
| Protection | 3S low-voltage alarm | LiPo over-discharge warning | required in operation |
| Motor | encoder DC motors x2 types | drivetrain candidates | JGB37-520 encoder status must be checked |
| Driver | motor driver | DC motor drive | voltage/current rating must be verified |
| Mechanical | tracked chassis | robot base | low-speed test platform |
| Wiring | AWG14/16/18 wires | power wiring | high-current and auxiliary power |
| Wiring | 24AWG wires | signal wiring | encoder/UART/I2C/PWM |
| Build | perfboard, headers, sockets | power/signal hub | do not route motor current through perfboard traces |

## Purchase Deferred

| Component | Reason |
|---|---|
| BMS | not used with finished RC LiPo pack in this project phase |
| CAN transceiver | UART first, CAN later |
| USB-CAN adapter | CAN deferred |
| LiDAR | drivetrain and odometry first |
| large 5000mAh battery | current 3S LiPo is enough for initial validation |

## Missing Or Optional

| Component | Priority | Reason |
|---|---|---|
| LiPo safety bag or metal storage box | high | safer charging and storage |
