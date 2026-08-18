# Physical E-stop RevB Circuit Architecture

## 목적

이 문서는 `REQ-ESTOP-001~020`을 RevB 회로도로 옮기기 전에 기능 회로, net, 인터페이스와
고장 시 동작을 고정하는 Step 6 정본이다.

```text
SG-ESTOP-001
-> hazard/FMEA
-> REQ-ESTOP-001~020
-> 이 문서의 CD-ESTOP-001~007
-> Step 7 component/rating selection
-> Step 8 KiCad RevB/ERC
-> T-ESTOP-001~007
```

이 단계에서 확정하는 것은 **어떤 기능 블록을 어떤 순서로 연결할지**다. 릴레이 형번,
접점·코일 정격, 퓨즈값, 저항·커패시터값, clamp 소자와 connector 형번은 Step 7에서 공식
자료와 계산으로 정한다.

## 근거와 주장 경계

2026-08-10 이후 이 설계는 `ARCH-001`, `RISK-001`, `FMEA-001`, `SAFE-CTRL-001`,
`ESTOP-001`, `ELEC-DOC-001`, `PCB-HAR-001`, `PART-001`, `VVT-001`을
`ADOPTED FORWARD BASIS`로 사용한다.

- Physical E-stop 원칙은 ISO 13850, IEC 60204-1과 IEC 60947-5-5를 참고한다.
- STM32 핀 후보는 ST의 STM32F446xC/E datasheet `DS10693`과 NUCLEO-64 user manual
  `UM1724`를 기준으로 현재 `.ioc`와 충돌 여부를 확인했다.
- 이 문서는 산업 안전 인증, ISO 13849 PL, SIL, single-fault tolerance 또는 표준 전체
  적합성을 주장하지 않는다.
- 일반 relay 보조접점과 STM32 ADC는 safety-rated/force-guided monitoring channel이 아니다.
- Architecture baseline은 회로도 작성, ERC, 부품 적합성 또는 실제 차단 시험 PASS가 아니다.
- `CD-ESTOP-005` PA4/PB0 dual-rail ADC는 post-MVP diagnostic option이다. MVP Step 8과
  첫 motor gate에는 K1 hardware cut, three-wire re-enable, PC7 sense와 direct rail test point만 필수다.

공식 MCU 자료:

- [STM32F446xC/E datasheet DS10693](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)
- [STM32 Nucleo-64 boards user manual UM1724](https://www.st.com/resource/en/user_manual/DM00105823-.pdf)

## Step 6 설계 입력

| Input | Circuit consequence |
| --- | --- |
| `REQ-ESTOP-003` | K1 주접점은 firmware와 무관하게 `MDD10A POWER+`를 차단한다. |
| `REQ-ESTOP-005~006` | S0-B는 motor/coil current와 분리된 fail-safe input이며 PC7에는 3.3 V logic만 들어간다. |
| `REQ-ESTOP-007~008`, `011` | Release와 power restore만으로 K1가 재인가되지 않는 3선식 수동 재투입 회로를 사용한다. |
| `REQ-ESTOP-012~015` | Post-MVP option으로 K1 전·후 rail voltage를 ADC로 직접 비교한다. MVP는 downstream test point를 직접 측정한다. |
| `REQ-ESTOP-016` | Coil clamp는 위치만 확정하고 topology/value는 K1 자료와 timing 측정으로 승인한다. |
| `REQ-ESTOP-017` | Logic/USB/GPIO가 open K1을 우회하는 backfeed path가 없는지 별도 시험한다. |
| `REQ-ESTOP-018` | Coil, sense와 high-current connector를 구분하고 오접속을 예방한다. |

## 전체 기능 구조

```text
B1 3S LiPo+
  -> J1 XT60
  -> F1 MAIN FUSE
  -> S1 MAIN_DC_SWITCH
  -> VBAT_PROTECTED
       +-> K1-MAIN-NO
       |    -> MOTOR_VBAT_SAFE
       |         -> MDD10A POWER+
       |
       +-> logic/aux branch -> XL4015 -> controller/sensor power
       |
       +-> F2 ESTOP_CONTROL_FUSE
            -> S0-A NC
            -> ESTOP_CONTROL_PERMISSION
                 +-> [S2 momentary NO OR K2-HOLD-NO]
                 |    -> K2 coil -> PWR_GND
                 |
                 +-> K2-K1-ENABLE-NO
                      -> K1 coil -> PWR_GND

B1 3S LiPo- -> PWR_GND -> MDD10A POWER-/buck/controller signal reference

5 V -> S0-B NC -> optocoupler LED -> GND
3.3 V pull-up -> optocoupler transistor -> ESTOP_SENSE -> STM32 GPIO candidate PC7
VBAT_PROTECTED -> protected divider/filter -> VBAT_PROTECTED_SENSE -> PA4 ADC (POST-MVP OPTION)
MOTOR_VBAT_SAFE -> protected divider/filter -> MOTOR_VBAT_SAFE_SENSE -> PB0 ADC (POST-MVP OPTION)
```

K1 주접점이 여는 것은 positive motor feed 하나다. `PWR_GND`, PWM/DIR와 logic power는
연결된 상태이므로 이 구조는 galvanic isolation이 아니다.

## Circuit decision records

### `CD-ESTOP-001`: K1은 high-side de-energized-open motor-feed relay다

```text
VBAT_PROTECTED -> K1-MAIN-NO -> MOTOR_VBAT_SAFE -> MDD10A POWER+
```

- K1 coil OFF 또는 control-wire open이면 주접점의 정상 상태는 open이다.
- K1는 motor current를 직접 운반하는 유일한 E-stop controlled contact다.
- Logic branch는 K1 upstream에 남겨 fault 기록과 rail 진단을 계속할 수 있게 한다.
- K1 main contact weld/stuck-closed는 여전히 가능한 dangerous failure다. S1과 battery
  connector가 독립적인 backup source isolation으로 남는다.

의도는 MCU가 hang하거나 UART가 잘못 동작해도 S0-A가 K1 coil permission을 물리적으로
제거하게 하는 것이다.

### `CD-ESTOP-002`: S0-A와 S2/K2가 3선식 수동 재투입을 구성한다

```text
VBAT_PROTECTED
  -> F2
  -> ESTOP_CTRL_FUSED
  -> S0-A NC
  -> ESTOP_CONTROL_PERMISSION
       +-> +-> S2 momentary NO ------+
       |   |                         |
       |   +-> K2-HOLD-NO -----------+
       |        -> K2_COIL_P -> K2 coil -> PWR_GND
       |
       +-> K2-K1-ENABLE-NO -> K1_COIL_P -> K1 coil -> PWR_GND
```

- Initial power-up: K2가 OFF이므로 S2를 누르기 전 K1도 OFF.
- S2 press: K2가 energize되고 pole 1이 K2를 hold하며 pole 2가 K1 coil을 energize한다.
- S0 press/control-wire break/power loss: S0-A가 공통 permission을 열어 K2와 K1을 OFF한다.
- S0 release: K2-HOLD가 이미 open이므로 K2/K1 OFF 유지.
- Power restoration: K2가 OFF이므로 자동 재인가되지 않는다.
- MCU는 K2/K1 coil을 energize하거나 seal-in을 유지하는 경로에 포함하지 않는다.

F2는 main motor fuse F1과 별도의 control-branch protection 기능이다. F2의 정격과 fuse
형태는 K1+K2 coil current, S0/S2/K2 contact rating과 wire ampacity로 Step 7에서 정한다.

Step 6 초기의 K1-AUX seal-in은 Step 7 official minimum-load review에서 폐기했다. K1 power
contact의 최소 부하가 coil 자기유지 전류보다 큰 후보가 확인됐기 때문이다. K2를 분리해
power relay와 low-current control relay의 역할을 나누며, K2 contact도 K1 주접점 open의
증거로 사용하지 않는다.

### `CD-ESTOP-003`: coil suppression은 각 coil 바로 옆의 미확정 clamp block이다

```text
K1_COIL_P -> K1 coil -> PWR_GND
               |          |
               +-- X1_K1_CLAMP --+

K2_COIL_P -> K2 coil -> PWR_GND
               |          |
               +-- X2_K2_CLAMP --+
```

`X1_K1_CLAMP`와 `X2_K2_CLAMP`는 회로 기능명이며 확정 부품명은 아니다. Diode,
diode+zener 또는 TVS 중 하나를 자동 채택하지 않는다.

Step 7/9 승인 조건:

1. Maximum coil current와 stored energy에서 S0/S2/K2 contact/clamp stress가 정격 안이다.
2. Clamp가 short되면 F2가 control branch를 보호하고 K1는 safe-direction으로 OFF된다.
3. Clamp turn-off가 `T_K1_OPEN_MAX`와 `T_RAIL_DECAY_MAX`를 만족한다.
4. S0-A, coil voltage와 `MOTOR_VBAT_SAFE`를 동시에 측정한 evidence가 있다.

### `CD-ESTOP-004`: S0-B는 5 V contact loop와 PC7 optocoupler input을 사용한다

```text
ESTOP_SENSE_5V
  -> R_OPTO_LED
  -> J_S0B -> S0-B NC
  -> U_ESTOP_SENSE LED
  -> LOGIC_GND

STM32 3V3
  -> R_PC7_PULLUP
  -> ESTOP_SENSE -> PC7 GPIO/EXTI candidate
  -> U_ESTOP_SENSE transistor
  -> LOGIC_GND

healthy/closed = LOW
pressed/open or wire break = HIGH
```

- External 3.3 V pull-up을 사용하고 internal pull-up만으로 정상 동작을 주장하지 않는다.
- S0-B contact에는 5 V에서 공식 minimum applicable load보다 큰 전류를 흘린다.
- PC7에는 optocoupler transistor 쪽 3.3 V logic만 연결한다.
- S0-B에는 coil current나 motor current가 흐르지 않는다.
- Contact open 순서나 EXTI 처리와 무관하게 S0-A hardware path가 K1를 제거해야 한다.
- RC와 software debounce는 chatter를 줄일 수 있지만 first asserted edge의 safe-output 처리를
  의도적으로 늦추면 안 된다.
- Optocoupler transistor short, PC7 short-to-GND 또는 contact stuck-closed는 false healthy가
  될 수 있는 잔여 고장이다.
  Startup/session press test, S0-B/rail discrepancy와 harness inspection으로 관리한다.

PC7은 현재 motor/UART/encoder/CAN/SWD 배정과 충돌하지 않고 NUCLEO-F446RE Arduino D9로
접근 가능한 후보다. 현재 `.ioc`에는 아직 구성되지 않았으므로 CubeMX pin-conflict review,
GPIO input threshold 계산과 실제 전압 시험 전까지 `CANDIDATE`다.

### `CD-ESTOP-005`: K1 전·후 독립 ADC 비교는 post-MVP diagnostic option이다

```text
VBAT_PROTECTED
  -> R_UP_TOP_A + R_UP_TOP_B
  -> VBAT_PROTECTED_DIV
       -> R_UP_BOTTOM -> ANALOG_GND
       -> C_UP_FILTER -> ANALOG_GND
       -> R_UP_SERIES -> VBAT_PROTECTED_SENSE -> PA4 / ADC12_IN4 candidate

MOTOR_VBAT_SAFE
  -> R_DN_TOP_A + R_DN_TOP_B
  -> MOTOR_VBAT_SAFE_DIV
       -> R_DN_BOTTOM -> ANALOG_GND
       -> C_DN_FILTER -> ANALOG_GND
       -> R_DN_SERIES -> MOTOR_VBAT_SAFE_SENSE -> PB0 / ADC12_IN8 candidate
```

두 divider는 서로 전기적으로 독립이어야 한다. `R_*_TOP_A/B`처럼 high-side resistance를
둘로 나누는 구조는 단일 부품 short와 voltage/power stress 검토를 가능하게 하기 위한 target이다.
정확한 값과 ADC protection topology는 Step 7에서 정한다.

이 block은 KiCad RevB MVP에서 생략하거나 명확한 `DNP/POST-MVP` footprint로 둘 수 있다.
미실장이라도 `TP_VBAT_PROTECTED`와 `TP_MOTOR_VBAT_SAFE`에서 direct DMM/continuity 검증은
반드시 가능해야 한다.

- PA4/A2: 기존 battery ADC 후보를 `VBAT_PROTECTED_SENSE` upstream reference로 구체화한다.
- PB0/A3: `MOTOR_VBAT_SAFE_SENSE` downstream candidate로 신규 배정한다.
- DS10693은 PA4를 `ADC12_IN4`, PB0를 `ADC12_IN8`로 식별한다.
- UM1724는 NUCLEO-F446RE에서 PA4/PB0를 Arduino A2/A3로 제공한다.
- 현재 `.ioc`에서 두 핀은 사용되지 않았지만 아직 ADC로 설정되지도 않았다.

ADC diagnostic logic은 다음 두 조건을 모두 사용한다.

1. K1 expected OFF 뒤 `T_RAIL_DECAY_MAX`가 지났을 때 downstream이
   `V_RAIL_OFF_MAX`를 넘으면 `K1_OFF_DISCREPANCY`.
2. Deliberate S2 re-enable 뒤 ARM 전에 upstream/downstream이 정한 tolerance 안에서
   일치하지 않으면 `RAIL_SENSE_FAULT`.

두 번째 비교가 없으면 downstream divider open이 정상 OFF처럼 보일 수 있다. 이 비교를
추가해 false-low/open을 motion 전 진단한다. ADC는 physical disconnect가 아니라 diagnostic
channel이며 DMM/scope 측정을 대체하지 않는다.

`MOTOR_VBAT_SAFE`가 자연 방전만으로 timing을 만족하지 못할 경우를 대비해
`R_RAIL_BLEED` footprint를 RevB 후보로 둔다. Populate 여부, resistance와 power rating은
no-motor rail-decay 측정 뒤 결정한다.

### `CD-ESTOP-006`: safety 관련 connector와 test point를 기능별로 분리한다

| Functional name | Conductors | Rule |
| --- | --- | --- |
| `J_PWR_IN` | Battery positive/negative | XT60 polarity 고정, high-current 전용 |
| `J_K1_MAIN` | `VBAT_PROTECTED`, `MOTOR_VBAT_SAFE` | High-current terminal, logic connector와 물리적 분리 |
| `J_S0A_CTRL` | S0-A control loop 2선 | Coil-control 전용, S0-B와 비호환 keying |
| `J_S0B_SENSE` | 5 V contact loop/S0-B 2선 | Sense 전용, S0-A와 비호환 keying |
| `J_S2_REENABLE` | S2 momentary NO 2선 | Re-enable 전용 label과 momentary switch |
| `J_K2_CONTROL` | K2 coil/2-contact control interface | K1 main terminal과 분리, pinout 기록 |
| `J_K1_COIL` | K1 coil interface | K1 main contact terminal과 분리, polarity/clamp 기록 |

Exact connector family, current/voltage rating, wire gauge, color와 strain relief는 Step 7에서
정한다. 같은 2-pin housing을 S0-A와 S0-B에 무구분으로 사용하지 않는다. 부품 제약상 같은
family를 사용해야 한다면 서로 다른 key/code 또는 하나의 keyed multi-pole harness와 100%
continuity test를 요구한다.

RevB에는 최소 다음 측정점을 둔다.

```text
TP_VBAT_PROTECTED
TP_MOTOR_VBAT_SAFE
TP_K1_COIL_P
TP_K2_COIL_P
TP_ESTOP_SENSE
TP_UPSTREAM_ADC          (POST-MVP option)
TP_DOWNSTREAM_ADC        (POST-MVP option)
TP_LOGIC_GND
TP_PWR_GND
```

Test point는 DMM/scope probe가 high-current terminal을 미끄러져 short시키는 위험을 줄이고,
`T-ESTOP-003/005/006`의 trigger와 rail evidence를 반복 측정하기 위한 것이다.

### `CD-ESTOP-007`: logic connection은 K1 open을 우회할 권한이 없다

- PWM/DIR는 K1 open 중에도 MDD10A logic pin에 연결될 수 있지만 firmware가 zero로 유지한다.
- PWM/DIR zero는 `MOTOR_VBAT_SAFE` physical isolation 증거가 아니다.
- USB, XL4015, encoder 5 V, UART와 GPIO를 각각 단독/복합 공급한 power-source matrix에서
  downstream rail과 비정상 current/heat를 확인한다.
- Divider, MCU protection diode, MDD10A logic input 또는 buck을 통한 backfeed가
  `V_RAIL_OFF_MAX`를 넘으면 isolation/series element 또는 power architecture를 재설계한다.
- Common `PWR_GND`가 남으므로 open K1를 감전·정비용 complete isolation으로 표현하지 않는다.

## 정상 및 전이 truth table

| S1/source | S0 | S2 action | K1 / motor rail | `ESTOP_SENSE` | Required software condition |
| --- | --- | --- | --- | --- | --- |
| OFF | released or pressed | none | OFF / de-energized | USB logic이 있으면 contact 상태 반영 | PWM zero, no motion |
| ON | released | none after initial power | OFF / de-energized | LOW | `DISARMED`, `K1_REENABLE_REQUIRED` |
| ON | released | deliberate press | ON / present after checks | LOW | 여전히 `DISARMED`; ARM 전 rail plausibility 확인 |
| ON | pressed/latched | irrelevant | OFF / decay | HIGH | immediate safe output, E-stop latch, ARM/CMD reject |
| ON | released after press | none | OFF / de-energized | LOW | latch 유지, release alone does not re-enable |
| Restored after loss | released | none | OFF / de-energized | LOW | boot safe, deliberate S2 required |
| ON, K1 main welded | pressed | irrelevant | Unexpected HIGH | HIGH | `K1_OFF_DISCREPANCY`, outputs zero, S1/battery isolation required |

K1 manual re-enable, software reset, new ARM과 new CMD는 서로 다른 권한이다. 어느 하나만으로
motion을 복구하지 않으며, 수행 순서가 달라도 stale command를 재사용하지 않는다.

## 고장 방향 검토

| Fault | Expected circuit effect | Remaining limitation/control |
| --- | --- | --- |
| S0-A/control wire open | K1 coil OFF, motor rail OFF | Moving/incline 상태의 coast 위험은 별도 mechanical test |
| S0-A short/bypass | K1 may stay ON | S0-B vs rail discrepancy, preflight, S1 backup |
| S0-B/sense wire open | GPIO HIGH, software latch | Hardware K1는 S0-A에 의존 |
| S0-B short-to-GND | False healthy 가능 | Session press test와 rail comparison; single-fault tolerant 미주장 |
| S2 stuck open | K1 re-enable 불가 | Bypass 금지, inspect/repair |
| S2 stuck closed | K2-HOLD가 open인 initial state에서는 단독 auto-reenable 금지 | Step 8 cross-contact review와 fault injection |
| K2-HOLD welded/stuck closed | Power restore/release 뒤 auto-reenable 위험 | `T-ESTOP-004/005`, software DISARMED, S1 backup; 일반 safety relay가 아님 |
| K2-K1-ENABLE welded | K2 OFF 뒤에도 K1 coil path가 남을 수 있음 | S0-A는 common upstream cut 유지; coil/rail discrepancy test |
| K2 coil open/control fault | K1 re-enable 불가 | Availability loss, inspect/repair |
| K1 coil open/control fuse open | K1 OFF | Availability loss, fault inspection |
| K1 main welded | Coil OFF에도 rail HIGH | Direct rail discrepancy; S1/battery removal |
| Clamp open | Turn-off transient | Scope stress test와 rated clamp 필요 |
| Clamp short | F2 trip/K1 OFF target | F2 coordination 필요 |
| Downstream divider open | False-low 가능 | K1 ON pre-ARM upstream/downstream comparison |
| Divider short/ADC overrange | Input damage/false reading 가능 | Two-part top resistance, series/protection, current-limited test |
| USB/GPIO backfeed | K1 open인데 residual rail 가능 | `T-PWR-003`, `T-ESTOP-005/006`; 필요 시 회로 변경 |

## Requirement/design/test traceability

| Design decision | Requirements | Primary tests |
| --- | --- | --- |
| `CD-ESTOP-001` K1 high-side cut | `003~004`, `012~013`, `015`, `017` | `T-ESTOP-001`, `005~006` |
| `CD-ESTOP-002` three-wire re-enable | `001~002`, `007~008`, `011`, `018` | `T-ESTOP-001~002`, `004~005` |
| `CD-ESTOP-003` coil clamp | `004`, `009`, `016` | `T-ESTOP-001`, `006` |
| `CD-ESTOP-004` S0-B sense | `002`, `005~010`, `018` | `T-ESTOP-002~005` |
| `CD-ESTOP-005` dual rail sense | `012~015` SHOULD/POST-MVP | `T-ESTOP-006` |
| `CD-ESTOP-006` connector/test point | `004`, `018~020` | `T-ESTOP-001~003`, `006` |
| `CD-ESTOP-007` backfeed boundary | `003`, `013~017` | `T-ESTOP-005~006`, `T-PWR-003` |

## Step 7로 넘기는 component/rating 결정

| Open item | Required basis before closure |
| --- | --- |
| K1 relay and contact arrangement | Main NO motor-power 기능, 3S LiPo DC make/break, `I_MOTOR_WORST`, inductive load, temperature, life data |
| K1 coil voltage/current | 3S operating envelope에서 pickup/hold/dropout, S0/S2 contact current와 F2 coordination |
| K2 control relay | 2 independent NO functions, minimum switching load, 3S low-voltage pickup와 K1 coil switching |
| S0 actuator/contact blocks | Red latching actuator, independent NC blocks, direct-opening/terminal/contact ratings from official datasheet |
| S2 | Momentary NO, coil make current와 DC rating |
| F1/F2 | Motor/current envelope, wire/terminal ampacity, fuse time-current curve와 fault energy |
| `X1_K1_CLAMP`, `X2_K2_CLAMP` | Coil energy, switching stress, `T_K1_OPEN_MAX`와 rail decay |
| ADC networks | 12.6 V plus declared transient margin, MCU input/ADC limits, source impedance, filter settling, fault current |
| `R_RAIL_BLEED` | Natural rail decay measurement, resistance/power/thermal calculation |
| Connectors/wire/terminals | Continuous/fault current, DC voltage, temperature, keying, strain relief and accessible touch protection |

MG540P30_12V 공식 전류 자료가 없으므로 K1/F1/main wire의 최종 정격을 이 단계에서
추정 확정하지 않는다.

## Step 6 gate

```text
K1 main-feed topology: BASELINED
Three-wire manual re-enable topology: BASELINED
Independent 5 V/opto S0-B sense topology: BASELINED
Upstream/downstream rail diagnostic topology: BASELINED / POST-MVP OPTION
Target pin candidates: PC7 MVP; PA4 / PB0 POST-MVP, NOT CONFIGURED OR TESTED
Connector/test-point partition: BASELINED
S0/S2/K2/opto part candidates: SELECTED IN STEP 7, CONDITIONAL
K1/F1/main-current parts and exact values: TBD/TBR / MOTOR DATA BLOCKED
RevB pull-down checkpoint schematic/ERC: PASS
Physical E-stop schematic/ERC: NOT STARTED
Firmware implementation: NOT STARTED
Hardware verification: NOT TESTED
Residual-risk acceptance: NOT PERFORMED
```

Step 6 완료는 요구사항을 회로 기능과 net 수준으로 변환했다는 뜻이다. Relay가 실제 motor
current를 안전하게 끊거나 no-auto-restart가 검증됐다는 뜻은 아니다. MVP는 Step 7의
K1/F1/control/sense 정격 선정과 Step 8 회로도/ERC 뒤에만 motor-disconnected test로 이동한다.
PA4/PB0 network 미구현은 그 이동을 막지 않지만 direct rail test point 미구현은 막는다.

Step 7의 official minimum-load review로 K1-AUX seal-in을 K2 2-contact control relay로,
S0-B direct 3.3 V contact input을 5 V optocoupler conditioner로 보정했다. 상세 부품 판정은
[`26_Physical_EStop_Component_and_Rating_Selection_ko.md`](26_Physical_EStop_Component_and_Rating_Selection_ko.md)를 따른다.

## 2026-08-13 Step 8 implementation update

위 `Step 6 gate` 표는 Step 6 종료 시점의 역사 상태를 보존한다. 이후 Step 8에서 Physical
E-stop 기능 회로를 RevB-WIP KiCad에 반영했다.

```text
K2 split hold/K1-enable contacts: IMPLEMENTED IN FUNCTIONAL SCHEMATIC
S0-A/S0-B and S2 connector boundaries: IMPLEMENTED
VO617A-3 candidate sense path and R13/R14: IMPLEMENTED
Direct rail/control/sense test points: IMPLEMENTED
K1/F1/main-current exact parts and values: STILL TBD / MOTOR DATA BLOCKED
ERC: 0 errors / 0 warnings
Ref/Pin/Net tuples: 120 preserved
Hardware/perfboard implementation: NOT TESTED / NO SOLDER RELEASE
```

현재 A4 배치는 전기적 WIP 검토본으로 승인했고 포트폴리오 수준의 기능 흐름 재배치는
학습 후 별도 수행한다. 이는 actual part/rating, continuity, board power/back-power 또는
`T-ESTOP-001~005` 통과를 뜻하지 않는다.
