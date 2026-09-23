# 2026-08-13 Motor Output Safety And Perfboard Planning Session

## 상태

`COMPLETED — REQUIRED SCOPE`

필수 motor-output 안전 범위는 2026-08-12에 앞당겨 완료했다. 이 문서는 당시 실행 계획과
판정 기준의 역사 기록이며 현재 작업 지시가 아니다. 현재 continuation은
[`2026-08-13_power_and_physical_estop_session_ko.md`](2026-08-13_power_and_physical_estop_session_ko.md)다.

완료 결과:

- Command timeout: configured 300 ms 주변 bounded stop, UART-calibrated frame-end-to-last-edge
  약 `299.690 ms`, 이후 약 `8.939 s` 재출력 없음 — `PASS`.
- Software fault: marker 뒤 expected next PWM pulse 차단, 약 `2.052 s` latch — `PASS`.
  Marker가 PWM LOW phase에 발생했으므로 앞선 last fall과의 `5.25 us` 차이는 fault latency로
  표현하지 않는다.
- External reset: pull-down 미적용 시 네 motor input 약 `159 ms` HIGH — `FAIL` 보존.
  각 signal의 외부 `10 kΩ` pull-down 적용 뒤 5 s 전 구간 LOW — `PASS`.
- 모든 hook `0U`, contract `15/15`, final post-READY TEL 155/155 safe over 15.4 s — `PASS`.
- 선택 항목인 E-stop perfboard 초안과 acrylic mounting freeze는 다음 대단원으로 이월했다.

정본 결과는
[`../verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`](../verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md)다.

이 세션의 필수 목표는 실제 motor 전원을 인가하는 것이 아니다. Motor-disconnected 조건에서
남은 MCU motor-output 안전 파형 세 가지를 측정하고, 모든 임시 test hook을 끈 정상
firmware로 복구하는 것이 목표다. 시간이 남으면 Physical E-stop control perfboard 문서의
골격과 acrylic mounting 결정을 정리한다.

## 오늘의 완료 목표

1. Command-timeout event에서 PB6/PB7 final PWM edge까지 shutdown latency를 측정한다.
2. Software-fault event에서 PB6/PB7 final PWM edge까지 latency와 reset 전 latch를 측정한다.
3. 모든 hook을 `0U`로 복구한 safe image에서 external reset marker와 PB6/PB7/PC8/PC9를
   동시에 capture해 boot pulse가 없음을 확인한다.
4. Contract `15/15`, STM32/ESP32 build, safe flash와 UART regression을 다시 통과한다.
5. 선택 작업으로 E-stop perfboard 전용 문서의 component zone, connector map과 open item을
   작성한다. 실제 납땜은 하지 않는다.

## 기상 후 작업 계획표

시간은 부품 배송이나 예상 밖 debugging을 제외한 순수 작업시간이다.

| 기상 후 | 작업 | 의도 | 완료/PASS 기준 |
| ---: | --- | --- | --- |
| `+0:00~0:20` | 작업 상태와 물리 조건 확인 | 잘못된 image·배선·전원 조건에서 측정을 시작하지 않는다. | `git status` 확인, current hook 상태 기록, motor와 LiPo/MDD10A motor-energy 분리, analyzer GND=STM32 GND 확인 |
| `+0:20~1:10` | 실제 source 재검토 후 timeout/fault 계측용 임시 변경을 한 번에 작성 | 여러 번 수정·build하는 낭비를 줄이고 두 시험의 marker와 10% cap을 동시에 고정한다. | exact insertion location 검토, duty `<=10%`, temporary macro와 marker가 명확하고 normal default는 OFF |
| `+1:10~1:35` | STM32 build와 flash | 계측 대상 binary가 경고 없이 생성·다운로드됐는지 확인한다. | STM32 `0 errors / 0 warnings`, flash verify PASS |
| `+1:35~2:20` | Command-timeout shutdown capture | stale command가 정해진 timeout 주변에서 실제 PWM을 차단하는지 측정한다. | 1 ms `HAL_GetTick` phase와 analyzer clock tolerance를 명시한 bounded stop, 이후 PB6/PB7 inactive, 자동 재활성화 없음 |
| `+2:20~3:05` | Software-fault shutdown/latch capture | fault가 common safe-output path를 통해 두 channel을 끄고 reset까지 유지되는지 확인한다. | marker와 PWM phase를 함께 해석해 next-pulse 억제 또는 positive latency를 판정, PB6/PB7 inactive, PC8/PC9 LOW, reset 전 재활성화 없음 |
| `+3:05~3:25` | 휴식 및 두 raw capture 백업 | cursor 작업 전에 원본 손실을 막고 잘못된 capture를 조기에 발견한다. | `.sr`, `.pvs`가 열리고 channel map·sample rate·physical setup 메모가 존재 |
| `+3:25~4:15` | 모든 임시 hook `0U` 복구와 정적 검사 | controlled image가 정상 firmware로 남는 것을 방지한다. | STM32/ESP32 hook 전부 `0U`, contract `15/15`, controlled marker 잔존 여부 확인 |
| `+4:15~5:00` | Safe build·flash·external-reset boot capture | 실제 복구된 image가 reset 순간에도 PWM/DIR pulse를 만들지 않는지 확인한다. | 양 firmware build PASS, safe flash verify, reset marker 포함 PB6/PB7 pulse 0, PC8/PC9 safe LOW |
| `+5:00~5:40` | Safe UART regression과 증빙 저장 | waveform PASS와 통신 safe behavior가 동일한 복구 cycle에서 유지되는지 확인한다. | exact ACK/PONG/READY, ARM/CMD/test/failure 0, DISARMED/zero TEL 유지, raw log·hash·physical setup 기록 |
| `+5:40~6:30` | 결과 문서와 progress 갱신 | 측정 수치, binary, 물리 조건과 한계를 다른 사람이 재현할 수 있게 남긴다. | test report/result table, evidence README와 progress에 raw 파일·PNG·판정 연결 |
| `+6:30~7:30` | 선택: E-stop perfboard 문서 초안과 30~60분 mounting freeze | 다음 대단원에서 회로도 없이 바로 납땜하는 일을 방지하고 acrylic 주문 결정을 내린다. | K2/opto/F2=저전류 board, K1/F1=별도 high-current path, connector zone·TBD·아크릴 추가 가공 여부 기록 |

## 작업 시작 전 물리 조건

- Actual motor는 연결하지 않는다.
- LiPo와 MDD10A `B+/B-`, motor terminal에는 analyzer를 연결하지 않는다.
- NUCLEO와 ESP32를 USB로 동시에 공급한다면 두 board의 `5 V/VBUS/VIN`을 서로 연결하지 않는다.
- Logic analyzer GND는 STM32 logic GND 한 곳에만 연결한다.
- PWM test duty는 `100 permille = 10%`를 넘지 않는다.
- 기존 current baseline은 all-hooks-`0U`, contract `15/15`, STM32 safe ELF
  `46A80919B8ECE0521CBFA0861D74446F51904F7D9967517DCDC63118EA73B98A`, ESP32 safe BIN
  `4321B4BF2811590167EB7DCEF58CA84ABE5C0C7EEC67656E20D0EFD787A2724D`다. 새 build는
  새 hash로 별도 기록한다.

## Logic Analyzer 기본 channel 계획

| Channel | Signal | 용도 |
| --- | --- | --- |
| D0 | PC8 / DIR1 | Channel 1 direction |
| D1 | PB6 / PWM1 | Channel 1 final active edge |
| D2 | PC9 / DIR2 | Channel 2 direction |
| D3 | PB7 / PWM2 | Channel 2 final active edge |
| D4 | PA10 / USART1 RX | Timeout 시험의 last valid CMD reference |
| D5 | Fault event marker | Software-fault 기준점; exact pin은 source 재검토 후 확정 |
| D6 | NRST 또는 검증된 external reset marker | Safe boot capture 기준점 |
| D7 | Reserved | 필요 시 TX/ACK 또는 보조 marker |
| GND | STM32 GND | 유일한 digital reference |

Timeout, fault와 reset 시험의 channel 목적이 다르므로 한 capture에서 모든 신호를 억지로
사용하지 않는다. 각 capture 전에 channel map을 evidence metadata에 다시 기록한다.

## 증빙 파일명 초안

```text
assets/captures/logic_analyzer/2026-08-13_stm32_command_timeout_shutdown_<result>.sr
assets/captures/logic_analyzer/2026-08-13_stm32_command_timeout_shutdown_<result>.pvs
assets/captures/logic_analyzer/2026-08-13_stm32_software_fault_shutdown_latch_<result>.sr
assets/captures/logic_analyzer/2026-08-13_stm32_software_fault_shutdown_latch_<result>.pvs
assets/captures/logic_analyzer/2026-08-13_stm32_safe_reset_boot_no_output_<result>.sr
assets/captures/logic_analyzer/2026-08-13_stm32_safe_reset_boot_no_output_<result>.pvs
assets/screenshots/logic_analyzer/2026-08-13_<measurement>_<result>.png
```

각 evidence에는 operator, date/time, physical no-power setup, channel map, sample rate, test
macro, build output, retained binary hash, 측정 cursor와 limitation을 기록한다.

## 중단 기준

다음 중 하나면 다음 시험으로 넘어가지 않고 전원을 제거하거나 현재 raw capture를 보존한 뒤
원인을 먼저 확인한다.

- Motor, battery 또는 MDD10A power terminal이 연결되어 있다.
- Analyzer GND 기준이나 board 간 5 V rail 상태가 불명확하다.
- Duty가 10%를 넘거나 예상하지 않은 PWM/DIR transition이 나온다.
- Build warning/error 또는 flash verify failure가 발생한다.
- Timeout 전에 PWM이 꺼지거나 timeout/fault 뒤 output이 자동 재개된다.
- Safe restore 뒤 임시 macro가 `1U`이거나 controlled marker가 남아 있다.
- External reset marker를 capture하지 못했다. 이 경우 boot no-output을 PASS로 확대하지 않는다.

## Perfboard 선택 작업의 범위

내일은 다음 문서의 골격만 작성한다.

```text
09_Electrical_Design/01_Perfboard_Assembly_and_Wiring_Plan_ko.md
```

포함할 내용:

- 150 x 100 mm, 55 x 37 hole baseline
- component-side와 solder-side 좌표 기준
- NUCLEO/ESP32/BNO085 기존 zone과 새 K2/VO617A/F2 control zone
- S0, S2, K1 coil, STM32 sense와 12 V/GND connector map
- K1 main contact와 F1 motor current가 perfboard trace를 통과하지 않는 경계
- K1/F1/main wire 미선정과 exact footprint를 `TBD`로 유지하는 규칙
- continuity, short, polarity와 no-auto-restart 검사 순서

Step 8 KiCad RevB와 schematic-to-hardware continuity review가 끝나기 전에는 permanent soldering을
시작하지 않는다.

## 오늘 하지 않는 것

- Actual motor 회전
- LiPo/MDD10A motor-power 인가
- K1/F1/main wire를 motor data 없이 임의 구매
- Physical E-stop을 산업 안전 인증 회로로 주장
- Perfboard permanent soldering
- UART Gate C controlled vector 재시험

## 종료 판정

필수 일정의 성공 조건은 다음과 같다.

```text
timeout latency capture PASS
AND software-fault latency/latch capture PASS
AND all hooks 0U
AND contract 15/15
AND build/flash PASS
AND external-reset-marker boot no-output PASS
AND final safe UART regression PASS
= 대단원 1 MCU 저수준 안전 검증 완료
```

실행 결과 필수 항목을 모두 통과해 대단원 1은 `PASS — motor-disconnected MCU-pin scope`다.
Perfboard 초안은 선택 작업이므로 미완료 상태로 다음 대단원에 이월했다.

## 첫 시작 명령

프로젝트 repository root에서 다음을 먼저 실행한다.

```powershell
git status --short -- Projects/Tracked_Mobile_Robot
```

그다음 실제 저장된 STM32/ESP32 source와 모든 test hook 값을 다시 읽고 첫 코드 변경 위치를
결정한다.
