# Physical E-stop Received-Component Incoming Precheck Report

- 시험일: 2026-08-28
- 시험 범위: K1, S0, S2, `VO617A-3`, P6KE, F2와 6P connector kit의 무전원 입고 선별
- 결과: `PARTIAL PASS — RECEIVED-COMPONENT UNPOWERED PRECHECK ONLY`
- 전체 Physical E-stop 판정: `NOT PASSED`

## 1. 목적과 증거 경계

2026-08-27~28에 도착이 보고된 Physical E-stop 부품 중 전원을 인가하지 않고 확인할 수 있는
항목을 선별했다. 모든 저항·다이오드·도통 측정은 relay, switch와 semiconductor를 회로에서
분리하고 LiPo, motor, USB 및 외부 전원을 모두 제거한 상태에서 사용자가 수행했다.

이번 보고서가 증명하는 범위는 다음과 같다.

- K1 입고품의 구성품 식별, coil resistance, 무여자 NO-open과 저전압 coil-contact 단락 선별
- S0 두 NC channel의 기본 truth table, latch/turn-release 반복 동작과 channel 간 단락 선별
- `VO617A-3` input LED polarity와 무전원 input-output 단락 선별
- F2 fuse/holder 조합의 무전원 연결성
- 6P 부품이 완성 하네스가 아니라 직접 압착·조립하는 loose connector kit임을 확인
- S2 momentary NO contact의 release/press/release truth table
- P6KE16CA x3의 exact `CA` marking, 양방향 gross-short 선별과 무극성 외관

다음은 이번 보고서의 PASS 범위가 아니다.

- K1/K2 powered pickup/dropout, coil clamp, release delay와 contact switching
- K1 main-contact milliohm resistance, loaded voltage drop, temperature rise 또는 downstream rail-off
- K1/VO617A-3/S0의 insulation resistance 또는 정격 isolation-withstand 성능
- S0 실제 DC load, direct-opening 성능 또는 완성 회로에서의 two-channel 동작
- `VO617A-3` CTR, 5 V LED-loop current, transistor saturation 또는 conditioned PC7 LOW/HIGH
- F2 정확한 실물 marking 대조, time-current coordination, interruption 또는 loaded thermal 성능
- 6P cavity map, crimp quality, intended-pair continuity, unintended-pair open, seal 또는 terminal retention
- P6KE breakdown/clamp voltage, pulse energy 또는 powered K1/K2 release 영향
- `T-ESTOP-001~004`, nominal `T-ESTOP-005A`, actual motor stop 또는 산업 안전 적합성

## 2. K1 TE assembly 무전원 검사

### 2.1 구성품 식별

사용자는 입고 구성을 다음과 같이 대조했다.

| Role | Actual item reported | Quantity | Result |
| --- | --- | ---: | --- |
| K1 relay | TE `V23134J1052D642` | 1 | MATCH |
| Socket | TE `VCF7-1000` | 1 | MATCH |
| Main-contact terminal | TE `280756-4` | 2 | MATCH |
| Coil terminal | TE `42281-1` | 2 | MATCH |

`280756-4`와 `42281-1`은 아직 wire에 crimp하거나 socket에 삽입하지 않았다. Loose terminal의
최종 orientation, crimp, socket retention과 extraction/serviceability는 계속 열려 있다.

### 2.2 전기 선별

| Check | Operator-observed result | Acceptance | Verdict |
| --- | ---: | --- | --- |
| Coil `85–86` | `89.5 ohm` | Official `90 ohm +/-10%`, 즉 `81~99 ohm` | PASS |
| De-energized main NO `30–87` | 도통음 없음 | Open | PASS |
| `85–30`, `85–87`, `86–30`, `86–87` | 전부 도통음 없음 | No low-voltage short | PASS |

따라서 K1은 `UNPOWERED ELECTRICAL SCREEN PASS`다. 마지막 행은 DMM continuity 범위의 단락
선별이지 정격 insulation withstand 시험이 아니다. Socket terminal fit, main terminal crimp,
powered contact close/open과 motor-load release는 검증하지 않았다.

## 3. `VO617A-3` 무전원 검사

사용자는 actual part를 `VO617A-3`로 확인하고 DIP-4 단품에서 측정했다.

| Check | Operator-observed result | Verdict |
| --- | --- | --- |
| Input LED, red probe pin 1 / black probe pin 2 | `955`, 즉 약 `0.955 V` | PASS |
| Input LED reverse, pin 2 -> pin 1 | Meter `1`/open, 변화 없음 | PASS |
| Output transistor pins 3–4, both directions | Meter `1`/open, 도통음 없음 | PASS |
| Input-output cross pairs `1–3`, `1–4`, `2–3`, `2–4` | 전부 도통음 없음 | PASS |

따라서 `VO617A-3`는 `UNPOWERED DIODE/GROSS-SHORT SCREEN PASS`다. Cross-pair open은
저전압 DMM에서 input-output 사이에 명백한 단락이 없다는 선별 결과일 뿐, insulation
resistance나 isolation withstand 성능을 증명하지 않는다. `0.955 V`는 사용한 DMM의
diode-test current에서 관찰한 값이며, datasheet 특정 시험조건의 `V_F` 재현값으로 해석하지
않는다. 실제 `5 V -> 680 ohm -> S0-B -> LED` 경로, external `10 kohm` pull-up, PC7 voltage와
wire-open safe direction은 별도 powered motor-disconnected 시험이 필요하다.

## 4. S0 Autonics E-stop switch 무전원 검사

### 4.1 사진 식별

원본 사진에서 다음 visible marking을 확인했다.

- Actuator/body: `SF2ER-E2R2B`, `EMERGENCY STOP DEVICE`, `AE21R`
- Contact block: `SFEA-CB` x2
- 두 contact block 모두 `NC`
- 각 block terminal: `.1`, `.2`

구매 기록의 complete order description은 `SF2ER-E2R2B-A`다. 실물 body 사진에는 `-A`가
보이지 않으므로 body 기본형번과 주문 suffix를 구분해 기록한다. 이것만으로 다른 제품이라고
판정하지 않지만, official order-code/포장 label 대조 없이 body에 없는 suffix를 관찰값처럼
기록하지 않는다.

### 4.2 Truth table과 channel 간 단락 선별

| State/check | Upper NC `.1–.2` | Lower NC `.1–.2` | Verdict |
| --- | --- | --- | --- |
| Released | 도통음 발생 | 도통음 발생 | PASS |
| Pressed/latched | 도통음 없음 | 도통음 없음 | PASS |
| Turn release | 도통 복귀 | 도통 복귀 | PASS |

Pressed latch 유지와 turn release 후 두 NC channel 복귀를 총 3회 반복해 모두 통과했다.
Released 상태에서 다음 cross-channel 네 조합도 모두 도통음이 없었다.

```text
upper .1 <-> lower .1
upper .1 <-> lower .2
upper .2 <-> lower .1
upper .2 <-> lower .2
```

따라서 S0는 `UNPOWERED 2NC/LATCH FUNCTION SCREEN PASS`다. 이 결과는 두 NC contact를
실제 S0-A coil-control loop와 S0-B 5 V sensing loop에 배선한 통합 시험이 아니다.

## 5. F2 1 A fuse와 holder 무전원 검사

구매 정본은 Littelfuse `0287001.PXCN` 1 A ATOF와 `FHAC0001ZXJA` holder다. 이번 session에는
실물의 exact body/fuse marking 원문을 별도로 기록하지 못했으므로 구매 형번과 observed marking을
같은 증거로 취급하지 않는다.

| Check | Operator-observed result | Verdict |
| --- | --- | --- |
| Fuse 단품 continuity | 도통 PASS 보고 | PASS |
| Empty holder, lead-to-lead | 도통음 없음 | PASS |
| Fuse installed, lead-to-lead | 도통음 발생 | PASS |
| Installed 상태에서 lead를 가볍게 움직임 | 끊김 없음, 전부 정상 | PASS |

따라서 F2는 `UNPOWERED CONTINUITY SCREEN PASS / EXACT MARKING OPEN`이다. 1 A identity,
time-current curve, battery fault-current coordination, loaded voltage drop와 holder temperature는
별도 증거가 필요하다.

## 6. 6P connector kit와 18 AWG 상태 정정

2026-08-27 문서에서는 도착품을 `6P waterproof harness/18 AWG`라고 요약했다. 2026-08-28
scale-grid 사진으로 실물을 다시 확인한 결과, 정확한 현재 상태는 다음과 같다.

```text
loose/unassembled 6P waterproof connector kit
+ separate 18 AWG wire
```

사진에는 암·수 housing, loose male/female open-barrel terminal, yellow individual wire seal과 red
secondary lock이 분리된 상태로 보인다. Preterminated wire나 이미 검증된 1:1 harness가 아니다.

1 cm grid로 가늠한 사진 기반 근사치는 다음과 같다.

- 큰 housing envelope: 약 `4.3~4.5 x 4.1~4.3 cm`
- 작은 housing envelope: 약 `4.4~4.6 x 2.2~2.5 cm`
- loose terminal length: 약 `2.0~2.5 cm`

이는 perspective가 포함된 사진 기반 근사치이며 caliper 측정 또는 mounting release 치수가 아니다.
현재 terminal, seal과 secondary lock은 삽입하지 않았다.

기능 배치 후보는 S0-A 2선, S0-B 2선과 S2 2선이다. 기존 문서의 S2 `5–6` reference가 있지만,
actual mating-face numbering과 orientation을 확인하기 전에는 전체 `1–6` cavity map을 동결하지
않는다. 따라서 다음 항목은 모두 `OPEN`이다.

- Actual cavity number와 mating-face orientation
- `S0-A / S0-B / S2` pair assignment release
- Male-female 1:1 continuity와 모든 unintended-pair open/short screen
- 18 AWG conductor crimp와 yellow seal crimp
- Terminal insertion/retention, secondary-lock engagement와 strain relief

## 7. Crimp tool 주문 상태

사용자는 2026-08-28 `VH-30J` 교체식 die set를 주문했다. 판매 자료에 표시된 구성은
`WX-35WF (10~35 mm2)`, `WX-03B (0.5~6 mm2)`, `WS-25WF (2x0.5~2x6 mm2)`와
`WS-692 (1.5~6 mm2)`다. 이는 seller-claimed 범위이며 아직 공구가 도착하지 않았고 실제
jaw profile, 6P terminal/seal crimp와 TE `280756-4` crimp를 확인하지 않았다.

현재 판정은 다음과 같다.

```text
Procurement: USER-REPORTED ORDERED
Arrival: NOT RECEIVED
6P compatibility: NOT VALIDATED
K1 280756-4 compatibility: NOT VALIDATED
Crimp/retention/electrical release: OPEN
```

공구 도착 후에는 여분 6P terminal로 first-article conductor/seal crimp의 외관, 강한 손당김과
housing insertion/retention을 먼저 확인한다. K1 `280756-4`는 2개뿐이므로 첫 연습용
terminal로 사용하지 않는다. K1 main crimp는 final wire와 die fit을 확인한 뒤 실행하고 이후
loaded voltage-drop/thermal 시험으로 별도 release한다.

## 8. S2 IDEC `ABW110G` 무전원 검사

입고품은 terminal `3`, `4`의 2-terminal momentary pushbutton이다.

| State/check | Operator-observed result | Acceptance | Verdict |
| --- | --- | --- | --- |
| Released, `3–4` | 도통음 없음 / open | NO contact released-open | PASS |
| Pressed, `3–4` | 도통음 발생 | Pressed-closed | PASS |
| Release after press | open으로 복귀 | Momentary return | PASS |
| Repeated operation | 동일 truth table 유지 | Repeatable return | PASS |

따라서 S2는 `UNPOWERED MOMENTARY-NO FUNCTION SCREEN PASS`다. 이는 K2/K1 self-hold loop에
배선된 상태의 reset/re-enable, contact bounce, actual DC current 또는 `FM-ESTOP-014`
stuck-closed fault tolerance를 증명하지 않는다.

## 9. `P6KE16CA-E3/54` x3 무전원 검사

사용자는 세 입고품의 `P6KE16CA` marking을 확인했다. `CA` suffix는 bidirectional TVS이므로
일반 정류 다이오드와 달리 한쪽 극성을 나타내는 cathode stripe가 없는 외관과 일치한다.

| Check | Operator-observed result | Verdict |
| --- | --- | --- |
| Continuity, both probe directions | 세 샘플 모두 도통음 없음 | PASS |
| Diode mode, both probe directions | 세 샘플 모두 meter `1`/open | PASS |
| Polarity stripe | 보이지 않음 | Consistent with bidirectional `CA` |

따라서 P6KE x3는 `UNPOWERED IDENTITY / GROSS-SHORT SCREEN PASS`다. DMM의 continuity/diode
mode는 13.6 V stand-off, 15.2~16.8 V breakdown, 22.5 V clamp, surge energy 또는 K1/K2 coil release time을 시험할
전압·전류가 아니다. 이 양방향 TVS는 coil 양단에 극성 구분 없이 병렬 설치할 수 있지만 lead insulation, mechanical support와
powered pickup/dropout/release test는 계속 열려 있다.

## 10. 남은 조립·공구와 직렬 Gate

| Item | 2026-08-28 status | Gate |
| --- | --- | --- |
| S2 IDEC `ABW110G` | RECEIVED / UNPOWERED FUNCTION SCREEN PASS | Nominal K2/K1 re-enable path integration |
| `P6KE16CA-E3/54` x3 | RECEIVED / UNPOWERED GROSS-SHORT SCREEN PASS | K1/K2 installation와 powered release-time test |
| `VH-30J` multi-die set, including `WX-03B` | ORDERED / NOT RECEIVED | 6P/K1 first-article crimp validation |
| 6P loose kit + 18 AWG | RECEIVED / UNASSEMBLED | Cavity map, crimp, 1:1/unintended-pair open과 retention |

S2와 P6KE incoming은 닫혔지만 6P가 미조립이고 crimp tool compatibility도 검증하지 않았으므로
complete control path assembly와 powered K1/K2 coil 시험은 아직 시작하지 않는다. Crimp tool
도착은 부품 입고 PASS 자체와 별개이며, 실제 first-article crimp 결과를 확인해야 한다.

## 11. 종합 판정

닫힌 범위:

- K1 exact received components와 unpowered coil/NO/coil-contact gross-short screen
- `VO617A-3` unpowered LED direction, output-open과 input-output short screen
- S0 2NC, latch/turn-release three-cycle 및 cross-channel gross-short screen
- F2 fuse/holder unpowered continuity screen
- 6P 실물의 `loose connector kit + separate 18 AWG` 상태 식별
- S2 `3–4` momentary NO release/press/release screen
- P6KE16CA x3 identity와 bidirectional gross-short screen

열린 범위:

- Crimp-tool incoming과 6P first-article compatibility
- F2 exact actual marking
- 6P assembly와 모든 cavity/crimp/retention evidence
- Conditioned PC7 path와 powered K1/K2 control circuit
- Direct downstream rail-off, back-power, voltage-drop/thermal와 actual motor stop

따라서 전체 판정은 계속 다음과 같다.

```text
Executed unpowered electrical screens: PASS — LIMITED DMM SCREEN SCOPE
Overall received-component incoming: PARTIAL — F2 marking, 6P/tooling and powered integration OPEN
Harness/tooling readiness: PARTIAL / UNASSEMBLED
Physical E-stop integrated hardware: NOT TESTED
T-ESTOP-001~004: BLOCKED / NOT PASSED
T-ESTOP-005A: BLOCKED / NOT PASSED
Actual motor stop: NOT TESTED
Industrial-safety or single-fault-tolerant claim: NOT ALLOWED
```

## 12. Evidence provenance

측정값과 continuity 결과는 사용자가 session에서 보고한 operator-observed evidence다. DMM 화면
사진이나 raw measurement log는 repository에 보존되지 않았다.

사진 원본은 작성 시점에 operator Desktop에만 있고 repository에는 아직 복사되지 않았다.

| Original file | Subject | Resolution | SHA-256 |
| --- | --- | ---: | --- |
| `KakaoTalk_20260828_013340216.jpg` | S0 front/body marking | `4032 x 3024` | `7B99D3FF91F07A2098F1E58651E8E77B0306EB411A93CC653C1CA39BCBF53E65` |
| `KakaoTalk_20260828_013340216_01.jpg` | S0 rear/two NC blocks | `4032 x 3024` | `343D260ACCBCCFC27C29BF0D2527C92830CB4BBBF5DFCAE0562670331DB651F2` |
| `KakaoTalk_20260828_015357393.jpg` | Loose 6P connector kit on 1 cm grid | `4032 x 3024` | `8D600006C2EB81EF9EF175D3620ABBF72508180AAFB08616D5ADFE8706662CA0` |

상위 architecture와 다음 powered-test 기준은 다음 문서를 따른다.

- [`../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md)
- [`../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md`](../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md)
- [`06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)
- Historical direct-PC7/K2/F1 report:
  [`18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md`](18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md)
