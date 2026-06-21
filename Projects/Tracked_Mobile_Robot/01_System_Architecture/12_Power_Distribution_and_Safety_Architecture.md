# Power Distribution and Safety Architecture

## Purpose

This document defines the first power distribution and safety architecture for
the tracked mobile robot project.

It expands the project safety decisions into a practical power plan:

- 3S LiPo battery is the main energy source.
- A main fuse and DC-rated switch are placed near the battery.
- Motor power and logic power are treated as separate power domains.
- XL4015/XL4016 buck converters are adjusted and verified before any MCU is
  connected.
- STM32 owns low-voltage decision logic after voltage sensing is implemented.
- A 3S LiPo alarm remains an independent operator warning.
- BMS is not used for the finished RC LiPo pack in this project phase.

This document is not a final schematic. It is the architecture and validation
rule set for safe bench bring-up.

## 1. Safety Principle

The power system must be designed around the failure modes of batteries,
motors, and wiring.

Core rule:

```text
Power is validated before firmware is trusted.
Firmware safety is added after electrical safety is verified.
```

Engineering implications:

- A fuse does not make the robot safe by itself.
- A switch does not replace firmware motor disable logic.
- Firmware low-voltage stop does not replace a LiPo alarm.
- A buck converter setting is not trusted until measured with a multimeter.
- A common ground is required for logic signals, but motor current must not be
  routed through weak signal wiring.

## 2. Power Domains

The robot has three initial power domains.

| Domain | Source | Loads | Notes |
| --- | --- | --- | --- |
| Battery domain | 3S LiPo | fuse, switch, buck inputs, motor rail | High energy, highest risk |
| Motor domain | switched battery rail | MDD10A `POWER+`/`POWER-`, DC motors | Noisy and high current |
| Logic domain | buck converter output | STM32, ESP32, sensors, driver logic | Regulated low-voltage electronics |

The domains share a reference ground where signals cross domains, but their
current paths should remain physically separated as much as practical.

## 3. Main Power Path

Initial power path:

```text
3S LiPo battery
    |
    +-- XT60 main connector
    |
    +-- AWG14 main positive wire
    |
    +-- blade fuse holder
    |
    +-- blade fuse
    |
    +-- DC-rated main switch
    |
    +-- switched battery rail
            |
            +-- MDD10A motor driver POWER+
            |
            +-- XL4015 #1 input
            |
            +-- XL4015 #2 input
            |
            +-- XL4016 input candidate
```

Battery negative path:

```text
3S LiPo negative
    |
    +-- motor driver B-
    |
    +-- buck converter input negative
    |
    +-- controlled common ground reference for logic signals
```

Notes:

- Put the fuse close to the battery positive side.
- The main switch should disconnect the robot power path after the fuse.
- Do not put the fuse only after the power distribution split.
- Do not use perfboard copper traces for motor current.
- XT60 polarity must be checked before the first powered test.

## 4. LiPo Operating Envelope

A 3S LiPo pack has three cells in series.

Reference values:

| State | Per cell | Pack voltage |
| --- | --- | --- |
| Fully charged | about 4.2 V | about 12.6 V |
| Nominal | about 3.7 V | about 11.1 V |
| Storage target | about 3.7-3.85 V | about 11.1-11.55 V |
| Conservative warning region | about 3.6 V | about 10.8 V |
| Conservative stop region | about 3.5 V | about 10.5 V |

Project rules:

- Do not intentionally deep-discharge the pack.
- Do not rely only on firmware for LiPo protection.
- Use the 3S low-voltage alarm during tests.
- Disconnect the battery after every test.
- Store the pack at storage voltage when it will not be used soon.
- Stop using a swollen, punctured, overheated, or mechanically damaged pack.
- Charge only with a LiPo balance charger.

Initial voltage policy:

| Condition | Initial behavior |
| --- | --- |
| Pack above warning threshold | Operation allowed if no other fault exists |
| Pack near warning threshold | Telemetry warning and prepare to stop |
| Pack below stop threshold | STM32 disables motor output |
| Low-voltage alarm sounds | Operator stops test and disconnects battery |

The exact thresholds must be tuned after measuring voltage sag under load.

## 5. Fuse Architecture

The fuse primarily protects wiring and reduces fire risk during a fault. It
does not guarantee that the motor driver or MCU survives every fault.

Initial blade fuse plan:

| Test stage | Fuse candidate | Reason |
| --- | --- | --- |
| Bench power test, no motor load | 10 A | Lower fault energy during early wiring checks |
| Wheels lifted motor test | 10 A or 15 A | Low-load motor behavior only |
| Low-speed chassis test | 15 A or 20 A | Allows moderate drivetrain load |
| Higher-load test | 30 A only after current measurement | Not allowed as the first test fuse |

Selection rules:

- Start with the lowest fuse that does not nuisance-blow during the current
  test stage.
- Increase fuse rating only after measuring or estimating real current.
- Fuse rating must remain compatible with wire gauge and connector current.
- A larger fuse is not a fix for a wiring, stall, or mechanical friction issue.

## 6. Main Switch Architecture

The main switch is a manual energy isolation device.

Requirements:

- DC-rated switch.
- Current rating suitable for the expected robot current.
- Placed after the fuse in the battery positive path.
- Mechanically reachable during bench testing.
- Clearly labeled ON/OFF direction.

Important limitation:

```text
The main switch is not an emergency-stop design by itself.
```

The firmware must still set MDD10A PWM outputs to zero during faults, timeout,
disarm, and startup.

## 7. Buck Converter Architecture

Initial converter roles:

| Converter | Initial role | Notes |
| --- | --- | --- |
| XL4015 #1 | STM32/ESP32 logic 5 V candidate | Verify output before connection |
| XL4015 #2 | sensor or auxiliary 5 V candidate | Keeps noisy/aux load separate |
| XL4016 | higher-current auxiliary candidate | Deferred unless a load requires it |

Rules:

- Adjust each buck converter without MCU boards connected.
- Verify output voltage with a multimeter before connecting loads.
- Start at 5.0 V for 5 V rails unless a module requires a different voltage.
- Do not connect 3S LiPo directly to STM32, ESP32, sensors, or encoder logic.
- Do not assume the trimmer position is safe when the converter is new.
- Record the converter output voltage before every first integration test.

Board-power caution:

- During early firmware development, powering STM32/ESP32 from USB is simpler
  and safer.
- When switching to buck-powered operation, verify the board's allowed 5 V
  input path from the board manual.
- Avoid back-powering a PC USB port from the robot buck converter.
- Choose one controlled power method for each test and write it in the test
  log.

## 8. Grounding Architecture

The project needs common ground for logic signals, but the ground path must be
intentional.

Ground model:

```text
Battery negative
    |
    +-- motor current return path to MDD10A
    |
    +-- buck converter negative input
            |
            +-- logic ground reference
                    |
                    +-- STM32 GND
                    +-- ESP32 GND
                    +-- sensor GND
                    +-- MDD10A logic GND
```

Rules:

- STM32 and MDD10A logic GND must be common for PWM/DIR signals to work.
- ESP32 and STM32 GND must be common for UART to work.
- Sensor GND and STM32 GND must be common for I2C/ADC signals to work.
- Avoid routing high motor current through thin signal ground wires.
- Keep motor current loops short and physically away from UART/I2C/encoder
  wires when practical.

## 9. Motor Power Safety

MDD10A sits between the motor power rail and the motors.

Rules:

- Motor power is connected only after logic output behavior is verified.
- STM32 PWM pins must start at zero duty.
- MDD10A PWM pins must default to zero during STM32 reset.
- Use external pull-downs on PWM lines or a separate power gate if reset
  behavior is uncertain.
- For one motor, PWM must be ramped to zero before changing `DIR`.
- First motor test must be low duty with the robot lifted or tracks unloaded.

Recommended staged motor tests:

| Stage | Motor power | Motor load | Goal |
| --- | --- | --- | --- |
| M0 | disconnected | none | Verify STM32 PWM/DIR pins |
| M1 | connected | motor disconnected from track if possible | Verify driver output behavior |
| M2 | connected | wheels/tracks lifted | Verify direction and low-duty response |
| M3 | connected | chassis on ground | Low-speed motion only |

## 10. Logic and Signal Protection

Early prototype protection candidates:

| Signal | Protection candidate | Reason |
| --- | --- | --- |
| STM32 PWM/DIR to MDD10A | 100-330 ohm series resistor | Limits fault current during wiring mistakes |
| UART TX lines | 100-330 ohm series resistor | Reduces risk during early cross-board tests |
| Encoder outputs | level shifter or divider if needed | Required if output exceeds STM32 input limits |
| PWM lines | pull-down resistor | Keeps MDD10A command at zero during reset |

The encoder voltage must be measured before direct STM32 connection.

## 11. Battery Voltage Sensing Plan

STM32 will later monitor battery voltage through a resistor divider and ADC.

Initial plan:

```text
Battery switched rail
    |
    +-- resistor divider
    |
    +-- STM32 ADC input
```

Requirements:

- Divider output must stay below the STM32 ADC input limit at full charge
  voltage.
- Use resistor values that limit current but keep ADC readings stable enough.
- Add filtering later if motor noise makes readings unstable.
- Calibrate ADC reading against a multimeter.
- The 3S LiPo alarm remains connected independently during early tests.

Example design target:

```text
12.6 V full-charge pack -> ADC voltage safely below 3.3 V
```

The exact resistor values are not finalized in this document.

## 12. Power-Up Procedure

### Stage A: No Battery, No MCU Load

Checklist:

- Inspect polarity of XT60, fuse holder, switch, and distribution points.
- Check continuity of battery positive path with switch ON.
- Check open circuit with switch OFF.
- Check there is no short between battery positive and negative rails.
- Label motor rail and logic rail.

### Stage B: Buck Converter Setup

Checklist:

- Connect buck converter input through a fuse.
- Do not connect STM32/ESP32 yet.
- Turn on main switch.
- Adjust output to target voltage.
- Measure output polarity.
- Turn off switch and disconnect battery.

### Stage C: Logic-Only Power

Checklist:

- Connect STM32/ESP32/sensor rail only after buck output is verified.
- Keep motor driver `B+` disconnected if practical.
- Confirm board power LEDs and USB debug behavior.
- Confirm UART or USB serial communication.
- Confirm STM32 motor outputs stay disabled at boot.

### Stage D: Driver Logic Test

Checklist:

- Connect MDD10A logic side.
- Keep motor power disabled or motors disconnected where practical.
- Verify PWM outputs are zero at boot.
- Verify PWM pins are zero at boot.
- Command low-duty output only after confirming direction logic.

### Stage E: Low-Power Motor Test

Checklist:

- Use a conservative fuse.
- Lift tracks off the ground.
- Apply very low duty first.
- Confirm motor direction.
- Confirm no abnormal heating, smell, or reset.
- Stop immediately if the low-voltage alarm sounds.

## 13. Shutdown Procedure

Normal shutdown:

1. Send `DISARM` or stop command.
2. Confirm PWM output is zero.
3. Keep MDD10A PWM outputs at zero.
4. Turn off main switch.
5. Disconnect LiPo battery.
6. Let motor drivers and buck converters cool if warm.
7. Record any abnormal behavior.

Emergency shutdown:

1. Release control input or send stop if possible.
2. Turn off main switch if physically safe.
3. Disconnect battery if the switch does not stop the condition.
4. Do not touch overheated or damaged LiPo directly.

## 14. Validation Measurements

Initial measurements to record:

| Measurement point | Expected result | When |
| --- | --- | --- |
| LiPo pack voltage | Within safe 3S range | Before every test |
| After fuse/switch voltage | Similar to pack voltage when ON | First power path test |
| Buck output | 5.0 V target unless otherwise specified | Before MCU connection |
| STM32 5 V/3.3 V rails | Within board-allowed range | Logic-only power |
| ESP32 power rail | Within board-allowed range | Logic-only power |
| MDD10A logic input | 3.3 V PWM/DIR signal | Driver logic test |
| Voltage between STM32 GND and driver GND | Near 0 V | Before signal test |
| Motor rail voltage during low duty | No severe collapse | Low-speed motor test |

Record format:

```text
Date:
Battery:
Fuse:
Switch:
Buck converter:
Load connected:
Measured voltage:
Observation:
Decision:
```

## 15. Fault Response Table

| Fault | Detection | Required response |
| --- | --- | --- |
| Low battery alarm sounds | Audible alarm | Stop test, disarm, disconnect LiPo |
| STM32 ADC below stop threshold | Firmware | Set PWM zero, disable driver, report fault |
| UART/CAN command timeout | Firmware | Set PWM zero, keep system disarmed or safe |
| Buck output over target | Multimeter | Do not connect MCU, readjust converter |
| Reverse polarity found | Visual/multimeter | Do not power, fix wiring |
| Fuse blows | Fuse inspection | Stop and investigate current path before replacing |
| MCU resets when motor starts | Serial log/LED reset | Stop motor test, inspect power/GND/noise |
| Motor driver overheats | Touchless check/thermal caution | Stop test and reduce load/duty |
| Encoder signal overvoltage | Multimeter/oscilloscope | Add level shifting before STM32 input |

## 16. Items Deferred From First Power Bring-Up

Deferred:

- CAN bus power integration
- LiDAR power integration
- ROS2 computer power integration
- custom power distribution PCB
- high-load driving
- battery current sensor
- fully integrated emergency-stop circuit

Reason:

The first power phase should validate basic battery, fuse, switch, buck,
controller, driver, and motor behavior before adding more loads.

## 17. Exit Criteria

This architecture is ready for HAL bare-metal drivetrain bring-up when:

- The main battery path is fused and switched.
- Buck converter outputs are measured before MCU connection.
- STM32/ESP32/sensor power is separated from raw battery voltage.
- MDD10A motor current does not pass through perfboard traces.
- Common ground is intentional and documented.
- MDD10A PWM output defaults to zero.
- Low-voltage alarm is used during LiPo tests.
- A measurement log exists for the first powered test.

## Final Decision

The initial power architecture uses a conservative fused 3S LiPo distribution
with separate motor and logic domains.

STM32 firmware will later add voltage-based safety behavior, but the first line
of protection is still correct wiring, fuse selection, measured buck output,
manual switch control, and disciplined LiPo handling.
