# Physical E-stop Safety Requirements

**현재 — 2026-11-20 비실물 검토 완료:** [통합 결과46](../docs/verification/46_MVP_Nonphysical_Closeout_2026-11-20_ko.md)에 부품/선재 식별, 퓨즈·코일·옵토 계산, 저장 ERC와 기존 시험 근거 대조를 완료했다. 현재 소스27개에 대한 검사 입력29건의 해시가 이전 검사와 일치한다. 상위9 PASS·4 PARTIAL, T004/T005A 정상 기능 PASS 유지. 남은 것은R1 전체 보호협조 수용,R2 clamp stress 근거,R3 T002/T003 기록 수용,R4 엔코더 전기적·실제 정지 증거다. 자료 부족을 시험 미수행으로 바꾸거나 같은 부품/정상 동작을 재확인하지 않는다. 사용자 결정대로 기존 선행을 모두 닫은 뒤 촬영한다. 배선 길이/길이 기반 전압강하 검토는 제외했고, 후속 열·전류·T006을 새 필수로 복원하지 않는다.


> 문서 역할·상태 대조: **2026-11-20** — T004 PASS, T005A 정상 기능 한정 PASS, T007 정식 수용 미완료. 전체 전원 조합/잔류 에너지 수용은 OPEN이다.
> [현재 구현·검증 범위와 문서 안내](README.md) · [최신 검증 판정](../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md). 날짜별 과거 수치·판정은 당시 기록이다.

## 목적

**2026-11-20 사용자 채택:** [결정44 §10](../docs/verification/44_EStop_Acceptance_Proposal_2026-11-19_ko.md)의 수용 범위 변경을 적용했다. T005A는 모터 분리·시험한 정상 전원 구성의 공급 차단/PWM 정지/무자동 재출발 기능에 한정해 PASS다. 수치 rail-off/잔류 에너지·전체 역급전 수용은 OPEN으로 분리한다. 이전 수치 조건을 만족한 것으로 소급한 판정이 아니며, 아래 날짜별 이력의 PARTIAL은 당시 기록이다. 다른 gate의 미결과 T007 실측 목표는 유지한다.

**2026-11-19 후속 결정:** 사용자가 제한된 저속 시험의 정지 성능 목표를 채택했다. 실제 속도0.10m/s 이하, 비상정지 작동 후 정지시간1.0초 이하, 잔여 이동0.10m 이하를 적용한다. 이는 성능 목표 확정이며 실측 PASS나 산업용 안전 인증이 아니다. T005A 전원 차단 수용과 T007의 선행 조건은 유지한다. [결정 기록44](../docs/verification/44_EStop_Acceptance_Proposal_2026-11-19_ko.md).

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

## 이전 검증 상태 — 2026-09-23

[report 25](../docs/verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md)는 conditioned PC7 전압 기능,
[report 26](../docs/verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md)는 T004 firmware/PWM/latch/reset/wire-open PASS,
[report 27](../docs/verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md)는 MDD 전력단 연결 후 관측과 T005A PARTIAL의 근거다.
아래 현재 상태 열에 후속 증거를 반영했다. 날짜별 이력의 미완료 표현은 당시 기록으로 보존한다.

## TBR parameter register

TBR은 requirement를 무기한 모호하게 두기 위한 표기가 아니다. 각 parameter는 지정된 gate
전에 근거와 승인 기록으로 닫아야 한다.

| Parameter | Meaning | Closure basis | Must close before / 현재 반영 상태 |
| --- | --- | --- | --- |
| `I_MOTOR_WORST` | 동시 motor 운전/starting/stall을 포함한 worst-case current envelope | MG540 official data + controlled current measurement | K1/fuse/wire final selection; `T-ESTOP-001 PASS` |
| `V_SENSE_LOW_MAX`, `V_SENSE_HIGH_MIN` | 선택한 STM32 GPIO의 guaranteed LOW/HIGH input boundary | STM32 datasheet + selected pin/configuration | RevB schematic approval/T003 이전 기준 확정. T003 전압 기능 판정에는 VDD=3.30 V에서 LOW ≤0.99 V / HIGH ≥2.31 V 적용(report 25); current/계측 evidence package는 PARTIAL |
| `V_RAIL_OFF_MAX` | 잔류 전압·에너지와 전체 전원 조합을 정량 수용할 downstream rail upper limit | 허용 에너지/장치 전원 상실 거동·전원 조합·계측 불확도와 연결할 근거는 미결 | **TBR/OPEN**.11/20 채택으로 T005A 정상 기능 수용의 선행에서 분리. 기존 후속T006 및 REQ-ESTOP-013/017 정량 수용에 연결 |
| `T_PWM_ZERO_MAX` | S0-B assertion edge에서 both PWM inactive까지 허용 시간 | Hazard review + motor-disconnected capture; active DISARM baseline is reference only | T004 PASS 이전 기준 확정. Motor-disconnected 기준 200 ms, 이후 ≥500 ms no-edge 적용 완료; report 26 §3 및 9/8 runbook. Trigger는 conditioned PC7 first stable HIGH |
| `T_K1_OPEN_MAX` | S0-A assertion에서 K1 main contact open까지 허용 시간 | K1 datasheet + coil/clamp measurement | Post-MVP `T-ESTOP-006` precision characterization |
| `T_RAIL_DECAY_MAX` | K1 open 뒤 rail이 `V_RAIL_OFF_MAX` 아래로 내려가는 허용 시간 | No-motor then lifted-motor rail waveform | Post-MVP `T-ESTOP-006` precision characterization |
| `T_STOP_MAX`, `D_STOP_MAX` | 실제 속도≤0.10m/s인 제한된 저속 시험에서 정지시간≤1.0초, 잔여 이동≤0.10m | 2026-11-19 사용자 성능 목표 채택. 측정 불확도를 포함한 상한으로 판정. 기존127.32ms 엔코더 관측은 기계 정지 실측을 대신하지 않음 | **목표 확정 / 시험 미완료.** 공중 시험은 궤도 이동, 지상 시험은 차체 이동으로 구분. T005A 선행 유지 |

`T_PWM_ZERO_MAX`의 T004 사전 기준은 **200 ms**였고 report 26에 판정 방법과 결과를 보존했다.
PC7 first stable HIGH부터 늦은 PWM last-fall까지를 측정하며, run06은 357.25 µs였다.
기존 UART active DISARM 23.50 µs와 다른 trigger path다. PC7 이전 접점/광결합기 지연,
K1 접점·rail decay나 실제 모터 정지 시간까지 측정한 값으로 확대하지 않는다.

## Mechanical and hardware interruption requirements

| ID | Requirement and acceptance criteria | Source | Maturity / verification |
| --- | --- | --- | --- |
| `REQ-ESTOP-001` | Physical actuator shall be a red mushroom, mechanically latched, manual twist/pull-release device. PASS: official datasheet identifies the actuation/release mechanism and visual/functional inspection confirms press remains latched until deliberate release. | `HZ-ESTOP-009`; `FM-ESTOP-009~012` | `BASELINED / PARTIAL` — actual S0 red-mushroom body, latch, deliberate release와 2NC restoration 무전원 PASS; order suffix trace와 installed access/fit pending |
| `REQ-ESTOP-002` | S0 shall provide independent `S0-A NC` relay-control and `S0-B NC` sense paths. `S0-A`/control-wire open shall remove K1 coil permission; `S0-B`/sense-wire open shall assert software stop/latch. PASS: unpowered continuity and each independent wire-open test match the truth table with no unintended cross-contact continuity. | `HZ-ESTOP-002`, `007`; `FM-ESTOP-009~013` | `BASELINED / PARTIAL` — 기존 6P/NC truth table·독립성 PASS, report 25 conditioned S0-B open 전압과 report 26 active wire-open PWM/latch PASS 추가. 전체 하네스 release 증거는 별도 |
| `REQ-ESTOP-003` | K1 shall open the positive feed between `VBAT_PROTECTED` and `MOTOR_VBAT_SAFE` without depending on STM32, ESP32, UART or application firmware. Normal-function acceptance combines the hardware path/de-energized NO-contact evidence with direct downstream voltage observations; controller-absent/unpowered full-condition acceptance remains separately OPEN. | `HZ-ESTOP-002`; `FM-ESTOP-001`, `005`, `018` | `PARTIAL / T005A NORMAL FUNCTION PASS` — 보고서24/27과 결정44 §8~10의 접점/직접 전압/출력·복구 근거.11/20 범위 변경으로 정상 기능 수용. Controller-independent 전체 조건 및 정량 잔류 에너지 수용은 미완료 |
| `REQ-ESTOP-004` | K1, fuse, wire, connector and terminal shall be suitable for the documented 3S LiPo DC voltage, `I_MOTOR_WORST`, make/break, inductive and temperature conditions. PASS: official DC ratings, derating, fuse coordination and wire/terminal calculation are recorded; AC-only rating or sales-title current is not accepted. 2026-11-20 사용자 변경: 배선 길이 측정·길이 기반 전압강하 계산은 MVP/T001 필수 수용에서 제외하며 미완료 사유로 쓰지 않는다. S1 판매 사양 수용은 시험 계획06의 개별 결정에 따른다. | `HZ-ESTOP-005`, `010`; `FM-ESTOP-001`, `003`, `006`, `022` | `BASELINED/TBR / PARTIAL-BLOCKED` — 6P/K1/P6KE 기존 조립 관측 유지.11/19 사용자 확인으로 K1 30·87 주전력선 모두12AWG,87→B+ 중간 접속 없음:280756-4 지정12–10AWG와의 도체 굵기 불일치는 해소. 나머지 정격 수용을 자동 PASS로 바꾸거나 후속/제외된 전류·열·정밀 timing 시험을 MVP 필수로 복원하지 않음 |

## Control, restart and software requirements

| ID | Requirement and acceptance criteria | Source | Maturity / verification |
| --- | --- | --- | --- |
| `REQ-ESTOP-005` | `ESTOP_SENSE` shall be a 3.3 V-safe, externally biased fail-safe input electrically separated from motor and coil current. Healthy/closed shall satisfy the selected GPIO LOW limit; pressed/open/wire-break shall satisfy its HIGH limit without exceeding pin absolute maximum. PASS: calculation, DMM table and input-state capture close `V_SENSE_*`. | `HZ-ESTOP-007`; `FM-ESTOP-011~013`, `018` | `BASELINED / PARTIAL` — report 25 actual S0-B/VO617A/PC7 0.06 V healthy, 3.27 V pressed/open 기능 PASS; current·계측 metadata 보완 미완료 |
| `REQ-ESTOP-006` | S0-B assertion shall invoke the common safe-output path, make both PWM outputs inactive within `T_PWM_ZERO_MAX`, zero stored motion commands and set a persistent E-stop latch. PASS: logic capture, state/UART log and command-variable evidence agree for armed and disarmed cases. | `HZ-ESTOP-001`; `FM-ESTOP-018~020` | `BASELINED / T004 PASS — MOTOR-DISCONNECTED CONDITIONED FIRMWARE/PWM SCOPE` — report 26 §3, 200 ms/500 ms 기준과 run06 357.25 µs; rail/실모터 정지는 별도 |
| `REQ-ESTOP-007` | Mechanical release, manual K1 re-enable and software reset shall not individually restore motion. Valid software reset shall only clear the latch and remain `DISARMED`; motion requires a new ARM and post-reset new CMD. PASS: stale/pre-E-stop command is never replayed in release/reset/re-enable order permutations. | `HZ-ESTOP-001`; `FM-ESTOP-014`, `019` | `PARTIAL / T004 AND T005A NORMAL FUNCTION PASS` — 기록된 latch/reset/ARM-only/fresh CMD 및 정상 복구 순서 수용. 전체 순열·FM-014 확장까지 수용한 것은 아님 |
| `REQ-ESTOP-008` | Initial power-up, controller boot/reset, E-stop-open boot and control-power restoration shall begin with K1/output safe and no automatic motion. MVP PASS uses a verified healthy/released S2 and non-shorted harness: K1 remains off until deliberate S2 action and PWM remains zero until valid reset/new ARM/CMD. S2 stuck/6P pair-short single-fault tolerance is the separate post-MVP `T-ESTOP-005B`. | `HZ-ESTOP-001`; `FM-ESTOP-004`, `014`, `018~019` | `PASS — TESTED NORMAL CONFIGURATION` — 보고서24/26/27 및 결정44 §10. 전체 전원 순열/단일고장 내성은 포함하지 않음 |
| `REQ-ESTOP-009` | Electrical shutdown evidence and mechanical stop evidence shall be recorded separately. MVP acceptance: `T-ESTOP-004` records sense-to-PWM zero, `T-ESTOP-005A` records normal source-interruption/no-auto-restart using direct downstream observations, and `T-ESTOP-007` records actual motor stop. Electrical interruption is not immediate mechanical stop. Quantitative residual-energy/rail-off acceptance and synchronized `t0~t3` characterization remain OPEN, linked to post-MVP `T-ESTOP-006`. | `HZ-ESTOP-003`, `008`, `011~012`; `FM-ESTOP-004`, `008` | `PARTIAL` — T004/T005A 각 명시 범위 PASS. T007 정량 정지 실측과 후속 정량 잔류/과도 검토는 미완료 |
| `REQ-ESTOP-010` | Telemetry or bench log should distinguish physical-open, latched, re-enable-required, rail-present, discrepancy, rail-sense-fault and reset-rejected states. PASS: each injected/physical state has a unique observable record; telemetry is not used as sole proof of isolation. | `HZ-ESTOP-002`, `009`; `FM-ESTOP-020` | `BASELINED / PARTIAL` — report 26의 ESTOP_ACTIVE/ESTOP_LATCHED·reset ERR/ACK·DISARMED 관측. Rail-present/re-enable-required/discrepancy/rail-sense-fault 전체 관측은 미구현·미검증 |
| `REQ-ESTOP-011` | Manual rail re-enable shall use `S0-A NC -> [S2 momentary NO OR K2-HOLD-NO] -> K2 coil`, with a separate `K2-K1-ENABLE-NO -> K1 coil`, or a documented equivalent preserving the same nominal behavior. MVP PASS with verified healthy/released S2 and non-shorted harness: initial power, S0 press, mechanical release and power restoration leave K2/K1 off; only deliberate S2 action energizes them. Stuck/short single-fault tolerance remains `T-ESTOP-005B`. | `HZ-ESTOP-001`; `FM-ESTOP-009`, `014~015` | `PASS — TESTED NORMAL CONFIGURATION` — 보고서24의 K2 수정 후 pickup/self-hold/dropout/no-auto-reenable 및 보고서27/결정44의 직접 rail 관측. FM-014 단일고장 확장은 OPEN |

## Actual-off diagnostic requirements

| ID | Requirement and acceptance criteria | Source | Maturity / verification |
| --- | --- | --- | --- |
| `REQ-ESTOP-012` | RevB should provide protected downstream `MOTOR_VBAT_SAFE_SENSE` independent of S0-B. At worst-case pack voltage the STM32 input should remain within rating, and OFF-state false-high plus ON-state false-low/open faults should be detectable through upstream/downstream plausibility. PASS: divider/protection calculation, bench-voltage sweep, deliberate K1-on pre-ARM comparison, DMM and ADC log agree within recorded uncertainty. | `HZ-ESTOP-002`, `006`; `FM-ESTOP-001`, `016~017`, `021` | `BASELINED/TBR / POST-MVP / NOT TESTED` |
| `REQ-ESTOP-013` | When K1 is expected OFF and `MOTOR_VBAT_SAFE_SENSE` remains above `V_RAIL_OFF_MAX` after `T_RAIL_DECAY_MAX`, STM32 should latch `K1_OFF_DISCREPANCY`, zero outputs and reject reset/ARM/CMD. PASS: motor-disconnected safe fault injection produces the latch and no nonzero PWM/command acceptance. | `HZ-ESTOP-002`, `006`, `008`; `FM-ESTOP-001`, `005`, `009`, `021` | `BASELINED/TBR / POST-MVP / NOT TESTED` |
| `REQ-ESTOP-014` | Implausible rail-sense open, short, overrange or upstream/downstream contradiction should set `RAIL_SENSE_FAULT` and block motion. After deliberate K1 re-enable and before ARM, downstream rail should match the valid upstream source within a closed tolerance. PASS: current-limited motor-disconnected false-low/open and false-high tests converge to zero output/latch without input damage. | `HZ-ESTOP-002`, `006`; `FM-ESTOP-016~017` | `BASELINED/TBR / POST-MVP / NOT TESTED` |
| `REQ-ESTOP-015` | A general relay auxiliary/control contact should not be accepted as sole evidence that the K1 power main contact opened unless mechanically linked/force-guided behavior is officially established. PASS: design review traces actual-off verdict to direct downstream voltage/continuity evidence; K2 state is control evidence only. | `HZ-ESTOP-002`; `FM-ESTOP-001`, `020` | `BASELINED / POST-MVP / NOT TESTED` |
| `REQ-ESTOP-016` | K1/K2 coil suppression shall keep switch/contact stress within component ratings and shall not prevent functional K1 drop-out. MVP PASS: official coil/clamp ratings plus `T-ESTOP-005A` direct rail-removal observation agree. Precision `T_K1_OPEN_MAX`/`T_RAIL_DECAY_MAX` waveform characterization remains post-MVP `T-ESTOP-006`. | `HZ-ESTOP-003`, `005`, `008`; `FM-ESTOP-006~008` | `BASELINED/TBR / PARTIAL-BLOCKED` — K1 85-86 병렬 `P6KE16CA` 조립/continuity와 control-only drop subset PASS; 11/20 검토46에서K2 suppression 설치·정상169mA/VRWM 비교·T005A 기능 차단 대조 완료. 전체clamp 에너지/stress 근거는R2로 남음. 정밀drop-out/rail-decay timing은 후속T006이며 MVP 필수로 복원하지 않음 |

## Integration, operation and evidence requirements

| ID | Requirement and acceptance criteria | Source | Maturity / verification |
| --- | --- | --- | --- |
| `REQ-ESTOP-017` | Logic power, USB and PWM/DIR connections shall not bypass open K1 with hazardous downstream energy. Full acceptance requires an approved power-source matrix and quantitative residual-energy/rail-off criteria, with no unintended motor-output activation. Quantitative current/heat work follows the existing deferred scope. | `HZ-ESTOP-006`; `FM-ESTOP-021` | `BASELINED/TBR / OPEN` —11/20 채택으로 정상 구성T005A와 분리. 전체 전원 조합/잔류 에너지 수용은 미완료이며 정상 기능 PASS로 대체하지 않음 |
| `REQ-ESTOP-018` | S0-A, S0-B, S2, K2, optocoupler, K1 coil/main and rail-sense wiring shall use an unambiguous connector/pin/label scheme that prevents or detects interchange and unsafe cross-connection. PASS: no-power pin-to-pin review, connector-keying check and controlled open/cross-wire matrix produce no unsafe false-healthy path or STM32 overvoltage. | `HZ-ESTOP-007`, `010`; `FM-ESTOP-005`, `011`, `013`, `022` | `BASELINED / PARTIAL` — 6P 18 AWG first article, full assembly, cavity pair truth table, isolation과 retention은 operator-reported PASS. As-built control은 `F2 -> 6P.1 -> S0-A -> 6P.2 -> JESTOP.2`이며 JESTOP.1은 unused/no-jumper. Permanent labels, powered cross-wire/overvoltage와 final evidence는 OPEN |
| `REQ-ESTOP-019` | Powered motion tests shall use an accessible S0/S1, fixed stand for lifted tests, defined exclusion zone and flat surface; incline/edge operation is prohibited until a separate holding/braking hazard cycle. PASS: preflight checklist and layout/photo/video show operator reach without entering the track zone and the permitted environment. | `HZ-ESTOP-003~004`, `009`, `011~012`; `FM-ESTOP-004`, `023` | `BASELINED / NOT TESTED` |
| `REQ-ESTOP-020` | Each test shall record configuration, parts/datasheets, firmware commit, schematic revision, power sources, fuse/load/fixture, instruments, expected/observed result and evidence boundary. `T-ESTOP-001~004 + T-ESTOP-005A` shall PASS before powered single-motor test. Acceptance audits each test against its approved scope and keeps unverified evidence/risk explicit. | All hazards; all FMEA groups; `CM-001`, `VVT-001` | `PARTIAL` —11/20 T005A는 채택한 정상 기능 범위 PASS. T001~T003의 전체 수용과 다른 선행을 자동 면제하지 않음. 증거 부족을 시험 미수행과 구분 |

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
Parameter groups tracked: 7 (current closure notes in the register above)
Hazard-to-requirement traceability: COMPLETE
FMEA-to-requirement traceability: COMPLETE
Requirement-to-test traceability: COMPLETE
Requirement implementation: PARTIAL
Verification evidence: PARTIAL — conditioned sense function, T004 firmware/PWM PASS; T005A observations retained, full rail acceptance and actual motor pending
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

## 2026-09-05 당시 as-built integration 상태와 다음 Gate

아래 다음 실행은 9/5 당시 계획이다. 후속 report 25/26/27 결과와 현재 재개 순서는 문서 상단의 최신 판정 링크를 따른다.

- 6P harness는 18 AWG first article, full male/female assembly, terminal retention, intended-pair
  continuity와 unintended-pair isolation을 operator-reported PASS했다. Pin 1/2는 S0-A NC,
  pin 3/4는 S0-B NC, pin 5/6은 S2 momentary NO다.
- 현재 control wiring은 `S1 OUT -> F2 -> 6P.1 -> S0-A NC -> 6P.2 -> JESTOP.2`이며
  board-side JESTOP.1은 사용하지 않고 JESTOP.1-2 jumper도 없다.
- K1은 coil 85/86에 18 AWG, main 30/87에 14 AWG를 압착·결착했고 P6KE16CA를 85-86에
  병렬 설치했다. Coil 저항 `91~92.4 ohm`, retention과 continuity는 통과했지만 main terminal
  `280756-4`의 documented AWG 12~10 범위와 14 AWG as-built 편차가 남는다.
- K2 datasheet의 pin diagram이 bottom view임을 반영해 actual component-side coil을
  physical pin 1(+)=`K2_COIL_P`, pin 12(-)=GND로 수정했다. Pin `9->8` hold와 `4->5`
  K1-enable 경로에서 S2 seal-in, S0/S1 drop, release/power-restore no-auto-reenable의
  motor-disconnected control-only subset을 통과했다.
- 이 결과로 complete system을 PASS시키지 않는다. Powered `T-ESTOP-003`의
  `AUX5V -> S0-B -> VO617A -> ESTOP_SENSE/PC7`, formal firmware/PWM `T-ESTOP-004`, full
  `T-ESTOP-005A`, K1/K2 timing/load/thermal과 actual motor `T-ESTOP-007`은 OPEN이다.

다음 실행은 [`remaining bench gates`](../docs/plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md)의
power-off reentry, K2 post-rework direct continuity와 남은 `T-ESTOP-002` wire-break/독립성부터
시작한다. 그 뒤 powered sense `T-ESTOP-003`, `T-ESTOP-004` formal firmware 결합,
main-terminal AWG 편차 해소와 full `T-ESTOP-005A`를 차례로 닫는다.
전체 판정은 계속 `PARTIAL / MOTOR ENERGY NOT RELEASED`다.
