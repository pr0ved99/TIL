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

## Integrity and Reuse Notes

- 판정 수치를 다시 검토할 때는 `.sr`을 PulseView에서 열고 위 channel map을 적용한다.
- `.pvs`만으로 sample data가 보존된다고 가정하지 않는다.
- 파일명을 바꾸면 report와 screenshot index의 상대 링크도 함께 갱신한다.
- 이 자료는 MCU logic pin 측정이며 MDD10A power terminal, motor current, 실제 motor stop 또는 Physical E-stop을 입증하지 않는다.
- Active-DISARM capture 당시 ESP scripted hook과 STM32 UART output hook은 `1U`였다. 현재 worktree는 ESP `0U/1000 ms`, STM32 output hook `0U`로 복구됐고 contract `15/15`와 isolated clean STM32/ESP32 build run `20260804043010-26408-7918`이 PASS다. Restored safe images의 board reflash/run과 ARM/CMD 0 runtime evidence는 pending이다.
