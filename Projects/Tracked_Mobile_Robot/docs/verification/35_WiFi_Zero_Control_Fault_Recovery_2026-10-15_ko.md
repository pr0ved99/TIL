# Wi-Fi zero-only 정지·리셋·UART 단절 관측

> 2026-10-17 마감: UR-02와 AC-S01~08 선택 zero-only 실물 시나리오는 완료했다. [최신 완료 범위와 근거](37_Zero_Only_ACS_Bench_Closeout_2026-10-17_ko.md)를 우선한다. 아래 당시 계획·미완료·실패 기록과 원래 수용 조건은 보존한다.

- 실물 시험일: **2026-10-15**. 문서화·PC 재현: **2026-10-16**.
- 사용자: 조작·배선·모니터/화면 제공. Codex: 실제 소스 대조·로그 분석·PC 진단.
- 최신 판정: **AC-S PARTIAL.** 10/15 첫 DISARM 실패는 아래 원관측으로 보존한다. 10/16 CAN+LF 수정·PC 검사·재연결 첫 정지 성공과 부분 명령 실물 수용 대기는 [보고서36](36_UART_Line_Cancel_Recovery_2026-10-16_ko.md)을 따른다.
- 원본 첨부에서 선택한 행, 대화 전사와 소스 식별값: [증거 묶음](../../assets/logs/wifi_link/2026-10-15_zero_control_bench/README.md).
- 기준 Git HEAD: `c6fa6c85e10d0a9da83ca9a681c5015a2ff230b8`. 실행 바이너리 SHA256은 미확보다. 문서화 당시 소스 해시가 그 바이너리와 동일하다고 가정하지 않는다.

## 1. 구성과 관측 범위

앱은 `esp32_wifi_link`이며 브라우저 ARM 후 반복 CMD는 vx/w 모두0이다. STM이 모터 출력·watchdog·PC7 fault/latch를 담당한다.

| 항목 | 사용자 확인·관측 |
| --- | --- |
| 보드 공급 | 각각 USB. XL4015 #1의 보드용 2핀 두 개 분리 |
| 감지 회로 | #2 AUX 감지 회로 연결. LiPo/S1 공급 후 #2 출력 측정값5.07V. 이 값을 PC7 핀 전압으로 해석하지 않음 |
| 모터 전력 | MDD10A B+를 분리·절연한 후 AC-S 조작. 처음 분리 전 B+↔B−0V 보고와 구분 |
| UART 단절 시험 시 배치 | STM은 만능기판에 장착, ESP는 탈거해 외부 점퍼 연결. PA9→GPIO18, GPIO17→PA10, 공통GND |
| 10/16 최신 확인 | USB·LiPo 연결 중, 위 STM/ESP 배치와 UART 연결, 로직애널라이저 보유. 전원 종료 완료 보고 없음 |
| 측정 한계 | 이 보고서의10/15 묶음에는 새 로직 캡처가 없다.10/16 후속 UART4채널 캡처는 [보고서36](36_UART_Line_Cancel_Recovery_2026-10-16_ko.md)이며 PWM/PC7 근거는 아님 |

USB만으로 감지 회로가 공급되지 않은 초기에는 FAULT/ESTOP_ACTIVE가 지속됐다. 감지 공급·S0 해제 뒤 ESTOP_LATCHED, STM reset 뒤 DISARMED/BOOT를 관측했다. FAULT 우회 설정은 사용하지 않았다.

## 2. 실제 관측과 수용 기준의 대응

AC-S 원래 기준은 [제어 계약](../plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md#8-검증-gate와-정확한-pass-기준)을 따른다. 아래 기능 관측이 전체 기준 PASS를 뜻하지 않는다.

| ID | 이번에 확인한 범위 | 남은 조건 |
| --- | --- | --- |
| AC-S01 | 수동 ARM ACK→zero CMD ACK/TEL, ACTIVE/ARMED·속도/PWM/CPS0 | 실제 PWM 핀0 동시 관측 |
| AC-S02 | A 제어 중 B ARM은 BUSY, B CMD는 TICKET_REJECTED. A CMD 계속 수락. B DISARM은 정지 성공 | B CMD는 의도적으로 잘못된 ticket. 유효 A ticket을 다른 연결에서 재사용하는 경로·ARM owner 전용 거부 분기는 별도 |
| AC-S03 | ACTIVE WS 정상 close 후 DISARM ACK/정지 TEL. 창 전환 정지는10/13 사용자 관측 | 마지막 CMD와 출력의 실제 동시 캡처. 정상 WS close와 RF 유실을 구분 |
| AC-S04 | UART 방향별 단절에서 응답 유실·timeout과 허가 취소 관측 | 선택적 ACK 지연/유실, 늦은 ACK·만료 입력의 실물 주입은 미완료 |
| AC-S05 | 실제 ACTIVE에서 STM reset·ESP reset, 자동 ARM/CMD 없이 정지/복구 관측 | reset 구간 실제 PWM/입력파형. STM reset은 BLOCKED 후 수동 DISARM 필요 |
| AC-S06 | ESP→STM 단절 시 STM DISARMED/CMD_TIMEOUT.10/16 실제 STM C의 PC 실행에서 CMD-only 거부·새 ARM/zero 수락 확인 | 현재 실물 이미지의 CMD-only 재무장 거부, 새 수동 ARM/zero 및 UART 캡처 |
| AC-S07 | S0 active→FAULT/ESTOP_ACTIVE, 해제→ESTOP_LATCHED, STM reset→DISARMED/BOOT. 자동 재무장 없음 | 해당 조작의 PC7/PWM 동시 캡처. ESTOP_RESET 명령 절차는 별도 |
| AC-S08 | stop 응답 실패→BLOCKED. TEL 복구만으로 해제되지 않음. 수동 DISARM 성공 후 IDLE. TX 재연결 첫 DISARM 보완·부분 CMD/ARM 폐기는10/16 보고서36에서 확인 | 늦은 ACK 미해제 실물 증거는 남음 |

### WS 종료와 두 연결

- WS close: 마지막 CMD seq283800489 ACK 뒤 DISARM490 TX560579/ACK560599, TEL560649의 STM334703에서 DISARMED/DISARM. graceful close 관측이며 무선 단절 시간 보장이 아니다.
- 비소유자 정지: A session1, B session2. B DISARM request4→seq1250321035 ACK, 정지 TEL. 직전에 접수된 A CMD98의 TX는 발췌 범위에 없다. 사용자는 네 번 시도했으나 첨부에서 한 ARM 사이클만 확인했으므로 네 번 모두 PASS라 기록하지 않는다.
- 비소유자 입력: B session3 ARM1/BUSY, CMD2/TICKET_REJECTED(ticket1), A owner1/control6의 CMD가 이후에도 정상 수락됐다. B 마무리 DISARM3→seq1250321053 ACK 후 IDLE.

### 리셋과 물리 fault

- STM reset 실제 시도: reset 전 CMD seq283800551은 ACK 미확인, DISARM552는 ACK를 받았다. 이후 STM t_ms가157100→100으로 돌아왔다. ESP는 STOP_UNCONFIRMED/BLOCKED를 유지했다. 수동 DISARM20/seq553 ACK와 새 정지 TEL 후 IDLE을 확인했다.
- 앞선 별도 시도는 사용자가 **RESET을 누르지 않았다**고 정정했다. CMD43 ticket 거부 당시 로그는 단순 만료 확정 근거가 아니며 리셋 시험 성공으로 쓰지 않는다.
- ESP reset 실제 시도: 마지막 ARMED TEL STM781200 후 새 boot275098552. 첫 새 TEL STM782000은 DISARMED/CMD_TIMEOUT. startup DISARM1250320934/PING935 후 READY, 자동 ARM/CMD는 관측되지 않았다.
- 별도 앞선 ESP reset 시도는 이미 DISARM33을 완료한 뒤 리셋했다. ACTIVE reset 성공 근거에서 제외했다.
- ESP 재기동에서 seq0/BAD_TYPE과 err 증가를 관측했다. 정상 복구 후 누적 err은 유지됐으며 전기적 원인은 확정하지 않았다.
- S0: STM1033700에서 FAULT/ESTOP_ACTIVE, ESP DISARM944 ACK. S0 해제 후 ESTOP_LATCHED, STM reset 후 t_ms5300·DISARMED/BOOT·err0. reset으로 err이0이 된 것은 오류 원인을 수정한 증거가 아니다.

## 3. UART 단절·복구와 첫 정지 실패

아래는 같은 ESP boot **2317088236**, session1의 시험이다.

| 순서 | UART·상태 관측 | 판정 |
| --- | --- | --- |
| STM→ESP 단절 | 마지막 정상 TEL STM80400 ARMED. DISARM8622 송신 뒤 matching ACK 없음, stale6103ms, BLOCKED/STOP_UNCONFIRMED | stop 확인 실패를 차단 상태로 유지. stale ARMED는 현재 STM 상태가 아님 |
| RX 재연결 | STM162800부터 DISARMED/DISARM TEL 복구, last_seq8622. ESP는 BLOCKED 유지 | STM은 앞선 DISARM을 처리했고 ESP 수신만 끊긴 것과 일치 |
| 수동 DISARM13 | 화면 OK/IDLE, last_seq8623·err0 | 복구 관측. 이 요청의 raw matching ACK 로그는 미제공 |
| ESP→STM 단절 | 마지막 CMD8630 ACK. CMD8631과 DISARM8632는 송신만 기록되고 ACK 없음. STM1013000에서 DISARMED/CMD_TIMEOUT | STM 독립 watchdog 정지 관측, ESP는 BLOCKED |
| TX 재연결 후 무조작 | DISARMED/CMD_TIMEOUT, last_seq8630, err0; ESP BLOCKED | 연결 복구만으로 제어가 재개되지 않음 |
| 첫 수동 DISARM23 | seq2760658633,22/22. STM ERR seq0/typeCMD/MISSING_SEQ, err0→1. last_seq8630 유지 | **실패 / OPEN** |
| 두 번째 수동 DISARM24 | seq2760658634 TX1532099→ACK1532129. TEL1532219에서 DISARMED/DISARM. 화면 OK/IDLE | 수동 복구 성공. 첫 요청 실패는 해소되지 않음 |

표의 짧은8622~8630 표기는 해당 seq의 끝자리다. 정확한 수치는 [대화 전사](../../assets/logs/wifi_link/2026-10-15_zero_control_bench/chat_excerpts.txt)와 첨부 발췌를 따른다.

마지막 화면: READY/IDLE, STM DISARMED/DISARM, last_seq2760658634, PWM/CPS0, drop0, err1. 이것은 현재 복구 상태이며 장기 UART 무결성 PASS가 아니다.

## 4. 10/16 실제 C 코드의 PC 재현

[진단 러너](../../03_Firmware/tests/reproduce_uart_reconnect.py)는 STM `uart_mvp_protocol.c` 전체, 실제 parser/ring/mapper, ESP executor/state/owner/ticket/contract를 PC에서 실행한다. HAL 시간·UART·GPIO·모터·IRQ만 mock이다. 보드 직렬 포트는 열지 않는다.

1. 정상 분할 프레임은 LF 뒤에만 처리된다.
2. 합성 입력 `CMD,seq=`를 받다가 끊고300ms watchdog 만료 및10초 경과를 줘도, STM의 부분 줄은 남아 있었다.
3. 실제 ESP executor가 만든 DISARM seq2760658633은22byte이며 선행 동기화가 없다. 그 줄이 CMD 조각에 이어져 **typeCMD/MISSING_SEQ**로 거부됐다.
4. 그 LF가 버퍼를 비운 뒤 두 번째 DISARM은 ACK됐다.55byte CMD의 비어 있지 않은 미완성 prefix **54/54개**에서 첫 DISARM 유실을 재현했다.
5. 단순히 선행 LF를 추가하면, `ARM,seq=99`가 남은 상태에서는 오래된 ARM이 실행되는 반례가 있었다. 복구는 남은 프레임을 **실행하지 않고 폐기**해야 한다.
6. 별도 PC 확인:299ms에는 ARMED,300ms에는 DISARMED. 그 뒤 CMD만으로는 NOT_ARMED, 새 ARM/zero는 수락됐다. HAL 오류 경로는 다음 LF까지 폐기한 뒤 복구됐다.

**확정한 것은 코드상 가능한 실패 경로다. 실물에서 남았던 정확한 바이트는 아직 없다.** 배선 접촉·UART framing error 등 다른 원인과의 구분은 로직 캡처로 이어간다. 이 PC 재현 시점에는 생산 펌웨어 미수정이었다. 후속 코드·저장본 PC·사용자 빌드/플래시·UART 캡처는 [보고서36](36_UART_Line_Cancel_Recovery_2026-10-16_ko.md)에 별도로 기록했다.

## 5. 후속 상태 — 10/16 마감

UR-00/01 캡처, CAN+LF 보완, 저장본 PC513+17+42, 사용자 STM/ESP 빌드/플래시, UR-02 재연결 첫 DISARM의 ACK/새 TEL/IDLE을 [보고서36](36_UART_Line_Cancel_Recovery_2026-10-16_ko.md)에 보존했다. 원래 실패는 당시 관측으로 남으며 후속 성공으로 소급 수정하지 않는다.

10/16 오후 후속: [보고서36](36_UART_Line_Cancel_Recovery_2026-10-16_ko.md)에서 UR-02 재연결·미완성 CMD/ARM 실물 폐기와 mode0 복원을 확인했다. 전체 AC-S는 PARTIAL이며 다음은 UR-03의 미확인 조건(선택적 늦은 ACK, 현재 이미지 CMD-only 거부, 실제 PWM·PC7 등)이다. 완료한 UR-02는 반복하지 않는다.

세부 순서는 [UR 계획](../plans/2026-10-16_WiFi_UART_Recovery_Bench_Plan_ko.md)을 따른다. 원래10/15~18 일자별 일정 원문은 저장소에서 찾지 못했으므로 일정 전체 완료율을 추정하지 않는다.
