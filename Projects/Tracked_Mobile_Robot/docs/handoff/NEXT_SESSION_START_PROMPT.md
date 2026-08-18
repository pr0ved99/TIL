# Next Session Start Prompt

새 Codex 대화창에서 아래 프롬프트를 그대로 붙여넣는다.

```text
Tracked_Mobile_Robot 프로젝트를 기존 작업 방식과 안전 기준을 유지하면서 이어서 진행해라.

프로젝트 경로:
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot

먼저 repository root C:\Users\eyh12\workspace\TIL 에서 아래 명령으로 실제 상태를 확인해라.

git status --short -- Projects/Tracked_Mobile_Robot
git log -1 --oneline -- Projects/Tracked_Mobile_Robot

기존 변경은 사용자 작업이므로 임의로 되돌리거나 덮어쓰지 마라. 사용자가 요청하기 전에는
commit/push하지 마라.

그다음 아래 파일을 실제 저장소에서 순서대로 처음부터 끝까지 읽어라.

1. Projects/Tracked_Mobile_Robot/PROJECT_MEMORY.md
2. Projects/Tracked_Mobile_Robot/docs/progress/2026-08-18_progress.md
3. Projects/Tracked_Mobile_Robot/docs/handoff/2026-08-18_k1_order_and_physical_estop_continuation_ko.md
4. Projects/Tracked_Mobile_Robot/09_Electrical_Design/10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md
5. Projects/Tracked_Mobile_Robot/docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md
6. Projects/Tracked_Mobile_Robot/docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md
7. Projects/Tracked_Mobile_Robot/docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md
8. Projects/Tracked_Mobile_Robot/docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md
9. Projects/Tracked_Mobile_Robot/01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md
10. Projects/Tracked_Mobile_Robot/01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md

과거 handoff는 역사 기록이다. 현재 continuation source는
2026-08-18_k1_order_and_physical_estop_continuation_ko.md다.

작업 방식:

- 사용자는 STM32/ESP32 firmware를 학습하면서 직접 타이핑한다. 작은 code block과 정확한
  삽입 위치를 먼저 알려주고, 사용자가 저장하면 실제 파일을 다시 읽어 검토한다.
- 사용자가 직접 수정을 위임하면 지정된 범위만 Codex가 수정한다.
- `확인해봐` 요청에는 대화만 보지 말고 실제 저장 파일을 다시 읽는다.
- Build/static test와 board runtime/electrical evidence를 구분한다.
- 배선, 전원, flash, reset과 계측은 사용자가 수행한다. 사전 조건, 예상 결과, 중지 조건과
  PASS 기준을 먼저 설명한다.

완료된 현재 기준선:

- UART Gate A/B/C와 필수 parser/recovery 벡터는 PASS했고 controlled test hook은 모두 `0U`,
  firmware contract는 `15/15`다.
- Permanent perfboard의 PC8/DIR1, PB6/PWM1, PC9/DIR2, PB7/PWM2에는 각각 10 kΩ pull-down이 있다.
- Motor-disconnected MDD10A-input final active test는 CH1/CH2 `19.049/19.058 kHz`, 약 10% duty,
  direction 전후 약 2 ms PWM-zero, expected MDD10A LED 순서로 PASS했다.
- Safe restore 뒤 final 5 s D0~D3 capture는 HIGH sample/transition 0으로 PASS했다.
- WHEELTEC MG540P30_12V 제조사 회신값은 motor당 12 V, rated 1.44 A, stall 9 A,
  rated 2.6 kgf·cm, stall 10 kgf·cm, PWM 5~20 kHz다.
- Two-motor envelope는 rated 2.88 A, simultaneous stall 18 A, 12.6 V 보수 환산 18.9 A다.
- TE K1 assembly를 2026-08-18 주문했다: V23134J1052D642/1393304-9 x1,
  VCF7-1000/1393310-4 x1, 280756-4 x2, 42281-1 x2. 결제 합계 31,154원이며
  판매 화면 발송 예정일은 2026-08-27이었다.
- K1 official catalog numerical gate는 18.9 A envelope에 PASS하지만 입고품 continuity,
  suppression, motor-load/voltage-drop/thermal과 rail-off는 아직 미검증이다.
- Prototype F1은 Littelfuse 0287010.PXCN 10 A ATOF 후보이며 wiring/short protection용이다.
  Locked-rotor motor protector로 입증한 것은 아니다.
- TE 280756-4 main terminal은 AWG 12~10용이므로 common main harness는 AWG 12가 우선이다.
  기존 AWG 14 fuse-holder lead를 이 terminal에 직접 crimp하면 안 된다.
- 실제 motor output, actual motor stop, Physical E-stop PASS 또는 산업 안전 인증은 아직 아니다.

현재 즉시 작업:

1. LiPo와 motor를 분리하고 모든 전원을 끈 상태에서 기존 F1 fuse-holder의 part marking,
   lead gauge, contact/terminal 구조, fuse 규격과 열화 여부를 확인한다.
2. AWG 12 대응 holder/wire/connector 조합을 확정하고 F1을 provisional에서 release candidate로 닫는다.
3. K1 입고 후 part marking을 대조하고 coil resistance 81~99 Ω, 무전원 NO open, socket/terminal
   fit과 suppression 구성을 확인한다.
4. 그 후에만 motor-disconnected T-ESTOP-001~005를 순서대로 수행한다.
5. 위 gate가 모두 PASS한 뒤 lifted single-motor 5~10% no-load 시험으로 이동한다.

중지 조건:

- 전원/모터가 연결된 상태에서 resistance나 continuity를 측정하려는 경우
- K1 NO contact가 무전원에서 short이거나 coil resistance가 81~99 Ω 밖인 경우
- holder/terminal이 AWG 12를 확실히 지원하지 않거나 손상·발열 흔적이 있는 경우
- `T-ESTOP-001~005` 전에 actual motor-energy를 인가하려는 경우

첫 답변에서는 실제 git status/HEAD, 완료된 기준선, 남은 evidence boundary와 F1 holder
무전원 검사 절차만 간단히 보고해라.
```
