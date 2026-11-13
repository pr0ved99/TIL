# UART 줄 폐기 복구 — 코드·PC 검사·실물 재연결·부분 명령 시험

> 2026-10-17 마감: UR-02와 AC-S01~08 선택 zero-only 실물 시나리오는 완료했다. [최신 완료 범위와 근거](37_Zero_Only_ACS_Bench_Closeout_2026-10-17_ko.md)를 우선한다. 아래 당시 계획·미완료·실패 기록과 원래 수용 조건은 보존한다.

- 날짜: **2026-10-16**, 새벽 재연결 시험에 오후 부분 CMD/ARM 주입과 mode0 복원 결과를 추가했다.
- 판정: **UR-02 UART 복구 범위 PASS** — 재연결·부분 CMD·LF 없는 ARM 폐기·첫 DISARM 복구 및 mode0 정상 이미지 복원 확인. **전체 AC-S는 PARTIAL.**
- 사용자: 펌웨어 입력·보드 빌드/플래시·배선 조작·캡처. Codex: 코드 검토·PC 검사·UART 해독·증거 정리.
- 이전 실패: [보고서35](35_WiFi_Zero_Control_Fault_Recovery_2026-10-15_ko.md). 첫 DISARM23의 MISSING_SEQ 실패를 후속 성공으로 소급 변경하지 않는다.

## 1. 변경과 검증 범위

STM은 줄 중간의 ASCII CAN `0x18`을 받으면 남은 줄을 실행하지 않고 LF까지 폐기한다. ESP는 부팅·기존 명령 경로·executor의 모든 DISARM 앞에 `0x18 0x0A`를 붙인다. CAN은 통신 줄 취소이며 CAN 버스나 모터 정지 명령이 아니다. 실제 정지는 뒤의 DISARM이 담당한다.

변경 파일은 `uart_mvp_protocol.c`, `wifi_control_executor.h/.c`, `wifi_link_main.c` 네 개다. 기존 `need_line_sync`는 제거했다. ACK의 명령/seq 대조와 이후 새 정지 TEL 확인, 오류 시 BLOCKED, 수동 복구, E-stop latch는 유지했다. 이미 처리된 명령을 취소하거나 연결 오류 중 첫 요청의 도착을 보장하는 기능은 아니다.

[코드 안내](../plans/2026-10-16_UART_Line_Cancel_Recovery_Code_Guide_ko.md)의 사용자 입력 뒤 오타·삭제 누락·잘못 붙은 매크로를 실제 파일에서 발견했다. 사용자 수정 후 저장본은 검토 후보와 주석 끝 공백을 제외하고 일치했다.

| 근거 | 결과 | 경계 |
| --- | --- | --- |
| 수정 전 실제 C 진단 | 잔여 CMD와 첫 DISARM 결합 실패 54/54, LF만 붙일 때 오래된 ARM 실행 반례 | 코드상 가능한 실패이며 당시 실물 잔여 바이트는 미확보 |
| 후보 PC 검사 | 513 prefix/state 조합, executor 17, main adapter 42 및 복구 경계 검사 PASS | 임시 후보 소스 |
| 최종 저장본 PC 검사 | 같은 검사 PASS. 분할/반복 취소, overflow/HAL 오류, timeout, CMD-only 거부, latch, ACK/새 TEL, startup 포함 | HAL·UART·RTOS mock, 전체 MCU 빌드가 아님 |
| STM·ESP 빌드 | 두 프로젝트 성공 사용자 보고 | 전체 원본 빌드 로그와 실행 바이너리 hash 미확보 |
| 플래시 후 부팅 | 새 ESP boot `2324278617`, line cancel, 첫 DISARM ACK/PONG, READY 및 정상 TEL | 새 동작의 부팅 관측. 플래시 바이너리 readback은 없음 |

최종 저장본 [PC 출력](../../assets/logs/wifi_link/2026-10-16_uart_cancel_saved/saved_pc.txt)과 [소스/검사 SHA256 manifest](../../assets/logs/wifi_link/2026-10-16_uart_cancel_saved/source_manifest.json)를 기준으로 한다. [부팅 로그 발췌](../../assets/logs/wifi_link/2026-10-16_uart_cancel_saved/startup_monitor_excerpt.txt)는 사용자 대화에 붙여 넣은 원문에서 선택한 행이며 전체 serial/flash transcript가 아니다. 후보 manifest는 입력 전 이력으로 보존한다. PAGE JS46은 10/13 이력이며 이번 변경에서 새로 실행한 검사 수에 합산하지 않는다.

## 2. 실물 구성과 캡처

STM은 만능기판에 장착, ESP는 탈거해 외부 UART 점퍼로 연결했다. 두 USB·LiPo 연결, #1 보드용 2핀 두 개와 MDD10A B+ 분리·절연, #2 감지 전원 유지 조건이다. 종료 전원 분리 완료는 이 문서 작성 시 미보고다. #2 출력 5.07V의 과거 측정값을 PC7 핀 전압으로 바꾸지 않는다.

| 채널 | 측정점 |
| --- | --- |
| D0 | JDBG_UART Pin1 → STM PA9 TX |
| D1 | JDBG_UART Pin2 → STM PA10 RX |
| D2 | ESP GPIO18 RX |
| D3 | ESP GPIO17 TX |
| GND | 공통 LOGIC_GND / JDBG_UART Pin3 |

UART 115200/8N1/LSB-first/non-inverted, 샘플링 4 MHz. UART 양끝을 측정했고 PWM·PC7·전력단은 측정하지 않았다.

| 캡처 | 관측 |
| --- | --- |
| [UR-00 원본](../../assets/captures/logic_analyzer/2026-10-16_ur00_uart_baseline_run01.sr), [해독](../../assets/logs/wifi_link/2026-10-16_ur00_uart_baseline_run01/summary.json) | 17.008384초. PING/PONG seq2760658635, 두 UART 쌍 decoded byte 일치. 정상 TEL170개, err1 유지, invalid stop0 |
| [UR-01 원본](../../assets/captures/logic_analyzer/2026-10-16_ur01_uart_reconnect_run01.sr), [관측](../../assets/logs/wifi_link/2026-10-16_ur01_uart_reconnect_run01/observations.json) | 수정 전 50초. CMD8646·DISARM8647 전체 유실, CMD_TIMEOUT. 재연결 첫 수동 DISARM2760658648 ACK와 새 정지 TEL, 요청38 OK/IDLE. 부분 명령 실패는 재현되지 않음 |
| [UR-02 원본](../../assets/captures/logic_analyzer/2026-10-16_ur02_uart_cancel_reconnect_run01.sr), [관측](../../assets/logs/wifi_link/2026-10-16_ur02_uart_cancel_reconnect_run01/observations.json) | 수정 후 50초. CAN+LF와 첫 복구 DISARM 양끝 일치, matching ACK와 새 TEL, 요청16 OK/IDLE |

각 원본과 같은 이름의 `.pvs`를 보존했다. 해독은 [공용 Python decoder](../../assets/logs/wifi_link/2026-10-16_ur00_uart_baseline_run01/decode_capture.py)를 사용한다. sampled transition 차이나 단일 sample excursion이 있으므로 decoded byte 일치를 아날로그 신호 무결성 보장으로 쓰지 않는다. UR-01 시작의 invalid-stop 후보 두 개는 첫 LF 이전 캡처 경계에만 있었다.

## 3. UR-02 run01 순서

원본 SHA256: `9df725381c6f84097ebb98d95b7e43ee310eed62202493c1325c36a545f67c42`.
아래 초 단위는 캡처 시작 기준이며 STM `t_ms`와 다른 시계다.

| 캡처 시각 | 관측 |
| --- | --- |
| 2.328초 | ARM1024243099 양끝 수신, ACK 후 ARMED TEL |
| 3.587초 | 마지막 정상 CMD1024243111, STM ACK `t_ms=328698` |
| 3.687 / 3.847초 | CMD3112와 CAN+LF/DISARM3113은 D3에만 있고 D1에는 전체가 없음 |
| 3.894초 | 첫 `DISARMED/CMD_TIMEOUT` TEL, STM329001, command_age303ms, last_seq3111 |
| 11.157초 | D3·D1 모두 `18 0A` 뒤 `DISARM,seq=1024243114\n` 확인 |
| 11.159초 | D0·D2에 정확한 DISARM ACK, STM336278 |
| 11.182초 | 새 TEL STM336301, DISARMED/DISARM, last_seq1024243114 |
| 최종 사용자 화면 | boot2324278617, 요청16 DISARM OK, READY/IDLE, fresh TEL, err0 |

전체 TEL501개에서 PWM/CPS0, drop0/err0, 모든 채널의 invalid stop0이었다. D0↔D2 응답 바이트는 일치했다. 복구 뒤 캡처 끝까지 자동 ARM/CMD와 ARMED 재진입은 관측되지 않았다. 중간 브라우저 BLOCKED 화면/로그는 이번 묶음에 없으므로 캡처의 STM timeout 증거와 구분한다.

## 4. 오후 부분 명령 시험과 정상 이미지 복원

ESP 기존 UART 태스크에 기본0U·수동 POST·부팅당1회 시험 기능을 추가했다. mode1은 `CMD,seq=`, mode2는 유효한 `ARM,seq=…`를 LF 없이 송신하고 약100ms 뒤 기존 CAN+LF/DISARM 경로로 정지한다. 시험 이미지에서는 일반 PING/ARM/CMD를 거부한다. 초기 PAGE 누락은 사용자 직접 수정 위임으로 Codex가 복원했고, [실제 저장본 PC 검사](../../assets/logs/wifi_link/2026-10-16_uart_partial_saved/page_restored_pc.txt)를 통과했다. 사용자가 각 ESP 시험 이미지 빌드·플래시와 측정을 수행했다.

| 조건 | UART 캡처·실행 근거 | 판정 |
| --- | --- | --- |
| 부분 CMD | [원본](../../assets/captures/logic_analyzer/2026-10-16_UR02_MODE1_PARTIAL_CMD_run02.sr), [해독](../../assets/logs/wifi_link/2026-10-16_ur02_mode1_partial_cmd_retry/summary.json), [사용자 로그/화면 전사](../../assets/logs/wifi_link/2026-10-16_ur02_mode1_partial_cmd_retry/esp_monitor_excerpt.txt). `CMD,seq=` → CAN+LF → 첫 DISARM2750537414. ACK STM32157 → 같은 seq의 새 TEL STM32200. end=1/1, boot3417001124, READY/IDLE | UART 기능 PASS |
| LF 없는 ARM | [원본](../../assets/captures/logic_analyzer/2026-10-16_UR02_MODE2_PARTIAL_ARM_run01.sr), [해독](../../assets/logs/wifi_link/2026-10-16_ur02_mode2_partial_arm_run01/summary.json), [사용자 로그/화면 전사](../../assets/logs/wifi_link/2026-10-16_ur02_mode2_partial_arm_run01/esp_monitor_excerpt.txt). ARM1152473122 뒤 CAN+LF, **ARM ACK 없이** 첫 DISARM1152473123 ACK STM1125894 → 새 TEL STM1125903. end=1/1, boot312894, READY/IDLE | UART 기능 PASS |
| 일반 이미지 복원 | [부팅 로그](../../assets/logs/wifi_link/2026-10-16_uart_partial_normal_restore/startup_monitor_excerpt.txt), [복원 관측/소스 해시](../../assets/logs/wifi_link/2026-10-16_uart_partial_normal_restore/observations.json). 소스0U, boot3996125447, DISARM451258570 ACK/PING451258571 PONG/READY. 화면 시험 배너 없음, IDLE·fresh DISARMED/zero | 복원 확인 |

두 최종 시험 캡처는 각각4MHz/50M=12.5초다. D3↔D1 명령 및 D0↔D2 응답의 해독 바이트가 일치했다. 각125개 정상 TEL 모두 DISARMED/DISARM, PWM/CPS/drop/err0이고 추가 ARM/CMD ACK·ERR는 없었다. 정상 복원 로그의 TEL54개도 DISARMED/zero/drop0/err0이다. 소스의 정규화 SHA256은 `c6919bccf50713ebce9344ae44a98d7cecb35adbd1b0c4197258cbfd78842515`로 앞서 PC 검사한 복원본과 같다. 이번 첨부는 모니터 로그이며 전체 빌드/플래시 transcript나 바이너리 readback은 아니다.

### 측정 한계와 재시도 이력

- 첫 mode1은 D0/D1 미연결로 양끝 비교 불가였다. 사용자가 미연결을 확인하고 보완했다. 같은 부팅에서 재요청한 ALREADY_USED는 부팅당1회 제한이며 새 주입 성공으로 계산하지 않는다.
- 이전 run02의 DISARM3542617269 캡처는 재시도 때 같은 파일명으로 덮어써졌다. 이전 hash `eb39b1947479727e5adfddb692eefe4412816624ce61fe53602e8bf745c2fef4`의 [해독 결과](../../assets/logs/wifi_link/2026-10-16_ur02_mode1_partial_cmd_run02/summary.json)는 남지만 원본 파일은 현재 재시도 hash `bf6f76266281c1e0101227db167cc905bcd8775e34e530d3fca43f72b49d2e30`다. 최종 mode1 판정에는 **동일 회차2750537414**의 캡처·로그·화면을 묶었다.
- 이전 run02의 D1 한 글자 오독은 [중앙3/5/7샘플 재해독](../../assets/logs/wifi_link/2026-10-16_ur02_mode1_partial_cmd_run02/D1_sampling_check.json)에서는 모두 D3와 일치했다. 최종 mode1/2도 D1에 각각1080/1085개의 단일0.25µs excursion이 남는다. 원인은 미확정이며 원시 레벨 완전 일치나 아날로그 신호 무결성 PASS가 아니다.
- 최종 mode1/2의 D0/D2 invalid-stop 후보 각1개는 각각 캡처 시작0.00011초/0.00000775초에 있으며 시험 주입 전이다. 해독 기록을 삭제하거나 오류0으로 변경하지 않았다.
- 원래 DISARM23 실패 당시의 잔여 바이트를 소급 복원한 시험은 아니다. 실제 PWM·PC7·전력 차단·모터 정지는 이번 UART 캡처의 판정 범위 밖이다.

## 5. 판정과 남은 작업

**UR-02의 재연결·부분 CMD·LF 없는 ARM 폐기와 정상 이미지 복원을 완료했다.** 다음은 보고서35 AC-S의 남은 수용 항목을 UR-03으로 진행한다: 선택적 ACK 지연/유실·늦은 ACK, 현재 이미지의 timeout 뒤 CMD-only 재무장 거부, 유효 ticket의 다른 연결 재사용, 실제 PWM/PC7 동시 관측 등이다. 완료한 UR-02를 이유 없이 반복하지 않는다.

별도 USB–UART 추가 구매 없이 기존 ESP와 LA로 이번 범위를 확인했다. 마지막 전원은 USB·LiPo 연결 상태이며 전원 분리 완료는 미보고다. Git commit/push는 요청받거나 실행하지 않았다.
