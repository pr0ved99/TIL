# 기존 MVP 마무리 — 첫 근거 대조

2026-11-19 · [마무리 계획](../plans/2026-11-19_to_20_MVP_Closeout_Plan_ko.md) §3~4의 첫 결과.

**현재 판정은 [11/20 통합 검토46](46_MVP_Nonphysical_Closeout_2026-11-20_ko.md)을 따른다.** T004/T005A 정상 기능 PASS,상위9 PASS·4 PARTIAL 유지. 이 보고서의 원본 감사 결과와 단일 모터 기능/소음 근거는 재사용한다. 아래 T005A PARTIAL·K1 구매안·다음 진단은 당시 이력이며 현재 지시가 아니다. 엔코더 공급3.3~5V/pull-up 출력은 기존 제조사 회신으로 확인됐고, 상세 내부 회로·무전원/과도 수용과 구분한다.

## 1. 이번에 확인한 결론

**통신·방향 출력·통신 유실 정지의 기존 근거가 있다. 먼저 문서에서 남아 있던 오래된 미실행 안내를 고친다.** 기존 시험을 처음부터 다시 하거나 PCB/ADC 작업을 시작할 이유는 없다.

이번 원본 재대조는 T004 reset, NZ-02 후진/양방향 회전, 10/20 통신선 단절·재연결에 한정한다. 전원·단일 모터 전체·엔코더 아날로그 조건은 기존 요구/판정/제외 결정으로 1차 분류했다. 전 시험의 원시 파형 전수 감사나 새 실물 시험을 했다는 뜻은 아니다.

전체 MVP의 8개 PARTIAL 행을 이번에 PASS로 올리지 않는다. 대신 **새 시험이 필요 없는 확인 범위와 실제 미결을 아래에 특정했다.** T005A/T007의 미결 및 기존 조사 제외가 유지되는 현재 조건에서는 11/20 전체 MUST PASS를 약속할 수 없다. 이 충돌이 통신 문서 정정·구성 기록 등 가능한 마감 작업까지 막지는 않는다.

## 2. 저장 원본에서 다시 확인한 내용

| 항목 | 이번 확인 | 닫을 수 있는 안내 / 남는 한계 |
| --- | --- | --- |
| E-stop active 중 reset 거절 | [T004 run03 UART](../../assets/logs/estop/2026-09-22_t004/run03_D5_uart.txt) 11.0024555s에 `ERR,type=ESTOP_RESET,code=ESTOP_ACTIVE` | “reset ERR target 미실행” 안내는 해소. 모터 분리 당시의 관측 |
| 해제 후 명시적 reset | 같은 원본 18.25675375s reset ACK → 18.3212885s `DISARMED/ESTOP_RESET`, PWM 0/0. age는 latch TEL의7444ms에서7544ms로 증가 | “reset ACK/후속 TEL 미실행” 안내는 해소. reset으로 age가 초기화되지 않은 실제 예시 |
| ARM만으로 재구동하지 않음 | reset 뒤 첫 ARMED TEL의 PWM 0/0 확인. 실제 PWM 재출력 시점은 [보고서26](26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md) §4의 fresh CMD와 연결 | 새 ARM-only 반복 시험 불필요. K1/MDD 전력 차단의 전체 수용과 별개 |
| 후진·회전의 signed TEL | [NZ-02 원본 UART](../../assets/logs/wifi_link/2026-10-17_nz02_reverse_turns_run01/D0.txt)에 −50/−50, −50/+50, +50/−50 존재 | “음수 부호/후진 근거가 전혀 없음”으로 안내하지 않음. 절댓값이 서로 다른 좌우 출력의 파형 검증과 구분 |
| 당시 실제 PWM/DIR | [NZ-02 판독 결과](../../assets/logs/wifi_link/2026-10-17_nz02_reverse_turns_run01/observations.json): 명령194개/ACK194개, DIR 전환10회 PWM LOW, 양PWM 약5%. SR/ESP console 해시 일치 | 저장된 디지털 판독 결과를 재사용. 이번에 전체 sample decoder를 다시 실행한 것은 아님. MDD 전력 출력/기계 정지의 증거로 확대하지 않음 |
| 통신선 단절 후 timeout | [단절 browser JSON](../../assets/logs/wifi_link/2026-10-20_uart_tx_disconnect_timeout_air_run01/browser_report.json) 2619행 재대조. CMD_TIMEOUT217행 모두 command/PWM0. 최초 timeout TEL의 age363ms, CPS960/760 | GPIO17 분리·S0 없이 실제 정지는 당시 사용자 보고. age363ms는 첫 TEL 관측값이며 설정 timeout/정지시간이 아님. PWM TEL0와 기계 정지는 동시라고 가정하지 않음 |
| 재연결 뒤 무재출발·수동 복구 | [복구 browser JSON](../../assets/logs/wifi_link/2026-10-20_uart_tx_reconnect_recovery_air_run01/browser_report.json) 2733행 모두 command/PWM/CPS0, count1959/1541 고정. 이후 DISARM reason 확인 | 재연결 뒤3초 동안 두 궤도 정지는 당시 사용자 보고. 두 export 사이131.1초의 미기록 구간과 정확한 재연결 시각은 복원하지 않음 |

[검사 수치·파일 식별 기록](../../assets/logs/mvp_closeout/2026-11-19_evidence_review/review.json)에 재대조한 항목과 한계를 저장했다. SR/console 및 browser 원본의 저장 해시와 실제 파일을 비교했고, UART 텍스트/JSON의 해당 상태를 직접 검사했다. 보드에 접속하거나 명령을 보내지 않았다.

## 3. 현재 저장 소스와 과거 실행 근거의 구분

10/24 UI 변경 **이전** [기준 manifest](../../assets/logs/wifi_link/2026-10-24_mvp_operation_documentation/baseline_manifest.json)와 비교하면 현재 소스13개 중12개, artifact6개 중4개가 일치한다. 차이는 ESP `wifi_link_main.c`와 ESP ELF/BIN이다.

10/24 [진행 기록](../progress/2026-10-24_progress.md)의 새 UI 수정·사용자 ESP 플래시 보고가 있으므로 이 차이를 즉시 오염/고장으로 판단하지 않는다. 반대로 해당 이전 manifest로 현재 전체 이미지를 식별했다고 쓰지도 않는다. 현재 보드 내부 이미지의 readback은 이번에 하지 않았다. **readback을 새 MVP 필수 요구로 추가하지 않는다.** 필요한 것은 실제 적용 버전·사용자 플래시 보고·해당 시험 조건을 정직하게 연결하는 것이다.

## 4. 미완료 8행의 첫 처리표

아래 분류는 각 행의 **남은 부분에 대한 처리**이며 상위 요구 전체의 새 PASS 판정이 아니다. `현재 보완 가능`은 문서/식별 작업부터 가능하다는 뜻이며, 미충족 선행 조건을 건너뛴 실물 시험 허가가 아니다.

| ID | 확보한 부분 | 실제 남은 부분 | 분류와 다음 처리 |
| --- | --- | --- | --- |
| MVP-001 UART | 정상 통신 기존 PASS, 이번 reset ERR/ACK/TEL·signed TEL 원본 대조 | 현재 실행 구성과 적용 요구 전체의 증거 연결 | **기존 근거로 충족한 부분 반영**. 미실행 안내 수정. 과거 P04의 없는 원본을 새 시험으로 소급 복원하려 하지 않음 |
| MVP-002 ESP 경로 | 현재 Wi-Fi 앱의 명령/정지·선택 AC-S와 NZ 시험, 통신 유실/복구 | 현재 앱과 옛 bridge 시험의 적용 범위 구분 | **현재 문서 보완 가능**. 옛 bridge default-off 미복구 문구를 현재 앱의 결함처럼 쓰지 않음. 모든 상상 가능한 오류 조합을 새 필수로 추가하지 않음 |
| MVP-003 전원 | 실제 보드 공급·USB/2P 분리 운영·셀 알람 감독하 운용 | 기존 전체 부하/최종 선재·단자 수용 | **기존 제외와 충돌**. 10/17 정격/도면 조사 재개 금지 유지. 현 구성 식별은 가능하나 전체 정격 PASS와 별개 |
| MVP-004 PWM/DIR | routing·방향 전환 순서·MCU/MDD 입력 범위 기존 PASS, NZ 실제 신호 | 상위 전력/기계 통합 수용과 구성 연결 | **기존 근거로 충족한 신호 범위 반영**. 동일 신호 시험 반복 대신 MVP-009/013과 공유 근거 연결 |
| MVP-005 단일 모터 | 기존 A/B 펄스·A DISARM/S0·A/B3초·후속 주행 | 원래 no-load 소음/반복 조건의 미기록, T005A 선행 | **문서 보완 가능 + 선행 충돌**. 기존 기록에서 관측 여부를 먼저 특정. T005A를 통과한 것으로 가정해 새 시험하지 않음 |
| MVP-007 엔코더 | 조정부 전압·독립 count/부호·실구동 디지털 전이 | 출력 회로형식·아날로그 pulse shape/전원순서·전이 이상 원인 | **추가 근거 필요**. 이번에는 아날로그 원본/장비 가용성을 새로 확인하지 않음. LA·1m 정확도 기록으로 아날로그 안전성을 대신하지 않음 |
| MVP-009 출력0 | MCU/MDD 입력의 기존 boot/reset/fault PASS, T004, 실제 timeout 정지 | 조건별 전기/기계 통합 수용 경계 | **기존 근거로 충족한 범위 반영**. TEL0만으로 실제 핀0를 새로 주장하지 않음. 기계 정량 항목은 MVP-013으로 연결 |
| MVP-013 물리 E-stop | 감지/latch/reset, K1/S2 기능, rail DMM, A 구동 S0·시연 | T005A rail-off 기준/전체 수용 및 T007 정지 시간·거리 | **기존 제외와 충돌 + 추가 근거 필요**. T007 BLOCKED 유지. 임의 기준·장비 구매·새 구동 시험 없음 |

전원/구동/엔코더/비상정지의 상세 잔여 판단은 [보고서41](41_MVP_Acceptance_Disposition_2026-10-24_ko.md) §2·5와 [검증 매트릭스](05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)를 따른다. 10/17 제외 결정을 근거 없이 취소하거나 제외된 요구를 기술적 PASS로 바꾸지 않는다.

## 5. 현재 구성 확인 완료와 다음 작업

사용자는11/19 “배선 바뀐거 없어. 여태까지 공부만 하느라 로봇은 털끝하나 안건드렸어”라고 보고했다. **로봇 실물의 변경 없음은 사용자 보고로 확인했고 사진 요청은 철회한다.** 기존 장착/배선 검사를 반복하지 않고, 각 시험 당시 조건과 한계를 유지해 근거를 재사용한다. 보드 이미지 readback이나 새로운 전원 상태 계측을 했다는 뜻은 아니다.

이어서11/5 [외부 관측 기록](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md)을 확인했다. M1B 전진·M2B 전진/후진 계측 회차에는 양쪽 회전→해제 정지→DISARM 및 이상 없음 보고가 있다. M1B 후진은 정지 보고가 있으나 해당 회차의 DISARM 확인은 별도 미보고다. 따라서 “최근 구동/정지·이상 관측이 전혀 없음”으로 안내하지 않는다. 측정선을 M1B/M2B로 바꾼 양쪽 구동을 단일 모터 no-load 시험으로 동일시하거나, 전체 소음/반복·T005A 선행 수용으로 확대하지 않는다.

다음은 남은 수용 항목별로 기존 증거로 닫는 범위와 실제 추가 검증이 필요한 범위를 확정하는 것이다. 실물 재시험을 먼저 지시하지 않는다. T005A/T007은 기존 제외 결정과 겹치는 구체적인 기준/측정 요구를 먼저 제시하며, 일반적인 진행 요청을 제외 조사 재개로 해석하지 않는다.

## 6. 문서 수정 범위

- UART 요구사항01의 오래된 reset 미실행/부호 미확인 문구에 후속 증거와 당시 범위를 연결했다.
- 검증표05의 옛 bridge 일반 PC 전달/default-off 미완료 안내를 현재 production 앱 근거와 구분했다.
- 현재 진행/인수인계·검증 목차·마무리 계획에 이 결과를 연결했다. 날짜별 원본 보고서의 당시 관측·실패·한계는 보존했다.
- 상위 MVP 판정, T005A PARTIAL/T007 BLOCKED 유지. 펌웨어/CAD/실물/빌드·플래시 변경 및 Git/Notion/Calendar 게시는 없다.

## 7. 후속 판정 — UART와 PWM 신호 요구 마감

### 7.1 이번에 닫는 범위

원래 요구 문장과 기존 하위 수용 판정을 다시 대조했다. **MVP-001은 UART 응답/텔레메트리, MVP-004는 PWM/DIR 신호 생성, MVP-009는 지정 상태에서 실제 PWM 신호0**을 요구한다. 전력 차단·기계 정지시간·전체 제작품 정격을 이 세 항목에도 중복 조건으로 붙여 PARTIAL을 유지했던 판정을 정정한다.

요구 문장·필수 항목을 삭제하거나 합격 수치를 낮추지 않는다. 모터 에너지 차단과 정량 정지, 전원·하네스, no-load 전체 및 엔코더 전기적 수용은 기존 MVP-003/005/007/013과 T005A/T007에 계속 남는다. 제품 전체 안전이나 모든 시험 이미지의 완전한 추적성이 확보됐다는 판정은 아니다.

| 항목 | 이전 → 현재 | 판정 근거 |
| --- | --- | --- |
| MVP-001 | PARTIAL → **PASS — 정의된 UART 응답/소프트웨어 텔레메트리 범위** | 아래 REQ-UART001~006 대조. 이전005 PASS를 유지하고006의 reset/복원 미결을 T004로 닫음 |
| MVP-004 | PARTIAL → **PASS — PWM/DIR 신호 생성·검증된 MDD 논리입력 범위** | routing·최종19kHz·방향 변경 전후 PWM0·후속 방향 매핑·제한 출력/정지. 전력단 부하 적합성은 포함하지 않음 |
| MVP-009 | PARTIAL → **PASS — 지정 boot/reset/DISARM/timeout/fault의 PWM 신호0 범위** | 실제 핀/논리입력의 기존 캡처와 T004. TEL0만으로 핀0를 추정한 판정이 아님. 기계 정지시간은 MVP-013에서 별도 유지 |

### 7.2 UART 요구별 증거

| 요구 | 직접 대조/재사용 근거 | 판단 |
| --- | --- | --- |
| REQ-UART-001 연결·주기 TEL | [7/9 CSV](../../04_PC_Serial_Control/logs/2026-07-09_uart_mvp_validation_session.csv) 17,826행의 CONNECTED/수신 TEL 및 기존 화면 | 기존 PASS 유지. 당시 PC-first 경로와 이후 production USART1 경로를 구분 |
| REQ-UART-002 PING/PONG | 같은 CSV의 matching seq1 및 기존 Gate A/B | 기존 PASS 유지 |
| REQ-UART-003 ACK type/seq | 같은 CSV의 ARM/CMD/DISARM, T004 run03 healthy reset ACK | 기존 PASS 유지, 후속 reset 근거 연결 |
| REQ-UART-004 ERR type/seq/code | 같은 CSV의 NOT_ARMED/OUT_OF_RANGE/TIMEOUT_OUT_OF_RANGE, T004 active reset ESTOP_ACTIVE | 기존 PASS 유지 |
| REQ-UART-005 applied signed PWM | P04A 원본49 TEL 중50/50은7개, 나머지zero; NZ-02의 음수·반대 부호, 후속 실제 Wi-Fi TEL. 현재 motor 출력 실패의 cache0는 소스 및 아래 PC 실행으로 확인 | 기존 **UART/software-cached scope PASS 유지**. PC 오류 입력/모의 HAL 결과를 보드의 실제 고장 주입으로 표현하지 않음 |
| REQ-UART-006 reason/age/reset | P04B 원본99 TEL의 sentinel·accepted-CMD age·485→585ms timeout bracket·DISARM 후 age 유지. T004 run03 active ERR/후속 active reason→latch→reset ACK/zero→ARM-only0, run07의199개 DISARMED/zero TEL | **PARTIAL → PASS — 정의된 UART/software-state 범위**. 오류1은 startup sync 당시 기록이며 무오류 cold-start 보장을 뜻하지 않음 |

P04A/P04B 및 최종 PWM 캡처3개의 해시를 보고서와 대조했다. 이전 T004/NZ-02 원본 재대조도 재사용했다. [이번 재대조 기록](../../assets/logs/mvp_closeout/2026-11-19_evidence_review/uart_pwm_review.json).

### 7.3 PWM 신호와 정지 증거

| 요구 상태 | 기존 전기적 근거 | 적용 경계 |
| --- | --- | --- |
| 좌우 PWM/DIR·방향 변경 | [보고서17](17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md)의 MDD 입력 CH1/CH2 19.049/19.058kHz, 방향 전환 전후 약2ms zero, hook0 all-LOW. NZ-02의 실제 부호/방향 후속 대조 | 논리입력 범위. 과거20kHz 초기값을 현재 설정으로 쓰지 않음 |
| boot/reset | [보고서16](16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md)의 pull-down 전 FAIL/후 PASS와 영구 기판 후속 검사, T004 정상/active 부팅·복원 | 현재도 외부10kΩ pull-down을 유지하는 구성. 초기 FAIL 이력 보존 |
| DISARM | [보고서10](10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md), NZ-03 및 report32의 실제 PWM 차단 | 당시 신호 위치/시계별 결과. 모든 조건의 최악 지연 보장 아님 |
| timeout | 보고서16의300ms, [보고서21](21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md)의500ms MCU control-net·새 ARM/CMD 복구,10/20 실구동 통신 단절 보조 근거 | 기존 전기 캡처와 후속 사용자 정지 보고를 구분 |
| fault/E-stop sense | 보고서16 Error_Handler 주입 후 다음 PWM 없음, 보고서26의 S0/감지선 단선·latch/reset 실제 PWM | 해당 fault 경로의 신호0. 임의 하드웨어 고장 전체나 K1 에너지 차단 성능 보장 아님 |

현재 저장 `motor_output.c`의200‰ 상한과 `PWM0→1ms→DIR→1ms→PWM` 순서를 확인했다. 10/18 변경은 기존100‰ 상한을200‰로 확장한 이력이 있으며 현재 일반150‰/순수회전200‰ 경로는 다음 PC 검사와 기존 실구동 기록으로 연결한다. 최초5~10% 시험과 최종 운용값을 혼동하지 않는다.

### 7.4 현재 소스 검사와 실패 기록

기존 `test_firmware_contract`의 선택2개 중 applied-output 검사는 PASS, reason/age 검사는 **FAIL(실제512 ≠ 과거 고정384바이트)**이었다. 이 실패를 숨기거나384에 맞춰 production 코드를 되돌리지 않았다. 이 검사는 이전 UART bridge와 count 확장 전 버퍼/분기 수를 전제한다.

현행 [저장본 C 모의 실행](../../assets/logs/mvp_closeout/2026-11-19_evidence_review/current_stm_host_review.json)은 `test_distance_control_candidate.py --saved`로 **24개 출력 검사 기록 PASS**였다. 이 수에는 범위 설명용 출력도 포함되므로 독립 시험24건으로 환산하지 않는다. 실제 저장 parser/protocol/mapper/motor 코드를 PC에서 실행하여 다음을 확인했다.

- 전진144/150·후진−140/−150, 회전200·혼합150·zero,300ms timeout/DISARM/E-stop.
- signed/raw201 초과 오류의 실제 getter0/0 및 모의 timer compare0, 송신 queue/완료 유실/HAL ERROR·BUSY 시 stop/latch.
- 기존 거리 명령의 도달/중단/재무장과 현재 UART 송신·encoder 경로의 회귀.

HAL/타이머/GPIO/UART는 모의다. MCU 빌드·플래시·실물 전기 계측이 아니며 production 소스를 수정하지 않았다. 이 결과와 기존 실물 증거를 합쳐 해당 소프트웨어/신호 요구를 판단했다. 새로 모든 하드웨어 오류를 주입했다는 뜻은 아니다.

### 7.5 현재 남은 항목과 다음 작업

이 UART/PWM 대조 종료 시점에는 상위 MUST13개 중 **8개 PASS(각 명시 범위),5개 PARTIAL**이었다. 당시 남은 ID는 **002·003·005·007·013**이다. 이후002 판정은8절을 따른다. T005A PARTIAL/T007 BLOCKED와 기존 제외 결정은 유지한다.

**다음은 MVP-002의 유일한 production command ingress를 닫는 대조**다. 현재 STM UART 수신 진입점과 ESP Wi-Fi 명령 경로, optional PC upstream 조건을 실제 소스/기존 회차에 연결한다. 옛 bridge 일반 PC 전달이나 전체 오류 조합을 새 필수로 복원하지 않는다. 이후 남은 전원/no-load/encoder/E-stop을 실제 추가 검증 필요 항목으로 다룬다. 지금 사용자 실물 조작은 필요 없다.

## 8. 후속 판정 — ESP 단일 production 명령 경로

**MVP-002 PARTIAL → PASS — 현재 정상 운용의 단일 명령 경로/ADR-015 범위.** PC 브라우저는 ESP32의 upstream client이고 STM32가 최종 출력·timeout·안전 판단을 유지한다. 새 펌웨어나 배선을 만들지 않고 이미 구현·실행된 경로를 원래 요구에 연결한 판정이다.

```text
PC 브라우저 → Wi-Fi/WebSocket → ESP32 세션·제어권·명령 처리
→ ESP UART1 GPIO17/18 ↔ STM USART1 PA9/10 → STM parser/안전 상태/PWM
```

| 확인할 조건 | 실제 저장본·기존 근거 | 판정 |
| --- | --- | --- |
| STM 명령 parser는 한 UART에만 연결 | [main.c](../../03_Firmware/stm32_uart_mvp/Core/Src/main.c)의 `uart_mvp_init(&huart1)` 단일 호출. [protocol](../../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c)의 RX 시작·재등록3곳 모두`s_uart`, 다른 UART 콜백은 ring push 전에 return | 충족 — 소스 대조 |
| USART2가 별도 PC production 명령원이 아님 | Core 전체 수신 시작 호출은 위 protocol3곳뿐. huart2는 main의 진단 TX이며 명령 수신을 시작하지 않음 | 충족 — USART2 주변장치 초기화와 명령 RX 시작을 구분. 이번에 USB 명령을 실제 주입한 것은 아님 |
| PC 제어는 ESP를 경유 | [ESP main](../../03_Firmware/esp32_wifi_link/main/wifi_link_main.c)의`/ws`→`ws_receive` typed parse→`wifi_command_admit_locked`→ARM/CMD executor·session ticket→`wifi_control_step`→UART1. PING/DISARM도 ESP 명령 경로에서 처리 | 충족 — 현재 browser upstream 구현. 별도 USB serial/Python bridge를 새 필수로 요구하지 않음 |
| 현재 앱·모드 식별 | [CMakeLists](../../03_Firmware/esp32_wifi_link/main/CMakeLists.txt)의wifi_link/control6개 source. UART test mode0·zero-only0, UART1 GPIO17/18. STM [usart.c](../../03_Firmware/stm32_uart_mvp/Core/Src/usart.c)의PA9/10 AF7 | 충족 — 옛esp32_uart_bridge 시험 앱과 구분 |
| 연결된 경로의 실제 실행 | [NZ-02 ESP console](../../assets/logs/wifi_link/2026-10-17_nz02_reverse_turns_run01/esp_console.txt)의WS QUEUED·CONTROL TX와 [동일 회차 판독](../../assets/logs/wifi_link/2026-10-17_nz02_reverse_turns_run01/observations.json)의194명령/194ACK·UART capture 대응.10/18 배터리 단독 지상 주행 및10/24 새 UI 플래시 사용자 보고/시연 | 충족 — 당시 실제 보드/사용자 보고 조건. 모든 오류 조합의 새 수용 시험을 했다는 뜻은 아님 |

현재 ESP main 해시는`37dc255d7caa7f02fc3a536650a3fb9202273300e27139d75f39a311264272b0`로 [10/24 UI 검사](../../assets/logs/wifi_link/2026-10-24_browser_dashboard_review/validation.json)의 변경 후 소스와 일치한다. 해당 검사는 PAGE 밖 바이트 불변을 기록했고, 이후 플래시·새 화면 확인은 [10/24 진행](../progress/2026-10-24_progress.md)에 사용자 보고로 남아 있다. 현재 로봇 변경 없음 보고도 유지한다. 독립 flash readback이나 암호학적 source-to-board 동일성을 주장하지 않는다.

[이번 근거 기록](../../assets/logs/mvp_closeout/2026-11-19_evidence_review/ingress_review.json)에11개 소스 조건·파일 식별·원본 연결을 저장했다. 이전 검사 이후 코드 변경이나 새 실패가 없어 전체 PC/보드 시험을 반복하지 않았다. 다른 UART 콜백 무시는 소스 확인이며 이번에 다른 UART로 명령을 넣는 실물 시험을 수행한 것은 아니다. 인증·물리적 재배선 공격 방어·전체 anti-replay/오류 조합·모터 안전 인증은 이 요구의 PASS 범위가 아니다.

발견한 최신화 누락은 UART 인터페이스 계약의`optional PC arbitration/logger/dashboard pending`과 ADR-015의`PC→ESP production forwarding 미구현`이다. 현재 browser/WebSocket 경로로 갱신하고,10/11 및 ADR 채택 당시 미실행 내용은 과거 기록으로 구분했다. 원래 단일 ingress/STM 안전 소유권 결정은 변경하지 않았다.

**이 단계에서 상위 MUST 13개 중 9개 PASS·4개 PARTIAL**, 남은 항목은 MVP-003 전원,005 단일 모터 no-load 전체,007 엔코더 입력 수용,013 물리 E-stop이다. 전체 MVP는 미완료이고 T005A PARTIAL/T007 BLOCKED 유지. 당시 다음 작업이었던 MVP-003의 대조 결과는 아래 9절이다.

## 9. 후속 판정 — 전원 근거와 실제 잔여 조건

**REQ-POWER-003은 PASS — 현재 보드의 전원 연결 규칙 범위로 정정한다. 상위 MVP-003은 PARTIAL을 유지한다.** 하위 요구사항 하나의 정정과 전체 전원 인수를 구분한다. 새 계측·배선·구매·빌드·플래시는 하지 않았다.

### 9.1 원래 요구와 기존 시험의 대응

| 요구 | 직접 대조한 기존 기록 | 판단 |
| --- | --- | --- |
| REQ-POWER-001: fuse/switch와 OFF/ON 극성 | 기존 PASS와 7/26 배터리12.36V/MDD 입력12.35V 모터 미연결 기록 | 기존 PASS 유지. 실제 모터 부하 전체를 뜻하지 않음 |
| REQ-POWER-002: 두 buck의 무부하 조정, 약1A 5분, 약1.8A 3분 결과·강하 기록 | [buck 원장](../../02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md)과 [7/18 사용자 보고](../progress/2026-07-18_progress.md): #1은 nominal1A 5분/단자4.91→4.93V, 1.76~1.80A 3분/단자4.88V. #2는0.94A 5분/단자4.91→4.90~4.89V, 1.78~1.80A 3분/USB측4.73V | **요구한 시험의 수행·기록은 확보**. 기존 사용 수용 판정 CONDITIONAL PASS 유지. #2 고부하 3분 때 converter 단자 전압은 동시 측정되지 않았고 #1 USB측 값은 확정하지 않음 |
| REQ-POWER-003: 보드별 USB/buck 전원 연결 규칙 확정 | [8/16 기록](../progress/2026-08-16_progress.md)의 단독 USB·dual USB·buck 단독/동시 공급·전원 제거, [9/8 보고서25](25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md)의 실제 두2P 분기, [현재 운용 절차](../handoff/CURRENT_MVP_OPERATION_RUNBOOK_ko.md#전원-기준) | **PASS — 정의된 보드 전원 연결 규칙/시험 구성 범위**. 하네스 정격·전체 구동 부하를 이 규칙의 추가 완료 조건으로 중복 적용하지 않음 |
| REQ-POWER-004: 셀 알람·감독·경고 후 종료 | 기존 설정/표시와 [10/23 경고음→수동 전원 차단 보고](../progress/2026-10-23_progress.md#리포-알람-실제-경고-동작의-과거-관측-확인) | 기존 USER-REPORTED PASS 유지. 반복 저전압 시험 없음 |

7/18 수치는 당시 시험 구성의 기록이다. nominal1A를 실제 정확히1.000A로 바꾸거나 USB측4.73V를 buck 단자 전압으로 바꾸지 않는다. 발열 보고의 대상은 **#1 시험의 전자부하 발생기**이며, 이 보고만으로 buck 과열을 확정하지 않는다. 사진4개는 파일 존재/식별을 확인했지만 이번에 판독하거나 사진으로 3분·5분 지속 시간을 증명하지 않았다. 시간과 당시 동작은 사용자 보고 근거다.

10/23에는 #1 세팅 변경 후 두 보드 연결5.02V, 별도 약1A 저항 부하에서 XL OUT5.00V/USB4.85~4.87V·0.93A가 보고됐다. [해당 관측값](../../assets/logs/wifi_link/2026-10-23_power_adjusted_drive_run01/session_observations.json)은 현재 구성에 대한 보조 근거다. 7월 고부하 회차와 같은 설정이라고 가정하지 않으며 새 5분/3분 시험으로 세지 않는다.

### 9.2 닫는 전원 규칙과 적용 한계

1. 배터리 단독 운용: 보드 USB를 모두 제거하고 #1의 두2P로 NUCLEO E5V/ESP 5V를 공급한다. NUCLEO `JP5=PWR-E5V`, `JP1=open`.
2. dual-USB 개발: #1의 보드용 두2P를 분리하고 보드마다 USB로 공급한다. 보드 간 전원 rail을 묶지 않고 UART/GND만 연결한다.
3. 한 보드만 USB로 공급: 무전원 보드로 향하는 UART TX/RX도 분리한다. 8/16의 반대편5V/3V3=0V는 이 신호선 분리 조건이다.
4. 전원 공급 방식 전환: 전원 OFF·케이블 분리·rail0V 확인 뒤 전환한다. USB/buck 동시 공급은 사용하지 않는다.

9/8 동시 공급에서 OUT4.95V, NUC E5V4.94V/3V3 3.30V, ESP5V4.95V/3V3 3.27V와 전원 제거 후0V가 기록돼 있다. 이 실제 구성의 시험 결과와 이미 확정된 규칙에 따라 REQ-POWER-003을 닫는다. K1 뒤 MDD rail의 모든 GPIO 역급전 경로나 전원 전이 순간까지 검증했다는 뜻은 아니다. 그 범위는 기존 T005A/T006과 구분한다.

### 9.3 남은 것은 무엇이며 지금 무엇을 할 것인가

| 남은 구분 | 부족한 근거 | 이번 처리 |
| --- | --- | --- |
| buck/분기 사용 수용 | 현재 설정·배선에서 각 분기가 실제 요구하는 최대/기동 부하와 해당 부하에서의 공급 조건 대응. 과거 전자부하 시험은 있지만 현재 전체 분기의 연속/기동 여유까지 입증하지 않음 | REQ-POWER-002/T-PWR-002의 기존 조건부 판정 보존. 7월 시험을 미실행이라고 하거나 일괄 반복하지 않음 |
| 전체 전력 경로 적합성 | 기존 전력 하네스/접속부 적합성 미결. 정상 전압·짧은 구동만으로 전체 정격 적합을 대신할 수 없음 | MVP-003의 미결로 유지. 이미 제외된 검토를 이번에 재개하거나 새 구매/재배선을 요구하지 않음 |
| 모터 에너지 차단 | 기존 T005A/T007의 기준·전체 수용 미결 | MVP-013과 공통으로 추적. 같은 내용을 새 전원 시험으로 중복 추가하지 않음 |

즉 **공급 시험과 운영 규칙이 없어서 멈춘 상태가 아니다.** 이번에 수행 가능한 문서 정정을 끝냈고, 전원 전체를 닫으려면 남은 사용 조건/기존 제외의 처리 결정이 필요하다. 현재 근거만으로 전체 PASS나 새로운 안전한 부하 상한을 선언하지 않는다. 제외 유지 상태에서 전체 전원 인수는 미완료이며, 그 결정을 대신해 제조사 조사·반복 계측을 시작하지 않는다.

**다음은 MVP-005:** 기존 단일 A/B 펄스·3초 구동·정지 관측을 원래 no-load 조건에 대조하고, T005A의 공통 미결과 별개로 실제 누락이 있는지 한 번에 정리한다. 이후 엔코더/물리 정지와 겹치는 미결을 묶어 실행 가능한 최소 작업을 제시한다. 이번에는 사용자에게 전원 인가나 재배선을 요청하지 않는다.

현재 상위 **9 PASS·4 PARTIAL** 유지. [이번 대조·파일 식별](../../assets/logs/mvp_closeout/2026-11-19_evidence_review/power_review.json). 과거 날짜별 시험 결과와 제외 결정은 보존했다.

## 10. 후속 판정 — 단일 모터 구동과 실제 잔여 조건

**MVP-005 / REQ-MOTOR-005 / T-MOTOR-003은 PARTIAL 유지. 기본 정·역회전과 정지 근거는 이미 있다.** 이번 결과는 같은 구동을 다시 하라는 지시가 아니라, 이미 충족한 관측과 실제 미결의 분리다. 새 실물 시험·펌웨어 변경은 없다.

### 10.1 이미 있는 단일 모터 근거

| 적용 조건 | 직접 대조한 근거 | 판단 |
| --- | --- | --- |
| 섀시 분리·낮은 duty에서 시작 | [보고서31](31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md): A5% 미회전 관측 뒤10%, B10%. 두 모터는 섀시 분리 상태였고 비대상 채널은0 | 낮은 duty 시작 확인. 5%에서 회전했다고 쓰지 않음 |
| A 정·역회전 / timeout 정지 | [9/30 원본01](../../assets/logs/motor_output/2026-09-30_single_motor_run/01_m1_positive_timeout_console.txt) +100, [9/29 원본05](../../assets/logs/motor_output/2026-09-29_single_motor_bench/05_m1_a_negative_10pct.txt) −100. 양수/음수 CPS 후 timeout PWM0, 최종 PWM/CPS0 유지2.8/9.3초. 실제 방향은 보고서31/32의 사용자 관측 | 방향·부호·timeout 후 정지 관측 확보. TEL의 시간으로 정확한 축 정지시간을 정하지 않음 |
| B 정·역회전 / timeout 정지 | [9/29 원본11](../../assets/logs/motor_output/2026-09-29_single_motor_bench/11_m2_b_forward_after_dir_fix.txt) +100, [원본12](../../assets/logs/motor_output/2026-09-29_single_motor_bench/12_m2_b_reverse_after_dir_fix.txt) −100. 실제 방향 사용자 확인, timeout PWM0, 최종 PWM/CPS0 유지8.9/4.1초 | DIR 보정 후 양방향·정지 관측 확보. 초기 미회전/잘못된 DIR 이력은 보존 |
| active DISARM | [9/30 보고서32](32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)의 A 구동 중 DISARM: 프레임 끝→마지막 PWM 하강364.44µs, 실제 정지 사용자 보고 | 실제 PWM 경계와 정지 관측 확보. 364.44µs를 기계 정지시간으로 쓰지 않음 |
| A/B 각각 3초 구동·DISARM·정지 후 안정 | 같은 보고서 및 보관 분석: PWM A2.99828925초/B2.988788초, 각 명령33개/ACK33개. 엔코더1432/1384전이, 마지막 전이 이후20.00838/20.50647초 고정 | B에도 예정 DISARM과 정지 근거가 있다. A/B 단일 구동을 모두 미실행으로 안내하지 않음 |

이번에 원시 UART4개, 총285 TEL의 부호·비대상 채널0·timeout 출력0·최종 정지 구간을 다시 추출했다. 보관 원본/파생 분석22개와 캡처/설정8개, 총30개의 해시가 manifest와 일치했다. 캡처 수치는 당시 파생 JSON을 재사용했으며 전체 파형을 새로 디코딩하지 않았다. [대조 기록](../../assets/logs/mvp_closeout/2026-11-19_evidence_review/motor_review.json).

### 10.2 남는 조건과 삭제할 중복 요구

1. **소음 관측 기록:** A5%에서 소리·떨림, 초기 B10%에서 소리만 나고 미회전했다는 관측은 있다. 성공한 단일 모터 정·역 구동의 비정상 소음 여부를 명시한 기록은 이번에 읽은 보고서31/32·9/29~10/1 진행 기록에서 찾지 못했다. 관측을 안 했다고 단정하지 않으며, encoder 디지털 전이의 정상 여부로 소음 판정을 대체하지 않는다. [11/5](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md)의 이상 없음은 양쪽 궤도 구동 조건이므로 당시 단일 모터 시험의 보고로 소급하지 않는다. 정량 dB 측정이나 새 계기를 필수로 추가하지 않는다.
2. **T005A 선행 수용:** 원래 T-MOTOR-003의 선행 조건이었고 당시에도 PARTIAL이었다. 실제 구동·정지 결과는 보존하지만 실행됐다는 이유로 선행을 통과한 것으로 바꾸지 않는다. 이 공통 미결은 MVP-003/013과 함께 추적하며, 현재 새 구동 시험을 시작하지 않는다.
3. **반복 문구 정정:** 현재 REQ-MOTOR-005와 [모터 계약 Stage2](../../01_System_Architecture/08_Motor_Driver_and_HBridge_Control_ko.md)는 별도 반복 횟수·반복 신뢰성 합격선을 정하지 않았다. 과거의 “반복 신뢰성을 입증하지 않음”이라는 한계를 **“추가 N회 시험을 해야 완료”라는 요구로 바꾸지 않는다.** 현재 잔여 안내의 모호한 반복 조건을 제거하고, 원래 기능/소음·선행 조건을 유지한다. 장시간/반복 신뢰성을 통과했다고 선언한 것은 아니다.

REQ-MOTOR-004는 낮은 duty 시작 근거가 있다. [10/18 기록](../progress/2026-10-18_progress.md)에는 지상 회전 정체·공중 비교 뒤 일반150‰/순수회전200‰를 적용한 이유와 결과도 있다. 따라서 “제한값과 변경 이유가 전혀 없음”은 틀리다. 다만 이 기록을 전체 부하의 제한 해제 수용으로 확대하지 않고 기존 CONDITIONAL PASS를 유지한다. 현재 duty를 더 올리거나 원래5~10% 시험을 다시 시작하지 않는다.

전류·정량 부하와 온도는 기존 후속 범위를 유지한다. 당시 Stage2의 온도 문구는 이후 사용자 결정과 함께 읽으며 새 필수 시험으로 복원하지 않는다. 성공한 구동 관측과 초기 미회전·정지 직전 반대 전이·회차 사이 err 증가의 원인 미결도 함께 보존한다.

### 10.3 다음 작업

**MVP-007 엔코더 입력:** 이미 있는 입력 전압·손회전 부호·구동 중 디지털 전이·count를 재사용하고, 실제 입력의 전기적 조건에서 무엇이 부족한지 확인한다. 그 뒤 물리 정지와 공통 선행을 묶어 남은 실행/결정 대상을 제시한다. 지금 모터 분해·소음 재시험·반복 구동을 요청하지 않는다. 상위 상태는 **9 PASS·4 PARTIAL**이다.

## 11. 후속 사용자 소음 관측 보완과 엔코더 근거 경계

사용자는 기존 A/B 단일 모터 정·역 정상 회전의 비정상 소음 유무 질문에 **“비정상 소음 없었음”**이라고 답했다. 이는 당시 관측에 대한11/19 후속 진술이며 새 시험/녹음 분석/정량 dB 측정이 아니다. 앞선 성공 구동 근거와 연결해 REQ-MOTOR-005의 기능·소음 범위는 PASS로 보완한다. 초기 저 duty 미회전/떨림 기록은 보존한다. 상위 MVP-005와 T-MOTOR-003의 공통 T005A 선행 미결을 해소한 것은 아니다. 소음 확인만을 위한 재구동은 하지 않는다.

엔코더는 [초기 입력 검사](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md)와 [실제 영구 회로 검사30](30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md)를 대조했다. 기존 부하10kΩ/15kΩ HIGH 관측은 내부 약10kΩ pull-up과 일치하는 추정 근거이며 open-collector/open-drain 형식 확정은 아니다. 영구 조정부의 네 입력 LOW0V/HIGH약2.86V는 이미 확보돼 반복하지 않는다. 기존 PCB 사진도 확인했지만 센서 IC 품번/출력 회로 전체를 판독하지 못했다. 이번 모델명 표적 웹 검색에서 적용 가능한 제조사 출력 회로 원문은 확보하지 못했고 다른 모터 자료를 대입하지 않았다.

보고서32의1432/1384 디지털 전이·정지 고정 근거는 재사용한다. 이번에 원시 파형을 새로 디코딩한 것은 아니며 전압 overshoot/출력형식까지 수용한 것이 아니다. 오실로스코프 이용 불가와 전기적 미결을 유지한다. 새 계측기 구매·배선 변경을 지시하지 않는다.

다음 공통 수용 검토에서는 기존 T005A 직접 rail 감소/수동 재인가와 S0 후 마지막 엔코더 전이127.32ms를 구분한다. 마지막 전이는 정확한 기계적 정지 시각이 아니다. 기존 결과에 맞춰 rail·정지 합격선을 만들지 않는다. K1 단자 추가 검토 중단은 계속 유지한다.
