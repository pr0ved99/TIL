# Motor Driver Selection Comparison

## 목적

이 문서는 첫 drivetrain MVP에서 BTS7960 대신 MDD10A를 선택하게 된 과정을 정리한다.

목표는 BTS7960 검토 흔적을 지우는 것이 아니라, 실제 프로젝트 조건을 기준으로 왜 MDD10A가 더 적합한지
보여주는 것이다. 포트폴리오 관점에서는 부품이 바뀐 사실보다, 바뀐 이유와 그에 따른 firmware, wiring,
validation 영향이 더 중요하다.

## 결론

현재 first drivetrain path는 MDD10A다.

```text
이전 검토: BTS7960 dual-PWM H-bridge module x2
현재 결정: MDD10A dual-channel PWM + DIR driver x1
```

BTS7960은 superseded decision으로 남긴다. 즉, 잘못된 선택이었다기보다 다음 이유로 첫 MVP에서는
MDD10A보다 우선순위가 낮아진 후보로 기록한다.

- 모터 2개를 위해 BTS7960 module 2개가 필요하다.
- STM32 PWM channel 요구량이 2개에서 4개로 늘어난다.
- `RPWM/LPWM/R_EN/L_EN` 배선과 reset-safe enable 처리가 늘어난다.
- Dual-PWM mutual exclusion을 firmware에서 계속 강제해야 한다.
- 현재 보유한 MDD10A는 2채널을 한 보드에서 처리하고 3.3 V logic input을 공식적으로 지원한다.

## 비교 표

| 항목 | BTS7960 path | MDD10A path | 프로젝트 판단 |
| --- | --- | --- | --- |
| 보드 구성 | 모터당 BTS7960 module 1개, 총 2개 | MDD10A 1개로 좌/우 모터 2개 | MDD10A가 배선과 bench setup이 단순함 |
| 제어 방식 | 모터당 `RPWM` + `LPWM` + enable | 모터당 `PWM` + `DIR` | MDD10A가 STM32 output 수를 줄임 |
| STM32 PWM 수요 | 좌/우 합계 PWM 4개 | 좌/우 합계 PWM 2개 + DIR GPIO 2개 | MDD10A가 timer allocation 부담이 작음 |
| 방향 전환 안전 | inactive PWM을 0으로 만들고 active PWM만 사용 | PWM을 0으로 낮춘 뒤 DIR 변경 | 둘 다 firmware safety 필요 |
| Enable/safety | enable pin을 별도로 관리 가능 | 별도 enable pin 없음, PWM zero와 power path가 기본 차단 | MDD10A는 optional power gate 검토 여지 있음 |
| Reset 기본 상태 | enable pull-down 설계 필요 | PWM pin safe default와 optional pull-down 필요 | 둘 다 boot-safe 검증 필요 |
| Logic 호환성 | module별 3.3 V 인식 확인 필요 | MDD10A는 3.3 V / 5 V logic input 지원 | MDD10A가 초기 STM32 연결 리스크가 낮음 |
| 검증 복잡도 | module 2개, enable, dual PWM 상호 배제 확인 | channel 2개, PWM/DIR mapping 확인 | MDD10A가 첫 no-load test까지 짧음 |
| 확장성 | 개별 module 교체 쉬움 | 한 보드에 dual channel 통합 | 첫 MVP는 MDD10A가 실용적 |
| 현재 상태 | 검토 기록으로 보존 | first drivetrain MVP active decision | MDD10A 선택 |

## BTS7960을 먼저 검토했던 이유

BTS7960은 처음에 충분히 자연스러운 후보였다.

- H-bridge 동작과 dual-PWM 제어를 학습하기 좋다.
- 모터 1개당 독립 module을 두면 좌/우 channel을 물리적으로 분리하기 쉽다.
- TB6612FNG급 소형 driver보다 current margin을 더 크게 잡을 수 있다.
- WHEELTEC 참고 코드의 dual-PWM motor output 구조와 개념적으로 연결된다.

따라서 BTS7960 검토는 삭제할 내용이 아니라 설계 탐색의 일부다.

다만 현재 프로젝트의 첫 목표는 "복잡한 motor-driver topology를 비교 실험하는 것"이 아니라,
STM32 기반 low-level drivetrain을 빠르고 안전하게 bring-up하는 것이다. 이 목표에서는 MDD10A가 더
간결하다.

## MDD10A를 선택한 이유

MDD10A는 첫 MVP 조건에 더 잘 맞는다.

1. 좌/우 모터 2개를 한 보드에서 처리한다.
2. STM32 출력은 `PWM_L`, `DIR_L`, `PWM_R`, `DIR_R`로 충분하다.
3. 기존 pin 후보인 PB6/PB7 PWM, PC8/PC9 DIR 구조와 맞는다.
4. 모터당 dual-PWM mutual exclusion 대신 direction-change rule만 명확히 지키면 된다.
5. MDD10A logic input은 STM32 3.3 V GPIO와 직접 연결하기 쉽다.
6. Hardware validation 문서를 `MDD10A visual/DMM -> power bring-up -> PWM/DIR logic -> no-load motor` 순서로 단순화할 수 있다.

## Firmware 영향

BTS7960 path였다면 motor output abstraction은 다음에 가까웠다.

```text
left_rpwm
left_lpwm
right_rpwm
right_lpwm
left_enable
right_enable
```

MDD10A path에서는 다음이 canonical output이다.

```text
left_pwm
left_dir
right_pwm
right_dir
```

공통으로 유지되는 추상화:

- signed motor command
- output permission
- command timeout
- PWM clamp
- ramp limit
- encoder sign validation
- low-voltage stop

바뀌는 low-level mapping:

```text
signed command > 0  -> PWM = duty, DIR = forward mapping
signed command < 0  -> PWM = duty, DIR = reverse mapping
signed command == 0 -> PWM = 0
unsafe state        -> PWM = 0
```

방향 전환 규칙:

```text
if direction must change:
    ramp PWM to 0
    change DIR
    apply limited PWM
```

## Wiring 영향

MDD10A 기준 first wiring contract:

```text
STM32 PB6 / TIM4_CH1 -> MDD10A PWM1
STM32 PC8            -> MDD10A DIR1
STM32 PB7 / TIM4_CH2 -> MDD10A PWM2
STM32 PC9            -> MDD10A DIR2
STM32 GND            -> MDD10A GND

3S LiPo + -> fuse -> switch -> MDD10A POWER+
3S LiPo - ------------------> MDD10A POWER-

Left motor  -> MDD10A M1A/M1B
Right motor -> MDD10A M2A/M2B
```

최종 left/right channel mapping은 bench wiring 후 확정한다. 문서에서는 `PWM1/DIR1 = left`를 후보로
두되, 실제 motor direction과 encoder sign test 결과로 결정한다.

## Validation 영향

MDD10A 선택 후 hardware validation 순서는 다음으로 고정한다.

1. `00_MDD10A_Visual_and_Multimeter_Inspection.md`
2. `01_Power_Bringup_Checklist.md`
3. `02_Buck_Converter_Calibration_Log.md`
4. `03_MDD10A_Logic_Input_Test.md`
5. `04_Encoder_Signal_Safety_Test.md`
6. `05_First_Motor_No_Load_Test.md`
7. `06_Left_Right_Drivetrain_Test.md`

BTS7960 전용 logic test 문서는 현재 active validation path가 아니다.

## Decision Record

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-06-04 이전 | BTS7960-class dual-PWM path 검토 | WHEELTEC dual-PWM 구조와 H-bridge 학습 흐름이 자연스러웠음 |
| 2026-06-08 | MDD10A를 first drivetrain path로 변경 | 보유 부품, 2채널 통합, STM32 pin 부담 감소, 3.3 V logic 지원, 검증 단순화 |
| 현재 | BTS7960은 superseded alternative로 보존 | 설계 변화 근거와 비교 대상으로 유지 |

## Final Rule

현재 프로젝트 문서에서 motor driver를 active path로 말할 때는 MDD10A를 기준으로 한다.

BTS7960은 다음 맥락에서만 사용한다.

- 이전 검토 기록
- 설계 대안 비교
- 왜 MDD10A를 선택했는지 설명하는 변화 과정
- 나중에 MDD10A 전류 여유가 부족할 때 재검토할 후보군
