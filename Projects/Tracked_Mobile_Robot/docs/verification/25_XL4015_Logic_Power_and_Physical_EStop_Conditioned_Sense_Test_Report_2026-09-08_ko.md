# XL4015 Logic Power And Physical E-stop Conditioned Sense Test Report

- 시험일: 2026-09-08
- 대상: XL4015 #1 NUCLEO/ESP32 logic-power distribution, XL4015 #2 `AUX_5V`, RevC S0-B/VO617A/PC7 sense path
- 전원 범위: 3S LiPo, MDD10A `B+`와 motor 분리
- 결과: `PARTIAL PASS — LOGIC-POWER AND CONDITIONED-SENSE FUNCTIONAL SUBSETS`
- 전체 Physical E-stop 판정: `PARTIAL / NOT PASSED`

## 1. 목적과 증거 경계

이 보고서는 2026-09-08에 사용자가 직접 배선·측정한 결과를 기록한다. 원자료는 대화에서 보고한
DMM 값과 도통음/동작 판정이다. DMM 화면, 계측기 모델·range, 사진과 연속 raw log는 repository에
보존되지 않았다. 따라서 PASS는 모두 `operator-reported` 범위다.

이번 실행이 확인한 범위:

- S0-A/S0-B 실제 한 가닥 단선 시 두 NC 경로의 독립성과 복구
- XL4015 #1의 두 개별 2P/26 AWG branch와 NUCLEO·ESP32 단독/동시 logic power
- XL4015 #2의 `J3/AUX_5V` 공급 경로와 #1 5 V rail 분리
- S0 released/pressed/released 및 S0-B wire-open에서 실제 VO617A conditioned `ESTOP_SENSE`

이번 실행에 포함하지 않은 범위:

- STM32 firmware latch, active PWM zero timing, reset/ARM/CMD sequence (`T-ESTOP-004`)
- MDD10A direct downstream B+ rail 차단과 실제 motor
- 26 AWG/connector의 startup current, voltage drop, 온도와 최종 정격 release
- LED-loop current, transient, optocoupler CTR margin과 장시간 동작
- 산업 안전 적합성 또는 single-fault-tolerant claim

## 2. As-built 전원 구조

XL4015 #1은 NUCLEO/ESP32 logic supply, XL4015 #2는 encoder와 S0-B optocoupler 입력의
`AUX_5V` supply다. 두 OUT+는 서로 연결하지 않고 Logic GND만 공통으로 사용한다.

```text
LiPo+ -> F1 -> S1 -> S1 OUT / VBAT_PROTECTED
                     |- K1 pin 30
                     |- XL4015 #1 IN+
                     |- XL4015 #2 IN+
                     `- F2 -> 6P.1 -> S0-A NC -> 6P.2 -> JESTOP.2

LiPo- -> PWR_GND -> XL4015 #1 IN-, XL4015 #2 IN-, MDD return/common ground
```

XL4015 #1 OUT+/OUT-에서는 26 AWG 두 cable pair가 바로 갈라져 NUC와 ESP의 별도 2P에
연결된다. Inline 4P connector는 없다. Board endpoint는 다음과 같다.

| Branch | 2P board landing | Board endpoint |
| --- | --- | --- |
| NUCLEO | pin 1 `C1,R31=GND`, pin 2 `C1,R32=5V_NUC` | `C9,R28=GND`, `C8,R28=E5V` |
| ESP32 | pin 1 `C1,R34=GND`, pin 2 `C1,R35=5V_ESP` | `C31,R26=GND`, `C32,R26=5V` |

Development dual-USB mode에서는 두 2P를 모두 기판에서 제거한다. Standalone mode에서는 모든
USB를 제거하고 NUCLEO를 `JP5=PWR-E5V`, `JP1=open`으로 둔다.

## 3. 무전원 검사

### 3.1 S0-A/S0-B wire-break independence

| Condition | Control `S1 OUT↔JESTOP.2` | Sense `JESTOP.3↔JESTOP.4` | Result |
| --- | --- | --- | --- |
| Normal baseline | continuity | continuity | PASS |
| S0-B conductor open | continuity 유지 | open | PASS |
| S0-B restored | continuity 유지 | continuity 복귀 | PASS |
| S0-A conductor open | open | continuity 유지 | PASS |
| Final restore | continuity 복귀 | continuity 유지 | PASS |

실제 분리 종단/cavity와 numeric Ω/OL은 기록되지 않아 `T-ESTOP-002`의 기능 subset만 통과한
것으로 판정한다.

### 3.2 XL4015 #1/#2 path

- #1 board path의 잔류전압, 도통과 rail isolation은 모두 사용자 보고 PASS다.
- #1 source harness의 각 2P pin 1→OUT-, pin 2→OUT+ 도통·극성과 +/− gross-short 부재도 PASS다.
- #2는 `OUT+→J3.1 C52,R1→R13.1 C52,R2`,
  `OUT-→J3.2 C51,R1→LOGIC_GND C15,R4`가 도통되고 #1 positive rail과 분리됨을 확인했다.
- 개별 Ω/OL과 사진은 제공되지 않았다.

## 4. XL4015 #1 powered board test

Board 연결 전 #1 출력과 두 branch endpoint는 `5.02 V`였다. USB를 모두 분리한 뒤 다음 순서로
측정했다.

| Mode | Measurements | Result |
| --- | --- | --- |
| NUCLEO only | OUT `4.97 V`, E5V `4.97 V`, STM32 3V3 `3.30 V`, ESP 5V `0 V` | PASS |
| ESP32 only | OUT `4.97 V`, ESP 5V `4.97 V`, ESP 3V3 `3.27 V`, NUC E5V `0 V` | PASS |
| Both | OUT `4.95 V`, NUC E5V `4.94 V`, STM32 3V3 `3.30 V`, ESP 5V `4.95 V`, ESP 3V3 `3.27 V` | PASS |
| Power removed | 모든 안내 rail `0 V` | PASS |

NUCLEO E5V는 모든 측정에서 공식 `4.75~5.25 V` 범위 안이다. Reset/brownout은 보고되지 않았고
사용자는 각 단계의 기능 확인도 통과했다고 보고했다. Current, branch drop, 온도와 사진이 없으므로
converter/connector/wire의 최종 load release는 아니다.

## 5. XL4015 #2 and conditioned `ESTOP_SENSE`

XL4015 #2는 board 연결 전 무부하 `5.03 V`, power-off `0 V`, 실제 J3 연결 후 `5.08 V`였다.
NUCLEO는 #1, optocoupler LED loop는 #2에서 공급했고 ESP32는 분리했다.

Probe는 `ESTOP_SENSE C29,R19`와 `LOGIC_GND C15,R4` 사이에 고정했다.

| State | Measured | Threshold result |
| --- | ---: | --- |
| S0 released / S0-B closed | `0.06 V` | LOW PASS |
| S0 pressed and latched | `3.27 V` | HIGH PASS |
| S0 manually released | `0.06 V` | LOW recovery PASS |
| S0-B conductor open | `3.27 V` steady | HIGH/open-fault PASS |

같은 전원 시험에서 STM32 3V3는 `3.30 V`였다. 이에 따른 CMOS bench threshold는
`LOW <= 0.99 V`, `HIGH >= 2.31 V`이며 네 측정은 요구한 LOW/HIGH 상태와 margin을 만족한다.
Pressed와 wire-open은 같은 asserted HIGH가 됐고 5 V direct level은 관찰되지 않았다.

사용자는 전원 제거, 분리한 S0-B 복구와 정상 LOW 복귀까지 통과했다고 보고했다. 복구 뒤 exact
전압과 LED-loop current는 기록하지 않았다. 따라서 conditioned voltage/function subset은 PASS지만
`T-ESTOP-003` 전체 evidence package는 `PARTIAL`이다.

## 6. Test-ID 판정

| Test ID | 2026-09-08 반영 상태 | 남은 범위 |
| --- | --- | --- |
| `T-ESTOP-002` | `FUNCTIONAL SUBSET PASS / EVIDENCE PARTIAL` | Exact removed cavity, numeric Ω/OL, photo/raw record |
| `T-ESTOP-003` | `CONDITIONED VOLTAGE SUBSET PASS / EVIDENCE PARTIAL` | LED-loop current, instrument/source metadata, repository photo/raw log |
| `T-ESTOP-004` | `NOT RUN IN THIS SESSION` | User-authored firmware test step, PC7/PWM capture, latch/reset/ARM/CMD sequence |
| `T-ESTOP-005A` | `PARTIAL` | Direct MDD10A downstream rail and combined PWM/no-restart cases |
| `T-ESTOP-007` | `BLOCKED` | Earlier gates and lifted-motor test setup |

Firmware source 수정, flash와 runtime은 수행하지 않았다. 다음 실행은 사용자가 코드를 직접 작성하고
설명을 따라가는 기존 학습 방식으로 `T-ESTOP-004`를 준비한다. MDD10A B+와 motor는 계속 분리한다.

## 7. 관련 문서

- [2026-09-08 progress](../progress/2026-09-08_progress.md)
- [Remaining bench gates](../plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md)
- [Physical E-stop requirements and verification plan](06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)
- [XL4015 #1 dual-board power distribution plan](../../09_Electrical_Design/11_XL4015_1_Dual_Board_Power_Distribution_Plan_2026-09-08_ko.md)
- [2026-09-05 report 24](24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md)
