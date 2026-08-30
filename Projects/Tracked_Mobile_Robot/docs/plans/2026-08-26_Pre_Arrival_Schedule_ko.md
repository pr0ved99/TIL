# 2026-08-26 Pre-Arrival Schedule

## 문서 상태

- 일정 구간: 2026-08-26 ~ 2026-09-15
- 상태: `ACTIVE / ALL-SELECTED-PARTS-ARRIVED TRANSITION 2026-08-30`
- 상위 실행계획: [`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md)
- 현재 진행기록: [`../progress/2026-08-30_progress.md`](../progress/2026-08-30_progress.md)
- 일정 수립 기록: [`../progress/2026-08-26_progress.md`](../progress/2026-08-26_progress.md)
- 기준: 2026-08-30 K1/S0/S2/VO617A-3/P6KE/F2의 지정된 무전원 component screen은 report
  19에 기록했다. 6P는 loose kit+별도 18 AWG로 미조립이다. `VH-30J`/`WX-03B` crimp-tool
  set도 사용자 보고로 도착했지만 exact 구성/상태, die 형상과 first-article crimp는 미검증이다.

이 일정은 평일 하루 `2~3시간`의 집중 작업을 기준으로 한다. 토요일은 필수 신규 기능을
넣는 날이 아니라 밀린 검증·수정용 `1~2시간 buffer`, 일요일은 원칙적으로 휴식이다.
사용자가 더 오래 작업할 수 있더라도 다음 날짜의 Gate를 건너뛰어 actual motor 단계로
이동하지 않는다.

## 2026-08-30 All-selected-parts-arrived transition

| 구분 | 부품/작업 | 현재 처리 |
| --- | --- | --- |
| Unpowered screen recorded | K1 exact parts/`89.5 ohm`/NO/isolation, S0 2NC/latch, S2 momentary-NO, VO617A-3 diode/isolation, P6KE x3 identity/gross-short, F2 continuity/movement | Report 19 범위를 보존하고 powered/integrated 증거와 구분 |
| Received / unassembled | Loose 6P connector kit + separate 18 AWG | Mating-face numbering, qualified first-article crimp, 6x6 continuity/isolation, seal/retention 필요 |
| User-reported received / unverified | `VH-30J` set ordered with `WX-03B` | Exact set/die marking과 tool condition 확인 -> spare 18 AWG terminal first article -> pull/continuity/housing retention |

배송 대기는 더 이상 blocker가 아니다. 현재 blocker는 압착 공구의 실제 적합성 검증과 6P 첫
압착/조립이며, 이를 통과하기 전 complete control-path assembly, powered K1/K2와
`T-ESTOP-001~005A`를 시작하지 않는다. Firmware는 P-04B reset runtime/안전 복구를 집에서
닫은 뒤 P-05로 이동한다.

## 2026-08-28 Historical received-subset screen transition

| 구분 | 부품/작업 | 현재 처리 |
| --- | --- | --- |
| Unpowered screen recorded | K1 exact parts/`89.5 ohm`/NO/isolation, S0 2NC/latch, VO617A-3 diode/isolation, F2 continuity/movement | Report 19 범위를 보존하고 powered/integrated 증거와 구분 |
| Received / unassembled | Loose 6P connector kit + separate 18 AWG | Mating-face numbering을 먼저 기록; tooling 도착 뒤 spare terminal first-article와 6x6 검사 |
| Not received | S2 `ABW110G`, `P6KE16CA-E3/54` x3, crimp tooling | Complete control path, powered K1/K2와 `T-ESTOP-001~005A` 계속 금지 |

당시 다음 작업 장소는 **집 우선**이었다. `H-02` P-03 motor/LiPo-disconnected target runtime을 닫고,
시간이 남으면 `H-01` plate dry-fit과 6P molded cavity orientation을 기록한다. P-04 TEL source
변경은 P-03 runtime 뒤 카페 세션에서 시작한다. 아래 2026-08-27 transition은 역사적 도착
상태로 보존한다.

## 2026-08-27 Historical Partial-Arrival Transition

| 구분 | 부품 | 현재 처리 |
| --- | --- | --- |
| User-reported received | K1 assembly, S0, VO617A-3, F2 fuse/holder, 6P waterproof harness/18 AWG | LiPo/motor/모든 전원을 분리한 `A-01` 무전원 입고검사를 즉시 시작할 수 있음 |
| Already received and screened | K2 `TX2-12V` x2, F1 holder/fuse | 기존 무전원 evidence 보존; 아직 powered release 아님 |
| Not received | S2 `ABW110G`, `P6KE16CA-E3/54` x3 | 도착 뒤 같은 `A-01` 검사; 그 전 complete control-path assembly와 coil energize 금지 |

Partial arrival로 received subset의 `A-01`만 일정에 앞당긴다. S2가 없으므로 nominal three-wire
re-enable path와 `T-ESTOP-005A`를 완성할 수 없고, P6KE/internal-suppression 확인 전에는
K1/K2 coil을 energize하지 않는다. Firmware `P-02` 이후 작업은 무전원 입고검사와 병렬로
계속한다.

`P-01~P-09`와 통합 회귀의 총 예상 작업량은 약 `32~46 focused hours`다. 이는 사용자가
firmware를 직접 타이핑하고, 저장된 파일 재검토와 관련 시험까지 수행하는 시간을 포함한
계획값이며 실제 부품 도착일이나 실패 수정 시간에 따라 달라질 수 있다.

## 일정 목표

9월 15일까지 다음 상태를 만드는 것이 목표다.

```text
production command path와 timeout policy가 host/static 및 motor-disconnected board 범위에서 검증됨
+ 필요한 TEL/battery/odometry software 준비가 완료됨
+ received adapter plate identity/fit용 H-01 packet과 mechanical/harness preflight가 준비됨
+ received subset의 A-01 기록과 remaining S2/P6KE 도착 즉시 사용할 시험표·중지 조건이 준비됨
```

이 종료선은 Physical E-stop PASS, K1 rail-off PASS 또는 actual motor PASS가 아니다.

## 우선순위

| 등급 | Work package | 이유 |
| --- | --- | --- |
| `Priority A` | `P-01`, `P-02`, `P-03`, `P-07`, `P-08`, `P-09` | 부품 도착 직후 hardware Gate와 이후 motor command를 막는 항목 |
| `Priority B` | `P-04` | 실제 applied state와 시험 로그의 해석 가능성을 확보 |
| `Priority C` | `P-05`, `P-06` | Final MVP 필수지만 부품 입고검사 자체는 막지 않음; 일정 지연 시 hardware 입고검사와 병렬 지속 |

## 작업 장소 분리

여기서 `카페`는 노트북만 있고 STM32/ESP32/부품/DMM/logic analyzer가 없는 상태를 뜻한다.
노트북에서 compile하는 `build`는 카페 작업이지만, board를 연결하는 `flash/runtime`은 집 작업이다.

| Work package | 카페에서 완료할 범위 | 집에서 완료할 범위 |
| --- | --- | --- |
| `P-01` | command owner, USART1/USART2 역할, source-loss 규칙 문서화 | 없음 |
| `P-02` | mapper 수식/interface, source 구현, host/static vectors, STM32 build | STM32 flash, motor/LiPo-disconnected UART와 PWM/DIR target regression |
| `P-03` | `[P-03A/P-03B COMPLETE]` timeout/recovery source, host/static `26/26`와 32-object build | STM32+ESP32에서 timeout -> `DISARMED` -> new ARM/CMD runtime |
| `P-04` | TEL schema/source mapping, STM32/ESP32 source 수정, parser/format test와 양 firmware build | STM32+ESP32 end-to-end TEL runtime; 필요 시 logic analyzer와 applied output 대조 |
| `P-05` | divider/protection 계산, threshold/hysteresis 근거, pure conversion과 host tests | divider가 실제 구성된 뒤 안전한 ADC voltage sweep; LiPo 직접 ADC 연결 금지 |
| `P-06` | count-to-distance math, host tests, 1 m calibration/validation 기록표 | encoder hand-turn target check와 이후 실제 1 m 시험 |
| `P-07` | received plate source audit, mounting boundary, routing/checklist와 fit sheet 작성 | chassis/carrier와 도착 부품 치수·사진 확보, dry fit, track/fixture/접근성 확인 |
| `P-08` | F1 `257/287` 공식자료 대조, S1 DC basis 조사, current/drop/thermal 계측계획 | marking/continuity 재확인과 이후 DMM/온도/부하 계측 |
| `P-09` | 모든 빈 시험표, cavity map 양식, 중지 조건과 arrival packet 작성 | 부품 도착 뒤 실제 marking/pin/cavity/측정값 기입 |

따라서 카페에서 완전히 닫을 수 있는 것은 `P-01`이다. `P-02~P-09`도 대부분의 설계·코드·host
test·시험표 작업은 카페에서 진행할 수 있지만, 해당 항목의 board/electrical/physical evidence까지
PASS하려면 집 작업이 필요하다.

### 권장 home checkpoint

집 작업은 매일 조금씩 섞지 않고 다음 checkpoint로 묶는다.

1. `H-01 Mechanical Capture`: `P-07`용 chassis/carrier/도착 부품 치수와 사진, terminal 접근성,
   track/fixture 상태를 한 번에 기록한다.
2. `H-02 Command Runtime`: `P-02/P-03`의 host/static/build가 모두 PASS한 뒤 STM32+ESP32를
   flash하고 motor/LiPo-disconnected UART/timeout 회귀를 한 번에 수행한다.
3. `H-03 Telemetry Runtime`: `P-04` parser/build PASS 뒤 STM32+ESP32 end-to-end TEL만 확인한다.
4. `H-04 Arrival Bench`: 지금 도착한 subset의 무전원 incoming inspection을 먼저 수행하고,
   S2/P6KE 도착 뒤 잔여 incoming을 같은 양식으로 닫는다.

`H-02/H-03`는 source가 준비되면 같은 집 세션으로 합칠 수 있다. 준비되지 않은 source를 서둘러
flash하기 위해 카페 작업을 생략하지 않는다.

## 날짜별 실행 일정

2026-08-26 사용자가 custom PC plate 수령을 확인해 기존 08-27~28 plate 주문 일정은
삭제했다. Plate physical fit은 다음 집 `H-01`로 이동하고, 확보된 이틀은 카페에서 `P-02`를
앞당기는 데 사용한다.

| 날짜 | 작업 | 예상 집중시간 | 그날의 완료 조건 |
| --- | --- | ---: | --- |
| **08-26 수** | `P-01 [COMPLETED]` command owner와 UART ownership 동결 | 1.5~2 h | ESP32/PC 역할, 단일 motion owner와 source-loss timeout 규칙을 ADR-015 `Accepted`로 확정 |
| **08-27 목** | `P-02A/P-02B [COMPLETED]` Git checkpoint, mapper source/build와 independent vectors/static source contract | 2~3 h | canonical `23/23 PASS`; C native execution/target runtime이 아니라는 evidence boundary 명시 |
| **08-28 금** | `P-02C-1/P-02C-2 [COMPLETED EARLY 08-27]` signed adapter와 production caller source/static/build | 1~2 h | historical `24/24`, P-02C-2 `25/25`, 32-object forced build와 nonzero ELF linkage PASS; target runtime 경계 기록 |
| **08-29 토** | Week 1 buffer | 0~2 h | `P-01/P-02` 누락 보완만 수행; PASS면 휴식 |
| **08-30 일** | 휴식 | - | 작업 없음 |
| **08-31 월** | `[COMPLETED EARLY 08-27] P-03A` timeout 뒤 `DISARMED`, accepted ARM + valid CMD state recovery 구현 | 완료 | pre-RX stop/stored-zero/DISARMED와 ARM default 300 ms window source/static PASS; transport freshness/anti-replay 제외 |
| **09-01 화** | `[COMPLETED EARLY 08-27] P-03B` timeout recovery regression과 full build | 완료 | all-hooks-`0U`, canonical `26/26`, 32-object build exit 0/진단 0건 |
| **09-02 수** | `P-02/P-03` 통합 target 검증 | 2~3 h | ESP script ARM->CMD cadence를 300 ms 미만으로 조정한 뒤 motor/LiPo-disconnected board UART/PWM 회귀 PASS |
| **09-03 목** | `P-04A` TEL schema와 applied left/right request/PWM, E-stop latch, command-age source 정의 | 2~3 h | 실제 runtime source와 아직 `TARGET PENDING`인 field를 구분한 mapping 표 완성 |
| **09-04 금** | `P-04B` STM32 TEL/ESP32 parser 연동과 regression | 2~3 h | parser/format test와 motor-disconnected UART runtime에서 구현된 field의 일관성 확인; `batt_mv` 실측 source는 `P-05`까지 pending |
| **09-05 토** | Week 2 buffer | 0~2 h | 실패 vector 수정·재검증 또는 evidence 정리; PASS면 휴식 |
| **09-06 일** | 휴식 | - | 작업 없음 |
| **09-07 월** | `P-05A` battery divider/protection, ADC scaling과 low-voltage threshold/hysteresis 설계 | 2~3 h | 12.6 V worst case, ADC margin, resistor 후보, warning/stop/recovery 수치와 근거 기록 |
| **09-08 화** | `P-05B` `raw ADC -> batt_mv` pure conversion과 low-voltage state host tests | 2~3 h | boundary/hysteresis/debounce vectors PASS. 실제 voltage sweep는 `TARGET PENDING` 유지 |
| **09-09 수** | `P-06A` count-to-distance 최소 odometry 구현·host tests | 2~3 h | 1560 count/rev 기반 zero/forward/reverse/wrap/누적거리 vector PASS |
| **09-10 목** | `P-06B` 1 m calibration/validation 기록표 | 2~3 h | 반복 횟수·surface·battery/payload 기록 양식 완성 |
| **09-11 금** | `P-08` F1 `257`/ordered `287`, S1 DC basis와 current/drop/thermal 측정계획 | 2~3 h | 식별 경계, 계측점, instrument range, duration와 stop criteria 완성 |
| **09-12 토** | Week 3 buffer + `P-09A` arrival sheet 초안 | 0~2 h | incoming/continuity/cavity/VO617/rail-off 빈 표 준비 |
| **09-13 일** | 휴식 | - | 작업 없음 |
| **09-14 월** | `P-09B` arrival-day packet + pre-arrival closeout | 2~3 h | 005A/single-motor sheet와 미완료 목록 준비 |
| **09-15 화** | Schedule buffer / arrival state refresh | 0~2 h | 실제 배송·입고 상태와 unresolved 목록을 한 번 갱신 |

## Milestone Gate

| Milestone | 목표일 | PASS 조건 |
| --- | --- | --- |
| `M0 Scope/Mechanical Ready` | 08-26 | `P-01` 완료, received plate state 정정과 H-01 fit packet 준비 |
| `M1 Production Command RC` | 09-02 | `P-02/P-03` host/static + build + motor-disconnected board regression PASS |
| `M2 Observable Runtime` | 09-04 | `P-04` TEL/parser/runtime consistency PASS |
| `M3 Battery/Odometry Design RC` | 09-10 | `P-05/P-06` calculation·host tests·target-pending boundary 완료 |
| `M4 Arrival Ready` | 09-14 | `P-08/P-09`와 모든 incoming/test sheet 준비, unresolved item 목록 1개로 통합 |

## 매 작업일 공통 절차

```text
실제 저장 파일 재확인
-> 오늘 바꿀 requirement/test vector 1개 고정
-> 작은 code block 또는 문서 단위 작업
-> 저장 파일 재검토
-> 관련 host/static test
-> 필요한 날만 build/board motor-disconnected regression
-> hook 0U, evidence boundary와 다음 시작점을 기록
```

한 작업일에 `P-02`, `P-03`, `P-04`를 동시에 수정하지 않는다. 실패 시 다음 기능으로 넘어가지
않고 해당 날짜 또는 토요일 buffer에서 원인·수정·회귀를 닫는다.

## 배송 변동 대응

### 부품이 9월 15일보다 일찍 도착한 경우

2026-08-27 K1/S0/VO617A-3/F2/6P-18 AWG에 대해 이 전환 규칙이 발동됐고, 지정된 received
subset의 `A-01 incoming inspection`은 2026-08-28 report 19 범위에서 완료됐다. 현재는
motor/LiPo-disconnected P-03 target runtime과 mechanical dry-fit을 병렬로 진행할 수 있지만,
S2/P6KE 도착·검사 전 complete `A-02` control-path assembly와 powered coil test는 허용하지 않는다.

1. 진행 중 firmware 작업을 test PASS/all-hooks-`0U`인 safe checkpoint에서 멈춘다.
2. LiPo/motor를 분리하고 `A-01` incoming inspection만 먼저 수행한다.
3. Received subset incoming PASS 뒤에는 software 일정과 mechanical dry-fit만 병렬 진행한다.
   S2/P6KE 도착·incoming 전 complete `A-02` control-path assembly는 시작하지 않는다.
4. `T-ESTOP-001~004 + T-ESTOP-005A` 전에는 actual motor energy를 인가하지 않는다.

### 9월 15일까지 도착하지 않은 경우

1. 배송 상태만 갱신하고 완료되지 않은 `P-*`를 priority 순서로 계속한다.
2. `P-05/P-06` target test, portfolio diagram/BOM과 test automation을 보완한다.
3. CAN/FreeRTOS/ROS 2 등 새 범위를 시작하지 않는다.

## 일정 지연 시 축소 규칙

- 절대 미루지 않음: `P-01`, `P-02`, `P-03`, `P-07` received-plate fit, `P-08`, `P-09`
- 기능 범위를 줄여도 완료: `P-04`는 applied request/PWM + E-stop/timeout 식별부터 닫고 장식용 TEL은 미룬다.
- hardware 도착 뒤 병렬 지속 가능: `P-05` target sweep와 `P-06` 실제 1 m execution
- MVP 밖으로 유지: PID, IMU fusion, dual-owner UART, `T-ESTOP-005B`, CAN, FreeRTOS, ROS 2

## 잔여 배송·통합 Gate 전 중지 조건

- actual motor 또는 LiPo motor-energy path를 연결하려는 경우
- controlled output hook을 `1U`인 채 baseline/build 결과로 보존하려는 경우
- timeout/FAULT/E-stop에서 nonzero applied request가 남는 경우
- host/static PASS를 battery ADC 또는 Physical E-stop electrical PASS로 기록하려는 경우
- actual terminal 방향·bend radius 확인 전 final AWG12/16 절단·crimp를 하려는 경우
