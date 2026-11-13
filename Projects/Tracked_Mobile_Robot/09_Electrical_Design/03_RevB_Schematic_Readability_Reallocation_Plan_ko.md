# RevB 회로도 가독성 재배치 계획

## 목적

이 문서는 [`02_RevB_Schematic_Position_Baseline_2026-08-13_ko.md`](02_RevB_Schematic_Position_Baseline_2026-08-13_ko.md)에
기록한 실제 좌표와 `C:\Users\eyh12\Desktop\회로도 인쇄.pdf`의 A4 출력 결과를 기준으로
RevB를 다시 배치하는 실행 계획이다.

이번 재배치는 회로 기능, 부품 선정 상태 또는 net 이름을 변경하지 않는다. 목표는 다음과 같다.

1. 기존 검증된 encoder, motor logic, UART 영역은 불필요하게 흔들지 않는다.
2. Physical E-stop을 `main power`, `control/re-enable`, `sense`의 세 흐름으로 구분한다.
3. 심볼, Reference, Value, net label, GND와 설명 주석의 겹침을 없앤다.
4. 인쇄 PDF에서 화면 확대 없이도 흐름을 따라갈 수 있게 한다.

## 좌표와 표시 규칙

- 모든 좌표는 **mils**다.
- 표의 좌표는 심볼 center/anchor다.
- 모든 부품 심볼의 `Reference = 50 mils`, `Value = 40 mils`로 통일한다.
- net label과 긴 설명 주석은 기본 `25 mils`를 사용한다.
- 심볼만 단독으로 옮기지 않는다. 해당 pin에 직접 붙은 net label, GND, no-connect marker를
  함께 선택해 이동한다.
- 좌표만 보고 PASS하지 않는다. 각 phase 후 KiCad 원본, netlist, ERC와 A4 PDF를 다시 확인한다.

## 목표 영역

```text
X 1500 ---------------------------------------------------------- 10800

Y  700   [Battery / fuse / main switch / K1 main contact / MDD10A power]
Y 2000   [XL4015 feeds]                         [K1 relay]
Y 2600   [Physical E-stop control and manual re-enable]   [TP column]
Y 3800   [MDD10A logic] [K2 hold + K1 coil interface]
Y 5000   [S0-B 5 V contact-wetting and optocoupler sense block]
Y 5850   [UART]              [sense explanation]
Y 6400   [candidate output / lower notes]
```

## 전체 심볼 목표 좌표

`유지`도 명시한다. 표에 없는 임의 이동은 하지 않는다.

### 기존 기능 블록: 위치 유지

| 그룹 | References | 목표 |
| --- | --- | --- |
| TIM3 encoder | J1, R1, R2, R5, R6 | 현재 좌표 유지 |
| TIM5 encoder | J2, R3, R4, R7, R8 | 현재 좌표 유지 |
| XL4015 output / motor output | J3, J4 | 현재 좌표 유지 |
| MDD10A logic/pull-down | J5, R9, R10, R11, R12, J6 | 현재 좌표 유지 |
| Main power | J8, F1, SW1, J19, J7 | 현재 좌표 유지 |
| Converter feeds | J9, J10 | 현재 좌표 유지 |
| Main relay | K1 | 현재 좌표 유지 |
| E-stop front/control | F2, J14, S0, S2, K2, J16, J17 | 현재 좌표 유지 |
| Test points | TP1~TP7 | 현재 좌표 유지 |
| UART/candidate output | J11, J12, J13 | 현재 좌표 유지 |

위 유지 그룹도 Value가 50 mils이면 위치 이동 없이 40 mils로만 바꾼다.

### 이동 대상: S0-B 감지 블록

| 순서 | Ref | 현재 X,Y | 목표 X,Y | 회전 | 같이 이동할 항목 |
| ---: | --- | --- | --- | ---: | --- |
| 1 | R13 | 9500, 4950 | **6500, 5000** | 90 유지 | `AUX_5V`, `S0B_LED_FEED` labels |
| 2 | J15 | 8450, 4650 | **6500, 5550** | 0 유지 | pin1 `S0B_LED_FEED`, pin2 `S0B_TO_OPTO_ANODE` labels |
| 3 | R14 | 8450, 5350 | **9000, 5650** | 0 유지 | `STM32_3V3`, `ESTOP_SENSE` labels |
| 4 | U1 | 7400, 5350 | **8000, 5650** | 0 유지 | 두 signal labels와 U1 양쪽 GND 심볼 |
| 5 | J18 | 10000, 5200 | **10000, 5500** | 0 유지 | pin1/2 labels와 pin3 GND 심볼 |

목표 pin 위치는 다음과 같이 고정한다.

| Ref | Pin | 목표 좌표 | Net |
| --- | --- | --- | --- |
| R13 | 1 | 6350, 5000 | AUX_5V |
| R13 | 2 | 6650, 5000 | S0B_LED_FEED |
| J15 | 1 | 6300, 5550 | S0B_LED_FEED |
| J15 | 2 | 6300, 5650 | S0B_TO_OPTO_ANODE |
| U1 | 1 | 7700, 5550 | S0B_TO_OPTO_ANODE |
| U1 | 2 | 7700, 5750 | GND |
| U1 | 4 | 8300, 5550 | ESTOP_SENSE |
| U1 | 3 | 8300, 5750 | GND |
| R14 | 1 | 9000, 5500 | STM32_3V3 |
| R14 | 2 | 9000, 5800 | ESTOP_SENSE |
| J18 | 1 | 9800, 5400 | STM32_3V3 |
| J18 | 2 | 9800, 5500 | ESTOP_SENSE |
| J18 | 3 | 9800, 5600 | GND |

이 배치는 이전에 잘못 제시한 `U1 = 8800,5200`을 폐기한다. 그 좌표는 현재 R14 영역을
침범하므로 사용하지 않는다.

### 이동 대상: 설명 주석

| 순서 | 주석 | 현재 X,Y | 목표 X,Y | 목표 크기 |
| ---: | --- | --- | --- | ---: |
| 1 | K2 CONTROL RELAY | 9200, 2150 | **5000, 5000** | 25 |
| 2 | K1 COIL INTERFACE | 8450, 4010 | **8450, 4750** | 25 |
| 3 | S0-B SENSE | 7580, 5790 | **7800, 6250** | 25 |
| - | K1 MAIN CONTACT INTERFACE | 8850, 1250 | 유지 | 25 |

주석은 부품 이동 공간을 먼저 비운 뒤 옮긴다. K2와 K1 설명은 sense block 위쪽 경계를
넘지 않게 하고, S0-B 설명은 감지 블록 아래 독립 행에 둔다.

## 실행 순서

### Phase 0. 기준선 보존

1. KiCad 파일을 저장한다.
2. source SHA-256이 기준선과 같은지 확인한다.
3. ERC `0/0`을 확인한다.
4. 기존 A4 PDF를 보존한다.

PASS:

```text
48 component symbols accounted for
19 power symbols accounted for
ERC 0/0
No unplanned schematic edit
```

### Phase 1. 텍스트 규칙 통일

1. 모든 Reference를 50 mils로 맞춘다.
2. 모든 Value를 40 mils로 맞춘다.
3. 주요 설명 주석은 25 mils로 맞춘다.
4. 자동 필드 재배치 후 겹침을 확인한다.

이 단계에서는 심볼 좌표를 바꾸지 않는다.

### Phase 2. 주석으로 이동 공간 확보

다음 순서로 설명 주석만 옮긴다.

```text
K2 CONTROL RELAY -> 5000,5000
K1 COIL INTERFACE -> 8450,4750
S0-B SENSE -> 7800,6250
```

### Phase 3. 감지 블록 이동

충돌을 피하기 위해 다음 순서만 사용한다.

```text
R13 -> J15 -> R14 -> U1 -> J18
```

- R13과 J15를 먼저 왼쪽 빈 영역으로 옮긴다.
- R14를 U1 목표 위치에서 먼저 치운다.
- 그다음 U1을 목표 위치로 옮긴다.
- J18은 마지막에 아래로 300 mils 이동한다.
- 각 심볼은 해당 labels/GND와 함께 이동한다.

각 한 단계 후 사용자가 저장하면 실제 `.kicad_sch`를 다시 읽어 다음을 확인한다.

```text
center/rotation
Reference/Value size
pin endpoint coordinates
attached label/GND coordinate
netlist pin mapping
ERC
```

### Phase 4. 전체 시각 검토

1. A4 portrait PDF를 새로 출력한다.
2. 전체 페이지에서 기능 블록 간 여백을 확인한다.
3. E-stop 우하단을 확대 출력해 문자열 겹침을 확인한다.
4. 다음 항목이 하나라도 겹치면 좌표를 즉흥 변경하지 않고 계획 문서를 먼저 수정한다.

```text
symbol body
Reference
Value
pin number/name
net label
GND symbol
no-connect marker
blue explanatory note
```

### Phase 5. 전기적 동일성 검증

재배치 전후 netlist에서 모든 Ref/pin/net tuple을 비교한다.

필수 PASS:

```text
component count: 48 unchanged
all Ref/pin/net mappings unchanged
ERC: 0 errors / 0 warnings
no new dangling pin
no missing GND
no changed no-connect pin
```

## 최종 레이아웃 PASS 기준

- A4 출력에서 세 흐름이 구분된다.
  - main motor power
  - E-stop control/re-enable
  - S0-B/PC7 sense
- K2/J16/J17 설명과 심볼이 겹치지 않는다.
- R13/J15/U1/R14/J18이 독립 sense block으로 읽힌다.
- U1과 R14의 심볼·필드·라벨 사이에 가시적인 빈 공간이 있다.
- J18의 긴 Value가 우측 도면 경계를 넘지 않는다.
- 모든 Reference는 50 mils, 모든 Value는 40 mils다.
- ERC와 netlist equivalence가 모두 PASS다.

## 변경 금지 범위

재배치 중 다음은 변경하지 않는다.

- net name
- reference number
- pin number
- S0/K1/K2 contact topology
- K1/F1/K2/S0/S2의 TBD/CANDIDATE 상태
- pull-down resistor value와 topology
- footprint/BOM/on-board 속성
- 회로도 revision claim과 검증 상태

문서 기준 좌표가 실제 출력에서 실패하면 사용자가 임의로 맞추는 것이 아니라,
`현재 좌표 -> 관찰된 충돌 -> 수정 목표 좌표`를 이 문서에 먼저 기록한 뒤 다음 이동을 한다.

## 2026-08-13 사전 모의 배치 결과

원본을 변경하지 않고 `_review_render/revb_layout_mock.kicad_sch` 임시 복제본에만 위 목표
좌표를 적용해 SVG를 출력했다.

```text
Original source SHA-256:
A628C02E19E4C4DB2F5EA9BF52584E16292BACA759AB4A3A9D7AEAC19D89BB81

Mock ERC: 0 errors / 0 warnings
Original netlist tuples: 120
Mock netlist tuples: 120
Ref/pin/net tuple differences: 0
```

시각 검토에서는 R13/J15, U1, R14, J18 사이에 분리 공간이 생겼고 이전에 발생했던
U1-R14 직접 겹침은 없었다. 원본의 SHA-256은 모의 배치 전후 동일했다.

단, 이 결과는 계획 좌표의 1차 유효성 검토다. 사용자가 KiCad에서 실제로 이동할 때
필드 자동 배치와 함께 저장된 최종 결과를 매 단계 다시 읽어야 한다.
