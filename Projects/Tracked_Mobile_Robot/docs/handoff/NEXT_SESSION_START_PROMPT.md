# Next Session Start Prompt

새 대화창에서 아래 프롬프트를 사용한다. 최신 문서 복원은 2026-09-07, 최신 하드웨어 결과는
2026-09-05다. 상세 실측·역사 기록은 연결 문서에 보존한다.

```text
Tracked_Mobile_Robot 프로젝트를 기존 학습 방식과 안전 기준에 따라 이어서 진행해라.

저장소: C:\Users\eyh12\workspace\TIL
프로젝트: Projects/Tracked_Mobile_Robot
현재 작업 브랜치: agent/dual-encoder-bringup

먼저 repository root에서 실제 상태를 확인해라.

git status --short -- Projects/Tracked_Mobile_Robot
git log -3 --oneline -- Projects/Tracked_Mobile_Robot
git branch -vv

기존 변경을 임의로 되돌리거나 덮어쓰지 마라. Commit/push는 해당 세션의 사용자 요청 범위에
따라 진행한다. 이전 closeout의 Git 요청을 모든 미래 작업에 대한 포괄 승인으로 해석하지 마라.

시작할 때 다음 파일을 읽어 현재 상태를 복원해라.

1. Projects/Tracked_Mobile_Robot/AGENTS.md
2. Projects/Tracked_Mobile_Robot/PROJECT_MEMORY.md
3. Projects/Tracked_Mobile_Robot/docs/progress/README.md와 최신 progress
4. Projects/Tracked_Mobile_Robot/docs/handoff/2026-09-07_session_recovery_handoff.md
5. Projects/Tracked_Mobile_Robot/README.md

Bench 작업을 시작할 때 다음 정본을 읽어라.

- docs/plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md
- docs/progress/2026-09-05_progress.md
- docs/verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md
- docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md

위 경로는 프로젝트 기준이다. 작업에 필요한 한국어 architecture/requirements 문서를 추가로
읽고 수용 기준을 확인한다. 이전 progress 전체와 세션 원문을 매번 한꺼번에 읽지 않는다.
2026-09-01/03은 역사 조립 기록이며 최신 배선 지시가 아니다.

현재 완료 범위:

- RevC 납땜/local 무전원 검사, 18 AWG 6P first article/full harness와 retention/truth table은
  operator-reported PASS다. Cavity는 1-2=S0-A NC, 3-4=S0-B NC, 5-6=S2 NO다.
- K2 coil 역극성 수정 후 12.24 V control-only S2 self-hold, JK1COIL.1=12.19 V,
  K1 enable/S0 dropout, S0 release와 S1 OFF->ON nominal no-auto-restart는 PASS다.
- MDD10A B+와 motor는 해당 시험에서 분리됐다. Conditioned PC7, firmware/PWM, 실제 MDD
  downstream rail과 motor 검증은 미완료이며 전체 Physical E-stop은 PARTIAL/NOT PASSED다.
- Current host/static은 2026-09-07 재확인 29/29다. Current bench hooks는 모두 0U다.
  P-04B current-schema active reset reject/released reset success와 최종 hook-0 target
  reflash/no-command runtime은 OPEN이다. Host PASS를 target/electrical PASS로 확대하지 마라.

보존할 계약:

- STM32 최종 safety authority, ESP32-S3 단일 production ingress, USART1 production,
  USART2 bench-only, MDD10A PWM+DIR와 TIM4 period 4420을 유지한다.
- 실제 K2 pin 1(+)=C37,R21/K2_COIL_P, pin 12(-)=C37,R19/GND다.
  9->8은 self-hold, 4->5는 K1 enable이다. Post-rework direct pad continuity는 아직 남아 있다.
- S0-A는 S1 OUT -> F2 -> 6P.1 -> S0-A -> 6P.2 -> JESTOP.2다.
  Board JESTOP.1은 미사용이며 .1-.2 jumper를 추가하지 않는다.
- FINAL/WIP/PDF는 K2 corrected as-built가 검증된 제작 정본이 아니다. 현재 hash는
  09_Electrical_Design/VeroRoute/README.md를 확인한다.
- USB와 buck를 동시에 연결하지 않는다. Dual USB는 UART TX/RX/GND만 연결한다.
- K1 as-built main lead 14 AWG와 280756-4 AWG 12~10 적합성, F1 257/ordered 287 identity,
  F2 coordination 및 load/thermal/timing은 OPEN이다.
- FM-ESTOP-014/T-ESTOP-005B는 post-MVP residual risk로 유지한다.

즉시 다음 작업:

Remaining-gates Gate 0 무전원 재진입 -> Gate 1 K2 post-rework continuity -> Gate 2 explicit
S0-A/S0-B wire-removal/독립성을 먼저 닫는다. 그 뒤 T-ESTOP-003 conditioned sense,
T-ESTOP-004 firmware/PWM로 진행한다. T-ESTOP-001~004 모두 PASS 전에는 MDD10A B+를
재연결하지 않는다. Full motor-disconnected T-ESTOP-005A PASS 전에는 actual motor를 연결하지 않는다.

학습과 실행 방식:

- Firmware는 작은 코드 블록과 정확한 위치 안내 -> 사용자 저장 -> 실제 파일 재검토가 기본이다.
  직접 편집을 위임받으면 해당 범위만 수정한다.
- 배선/전원/flash/reset/실측은 사용자가 수행한다. 실행 전에 precondition, expected result,
  stop condition과 PASS 기준을 설명한다. 실제 현재 전원 상태를 과거 문서만으로 추정하지 마라.
- 측정 없이 수치나 PASS를 만들지 않는다. 검증된 항목을 반복할 때는 변경·실패 등 이유가 있어야 한다.
- 의미 있는 작업 뒤 dated progress, PROJECT_MEMORY와 필요한 index/handoff를 최신화한다.
```
