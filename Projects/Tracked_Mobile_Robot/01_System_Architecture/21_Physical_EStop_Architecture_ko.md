# Physical E-stop Architecture

## 목적

이 문서는 첫 실제 모터 구동 전에 필요한 Physical E-stop의 설계 경계를 정의한다.

이 프로젝트에서 Physical E-stop은 STM32 명령 하나가 아니다. 다음 두 경로가 서로 독립적으로 같은 안전 상태를 만든다.

```text
Physical stop path
    -> motor energy path를 hardware로 차단

Monitoring path
    -> STM32가 E-stop 상태를 감지
    -> software stop latch
    -> PWM zero, re-arm 금지, telemetry 기록
```

STM32가 정상 동작하지 않더라도 physical stop path가 motor energy를 제거해야 한다. 반대로 hardware contact가 복구돼도 STM32는 명시적인 reset 절차 전까지 motion을 다시 허용하지 않는다.

이 문서는 산업 안전 인증이나 정식 safety category를 주장하지 않는다. 개인 로봇 MVP에서 single MCU/software stop만 Physical E-stop으로 잘못 간주하지 않기 위한 설계 baseline이다.

## MVP 범위와 후속 확장 경계

Physical E-stop을 첫 모터 시험의 필수 안전 gate로 유지하되, 개인 프로젝트 MVP에서 입증할
범위는 다음으로 제한한다.

- K1이 MCU·통신과 독립적으로 motor positive feed를 차단한다.
- S0-B/PC7 감지 시 PWM zero와 persistent latch가 걸린다.
- Button release와 power restoration만으로 K1 또는 motion이 자동 복구되지 않는다.
- Motor-disconnected direct continuity/DMM 측정으로 K1 downstream rail 차단을 확인한다.
- 첫 lifted motor setup에서 실제 정지와 no-auto-restart를 기록한다.

다음은 설계 확장 후보로 보존하지만 MVP blocker로 사용하지 않는다.

- PA4/PB0 upstream/downstream ADC의 continuous plausibility 진단
- `K1_OFF_DISCREPANCY`, `RAIL_SENSE_FAULT`와 welded-contact 자동 검출
- S0/PWM/K1/rail의 정밀 동기 timing 및 transient 분포 시험
- Force-guided contact, safety relay, 이중화 진단과 ISO 13849 PL/IEC 62061 SIL 주장

따라서 MVP의 `hardware cut PASS`는 매 시험 전 direct measurement를 포함하는 제한된 bench
claim이다. 연속적인 welded-contact 자동 진단이나 산업용 single-fault tolerance를 뜻하지 않는다.

## 안전 목표와 안전 상태

2026-08-10 이후 이 절은 `RISK-001`, `ESTOP-001`, `REQ-001`, `VVT-001`을
`ADOPTED FORWARD BASIS`로 사용한다. Basis ID와 주장 경계는
[`../docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md`](../docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md)를 정본으로 한다.

### `SG-ESTOP-001` Physical E-stop safety goal

```text
E-stop actuator가 눌리거나 physical stop loop의 건전성이 상실되면
MCU, firmware와 communication 상태에 의존하지 않고 motor energy path를 차단한다.

동작 가능한 controller는 동시에 모든 motion-authorizing output을 zero로 만들고
E-stop latch를 설정한다.

Physical release는 contact health만 복구하며 motion authority를 복구하지 않는다.
재가동에는 healthy contact, explicit reset, new ARM과 post-reset new command가 필요하다.
```

이 safety goal은 `모터가 즉시 정지한다`고 주장하지 않는다. Electrical isolation,
motor-rail decay와 실제 track의 mechanical stop은 서로 다른 측정 대상이다.

### Safe-state vector

| 영역 | E-stop asserted/open에서 요구되는 상태 | Controller가 동작하지 않을 때의 경계 |
| --- | --- | --- |
| Motor energy path | Physical disconnect open/de-energized; MDD10A `POWER+` 공급 경로 개방 | 반드시 hardware path가 단독으로 만족해야 함; `POWER-`/common GND 유지 상태를 완전한 galvanic isolation으로 표현하지 않음 |
| PWM output | 두 PWM request와 실제 PWM pin inactive/zero | MCU failure 때문에 software zero를 보장할 수 없어도 physical path가 motion energy를 차단해야 함 |
| DIR output | Motion authority 없음; PWM zero와 motor rail isolation이 우선 | DIR level만으로 safe state를 주장하지 않음 |
| Controller safety state | `ESTOP_LATCHED`; externally visible operating state는 `DISARMED` 또는 동등한 non-motion state | 다음 boot에서 open contact를 감지해 ARM/CMD를 거부해야 함 |
| Stored command | Zero 처리하고 자동 replay 금지 | 다음 boot 또는 recovery에서 이전 command를 재사용하지 않음 |
| ARM/CMD | E-stop asserted 또는 latched 동안 reject | Hardware contact가 복구돼도 controller가 유효한 reset을 처리하기 전까지 motion 금지 |
| Physical release | Contact health를 `healthy`로 변경해도 K1 motor rail off, software latch와 output zero 유지 | Release만으로 motor energy 또는 motion authority가 복구되면 안 됨; 별도 hardware re-enable 회로는 Step 6에서 구현 |
| Explicit reset | Contact가 open이면 reject; healthy일 때 latch만 clear하고 `DISARMED` 유지 | Reset은 ARM이 아니며 output을 활성화하지 않음 |
| Re-enable | Healthy contact + explicit reset + new ARM + post-reset new command | 이전 command, pre-E-stop ARM 또는 release edge를 재사용하지 않음 |
| Observability | asserted, latched, release-detected, reset-rejected 상태를 log/telemetry에서 구분 | Log는 monitoring evidence이며 physical isolation evidence를 대체하지 않음 |

### Safety invariants

1. Physical stop path는 STM32, ESP32, UART와 software safe-output path에 의존하지 않는다.
2. Physical release와 software reset은 서로 다른 사건이다.
3. Valid reset은 latch만 clear하고 controller를 `DISARMED`에 둔다. Reset은 ARM이 아니다.
4. Telemetry의 `ESTOP` 표시는 power contact가 실제 open이라는 전기적 증거를 대체하지 않는다.
5. PWM zero와 motor rail isolation은 각각 계측한다.
6. Electrical shutdown과 mechanical stop time/distance는 각각 계측한다.

### Step 1 definition gate

```text
Safety goal: BASELINED
Safe-state vector: BASELINED
Restart policy: BASELINED
Component-specific threshold: TBD
Motor-rail re-energization policy after release: SEPARATE MANUAL HARDWARE RE-ENABLE REQUIRED (Step 3)
Re-enable circuit implementation: TBD (Step 6)
Hardware implementation: NOT STARTED
Hardware/runtime verification: NOT TESTED
```

이 gate의 완료는 문서 정의가 일관됐다는 뜻이다. Physical E-stop 기능이 구현 또는
검증됐다는 뜻이 아니다.

## Step 2 시스템 경계와 경로 정의

이 절은 `SG-ESTOP-001`을 실제 전기·제어 인터페이스로 분해한다. ISO 13850과
IEC 60204-1은 emergency-stop 기능과 전기적 구현을 검토하기 위한
`standards-informed` 참고 근거로만 사용한다. 이 프로젝트가 해당 표준에 적합하거나
인증됐다는 뜻은 아니다.

### 시스템 경계

| 구분 | 경계 안 | 경계 밖 또는 별도 검증 |
| --- | --- | --- |
| Energy source interface | XT60 이후 fuse, main switch, motor/logic 분기 | LiPo cell 내부 보호 설계, charger와 배터리 제조 품질 |
| Motor-energy path | `F1 -> S1 -> K1 main contact -> MDD10A POWER+ -> motor` | 별도 mechanical brake, 양극 동시 차단, 산업용 safe-torque-off |
| E-stop control path | Mechanical-latching actuator `S0-A NC`, K1 coil permission과 보호회로 | Remote/wireless E-stop, 최종 reset/interlock 회로 상세 |
| Monitoring path | `S0-B NC -> ESTOP_SENSE -> STM32 latch/telemetry` | Monitoring만으로 K1 main contact가 실제 open이라고 주장하는 것 |
| Logic-power interaction | XL4015, STM32, ESP32, encoder와 MDD10A logic input | USB host 자체의 안전성; 단, USB 역급전은 integration 시험 범위에 포함 |
| Verification object | Rail continuity/voltage, sense voltage, PWM, state, stop time | ISO 13849 PL, IEC 62061/61508 SIL, 제품 인증과 법적 적합성 |

배터리 pack은 energy source로 사용하지만 이번 E-stop 회로 설계의 내부 대상은 XT60 이후다.
반대로 USB 전원은 경계 밖의 source여도 motor rail로 역급전될 수 있으므로 integration
verification 대상에는 포함한다.

### RevA 현재 경로와 RevB 목표 경로

RevA 정본 KiCad source에서 확인한 현재 net path는 다음과 같다.

```text
VBAT_RAW -> FUSE_TBD -> VBAT_FUSED -> MAIN_DC_SWITCH -> VBAT_SW
                                                        +-> MDD10A POWER+
                                                        +-> XL4015 #1 IN+
                                                        +-> XL4015 #2 IN+
```

현재는 motor와 logic load가 `VBAT_SW` 하나에서 함께 분기되므로 E-stop이 motor rail만
독립적으로 차단할 수 없다.

RevB 목표 interface path는 다음과 같이 baseline으로 고정한다.

```text
3S LiPo pack (source boundary)
  BATT+
    -> XT60
    -> F1 main fuse
    -> S1 MAIN_DC_SWITCH
    -> VBAT_PROTECTED
         +-> K1 DC power relay main contact
         |     (coil de-energized = open)
         |      -> MOTOR_VBAT_SAFE
         |           -> MDD10A POWER+
         |                -> left/right motor
         |
         +-> protected logic branch
               -> XL4015 #1 / #2
                    -> STM32 / ESP32 / encoder rails

  BATT-
    -> PWR_GND
         +-> MDD10A POWER-
         +-> XL4015 IN-
         +-> controlled logic common GND
```

`K1`은 relay 방식이라는 architecture selection을 뜻하는 기능 이름이다. 실제 part number,
contact rating, coil voltage/current와 package는 아직 선정하지 않는다. Relay가
de-energized일 때 main contact가 open되는 방향을 사용해 control power loss가 motor-energy
cut 방향으로 작용하게 한다.

이 구조는 battery positive high-side 한 선을 여는 구조다. `MOTOR_VBAT_SAFE`의
`POWER+` 공급은 끊기지만 MDD10A `POWER-`와 logic common GND는 남는다. 따라서
`galvanic isolation`이나 `motor terminal energy가 즉시 0 V`라고 주장하지 않는다.

### Relay control path

```text
VBAT_PROTECTED
  -> K1 coil supply/protection            (voltage/flyback TBD)
  -> manual re-enable/reset interlock     (Step 6 three-wire circuit baselined)
  -> S0-A E-stop NC control contact
  -> K1 coil
  -> PWR_GND
```

필수 동작 방향:

- `S0-A` press, control-wire open 또는 coil-power loss는 K1 de-energize 방향이어야 한다.
- STM32, ESP32, UART와 application firmware는 K1 coil 유지의 필수 조건이 아니어야 한다.
- Button release만으로 K1 motor rail을 재인가하지 않는다. 별도 manual hardware re-enable이
  필요하며 정확한 reset/self-hold/interlock 회로는 Step 6에서 확정한다.
- Coil flyback suppression은 contact open 시간을 불필요하게 늘릴 수 있으므로 부품 선택과
  shutdown timing을 함께 검증한다.

### Independent sense path

```text
STM32 3V3
  -> external pull-up
  -> ESTOP_SENSE
  -> S0-B E-stop NC auxiliary contact
  -> GND

healthy/closed = LOW
asserted, wire-open or connector-open = HIGH
```

`S0-B`는 K1 coil current나 motor current를 운반하지 않는다. 이 path는 actuator와 sense
harness의 상태를 알려 주지만, K1 main contact 용착 또는 실제 `MOTOR_VBAT_SAFE` 전압을
직접 증명하지 않는다. Step 3은 actual-off 확인 필요성을 도출했고, Step 4 FMEA는
downstream voltage sensing과 direct bench rail measurement를 선택했다. 일반 K1 auxiliary
contact는 main contact open의 단독 증거로 사용하지 않는다.

### Interface contract

| ID | Interface/net | Owner | Normal operation | E-stop asserted/open | Evidence |
| --- | --- | --- | --- | --- | --- |
| `PWR-ESTOP-01` | `VBAT_PROTECTED` | Fuse/main switch distribution | Battery source available | Logic branch 유지 가능 | Schematic review, DMM |
| `PWR-ESTOP-02` | `MOTOR_VBAT_SAFE` | K1 main contact | Rated motor source available | `POWER+` source feed open/decaying | Continuity, rail waveform |
| `CTL-ESTOP-01` | `S0-A`/K1 coil loop | Physical E-stop circuit | Coil permission may be present | Coil permission removed | Continuity, coil voltage |
| `SNS-ESTOP-01` | `ESTOP_SENSE` | STM32 input | Stable LOW | HIGH/fault | DMM, logic capture |
| `CTL-MOTOR-01` | PWM1/2, DIR1/2 | STM32 | Safety-gated command | PWM inactive/zero | Logic capture |
| `OBS-ESTOP-01` | UART telemetry/log | STM32/ESP32 | Healthy state visible | asserted/latch/reset-reject 구분 | Raw UART log |

Logic rail을 유지한 상태에서는 다음을 별도 확인한다.

1. USB, XL4015 또는 GPIO/PWM/DIR을 통해 `MOTOR_VBAT_SAFE`가 유의미하게 역급전되지 않는다.
2. MDD10A motor supply가 제거된 상태에서 logic input이 high여도 motor output이 재활성화되지 않는다.
3. MDD10A, motor와 wiring에 남는 regenerative/back-EMF energy를 rail-decay 파형으로 확인한다.
4. Logic power 유지가 telemetry evidence에는 도움이 되지만 physical contact-open evidence를 대체하지 않는다.

### Step 2 definition gate

```text
RevA actual net path: CONFIRMED FROM KICAD SOURCE
System boundary: BASELINED
RevB motor-energy path: BASELINED
Independent sense path: BASELINED
Disconnect method: K1 DC POWER RELAY SELECTED
Exact K1/S0 part and ratings: TBD
Coil voltage/driver/flyback and re-enable circuit implementation: TBD (Step 6)
K1 actual-off diagnostic method: DOWNSTREAM MOTOR RAIL SENSE + DIRECT BENCH MEASUREMENT (Step 4)
STM32 GPIO and schematic implementation: NOT STARTED
Hardware/runtime verification: NOT TESTED
```

Step 2 완료는 어떤 path를 설계하고 검증할지 고정했다는 뜻이다. Relay 정격 적합성,
회로 구현 또는 실제 motor-energy 차단을 통과했다는 뜻이 아니다.

Step 3 hazard analysis 정본은
[`22_Physical_EStop_Hazard_Analysis_ko.md`](22_Physical_EStop_Hazard_Analysis_ko.md)다.
이 분석으로 mechanical release와 별도인 manual K1 hardware re-enable 필요성을
design input으로 고정했다.

Step 4 FMEA 정본은 [`23_Physical_EStop_FMEA_ko.md`](23_Physical_EStop_FMEA_ko.md)다.
FMEA 결과 manual re-enable은 three-wire control을 RevB target으로 선택했고, Step 7
minimum-load review에서 S2 momentary NO와 K2 2-contact relay를 사용하는 구조로 구체화했다.
K1 actual-off는 일반 auxiliary contact만 믿지 않고
`MOTOR_VBAT_SAFE` downstream rail sensing과 direct bench measurement로 확인한다.

Step 5 requirement 정본은
[`24_Physical_EStop_Safety_Requirements_ko.md`](24_Physical_EStop_Safety_Requirements_ko.md)다.
Hazard/FMEA action을 20개 `REQ-ESTOP-*`와 7개 TBR register item으로 변환했다.

## 현재 하드웨어 경계

현재 전원 baseline은 다음과 같다.

```text
3S LiPo+
  -> 10 A bench fuse
  -> MAIN_DC_SWITCH
  -> VBAT_SW
       +-> MDD10A POWER+
       +-> XL4015 #1 IN+
       +-> XL4015 #2 IN+

3S LiPo-
  -> common power GND
```

MDD10A는 channel별 `PWM + DIR` 입력을 사용하며 별도 enable 입력이 없다. 따라서 `PWM=0`은 정상 software stop 수단이지만 MCU hang, pin fault, firmware defect와 독립적인 physical isolation 수단은 아니다.

Cytron의 MDD10A 공식 제품 자료는 다음 경계를 명시한다.

- Motor supply: 5~30 VDC
- Channel당 최대 10 A continuous, 30 A peak
- 3.3 V/5 V PWM·DIR logic 입력
- PWM frequency 최대 20 kHz
- Vmotor reverse-polarity protection 없음
- Regenerative braking 지원

Reference: <https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels>

위 수치는 E-stop contact나 contactor의 정격을 자동으로 결정하지 않는다. 실제 motor stall current, 배선, fuse, interrupt device의 DC rating과 regenerative-energy behavior를 별도로 검증해야 한다.

## 설계 결정

### 1. Physical E-stop은 normally-closed loop를 사용한다

정상 상태에서 contact가 닫혀 있고, 버튼을 누르거나 배선이 끊기면 loop가 열린다.

```text
healthy loop closed  -> operation may be permitted
button pressed       -> motor energy off
wire disconnected    -> motor energy off
connector removed    -> motor energy off
```

Normally-open contact만 사용하면 단선이 정상 상태처럼 보일 수 있으므로 채택하지 않는다.

### 2. Motor energy cut와 MCU sense는 분리한다

최종 switch assembly는 독립 contact 두 개 또는 동등한 기능을 가져야 한다.

```text
NC contact A
    -> K1 relay coil permission / motor-energy disconnect control path

NC contact B
    -> 3.3 V STM32 sense loop
```

두 actuator contact 모두 motor current를 직접 운반하지 않는다. Motor current는 K1 main
contact로만 흘리고, K1 main contact, S0 control contact와 logic sense contact의
정격·배선·connector를 섞지 않는다.

### 3. 첫 RevB disconnect 방식은 DC power relay로 한다

E-stop actuator의 소형 contact에 motor current를 직접 흘리지 않는다. `S0-A NC`는 K1 coil
permission path를 열고, K1 main contact가 motor current를 차단한다.

```text
S0-A NC control loop -> K1 coil permission
LiPo+ -> fuse -> main switch -> K1 main contact -> MOTOR_VBAT_SAFE -> MDD10A
```

Direct-contact와 solid-state disconnect는 첫 RevB active baseline에서 제외한다. 단, motor
current envelope를 확보한 뒤 일반 power relay가 DC breaking, continuous/starting/stall current,
inrush와 반복 개폐 조건을 만족하지 못하면 contactor급 부품으로 재선정한다. 이 경우에도
`K1 relay-controlled disconnect`라는 interface contract는 유지하고 변경 근거를 ADR로 기록한다.

AC rating만 표시된 relay/switch를 DC motor-energy 차단 근거로 사용하지 않는다. 부품 정격과
실제 측정 없이 `PASS`로 확정하지 않는다.

### 4. E-stop은 motor rail을 우선 차단한다

목표 topology는 다음과 같다. 상세 net boundary는 위 Step 2 절을 정본으로 한다.

```text
3S LiPo+
  -> fuse
  -> main switch
  -> VBAT_PROTECTED
       +-> K1 relay main contact -> MOTOR_VBAT_SAFE -> MDD10A POWER+
       +-> protected logic-power branch -> STM32 / ESP32 / encoder supply
```

가능하면 MCU와 telemetry는 살아 있어야 E-stop 원인과 상태를 기록할 수 있다. 현재 RevA는 `VBAT_SW`에서 MDD10A와 두 XL4015가 함께 분기되므로, 이 topology는 아직 구현된 회로가 아니라 다음 electrical revision 후보다.

Logic rail을 살려 두는 방식이 back-power 또는 unexpected motor-power path를 만들면 안 된다. USB, XL4015, STM32, ESP32, MDD10A common GND와 역급전 검증을 먼저 통과해야 한다.

### 5. Mechanical release와 software reset은 별개다

E-stop 버튼은 기계적으로 latch되어야 한다. 버튼을 twist/pull하여 물리 contact를 복구하는 행위만으로 motor output이 재개되면 안 된다.

재가동 조건:

1. Physical E-stop이 released 상태다.
2. Sense loop가 healthy 상태로 안정적으로 유지된다.
3. Controller는 `DISARMED`다.
4. Active motion command와 PWM request가 zero다.
5. Operator가 mechanical release와 별도의 manual K1 hardware re-enable을 수행한다.
6. Operator가 software latch를 위한 explicit reset을 수행한다.
7. 이후 새로운 ARM request와 post-reset new command를 수행한다.

Step 6/7은 hardware re-enable을 `S0-A NC -> [S2 NO OR K2-HOLD-NO] -> K2 coil`,
`K2-K1-ENABLE-NO -> K1 coil`의 3선식 회로로 확정했다. K1 power contact를 저전류
self-hold에 겸용하지 않는다. Hardware re-enable과 software reset은 순서와 무관하게 각각 별도
operator action이며, 어느 하나만으로 motion을 복구하지 않는다. 상세 회로 정본은
[`25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](25_Physical_EStop_RevB_Circuit_Architecture_ko.md),
부품 정격 정본은
[`26_Physical_EStop_Component_and_Rating_Selection_ko.md`](26_Physical_EStop_Component_and_Rating_Selection_ko.md)다.

다음 동작은 금지한다.

- E-stop release 즉시 자동 ARM
- E-stop release만으로 K1 motor rail 자동 재인가
- 이전 command 자동 재적용
- Remote command만으로 physical latch 해제
- Boot 중 E-stop 상태를 무시하고 output 활성화

## STM32 sense contract

Step 6 pin-conflict review 결과 `PC7`을 `ESTOP_SENSE` GPIO/EXTI 후보로 선정했다. PC7은
NUCLEO-F446RE Arduino D9에서 접근 가능하고 현재 `.ioc`의 motor/UART/encoder 핀과 충돌하지
않는다. 아직 CubeMX 구성, input threshold 계산과 전압 시험을 하지 않았으므로 최종
firmware pin이 아니라 `CANDIDATE`다.

권장 electrical sense:

```text
STM32 3V3
  -> external pull-up
  -> ESTOP_SENSE input
  -> NC auxiliary contact
  -> GND

healthy/closed = LOW
pressed/open   = HIGH
wire break     = HIGH
```

요구사항:

- 5 V를 STM32 GPIO에 직접 입력하지 않는다.
- External pull-up 또는 동등한 fail-safe bias를 사용한다.
- Boot 직후 input이 open이면 ARM을 금지한다.
- Assertion은 release debounce보다 우선한다.
- Release bounce로 latch가 자동 clear되면 안 된다.
- Sense wire를 motor/PWM high-current wiring과 분리해 routing한다.
- Long harness가 확정되면 RC filter, Schmitt input, transient protection 필요성을 파형으로 판단한다.

초기 firmware 처리 후보:

```text
asserted/open sample
    -> immediately request Motor_Output_ForceSafe()
    -> set ESTOP latch
    -> reject ARM/CMD

released/closed samples
    -> only mark physical contact healthy
    -> latch remains set

explicit reset while safe
    -> clear software latch
    -> remain DISARMED
```

EXTI는 빠른 감지에 도움이 되지만 sole safety mechanism이 아니다. Fast polling과 EXTI 어느 쪽을 쓰더라도 hardware power cut가 독립적으로 존재해야 한다.

## Software state contract

기존 `SAFETY_ESTOP_LATCHED` 설계를 다음 규칙으로 구체화한다.

| Condition | Required behavior |
| --- | --- |
| Boot with E-stop open | `DISARMED` 또는 `ESTOP_LATCHED`, ARM reject, PWM zero |
| E-stop opens while disarmed | Latch set, PWM zero 유지 |
| E-stop opens while armed | 즉시 common safe-output 함수 호출, latch set |
| E-stop sense wire breaks | Pressed와 동일하게 처리 |
| E-stop contact closes again | Latch 유지, 자동 motion 금지 |
| Reset request while contact open | Reject |
| Valid reset after release | Latch clear, state remains `DISARMED` |
| MCU reset while E-stop open | Physical motor rail off, firmware ARM reject |
| UART/ESP32 disconnect | Physical E-stop behavior에 영향 없음 |

E-stop, software fault, timeout과 DISARM은 모두 최종 motor output owner의 공통 safe-output path로 수렴해야 한다. 단, Physical E-stop의 motor-energy cut는 이 software path와 독립적이다.

## Stop behavior와 energy 주의사항

Physical power cut 뒤 motor가 즉시 zero speed가 된다고 가정하지 않는다.

- Track/motor inertia로 coast할 수 있다.
- Driver regenerative braking 동작과 power removal 시점이 상호작용할 수 있다.
- Driver input을 끊는 것과 motor terminal을 short-brake하는 것은 같은 동작이 아니다.
- Back-EMF, bus overshoot, MDD10A 상태와 실제 stopping distance를 계측해야 한다.

따라서 최종 수용 기준에는 `electrical shutdown latency`와 `mechanical stop time/distance`를 분리해 기록한다.

## 부품 선정 체크리스트

구매 전 다음 항목을 모두 채운다.

| Item | Required record |
| --- | --- |
| Switch type | Red mushroom, mechanical latch, twist/pull release |
| E-stop actuator contacts | 최소 2개 독립 NC: `S0-A` relay control + `S0-B` auxiliary sense |
| K1 main contact | Coil de-energized에서 open, 실제 DC motor current/breaking 조건에 적합 |
| DC rating | Voltage, continuous current, breaking current, load category |
| Interrupt method | `S0-A`가 K1 DC power relay를 de-energize하는 방식 |
| K1 actual-off diagnostic | `MOTOR_VBAT_SAFE` downstream sense + direct bench measurement; 일반 auxiliary contact 단독 proof 금지 |
| Default state | Control power loss·wire break에서 motor rail off |
| Terminal | Wire gauge, ferrule/ring terminal, touch protection |
| Mounting | Operator가 즉시 접근 가능하고 accidental press/release 위험이 낮은 위치 |
| Fuse relation | Fuse rating이 switch/disconnect와 wire rating을 보호하는지 |
| Regeneration | Power cut 시 bus voltage/back-EMF 처리 근거 |
| Auxiliary sense | 5 V contact-wetting loop와 optocoupler 3.3 V input이 motor current와 분리되는지 |

`Emergency stop`, `12 V`, `10 A`라는 판매 제목만으로 선정하지 않는다. 반드시 datasheet의 DC switching/breaking rating을 확인한다.

## 구현 순서

1. Motor stall/current envelope와 현재 10 A fuse 목적을 다시 확인한다.
2. `[완료]` Three-wire manual re-enable, downstream rail-sense와 coil protection 기능 구조를
   [`25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](25_Physical_EStop_RevB_Circuit_Architecture_ko.md)로 확정한다.
3. E-stop과 disconnect 부품의 공식 datasheet를 저장한다.
4. RevB schematic에 K1/S0 target path와 아직 선정되지 않은 part를 `TBD`로 반영하고 ERC를 실행한다.
5. Motor-disconnected continuity/DMM 시험을 수행한다.
6. STM32 sense pin과 software latch/reset을 구현한다.
7. Logic analyzer로 sense-to-PWM-zero latency를 측정한다.
8. Driver powered/no-motor 상태에서 rail cut와 no-auto-restart를 확인한다.
9. Lifted single-motor low-duty 상태에서 mechanical stop을 확인한다.
10. 모든 evidence가 연결된 뒤에만 final wiring release에 반영한다.

상세 수용 기준과 시험 절차는 [`../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)를 정본으로 사용한다.

## 현재 판정

```text
Safety goal/safe-state definition: BASELINED (2026-08-10)
System boundary/energy/sense paths: BASELINED (2026-08-10)
Hazard analysis: BASELINED (2026-08-10)
FMEA: BASELINED (2026-08-10)
Safety requirements: 20 BASELINED / 7 TBR REGISTER ITEMS OPEN (2026-08-10)
Disconnect method: K1 DC POWER RELAY SELECTED
Motor-rail re-enable policy: SEPARATE MANUAL HARDWARE ACTION REQUIRED
Re-enable target: THREE-WIRE S2 + K2 TWO-CONTACT CONTROL
MVP actual-off evidence: DIRECT DOWNSTREAM CONTINUITY/VOLTAGE MEASUREMENT REQUIRED
Post-MVP diagnostic: PA4/PB0 DUAL-RAIL SENSE SELECTED, DEFERRED
RevB functional circuit architecture: BASELINED (2026-08-10)
Target pin candidates: PC7 MVP; PA4 / PB0 POST-MVP, NOT CONFIGURED OR TESTED
S0/S2/K2/opto selection: PREFERRED CANDIDATES / CONDITIONAL
K1/F1/main-current selection: BLOCKED BY MOTOR CURRENT DATA
Schematic implementation: NOT STARTED
Firmware sense/latch implementation: NOT STARTED
Motor-disconnected verification: NOT TESTED
Motor-connected stop verification: NOT TESTED
Overall Physical E-stop: PLANNED
```
