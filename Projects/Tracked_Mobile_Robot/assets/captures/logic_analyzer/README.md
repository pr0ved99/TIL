# Logic Analyzer Raw Captures

이 디렉터리는 PulseView/sigrok로 저장한 원본 로직 분석기 자료를 보관한다.

- `.sr`: 실제 digital sample과 capture metadata를 포함하는 sigrok session archive. 재검토 시 기준이 되는 원본 증거다.
- `.pvs`: PulseView의 화면 배치, decoder, channel 표시 등 session view 상태를 보관한다. `.sr`을 대체하는 raw data 파일이 아니다.
- `.png`: 판정에 사용한 cursor와 확대 화면이다. 기존 capture는 주로 [`../../screenshots/logic_analyzer/README.md`](../../screenshots/logic_analyzer/README.md)에서 관리하며, 2026-08-04 active-DISARM PNG 두 개는 raw session과 함께 이 디렉터리에 보존한다.

관련 문서:

- [STM32 Motor Output Waveform and Direction Timing Test Report](../../../docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md)
- [STM32 Active DISARM Shutdown Latency Test Report](../../../docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)
- [Motor Output Waveform And Shutdown Latency Test](../../../02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md)
- [Screenshot index](../../screenshots/logic_analyzer/README.md)

## Canonical Channel Map for 2026-08-03 Motor Capture

| PulseView channel | Connected signal |
| --- | --- |
| `D0` | `PC8 / DIR1` |
| `D1` | `PB6 / TIM4_CH1 / PWM1` |
| `D2` | `PC9 / DIR2` |
| `D3` | `PB7 / TIM4_CH2 / PWM2` |
| `D4`~`D7` | Not connected |
| Analyzer `GND` | STM32 GND |

Motor capture 설정은 4 MHz sample rate였다. Initial inactive capture는 1 M samples, B1 six-step capture는 50 M samples이다. 모터와 MDD10A 전력단은 분리하고 STM32 측 3.3 V signal만 관찰했다.

## Capture Sets

### 2026-08-02 STM32 USART1 TX UART decode

- Raw capture: [2026-08-02_stm32_usart1_tx_uart_decode_pass.sr](./2026-08-02_stm32_usart1_tx_uart_decode_pass.sr)
- PulseView session: [2026-08-02_stm32_usart1_tx_uart_decode_pass.pvs](./2026-08-02_stm32_usart1_tx_uart_decode_pass.pvs)
- Screenshot: [2026-08-02_stm32_usart1_tx_uart_decode_pass.png](../../screenshots/logic_analyzer/2026-08-02_stm32_usart1_tx_uart_decode_pass.png)

UART decoder가 STM32 USART1 TX telemetry text를 해석하는 것을 확인한 별도 준비 capture다. 2026-08-03 PWM/DIR timing 판정의 raw capture는 아니다.

### 2026-08-03 Initial inactive interval

- Raw capture: [2026-08-03_stm32_motor_io_boot_inactive_pass.sr](./2026-08-03_stm32_motor_io_boot_inactive_pass.sr)
- PulseView session: [2026-08-03_stm32_motor_io_boot_inactive_pass.pvs](./2026-08-03_stm32_motor_io_boot_inactive_pass.pvs)
- Screenshot: [2026-08-03_stm32_motor_io_boot_inactive_pass.png](../../screenshots/logic_analyzer/2026-08-03_stm32_motor_io_boot_inactive_pass.png)

캡처된 0.25초 구간에서 D0~D3 transition이 관찰되지 않았다. 외부 reset marker가 없으므로 reset 순간 전체 또는 장시간 boot 동작의 증거로 확대하지 않는다.

### 2026-08-03 B1 six-step PWM/DIR sequence

- Raw capture: [2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.sr](./2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.sr)
- PulseView session: [2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.pvs](./2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.pvs)
- Overview screenshot: [2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.png](../../screenshots/logic_analyzer/2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.png)

이 raw capture에서 PWM1/PWM2 frequency와 duty, 두 방향 전환의 pre/post inactive interval을 cursor로 측정했다. B1 six-step은 임시 bench hook이며 production 동작이 아니다.

측정 요약:

| Signal | Period / frequency | High time / duty | Pre-DIR inactive | Post-DIR inactive |
| --- | --- | --- | --- | --- |
| PWM1 / D1 | 49.750 µs / 20.1005 kHz | 5.000 µs / 약 10.05% | 1994.000 µs | 2038.750 µs |
| PWM2 / D3 | 49.750 µs / 20.1005 kHz | 5.000 µs / 약 10.05% | 1547.250 µs | 약 2040.00 µs edge-to-edge |

High-time cursor에 표시되는 약 200 kHz는 `1 / 5 µs`이며 PWM 반복 주파수가 아니다.

PWM2 post-DIR PNG의 선택 범위는 DIR edge보다 약 `18.3 µs` 일찍 시작해 `2058.320205 µs`로 표시된다. Raw signal edge-to-edge 간격은 약 `2040.00 µs`이며 판정에는 이 값을 사용한다.

## Channel Map for 2026-08-04 Active DISARM Capture

| PulseView channel | Connected signal |
| --- | --- |
| `D0` | `PC8 / DIR1` |
| `D1` | `PB6 / TIM4_CH1 / PWM1` |
| `D2` | `PC9 / DIR2` |
| `D3` | `PB7 / TIM4_CH2 / PWM2` |
| `D4` | `PA10 / USART1 RX` |
| `D5` | `PA9 / USART1 TX` |
| `D6`, `D7` | Not used |
| Analyzer `GND` | STM32 GND |

`.pvs`는 D4를 UART RX, D5를 UART TX로 assign한다. D0~D5의 실제 pin 배선과
motor-energy 분리 조건은 작업자 확인 전까지 `operator confirmation pending`이며,
raw digital data만으로 물리 setup 전체를 독립 증명한다고 해석하지 않는다.

### 2026-08-04 Active DISARM UART-to-PWM stop

- Raw capture: [2026-08-04_stm32_disarm_active_pwm_stop_pass.sr](./2026-08-04_stm32_disarm_active_pwm_stop_pass.sr)
- PulseView session: [2026-08-04_stm32_disarm_active_pwm_stop_pass.pvs](./2026-08-04_stm32_disarm_active_pwm_stop_pass.pvs)
- Overview: [2026-08-04_stm32_disarm_rx_pwm_stop_before_ack_pass.png](./2026-08-04_stm32_disarm_rx_pwm_stop_before_ack_pass.png)
- Detail: [2026-08-04_stm32_disarm_pwm_stop_before_ack_detail.png](./2026-08-04_stm32_disarm_pwm_stop_before_ack_detail.png)

Capture metadata는 8 channels, 4 MHz, 20 M samples, 1 byte/sample이다. Raw sample
audit 결과:

| Event | Time |
| --- | ---: |
| DISARM final LF stop-bit end | `2,287,888.50 µs` |
| D1/D3 last active falling edge | `2,287,912.00 µs` |
| STM32 ACK start on D5 | `2,287,974.75 µs` |
| DISARM-to-PWM-zero baseline | `23.50 µs` |
| PWM stop before ACK | `62.75 µs` |

D1/D3은 마지막 edge 뒤 남은 10,848,352 samples, 약 2.712088 s 동안 HIGH sample이
없고 D0/D2는 LOW다. 이 결과는 MCU-pin first baseline `PASS — scoped`이며 numeric
release limit은 아직 고정되지 않았다.

## Channel Map for 2026-08-12 Timeout, Fault And Reset Captures

| PulseView channel | Connected signal |
| --- | --- |
| `D0` | `PA9 / USART1_TX` |
| `D1` | `PA10 / USART1_RX` |
| `D2` | `PC8 / DIR1` |
| `D3` | `PB6 / PWM1` |
| `D4` | `PC9 / DIR2` |
| `D5` | `PB7 / PWM2` |
| `D6` | `PA5 / LD2 / FAULT_MARKER` |
| `D7` | reset captures에서 `NRST`; timeout/fault에서는 미사용 |
| Analyzer `GND` | STM32 GND |

공통 물리 조건은 motor, LiPo와 MDD10A `B+/B-` motor energy 분리, board 간
`5 V/VBUS/VIN` 미연결, analyzer GND=STM32 GND다. 이 조건은 작업자 확인이며 raw `.sr`
자체에 완전히 내장되지 않는다. 상세 수치와 claim boundary는
[`../../../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`](../../../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md)를 따른다.

### Command-timeout shutdown PASS

- Raw capture: [2026-08-12_stm32_command_timeout_shutdown_pass.sr](./2026-08-12_stm32_command_timeout_shutdown_pass.sr)
- PulseView session: [2026-08-12_stm32_command_timeout_shutdown_pass.pvs](./2026-08-12_stm32_command_timeout_shutdown_pass.pvs)
- SHA-256: `12CE83B2899FE6E00CFCD27F34999E5981D7C92B06DA86AD5B963903E541D64D`

`timeout_ms=300` command의 final LF부터 두 PWM last edge까지 nominal 4 MHz로
`298.6755 ms`, UART bit-width로 보정한 analyzer rate 기준 `299.690003 ms`였다. Stop 뒤
약 `8.939464 s` 동안 PWM edge가 다시 나오지 않았다. 1 ms `HAL_GetTick()` phase와 analyzer
clock tolerance를 명시한 scoped baseline PASS다.

### Software-fault shutdown/latch PASS

- Raw capture: [2026-08-12_stm32_software_fault_shutdown_latch_pass.sr](./2026-08-12_stm32_software_fault_shutdown_latch_pass.sr)
- PulseView session: [2026-08-12_stm32_software_fault_shutdown_latch_pass.pvs](./2026-08-12_stm32_software_fault_shutdown_latch_pass.pvs)
- SHA-256: `E7D1CD59D3CA8C76E3757E2BD7E765468189EB3C609652B0B5D62E12B84AA02D`

Fault marker는 PWM LOW phase에서 발생해 last falling edge보다 `5.25 us` 늦었다. 따라서
이 값을 shutdown latency로 표현하지 않는다. Marker 뒤 예정된 next PWM rise가 차단됐고
약 `2.052214 s` 동안 두 PWM edge 0으로 no-reactivation latch를 확인했다.

### External reset without pull-down FAIL

- Raw capture: [2026-08-12_stm32_external_reset_floating_motor_inputs_fail.sr](./2026-08-12_stm32_external_reset_floating_motor_inputs_fail.sr)
- PulseView session: [2026-08-12_stm32_external_reset_floating_motor_inputs_fail.pvs](./2026-08-12_stm32_external_reset_floating_motor_inputs_fail.pvs)
- SHA-256: `4B638CD9B9F9A37CB68275FFF344B604BA66DE14457B3741DE3B8FC6E7F308B8`

NRST LOW 중 DIR1/PWM1/DIR2/PWM2가 약 `159 ms` HIGH로 판독됐다. Motor power가 분리돼
실제 회전은 없었지만 reset 구간 safe LOW가 전기적으로 보장되지 않아 FAIL로 보존한다.

### External reset with `10 kΩ` pull-down PASS

- Raw capture: [2026-08-12_stm32_external_reset_boot_10kohm_pulldown_pass.sr](./2026-08-12_stm32_external_reset_boot_10kohm_pulldown_pass.sr)
- PulseView session: [2026-08-12_stm32_external_reset_boot_10kohm_pulldown_pass.pvs](./2026-08-12_stm32_external_reset_boot_10kohm_pulldown_pass.pvs)
- SHA-256: `A4E16F12B433282941B9404E7792412F0FA52BE7C25A96A9E622E95681976EA5`

PC8/PB6/PC9/PB7 각각 signal-to-GND `10 kΩ`을 적용했다. 5 s/20 M samples에서 네
signal의 HIGH sample과 transition이 모두 0이었다. PA5/LD2는 motor control output이 아니며
fault marker 의미는 firmware 실행 중에만 유효하므로 reset no-output acceptance에서 제외했다.

## Integrity and Reuse Notes

- 판정 수치를 다시 검토할 때는 `.sr`을 PulseView에서 열고 위 channel map을 적용한다.
- `.pvs`만으로 sample data가 보존된다고 가정하지 않는다.
- 파일명을 바꾸면 report와 screenshot index의 상대 링크도 함께 갱신한다.
- 이 자료는 MCU logic pin 측정이며 MDD10A power terminal, motor current, 실제 motor stop 또는 Physical E-stop을 입증하지 않는다.
- Active-DISARM capture 당시 ESP scripted hook과 STM32 UART output hook은 `1U`였다.
  2026-08-12 timeout/fault controlled capture 뒤 모든 hook을 `0U`로 복구했고 contract
  `15/15`, 양 firmware build와 safe UART 회귀가 PASS다. External-reset-marker capture는
  pull-down 미적용 FAIL을 거쳐 `10 kΩ` 적용 재시험 PASS로 닫았다. Raw flash console과
  log-embedded physical setup이 없어 exact artifact/setup provenance는 scoped limitation이다.
