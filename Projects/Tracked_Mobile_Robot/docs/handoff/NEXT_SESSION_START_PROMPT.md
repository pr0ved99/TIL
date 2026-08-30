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
2. Projects/Tracked_Mobile_Robot/docs/progress/2026-08-30_progress.md
3. Projects/Tracked_Mobile_Robot/docs/progress/2026-08-29_progress.md
4. Projects/Tracked_Mobile_Robot/docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md
5. Projects/Tracked_Mobile_Robot/docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md
6. Projects/Tracked_Mobile_Robot/docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md
7. Projects/Tracked_Mobile_Robot/docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md
8. Projects/Tracked_Mobile_Robot/docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md
9. Projects/Tracked_Mobile_Robot/docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md
10. Projects/Tracked_Mobile_Robot/docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md
11. Projects/Tracked_Mobile_Robot/docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md
12. Projects/Tracked_Mobile_Robot/docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md
13. Projects/Tracked_Mobile_Robot/01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md
14. Projects/Tracked_Mobile_Robot/01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md
15. Projects/Tracked_Mobile_Robot/01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md
16. Projects/Tracked_Mobile_Robot/09_Electrical_Design/10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md

과거 handoff는 역사 기록이다. 현재 continuation source는
2026-08-30_progress.md다. 2026-08-29_progress.md와 report 23은 바로 앞 P-04B runtime
checkpoint이고 report 22는 P-04A baseline이며 reports
19/20/21은 hardware/P-03 evidence다.
2026-08-26 pre-arrival schedule은 역사 기록이다.
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

- UART Gate A/B/C와 필수 parser/recovery 벡터는 PASS했고 current source의 controlled test hook은
  모두 `0U`다. Current host/static test는 firmware contract `25/25` + mapper vectors `2/2` +
  UART frame contract `2/2`, 합계 `29/29`다. Historical `15/15`, 2026-08-24 `20/20`,
  P-02B `23/23`, P-02C-1 `24/24`, P-02C-2 `25/25`, P-03 `26/26`, P-04A `27/27`,
  P-04B reason/age `28/28` checkpoint와 혼동하지 마라. Historical hook-0 isolated STM32/ESP32
  build와 current default-off reset-harness ESP32 isolated build는 PASS했고, 변경 source의 target
  flash/runtime restore는 아직 OPEN이다.
- Permanent perfboard의 PC8/DIR1, PB6/PWM1, PC9/DIR2, PB7/PWM2에는 각각 10 kΩ pull-down이 있다.
- Motor-disconnected MDD10A-input final active test는 CH1/CH2 `19.049/19.058 kHz`, 약 10% duty,
  direction 전후 약 2 ms PWM-zero, expected MDD10A LED 순서로 PASS했다.
- Safe restore 뒤 final 5 s D0~D3 capture는 HIGH sample/transition 0으로 PASS했다.
- PC7은 internal pull-up, active HIGH/open `ESTOP_SENSE`로 구현됐다. Motor/LiPo/K1을 연결하지
  않은 historical old-schema direct PC7 runtime에서 open/HIGH FAULT latch, ARM/CMD와 active
  reset reject, LOW 복구 뒤 latch 유지, explicit `ESTOP_RESET` 후 `DISARMED` 복귀를 확인했다. 이는 VO617/S0/K1
  통합 PASS가 아니다.
- WHEELTEC MG540P30_12V 제조사 회신값은 motor당 12 V, rated 1.44 A, stall 9 A,
  rated 2.6 kgf·cm, stall 10 kgf·cm, PWM 5~20 kHz다.
- Two-motor envelope는 rated 2.88 A, simultaneous stall 18 A, 12.6 V 보수 환산 18.9 A다.
- TE K1 assembly의 exact relay/socket/terminal을 대조했고 coil `89.5 ohm`, 무여자 NO open과
  coil-contact gross-short screen이 무전원 PASS했다. 이는 정격 절연시험이 아니다. Official catalog numerical gate도 18.9 A
  envelope에 PASS하지만 crimped retention, suppression, powered pickup/dropout,
  motor-load/voltage-drop/thermal과 rail-off는 아직 미검증이다.
- 입고 F1 holder는 Littelfuse 표시와 `GXL 12AWG SCL -LF-` lead가 있고, fuse에는
  `LITTELFUSE/257/32V/10`, 측면 `2340`이 있다. 무전원 외관/continuity/movement precheck는
  PASS했다. 주문 `0287010.PXCN` 287 ATOF와 `257` 각인의 identity/curve, load voltage drop,
  thermal/interruption과 locked-rotor protection은 아직 미확정이다.
- K2 `TX2-12V` 두 개는 coil `1.025/1.035 kΩ`, 무전원 `3-4`/`10-9` closed,
  `4-5`/`9-8` open과 coil-contact gross-short screen으로 incoming precheck PASS했다. Powered
  pickup/dropout은 P6KE clamp를 올바르게 설치하고 current-limited supply/coil 연결을 검토한 뒤에만 한다.
- VO617A-3용 후보 저항은 `670.1 Ω`과 `9.97 kΩ`을 선별했다. VO617A-3는 pin 1->2 diode
  `955`, reverse OL과 input-output gross-short screen이 무전원 PASS했다. 정격 절연과 실제 5 V S0-B/PC7 path는 미검증이다.
- S0 body `SF2ER-E2R2B`, actuator `AE21R`, `SFEA-CB` NC block 두 개를 확인했고 released
  closed/pressed-latched open/turn-release recovery와 cross-channel gross-short screen이 무전원 PASS했다.
  주문 suffix `-A` trace와 integrated path는 open이다.
- F2는 operator-reported continuity/movement screen만 PASS했다. Exact marking과 powered
  coordination은 open이다.
- 6P 품목은 완성 harness가 아니라 loose housings/terminals/seals/secondary locks와 별도
  18 AWG wire다. Inventory/visual만 PASS했고 cavity map, crimp, 6x6 intended-continuity/unintended-open, retention은 open이다.
- `VH-30J`/`WX-03B` crimp-tool set는 2026-08-30 사용자 보고로 도착했다. Exact set/visual
  inspection, die fit과 spare 6P terminal first-article crimp/pull/continuity/retention은 NOT RUN이다.
  K1 `280756-4` 두 개를 practice terminal로 사용하지 않는다.
- S2 `ABW110G`와 `P6KE16CA-E3/54` x3는 도착했다. S2 `3–4` momentary-NO truth table과
  P6KE exact `CA` marking/양방향 gross-short screen은 무전원 PASS다. Crimp tool 도착은
  기록했지만 위 first-article 결과가 없으므로 6P는 계속 unassembled다.
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
  accepted ARM의 default 300 ms/current-tick first-CMD window 재시작을 구현했다. Historical
  P-03 canonical은 `26/26`; 32-object forced ARM build는 exit `0`, 진단 0건, ELF `text=29268`,
  `data=172`, `bss=2832`다. 2026-08-28 P-03 current-default target run은 timeout-to-`DISARMED`,
  CMD-only reject, ARM-only old-command 미복원, new ARM+CMD recovery와 PB6/PB7 약
  19.06 kHz/5% burst를 PASS했고 all-hooks-`0U` D0~D3 10 s all-LOW로 복구했다. Canonical
  `REQ-SAFE-004 timeout_ms=500` run03도 same-run D4/D5 UART+D0~D3에서 timeout/reject/ARM-only
  expiry/fresh recovery/final safe tail을 PASS했다. Operator dual-reset release의 RST net 자체는
  미계측이다. Post-run run04는 source hook `0U`, host/static `26/26`, safe build/flash,
  script-disabled startup DISARM/PING/READY, ARM/CMD TX 0회, 약 14.3 s/144 TEL의
  `DISARMED/zero`와 D0~D3 10 s all-LOW를 PASS했다. Exact controlled BIN linkage, clean
  electrical cold-start와 actual motor는 open이다.
- P-04A는 TEL `left_pwm/right_pwm`를 motor-output software cache의 signed permille과 연결하고
  ESP32 parser/log까지 확장했다. STM32 incremental build는 0 errors/0 warnings, ELF
  `29428/172/2832`다. Controlled run01의 active 7 TEL은 `50/50`, ARM-only 5개와 DISARMED
  37개는 `0/0`이었고, hook-0 run02는 script disabled, ARM/CMD 0회와 TEL 50/50
  `DISARMED/0/0`을 PASS했다. `50`은 50 permille=5% target이며 measured physical PWM이 아니다.
  Reverse/asymmetric sign, exact binary linkage와 battery는 open이다.
- P-04B는 STM TEL과 ESP strict parser/log에 `reason/command_age_ms`를 연결했다. Controlled run02는
  no-CMD sentinel, successful-CMD-only age reset, 500 ms `CMD_TIMEOUT`, ARM-only timeout과 fresh-CMD
  recovery를 PASS했다. 서로 독립인 direct-PC7 run03/run04는 각각 `ESTOP_ACTIVE`와
  `ESTOP_ACTIVE -> ESTOP_LATCHED`를 보였고 모든 FAULT TEL의 software PWM은 `0/0`이었다.
  새 schema의 active reset reject와 released reset success는 NOT RUN이다. 2026-08-30 default-`0U`
  reset closeout harness를 추가해 current canonical `29/29`과 ESP32 isolated build를 PASS했다.
  이 harness는 active에서 `ESTOP_RESET` 1회, latched에서 1회만 보내고 safe TEL을 확인하도록
  준비했을 뿐이다. Active reset `ERR`, release 뒤 reset `ACK` + `DISARMED/ESTOP_RESET/PWM 0/0`
  및 `VECTOR DONE`, target flash/no-command safe runtime은 OPEN이다. 따라서 P-04B는 `PARTIAL`이다.
- 실제 motor output, actual motor stop, Physical E-stop PASS 또는 산업 안전 인증은 아직 아니다.

현재 즉시 작업:

1. `P-01`은 ADR-015로 완료했다: ESP32-S3 단일 production ingress, STM32 USART1 production,
   USART2 bench-only, direct dual-owner 금지와 source-loss recovery 정책을 보존한다.
2. Custom PC adapter plate는 2026-08-26 사용자 보고 기준 이미 수령했다. Exact RevB source
   identity와 치수/chassis/module fit은 집 `H-01`에서 확인하고, 카페에서는 이를 추정하지 않는다.
3. `P-02A~P-02C-2` mapper, signed adapter와 production caller source/static/full-build는
   완료했다. Historical `23/23`, `24/24`, `25/25`을 보존한다.
4. `P-03`의 current-default 300 ms target runtime과 당시 safe restore는 report 20에서 완료했다.
   Canonical `REQ-SAFE-004` 500 ms target acceptance는 report 21에서 완료했다. Run03 뒤 source
   hook `0U`, 당시 host/static `26/26`과 run04 safe build/flash/UART/all-LOW runtime restore까지 PASS했다.
5. `P-04A` applied-output TEL/ESP parser와 hook-0 safe runtime은 report 22에서 완료했다.
   `P-04B` reason/command-age와 direct-PC7 active/latch UART subset은 report 23에서 PASS했지만
   전체 상태는 PARTIAL이다. 다음은 motor/LiPo disconnected 상태의 active reset reject와 released
   reset success를 같은 새 schema로 기록한 뒤 all-hooks-`0U` reflash/no-command safe runtime을
   닫는 것이다. 그 뒤 `P-05` battery ADC/low-voltage policy와 `P-06` wheel-distance/1 m odometry로 간다.
6. 일정 후반의 `P-08/P-09`: F1 `257`/ordered `287` identity와 S1 basis, incoming checklist와
   T-ESTOP capture sheet를 닫는다.
7. Report 19의 K1/S0/S2/VO617/P6KE/F2 무전원 screen은 보존한다. 집에서 도착한 tool의 exact
   `VH-30J`/`WX-03B` set와 die를 먼저 확인하고, 6P molded cavity number/orientation을 비파괴
   기록한 뒤 spare 6P terminal first article을 visual/pull/continuity/housing-retention으로 확인한다.
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
- 건강한 S2 release-open과 6P intended-pair continuity/unintended-pair open을 확인하지 않고 powered `T-ESTOP-005A`를 시작하려는 경우
- `T-ESTOP-001~004 + T-ESTOP-005A` 전에 actual motor-energy를 인가하려는 경우

첫 답변에서는 실제 git status/HEAD, current `29/29`, P-04B reason/command-age와 active/latch
UART subset, default-`0U` reset harness source/static/ESP isolated build PASS, active reset
`ERR`/released reset `ACK`+TEL+vector 및 target flash/runtime OPEN, 남은 physical evidence
boundary와 arrived-but-unverified crimp-tool/6P blocker를 간단히 보고해라. 다음 작업은 집에서
motor/LiPo disconnected P-04B reset/recovery와 hook-0 safe restore, 또는 tool inspection 뒤
spare-terminal first-article crimp다.
```
