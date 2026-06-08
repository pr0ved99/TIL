# 전원 분배와 안전 아키텍처

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트의 첫 power distribution과 safety architecture를 정의한다.

프로젝트의 안전 결정을 실제 전원 계획으로 확장한다.

- 3S LiPo battery를 main energy source로 사용한다.
- Main fuse와 DC-rated switch를 battery 가까이에 둔다.
- Motor power와 logic power를 별도의 power domain으로 취급한다.
- XL4015/XL4016 buck converter는 MCU를 연결하기 전에 조정하고 측정한다.
- Voltage sensing 구현 이후 저전압 판단은 STM32가 담당한다.
- 3S LiPo alarm은 독립적인 operator warning으로 유지한다.
- 완제품 RC LiPo pack을 사용하는 이 phase에서는 BMS를 사용하지 않는다.

이 문서는 최종 schematic이 아니다. 안전한 bench bring-up을 위한 architecture와 validation rule
set이다.

## 1. Safety Principle

전원계는 battery, motor, wiring의 failure mode를 기준으로 설계해야 한다.

핵심 규칙:

```text
전원은 firmware를 믿기 전에 먼저 검증한다.
Firmware safety는 electrical safety가 검증된 뒤 추가한다.
```

공학적 의미:

- Fuse 하나만으로 robot이 안전해지는 것은 아니다.
- Switch는 firmware motor disable logic을 대체하지 않는다.
- Firmware low-voltage stop은 LiPo alarm을 대체하지 않는다.
- Buck converter 설정값은 multimeter로 측정하기 전까지 믿지 않는다.
- Logic signal을 위해 common ground가 필요하지만, motor current를 약한 signal wiring으로 흘리면 안 된다.

## 2. Power Domains

Robot은 초기 기준으로 세 개의 power domain을 가진다.

| Domain | Source | Loads | Notes |
| --- | --- | --- | --- |
| Battery domain | 3S LiPo | fuse, switch, buck input, motor rail | 에너지가 크고 위험도가 가장 높음 |
| Motor domain | switched battery rail | MDD10A `POWER+`/`POWER-`, DC motor | noise와 high current가 큼 |
| Logic domain | buck converter output | STM32, ESP32, sensor, driver logic | regulated low-voltage electronics |

신호가 domain을 넘나드는 지점에서는 기준 ground를 공유해야 하지만, 실제 current path는 가능한 한
물리적으로 분리한다.

## 3. Main Power Path

초기 power path:

```text
3S LiPo battery
    |
    +-- XT60 main connector
    |
    +-- AWG14 main positive wire
    |
    +-- blade fuse holder
    |
    +-- blade fuse
    |
    +-- DC-rated main switch
    |
    +-- switched battery rail
            |
            +-- MDD10A motor driver POWER+
            |
            +-- XL4015 #1 input
            |
            +-- XL4015 #2 input
            |
            +-- XL4016 input candidate
```

Battery negative path:

```text
3S LiPo negative
    |
    +-- MDD10A POWER-
    |
    +-- buck converter input negative
    |
    +-- controlled common ground reference for logic signals
```

Notes:

- Fuse는 battery positive 쪽 가까이에 둔다.
- Main switch는 fuse 뒤의 battery positive path를 끊도록 둔다.
- Fuse를 power distribution 분기 이후에만 두지 않는다.
- Motor current는 perfboard copper trace로 흘리지 않는다.
- 첫 전원 투입 전에 XT60 polarity를 확인한다.

## 4. LiPo Operating Envelope

3S LiPo pack은 cell 3개가 직렬로 연결된 battery다.

Reference values:

| State | Per cell | Pack voltage |
| --- | --- | --- |
| Fully charged | 약 4.2 V | 약 12.6 V |
| Nominal | 약 3.7 V | 약 11.1 V |
| Storage target | 약 3.7-3.85 V | 약 11.1-11.55 V |
| Conservative warning region | 약 3.6 V | 약 10.8 V |
| Conservative stop region | 약 3.5 V | 약 10.5 V |

Project rules:

- Pack을 의도적으로 deep-discharge하지 않는다.
- LiPo protection을 firmware에만 의존하지 않는다.
- Test 중에는 3S low-voltage alarm을 사용한다.
- Test가 끝나면 battery를 분리한다.
- 당분간 사용하지 않을 pack은 storage voltage로 보관한다.
- 부풀거나, 찢어졌거나, 과열됐거나, 물리적 손상이 있는 pack은 사용하지 않는다.
- LiPo balance charger로만 충전한다.

Initial voltage policy:

| Condition | Initial behavior |
| --- | --- |
| Pack above warning threshold | 다른 fault가 없으면 operation allowed |
| Pack near warning threshold | Telemetry warning 후 stop 준비 |
| Pack below stop threshold | STM32가 motor output disable |
| Low-voltage alarm sounds | Operator가 test stop 후 battery disconnect |

정확한 threshold는 load가 걸렸을 때의 voltage sag를 측정한 뒤 조정한다.

## 5. Fuse Architecture

Fuse는 주로 wiring을 보호하고 fault 상황의 fire risk를 줄이기 위한 부품이다. Motor driver나 MCU가
모든 fault에서 살아남도록 보장하지 않는다.

Initial blade fuse plan:

| Test stage | Fuse candidate | Reason |
| --- | --- | --- |
| Bench power test, no motor load | 10 A | 초기 wiring check에서 fault energy를 낮춤 |
| Wheels lifted motor test | 10 A 또는 15 A | 낮은 load의 motor behavior만 확인 |
| Low-speed chassis test | 15 A 또는 20 A | 중간 수준 drivetrain load 허용 |
| Higher-load test | Current measurement 이후에만 30 A | 첫 test fuse로 사용하지 않음 |

Selection rules:

- 현재 test stage에서 불필요하게 끊어지지 않는 가장 낮은 fuse부터 시작한다.
- Fuse rating은 실제 current를 측정하거나 추정한 뒤에만 올린다.
- Fuse rating은 wire gauge와 connector current에 맞아야 한다.
- 더 큰 fuse는 wiring, stall, mechanical friction 문제의 해결책이 아니다.

## 6. Main Switch Architecture

Main switch는 수동 energy isolation device다.

Requirements:

- DC-rated switch.
- 예상 robot current에 맞는 current rating.
- Battery positive path에서 fuse 뒤에 배치.
- Bench test 중 손이 닿기 쉬운 위치.
- ON/OFF 방향을 명확히 표시.

중요한 한계:

```text
Main switch 하나만으로 emergency-stop 설계가 완성되는 것은 아니다.
```

Firmware는 fault, timeout, disarm, startup 상황에서 여전히 MDD10A PWM을 0으로 만들고
nonzero motor output을 차단해야 한다.

## 7. Buck Converter Architecture

초기 converter 역할:

| Converter | Initial role | Notes |
| --- | --- | --- |
| XL4015 #1 | STM32/ESP32 logic 5 V candidate | 연결 전 output 확인 |
| XL4015 #2 | sensor 또는 auxiliary 5 V candidate | noise/aux load를 분리 |
| XL4016 | higher-current auxiliary candidate | 해당 load가 필요할 때까지 deferred |

Rules:

- 각 buck converter는 MCU board를 연결하지 않은 상태에서 조정한다.
- Load를 연결하기 전에 multimeter로 output voltage를 확인한다.
- Module이 다른 voltage를 요구하지 않는 한 5 V rail은 5.0 V로 시작한다.
- 3S LiPo를 STM32, ESP32, sensor, encoder logic에 직접 연결하지 않는다.
- 새 converter의 trimmer 위치가 안전하다고 가정하지 않는다.
- 첫 integration test 전에 converter output voltage를 기록한다.

Board-power caution:

- 초기 firmware development 중에는 STM32/ESP32를 USB로 전원 공급하는 편이 더 단순하고 안전하다.
- Buck-powered operation으로 넘어갈 때는 board manual에서 허용된 5 V input path를 확인한다.
- Robot buck converter가 PC USB port를 역으로 powering하지 않도록 주의한다.
- 각 test에서 하나의 controlled power method를 선택하고 test log에 적는다.

## 8. Grounding Architecture

이 프로젝트는 logic signal을 위해 common ground가 필요하지만, ground path는 의도적으로 설계해야 한다.

Ground model:

```text
Battery negative
    |
    +-- motor current return path to MDD10A
    |
    +-- buck converter negative input
            |
            +-- logic ground reference
                    |
                    +-- STM32 GND
                    +-- ESP32 GND
                    +-- sensor GND
                    +-- MDD10A logic GND
```

Rules:

- PWM/DIR signal이 동작하려면 STM32와 MDD10A logic GND가 common이어야 한다.
- UART가 동작하려면 ESP32와 STM32 GND가 common이어야 한다.
- I2C/ADC signal이 동작하려면 sensor GND와 STM32 GND가 common이어야 한다.
- Thin signal ground wire로 high motor current가 흐르지 않게 한다.
- Motor current loop는 짧게 만들고, 가능하면 UART/I2C/encoder wire와 물리적으로 떨어뜨린다.

## 9. Motor Power Safety

MDD10A module은 motor power rail과 motor 사이에 위치한다.

Rules:

- Logic output behavior를 검증한 뒤 motor power를 연결한다.
- STM32 PWM pin은 zero duty로 시작해야 한다.
- STM32 PWM pin은 reset 중 zero 또는 input-safe 상태가 기본이어야 한다.
- Reset behavior가 불확실하면 PWM line에 external pull-down 또는 별도 power gate를 추가한다.
- 방향 전환 전에는 해당 motor PWM을 0으로 낮춘다.
- 첫 motor test는 robot을 들어 올리거나 track load를 제거한 상태에서 low duty로 진행한다.

Recommended staged motor tests:

| Stage | Motor power | Motor load | Goal |
| --- | --- | --- | --- |
| M0 | disconnected | none | STM32 PWM/DIR pin 확인 |
| M1 | connected | 가능하면 motor를 track에서 분리 | Driver output behavior 확인 |
| M2 | connected | wheels/tracks lifted | Direction과 low-duty response 확인 |
| M3 | connected | chassis on ground | Low-speed motion only |

## 10. Logic and Signal Protection

초기 prototype 보호 후보:

| Signal | Protection candidate | Reason |
| --- | --- | --- |
| STM32 PWM/DIR to MDD10A | 100-330 ohm series resistor | Wiring mistake 시 fault current 제한 |
| UART TX lines | 100-330 ohm series resistor | 초기 cross-board test risk 감소 |
| Encoder outputs | 필요 시 level shifter 또는 divider | Output이 STM32 input limit을 넘으면 필요 |
| PWM lines | pull-down resistor | Reset 중 PWM zero 유지 |

STM32에 직접 연결하기 전에 encoder voltage를 측정해야 한다.

## 11. Battery Voltage Sensing Plan

STM32는 나중에 resistor divider와 ADC를 통해 battery voltage를 monitoring한다.

Initial plan:

```text
Battery switched rail
    |
    +-- resistor divider
    |
    +-- STM32 ADC input
```

Requirements:

- Full-charge voltage에서도 divider output이 STM32 ADC input limit보다 낮아야 한다.
- Resistor value는 current를 제한하면서도 ADC reading이 충분히 안정적이어야 한다.
- Motor noise로 reading이 불안정하면 나중에 filtering을 추가한다.
- ADC reading은 multimeter 측정값으로 calibration한다.
- 초기 test 중에는 3S LiPo alarm을 독립적으로 계속 연결한다.

Example design target:

```text
12.6 V full-charge pack -> ADC voltage safely below 3.3 V
```

정확한 resistor value는 이 문서에서 확정하지 않는다.

## 12. Power-Up Procedure

### Stage A: No Battery, No MCU Load

Checklist:

- XT60, fuse holder, switch, distribution point의 polarity를 점검한다.
- Switch ON 상태에서 battery positive path continuity를 확인한다.
- Switch OFF 상태에서 open circuit인지 확인한다.
- Battery positive와 negative rail 사이에 short가 없는지 확인한다.
- Motor rail과 logic rail에 label을 붙인다.

### Stage B: Buck Converter Setup

Checklist:

- Buck converter input을 fuse를 통해 연결한다.
- 아직 STM32/ESP32는 연결하지 않는다.
- Main switch를 켠다.
- Output을 target voltage로 조정한다.
- Output polarity를 측정한다.
- Switch를 끄고 battery를 분리한다.

### Stage C: Logic-Only Power

Checklist:

- Buck output이 확인된 뒤 STM32/ESP32/sensor rail을 연결한다.
- 가능하면 motor driver `B+`는 연결하지 않는다.
- Board power LED와 USB debug behavior를 확인한다.
- UART 또는 USB serial communication을 확인한다.
- STM32 motor output이 boot 시 disabled인지 확인한다.

### Stage D: Driver Logic Test

Checklist:

- MDD10A logic side를 연결한다.
- 가능하면 motor power를 disable하거나 motor를 분리한다.
- PWM pin이 boot 시 zero인지 확인한다.
- DIR logic 확인 후에만 low-duty output을 명령한다.

### Stage E: Low-Power Motor Test

Checklist:

- Conservative fuse를 사용한다.
- Track을 지면에서 띄운다.
- 매우 낮은 duty부터 적용한다.
- Motor direction을 확인한다.
- 이상 발열, 냄새, reset이 없는지 확인한다.
- Low-voltage alarm이 울리면 즉시 stop한다.

## 13. Shutdown Procedure

Normal shutdown:

1. `DISARM` 또는 stop command를 보낸다.
2. PWM output이 zero인지 확인한다.
3. Nonzero motor output이 차단됐는지 확인한다.
4. Main switch를 끈다.
5. LiPo battery를 분리한다.
6. Motor driver와 buck converter가 따뜻하면 식힌다.
7. 이상 behavior를 기록한다.

Emergency shutdown:

1. 가능하면 control input을 놓거나 stop을 보낸다.
2. 물리적으로 안전하면 main switch를 끈다.
3. Switch로 상황이 멈추지 않으면 battery를 분리한다.
4. 과열되거나 손상된 LiPo를 맨손으로 만지지 않는다.

## 14. Validation Measurements

처음 기록할 measurement:

| Measurement point | Expected result | When |
| --- | --- | --- |
| LiPo pack voltage | Safe 3S range 안에 있음 | 매 test 전 |
| After fuse/switch voltage | ON 상태에서 pack voltage와 유사 | 첫 power path test |
| Buck output | 별도 지정 없으면 5.0 V target | MCU 연결 전 |
| STM32 5 V/3.3 V rails | Board-allowed range 안에 있음 | Logic-only power |
| ESP32 power rail | Board-allowed range 안에 있음 | Logic-only power |
| MDD10A logic input | 3.3 V PWM/DIR signal | Driver logic test |
| STM32 GND와 driver GND 사이 전압 | 0 V에 가까움 | Signal test 전 |
| Low duty 중 motor rail voltage | 심한 collapse 없음 | Low-speed motor test |

Record format:

```text
Date:
Battery:
Fuse:
Switch:
Buck converter:
Load connected:
Measured voltage:
Observation:
Decision:
```

## 15. Fault Response Table

| Fault | Detection | Required response |
| --- | --- | --- |
| Low battery alarm sounds | Audible alarm | Test stop, disarm, LiPo disconnect |
| STM32 ADC below stop threshold | Firmware | PWM zero, fault report |
| UART/CAN command timeout | Firmware | PWM zero, safe/disarmed state 유지 |
| Buck output over target | Multimeter | MCU 연결 금지, converter 재조정 |
| Reverse polarity found | Visual/multimeter | Power 금지, wiring 수정 |
| Fuse blows | Fuse inspection | 교체 전 current path 조사 |
| MCU resets when motor starts | Serial log/LED reset | Motor test stop, power/GND/noise 점검 |
| Motor driver overheats | Touchless check/thermal caution | Test stop, load/duty 감소 |
| Encoder signal overvoltage | Multimeter/oscilloscope | STM32 입력 전 level shifting 추가 |

## 16. Items Deferred From First Power Bring-Up

Deferred:

- CAN bus power integration
- LiDAR power integration
- ROS2 computer power integration
- custom power distribution PCB
- high-load driving
- battery current sensor
- fully integrated emergency-stop circuit

Reason:

첫 power phase는 더 많은 load를 추가하기 전에 battery, fuse, switch, buck, controller, driver,
motor의 기본 동작을 검증하는 단계다.

## 17. Exit Criteria

이 architecture는 다음 조건을 만족하면 HAL bare-metal drivetrain bring-up으로 넘어갈 준비가 된다.

- Main battery path가 fused and switched 상태다.
- Buck converter output을 MCU 연결 전에 측정했다.
- STM32/ESP32/sensor power가 raw battery voltage와 분리되어 있다.
- MDD10A motor current가 perfboard trace로 흐르지 않는다.
- Common ground가 의도적으로 설계되고 문서화되어 있다.
- Motor PWM은 zero가 기본이다.
- LiPo test 중 low-voltage alarm을 사용한다.
- 첫 powered test의 measurement log가 존재한다.

## Final Decision

초기 power architecture는 보수적인 fused 3S LiPo distribution을 사용하고, motor domain과 logic
domain을 분리한다.

STM32 firmware는 나중에 voltage-based safety behavior를 추가하지만, 첫 번째 보호선은 여전히 올바른
wiring, fuse selection, measured buck output, manual switch control, disciplined LiPo handling이다.
