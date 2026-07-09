# Initial Purchase and Safety

## Current Decision

- BMS is not used in the initial power architecture.
- CAN communication is deferred from first power and motor bring-up, but remains
  a required later project phase.
- UART / USB Serial is used first.
- LiPo battery is charged only with a balance charger.
- Main power line uses a fuse and a manual switch.
- Low-voltage protection uses a 3S LiPo alarm and later STM32 ADC voltage monitoring.

## Initial Power Path

```text
3S LiPo
-> XT60
-> AWG14 fuse holder
-> blade fuse
-> main power switch
-> power distribution
   -> motor driver
   -> XL4015 #1
   -> XL4015 #2
```

## First Test Fuse Plan

```text
bench test: 10A or 15A
wheels lifted test: 15A or 20A
low-speed chassis test: 20A
higher-load test: 30A only after current measurements
```

## LiPo Safety Rules

- Use balance charge mode.
- Do not charge unattended.
- Do not store fully charged for long periods.
- Use storage mode for long-term storage.
- Stop using swollen, punctured, or overheated packs.
- Disconnect battery after every test.
- Check XT60 polarity before first connection.
- Keep charging and storage away from flammable materials.

## Buck Converter Rules

- Adjust XL4015 output with a multimeter before connecting any board.
- Use 5.0V for STM32/ESP32/sensor rails unless a module requires otherwise.
- Do not power STM32/ESP32 directly from 3S LiPo.
- Keep motor power wiring separate from signal wiring.
- Connect all grounds at a controlled common reference point.

## Deferred Items

- CAN bus during first power and motor bring-up
- LiDAR
- ROS2 navigation
- custom PCB
- custom battery pack BMS

## Required Later Learning Items

- FreeRTOS task architecture
- CAN transceiver and CAN bus validation
- USB-CAN based bus inspection
- HAL to LL Driver migration for timing-critical firmware paths
