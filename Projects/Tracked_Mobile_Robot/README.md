# Tracked Mobile Robot

STM32 기반 하위 제어기와 엔코더 모터를 사용해 궤도형 모바일 로봇 플랫폼을 만드는 프로젝트다.

초기 목표는 자율주행 전체 시스템이 아니라, 자율주행으로 확장 가능한 안정적인 하위 구동 플랫폼을 만드는 것이다. 먼저 전원계, 모터 제어, 엔코더, IMU, UART 통신을 검증하고, 이후 ROS2, LiDAR, CAN으로 확장한다.

## Project Direction

- Start point: STM32 motor control and encoder validation
- Main platform: tracked mobile robot chassis
- Low-level controller: NUCLEO-F446RE
- Support controller: ESP32-S3 DevKitC
- Main power: 3S LiPo battery
- Initial communication: UART / USB Serial
- Deferred communication: CAN bus
- Deferred autonomy stack: ROS2, LiDAR, SLAM, Nav2

## Structure

- `00_Project_Charter`: project goal, scope, requirements, inventory
- `01_System_Architecture`: block diagram, interface map, control architecture
- `02_Hardware_Validation`: power, motor, driver, wiring, safety validation
- `03_Firmware`: STM32 firmware design and implementation notes
- `04_PC_Serial_Control`: PC-side serial test scripts and protocol notes
- `05_ROS2_Integration`: ROS2 bridge, topic mapping, RViz validation
- `06_Test_Report`: bench, load, chassis, and field test reports
- `assets`: photos, wiring diagrams, screenshots, plots
- `docs/handoff`: continuation notes for future work

## Initial MVP

The first MVP is complete when:

1. STM32 controls left/right motors with PWM.
2. Encoder signals are read reliably.
3. Left/right motor speeds are estimated.
4. A simple UART command changes robot motion.
5. The tracked chassis can move forward, backward, and rotate at low speed.
6. Power safety rules are documented and followed.

## Current Strategy

- Use BMS: no
- Use CAN now: no
- Use UART first: yes
- Use fuse and main switch: yes
- Use LiPo balance charger: yes
- Use low-voltage alarm and STM32 voltage monitoring: yes
