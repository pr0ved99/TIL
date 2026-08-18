# Perfboard Low-current Allocation Plan

## 목적과 상태

이 문서는 `150 x 100 mm`, `55 x 37홀` controller carrier 만능기판의 **남은 영역**에
들어갈 저전류 회로의 범위와 물리적 영역을 먼저 고정한다. 현재 상태는
`DRAFT / NO NEW SOLDER`다.

이 기판은 빈 만능기판이 아니다. 2026-08-12 사용자 확인에 따라 NUCLEO-F446RE,
ESP32-S3와 GY-BNO085용 socket/header 위치가 이미 영구 납땜돼 있다. Module은 분리할 수
있지만 header 위치는 이동 대상으로 취급하지 않는다.

정확한 hole coordinate는 actual K2, optocoupler, terminal block, fuse holder의 몸체 치수와
pin pitch를 확인한 뒤 정한다. 이 문서는 KiCad E-stop schematic 또는 continuity evidence를
대체하지 않는다.

## 설계 근거

- [`19_Architecture_Decision_Record_ko.md`](../01_System_Architecture/19_Architecture_Decision_Record_ko.md)의
  reset-safe `10 kΩ` 결정
- [`25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md)의
  K2 three-wire re-enable, S0-B optocoupler와 connector/test-point 경계
- [`26_Physical_EStop_Component_and_Rating_Selection_ko.md`](../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md)의
  conditional K2/VO617A 후보와 K1/F1 blocker
- [`01_Adapter_Plate_and_Electronics_Layout_ko.md`](../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md)의
  `150 x 100 mm`, `55 x 37홀` mechanical baseline

## Existing Fixed Occupancy

Onshape Top View 기준 고정 경계는 다음과 같다.

| Area | Existing use | Constraint |
| --- | --- | --- |
| Left | NUCLEO-F446RE/ST-LINK socket/header | Header desolder/move 금지, USB와 board removal envelope 유지 |
| Upper middle | GY-BNO085 socket/header | Header 위치 유지, sensor module과 wiring 접근 공간 유지 |
| Lower right | ESP32-S3 socket/header | Header 위치 유지, USB cable와 module removal envelope 유지 |
| ESP32 right end | PCB antenna region | 위·아래·주변에 relay, connector, ground bus와 wire bundle 추가 금지 |
| Upper right | 현재 open-hole candidate area | Motor logic pull-down과 low-current E-stop/control의 1순위 후보 |

기존 header의 납땜면 joint와 이미 연결된 wire가 차지한 hole은 사진/continuity로 확인하기
전까지 빈 hole로 계산하지 않는다.

## 만능기판 남은 영역에 올리는 것과 올리지 않는 것

| 구분 | 기본 위치 | 이유 |
| --- | --- | --- |
| R9~R12 MDD10A DIR/PWM `10 kΩ` pull-down | Upper-right top edge의 MDD10A logic connector 바로 옆 | STM32 cable이 빠져도 driver input이 LOW 쪽으로 유지되게 함 |
| K2 two-pole control relay | Upper-right open area 후보 | Self-hold와 K1 coil permission을 담당하는 저전류 control 회로 |
| K2 coil clamp | K2 coil pin 바로 옆 | Clamp loop 면적과 switching transient를 줄임; exact topology/value는 TBD |
| F2 control fuse/holder | 만능기판 또는 인접 inline 후보 | K1+K2 coil/control branch 보호; `0.5 A time-delay`는 preliminary |
| S0-A, S2, K1-coil connector | 만능기판 가장자리 | Panel/offboard part와 분리 가능한 harness 경계 제공 |
| VO617A-3, `680 Ω` LED resistor, PC7 `10 kΩ` pull-up | 만능기판 후보 | S0-B 5 V loop와 STM32 3.3 V sense conditioning |
| R9~R12/coil/sense test points | 만능기판 가장자리 또는 부품 옆 | DMM/logic probe의 반복 측정과 오접촉 감소 |
| K1 main contact | 만능기판 밖 | 두 motor의 make/carry/break current가 perfboard trace를 지나면 안 됨 |
| F1 main fuse와 battery/motor power distribution | 만능기판 밖 | High-current fault path와 holder/wire rating이 아직 motor-data blocked |
| MDD10A motor `POWER+/-`, motor output current | 만능기판 밖 | Motor current는 dedicated wire/terminal로만 운반 |
| K1 coil clamp | K1 coil terminal 바로 옆, 기본적으로 만능기판 밖 | Clamp는 보호 대상 coil에 물리적으로 가까워야 함 |
| PA4/PB0 dual-rail ADC network | 미실장/DNP | Post-MVP diagnostic V-cycle |

K1 coil control wire는 만능기판 connector를 통과할 수 있지만 K1 main motor current는 절대
만능기판 동박을 통과하지 않는다.

## Component-side 영역 초안

아래는 사용자 확인 Onshape Top View를 단순화한 개념 배치다. Hole coordinate가 아니라
기존 고정 header와 남은 영역의 관계를 표시한다.

```text
Onshape Top View / 55 columns ---------------------------------------->

+-------------------------+-----------+-------------------------------+
| NUCLEO FIXED HEADER     | BNO FIXED | UPPER-RIGHT CANDIDATE         |
| / module envelope       | HEADER    | A: MDD logic conn. + R9~R12  |
|                         |           | B: VO617A/680R/PC7 pull-up    |
|                         |           | C: F2/K2/S0/S2/K1-coil conn. |
|                         |           | test points + rework gap     |
+-------------------------+-----------+-------------------------------+
| NUCLEO FIXED / removal envelope     | ESP32 FIXED HEADER/MODULE     |
|                                     | USB path | ANTENNA KEEP-OUT    |
+-------------------------------------+----------+---------------------+

37 rows
```

Upper-right candidate 내부 권장 순서:

- MDD10A와 가까운 top edge: logic connector와 R9~R12
- NUCLEO/PC7 쪽: VO617A sense block
- Outer/right edge: S0-A, S0-B, S2와 K1-coil offboard connectors
- 중앙: F2/K2와 coil test points
- BNO/module-removal 경계와 ESP32 antenna 경계에는 routing/rework gap

이 영역에 actual parts와 service loop가 들어가지 않으면 fixed header를 옮기지 않고 별도
small low-current daughterboard로 전환한다.

## Placement Rules

1. R9~R12는 STM32 header보다 MDD10A logic connector 가까이에 둔다.
2. 네 pull-down의 GND는 MDD10A logic reference GND와 직접 이어지며 motor return current를
   운반하지 않는다.
3. Signal line은 저항을 직렬 통과하지 않는다. 각 resistor는 signal node에서 GND로 내려가는
   shunt다.
4. VO617A의 pin 1~4 orientation과 K2 coil/contact pinout은 received-part marking과 official
   datasheet를 대조하기 전 배선하지 않는다.
5. S0-A, S0-B, S2 connector는 label/keying으로 구분한다. 동일한 무표기 2-pin connector를
   서로 바꿔 꽂을 수 있게 만들지 않는다.
6. K2 clamp는 K2 coil 바로 옆, K1 clamp는 K1 coil 바로 옆에 둔다.
7. `TP_ESTOP_SENSE`, `TP_K2_COIL_P`, `TP_K1_COIL_P`, `TP_LOGIC_GND`, `TP_PWR_GND`는
   probe가 인접 pin을 short시키지 않게 가장자리에서 접근 가능해야 한다.
8. Logic/control GND는 system의 지정된 common-ground 지점으로만 돌아가며 motor current가
   board ground wire를 통과하지 않게 한다.
9. 모든 connector에는 기능명, pin 1과 polarity를 component side에 영구 표기한다.
10. 최소 20%의 hole area를 spare/rework 공간으로 남긴다.
11. Existing NUCLEO/ESP32/BNO socket/header, 납땜 joint와 module removal envelope를 침범하지
    않는다.
12. ESP32 PCB antenna 아래·위·오른쪽 edge 방향에는 부품, copper bus와 wire bundle을
    추가하지 않는다.

## Exact Layout Freeze 입력

다음 실물이 확인되기 전에는 hole coordinate와 납땜을 승인하지 않는다.

| Required input | 확인 내용 |
| --- | --- |
| Perfboard | 실제 `55 x 37홀`, mounting-hole/edge clearance와 copper pattern |
| Existing carrier wiring | Component-side와 solder-side 정면 사진, header solder joint와 occupied-hole map |
| K2 | Actual part number, body size, pin pitch, coil/contact pin numbering |
| Optocoupler | Actual `VO617A-3` suffix, DIP-4 orientation과 pin 1 marking |
| Connectors | Pole count, pitch, wire exit direction, keying과 current rating |
| F2 holder | Actual footprint, time-current/interrupt-rated fuse와 service access |
| K1 coil interface | Coil voltage/current/polarity와 clamp 위치; K1 part selection은 별도 blocker |
| Harness direction | STM32, MDD10A, panel S0/S2와 K1로 나가는 실제 방향 |

## 다음 작업 순서

```text
Physical E-stop functional KiCad schematic + ERC
-> actual parts/board photo and dimensions
-> photo joint + Onshape body/removal boundary map
-> VeroRoute compatibility pilot
-> 55 x 37 digital component/solder-side layout
-> independent KiCad-net-to-hole review
-> 1:1 print overlay
-> component-side 1:1 dry placement
-> received-part connector/pinout table
-> hole-coordinate map and underside wiring plan
-> independent review
-> user soldering
-> de-energized resistance/continuity test
-> board power/back-power test
```

현재 승인 범위는 `fixed occupancy + upper-right candidate allocation only`다. 기존 header는
그대로 유지한다. 새 부품을 꽂아보는 dry placement는 가능하지만 lead cutting, soldering,
battery/USB/buck 연결은 아직 하지 않는다.
