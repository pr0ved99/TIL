# Physical E-stop RevC Assembly And Control-Path Bench Test Report

- 시험일: 2026-09-05
- 대상: RevC E-stop perfboard, 6P waterproof harness, S0/S2, K2, K1 control/main-terminal assembly
- 전원 범위: 3S LiPo control-path bench, motor disconnected, MDD10A `B+` disconnected
- 결과: `PARTIAL PASS — ASSEMBLY AND MOTOR-DISCONNECTED CONTROL-PATH SUBSET ONLY`
- 전체 Physical E-stop 판정: `NOT PASSED`

## 1. 목적과 증거 경계

이 보고서는 2026-09-05 session에서 사용자가 조립하고 직접 측정한 RevC Physical E-stop의
무전원 검사와 제한된 powered control-path 결과를 기록한다. 결과의 원자료는 사용자가 대화에서
보고한 DMM 값·도통음·동작 관찰과 session에 첨부한 조립 사진이다. DMM 화면, 연속 raw log,
logic-analyzer capture, 계측기 교정 기록과 사진 원본은 이 작성 시점에 repository evidence로
보존되지 않았다. 따라서 아래 PASS는 모두 `operator-reported/session-attached evidence` 범위다.

이번 실행이 증명하는 범위:

- RevC E-stop perfboard의 조립 완료와 제한된 무전원 continuity/isolation screen
- 18 AWG 6P harness의 압착·retention·pair truth table
- K1 coil/main lead와 K1 coil suppression assembly의 제한된 무전원/무부하 기능
- 건강한 S2와 pair short가 없는 조건에서 K2/K1 pickup, seal-in, dropout과 no-auto-restart
- K2 polarity 오류의 발견, 수정과 동일 범위 재시험

이번 실행이 증명하지 않는 범위:

- `S0-B -> VO617A-3 -> ESTOP_SENSE/PC7` conditioned 5 V/3.3 V electrical path
- active PWM 상태의 firmware latch, PWM-zero timing 또는 reset/ARM/CMD sequence
- K1 downstream에 실제 연결된 MDD10A `B+` rail-off; 이번 시험에서 MDD10A `B+`는 분리됨
- K1 접점의 motor-load voltage drop, temperature rise, interruption 또는 welded-contact 진단
- K1/K2 clamp transient와 relay release time
- actual motor stop, stop time/distance, `T-ESTOP-007`
- `FM-ESTOP-014` S2 stuck-closed/6P pair-short 단일고장 내성
- insulation-withstand, 인증 또는 산업 안전 적합성

## 2. As-built 구성

### 2.1 RevC board와 6P harness

사용자는 RevC 회로 납땜을 완료했다고 보고했다. 무전원 precheck에서 다음 test point는 모두
effectively `0 V`였다.

```text
AUX5V        0 V
3V3          0 V
SENSE        0 V
PERMISSION   0 V
K2_COIL_P    0 V
K1_COIL_P    0 V
```

6P waterproof connector 양쪽은 18 AWG로 조립했다. 사용자 보고 기준 cavity 기능은 다음과 같다.

| Cavity pair | Function | Unpowered result |
| --- | --- | --- |
| `1–2` | `S0-A` control NC | Released continuity, pressed/latched open, release recovery PASS |
| `3–4` | `S0-B` sense NC | Released continuity, pressed/latched open, release recovery PASS |
| `5–6` | `S2` momentary NO | Released open, pressed continuity, release-open PASS |

압착 상태, terminal locking/retention, intended pair continuity와 tested unintended-pair open은
사용자 보고로 통과했다. 이는 6P 조립 전 상태를 기록한 report 19를 supersede하지만 seal/IP 등급,
정격 진동, 장기 strain relief 또는 공구/die의 제조사-qualified crimp 승인은 아니다.

조립 경로를 결합한 뒤 board `JESTOP.3 <-> JESTOP.4`에서도 S0 released continuity,
pressed/latched open, manual release continuity 복귀를 사용자 보고로 재확인했다.
이는 explicit sense-conductor removal이나 S0-A/S0-B end-to-end 독립성 시험을 대신하지 않는다.

### 2.2 K1 assembly

| Item | As-built / observed result | Verdict boundary |
| --- | --- | --- |
| Coil terminals `85–86` | 18 AWG, extension 후 connector end-to-terminal continuity PASS | Assembly continuity PASS |
| Main terminals `30–87` | 14 AWG, crimp와 socket retention PASS | Prototype assembly only |
| K1 coil | `91 ohm`, later `92.4 ohm` | Consistent with official `81~99 ohm` incoming band |
| Coil clamp | `P6KE16CA` installed across `85–86` | Installed; transient/release timing NOT TESTED |
| Main NO contact | De-energized open; powered no-load `87` output observed | No-load functional subset PASS |

실제 14 AWG main lead는 이전 release 후보였던 TE `280756-4`의 documented conductor range와
별도로 terminal/wire compatibility를 확인해야 한다. 손당김과 도통 통과만으로 released high-current
harness 또는 18.9 A envelope 적합성을 주장하지 않는다.

## 3. K2 polarity anomaly와 수정

### 3.1 최초 관찰

최초 powered check에서 사용자는 S2를 누른 동안 K2 coil로 가정한 양단에서 `12.22 V`,
contact-side 한 점에서 `12.24 V`, 다음 점에서 `0 V`를 관찰했지만 K2 click과 self-hold는 없었다.
전압 크기만으로 coil polarity와 실제 pin identity가 옳다고 판단할 수 없었다.

2026-09-07 세션 복원에서 추가로 보존한 재작업 전 무전원 사용자 실측값:

| 기준점 | Component-side 측정점 | 보고값 | 해석 경계 |
| --- | --- | --- | --- |
| `J3_AUX5V.2` GND | K2 좌하단, actual pin 1 쪽 | `0.002 kΩ` | pin 1 쪽이 GND에 연결됐다는 진단 근거 |
| `J3_AUX5V.2` GND | K2 좌상단, actual pin 12 쪽 | `1.009 kΩ` | 반대쪽은 coil을 거친 저항으로 해석; post-rework 검증 아님 |

별도 coil 재검사에서 사용자는 `1.006`이라고 응답했다. 당시 여러 프로브 방향과 lead baseline을
함께 요청한 상태여서 단위·프로브 방향별 결과를 이 단일 응답으로 확정하지 않는다. Raw DMM
파일 없이 세션 텍스트에서 복원한 값이며, 새로운 측정이나 정밀 접속저항 검증이 아니다.

### 3.2 원인

Panasonic의 공식
[`TX Relays datasheet`](https://industry.panasonic.com/ac/cdn/e/control/relay/signal/catalog/mech_eng_tx.pdf)는
PC-board schematic을 `BOTTOM VIEW`로 표시한다. Single-side-stable TX2 coil은 polarized이고
pin 1이 `+`, pin 12가 `-`다. 부품면 사진의 원형 dimple은 physical pin 1 쪽을 식별한다.

기존 component-side hole table은 datasheet의 bottom-view 행을 부품면에 그대로 옮겨 physical
pin 1과 pin 12를 반대로 해석했다. 그 결과 최초 상태에서는 dimple 쪽 physical pin 1이 GND,
physical pin 12가 `K2_COIL_P`에 놓여 coil이 역극성으로 인가됐다. 사용자는 polarity를 수정했다.

코일 저항과 de-energized DPDT contact truth table은 상·하 행을 뒤바꿔도 동일한 값이 나올 수 있어
기존 무전원 검사가 이 오류를 검출하지 못했다. RevC FINAL/VeroRoute의 K2 전체 pin/coordinate 표는
post-rework point-to-point continuity로 다시 세기 전까지 as-built 정본으로 사용하지 않는다.

## 4. Powered control-path 재시험

K2 polarity 수정 후, motor와 MDD10A `B+`를 분리한 상태에서 사용자가 보고한 결과다.

| Case | Expected | Operator-observed result | Verdict |
| --- | --- | --- | --- |
| Initial/no deliberate S2 | K2/K1 remain OFF | No unintended enable reported | PASS — bounded subset |
| Deliberate S2 | K2 pickup and seal-in | Pickup/self-hold 정상 | PASS |
| S2 release 뒤 coil feed | K1 coil feed 유지 | `JK1COIL.1 <-> J3_AUX5V.2 = 12.19 V` 유지, supply `12.24 V` | PASS — operator-reported steady state |
| K2 pole 2 -> K1 | K1 energized, no-load `87` available | K1 enable and `87` output 정상 | PASS |
| S0 press/latch | K2/K1 drop out | Both dropped out | PASS |
| S0 physical release only | No automatic re-enable | S2 전까지 restart 없음 | PASS |
| S1 control power OFF -> ON | No automatic re-enable | S2 전까지 restart 없음 | PASS |

이 결과는 healthy momentary S2와 정상 6P harness에서 `T-ESTOP-005A`의 control-relay subcases를
지지한다. 그러나 MDD10A `B+`가 분리돼 direct downstream rail을 측정하지 않았고,
`ESTOP_SENSE`/PWM/UART를 동시에 관찰하지 않았으므로 전체 `T-ESTOP-005A PASS`가 아니다.

## 5. Test-ID 판정

| Test ID | 2026-09-05 반영 상태 | 남은 범위 |
| --- | --- | --- |
| `T-ESTOP-001` | `PARTIAL` — board/6P/K1/K2 as-built subset 추가 | Exact release review, fuse/wire/terminal coordination, loaded/thermal evidence |
| `T-ESTOP-002` | `PARTIAL` — 6P pair map, S0-A/S0-B truth table와 selected isolation PASS | Complete end-to-end wire-removal/cross-wire log와 repository raw evidence |
| `T-ESTOP-003` | `PARTIAL/BLOCKED` — 기존 direct-PC7 subset만 유효 | Actual S0-B/VO617A-3 conditioned LOW/HIGH, current, wire-open and isolation |
| `T-ESTOP-004` | `PARTIAL/BLOCKED` — 기존 direct-PC7 firmware subset만 유효 | Integrated S0-B assertion, active PWM-zero timing and current reset runtime |
| `T-ESTOP-005A` | `PARTIAL` — healthy-path K2/K1 pickup/latch/dropout/no-restart subcases PASS | Direct MDD10A downstream rail, PWM and firmware reset/ARM/CMD cases |
| `T-ESTOP-005B` | `DEFERRED / POST-MVP` | `FM-ESTOP-014` mitigation and stuck/pair-short fault injection |
| `T-ESTOP-007` | `BLOCKED` | Full motor-disconnected gate, then lifted motor test |

Overall:

```text
RevC assembly and selected unpowered checks: OPERATOR-REPORTED PASS
6P 18 AWG harness/cavity functional truth table: OPERATOR-REPORTED PASS
K1/K2 motor-disconnected control-relay subset after polarity correction: OPERATOR-REPORTED PASS
Conditioned PC7 path: NOT TESTED IN THIS RUN
Full T-ESTOP-005A direct downstream rail/PWM acceptance: NOT PASSED
Actual motor stop: NOT TESTED
Physical E-stop overall: PARTIAL / NOT PASSED
Industrial-safety or single-fault-tolerant claim: NOT ALLOWED
```

## 6. 다음 검증 Gate

1. [`Remaining bench gates`](../plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md)의
   Gate 0~2에 따라 무전원 재진입, K2 post-rework direct continuity와 남은 `T-ESTOP-002`
   sense/control wire-removal 및 독립성 기록을 먼저 닫는다.
2. 모든 motor-power source를 계속 분리하고 `S0-B -> VO617A-3 -> PC7` conditioned path의
   healthy/pressed/wire-open 전압과 isolation을 실행한다 (`T-ESTOP-003`).
3. Motor-disconnected 상태에서 actual S0-B assertion과 active PWM-zero/latch/reset sequence를
   capture한다 (`T-ESTOP-004`).
4. `T-ESTOP-001~004`가 모두 PASS한 뒤에만 current-limited setup에서 MDD10A `B+`를 의도적으로 연결하고,
   K1 downstream rail을 직접 측정해 full nominal `T-ESTOP-005A`를 실행한다.

## 7. 관련 문서

- [`2026-09-05 progress`](../progress/2026-09-05_progress.md)
- [`2026-09-05 remaining bench gates`](../plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md)
- [`06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)
- [`05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)
- [`19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md`](19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md)
- [`../plans/2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md`](../plans/2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md)
- [`../../09_Electrical_Design/VeroRoute/README.md`](../../09_Electrical_Design/VeroRoute/README.md)
