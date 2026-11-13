# STM32 Active DISARM Shutdown Latency Test Report - 2026-08-04

## 판정

```text
Active DISARM UART-RX-to-PWM-zero baseline: PASS — STM32 MCU logic pins
Measured latency: 23.50 us
Overall motor safety gate: PARTIAL
```

Valid `DISARM,seq=72192971`의 마지막 LF stop bit가 STM32 USART1 RX에 도착한
시점부터 `PB6/PWM1`, `PB7/PWM2`의 마지막 active edge까지를 같은 4 MHz raw
capture에서 측정했다. 두 PWM은 frame 완료 뒤 23.50 us에 inactive가 됐고,
STM32 ACK 전송이 시작되기 62.75 us 전에 이미 멈췄다.

이 결과는 MCU 3.3 V logic pin의 active-DISARM shutdown baseline만 통과시킨다.
MDD10A power terminal, motor current, 실제 motor stop, mechanical stop time/distance
또는 Physical E-stop을 검증한 결과가 아니다.

## 해결하려는 검증 문제

이전 UART monitor와 MDD10A LED 시험은 `DISARM` 뒤 output이 결국 zero가 되는
기능을 보여줬지만, console timestamp나 100 ms telemetry로는 실제 PWM 차단
시점을 계측할 수 없다. 이 시험은 UART request와 PWM edge를 같은 timebase에
기록해 다음 질문에 답한다.

```text
valid DISARM frame 수신 완료
-> STM32 parser/safety path
-> motor_output safe path
-> PB6/PB7 active edge 종료
```

## 시험 조건과 현재 확인 범위

| Item | Value / status |
| --- | --- |
| STM32 | NUCLEO-F446RE |
| Command source | ESP32-S3 UART1 |
| UART | `115200 8-N-1` |
| Analyzer | sigrok FX2 LA, 8 channels |
| Sample rate | 4 MHz |
| Sample resolution | 0.25 us/sample |
| Capture length | 20,000,000 samples / 5.0 s |
| Test output | STM32 `UART_MVP_OUTPUT_TEST_ENABLED=1U`, 100 permille cap |
| ESP script | `BRIDGE_SCRIPTED_TEST_ENABLED=1U`, 100 ms step period |
| LiPo / MDD10A B+/B- / actual motor power disconnected | operator confirmation pending |
| Analyzer connected only to STM32 logic pins/common GND | channel data는 확인, 물리 setup은 operator confirmation pending |
| Flash transcript / binary hash | capture와 raw UART log만으로 독립 확인 불가 |

위 표의 `1U/100 ms`는 active-DISARM capture 당시 시험 조건이다. 현재 worktree는
ESP `0U/1000 ms`, STM output hook `0U`로 복구됐고 contract `15/15`와 isolated clean
dual build run `20260804043010-26408-7918`이 PASS다. 2026-08-06 follow-up에서는
wrong-ACK hook까지 `0U`로 복구하고 current `15/15`, STM32 build와 safe-image UART
runtime behavior를 PASS했다. Exact image/setup provenance와 reset-marker boot는 pending이다.

## Channel Map

| Analyzer channel | STM32 signal | Purpose |
| --- | --- | --- |
| `D0` | `PC8 / DIR1` | channel 1 direction |
| `D1` | `PB6 / TIM4_CH1 / PWM1` | channel 1 PWM |
| `D2` | `PC9 / DIR2` | channel 2 direction |
| `D3` | `PB7 / TIM4_CH2 / PWM2` | channel 2 PWM |
| `D4` | `PA10 / USART1 RX` | ESP32 -> STM32 DISARM reference |
| `D5` | `PA9 / USART1 TX` | STM32 -> ESP32 ACK reference |
| `D6`, `D7` | not used | — |
| Analyzer `GND` | STM32 GND | digital reference |

## 제어 흐름과 데이터 흐름

UART raw log에서 startup이 READY가 된 뒤 controlled sequence가 진행됐다.

| Step | UART observation | State/output observation |
| --- | --- | --- |
| Startup | exact DISARM ACK, exact PONG, READY | DISARMED / zero |
| CMD before ARM | `ERR ... NOT_ARMED` | DISARMED / zero |
| ARM | `ACK,type=ARM` | ARMED |
| Valid CMD | `ACK,type=CMD`, `vx=50` | both 10%-limited PWM active |
| Invalid CMD | `ERR ... OUT_OF_RANGE` | previous valid active output retained |
| Active DISARM | `ACK,type=DISARM` | both PWM stop, DIR safe LOW, DISARMED/zero |

Startup line sync 직후 raw log에는 `ERR,type=RX,code=RX_DESYNC`가 1회 기록됐다.
다음 정상 DISARM/ACK와 PING/PONG에서 복구돼 READY에 진입했으며 active-DISARM
측정 경로를 깨지 않았다. 이 capture를 통신 무오류 증거로 해석하지 않는다.

The out-of-range command intentionally does not replace the previous valid active
command. This creates an active-output condition immediately before DISARM and tests
the common safe-output path rather than an already-zero output.

## 측정 정의

```text
t0   = DISARM frame final LF stop-bit end on PA10/D4
t1   = last active falling edge on PB6/D1 and PB7/D3
tACK = first start edge of STM32 ACK on PA9/D5

shutdown baseline = t1 - t0
PWM-before-ACK margin = tACK - t1
```

Console log time는 수 ms 단위 task timestamp이고 telemetry는 100 ms 주기이므로
이 수치 계산에 사용하지 않았다. Raw `.sr` sample과 UART waveform을 동일 4 MHz
timebase에서 해석했다.

## 측정 결과

| Measurement | Value | Result |
| --- | ---: | --- |
| `t0`, DISARM LF stop-bit end | `2,287,888.50 us` | reference |
| PWM1 last active falling edge | `2,287,912.00 us` | both channels agree |
| PWM2 last active falling edge | `2,287,912.00 us` | both channels agree |
| `t1 - t0` | `23.50 us` | PASS baseline |
| `tACK`, ACK start | `2,287,974.75 us` | reference |
| `tACK - t1` | `62.75 us` | PWM stopped before ACK |
| `tACK - t0` | `86.25 us` | informational |
| D1/D3 high samples after `t1` | `0` across remaining 10,848,352 samples | no restart in captured remainder |
| D0/D2 after shutdown | LOW | safe direction level observed |

한 sample은 0.25 us다. 따라서 23.50 us는 94 sample에 해당하며, 이 sample
rate의 양자화 한계를 포함한 baseline이다. Numeric release deadline은 아직
별도 requirement로 고정되지 않았으므로 이 결과를 임의의 인증 한계 통과로
표현하지 않는다. 현재 절차의 첫 measurement acceptance는 실제 baseline을
기록하고 두 PWM zero, DIR LOW, 재시작 없음과 ACK 전 stop을 확인하는 것이다.

## 정상 경로와 실패 경로 해석

정상 경로는 valid DISARM의 exact parse 뒤 safety state가 DISARMED로 바뀌고
common motor-output stop path가 두 PWM compare output과 두 DIR을 safe level로
내리는 것이다. 캡처는 두 PWM이 같은 시점에 멈추고 ACK보다 먼저 zero가 됨을
보여준다.

이 시험이 다루지 않은 오류·실패 경로:

- malformed 또는 wrong-sequence DISARM 거부 뒤 active output 처리
- UART RX overflow/desync 중 즉시 stop 정책
- command-timeout event-to-PWM-zero latency
- `Error_Handler()` 또는 software fault event-to-PWM-zero latency
- reset edge부터 boot-safe output까지의 전체 window
- MDD10A나 motor의 electrical/mechanical failure

## Safety Invariant 확인

- `DISARM` 뒤 두 PWM은 inactive다.
- 두 DIR은 safe LOW로 수렴한다.
- ACK 전 이미 PWM이 멈춘다.
- 캡처 남은 약 2.712088 s 동안 ARM 없이 PWM이 재개되지 않는다.
- 최종 UART telemetry는 `DISARMED`, `vx=0`, `w=0`을 유지한다.
- STM32가 실제 motor-output permission의 최종 authority로 남는다.

## Evidence

- [Raw sigrok capture](../../assets/captures/logic_analyzer/2026-08-04_stm32_disarm_active_pwm_stop_pass.sr)
- [PulseView session](../../assets/captures/logic_analyzer/2026-08-04_stm32_disarm_active_pwm_stop_pass.pvs)
- [DISARM RX and PWM stop overview](../../assets/captures/logic_analyzer/2026-08-04_stm32_disarm_rx_pwm_stop_before_ack_pass.png)
- [PWM stop before ACK detail](../../assets/captures/logic_analyzer/2026-08-04_stm32_disarm_pwm_stop_before_ack_detail.png)
- [ESP32 UART raw monitor log](../../assets/logs/esp32_uart_bridge/2026-08-04_uart_disarm_active_pwm_stop_pass.txt)
- [Executable measurement procedure](../../02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md)

| Evidence | SHA-256 |
| --- | --- |
| `.sr` | `1955e13983258de3e923a6db10c00639ad50259131e83e6a94f134fc533eed76` |
| `.pvs` | `7ea2376dfa3dd27e4f204521ee5c259c50d8e85dd6bfade021663864ac48800e` |
| overview PNG | `548824acf219623075d167b667a32feb05859964d5c8305c49a12ddf4fc8283a` |
| detail PNG | `64d5a94ba4a340954db4bf5c5397dc89d8bdcdc501f8a779c560924c00e3ec09` |
| UART log | `4c99602796d1e25ba7fd3647b9cd8109e251525b2db4706bd5c9c312f82f4631` |

## 가능한 다른 계측 설계와 Trade-off

- Dedicated firmware marker는 parser acceptance 시점을 더 직접 표시할 수 있지만
  시험용 source와 pin이 추가된다. 이번 방법은 실제 UART wire를 기준으로 해
  end-to-end input timing을 보존한다.
- Sample rate를 12~24 MHz로 높이면 양자화 오차가 줄지만 5초 capture buffer가
  커진다. 4 MHz는 20 kHz PWM과 115200 baud UART를 동시에 해석하고 첫 baseline을
  얻기에 충분했다.
- Oscilloscope로 MDD10A output/current까지 계측하면 power-stage latency를 볼 수
  있지만 logic analyzer와 다른 전압·접지 안전 절차가 필요하다. 이 자료를 그
  결과로 대체하지 않는다.

## 남은 검증과 PASS 기준

1. 완료된 all-hooks-`0U` source, contract `15/15`, build와 별도 observed safe UART runtime evidence를 보존한다.
2. Exact image/setup provenance와 external-reset-marker motor-pin capture를 별도 evidence로 닫는다.
3. 마지막 valid CMD frame과 PWM을 함께 캡처해 configured timeout 이후 bounded
   loop delay 안에 PWM이 멈추고 old command가 재적용되지 않음을 확인한다.
4. Dedicated marker 또는 분리된 debounced event로 software-fault latency와 latch를
   확인한다.
5. 외부 reset marker와 네 motor-control pin을 함께 기록해 전체 boot window를
   확인한다.
6. 별도 안전 절차와 계측기로 MDD10A powered/no-motor, Physical E-stop, actual motor
   stop을 단계별 검증한다.
