# Physical E-stop Safety Requirements

## 목적

이 문서는 Physical E-stop의 safety goal, architecture, hazard analysis와 FMEA에서 도출된
검증 가능한 요구사항을 정의하는 정본이다.

```text
SG-ESTOP-001
-> 21 architecture/system boundary
-> 22 HZ-ESTOP-001~012
-> 23 FM-ESTOP-001~023
-> 24 REQ-ESTOP-001~020
-> T-ESTOP-001~007
-> evidence and residual-risk decision
```

시험 절차와 실제 판정 정본은
[`../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)다.

## 근거와 주장 경계

2026-08-10 이후 이 요구사항은 `REQ-001`, `RISK-001`, `FMEA-001`, `SAFE-CTRL-001`,
`ESTOP-001`, `VVT-001`, `MET-001`, `CM-001`을 `ADOPTED FORWARD BASIS`로 사용한다.

- 요구사항은 하나 이상의 hazard/failure mode와 Test ID에 연결한다.
- `shall`은 `MUST`, `should`는 `SHOULD`를 뜻한다.
- 수치 근거가 없는 값은 추정 확정하지 않고 TBR parameter로 관리한다.
- Requirement baseline은 구현, 시험 PASS, 표준 적합성 또는 인증을 뜻하지 않는다.

## Requirement maturity와 verification status

| Field | Value | Meaning |
| --- | --- | --- |
| Maturity | `BASELINED` | 요구 behavior와 검증 방법이 고정됨 |
| Maturity | `BASELINED/TBR` | 요구 behavior는 고정됐지만 수치 parameter가 열려 있음 |
| Verification | `NOT TESTED` | 구현 또는 시험 evidence 없음 |
| Verification | `PARTIAL` | 요구사항의 일부 경로만 확인됐고 나머지 acceptance evidence가 열려 있음 |
| Verification | `BLOCKED` | 설계 gap, 부품·계측 또는 선행 데이터 때문에 PASS 판정 불가 |
| Verification | `PASS/FAIL` | 정본 절차와 evidence로 판정됨 |

## TBR parameter register

TBR은 requirement를 무기한 모호하게 두기 위한 표기가 아니다. 각 parameter는 지정된 gate
전에 근거와 승인 기록으로 닫아야 한다.

| Parameter | Meaning | Closure basis | Must close before |
| --- | --- | --- | --- |
| `I_MOTOR_WORST` | 동시 motor 운전/starting/stall을 포함한 worst-case current envelope | MG540 official data + controlled current measurement | K1/fuse/wire final selection; `T-ESTOP-001 PASS` |
| `V_SENSE_LOW_MAX`, `V_SENSE_HIGH_MIN` | 선택한 STM32 GPIO의 guaranteed LOW/HIGH input boundary | STM32 datasheet + selected pin/configuration | RevB schematic approval; `T-ESTOP-003` |
| `V_RAIL_OFF_MAX` | K1 expected OFF에서 de-energized로 판정할 downstream rail upper limit | MDD10A/no-motor/back-power baseline, instrument uncertainty | Direct DMM rail-off 판정; `T-ESTOP-005A` |
| `T_PWM_ZERO_MAX` | S0-B assertion edge에서 both PWM inactive까지 허용 시간 | Hazard review + motor-disconnected capture; active DISARM baseline is reference only | `T-ESTOP-004 PASS` |
| `T_K1_OPEN_MAX` | S0-A assertion에서 K1 main contact open까지 허용 시간 | K1 datasheet + coil/clamp measurement | Post-MVP `T-ESTOP-006` precision characterization |
| `T_RAIL_DECAY_MAX` | K1 open 뒤 rail이 `V_RAIL_OFF_MAX` 아래로 내려가는 허용 시간 | No-motor then lifted-motor rail waveform | Post-MVP `T-ESTOP-006` precision characterization |
| `T_STOP_MAX`, `D_STOP_MAX` | Defined low-duty setup에서 mechanical stop time/distance limit | First safe baseline + hazard review; repeatability/measurement uncertainty | Ground drivetrain acceptance |

현재 `T_PWM_ZERO_MAX`는 기존 active DISARM `23.50 us`를 자동 재사용하지 않는다. UART frame
수신과 physical S0-B edge는 서로 다른 trigger path이므로 Physical E-stop capture로 별도
기준을 확정한다.

## Mechanical and hardware interruption requirements

| ID | Requirement and acceptance criteria | Source | Maturity / verification |
| --- | --- | --- | --- |
| `REQ-ESTOP-001` | Physical actuator shall be a red mushroom, mechanically latched, manual twist/pull-release device. PASS: official datasheet identifies the actuation/release mechanism and visual/functional inspection confirms press remains latched until deliberate release. | `HZ-ESTOP-009`; `FM-ESTOP-009~012` | `BASELINED / PARTIAL` — actual S0 red-mushroom body, latch, deliberate release와 2NC restoration 무전원 PASS; order suffix trace와 installed access/fit pending |
| `REQ-ESTOP-002` | S0 shall provide independent `S0-A NC` relay-control and `S0-B NC` sense paths. `S0-A`/control-wire open shall remove K1 coil permission; `S0-B`/sense-wire open shall assert software stop/latch. PASS: unpowered continuity and each independent wire-open test match the truth table with no unintended cross-contact continuity. | `HZ-ESTOP-002`, `007`; `FM-ESTOP-009~013` | `BASELINED / PARTIAL` — 두 NC block truth table와 block 간 isolation 무전원 PASS; 6P 조립 뒤 각 wire-open/control/sense end-to-end test pending |
| `REQ-ESTOP-003` | K1 shall open the positive feed between `VBAT_PROTECTED` and `MOTOR_VBAT_SAFE` without depending on STM32, ESP32, UART or application firmware. PASS: with controllers absent/unpowered and motor disconnected, S0-A assertion de-energizes K1 and direct continuity/voltage measurement confirms the downstream source feed is open. | `HZ-ESTOP-002`; `FM-ESTOP-001`, `005`, `018` | `BASELINED / PARTIAL` — K1 exact part, `89.5 ohm` coil, de-energized NO/isolation 무전원 PASS; assembled direct rail-off measurement pending |
| `REQ-ESTOP-004` | K1, fuse, wire, connector and terminal shall be suitable for the documented 3S LiPo DC voltage, `I_MOTOR_WORST`, make/break, inductive and temperature conditions. PASS: official DC ratings, derating, fuse coordination and wire/terminal calculation are recorded; AC-only rating or sales-title current is not accepted. | `HZ-ESTOP-005`, `010`; `FM-ESTOP-001`, `003`, `006`, `022` | `BASELINED/TBR / PARTIAL-BLOCKED` — K1 numerical gate와 F1/K1 loose-part screen PASS; final crimp, suppression, voltage-drop, start-current와 thermal evidence pending |

## Control, restart and software requirements

| ID | Requirement and acceptance criteria | Source | Maturity / verification |
| --- | --- | --- | --- |
| `REQ-ESTOP-005` | `ESTOP_SENSE` shall be a 3.3 V-safe, externally biased fail-safe input electrically separated from motor and coil current. Healthy/closed shall satisfy the selected GPIO LOW limit; pressed/open/wire-break shall satisfy its HIGH limit without exceeding pin absolute maximum. PASS: calculation, DMM table and input-state capture close `V_SENSE_*`. | `HZ-ESTOP-007`; `FM-ESTOP-011~013`, `018` | `BASELINED/TBR / PARTIAL — DIRECT PC7 INPUT ONLY; VO617/S0-B PATH OPEN` |
| `REQ-ESTOP-006` | S0-B assertion shall invoke the common safe-output path, make both PWM outputs inactive within `T_PWM_ZERO_MAX`, zero stored motion commands and set a persistent E-stop latch. PASS: logic capture, state/UART log and command-variable evidence agree for armed and disarmed cases. | `HZ-ESTOP-001`; `FM-ESTOP-018~020` | `BASELINED/TBR / PARTIAL — DIRECT PC7 LATCH/REJECT/RESET ONLY; PWM EDGE CAPTURE OPEN` |
| `REQ-ESTOP-007` | Mechanical release, manual K1 re-enable and software reset shall not individually restore motion. Valid software reset shall only clear the latch and remain `DISARMED`; motion requires a new ARM and post-reset new CMD. PASS: stale/pre-E-stop command is never replayed in release/reset/re-enable order permutations. | `HZ-ESTOP-001`; `FM-ESTOP-014`, `019` | `BASELINED / PARTIAL — DIRECT PC7 RELEASE/RESET ONLY; NOMINAL K1/S2 ORDER PERMUTATIONS OPEN; FM-014 SINGLE-FAULT EXTENSION POST-MVP` |
| `REQ-ESTOP-008` | Initial power-up, controller boot/reset, E-stop-open boot and control-power restoration shall begin with K1/output safe and no automatic motion. MVP PASS uses a verified healthy/released S2 and non-shorted harness: K1 remains off until deliberate S2 action and PWM remains zero until valid reset/new ARM/CMD. S2 stuck/6P pair-short single-fault tolerance is the separate post-MVP `T-ESTOP-005B`. | `HZ-ESTOP-001`; `FM-ESTOP-004`, `014`, `018~019` | `BASELINED / PARTIAL-BLOCKED — NOMINAL INTEGRATED PATH OPEN; FM-014 SINGLE-FAULT EXTENSION POST-MVP` |
| `REQ-ESTOP-009` | Electrical shutdown evidence and mechanical stop evidence shall be recorded separately. MVP PASS: `T-ESTOP-004` records sense-to-PWM zero, `T-ESTOP-005A` records direct downstream rail-off and `T-ESTOP-007` records actual motor stop without treating electrical isolation as immediate mechanical stop. Synchronized `t0~t3` transient characterization is post-MVP `T-ESTOP-006`. | `HZ-ESTOP-003`, `008`, `011~012`; `FM-ESTOP-004`, `008` | `BASELINED/TBR / BLOCKED` |
| `REQ-ESTOP-010` | Telemetry or bench log should distinguish physical-open, latched, re-enable-required, rail-present, discrepancy, rail-sense-fault and reset-rejected states. PASS: each injected/physical state has a unique observable record; telemetry is not used as sole proof of isolation. | `HZ-ESTOP-002`, `009`; `FM-ESTOP-020` | `BASELINED / NOT TESTED` |
| `REQ-ESTOP-011` | Manual rail re-enable shall use `S0-A NC -> [S2 momentary NO OR K2-HOLD-NO] -> K2 coil`, with a separate `K2-K1-ENABLE-NO -> K1 coil`, or a documented equivalent preserving the same nominal behavior. MVP PASS with verified healthy/released S2 and non-shorted harness: initial power, S0 press, mechanical release and power restoration leave K2/K1 off; only deliberate S2 action energizes them. Stuck/short single-fault tolerance remains `T-ESTOP-005B`. | `HZ-ESTOP-001`; `FM-ESTOP-009`, `014~015` | `BASELINED / BLOCKED — NOMINAL INTEGRATED PATH OPEN; FM-014 SINGLE-FAULT EXTENSION POST-MVP` |

## Actual-off diagnostic requirements

| ID | Requirement and acceptance criteria | Source | Maturity / verification |
| --- | --- | --- | --- |
| `REQ-ESTOP-012` | RevB should provide protected downstream `MOTOR_VBAT_SAFE_SENSE` independent of S0-B. At worst-case pack voltage the STM32 input should remain within rating, and OFF-state false-high plus ON-state false-low/open faults should be detectable through upstream/downstream plausibility. PASS: divider/protection calculation, bench-voltage sweep, deliberate K1-on pre-ARM comparison, DMM and ADC log agree within recorded uncertainty. | `HZ-ESTOP-002`, `006`; `FM-ESTOP-001`, `016~017`, `021` | `BASELINED/TBR / POST-MVP / NOT TESTED` |
| `REQ-ESTOP-013` | When K1 is expected OFF and `MOTOR_VBAT_SAFE_SENSE` remains above `V_RAIL_OFF_MAX` after `T_RAIL_DECAY_MAX`, STM32 should latch `K1_OFF_DISCREPANCY`, zero outputs and reject reset/ARM/CMD. PASS: motor-disconnected safe fault injection produces the latch and no nonzero PWM/command acceptance. | `HZ-ESTOP-002`, `006`, `008`; `FM-ESTOP-001`, `005`, `009`, `021` | `BASELINED/TBR / POST-MVP / NOT TESTED` |
| `REQ-ESTOP-014` | Implausible rail-sense open, short, overrange or upstream/downstream contradiction should set `RAIL_SENSE_FAULT` and block motion. After deliberate K1 re-enable and before ARM, downstream rail should match the valid upstream source within a closed tolerance. PASS: current-limited motor-disconnected false-low/open and false-high tests converge to zero output/latch without input damage. | `HZ-ESTOP-002`, `006`; `FM-ESTOP-016~017` | `BASELINED/TBR / POST-MVP / NOT TESTED` |
| `REQ-ESTOP-015` | A general relay auxiliary/control contact should not be accepted as sole evidence that the K1 power main contact opened unless mechanically linked/force-guided behavior is officially established. PASS: design review traces actual-off verdict to direct downstream voltage/continuity evidence; K2 state is control evidence only. | `HZ-ESTOP-002`; `FM-ESTOP-001`, `020` | `BASELINED / POST-MVP / NOT TESTED` |
| `REQ-ESTOP-016` | K1/K2 coil suppression shall keep switch/contact stress within component ratings and shall not prevent functional K1 drop-out. MVP PASS: official coil/clamp ratings plus `T-ESTOP-005A` direct rail-removal observation agree. Precision `T_K1_OPEN_MAX`/`T_RAIL_DECAY_MAX` waveform characterization remains post-MVP `T-ESTOP-006`. | `HZ-ESTOP-003`, `005`, `008`; `FM-ESTOP-006~008` | `BASELINED/TBR / BLOCKED` |

## Integration, operation and evidence requirements

| ID | Requirement and acceptance criteria | Source | Maturity / verification |
| --- | --- | --- | --- |
| `REQ-ESTOP-017` | Logic power, USB and PWM/DIR connections shall not bypass open K1 with hazardous downstream energy. PASS: approved power-source matrix with motor disconnected keeps rail at/below `V_RAIL_OFF_MAX`, causes no motor-output activation and shows no abnormal current/heat. | `HZ-ESTOP-006`; `FM-ESTOP-021` | `BASELINED/TBR / BLOCKED` |
| `REQ-ESTOP-018` | S0-A, S0-B, S2, K2, optocoupler, K1 coil/main and rail-sense wiring shall use an unambiguous connector/pin/label scheme that prevents or detects interchange and unsafe cross-connection. PASS: no-power pin-to-pin review, connector-keying check and controlled open/cross-wire matrix produce no unsafe false-healthy path or STM32 overvoltage. | `HZ-ESTOP-007`, `010`; `FM-ESTOP-005`, `011`, `013`, `022` | `BASELINED / PARTIAL` — K1 terminal identity와 loose 6P kit inventory 확인; cavity map, first-article crimp, label, 6x6 isolation/open/cross-wire matrix pending |
| `REQ-ESTOP-019` | Powered motion tests shall use an accessible S0/S1, fixed stand for lifted tests, defined exclusion zone and flat surface; incline/edge operation is prohibited until a separate holding/braking hazard cycle. PASS: preflight checklist and layout/photo/video show operator reach without entering the track zone and the permitted environment. | `HZ-ESTOP-003~004`, `009`, `011~012`; `FM-ESTOP-004`, `023` | `BASELINED / NOT TESTED` |
| `REQ-ESTOP-020` | Each test shall record configuration, parts/datasheets, firmware commit, schematic revision, power sources, fuse/load/fixture, instruments, expected/observed result and evidence boundary. `T-ESTOP-001~004 + T-ESTOP-005A` shall PASS before powered single-motor test. PASS: traceability/evidence audit has no missing MVP-MUST evidence or unsafe TBD in the executed build. | All hazards; all FMEA groups; `CM-001`, `VVT-001` | `BASELINED / PARTIAL` |

## Hazard/FMEA traceability

| Source | Derived requirements |
| --- | --- |
| `HZ-ESTOP-001` | `REQ-ESTOP-006~008`, `011`, `013~014` |
| `HZ-ESTOP-002` | `REQ-ESTOP-002~004`, `012~015` |
| `HZ-ESTOP-003~004` | `REQ-ESTOP-009`, `016`, `019` |
| `HZ-ESTOP-005` | `REQ-ESTOP-004`, `016`, `018`, `020` |
| `HZ-ESTOP-006` | `REQ-ESTOP-012~014`, `017` |
| `HZ-ESTOP-007~008` | `REQ-ESTOP-002`, `005`, `009`, `016`, `018` |
| `HZ-ESTOP-009~010` | `REQ-ESTOP-004`, `010`, `018~020` |
| `HZ-ESTOP-011~012` | `REQ-ESTOP-009`, `019~020` |
| `FM-ESTOP-001~008` | `REQ-ESTOP-003~004`, `012~013`, `016` |
| `FM-ESTOP-009~015` | `REQ-ESTOP-002`, `005`, `007`, `011`, `018` |
| `FM-ESTOP-016~020` | `REQ-ESTOP-006~010`, `012~015` |
| `FM-ESTOP-021~023` | `REQ-ESTOP-004`, `017~020` |

## Requirement-to-test mapping

| Test | Requirements | Primary evidence |
| --- | --- | --- |
| `T-ESTOP-001` | `001`, `003~004`, `011`, `016~020` | Datasheets, calculations, schematic/ERC, review checklist |
| `T-ESTOP-002` | `001~003`, `011`, `018` | Continuity/open/cross-wire table, latch inspection |
| `T-ESTOP-003` | `005`, `018` | DMM GPIO voltage table, current-limited wire-open test |
| `T-ESTOP-004` | `006~008`, `010` | UART/state log, PWM/sense capture, negative test |
| `T-ESTOP-005A` | `003`, `007~009`, `011`, `016~017` | MVP nominal healthy-S2/harness powered/no-motor direct rail/PWM/state capture |
| `T-ESTOP-005B` | `007~008`, `011`, `018` | Post-MVP S2 stuck-closed/6P pair-short single-fault injection and residual-risk closure |
| `T-ESTOP-006` | `009`, `012~016`, `017` | Post-MVP coil/contact/rail synchronized waveform and fault injection |
| `T-ESTOP-007` | `009`, `019~020` | Fixed/lifted single-motor video, stop time/distance table |
| `T-PWR-003` | `017` | USB/buck back-power matrix |

모든 `MUST` requirement는 적어도 하나의 MVP Test ID에 연결됐다. `REQ-ESTOP-010`과
`REQ-ESTOP-012~015`는 SHOULD/POST-MVP이며, 미완료여도 MVP 종료를 막지 않는다. 단,
`REQ-ESTOP-003`의 direct downstream continuity/voltage evidence는 생략할 수 없다.

## Step 5 gate

```text
Safety requirements: 20 BASELINED
MUST/SHOULD: 15 MUST / 5 SHOULD
Open TBR register items: 7
Hazard-to-requirement traceability: COMPLETE
FMEA-to-requirement traceability: COMPLETE
Requirement-to-test traceability: COMPLETE
Requirement implementation: PARTIAL
Verification evidence: PARTIAL — direct-PC7 and selected incoming checks only
Residual risk acceptance: DOCUMENTED / NOT CLOSED
```

Step 5 완료는 요구 behavior와 PASS 방법이 고정됐다는 뜻이다. TBR이 닫히거나 구현·시험이
완료됐다는 뜻이 아니다. MVP MUST에 연결된 TBR은 해당 시험 전에 닫고, 오직
`REQ-ESTOP-012~015`/`T-ESTOP-006`에 연결된 post-MVP TBR은 확장 V-cycle에서 닫는다.

## 2026-08-24 partial-evidence와 설계 gap 갱신

- Motor/LiPo/K1 경로를 연결하지 않은 direct PC7-to-GND/open 시험에서 PC7 LOW/HIGH,
  persistent latch, ARM/CMD reject, reset reject/accept와 reset 뒤 `DISARMED`를 확인했다.
  Host static regression은 `20/20 PASS`였다.
- 이 결과는 PC7 firmware/input 경로의 partial evidence다. 아직 도착하지 않은 `VO617A-3`,
  실제 S0-B 5 V loop, external 10 kOhm pull-up, sense-to-PWM timing과 K1 rail-off를 검증하지
  않았으므로 `REQ-ESTOP-005~007` 전체 PASS가 아니다.
- 현재 RevB의 `S2 NO OR K2-HOLD-NO` 병렬 경로는 S2가 정상적으로 해제되어 open이고
  `J_S2` 5-6 cross-short가 없을 때만 nominal no-auto-reenable을 제공한다. S2 stuck-closed 또는
  5-6 short이면 S0 release/전원 복구와 함께 K2/K1가 자동 energize될 수 있다.
- 당시 판정은 `FM-ESTOP-014` mitigation과 negative test를 기존 단일 `T-ESTOP-005`의
  선행 조건으로 두었다. 아래 2026-08-25 범위 재조정이 이 일정 판정을 supersede하지만,
  failure mode 자체와 firmware가 hardware rail-off를 대신할 수 없다는 경계는 그대로 유지한다.

## 2026-08-25 MVP와 단일고장 확장 범위 재조정

- `T-ESTOP-005A`는 정상적으로 해제된 S2와 short가 없는 검증된 6P harness를 전제로 initial
  power, S0 press/release, control-power restore, deliberate S2, software reset와 new ARM/CMD의
  nominal no-auto-motion 및 direct rail-off를 확인하는 MVP 시험이다.
- `T-ESTOP-005B`는 S2 stuck-closed와 6P S2-pair short를 주입해 단일고장 내성을 확인하는
  post-MVP 시험이다. `FM-ESTOP-014`는 닫히지 않은 residual risk로 계속 추적한다.
- 이 분리는 현 회로를 산업 안전회로나 single-fault tolerant 설계로 승격하지 않는다.
  포트폴리오 claim은 `functional prototype with documented residual risk`로 제한한다.
- 따라서 actual motor 전원 인가의 MVP 선행 조건은 `T-ESTOP-001~004 + T-ESTOP-005A PASS`다.
