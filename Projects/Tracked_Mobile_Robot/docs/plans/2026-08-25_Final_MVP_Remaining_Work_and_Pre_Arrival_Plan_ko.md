# Final MVP Remaining Work And Pre-Arrival Plan

## 문서 상태

- 기준일: 2026-08-25
- 상태: `ACTIVE / P-04A + ALL-SELECTED-INCOMING UPDATE 2026-08-29`
- 목적: Final MVP까지 남은 작업의 임계 순서와 잔여 부품 대기 중 병렬 작업을 분리한다.
- 현재 진행 기록: [`../progress/2026-08-29_progress.md`](../progress/2026-08-29_progress.md)
- 날짜별 실행 일정: [`2026-08-26_Pre_Arrival_Schedule_ko.md`](2026-08-26_Pre_Arrival_Schedule_ko.md)
- 상위 계획: [`00_Project_Master_Plan_To_Final_MVP_ko.md`](00_Project_Master_Plan_To_Final_MVP_ko.md)

사용자가 전달한 현재 배송 예상은 2026년 9월 중순이다. 개별 부품의 실제 도착일과 상태는
입고 전 확정하지 않는다. 배송 완료는 시험 PASS가 아니며, 입고 검사와 motor-disconnected
통합 시험이 끝나야 actual motor 단계로 이동할 수 있다.

### 2026-08-29 current execution update

현재 continuation은 [`../progress/2026-08-29_progress.md`](../progress/2026-08-29_progress.md),
[P-04A report 22](../verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md)와
[incoming report 19](../verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md)를 따른다.

| State | Items | Current consequence |
| --- | --- | --- |
| UNPOWERED COMPONENT SCREEN PASS | K1 exact parts/`89.5 ohm`/NO/isolation, S0 2NC/latch, S2 momentary-NO, VO617A-3 diode/isolation, P6KE x3 identity/gross-short, F2 continuity/movement | 해당 component-level A-01 subset은 반복하지 않고 powered/integrated Gate로 trace |
| RECEIVED / UNASSEMBLED | Loose 6P waterproof connector kit + separate 18 AWG | Mating-face numbering, qualified first-article crimp, 6x6 continuity/isolation, seal/retention 필요 |
| ORDERED / NOT RECEIVED | `VH-30J`/`WX-03B` tooling | Complete 6P assembly와 powered coil test는 first-article crimp까지 blocked |
| P-04A COMPLETE | Applied left/right signed PWM TEL -> ESP parser/log, current `27/27`, target UART + hook-0 safe runtime | P-04B reason/age와 P-05 battery로 진행; measured PWM/actual motor 주장 금지 |

다음 카페 세션은 P-04B reason/command-age telemetry, 다음 집 세션은 plate dry-fit과 6P cavity
orientation을 비파괴 기록한다. Tool 도착 뒤 spare 18 AWG terminal first-article crimp를 먼저
검증한다. 이 update가 아래 2026-08-27 도착 요약보다 우선한다.

### 2026-08-27 historical arrival update

이 절은 2026-08-27 당시의 partial-arrival snapshot이다. 현재 continuation은
[`../progress/2026-08-28_progress.md`](../progress/2026-08-28_progress.md)와
[`../verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md`](../verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md)를 따른다.

| State | Items | Current consequence |
| --- | --- | --- |
| USER-REPORTED RECEIVED / INCOMING OPEN | K1 assembly, S0, VO617A-3, F2 fuse/holder, 6P waterproof harness/18 AWG | 해당 subset의 `A-01` 무전원 입고검사를 지금 시작할 수 있음 |
| ORDERED / NOT RECEIVED | S2 `ABW110G`, `P6KE16CA-E3/54` x3 | Complete nominal control path와 powered coil test는 계속 blocked |

도착 보고는 exact part/수량/각인, continuity, polarity, terminal map, fit 또는 retention PASS가
아니다. 실행 순서는 `received subset A-01 -> S2/P6KE arrival and remaining A-01 -> complete
integration -> T-ESTOP-001~004 -> T-ESTOP-005A`로 전환한다. 이 dated update가 아래의
“모든 부품 도착 전” 표현보다 우선한다.

## 이번 재계획의 핵심 결정

### 기존 4대단원은 유지한다

새 대단원을 추가하지 않는다.

1. 대단원 1: MCU 저수준 안전 검증 — 완료
2. 대단원 2: 전원과 Physical E-stop — 실물 부품 대기, 부분 완료
3. 대단원 3: 첫 실제 motor 구동 — 대단원 2 Gate 뒤
4. 대단원 4: dual drivetrain, ground motion과 odometry — 대단원 3 뒤

### Physical E-stop MVP와 단일고장 학습 범위를 분리한다

현재 RevB는 정상인 S2와 정상 6P harness 조건에서 manual re-enable 기능을 검증할 수 있지만,
S2 stuck-closed 또는 S2 pair short에서는 rail이 재인가될 수 있는 `FM-ESTOP-014` 한계가 있다.

따라서 시험 범위를 다음처럼 분리한다.

| Test | 범위 | MVP 관계 |
| --- | --- | --- |
| `T-ESTOP-005A` | 정상 부품과 사전 continuity PASS 조건에서 S0 차단, direct rail-off, release/power-restore 후 deliberate S2 전까지 rail OFF, firmware latch/reset/new ARM 확인 | `MUST / MVP BLOCKER` |
| `T-ESTOP-005B` | S2 stuck-closed와 6P S2-pair short fault injection에서 rail no-auto-reenable 확인 | `POST-MVP / RESIDUAL RISK` |

이 분리는 `FM-ESTOP-014`가 해결됐다는 뜻이 아니다. Final MVP는 다음과 같이만 주장한다.

```text
Mechanical-latching S0와 K1을 이용한 MCU-independent motor-energy cut을
정상 부품 조건의 기능 시험으로 검증했고, STM32의 독립적인 PWM-zero/latch/reset 경로와
lifted actual-stop evidence를 확보한 portfolio prototype이다.

S2 stuck/short 단일고장 내성, safety relay/force-guided contact와 PL/SIL 적합성은
검증하지 않았으며 post-MVP residual risk로 기록한다.
```

### 정상 motion command path는 아직 미구현이다

현재 STM32 `handle_cmd()`는 controlled output test hook이 enable되고 정확히
`vx_mmps=50`, `w_mradps=0`일 때만 고정 duty를 출력한다. 현재 hook은 `0U`이므로 정상
CMD는 검증·저장·ACK되지만 실제 좌우 motor request로 변환되지 않는다.

Final MVP에는 PID가 아니라 다음 최소 open-loop path가 필요하다.

```text
vx_mmps, w_mradps
-> left/right signed request
-> saturation + initial 5~10% cap
-> sign to DIR, magnitude to PWM
-> motor_output_set_raw()
```

실제 channel/vehicle-forward 상수는 첫 lifted single-motor mapping 뒤 확정한다.

## 전체 남은 작업의 임계 순서

아래 순서를 바꾸지 않는다. 단, `P-*` pre-arrival 작업은 부품 배송과 병렬로 수행한다.

| 순서 | Work package | 주요 작업 | 다음 단계 Gate |
| ---: | --- | --- | --- |
| 1 | `P-01~P-09` | firmware, 저전압, odometry, 기구와 시험 준비 | 각 항목 host/static/design evidence |
| 2 | `A-01` | K1/S0/S2/VO617/P6KE/F2/6P 등 입고·무전원 검사 | 형번, pin, resistance/continuity, fit PASS |
| 3 | `A-02` | E-stop control/sense path 무전원 조립 | short/cross-wire 없음, truth table PASS |
| 4 | `A-03` | motor-disconnected `T-ESTOP-001~004`, `005A` | nominal direct rail-off/latch/manual re-enable PASS |
| 5 | `A-04` | plate fit, 부품 위치 동결, AWG12/16 final harness | insulation, access, retention, back-power PASS |
| 6 | `A-05` | lifted single motor 5~10%와 `T-ESTOP-007` | current/drop/thermal/noise/mapping/actual stop PASS |
| 7 | `A-06` | production mapper 실제 mapping 반영, low-voltage runtime | final command path와 voltage stop PASS |
| 8 | `A-07` | dual motor lifted | 좌우 독립·동시·회전 조합과 stop PASS |
| 9 | `A-08` | 저속 ground motion | forward/backward/rotation와 fault stop PASS |
| 10 | `A-09` | 1 m odometry | calibration과 별도 validation evidence PASS |
| 11 | `A-10` | final regression과 portfolio release | all-hooks-0U, build/hash/log/photo/video/matrix/README |

## 부품 도착 전 수행 작업

### `P-01` 범위와 source ownership 동결

상태: `COMPLETED / ACCEPTED — ADR-015 (2026-08-26)`

1. Final MVP의 유일한 production external command ingress는 ESP32-S3다.
2. Production link는 `ESP32 UART1 GPIO17/GPIO18 <-> STM32 USART1 PA9/PA10`이다.
3. USART2 PA2/PA3는 bench debug/encoder logger와 historical PC-first evidence로만 사용하며
   production command RX를 받지 않는다.
4. PC interactive control이 필요하면 `PC -> ESP32 -> STM32`로 추가하며, direct dual-owner
   구조는 만들지 않는다.
5. STM32는 parser, timeout, motor permission과 PWM/DIR의 최종 authority를 유지한다.

완료 증거:

- architecture/README에 final owner 한 줄
- conflict 없는 UART path
- command-source loss 시 output/stored command zero -> `DISARMED` -> new `ARM` + new `CMD` 정책
- [`../../01_System_Architecture/19_Architecture_Decision_Record_ko.md`](../../01_System_Architecture/19_Architecture_Decision_Record_ko.md)의 ADR-015 `Accepted`
- Current source에서 protocol RX는 `huart1` 하나, USART2 `HAL_UART_Receive*`는 0건이고
  당시 host/static discovery `20/20`, P-02B `23/23`, P-02C-1 `24/24` checkpoint를 보존한다.
  P-02C-2 production caller checkpoint는 `25/25`, P-03 timeout contract까지 포함한 current
  canonical은 `26/26 PASS`다.

Evidence boundary:

- P-01은 architecture/ownership decision 완료다. P-03 source/static/full-build도 ADR-015
  recovery와 일치하며 motor/LiPo-disconnected target runtime은 아직 남아 있다.

### `P-02` production open-loop command mapper

상태: `P-02A/P-02B/P-02C-1/P-02C-2 COMPLETE / TARGET RUNTIME PENDING`

구현 범위:

- `vx,w`를 좌우 signed request로 변환하는 pure function
- zero, straight, reverse, left/right rotation 조합
- 입력 range와 output saturation
- initial duty cap parameter
- sign/DIR와 magnitude/PWM 분리
- actual channel mapping 전 provisional 상수의 명시
- host/static unit vectors
- production `handle_cmd()`의 validation/ARMED/3x E-stop/mapper/output/success-only commit+ACK 연결
- mapper/output failure의 stop-all, stored `vx/w` zero, ERR, return 경로

완료 증거:

- P-02C-2 당시 canonical `21 + 2 + 2 = 25/25 PASS`
- 32-object forced ARM build exit `0`, compiler/linker warning/error 진단 0건
- mapper와 signed adapter의 nonzero ELF linkage

Evidence boundary:

- P-02 checkpoint 자체에는 새 flash/board runtime, PWM/DIR waveform 또는 actual motor evidence가 없었다.
  후속 P-03 target runtime과 P-04A TEL runtime은 각각 별도 보고서에서 닫았다.
- channel/forward polarity는 provisional이다. TEL applied PWM placeholder는 P-04A에서 연결했지만
  measured physical feedback은 아니다.
- timeout-to-`DISARMED` source/static/full-build와 target runtime은 후속 P-03/report 20~21에서 닫았다.

금지:

- 부품 도착 전 actual motor enable
- test hook을 켠 상태로 production baseline 저장
- PID, IMU fusion 또는 track-slip compensation 추가

### `P-03` timeout과 motion-recovery 구현·검증

상태: `COMPLETE — 300 ms TARGET SUBVECTOR + CANONICAL 500 ms ACCEPTANCE / MOTOR-LIPO-DISCONNECTED SCOPE`

P-03A/P-03B source는 다음 ADR-015 정책과 requirement를 일치시켰다.

ADR-015 Accepted baseline:

```text
CMD timeout
-> motor_output_stop_all()
-> stored command zero
-> DISARMED
-> accepted ARM + subsequently processed valid CMD required
```

여기서 구현된 것은 state gate와 stored-command 자동 복원 방지다. Sequence/session freshness,
RX queue purge와 transport anti-replay는 P-03 구현·검증 범위가 아니다.

구현·검증 증거:

- `command_timeout_enforce()`를 RX byte 처리 전에 실행한다.
- deadline 초과 시 stop-all -> stored `vx/w` zero -> `DISARMED` 순서를 강제한다.
- accepted `ARM`은 stored/output zero를 유지하고 default `300 ms`와 current tick으로
  first-CMD window를 다시 시작한다.
- timeout 자체는 ACK/ERR, error count 또는 `last_seq`를 만들지 않는다.
- canonical host/static `22 + 2 + 2 = 26/26 PASS`
- 32-object forced ARM build exit `0`, warning/error 진단 0건, ELF
  `text=29268`, `data=172`, `bss=2832`
- 2026-08-28 current-default 300 ms target UART/PWM에서 timeout-to-`DISARMED`, CMD-only 거부,
  ARM-only old-command 미복원/expiry, fresh ARM+CMD recovery와 final DISARM PASS
- canonical `timeout_ms=500` same-run UART+MCU control-net acceptance와 post-test hook-0
  UART/D0~D3 safe restore PASS

Evidence boundary:

- Exact controlled binary linkage, reset-net 동시성, clean electrical cold-start와 actual motor stop은
  P-03/report 20~21의 증거 범위 밖이다.
- Sequence/session anti-replay와 exhaustive timeout sweep은 별도 요구사항으로 남는다.

### `P-04` 실제 telemetry 값 연결

상태: `P-04A COMPLETE / P-04B READY / BATTERY MOVED TO P-05`

P-04A에서 hard-coded `left_pwm/right_pwm=0`을 motor-output software cache의 signed permille과
연결하고 ESP32 parser/log까지 확장했다. Current canonical `27/27`, STM32 build 0 errors/0 warnings,
positive symmetric `50/50`, timeout/ARM-only/DISARM `0/0`과 hook-0 safe UART restore를 PASS했다.
이는 measured PWM feedback이 아니며 reverse/asymmetric sign과 actual motor는 미검증이다.

MVP telemetry 우선순위:

1. `[COMPLETE — P-04A]` applied left/right signed PWM target
2. `[P-04B]` E-stop active/latch/reset-rejected 식별
3. `[P-04B]` command age 또는 timeout 상태
4. `[P-05]` battery millivolt
5. `[EXISTING PASS]` left/right CPS

### `P-05` battery ADC와 low-voltage 설계

상태: `DESIGN READY / TARGET RUNTIME PENDING`

1. 12.6 V full-charge에서 STM32 ADC limit 아래인 divider를 계산한다.
2. 입력 보호, divider current, ADC source impedance와 filtering을 검토한다.
3. `batt_mv` 변환과 host test를 구현한다.
4. warning, motor-stop, hysteresis/debounce 수치를 근거와 함께 확정한다.
5. 실제 전압 sweep와 3S cell pre/post 확인은 별도 target evidence로 남긴다.

부품과 계측 경로가 준비되지 않으면 계산·코드·host test까지만 수행하고 electrical PASS로
표시하지 않는다.

### `P-06` odometry 최소 구현과 1 m 시험 준비

상태: `READY`

MVP는 full pose/IMU fusion이 아니라 다음만 구현한다.

- accumulated left/right count 보존 또는 telemetry
- `1560 counts/output rev` 기준의 provisional distance calculation
- effective track travel/count parameter
- calibration run과 validation run 분리
- 1 m actual/estimated/absolute/percentage error 계산
- repeat count, surface, battery voltage와 payload 기록 양식

### `P-07` 기구·하네스 preflight

상태: `PLATE USER-REPORTED RECEIVED / PHYSICAL FIT PENDING`

1. 2026-08-26 사용자는 custom PC adapter plate 수령을 확인했다. 집 `H-01`에서 actual plate와
   RevB source의 외곽·두께·hole pattern identity, chassis fit과 module fit을 기록한다.
2. K1/K2/F1/F2/MDD10A와 만능기판의 후보 위치를 도면에 배치한다.
3. LiPo strap/tray, 천공·마찰 방지와 XT60 strain relief를 설계한다.
4. S0와 S1을 track 접근 없이 누를 수 있는 위치로 둔다.
5. motor/power wire와 encoder/UART wire routing을 분리한다.
6. track tension, 좌우 정렬, hand rotation binding, sprocket/fastener 점검표를 만든다.
7. lifted fixture와 ground exclusion zone을 정한다.

실제 terminal 방향과 굽힘 반경이 확정되기 전 AWG12/16 wire를 final length로 절단하지 않는다.
수령 plate를 확인하기 전 추가 drilling 또는 재주문도 진행하지 않는다.

### `P-08` F1/S1와 측정 방법 정리

상태: `READY`

- 입고 fuse의 `257/32V/10` marking과 주문 `0287010.PXCN`의 공식 identity/time-current 자료 대조
- S1 exact model/DC rating 확인 또는 prototype loaded voltage-drop/thermal release 기준 작성
- start/steady current 측정 방법과 instrument range 확정
- F1/S1/K1/MDD10A 전후 voltage-drop 측정점 정의
- ambient, duration, component temperature 기록표와 중지 조건 작성

영구 current sensor 구매는 MVP 필수가 아니다. 적절한 외부 계측으로 수치 evidence를 남기면 된다.

### `P-09` arrival-day test packet 준비

상태: `READY`

미리 준비할 표:

- incoming marking/photo checklist
- K1/K2 coil/contact resistance/continuity table
- S0-A/S0-B/S2 contact truth table
- 6P mating-face cavity map과 non-adjacent isolation matrix
- VO617 input/output voltage table
- `T-ESTOP-005A` initial/release/power-restore/manual-reenable table
- rail-off/back-power table
- single-motor current/drop/temperature/noise table

## 부품 도착 뒤 상세 순서

### `A-01` incoming inspection

LiPo와 motor를 분리하고 전원을 모두 끈다.

1. exact marking과 포장/납품 trace 확인
2. coil resistance와 무전원 contact state
3. terminal, seal, socket, housing과 wire fit
4. connector cavity 100% mapping과 isolation
5. 손상, 부식, 변형과 retention 확인

### `A-02` E-stop 무전원 조립

```text
F2 -> S0-A NC -> [S2 NO OR K2-HOLD-NO] -> K2 coil
K2 pole 2 -> K1 coil permission
5 V -> S0-B NC -> VO617 LED -> 0 V
3.3 V pull-up -> VO617 transistor -> PC7 ESTOP_SENSE
```

P6KE clamp, pin direction과 direct PC7-GND 임시 jumper 제거를 확인한다.

### `A-03` motor-disconnected powered E-stop

`T-ESTOP-001~004` 뒤 `T-ESTOP-005A`만 실행한다.

필수 PASS:

- initial K1 rail OFF
- deliberate S2 뒤에만 K2/K1 ON
- S0 press에서 K1/source feed OFF와 PC7 `FAULT`
- S0 release/control-power restore만으로 healthy S2 조건의 rail 복귀 없음
- physical release 뒤 firmware latch 유지
- explicit reset은 `DISARMED`만 복원
- new ARM/CMD 전 PWM zero
- K1 OFF에서 USB/buck/GPIO back-power 없음

`T-ESTOP-005B`는 실행하지 않아도 MVP를 막지 않지만 residual risk로 계속 기록한다.

### `A-04~A-10` motor, ground와 closeout

1. plate fit과 final harness release
2. lifted single motor 5~10% pulse
3. channel/side/direction, current, voltage drop, thermal, powered encoder/UART noise
4. DISARM/timeout/UART-loss/S0 actual stop
5. low-voltage target verification
6. dual lifted, then low-speed flat-ground motion
7. 1 m calibration/validation
8. all-hooks-`0U` final build/hash/flash/cold-boot regression
9. matrix, BOM, README, photos, raw logs와 short demo 갱신

## 중지 조건

- 전원이 연결된 상태에서 resistance/continuity를 측정하려는 경우
- K1/S0/S2/6P pin map 또는 contact truth table이 불확실한 경우
- direct PC7-GND jumper가 남은 채 VO617 path를 연결하려는 경우
- clamp/internal suppression 확인 전 K1/K2 coil을 energize하려는 경우
- K1 OFF인데 downstream motor rail이 예상보다 올라가는 경우
- final fuse/wire/terminal fit 또는 polarity가 불확실한 경우
- boot/reset/DISARM/timeout/E-stop에서 PWM zero가 아닌 경우
- 비정상 전류, 전압강하, 발열, 냄새, spark, reset 또는 encoder runaway count가 있는 경우
- track/robot이 fixture에서 움직이거나 exclusion zone을 침범하는 경우

## 배송 대기 중 하지 않을 작업

- actual motor-energy 인가
- incomplete E-stop을 Physical E-stop PASS로 판정
- `FM-ESTOP-014` 단일고장 내성 또는 산업 안전 인증 주장
- CAN, FreeRTOS, LL, ROS 2, LiDAR/Nav2로 scope 확장
- actual-part fit 전 final high-current wire 절단·영구 crimp
- host/static PASS를 target electrical evidence로 대체

## 일정 판단

부품이 2026년 9월 중순에 정상 도착해도 입고·조립·motor-disconnected 시험에 추가 시간이
필요하다. 추가 오배송/불량이 없다는 조건에서 첫 actual motor evidence는 9월 하순이 현실적인
최초 시점이며, Final MVP는 이후 dual/ground/odometry 결과에 따라 9월 말~10월 초를 목표로 한다.
