# Logic Analyzer Screenshot Index

이 디렉터리는 PulseView raw capture에서 판정에 사용한 overview와 cursor measurement 화면을 보관한다. PNG는 검토와 문서 표시를 위한 파생 증거이며, 재측정 기준은 [`../../captures/logic_analyzer/README.md`](../../captures/logic_analyzer/README.md)에 정리된 `.sr` raw capture다.

관련 문서:

- [STM32 Motor Output Waveform and Direction Timing Test Report](../../../docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md)
- [Motor Output Waveform And Shutdown Latency Test](../../../02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md)
- [Raw capture and session index](../../captures/logic_analyzer/README.md)

## Actual Motor Capture Channel Map

| Channel | Signal |
| --- | --- |
| `D0` | `PC8 / DIR1` |
| `D1` | `PB6 / TIM4_CH1 / PWM1` |
| `D2` | `PC9 / DIR2` |
| `D3` | `PB7 / TIM4_CH2 / PWM2` |

Capture sample rate는 4 MHz였다. 화면의 cursor 수치는 PulseView 표시값이며 nominal sample 간격은 0.25 µs이다.

## 2026-08-02 UART Decoder Preparation

| Screenshot | Purpose | Raw/session |
| --- | --- | --- |
| [STM32 USART1 TX UART decode PASS](./2026-08-02_stm32_usart1_tx_uart_decode_pass.png) | USART1 TX text decode 확인 | [SR](../../captures/logic_analyzer/2026-08-02_stm32_usart1_tx_uart_decode_pass.sr), [PVS](../../captures/logic_analyzer/2026-08-02_stm32_usart1_tx_uart_decode_pass.pvs) |

## 2026-08-03 Overview Captures

| Screenshot | Observation | Raw/session |
| --- | --- | --- |
| [Initial inactive interval](./2026-08-03_stm32_motor_io_boot_inactive_pass.png) | 캡처된 0.25초 구간에서 D0~D3 transition 없음 | [SR](../../captures/logic_analyzer/2026-08-03_stm32_motor_io_boot_inactive_pass.sr), [PVS](../../captures/logic_analyzer/2026-08-03_stm32_motor_io_boot_inactive_pass.pvs) |
| [B1 six-step sequence](./2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.png) | 두 PWM/DIR 채널의 순차 시험과 최종 inactive 상태 | [SR](../../captures/logic_analyzer/2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.sr), [PVS](../../captures/logic_analyzer/2026-08-03_stm32_motor_io_b1_six_step_sequence_pass.pvs) |

Initial inactive 화면에는 외부 reset marker가 없으므로 reset 순간 전체의 독립 증거로 확대하지 않는다. B1 six-step은 임시 bench hook이며 production 동작이 아니다.

## PWM1 / D1 Measurements

| Screenshot | PulseView value | Interpretation |
| --- | ---: | --- |
| [High time](./2026-08-03_stm32_motor_io_pwm1_high_time_5us_pass.png) | 5.000000 µs | PWM high width; 약 200 kHz 표시는 이 폭의 역수이며 PWM 반복 주파수가 아님 |
| [Period](./2026-08-03_stm32_motor_io_pwm1_period_20khz_pass.png) | 49.750000 µs / 20.100502513 kHz | Rising-to-rising PWM period/frequency |
| [Pre-DIR inactive](./2026-08-03_stm32_motor_io_pwm1_pre_dir_zero_ge1ms_pass.png) | 1994.000000 µs | Last PWM pulse부터 DIR edge까지; ≥1.0 ms PASS |
| [Post-DIR inactive](./2026-08-03_stm32_motor_io_pwm1_post_dir_zero_ge1ms_pass.png) | 2038.750000 µs | DIR edge부터 first PWM pulse까지; ≥1.0 ms PASS |

PWM1 calculated duty: `5.000 / 49.750 × 100 = 약 10.05%`.

## PWM2 / D3 Measurements

| Screenshot | PulseView value | Interpretation |
| --- | ---: | --- |
| [High time](./2026-08-03_stm32_motor_io_pwm2_high_time_5us_pass.png) | 5.000000 µs | PWM high width; 약 200 kHz 표시는 이 폭의 역수이며 PWM 반복 주파수가 아님 |
| [Period](./2026-08-03_stm32_motor_io_pwm2_period_20khz_pass.png) | 49.750000 µs / 20.100502512 kHz | Rising-to-rising PWM period/frequency |
| [Pre-DIR inactive](./2026-08-03_stm32_motor_io_pwm2_pre_dir_zero_ge1ms_pass.png) | 1547.250000 µs | Last PWM pulse부터 DIR edge까지; ≥1.0 ms PASS |
| [Post-DIR inactive](./2026-08-03_stm32_motor_io_pwm2_post_dir_zero_ge1ms_pass.png) | 화면 선택 2058.320205 µs; edge-to-edge 약 2040.00 µs | 선택 시작점이 DIR edge보다 약 18.3 µs 앞섬; 실제 DIR edge부터 first PWM pulse까지도 ≥1.0 ms PASS |

PWM2 calculated duty: `5.000 / 49.750 × 100 = 약 10.05%`.

## Scope and Pending Evidence

- 이 PNG 세트는 STM32 3.3 V digital output의 waveform/direction timing 하위 시험을 입증한다.
- MDD10A powered output, motor current/rotation/stop, Physical E-stop은 입증하지 않는다.
- `DISARM`, command timeout, software fault shutdown latency 캡처는 아직 없다.
- 임시 hook source는 `0U`로 복구되었고 restored-source build는 성공했다. 복구 binary를 실제 STM32에 flash한 뒤의 최종 hook-off boot/runtime screenshot은 아직 pending이다.
