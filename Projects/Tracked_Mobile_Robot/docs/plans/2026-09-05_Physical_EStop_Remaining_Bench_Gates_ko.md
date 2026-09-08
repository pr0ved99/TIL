# 2026-09-05 Physical E-stop Remaining Bench Gates

## 상태와 목표

- 상태: `CURRENT / GATE 2 FUNCTIONAL PASS — GATE 4 CONDITIONED VOLTAGE SUBSET PASS, GATE 5 NEXT`
- 최신 결과: [`2026-09-08 progress`](../progress/2026-09-08_progress.md)
- 공식 수용 기준: [`Physical E-stop verification plan`](../verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)
- 목표: 완료된 K2/Gate 2, XL4015 #1/#2와 `T-ESTOP-003` voltage-function 결과를 보존하고,
  motor-disconnected `T-ESTOP-004` firmware/PWM integration으로 이동한다.

2026-09-07 사용자는 bottom-view 해석 오류를 설명하고 VeroRoute의 K2 Label을 정정해
`Tracked_Mobile_Robot_Perfboard_RevC_Estop_WIP_수정본.vrt`로 저장했다. 수정본의 Label 배열과
화면 위쪽 `R19=12/10/9/8`, 아래쪽 `R21=1/3/4/5`는 아래 Gate 1 표와 일치한다.
기존 `_WIP.vrt`는 이전 Label 배열이므로 현재 표시 기준으로 혼용하지 않는다.
이전 `2 kΩ` range의 `1.017 / 1.109 / 1.019 / 0.002`는 실제 접촉 패드가 확정되지 않은
raw로 보존하며 배선 오류나 PASS로 판정하지 않는다. 수정된 표시 기준의 K2-R02a/R02b/R03
재측정은 각각 `0.002~0.003 kΩ`라는 공통 범위 보고를 받았고 lead baseline `.003 kΩ`에 가까워
low-Ω subset `OPERATOR-REPORTED PASS`로 기록했다. 9/8에는 K2-R04a/R04b/R05 안내에
사용자가 `모두 통과`로 응답했고 정성 `OPERATOR-REPORTED PASS`로 기록했다(개별 숫자 미제공).
이후 사용자는 기존 LiPo 연결 스위치 PASS를 근거로 추가 NC/NO 재검사를 중단하고 다음으로
넘어가라고 지시했다. R06~R09는 `NOT RUN / SKIPPED PER USER DIRECTION`으로 남기며,
새 PASS로 바꾸지 않는다. 기존 정상 동작 PASS와 이번 R02~R05 도통 기록을 유지하고
K2 재진입 확인을 종료한다. Gate 2의 control/sense baseline은 도통 모드에서 모두
`OPERATOR-REPORTED PASS`다(정확한 Ω 미제공). 다음은 S0-B 한 가닥의 실제 단선·독립성이다. Powered 단계는 해당
Gate 2와 conditioned-sense preflight가 완료된 뒤에만 진행한다. 이후 S0-B 한쪽을 실제 분리한
상태에서 sense `open/no beep`, control `continuity/beep 유지`를 사용자가 모두 통과했다고 보고했다.
정확한 분리 종단/cavity와 Ω/OL 화면은 미기록이다. 이후 S0-B 복구/retention/도통 복귀,
S0-A 한쪽 단선의 control-open/sense-closed 독립성과 최종 복구도 모두 통과했다고 보고했다.
Gate 2 기능은 `OPERATOR-REPORTED PASS`, evidence metadata는 미완료다. 다음은 Gate 3 preflight다.

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

아래는 direct-pad 검사 참조표다. R02~R05는 위 기록대로 완료됐고, R06~R09는 9/8 사용자 지시로
이번 세션의 추가 재검사에서 제외했다. 이 표를 근거로 완료한 정상 릴레이 시험을 다시 시작하지 않는다.

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

Gate 0 무전원 확인, 위에 기록한 Gate 1 재진입 종료 결정과 Gate 2 단선·독립성 통과 뒤에만 진행한다.

1. STM32F446 PC7의 선택된 input configuration과 `V_SENSE_LOW_MAX`, `V_SENSE_HIGH_MIN`, absolute
   maximum 근거를 기록한다.
2. `R_OPTO_LED`, `R_PC7_PULLUP`, VO617A-3 방향과 actual board Net continuity를 대조한다.
3. Direct PC7-to-GND jumper가 제거됐고 `ESTOP_SENSE`에 5 V direct path가 없음을 무전원으로
   확인한다.
4. 사용할 단일 logic power-source configuration, DMM range와 probe ground를 기록한다.
5. MDD10A B+와 motor가 여전히 분리·절연됐는지 확인한다.

하나라도 닫히지 않으면 `T-ESTOP-003`을 시작하지 않는다.

현재 source 확인 결과 PC7은 `GPIO_MODE_INPUT + GPIO_PULLUP`, active-HIGH/open-fault다.
NUCLEO의 실제 접근점은 Arduino `D9`, `CN5 pin 2`다. STM32F446RE 공식
[`DS10693 Rev 11`](https://www.st.com/resource/en/datasheet/stm32f446re.pdf) Table 56의
CMOS production-test 기준에 따라 이번 벤치 판정은 실측 VDD에 대해
`V_SENSE_LOW_MAX=0.3 × VDD`, `V_SENSE_HIGH_MIN=0.7 × VDD`로 둔다.
VDD가 정확히 `3.300 V`일 때만 각각 `0.99 V`, `2.31 V`다.
PC7은 FTf pin이지만 architecture상 3.3 V pull-up 출력만 허용하며 5 V direct input으로 시험하지 않는다.
실제 `STM32_3V3`도 함께 측정하고, sense에서 5 V-class가 관찰되면 즉시 전원을 제거한다.

9/3에 R14 약 `10 kΩ`, U1.4↔GND와 U1.1↔U1.4 gross-short 없음,
U1.4↔PC7 및 R14.2↔3V3 continuity는 operator-reported PASS다. 관련 배선이 바뀌지 않았으므로
반복하지 않는다. 아직 필요한 preflight는 과거 direct-PC7용 D9-to-GND 점퍼의 물리적 제거,
사용할 단일 logic power-source 구성과 MDD10A B+/motor 분리 확인이다.

사용자는 현물에 별도 D9/PC7-to-GND jumper가 없음을 확인했다. 설계/netlist 기준 `R13.1`의
`AUX_5V`는 `J3.1 = XL4015 #2 OUT+`이며, 기존 승인된 USB 없는 board-power 구성은 XL4015 #1에서
NUCLEO E5V와 ESP32 5V를 공급한다. 두 buck OUT+를 서로 합치지 않는다. 현재 두 XL4015는
만능기판에 연결돼 있지 않으므로 `R13 ↔ buck OUT+` 도통검사를 요구하지 않는다. 두 모듈을
식별하고 board 연결 전 각각의 무부하 출력 전압과 극성을 확인한 뒤, 전원 OFF/rail 0 V 상태에서
#1 board-power와 #2 `J3.1/AUX_5V`를 분리된 출력 Net으로 연결한다.
XL4015 #1의 영구 분배는
[`11_XL4015_1_Dual_Board_Power_Distribution_Plan_2026-09-08_ko.md`](../../09_Electrical_Design/11_XL4015_1_Dual_Board_Power_Distribution_Plan_2026-09-08_ko.md)의
두 개별 2P의 탈착·극성·전원 Gate를 먼저 따른다. #1 OUT+/OUT-에서 두 cable pair로 바로 분기하며
inline 4P connector는 없다. Dual-USB mode에서는 두 2P를 모두 기판에서 제거한다. Board-path,
dual-2P source polarity와 NUCLEO/ESP32 단독·동시 powered 검증은 9/8 operator-reported PASS다.

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

2026-09-08 실행 결과:

| Condition | `ESTOP_SENSE C29,R19` to `LOGIC_GND C15,R4` |
| --- | ---: |
| S0 released / S0-B closed | `0.06 V` |
| S0 pressed and latched | `3.27 V` |
| S0 manually released | `0.06 V` |
| S0-B conductor open | `3.27 V` steady |

NUCLEO는 XL4015 #1, R13/S0-B/VO617A 입력은 XL4015 #2에서 공급했고 ESP32, MDD10A B+와
motor는 분리했다. 같은 실행에서 STM32 3V3는 `3.30 V`였으므로 `0.99/2.31 V` LOW/HIGH
threshold에 여유 있게 들어온다. 전원 제거·S0-B 복구와 정상 LOW 복귀도 사용자 보고 PASS다.
LED-loop current, 복구 뒤 exact voltage, DMM 모델/range와 photo/raw-log가 없어 formal evidence는
`PARTIAL`이지만 conditioned voltage/function subset은 `OPERATOR-REPORTED PASS`로 닫는다.
상세 결과는 [report 25](../verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md)를 따른다.

## Gate 5 — Later `T-ESTOP-004` Firmware/PWM Integration

`T-ESTOP-003 PASS` 뒤 motor와 MDD10A B+를 계속 분리하고 진행한다.

현재 `NOT RUN`이다. Firmware source 변경·flash·runtime은 없었다. 이 단계부터는 기존 학습 방식대로
Codex가 현재 코드를 확인하고 한 번에 작은 코드 단위와 위치·이유를 설명하면 사용자가 직접 입력·저장한다.
저장 후 Codex가 확인하고, 사용자가 지시할 때 build/flash/bench로 이동한다.

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
