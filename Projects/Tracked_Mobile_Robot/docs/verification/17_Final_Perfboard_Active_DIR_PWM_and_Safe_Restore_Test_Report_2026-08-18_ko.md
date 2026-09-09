# Final Perfboard Active DIR/PWM and Safe-Restore Test Report

- 시험일: 2026-08-18
- 대상: NUCLEO-F446RE -> permanent perfboard R9~R12/J5 -> MDD10A logic input
- 결과: `PASS — motor-disconnected MDD10A-input scope`
- 전체 drivetrain release: `PARTIAL`

## 1. 목적과 증거 경계

영구 만능기판에 실장한 네 개의 `10 kOhm` pull-down과 5선 logic harness가 기본 LOW만
유지하는 것이 아니라, controlled 6-step의 active DIR/PWM도 MDD10A input까지 정확히
전달하는지 확인했다. 시험이 끝난 뒤에는 모든 controlled hook을 `0U`로 복구하고 5초
all-LOW를 다시 확인했다.

이번 시험에 motor는 연결하지 않았다. 따라서 다음은 증명하지 않는다.

- 실제 motor 회전 방향, 속도, 전류와 발열
- MDD10A power-stage output 또는 motor stop latency
- vehicle left/right channel mapping
- Physical E-stop의 motor-energy 차단과 no-auto-restart

## 2. 기준 변경: nominal 20 kHz에서 19 kHz로

WHEELTEC 기술지원은 이 motor의 PWM 범위를 `5~20 kHz`로 회신했다. 기존 TIM4 설정은
nominal 20 kHz였지만 baseline 재측정 평균이 약 `20.054 kHz`로 상한을 근소하게 넘었다.
이는 MCU timer와 logic-analyzer clock tolerance 안의 작은 차이지만, 제조사 상한 밖의
운용점을 의도적으로 유지할 이유가 없으므로 margin을 두고 nominal 19 kHz로 내렸다.

최종 CubeMX/generated setting:

```text
TIM4 prescaler = 0
TIM4 period    = 4420
Nominal PWM    = 84 MHz / (4420 + 1) = about 19.0002 kHz
```

19 kHz standalone 재측정은 `19.056238 kHz`, period `52.476253 us`, HIGH
`5.248300 us`, duty `10.001285%`였다.

## 3. 물리 구성과 계측 설정

```text
D0 = DIR1
D1 = PWM1
D2 = DIR2
D3 = PWM2
GND = NUCLEO/MDD10A common GND
```

- Probe point: MDD10A input-side after permanent perfboard path
- MDD10A: powered through existing fused/switched path
- Motor terminals: disconnected
- Active captures: 1 MHz, 5 M samples, 5 s
- Controlled source: `MOTOR_OUTPUT_PIN_TEST_ENABLED=1U`, other hooks `0U`

## 4. Active 6-step 결과

### Capture A — Channel 1

| Check | Measured | Result |
| --- | --- | --- |
| PWM1 average frequency | 19.049003 kHz | PASS |
| PWM1 average period | 52.496186 us | PASS |
| PWM1 HIGH | 5.256869 us | PASS |
| PWM1 duty | 10.0138% | PASS |
| DIR1 HIGH interval | 2.062860~3.102293 s | PASS |
| PWM-zero before DIR transition | 2.017 ms | PASS, >=1 ms |
| PWM-zero after DIR transition | 2.020 ms | PASS, >=1 ms |
| Inactive D2/D3 | all LOW | PASS |
| Initial/final state | all LOW | PASS |

### Capture B — Channel 2

| Check | Measured | Result |
| --- | --- | --- |
| PWM2 average frequency | 19.057518 kHz | PASS |
| PWM2 average period | 52.472731 us | PASS |
| PWM2 HIGH | 5.248824 us | PASS |
| PWM2 duty | 10.0030% | PASS |
| DIR2 HIGH interval | 2.030958~3.019176 s | PASS |
| PWM-zero before DIR transition | 2.006 ms | PASS, >=1 ms |
| PWM-zero after DIR transition | 2.029 ms | PASS, >=1 ms |
| Inactive D0/D1 | all LOW | PASS |
| Initial/final state | all LOW | PASS |

사용자 관찰 기준 MDD10A LED 순서도 계획한
`M1A -> M1B -> OFF -> M2A -> M2B -> OFF`와 일치했고 이상 발열·냄새·소음은 없었다.

## 5. Safe restore

시험 뒤 다음 hook이 모두 `0U`인 실제 source를 재확인했다.

```text
MOTOR_OUTPUT_PIN_TEST_ENABLED       0U
MOTOR_FAULT_INJECTION_TEST_ENABLED  0U
UART_MVP_OUTPUT_TEST_ENABLED        0U
```

- 사용자 수행 STM32 build: `0 errors / 0 warnings`
- 사용자 수행 flash/run: PASS
- B1 반복 입력: D0~D3 output 없음
- Final raw capture: 1 MHz, 5 M samples, D0~D3 HIGH sample `0`, transition `0`
- Host contract test: `15/15 PASS`

Build/flash는 사용자가 관찰한 session 결과이고, 이번 기록에는 flashed ELF hash를
내장한 transcript가 없다. Raw logic capture는 최종 전기 동작을 증명하지만 특정 ELF와의
암호학적 linkage까지 증명하지는 않는다.

## 6. Raw evidence와 SHA-256

| Evidence | SHA-256 |
| --- | --- |
| `2026-08-18_perfboard_pwm20k_baseline_remeasurement.sr` | `BF960D9123BE7DF4B9EAA94880EA995A0D6230F51129480590CA311F3B812817` |
| `2026-08-18_perfboard_pwm19k_final_remeasurement.sr` | `8842221E0D3AE167C36C65EFBFD7F0FD64C94A4B83706392D2F531B3324E23E8` |
| `2026-08-18_perfboard_pwm19k_active_6step_capture_A.sr` | `5795153918B66DFAFE84E158747A936159B4C0650C911F81DA279AE6ED4C3662` |
| `2026-08-18_perfboard_pwm19k_active_6step_capture_B.sr` | `8E6D9EF688D924124D2839CF838839239A691FFD274986932218AF02EAE7B6E3` |
| `2026-08-18_perfboard_pwm19k_hook0_final_all_low.sr` | `4964812C2FFDD07EC788E993CF226D130EC1E347239941E3C54EB6119271D76D` |

경로: `assets/captures/logic_analyzer/`

## 7. 판정과 다음 Gate

Final perfboard 5-Net은 boot/reset default LOW, active 6-step, direction-change dead interval,
inactive-channel LOW와 restored safe image all-LOW를 모두 통과했다. 이 범위는
`PASS — motor-disconnected MDD10A-input scope`로 닫는다.

다음 직렬 Gate:

```text
Physical E-stop component/continuity and T-ESTOP-001~005
-> lifted single motor 5~10% with current/heat/noise observation
-> powered encoder-noise and actual stop/no-auto-restart
```
