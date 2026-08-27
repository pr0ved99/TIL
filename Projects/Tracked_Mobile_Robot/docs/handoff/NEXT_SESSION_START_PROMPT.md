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
2. Projects/Tracked_Mobile_Robot/docs/progress/2026-08-28_progress.md
3. Projects/Tracked_Mobile_Robot/docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md
4. Projects/Tracked_Mobile_Robot/docs/plans/2026-08-26_Pre_Arrival_Schedule_ko.md
5. Projects/Tracked_Mobile_Robot/docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md
6. Projects/Tracked_Mobile_Robot/docs/verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md
7. Projects/Tracked_Mobile_Robot/docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md
8. Projects/Tracked_Mobile_Robot/01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md
9. Projects/Tracked_Mobile_Robot/01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md
10. Projects/Tracked_Mobile_Robot/01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md
11. Projects/Tracked_Mobile_Robot/docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md
12. Projects/Tracked_Mobile_Robot/docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md
13. Projects/Tracked_Mobile_Robot/09_Electrical_Design/10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md

과거 handoff는 역사 기록이다. 현재 continuation source는
2026-08-28_progress.md와 report 19, 2026-08-26_Pre_Arrival_Schedule_ko.md다.
2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md는 authoritative scope/sequence다.
Report 18은 direct-PC7/K2/F1/resistor의 앞선 hardware evidence baseline이다.

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
  current host/static test는 firmware contract `22/22` + mapper vectors `2/2` + UART frame
  contract `2/2`, 합계 `26/26`다. Historical `15/15`, 2026-08-24 `20/20`, P-02B
  `23/23`, P-02C-1 `24/24`, P-02C-2 `25/25` checkpoint와 혼동하지 마라.
- Permanent perfboard의 PC8/DIR1, PB6/PWM1, PC9/DIR2, PB7/PWM2에는 각각 10 kΩ pull-down이 있다.
- Motor-disconnected MDD10A-input final active test는 CH1/CH2 `19.049/19.058 kHz`, 약 10% duty,
  direction 전후 약 2 ms PWM-zero, expected MDD10A LED 순서로 PASS했다.
- Safe restore 뒤 final 5 s D0~D3 capture는 HIGH sample/transition 0으로 PASS했다.
- PC7은 internal pull-up, active HIGH/open `ESTOP_SENSE`로 구현됐다. Motor/LiPo/K1을 연결하지
  않은 direct PC7 runtime에서 open/HIGH FAULT latch, ARM/CMD와 active reset reject, LOW 복구
  뒤 latch 유지, explicit `ESTOP_RESET` 후 `DISARMED` 복귀를 확인했다. 이는 VO617/S0/K1
  통합 PASS가 아니다.
- WHEELTEC MG540P30_12V 제조사 회신값은 motor당 12 V, rated 1.44 A, stall 9 A,
  rated 2.6 kgf·cm, stall 10 kgf·cm, PWM 5~20 kHz다.
- Two-motor envelope는 rated 2.88 A, simultaneous stall 18 A, 12.6 V 보수 환산 18.9 A다.
- TE K1 assembly의 exact relay/socket/terminal을 대조했고 coil `89.5 ohm`, 무여자 NO open과
  coil/contact cross-isolation이 무전원 PASS했다. Official catalog numerical gate도 18.9 A
  envelope에 PASS하지만 crimped retention, suppression, powered pickup/dropout,
  motor-load/voltage-drop/thermal과 rail-off는 아직 미검증이다.
- 입고 F1 holder는 Littelfuse 표시와 `GXL 12AWG SCL -LF-` lead가 있고, fuse에는
  `LITTELFUSE/257/32V/10`, 측면 `2340`이 있다. 무전원 외관/continuity/movement precheck는
  PASS했다. 주문 `0287010.PXCN` 287 ATOF와 `257` 각인의 identity/curve, load voltage drop,
  thermal/interruption과 locked-rotor protection은 아직 미확정이다.
- K2 `TX2-12V` 두 개는 coil `1.025/1.035 kΩ`, 무전원 `3-4`/`10-9` closed,
  `4-5`/`9-8` open과 coil-contact isolation으로 incoming precheck PASS했다. Powered
  pickup/dropout은 P6KE clamp 도착 뒤에만 한다.
- VO617A-3용 후보 저항은 `670.1 Ω`과 `9.97 kΩ`을 선별했다. VO617A-3는 pin 1->2 diode
  `955`, reverse OL과 input-output isolation이 무전원 PASS했다. 실제 5 V S0-B/PC7 path는 미검증이다.
- S0 body `SF2ER-E2R2B`, actuator `AE21R`, `SFEA-CB` NC block 두 개를 확인했고 released
  closed/pressed-latched open/turn-release recovery와 cross-channel isolation이 무전원 PASS했다.
  주문 suffix `-A` trace와 integrated path는 open이다.
- F2는 operator-reported continuity/movement screen만 PASS했다. Exact marking과 powered
  coordination은 open이다.
- 6P 품목은 완성 harness가 아니라 loose housings/terminals/seals/secondary locks와 별도
  18 AWG wire다. Inventory/visual만 PASS했고 cavity map, crimp, 6x6 isolation, retention은 open이다.
- `VH-30J`/`WX-03B` crimp-tool set는 주문했지만 미도착·미검증이다. K1 `280756-4` 두 개를
  practice terminal로 사용하지 않는다.
- 아직 도착하지 않은 electrical parts는 S2 `ABW110G`와 `P6KE16CA-E3/54` x3이고,
  crimp-tool set도 미도착이다.
- 현재 RevB는 S2 stuck-closed 또는 S2 6P pair short에서 S0 release/control-power restore 시
  K2/K1과 motor rail이 자동 재인가될 수 있다. `FM-ESTOP-014` design gap이며 firmware
  `DISARMED`/PWM zero는 hardware no-auto-reenable의 대체가 아니다.
- 2026-08-25에 nominal healthy-S2/harness 시험을 MVP `T-ESTOP-005A`, 위 stuck/short
  single-fault 시험을 post-MVP `T-ESTOP-005B`로 분리했다. 위험은 residual risk로 계속
  추적하며 single-fault tolerance나 산업 안전을 주장하지 않는다.
- P-02B HAL-independent mapper와 P-02C-1 signed adapter에 이어 P-02C-2 production
  `handle_cmd()` caller를 연결했다. 순서는 validation -> `ARMED` -> E-stop -> mapper(cap 10%) ->
  E-stop -> mutually exclusive raw/signed output -> E-stop -> success-only state commit/ACK다.
  Mapper/output 실패는 stop-all, stored `vx/w` zero, ERR, return으로 닫힌다. 이는 historical
  `25/25` P-02C-2 checkpoint다.
- P-03A/P-03B는 pre-RX timeout helper의 stop-all -> stored `vx/w` zero -> `DISARMED`와
  accepted ARM의 default 300 ms/current-tick first-CMD window 재시작을 구현했다. Current
  canonical은 `26/26`; 32-object forced ARM build는 exit `0`, 진단 0건, ELF `text=29268`,
  `data=172`, `bss=2832`다. Flash/board/PWM runtime은 없고 TEL PWM fields는 zero placeholder다.
- 실제 motor output, actual motor stop, Physical E-stop PASS 또는 산업 안전 인증은 아직 아니다.

현재 즉시 작업:

1. 다음 세션은 집을 우선한다. `P-01`은 ADR-015로 완료했다: ESP32-S3 단일 production ingress, STM32 USART1 production,
   USART2 bench-only, direct dual-owner 금지와 source-loss recovery 정책을 보존한다.
2. Custom PC adapter plate는 2026-08-26 사용자 보고 기준 이미 수령했다. Exact RevB source
   identity와 치수/chassis/module fit은 집 `H-01`에서 확인하고, 카페에서는 이를 추정하지 않는다.
3. `P-02A~P-02C-2` mapper, signed adapter와 production caller source/static/full-build는
   완료했다. Historical `23/23`, `24/24`, `25/25`을 보존한다.
4. `P-03A/P-03B` source/static/full-build는 완료했다. 집 H-02에서 motor/LiPo-disconnected
   timeout -> `DISARMED` -> pre-reARM CMD reject -> new ARM -> new CMD target regression을
   수행한다. 현재 ESP controlled script의 1000 ms step은 300 ms first-CMD window보다 길므로
   target test 전 ARM->CMD cadence를 300 ms 미만으로 조정한다.
5. 다음 카페 firmware 작업은 `P-04~P-06`: 실제 TEL fields, battery ADC/low-voltage policy와
   wheel-distance/1 m odometry path다. Build/static 결과를 board evidence로 쓰지 않는다.
6. 일정 후반의 `P-08/P-09`: F1 `257`/ordered `287` identity와 S1 basis, incoming checklist와
   T-ESTOP capture sheet를 닫는다.
7. Report 19의 K1/S0/VO617/F2 무전원 screen은 보존한다. 집에서 6P molded cavity number와
   orientation을 비파괴 기록하고, tool 도착 뒤 spare 6P terminal first article을 visual/pull/
   housing-retention으로 확인한다. S2/P6KE는 도착 뒤 동일한 incoming 절차를 수행한다.
8. Direct PC7-GND 임시 jumper 제거, conditioned path, clamp/internal suppression과
   current-limited K2/K1 pickup/dropout을 motor-disconnected 상태에서 검증한다.
9. `T-ESTOP-001~004 + T-ESTOP-005A`를 PASS한 후에만 lifted single-motor 5~10% no-load와
   `T-ESTOP-007`로 이동한다. `FM-ESTOP-014/T-ESTOP-005B`는 post-MVP residual-risk V-cycle이다.

중지 조건:

- 전원/모터가 연결된 상태에서 resistance나 continuity를 측정하려는 경우
- K1 NO contact가 무전원에서 short이거나 coil resistance가 81~99 Ω 밖인 경우
- F1 identity/curve가 닫히지 않았거나 holder/terminal이 AWG 12를 확실히 지원하지 않는 경우
- Direct PC7-GND jumper가 남은 채 VO617/S0-B path를 시험하려는 경우
- Clamp/internal suppression을 확인하기 전에 K1/K2 coil을 energize하려는 경우
- 건강한 S2 release-open과 6P pair isolation을 확인하지 않고 powered `T-ESTOP-005A`를 시작하려는 경우
- `T-ESTOP-001~004 + T-ESTOP-005A` 전에 actual motor-energy를 인가하려는 경우

첫 답변에서는 실제 git status/HEAD, 2026-08-28 continuation, 현재 evidence boundary와
pending parts를 간단히 보고하고 집이면 P-03 target runtime, 카페면 그 준비표부터 시작해라.
```
