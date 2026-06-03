# Fault Model and Safety Cases

## 목적

이 문서는 궤도형 모바일 로봇에서 예상되는 fault case와 각 case의 required safe response를 정의한다.

프로젝트는 3S LiPo battery, high-current DC motor, BTS7960 H-bridge driver, STM32 firmware, ESP32 support
logic, 그리고 향후 CAN/ROS2 integration을 사용한다. 따라서 fault handling은 electrical failure와
software failure를 모두 다뤄야 한다.

이 문서는 다음 질문에 답한다.

- 무엇이 고장날 수 있는가
- Firmware 또는 operator가 어떻게 감지할 수 있는가
- Robot이 즉시 무엇을 해야 하는가
- Validation 중 어떤 evidence를 남겨야 하는가

## Safety Principle

Robot은 fault가 발생하면 no motion 방향으로 실패해야 한다.

핵심 규칙:

```text
Controller가 확신할 수 없으면 motor output은 zero가 되고 driver enable은 disabled가 된다.
```

이 규칙은 UART, CAN, ESP32, ROS2, encoder, battery, firmware fault에 모두 적용된다.

## 1. Fault Severity Levels

| Level | Meaning | Motor response |
| --- | --- | --- |
| Info | 유용한 diagnostic condition | Automatic stop 없음 |
| Warning | 비정상이지만 즉시 위험하지 않음 | Limit 또는 prepare stop |
| Stop | Motion을 멈춰야 함, recovery는 비교적 단순 | PWM zero, driver disabled |
| Latched fault | Explicit reset 전까지 motion 금지 | PWM zero, driver disabled |
| Hardware emergency | Operator가 power를 제거해야 함 | Switch 사용, 안전하면 battery disconnect |

## 2. Fault Categories

| Category | Examples |
| --- | --- |
| Power faults | Low voltage, buck overvoltage, reverse polarity, fuse trip |
| Motor driver faults | BTS7960 heat, enable stuck, wrong PWM combination |
| Command faults | UART timeout, CAN heartbeat timeout, invalid command |
| Sensor faults | Encoder stuck, encoder sign mismatch, IMU missing |
| Firmware faults | Assertion failure, loop timing overrun, watchdog reset |
| Wiring faults | Loose ground, swapped CANH/CANL, encoder 5 V into unsafe pin |
| Mechanical faults | Track jam, high friction, chassis collision |
| Operator faults | Wrong connector polarity, wrong fuse, unsafe battery handling |

## 3. Fault Response Table

| Fault | Detection method | Immediate response | Recovery |
| --- | --- | --- | --- |
| Boot not complete | Startup state | PWM zero, enable disabled 유지 | Init 완료 후 disarmed |
| Command timeout | Command age가 timeout 초과 | Motor stop | Disarm/arm flow 이후 새 valid command |
| CAN heartbeat timeout | Heartbeat missing | Motor stop | Bus reconnect, disarm/arm |
| E-stop request | Command 또는 physical input | Stop latch | Explicit operator reset |
| Low-voltage warning | ADC 또는 LiPo alarm | Warning, test scope 축소 | Recharge 또는 곧 stop |
| Low-voltage stop | ADC가 stop threshold 아래 | Motor stop | Recharge, operator reset |
| Buck output wrong | Multimeter check | Electronics 연결 금지 | Converter 조정/교체 |
| Encoder stuck | Commanded motion but count change 없음 | Stop 또는 motion limit | Wiring/mechanics 점검 |
| Encoder direction mismatch | Sign check 실패 | Closed-loop mode 진입 금지 | Sign mapping 수정 |
| Driver enable unexpected | 가능하면 readback/test mismatch | Test stop | Wiring/pull-down 점검 |
| RPWM and LPWM both active | Firmware assertion 또는 output audit | 둘 다 zero 강제 | Motor output code 수정 |
| Motor overheat | Operator touch/IR thermometer | Test stop | Cool down, load 감소 |
| BTS7960 overheat | Operator check | Test stop | Cool down, mounting 개선 |
| Fuse blows | Motor/robot power loss | Test stop | 원인 찾기 전 fuse 교체 금지 |
| Watchdog reset | Reset cause register/log | Reboot 후 disarmed 유지 | Loop blocking 점검 |
| CAN bus-off | CAN error state | Motor stop, fault report | Bus 수정, CAN reset |
| UART parse storm | Invalid frames 반복 | Ignore, timeout rule 유지 | Sender 수정 |
| IMU missing | No data 또는 bus error | IMU-dependent mode disable | Wiring/I2C 확인 |

## 4. Power Safety Cases

### Case P1: Buck Converter Output Too High

Risk:

- STM32, ESP32, sensors, encoder logic가 손상될 수 있다.

Detection:

- Board 연결 전 buck output을 측정한다.

Required response:

- Load를 연결하지 않는다.
- Output을 target voltage로 조정한다.
- Light load에서 다시 측정한다.

Evidence:

- Multimeter photo 또는 recorded voltage table.

### Case P2: LiPo Low Voltage

Risk:

- LiPo cell damage, voltage sag, unreliable electronics.

Detection:

- 3S LiPo alarm.
- 구현 이후 STM32 ADC voltage monitor.

Required response:

- Warning threshold: test 축소 또는 stop 준비.
- Stop threshold: motor output disable.

Evidence:

- ADC raw value, converted pack voltage, threshold used.

### Case P3: Fuse Trip

Risk:

- Short circuit, wiring fault, stall current, wrong fuse.

Detection:

- Switched battery power loss.
- Fuse continuity check 실패.

Required response:

- Battery disconnect.
- Fuse 교체 전 wiring inspect.

Evidence:

- Fault log와 physical inspection note.

## 5. Motor Driver Safety Cases

### Case M1: Both Direction PWM Inputs Active

Risk:

- Module design에 따라 undefined driver behavior, heating, shoot-through-like stress.

Detection:

- Firmware output audit.
- Validation 중 logic analyzer 또는 oscilloscope.

Required response:

- 두 PWM channel을 zero로 설정.
- 감지되면 driver enable disable.

Rule:

```text
Active channel을 적용하기 전에 inactive PWM channel을 zero로 설정한다.
```

### Case M2: Track Jam or Stall

Risk:

- High motor current, driver heat, fuse trip, battery sag.

Detection:

- Motor command가 있는데 encoder count 변화 없음.
- 가능하면 current measurement.
- Voltage sag 또는 heat.

Required response:

- Motor output stop.
- Operator inspection 요구.

### Case M3: Driver Enable Unsafe During Reset

Risk:

- Firmware 준비 전 motor가 움직일 수 있다.

Detection:

- Motor power disconnected 상태에서 bench boot test.

Required response:

- External pull-down 추가 또는 wiring 수정.
- Safe reset behavior 확인 전 motor power 연결 금지.

## 6. Communication Safety Cases

### Case C1: UART Command Timeout

Detection:

- `last_command_age_ms > timeout_ms`.

Required response:

- PWM zero.
- State-machine decision에 따라 driver disabled 또는 armed idle.
- Telemetry로 timeout report.

### Case C2: CAN Heartbeat Timeout

Detection:

- Configured window 안에 `HEARTBEAT` frame 없음.

Required response:

- Safe stop.
- `FAULT_HEARTBEAT_TIMEOUT` report.

### Case C3: Invalid Command Frame

Detection:

- Required fields missing.
- Invalid DLC.
- Out-of-range values.

Required response:

- Frame reject.
- Active command update 금지.
- Timeout logic 유지.

## 7. Sensor Safety Cases

### Case S1: Encoder Direction Mismatch

Detection:

- Forward command에서 한쪽 count가 negative.

Required response:

- Closed-loop speed control 진입 금지.
- Wiring 또는 firmware mapping에서 sign 수정.

### Case S2: Encoder Stuck

Detection:

- Nonzero PWM command에도 configured window 동안 count 변화 없음.

Required response:

- Early open-loop test에서는 warn 후 수동 stop.
- Closed-loop operation에서는 stop 또는 motion limit.

### Case S3: IMU Missing

Detection:

- I2C read failure 또는 valid BNO08x report 없음.

Required response:

- IMU-dependent mode 사용 금지.
- 명시적으로 허용한 경우 encoder-only mode는 지속 가능.

## 8. Firmware Safety Cases

### Case F1: Control Loop Overrun

Detection:

- `loop_dt_us`가 maximum allowed period를 초과.

Required response:

- Diagnostic counter 기록.
- 반복되면 fault 또는 safe stop.

### Case F2: Watchdog Reset

Detection:

- Reset cause register 또는 boot counter.

Required response:

- Disarmed state로 boot.
- Motion 자동 재개 금지.

### Case F3: Internal Assertion Failure

Detection:

- Firmware가 impossible state, invalid enum, unsafe output request를 감지.

Required response:

- PWM zero 강제.
- Driver enable disable.
- Fault latch.

## 9. Operator Safety Cases

Operator rules:

- 첫 motor test에서는 robot을 들어 올린다.
- Early test에서는 가능한 낮은 fuse를 사용한다.
- Battery를 끊을 수 있는 경로를 확보한다.
- LiPo를 unattended 상태로 충전하지 않는다.
- 손상되거나 부푼 LiPo pack을 사용하지 않는다.
- Mechanical 또는 wiring 문제를 숨기려고 fuse rating을 올리지 않는다.
- 측정 없이 STM32 pin을 unknown encoder voltage에 연결하지 않는다.

## 10. Fault Telemetry

Minimum fields:

```text
safety_state
fault_code
last_fault_time_ms
command_age_ms
battery_mv
left_pwm
right_pwm
left_encoder_count
right_encoder_count
loop_dt_max_us
reset_cause
```

Fault log에는 다음이 포함되어야 한다.

- 어떤 command가 active였는지
- Robot이 어떤 state였는지
- 어떤 safety response가 적용되었는지
- Physical power를 제거했는지

## 11. Validation Matrix

| Validation | Method | Pass condition |
| --- | --- | --- |
| Boot safe output | Logic only, motor disconnected | PWM zero, enable disabled |
| Command timeout | Command 전송 중단 | Motor output stop |
| E-stop | E-stop frame 또는 command 전송 | Fault latched, output disabled |
| Low voltage simulated | Low ADC equivalent injection | Output disabled |
| Encoder sign | Lifted motor test | Forward command produces expected signs |
| CAN timeout | Heartbeat 중단 | Output disabled |
| Watchdog recovery | Safe test 중 reset 강제 | Reboot remains disarmed |
| Fuse stage | Low fuse first | Fuse choice documented |

## Final Decision

Fault model은 architecture의 일부이지 나중에 붙이는 부가기능이 아니다.

모든 command path는 같은 fail-safe behavior를 공유해야 한다.

```text
invalid, stale, missing, or unsafe input -> PWM zero and driver disabled
```

Latched safety fault에서 회복하려면 explicit operator action이 필요하다.
