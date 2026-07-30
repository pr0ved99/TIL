# First Motor No-Load Test

## 목적

이 문서는 motor 1개와 MDD10A 1개 channel을 사용해 첫 low-duty no-load motor test를 수행하는 절차를 정의한다.

목표는 chassis 전체를 움직이기 전에 한쪽 motor path에서 power, driver, PWM, direction, encoder behavior를 안전하게 확인하는 것이다.

## Test Scope

허용:

- Motor 1개만 연결
- Track 또는 wheel unloaded/lifted 상태
- Low duty PWM만 사용
- 짧은 duration test
- Fuse 낮은 값 사용
- Encoder count 관찰

금지:

- Robot을 바닥에 두고 장시간 구동
- High duty test
- Fuse rating을 원인 분석 없이 올리기
- Encoder sign 모르는 상태로 closed-loop 제어
- PWM이 0이 아닌 상태에서 DIR 전환

## Required Preconditions

| Precondition | Source document | Result |
| --- | --- | --- |
| Power path checked | `01_Power_Bringup_Checklist.md` | PASS through MDD10A powered/no-motor input |
| Buck output calibrated if logic uses buck | `02_Buck_Converter_Calibration_Log.md` | CONDITIONAL PASS; board power/back-power TBD |
| MDD10A logic input safe | `03_MDD10A_Logic_Input_Test.md` | PARTIAL; timeout/DISARM와 software fault output-zero/latch functional PASS, actual PWM waveform/timing과 physical E-stop required |
| Actual PWM/DIR timing measured | `09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md` | NOT TESTED; logic analyzer pending |
| Physical E-stop staged verification | `../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md` | PLANNED/BLOCKED; `T-ESTOP-001~006` must pass first |
| Encoder signal/input conditioning checked | `04_Encoder_Signal_Safety_Test.md` | CONDITIONAL PASS; A/B별 1 kΩ series와 MCU-side 15 kΩ-to-GND 유지 |
| Motor-off encoder count/sign | `04_Encoder_Signal_Safety_Test.md`, `../assets/logs/encoder/README.md` | TIM3/TIM5 dual independent hand rotation와 encoder-side A=right/TIM5, B=left/TIM3 forward-positive sign PASS |
| Motor fixed or lifted safely | Physical setup | TBD |
| Bench fuse selected from validated current envelope | Test stage | TBD; 10 A candidate, no rating increase without root-cause/design review |

Current gate decision: `NOT READY`

Encoder loaded-voltage gate, TIM3/TIM5 dual motor-power-off independent count/sign과 encoder-side vehicle-forward sign은 통과했다. 그러나 이 결과는 MDD10A powered channel-to-side mapping이나 powered-motor noise를 입증하지 않는다. Powered/no-motor timeout/DISARM와 software fault output-zero/latch functional gate도 통과했지만, 실제 motor 연결 전 actual PWM pin waveform/shutdown latency, exact PWM/direction timing과 physical E-stop gate를 확인해야 한다.

## Wiring Under Test

```text
3S LiPo +
    -> fuse
    -> verified Physical E-stop motor-power disconnect
       (selected T-ESTOP variant, including its main-switch topology)
    -> MDD10A POWER+

3S LiPo -
    -> MDD10A POWER-
    -> common logic GND

STM32 PWM -> MDD10A PWM1 or PWM2
STM32 DIR -> MDD10A DIR1 or DIR2
Motor leads -> MDD10A selected channel output
Encoder A/B -> 1 kΩ series -> STM32 timer input node
Each STM32 input node -> 15 kΩ -> common GND
```

## Test Configuration

| Item | Value |
| --- | --- |
| Motor under test | TBD |
| MDD10A channel | TBD |
| Fuse rating | TBD |
| Battery voltage before test | TBD |
| PWM frequency | TBD |
| Duty limit | TBD |
| Command timeout | TBD |
| Encoder connected? | TBD |
| Test duration limit | TBD |

Recommended initial limits:

```text
Duty: 5-10% first
Duration: 1-2 seconds per pulse
Motor load: lifted/no-load
```

## Test 1: Motor Power Connected, Output Disabled

Procedure:

1. Keep STM32 in disarmed state.
2. Connect motor to selected MDD10A channel.
3. Switch ON.
4. Confirm motor does not move.
5. Confirm PWM zero.
6. Check heat/noise/smell.

| Check | Expected | Observed |
| --- | --- | --- |
| Motor movement at boot | None | TBD |
| PWM state | Zero | TBD |
| Heat/smell/noise | None | TBD |

## Test 2: Low-Duty Forward Pulse

Procedure:

1. Arm only if safety conditions pass.
2. Apply low-duty positive command for short duration.
3. Stop command.
4. Confirm motor stops.
5. Record encoder sign if connected.
6. Compare count change with physical motion and record false counts/noise during and immediately after the pulse.

| Item | Expected | Observed |
| --- | --- | --- |
| PWMx | Low duty | TBD |
| DIRx | Forward mapping | TBD |
| Motor direction | Forward candidate | TBD |
| Encoder count sign | Expected positive after mapping | TBD |
| Encoder false count/noise | No unexplained jump while stationary | TBD |
| Stop behavior | PWM zero | TBD |

## Test 3: Low-Duty Reverse Pulse

Procedure:

1. Apply low-duty negative command for short duration.
2. Stop command.
3. Confirm motor stops.
4. Record encoder sign if connected.
5. Compare count change with physical motion and record false counts/noise during and immediately after the pulse.

| Item | Expected | Observed |
| --- | --- | --- |
| PWMx | Low duty | TBD |
| DIRx | Reverse mapping | TBD |
| Motor direction | Reverse candidate | TBD |
| Encoder count sign | Opposite of forward | TBD |
| Encoder false count/noise | No unexplained jump while stationary | TBD |
| Stop behavior | PWM zero | TBD |

## Test 4: Timeout Stop

Procedure:

1. Apply low-duty command.
2. Stop sending command or trigger timeout condition.
3. Confirm output goes safe.

| Item | Expected | Observed |
| --- | --- | --- |
| Command age exceeds timeout | Yes | TBD |
| PWM after timeout | 0 | TBD |
| Motor output permission after timeout | Disabled or safe idle | TBD |
| Motor movement | Stops | TBD |

## Test 5: Heat and Current Observation

If current measurement is available, record it. If not, record qualitative observations.

| Item | Before | After | Notes |
| --- | --- | --- | --- |
| Battery voltage | TBD | TBD | TBD |
| MDD10A temperature | TBD | TBD | TBD |
| Motor temperature | TBD | TBD | TBD |
| Wire/connector temperature | TBD | TBD | TBD |
| Fuse condition | TBD | TBD | TBD |

## Stop Conditions

Stop immediately if:

- Motor moves at boot or disarmed state
- Motor does not stop on command stop
- Command timeout does not stop output
- MDD10A heats quickly
- Motor or wire heats
- Fuse blows
- Encoder count behaves impossibly
- DIR changes while PWM is nonzero
- Battery voltage sags abnormally

## Result Summary

| Item | Pass/Fail | Notes |
| --- | --- | --- |
| Boot output safe | TBD | TBD |
| Forward low-duty pulse | TBD | TBD |
| Reverse low-duty pulse | TBD | TBD |
| Stop command | TBD | TBD |
| Timeout stop | TBD | TBD |
| Encoder sign | TBD | TBD |
| Heat/current acceptable | TBD | TBD |
| Ready for opposite side test | TBD | TBD |

## Next Step

Motor 1개 no-load test가 통과하면 반대쪽 motor도 같은 방식으로 검증한 뒤 좌우 drivetrain test로 넘어간다.

```text
06_Left_Right_Drivetrain_Test.md
```
