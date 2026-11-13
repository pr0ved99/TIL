# Adapter Plate RevB E-stop Mounting Preflight

## 목적과 현재 판정

이 문서는 `P-07A`의 received-plate 기구 검토다. 기존 adapter plate에 E-stop 관련 부품을 모두
직접 체결한다는 뜻이 아니라, 각 부품을 다음 네 종류로 나눠 장착 경계와 케이블 접근성을
동결하는 것이 목적이다.

1. adapter plate 또는 별도 강성 bracket에 고정할 부품
2. permanent perfboard에 납땜할 저전류 부품
3. harness 중간에 고정할 inline 부품
4. 사용자가 접근하는 별도 operator panel 부품

현재 판정은 다음과 같다.

```text
P-07A laptop/source audit: COMPLETE
Fabricated PC plate: USER-REPORTED RECEIVED
Exact revision identity and physical fit: NOT TESTED
P-07A physical mounting freeze: HOME H-01 PENDING
```

2026-08-26 사용자는 custom PC plate가 이미 도착했다고 확인했다. 이는 current fabricated
state를 `NOT SUBMITTED`로 판단했던 직전 repository audit를 정정한다. 다만 저장소에는 아직
도착품 사진, 실측값, 주문서 또는 실제 제조에 사용된 파일 hash가 없으므로 received plate를
아래 RevB DWG/DXF와 동일한 물건이라고 단정하지 않는다. 이 evidence gap은 “판이 없다”는
뜻이 아니라 source-to-part 추적성과 physical fit이 아직 열려 있다는 뜻이다.

2026-08-28 K1 assembly, S0, S2, VO617A-3, P6KE16CA x3와 F2 holder/fuse의 지정된 무전원
component screen은 PASS했다. 6P는 완성 harness가 아니라 loose connector kit와 별도 18 AWG
전선이며 아직 cavity map/crimp/retention이 열려 있다. 이 부품들은 H-01 dry placement가 가능하지만
mechanical fit PASS는 아니다. 2026-08-30 사용자는 `VH-30J + WX-03B` 압착 공구 세트가
도착했다고 보고했다. Exact 구성·상태·die fit과 6P first-article crimp/pull/continuity/retention은
아직 검사하지 않았으므로 mounting freeze는 계속 HOLD다.

## 저장소의 CAD 기준 감사

### 정식 문서화된 release와 최신 후보

| 구분 | 상태 | 근거 |
| --- | --- | --- |
| RevA | 문서화된 release, 주문 미제출 | [`releases/revA/README.md`](releases/revA/README.md) |
| RevB | 도착품의 유력한 주문 source 후보, 실물 동일성 미확인 | [`../assets/2026-08-18_adapter_plate_revB_PC3T_hole3p0_order.dxf`](../assets/2026-08-18_adapter_plate_revB_PC3T_hole3p0_order.dxf), [`../assets/2026-08-18_adapter_plate_revB_PC3T_hole3p0_order.dwg`](../assets/2026-08-18_adapter_plate_revB_PC3T_hole3p0_order.dwg) |
| Fabricated plate | 2026-08-26 사용자 보고 `RECEIVED` | 사진·실측·source mapping은 집 `H-01`에서 기록 |

RevB DXF를 직접 읽어 확인한 형상은 다음과 같다.

- 단위: mm
- 외곽: `174 x 208.933793526 mm`, corner radius `10 mm`
- 원형 관통 형상: `31개`
  - `8 x diameter 3.0 mm`
  - `21 x diameter 3.3 mm`
  - `2 x diameter 30 mm`
- RevA 대비 변경: 같은 위치의 8개 홀만 `diameter 2.2 -> 3.0 mm`
- 외곽과 나머지 홀 중심은 RevA와 동일

따라서 기존의 “small hole 3.0 mm” 표현은 전체 홀 패턴 설명으로는 부정확하다. RevB는
`3.0 mm`와 `3.3 mm` 소형 홀이 섞인 형상이다. DXF에는 각 홀의 부품 용도 메타데이터가
없으므로 좌표 비교만으로 fastener 목적까지 확정하지 않는다.

파일 무결성 기준:

| File | SHA-256 |
| --- | --- |
| `2026-08-18_adapter_plate_revB_PC3T_hole3p0_order.dxf` | `E2117F18E068E262595F232982F5A633319EBCE79F0C2D317FD2341C6F02EC2E` |
| `2026-08-18_adapter_plate_revB_PC3T_hole3p0_order.dwg` | `BF1AF96B33D35CA9C47BC98F77CCFC0706BDAF1A68E9A467F5FCB29D6CB65C3A` |

`PC 3T`는 파일명과 주문 당시 설계 의도다. 2D DXF 자체는 재질이나 두께를 증명하지 않으므로
도착품의 두께와 재질 표시, 주문 내역 또는 vendor 기록으로 별도 확인한다.

## 부품별 장착 경계

| 부품 | 장착 경계 | 현재 설계 결정 | 아직 필요한 evidence |
| --- | --- | --- | --- |
| K1 `V23134J1052D642` + `VCF7-1000` | adapter plate/chassis 쪽 별도 강성 bracket 우선 | Motor current와 AWG 12 main path는 perfboard를 통과하지 않는다. Exact relay/socket/terminal identity와 loose fit 무전원 PASS; 기존 RevB에 K1 전용 장착 형상은 없다. | 전체 dry fit, bracket/retention, terminal 출구, AWG 12 굽힘·공구 접근 공간 |
| K2 `TX2-12V` | permanent perfboard THT | `15 x 7.4 x 8.2 mm` PCB relay이며 upper-right low-current 영역 후보. 별도 plate hole은 필요하지 않다. | 현재 배선이 반영된 perfboard 위 실제 8-pin 정렬, 부품·module 탈착과 rework 여유 사진 |
| `VO617A-3`, `680 ohm`, `10 kohm` | permanent perfboard THT | PC7 E-stop sense conditioner로 K2 인접 저전류 영역에 둔다. Actual suffix, input diode 방향과 input-output isolation 무전원 PASS다. | Pin-1 orientation을 보존한 current perfboard dry fit와 assembled continuity |
| K2용 `P6KE16CA` | K2 coil 바로 옆 perfboard | Clamp loop를 짧게 유지한다. Exact `CA` marking과 bidirectional gross-short 무전원 screen은 PASS했다. | K2 내부 suppression 부재 확인, lead forming과 clearance |
| K1용 `P6KE16CA` | K1 coil terminal 바로 옆 절연 지지점 | K1에서 떨어진 perfboard까지 긴 clamp loop를 만들지 않는다. Exact `CA` marking과 bidirectional gross-short 무전원 screen은 PASS했다. | K1/VCF7 실제 coil terminal 접근과 절연·고정 방법 |
| F1 `FHAC0002ZXJA` 계열 holder | AWG 12 main harness의 inline holder | Plate 관통 장착 부품이 아니다. body를 P-clamp 또는 rated tie mount로 구속하고 양쪽 wire strain relief와 fuse service 공간을 둔다. | actual body 치수, lid opening 방향, clamp 선정, 설치 위치와 lead bend |
| F2 `FHAC0001ZXJA` | control harness의 inline holder | Perfboard current trace 위에 fuse holder를 억지로 올리지 않는다. Holder에 인장이 걸리지 않도록 인접 위치에 고정한다. | 입고 body/lead 확인, fuse 교체 접근과 clamp 선정 |
| S0 `SF2ER-E2R2B-A` | 별도 operator panel | 사용자가 track을 건드리지 않고 즉시 누르고 의도적으로 해제할 수 있어야 한다. Body `SF2ER-E2R2B`, 2NC block과 latch/release 무전원 PASS; Main horizontal plate 내부 장착 대상으로 보지 않는다. | Order suffix `-A` trace, panel cutout/두께, rear depth와 배선 접근 |
| S2 `IDEC ABW110G` | 별도 operator panel | `diameter 22 mm`급 momentary re-enable 조작부다. Terminal `3-4` momentary-NO 무전원 screen은 PASS했고 S0와 기능·label을 명확히 분리한다. | actual rear depth, terminal 방향, panel cutout와 tool access |
| S1 main power switch | 별도 operator panel 또는 chassis edge | S0와 혼동되지 않고 track 접근 없이 조작 가능해야 한다. | exact model, DC rating, marking, cutout와 rear depth |
| 6P E-stop loose connector kit | signal/control inline disconnect | S0-A/S0-B/S2 회로를 분리·점검하기 위한 connector다. Motor current를 운반하지 않으며 아직 harness로 조립되지 않았다. | mating-face cavity map, keying, first-article 18 AWG crimp/terminal retention, bend/strain relief와 label |

K1 relay body의 catalog 치수만으로는 장착을 동결할 수 없다. 실제 build는 socket, crimp
terminal과 AWG 12 wire가 결합되며 이 조립체의 출구 방향과 굽힘 공간이 body 자체보다 큰
제약이기 때문이다.

참고한 제조사 자료:

- [TE Connectivity 1393304-9 product page](https://www.te.com/en/product-1393304-9.html)
- [Panasonic TX relay official drawing](https://industry.panasonic.com/ac/cdn/e/control/relay/signal/catalog/mech_eng_tx.pdf)
- [Littelfuse FHAC inline holder data](https://www.littelfuse.com/assetdocs/ato-fhac-datasheet?assetguid=272e0b1a-a576-4173-8740-c1eb469efd79)
- [IDEC ABW110G product page](https://www.idec.com/en-in/switches-indicator-lights/switches-pushbuttons/22mm-25mm-30mm-switches/tw-22mm-metal-bezel/abw110g)
- [Vishay VO617A datasheet](https://www.vishay.com/docs/83430/vo617a.pdf)
- [Vishay P6KE datasheet](https://www.vishay.com/docs/88369/p6ke.pdf)

## Cable And Service Rules

1. Battery/K1/MDD10A motor-current path와 encoder/UART/E-stop sense wire는 묶음과 통과
   경로를 분리한다.
2. K1/F1 common path는 AWG 12를 기준으로 하며 motor current를 perfboard copper로
   운반하지 않는다.
3. F1과 F2는 fuse를 교체할 때 다른 module이나 track을 분해하지 않아도 접근 가능해야 한다.
4. S0, S1, S2의 rear terminal은 chassis edge 또는 sharp cutout과 접촉하지 않게 절연하고
   tool 접근 공간을 둔다.
5. 6P connector는 S0-A/S0-B/S2를 label과 cavity map으로 구분하며, 흔들림이 contact terminal로
   직접 전달되지 않게 strain relief를 둔다.
6. K1/K2 clamp는 각 coil 바로 옆에 둔다.
7. Terminal 출구 방향과 실제 굽힘 반경이 정해지기 전 AWG 12/16 wire를 final length로
   절단하지 않는다.

## 추가 가공·장착 전 GO/NO-GO 표

| Gate | 판정 | 이유 또는 완료 조건 |
| --- | --- | --- |
| RevB DXF 외곽·홀 개수·RevA delta 확인 | `PASS / SOURCE INSPECTION` | DXF에서 수치 확인. 제조품 또는 DWG parity 증거는 아님 |
| Received plate와 RevB source 동일성 | `OPEN` | 주문 내역 또는 실측 홀 패턴을 DWG/DXF와 대조해야 함 |
| Received plate chassis/fastener fit | `NOT TESTED` | 실제 chassis overlay와 무전원 체결 필요 |
| Received PC plate 재질·두께 | `USER-REPORTED / MEASUREMENT OPEN` | 두께 실측과 가능하면 주문 내역 확인 필요 |
| K1 assembly 장착·배선 공간 | `NO-GO` | 실제 K1+VCF7+terminal dry fit과 bracket 위치가 없음 |
| K2/VO617/P6KE perfboard 공간 | `TARGET PENDING` | current perfboard top/bottom 사진과 actual-part dry fit 필요 |
| F1/F2 inline retention | `TARGET PENDING` | actual body와 service 방향에 맞는 clamp/tie point 필요 |
| S0/S1/S2 operator panel | `TARGET PENDING` | 별도 panel 원칙은 고정, exact cutout/rear depth와 위치는 미동결 |
| 6P routing/strain relief | `TARGET PENDING` | cavity map과 실제 vehicle routing 미확정 |
| Adapter plate 제작·수령 | `USER-REPORTED RECEIVED` | 주문 단계는 완료된 것으로 정정. exact revision/fit PASS는 아님 |
| 추가 plate 가공 또는 재주문 | `HOLD` | H-01 fit과 E-stop bracket 결정 전에는 drilling/reorder하지 않음 |

과거 RevA 업로드 시 vendor server 오류가 있었던 것은 역사적으로 맞다. 이후 PC plate 주문과
수령은 별도 사건이다. 두 기록을 합쳐 현재 plate까지 `NOT SUBMITTED`라고 판단하면 안 된다.

## 집에서 수행할 다음 물리 확인 순서

### H-01A: 현재 perfboard와 K2 dry fit

사전 조건:

- LiPo와 motor를 분리한다.
- USB, buck, STM32, ESP32를 포함한 모든 전원을 끈다.
- K2를 납땜하거나 pin을 억지로 벌리지 않는다.

작업:

1. 최종 pull-down 배선까지 반영된 perfboard component side와 solder side를 수직으로 촬영한다.
2. 눈금자 또는 hole grid가 보이게 한다.
3. K2 한 개를 upper-right 후보 영역 위에 가볍게 올리고 top marking과 pin-1 방향이 보이게
   촬영한다. 아직 삽입·납땜하지 않는다.

예상 결과:

- 8개 pin이 2.54 mm hole grid에 맞는다.
- 기존 resistor/wire/header와 겹치지 않는다.
- NUCLEO, BNO085, ESP32와 cable connector의 탈착 경로가 유지된다.
- K2 주변에 clamp, control wire와 probe 접근 공간을 남길 수 있다.

중지 조건:

- K2 pin이 기존 copper/wire 또는 부품 lead에 닿는다.
- pin을 굽혀야만 hole에 맞는다.
- 기존 module이나 connector를 뽑을 수 없게 된다.
- 촬영을 위해 전원을 연결해야 하는 상황이 된다.

PASS 기준:

```text
K2 8-pin grid fit
+ no existing-part contact
+ module/connector service path retained
+ clamp/wire/probe space identifiable in photos
```

### H-01B: K1과 inline holder capture

무전원 incoming screen을 통과한 K1/VCF7 relay, socket, 280756-4/42281-1 terminal과 F1/F2
holder를 ruler와 함께 촬영하고 실제 terminal 방향을 정한다. 그 다음에만 on-plate bracket인지
별도 chassis bracket인지 결정한다.

### H-01C: received plate identification and fit

모든 전원을 분리한 상태에서 다음을 기록한다.

1. Plate top/bottom 전체와 edge를 ruler와 함께 촬영한다.
2. 폭·높이·두께를 실측한다.
3. `8 x diameter 3.0 + 21 x diameter 3.3 + 2 x diameter 30 mm` 후보 패턴과 대조한다.
4. 억지 가공 없이 chassis, perfboard, XL4015 x2와 MDD10A를 dry fit한다.
5. 결과는 [`../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md`](../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md)에 기록한다.

## 카페에서의 즉시 다음 작업

카페에서는 physical fit을 추정하지 않는다. P-03 target runtime용 vector/evidence sheet와 H-01
fit-check·6P cavity-map 양식을 준비할 수 있다. P-03 target runtime을 집에서 닫은 뒤에는 `P-04`
TEL schema/source 설계로 이동한다.

## P-07A 완료 조건

다음이 모두 충족되면 `P-07A mounting freeze PASS`로 바꾼다.

1. K1/K2/F1/F2/S0/S1/S2와 6P connector의 장착 경계가 실제 부품 기준으로 확인됨
2. K1 bracket/retention, F1/F2 retention과 operator panel 위치가 도면에 반영됨
3. AWG 12/16 terminal 출구, bend, service와 power/signal 분리 경로가 확인됨
4. Received plate와 RevB source의 outer/hole pattern 동일성이 확인됨
5. Actual plate의 두께, 평탄도, chassis/module fit과 절연·접근성이 PASS함
6. 추가 drilling 또는 별도 bracket 필요 여부가 실제 부품 기준으로 확정됨

그 뒤 `P-07` mechanical fit을 닫는다. 새 plate나 추가 가공이 필요하다는 결과가 나온 경우에만
별도의 CAD revision과 주문 Gate를 다시 연다.
