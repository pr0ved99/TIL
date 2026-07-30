# Motor Output Waveform And Shutdown Latency Test

## 목적

이 문서는 logic analyzer로 STM32의 실제 MDD10A control signals를 계측하는 절차를 정의한다.

기존 DMM/LED 시험은 static routing과 기능적 all-off를 확인했다. 이 시험은 다음 미검증 항목을 닫는다.

- `PB6/TIM4_CH1`, `PB7/TIM4_CH2`의 actual PWM frequency와 duty
- `PC8/DIR1`, `PC9/DIR2`의 방향 mapping
- `PWM zero -> DIR edge -> PWM resume`의 두 settle interval
- boot/reset에서 unintended PWM pulse가 없는지
- DISARM, command timeout, software fault의 actual shutdown timing

이 문서는 계측 전 실행 계획이다. 측정값이 기록되기 전에는 `PASS`가 아니다.

## Safety scope

첫 단계는 motor-disconnected STM32 pin-only 또는 MDD10A powered/no-motor 조건에서만 수행한다.

금지:

- Logic analyzer를 3S LiPo, MDD10A POWER/MOTOR terminal 또는 XL4015 input에 직접 연결
- Analyzer GND를 common STM32 logic GND가 아닌 임의 power node에 연결
- 10%를 넘는 test duty
- Test macro가 켜진 build를 정상 firmware로 남기기
- Logic capture PASS를 실제 motor stop 또는 Physical E-stop PASS로 확대 해석

사용 예정 analyzer의 advertised input range `-0.5~5.25 V`는 STM32 3.3 V digital signal 관찰에는 적합하다. Motor-power rail 계측 정격이 아니므로 power terminal에는 사용하지 않는다.

## Baseline under test

| Item | Baseline |
| --- | --- |
| MCU | NUCLEO-F446RE / STM32F446RE |
| Timer | TIM4, APB1 timer clock 84 MHz |
| Prescaler | 0 |
| Auto-reload | 4199 |
| Expected PWM | `84 MHz / (4199 + 1) = 20 kHz` |
| Test duty cap | 100 permille = 10% |
| Direction zero settle | 1 ms minimum |
| Post-DIR settle | 1 ms minimum |
| UART | USART1 PA10 RX / PA9 TX, 115200 8-N-1 |

Firmware source:

- `03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c`
- `03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c`
- `03_Firmware/stm32_uart_mvp/Core/Src/main.c`

## Channel map

권장 8-channel connection:

| Analyzer channel | STM32 signal | Purpose |
| --- | --- | --- |
| `CH0` | `PB6 / TIM4_CH1 / PWM1` | MDD10A channel 1 PWM |
| `CH1` | `PC8 / DIR1` | MDD10A channel 1 direction |
| `CH2` | `PB7 / TIM4_CH2 / PWM2` | MDD10A channel 2 PWM |
| `CH3` | `PC9 / DIR2` | MDD10A channel 2 direction |
| `CH4` | `PA10 / USART1_RX` | CMD/DISARM frame boundary decode |
| `CH5` | `PC13 / B1` | Temporary button/fault-injection event reference |
| `CH6` | Future `ESTOP_SENSE` | E-stop timing; pin TBD, do not connect yet |
| `CH7` | Reserved test marker | Internal event marker if later required |
| Analyzer `GND` | STM32 GND | Sole digital capture reference |

CH4/CH5는 해당 test에서 필요할 때만 연결한다. STM32 pin header 위치는 NUCLEO pin map과 CubeMX label을 함께 대조한다.

## Capture settings

| Setting | Initial value |
| --- | --- |
| Software | PulseView / sigrok-compatible capture |
| Sample rate | 12 MHz or 24 MHz recommended; minimum 2 MHz |
| Digital threshold | Device default compatible with 3.3 V logic |
| Capture duration | Steady/direction: 100 ms 이상; timeout: command timeout + 500 ms 이상 |
| UART decoder | 115200 baud, 8 data, no parity, 1 stop, idle high |
| Trigger | PWM edge, DIR edge, PA10 UART activity or PC13 edge by test |

24 MHz에서는 20 kHz PWM period당 약 1200 sample을 얻는다. 긴 timeout capture에서 buffer가 부족하면 sample rate를 낮추되 2 MHz 아래로 내리지 않는다.

## Evidence file convention

각 capture는 다음 위치에 저장한다.

```text
assets/logs/motor_output/YYYY-MM-DD_<test>_<result>.sr
assets/logs/motor_output/YYYY-MM-DD_<test>_<result>.csv
assets/logs/motor_output/YYYY-MM-DD_<test>_<result>.png
```

각 evidence summary에는 다음을 기록한다.

```text
Date/time:
Operator:
Firmware commit:
Firmware build profile/hash:
Test macros and values:
Analyzer model:
Sample rate:
Channel map:
Trigger/reference event:
Measured values:
Result:
Limits:
```

## Test 1: Boot and reset output-safe capture

Setup:

- Motor disconnected.
- `MOTOR_OUTPUT_PIN_TEST_ENABLED=0U`
- `MOTOR_FAULT_INJECTION_TEST_ENABLED=0U`
- `UART_MVP_OUTPUT_TEST_ENABLED=0U`
- ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED=0U`

Procedure:

1. CH0~CH3와 GND를 연결한다.
2. Capture를 먼저 시작한다.
3. STM32 reset 또는 power-on을 수행한다.
4. Initialization 완료 후 1초 이상 유지한다.
5. 두 PWM과 두 DIR의 transition을 검사한다.

Acceptance:

- PB6/PB7에 active-high PWM pulse가 없어야 한다.
- PC8/PC9는 safe default LOW로 수렴해야 한다.
- Reset 동안 단발 active pulse가 없어야 한다.
- Test-disabled build에서 B1 입력은 output을 바꾸지 않아야 한다.

## Test 2: Steady 10% PWM frequency and duty

Setup:

- Motor disconnected.
- Controlled bench hook에서 한 channel만 100 permille로 활성화한다.
- 다른 channel은 0을 유지한다.

Measure:

| Metric | Acceptance |
| --- | --- |
| PWM frequency | 19.8~20.2 kHz |
| Duty at 100 permille request | 9.5~10.5% |
| Inactive channel | No active PWM pulse |
| DIR stability | Commanded static level; no unexpected toggle |

Channel 1과 channel 2를 각각 측정한다.

## Test 3: Direction-change settle timing

각 channel을 독립적으로 다음 sequence로 전환한다.

```text
forward 10%
-> request reverse 10%
-> reverse 10%
-> request forward 10%
```

Measure:

```text
t0: last active PWM edge before direction change
t1: DIR edge
t2: first active PWM edge after direction change
```

Acceptance:

| Interval | Acceptance |
| --- | --- |
| `t1 - t0` | 1.0 ms 이상 PWM inactive |
| `t2 - t1` | 1.0 ms 이상 PWM inactive |
| During both intervals | Both PWM compare outputs inactive as designed |
| Direction edge count | One intended edge; no chatter |

현재 `motor_output_set_raw()`는 어느 한 channel의 direction이 바뀌면 두 channel PWM을 함께 zero로 만든다. Capture에서 이 실제 동작을 확인하고, dual-channel control requirement와 맞는지는 별도 review한다.

## Test 4: DISARM shutdown timing

Setup:

- CH4 PA10을 함께 capture하고 UART decoder를 켠다.
- Controlled motor-disconnected 10% output hook만 사용한다.

Measure:

```text
t0: DISARM frame final stop bit or newline receive completion
t1: last active PB6/PB7 PWM edge
latency = t1 - t0
```

Acceptance:

- DISARM frame이 valid하면 두 PWM이 inactive가 된다.
- DIR도 safe LOW로 수렴한다.
- 이후 ARM 없이 output이 재개되지 않는다.
- First measurement는 actual latency baseline을 기록한다. Numeric release limit은 baseline과 loop architecture review 후 requirement로 고정한다.

100 ms TEL timestamp나 ESP32 console 출력 시각을 shutdown edge로 사용하지 않는다.

## Test 5: Command-timeout shutdown timing

1. Known `timeout_ms`의 valid CMD로 controlled 10% output을 시작한다.
2. 추가 CMD를 보내지 않는다.
3. PA10에서 마지막 valid CMD frame과 PB6/PB7을 동시에 capture한다.

Measure:

```text
t0: final stop bit/newline of last valid CMD
t1: last active PWM edge
observed total = t1 - t0
software overrun estimate = observed total - configured timeout_ms
```

Acceptance:

- Observed total이 configured timeout보다 짧아 stale command를 조기 종료하지 않는다.
- Configured timeout 뒤 bounded loop delay 내 두 PWM이 inactive가 된다.
- Timeout 뒤 old command가 자동 재적용되지 않는다.
- Exact bound는 parser/safety-state refactor와 first measurement 뒤 고정한다.

현재 firmware가 timeout 뒤 state를 별도 latched stop으로 전환하는지 source/runtime을 함께 확인한다. Architecture contract와 다르면 `PASS`하지 않는다.

## Test 6: Software fault shutdown timing

Setup:

- Motor disconnected.
- Temporary fault injection hook는 source에 명확히 표시하고 10% cap을 유지한다.
- CH5 PC13 또는 dedicated test marker를 reference event로 사용한다.

Measure:

```text
t0: debounced fault injection event 또는 dedicated marker
t1: last active PWM edge
```

Acceptance:

- Common safe-output path가 두 PWM을 inactive로 만든다.
- PC8/PC9도 safe LOW다.
- Fault latch 후 추가 B1/ARM/CMD로 output이 재개되지 않는다.
- Reset 전까지 latch가 유지된다.
- Operator button의 50 ms debounce를 firmware shutdown latency와 혼합하지 않고 별도 기록한다.

## Test 7: Final test-hook-off regression

모든 capture 뒤:

1. STM32/ESP32 temporary test macro를 모두 `0U`로 복구한다.
2. Firmware contract tests를 실행한다.
3. STM32 Debug와 ESP32 clean isolated build를 실행한다.
4. 두 board를 flash한 뒤 boot no-output을 다시 capture한다.
5. `git diff`에서 test hook이 남지 않았는지 확인한다.

Commands:

```powershell
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_firmware_contract.py
pwsh -File Projects/Tracked_Mobile_Robot/03_Firmware/tools/Build-Firmware.ps1 -Target All -RequireClean
```

## Result table

| Test | Result | Evidence | Notes |
| --- | --- | --- | --- |
| Boot/reset no pulse | `NOT TESTED` | TBD | Logic analyzer pending |
| CH1 20 kHz / 10% | `NOT TESTED` | TBD |  |
| CH2 20 kHz / 10% | `NOT TESTED` | TBD |  |
| CH1 direction settle | `NOT TESTED` | TBD |  |
| CH2 direction settle | `NOT TESTED` | TBD |  |
| DISARM latency | `NOT TESTED` | TBD | Numeric bound TBD after baseline |
| Timeout latency | `NOT TESTED` | TBD | Safety-state semantics must match architecture |
| Software fault latency/latch | `NOT TESTED` | TBD |  |
| Final hook-off boot regression | `NOT TESTED` | TBD |  |

## Current gate decision

```text
Execution plan: READY
Logic analyzer: ORDERED / NOT YET AVAILABLE
Actual waveform evidence: NOT TESTED
First powered motor test: NOT READY
```

Physical E-stop은 별도 hardware-energy-cut requirement다. 이 문서의 software PWM shutdown capture로 [`../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)를 대체하지 않는다.

