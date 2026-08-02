# Logic Analyzer Raw Captures

이 디렉터리는 PulseView/sigrok로 저장한 원본 로직 분석기 자료를 보관한다.

- `.sr`: 실제 digital sample과 capture metadata를 포함하는 sigrok session archive. 재검토 시 기준이 되는 원본 증거다.
- `.pvs`: PulseView의 화면 배치, decoder, channel 표시 등 session view 상태를 보관한다. `.sr`을 대체하는 raw data 파일이 아니다.
- `.png`: 판정에 사용한 cursor와 확대 화면이다. [`../../screenshots/logic_analyzer/README.md`](../../screenshots/logic_analyzer/README.md)에서 관리한다.

관련 문서:

- [STM32 Motor Output Waveform and Direction Timing Test Report](../../../docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md)
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

## Integrity and Reuse Notes

- 판정 수치를 다시 검토할 때는 `.sr`을 PulseView에서 열고 위 channel map을 적용한다.
- `.pvs`만으로 sample data가 보존된다고 가정하지 않는다.
- 파일명을 바꾸면 report와 screenshot index의 상대 링크도 함께 갱신한다.
- 이 자료는 MCU logic pin 측정이며 MDD10A power terminal, motor current, 실제 motor stop 또는 Physical E-stop을 입증하지 않는다.
- 임시 test source는 현재 `0U`로 복구되었고 restored-source build는 성공했지만, 복구 binary의 물리적 flash 및 post-flash final capture는 아직 pending이다.
