# RevB 회로도 기능 배치 학습 및 후속 재작업 계획

## 결정과 현재 상태

2026-08-13의 RevB-WIP 회로도는 현재 MVP 진행에 사용할 **전기적 검토 기준본**으로
동결한다.

```text
Functional topology: REVIEWED
KiCad ERC: 0 errors / 0 warnings
Component text rule: Reference 50 mil / Value 40 mil
Netlist: 120 Ref/Pin/Net tuples preserved
Sense-block overlap removal: PASS
Portfolio-level functional layout: DEFERRED FOR LEARNING
Manufacturing/perfboard release: NOT APPROVED
```

현재 배치는 심볼·필드·라벨 겹침을 제거하고 전기 연결을 보존하는 데 성공했다. 그러나 A4
PDF에서 `전원 -> E-stop control/re-enable -> K1 motor rail -> S0-B/PC7 sense`의 기능 흐름과
관련 주석의 소속이 한눈에 읽히는 수준까지는 도달하지 않았다.

따라서 좌표를 다시 즉흥 수정하지 않는다. 회로도 독해와 기능 블록 배치 원칙을 학습한 뒤
별도 시각 개선 작업으로 재개한다. 이 보류는 permanent wiring, power/back-power 정책과
motor-disconnected E-stop 시험 준비를 막지 않는다.

## 현재 기준 증거

- Schematic SHA-256: `52BFD10D8ED0951D046D9D030B90505DE4F2E7869CBCBC5CA8324BB1B8CC8878`
- User PDF SHA-256: `10E3FC907DD63B9F754B673813435BE7C490F3ABC9F183BB2CFB4E50B6C23872`
- PDF: A4 landscape, 1 page, drawing sheet/title block not clipped
- ERC: `0 errors / 0 warnings`
- 48 component symbols: all Reference `50 mil`, Value `40 mil`
- Final sense block:
  - `R13`: `AUX_5V -> S0B_LED_FEED`
  - `J15`: `S0B_LED_FEED -> S0B_TO_OPTO_ANODE`
  - `U1`: input/GND -> `ESTOP_SENSE`/GND
  - `R14`: `STM32_3V3 -> ESTOP_SENSE`
  - `J18`: `STM32_3V3 / ESTOP_SENSE / GND`

PDF 시각 검토에서 직접 겹침은 없었다. 다만 K1/K2 설명문과 대상 심볼의 시각적 결속,
기능 흐름의 좌우 방향성과 기능 블록 간 경계는 추가 개선 대상으로 남긴다.

## 재작업 전 학습 항목

다음 항목을 실제 RevB 회로에 적용해 설명할 수 있을 때 재배치를 재개한다.

1. **전원과 신호의 기본 방향**
   - 전원은 위에서 아래, 기능 흐름은 왼쪽에서 오른쪽으로 읽히게 하는 이유
2. **기능 블록 구분**
   - main motor power, E-stop control/re-enable, S0-B sense, MCU interface를 분리하는 방법
3. **Net label과 직접 wire의 역할**
   - 긴 교차 배선은 label로 줄이되 신호 인과관계가 끊겨 보이지 않게 하는 기준
4. **Reference/Value/주석 계층**
   - 부품 식별 정보, 설계 상태, 계산/선정 주석을 서로 다른 수준으로 배치하는 방법
5. **커넥터 경계**
   - on-board circuit과 off-board harness가 어디에서 나뉘는지 드러내는 방법
6. **전원 심볼과 return path**
   - LOGIC_GND와 PWR_GND의 역할을 읽을 수 있게 하면서 motor current path를 오해시키지 않는 방법
7. **검증을 보존하는 재배치**
   - Ref/Pin/Net tuple, no-connect, ERC와 PDF를 전후 비교하는 방법

## 학습 후 재작업 순서

```text
현재 RevB-WIP source/PDF/hash 보존
-> 기능 블록과 signal-flow 초안 작성
-> 새 작업 복사본에서만 전체 배치 모의 적용
-> A4 전체와 기능 블록 확대 PDF 검토
-> Ref/Pin/Net 전후 비교
-> ERC 0/0
-> 원본 반영 여부 결정
```

재작업에서는 먼저 좌표를 정하지 않는다. 각 기능 블록의 입력, 출력, 전원, return,
off-board connector와 관련 설명을 표로 만든 뒤 블록 사각형과 흐름을 정하고 마지막에 mil
좌표를 확정한다.

## 후속 레이아웃 PASS 기준

- A4 한 페이지에서 다음 네 블록이 5초 안에 식별된다.
  - main motor power
  - E-stop control/re-enable
  - K1 motor rail boundary
  - S0-B/PC7 sense
- K1/K2/S0/S2 설명문이 해당 심볼과 인접하고 다른 블록의 설명으로 오해되지 않는다.
- 정상 동작과 E-stop 작동 시 에너지 및 신호 흐름을 도면만 보고 설명할 수 있다.
- 모든 Reference/Value와 net label이 겹치지 않는다.
- 48개 component와 120개 Ref/Pin/Net tuple이 보존된다.
- ERC가 `0 errors / 0 warnings`다.
- 이 결과도 manufacturing release나 산업 안전 인증으로 확대 주장하지 않는다.

## 현재 프로젝트 진행과의 관계

지금부터는 이 시각 개선을 기다리지 않고 다음 안전 Gate 준비를 진행한다.

```text
actual perfboard/보유 부품 사진과 치수 수집
-> received-part/occupied-hole map
-> 1:1 dry placement
-> permanent pull-down wiring and de-energized continuity
-> board power/back-power policy and measurement
-> motor-disconnected T-ESTOP-001~005
```

새 부품 납땜, LiPo/MDD10A motor power 연결과 실제 motor 시험은 각 선행 Gate가 통과하기
전까지 승인하지 않는다.
