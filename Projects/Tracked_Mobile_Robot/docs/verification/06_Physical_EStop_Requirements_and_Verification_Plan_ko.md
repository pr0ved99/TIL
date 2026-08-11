# Physical E-stop Requirements And Verification Plan

## 목적

이 문서는 Physical E-stop 요구사항의 시험 순서, 증거와 판정을 관리한다.

설계 정본은 [`../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md`](../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md)다.
요구사항 정본은 [`../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md`](../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md)다.
RevB 기능 회로 정본은
[`../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md)다.

이 계획은 다음 두 주장을 분리한다.

```text
Hardware claim
    MCU/software 상태와 무관하게 motor energy path가 차단된다.

Software claim
    STM32가 E-stop을 감지해 output zero와 latch/no-auto-restart를 보장한다.
```

둘 중 하나만 통과하면 Physical E-stop 전체를 `PASS`로 판정하지 않는다.

## MVP gate와 확장 진단의 분리

첫 actual motor 시험을 막는 Physical E-stop gate는 `T-ESTOP-001~005`다. 이 범위는
정격이 확인된 K1/S0/K2 path, no-power continuity, PC7 sense, firmware latch,
motor-disconnected direct downstream rail-off와 no-auto-restart를 검증한다.

`T-ESTOP-007`은 그 gate 뒤 첫 lifted motor setup에서 실제 정지를 확인하는 MVP 시험이다.
`T-ESTOP-006`의 PA4/PB0 dual-rail plausibility, discrepancy fault injection, synchronized
rail transient characterization은 유용한 후속 진단이지만 MVP blocker가 아니다. 이 분리는
direct DMM/continuity evidence를 생략한다는 뜻이 아니며 산업 안전 적합성을 주장하지도 않는다.

## Safety goal traceability

Safety goal과 safe-state vector의 설계 정본은
[`../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md`](../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md)의
`SG-ESTOP-001`이다.

| Safety goal | Basis ID | Derived requirement | Verification |
| --- | --- | --- | --- |
| `SG-ESTOP-001` | `RISK-001`, `ESTOP-001`, `REQ-001`, `VVT-001` | `REQ-ESTOP-001~020` | `T-ESTOP-001~007` |

2026-08-10의 Step 1 definition gate는 다음 항목을 문서 baseline으로 고정했다.

- Hardware-independent motor-energy isolation
- Controller safe-output와 E-stop latch
- Release와 reset의 분리
- Valid reset 뒤 `DISARMED` 유지
- New ARM과 post-reset new command 전 motion 금지
- Electrical shutdown과 mechanical stop evidence의 분리

현재 판정은 `DEFINITION BASELINED / IMPLEMENTATION NOT STARTED / VERIFICATION NOT TESTED`다.
문서 baseline은 아래 `REQ-ESTOP-*` 또는 시험 결과의 `PASS`를 의미하지 않는다.

## Step 2 system-boundary traceability

2026-08-10 Step 2는 RevA actual net과 RevB target path를 분리하고 다음 검증 경계를
baseline으로 고정했다.

| Path | Architecture boundary | Related requirement | Verification consequence |
| --- | --- | --- | --- |
| Motor energy | `VBAT_PROTECTED -> K1 main contact -> MOTOR_VBAT_SAFE -> MDD10A POWER+` | `REQ-ESTOP-003~004`, `016~017`; post-MVP `012~015` | MVP는 K1 open continuity/direct rail voltage와 back-power를 측정; dual-rail ADC 진단은 후속 |
| Relay control | `S0-A NC -> K1 coil permission`; MCU-independent | `REQ-ESTOP-002~004`, `011`, `016` | Press, wire-open, manual re-enable와 coil-power-loss 방향 확인 |
| Monitoring | 5 V `S0-B NC` loop -> optocoupler -> 3.3 V `ESTOP_SENSE`; motor/coil current와 분리 | `REQ-ESTOP-005~010`; post-MVP `012~015` | MVP는 contact-loop current, PC7 level, latch/reset reject; rail plausibility는 후속 |
| Logic power | XL4015/USB controller path remains available candidate | `REQ-ESTOP-008`, `017`; post-MVP `012~014` | Motor rail 역급전과 logic-powered no-auto-restart 확인 |
| Mechanical response | K1/MDD10A 이후 motor/track | `REQ-ESTOP-009`, `019~020` | Electrical rail decay와 stop time/distance를 분리 |

Step 2에서 disconnect 방식은 `K1 DC power relay`로 선택했다. Step 6에서 manual hardware
re-enable과 downstream rail-sense 확장 회로 및 STM32 target pin 후보를 정했다. Step 7에서는
S0/S2/K2/opto 후보를 좁혔지만 K1/F1/main-current part, coil clamps와 divider/protection
value는 여전히 TBD/TBR다. Actual-off
diagnostic 방법은 Step 4에서 downstream rail sensing으로 선택했다.
따라서 현재 판정은 `PATH DEFINITION BASELINED / IMPLEMENTATION NOT STARTED /
VERIFICATION NOT TESTED`다.

## Step 3 hazard traceability

Hazard analysis 정본은
[`../../01_System_Architecture/22_Physical_EStop_Hazard_Analysis_ko.md`](../../01_System_Architecture/22_Physical_EStop_Hazard_Analysis_ko.md)다.

| Hazard group | Primary requirements/tests | Step 3 decision |
| --- | --- | --- |
| `HZ-ESTOP-001` unexpected restart | `REQ-ESTOP-006~008`, `011`, `013~014`; `T-ESTOP-004~005` | Release와 별도 manual K1 hardware re-enable required |
| `HZ-ESTOP-002`, `006~008` isolation/diagnostic | `REQ-ESTOP-002~005`, `009`, `016~018`; post-MVP `012~015` | Direct downstream rail evidence is MVP-mandatory; automatic plausibility is post-MVP |
| `HZ-ESTOP-003~004`, `009`, `011~012` motion/exposure | `REQ-ESTOP-009~010`, `019~020`; `T-ESTOP-006~007` | Fixed stand, exclusion zone, flat surface and reach gate required |
| `HZ-ESTOP-005`, `010` thermal/electrical | `REQ-ESTOP-004`, `016`, `018`, `020`; `T-ESTOP-001~003` | Current/rating data, fuse and instrument preflight required |

12개 hazard의 initial screening은 완료했지만 safeguard 구현과 residual-risk 판정은 아직
없다. `Hazard BASELINED`는 E-stop 구현 또는 시험 `PASS`가 아니다.

## Step 4 FMEA traceability

FMEA 정본은
[`../../01_System_Architecture/23_Physical_EStop_FMEA_ko.md`](../../01_System_Architecture/23_Physical_EStop_FMEA_ko.md)다.

| FMEA group | Failure modes | Verification consequence |
| --- | --- | --- |
| K1 main/coil/clamp | `FM-ESTOP-001~008` | DC rating, continuity, coil transient, drop-out와 downstream rail-decay evidence |
| S0/manual re-enable | `FM-ESTOP-009~015` | Open/cross-wire test, release-only no-rail, deliberate S2 action과 stuck-contact negative test |
| Monitoring/software | `FM-ESTOP-016~020` | Upstream/downstream plausibility, discrepancy latch, reset/ARM/CMD rejection |
| Power/backup isolation | `FM-ESTOP-021~023` | Back-power matrix, fuse/wire record, S1 reach/continuity test |

Step 4는 다음 설계 방향을 고정했다.

- Manual re-enable: `S0-A NC -> [S2 momentary NO || K2-HOLD-NO] -> K2 coil`, K2 pole 2 -> K1 coil
- Actual-off evidence: direct DMM/continuity is MVP-mandatory; protected `MOTOR_VBAT_SAFE_SENSE` is post-MVP diagnostic
- K1 power contact: official minimum switching load보다 작은 seal-in load에 사용 금지
- Coil suppression: exact K1/K2 datasheet와 measured drop-out timing 전까지 TBD

23개 failure mode와 action 및 Step 6 기능 회로는 baselined됐지만, exact parts/values,
KiCad RevB, firmware와 실제 시험은 아직 없다.

## Step 5 requirement baseline

요구사항 정본은
[`../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md`](../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md)다.

| Requirement group | IDs | Primary verification |
| --- | --- | --- |
| Mechanical/hardware interruption | `REQ-ESTOP-001~004` | `T-ESTOP-001~002` |
| Control/restart/software | `REQ-ESTOP-005~011` | `T-ESTOP-003~005` |
| Actual-off diagnostic/clamp | `REQ-ESTOP-016` MVP; `REQ-ESTOP-012~015` post-MVP | `T-ESTOP-001`, `005`; post-MVP `T-ESTOP-006` |
| Integration/operation/evidence | `REQ-ESTOP-017~020` | `T-PWR-003`, `T-ESTOP-001~007` |

20개 requirement는 baselined됐으며 15 MUST/5 SHOULD다. MVP MUST에 연결된
timing/current/voltage TBR은 관련 powered-test gate 전에 닫는다. 오직 post-MVP
`REQ-ESTOP-012~015`/`T-ESTOP-006`에 연결된 TBR은 확장 V-cycle에서 닫는다.

## Step 6 circuit-architecture traceability

기능 회로 정본은
[`../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md)다.

| Circuit decision | Baseline | Verification consequence |
| --- | --- | --- |
| `CD-ESTOP-001` | `VBAT_PROTECTED -> K1-MAIN-NO -> MOTOR_VBAT_SAFE` | K1 open continuity와 actual rail voltage를 직접 측정 |
| `CD-ESTOP-002` | `F2 -> S0-A NC -> [S2 NO OR K2-HOLD-NO] -> K2`; K2 pole 2 -> K1 coil | Initial/release/power-restore OFF와 deliberate S2 re-enable 확인 |
| `CD-ESTOP-003` | K1/K2 coil-side clamp function blocks | Stress와 K1-open/rail-decay timing을 함께 승인 |
| `CD-ESTOP-004` | 5 V S0-B loop -> optocoupler -> external-pull-up PC7 | Contact current, GPIO voltage, 5 V/wire-open, latch와 PWM-zero latency 확인 |
| `CD-ESTOP-005` | PA4 upstream/PB0 downstream independent ADC networks | Post-MVP diagnostic option; MVP schematic/first motor blocker가 아님 |
| `CD-ESTOP-006~007` | Keyed connector/test points and no-backfeed boundary | Cross-wire/continuity와 power-source matrix 실행 |

현재 판정은 `FUNCTIONAL CIRCUIT BASELINED / STEP 7 PARTIAL / IMPLEMENTATION NOT STARTED /
VERIFICATION NOT TESTED`다.

## Step 7 component/rating traceability

부품·정격 정본은
[`../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md`](../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md)다.

| Selection decision | Current status | Verification consequence |
| --- | --- | --- |
| `SD-ESTOP-001` K2 separated control | Baselined architecture | S2 stuck, K2-HOLD/K2-K1 contact fault와 power-restore test 추가 |
| `SD-ESTOP-002` Omron `A22NE-M-PD02-N` | Preferred candidate | Received-part 2NC/direct terminal continuity 확인 |
| `SD-ESTOP-003` Schneider `ZB5AA3 + ZB5AZ009 + ZBE1016` | Conditional | Official minimum-load closure, momentary 1NO continuity와 stuck-closed negative test |
| `SD-ESTOP-004` Panasonic `TX2-12V` | Conditional | Worst-case K2 coil voltage가 9.0 V 이상인지 DMM sweep으로 확인 |
| `SD-ESTOP-005` Vishay `VO617A-3`, 680 ohm/10 kohm candidate | Conditional | 5 V tolerance, contact current, PC7 LOW/HIGH와 wire-open 측정 |
| `SD-ESTOP-006` K1/F1/main-current path | Motor-data blocked | Official motor current 또는 approved characterization 전 powered motor test 금지 |

F2 `0.5 A time-delay`는 preliminary candidate일 뿐이다. Exact fuse/holder curve, K1/K2 clamp,
ADC values는 post-MVP open item으로 유지한다. K1/F1/main wire, connector와 MVP coil clamp가
닫힐 때까지 Step 8 MVP schematic에는 명확한 TBD와 calculation note를 남긴다.

## 상태 정의

| Status | Meaning |
| --- | --- |
| `PLANNED` | 요구사항/절차만 있고 구현 또는 시험 전 |
| `PARTIAL` | Hardware와 software 중 일부만 구현·검증 |
| `BLOCKED` | 선행 부품·계측·회로가 없어 실행 불가 |
| `PASS` | 수용 기준과 저장소 evidence가 모두 충족 |
| `FAIL` | 수용 기준 위반; 원인 수정 전 powered test 금지 |

## 요구사항 요약

상세 shall statement, acceptance criteria, hazard/FMEA source와 TBR register는
[`24_Physical_EStop_Safety_Requirements_ko.md`](../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md)를
유일한 정본으로 사용한다. 이 시험계획에는 status와 test mapping만 유지한다.

| IDs | Scope | Current verification status |
| --- | --- | --- |
| `REQ-ESTOP-001~003` | Actuator, independent NC paths, MCU-independent K1 cut | `NOT TESTED` |
| `REQ-ESTOP-004` | DC rating/fuse/wire coordination | `BLOCKED` |
| `REQ-ESTOP-005~008` | 3.3 V sense, PWM/latch, restart and boot-safe | `NOT TESTED` |
| `REQ-ESTOP-009` | MVP electrical/mechanical evidence separation; post-MVP precision timing | `BLOCKED` |
| `REQ-ESTOP-010~011` | Observability and three-wire manual re-enable | `NOT TESTED` |
| `REQ-ESTOP-012~015` | Downstream rail diagnostic and discrepancy/plausibility | `POST-MVP / NOT TESTED` |
| `REQ-ESTOP-016` | Coil clamp rating and functional K1 drop-out | `BLOCKED` |
| `REQ-ESTOP-017~020` | Back-power, harness, safe test environment and evidence | `NOT TESTED/BLOCKED` |

## Traceability matrix

| Requirement | Design / implementation | Test ID | Required evidence | Status |
| --- | --- | --- | --- | --- |
| `REQ-ESTOP-001~004`, `011`, `016`, `018`, `020` | `CD-ESTOP-001~004`, `006`; power schematic, component/harness records | `T-ESTOP-001~002` | Datasheet, calculation, schematic/ERC, continuity/cross-wire log | `PLANNED/BLOCKED` |
| `REQ-ESTOP-005`, `018` | `CD-ESTOP-004`, `006`; S0-B interface | `T-ESTOP-003` | DMM GPIO voltage table, pin configuration, wire-open log | `PLANNED` |
| `REQ-ESTOP-006~008`, `010` | Safety state/latch and common safe-output handling | `T-ESTOP-004~005` | UART log, GPIO/PWM/direct rail capture, reset/re-enable regression | `PLANNED` |
| `REQ-ESTOP-009`, `016~017` | Functional K1 drop-out, direct rail-off and back-power | `T-PWR-003`, `T-ESTOP-005`, `T-ESTOP-007` | Direct rail observation, power-source matrix and stop evidence | `BLOCKED` |
| `REQ-ESTOP-012~015` | `CD-ESTOP-005`; dual rail ADC plausibility and discrepancy handling | `T-ESTOP-006` | Post-MVP ADC sweep, synchronized waveform and fault injection | `DEFERRED` |
| `REQ-ESTOP-009`, `019~020` | Lifted motor mechanical stop and environment/evidence gate | `T-ESTOP-007` | Fixture photo, synchronized video, stop-time/distance table | `BLOCKED` |

## Test sequence and gates

시험은 아래 순서대로 수행한다. 뒤 단계는 앞 단계의 acceptance가 통과하기 전 실행하지 않는다.

### `T-ESTOP-001` Design and component review

상태: `PLANNED`

Motor와 battery를 연결하지 않은 laptop/document review다.

확인 항목:

- `S0-A` NC relay-control path와 `S0-B` NC auxiliary sense path가 분리돼 있다.
- Power disconnect 위치가 fuse 뒤, MDD10A motor rail 앞이다.
- RevA actual net과 RevB `VBAT_PROTECTED/K1/MOTOR_VBAT_SAFE` target net이 구분돼 있다.
- K1 main contact의 de-energized-open 동작과 `S0-A`/`S0-B` 독립 경로가 명시돼 있다.
- S2 manual re-enable/seal-in과 direct `MOTOR_VBAT_SAFE` measurement point가 명시돼 있다.
- PC7 target pin과 5 V/opto sense가 명시돼 있다. PA4/PB0 divider는 post-MVP option으로
  넣거나 명시적으로 미실장 처리할 수 있으며 `T-ESTOP-001` MVP PASS를 막지 않는다.
- DC breaking rating, continuous current, contact/coil default state가 공식 datasheet로 확인된다.
- Fuse, wire, terminal과 disconnect device의 보호 관계가 문서화된다.
- Logic rail 유지 시 USB/buck back-power 경로가 추가되지 않는다.
- Regenerative braking/back-EMF 검증 항목이 남아 있다.

Acceptance:

```text
No unnamed/TBD safety-critical device in the test build
No AC-only contact rating used as DC interruption evidence
Schematic ERC = 0 errors / 0 warnings
Human review checklist = all checked
```

Evidence filename candidates:

```text
09_Electrical_Design/.../exports/YYYY-MM-DD_..._estop_draft.pdf
09_Electrical_Design/.../reports/YYYY-MM-DD_..._estop_erc.rpt
assets/logs/estop/YYYY-MM-DD_estop_component_review.md
```

### `T-ESTOP-002` Unpowered continuity and wire-break test

상태: `BLOCKED` — E-stop/disconnect part 필요

준비:

- Battery, USB, STM32, ESP32, motor를 모두 분리한다.
- DMM continuity mode를 확인한다.
- Power contact와 auxiliary contact를 식별한다.

절차:

1. K1 coil과 모든 source가 분리된 상태에서 K1 main contact가 open인지 측정한다.
2. Released 상태에서 `S0-A` control NC continuity를 측정한다.
3. Pressed/latched 상태에서 `S0-A` control path가 open인지 확인한다.
4. Released 상태에서 `S0-B` auxiliary sense NC continuity를 측정한다.
5. Pressed/latched 상태에서 `S0-B` sense path가 open인지 확인한다.
6. Control connector와 sense connector를 각각 한쪽씩 분리해 open fault가 재현되는지 확인한다.
7. Mechanical latch가 press 후 유지되고 manual release가 필요한지 확인한다.
8. K1 main contact, coil, S0-A와 S0-B 사이 unintended continuity가 없는지 확인한다.

Acceptance:

| Condition | K1/control path | Sense path |
| --- | --- | --- |
| K1 coil unpowered | Main contact open | Independent |
| S0 released/healthy | `S0-A` closed | `S0-B` closed |
| S0 pressed/latched | `S0-A` open | `S0-B` open |
| Control wire removed | Control open/fault | State independent |
| Sense wire removed | Control state independent | Open/fault |

### `T-ESTOP-003` 3.3 V sense electrical test

상태: `BLOCKED` — sense circuit/pin 필요

Motor power와 MDD10A output은 연결하지 않는다.

측정:

| Point | Healthy expected | Pressed/open expected |
| --- | --- | --- |
| `ESTOP_SENSE` to STM32 GND | Logic LOW | 3.3 V-class HIGH |
| GPIO absolute level | 3.3 V input limits 내 | 3.3 V input limits 내 |
| Wire removed | N/A | HIGH/fault |

Acceptance:

- No 5 V direct input.
- Pressed와 wire break가 동일한 asserted state다.
- Released bounce는 software latch를 clear하지 않는다.
- Power contact와 sense contact에 unintended current sharing이 없다.

### `T-ESTOP-004` Firmware latch and common-safe-path test

상태: `BLOCKED` — firmware sense/latch 필요

Motor-disconnected 상태에서 수행한다.

Test cases:

1. Boot with E-stop released -> `DISARMED`, output zero.
2. Boot with E-stop pressed/open -> ARM reject, output zero.
3. ARM/limited output hook 상태에서 E-stop assert -> both PWM zero, latch set.
4. E-stop physical release -> output remains zero, ARM/CMD reject.
5. Reset request while contact open -> reject.
6. Physical release + explicit reset -> latch clear, still `DISARMED`.
7. New ARM request 전에는 output이 다시 활성화되지 않는다.
8. Sense wire removal -> case 3과 동일하다.

Acceptance:

```text
assertion -> Motor_Output_ForceSafe() path reached
both PWM requests = 0
software latch persists until valid explicit reset
no automatic command replay
all test hooks restored to 0U after test
```

### `T-ESTOP-005` Driver powered, motor disconnected no-auto-restart test

상태: `BLOCKED` — `T-ESTOP-001~004 PASS` 필요

- 검증된 current envelope에 맞는 bench fuse와 switch path를 사용한다. 현재 10 A는 candidate이며 nuisance trip의 원인을 규명하지 않은 채 rating을 높이지 않는다.
- Motor는 MDD10A에서 분리한 상태로 유지한다.
- Logic analyzer로 `ESTOP_SENSE`, `PB6/PWM1`, `PB7/PWM2`를 관찰한다.
- DMM 또는 적절한 probe로 MDD10A motor-power rail을 확인한다.

Acceptance:

- E-stop assert에서 motor-power rail이 hardware로 제거된다.
- PB6/PB7은 software path로 zero가 된다.
- 버튼 release만으로 motor rail/output/motion이 재활성화되지 않는다. Motor rail은 별도 manual hardware re-enable 후에만 재인가될 수 있다.
- K1 expected OFF에서 direct DMM 또는 voltage-appropriate instrument로 downstream rail이
  닫힌 `V_RAIL_OFF_MAX` 이하인지 확인한다. K2/contact state만으로 차단을 추정하지 않는다.
- Explicit reset과 new ARM 전까지 zero 유지다.
- UART/ESP32가 끊겨도 동일하다.

### `T-ESTOP-006` Timing and rail-transient measurement

상태: `DEFERRED / POST-MVP` — logic analyzer, voltage-appropriate measurement와 optional dual-rail ADC 필요

이 시험은 `T-MOTOR-003`의 선행 조건이 아니다. MVP 기본 동작과 actual-stop evidence를 닫은 뒤
진단 깊이를 확장할 때 수행한다.

측정값을 구분한다.

```text
t0: ESTOP_SENSE assertion edge
t1: PWM output reaches inactive
t2: motor rail disconnect state
t3: motor rail decays below defined threshold
```

기록:

- `t1 - t0`: software output-zero latency
- `t2 - t0`: hardware disconnect latency
- Peak/undershoot/overshoot on motor rail
- Contact bounce and sense debounce behavior
- PA4/PB0 upstream/downstream plausibility와 `K1_OFF_DISCREPANCY`/`RAIL_SENSE_FAULT` fault injection

24 MHz, 5 V-class logic analyzer는 STM32 digital signals 관찰용이다. 3S LiPo/MDD10A power rail에 직접 연결하지 않는다. Motor rail의 차단 지연, 감쇠와 overshoot/undershoot는 적절한 voltage rating과 grounding을 가진 oscilloscope/probe로 측정한다. DMM은 steady-state 또는 정적 rail 존재 여부 확인에만 사용하며 transient timing evidence를 대체하지 않는다.

수치 acceptance threshold는 계측 baseline과 hazard review 후 확정한다. 측정 전 임의 숫자를 `PASS` 기준으로 만들지 않는다.

### `T-ESTOP-007` Lifted single-motor stop test

상태: `BLOCKED` — `T-ESTOP-001~005`와 `T-MOTOR-003` PASS, physical fixture 필요

조건:

- 한쪽 motor/track만 완전히 lifted.
- 5~10% 제한 duty.
- Operator 손이 track/motor에서 떨어져 있다.
- Main switch와 battery disconnect에도 즉시 접근 가능하다.
- Current, heat, sound, motion video와 command log를 기록한다.

측정:

- E-stop press에서 command/PWM/rail/motor motion 변화
- Mechanical stop time
- Shaft 또는 track stop distance
- Driver/battery rail abnormal behavior
- Release 후 no-auto-restart

Acceptance threshold는 첫 no-load baseline을 얻은 뒤 수치화한다. `멈춘 것처럼 보임`만으로 PASS하지 않는다.

## Evidence record template

```text
Date/time:
Operator:
Firmware commit:
KiCad revision:
E-stop/disconnect part number:
Datasheet URL/hash:
Battery voltage:
Fuse rating:
Motor connection state:
Instrumentation:
Test ID:
Expected:
Observed:
Measured timing/voltage:
Photos/log/video paths:
Result: PASS / FAIL / PARTIAL
Limits and next action:
```

## Stop rules

다음 중 하나라도 발생하면 즉시 main switch OFF, battery disconnect 후 원인을 조사한다.

- E-stop press에도 power contact가 closed로 남음
- Sense wire open이 healthy로 읽힘
- E-stop release만으로 PWM 또는 motor rail이 자동 재활성화됨
- Motor rail overshoot/역극성/grounding 이상
- Switch, contactor, terminal, wire, fuse holder의 발열·냄새·변색
- Contact welding 또는 mechanical latch 불량
- Logic analyzer ground를 3S power node에 잘못 연결할 위험

## Current decision

```text
Safety goal/safe-state definition: BASELINED (2026-08-10)
System boundary/energy/sense paths: BASELINED (2026-08-10)
Hazard analysis: BASELINED (2026-08-10)
FMEA: BASELINED (2026-08-10)
Disconnect method: K1 DC POWER RELAY SELECTED
Motor-rail re-enable policy: SEPARATE MANUAL HARDWARE ACTION REQUIRED
MVP actual-off evidence: DIRECT DOWNSTREAM CONTINUITY/VOLTAGE MEASUREMENT REQUIRED
Post-MVP diagnostic: PA4/PB0 DUAL-RAIL SENSE SELECTED, DEFERRED
Requirements: 20 BASELINED / 15 MUST / 5 SHOULD / 7 TBR REGISTER ITEMS OPEN (2026-08-10)
Architecture: DRAFTED
Component selection: BLOCKED/TBD
Schematic: NOT STARTED
Firmware: NOT STARTED
Bench verification: NOT TESTED
Overall result: PLANNED
```

Motor-disconnected 단계인 `T-ESTOP-001~005`가 모두 `PASS`되기 전에는
[`T-MOTOR-003`](05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)의 powered
single-motor test를 시작하지 않는다. `T-ESTOP-007`은 그 선행 gate를 통과한 lifted
single-motor setup에서 실행한다. `T-ESTOP-006`은 post-MVP 확장 진단이며 이 gate에 포함하지 않는다.
