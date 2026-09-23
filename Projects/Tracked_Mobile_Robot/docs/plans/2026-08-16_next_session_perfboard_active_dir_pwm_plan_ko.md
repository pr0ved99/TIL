# 다음 세션: Final Perfboard Active DIR/PWM 검증 계획

작성일: 2026-08-16
예상 소요: 문제 없을 때 45~60분
완료일: 2026-08-18
상태: `COMPLETE — motor-disconnected MDD10A-input scope`

## 목적

영구 만능기판의 `STM32 -> R9~R12/J5 -> MDD10A` 경로가 부팅·리셋 중 LOW를 유지하는
것뿐 아니라, 실제 `DIR1/PWM1/DIR2/PWM2` active 신호도 올바르게 전달하는지 motor를
분리한 상태에서 확인한다.

이 시험은 다음을 검증한다.

- final perfboard의 네 signal net과 common GND가 active 상태에서도 정상이다.
- 두 PWM이 제조사 범위 안의 nominal 19 kHz/10%로 MDD10A input까지 도달한다.
- 각 DIR level과 MDD10A A/B LED 선택이 일치한다.
- 시험 firmware를 제거한 뒤 네 신호가 다시 all-LOW가 된다.

이 시험은 실제 motor 회전, motor current, vehicle 좌우/전진 방향 또는 Physical E-stop을
검증하지 않는다.

## 현재 재개 기준

- `MOTOR_OUTPUT_PIN_TEST_ENABLED = 0U`
- `MOTOR_FAULT_INJECTION_TEST_ENABLED = 0U`
- `UART_MVP_OUTPUT_TEST_ENABLED = 0U`
- Permanent R9~R12/5-Net continuity, power-up/NRST all-LOW: PASS
- Board power/back-power: PASS
- 마지막 보고 상태: XL4015 input OFF 후 NUCLEO `E5V/3V3`, ESP32 `5V/3V3` 모두 0 V
- 마지막 보고 NUCLEO jumper: `JP5=PWR-E5V`, `JP1=open`; 실제 상태는 시작 전에 재확인
- Actual motor test: 아직 금지

## 1. 시작 전 무전원 확인 — 5~10분

1. XL4015 input switch OFF, 모든 USB와 LiPo/MDD10A power를 분리한다.
2. NUCLEO와 ESP32의 5 V/3.3 V rail이 0 V인지 확인한다.
3. `M1A/M1B/M2A/M2B`에 motor가 연결되지 않았는지 직접 확인한다.
4. 만능기판의 J5 5-Net, R9~R12, GND와 MDD10A header 방향을 육안 확인한다.
5. Logic analyzer GND를 circuit common GND에 연결한다.

중지 조건:

- motor terminal에 motor 또는 다른 load가 연결돼 있음
- 5 V/3.3 V rail이 0 V로 내려가지 않음
- 배선의 피복 손상, 풀린 strand, GND 단선 또는 신호 간 접촉이 보임

## 2. 시험 전원 구성 — 5분

이번 시험에서는 ESP32와 XL4015 logic output을 사용하지 않는다.

1. XL4015 #1 output을 NUCLEO/ESP32에서 분리한다.
2. 전원이 0 V인 상태에서 NUCLEO `JP5`를 `PWR-U5V`로 되돌리고 `JP1=open`을 확인한다.
3. NUCLEO는 ST-LINK USB로 공급한다.
4. MDD10A는 기존 fuse/main-switch 경로의 12 V를 사용한다.
5. NUCLEO와 MDD10A는 만능기판의 `DIR1/PWM1/DIR2/PWM2/GND` 5선으로만 연결한다.
6. Logic analyzer probe는 MDD10A input-side에서 다음과 같이 연결한다.

```text
D0 = DIR1
D1 = PWM1
D2 = DIR2
D3 = PWM2
GND = MDD10A/NUCLEO common GND
```

USB와 XL4015 5 V를 동시에 NUCLEO에 공급하지 않는다.

## 3. Controlled test firmware — 5~10분

`03_Firmware/stm32_uart_mvp/Core/Src/main.c`에서 시험 중에만 다음과 같이 설정한다.

```c
#define MOTOR_OUTPUT_PIN_TEST_ENABLED       1U
#define MOTOR_FAULT_INJECTION_TEST_ENABLED  0U
```

`uart_mvp_protocol.c`의 `UART_MVP_OUTPUT_TEST_ENABLED`는 `0U`를 유지한다.

STM32 Debug build `0 errors / 0 warnings`를 확인하고 NUCLEO에 flash한다. 이 상태는
controlled test image이며 최종 상태가 아니다.

## 4. Final perfboard active 6-step — 15~20분

Logic analyzer 설정:

```text
Sample rate = 1 MHz
Samples     = 5 M
Capture     = 5 s
```

한 번에 급히 여섯 번 누르지 않고 두 capture로 나눈다.

### Capture A

1. acquisition 시작
2. B1 1회: CH1 10%, DIR1 LOW
3. 약 0.5~1초 뒤 B1 2회: CH1 10%, DIR1 HIGH
4. 약 0.5~1초 뒤 B1 3회: all stop

### Capture B

1. acquisition 시작
2. B1 4회: CH2 10%, DIR2 LOW
3. 약 0.5~1초 뒤 B1 5회: CH2 10%, DIR2 HIGH
4. 약 0.5~1초 뒤 B1 6회: all stop, state counter reset

예상 결과:

| Step | DIR1 | PWM1 | DIR2 | PWM2 | MDD10A LED |
| --- | --- | --- | --- | --- | --- |
| Initial | LOW | LOW | LOW | LOW | all off |
| 1 | LOW | 약 19 kHz/10% | LOW | LOW | M1A |
| 2 | HIGH | 약 19 kHz/10% | LOW | LOW | M1B |
| 3 | LOW | LOW | LOW | LOW | all off |
| 4 | LOW | LOW | LOW | 약 19 kHz/10% | M2A |
| 5 | LOW | LOW | HIGH | 약 19 kHz/10% | M2B |
| 6 | LOW | LOW | LOW | LOW | all off |

PASS 기준:

- PWM period `52.1~53.2 us` 또는 `18.8~19.2 kHz`, 그리고 제조사 상한 `20 kHz` 이하
- HIGH time `4.7~5.3 us` 또는 duty `9.5~10.5%`
- DIR 변경 전후 active PWM 사이 LOW gap가 각각 최소 1 ms
- 비활성 channel PWM은 LOW
- MDD10A LED 순서 `M1A -> M1B -> OFF -> M2A -> M2B -> OFF`
- 예상하지 않은 pulse, 동시 channel 출력, 발열, 냄새 또는 이상음 없음

즉시 중지 조건:

- idle 또는 stop 단계에서 PWM pulse가 계속됨
- 예상과 다른 channel/방향 LED가 켜짐
- 두 방향 LED가 동시에 켜지거나 MDD10A가 발열함
- 파형이 3.3 V logic으로 정상 인식되지 않거나 GND 기준이 흔들림

## 5. 정상 firmware 복구 — 10분

1. MDD10A main switch를 OFF한다.
2. `MOTOR_OUTPUT_PIN_TEST_ENABLED`를 다시 `0U`로 복구한다.
3. 세 controlled hook이 모두 `0U`인지 검색한다.
4. STM32 full build `0 errors / 0 warnings` 후 다시 flash한다.
5. Motor는 계속 분리한 채 MDD10A를 켜고 모든 output LED가 OFF인지 확인한다.
6. MDD10A input-side D0~D3를 5초 capture해 전 구간 all-LOW인지 확인한다.

최종 PASS는 active 6-step만으로 끝나지 않는다. `hook 0U + safe rebuild/reflash + final
all-LOW`가 함께 있어야 한다.

## 6. 증빙과 종료 — 5~10분

권장 파일명:

```text
YYYY-MM-DD_perfboard_active_dir_pwm_capture_a_steps1to3.sr
YYYY-MM-DD_perfboard_active_dir_pwm_capture_b_steps4to6.sr
YYYY-MM-DD_perfboard_hook0_final_all_low.sr
```

원본 `.sr`, STM32 build/flash 결과, MDD10A LED 관찰과 실제 probe mapping을 progress와
hardware validation 문서에 기록한다.

## 이 시험 다음 순서

```text
Final perfboard active DIR/PWM + hook-0 restore PASS
-> Physical E-stop component/continuity/T-ESTOP-001~005
-> lifted single-motor 5~10% no-load test
```

K1/F1/main-wire 선정은 MG540 current 자료 또는 승인된 current-limited characterization가
확보될 때까지 별도의 blocked item으로 유지한다.

## 완료 결과

2026-08-18에 WHEELTEC 회신의 PWM 범위 `5~20 kHz`를 적용했다. 기존 nominal 20 kHz
baseline이 평균 약 `20.054 kHz`로 상한을 근소하게 넘어 TIM4 period를 `4420`으로 바꾸고
nominal 19 kHz로 확정했다.

- CH1: `19.049003 kHz`, duty `10.0138%`, pre/post DIR LOW `2.017/2.020 ms`
- CH2: `19.057518 kHz`, duty `10.0030%`, pre/post DIR LOW `2.006/2.029 ms`
- Inactive channel 및 initial/final: all LOW
- MDD10A LED: `M1A -> M1B -> OFF -> M2A -> M2B -> OFF`
- Safe restore: 모든 hook `0U`, contract `15/15`, final 5 s D0~D3 all-LOW

상세 판정과 raw capture hash는
[`../verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md`](../verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md)에 보존한다.

WHEELTEC 회신으로 rated `1.44 A`, stall `9 A`를 확보했지만, K1/F1/main wire의 최종
선정에는 two-motor current envelope, DC motor-load make/break, fuse time-current와 thermal
coordination이 필요하다. 따라서 blocker는 `motor data 없음`에서 `계산·부품 정격 검토
미완료`로 변경한다.
