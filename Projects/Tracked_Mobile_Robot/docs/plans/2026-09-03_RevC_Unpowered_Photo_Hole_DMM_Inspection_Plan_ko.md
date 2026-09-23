# 2026-09-03 RevC 부분 실장 무전원 검사 계획

> **2026-09-05 실행 종료 / 역사 문서:** 이 runbook의 실행은 종료됐다. 실제 후속 결과와
> evidence boundary는 [`2026-09-05 progress`](../progress/2026-09-05_progress.md), 남은 Gate는
> [`2026-09-05 remaining bench gates`](2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md)를 따른다.
> 아래 K2 좌표표는 TX2 bottom-view를 component-side에 직접 적용한 오류가 있는 frozen 기록이므로
> 실물 핀 식별의 정본으로 사용하지 않는다.

## 상태와 오늘의 종료선

- 상태: `EXECUTION CLOSED 2026-09-05 / PARTIAL EVIDENCE` — 2026-09-03 rail 0 V와 U1
  `V-02~V-03` PASS 뒤 후속 배선 및 control-only powered subset까지 수행했다. 세부 결과와
  미완료 Gate는 2026-09-05 progress로 이관했다.
- 예상 소요: 순수 작업 `1.5~2시간`, 재확인 버퍼 포함 최대 `2.5시간`
- 대상: 2026-09-01에 작업한 RevC E-stop 부분 실장 구간
- 오늘의 종료선: 무전원 사진, 정확한 홀 재확인, 로컬 도통/저항/다이오드 및 절연 검사를
  기록하고 `PASS`, `FAIL/HOLD` 또는 `NOT RUN`으로 판정한다.
- 이 문서는 오늘 작업 중 순서와 판정 기준을 제공하는 실행 문서다. 실제 결과는 측정 후 별도
  progress 또는 verification report에 기록한다.

부분 실장 구간이 이 계획을 통과해도 전체 `T-ESTOP-002`, 6P 방수 하네스, S0/F2/K1 통합,
conditioned PC7 동작, powered pickup/dropout, rail-off 또는 motor 시험이 통과한 것은 아니다.

## 기준 자료

1. [`Tracked_Mobile_Robot_Perfboard_RevC_Estop_FINAL.vrt`](../../09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_FINAL.vrt)
2. [`2026-08-31 component-side reference`](../../09_Electrical_Design/VeroRoute/exports/2026-08-31_Tracked_Mobile_Robot_Perfboard_RevC_Estop_component_side_reference.pdf)
3. [`2026-08-31 solder-side mirrored`](../../09_Electrical_Design/VeroRoute/exports/2026-08-31_Tracked_Mobile_Robot_Perfboard_RevC_Estop_solder_side_mirrored.pdf)
4. [`2026-09-01 progress`](../progress/2026-09-01_progress.md)
5. [`Physical E-stop verification plan`](../verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)

좌표와 Net 판정은 FINAL VRT를 따른다. component-side reference는 실물 부품면과 같은 방향의
unflipped 배치도이므로 실제 component-side 사진을 다시 수평 반전하지 않는다. 이 만능기판의
부품면 가장자리 인쇄 숫자는 프로젝트 열 번호와 반대로 보인다. 인쇄 숫자를 `P`라 하면 프로젝트
열은 `C(56-P)`로 환산하고, pin 번호·상대 배치·Net을 함께 확인한다. solder-side를 볼 때만
solder-side mirrored PDF를 사용한다.

## 포함 범위

- R14, U1, K2, D2, JESTOP의 실장 위치와 방향
- `R14 P1 -> C15,R5 / U1.4` 경로
- `R14 P2 -> C13,R28` 경로
- 현재 실장된 E-stop 로컬 Net의 도통과 서로 다른 Net 사이 gross-short 검사
- 사진과 DMM 수치 보존

## 제외 범위

- 전원 인가, K2/K1 동작, motor 또는 LiPo 연결
- S0/F2/K1과 6P 방수 하네스의 전체 end-to-end 검증
- VO617A의 정격 절연 시험이나 D2의 독립 항복전압 시험
- PC7 LOW/HIGH runtime, E-stop rail-off 및 actual-stop 시험
- 남은 배선이나 재작업의 즉석 진행

이 계획에서 이상이 나오면 같은 자리에서 원인을 기록하고 `FAIL/HOLD`로 종료한다. 재납땜이나
배선 변경은 측정 결과와 변경 대상을 먼저 확정한 뒤 별도 작업으로 수행한다.

## 실행 순서

### Gate 0 — 완전 무전원 확인

1. LiPo, motor, 모든 USB, XL4015/buck 입력과 외부 하네스를 분리한다.
2. 가능하면 NUCLEO와 ESP32를 소켓에서 빼서 외부 전원·보호회로의 우회 경로를 제거한다.
3. DMM을 **DC 전압 모드**로 놓고 board GND 기준으로 접근 가능한 `5V_LOGIC`,
   `STM32_3V3`, `ESTOP_CONTROL_PERMISSION`, `K2_COIL_P`, `K1_COIL_P`를 측정한다.
4. 모든 측정점이 `0 V`인 경우에만 다음 단계로 이동한다.
5. DMM을 continuity/저항 모드로 바꾼 뒤 probe 두 개를 맞대어 buzzer 동작과 lead 저항 기준값을
   기록한다.

하나라도 `0 V`가 아니면 저항/continuity/diode 측정을 시작하지 않는다. 전원을 임의로
단락시켜 방전하지 말고 연결 상태를 다시 확인한다.

### Gate 1 — 원본 사진과 육안 검사

다음 네 장을 수직에 가깝게, 초점이 맞고 홀 좌표를 셀 수 있게 촬영한다.

| ID | 사진 | 권장 파일명 |
| --- | --- | --- |
| P-01 | component-side 전체 | `assets/photos/perfboard/2026-09-03_01_revc_component_side_unpowered.jpg` |
| P-02 | E-stop 부분 component-side 확대 | `assets/photos/perfboard/2026-09-03_02_revc_estop_component_closeup.jpg` |
| P-03 | solder-side 전체 | `assets/photos/perfboard/2026-09-03_03_revc_solder_side_unpowered.jpg` |
| P-04 | E-stop 부분 solder-side 확대 | `assets/photos/perfboard/2026-09-03_04_revc_estop_solder_closeup.jpg` |

사진에는 가능하면 board의 행/열 표식, U1 pin-1 corner dot, JESTOP pin 1 방향이 함께 보이게 한다.
양면에서 아래 항목을 검사한다.

- 납이 pad와 lead 양쪽을 젖혔는지
- dull/cold joint, 움직이는 lead, 납땜 누락이 없는지
- 인접 pad bridge, solder whisker, 잘린 lead 조각이 없는지
- 피복이 과도하게 벗겨졌거나 다른 도체에 닿는 strand가 없는지
- Wire가 의도한 홀에서 시작하고 끝나는지

### Gate 2 — exact-hole recount

`왼쪽/오른쪽` 표현만으로 PASS시키지 않는다. FINAL 기준으로 아래 좌표를 사진과 실물에서
각각 다시 센다.

> **K2 ERRATUM — 아래 K2 행은 비정본:** Panasonic `TX2-12V`의 pin diagram은 bottom-view이고,
> 이를 component-side에 그대로 적용해 K2의 R19/R21 행을 반대로 적었다. 실물 원형 dimple=pin 1
> 기준 실제 pin 1은 `C37,R21`, pin 12는 `C37,R19`다. Corrected Net은
> `C37,R21=K2_COIL_P`, `C37,R19=GND`이며 3/4/5도 R21, 10/9/8도 R19 행이다. 전체 corrected
> 표와 post-rework 재검사 절차는 2026-09-05 progress/remaining-gates 문서를 따른다. 아래 표는
> 당시 frozen FINAL 해석을 보존하기 위해 삭제하지 않았으며 K2 배선·측정 지시로 사용하지 않는다.
> 같은 이유로 아래 Gate 3의 `C-03/C-05~C-07`과 Gate 4의 `V-06~V-10`에 적힌 K2 pin 번호도
> 비정본이다. 해당 항목을 재측정할 때는 새 remaining-gates 계획의 corrected 좌표를 사용한다.

| 부품 | Pin | FINAL 좌표 | Net / 기능 | 관찰 | 판정 |
| --- | ---: | --- | --- | --- | --- |
| R14 | 1 | `C29,R19` | `ESTOP_SENSE / PC7` |  | `NOT RUN` |
| R14 | 2 | `C33,R19` | `STM32_3V3` |  | `NOT RUN` |
| U1 | 1 | `C29,R23` | `S0B_TO_OPTO_ANODE` |  | `NOT RUN` |
| U1 | 2 | `C30,R23` | GND |  | `NOT RUN` |
| U1 | 3 | `C30,R20` | GND |  | `NOT RUN` |
| U1 | 4 | `C29,R20` | `ESTOP_SENSE / PC7` |  | `NOT RUN` |
| K2 | 1 | `C37,R19` | `K2_COIL_P` |  | `NOT RUN` |
| K2 | 3 | `C39,R19` | NC1, no board Wire |  | `NOT RUN` |
| K2 | 4 | `C40,R19` | `ESTOP_CONTROL_PERMISSION` |  | `NOT RUN` |
| K2 | 5 | `C41,R19` | `K2_COIL_P` |  | `NOT RUN` |
| K2 | 12 | `C37,R21` | GND |  | `NOT RUN` |
| K2 | 10 | `C39,R21` | NC2, no board Wire |  | `NOT RUN` |
| K2 | 9 | `C40,R21` | `ESTOP_CONTROL_PERMISSION` |  | `NOT RUN` |
| K2 | 8 | `C41,R21` | `K1_COIL_P` |  | `NOT RUN` |
| D2 | 1 | `C35,R23` | GND |  | `NOT RUN` |
| D2 | 2 | `C39,R23` | `K2_COIL_P` |  | `NOT RUN` |
| JESTOP | 1 | `C55,R13` | external `ESTOP_CTRL_FUSED` |  | `NOT RUN` |
| JESTOP | 2 | `C55,R14` | `ESTOP_CONTROL_PERMISSION` |  | `NOT RUN` |
| JESTOP | 3 | `C55,R15` | `S0B_LED_FEED` |  | `NOT RUN` |
| JESTOP | 4 | `C55,R16` | `S0B_TO_OPTO_ANODE` |  | `NOT RUN` |
| JESTOP | 5 | `C55,R17` | `ESTOP_CONTROL_PERMISSION` |  | `NOT RUN` |
| JESTOP | 6 | `C55,R18` | `K2_COIL_P` |  | `NOT RUN` |

U1의 실제 component-side 핀 배열은 `좌상 4 / 우상 3 / 좌하 1 / 우하 2`다. 작은 원형 corner
dot/dimple이 pin 1 식별표시이며, 2026-09-03 근접사진의 **좌하단** dimple은 FINAL과 일치한다.

### Gate 3 — 의도된 board-Net 도통

DMM continuity 또는 낮은 저항 범위를 사용한다. 각 그룹 안의 endpoint는 도통되어야 한다.
단, 이 Gate는 해당 그룹의 모든 Wire와 joint가 실제로 납땜된 뒤에만 실행한다. 명시적으로 아직
조립하지 않은 그룹의 open은 `FAIL`이 아니라 `NOT RUN / ASSEMBLY PENDING`으로 기록하고, FINAL에
따라 그 Net을 완성한 뒤 다시 측정한다.

| ID | 같은 Net으로 도통되어야 하는 endpoint | 기대 |
| --- | --- | --- |
| C-01 | `C15,R5` ↔ R14.1 `C29,R19` ↔ U1.4 `C29,R20` | lead 기준에 가까운 낮은 저항 / beep |
| C-02 | `C13,R28` ↔ R14.2 `C33,R19` | lead 기준에 가까운 낮은 저항 / beep |
| C-03 | U1.2 ↔ U1.3 ↔ K2.12 ↔ D2.1 ↔ board GND | lead 기준에 가까운 낮은 저항 / beep |
| C-04 | JESTOP.4 ↔ U1.1 | lead 기준에 가까운 낮은 저항 / beep |
| C-05 | JESTOP.2 ↔ JESTOP.5 ↔ K2.4 ↔ K2.9 | lead 기준에 가까운 낮은 저항 / beep |
| C-06 | JESTOP.6 ↔ K2.1 ↔ K2.5 ↔ D2.2 | lead 기준에 가까운 낮은 저항 / beep |
| C-07 | K2.8 ↔ JK1COIL.1 | JK1COIL이 실장된 경우 낮은 저항 / beep |
| C-08 | JESTOP.3 ↔ R13의 JESTOP 측 endpoint | R13 경로가 실장된 경우 낮은 저항 / beep |

endpoint 한 쌍만 재지 말고 각 그룹의 첫 endpoint를 기준으로 나머지를 모두 확인한다.

### Gate 4 — 부품과 relay 상태 확인

| ID | FROM | TO | 모드 | 무전원 기대값 |
| --- | --- | --- | --- | --- |
| V-01 | R14.1 | R14.2 | Ω | 약 `10 kΩ`; 선별값 기준 약 `9.97 kΩ` |
| V-02 | U1.1 red | U1.2 black | diode | 선별 당시 약 `0.955 V`; 실장 회로 영향은 별도 기록 |
| V-03 | U1.1 black | U1.2 red | diode | reverse open이 기본 기대; 실장 회로 영향은 별도 기록 |
| V-04 | U1.1 | U1.4 | Ω/continuity | near-zero short 또는 beep가 없어야 함 |
| V-05 | U1.4 | GND | Ω/continuity | near-zero short 또는 beep가 없어야 함 |
| V-06 | K2.1 | K2.12 | Ω | 약 `1.03 kΩ` (`1.028 kΩ ±10%` 범위 참고) |
| V-07 | K2.3 | K2.4 | continuity | 무여자 NC이므로 closed / beep |
| V-08 | K2.4 | K2.5 | continuity | 무여자 NO이므로 open / no beep |
| V-09 | K2.10 | K2.9 | continuity | 무여자 NC이므로 closed / beep |
| V-10 | K2.9 | K2.8 | continuity | 무여자 NO이므로 open / no beep |

오판 방지 기준:

- R14 양단은 `10 kΩ`이므로 continuity buzzer가 울려야 하는 구간이 아니다.
- U1.2와 U1.3은 이 board에서 의도적으로 GND에 함께 연결되어 있다. 둘 사이 도통은 정상이다.
- K2.1↔K2.5와 K2.4↔K2.9는 의도된 board tie다.
- K2 무여자 상태에서 3↔4와 10↔9는 relay 내부 NC 접점 때문에 도통되는 것이 정상이다.
  따라서 K2.3과 K2.10은 VeroRoute상 별도 Wire가 없어도 관련 NC 경로에서 buzzer가 울릴 수 있다.
- D2는 K2 coil과 병렬이다. 실장 후 D2 양단 저항이 약 `1.03 kΩ`으로 보일 수 있으며 이것은
  곧 D2 short를 뜻하지 않는다. D2 독립 항복 시험은 이 계획에서 하지 않는다.

### Gate 5 — 서로 다른 Net 절연/gross-short 확인

아래는 `무조건 OL`을 요구하는 정격 절연 시험이 아니다. 부품을 통한 유한 저항은 실제 수치로
기록하고, **near-zero 저항 또는 buzzer로 나타나는 비의도 short**가 없는지 확인한다.

| ID | FROM | TO | 기대 |
| --- | --- | --- | --- |
| I-01 | `STM32_3V3` | GND | near-zero short / beep 없음 |
| I-02 | `ESTOP_CONTROL_PERMISSION` | `K2_COIL_P` | K2 무여자에서 near-zero short / beep 없음 |
| I-03 | JESTOP.1 | JESTOP.2 | 반드시 open / no beep |
| I-04 | JESTOP.1 | JESTOP.3~6 각각 | 외부 하네스 분리 상태에서 open / no beep |
| I-05 | U1.1 | U1.4 | near-zero short / beep 없음 |
| I-06 | U1.4 | GND | near-zero short / beep 없음 |
| I-07 | 각 신규 solder joint | 인접한 서로 다른 Net pad | near-zero short / beep 없음 |

JESTOP.1은 외부 `F2 OUT`이 나중에 직접 landing하는 singleton 경계점이므로 board 내부에서
연결이 없는 것이 정상이다. JESTOP.1↔JESTOP.2를 jumper하면 S0-A NC를 우회하므로 즉시
`FAIL/HOLD`다.

## 즉시 중지 조건

다음 중 하나라도 발생하면 전원을 넣지 않고 `FAIL/HOLD`로 기록한다.

- 전원·USB·LiPo·motor가 연결되어 있거나 rail이 `0 V`가 아님
- hole 좌표 또는 U1 방향이 FINAL과 다름
- 납 bridge, loose strand, 움직이는 joint 또는 타버린 부품을 발견함
- 의도된 도통 경로가 open임
- 서로 다른 Net 사이에서 예상하지 않은 near-zero 저항/beep가 남음
- R14가 약 `0 Ω`, open 또는 `10 kΩ`에서 크게 벗어남
- K2 coil이 약 `0 Ω`/open이거나 무여자 접점 상태가 기대와 다름
- U1.1↔U1.4 또는 U1.4↔GND에 gross short가 있음
- JESTOP.1↔JESTOP.2가 도통됨

## 측정 기록표

측정할 때 아래 표를 복사해 actual progress/report에 채운다. 수치는 `beep`만 쓰지 말고 가능하면
Ω 또는 diode 전압도 함께 적는다.

| ID | FROM | TO | 모드 | 기대 | 측정값 | 판정 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G0-01 | DMM lead | DMM lead | Ω/continuity | baseline |  | `NOT RUN` |  |
|  |  |  |  |  |  | `NOT RUN` |  |

### 재작업/편차 기록

| 시간 | 발견 항목 | 위치 | 조치 여부 | 재검사 ID | 결과 |
| --- | --- | --- | --- | --- | --- |
|  |  |  | 미실시 |  | `NOT RUN` |

## 완료 판정과 다음 단계

오늘 범위의 `PASS` 조건은 다음과 같다.

1. Gate 0~5가 모두 실행되고 수치가 기록되었다.
2. 네 장의 원본 사진과 exact-hole recount가 보존되었다.
3. 의도된 모든 local path가 도통되고 비의도 low-resistance short가 없다.
4. 이상 또는 재작업 항목이 미해결로 남지 않았다.
5. 결과를 날짜별 progress 또는 verification report에 옮기고 이 문서 상태를 갱신했다.

PASS 후의 다음 작업 후보는 `VH-30J/WX-03B` 확인과 spare terminal을 이용한 6P 18 AWG
first-article crimp 검증이다. K2/K1 powered test와 motor energy는 별도 Physical E-stop Gate
전까지 계속 금지한다.

## 2026-09-05 실행 종료 기록

- 실행 결과 정본: [`2026-09-05 progress`](../progress/2026-09-05_progress.md)
- 다음 실행 정본: [`2026-09-05 Physical E-stop remaining bench gates`](2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md)
- K2 bottom-view/polarity as-built correction 뒤 12.24 V control-only K2/K1 nominal subset은
  PASS했다. MDD10A B+는 K1-87에서 분리·절연했으므로 downstream rail/motor-energy PASS가 아니다.
- S0-B `JESTOP.3 <-> JESTOP.4`의 released/pressed-latched/manual-release contact truth table은
  무전원 PASS했다.
- Explicit sense-wire removal, S0-A/S0-B end-to-end independence와 `T-ESTOP-003` powered
  VO617A-3/PC7 sense는 OPEN이다.
- 세션 사진과 측정은 operator-reported/session-attached 경계이며 원본 사진·hash·raw DMM log가
  repository에 보존되지 않았다. 따라서 이 문서의 빈 표나 `NOT RUN`을 추정값으로 채우지 않는다.
- 이 historical runbook을 다시 실행하지 않는다. 다음 세션은 모든 전원을 제거한 상태에서
  corrected K2 direct continuity와 남은 `T-ESTOP-002` wire-break matrix부터 시작한다.
