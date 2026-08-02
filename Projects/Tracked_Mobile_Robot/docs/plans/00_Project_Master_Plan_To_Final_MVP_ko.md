# Project Master Plan To Final MVP

## 문서 기준

- Revision: 2026-08-03 logic-analyzer PWM/direction timing sub-gate checkpoint
- 현재 실행 위치: `G3/G4A PARTIAL`, `G5 encoder PARTIAL`, `G6 encoder mapping subtest PASS`; 양 채널 actual PWM `20.1005 kHz`, duty 약 `10.05%`와 DIR 전·후 PWM-zero 여유 `1 ms 이상`을 확인해 파형·방향 timing 하위 게이트는 `PASS`했다. 전체 motor-output gate는 active DISARM/timeout/software-fault shutdown latency, hook-off safe image board 재플래시와 reset-marker boot 회귀, Physical E-stop 및 실제 motor 시험이 남아 `PARTIAL`이다.
- 기구 제작 상태: Rev A release 준비 완료, 주문 접수 전
- 요구사항·검증 정본: [`../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)

이 문서는 Tracked Mobile Robot 프로젝트의 최신 전체 실행 로드맵이다. 날짜별 progress log는 실제로 수행한 일을 기록하고, 이 문서는 다음에 무엇을 해야 하며 어떤 증거가 있어야 다음 단계로 갈 수 있는지를 정의한다.

## 최종 MVP 종료선

1차 종료선은 완성형 자율주행 로봇이 아니다.

```text
STM32 기반 하위 구동 플랫폼이
PC 또는 ESP32의 속도 명령을 받아
안전 상태머신을 거쳐 좌우 모터를 제어하고
엔코더 기반 속도·이동량 telemetry를 생성하며
저속 전진·후진·제자리 회전과 1 m 측정 시험을 통과하고
요구사항부터 실제 증거까지 추적 가능한 상태
```

즉, 최종 MVP는 다음 두 가지가 동시에 완성돼야 한다.

1. 실제로 안전하게 움직이는 궤도형 하위 플랫폼
2. 설계 결정과 검증 결과를 재현할 수 있는 embedded system integration evidence

## MVP 범위 고정

### 이번 종료선의 MUST

- 3S LiPo, fuse, main switch와 검증된 5 V 전원 경로
- STM32가 최종 motor output authority인 안전 상태머신
- PC와 ESP32가 공통 UART protocol을 사용하는 command source
- MDD10A 좌우 PWM/DIR 출력
- boot/reset/DISARM/timeout/fault의 실제 PWM zero
- 방향 변경 전 PWM zero
- encoder A/B 입력 안전성, signed count와 speed telemetry
- lifted/no-load 단일 motor 시험
- 좌우 궤도 저속 전진, 후진과 제자리 회전
- 1 m 직진 실제 거리와 encoder 추정 거리 오차 기록
- 어댑터 플레이트 fit, 절연, 접근성과 배선 경로 검증
- README, 로그, 사진과 영상의 요구사항-증거 연결

### 이번 종료선을 막지 않는 후속 범위

- BNO08x IMU 통합
- closed-loop PID 속도 제어 고도화
- FreeRTOS task architecture 전환
- CAN transceiver와 command/telemetry 통합
- HAL-to-LL migration
- ROS 2 bridge, LiDAR, SLAM과 Nav2

이 항목들은 최종 MVP가 통과된 뒤 별도 V-cycle로 진행한다.

## Lightweight V-model 적용

이 프로젝트는 인증용 개발 절차를 주장하지 않는다. 대신 개인 프로젝트 규모의 경량 V-model로 요구사항, 설계와 시험의 대응을 유지한다.

```text
최종 MVP 목표·사용자 요구                 <-> G7 시스템 인수시험
  시스템 요구사항                         <-> G6 주행·안전 통합시험
    아키텍처·인터페이스 설계               <-> G4~G5 서브시스템 통합시험
      핀·회로·펌웨어·기구 상세설계         <-> G2~G3 단위·신호·치수 시험
                       구현
```

| 왼쪽 설계 단계 | 프로젝트 산출물 | 오른쪽 검증 단계 |
| --- | --- | --- |
| 목표와 사용 시나리오 | charter, `MVP-001~012` | 최종 기본 동작, 1 m, 문서 인수시험 |
| 시스템 요구사항 | UART, power, mechanical, motor, encoder, drive requirement | fault stop, drivetrain, telemetry 시험 |
| 아키텍처와 interface | controller ownership, pin map, UART, power, MDD10A contract | PC/ESP32-STM32, STM32-MDD10A, encoder 통합시험 |
| 상세 설계 | CubeMX pin/timer, motor-output module, CAD Rev, harness | 핀 파형, DMM, 치수와 fit 시험 |
| 구현 | firmware, wiring, fabricated plate | build/flash 뒤 실제 계측과 동작 증거 |

적용 규칙:

1. 각 `MUST` 요구사항에는 acceptance criteria와 Test ID가 있어야 한다.
2. `Build Successful`은 구현 확인이지 하드웨어 시험 통과가 아니다.
3. command 변수 zero와 실제 PWM output zero를 별도 요구사항으로 검증한다.
4. CAD 1:1 출력 PASS와 제작품 fit PASS를 구분한다.
5. 다음 Gate는 선행 Gate의 evidence가 있어야 시작한다.
6. 설계가 바뀌면 영향받는 requirement, test와 evidence를 함께 갱신한다.

## 2026-08-03 현재 기준선

| Workstream | 현재 상태 | 판정 근거 | 다음 행동 |
| --- | --- | --- | --- |
| PC-first STM32 UART MVP | `PASS` | requirements, matrix, CSV, screenshots, test report | baseline 보존 |
| ESP32-STM32 UART bridge | `PASS` | loopback, PING/PONG, structured TEL, scripted safety, timeout-zero raw log | baseline 보존 |
| MDD10A 무전원 검사 | `PASS` | visual/DMM hard-short inspection | logic input 전 재확인 |
| Fuse/switch power path | `PASS` | OFF 0 V, ON 12.49 V와 wiring evidence | 실제 통합 harness에서 재검증 |
| XL4015 x2 | `CONDITIONAL PASS` | 약 1 A 5분, 약 1.8 A 3분과 회복 전압 기록 | board power/back-power policy 결정 |
| Adapter plate Rev A release | `PASS` | A4 1:1 user comparison, vector/scale preflight, release hash | 업체 주문 접수 |
| Adapter plate fabricated fit | `BLOCKED` | 제작품 미입고 | 입고 후 fit check |
| STM32 PWM/DIR | `PARTIAL` | PB6/PB7 `20.1005 kHz`/약 `10.05%`, PC8/PC9 DIR, direction 전·후 PWM-zero `>=1 ms` 하위 게이트 PASS | active DISARM -> timeout -> software-fault shutdown latency; final safe reflash/reset-marker boot; Physical E-stop |
| MDD10A logic input | `PARTIAL` | powered/no-motor 6-step, timeout/DISARM LED all-off, fault latch 네 pin 0 V, actual MCU output waveform/timing PASS | active shutdown latency, driver output/actual motor stop, Physical E-stop closure |
| Encoder | `PARTIAL` | conditioning, dual count/CPS/mRPM, 1560 counts/rev와 encoder-side A=right/TIM5·B=left/TIM3 forward-positive PASS | powered-noise, external tachometer/wheel-speed 검증 |
| First motor no-load | `NOT TESTED` | motor, duty, current data 없음 | 앞선 안전 Gate 후 실행 |
| Dual drivetrain / chassis | `NOT TESTED` | MDD10A powered channel-to-side mapping과 주행 evidence 없음 | single motor/encoder 후 실행 |

정적 motor-output, powered/no-motor direction 회귀, timeout/DISARM LED shutdown, software fault output-zero/latch, actual PWM frequency/duty·direction settle과 encoder-side vehicle-frame sign까지 진행됐지만 MDD10A의 실제 좌우 motor 대응, active shutdown exact latency, reset-marker boot, Physical E-stop과 실제 motor 회전은 아직 검증하지 않았다. 따라서 진행률 숫자보다 Gate 상태를 기준으로 판단한다.

## Gate 로드맵

### G0. MVP 요구사항 기준선

목표:

- 이번 MVP의 MUST와 후속 확장을 분리한다.
- requirement, design, Test ID와 evidence 경로를 연결한다.

Exit criteria:

- `MVP-001~012`와 하위 요구사항이 verification matrix에 존재한다.
- actual PWM zero, fabricated fit처럼 기존에 혼동되던 검증 범위가 분리돼 있다.

상태:

```text
PASS - 2026-07-24 V-model refresh
```

### G1. UART command and safety baseline

목표:

- PC와 ESP32 command path에서 STM32 parser와 safety authority를 검증한다.

검증된 항목:

- periodic TEL
- PING/PONG
- ACK/ERR와 sequence
- CMD before ARM rejection
- ARM, valid CMD와 invalid range rejection
- command timeout 후 command variable zero
- DISARM과 final DISARMED state

Exit criteria:

- PC-first UART matrix가 모두 PASS다.
- ESP32 scripted safety sequence와 raw evidence가 있다.

상태:

```text
PASS - 완료된 baseline은 문제가 재발하지 않는 한 다시 구현하지 않는다.
```

### G2A. Power component baseline

목표:

- motor power 투입 전 전원 구성품과 경로를 검증한다.

완료:

- MDD10A visual/DMM hard-short check
- 3S LiPo polarity
- fuse-before-switch path
- switch OFF 0 V / ON normal voltage
- XL4015 x2 no-load 5.03 V 조정
- 약 1 A 5분과 약 1.8 A 3분 bench load 기록

남은 Exit criteria:

- STM32, ESP32와 sensor의 최종 5 V 공급 분담을 정한다.
- USB와 buck 동시 연결 시 back-powering을 막는 규칙을 정한다.
- 실제 장착 harness에서 polarity, continuity와 output voltage를 다시 확인한다.

상태:

```text
CONDITIONAL PASS - signal-only firmware 작업은 진행 가능, board power 통합은 아직 금지
```

### G2B. Mechanical release and fabricated fit

목표:

- electronics를 셰시에 안전하게 고정할 Rev A plate를 제작하고 실물 검증한다.

Release branch:

- 174 x 208.93379 mm
- acrylic 3T candidate
- nominal 3.3 mm small holes
- A4 1:1 comparison PASS
- order PDF vector and scale PASS

발주 직후 기록할 항목:

- 실제 제출 파일과 revision
- acrylic 세부 재질, kerf, 최소 hole과 공차
- 수량, 견적, 배송비/VAT, order ID와 예상 납기

입고 후 Exit criteria:

- 외곽, 두께, 주요 hole 지름과 center distance를 실측한다.
- 억지 가공이나 plate 휨 없이 chassis에 체결한다.
- universal PCB, XL4015 x2와 MDD10A를 무전원 가조립한다.
- USB·terminal 접근, spacer, 납땜면 절연과 cable path를 확인한다.
- 결과를 `PASS` 또는 Rev B 필요로 판정한다.

상태:

```text
RELEASE PASS / ORDER NOT SUBMITTED / FABRICATED FIT BLOCKED
```

### G3. STM32 PWM/DIR signal-only verification

목표:

- MDD10A와 motor power를 연결하기 전에 STM32 자체 motor-output contract를 구현·계측한다.

정적/DMM 범위는 2026-07-26에 완료했고, actual PWM/direction timing 하위 게이트는 2026-08-03에 통과했다. Active shutdown latency와 reset-marker를 포함한 최종 hook-off boot 회귀는 남아 있다.

먼저 확정할 결정:

- MDD10A channel 1/2의 차량 left/right mapping
- 첫 motor 후보
- PWM frequency: target `20 kHz`, actual `20.1005 kHz` 계측 PASS
- direction polarity와 vehicle-forward 정의

Bench-confirmed pin mapping:

| Function | Mapping |
| --- | --- |
| Channel 1 PWM | `PB6 / TIM4_CH1` |
| Channel 2 PWM | `PB7 / TIM4_CH2` |
| Channel 1 DIR | `PC8` |
| Channel 2 DIR | `PC9` |

구현 순서:

1. CubeMX에서 TIM4 CH1/CH2와 PC8/PC9의 충돌을 다시 확인한다.
2. boot 시 PWM 0과 safe DIR을 보장한다.
3. UART parser와 분리된 `motor_output` interface를 만든다.
4. 5~10% test duty cap을 적용한다.
5. `PWM 0 -> DIR 변경 -> PWM 재개` 순서를 구현한다.
6. DISARMED, timeout와 fault path가 실제 compare value를 0으로 만드는 함수를 공유하게 한다.

현재 checkpoint의 구현은 `PWM 0 -> 1 ms PWM-zero settle -> DIR 변경 -> 1 ms post-DIR settle -> PWM 재개` 순서다. 2026-08-03 motor-disconnected logic-analyzer capture에서 양 채널은 period `49.75 us`, frequency `20.1005 kHz`, high time `5.00 us`, duty 약 `10.05%`였다. Direction 전환의 PWM-zero 구간은 channel 1 pre/post `1.994/2.03875 ms`, channel 2 pre/post `1.54725/약 2.040 ms`로 모두 최소 `1 ms`를 만족했다. Sampled initial inactive interval도 확인했지만 외부 reset marker가 없어 최종 boot/reset 회귀로 확대하지 않는다.

시험 조건:

- motor 미연결
- MDD10A main power 미연결
- 가능하면 MDD10A logic input도 분리한 STM32 핀 단독 상태에서 시작
- logic analyzer 또는 oscilloscope 우선, 없으면 LED/DMM 최소 확인

Exit criteria:

- reset 직후 좌우 PWM 0
- 채널별 저 duty와 DIR 변화 확인
- direction 전환 중 PWM zero 확인
- DISARM/timeout에서 actual pin zero 확인
- build log와 measurement evidence 저장

상태:

```text
PARTIAL - static/DMM routing + 20.1005 kHz/약 10.05% PWM + direction pre/post zero >= 1 ms sub-gate PASS; active DISARM/timeout/software-fault shutdown latency와 reset-marker hook-off boot regression pending
```

### G4. Driver, power and mechanical interface integration

목표:

- 각각 검증된 STM32 signal, MDD10A, 전원 경로와 기구물을 단계적으로 연결한다.

#### G4A. MDD10A logic input

- G3가 PASS한 뒤 STM32 GND와 MDD10A logic GND를 연결한다.
- PWM1/DIR1, PWM2/DIR2 mapping을 확인한다.
- motor terminal은 비운 상태로 boot, low-duty, direction, timeout/DISARM을 시험한다.
- 예상 밖 back-power, 발열 또는 boot active PWM이 보이면 즉시 중단한다.
- 2026-07-26 battery 12.36 V, MDD10A input 12.35 V에서 powered/no-motor 6-step LED sequence를 통과했다.
- 양 채널 PWM/DIR swap을 진단·교정하고 `PB6->PWM1`, `PC8->DIR1`, `PB7->PWM2`, `PC9->DIR2`를 bench mapping으로 고정했다.
- 2026-07-29 수정된 direction-change 순서로 같은 6-step LED sequence와 final all-off를 다시 통과했다.
- 2026-07-29 임시 10%-limited UART hook으로 active timeout과 `DISARM`에서 MDD10A LED all-off를 확인했다. 당시 범위는 powered/no-motor functional scope PASS였고 actual PWM pin/waveform, fault/E-stop과 motor stop은 미검증이었다.
- 시험 뒤 UART hook을 `0U`로 복구하고 default scripted sequence 전체 all-off를 재확인했다.
- 2026-07-30 임시 dual-channel 10% button hook으로 `Error_Handler()` fault를 주입했다. MDD10A all-off, `PB6/PB7/PC8/PC9=0 V`와 reset 전 latch를 확인했다.
- 시험 뒤 `MOTOR_OUTPUT_PIN_TEST_ENABLED`와 `MOTOR_FAULT_INJECTION_TEST_ENABLED`를 모두 `0U`로 복구하고 B1 무출력을 재확인했다. Exact shutdown latency와 physical E-stop은 포함하지 않는다.
- 2026-08-03 motor-disconnected B1 six-step logic-analyzer capture에서 양 채널 `20.1005 kHz`, 약 `10.05%` PWM과 direction 전·후 PWM-zero `1 ms 이상`을 확인해 waveform/direction timing 하위 게이트를 `PASS`했다.
- 모든 temporary hook이 `0U`인 source와 STM32 Debug build 확인은 통과했지만, 2026-08-03에 ESP32 clean build를 새로 실행한 것은 아니다. Controlled latency 시험 후 STM32/ESP32 양쪽 clean build·safe image 재플래시와 reset marker를 포함한 post-flash boot no-output capture가 남아 있다.

#### G4B. Board power integration

- USB-only, buck-only와 전환 절차를 문서화한다.
- 두 전원 source가 서로 역급전하지 않는지 확인한다.
- buck terminal과 board input의 전압을 모두 측정한다.

#### G4C. Fabricated plate fit

- `02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md`를 무전원 상태로 수행한다.
- fit PASS 전에는 최종 harness 길이와 module fastener를 확정하지 않는다.

Exit criteria:

- MDD10A logic test의 active safety와 timing 항목까지 PASS
- board power/back-power policy와 측정 PASS
- fabricated plate fit와 insulation PASS
- final wiring diagram 또는 사진 기반 connection map 작성

상태:

```text
PARTIAL - G4A static routing, timeout-DISARM/software-fault functional, actual waveform/direction timing sub-gates PASS; active shutdown edge latency, reset-marker safe-image boot regression, physical E-stop, G4B와 G4C pending
```

### G5. Encoder safety and first motor no-load

목표:

- STM32 입력을 보호하면서 한쪽 motor를 lifted 상태에서 처음 구동한다.

실행 순서:

1. 사용할 motor와 encoder wire를 식별한다. `MG540-A/B`와 six-pad map은 완료했다.
2. STM32를 연결하지 않고 encoder supply와 A/B voltage를 측정한다. 15 kΩ loaded-voltage 범위는 완료했다.
3. 각 A/B에 `1 kΩ series + MCU-side 15 kΩ pull-down`을 적용한다. 두 motor 모두 conditioning node HIGH 3.06~3.07 V를 확인했다.
4. Motor power 없이 TIM3 PB4/PB5와 TIM5 PA0/PA1 dual hand-rotation count/sign을 확인한다. 두 encoder 동시 연결의 독립 count와 방향별 50회전 `1560 counts/output rev` 보정까지 완료했다.
5. 16-bit TIM3와 32-bit TIM5의 modular delta, wrap-safe 누적 count, nominal 100 ms counts/s와 signed mRPM 변환을 확인한다. Synthetic wrap/mRPM self-test, stationary와 305-row dynamic bench log까지 완료했다.
6. CPS를 production UART `TEL`의 `left_cps/right_cps`로 전달하고 ESP32 parser에서 확인한다. 독립 CW/CCW, inactive channel zero와 stop-to-zero까지 완료했다.
7. 한쪽 motor만 MDD10A에 연결하고 track/wheel을 완전히 띄운다.
8. output disabled 상태부터 확인한다.
9. 5~10% forward pulse, zero, reverse pulse를 짧게 시험한다.
10. timeout과 DISARM stop을 실제 회전 상태에서 확인한다.
11. current, heat, smell, noise와 vibration을 기록한다.

Exit criteria:

- encoder voltage가 STM32-safe로 판정된다.
- motor가 저 duty 전진·후진에 안정적으로 반응한다.
- timeout/DISARM에서 실제 motor가 정지한다.
- 과열, 과전류, 냄새와 비정상 진동이 없다.

상태:

```text
PARTIAL - encoder conditioning, dual count/sign, 50-rev 1560 scale, wrap-safe CPS/mRPM, production TEL -> ESP32와 encoder-side vehicle forward-positive mapping PASS; external tachometer/wheel-speed, powered-noise와 motor no-load pending
```

### G6. Encoder telemetry and dual drivetrain integration

목표:

- 좌우 motor와 encoder를 함께 연결해 실제 drivetrain subsystem을 완성한다.

구현·시험:

- TIM3와 TIM5 encoder mode 설정
- [x] encoder-side 좌우 signed count와 forward sign 확인
- fixed interval count delta와 CPS 또는 wheel speed 계산
- TEL에 left/right measurement 반영
- [x] A=right/TIM5, B=left/TIM3 encoder-side map 고정
- [ ] MDD10A powered channel 1/2와 실제 좌우 motor map 고정
- lifted straight, backward와 rotation
- 저속 ground straight와 rotation
- UART disconnect, timeout과 DISARM actual stop

Exit criteria:

- 좌우 independent direction과 부호가 문서와 일치한다.
- TEL에서 실제 count/speed 변화가 관찰된다.
- 저속 전진, 후진과 제자리 회전이 가능하다.
- fault 상황에서 양쪽 track이 정지한다.

상태:

```text
PARTIAL - production CPS TEL과 encoder-side A=right/TIM5, B=left/TIM3 forward-positive map PASS; MDD10A powered channel-to-side mapping과 drivetrain tests pending
```

### G7. Final MVP system acceptance

목표:

- 처음 정의한 사용자 수준의 성공 기준을 실제 chassis에서 검증한다.

필수 시험:

1. cold boot output-zero
2. PC command source basic motion
3. ESP32 command source basic motion
4. low-speed forward, backward와 in-place rotation
5. command timeout actual stop
6. DISARM actual stop
7. invalid command가 이전 safe output을 훼손하지 않음
8. UART disconnect actual stop
9. 1 m straight actual distance 대 encoder estimate
10. power, driver, motor와 wiring heat observation

Exit criteria:

- verification matrix의 모든 `MUST`가 `PASS`다.
- `CONDITIONAL PASS`, `PARTIAL`, `BLOCKED`와 `NOT TESTED`가 남아 있지 않다.
- 각 PASS에 log, photo, measurement table 또는 video index가 연결돼 있다.
- limitation과 residual risk가 기록돼 있다.

상태:

```text
PLANNED
```

### G8. Portfolio release

목표:

- 구현 범위와 시스템 통합 능력이 처음 보는 사람에게도 분명하게 보이게 한다.

필수 산출물:

- problem and goal
- 사용자 본인의 구현·검증 범위
- system architecture diagram
- power, UART, PWM/DIR와 encoder integration map
- requirement-to-evidence matrix
- build/run instructions
- short demo video 또는 GIF
- 계측값과 1 m result
- failure/debugging 사례
- limitations and next steps

Exit criteria:

- README만 읽어도 구조, 역할, 검증 결과와 한계를 이해할 수 있다.
- 면접에서 `문제 -> 설계 근거 -> 구현 -> 검증 -> 한계` 순서로 설명할 수 있다.

상태:

```text
PLANNED
```

## 제작 대기 중 병렬 실행 계획

어댑터 플레이트 납기 때문에 firmware와 signal 검증을 멈추지 않는다.

```text
Mechanical branch
Rev A order -> vendor confirmation -> fabrication -> fit check -----+
                                                               |
Control branch                                                 v
pin/frequency config -> static pin PASS -> MDD static PASS -> timing/active safety
                                                               |
Power/encoder branch                                           v
board power policy -> encoder identification/safe voltage -> final integration
```

2026-08-03 이후 우선순위:

아래 2~7은 실제 motor 활성화 전 직렬 safety chain이다. 앞 단계가 통과하기 전에는 다음 단계로 넘어가지 않는다.

1. 2026-08-03 actual `20.1005 kHz`/약 `10.05%` PWM과 direction pre/post zero `>= 1 ms` evidence, TIM3/TIM5 encoder conditioning·`1560 counts/output rev`·forward-positive mapping evidence를 회귀 기준으로 보존한다.
2. 다음 세션에서 MDD10A/motor 전원 인가 전, 현재 네 test hook `0U` source를 기준으로 STM32 safe image를 먼저 flash/run해 임시 B1 six-step image 가능성을 제거한다. 이 시작 전 복구는 발행 게이트가 아니라 벤치 안전 선행조건이다.
3. Motor-disconnected 10%-limited output에서 valid active `DISARM` frame 완료 시점부터 PB6/PB7 last active edge까지 shutdown latency를 동시 capture한다.
4. 같은 조건에서 마지막 valid CMD 완료 시점부터 configured timeout 뒤 PB6/PB7 last active edge까지 command-timeout shutdown latency를 capture한다.
5. Dedicated marker 또는 debounced event와 PB6/PB7을 함께 capture해 software-fault shutdown latency를 측정하고, button debounce와 firmware latency를 분리해 기록한다.
6. `MOTOR_OUTPUT_PIN_TEST_ENABLED`, `MOTOR_FAULT_INJECTION_TEST_ENABLED`, `UART_MVP_OUTPUT_TEST_ENABLED`, `BRIDGE_SCRIPTED_TEST_ENABLED`를 모두 `0U`로 복구한다. Contract test와 clean build 뒤 STM32/ESP32 safe image를 두 board에 재플래시하고, reset reference marker를 포함해 PB6/PC8/PB7/PC9 boot no-output 회귀를 capture한다.
7. Board power/back-power 선행 조건을 닫고 `T-ESTOP-001~006`의 component/schematic, continuity, 3.3 V sense, latch/reset reject, no-auto-restart와 motor-disconnected timing을 통과시켜 Physical E-stop gate를 닫는다.
8. 위 active-output safety chain이 모두 `PASS`한 뒤에만 `T-MOTOR-003` first lifted/no-load 실제 motor 시험을 5~10% 제한으로 수행하고, current/heat/smell/noise, timeout/DISARM actual stop과 powered encoder false count/noise를 기록한다.
9. 업체 주문이 가능해지면 order ID, 실제 제출 revision, 재질·공차와 납기를 기록하고, 제작품 입고 시 control 작업과 별도로 fit-check branch를 수행한다.

## 사용자 직접 타이핑 학습 방식

STM32와 ESP32 firmware는 다음 사이클을 기본으로 한다.

```text
요구사항과 개념 확인
-> 작은 코드 블록 안내
-> 사용자가 직접 타이핑
-> 저장된 코드 검토와 설명
-> build/flash
-> 실제 계측 또는 log 검증
-> 학습 노트와 evidence 저장
```

작업 규칙:

- 한 번에 큰 모듈 전체를 복사하지 않는다.
- 한 단계마다 왜 필요한지, 입력·출력과 실패 조건을 설명한다.
- 사용자 작성 영역과 CubeMX generated 영역을 구분한다.
- compile 성공 뒤에도 해당 Test ID의 실제 수용 기준을 확인한다.
- 사용자 요청 없이 학습 대상 firmware를 대신 완성하지 않는다.

## 예상 작업 세션

아래 시간은 5시간 내외의 작업 세션 기준 추정이며, 계측 장비와 하드웨어 상태에 따라 달라진다.

| Session | 목표 | 예상 | 주요 산출물 |
| --- | --- | --- | --- |
| S1 | 발주 기록 + motor pin/frequency/channel 결정 + CubeMX | 2~4 h | decision record, `.ioc` change |
| S2 | safe motor-output module + STM32 pin 단독 시험 | 3~5 h | firmware, waveform/measurement |
| S3 | MDD10A logic input test | 2~4 h | checklist, wiring photo, signal evidence |
| S4 | plate fit + board power policy + encoder voltage | 2~4 h | fit record, DMM log |
| S5 | first motor no-load | 2~3 h | current/heat observation, video |
| S6 | encoder count와 speed telemetry | 3~5 h | count/sign log, TEL evidence |
| S7 | dual drivetrain 저속 시험 | 3~5 h | direction map, motion video |
| S8 | fault와 1 m acceptance | 3~5 h | fault evidence, distance table |
| S9 | 최종 matrix와 portfolio packaging | 3~5 h | README, evidence index, demo |

## Gate별 blocking decisions

### G3 전에 확정

- final PWM frequency
- MDD10A channel 1/2의 left/right mapping
- DIR level과 vehicle-forward 관계
- 첫 motor 후보

### G4~G5 전에 확정

- USB/buck 동시 연결 금지 또는 격리 방식
- fabricated plate fastener와 insulating spacer
- encoder supply와 input protection
- initial test duty와 fuse

### G7 전에 확정

- encoder counts per revolution 또는 실측 scale
- track effective travel scale
- low-voltage warning와 motor-stop threshold
- 1 m test procedure와 repeat count

### 최종 MVP 이후 결정

- CAN transceiver와 USB-CAN adapter
- FreeRTOS task period/priority
- LL migration target
- IMU owner STM32 또는 ESP32
- ROS 2 transport와 autonomy stack

## 중단 기준

다음 상황에서는 기능 추가를 멈추고 전원 제거와 원인 분석을 먼저 한다.

- polarity, short 또는 ground reference가 불확실하다.
- boot/reset 중 PWM이 active다.
- DISARM/timeout에서 actual PWM 또는 motor가 멈추지 않는다.
- PWM nonzero 상태에서 DIR이 바뀐다.
- buck, MDD10A, motor, wire 또는 전자부하가 비정상적으로 뜨겁다.
- 냄새, 연기, spark, fuse trip 또는 배터리 이상이 있다.
- encoder high voltage가 STM32 input 허용 범위를 넘는다.
- plate 또는 PCB를 억지로 휘거나 hole을 넓혀야 조립된다.
- track이 예상과 다른 방향으로 급격히 움직인다.

## 최종 산출물 체크리스트

- [ ] 모든 MUST requirement와 Test ID의 판정 완료
- [x] PC-first UART requirements, matrix와 report
- [x] ESP32-STM32 bridge raw log와 screenshot
- [x] MDD10A unpowered inspection
- [x] fuse/switch power bring-up evidence
- [x] XL4015 x2 bench load evidence
- [x] Adapter plate Rev A release와 preflight evidence
- [ ] Adapter plate fabricated fit evidence
- [x] PWM/DIR actual pin static/DMM evidence
- [x] MDD10A logic input static/LED evidence
- [x] PWM frequency/duty와 direction deadtime instrument evidence
- [ ] board power/back-power rule와 measurement
- [ ] first motor no-load report
- [x] motor-off encoder voltage, dual count와 speed telemetry evidence
- [ ] powered encoder noise와 external speed evidence
- [ ] dual drivetrain low-speed report
- [x] motor-disconnected timeout/DISARM/software-fault output-zero functional evidence
- [ ] active shutdown latency, reset-marker safe-image boot regression, physical E-stop와 motor-stop report
- [ ] 1 m distance/odometry report
- [ ] portfolio-ready README와 short demo

## 최종 포트폴리오 메시지

```text
STM32F446RE 기반 하위 구동 제어기를 구현하고,
UART command/telemetry protocol과 safety state machine,
ESP32 command bridge, MDD10A PWM/DIR motor output,
encoder feedback, 전원·기구 통합과 fault validation을
요구사항부터 실제 증거까지 추적한 tracked mobile robot platform
```

핵심 강조점:

- STM32가 final drivetrain safety authority다.
- PC/ESP32는 command source이며 safety를 우회할 수 없다.
- hardware bring-up을 무전원, signal-only, no-load, lifted, ground 단계로 분리했다.
- command-level zero와 physical output zero를 구분해 검증한다.
- 성공 화면뿐 아니라 계측값, fault와 residual risk를 증거로 남긴다.

## 관련 문서

- [`../../00_Project_Charter/01_Goal_and_Scope.md`](../../00_Project_Charter/01_Goal_and_Scope.md)
- [`../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)
- [`../../01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md`](../../01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md)
- [`../../01_System_Architecture/08_Motor_Driver_and_HBridge_Control_ko.md`](../../01_System_Architecture/08_Motor_Driver_and_HBridge_Control_ko.md)
- [`../../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md`](../../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md)
- [`../../01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md`](../../01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md)
- [`../../01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md`](../../01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md)
- [`../../01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md`](../../01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md)
- [`../../01_System_Architecture/17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md`](../../01_System_Architecture/17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md)
- [`../../01_System_Architecture/18_Fault_Model_and_Safety_Cases_ko.md`](../../01_System_Architecture/18_Fault_Model_and_Safety_Cases_ko.md)
- [`../../02_Hardware_Validation/README.md`](../../02_Hardware_Validation/README.md)
- [`../../08_Mechanical_Design/README.md`](../../08_Mechanical_Design/README.md)
