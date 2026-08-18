# Next Session Start Prompt

새 Codex 대화창에서 아래 프롬프트를 그대로 붙여넣는다.

```text
Tracked_Mobile_Robot 프로젝트를 기존 작업 방식과 안전 기준을 유지하면서 이어서 진행해라.

프로젝트 경로:
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot

대답하기 전에 repository root C:\Users\eyh12\workspace\TIL 에서 다음 명령으로
현재 변경 상태부터 확인해라.

git status --short -- Projects/Tracked_Mobile_Robot

기존 변경 파일은 사용자의 작업이므로 임의로 되돌리거나 덮어쓰지 마라. 사용자가 요청하기
전에는 commit/push하지 마라.

그 다음 아래 문서를 순서대로 실제 파일에서 처음부터 끝까지 읽어라.

1. Projects/Tracked_Mobile_Robot/PROJECT_MEMORY.md
2. Projects/Tracked_Mobile_Robot/docs/progress/2026-08-12_progress.md
3. Projects/Tracked_Mobile_Robot/docs/handoff/2026-08-13_power_and_physical_estop_session_ko.md
4. Projects/Tracked_Mobile_Robot/docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md
5. Projects/Tracked_Mobile_Robot/docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md
6. Projects/Tracked_Mobile_Robot/docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md
7. Projects/Tracked_Mobile_Robot/09_Electrical_Design/README.md
8. Projects/Tracked_Mobile_Robot/01_System_Architecture/21_Physical_EStop_Architecture_ko.md
9. Projects/Tracked_Mobile_Robot/01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md
10. Projects/Tracked_Mobile_Robot/01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md
11. Projects/Tracked_Mobile_Robot/01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md

과거 handoff를 현재 지시보다 우선하지 마라. 현재 continuation source는
2026-08-13_power_and_physical_estop_session_ko.md다.

작업 방식:

- 사용자는 STM32/ESP32 firmware를 학습하면서 직접 타이핑한다. 작은 code block과 정확한
  삽입 위치를 먼저 알려주고, 사용자가 저장하면 실제 파일을 다시 읽어 검토한다.
- 사용자가 직접 수정을 위임하면 지정된 범위만 Codex가 수정한다.
- `확인해봐` 요청에는 대화만 보지 말고 실제 저장 파일을 다시 읽는다.
- Build/static test와 board runtime/electrical evidence를 구분한다.
- 배선, 전원, flash, reset과 계측은 사용자가 수행한다. 사전 조건, 예상 결과, 중지 조건과
  PASS 기준을 먼저 설명한다.

완료된 현재 기준선:

- UART Gate A/B, T-BRIDGE-007/008 required runtime PASS.
- 모든 ESP32/STM32 controlled test hook `0U`, firmware contract `15/15` PASS.
- Motor-output safety 뒤 final UART는 exact DISARM ACK/PING/PONG/READY, post-READY TEL
  155/155 DISARMED/zero over 15.4 s, ARM/CMD/retry/failure 0으로 PASS.
- 2026-08-03의 20.1005 kHz는 historical baseline이다. Vendor `5~20 kHz` 상한 margin을 위해
  final nominal을 19 kHz로 변경했고 permanent perfboard MDD10A-input에서 CH1/CH2
  19.049/19.058 kHz, 약 10%, direction 전후 약 2 ms PWM-zero를 PASS했다.
- Active DISARM은 UART frame end부터 PWM last edge까지 23.50 us MCU-pin baseline PASS.
- Command timeout 300 ms는 UART-calibrated frame-end-to-last-edge 약 299.690 ms, 이후
  약 8.939 s no-reactivation으로 scoped PASS.
- Software fault는 marker 뒤 expected next PWM pulse 억제와 약 2.052 s latch PASS.
  Last fall이 marker보다 5.25 us 앞선 것은 LOW phase 때문이므로 fault latency가 아니다.
- External reset 첫 시험은 네 motor input이 약 159 ms HIGH여서 FAIL.
- PC8/DIR1, PB6/PWM1, PC9/DIR2, PB7/PWM2 각각 영구 10 kΩ to GND가 반영된 만능기판에서
  continuity, power-up/NRST all-LOW와 final hook-0 5 s transition/HIGH sample 0을 PASS했다.
- 이 판정은 motor-disconnected MDD10A-input scope다. MDD10A motor output, actual motor,
  Physical E-stop 또는 산업 안전 인증을 입증하지 않는다.

현재 safe artifact checkpoint:

- STM32 ELF: 1,241,208 bytes, SHA-256
  3B80E7A6A465545A0324AA7CD83503C95E387DE203374548BCA368FDC7DA831B
- ESP32 BIN: 176,656 bytes, SHA-256
  8F46810367A370A080781A09E52B04F3DF348CF9F3430ABA536686DFFEF033C3
- Raw runtime에 flash transcript와 artifact hash가 내장되지 않아 exact board-artifact
  identity와 physical setup provenance는 독립 증명되지 않는다.

고정 안전·배선 결정:

- ESP GPIO17 TX -> STM32 PA10 RX, ESP GPIO18 RX <- STM32 PA9 TX, common GND,
  115200 8-N-1.
- 두 board를 각각 USB로 공급할 때 board 간 5 V/VBUS/VIN을 연결하지 않는다.
- STM32가 parser, timeout, motor output, encoder와 final safety authority다.
- 각 motor control signal은 permanent external 10 kΩ pull-down to GND가 필요하다.
- K1 main contact/F1 motor-current path는 만능기판 copper trace를 통과시키지 않는다.

다음 작업 순서:

1. External 10 kΩ 네 개를 RevB schematic/permanent wiring에 반영하고 continuity를 확인한다.
2. Motor와 LiPo를 분리한 채 USB/buck/back-power policy와 board input 전압을 검증한다.
3. K1/F1/main wire 정격을 motor starting/stall current 근거로 닫는다.
4. Physical E-stop T-ESTOP-001~005를 motor-disconnected 상태에서 검증한다.
5. 위 gate가 모두 PASS한 뒤에만 lifted single-motor 5~10% 시험으로 이동한다.

금지 사항:

- 현재 단계에서 actual motor 또는 MDD10A motor-energy 인가
- Motor data 없이 K1/F1/main wire 정격 확정
- Breadboard pull-down PASS를 RevB/permanent wiring PASS로 확대
- MCU-pin capture를 MDD10A/motor/E-stop PASS로 확대
- 원본 raw evidence 편집 또는 덮어쓰기
- UART pin/baud, STM32 safety authority 또는 MDD10A architecture 임의 변경
- 사용자 요청 없는 commit/push

첫 답변에서는 실제 git status, 완료된 UART/MCU-pin gate, 남은 evidence boundary와
대단원 2의 첫 작업인 RevB 10 kΩ 반영/continuity 계획만 간단히 보고해라.
```
