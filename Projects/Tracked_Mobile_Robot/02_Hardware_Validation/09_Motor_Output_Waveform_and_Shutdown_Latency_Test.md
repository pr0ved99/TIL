# Motor Output Waveform And Shutdown Latency Test

## 목적

이 문서는 logic analyzer로 STM32의 실제 MDD10A control signals를 계측하는 절차를 정의한다.

기존 DMM/LED 시험은 static routing과 기능적 all-off를 확인했다. 이 시험은 다음 미검증 항목을 닫는다.

- `PB6/TIM4_CH1`, `PB7/TIM4_CH2`의 actual PWM frequency와 duty
- `PC8/DIR1`, `PC9/DIR2`의 방향 mapping
- `PWM zero -> DIR edge -> PWM resume`의 두 settle interval
- boot/reset에서 unintended PWM pulse가 없는지
- DISARM, command timeout, software fault의 actual shutdown timing

이 문서는 계측 절차와 2026-08-03~08-18 실행 결과를 함께 기록한다. 파형·방향 전환,
active DISARM, command-timeout, software-fault latch와 external-reset-marker boot subtest를
통과했다. Reset 첫 시험에서 네 motor-control signal이 부유해 FAIL했고 signal별 외부
`10 kΩ` pull-down 적용 재시험에서 5 s/20 M samples all-LOW를 확인했다. MDD10A power
stage, actual motor와 Physical E-stop은 아직 완료되지 않았다.

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
| Auto-reload | 4420 |
| Expected PWM | `84 MHz / (4420 + 1) = about 19.0002 kHz` |
| Test duty cap | 100 permille = 10% |
| Direction zero settle | 1 ms minimum |
| Post-DIR settle | 1 ms minimum |
| UART | USART1 PA10 RX / PA9 TX, 115200 8-N-1 |

Firmware source:

- `03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c`
- `03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c`
- `03_Firmware/stm32_uart_mvp/Core/Src/main.c`

## Channel map

2026-08-03 실제 캡처 connection:

| Analyzer channel | STM32 signal | Purpose |
| --- | --- | --- |
| `D0` | `PC8 / DIR1` | MDD10A channel 1 direction |
| `D1` | `PB6 / TIM4_CH1 / PWM1` | MDD10A channel 1 PWM |
| `D2` | `PC9 / DIR2` | MDD10A channel 2 direction |
| `D3` | `PB7 / TIM4_CH2 / PWM2` | MDD10A channel 2 PWM |
| `D4` | Not connected | Reserved |
| `D5` | Not connected | Reserved |
| `D6` | Not connected | Future `ESTOP_SENSE`; pin TBD |
| `D7` | Not connected | Reserved test marker |
| Analyzer `GND` | STM32 GND | Sole digital capture reference |

향후 shutdown latency 시험에서는 빈 channel에 `PA10 / USART1_RX` 또는 dedicated marker를 추가한다. 저장된 PulseView session의 channel label은 `D0`~`D7`이므로 위 표와 evidence README를 canonical mapping으로 사용한다.

2026-08-04 active DISARM capture에서는 다음 channel을 추가했다.

| Analyzer channel | STM32 signal | Purpose |
| --- | --- | --- |
| `D4` | `PA10 / USART1 RX` | ESP32 -> STM32 DISARM frame reference |
| `D5` | `PA9 / USART1 TX` | STM32 -> ESP32 ACK reference |

D0~D3와 GND는 2026-08-03 map을 그대로 사용했다. 실제 물리 배선과 motor-energy
분리 조건은 작업자 확인 전까지 `operator confirmation pending`이다.

## Capture settings

| Setting | Initial value |
| --- | --- |
| Software | PulseView / sigrok-compatible capture |
| Sample rate | 12 MHz or 24 MHz recommended; minimum 2 MHz; 2026-08-03 actual 4 MHz |
| Digital threshold | Device default compatible with 3.3 V logic |
| Capture duration | Steady/direction: 100 ms 이상; timeout: command timeout + 500 ms 이상 |
| UART decoder | 115200 baud, 8 data, no parity, 1 stop, idle high |
| Trigger | PWM edge, DIR edge, PA10 UART activity or PC13 edge by test |

24 MHz에서는 19 kHz PWM period당 약 1260 sample을 얻는다. 긴 timeout capture에서 buffer가 부족하면 sample rate를 낮추되 2 MHz 아래로 내리지 않는다.

## Evidence file convention

각 capture는 다음 위치에 저장한다.

```text
assets/captures/logic_analyzer/YYYY-MM-DD_<test>_<result>.sr
assets/captures/logic_analyzer/YYYY-MM-DD_<test>_<result>.pvs
assets/screenshots/logic_analyzer/YYYY-MM-DD_<measurement>_<result>.png
```

`.sr`은 raw sample, `.pvs`는 PulseView session 설정, `.png`는 판정에 사용한 view/cursor 증거다. 이번 interactive cursor 측정에서는 CSV를 필수 산출물로 만들지 않았다. 파일별 관계와 실제 channel map은 각 evidence 디렉터리의 `README.md`에 기록한다.

기본 PNG 위치는 `assets/screenshots/logic_analyzer`다. 다만 2026-08-04처럼 하나의
`.sr/.pvs` capture bundle에서 직접 만든 overview/detail PNG는 raw 파일과의 관계를
명확히 하기 위해 `assets/captures/logic_analyzer`에 함께 둘 수 있으며, 이 예외는 해당
디렉터리 `README.md`에 색인한다.

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
- `PC8`, `PB6`, `PC9`, `PB7` 각각 signal-to-GND 외부 `10 kΩ` pull-down 적용

Procedure:

1. CH0~CH3와 GND를 연결한다.
2. Capture를 먼저 시작한다.
3. STM32 reset 또는 power-on을 수행한다.
4. Initialization 완료 후 1초 이상 유지한다.
5. 두 PWM과 두 DIR의 transition을 검사한다.

Acceptance:

- PB6/PB7에 active-high PWM pulse가 없어야 한다.
- PB6/PB7/PC8/PC9는 reset 시작부터 firmware 초기화 뒤까지 LOW여야 한다.
- Reset 동안 단발 active pulse가 없어야 한다.
- Test-disabled build에서 B1 입력은 output을 바꾸지 않아야 한다.

2026-08-12 result:

- Pull-down 미적용 첫 external-reset capture: DIR/PWM 네 signal이 NRST LOW 구간에 약
  159 ms HIGH로 판독돼 `FAIL`.
- 각 signal-to-GND `10 kΩ` 적용 재시험: 5 s/20 M samples에서 D2~D5 HIGH sample과
  transition 모두 0, `PASS`.
- PA5/LD2 fault marker는 motor control output이 아니며 reset 중 의미가 없으므로 이
  acceptance에서 제외한다.

## Test 2: Steady 10% PWM frequency and duty

Setup:

- Motor disconnected.
- Controlled bench hook에서 한 channel만 100 permille로 활성화한다.
- 다른 channel은 0을 유지한다.

Measure:

| Metric | Acceptance |
| --- | --- |
| PWM frequency | 18.8~19.2 kHz, vendor upper limit 20 kHz 이하 |
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

2026-08-04 result:

- DISARM target: `DISARM,seq=72192971\n`
- `t0`, final LF stop-bit end: `2,287,888.50 us`
- `t1`, PB6/PB7 last active falling edge: `2,287,912.00 us`
- first baseline `t1 - t0`: `23.50 us`
- STM32 ACK start: `2,287,974.75 us`; PWM stop은 ACK보다 `62.75 us` 선행
- 이후 남은 약 2.712088 s 동안 두 PWM HIGH sample 0, 두 DIR LOW

판정은 `PASS — scoped first baseline`이다. Numeric release limit은 아직 고정되지
않았고 MCU logic pin만 측정했으므로 MDD10A/motor/E-stop PASS가 아니다. 상세 결과는
[`../docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md`](../docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)를 따른다.

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

- Observed total은 configured timeout 주변에서 bounded stop이어야 한다. `HAL_GetTick()`의
  1 ms phase와 analyzer sample-clock tolerance를 별도 기록한다.
- Configured timeout의 정수 tick 경계 뒤 bounded loop delay 내 두 PWM이 inactive가 된다.
- Timeout 뒤 old command가 자동 재적용되지 않는다.
- Exact bound는 parser/safety-state refactor와 first measurement 뒤 고정한다.

현재 firmware가 timeout 뒤 state를 별도 latched stop으로 전환하는지 source/runtime을 함께 확인한다. Architecture contract와 다르면 `PASS`하지 않는다.

2026-08-12 result:

- `CMD,seq=607604632,vx_mmps=50,w_mradps=0,timeout_ms=300`
- Nominal 4 MHz 계산은 LF-to-last-edge `298.6755 ms`.
- UART 115200 bit width로 추정한 actual analyzer rate를 적용하면 `299.690003 ms`.
- 두 PWM 정지 뒤 약 `8.939464 s` edge 0, 두 DIR LOW, 자동 재활성화 없음.
- `PASS — scoped baseline`; `300.000 ms` 이상이라는 이전 strict 조건은 tick/sample-clock
  phase를 무시하므로 사용하지 않는다.

## Test 6: Software fault shutdown timing

2026-07-30 작업자/DMM·LED 기능시험에서는 software fault 뒤 output-zero와 reset 전
latch가 PASS했다. 이 Test 6은 그 기능 판정을 대체하는 것이 아니라 아직 없는
fault-event-to-PWM-edge latency를 계측하고 latch를 파형과 함께 회귀 확인한다.

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

2026-08-12 result:

- PA5 fault marker는 `2.94778575 s`, PB6/PB7 last falling edge는 marker보다 `5.25 us`
  앞이었다.
- Marker가 PWM LOW phase에 발생했으므로 `5.25 us`를 shutdown latency로 표현하지 않는다.
- 약 `39.5 us` 뒤 예정됐던 next rising edge가 차단됐고 marker 이후 edge 0, 약
  `2.052214 s` no-reactivation latch를 확인했다.
- `PASS — bounded stop/latch`; exact positive marker-to-disable latency는 별도 trigger/marker
  설계 없이는 주장하지 않는다.

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
pwsh -File Projects/Tracked_Mobile_Robot/03_Firmware/tools/Build-Firmware.ps1 -Target All
```

Capture evidence를 저장하고 검토한다. 사용자가 커밋을 요청한 경우에만 범위를 확인해
커밋한 뒤 동일 build를 `-RequireClean`으로 한 번 더 실행해 최종 tracked state가
clean인지 확인한다. 커밋 요청이 없으면 `-RequireClean`을 completion 조건으로 삼지
않고 현재 worktree 상태와 일반 build 결과를 별도로 기록한다. 미추적 `.sr/.csv/.png`가
있는 상태에서 `-RequireClean`을 먼저 사용하지 않는다.

## Result table

| Test | Result | Evidence | Notes |
| --- | --- | --- | --- |
| Sampled initial inactive interval | `PASS — scoped` | [`PNG`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_boot_inactive_pass.png), [`SR/PVS`](../assets/captures/logic_analyzer/README.md) | D0~D3 transition 없음. 외부 reset marker가 없어 reset 순간 전체를 독립 입증한 결과로 확대하지 않음 |
| CH1 20 kHz / 10% | `PASS` | [`period`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_pwm1_period_20khz_pass.png), [`high time`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_pwm1_high_time_5us_pass.png) | 49.75 us = 20.1005 kHz, high 5.00 us, duty 약 10.05% |
| CH2 20 kHz / 10% | `PASS` | [`period`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_pwm2_period_20khz_pass.png), [`high time`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_pwm2_high_time_5us_pass.png) | 49.75 us = 20.1005 kHz, high 5.00 us, duty 약 10.05% |
| Final perfboard CH1 19 kHz / 10% | `PASS` | [2026-08-18 report](../docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md) | 19.049003 kHz, duty 10.0138%, pre/post DIR zero 2.017/2.020 ms |
| Final perfboard CH2 19 kHz / 10% | `PASS` | [2026-08-18 report](../docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md) | 19.057518 kHz, duty 10.0030%, pre/post DIR zero 2.006/2.029 ms |
| Final hook-0 perfboard all-LOW | `PASS` | [2026-08-18 report](../docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md) | D0~D3 5 s HIGH sample/transition 0, B1 no output |
| CH1 direction settle | `PASS` | [`pre-DIR`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_pwm1_pre_dir_zero_ge1ms_pass.png), [`post-DIR`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_pwm1_post_dir_zero_ge1ms_pass.png) | 1.994 ms / 2.03875 ms, 모두 최소 1 ms 이상 |
| CH2 direction settle | `PASS` | [`pre-DIR`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_pwm2_pre_dir_zero_ge1ms_pass.png), [`post-DIR`](../assets/screenshots/logic_analyzer/2026-08-03_stm32_motor_io_pwm2_post_dir_zero_ge1ms_pass.png) | 1.54725 ms / screenshot 약 2.05832 ms; raw edge review 약 2.040 ms, 모두 최소 1 ms 이상 |
| DISARM latency | `PASS — scoped first baseline` | [2026-08-04 report](../docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md), [SR/PVS/PNG](../assets/captures/logic_analyzer/README.md) | UART RX end -> both PWM last edge 23.50 us; numeric release bound TBD |
| Timeout latency | `PASS — scoped baseline` | [2026-08-12 report](../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md), [SR/PVS](../assets/captures/logic_analyzer/README.md) | 300 ms command; calibrated LF-to-last-edge 약 299.690 ms, stop 뒤 약 8.939 s edge 0; 1 ms tick/sample-clock tolerance 명시 |
| Software fault output-zero/latch function | `PASS — functional DMM/LED scope` | [2026-07-30 operator record](../assets/logs/motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md) | 정확한 edge latency 증거는 아님 |
| Software fault next-pulse stop/latch | `PASS — bounded` | [2026-08-12 report](../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md), [SR/PVS](../assets/captures/logic_analyzer/README.md) | Marker가 LOW phase여서 exact positive latency는 미주장; next rise 차단, marker 뒤 edge 0, 약 2.052 s latch |
| External reset without pull-down | `FAIL — root cause preserved` | [SR/PVS](../assets/captures/logic_analyzer/README.md) | NRST LOW 동안 네 control signal 약 159 ms HIGH 판독 |
| External reset with `10 kΩ` pull-down | `PASS` | [2026-08-12 report](../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md), [SR/PVS](../assets/captures/logic_analyzer/README.md) | 5 s/20 M samples에서 PB6/PB7/PC8/PC9 HIGH sample·transition 0 |
| Final hook-off source/static/build regression | `PASS` | [2026-08-12 report](../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md) | ESP/STM 모든 controlled hook `0U`; contract `15/15`, 양 firmware build artifact hash 기록 |
| Restored safe-image board regression | `PASS — behavior / provenance scoped` | [final raw log](../assets/logs/esp32_uart_bridge/2026-08-12_post_motor_output_safety_safe_uart_runtime_regression_pass.txt) | Exact ACK/PONG/READY, post-READY 15.4 s/TEL 155 safe, ARM/CMD/retry/error 0; raw flash console 미보존 |

상세 수치, 판정 범위와 증거 연결은 [`../docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md`](../docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md)를 따른다. High-time 화면의 약 200 kHz 표시는 `1 / 5 us`이며 PWM 반복 주파수가 아니다. PWM 주파수 판정은 rising-to-rising 49.75 us 측정만 사용했다.

## Current gate decision

```text
Logic analyzer: AVAILABLE / CAPTURED
Boot inactive + final perfboard 19 kHz/10% + direction settle subtests: PASS
DISARM pin-edge latency: PASS — scoped first baseline, 23.50 us
Timeout shutdown: PASS — scoped baseline, calibrated 299.690 ms for timeout_ms=300
Software-fault stop/latch: PASS — bounded next-pulse suppression; exact positive latency not claimed
External-reset-marker motor-pin capture: initial FAIL -> 10 kΩ pull-down retest PASS
Safe-image UART board runtime: PASS — exact image/setup provenance scoped
Motor-disconnected MCU and MDD10A-input logic safety chapter: PASS
First powered motor test: NOT READY
```

Physical E-stop은 별도 hardware-energy-cut requirement다. 이 문서의 software PWM shutdown capture로 [`../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)를 대체하지 않는다.
