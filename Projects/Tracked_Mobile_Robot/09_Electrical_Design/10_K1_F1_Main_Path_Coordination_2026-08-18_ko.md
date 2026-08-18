# K1, F1 And Main-Path Coordination — 2026-08-18

## 목적과 판정

WHEELTEC가 직접 회신한 `MG540P30_12V` 전류값으로 Physical E-stop 주전원 경로의 K1,
F1과 배선 후보를 계산한다. 이 문서는 구매 확정서가 아니라 `T-ESTOP-001`에 들어갈
정격 검토 기록이다.

```text
Current-envelope calculation: COMPLETE
K1 ordered candidate: TE Connectivity V23134J1052D642 / TE 1393304-9
K1 procurement: COMPLETE — ordered 2026-08-18
K1 electrical release: NUMERICAL PASS / received-part and motor-load bench gate open
F1 prototype candidate: Littelfuse 0287010.PXCN, ATOF 10 A / 32 VDC
F1 final release: HOLD — measured start waveform and holder/wire gate open
Main wire candidate: AWG 14 is the electrical calculation baseline, but AWG 12 is preferred for the released common path because the ordered K1 terminal accepts AWG 12~10; exact wire not selected
Per-motor branch candidate: AWG 16 minimum; exact wire not selected
Actual motor test release: NOT APPROVED
```

## 입력과 주장 경계

| Input | Value | Evidence / boundary |
| --- | ---: | --- |
| Motor rated voltage | 12 V | WHEELTEC direct support reply |
| Rated current per motor | 1.44 A | WHEELTEC direct support reply, twice confirmed |
| Stall current per motor | 9 A | WHEELTEC direct support reply, twice confirmed |
| Battery maximum | 12.6 V | 3S LiPo full-charge architecture limit |
| MDD10A current headline | 10 A continuous / 30 A peak per channel | Cytron official product information |
| Starting-current duration | Unknown | Must be measured |
| Motor thermal/duty limit | Unknown | No manufacturer detail received |

`9 A` stall은 12 V 회신값이다. 아래 12.6 V 계산은 DC motor 정지 시 역기전력이 없고 전류가
전압에 대략 비례한다는 보수적 1차 추정이다. 제조사 보증값이나 실측값으로 표기하지 않는다.

## 두 모터 전류 envelope

```text
I_CONT_TOTAL_12V  = 2 x 1.44 A = 2.88 A
I_STALL_TOTAL_12V = 2 x 9 A    = 18.0 A

I_STALL_EACH_12V6_EST = 9 A x (12.6 / 12.0) = 9.45 A
I_STALL_TOTAL_12V6_EST = 2 x 9.45 A = 18.9 A
```

첫 lifted single-motor 시험의 계산 envelope는 정격 `1.44 A`, 보수적 스톨 진폭 `9.45 A`다.
최종 two-motor worst-current amplitude 후보는 `18.9 A`다. 시작 pulse의 지속시간과 반복률은
알 수 없으므로 F1 time-current와 motor thermal 보호를 이 숫자 하나로 닫지 않는다.

MDD10A의 10 A continuous/channel 표기는 `9.45 A`보다 높다. 따라서 MDD10A가 이 모터의
스톨 전류를 더 낮게 제한한다고 가정할 수 없다. 30 A peak headline도 모터 자체의 약 9.45 A
추정 스톨 진폭보다 높으므로 이 설계의 motor protection setpoint가 아니다.

## K1 motor-power relay 검토

### Panasonic `ACA14535` comparison benchmark

공식 자료의 핵심 조건은 다음과 같다.

- 1 Form A, de-energized open
- 12 V coil, internal resistor, usable coil voltage 10~16 V
- 20 A continuous at 80 °C
- Motor-load electrical-life test: 12 VDC, 120 A inrush / 20 A steady, 100,000 cycles
- Release time maximum 10 ms without diode
- Minimum switching load: 1 A at 14 VDC resistive

| Check | Requirement | ACA14535 evidence | Result |
| --- | ---: | ---: | --- |
| Normal carry | > 2.88 A | 20 A continuous at 80 °C | Numerical PASS |
| Worst estimated carry/break | >= 18.9 A | 20 A motor steady / continuous | Numerical PASS, only 5.8% headroom |
| Motor make | >= measured start; initial bound 18.9 A | 120 A motor inrush life test | Numerical PASS |
| Default state | De-energized open | 1 Form A | PASS |
| Coil range | 3S rail in operating range | 10~16 V | PASS at 12.6 V; low-battery pickup remains a gate |
| Release | Must be measured in assembly | <= 10 ms without diode | Datasheet PASS, bench open |

따라서 `ACA14535`는 motor-load life를 대조하는 **전기적 비교 기준**이다. 그러나 20 A와 18.9 A의
차이는 약 1.1 A뿐이고 motor tolerance, terminal heating, 12 V 시험과 12.6 V system 차이가
남는다. 또한 Panasonic은 이 automotive relay를 개인에게 판매하지 않는다고 명시한다.

이 부품 자체는 조달 대상이 아니라 TE 주문품을 평가하기 위한 comparison benchmark로 남긴다.
실제 구매품은 공식 자료에서 de-energized-open, 12 V coil, temperature-derated carry,
make/break와 suppression/release 자료를 확인해야 한다. 단순히 `자동차 릴레이 40 A`라고
적힌 무명 제품은 대체 근거가 아니다.

### 주문한 TE `V23134J1052D642` K1 후보

2026-08-18에 다음 exact parts를 주문했다.

| Role | Ordered part | Quantity | Status |
| --- | --- | ---: | --- |
| K1 relay | TE Connectivity alias `V23134J1052D642`, TE part `1393304-9` | 1 | Ordered; incoming inspection pending |
| K1 socket | TE `VCF7-1000`, TE part `1393310-4` | 1 | Ordered; fit/terminal-map check pending |
| Main-contact terminal | TE `280756-4`, 9.5 x 1.2 mm, AWG 12~10 | 2 | Ordered; crimp/tool/retention check pending |
| Coil terminal | TE `42281-1`, 6.3 x 0.8 mm, AWG 18~14 | 2 | Ordered; crimp/tool/retention check pending |

TE의 2026-07 F7 datasheet에서 exact relay code `V23134-J1052-D642`는 bracket, internal
suppression 없음, 1 Form A NO, 12 V coil, plug-in quick-connect 구성이다. 주요 정격은 다음과 같다.

- Maximum switching voltage for the 12 V version: `16 VDC`
- Continuous limiting current: `70 A at 23 °C`, `50 A at 85 °C`, `30 A at 125 °C`
- Making current: `240 A`; breaking current: `70 A`
- Coil: `12 V`, `90 ohm ±10%`, `1.6 W`; must-operate `7.2 V`, must-release `1.6 V`
- Operate/release time: approximately `7 ms / 2 ms`, without coil suppression
- Minimum load: `1 A at 5 VDC`

| Check | Project requirement | TE evidence | Result / boundary |
| --- | ---: | ---: | --- |
| System voltage | 12.6 V maximum | 16 VDC maximum switching | Numerical PASS |
| Normal carry | > 2.88 A | 30 A even at 125 °C | Numerical PASS |
| Conservative two-motor envelope | >= 18.9 A | 30 A at 125 °C; 50 A at 85 °C | Numerical PASS; 63% utilization at the strictest listed temperature point |
| Make / break amplitude | >= initial 18.9 A bound | 240 A make / 70 A break | Numerical PASS; actual waveform still unmeasured |
| Fail-safe default | De-energized open | 1 Form A NO | PASS by part definition; actual continuity pending |
| Coil load | Must be switchable by K2 | about 133 mA at 12 V nominal; about 156 mA at 12.6 V and -10% resistance | K2/S0/F2 coordination input established |
| Drop-out | Rail must open fast enough | 2 ms relay release without suppression | Datasheet basis only; assembled rail-decay capture pending |

따라서 exact K1 조달 blocker는 닫혔고, catalog 수치 기준 `NUMERICAL PASS`다. 그러나 TE의
공개 endurance 예시는 주로 resistive load이며, 프로젝트의 MDD10A input-capacitance, motor
start/stall waveform, battery wiring과 regenerative/transient 조건을 그대로 재현한 motor-life
증거는 아니다. 입고 후 label, terminal map, coil resistance, NO continuity, socket retention,
contact voltage drop와 온도, 실제 rail-off를 검증하기 전에는 `ELECTRICAL RELEASE`로 올리지 않는다.

이 relay에는 internal suppression이 없다. TE는 diode 또는 p-n junction 방식이 inductive
switching에서 relay release를 늦추고 접점 수명에 불리할 수 있다고 경고한다. 따라서 K1 coil에
일반 flyback diode를 즉시 확정하지 않고, resistor/TVS 계열 후보와 K2 contact stress,
`T_K1_OPEN_MAX`를 함께 계산·측정한다.

## F1 주전원 fuse 검토

Littelfuse `0287010.PXCN` ATOF 10 A는 32 VDC, 1000 A at 32 VDC interrupt rating과
ISO 8820-3 reference가 있는 fast-acting blade fuse다.

```text
Normal-load ratio = 2.88 A / 10 A = 28.8%
12 V simultaneous-stall ratio = 18 A / 10 A = 180%
12.6 V estimated-stall ratio = 18.9 A / 10 A = 189%
```

ATOF datasheet의 time-current acceptance points는 160%에서 0.25~50 s, 200%에서
0.15~5 s다. 189%의 정확한 용단시간을 두 점 사이에서 임의 선형 보간하지 않는다. 이 곡선은
10 A fuse가 동시 locked-rotor를 즉시 차단한다고 보장할 수 없음을 보여준다.

| Candidate | Use decision |
| --- | --- |
| ATOF 10 A / 32 VDC | `T-ESTOP-001~005`와 첫 lifted single-motor의 prototype F1 후보. 정상 2.88 A에는 충분한 여유가 있고 short/harness protection 목적을 명시한다. |
| ATOF 15 A / 32 VDC | 현재 보류. 18.9 A가 정격의 126%라 locked-rotor protection은 더 약해진다. 10 A의 실제 nuisance opening 증거 없이 올리지 않는다. |

현재 inventory에는 `AWG 14 fuse holder`와 red `10 A blade fuse`가 있고, 2026-07-10
3S LiPo no-load path에서 switch OFF `0.00 V`, ON `12.49 V`를 통과했다. 이는 보유와 기본
연속성 증거일 뿐이다. 기존 사진만으로 holder 제조사, 정확한 ATO/ATC 치수, DC voltage/current,
contact/lead temperature rating을 식별할 수 없으므로 F1 재사용은 conditional이다. 먼저 fuse를
분리한 무전원 상태에서 holder/fuse 각인과 치수를 확인하고, 자료가 없으면 정격이 명확한
sealed inline ATO/ATC holder로 교체한다.

또한 주문한 K1 main terminal `280756-4`의 적용 전선 범위는 AWG 12~10이다. 따라서 보유한
AWG 14 holder lead를 이 단자에 직접 압착하지 않는다. 최종 common path는 AWG 12 lead가
달린 holder를 사용해 AWG 12로 통일하는 방안을 우선한다. 기존 holder를 쓰려면 AWG 12와
AWG 14 사이의 별도 접속부가 필요한데, 그 접속부의 exact part, DC current rating, crimp 범위,
strain relief와 발열 증거를 추가해야 하므로 기본안으로 채택하지 않는다.

F1은 downstream short와 main harness 보호가 1차 목적이다. Motor locked-rotor 보호는
measured current/timeout, firmware safe-stop, 운용 제한과 열 시험을 별도 묶음으로 닫아야 한다.
Fuse holder는 32 VDC 이상, 10 A 이상이 아니라 접점 발열 여유를 둔 정격, 올바른 단자와
strain relief를 가져야 한다. Battery prospective short current가 1000 A interrupt rating 아래인지도
battery 자료 또는 제한된 fault-current 근거로 확인한다.

## Main wire와 voltage-drop 후보

Alpha Wire의 tinned-copper conductor chart에서 예시 저항값을 사용한 1 m 왕복 loop 계산이다.
실제 선정은 구매할 wire의 공식 insulation/temperature/ampacity 자료로 다시 승인한다.

| Path candidate | Example resistance | Current | 1 m loop drop | 1 m loop loss |
| --- | ---: | ---: | ---: | ---: |
| Common main, AWG 14 | 9.08 mΩ/m | 18.9 A | 0.172 V | 3.24 W |
| Common main, AWG 12 | 5.73 mΩ/m | 18.9 A | 0.108 V | 2.05 W |
| Per-motor branch, AWG 16 | 14.3 mΩ/m | 9.45 A | 0.135 V | 1.28 W |

12 V에서 임시 voltage-drop 목표를 3% (`0.36 V`)로 놓으면 AWG 14 common-path의 허용
왕복 길이 계산값은 약 `2.10 m`다. 이는 표준 적합성 주장이 아니라 배선 길이 검토 기준이다.

- AWG 14는 common path의 전기 계산 minimum baseline으로만 유지
- 주문한 `280756-4`가 AWG 12~10용이므로 Battery–F1–S1–K1–MDD10A common positive와 matching negative return의 released harness는 AWG 12 우선
- AWG 14를 섞는다면 별도 정격 접속부와 그 검증을 문서화하며, 단순 꼬임/납땜만으로 전선 굵기를 전환하지 않음
- MDD10A에서 각 motor로 나가는 branch: AWG 16 minimum candidate
- 실제 loop length, bundle, ambient, insulation temperature, crimp/terminal rating을 기록하기 전 release 금지
- Connector/holder common path는 20 A 이상 DC carry와 낮은 contact resistance를 공식 자료로 확인

## 보호협조 결론

```text
3S battery
-> F1: ATOF 10 A / 32 VDC prototype candidate
-> S1 / holder / connector: exact DC rating >= selected path requirement
-> K1: TE V23134J1052D642 ordered; numerical PASS, received-part bench release pending
-> AWG 12 preferred released common path; AWG 14 remains calculation baseline only
-> MDD10A: 10 A continuous per motor channel
-> AWG 16 minimum branch candidate
-> MG540P30_12V x 2
```

현재 K1 exact-part 조달과 catalog 정격 검토까지 닫혔다. 다음이 모두 닫혀야 배선/시험 release다.

1. 입고 K1/socket/terminal의 label, fit, NO/coil resistance와 continuity 검사
2. K1 coil suppression 선정 및 assembled drop-out/rail-decay 시간
3. 10 A ATOF exact holder와 실제 wire/terminal part, installed loop length
4. 무전원 pin-map/continuity/cross-wire 검사
5. Motor-disconnected `T-ESTOP-001~005`
6. 첫 lifted single-motor에서 supply current/start pulse/connector voltage drop/온도 기록

## K1 입고 직후 무전원 검사

배터리, USB와 모든 외부 전원을 분리한 상태에서만 아래 순서로 진행한다.

1. Relay label이 `V23134J1052D642` 또는 TE part `1393304-9`인지 확인한다.
2. Socket이 `VCF7-1000`/`1393310-4`, main terminal이 `280756-4` x2, coil terminal이
   `42281-1` x2인지 포장 label과 실물을 대조한다.
3. 깨짐, 휜 blade, 부식, socket 변형이 없고 relay가 socket에 끝까지 유지되는지 확인한다.
4. Relay 단독 coil resistance를 측정한다. 공식 `90 ohm +/-10%`에 따라 `81~99 ohm`이면 PASS다.
5. 무여자 상태에서 NO main contact는 open이어야 한다. 임의로 12 V를 인가하거나 main
   contact를 부하에 연결하지 않는다.

Part number 불일치, coil short/open, `81~99 ohm` 이탈, 무여자 main-contact continuity 또는
물리 손상이 있으면 즉시 HOLD하고 전원을 인가하지 않는다. Coil polarity와 suppression 회로는
입고 검사를 통과한 뒤 별도 bench 단계에서 확정한다.

실제 시험 중 fuse 용단, terminal/holder 발열, 냄새/변색, 예상 밖 rail 유지, K1 chatter 또는
전류 급상승이 보이면 즉시 power를 차단하고 다음 단계로 넘어가지 않는다.

## 공식 근거

- [TE Connectivity V23134J1052D642 / 1393304-9 product page](https://www.te.com/en/product-1393304-9.html)
- [TE Connectivity F7 relay datasheet, V23134X0000A002, Rev.2607](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=V23134X0000A002&DocType=Data+Sheet&PartCntxt=1393304-9)
- [Panasonic ACA14535 official product data](https://industry.panasonic.com/global/en/products/control/relay/vehicle/number/aca14535)
- [Littelfuse ATOF 287 series official datasheet](https://www.littelfuse.com/assetdocs/littelfuse_datasheet_287_atof_r2.7.pdf?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40)
- [Littelfuse 0287010.PXCN official product data](https://www.littelfuse.com/de/products/fuses-overcurrent-protection/fuses/automotive-fuses/blade-fuses-shunt/atof/287/0287010-pxcn)
- [Cytron MDD10A official FAQ](https://www.cytron.io/index.php?back=aHR0cHM6Ly93d3cuY3l0cm9uLmlvL2MtaW5kdXN0cnkvYW1wcC0xMGFtcC01di0zMHYtZGMtbW90b3ItZHJpdmVyLTItY2hhbm5lbHMjcHJvZHVjdC1mYXFz&product_id=35006&route=amp%2Fproduct%2Ffaq)
- [Alpha Wire AWG conversion and conductor resistance chart](https://cdn.belden.com/-/media/Project/AlphaWire/AlphaWire/Content/Part-Number-Color-Codes/AWG-Conversion.pdf)
- [WHEELTEC direct-support reply record](../assets/vendor/wheeltec/2026-08-17_mg540p30_12v_support_reply_ko.md)
