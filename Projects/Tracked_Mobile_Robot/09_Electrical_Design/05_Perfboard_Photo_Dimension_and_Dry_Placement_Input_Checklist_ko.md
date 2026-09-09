# 만능기판 사진·치수 및 1:1 드라이 배치 입력 체크리스트

## 목적과 현재 승인 범위

Physical E-stop RevB functional schematic/ERC 이후, 실제 `150 x 100 mm`, `55 x 37홀`
carrier의 빈 홀과 보유 부품 외형을 확인해 hole-coordinate 배치도를 만드는 입력 목록이다.

현재 허용 작업은 **전원 없는 관찰, 촬영, 치수 측정과 부품을 올려보는 dry placement**뿐이다.

```text
새 납땜: 금지
lead 절단/굽힘 고정: 금지
LiPo/USB/buck 연결: 금지
MDD10A motor power/motor 연결: 금지
```

## 촬영 전 안전 조건

1. 3S LiPo를 로봇과 완전히 분리한다.
2. NUCLEO와 ESP32의 USB를 모두 분리한다.
3. XL4015 입력과 출력에 외부 전원이 연결되지 않았는지 확인한다.
4. 금속 공구와 loose wire가 기판 위에 남지 않게 한다.
5. 제거 가능한 module을 뺄 때는 방향과 pin 위치를 먼저 촬영한다. 영구 soldered header는
   제거하지 않는다.

## 필수 사진 1: 실제 만능기판

사진은 원근 왜곡을 줄이기 위해 카메라를 면과 평행하게 두고, 기판 전체가 프레임에 들어오게
찍는다. 자 또는 10 mm grid를 같은 평면에 둔다.

| 번호 | 사진 | 필수 조건 | 권장 파일명 |
| ---: | --- | --- | --- |
| 1 | Component side 정면 | NUCLEO/ESP32/BNO085 위치, board edge와 4개 mounting hole 포함 | `01_perfboard_component_side_top.jpg` |
| 2 | Solder side 정면 | 모든 solder joint, copper strip/pad pattern, 기존 jumper/wire 포함 | `02_perfboard_solder_side_top.jpg` |
| 3 | Upper-right 확대 | 현재 low-current 후보 영역의 빈 홀과 기존 점유 홀 식별 가능 | `03_perfboard_upper_right_closeup.jpg` |
| 4 | Connector/wire exit 확대 | MDD10A, STM32, ESP32와 panel 방향으로 나가는 배선 경로 표시 | `04_perfboard_wire_exit_closeup.jpg` |
| 5 | ESP32 antenna 주변 | antenna 끝과 board edge 사이 keep-out 판단 가능 | `05_esp32_antenna_keepout.jpg` |

가능하면 component side는 module 장착 상태와 module만 제거한 상태를 각각 찍는다. Header와
socket은 항상 실제 점유물로 남겨서 촬영한다.

## 필수 치수 2: 기판과 고정 점유 영역

기준 원점은 **component side에서 보았을 때 좌상단 첫 usable hole의 중심**으로 임시 정의한다.
열은 왼쪽에서 오른쪽으로 `C1...`, 행은 위에서 아래로 `R1...`로 센다. Solder side 사진은
좌우가 반전되므로 임의로 같은 좌표를 쓰지 않고 별도 표기한다.

측정·확인할 항목:

- 실제 hole pitch와 전체 `55 x 37` 여부
- board 외곽 `150 x 100 mm` 여부
- 네 mounting-hole 중심과 usable-hole grid 사이 거리
- NUCLEO header가 점유하는 최소/최대 column·row
- BNO085 header가 점유하는 최소/최대 column·row
- ESP32 header가 점유하는 최소/최대 column·row
- USB cable 삽입에 필요한 여유
- module removal 방향과 손가락/공구 접근 여유
- ESP32 antenna 시작/끝 위치와 부품·동박·wire 금지 영역
- 이미 soldered된 jumper, resistor와 wire가 점유한 hole

정확한 hole 번호를 세기 어렵다면, 사진 위에 원점과 네 모서리를 표시한 뒤 자로 edge부터
거리만 측정해도 된다. 사진과 거리로 hole 좌표를 역산한다.

## 필수 사진·치수 3: 실제 보유 부품

후보 문서의 부품명이 아니라 **손에 있는 actual part**를 기준으로 한다. 각 부품은 윗면 형번과
pin/lead 면을 모두 찍고, 자 또는 caliper를 함께 둔다.

| 우선 | 부품 | 필요한 정보 |
| ---: | --- | --- |
| A | `10 kΩ` 저항 4개 | body length/diameter, lead pitch 후보, 실제 저항값 |
| A | MDD10A logic connector 후보 | pole count, pitch, wire exit 방향, keying |
| A | terminal/header/test-point 후보 | pole count, pitch, body와 probe 접근 크기 |
| B | K2 후보 | 실제 형번, top/underside, body L/W/H, pin pitch/numbering |
| B | VO617A-3 후보 | 실제 suffix, DIP-4 body, pin-1 mark와 pitch |
| B | R13/R14 | 실제 값, package/body size와 lead pitch |
| B | F2 holder/fuse 후보 | actual part number, footprint, fuse access 방향 |
| B | S0/S2/K1 coil용 connector 후보 | 서로 바꿔 꽂지 못하게 할 key/label 방식과 wire exit |
| C | S0, S2, K1 | actual part가 있을 때만 label, terminal map와 mounting depth |

보유하지 않은 부품은 억지 치수로 대체하지 않고 `NOT OWNED / HOLD`로 기록한다. K1/F1/main
wire는 motor-current gate가 닫히기 전까지 exact placement와 구매를 승인하지 않는다.

## 드라이 배치에서 확인할 것

사진과 치수로 1차 지도를 만든 뒤에만 실제 기판 위에 부품을 올린다. 아직 lead를 hole에
고정하거나 절단하지 않는다.

- R9~R12와 MDD logic connector 사이 신호 경로
- VO617A/R13/R14/J15/J18 sense block의 분리
- K2/F2/coil clamp 후보 공간
- S0-A/S0-B/S2/K1-coil offboard connector의 edge 접근성
- test point에 probe를 대도 인접 pin이 short되지 않는 간격
- NUCLEO/ESP32/BNO085 module 제거 가능성
- ESP32 antenna keep-out
- underside wire가 교차하거나 motor current path로 오해되지 않는지
- 최소 20% spare/rework hole 유지 가능성

## 입력 완료 후 Codex 산출물

필수 사진과 치수를 받으면 다음을 순서대로 만든다.

1. component-side `C1...C55 / R1...R37` occupied-hole map
2. fixed header, removal envelope, antenna keep-out와 open area 표시
3. 실제 보유 부품 footprint 표
4. 2~3개 dry-placement 대안과 장단점
5. 선택안의 부품 중심/pin hole 좌표
6. solder-side point-to-point wiring 초안
7. independent schematic-to-hole/net review checklist
8. VeroRoute 또는 동등 도구의 component/solder-side 1:1 출력과 open/short 결과
9. 1:1 출력물과 실제 `55 x 37홀` 기판의 한 홀 오차 여부 확인

이 산출물과 사용자 dry-placement 사진이 통과하기 전에는 permanent soldering 단계로
넘어가지 않는다.
