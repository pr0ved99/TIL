# Power Bring-up Checklist

## 목적

이 문서는 3S LiPo battery를 로봇 전원계에 처음 연결하기 전후의 안전 확인 절차를 정의한다.

목표는 firmware를 믿기 전에 battery, fuse, switch, wiring, polarity, ground path가 안전한지 확인하는 것이다.

## Test Scope

이 단계에서 허용되는 것:

- Battery polarity 확인
- XT60 polarity 확인
- Fuse holder continuity 확인
- Main switch ON/OFF 동작 확인
- Switched battery rail 전압 확인
- Buck converter input 전압 확인
- MDD10A motor power input 전압 확인

이 단계에서 금지되는 것:

- Motor를 실제로 구동
- STM32/ESP32를 buck converter에 연결
- Unknown voltage를 MCU pin에 연결
- Fuse 없이 battery positive path 구성
- Switch 없이 test 진행

## Required Equipment

| Item | Purpose |
| --- | --- |
| Multimeter | Voltage, continuity, polarity check |
| 3S LiPo battery | Main power source |
| XT60 connector/cable | Main battery connector |
| Blade fuse holder | Main positive path protection |
| 10 A blade fuse | First low-energy validation fuse |
| DC-rated main switch | Manual power isolation |
| AWG14 red/black wire | Main battery path |
| LiPo low-voltage alarm | Independent battery warning |
| Heat shrink / insulation | Exposed conductor protection |

## Pre-Power Checklist

### Battery and Connector

| Check | Expected | Result |
| --- | --- | --- |
| Battery pack voltage measured | 3S safe range, below 12.6 V full charge | TBD |
| XT60 polarity checked | Red = positive, black = negative | TBD |
| Connector solder joints inspected | No cold joint, no exposed strand | TBD |
| Balance connector not damaged | No bent or loose pins | TBD |
| LiPo pack condition inspected | No swelling, puncture, heat, smell | TBD |

Measured battery voltage:

```text
Date:
Battery:
Pack voltage:
Cell voltages if measured:
Operator:
```

### Fuse and Switch Path

| Check | Expected | Result |
| --- | --- | --- |
| Fuse holder placed near battery positive | Yes | TBD |
| Initial fuse rating | 10 A | TBD |
| Switch placed after fuse | Yes | TBD |
| Switch OFF continuity | Open circuit | TBD |
| Switch ON continuity | Closed circuit | TBD |
| Positive path insulation | No exposed conductor | TBD |

Power path:

```text
3S LiPo +
    -> XT60
    -> fuse holder
    -> blade fuse
    -> main switch
    -> switched battery rail
```

### Ground Path

| Check | Expected | Result |
| --- | --- | --- |
| Battery negative path identified | Clear black wire path | TBD |
| Motor driver ground path planned | Heavy return path, not signal wire | TBD |
| Buck converter negative tied to battery negative | Yes | TBD |
| Logic ground reference planned | Common GND where signals cross domains | TBD |

## First Power-On: No Load

Condition:

```text
No STM32 connected
No ESP32 connected
No sensor connected
No motor connected
Buck converter outputs not connected to boards
```

Procedure:

1. Install 10 A fuse.
2. Keep switch OFF.
3. Connect LiPo through XT60.
4. Measure voltage before switch.
5. Turn switch ON briefly.
6. Measure switched battery rail.
7. Turn switch OFF.
8. Confirm switched rail drops or is disconnected as expected.

Measurements:

| Measurement | Expected | Actual |
| --- | --- | --- |
| Battery + to battery - | Pack voltage | TBD |
| Before switch + to GND | Pack voltage | TBD |
| Switch OFF rail + to GND | 0 V or disconnected | TBD |
| Switch ON rail + to GND | Pack voltage | TBD |
| Fuse voltage drop | Near 0 V under no load | TBD |

## First Power-On: Buck Inputs Only

Condition:

```text
Buck converter input connected
Buck converter output disconnected from electronics
Motor drivers may be disconnected or motor output open
```

Procedure:

1. Switch OFF.
2. Connect buck converter inputs to switched battery rail.
3. Switch ON.
4. Measure buck input voltage.
5. Measure buck output voltage before calibration.
6. Switch OFF.

Measurements:

| Converter | Input voltage | Output voltage before calibration | Notes |
| --- | --- | --- | --- |
| XL4015 #1 | TBD | TBD | TBD |
| XL4015 #2 | TBD | TBD | TBD |
| XL4016 | TBD | TBD | TBD |

Important:

```text
If buck output is not already known safe, do not connect it to STM32, ESP32, sensors, or encoders.
```

## First Power-On: Motor Driver Power Input Only

Condition:

```text
MDD10A motor output disconnected
MDD10A logic input may remain disconnected
Motor disconnected
STM32 disconnected
```

Procedure:

1. Verify MDD10A POWER+ and POWER- polarity.
2. Switch ON briefly.
3. Measure MDD10A POWER+ to POWER- voltage.
4. Check for heat, smell, smoke, abnormal sound.
5. Switch OFF immediately after measurement.

Measurements:

| Driver | POWER+ to POWER- voltage | Heat/smell/noise | Result |
| --- | --- | --- | --- |
| MDD10A | TBD | TBD | TBD |

## Stop Conditions

Stop the test immediately if:

- Fuse blows
- Wire heats
- Connector heats
- Buck converter output is unexpectedly high
- Battery voltage sags abnormally under no load
- Smoke, smell, spark, or sound appears
- Polarity is uncertain

Recovery rule:

```text
원인을 찾기 전에는 fuse를 더 큰 값으로 교체하지 않는다.
```

## Result Summary

| Item | Pass/Fail | Notes |
| --- | --- | --- |
| Battery polarity | TBD | TBD |
| Fuse path | TBD | TBD |
| Main switch | TBD | TBD |
| Switched battery rail | TBD | TBD |
| Buck input path | TBD | TBD |
| MDD10A motor power input | TBD | TBD |

## Next Step

Power path가 통과하면 다음 문서로 진행한다.

```text
02_Buck_Converter_Calibration_Log.md
```
