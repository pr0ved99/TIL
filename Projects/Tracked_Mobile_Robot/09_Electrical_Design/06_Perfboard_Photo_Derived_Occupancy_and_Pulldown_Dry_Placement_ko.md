# 만능기판 사진 기반 점유 지도와 R9~R12 드라이 배치

## 상태와 좌표 기준

- 상태: `PHOTO + ONSHAPE CROSS-CHECKED PRELIMINARY / DRY PLACEMENT ONLY`
- 대상: `150 x 100 mm`, `55 x 37홀`, `2.54 mm pitch` carrier
- 기준면: component side
- 원점: 좌상단 첫 usable hole 중심
- 열: 왼쪽에서 오른쪽으로 `C1...C55`
- 행: 위에서 아래로 `R1...R37`

기판의 component-side 인쇄 열 번호는 사진에서 왼쪽부터 `55...01`로 보인다. 따라서 이 문서의
좌표 `C`와 인쇄 번호 `P`의 관계는 `P = 56 - C`다. 예를 들어 `C6`은 인쇄 `50`, `C33`은
인쇄 `23`, `C52`는 인쇄 `04`다.

이 지도는 2026-08-14 정면 사진 네 장의 실제 solder joint를 읽고 Onshape Top View
`assets/photos/perfboard/image.png`의 정투영 부품 외곽과 교차 확인한 결과다. Onshape는 body,
USB와 antenna 간섭 판단에 우선 사용하고, 실제 납땜 홀 점유는 실물 사진에 우선권을 둔다.
Onshape assembly가 모든 header를 hole grid에 구속했다는 치수 증거는 아직 없으므로 **납땜
전에는 사용자가 각 header의 첫 홀과 마지막 홀을 실물에서 한 번 더 세어야 한다.** 좌표가
맞아도 전기적 net 연결이나 module pinout까지 증명하지는 않는다.

## 고정 header 점유 홀

| 고정 블록 | 사진 기반 점유 홀 | 핀 수 | Component-side 인쇄 번호 | 상태 |
| --- | --- | ---: | --- | --- |
| NUCLEO upper socket | `C6...C24`, `R4...R5` | `2 x 19` | `50...32` | 이동/제거 금지 |
| NUCLEO lower socket | `C6...C24`, `R28...R29` | `2 x 19` | `50...32` | 이동/제거 금지 |
| GY-BNO085 socket | `C33`, `R1...R10` | `1 x 10` | `23` | 이동/제거 금지 |
| ESP32-S3 upper socket | `C31...C52`, `R26` | `1 x 22` | `25...04` | 이동/제거 금지 |
| ESP32-S3 lower socket | `C31...C52`, `R35` | `1 x 22` | `25...04` | 이동/제거 금지 |

2026-08-15 VeroRoute 실배치 중 사용자가 실제 BNO085 socket pin을 다시 세어 `10 pin`으로
확인했다. 따라서 사진/Onshape 추정으로 기록했던 `R1...R11`, `1 x 11`은 폐기하고
`C33`, `R1...R10`, `1 x 10`을 현재 실물 기준으로 사용한다.

Solder-side 사진은 좌우 반전되어 보이므로 위 component-side 열 번호를 그대로 눈으로 옮기지
않는다. 납땜면을 볼 때는 물리적으로 같은 홀을 관통해 확인한다.

## 보수적 module/service 금지영역

아래 영역은 실제 module body와 수직 탈착, USB plug 접근, 손가락/공구 여유를 사진에서
보수적으로 합친 **새 부품 배치 금지 후보**다. 고정 header 자체보다 넓으며 정밀 기구공차가
확정된 제조 좌표가 아니다.

| 대상 | 새 부품 배치 금지 후보 | 이유 |
| --- | --- | --- |
| NUCLEO | `C1...C28`, `R1...R32` | Onshape body 외곽에 ST-LINK/USB 접근과 수직 탈착 여유를 추가 |
| GY-BNO085 | `C25...C35`, `R1...R13` | Onshape sensor body 외곽에 수직 탈착/배선 접근 여유를 추가 |
| ESP32-S3 | `C26...C55`, `R23...R37` | Onshape body 외곽에 두 USB connector와 수직 탈착 여유를 추가 |
| ESP32 antenna 보수적 keep-out | `C44...C55`, `R21...R37` | Onshape antenna 방향 기준 새 부품, 새 copper bus와 wire bundle 금지 후보 |

ESP32 antenna 아래에는 이미 perfboard pad와 기존 socket 일부가 존재한다. 따라서 이 표는 RF
적합성을 증명하지 않으며, 최소한 **추가 금속·배선으로 상황을 더 악화시키지 않기 위한 경계**다.
Wi-Fi/BLE 링크 품질은 조립 후 별도 측정해야 한다.

## 현재 사용 가능한 큰 영역

고정 module/service 경계를 제외하면 우측 상단의 `C36...C55`, `R1...R20`이 가장 큰 연속
후보 영역이다. 단, 우측 mounting hole과 board edge, offboard connector wire exit를 위해
`C53...C55`와 최상단 일부는 바로 채우지 않는다.

```text
Component side / not to scale

 C1                         C30 C34 C38                    C55
 R1  +-------------------------+---+-------------------------+
     | NUCLEO service envelope |BNO| upper-right open area   |
     |                         |   | connector reserve       |
     |                         |   | R9~R12 dry candidate    |
 R20 |                         |   | rework/spare            |
     +-------------------------+---+-------------------------+
 R23 |                         | ESP32 service/antenna zone |
     |                         |                            |
 R37 +-------------------------+----------------------------+
```

## R9~R12 10 kΩ 드라이 배치 후보 A

목적은 STM32가 reset/boot/disconnected 상태일 때 MDD10A의 네 logic input이 뜨지 않도록 각
signal node를 logic GND로 당기는 것이다. 저항은 신호에 직렬로 넣지 않고 signal-to-GND
shunt로 둔다.

| Ref | Signal | 위쪽 signal lead | 아래쪽 GND lead | Lead 간격 |
| --- | --- | --- | --- | ---: |
| R9 | `PC8 / DIR1` | `C38,R5` | `C38,R9` | `4 pitch = 10.16 mm` |
| R10 | `PB6 / PWM1` | `C41,R5` | `C41,R9` | `4 pitch = 10.16 mm` |
| R11 | `PC9 / DIR2` | `C44,R5` | `C44,R9` | `4 pitch = 10.16 mm` |
| R12 | `PB7 / PWM2` | `C47,R5` | `C47,R9` | `4 pitch = 10.16 mm` |

- `C37...C49`, `R1...R3`: actual MDD10A logic connector footprint 확인 전 예약
- `C38...C47`, `R9`: 네 저항의 logic-GND 공통점 후보
- `R10` 아래: signal label과 probe 접근 여유
- resistor 간 2개 빈 열을 남겨 probe short와 재작업 위험을 줄임
- 이 배치는 실제 10 kΩ resistor body/lead 길이와 connector wire exit를 확인하기 전까지
  `candidate A`다.

## 오늘 드라이 배치 절차와 PASS 기준

전원은 모두 분리한 상태에서만 진행한다.

1. NUCLEO, ESP32와 BNO085를 현재 socket에 꽂아 body/service 경계를 확인한다.
2. `C38/C41/C44/C47`, `R5...R9` 위치에 저항 네 개를 **가볍게 올려보기만** 한다.
3. lead를 절단하거나 예각으로 굽히거나 납땜하지 않는다.
4. MDD logic connector가 들어갈 `C37...C49`, `R1...R3`을 가리지 않는지 확인한다.
5. NUCLEO/BNO085/ESP32를 수직으로 빼고 다시 꽂을 수 있는지 확인한다.
6. 위에서 촬영해 `C1/R1` 방향과 네 저항이 동시에 보이게 남긴다.

PASS:

- 네 resistor가 서로 닿지 않는다.
- BNO085 탈착과 우측 상단 wire exit를 막지 않는다.
- ESP32 antenna 보수적 keep-out을 침범하지 않는다.
- MDD connector 예약 영역과 최소 20% rework/spare area가 남는다.

STOP:

- resistor body가 실제 lead 간격 `10.16 mm`에 무리하게 맞아 lead가 body 근처에서 꺾인다.
- connector 또는 module 탈착 경로와 겹친다.
- 좌표를 세는 중 header 끝점이 위 표와 한 홀이라도 다르게 확인된다.

STOP이면 사진과 실제 첫/마지막 홀 번호를 다시 기록하고 좌표를 수정한다. 이 단계의 PASS는
영구 납땜, continuity, USB-only power 또는 motor power 시험 승인이 아니다.
