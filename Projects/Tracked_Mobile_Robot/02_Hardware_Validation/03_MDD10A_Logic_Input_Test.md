# MDD10A Logic Input Test

## 목적

이 문서는 STM32 motor-output 핀과 MDD10A logic input을 실제 motor 없이 단계적으로 검증한 기록이다.

목표는 다음 세 가지다.

- STM32가 `PWM1`, `DIR1`, `PWM2`, `DIR2`를 결정적으로 제어하는지 확인한다.
- Boot, idle, test-disabled 상태에서 PWM 출력이 0인지 확인한다.
- MDD10A에 전원을 공급하되 motor를 분리한 상태에서 양 채널의 A/B 출력 선택이 입력과 일치하는지 확인한다.

시험일: `2026-07-26`

## Test Scope

이번 시험에 포함한 것:

- STM32 핀 단독 DMM 확인
- MDD10A power disconnected 상태의 signal-only 확인
- MDD10A POWER connected, motor disconnected 상태의 powered/no-motor LED 확인
- 임시 10% duty test sequence
- PWM/DIR 배선 오류 재현, 원인 분리와 교정 후 재시험
- 임시 시험 매크로를 끈 뒤 safe-state 재확인

이번 시험에 포함하지 않은 것:

- 실제 motor 연결과 회전
- Oscilloscope 또는 logic analyzer를 이용한 PWM 주파수와 duty 계측
- Direction-change deadtime의 실제 시간 계측
- UART active command 상태에서 timeout/DISARM가 실제 PWM 핀을 0으로 만드는 시험
- 차량 기준 forward/reverse와 left/right motor mapping 확정

금지 조건:

- Fuse와 DC-rated main switch를 우회해 battery를 MDD10A에 직접 연결
- Motor output terminal에 실제 motor를 연결한 채 이 절차를 수행
- 10%를 초과하는 임시 raw test duty 사용
- 원인을 모르는 출력 LED나 전압이 관측된 상태에서 다음 단계 진행

## Signal Contract

2026-07-26 교정 후 확정한 bench mapping:

| STM32 | Function | MDD10A |
| --- | --- | --- |
| `PB6 / TIM4_CH1` | Firmware left PWM candidate | `PWM1` |
| `PC8` | Firmware left DIR candidate | `DIR1` |
| `PB7 / TIM4_CH2` | Firmware right PWM candidate | `PWM2` |
| `PC9` | Firmware right DIR candidate | `DIR2` |
| `GND` | Common reference | `GND` |

```text
PB6 / TIM4_CH1 -> PWM1
PC8            -> DIR1
PB7 / TIM4_CH2 -> PWM2
PC9            -> DIR2
STM32 GND      -> MDD10A GND
```

`left`와 `right`는 현재 firmware channel 이름이다. 실제 차량 좌우 motor mapping은 motor 장착 후 별도로 확정한다.

MDD10A에는 BTS7960식 별도 logic VCC pin이 없다. Signal-only 단계에서는 MDD10A POWER를 분리하고, powered/no-motor 단계에서만 검증된 fuse/switch 경로로 POWER를 공급했다.

## Firmware Test Baseline

| Item | Configured value | Physical verification |
| --- | --- | --- |
| Timer/channel | TIM4 CH1 / CH2 | Routing response confirmed |
| Timer period | `4199` | Source/CubeMX setting confirmed |
| Intended PWM frequency | 20 kHz | Not instrument-measured |
| Temporary duty limit | `100 / 1000 = 10%` | Source limit and LED/DMM response confirmed; exact waveform not measured |
| Current pre-DIR zero delay | `1 ms` | Source path confirmed; actual interval not measured; post-DIR settle 미구현 |
| Final test macro | `MOTOR_OUTPUT_PIN_TEST_ENABLED 0U` | Rebuilt/flashed and all MDD output LEDs off |

관련 구현:

- [`../03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c`](../03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c)
- [`../03_Firmware/stm32_uart_mvp/Core/Src/main.c`](../03_Firmware/stm32_uart_mvp/Core/Src/main.c)
- [`../03_Firmware/stm32_uart_mvp/stm32_uart_mvp.ioc`](../03_Firmware/stm32_uart_mvp/stm32_uart_mvp.ioc)

## Required Preconditions

| Precondition | Required | Result |
| --- | --- | --- |
| STM32 firmware can force both PWM compares to zero | Yes | PASS |
| STM32 firmware can set both DIR GPIOs | Yes | PASS |
| MDD10A signal header labels identified | Yes | PASS after wiring correction |
| STM32 GND and MDD10A GND common | Yes | PASS |
| Signal-only phase keeps MDD10A POWER disconnected | Yes | PASS |
| Powered phase uses fused/switched battery path | Yes | PASS |
| Motor remains disconnected | Yes | PASS |
| Temporary raw duty is capped at 10% | Yes | PASS |

## Test 1: Boot, Idle and Test-Disabled State

Procedure:

1. Keep motor and MDD10A main power disconnected.
2. Boot/reset STM32 and measure `PB6`, `PB7`, `PC8`, `PC9` with a DMM.
3. After all staged tests, set `MOTOR_OUTPUT_PIN_TEST_ENABLED` to `0U`, rebuild/flash, and repeat the safe-state observation with the powered driver and no motor.

| Signal/state | Expected | Observed | Result |
| --- | --- | --- | --- |
| `PB6 / PWM1` boot/idle | 0 V average | 0 V | PASS |
| `PB7 / PWM2` boot/idle | 0 V average | 0 V | PASS |
| `PC8 / DIR1` boot/idle | 0 V | 0 V | PASS |
| `PC9 / DIR2` boot/idle | 0 V | 0 V | PASS |
| Test macro `0U`, MDD powered/no motor | All output LEDs off | All output LEDs off | PASS |

DIR이 단독으로 바뀌더라도 PWM이 0이면 motor output을 만들지 않아야 한다. 이번 시험에서는 boot/idle과 최종 test-disabled 상태에서 네 신호가 safe state로 돌아오는 것을 확인했다.

## Test 2: Low-Duty PWM Routing

임시 button sequence는 각 PWM 채널을 10% 설정으로 한 번씩 활성화하고 다시 0으로 복귀하도록 구성했다.

| Channel | Configured duty | Observed | Result |
| --- | --- | --- | --- |
| `PB6 / PWM1` | 10% | DMM 평균값과 MDD channel 1 LED 반응이 단계 변화와 일치 | PASS for routing |
| `PB7 / PWM2` | 10% | DMM 평균값과 MDD channel 2 LED 반응이 단계 변화와 일치 | PASS for routing |
| Exact frequency/duty | 20 kHz / 10% intended | Oscilloscope/logic analyzer capture 없음 | NOT TESTED |

이번 결과는 signal routing과 low-duty 제한 동작의 최소 증거다. 정확한 20 kHz와 10% 파형을 계측한 결과로 확대 해석하지 않는다.

## Test 3: PWM/DIR Wiring Diagnosis and Powered-No-Motor Result

### Initial wiring fault

첫 powered/no-motor 시험에서는 MDD10A header의 양 채널 모두에서 PWM과 DIR를 서로 바꿔 연결했다.

| Step | Initial observation |
| --- | --- |
| 1 | LED 동작 없음 |
| 2 | M1A 밝게, M1B 약하게 점등 |
| 3 | LED 동작 없음 |
| 4 | LED 동작 없음 |
| 5 | M2A 밝게, M2B 약하게 점등 |

증상은 실제 PWM 입력을 DIR GPIO가 0/1로 고정하고, 실제 DIR 입력으로 10% PWM이 들어간 경우와 일치했다. 시험을 중단하고 양 채널의 PWM/DIR를 MDD10A 실크 인쇄에 맞게 교정했다.

![PWM/DIR swapped before correction](../assets/photos/mdd10a/2026-07-26_01_mdd10a_pwm_dir_swapped_before_fix.jpg)

### Corrected result

교정 후 동일한 6-step sequence를 다시 실행했다.

| Step | STM32 test state | Powered/no-motor observation | Result |
| --- | --- | --- | --- |
| 1 | CH1 10%, DIR low | M1A LED active | PASS |
| 2 | CH1 10%, DIR high | M1B LED active | PASS |
| 3 | Both channels stopped | All related LEDs off | PASS |
| 4 | CH2 10%, DIR low | M2A LED active | PASS |
| 5 | CH2 10%, DIR high | M2B LED active | PASS |
| 6 | Both channels stopped | All output LEDs off | PASS |

![Corrected PWM/DIR wiring](../assets/photos/mdd10a/2026-07-26_02_mdd10a_corrected_pwm_dir_wiring_pass.jpg)

이 사진은 교정된 logic wiring과 시험 종료 후 motor output 및 battery terminal이 분리된 상태를 보여준다.

차량 기준 forward/reverse는 motor를 연결하지 않았으므로 아직 확정하지 않는다. 현재 확인된 것은 DIR level에 따라 각 MDD channel의 A/B 선택이 결정적으로 바뀐다는 점이다.

## Test 4: MDD10A Power Input and Powered-No-Motor Safety

| Measurement/check | Observed | Result |
| --- | --- | --- |
| Battery pack | 12.36 V | Recorded |
| MDD10A POWER+ to POWER- | 12.35 V | PASS |
| Motor connection | Disconnected | PASS |
| Heat, smell, smoke, abnormal noise | None | PASS |
| Final output state after disabling test macro | All LEDs off | PASS |

Switch OFF 직후 `-0.24 V`가 관측됐고 `-0.14 V`를 거쳐 0 V 방향으로 천천히 감쇠했다. ON 극성과 전압은 정상이었다. 저장 커패시터 또는 부유 기준점의 영향으로 추정하지만 원인을 별도 계측으로 확정하지 않았으며, 이 관측만으로 역전원 여부를 판정하지 않는다.

전원 경로 세부 기록은 [`01_Power_Bringup_Checklist.md`](01_Power_Bringup_Checklist.md)를 참조한다.

## Test 5: Direction-Change Safety Sequence

`motor_output_set_raw()`는 active channel의 DIR가 바뀌면 다음 순서로 동작하도록 구현됐다.

```text
PWM1/PWM2 compare = 0
-> HAL_Delay(1 ms)
-> DIR GPIO update
-> requested PWM compare apply
```

Step 1에서 Step 2, Step 4에서 Step 5로 전환했을 때 최종 A/B LED 선택은 정상적으로 바뀌었다. 그러나 PWM zero 구간과 1 ms 간격은 계측하지 않았다.

| Requirement | Observed | Result |
| --- | --- | --- |
| Functional direction selection | Correct A/B LED selected after transition | PASS |
| PWM zero before DIR transition | Source path exists | NOT TESTED physically |
| Approximately 1 ms pre-DIR zero interval | Source constant exists | NOT TESTED physically |
| Post-DIR settle before PWM resume | Current source path does not provide it | NOT IMPLEMENTED |

Direction-change timing requirement의 최종 판정은 `PARTIAL`이다.

## Test 6: Timeout and DISARM Output Zero

UART protocol의 timeout, DISARM 및 error path에서 `motor_output_stop_all()`을 호출하는 코드는 존재한다. 하지만 production command 값을 PWM/DIR 출력으로 활성화한 상태에서 실제 핀과 MDD10A LED가 0으로 전환되는 시험은 아직 수행하지 않았다.

| Event | Expected | Observed | Result |
| --- | --- | --- | --- |
| Command timeout during active PWM | `PWM1=0`, `PWM2=0` | Code path only | NOT TESTED |
| DISARM during active PWM | `PWM1=0`, `PWM2=0` | Code path only | NOT TESTED |
| Firmware error path | `PWM1=0`, `PWM2=0` | Code path only | NOT TESTED |
| E-stop | `PWM1=0`, `PWM2=0` | Not implemented | NOT TESTED |

기존 UART command 변수의 timeout-zero PASS를 실제 motor-output zero PASS로 대체하지 않는다.

## Stop Conditions

다음 중 하나라도 발생하면 즉시 시험을 중단한다.

- Boot/reset에서 PWM output이 활성화됨
- PWM이 stop command 후 0으로 돌아오지 않음
- 배선, MDD10A 또는 connector가 뜨거워짐
- Smoke, smell, spark 또는 abnormal noise 발생
- MDD10A header label과 신호 역할이 불명확함
- Motor가 의도하지 않게 연결되거나 움직임

## Result Summary

| Item | Result | Notes |
| --- | --- | --- |
| STM32 pin-only boot/idle zero | PASS | PB6, PB7, PC8, PC9 모두 0 V |
| PWM1/PWM2 routing | PASS | DMM/LED minimum verification |
| Exact 20 kHz / 10% waveform | NOT TESTED | Instrument capture 없음 |
| DIR1/DIR2 behavior | PASS | 교정 후 M1A/M1B, M2A/M2B 선택 정상 |
| PWM/DIR wiring fault | RESOLVED | 양 채널 swap 교정 후 전체 sequence 재시험 |
| Powered/no-motor driver check | PASS | 12.35 V, motor disconnected, 이상 증상 없음 |
| Direction-change timing | PARTIAL | 현재 source는 PWM 0 -> 1 ms wait -> DIR -> 즉시 PWM; 의도한 post-DIR settle 수정과 계측 필요 |
| Active timeout/DISARM PWM zero | NOT TESTED | Production output activation test 필요 |
| Final test-disabled safe state | PASS | Macro `0U`, all output LEDs off |

Overall result: `PARTIAL`

이번 단계로 정적 신호 routing, MDD10A channel selection과 powered/no-motor 안전 상태는 확인했다. 파형 timing과 active safety shutdown이 남아 있으므로 전체 motor-output verification을 `PASS`로 종료하지 않는다.

## Next Step

1. 실제 motor를 활성화하기 전에 direction-change path를 `PWM 0 -> DIR -> settle -> PWM` 순서로 수정한다.
2. Oscilloscope 또는 logic analyzer를 사용할 수 있을 때 실제 20 kHz/10% PWM과 direction timing을 계측한다.
3. UART command state를 제한된 motor-output interface에 연결한다.
4. Active 10% output에서 timeout과 DISARM가 실제 PWM 핀과 MDD10A 출력 LED를 0으로 만드는지 확인한다.
5. Encoder loaded-voltage gate는 [`04_Encoder_Signal_Safety_Test.md`](04_Encoder_Signal_Safety_Test.md)에서 `CONDITIONAL PASS`했다. 다음 encoder 단계는 TIM3 PB4/PB5 motor-power-off hand-rotation count다.
6. 위 motor safety gate와 encoder count/sign gate를 통과한 뒤에만 [`05_First_Motor_No_Load_Test.md`](05_First_Motor_No_Load_Test.md)로 진행한다.
