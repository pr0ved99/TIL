# Project Master Plan To Final MVP

## 문서 기준

- Revision: 2026-08-12 UART Gate C closeout + 4대 실행단원/예상시간 + RevA acrylic conditional-order gate + active DISARM 23.50 us MCU-pin baseline
- 현재 실행 위치: `G3/G4A PARTIAL`, `G5 encoder PARTIAL`, `G6 encoder mapping subtest PASS`; PWM/direction timing과 active DISARM MCU-pin first baseline은 PASS했다. ESP32 response-gated Gate A/B와 `T-BRIDGE-007/008` required runtime behavior가 PASS했다. 2026-08-12 current source의 모든 hook `0U`, contract `15/15`와 final exact startup, READY 후 약 12.2 s/TEL 123 safe UART behavior도 PASS했다. Exact runtime-to-artifact linkage, external cold-start marker, log-embedded physical setup provenance, timeout/fault latency, reset-marker boot, Physical E-stop과 actual motor가 남아 전체 release는 `PARTIAL`이다.
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
- MCU와 독립된 Physical E-stop motor-energy 차단, release/power-restoration no-auto-restart와 lifted 실제 정지 evidence
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
- PA4/PB0 이중 rail ADC plausibility, welded-contact discrepancy 자동 진단
- 정밀 `t0~t3` rail-transient 분포와 확장 fault-injection campaign
- Force-guided/safety relay, ISO 13849 PL 또는 IEC 62061/61508 SIL 적합성·인증

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

## 2026-08-12 현재 기준선

| Workstream | 현재 상태 | 판정 근거 | 다음 행동 |
| --- | --- | --- | --- |
| PC-first STM32 UART MVP | `PASS` | requirements, matrix, CSV, screenshots, test report | baseline 보존 |
| ESP32-STM32 UART bridge | `PARTIAL` | Gate A/B와 T-BRIDGE-007/008 required runtime PASS; post-test all-hooks-`0U`, contract `15/15`, final exact startup과 READY 후 약 12.2 s/TEL 123 safe 회귀 PASS; exact linkage, external cold-start marker와 log-embedded physical provenance pending | UART evidence 보존 뒤 timeout/fault latency와 reset-marker boot |
| MDD10A 무전원 검사 | `PASS` | visual/DMM hard-short inspection | logic input 전 재확인 |
| Fuse/switch power path | `PASS` | OFF 0 V, ON 12.49 V와 wiring evidence | 실제 통합 harness에서 재검증 |
| XL4015 x2 | `CONDITIONAL PASS` | 약 1 A 5분, 약 1.8 A 3분과 회복 전압 기록 | board power/back-power policy 결정 |
| Adapter plate Rev A release | `PASS` | A4 1:1 user comparison, vector/scale preflight, release hash | 30~60분 E-stop 부품 장착 동결 확인 뒤 prototype RevA 즉시 주문 또는 final-hole freeze까지 보류 |
| Adapter plate fabricated fit | `BLOCKED` | 제작품 미입고 | 입고 후 fit check |
| STM32 PWM/DIR | `PARTIAL` | PB6/PB7 waveform/direction PASS + active DISARM UART-to-PWM 23.50 us MCU-pin baseline PASS + current all-hooks-`0U` source/build PASS + 별도 observed safe UART behavior PASS | Gate C 후 safe restore; timeout -> software-fault latency; reset-marker boot; Physical E-stop |
| MDD10A logic input | `PARTIAL` | powered/no-motor 6-step, timeout/DISARM LED all-off, fault latch 0 V, MCU waveform and DISARM pin timing PASS | timeout/fault timing, driver output/actual motor stop, Physical E-stop closure |
| Encoder | `PARTIAL` | conditioning, dual count/CPS/mRPM, 1560 counts/rev와 encoder-side A=right/TIM5·B=left/TIM3 forward-positive PASS | powered-noise, external tachometer/wheel-speed 검증 |
| First motor no-load | `NOT TESTED` | motor, duty, current data 없음 | 앞선 안전 Gate 후 실행 |
| Dual drivetrain / chassis | `NOT TESTED` | MDD10A powered channel-to-side mapping과 주행 evidence 없음 | single motor/encoder 후 실행 |

Current strict-parser UART의 Gate A exact startup, Gate B bounded failure/stale response/reset recovery와 T-BRIDGE-007 wrong-ACK behavior는 actual board log로 통과했다. 2026-08-06~12 T-BRIDGE-008A planned response vectors도 gate를 열지 않고 same-seq retry 뒤 exact response에서만 recovery했다. 2026-08-12 T-BRIDGE-008B는 malformed/unknown STM32 command 8개를 거부하고 TEL 200/200 `DISARMED/zero`를 유지한 뒤 final matching PING/PONG으로 복구했다. 최신 cycle 뒤 모든 hook `0U`, contract `15/15`와 final exact startup, READY 후 약 12.2 s/TEL 123 safe 회귀를 완료했다. Gate C required runtime scope는 PASS지만 raw UART log에 artifact hash와 physical setup metadata가 없어 exact linkage/provenance는 pending이다. Reset raw segment는 직전 failure를 포함하지 않아 post-failure session linkage도 operator confirmation pending이다. Motor-output은 waveform/direction, active DISARM 23.50 us MCU-pin baseline까지 진행됐지만 timeout/fault latency, MDD10A power stage, reset-marker boot, Physical E-stop과 실제 motor 회전은 미검증이다. 따라서 진행률 숫자보다 Gate 상태와 evidence boundary를 기준으로 판단한다.

## 실행 대단원과 예상 작업시간

아래 4개 대단원은 전체 일정을 이해하기 위한 **실행·일정 관점**이다. 뒤의 `G0~G8`은
requirement와 evidence 통과 여부를 관리하는 **검증 Gate 관점**이며 서로 대체하지 않는다.
예상시간은 부품 배송 대기를 제외한 실제 설계·구현·계측·문서화 작업시간이다.

| 대단원 | 대응 Gate | 주요 소단원 | 예상 작업시간 | 완료 조건 |
| --- | --- | --- | ---: | --- |
| 1. MCU 저수준 안전 검증 마무리 | `G3`, `G4A` | command-timeout latency, software-fault latency/latch, all-hooks-`0U` restore, external-reset-marker boot no-output | 3~5시간 | 세 waveform evidence와 safe restore PASS |
| 2. 전원·Physical E-stop | `G4B`, `T-ESTOP-001~005` | USB/buck back-power, K1/K2/S0/S2/opto/F1 회로·배선, sense/latch/reset, motor-disconnected energy-cut | 8~16시간 | power policy와 motor-disconnected E-stop MVP Gate PASS |
| 3. 첫 실제 motor 구동 | `G5`, `T-ESTOP-007` | lifted single motor 5~10%, current/heat/smell/noise, MDD channel/side/direction, powered encoder noise, actual stop/no-auto-restart | 6~12시간 | 한쪽 motor와 encoder, stop path evidence PASS |
| 4. 양쪽 궤도·이동·odometry | `G6`, `G7` | dual motor mapping, 전진/후진/제자리 회전, wheel-travel scale, 1 m distance error, final fault/stop regression | 12~24시간 | 저속 drivetrain와 1 m odometry acceptance evidence PASS |

합계는 **29~57시간**이며 주 25시간 기준 순수 작업시간은 약 **1.5~2.5주**다.
재배선, 파형 재측정, 부품 조달과 재시험을 포함한 현실적인 달력 일정은 **2~3주**로 잡는다.

### 대단원 간 직렬 순서

```text
현재: UART Gate C 완료
-> 대단원 1 timeout/fault/reset waveform
-> 대단원 2 power/back-power + Physical E-stop
-> 대단원 3 lifted single motor
-> 대단원 4 dual drivetrain + odometry
-> low-level drivetrain MVP acceptance
```

대단원 1~4는 safety evidence 관점에서는 직렬이다. 다만 adapter plate 제작과 배송은
control firmware 검증을 막지 않는 병렬 mechanical branch로 운영한다.

### RevA acrylic 주문 시점 Gate

현재 RevA는 `174 x 208.93379 mm`, acrylic 3T, nominal 3.3 mm hole 기준으로 주문 파일,
A4 1:1 chassis 대조와 vector/scale preflight를 통과했다. 실제 주문만 vendor upload 오류로
`NOT SUBMITTED`다. 반면 RevA의 component list에는 XL4015 x2, MDD10A와 universal PCB가
있지만 이후 추가된 Physical E-stop의 K1/K2/F1/S0/S2 exact mounting은 포함되지 않았다.

주문 전 30~60분 mechanical freeze check에서 다음을 확인한다.

1. K1/K2/F1을 RevA plate, universal PCB 또는 별도 bracket 중 어디에 고정할지 결정한다.
2. S0/S2는 operator 접근 가능한 chassis/body 위치에 별도 고정하며 plate hole이 필요한지 확인한다.
3. 현재 RevA hole을 바꾸지 않아도 절연·배선 굽힘·단자 접근·교체성이 확보되는지 확인한다.
4. 업체에 acrylic 방식/색상, kerf, minimum 3.3 mm hole, 공차, VAT/배송비를 확인한다.

판정 규칙:

- **Prototype RevA 1개이고 추가 가공 또는 RevB를 허용한다면:** 위 확인 직후 대단원 1과
  병렬로 주문한다. Firmware/E-stop 완료까지 기다리지 않는다.
- **이번 한 장을 final plate로 사용하고 재가공을 허용하지 않는다면:** K1/K2/F1 실제
  부품과 장착 위치가 동결되는 대단원 2 중반까지 보류하고, first motor 시험 전 주문한다.
- Order ID, revision, material, thickness, tolerance와 주문 PDF hash를 기록하기 전에는
  `ORDERED`로 표시하지 않는다.

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

정적/DMM 범위는 2026-07-26, actual PWM/direction timing은 2026-08-03, active DISARM MCU-pin first baseline은 2026-08-04에 통과했다. Timeout/software-fault latency와 reset-marker를 포함한 최종 hook-off boot 회귀는 남아 있다.

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
PARTIAL - static/DMM routing + 20.1005 kHz/약 10.05% PWM + direction settle + active DISARM 23.50 us MCU-pin sub-gates PASS; timeout/software-fault latency와 reset-marker hook-off boot pending
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
- 2026-08-03 safe-source checkpoint에서 temporary hook `0U`, contract `15/15`, STM32 Debug/ESP isolated build와 STM32 safe flash/no-output 회귀를 확인했다. 이후 response-gated Gate A/B runtime과 2026-08-04 active DISARM capture를 수행했다.
- 2026-08-04 active DISARM은 UART RX frame end부터 PB6/PB7 last edge까지 `23.50 us`, PWM stop부터 ACK start까지 `62.75 us`였다. MCU-pin first baseline만 PASS하며 MDD10A/motor/E-stop을 포함하지 않는다.
- 2026-08-04 safe-image UART runtime behavior는 exact startup, ARM/CMD 0과 TEL 118/118 DISARMED/zero/error 0으로 PASS했고, 이어서 wrong-ACK vector도 PASS해 `T-BRIDGE-007` required behavior를 닫았다. 당시 worktree/test image의 wrong-ACK hook `1U`는 historical controlled state다.
- 2026-08-06 T-BRIDGE-008A duplicate-required-`seq` ACK rejection/recovery subvector를 PASS했다. 시험 뒤 모든 test hook `0U`, contract `15/15`, STM32CubeIDE build/reflash와 post-READY 14.42 s/TEL 150 safe UART regression을 완료했다. 당시 safe ELF SHA-256은 `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`였고, trailing-comma vector 직전의 historical checkpoint로 보존한다.
- 2026-08-06~07 T-BRIDGE-008A trailing-comma ACK rejection/recovery subvector도 PASS했다. 시험 뒤 모든 test hook `0U`, contract `15/15`, controlled string 부재, safe reflash와 post-READY 15.51 s/TEL 160 safe UART regression을 완료했다. Post-Clean full build도 31개 object 전체를 재컴파일·링크해 `0 errors / 0 warnings`였고 retained safe artifact hashes를 재현했다. 당시 safe ELF SHA-256은 `3526206C7E2043634029B15B7D41F9C80B136904FCA72FB46D8CA24F4119DEE4`이며 required-`seq` uint32-overflow vector 직전의 historical checkpoint로 보존한다.
- 2026-08-07 T-BRIDGE-008A required-`seq` uint32-overflow ACK rejection/recovery subvector도 PASS했다. `seq=4294967296`을 1회 거부하고 500 ms same-seq retry 뒤 exact ACK/PONG에서만 READY가 열렸으며 post-READY TEL 140/140은 safe였다. 시험 뒤 모든 hook `0U`, contract `15/15`, protocol source 재컴파일과 ELF relink `0 errors / 0 warnings`, controlled string 부재, safe reflash와 post-READY 14.43 s/TEL 145 safe UART regression을 완료했다. 당시 safe ELF SHA-256은 `244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`다. Physical setup provenance는 pending이었다.
- 2026-08-11 T-BRIDGE-008A partial-frame-name ACK rejection/recovery subvector도 PASS했다. `AC,...`을 unknown frame으로 1회 거부하고 500 ms same-seq retry 뒤 exact ACK/PONG에서만 READY가 열렸다. 시험 뒤 모든 hook `0U`, contract `15/15`, full build `0 errors / 0 warnings`, controlled literal 부재, safe reflash와 post-READY 약 16.27 s/TEL 164 safe UART regression을 완료했다. 당시 safe ELF SHA-256은 `3567C9266C2D46DD920C8DAD6DE29656EBBC0BA73AB35CF1D55CC9368EABF4CA`다. Physical setup provenance는 pending이었다.
- 2026-08-12 embedded CR, control byte `0x01`와 overlong startup response를 거부하고 same-seq retry 뒤 exact ACK/PONG에서만 READY가 되는 남은 T-BRIDGE-008A vectors를 PASS했다. T-BRIDGE-008B도 malformed/unknown STM32 command 8/8 거부, TEL 200/200 safe와 final matching PING/PONG recovery를 PASS했다. All-hooks-`0U`, contract `15/15` 뒤 final exact startup, READY 후 약 12.2 s와 post-READY TEL 123/123 safe를 확인했다. Safe STM32 ELF SHA-256은 `46A80919B8ECE0521CBFA0861D74446F51904F7D9967517DCDC63118EA73B98A`, safe ESP32 BIN SHA-256은 `4321B4BF2811590167EB7DCEF58CA84ABE5C0C7EEC67656E20D0EFD787A2724D`다. Exact runtime linkage와 log-embedded setup provenance는 pending이다.

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
PARTIAL - G4A static routing, timeout-DISARM/software-fault functional, waveform/direction과 active DISARM MCU-pin sub-gates PASS; T-BRIDGE-008A/008B required runtime과 post-test all-hooks-`0U`/contract `15/15`/final safe UART behavior PASS; exact artifact linkage와 log-embedded physical setup provenance, timeout/fault edge latency, reset-marker boot, physical E-stop, G4B와 G4C pending
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

2026-08-12 이후 우선순위:

아래 2는 완료된 UART Gate C evidence를 보존하는 단계다. 아래 3~7은 actual motor 활성화 전 직렬 safety chain이며, 앞 단계가 통과하기 전에는 다음 단계로 넘어가지 않는다.

1. 2026-08-03 waveform/direction, 2026-08-04 active DISARM 23.50 us, Gate A/B와 wrong-ACK raw logs, encoder `1560 counts/output rev`와 forward-positive mapping을 회귀 기준으로 보존한다.
2. 2026-08-12 report 15, all-hooks-`0U` source, contract `15/15`, safe artifacts와 final post-READY TEL 123 safe UART behavior를 Gate C 완료 기준선으로 보존한다. 다음 evidence부터 raw flash transcript, retained binary hash와 physical no-power setup metadata를 함께 기록한다.
3. Motor-disconnected 10%-limited output에서 command-timeout UART-to-PWM latency를 capture한다.
4. Dedicated marker 또는 분리된 debounced event로 software-fault shutdown latency/latch를 capture한다.
5. 다시 safe restore한 뒤 external reset marker를 포함한 PB6/PC8/PB7/PC9 boot no-output 회귀를 capture한다.
6. Board power/back-power와 Physical E-stop MVP gate인 `T-ESTOP-001~005`를 닫는다.
7. 위 safety chain이 모두 PASS한 뒤에만 first lifted/no-load actual motor 시험을 5~10% 제한으로 수행한다.
8. 같은 lifted setup에서 `T-ESTOP-007` 실제 정지와 no-auto-restart evidence를 확보한다.
9. 정밀 rail transient/dual-rail plausibility인 `T-ESTOP-006`은 MVP 종료를 막지 않는 후속 진단 V-cycle로 수행한다.
10. 30~60분 E-stop mounting freeze check를 먼저 수행한다. RevA를 prototype으로 허용하면
    대단원 1과 병렬로 즉시 1개 주문하고, final-only라면 대단원 2 component placement
    freeze 뒤 first motor 전 주문한다. Order ID/revision/material/tolerance를 기록하고
    입고 후 fit check를 수행한다.

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
- [x] active DISARM MCU-pin first shutdown-latency baseline
- [ ] active timeout/fault latency, reset-marker safe-image boot, physical E-stop와 motor-stop report
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
