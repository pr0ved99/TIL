# Physical E-stop Hazard Analysis

## 목적

이 문서는 Physical E-stop을 포함한 첫 powered drivetrain 시험에서 사람, 장비와 환경에
발생할 수 있는 위해를 운용 상황 기준으로 식별하고 위험 감소 설계 입력을 도출한다.

다음 문서 사이의 연결점이다.

```text
21 Physical E-stop architecture
  -> 22 Hazard analysis (hazardous situation and harm)
  -> Step 4 FMEA (component/function failure mode and effect)
  -> Step 5 safety requirements
  -> Step 6 RevB circuit architecture
  -> staged verification
```

기존 [`18_Fault_Model_and_Safety_Cases_ko.md`](18_Fault_Model_and_Safety_Cases_ko.md)는
controller와 subsystem fault의 safe response를 다룬다. 이 문서는 그보다 앞에서
`어떤 작업에서 누가 어떤 energy에 노출되어 어떤 harm을 입는가`를 다룬다.

## 근거와 주장 경계

2026-08-10 이후 이 분석은 `RISK-001`, `ESTOP-001`, `REQ-001`, `VVT-001`을
`ADOPTED FORWARD BASIS`로 사용한다.

- [ISO 12100:2010](https://www.iso.org/standard/51528.html)의 machinery life-cycle hazard
  identification, risk estimation/reduction과 문서화 원칙을 프로젝트 규모에 맞게 참고한다.
- [ISO 13850:2015](https://www.iso.org/standard/59970.html)의 emergency-stop function
  원칙을 참고한다.
- 정확한 electrical implementation은
  [`21_Physical_EStop_Architecture_ko.md`](21_Physical_EStop_Architecture_ko.md)의
  system boundary를 사용한다.

이 문서는 ISO 12100 적합성, ISO 13849 PL/PLr, IEC 62061/61508 SIL 또는 제품 인증을
주장하지 않는다. 아래 risk matrix는 프로젝트 내부 우선순위 도구이며 표준이 지정한
정량 계산식이나 인증 등급이 아니다.

## 용어 분리

| Term | 이 문서의 의미 | 예시 |
| --- | --- | --- |
| Hazard | 위해를 만들 잠재력을 가진 source | 회전 track, 3S LiPo fault energy |
| Hazardous situation | 사람이 hazard에 노출된 상황 | 손이 track 가까이에 있는데 motor rail이 재인가됨 |
| Hazardous event | 상황을 harm으로 전개시키는 사건 | K1 미개방, unexpected command replay |
| Harm | 실제 부상 또는 손상 | 끼임, 충돌, 화상, 화재 |
| Failure mode | 부품·기능이 요구대로 동작하지 않는 방식 | K1 contact weld; Step 4 FMEA 대상 |
| Safeguard | 위험을 제거하거나 줄이는 수단 | relay isolation, fuse, stand, procedure |

Hazard와 failure mode를 섞지 않는다. 예를 들어 `K1 contact weld`는 failure mode이고,
그 결과 E-stop을 눌러도 robot이 계속 움직여 사람이 track에 노출되는 것이 hazardous
situation이다.

## 분석 경계와 운용 단계

분석 대상은 XT60 이후 power path, controller/USB interaction, K1 relay E-stop path,
MDD10A, motor와 track의 첫 저속 시험까지다.

| Phase | Foreseeable task | 사람의 위치와 energy state |
| --- | --- | --- |
| `L0` 보관·운반 | Battery와 robot 이동 | Motor off; battery chemical energy 존재 |
| `L1` 무전원 조립 | 배선, continuity, connector 작업 | Battery/USB 모두 분리; 손이 회로와 track에 접근 |
| `L2` logic-only | STM32/ESP32/sense 확인 | USB 또는 regulated logic power; motor rail off |
| `L3` driver powered/no motor | K1, MDD10A rail과 no-auto-restart 시험 | Battery source on; motor disconnected |
| `L4` lifted single motor | 저 duty 회전과 stop 측정 | Track 또는 shaft 회전; robot 고정 필요 |
| `L5` lifted dual drivetrain | 좌우 방향·timeout 검증 | 양쪽 track 회전 |
| `L6` flat-ground low speed | 전진·후진·회전 | 사람과 주변 물체가 mobile robot에 노출 |
| `L7` recovery/maintenance | E-stop 원인 확인, reset, 재배선 | 잔류 energy 또는 unexpected re-energization 가능 |

현재 MVP 분석에서 incline, 계단/낙하 가장자리, 사람과의 공유 공간, outdoor wet operation,
무인 autonomous operation은 허용 운용 조건이 아니다. 이 환경은 향후 별도 hazard cycle
없이 시험 범위에 포함하지 않는다.

### Foreseeable misuse

- E-stop mushroom을 release하면 즉시 운전 가능하다고 오해한다.
- 이전 ARM/CMD가 남아 있는 상태에서 reset 또는 relay re-enable을 누른다.
- Robot을 손으로 들고 track 가까이에서 powered test를 한다.
- Fuse가 끊어졌다는 이유만으로 원인 확인 없이 더 큰 fuse로 교체한다.
- AC contact rating만 확인하고 relay를 DC motor path에 사용한다.
- USB와 buck 5 V를 동시에 연결하거나 logic wire를 통해 motor rail을 역급전한다.
- Battery가 연결된 상태에서 DMM mode, oscilloscope ground 또는 wiring을 변경한다.
- E-stop이 멀리 있거나 가려진 상태에서 ground test를 시작한다.

## 정성 risk-screening 방법

### Severity

| Level | 프로젝트 정의 |
| --- | --- |
| `S1` | Injury 없음 또는 경미한 장비/데이터 손상 |
| `S2` | 가벼운 타박·찰과상·작은 화상처럼 일반적으로 회복 가능한 harm |
| `S3` | 끼임·충돌·낙하로 치료가 필요한 부상 또는 중대한 장비 손상 |
| `S4` | 영구적 중상, 생명 위협 또는 주변으로 확대될 수 있는 배터리/배선 화재 |

### Likelihood under the stated test phase

| Level | 프로젝트 정의 |
| --- | --- |
| `L1` | 정상·예상 오사용 조건에서 매우 드물 것으로 판단됨 |
| `L2` | 특정 fault 또는 오사용 조합에서 가능함 |
| `L3` | 반복 시험에서 현실적으로 노출되거나 발생할 수 있음 |
| `L4` | 현재 구조나 작업 방식에서 빈번하거나 거의 예상됨 |

Motor current, robot mass, actual speed와 stop distance가 아직 없으므로 likelihood는 failure
probability 계산값이 아니다. 근거가 부족할 때는 `L1`로 낮추지 않고 보수적으로 평가한다.

### Initial priority matrix

| Severity \ Likelihood | `L1` | `L2` | `L3` | `L4` |
| --- | --- | --- | --- | --- |
| `S1` | LOW | LOW | MEDIUM | MEDIUM |
| `S2` | LOW | MEDIUM | HIGH | HIGH |
| `S3` | MEDIUM | HIGH | HIGH | CRITICAL |
| `S4` | HIGH | HIGH | CRITICAL | CRITICAL |

- `CRITICAL`: 현재 조건에서 해당 powered task를 금지하고 design change를 먼저 한다.
- `HIGH`: 해당 motor-power 또는 ground-test gate 전에 risk reduction과 시험이 필수다.
- `MEDIUM`: 관련 단계 전에 보호수단과 확인 절차를 반영한다.
- `LOW`: 문서화·monitoring하며 변경 시 재평가한다.

## Initial hazard log

아래 등급은 safeguard 구현 전 또는 아직 검증되지 않은 현재 상태의 initial screening이다.
`Residual risk`는 Step 9의 실제 시험 뒤에만 판정한다.

| ID | Phase | Hazardous situation / event | Foreseeable harm | Initial risk |
| --- | --- | --- | --- | --- |
| `HZ-ESTOP-001` | L2~L7 | Power-up, E-stop release, relay re-enable 또는 MCU reset에서 stale ARM/CMD가 재사용되어 unexpected motion 발생 | Track 끼임, 충돌, robot 낙하 | `S3/L3 = HIGH` |
| `HZ-ESTOP-002` | L3~L7 | E-stop을 눌렀지만 K1 path가 motor-energy feed를 실제로 열지 못함 | 계속되는 motion에 의한 끼임·충돌 | `S3/L2 = HIGH` |
| `HZ-ESTOP-003` | L4~L6 | K1이 열리고 PWM이 zero여도 inertia, back-EMF 또는 drivetrain 상태 때문에 예상 거리 안에 정지하지 않음 | 사람·물체 충돌, bench/edge 낙하 | `S3/L3 = HIGH` |
| `HZ-ESTOP-004` | L4~L5, L7 | Lifted test나 jam 확인 중 손·옷·wire가 회전 shaft/track에 접근 | 끼임, 베임, entanglement | `S3/L3 = HIGH` |
| `HZ-ESTOP-005` | L3~L7 | Stall/short 또는 과소 정격 relay·wire·connector가 과열되고 contact가 용착되거나 LiPo fault energy가 지속됨 | 화상, 연기, 주변으로 확대되는 화재 | `S4/L2 = HIGH` |
| `HZ-ESTOP-006` | L2~L5 | Logic rail/USB/PWM-DIR path가 open K1을 우회해 `MOTOR_VBAT_SAFE` 또는 driver 내부를 역급전 | 예기치 않은 motor energization, 회로 손상·발열 | `S3/L2 = HIGH` |
| `HZ-ESTOP-007` | L1~L5 | S0-A/S0-B connector 오배선·단선·단락이 false healthy 표시 또는 잘못된 K1 동작을 만듦 | E-stop 기능 상실 또는 unexpected motion | `S3/L2 = HIGH` |
| `HZ-ESTOP-008` | L3~L6 | Coil suppression, contact bounce 또는 control transient 때문에 K1 drop-out이 지연되거나 motor rail이 간헐 재인가됨 | stop 지연, 충돌, driver transient damage | `S3/L2 = HIGH` |
| `HZ-ESTOP-009` | L4~L6 | Operator가 E-stop/main switch에 즉시 닿지 못하거나 actuator를 혼동함 | hazard exposure time 증가, 충돌·끼임 | `S3/L3 = HIGH` |
| `HZ-ESTOP-010` | L1~L3, L7 | Battery가 연결된 상태에서 probe ground, DMM current mode 또는 rewiring으로 short circuit 생성 | arc, 화상, wire/connector/LiPo 화재 | `S4/L2 = HIGH` |
| `HZ-ESTOP-011` | L6 | Incline/edge에서 motor torque를 제거했을 때 brake가 없어 coast·roll·fall함 | 충돌, robot/주변 물체 손상, 부상 | `S3/L2 = HIGH` |
| `HZ-ESTOP-012` | L7 | E-stop/main switch 뒤에도 capacitor, regenerative energy 또는 움직이는 track의 mechanical energy가 남아 있음 | 작은 화상·쇼트·손 끼임 | `S2/L2 = MEDIUM` |

## Risk-reduction controls and verification mapping

위험 감소는 가능한 경우 `inherently safer design -> protective measure -> information/procedure`
순으로 적용한다. 절차만으로 electrical/mechanical 설계 결함을 덮지 않는다.

| Hazard | Required or candidate control | Verification / evidence | Current state |
| --- | --- | --- | --- |
| `HZ-ESTOP-001` | K1은 release만으로 재인가하지 않고 별도 manual hardware re-enable 필요; firmware는 latch, `DISARMED`, new ARM/post-reset CMD 적용 | `T-ESTOP-004~005`, reset/replay raw log, rail/PWM capture | Design input fixed; circuit/firmware pending |
| `HZ-ESTOP-002` | De-energized-open K1, DC rating, accessible S1 main switch; K1 off-state를 실제 rail 또는 검증된 feedback으로 확인 | `T-ESTOP-001~002`, `005~006`, datasheet, continuity/rail waveform | Rating/feedback TBD |
| `HZ-ESTOP-003` | Low-duty staged test, exclusion distance, electrical latency와 mechanical stop time/distance 분리 | `T-ESTOP-006~007`, synchronized capture/video/table | Blocked until hardware |
| `HZ-ESTOP-004` | Robot을 fixture/stand에 고정, 한 motor부터 시험, 손·옷·wire exclusion zone, remote command | Fixture photo, preflight checklist, `T-ESTOP-007` video | Procedure baseline; physical evidence pending |
| `HZ-ESTOP-005` | Motor current envelope, K1/fuse/wire/connector DC rating과 derating; current/temperature stop rule | Official datasheets, calculation, current/thermal log, fuse record | Motor data blocker |
| `HZ-ESTOP-006` | Motor/logic branch 분리, USB/buck power policy, logic-only 상태에서 downstream rail measurement | `T-PWR-003`, `T-ESTOP-005~006`, DMM/scope record | Not tested |
| `HZ-ESTOP-007` | S0-A/S0-B 독립 NC, 서로 구분되는 label/connector, external pull-up, open/cross-wire test | `T-ESTOP-002~004`, continuity and voltage table | Schematic/hardware pending |
| `HZ-ESTOP-008` | Coil suppression을 release-time과 함께 설계; K1 control transient/contact bounce와 rail decay 측정 | K1 datasheet, `T-ESTOP-006` coil/sense/rail capture | Step 4/6 input |
| `HZ-ESTOP-009` | Red mushroom을 operator reach에 고정하고 S1/battery disconnect 접근 유지; ground-test spotter/clear zone | Layout review, reach test, test photo/video | Mounting TBD |
| `HZ-ESTOP-010` | Battery/USB 분리 후 rewiring, current-limited first energization, voltage-rated differential measurement, logic analyzer ground 제한 | Preflight checklist, instrument/setup photo, stop rules | Procedure baseline |
| `HZ-ESTOP-011` | 첫 ground test는 평탄면만 허용; incline/edge는 holding/braking hazard cycle 전 금지 | `T-ESTOP-007`, `T-DRIVE-001` environment record | Operating restriction fixed |
| `HZ-ESTOP-012` | Stop 뒤 rail decay 확인, battery disconnect, track 완전 정지와 DMM 확인 후 접근 | `T-ESTOP-006~007`, shutdown checklist | Evidence pending |

## Step 3에서 도출한 design inputs

아래 항목은 Step 5에서 검증 가능한 `REQ-*` 문장으로 변환한다.

| ID | Derived design input | Reason |
| --- | --- | --- |
| `DI-ESTOP-001` | E-stop mechanical release만으로 K1 motor rail을 재인가하지 않는다. 별도 manual hardware re-enable action이 필요하다. | `HZ-ESTOP-001` stale command/unexpected motion risk 감소 |
| `DI-ESTOP-002` | K1 off command/condition과 실제 downstream motor-rail 상태의 불일치를 검출 또는 시험할 수 있어야 한다. | `HZ-ESTOP-002`, `006`; S0-B alone cannot prove K1 opened |
| `DI-ESTOP-003` | S1 main switch와 battery disconnect는 K1/MCU와 독립된 operator backup isolation으로 접근 가능해야 한다. | `HZ-ESTOP-002`, `009` residual risk control |
| `DI-ESTOP-004` | S0-A control과 S0-B sense connector/wire는 식별 가능해야 하고 open/cross-wire test가 가능해야 한다. | `HZ-ESTOP-007` false healthy 방지 |
| `DI-ESTOP-005` | K1 coil suppression은 electrical protection뿐 아니라 measured drop-out/rail-decay timing을 만족해야 한다. | `HZ-ESTOP-008` delayed stop 방지 |
| `DI-ESTOP-006` | Relay/fuse/wire selection은 motor current envelope 전까지 최종화하지 않는다. | `HZ-ESTOP-005` thermal/fire risk와 contact weld 감소 |
| `DI-ESTOP-007` | 첫 motor/ground 시험은 fixed stand, exclusion zone와 flat surface gate를 통과해야 한다. | `HZ-ESTOP-003~004`, `009`, `011` exposure 감소 |
| `DI-ESTOP-008` | Powered test마다 energy source, fuse, load, fixture, operator reach와 stop condition을 기록한다. | Risk estimate와 evidence boundary 재현성 확보 |

`DI-ESTOP-001`로 motor-rail re-energization policy를 결정했다. 정확한 relay self-hold,
reset button, interlock contact와 power-up behavior는 Step 4 FMEA 뒤 Step 6 회로에서 확정한다.

`DI-ESTOP-002`는 영구적인 K1 auxiliary feedback을 바로 확정한 것이 아니다. Force-guided
contact가 아닌 일반 relay auxiliary contact의 진단 한계, downstream voltage sensing,
cost/complexity와 residual risk를 Step 4에서 비교한다. 최소한 bench verification에서는
`MOTOR_VBAT_SAFE`의 실제 voltage/decay evidence가 필수다.

## FMEA handoff

Step 4에서는 최소한 다음 failure mode를 분석한다.

- K1 main contact welded/stuck open/high resistance
- K1 coil open/short 또는 control power loss
- S0-A stuck closed/open, S0-B stuck closed/open
- S0-A/S0-B connector swap, short-to-GND/3V3/VBAT
- Re-enable contact stuck 또는 release edge에서 unintended K1 energization
- Flyback device open/short와 drop-out delay
- Fuse wrong rating/bypass, wire/terminal high resistance
- Logic/USB back-power into MDD10A or `MOTOR_VBAT_SAFE`
- STM32 input stuck/firmware hang/telemetry false healthy
- Main switch inaccessible or contact failure

FMEA에서는 각 failure mode의 local effect, system effect, detection, current control, recommended
action과 verification을 위 `HZ-ESTOP-*`에 다시 연결한다.

Step 4 결과 정본은
[`23_Physical_EStop_FMEA_ko.md`](23_Physical_EStop_FMEA_ko.md)다. 23개 failure mode를
분석해 three-wire manual re-enable target과 downstream motor-rail diagnostic을 선택했다.

## Step 3 gate

```text
Life-cycle/task boundary: BASELINED
Foreseeable misuse: BASELINED
Hazard log: 12 HAZARDS IDENTIFIED
Initial qualitative screening: COMPLETE
Manual K1 hardware re-enable policy: REQUIRED
Flat-surface/fixture/exclusion operating limits: REQUIRED
K1 actual-off diagnostic method at Step 3 exit: OPEN; RESOLVED BY STEP 4 AS DOWNSTREAM RAIL SENSE
Component rating and motor current data: BLOCKED/TBD
Residual risk acceptance: NOT PERFORMED
Hardware/runtime verification: NOT TESTED
```

이 gate는 hazard identification과 초기 우선순위가 문서화됐다는 뜻이다. 위험이 충분히
감소했거나 Physical E-stop이 안전하다는 판정이 아니다.
