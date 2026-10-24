# UART 재연결 첫 DISARM 복구와 AC-S 잔여 검증

> 2026-10-17 마감: UR-02와 AC-S01~08 선택 zero-only 실물 시나리오는 완료했다. [최신 완료 범위와 근거](../verification/37_Zero_Only_ACS_Bench_Closeout_2026-10-17_ko.md)를 우선한다. 아래 당시 계획·미완료·실패 기록과 원래 수용 조건은 보존한다.

작성:2026-10-16. 목적은 **첫 정지 요청 실패를 설명·보완하고, zero-only 제어의 미확인 조건을 닫는 것**이다. [보고서35](../verification/35_WiFi_Zero_Control_Fault_Recovery_2026-10-15_ko.md)의 기능 관측은 유지하며 같은 시험을 전부 다시 하지 않는다.

## 현재 위치 — 10/16 오후 정상 이미지 복원

- **UR-02 UART 복구 범위 PASS, 전체 AC-S PARTIAL.** 새벽 재연결에 오후 통제된 부분 CMD/ARM 주입을 추가했다. [보고서36](../verification/36_UART_Line_Cancel_Recovery_2026-10-16_ko.md).
- mode1 DISARM2750537414, mode2 LF 없는 ARM1152473122 폐기/첫 DISARM1152473123의 양끝 해독·정확한 ACK/새 TEL·IDLE을 확인했다. 초기 D0/D1 미연결은 보완됐다.
- 일반 이미지0U로 사용자 빌드·플래시 후 boot3996125447, DISARM ACK/PONG/READY, 시험 배너 없음·IDLE·fresh DISARMED/zero 확인. 전원 분리 완료는 미보고다.
- D1 단발0.25µs 샘플 차이 원인과 아날로그 신호 품질은 미확정이다. PWM/PC7/전력·모터는 이번 UART 측정 범위 밖이다.
- 기존 ESP UART 태스크의 수동·부팅당1회 기능과 LA로 완료했다. 별도 USB–UART 추가 구매는 필요하지 않았다.

## 순서와 종료선

| 단계 | 수행 | 종료 조건 |
| --- | --- | --- |
| UR-00 준비 | **완료**: 실제4채널 매핑·IDLE/PING 캡처 | 두 UART 쌍 decoded byte 일치. 물리 PWM 근거는 아님 |
| UR-01 수정 전 캡처 | **완료**: CMD/정지 전체 유실→timeout→첫 수동 DISARM 성공 | 부분 CMD 미포착, 기존 실패 재현 안 됨. 원본 보존 |
| UR-02 보완·재검증 | **UART 복구 범위 PASS**: 재연결·부분 CMD/ARM 주입·mode0 복원 | 양끝 해독·오래된 ARM/CMD ACK 없음·첫 DISARM ACK/새 TEL·IDLE. 전체 AC-S는 별도 |
| UR-03 수용 보완 | 선택적 ACK 유실/지연·늦은 ACK, CMD-only 거부, reset/fault/hidden의 미확인 파형 | 보고서35 표의 각 빈칸을 해당 증거로만 완료 처리 |

## UR-00: 사용자 실제 연결 기준 — 이전 제안 대체

처음에는 전원 차단 후 연결을 제안했지만 사용자가 **LiPo·USB 연결 유지**를 선택했다. 이후 PulseView 설정, 공통GND 연결과 아래 UART4채널 연결 완료를 보고했다. 전원 분리 완료로 해석하지 않는다. #1 두2핀과 B+ 분리·절연 조건은 유지한다.

이 표는 사용자 보고에 따른 실제 채널 배치다. 기존 D0=PC7/D1=PB6/D2=PB7 제안은 사용하지 않는다. PWM과 PC7은 아직 연결 보고가 없으며 이번 UART4채널 캡처로 물리 출력0을 판정하지 않는다.

| LA | 실제 측정점 | 목적 |
| --- | --- | --- |
| GND | JDBG_UART Pin3의 공통 LOGIC_GND | 신호 기준 |
| D0 | JDBG_UART Pin1→STM PA9 | STM 송신 ACK/ERR/TEL |
| D1 | JDBG_UART Pin2→STM PA10 | STM에 도착한 명령 |
| D2 | 외부 ESP GPIO18 | ESP에 도착한 ACK/ERR/TEL |
| D3 | 외부 ESP GPIO17, 탈착 점퍼의 ESP 쪽 | ESP가 내보내는 실제 바이트 |

JDBG 측정점은 [기존 T004 배선표](../verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md#1-시험-구성과-판정-범위) 기준이다. 현재 헤더 식별이 다르면 사진/실물을 확인한 뒤 연결한다. ESP 탈거 상태에서 만능기판의 빈 ESP 소켓을 송신점이라고 지정하지 않는다. LA는 위 로직 신호에만 연결하며 LiPo·MDD B+는 측정 대상이 아니다.

## UR-01 캡처와 판정

- 실제 캡처: UR-00은4MHz/68,033,536samples=17.008384초, UR-01/02는4MHz/200M=50초. UART115200/8N1/LSB-first/non-inverted. decoder STM RX=D1/TX=D0, ESP RX=D2/TX=D3. 설정과 캡처는 완료됐다.
- UR-00에서 IDLE/PING 정상 배선 대응을 확인했다. 완료한 동일 조건은 반복하지 않는다. 단절 대상은 **D3 쪽 GPIO17↔D1 쪽 PA10** 점퍼이며 반대 방향과 GND를 유지하는 절차다.
- 프로브/전원 확인 뒤 별도 한 시험 묶음으로 안내한다. 캡처 시작→브라우저 ARM·속도0→ACTIVE 유지→GPIO17↔PA10 신호선만 끊기→CMD_TIMEOUT/BLOCKED 확인→같은 선 복구→첫 DISARM 한 번. 공통GND는 유지하고 VS Code로 전환하지 않는다.
- 조작이 캡처 길이 안에 들어가지 않으면 길이를 늘린다. 마감 시간을 맞추려고 빠르게 배선을 만지지 않는다. 첫 요청이 실패하면 우선 원본을 저장한다. 두 번째 성공으로 실패 기록을 덮지 않는다.
- 확인할 것: 단절 직전 마지막 완전 CMD, PA10에 도착한 마지막 부분 프레임, 재연결 후 D3/D1 차이, DISARM의 정확한 seq/종결LF, 그 뒤 D0/D2의 ACK/ERR/TEL. PWM/PC7은 별도 연결·캡처 후 평가한다.
- 디지털 UART decode 오류가 계속되거나 기대하지 않은 PWM HIGH/FAULT가 나오면 ARM을 더 반복하지 않고 정지 상태에서 원인을 분리한다.
- `written=22/22`는 STM 수신 확인이 아니다. LA decode도 STM 내부 파싱 완료를 직접 보여주지 않으므로 응답 로그와 함께 해석한다.
- zero-only에서는 `마지막 PWM 하강까지 몇ms`라는 정지 지연을 만들지 않는다. 현재는 UART/state 전환만 기록하며, 후속 PWM 캡처에서는 실제 LOW 유지 여부를 확인한다.

저장 완료: `assets/captures/logic_analyzer/2026-10-16_ur00_uart_baseline_run01`, `2026-10-16_ur01_uart_reconnect_run01`, `2026-10-16_ur02_uart_cancel_reconnect_run01`의 `.sr/.pvs`. 대응 해독·hash·관측은 같은 접두사의 `assets/logs/wifi_link/` 디렉터리에 있다. 상세 판정은 보고서36을 따른다.

## 수정 설계에서 지킬 조건

1. 정지 앞의 잔여 줄은 실행하지 않고 폐기한다. 완성된 ARM에서 LF만 빠진 경우도 포함한다.
2. 정상 프레임 분할 수신, CRLF, 최대 길이/overflow, HAL 수신 오류 경로를 유지한다. 오류가 계속되는 동안 첫 정지 성공을 보장한다고 주장하지 않는다.
3. 자동 ARM·CMD 재시도나 stop 확인 기준 완화로 해결하지 않는다. ACK identity와 새 TEL 확인, BLOCKED에서 수동 정지 복구를 유지한다.
4. 후보를 실제 STM stream과 ESP formatter로 함께 검사하고, 사용자에게 정확한 교체 범위와 연결된 코드 블록을 제공한다. 보드 빌드/플래시는 사용자 수행이다.

## UR-02 추가 시험 완료와 다음 작업

[입력 가이드](2026-10-16_UART_Partial_Command_Test_Code_Guide_ko.md)의 기능을 반영했고 PAGE 복원 뒤 실제 저장본 PC 검사와 사용자 실물 시험을 완료했다. 현재 설정은0U다. mode1/2의 반복 주입을 다음 작업으로 안내하지 않는다.

다음 UR-03에서는 보고서35의 남은 AC-S 항목 하나를 골라 조건·관측·PASS 기준부터 정한다. ACK 지연/유실·늦은 ACK, timeout 뒤 CMD-only 거부, 유효 ticket의 다른 연결 재사용, 실제 PWM/PC7 동시 관측은 각각 별도 증거가 필요하다. 원래 첫 DISARM23 실패 기록은 유지하며 통제 주입 결과로 당시 잔여 바이트를 소급 확정하지 않는다.

## AC-S 이후와 구분

여기서 완료하는 것은 무선 zero-only 제어다. nonzero PWM의 차단 시간, 전력단 rail-off, 실제 모터 정지 거리, 전류·열·주행은 후속 Gate다. LA 보유만으로 아날로그 전력 차단 측정을 완료할 수 없다. 이번 작업의 Git commit/push는 아직 요청받지 않았다.
