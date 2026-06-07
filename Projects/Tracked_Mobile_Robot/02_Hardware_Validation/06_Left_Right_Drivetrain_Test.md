# Left Right Drivetrain Test

## 목적

이 문서는 left/right motor와 MDD10A dual-channel driver를 사용해 궤도차량 drivetrain을 저속으로 검증하는 절차를 정의한다.

목표는 한쪽 motor 단독 검증 이후, 좌우 방향, encoder sign, straight motion, rotation, timeout stop, heat behavior를 chassis 수준에서 확인하는 것이다.

## Entry Criteria

| Criteria | Required result |
| --- | --- |
| Power bring-up | Passed |
| Buck calibration | Passed if buck-powered electronics used |
| MDD10A logic input | Passed |
| Encoder signal safety | Passed or encoder disconnected intentionally |
| Left motor no-load | Passed |
| Right motor no-load | Passed |
| Fuse selected | Low-stage fuse selected |
| Main switch reachable | Yes |

## Test Setup

Initial setup:

```text
Robot lifted or tracks unloaded first
Low PWM duty limit
Short command duration
LiPo alarm connected
Fuse installed
Main switch reachable
```

Configuration:

| Item | Value |
| --- | --- |
| Battery voltage before test | TBD |
| Fuse rating | TBD |
| PWM frequency | TBD |
| Duty limit | TBD |
| Command timeout | TBD |
| Encoder connected? | TBD |
| Test surface | TBD |
| Tracks lifted? | TBD |

## Test 1: Dual Motor Boot Safety

Procedure:

1. Connect MDD10A and both motors.
2. Keep robot lifted.
3. Power ON.
4. Confirm no motor moves at boot.
5. Confirm telemetry/state if available.

| Check | Expected | Observed |
| --- | --- | --- |
| Left motor movement at boot | None | TBD |
| Right motor movement at boot | None | TBD |
| PWM outputs | Zero | TBD |

## Test 2: Left/Right Independent Direction

Procedure:

1. Command left motor only forward low duty.
2. Command left motor only reverse low duty.
3. Command right motor only forward low duty.
4. Command right motor only reverse low duty.
5. Record physical direction and encoder sign.

| Motor | Command | Physical direction | Encoder sign | Result |
| --- | --- | --- | --- | --- |
| Left | Forward | TBD | TBD | TBD |
| Left | Reverse | TBD | TBD | TBD |
| Right | Forward | TBD | TBD | TBD |
| Right | Reverse | TBD | TBD | TBD |

Pass condition:

```text
Command convention, physical direction, encoder sign이 문서화되고 firmware mapping에 반영된다.
```

## Test 3: Lifted Straight Motion

Procedure:

1. Robot lifted.
2. Command low forward motion.
3. Confirm both tracks move forward direction.
4. Stop command.
5. Repeat reverse.

| Command | Left behavior | Right behavior | Stop behavior | Result |
| --- | --- | --- | --- | --- |
| Forward low | TBD | TBD | TBD | TBD |
| Reverse low | TBD | TBD | TBD | TBD |

## Test 4: Lifted Rotation

Procedure:

1. Robot lifted.
2. Command low left rotation.
3. Confirm left/right track signs are opposite or as expected.
4. Command low right rotation.
5. Stop command.

| Command | Left track | Right track | Encoder signs | Result |
| --- | --- | --- | --- | --- |
| Rotate left | TBD | TBD | TBD | TBD |
| Rotate right | TBD | TBD | TBD | TBD |

## Test 5: Ground Low-Speed Straight Test

Only run this after lifted tests pass.

Procedure:

1. Place robot on clear floor.
2. Set very low duty/speed limit.
3. Command short forward motion.
4. Stop.
5. Measure drift and observe heat/noise.

| Item | Expected | Observed |
| --- | --- | --- |
| Robot moves forward | Yes, low speed | TBD |
| Robot stops | Yes | TBD |
| Left/right drift | Record | TBD |
| Track slip | Record | TBD |
| Battery voltage sag | Record | TBD |

## Test 6: Ground Low-Speed Rotation Test

Procedure:

1. Clear space around robot.
2. Command slow in-place rotation.
3. Stop after short duration.
4. Record yaw direction and rough angle.

| Command | Expected | Observed |
| --- | --- | --- |
| Rotate left | Counter-clockwise candidate | TBD |
| Rotate right | Clockwise candidate | TBD |
| Stop | No continued movement | TBD |

## Test 7: Timeout and E-Stop

Procedure:

1. Command low motion.
2. Trigger timeout by stopping command source.
3. Confirm motor stop.
4. Repeat with E-stop command if implemented.

| Safety case | Expected | Observed |
| --- | --- | --- |
| Command timeout | PWM zero, stop | TBD |
| E-stop | Latched stop | TBD |
| Disarm | Output disabled | TBD |

## Test 8: Heat and Power Observation

| Item | Before | After | Notes |
| --- | --- | --- | --- |
| Battery voltage | TBD | TBD | TBD |
| MDD10A temp | TBD | TBD | TBD |
| Left motor temp | TBD | TBD | TBD |
| Right motor temp | TBD | TBD | TBD |
| Main wire/connector temp | TBD | TBD | TBD |
| Fuse state | TBD | TBD | TBD |

## Stop Conditions

Stop immediately if:

- Robot moves at boot
- One side moves opposite to expected direction and cannot be controlled
- Stop command fails
- Timeout stop fails
- Fuse blows
- Driver, motor, wire, or connector heats quickly
- Track jams or derails
- Battery alarm sounds
- Robot becomes physically hard to restrain

## Result Summary

| Item | Pass/Fail | Notes |
| --- | --- | --- |
| Dual motor boot safe | TBD | TBD |
| Left/right independent direction | TBD | TBD |
| Lifted straight motion | TBD | TBD |
| Lifted rotation | TBD | TBD |
| Ground straight low-speed | TBD | TBD |
| Ground rotation low-speed | TBD | TBD |
| Timeout/E-stop | TBD | TBD |
| Heat/power acceptable | TBD | TBD |

## Next Step

좌우 drivetrain 저속 검증이 통과하면 다음 단계로 넘어간다.

```text
03_Firmware/
- HAL bare-metal drivetrain MVP design
- UART command parser
- encoder speed estimation
- command timeout

06_Test_Report/
- first drivetrain bring-up report
```
