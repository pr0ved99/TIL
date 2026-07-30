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
    -> motor energy disconnect path

NC contact B
    -> 3.3 V STM32 sense loop
```

Sense contact에 motor current를 흘리지 않는다. Motor-current contact와 logic contact의 정격·배선·connector를 섞지 않는다.

### 3. 직접 차단과 contactor 방식은 부품 선정 전까지 variant로 유지한다

#### Variant A: DC-rated latching E-stop이 motor current를 직접 차단

```text
LiPo+ -> fuse -> E-stop NC power contact -> main switch/distribution -> MDD10A
```

다음 조건이 모두 확인된 경우에만 허용한다.

- Contact의 DC voltage/current breaking rating이 실제 보호회로 조건보다 충분하다.
- Inrush, stall current와 반복 개폐 조건을 만족한다.
- 제조사가 inductive DC load 차단 용도를 허용한다.
- Wiring, terminal, connector와 fuse가 같은 current class를 만족한다.

AC rating만 표시된 저가 switch를 3S motor path에 바로 사용하지 않는다.

#### Variant B: E-stop NC loop가 DC-rated contactor 또는 검증된 solid-state disconnect를 제어

```text
E-stop NC control loop -> power disconnect control
LiPo+ -> fuse -> DC power disconnect -> motor-power rail -> MDD10A
```

Motor current가 operator switch의 소형 contact를 직접 통과하지 않아도 되는 방식이다. 최종 주행 단계의 preferred architecture이지만, contactor coil power, flyback suppression, default-off behavior, current/voltage rating과 failure mode를 먼저 검증해야 한다.

어느 variant도 부품 정격과 실제 측정 없이 `PASS`로 확정하지 않는다.

### 4. E-stop은 motor rail을 우선 차단한다

목표 topology는 다음과 같다.

```text
3S LiPo+
  -> fuse
  -> Physical E-stop disconnect
  -> MOTOR_VBAT_SAFE
       -> MDD10A POWER+

3S LiPo+
  -> protected logic-power branch
       -> STM32 / ESP32 / encoder supply
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
5. Operator가 별도의 explicit reset을 수행한다.
6. 이후 새로운 ARM request를 수행한다.

다음 동작은 금지한다.

- E-stop release 즉시 자동 ARM
- 이전 command 자동 재적용
- Remote command만으로 physical latch 해제
- Boot 중 E-stop 상태를 무시하고 output 활성화

## STM32 sense contract

최종 GPIO는 pin allocation 검토 후 정한다. 임의 pin을 지금 확정하지 않는다.

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
| Contacts | 최소 2개 독립 NC 또는 power NC + auxiliary NC |
| DC rating | Voltage, continuous current, breaking current, load category |
| Interrupt method | Direct contact / contactor / solid-state disconnect |
| Default state | Control power loss·wire break에서 motor rail off |
| Terminal | Wire gauge, ferrule/ring terminal, touch protection |
| Mounting | Operator가 즉시 접근 가능하고 accidental press/release 위험이 낮은 위치 |
| Fuse relation | Fuse rating이 switch/disconnect와 wire rating을 보호하는지 |
| Regeneration | Power cut 시 bus voltage/back-EMF 처리 근거 |
| Auxiliary sense | 3.3 V fail-safe sense가 motor current와 분리되는지 |

`Emergency stop`, `12 V`, `10 A`라는 판매 제목만으로 선정하지 않는다. 반드시 datasheet의 DC switching/breaking rating을 확인한다.

## 구현 순서

1. Motor stall/current envelope와 현재 10 A fuse 목적을 다시 확인한다.
2. Direct-contact 또는 contactor variant를 선택한다.
3. E-stop과 disconnect 부품의 공식 datasheet를 저장한다.
4. RevA schematic에 `TBD` variant로 반영하고 ERC를 실행한다.
5. Motor-disconnected continuity/DMM 시험을 수행한다.
6. STM32 sense pin과 software latch/reset을 구현한다.
7. Logic analyzer로 sense-to-PWM-zero latency를 측정한다.
8. Driver powered/no-motor 상태에서 rail cut와 no-auto-restart를 확인한다.
9. Lifted single-motor low-duty 상태에서 mechanical stop을 확인한다.
10. 모든 evidence가 연결된 뒤에만 final wiring release에 반영한다.

상세 수용 기준과 시험 절차는 [`../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)를 정본으로 사용한다.

## 현재 판정

```text
Architecture contract: DRAFTED
Hardware selection: TBD
Schematic implementation: NOT STARTED
Firmware sense/latch implementation: NOT STARTED
Motor-disconnected verification: NOT TESTED
Motor-connected stop verification: NOT TESTED
Overall Physical E-stop: PLANNED
```

