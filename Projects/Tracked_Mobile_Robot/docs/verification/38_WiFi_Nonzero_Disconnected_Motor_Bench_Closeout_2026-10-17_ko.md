# Wi-Fi nonzero 모터 분리 시험 마감

기준: 2026-10-17. **NZ-01~04의 선택한 모터 분리 UART/DIR/PWM 시나리오 PASS.**
브라우저 방향 입력을 ESP가 현재 owner/ticket으로 STM에 전달하고, 놓음·DISARM·창 전환에 따라 출력을 정리하는 경로를 확인했다. 실제 모터 회전·차량 주행·기계 정지 성능의 수용은 별도다.

## 구현과 실행 기준

- 사용자 저장·빌드·플래시: ESP core contract/state/executor와 PAGE/snapshot을 통합하고 `WIFI_CONTROL_ZERO_ONLY=0U`로 실행했다. `WIFI_UART_PARTIAL_TEST_MODE=0U`, STM 시험 switch14개0U 유지. 이 문서 마감에서 firmware 변경·보드 빌드·플래시는 하지 않았다.
- ARM → 첫 zero ACK/새 일치 TEL → ACTIVE를 유지한다. ACTIVE에서만 현재 입력을 새 ticket으로 송신한다. PAGE 명령은 직진±50mm/s, 회전±250mrad/s이며 실측 속도가 아니다. PWM cap은100permille, 이번 명령의 실제 듀티는 약5%다.
- 놓음은 zero CMD, DISARM·focus/visibility 유실은 의도 폐기와 정지 경로다. 복귀 시 이전 방향을 자동 복원하지 않는다.
- [mode0 저장본 PC 근거](../../assets/logs/wifi_link/2026-10-17_nonzero_mode0_saved_review/): 현재mode0 core13/adapter6, 임시mode1 회귀59+3+42+6, 브라우저66·PAGE C 초기화·negative control3 PASS. SDK 빌드·실물 증거와 구분한다. 사용자 mode0 빌드·플래시·화면 확인은 진행 기록에 있다.
- [구현 범위](../plans/2026-10-17_WiFi_Nonzero_Control_Integration_Plan_ko.md), [core 변경 설명](../plans/2026-10-17_WiFi_Nonzero_Core_Code_Guide_ko.md), [PAGE 변경 설명](../plans/2026-10-17_WiFi_Nonzero_PAGE_Code_Guide_ko.md).

## 회차별 결과

각 링크의 observations.json에 판정·세부 수치·캡처/로그 SHA256가 있다. 같은 폴더에 ESP 원본·UART 해독·재현용 analyze.py를 보존했다.

| 회차 | 확인한 동작 | UART 근거 | 실제 출력·관측 | 결과 |
| --- | --- | --- | --- | --- |
| [NZ-01](../../assets/logs/wifi_link/2026-10-17_nz01_forward_release_run01/observations.json) | 전진 → 놓음 zero → DISARM | ARM1/CMD66/DISARM1, ACK68 일치 | 양쪽 약5%, zero 후 PWM 재출력 없음. 정지 TEL 약5.89초 관측 | PASS |
| [NZ-02](../../assets/logs/wifi_link/2026-10-17_nz02_reverse_turns_run01/observations.json) | 후진·좌/우 회전과 구간별 ARMED/zero 복귀 | ARM1/CMD192/DISARM1, ACK194 일치 | 각 약5%, DIR10회 전환 모두 양PWM LOW. 최종 PWM LOW 약14.48초 | PASS |
| [NZ-03](../../assets/logs/wifi_link/2026-10-17_nz03_active_disarm_run01/observations.json) | 전진 출력 중 명시적 DISARM | ARM1/CMD118/DISARM1, ACK120 일치. nonzero 직후 zero 없이 DISARM | 출력 약5% → 양PWM LOW, 이후 약10.04초 재출력 없음 | PASS |
| [NZ-04](../../assets/logs/wifi_link/2026-10-17_nz04_focus_loss_run01/observations.json) | 전진 중 Alt+Tab·복귀 회차의 정지/자동 재무장 방지 | ARM1/CMD52/DISARM1, ACK54 일치. 정지 후 ARM/CMD 없음 | 출력 약5% → 양PWM LOW, 이후 약10.29초 재출력 없음 | PASS |

합계436개 명령/ACK가 각 회차 내 순서·seq/type 일치. 전체 TEL에서 PC7 활성 fault·CPS·drop·err 증가가 관측되지 않았다. PC7 LOW는 별도 디지털 채널로 확인했다.

| NZ-02 입력 | TEL 좌/우 PWM | 측정 DIR PC8/PC9 |
| --- | --- | --- |
| 후진 vx−50, w0 | −50/−50 | HIGH/LOW |
| 좌회전 vx0, w+250 | −50/+50 | HIGH/HIGH |
| 우회전 vx0, w−250 | +50/−50 | LOW/LOW |

NZ-01은 DIR 채널이 없었다. NZ-03/04 전진 출력 중에는 PC8/PC9 LOW/HIGH를 확인했다. zero CMD에서 DIR 기본 방향 레벨이 남는 것과 PWM 출력0은 구분한다.

## 원시 캡처

- [NZ-01 · 4MHz/16.007초](../../assets/captures/logic_analyzer/2026-10-17_WIFI_NZ01_FORWARD_RELEASE_PWM_run01.sr)
- [NZ-02 · 4MHz/36.575초](../../assets/captures/logic_analyzer/2026-10-17_WIFI_NZ02_REVERSE_TURNS_DIR_PWM_run01.sr)
- [NZ-03 · 4MHz/25.968초](../../assets/captures/logic_analyzer/2026-10-17_WIFI_NZ03_ACTIVE_DISARM_PWM_run01.sr)
- [NZ-04 · 4MHz/18.232초](../../assets/captures/logic_analyzer/2026-10-17_WIFI_NZ04_FOCUS_LOSS_NO_REARM_PWM_run01.sr)

115200/8N1. D0=JDBG_UART Pin1/PA9 STM TX, D1=Pin2/PA10 STM RX, GND=Pin3.
D4=JDBG_CTRL_1 Pin2/PB6 좌 PWM, D7=JDBG_CTRL_2 Pin1/PB7 우 PWM, D6=JDBG_CTRL_2 Pin2/PC7.
NZ-02부터 D2=JDBG_CTRL_1 Pin1/PC8 좌 DIR, D3=Pin3/PC9 우 DIR. D2/D3는 과거 ESP UART 채널로 디코드하지 않는다. 프로브 식별은 안내한 연결을 기준으로 하며 SR 메타데이터에는 D 번호가 있다.

## 경계와 현재 물리 상태

- NZ-01/04 끝의 불완전 TEL은 캡처 경계로 원본에 남겼다. NZ-02는 시작 중간 TEL 조각과 초기21.5/480.5µs decoder stop 오류2개를 보존했다. 첫 완전 TEL 이후/시험 구간의 UART 오류와 구분한다. NZ-03 완전 프레임은 오류 없이 종료됐다.
- 브라우저 pointer/key/focus/return timestamp는 기록되지 않았다. 놓음·Enter·Alt+Tab부터 정지까지의 지연, NZ-04의 blur/visibility/pointercancel 원인 분리는 측정하지 않았다. 복귀 절차는 사용자 회차이며 캡처는 정지 이후 재ARM/CMD·출력 재발 없음의 근거다.
- 모터 전력4선과 MDD 제어5핀 분리·절연, #1 보드용2핀 두 개 분리·절연 상태를 유지했다. MDD B+는 복원, B− 공통GND. 두 보드 USB와 LiPo/S1 ON·S0 해제의 감지 전원 조건으로 안내했고 이후 배선 변경 보고는 없다.
- 최신 화면: boot4247124430, DISARM 요청436 OK, STM last_seq2197817170, fresh DISARMED/DISARM, ESP IDLE, vx/w·PWM/CPS/drop/err0. **이번 묶음 종료 전원 분리는 아직 사용자 미보고다.**
- 이전 zero-only [보고서37](37_Zero_Only_ACS_Bench_Closeout_2026-10-17_ko.md)의 실패/미해결 이력은 보존한다. 이번 PASS로 모든 오류 조합·물리 안전·주행 수용을 확대하지 않는다.

## 다음 재개점

1. 이번 결과 문서/Git 마감과 사용자 시험 전원 종료 확인. 종료 완료 보고 전에는 분리됐다고 기록하지 않는다.
2. 다음 별도 회차에서 기존 모터 A/B 이력을 재사용하고, Wi-Fi 명령으로 lifted 단일 모터의 방향·놓음·DISARM을 확인할 범위와 연결 순서를 정한다. 이 문서는 지금 모터 연결/통전 지시가 아니다.
3. 완료한 NZ-01~04와 zero-only 전체 회차를 변경·실패·사용자 요청 없이 반복하지 않는다. ADC/자동 저전압 정지는 합의한 후속 PCB 범위를 유지한다.
