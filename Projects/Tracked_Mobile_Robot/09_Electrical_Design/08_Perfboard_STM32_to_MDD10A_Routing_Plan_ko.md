# STM32-MDD10A 만능기판 배선 경로 계획

## 상태

- 상태: `VEROROUTE DIGITAL CONNECTIVITY PASS — NET 1~5 CLOSED`
- 대상 파일: `VeroRoute/Tracked_Mobile_Robot_Perfboard_RevB_WIP.vrt`
- 좌표 기준: component-side 정본 좌표 `C1...C55`, `R1...R37`
- VeroRoute 작업 레이어: `Bottom`
- 물리 구현: 절연 점퍼선과 인접 한 홀 solder bridge만 사용

이 문서는 KiCad RevB-WIP의 MDD10A logic net을 실제 만능기판 홀 좌표로 옮기기 위한
작업 계획이다. Motor current는 이 기판을 통과하지 않는다.

## 확인된 Net과 고정 핀

| Net | 기능 | STM32 고정 핀 | 저항 signal lead | J5 |
| ---: | --- | --- | --- | --- |
| 1 | `PC8 / DIR1` | `C6,R4` | R9 `C38,R5` | J5-1 |
| 2 | `PB6 / PWM1` | `C14,R5` | R10 `C41,R5` | J5-2 |
| 3 | `PC9 / DIR2` | `C6,R5` | R11 `C44,R5` | J5-3 |
| 4 | `PB7 / PWM2` | `C16,R29` | R12 `C47,R5` | J5-4 |
| 5 | logic GND | `C15,R4` | R9~R12 GND bus `R9` | J5-5 |

J5와 R9~R12 사이의 우측 상단 local routing은 VeroRoute에서 서로 다른 Net 색으로 분리돼
있고 빨간 floating Wire가 없는 상태까지 확인했다. `Broken Nets 1...5`는 STM32 측이 아직
연결되지 않았기 때문에 예상되는 상태다.

## VeroRoute 배치 규칙

VeroRoute의 일반 부품 핀은 홀을 완전히 점유하므로 Wire 끝을 같은 홀에 놓을 수 없다.

```text
component pin -- one-pitch painted track -- empty-hole Wire endpoint
```

- Wire 끝끼리의 공유는 `Allow 2 wires to share a hole`을 사용한다.
- 절연 Wire의 교차는 `Allow 2 wires to cross / overlay`를 사용한다.
- 서로 다른 Net의 교차점에는 solder bridge나 junction을 만들지 않는다.
- 장거리 연결은 `Paint Track`으로 이어 붙이지 않고 절연 Wire로 구현한다.
- `P`는 pin Net 지정이고, `Space`는 track/solder bridge 입력이다.

## 전체 STM32 측 경로

아래 경로는 고정 header와 BNO085/ESP32 socket을 피하고 중앙 `R14...R18`을 순차적인
배선 통로로 사용하는 후보 A다. 각 Wire의 양 끝은 빈 홀이다.

### Net 1 — PC8 / DIR1

1. solder bridge: `C6,R4` ↔ `C6,R3`
2. Wire: `C6,R3` ↔ `C4,R3`
3. Wire: `C4,R3` ↔ `C4,R14`
4. Wire: `C4,R14` ↔ `C37,R14`
5. Wire: `C37,R14` ↔ `C37,R5`
6. solder bridge: `C37,R5` ↔ R9 `C38,R5`

### Net 2 — PB6 / PWM1

1. solder bridge: `C14,R5` ↔ `C14,R6`
2. Wire: `C14,R6` ↔ `C14,R15`
3. Wire: `C14,R15` ↔ `C40,R15`
4. Wire: `C40,R15` ↔ `C40,R5`
5. solder bridge: `C40,R5` ↔ R10 `C41,R5`

### Net 3 — PC9 / DIR2

1. solder bridge: `C6,R5` ↔ `C5,R5`
2. Wire: `C5,R5` ↔ `C5,R16`
3. Wire: `C5,R16` ↔ `C43,R16`
4. Wire: `C43,R16` ↔ `C43,R5`
5. solder bridge: `C43,R5` ↔ R11 `C44,R5`

### Net 5 — logic GND

1. solder bridge: `C15,R4` ↔ `C15,R3`
2. Wire: `C15,R3` ↔ `C15,R2`
3. Wire: `C15,R2` ↔ `C2,R2`
4. Wire: `C2,R2` ↔ `C2,R17`
5. Wire: `C2,R17` ↔ `C38,R17`
6. Wire: `C38,R17` ↔ `C38,R10`
7. solder bridge: `C38,R10` ↔ GND bus `C38,R9`

### Net 4 — PB7 / PWM2

1. solder bridge: `C16,R29` ↔ `C16,R30`
2. Wire: `C16,R30` ↔ `C28,R30`
3. Wire: `C28,R30` ↔ `C28,R18`
4. Wire: `C28,R18` ↔ `C46,R18`
5. Wire: `C46,R18` ↔ `C46,R5`
6. solder bridge: `C46,R5` ↔ R12 `C47,R5`

Net 2~4의 우측 수직 Wire는 `R9`의 GND bus를 절연 상태로 교차한다. 이는 연결점이 아니다.
실물에서는 피복 손상과 납땜 돌기 접촉이 없도록 Wire를 띄우거나 절연 슬리브를 유지한다.

## 입력 순서와 PASS 기준

입력 순서는 `Net 1 → Net 2 → Net 3 → Net 5 → Net 4`로 고정한다. 한 Net마다 다음을
확인한 뒤 다음 Net으로 이동한다.

- 모든 Wire가 검정 또는 해당 Net 색이며 빨간 floating 상태가 아니다.
- 해당 Net 번호가 `Broken Nets`에서 사라진다.
- 다른 Net의 색이 합쳐지지 않는다.
- component pin에는 Wire 끝이 아니라 한 홀 bridge만 연결된다.
- 좌표가 한 홀이라도 어긋나면 다음 Net을 추가하지 않고 수정한다.

## 2026-08-15 입력 결과

- 계획 순서 `Net 1 → Net 2 → Net 3 → Net 5 → Net 4` 입력 완료
- VeroRoute 화면의 `Broken Nets` 목록이 비어 있음
- 빨간 floating Wire와 빨간 broken-net 안내선이 없음
- 저장 파일: `VeroRoute/Tracked_Mobile_Robot_Perfboard_RevB_WIP.vrt`
- 저장 파일 크기: `99,971 bytes`
- SHA-256: `52F03CC17CAD1A832D94D2BE5FD2FB4D27FC879ECF83E3A2A57C35FC9D969630`

따라서 VeroRoute 내부의 디지털 connectivity는 PASS다. 이는 실제 납땜이나 전기적 검증
PASS를 의미하지 않는다. 납땜 전에는 KiCad net-to-hole 독립 대조, solder-side mirror 출력과
실물 1:1 dry placement가 남는다.
