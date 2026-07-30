# Physical E-stop Requirements And Verification Plan

## 목적

이 문서는 Physical E-stop 요구사항, 설계 연결, 시험 순서, 증거와 판정을 관리한다.

설계 정본은 [`../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md`](../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md)다.

이 계획은 다음 두 주장을 분리한다.

```text
Hardware claim
    MCU/software 상태와 무관하게 motor energy path가 차단된다.

Software claim
    STM32가 E-stop을 감지해 output zero와 latch/no-auto-restart를 보장한다.
```

둘 중 하나만 통과하면 Physical E-stop 전체를 `PASS`로 판정하지 않는다.

## 상태 정의

| Status | Meaning |
| --- | --- |
| `PLANNED` | 요구사항/절차만 있고 구현 또는 시험 전 |
| `PARTIAL` | Hardware와 software 중 일부만 구현·검증 |
| `BLOCKED` | 선행 부품·계측·회로가 없어 실행 불가 |
| `PASS` | 수용 기준과 저장소 evidence가 모두 충족 |
| `FAIL` | 수용 기준 위반; 원인 수정 전 powered test 금지 |

## 요구사항

| ID | Requirement / acceptance criteria | Priority | Current status |
| --- | --- | --- | --- |
| `REQ-ESTOP-001` | Physical actuator는 red mushroom, mechanical latch, manual release 방식이어야 한다. | MUST | `PLANNED` |
| `REQ-ESTOP-002` | Normally-closed path를 사용해 button press, connector removal 또는 sense-wire open을 stop으로 처리해야 한다. | MUST | `PLANNED` |
| `REQ-ESTOP-003` | MCU hang/reset/software defect와 무관하게 motor energy path를 hardware로 차단해야 한다. | MUST | `PLANNED` |
| `REQ-ESTOP-004` | Motor-current interrupt contact/device는 실제 DC voltage/current, breaking condition, fuse와 wire rating에 적합해야 한다. | MUST | `BLOCKED` |
| `REQ-ESTOP-005` | STM32 auxiliary sense는 3.3 V-safe fail-safe input이어야 하며 power contact와 전기적으로 역할이 분리돼야 한다. | MUST | `PLANNED` |
| `REQ-ESTOP-006` | E-stop assertion 시 공통 safe-output path가 두 PWM을 zero로 만들고 software E-stop latch를 설정해야 한다. | MUST | `PLANNED` |
| `REQ-ESTOP-007` | Physical release만으로 motion이 재개되면 안 되며 explicit reset 뒤에도 `DISARMED` 상태를 유지해야 한다. | MUST | `PLANNED` |
| `REQ-ESTOP-008` | Boot/reset 중 contact open이면 ARM/CMD를 거부하고 motor rail/output을 safe 상태로 유지해야 한다. | MUST | `PLANNED` |
| `REQ-ESTOP-009` | Electrical shutdown latency, motor rail decay, mechanical stop time/distance를 서로 분리해 측정하고 기록해야 한다. | MUST | `BLOCKED` |
| `REQ-ESTOP-010` | E-stop 상태와 reset 거부 원인은 telemetry 또는 bench log로 식별 가능해야 한다. | SHOULD | `PLANNED` |

`REQ-ESTOP-004`와 `REQ-ESTOP-009`는 현재 motor current envelope, 최종 disconnect 부품과 계측 장비가 확정되지 않아 `BLOCKED`다. 이는 설계 작업을 막는 것이 아니라 최종 `PASS` 판정을 막는다.

## Traceability matrix

| Requirement | Design / implementation | Test ID | Required evidence | Status |
| --- | --- | --- | --- | --- |
| `REQ-ESTOP-001~004` | Physical E-stop architecture, power schematic, selected-device datasheet | `T-ESTOP-001`, `T-ESTOP-002` | Datasheet, schematic export/ERC, continuity/DMM log | `PLANNED/BLOCKED` |
| `REQ-ESTOP-005` | STM32 sense circuit and pin allocation | `T-ESTOP-003` | DMM voltage table, pin configuration, wiring photo | `PLANNED` |
| `REQ-ESTOP-006~008` | Safety state/latch, common motor safe-output path | `T-ESTOP-004`, `T-ESTOP-005` | UART log, GPIO/PWM capture, reset regression log | `PLANNED` |
| `REQ-ESTOP-009` | Physical disconnect + MDD10A + lifted motor | `T-ESTOP-006`, `T-ESTOP-007` | Logic capture, rail waveform, video, stop-time/distance table | `BLOCKED` |
| `REQ-ESTOP-010` | TEL/ERR or dedicated bench log | `T-ESTOP-005` | Raw log with asserted/released/reset-rejected states | `PLANNED` |

## Test sequence and gates

시험은 아래 순서대로 수행한다. 뒤 단계는 앞 단계의 acceptance가 통과하기 전 실행하지 않는다.

### `T-ESTOP-001` Design and component review

상태: `PLANNED`

Motor와 battery를 연결하지 않은 laptop/document review다.

확인 항목:

- NC power path와 NC auxiliary sense path가 분리돼 있다.
- Power disconnect 위치가 fuse 뒤, MDD10A motor rail 앞이다.
- Direct-contact 또는 contactor variant가 명시돼 있다.
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

1. Released 상태에서 power NC continuity를 측정한다.
2. Pressed 상태에서 power path가 open인지 확인한다.
3. Released 상태에서 auxiliary NC continuity를 측정한다.
4. Pressed 상태에서 auxiliary path가 open인지 확인한다.
5. Sense connector 한쪽을 분리해 open fault가 재현되는지 확인한다.
6. Mechanical latch가 press 후 유지되고 manual release가 필요한지 확인한다.
7. 각 contact pair 사이와 motor/logic contact 사이 unintended continuity가 없는지 확인한다.

Acceptance:

| Condition | Power path | Sense path |
| --- | --- | --- |
| Released/healthy | Closed | Closed |
| Pressed/latched | Open | Open |
| Sense wire removed | Power state independent | Open/fault |

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
- 버튼 release 후 rail/output이 임의로 재활성화되지 않는다.
- Explicit reset과 new ARM 전까지 zero 유지다.
- UART/ESP32가 끊겨도 동일하다.

### `T-ESTOP-006` Timing and rail-transient measurement

상태: `BLOCKED` — logic analyzer와 voltage-appropriate measurement 필요

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

24 MHz, 5 V-class logic analyzer는 STM32 digital signals 관찰용이다. 3S LiPo/MDD10A power rail에 직접 연결하지 않는다. Motor rail의 차단 지연, 감쇠와 overshoot/undershoot는 적절한 voltage rating과 grounding을 가진 oscilloscope/probe로 측정한다. DMM은 steady-state 또는 정적 rail 존재 여부 확인에만 사용하며 transient timing evidence를 대체하지 않는다.

수치 acceptance threshold는 계측 baseline과 hazard review 후 확정한다. 측정 전 임의 숫자를 `PASS` 기준으로 만들지 않는다.

### `T-ESTOP-007` Lifted single-motor stop test

상태: `BLOCKED` — 모든 앞 단계 PASS, physical fixture 필요

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
Requirements: DRAFTED
Architecture: DRAFTED
Component selection: BLOCKED/TBD
Schematic: NOT STARTED
Firmware: NOT STARTED
Bench verification: NOT TESTED
Overall result: PLANNED
```

Motor-disconnected 단계인 `T-ESTOP-001~006`이 모두 `PASS`되기 전에는 [`T-MOTOR-003`](05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)의 powered single-motor test를 시작하지 않는다. 마지막 `T-ESTOP-007`은 그 선행 gate를 통과한 lifted single-motor setup에서 실행한다.
