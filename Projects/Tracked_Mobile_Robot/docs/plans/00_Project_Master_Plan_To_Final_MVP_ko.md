# Project Master Plan To Final MVP

## 문서 기준

- Revision: 2026-08-30 P-04B reset-harness prepared / all selected E-stop parts arrived
- 현재 실행 위치: `P-01/ADR-015 ACCEPTED`, `P-02A~P-02C-2 COMPLETE`, `P-03 COMPLETE`, canonical `REQ-SAFE-004` 500 ms target acceptance COMPLETE, `P-04A COMPLETE — UART/software-cached applied-output scope`, `P-04B PARTIAL — reason/command-age source/static + target runtime subset + reset closeout harness prepared`, `G3 PASS`, `G4A PASS — motor-disconnected MDD10A-input scope`, `G5 encoder PARTIAL`, `G6 encoder mapping subtest PASS`. Current host/static은 `29/29`이다. P-04B에서 no-CMD sentinel, accepted-CMD age reset, 500 ms timeout과 direct-PC7 `ESTOP_ACTIVE -> ESTOP_LATCHED` runtime subset을 PASS했다. Active E-stop 중 reset 거부는 별도 persistent reason이 아니라 `ERR,type=ESTOP_RESET,code=ESTOP_ACTIVE`와 계속 유지되는 `TEL state=FAULT,reason=ESTOP_ACTIVE`의 같은-run 조합으로 식별하는 계약이다. All-hooks-`0U` isolated STM32/ESP32 build와 artifact hash 기록은 PASS했다. Default-off reset harness의 source/static과 current ESP32 build도 PASS했지만, 이 reset-reject runtime, release 뒤 explicit reset 성공과 current hook-0 target reflash/no-command safe runtime은 아직 OPEN이다. P-04A/P-04B telemetry는 measured PWM feedback이나 actual motor evidence가 아니다. K1/S0/S2/VO617A-3/P6KE/F2는 report 19의 무전원 component screen을 통과했고 6P는 loose kit+별도 18 AWG로 확인됐지만 미조립이다. `VH-30J`/`WX-03B` crimp-tool set는 사용자 보고로 도착했지만 exact 구성/상태, die 적합성과 first-article crimp는 미검증이다. 다음 firmware 순서는 집에서 P-04B의 open 항목을 닫은 뒤 `P-05` battery로 이동하는 것이다. 집에서는 `H-01` plate/6P non-destructive capture와 crimp-tool inspection/first-article를 병행한다. 다음 실제 직렬 Gate는 Physical E-stop `T-ESTOP-001~004 + T-ESTOP-005A`이며 MDD10A power stage와 actual motor는 아직 미검증이라 전체 release는 `PARTIAL`이다.
- 기구 제작 상태: `USER-REPORTED RECEIVED / EXACT REVISION IDENTITY AND FIT NOT TESTED`. 실제 order source, 치수·hole pattern과 chassis/module fit은 아직 증거가 없다.
- 요구사항·검증 정본: [`../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)
- 현재 진행 기록: [`../progress/2026-08-30_progress.md`](../progress/2026-08-30_progress.md)

이 문서는 Tracked Mobile Robot 프로젝트의 최신 전체 실행 로드맵이다. 날짜별 progress log는 실제로 수행한 일을 기록하고, 이 문서는 다음에 무엇을 해야 하며 어떤 증거가 있어야 다음 단계로 갈 수 있는지를 정의한다.

## 최종 MVP 종료선

1차 종료선은 완성형 자율주행 로봇이 아니다.

```text
STM32 기반 하위 구동 플랫폼이
ESP32-S3 단일 production ingress의 속도 명령을 받아
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
- ESP32-S3가 유일한 Final MVP production command ingress를 맡고 STM32 USART1로 전달하는 구조; PC control은 필요 시 ESP32를 경유하고 USART2는 bench-only
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
- `FM-ESTOP-014`의 S2 stuck-closed/6P S2-pair short 단일고장 내성 및 `T-ESTOP-005B`
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
| 목표와 사용 시나리오 | charter, `MVP-001~013` | 최종 기본 동작, Physical E-stop, 1 m, 문서 인수시험 |
| 시스템 요구사항 | UART, power, mechanical, motor, encoder, drive requirement | fault stop, drivetrain, telemetry 시험 |
| 아키텍처와 interface | controller ownership, pin map, UART, power, MDD10A contract | ESP32-USART1 production ingress, STM32-MDD10A, encoder 통합시험 |
| 상세 설계 | CubeMX pin/timer, motor-output module, CAD Rev, harness | 핀 파형, DMM, 치수와 fit 시험 |
| 구현 | firmware, wiring, fabricated plate | build/flash 뒤 실제 계측과 동작 증거 |

적용 규칙:

1. 각 `MUST` 요구사항에는 acceptance criteria와 Test ID가 있어야 한다.
2. `Build Successful`은 구현 확인이지 하드웨어 시험 통과가 아니다.
3. command 변수 zero와 실제 PWM output zero를 별도 요구사항으로 검증한다.
4. CAD 1:1 출력 PASS와 제작품 fit PASS를 구분한다.
5. 다음 Gate는 선행 Gate의 evidence가 있어야 시작한다.
6. 설계가 바뀌면 영향받는 requirement, test와 evidence를 함께 갱신한다.

## 현재 기준선 — 2026-08-30 갱신

| Workstream | 현재 상태 | 판정 근거 | 다음 행동 |
| --- | --- | --- | --- |
| Historical PC-first STM32 UART MVP | `PASS — bench baseline` | requirements, matrix, CSV, screenshots, test report | production owner로 사용하지 않고 evidence 보존 |
| ESP32-STM32 UART bridge | `PARTIAL` | ADR-015 owner/path ACCEPTED; Gate A/B와 T-BRIDGE-007/008 required runtime, P-03/REQ-SAFE-004 recovery와 P-04A applied-output TEL/ESP parser PASS. P-04B reason/command-age source/static, no-CMD/accepted-CMD/timeout/direct-PC7 active-to-latched runtime subset와 hook-0 isolated build PASS. Default-off reset closeout harness와 current ESP32 build를 준비했고 current host/static은 `29/29`. P-04B active reset reject/released reset success와 current all-hooks-`0U` target reflash/runtime, exact artifact/setup provenance, reset-net evidence와 reverse/asymmetric sign은 open | 집에서 reset harness run -> all-hooks-`0U` 복구/reflash/no-command safe runtime -> P-05 battery |
| MDD10A 무전원 검사 | `PASS` | visual/DMM hard-short inspection | logic input 전 재확인 |
| Fuse/switch power path | `PASS` | OFF 0 V, ON 12.49 V와 wiring evidence | 실제 통합 harness에서 재검증 |
| XL4015 x2 | `CONDITIONAL PASS` | 약 1 A 5분, 약 1.8 A 3분과 회복 전압 기록 | board power/back-power policy 결정 |
| Adapter plate release | `PASS` | A4 1:1 비교와 3.0 mm 수정본까지 확인 | release 기준선 보존 |
| Adapter plate order/fabrication | `USER-REPORTED RECEIVED` | 2026-08-18 order 기록과 2026-08-26 사용자 수령 확인; actual order artifact/source hash는 없음 | 도착품을 RevB source와 물리적으로 대조 |
| Adapter plate fabricated fit | `READY / NOT TESTED` | 제작품은 수령했지만 사진·실측·체결 evidence 없음 | 집 H-01에서 치수/fit/절연 확인 |
| STM32 PWM/DIR | `PASS — motor-disconnected MCU-pin scope` | waveform/direction, active DISARM 23.50 us, timeout/fault/reset과 hook-0 safe restore PASS | 기준선 보존; Physical E-stop |
| MDD10A logic input | `PASS — motor-disconnected input scope` | Permanent pull-down/5-Net, powered/no-motor, final CH1/CH2 19.049/19.058 kHz 6-step와 final all-LOW PASS | MDD10A power-stage/actual motor stop, Physical E-stop closure |
| Encoder | `PARTIAL` | conditioning, dual count/CPS/mRPM, 1560 counts/rev와 encoder-side A=right/TIM5·B=left/TIM3 forward-positive PASS | powered-noise, external tachometer/wheel-speed 검증 |
| Physical E-stop MVP | `PARTIAL/BLOCKED` | direct-PC7 sense/latch/reset, report 18 F1/K2/resistors와 report 19 K1/S0/S2/VO617A-3/P6KE/F2 무전원 subset PASS. 6P는 loose kit로 미조립이다. Crimp-tool set는 도착했지만 구성/적합성과 first article은 미검증이고 clamp powered behavior/conditioned path/K1 rail-off도 open | Tool/die inspection -> spare 18 AWG first article -> 6P cavity/continuity/retention -> complete assembly -> `T-ESTOP-001~004` -> nominal `T-ESTOP-005A` |
| First motor no-load | `NOT TESTED` | vendor rated 1.44 A/stall 9 A 확보; actual current/thermal evidence 없음 | `T-ESTOP-001~004 + T-ESTOP-005A` PASS 뒤 실행 |
| Dual drivetrain / chassis | `NOT TESTED` | MDD10A powered channel-to-side mapping과 주행 evidence 없음 | single motor/encoder 후 실행 |

Current strict-parser UART Gate와 MCU-pin safety baseline을 보존한다. Permanent pull-down/5-Net,
board power/back-power와 final perfboard MDD10A-input 19 kHz active 6-step/safe restore까지 PASS했다.
WHEELTEC 회신으로 rated/stall current 입력을 확보하고 K1/F1/main-wire 계산을 완료했다. K1은
catalog numerical PASS이고 exact components/`89.5 ohm` coil/NO/coil-contact gross-short 무전원 screen도
통과했지만 suppression/thermal/rail-off는 미검증이다. S0/VO617A-3/F2의 지정된 무전원 screen도
report 19에 닫았다. S2/P6KE incoming도 같은 report에서 닫혔다. 그러나 6P
cavity/crimp/retention과 complete assembly가 PASS하기 전에는 powered coil test로 이동하지 않는다.
따라서 진행률 숫자나 배송상태보다 Gate와 evidence boundary를 기준으로 판단한다.

## 실행 대단원과 예상 작업시간

아래 4개 대단원은 전체 일정을 이해하기 위한 **실행·일정 관점**이다. 뒤의 `G0~G8`은
requirement와 evidence 통과 여부를 관리하는 **검증 Gate 관점**이며 서로 대체하지 않는다.
예상시간은 부품 배송 대기를 제외한 실제 설계·구현·계측·문서화 작업시간이다.

| 대단원 | 대응 Gate | 주요 소단원 | 예상 작업시간 | 완료 조건 |
| --- | --- | --- | ---: | --- |
| 1. MCU 저수준 안전 검증 마무리 | `G3`, `G4A` | command-timeout shutdown, software-fault next-pulse suppression/latch, all-hooks-`0U` restore, external-reset boot no-output | 3~5시간 | `COMPLETED` — 세 waveform scope와 safe restore PASS |
| 2. 전원·Physical E-stop | `G4B`, `T-ESTOP-001~004`, `T-ESTOP-005A` | USB/buck back-power, K1/K2/S0/S2/opto/F1 회로·배선, sense/latch/reset, motor-disconnected nominal energy-cut | 8~16시간 | power policy와 nominal motor-disconnected E-stop MVP Gate PASS |
| 3. 첫 실제 motor 구동 | `G5`, `T-ESTOP-007` | lifted single motor 5~10%, current/heat/smell/noise, MDD channel/side/direction, powered encoder noise, actual stop/no-auto-restart | 6~12시간 | 한쪽 motor와 encoder, stop path evidence PASS |
| 4. 양쪽 궤도·이동·odometry | `G6`, `G7` | dual motor mapping, 전진/후진/제자리 회전, wheel-travel scale, 1 m distance error, final fault/stop regression | 12~24시간 | 저속 drivetrain와 1 m odometry acceptance evidence PASS |

최초 합계는 **29~57시간**이었다. 대단원 1 완료 후 남은 순수 작업시간은 **26~52시간**이다.
2026-08-28 selected component 무전원 screen, P-03 scoped target runtime과 canonical
`REQ-SAFE-004` 500 ms target acceptance를 앞당겨 닫았고 2026-08-29 P-04A applied-output
telemetry도 닫았다. P-04B는 reason/command-age source/static과 target runtime subset까지 진행했지만
active reset reject/released reset success와 hook-0 target reflash/runtime restore가 남아 `PARTIAL`이다.
Crimp-tool 배송 blocker는 해소됐다. 현재 complete E-stop integration의 blocker는 tool/die
inspection과 6P first-article/assembly다. 종료일은 `tool 검증 + 6P 조립/통합시험 +
26~52시간의 유효 작업시간 + 재시험 여유`로
계산한다. 기존 `2~3주` 수치는 현재 일정 약속으로 사용하지 않는다.

### 대단원 간 직렬 순서

```text
완료: UART Gate C + 대단원 1 timeout/fault/reset MCU-pin + P-03 300 ms target runtime/safe restore + REQ-SAFE-004 500 ms target acceptance
-> run04 safe build/flash/UART/D0~D3 all-LOW restore 완료
-> P-04A applied-output telemetry + hook-0 safe restore 완료
-> P-04B reason/age + no-CMD/timeout/direct-PC7 active-to-latched runtime subset 완료, PARTIAL
-> 완료: default-0U P-04B E-stop-reset test harness + host/static contract + current ESP32 isolated build
-> 다음 HOME/BOARDS: active reset 거부 ERR+TEL pair -> release 뒤 explicit reset 성공
-> all-hooks-0U 양 board reflash -> ARM/CMD TX 0 no-command safe runtime
-> P-04B COMPLETE 뒤 P-05 battery -> P-06 odometry
-> 병행 HOME: plate/6P cavity non-destructive capture
-> 도착한 tooling의 exact 구성/상태/die 확인 -> spare 6P terminal first-article crimp -> cavity/intended-continuity/unintended-open/retention
-> complete assembly gate
-> 대단원 2: T-ESTOP-001~004 -> nominal T-ESTOP-005A
-> 대단원 3 lifted single motor
-> 대단원 4 dual drivetrain + odometry
-> low-level drivetrain MVP acceptance
```

대단원 1~4의 실제 energy-on 시험은 safety evidence 관점에서 직렬이다. 다만 부품 배송 중에는
[`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md)의
`P-01~P-09`를 병렬로 수행한다. `T-ESTOP-005B` 단일고장 확장은 MVP 뒤 별도 V-cycle이다.

### Received PC plate identification and fit Gate

2026-08-26 사용자는 custom PC adapter plate가 이미 도착했다고 확인했다. 저장소의
`2026-08-18_adapter_plate_revB_PC3T_hole3p0_order` DWG/DXF가 실제 제조 source일 가능성은
높지만 주문 artifact·사진·실측이 없어 아직 동일성을 입증하지 않았다. 따라서 plate 부재나
주문 미제출을 blocker로 두지 않고 physical evidence만 집 `H-01`로 분리한다.

집에서 모든 전원을 분리하고 다음을 확인한다.

1. 도착 plate의 top/bottom/edge 사진과 폭·높이·두께를 기록한다.
2. RevB 후보의 `8 x diameter 3.0 + 21 x diameter 3.3 + 2 x diameter 30 mm` 패턴과 대조한다.
3. 억지 가공이나 plate 휨 없이 chassis에 체결한다.
4. universal PCB, XL4015 x2와 MDD10A를 무전원 dry fit한다.
5. USB·terminal 접근, spacer, 납땜면 절연과 cable path를 확인한다.
6. K1/K2/F1/F2는 plate/perfboard/inline bracket, S0/S1/S2는 operator panel로 분류하고
   추가 drilling 필요 여부를 결정한다.

현재 카페에서는 이 실물 결과를 추정하지 않는다. `P-04B`는 active reset 거부의
`ERR,type=ESTOP_RESET,code=ESTOP_ACTIVE` + `TEL state=FAULT,reason=ESTOP_ACTIVE` pair,
release 뒤 explicit reset 성공, all-hooks-`0U` 양 board reflash와 ARM/CMD TX 0
no-command safe runtime 순서로 닫는다.

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

- Historical PC-first bench path와 current ESP32 production path의 증거를 구분해 STM32 parser와
  safety authority를 검증한다. Optional PC control은 `PC -> ESP32 -> STM32` 경로만 허용한다.

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

- electronics를 셰시에 안전하게 고정할 received PC plate를 식별하고 실물 검증한다.

Source candidate:

- 174 x 208.93379 mm
- PC 3T order intent
- RevB mixed hole pattern: 8 x diameter 3.0, 21 x diameter 3.3, 2 x diameter 30 mm
- A4 1:1 comparison PASS
- order PDF vector and scale PASS

Source-to-part identification에서 기록할 항목:

- 실제 제출 파일과 revision 또는 order artifact
- 도착품 material, thickness, outer size와 hole pattern
- 사진, 실측값과 candidate DWG/DXF 대조 결과

Exit criteria:

- 외곽, 두께, 주요 hole 지름과 center distance를 실측한다.
- 억지 가공이나 plate 휨 없이 chassis에 체결한다.
- universal PCB, XL4015 x2와 MDD10A를 무전원 가조립한다.
- USB·terminal 접근, spacer, 납땜면 절연과 cable path를 확인한다.
- 결과를 `PASS` 또는 Rev B 필요로 판정한다.

상태:

```text
FABRICATED PLATE USER-REPORTED RECEIVED
/ SOURCE IDENTITY OPEN
/ PHYSICAL FIT NOT TESTED
```

### G3. STM32 PWM/DIR signal-only verification

목표:

- MDD10A와 motor power를 연결하기 전에 STM32 자체 motor-output contract를 구현·계측한다.

정적/DMM 범위는 2026-07-26, actual PWM/direction timing은 2026-08-03, active DISARM MCU-pin first baseline은 2026-08-04에 통과했다. 2026-08-12 command-timeout, software-fault next-pulse suppression/latch와 external-reset boot를 추가로 닫아 motor-disconnected MCU-pin 범위를 완료했다.

먼저 확정할 결정:

- MDD10A channel 1/2의 차량 left/right mapping
- 첫 motor 후보
- PWM frequency: WHEELTEC `5~20 kHz`; historical 20 kHz baseline `20.1005 kHz`, final nominal `19 kHz`
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

현재 checkpoint의 구현은 `PWM 0 -> 1 ms PWM-zero settle -> DIR 변경 -> 1 ms post-DIR settle -> PWM 재개` 순서다. 2026-08-03의 20.1005 kHz는 historical baseline이다. WHEELTEC 상한 margin을 위해 2026-08-18 TIM4 period를 `4420`으로 변경했고 final perfboard input에서 CH1/CH2 `19.049/19.058 kHz`, 약 10% duty와 direction 전후 약 2 ms zero interval을 확인했다. 2026-08-12 external reset pull-down 미적용 FAIL과 signal별 `10 kΩ` 적용 5 s all-LOW도 보존한다.

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
PASS — motor-disconnected MCU-pin scope; timeout은 configured 300 ms 주변 bounded stop, fault는 expected next pulse 차단과 latch, reset은 signal별 external 10 kΩ 적용 전 구간 LOW. Driver power stage와 actual motor는 포함하지 않음
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
- 2026-08-12 motor-disconnected timeout/fault/reset 시험을 수행했다. 300 ms timeout은 UART-calibrated frame-end-to-last-edge 약 `299.690 ms`와 이후 약 `8.939 s` no-reactivation으로 통과했다. Software fault는 marker 뒤 expected next PWM pulse가 억제되고 약 `2.052 s` latch를 유지했다. External reset의 부동 HIGH FAIL 뒤 네 signal별 `10 kΩ` pull-down을 추가해 5 s 전 구간 LOW를 확인했다. 최종 모든 hook `0U`, contract `15/15`, READY 뒤 15.4 s/TEL 155 safe UART 회귀도 통과했다. 상세 evidence boundary는 verification report 16을 따른다.
- 2026-08-18 permanent perfboard MDD10A-input에서 nominal 19 kHz 양 채널 active 6-step,
  inactive-channel LOW와 direction 전후 약 2 ms zero interval을 PASS했다. 시험 뒤 모든 hook을
  `0U`로 복구하고 contract `15/15`, B1 no-output와 final 5 s D0~D3 all-LOW를 확인했다.

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
PARTIAL - G3와 G4A motor-disconnected input scope, permanent 10 kΩ/5-Net, G4B board power와 final 19 kHz active/safe restore PASS. Exact artifact linkage, fabricated fit, MDD10A power stage, Physical E-stop와 actual motor pending
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
2. ESP32 production command ingress basic motion
3. USART2 bench path가 production motion command를 소유하거나 우회하지 않음
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

## Current 병렬 실행 계획

상세 task, 완료 조건과 금지사항의 현재 정본은
[`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md)다.
P-03/REQ-SAFE-004 target acceptance와 selected-component incoming이 닫히고 crimp-tool set도
도착한 현재, 아래 software/document 작업과 6P/tooling 검증을 motor-energy 없이 병렬로 진행할 수 있다.

1. `[COMPLETED / ADR-015] P-01`: ESP32-S3 단일 production ingress, USART1 production/USART2 bench-only와 source-loss recovery 정책을 확정했다.
2. `[COMPLETE] P-02B`: test hook과 분리된 production mapper module, independent vectors/static source contract의 당시 `23/23` checkpoint와 full build를 닫았다.
3. `[PASS / HISTORICAL 24/24] P-02C-1`: provisional DIR polarity를 명시한 signed-output adapter와 fail-safe range/error 경로를 추가했다. 당시 no-caller section의 `--gc-sections` 제거는 P-02C-2에서 해소됐다.
4. `[COMPLETE / HISTORICAL 25/25] P-02C-2`: validation/ARMED/3x E-stop/mapper/상호 배타 output/success-only commit+ACK caller와 실패 시 stop/zero/ERR/return 계약을 연결했다. 당시 32-object forced build와 nonzero ELF linkage PASS이며 flash/board runtime은 pending이다.
5. `[COMPLETE — 300 ms P-03 + 500 ms REQ-SAFE-004 SCOPED TARGET RUNTIME + RUN04 SAFE RESTORE] P-03`: pre-RX timeout helper가 output/stored command zero -> `DISARMED`를 강제하고, accepted `ARM`이 default 300 ms first-CMD window를 다시 시작한다. Historical P-03 canonical `26/26`, forced 32-object build와 ELF `29268/172/2832`, motor/LiPo-disconnected 300 ms target UART/PWM recovery와 당시 all-hooks-`0U` safe restore가 PASS했다. Canonical 500 ms run03도 same-run UART/PWM acceptance를 PASS했고 run04에서 source hook `0U`, safe build/flash/UART와 D0~D3 10 s all-LOW restore를 PASS했다. Exact controlled artifact linkage, electrically captured reset timing, clean electrical cold-start와 actual motor는 범위 밖/pending이다.
6. `[P-04A COMPLETE / P-04B PARTIAL] P-04`: software-cached signed left/right applied PWM과 reason/command-age를 STM TEL 및 ESP parser/log에 연결했고 current canonical `29/29`이다. P-04B target에서는 no-CMD sentinel, accepted-CMD age reset, timeout과 direct-PC7 `ESTOP_ACTIVE -> ESTOP_LATCHED` subset을 PASS했다. Reset-rejected 식별 계약은 active 상태의 `ERR,type=ESTOP_RESET,code=ESTOP_ACTIVE`와 유지되는 `TEL state=FAULT,reason=ESTOP_ACTIVE` pair다. Default-off reset closeout harness와 current ESP32 isolated build는 PASS했지만 이 pair의 runtime과 release 뒤 `DISARMED/ESTOP_RESET` 성공은 아직 실행하지 않았다. 이어 all-hooks-`0U` 양 board reflash와 ARM/CMD TX 0 no-command safe runtime까지 확인한 뒤 P-04B를 완료한다. Battery actual source는 P-05로 분리한다.
7. `P-05`: battery ADC divider, calibration과 low-voltage policy를 설계·검증한다.
8. `P-06`: encoder count에서 wheel distance와 1 m odometry를 계산하는 경로를 구현한다.
9. `P-07`: received adapter plate identity/fit, E-stop mounting freeze, track/fastener/strain-relief와 6P cavity map을 준비한다.
10. `P-08`: F1 `257`/ordered `287` identity, S1 DC rating basis와 계측표를 닫는다.
11. `P-09`: 부품별 입고검사표와 `T-ESTOP-001~004 + T-ESTOP-005A` capture sheet를 미리 만든다.

K1/S0/S2/VO617A-3/P6KE/F2의 지정된 `A-01` 무전원 screen은 report 19에 기록했다.
6P cavity/crimp/retention과 complete assembly를 닫은 뒤
`T-ESTOP-001~004 -> T-ESTOP-005A -> lifted single motor 5~10% -> T-ESTOP-007 -> dual
drivetrain -> 1 m odometry` 순서를 지킨다. `FM-ESTOP-014`와
`T-ESTOP-005B`는 지우지 않고 post-MVP residual-risk V-cycle로 추적한다.

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
- [x] current logic-board power/back-power measurement
- [ ] final K1 downstream motor-rail back-power/rail-off measurement
- [ ] first motor no-load report
- [x] motor-off encoder voltage, dual count와 speed telemetry evidence
- [ ] powered encoder noise와 external speed evidence
- [ ] dual drivetrain low-speed report
- [x] motor-disconnected timeout/DISARM/software-fault output-zero functional evidence
- [x] active DISARM MCU-pin first shutdown-latency baseline
- [x] motor-disconnected active timeout, software-fault next-pulse/latch와 reset-marker boot report
- [x] external-reset motor-input floating FAIL 발견과 signal별 `10 kΩ` pull-down 재시험 PASS
- [x] RevB/permanent motor-input pull-down continuity와 safe-restore report
- [x] P-04B no-CMD/accepted-CMD/timeout/direct-PC7 active-to-latched UART runtime subset
- [ ] P-04B active reset 거부 ERR+TEL pair와 release 뒤 explicit reset 성공 same-run evidence
- [x] P-04B all-hooks-`0U` isolated STM32/ESP32 build와 artifact hash 기록
- [ ] P-04B all-hooks-`0U` 양 board reflash와 ARM/CMD TX 0 no-command safe runtime
- [ ] integrated physical E-stop `T-ESTOP-001~004 + T-ESTOP-005A`와 actual motor-stop report
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
- ESP32-S3는 Final MVP production command ingress이고 PC는 필요 시 ESP32 upstream client다. 어느 쪽도 STM32 safety를 우회할 수 없다.
- hardware bring-up을 무전원, signal-only, no-load, lifted, ground 단계로 분리했다.
- command-level zero와 physical output zero를 구분해 검증한다.
- 성공 화면뿐 아니라 계측값, fault와 residual risk를 증거로 남긴다.

## 관련 문서

- [`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md)
- [`../progress/2026-08-25_progress.md`](../progress/2026-08-25_progress.md)
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
