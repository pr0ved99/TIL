# Physical E-stop FMEA

## 목적

이 문서는 Physical E-stop을 구성하는 K1 relay, S0 actuator, manual re-enable,
monitoring, wiring과 firmware의 failure mode가 local effect에서 system effect로 어떻게
전파되는지 분석한다.

정본 연결은 다음과 같다.

```text
SG-ESTOP-001 safety goal
-> Step 2 system boundary
-> HZ-ESTOP-001~012 hazard analysis
-> FM-ESTOP-001~023 FMEA
-> Step 5 safety requirements
-> Step 6 RevB circuit
-> T-ESTOP staged verification
```

Hazard 정본은
[`22_Physical_EStop_Hazard_Analysis_ko.md`](22_Physical_EStop_Hazard_Analysis_ko.md),
architecture 정본은
[`21_Physical_EStop_Architecture_ko.md`](21_Physical_EStop_Architecture_ko.md)다.

## 근거와 주장 경계

2026-08-10 이후 이 분석은 `FMEA-001`, `RISK-001`, `SAFE-CTRL-001`, `ESTOP-001`,
`VVT-001`을 `ADOPTED FORWARD BASIS`로 사용한다.

- [IEC 60812:2018](https://webstore.iec.ch/en/publication/26359)의 failure mode, local/global
  effect, detection, treatment와 maintenance 원칙을 프로젝트 규모에 맞게 적용한다.
- [ISO 13849-1:2023](https://www.iso.org/standard/73481.html)은 safety-related control
  system의 fail-safe, diagnostic와 single-fault 관점을 검토하는 참고 근거로만 사용한다.

부품 failure rate, duty cycle, contact life와 field data가 없으므로 숫자 RPN을 계산하지
않는다. 이 문서는 FMEA worksheet와 action priority를 사용하며 FMECA, PL/PLr, SIL,
diagnostic coverage 또는 표준 적합성을 주장하지 않는다.

## 분석 방법

### Effect direction

| Direction | Meaning |
| --- | --- |
| `SAFE-DIRECTION` | Motor energy가 제거되거나 motion이 금지되지만 availability가 떨어짐 |
| `DANGEROUS` | E-stop 차단, no-auto-restart 또는 상태 진단이 약화됨 |
| `MIXED` | 조건에 따라 safe trip 또는 thermal/transient hazard가 됨 |

### Detection class

| Class | Meaning |
| --- | --- |
| `D1` | Controller/runtime에서 직접 discrepancy를 검출할 수 있음 |
| `D2` | Startup/preflight 또는 정기 continuity/DMM 시험으로 검출 가능 |
| `D3` | 현재 구조에서 신뢰성 있게 검출되지 않음; 추가 진단 필요 |

`D1`은 safety-independent protection을 의미하지 않는다. STM32가 멈추면 ADC나 telemetry
진단도 함께 사라질 수 있다.

### Action priority

| Priority | Required timing |
| --- | --- |
| `P1` | RevB schematic 또는 motor-power energization 전에 설계/시험 action 필요 |
| `P2` | Lifted-motor 또는 ground test 전에 action 필요 |
| `P3` | Availability/maintenance 개선; final wiring release 전에 처리 |

Priority는 숫자 RPN의 대체 계산식이 아니라 hazard severity, detectability와 현재 test
sequence를 함께 고려한 engineering disposition이다.

## Function decomposition

| Function | Item/interface | Required behavior |
| --- | --- | --- |
| Motor-energy interruption | K1 main contact | Coil de-energized에서 `MOTOR_VBAT_SAFE` positive feed open |
| Stop command path | S0-A NC/control wiring | Press/open fault에서 K1 coil permission 제거 |
| Manual re-enable | S2 momentary NO + K2 two-contact seal-in/interlock | Release만으로 K1 energize 금지; deliberate action 뒤에만 energize |
| Physical-state monitoring | S0-B 5 V loop/opto/`ESTOP_SENSE` | Press/open/5 V-loss fault를 fail-safe input으로 표시 |
| Actual rail diagnostic | `MOTOR_VBAT_SAFE_SENSE` candidate | K1 expected-off와 downstream rail-high discrepancy 검출 |
| Software safety | STM32 latch/output gate | PWM zero, reset/ARM/CMD sequencing, discrepancy latch |
| Backup isolation | S1 main switch/battery connector | K1 failure 때 operator가 전체 source 제거 가능 |

`MOTOR_VBAT_SAFE_SENSE`는 이 FMEA에서 선택하는 diagnostic function name이다. Divider,
protection, threshold, ADC pin과 sampling logic은 Step 5~6에서 확정한다.

## FMEA worksheet

### K1 power-disconnect and coil path

| ID | Failure mode | Local / system effect | Hazard | Detection | Priority and required action |
| --- | --- | --- | --- | --- | --- |
| `FM-ESTOP-001` | K1 main contact welded/stuck closed | Coil OFF에도 motor rail이 battery에 연결; E-stop energy cut 상실 | `HZ-ESTOP-002`, `005` | S0-B만으로 `D3`; downstream rail sense/measurement 시 `D1/D2` | `P1`: DC rating/derating, fuse, `MOTOR_VBAT_SAFE_SENSE`, preflight rail-off test; S1 backup 유지 |
| `FM-ESTOP-002` | K1 main contact stuck open | Motor rail energize 불가; unexpected motion은 줄지만 availability 상실 | Operational only | `D1` rail-low while manual re-enable expected | `P3`: fault telemetry, connector/coil/contact inspection |
| `FM-ESTOP-003` | K1 contact high resistance/intermittent/bounce | Voltage drop, heating, arcing, intermittent reset/motion | `HZ-ESTOP-005`, `008` | `D2` voltage-drop/current/thermal measurement | `P1`: current rating, terminal torque/strain relief, temperature and rail-drop test |
| `FM-ESTOP-004` | Coil/control power open or K1 coil open | K1 drops/stays open; safe-direction trip, operation unavailable | `HZ-ESTOP-003`, `011` in moving/slope condition | `D1` downstream rail-low; continuity `D2` | `P2`: fault report, flat-surface restriction, controlled stop-distance test |
| `FM-ESTOP-005` | Coil/control node shorted to supply downstream of S0-A | S0-A open이 coil을 제거하지 못해 K1 stays energized | `HZ-ESTOP-002` | Current S0-B only `D3`; rail remains high after assertion `D1` | `P1`: routing/connector separation, fuse control branch, downstream rail discrepancy latch |
| `FM-ESTOP-006` | K1 coil short/driver short | Control fuse trip, wire/driver heat; K1 state indeterminate | `HZ-ESTOP-005` | Branch current/fuse/thermal `D2` | `P1`: coil current rating, branch protection, driver flyback rating, current-limited bring-up |
| `FM-ESTOP-007` | Flyback/clamp device open | Coil turn-off transient may damage driver/contact or upset logic | `HZ-ESTOP-008` | Scope transient `D2`; runtime may be intermittent | `P1`: rated clamp, layout review, coil-node transient capture |
| `FM-ESTOP-008` | Flyback/clamp device short or clamp too low | Short: coil cannot energize; overly slow decay: K1 drop-out delayed | `HZ-ESTOP-003`, `008` | Coil/rail timing capture `D2` | `P1`: do not approve plain diode by assumption; select clamp with datasheet and measured drop-out/rail decay |

### S0 actuator and manual re-enable path

| ID | Failure mode | Local / system effect | Hazard | Detection | Priority and required action |
| --- | --- | --- | --- | --- | --- |
| `FM-ESTOP-009` | S0-A stuck closed or control contact bypassed | Button press does not remove K1 coil permission | `HZ-ESTOP-002`, `007` | S0-B may show press while rail stays high `D1`; continuity `D2` | `P1`: independent contacts, rail discrepancy latch, press/open continuity test, no bypass jumper |
| `FM-ESTOP-010` | S0-A stuck open/control wire open | K1 cannot energize or drops; safe-direction stop | `HZ-ESTOP-011` on slope/edge | Rail-low and continuity `D1/D2` | `P2`: fail-safe response accepted; flat-surface operation and repair-before-reset rule |
| `FM-ESTOP-011` | S0-B stuck closed, opto transistor short or PC7 short-to-GND | STM32 falsely reads healthy while S0 is pressed/open | `HZ-ESTOP-001`, `007` | Compare S0-B with rail/K1 behavior; single path alone `D3` | `P1`: press/open test each startup session, discrepancy logic, protected/labeled sense wiring |
| `FM-ESTOP-012` | S0-B/opto LED loop open, 5 V loss or PC7 short-high | False E-stop/latch; motion unavailable, safe-direction | Availability; abrupt stop can contribute to `HZ-ESTOP-011` | GPIO state, loop current and continuity `D1/D2` | `P2`: fault code, no automatic clear, inspect wiring before reset |
| `FM-ESTOP-013` | S0-A/S0-B connectors swapped, crosswired or tied together | Coil voltage can overdrive the 5 V opto input, sense may control wrong path, both functions lost | `HZ-ESTOP-005`, `007`, `010` | Visual/continuity/voltage `D2` | `P1`: non-interchangeable/keyed connectors, distinct labels/colors, no-power pin-to-pin checklist |
| `FM-ESTOP-014` | S2 stuck closed, K2-HOLD/K2-K1 contact welded or unsafe cross-contact | S0 release 또는 power restore에서 K1가 자동 재인가될 수 있음 | `HZ-ESTOP-001` | Rail rises without valid re-enable edge `D1` if edge/rail monitored | `P1`: momentary S2, K2 separated control review, release-edge inhibit/discrepancy latch, firmware remains `DISARMED`; ground test prohibited on fault |
| `FM-ESTOP-015` | S2, K2 coil or K2 contact stuck open | Manual re-enable 실패; motor rail remains off | Operational only | `D1/D2` no rail after deliberate S2 action | `P3`: fault report, contact/coil inspection; do not bypass interlock |

### Monitoring and software path

| ID | Failure mode | Local / system effect | Hazard | Detection | Priority and required action |
| --- | --- | --- | --- | --- | --- |
| `FM-ESTOP-016` | `MOTOR_VBAT_SAFE_SENSE` false-low/open/divider fault | Welded K1 or backfeed가 off로 오판될 수 있음 | `HZ-ESTOP-002`, `006` | Compare upstream/downstream at powered self-test; otherwise `D3` | `P1`: input bias/plausibility, upstream comparison, DMM preflight; sense is diagnostic only |
| `FM-ESTOP-017` | Rail sense false-high/short | False latched fault; motion unavailable; ADC overvoltage 가능 | Electrical damage, availability | ADC range/plausibility `D1`, DMM `D2` | `P1`: divider/protection worst-case 12.6 V, series resistance/clamp review, overrange fault |
| `FM-ESTOP-018` | STM32 hang, GPIO stuck or firmware does not process S0-B | PWM zero/latch/telemetry may fail, but physical K1 path should still open | `HZ-ESTOP-001`, `002` | External PWM/rail capture `D2`; runtime self-diagnosis limited | `P1`: K1 path MCU-independent, watchdog/boot DISARMED, motor-disconnected fault injection |
| `FM-ESTOP-019` | Stale command replay, invalid latch clear or auto ARM | K1 re-enable 뒤 unexpected motion request | `HZ-ESTOP-001` | State/UART/PWM capture `D1/D2` | `P1`: zero stored command, reset remains `DISARMED`, new ARM and post-reset CMD, regression tests |
| `FM-ESTOP-020` | Telemetry reports safe while K1 rail remains energized | Operator falsely assumes energy removed | `HZ-ESTOP-002`, `009` | Raw rail evidence vs telemetry comparison `D2` | `P1`: separate `ESTOP_SENSE`, `K1_EXPECTED`, `MOTOR_RAIL_PRESENT` states; telemetry never substitutes measurement |

### Power integration, protection and backup isolation

| ID | Failure mode | Local / system effect | Hazard | Detection | Priority and required action |
| --- | --- | --- | --- | --- | --- |
| `FM-ESTOP-021` | USB/buck/GPIO/PWM-DIR backfeeds downstream driver/motor rail | Open K1를 우회한 residual voltage/current, circuit damage or unintended energy | `HZ-ESTOP-006` | Logic-only downstream rail DMM/scope `D2`; rail sense `D1` | `P1`: T-PWR-003, controlled power-source matrix, isolation/series parts if measured |
| `FM-ESTOP-022` | Fuse oversized/bypassed, wire/terminal undersized or loose | Fault current persists; heat/arcing/contact welding | `HZ-ESTOP-005`, `010` | Visual/current/thermal/voltage-drop `D2` | `P1`: motor current data, fuse curve, wire/terminal rating, no fuse increase without cause analysis |
| `FM-ESTOP-023` | S1 main switch stuck closed, inaccessible or misidentified | K1 failure 시 operator backup isolation unavailable/delayed | `HZ-ESTOP-002`, `009` | Reach/continuity test `D2` | `P1`: accessible labeled S1, battery connector access, preflight open-circuit test |

## FMEA decisions

### `FD-ESTOP-001`: manual re-enable uses three-wire hardware control as the RevB target

정상 target은 다음 기능 구조다.

```text
VBAT_PROTECTED
  -> protected E-stop control supply
  -> S0-A NC
       +-> [S2 momentary NO || K2-HOLD-NO]
       |    -> K2 coil -> PWR_GND
       +-> K2-K1-ENABLE-NO -> K1 coil -> PWR_GND
```

- Initial power-up: S2를 누르기 전 K2/K1 OFF.
- E-stop press/control-power loss: S0-A open 또는 power loss로 K2/K1 OFF.
- Mechanical release: K2-HOLD가 open이므로 K2/K1 OFF 유지.
- Deliberate S2 action: K2 energize 후 pole 1이 self-hold하고 pole 2가 K1 coil을 enable한다.

이 구조는 `FM-ESTOP-014`의 stuck/weld failure를 완전히 제거하지 않는다. 따라서 rail
discrepancy monitoring, software `DISARMED`와 S1 backup을 독립 보호층으로 유지한다.
Safety-rated relay/reset module과 force-guided contact를 사용하지 않는 현재 구조는
single-fault tolerant 또는 PL 달성 구조로 주장하지 않는다.

### `FD-ESTOP-002`: actual-off diagnostic은 downstream rail sensing을 사용한다

RevB에 다음 diagnostic interface를 추가한다.

```text
VBAT_PROTECTED --------> upstream battery sense/reference candidate

MOTOR_VBAT_SAFE
  -> protected divider/filter
  -> MOTOR_VBAT_SAFE_SENSE
  -> STM32 ADC candidate
```

Required diagnostic behavior:

- E-stop asserted 또는 K1 expected OFF 뒤 decay window가 지났는데 downstream rail이
  threshold 이상이면 `K1_OFF_DISCREPANCY` latch.
- Discrepancy 동안 ARM/CMD와 software reset을 reject한다.
- Rail sense 자체가 implausible하면 `RAIL_SENSE_FAULT`로 처리하고 motion을 허용하지 않는다.
- Exact threshold와 decay window는 K1/MDD10A/no-motor measurement 뒤 정한다.

이 ADC path는 monitoring/diagnostic이며 physical K1 차단을 대체하지 않는다. STM32 hang과
ADC common-cause fault에서는 검출할 수 없으므로 motor-disconnected DMM/scope test와 S1
backup을 유지한다.

### `FD-ESTOP-003`: K2 contact는 welded-main proof로 사용하지 않는다

K2 contact는 manual seal-in/K1 coil permission에만 사용한다. K2는 K1 main contact와
mechanically linked/force-guided되지 않으므로 K1 main contact가 실제로 open됐다는 단독
증거로 사용하지 않는다. Actual motor rail을 직접 측정한다.

### `FD-ESTOP-004`: coil suppression은 part selection 뒤 timing으로 승인한다

Coil 양단의 plain flyback diode를 자동 채택하지 않는다. Diode, diode+zener 또는 TVS 등
후보를 K1 coil/driver 정격과 비교하고 `S0-B`, coil voltage와 `MOTOR_VBAT_SAFE` decay를
동시에 측정해 release-time requirement를 만족한 경우에만 승인한다.

### `FD-ESTOP-005`: discrepancy state를 telemetry에 분리한다

최소 상태 후보:

```text
ESTOP_PHYSICAL_OPEN
ESTOP_LATCHED
K1_REENABLE_REQUIRED
K1_OFF_DISCREPANCY
MOTOR_RAIL_PRESENT
RAIL_SENSE_FAULT
RESET_REJECTED
```

Telemetry는 진단 증거이며 physical isolation evidence를 대체하지 않는다.

## Open actions carried into requirements and circuit design

| Action | Owner step | Blocker/status |
| --- | --- | --- |
| K1/S0/S2 functional symbols and three-wire control detail | Step 6 | Function/net baseline complete; exact parts TBD |
| Downstream divider/filter/protection and ADC pin | Steps 5~7 | PA4/PB0 target selected; values/protection/threshold TBR |
| Coil clamp topology | Steps 6~7 | Clamp block/location fixed; exact topology needs K1 coil datasheet |
| K1/fuse/wire/terminal rating | Step 7 | MG540 current data pending |
| K1 expected-off/rail discrepancy firmware behavior | Step 5 then firmware phase | `REQ-ESTOP-012~014` baselined; not implemented |
| S0-A/S0-B connector keying/labeling | Step 5~8 | Functional partition baselined; connector parts/harness TBD |
| S1 reach and fixture/flat-surface test layout | Steps 8~9 | Physical layout evidence pending |

Step 5 requirement 정본은
[`24_Physical_EStop_Safety_Requirements_ko.md`](24_Physical_EStop_Safety_Requirements_ko.md)다.
FMEA action을 `REQ-ESTOP-001~020`과 7개 TBR register item으로 변환했다.

Step 6 circuit 정본은
[`25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](25_Physical_EStop_RevB_Circuit_Architecture_ko.md)다.
Three-wire re-enable, PC7 S0-B sense 후보, PA4/PB0 dual rail-sense 후보와 connector/test-point
partition을 기능/net 수준으로 고정했다.

## Residual limitations carried forward

- Single K1 main contact가 위험 방향으로 고장날 수 있다.
- STM32 rail diagnostic은 MCU/ADC failure와 독립적인 safety channel이 아니다.
- 일반 K1 auxiliary contact는 force-guided proof가 아니다.
- Motor coast, track stopping distance와 incline holding은 아직 측정되지 않았다.
- Exact motor current, relay breaking life와 fuse coordination이 없다.
- Operator가 접근 가능한 S1/main battery disconnect에 의존하는 residual control이 있다.

이 residual limitation 때문에 현 단계에서 actual motor power, ground operation, PL/SIL 또는
산업 안전 인증을 승인하지 않는다.

## Step 4 gate

```text
FMEA scope/functions: BASELINED
Failure modes: 23 IDENTIFIED
RPN/FMECA numeric claim: NOT USED
P1 actions before motor-power energization: IDENTIFIED
Manual re-enable target: THREE-WIRE S2 + K2 TWO-CONTACT CONTROL
MVP actual-off evidence: DIRECT DOWNSTREAM MEASUREMENT REQUIRED
Post-MVP automatic diagnostic: PA4/PB0 DUAL-RAIL SENSE SELECTED
General auxiliary contact as welded-main proof: REJECTED
Coil suppression topology: TBD PENDING PART/TIMING
Residual risk acceptance: NOT PERFORMED
Implementation/runtime verification: NOT TESTED
```

Step 4 완료는 failure mode와 recommended treatment가 연결됐다는 뜻이다. Recommended
action이 구현·시험됐거나 모든 single fault에서 안전하다는 뜻은 아니다.
