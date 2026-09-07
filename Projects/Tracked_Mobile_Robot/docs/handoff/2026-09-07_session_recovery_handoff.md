# 2026-09-07 Session Recovery Handoff

## 현재 목표와 복원 범위

`Tracked Mobile Robot 3`의 마지막 요청은 작업 종료, 진행 내용 문서화와 Git 최신화였다.
중단된 세션의 사용자 보고·마지막 수정과 현재 저장소를 대조해 문서 정리를 이어받았다.
이번 세션에서는 새 하드웨어 시험, 전원 인가, 배선 변경이나 firmware flash를 수행하지 않았다.

- 저장소: `C:\Users\eyh12\workspace\TIL`
- 프로젝트: `Projects/Tracked_Mobile_Robot`
- 작업 브랜치: `agent/dual-encoder-bringup`
- 복원 시작 commit: `b354029` — P-04B/RevC WIP checkpoint
- 최신 하드웨어 결과: [2026-09-05 progress](../progress/2026-09-05_progress.md),
  [report 24](../verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md)
- 최신 문서 복원·검사: [2026-09-07 progress](../progress/2026-09-07_progress.md)
- 다음 bench 실행 정본: [remaining bench gates](../plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md)

새 세션의 첫 확인은 repository root에서 실행한다.

```powershell
git status --short -- Projects/Tracked_Mobile_Robot
git log -3 --oneline -- Projects/Tracked_Mobile_Robot
git branch -vv
```

기존 사용자 변경을 보존한다. 이번 closeout 이후의 작업은 해당 세션에서 승인된 범위로 진행한다.

## 완료와 미완료

| 영역 | 보존할 완료 결과 | 남은 범위 |
| --- | --- | --- |
| RevC/6P | 납땜, local 무전원 검사, 18 AWG first article/full harness, cavity `1-2=S0-A`, `3-4=S0-B`, `5-6=S2`, retention/truth table operator-reported PASS | K2 post-rework 직접 도통, explicit wire-removal/독립성, 사진·수치 원자료 |
| K2/K1 | Coil 극성 수정 후 12.24 V control-only pickup/self-hold/dropout, `JK1COIL.1=12.19 V`, S0/S1 nominal no-auto-restart PASS | Conditioned PC7, firmware/PWM, direct MDD10A downstream rail, load/thermal/timing |
| Firmware | P-03 300/500 ms scoped runtime와 P-04A UART applied-output 완료; P-04B reason/age와 direct-PC7 active/latch subset PASS | P-04B current-schema active reset reject/released reset success, final hook-0 reflash/no-command target runtime |
| Host checks | 2026-09-07 contract `25 + 2 + 2 = 29/29` PASS; bench hooks default `0U` | Host PASS는 board/electrical PASS가 아님 |
| Digital artifacts | FINAL/WIP/PDF 실제 파일 보존, 현재 size/hash를 VeroRoute README에 기록 | Corrected physical as-built와 source/export linkage 검증; current PDF mirror/scale 재검증 |
| Main power | K1 18 AWG coil, 14 AWG 30/87 assembly와 제한된 무부하 기능 PASS | `280756-4` AWG 12~10 대비 14 AWG 적합성, F1 `257`/ordered `287`, F2와 실제 부하 검증 |

전체 Physical E-stop은 `PARTIAL / NOT PASSED`다. Report 24는 사용자 보고와 세션 첨부사진 범위다.
K1-87의 정확한 OFF 전압, release time 또는 MDD10A B+ rail-off 실측을 새로 만들어 넣지 않는다.

## 보존할 배선·안전 계약

- NUCLEO-F446RE가 최종 output/safety authority이며 ESP32-S3가 production ingress다.
  USART1 production, USART2 bench-only와 MDD10A PWM+DIR 결정을 보존한다.
- TIM4 period `4420`, PB6/PB7 PWM, PC8/PC9 DIR의 각 `10 kΩ` pull-down과 current hooks `0U`를 보존한다.
- Dual USB는 UART TX/RX/GND만 연결한다. Buck-only는 USB를 모두 분리한다. USB+buck 동시 사용은 금지다.
- 실제 component-side K2는 pin 1(+)=`C37,R21/K2_COIL_P`, pin 12(-)=`C37,R19/GND`다.
  Pin `9->8`은 hold, `4->5`는 K1 enable이다. 재작업 후 정확한 pad continuity는 아직 기록해야 한다.
- S0-A 실제 경로는 `S1 OUT -> F2 -> 6P.1 -> S0-A -> 6P.2 -> JESTOP.2`다.
  Board `JESTOP.1`은 미사용이며 `.1-.2` jumper를 추가하지 않는다.
- [VeroRoute README](../../09_Electrical_Design/VeroRoute/README.md)의 FINAL/WIP/PDF는 현재 실물과
  일치가 검증된 제작 정본이 아니다. 새 corrected revision은 실제 도통 근거를 확보해 별도로 만든다.
- `FM-ESTOP-014/T-ESTOP-005B`는 S2 stuck/6P short residual risk로 post-MVP에 남는다.

## 다음 구체 작업

1. Remaining-gates Gate 0의 무전원 재진입과 0 V 확인 후 Gate 1 K2 corrected pad continuity를 기록한다.
2. Gate 2의 S0-A/S0-B explicit wire-removal/독립성·복구를 기록해 `T-ESTOP-002` 남은 범위를 닫는다.
3. 그 뒤에만 `T-ESTOP-003` conditioned VO617A/PC7 LOW-HIGH/open,
   `T-ESTOP-004` firmware/PWM latch 순서로 진행한다.
4. `T-ESTOP-001~004` 모두 PASS 뒤 motor는 계속 분리하고 full `T-ESTOP-005A` direct MDD rail을 검증한다.
5. 위 motor-disconnected gate 전체가 끝난 뒤에만 lifted motor와 `T-ESTOP-007`로 이동한다.

배선·전원·flash·실측은 사용자가 수행한다. 실행 전 precondition, expected result, stop condition과
PASS 기준을 현재 정본에서 확인한다. 현재 실제 전원 상태는 이 문서로 확인된 것으로 간주하지 않는다.
Firmware 학습은 작은 블록과 정확한 삽입 위치 안내 → 사용자 저장 → 실제 파일 재검토 방식을 유지한다.
