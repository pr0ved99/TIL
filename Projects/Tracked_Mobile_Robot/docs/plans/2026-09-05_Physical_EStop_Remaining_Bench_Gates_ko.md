# 2026-09-05 Physical E-stop Remaining Bench Gates

## 상태와 목표

- 상태: `CURRENT / POWER-OFF REENTRY FIRST`
- 최신 결과: [`2026-09-05 progress`](../progress/2026-09-05_progress.md)
- 공식 수용 기준: [`Physical E-stop verification plan`](../verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)
- 목표: K2 post-rework 좌표를 무전원으로 고정하고, 남은 `T-ESTOP-002` wire-break/독립성부터
  순서대로 닫은 뒤 `T-ESTOP-003` conditioned sense로 이동한다.

2026-09-05에는 12.24 V control-only setup에서 K2/K1 nominal pickup/dropout, S2 self-hold,
`JK1COIL.1=12.19 V`, S0/S1 no-auto-restart를 확인했다. S0-B `JESTOP.3 <-> JESTOP.4`의
released/pressed-latched/manual-release truth table도 무전원 PASS다. 이 항목은 배선을 바꾸지 않는
한 반복하지 않는다.

MDD10A B+는 K1-87에서 분리·절연돼 있었고 motor/conditioned PC7/PWM은 시험하지 않았다.
따라서 이번 계획은 아직 완료되지 않은 Formal Gate만 다룬다.

## 절대 경계

- 저항·continuity·diode mode는 모든 source와 USB가 분리되고 rail이 0 V일 때만 사용한다.
- Powered 단계 중 connector, probe range 또는 배선을 바꾸지 않는다. 변경은 S1 OFF, XT60/USB
  분리와 0 V 재확인 뒤 수행한다.
- MDD10A B+는 Gate 6 진입 조건을 모두 충족하기 전까지 계속 분리·절연한다. Motor는
  Gate 6 전체가 끝날 때까지 계속 분리한다.
- Direct PC7-to-GND 임시 jumper가 있으면 conditioned path 전원 인가 전에 제거한다.
- NUCLEO USB와 buck/외부 5 V를 동시에 사용하지 않는다. 승인된 한 가지 power-source
  configuration만 사용하고 PWR_GND/LOGIC_GND 기준을 먼저 확인한다.
- 예상과 다른 continuity, polarity, 5 V at PC7, relay chatter, 발열·냄새·변색 또는 S0/S1 release
  뒤 자동 재인가가 하나라도 나오면 즉시 `FAIL/HOLD`한다.

## Gate 0 — Safe Power-Off Reentry

1. S1을 OFF하고 S0를 눌러 latched 상태로 둔다. S2는 놓는다.
2. XT60, 모든 USB, XL4015, STM32/ESP32와 motor를 분리한다.
3. MDD10A B+ 단부가 K1-87에서 분리돼 개별 절연됐는지 육안 확인한다.
4. DC V mode로 `K2_COIL_P`, `K1_COIL_P`, K1-87, `5V_LOGIC`, `STM32_3V3`를 각 GND 기준으로
   측정한다.
5. 모두 effectively 0 V인 경우에만 DMM을 continuity/ohm mode로 바꾸고 lead baseline을 기록한다.

Acceptance:

```text
all checked rails = effectively 0 V
MDD10A B+ = disconnected and insulated
motor / USB / buck / MCU logic = disconnected
DMM lead baseline = recorded
```

## Gate 1 — K2 Bottom-View Post-Rework Continuity

기존 RevC FINAL/PDF와 2026-09-03 계획의 K2 좌표표는 bottom-view를 component-side에 직접
적용한 frozen historical mapping이라 실물 핀 정본이 아니다. Body의 원형 dimple을 pin 1로 잡은
corrected component-side mapping은 다음과 같다.

| 실제 K2 pin | 좌표 | Expected Net / state |
| ---: | --- | --- |
| 1 | `C37,R21` | `K2_COIL_P` |
| 3 | `C39,R21` | NC1 |
| 4 | `C40,R21` | `ESTOP_CONTROL_PERMISSION` |
| 5 | `C41,R21` | `K1_COIL_P` / K1-enable-pole NO |
| 12 | `C37,R19` | GND |
| 10 | `C39,R19` | NC2 |
| 9 | `C40,R19` | `ESTOP_CONTROL_PERMISSION` |
| 8 | `C41,R19` | `K2_COIL_P` / hold-pole NO |

아래를 direct pad에서 확인한다.

| ID | FROM | TO | 기대 |
| --- | --- | --- | --- |
| K2-R01 | actual pin 1 `C37,R21` | actual pin 12 `C37,R19` | 약 `1.03 kΩ` coil |
| K2-R02 | JESTOP.6 | actual pin 1과 pin 8 | low Ω / continuity |
| K2-R03 | board GND | actual pin 12 | low Ω / continuity |
| K2-R04 | JESTOP.2 또는 .5 | actual pin 4와 pin 9 | low Ω / continuity |
| K2-R05 | JK1COIL.1 | actual pin 5 | low Ω / continuity |
| K2-R06 | actual pin 3 | actual pin 4 | de-energized NC closed |
| K2-R07 | actual pin 4 | actual pin 5 | de-energized NO open |
| K2-R08 | actual pin 10 | actual pin 9 | de-energized NC closed |
| K2-R09 | actual pin 9 | actual pin 8 | de-energized NO open |

각 결과는 `beep`만 쓰지 말고 가능한 경우 Ω/OL display를 기록한다. Corrected mapping과 하나라도
다르면 powered test로 돌아가지 않고 VRT/실물/배선을 다시 대조한다.

## Gate 2 — Complete `T-ESTOP-002` Wire-Break And Independence

### 이미 완료된 subset

`JESTOP.3 <-> JESTOP.4` S0-B contact truth table:

```text
released             -> continuity / beep
pressed and latched  -> open / no beep
manual release       -> continuity / beep restored
```

이는 PASS이며 S0-B 배선이나 contact block을 변경하지 않았다면 반복하지 않는다.

### 남은 시험

1. S0 released 상태에서 완성된 S0-A 경로의 양 끝인 `S1 OUT <-> JESTOP.2` baseline을
   기록한다. 이 측정에는 F2, 6P cavity 1/2와 S0-A NC가 직렬로 포함된다.
2. S0-B sense conductor 한쪽을 housing/terminal 손상 없이 분리한다.
3. `JESTOP.3 <-> JESTOP.4 = OL/no beep`인지 확인한다.
4. 같은 상태에서 S0-A control baseline이 변하지 않았는지 확인한다.
5. Sense conductor를 원위치하고 retention을 확인한 뒤 `JESTOP.3 <-> JESTOP.4` continuity가
   복귀하는지 확인한다.
6. 6P cavity 1 또는 2의 S0-A control conductor 한쪽을 분리해
   `S1 OUT <-> JESTOP.2 = OL/no beep`를 확인한다.
7. 같은 상태에서 released S0-B `JESTOP.3 <-> JESTOP.4`가 closed를 유지하는지 확인한다.
8. Control conductor를 복구하고 retention과 두 baseline을 다시 확인한다.
9. S0-A/S0-B, K1 coil/main contact 사이 unintended near-zero continuity가 없는지 기록한다.

Board `JESTOP.1`은 현재 as-built에서 미사용이다. `JESTOP.1 <-> JESTOP.2`를 control baseline으로
측정하거나 둘을 jumper하지 않는다.

Acceptance:

| Fault injection | Control path | Sense path |
| --- | --- | --- |
| none, S0 released | closed | closed |
| S0 pressed/latched | open | open |
| sense wire removed | 기존 control 상태 유지 | open |
| control wire removed | open | 기존 sense 상태 유지 |

모든 실제 Ω/OL, 제거한 정확한 cavity/conductor, 복구 뒤 retention과 사진 경로를 기록해야
`T-ESTOP-002 PASS` 후보로 올릴 수 있다.

## Gate 3 — `T-ESTOP-003` Preflight

Gate 0~2가 통과한 뒤에만 진행한다.

1. STM32F446 PC7의 선택된 input configuration과 `V_SENSE_LOW_MAX`, `V_SENSE_HIGH_MIN`, absolute
   maximum 근거를 기록한다.
2. `R_OPTO_LED`, `R_PC7_PULLUP`, VO617A-3 방향과 actual board Net continuity를 대조한다.
3. Direct PC7-to-GND jumper가 제거됐고 `ESTOP_SENSE`에 5 V direct path가 없음을 무전원으로
   확인한다.
4. 사용할 단일 logic power-source configuration, DMM range와 probe ground를 기록한다.
5. MDD10A B+와 motor가 여전히 분리·절연됐는지 확인한다.

하나라도 닫히지 않으면 `T-ESTOP-003`을 시작하지 않는다.

## Gate 4 — `T-ESTOP-003` Conditioned Sense Powered Test

Probe는 `ESTOP_SENSE`인 R14.1/U1.4/PC7 Net과 `LOGIC_GND` 사이에 둔다. 전원 인가 후에는
probe와 배선을 움직이지 않고 S0만 조작한다.

| Condition | Expected `ESTOP_SENSE` |
| --- | --- |
| S0 released / S0-B closed | Logic LOW, `V_SENSE_LOW_MAX` 이하 |
| S0 pressed and latched | 3.3 V-class HIGH, `V_SENSE_HIGH_MIN` 이상 |
| S0 manually released | Logic LOW 복귀; software latch 결과는 다음 Gate |
| Sense wire open | 3.3 V-class HIGH / fault |

Sense-wire-open powered case는 live disconnect하지 않는다. Power OFF와 0 V 확인 후 conductor를
분리하고, probe를 고정한 다음 다시 같은 단일 logic source만 인가한다. 모든 state에서 PC7
absolute maximum을 넘지 않아야 하며 5 V가 보이면 즉시 전원을 제거한다.

Acceptance:

- Healthy LOW와 pressed/open HIGH가 STM32 datasheet threshold margin을 만족한다.
- Pressed와 wire break가 같은 asserted electrical state다.
- 5 V direct input, control/sense unintended current sharing과 비정상 발열이 없다.
- 각 상태의 voltage, source configuration, DMM와 사진/log 경로가 남는다.

## Gate 5 — Later `T-ESTOP-004` Firmware/PWM Integration

`T-ESTOP-003 PASS` 뒤 motor와 MDD10A B+를 계속 분리하고 진행한다.

- Logic analyzer: PC7/`ESTOP_SENSE`, PB6/PWM1, PB7/PWM2와 공통 LOGIC_GND.
- Boot released/open, active limited-output assertion, physical release, reset-while-active reject,
  released explicit reset, new ARM/new CMD와 sense-wire-open case를 기록한다.
- S0-B assertion 후 both PWM zero, persistent latch와 no stale-command replay를 확인한다.
- Test hook은 종료 뒤 모두 `0U`로 복구하고 target reflash/no-command safe runtime을 남긴다.

`T_PWM_ZERO_MAX`와 exact firmware/artifact provenance가 닫히기 전에는 전체 PASS가 아니다.

## Gate 6 — Later Formal `T-ESTOP-005A`

`T-ESTOP-001~004`가 모두 PASS한 뒤에만 MDD10A B+를 K1-87에 연결한다. Motor는 계속 분리한다.

- Complete test build, F1/F2 identity·coordination, 6P cavity/crimp/continuity/retention을 먼저 닫는다.
- Defined `V_RAIL_OFF_MAX`와 instrument uncertainty를 기록한다.
- K1-87이 아니라 실제 MDD10A B+ to PWR_GND에서 ON/OFF rail을 측정한다.
- S2 enable, S0 drop, release no-auto, S1/control-power restore no-auto, firmware reset/new ARM/new CMD,
  UART/ESP32 loss를 sense/PWM/direct rail과 함께 기록한다.
- Back-power source matrix와 abnormal current/heat를 별도 확인한다.

이 Gate가 끝날 때까지 actual motor energy, lifted motor와 `T-ESTOP-007`은 `HOLD`다.
`T-ESTOP-005B`와 `T-ESTOP-006`은 post-MVP로 유지한다.

## 기록 양식

```text
Date/time:
Operator:
Gate / Test ID:
As-built revision:
Battery / logic source:
Fuse and motor state:
Instrument / mode / range:
FROM / TO:
Expected:
Observed / numeric value:
Photo or raw-log path:
Result: PASS / FAIL / PARTIAL / NOT RUN
Evidence boundary and next action:
```
