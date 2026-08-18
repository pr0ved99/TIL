# Physical E-stop Component And Rating Selection

## 목적

이 문서는 Step 6 기능 회로를 실제 부품과 정격으로 구체화하는 Step 7 정본이다.

```text
REQ-ESTOP-001~020
-> CD-ESTOP-001~007
-> 이 문서의 SD-ESTOP-001~006
-> Step 8 KiCad RevB/ERC
-> T-ESTOP-001~007
```

Step 7의 목표는 catalog 제목의 전류값만 보고 부품을 고르는 것이 아니다. 각 부품에 대해
최대 부하, 최소 적용 부하, DC make/break, coil voltage, 온도, 배선과 fuse coordination을
같이 검토한다.

## 현재 판정

```text
Step 7 overall: PARTIAL / K1 ORDERED, RECEIVED-PART AND REMAINING COMPONENT GATES OPEN
S0 emergency-stop actuator: PREFERRED CANDIDATE
S2 manual re-enable switch: PREFERRED CANDIDATE, LOW-POWER CONTACT GATE OPEN
K2 control/seal-in relay: PREFERRED CANDIDATE, LOW-VOLTAGE GATE OPEN
S0-B sense conditioner: PREFERRED CANDIDATE, VALUE/BENCH GATE OPEN
K1 motor-power relay: TE V23134J1052D642 ORDERED / NUMERICAL PASS / BENCH GATE OPEN
F2 control fuse: PRELIMINARY 0.5 A TIME-DELAY CANDIDATE
F1/main wire/connectors: PROVISIONAL CANDIDATES / EXACT PART AND MEASUREMENT GATE OPEN
ADC divider/clamp/bleed values: NOT SELECTED
Purchase release: NOT APPROVED
```

이 판정은 부품의 기능 후보를 좁혔다는 뜻이다. 회로도/ERC, 실제 구매품 확인, DMM/scope와
motor-disconnected 시험을 통과했다는 뜻은 아니다.

## 근거와 주장 경계

- Emergency-stop actuator와 contact block은 제조사 공식 lineup/specification을 사용한다.
- Relay는 AC 또는 resistive headline current를 motor interrupt rating으로 대체하지 않는다.
- Manufacturer motor current, fuse curve, DC motor-load relay data와 installed harness 근거를
  함께 닫기 전 K1, F1, main wire와 terminal을 최종 승인하지 않는다.
- 이 설계는 ISO 13850, IEC 60204-1과 IEC 60947-5-5의 원칙을 참고하지만 산업 안전 인증,
  PL, SIL, Category 또는 표준 전체 적합성을 주장하지 않는다.
- K2와 optocoupler는 no-auto-restart와 진단 신호를 구현하는 일반 부품이며 safety relay 또는
  safety-rated input이 아니다.

사용한 제조사 공식 자료:

- [Omron A22NE lineup](https://www.ia.omron.com/products/family/1111/lineup.html)
- [Omron A22NE specifications](https://www.ia.omron.com/products/family/1111/specification.html)
- [Schneider XB4/XB5 contact-block selection](https://www.se.com/us/en/faqs/FA321024/)
- [Schneider ZBE1016 low-power contact block](https://www.se.com/kr/ko/product/ZBE1016/)
- [Panasonic TX2-12V product page](https://na.industrial.panasonic.com/products/relays-contactors/mechanical-signal-relays/signal-relays/series/11597/model/12000)
- [Vishay VO617A datasheet](https://www.vishay.com/docs/83430/vo617a.pdf)
- [TE Connectivity V23134J1052D642 / 1393304-9 product page](https://www.te.com/en/product-1393304-9.html)
- [TE Connectivity F7 relay datasheet, Rev.2607](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=V23134X0000A002&DocType=Data+Sheet&PartCntxt=1393304-9)
- [Panasonic ACA14535 product page](https://industry.panasonic.com/global/en/products/control/relay/vehicle/number/aca14535)
- [Littelfuse ATOF 287 series datasheet](https://www.littelfuse.com/assetdocs/littelfuse_datasheet_287_atof_r2.7.pdf?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40)
- [Cytron MDD10A official FAQ](https://www.cytron.io/index.php?back=aHR0cHM6Ly93d3cuY3l0cm9uLmlvL2MtaW5kdXN0cnkvYW1wcC0xMGFtcC01di0zMHYtZGMtbW90b3ItZHJpdmVyLTItY2hhbm5lbHMjcHJvZHVjdC1mYXFz&product_id=35006&route=amp%2Fproduct%2Ffaq)
- [Alpha Wire conductor resistance chart](https://cdn.belden.com/-/media/Project/AlphaWire/AlphaWire/Content/Part-Number-Color-Codes/AWG-Conversion.pdf)
- [Panasonic ACW212 product page](https://na.industrial.panasonic.com/products/relays-contactors/mechanical-power-relays/lineup/automotive/series/2926/model/3108)
- [Schneider RPF2AJD product page](https://www.se.com/us/en/product/RPF2AJD/)
- [Schneider RSB2A080JD datasheet](https://iportal.se.com/Contents/docs/SQD-RSB2A080JD_DATA%20SHEET.PDF)

## Step 7에서 발견한 구조 문제

### 대전류 K1 접점은 저전류 자기유지 접점이 아니다

Step 6 초기안은 K1의 두 번째 NO 접점으로 K1 coil을 자기유지하려 했다. 그러나 검토한
대전류 relay의 최소 switching load가 실제 coil current보다 컸다.

| Candidate | Relevant official data | Step 7 interpretation |
| --- | --- | --- |
| Schneider `RPF2AJD` | 12 V coil, 2NO, 1.7 W, minimum switching current 500 mA | Coil current 약 142 mA가 500 mA보다 작아 두 번째 pole의 자기유지를 공식 조건으로 지지하지 못함 |
| Panasonic `ACW212` | 12 V, 2 Form A, coil 117 mA, minimum switching load 1 A at 14 VDC | 117 mA 자기유지 load가 최소 switching load보다 작음 |

Maximum contact current를 넘지 않는 것만으로는 충분하지 않다. 너무 작은 부하는 접점막을
안정적으로 파괴하지 못해 접촉 불량이 생길 수 있다. 따라서 K1의 두 번째 power pole을
자기유지용으로 사용하지 않는다.

### S0-B의 3.3 V direct dry-contact도 공식 최소 부하를 만족하지 못한다

Omron A22NE의 minimum applicable load는 `1 mA at 5 VDC`다. Step 6 초기안의
`3.3 V pull-up -> S0-B -> GND`는 전압 조건이 공식 최소 적용 조건보다 낮다. 그래서
S0-B에는 5 V에서 약 5 mA가 흐르는 contact-wetting loop를 사용하고, PC7은
optocoupler transistor로 level translation한다.

## Selection decisions

### `SD-ESTOP-001`: K2가 자기유지와 K1 coil permission을 분리한다

```text
VBAT_PROTECTED
  -> F2
  -> S0-A NC
  -> ESTOP_CONTROL_PERMISSION
       +-> [S2 NO OR K2-HOLD-NO]
       |    -> K2 coil
       |    -> PWR_GND
       |
       +-> K2-K1-ENABLE-NO
            -> K1 coil
            -> PWR_GND
```

동작은 다음과 같다.

1. Initial power-up에서는 K2가 OFF라 K1도 OFF다.
2. S2를 누르면 K2 coil이 energize된다.
3. K2 pole 1이 S2를 우회해 K2 자신을 hold한다.
4. K2 pole 2가 K1 coil을 energize한다.
5. S0-A가 열리면 K2와 K1 coil의 공통 permission이 제거된다.
6. S0를 release하거나 전원이 복구돼도 K2가 OFF이므로 다시 S2를 눌러야 한다.

이 구조는 `REQ-ESTOP-011`의 “documented equivalent preserving the same behavior”에
해당한다. MCU는 K2 또는 K1을 energize하는 경로에 포함되지 않는다.

### `SD-ESTOP-002`: S0는 Omron `A22NE-M-PD02-N`을 우선 후보로 한다

| Item | Official value | 판단 |
| --- | --- | --- |
| Actuator | Red, 40 mm, latching, turn reset | Emergency-stop 조작과 deliberate release 구분에 적합 |
| Contacts | 2NC | S0-A hardware cut와 S0-B monitoring 분리 가능 |
| Direct opening | NC model certified direct opening | 일반 pushbutton보다 목적 적합성이 높음 |
| Standards | EN 60947-5-1 direct opening, EN 60947-5-5 listed | 표준 원칙을 반영한 actuator 근거로 사용 |
| DC rating | DC-13 1 A at 30 VDC; DC-12 2 A at 30 VDC | 약 0.15 A 이하 control loop 후보에 충분한 여유 |
| Minimum load | 1 mA at 5 VDC | S0-B를 5 V/약 5 mA loop로 변경해야 함 |
| Protection | IP65 oil-resistant | Prototype enclosure의 기본 환경 저항 근거 |

구매 전에는 판매처 형번, 두 NC terminal 번호, panel cutout와 rear depth를 다시 확인한다.

### `SD-ESTOP-003`: S2는 Schneider 저전력 modular assembly를 우선 후보로 한다

우선 조합은 `ZB5AA3` green flush spring-return head, `ZB5AZ009` fixing collar와
`ZBE1016` gold-flashed screw-clamp 1NO low-power contact block이다. Standard contact가 포함된
complete `XB5AA31`보다 약 9~13 mA K2 coil load에 목적 적합성이 높다.

Schneider의 공식 contact-block selection은 `ZBE1016`을 “special contact block for low
power switching”으로 분류한다. 다만 현재 확보한 공개 자료에서 exact minimum switching
capacity 수치까지 닫지 못했으므로, 해당 수치가 K2 worst-case coil load보다 낮다는 공식
자료를 확보하거나 actual contact-drop/반복 동작을 검증하기 전에는 구매 승인하지 않는다.

S2 stuck-closed 한 개만으로 자동 재투입되지 않는지는 Step 8 schematic review와
`T-ESTOP-004/005` fault injection에서 확인한다. 이 부품의 green colour는 “run command”가
아니라 “motor-rail hardware re-enable request”라는 panel label과 함께 사용한다.

### `SD-ESTOP-004`: K2는 Panasonic `TX2-12V`를 우선 후보로 한다

| Item | Official value | Circuit use |
| --- | --- | --- |
| Contact arrangement | 2 Form C | NO pole 1 self-hold, NO pole 2 K1 coil permission |
| Coil | 12 V, 140 mW | Nominal current 약 `11.7 mA` |
| Pick-up | Nominal의 75% 이하 | 최대 9.0 V에서 pickup |
| Contact capacity | 2 A at 30 VDC resistive | K2/K1 coil current보다 큼; inductive clamp 검토는 별도 |
| Minimum switching capacity | 10 uA at 10 mVDC | K2 self-hold current보다 충분히 낮음 |
| Construction | Sealed, PCB terminal | Control PCB/perfboard footprint와 mechanical retention 필요 |

계산:

```text
I_K2_NOM = 0.140 W / 12 V = 11.7 mA
R_K2_EQ  = 12 V / 11.7 mA ~= 1.03 kohm
I_K2_AT_9V ~= 8.75 mA >> 10 uA minimum switching capacity
```

다만 battery, F2, S0-A와 harness drop를 포함한 `V_K2_COIL_MIN`이 9.0 V 이상인지 아직
입증하지 않았다. System undervoltage stop threshold가 확정되기 전까지 K2는
`PREFERRED CANDIDATE`, purchase release는 `HOLD`다.

검토 후 제외/보류한 대안:

| Part | 판정 | 이유 |
| --- | --- | --- |
| Schneider `RSB2A080JD` | 보류 | 2CO/12 V coil은 적합하지만 공식 minimum switching voltage가 12 V여서 방전 중 3S 조건을 직접 지지하지 못함 |
| Schneider `RPF2AJD` | K2/K1 자기유지용 제외 | Minimum switching current 500 mA가 coil load보다 큼 |

### `SD-ESTOP-005`: S0-B는 5 V optocoupler conditioner를 사용한다

```text
ESTOP_SENSE_5V
  -> R_OPTO_LED
  -> S0-B NC
  -> VO617A-3 LED
  -> LOGIC_GND

STM32 3V3
  -> R_PC7_PULLUP
  -> ESTOP_SENSE / PC7
  -> VO617A-3 transistor
  -> LOGIC_GND

healthy/closed = PC7 LOW
pressed/open, wire break or 5 V loss = PC7 HIGH
```

Vishay `VO617A-3` DIP-4를 prototype 우선 후보로 한다. `-3` CTR group은 5 mA input에서
충분한 transistor sink margin을 제공하는 방향으로 선택했다.

초기 계산 후보:

```text
V_SENSE_5V_MIN = 4.75 V        # 5 V rail tolerance assumption, 아직 측정 필요
V_F_MAX_DESIGN = 1.6 V         # datasheet worst-case design input
R_OPTO_LED      = 680 ohm
I_LED_MIN       = (4.75 - 1.6) / 680 = 4.63 mA

R_PC7_PULLUP    = 10 kohm
I_PC7_SINK      = 3.3 / 10k = 0.33 mA
```

`I_LED_MIN`은 A22NE의 1 mA at 5 V minimum-load current보다 크다. 그러나 5 V rail tolerance,
VO617A exact suffix/CTR/temperature, PC7 threshold, RC/debounce와 measured LOW/HIGH voltage를
Step 8/9에서 확인하기 전까지 `680 ohm`과 `10 kohm`은 회로도 후보값이다.

이 channel은 S0-B open/wire break/5 V loss를 safe direction인 HIGH로 만든다. Optocoupler
transistor short, PC7 short-to-GND와 S0-B stuck-closed는 false healthy 잔여 고장으로 남으며
session press test와 K1 downstream rail comparison으로 관리한다.

### `SD-ESTOP-006`: K1/F1/main path는 manufacturer current와 보호협조로 좁힌다

K1는 두 motor의 전류를 동시에 make/carry/break한다. 필요한 최소 입력은 다음과 같다.

```text
I_MOTOR_CONT_TOTAL = I_LEFT_CONT + I_RIGHT_CONT
I_MOTOR_START_TOTAL = I_LEFT_START + I_RIGHT_START
I_MOTOR_STALL_TOTAL = I_LEFT_STALL + I_RIGHT_STALL
I_MOTOR_WORST = max(documented simultaneous start/stall/current-limit case)
```

K1 승인에는 최소 다음이 필요하다.

```text
K1 continuous DC current after temperature derating > I_MOTOR_CONT_TOTAL
K1 motor-load make capability >= I_MOTOR_START_TOTAL
K1 DC break capability >= declared E-stop break current
K1 terminal/wire/fuse coordination documented
K1 release/clamp timing <= T_K1_OPEN_MAX
```

현재 비교 benchmark:

| Part | Useful official evidence | Current disposition |
| --- | --- | --- |
| TE `V23134J1052D642` / `1393304-9` | 1 Form A NO, 12 V/90 ohm coil, 16 VDC maximum switching, continuous limiting 70 A at 23 C/50 A at 85 C/30 A at 125 C, 240 A make/70 A break | 2026-08-18 exact K1/socket/terminals ordered. 18.9 A envelope numerical PASS; received-part, motor-load waveform, voltage-drop/thermal and rail-off bench hold |
| Panasonic `ACA14535` | 1 Form A, 12 V, internal resistor, 20 A continuous at 80 C; 12 V motor load 120 A inrush/20 A steady for 100k operations | 두 motor 18.9 A 보수 envelope에 수치상 적합한 preferred electrical benchmark. 20 A 대비 여유가 작고 개인 판매 제한이 있어 procurement/bench hold |
| Panasonic `ACW212` | 2 Form A, 10~16 V coil range, 120 A/5 s carrying; high-output motor failsafe application | Carry evidence는 강하지만 published switch-off line이 200 A resistive 3회이고 welding terminal; 현재 K1 확정 근거로 부족 |
| Schneider `RPF2AJD` | 2NO, 12 V, nominal 30 A class | Official motor-load make/break evidence가 없고 minimum load도 자기유지와 불일치; K1에서 제외 |

Motor label `MG540P30_12V`와 encoder pinout 사진만으로는 current rating을 확정할 수 없었다.
그러나 2026-08-17 WHEELTEC 기술지원 회신으로 motor당 rated `1.44 A`, stall `9 A`,
rated power `15 W`, rated speed `280 rpm`, rated torque `2.6 kgf·cm`, stall torque
`10 kgf·cm`와 PWM `5~20 kHz`를 확보했다. 이 회신은 정식 데이터시트 원본이 아니라
제조사 지원 답변이며 starting current, terminal resistance, temperature/duty-cycle 상세는
여전히 없다. 근거 정본은
[`../assets/vendor/wheeltec/2026-08-17_mg540p30_12v_support_reply_ko.md`](../assets/vendor/wheeltec/2026-08-17_mg540p30_12v_support_reply_ko.md)다.

따라서 two-motor steady benchmark는 `2 x 1.44 A = 2.88 A`, simultaneous stall envelope는
`2 x 9 A = 18 A`로 계산을 시작할 수 있다. 다만 이 두 값만으로 K1을 구매 승인하지 않는다.
Starting pulse, MDD10A current limiting, fuse time-current, DC motor-load make/break, harness
temperature rise와 실제 current-limited bench evidence를 함께 닫아야 한다.

3S full-charge `12.6 V`에서 정지 DC motor 전류가 전압에 비례한다고 보수적으로 추정하면
motor당 `9 x 12.6 / 12 = 9.45 A`, 두 motor 합은 `18.9 A`다. 이 값은 실측이나 제조사
보증 상한이 아니라 K1 break와 main-path transient 평가에 사용하는 1차 설계 envelope다. MDD10A의
official `10 A continuous / 30 A peak per channel`는 9.45 A보다 높으므로, driver가 이 motor의
locked-rotor current를 더 낮게 제한한다고 가정하지 않는다.

Panasonic `ACA14535`는 20 A continuous at 80 C와 motor-load 120 A inrush/20 A steady life
test를 제공하는 비교 benchmark다. 실제 주문품은 TE `V23134J1052D642`다. TE의 가장 엄격한
listed temperature point인 125 C에서도 continuous limiting current가 30 A이므로 18.9 A는
63% utilization이며 수치상 통과한다. 12.6 V도 12 V version의 16 VDC maximum switching 아래다.

다만 TE 공개 endurance 예시는 주로 resistive load이고 프로젝트의 MDD10A input, 실제 motor
start/stall waveform과 배선 transient를 그대로 보증하지 않는다. 따라서 판정은
`EXACT PART ORDERED / NUMERICAL PASS / RECEIVED-PART AND BENCH VALIDATION REQUIRED`다.
입고품의 label, terminal map, coil resistance/NO continuity, socket retention, voltage drop,
temperature와 actual rail-off를 확인하기 전 최종 release하지 않는다.

상세 계산 정본은
[`../09_Electrical_Design/10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md`](../09_Electrical_Design/10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md)다.

2026-08-16에는 WHEELTEC가 공개한 `R1/R3/R3X/TT` chassis 자료 묶음도 로컬에서 전수
검색했다. PDF 59개, 문서명 71개, ZIP 27개의 member/source text와 STP/DWG 등 loose
CAD/text 파일에서 `MG540`, `540P30`, rated/start/stall-current 계열 근거가 0건이었다.
미완료 표시가 남은 파일 2개는 serial terminal과 waveform-viewer 실행 파일이므로 이
결론에 영향을 주지 않는다. 이 자료 묶음 자체는 MG540 식별·전류 정격의 1차 근거로
채택하지 않는다. 이후 별도로 받은 2026-08-17 기술지원 회신이 rated/stall current 입력을
제공했지만, K1/F1 승인에는 위의 coordination 계산이 계속 필요하다.

## F2 control fuse preliminary calculation

K2 구조에서 F2가 정상적으로 운반하는 최대 steady current는 K2 coil과 K1 coil의 합이다.
K1 benchmark 중 더 큰 `ACA14535` coil을 사용하면:

```text
I_K2_12V  ~= 11.7 mA
I_K1_12V  = 130.9 mA
I_F2_NOM  ~= 142.6 mA
I_F2_AT_12V6 ~= 150 mA order
```

따라서 `0.5 A time-delay`가 1차 후보지만 아직 part number가 아니다. 최종 선택은 다음을
동시에 만족해야 한다.

- 3S full charge와 coil tolerance에서 nuisance opening이 없다.
- K1/K2 clamp short, coil/harness short에서 control wire보다 먼저 제한한다.
- 제조사 time-current curve와 interrupt rating이 battery fault current에 적합하다.
- Fuse holder와 lead/terminal 정격이 fuse nominal current보다 작지 않다.

S0-A는 ON 상태에서 K1+K2 coil current를, S2/K2-HOLD는 K2 coil current를,
K2-K1-ENABLE은 K1 coil current를 운반한다. Step 8에서는 각 contact에 이 load label을
표시한다.

## F1, main wire와 connector provisional decision

2026-08-18 계산에서는 `18.9 A`를 two-motor worst-current amplitude 후보로 사용한다.

| Item | Provisional decision | Remaining release evidence |
| --- | --- | --- |
| F1 | Littelfuse `0287010.PXCN`, ATOF 10 A/32 VDC prototype candidate | Start waveform, nuisance opening, exact holder, battery prospective short current와 thermal test |
| K1 main terminal | TE socket `VCF7-1000`/`1393310-4`, main terminals `280756-4` x2, coil terminals `42281-1` x2 ordered | Received-part fit, crimp/retention, contact resistance와 temperature rise |
| Main wire | AWG 14는 전기 계산 minimum baseline. 주문한 `280756-4`가 AWG 12~10용이므로 released common path는 AWG 12 우선 | Exact wire insulation/temperature/ampacity, 왕복 길이, bundling와 ambient |
| Per-motor branch | AWG 16 minimum candidate | Exact wire와 installed length/termination |
| Battery/K1/MDD10A connector | Common path 20 A 이상 DC-carry class를 출발 gate로 사용 | Exact official current/contact-resistance data, mating, keying와 strain relief |

10 A ATOF의 정상-load ratio는 `2.88/10 = 28.8%`이고, 18.9 A simultaneous-stall은
정격의 189%다. 공식 curve의 160% 지점은 0.25~50 s, 200% 지점은 0.15~5 s이므로
189%의 정확한 trip time을 임의 보간하지 않는다. F1은 downstream short/harness protection
후보이지 즉시 locked-rotor protection이라는 주장을 하지 않는다. 15 A로 올리면 18.9 A가
126%에 불과하므로, 10 A nuisance-opening 실측 원인을 규명하기 전 rating을 높이지 않는다.

Alpha Wire 예시 저항 `9.08 mΩ/m`를 사용하면 AWG 14 common 1 m 왕복 loop의 18.9 A
전압강하는 약 `0.172 V`, 손실은 약 `3.24 W`다. 12 V의 임시 3% drop target으로 계산한
최대 왕복 길이는 약 `2.10 m`다. 이 계산은 exact wire ampacity 또는 인증을 대신하지 않는다.

## Coil clamp MVP item과 post-MVP ADC open item

K1/K2 coil마다 coil 바로 옆에 독립 suppression function을 둔다. Plain diode를 자동 채택하지
않는다. Relay에 internal resistor/diode가 있으면 그것을 suppression function으로 기록하고
외부 clamp를 중복 장착하지 않는다. K1/K2 내부 suppression 유무, coil energy와 release-time
자료를 바탕으로 none, diode, diode+zener 또는 TVS를 선택하고 `T_K1_OPEN_MAX`를 scope로
확인한다.

PA4/PB0 divider는 post-MVP diagnostic option이다. 구현할 때는 `12.6 V`만 맞추고 끝내지
않으며, 다음 입력이 닫혀야 exact resistor, capacitor와 clamp를 승인한다.

- 3S full-charge tolerance와 rail transient design maximum
- STM32 absolute maximum과 ADC input range
- Divider Thevenin resistance와 selected ADC sample time
- Series/protection current under resistor short/open faults
- Filter settling time와 `T_RAIL_DECAY_MAX`
- USB/logic power가 있을 때 ADC clamp를 통한 backfeed

## Step 7 closure checklist

| Gate | Status | Closure evidence |
| --- | --- | --- |
| S0 exact model/contact topology | Candidate selected | Actual received-part label, 2NC terminal map와 continuity table |
| S2 exact assembly | Conditional | `ZB5AA3 + ZB5AZ009 + ZBE1016` official minimum-load closure와 actual momentary NO continuity |
| K2 exact model | Conditional | `V_K2_COIL_MIN >= 9.0 V` 또는 더 낮은 pickup relay 재선정 |
| S0-B conditioner | Conditional | KiCad calculation, PC7 LOW/HIGH DMM table와 wire-open test |
| K1 | Exact part ordered / numerical PASS | TE `V23134J1052D642`가 18.9 A envelope에 catalog 수치상 적합; 입고 검사, suppression, motor-load/thermal/rail-off bench 필요 |
| F2 | Conditional | Exact fuse/holder datasheet와 time-current coordination |
| F1/main wire/connectors | Provisional candidates | 10 A ATOF, AWG 12 common/per-motor AWG 16 우선. 기존 AWG 14 holder는 `280756-4`에 직접 압착 불가; exact holder/wire/connector와 start/thermal 계측 필요 |
| Coil clamps | Open | Exact relay suppression data and release-time capture |
| ADC networks | Deferred / post-MVP | Transient/input/source-impedance calculation and bench sweep; MVP blocker 아님 |

## 다음 단계

2026-08-13에 Step 8 KiCad RevB functional schematic와 ERC `0/0`을 완료했다. 다음은 다음
순서다.

1. 보유한 10 A blade fuse/holder의 exact 형상, DC 정격, lead gauge와 상태를 확인하고 F1 10 A ATOF 호환 여부를 결정한다.
2. AWG 12 common/AWG 16 branch wire와 connector 자료·설치 길이를 확보한다. 기존 AWG 14 holder를 재사용하려면 별도 정격 splice까지 승인한다.
3. TE K1/socket/terminal 입고 후 label, terminal map, fit, NO/coil resistance와 continuity를 기록한다.
4. Actual S0/S2/K2/F1의 exact part와 continuity를 기록한다.
5. Motor-disconnected `T-ESTOP-001~005`에서 no-auto-restart, wire-open, coil drop과 rail decay를 검증한다.
6. Gate PASS 뒤 첫 lifted single motor에서 start current, voltage drop, holder/terminal 온도와 encoder noise를 계측한다.
7. PA4/PB0 divider/protection은 MVP 뒤 별도 diagnostic V-cycle에서 계산·실장·검증한다.
