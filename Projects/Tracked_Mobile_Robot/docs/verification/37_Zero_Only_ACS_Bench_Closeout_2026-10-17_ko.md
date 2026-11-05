# Zero-only AC-S 실물 시험 마감

기준: 2026-10-17. **UR-02 UART 복구와 UR-03의 AC-S01~08 선택 시나리오를 모터 동력 차단·속도 0 조건에서 마감한다.** 각 회차의 브라우저/ESP 기록과 UART·PWM·PC7 캡처를 대조했다. 전체 오류 조합, nonzero Wi-Fi 구동, 전력단·기계 정지 성능의 수용 판정은 별도다.

요구사항은 [ARM/CMD 계약](../plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md), 이전 실패·복구 과정은 [보고서35](35_WiFi_Zero_Control_Fault_Recovery_2026-10-15_ko.md)와 [보고서36](36_UART_Line_Cancel_Recovery_2026-10-16_ko.md)에 보존한다. 이 표가 이번 시험 묶음의 최신 완료 범위다. 날짜가 지난 문서의 미완료 표기는 당시 상태다.

## 항목별 완료 범위

아래 링크는 판정·원시 로그·캡처 식별값을 담은 회차별 observations.json이다. PASS는 해당 시나리오와 관측 시간 안에서의 판정이다.

| 항목 | 확인한 시나리오 | 근거 | 경계 |
| --- | --- | --- | --- |
| AC-S01 | 수동 ARM→zero CMD ACK/TEL→ACTIVE/ARMED, 실제 MCU PWM 0 | [정상 제어](../../assets/logs/wifi_link/2026-10-16_ur03_acs01_zero_pwm_run01/observations.json) | 디지털 핀 관측, 모터 구동 없음 |
| AC-S02 | B의 A 미소비 ticket CMD 거부 뒤 A 동일 ticket 성공; B ARM 거부 뒤 A 유지; B DISARM에 의한 A 정지·소유권 해제 | [동일 ticket run04](../../assets/logs/wifi_link/2026-10-16_ur03_acs02_valid_ticket_pwm_run04/observations.json), [B ARM](../../assets/logs/wifi_link/2026-10-17_ur03_acs02_other_session_arm_pwm_run01/observations.json), [B DISARM](../../assets/logs/wifi_link/2026-10-17_ur03_acs02_other_session_disarm_run01/observations.json) | B ARM은 취소되고 만료된 IDLE ticket 사용. owner-only 검사 분기만 분리한 실물 증거는 아님. B DISARM helper의 INCOMPLETE는 아래 설명대로 보존 |
| AC-S03 | 탭 닫기/재연결과 탭 전환 정지, 자동 재ARM/CMD 없음 | [닫기](../../assets/logs/wifi_link/2026-10-16_ur03_acs03_tab_close_pwm_run01/observations.json), [전환 run02](../../assets/logs/wifi_link/2026-10-17_ur03_acs03_tab_hidden_pwm_run02/observations.json) | RF 단절과 blur/visibility 각각의 원인 분리는 미검증. 복귀 순간의 정확한 timestamp 없음 |
| AC-S04 | 만료·폐기 ARM ticket 거부; 실행된 CMD의 ACK 한 개 유실→TIMEOUT→정지; 정상 hook0 복원 | [만료 ARM](../../assets/logs/wifi_link/2026-10-16_ur03_acs04_expired_arm_pwm_run01/observations.json), [CMD ACK 유실](../../assets/logs/wifi_link/2026-10-17_ur03_acs04_cmd_ack_drop_pwm_run01/observations.json), [복원](../../assets/logs/wifi_link/2026-10-17_ur03_acs04_cmd_ack_drop_restore_pwm_run01/observations.json) | ticket 만료와 ID 불일치 분기를 실물에서 분리하지 않음. 늦은 DISARM ACK는 AC-S08 근거 사용 |
| AC-S05 | ESP/STM reset의 PWM0, 자동 제어 복원 없음, 수동 복구 | [ESP](../../assets/logs/wifi_link/2026-10-16_ur03_acs05_esp_reset_pwm_run01/observations.json), [STM](../../assets/logs/wifi_link/2026-10-16_ur03_acs05_stm_reset_pwm_run01/observations.json) | EN/NRST 직접 파형 없음. D1 reset transient 원인 미확정 |
| AC-S06 | STM CMD_TIMEOUT 뒤 CMD-only NOT_ARMED; 정상 이미지에서 새 수동 ARM/zero/DISARM | [timeout](../../assets/logs/wifi_link/2026-10-17_ur03_acs06_cmd_timeout_pwm_run01/observations.json), [복원 run02](../../assets/logs/wifi_link/2026-10-17_ur03_acs06_restore_pwm_run02/observations.json) | mode3로 STM timeout에 도달. age355ms는 첫 TEL 관측값이며 timeout 설정값·정밀 정지 시간이 아님 |
| AC-S07 | 물리 PC7 활성→FAULT/ESTOP_ACTIVE, 해제 뒤 latch 유지·자동 재ARM 없음, 수동 복구 | [sense/latch](../../assets/logs/wifi_link/2026-10-16_ur03_acs07_estop_latch_pwm_run01/observations.json) | protocol ESTOP_RESET 명령 시험과 구동 중 정지 시간·거리 수용은 별도 |
| AC-S08 | DISARM ACK 지연→STOP_UNCONFIRMED/BLOCKED, 늦은 ACK로 해제 안 됨; 새 수동 DISARM과 정상 이미지 복구 | [늦은 ACK](../../assets/logs/wifi_link/2026-10-16_ur03_acs08_late_disarm_ack_pwm_run01/observations.json), [수동 복구](../../assets/logs/wifi_link/2026-10-16_ur03_acs08_recovery_pwm_run01/observations.json), [정상 복원](../../assets/logs/wifi_link/2026-10-16_ur03_acs08_restore_pwm_run01/observations.json) | 최초 회차의 RECOVERY_PENDING은 후속 두 회차로 보완. 모든 stop ACK/TEL 오류 조합을 뜻하지 않음 |

## 마지막 AC-S02 결과와 관측기 수정

- B ARM 회차: boot3570331004, A6/B7, control8. B의 ticket67867 ARM은 TICKET_REJECTED였다. A의 zero CMD 14개(seq573834456~469)는 모두 ACK됐고 마지막 DISARM573834470과 새 정지 TEL이 일치했다. 10.294016초 캡처에서 D4/PB6·D6/PC7·D7/PB7 LOW, 정지 ACK 뒤 약6.79초 ARM/CMD 재발 없음. B ticket age241.2ms/광고 TTL150ms이므로 취소와 만료가 함께 적용된 입력이다.
- B DISARM 회차: A3/control7을 B4의 DISARM573834451이 정지시켰다. B의 ACK와 일치 DISARMED TEL은 A 후속 DISARM573834452보다 먼저 관측됐다. A는 경합한 CMD의 BUSY 응답에 보호 DISARM을 보냈다. 기존 helper가 이 seq 변경을 실패로 잘못 판단했으므로 브라우저 원본 INCOMPLETE를 그대로 보존하고 핵심 B 정지 판정을 별도로 기록했다.
- 수정 helper revision2는 B 정지 증거와 A 보호 DISARM을 따로 추적한다. PC 회귀 검사는 완료했으며 수정 helper의 추가 실물 회차는 실행하지 않았다. 이미 확보한 B 정지 근거를 다시 얻기 위한 재시험은 요구하지 않는다.
- A/B는 별도 WebSocket 세션이다. 시험 스크립트가 한 페이지 내부에 B를 만들므로 두 번째 브라우저 탭을 열거나 전환할 필요가 없다.

## 보존할 실패와 미해결 관측

- 동일 ticket run01~03의 미완료/시간 예산 부족과 run04 성공을 모두 보존한다. 한 번에 성공한 것으로 재작성하지 않는다.
- 탭 전환 run01은 캡처가 정지 전에 끝났고 run02로 보완했다. 관측된 정지 후 시간과 사용자가 페이지에 돌아온 후 시간을 혼동하지 않는다.
- [AC-S06 복원 run01](../../assets/logs/wifi_link/2026-10-17_ur03_acs06_restore_pwm_run01/observations.json)의 수동 DISARM 전 자동 정지/명령 전달 공백 원인은 미확정이다. 사용자 포커스 전환 없음 보고를 유지한다. 후속 정상 run02나 탭 전환 시험으로 원인이 해결됐다고 쓰지 않는다.
- ESP reset의 D1 transient와 앞선 UART 양끝 0.25µs 단발 차이 원인은 미확정이다. 캡처 경계의 불완전 프레임은 원본에 남기고 완전 프레임 집계에서 제외한다.

## 복원 상태와 물리 조건

- 현재 ESP 소스 WIFI_UART_PARTIAL_TEST_MODE=0U, STM 시험 switch 14개=0U. 정상 이미지 복원과 수동 제어 근거는 위 AC-S04/S06/S08 후속 회차에 있다.
- UTF-8 정규화 소스 SHA256: ESP main `2122b341e74e2a85019dff3e060c8b2995667438f8df8a779cecfd170099d2a0`, STM protocol `a3cac86b2e10e715dc5bf1477209b69966b3a0b9ac105d3195c8a61c2ca73370`. 소스 식별값이며 플래시 바이너리 readback을 대신하지 않는다.
- 마지막 보고: 두 USB·LiPo 연결, S1 ON/S0 해제, #1 보드용 2핀 두 개와 MDD10A B+ 분리·절연, #2 감지 회로 공급·공통 GND. 종료 전원 분리 완료는 미보고다.
- LA 4MHz: D0=JDBG_UART Pin1/PA9 TX, D1=Pin2/PA10 RX, D4=JDBG_CTRL_1 Pin2/PB6, D6=JDBG_CTRL_2 Pin2/PC7, D7=JDBG_CTRL_2 Pin1/PB7. D2/D3 제거, 기존 D5 대신 D7. GND=JDBG_UART Pin3.

## 다음 단계

이번 zero-only 시험 묶음은 완료다. 코드·배선 변경, 새 실패 또는 사용자의 재시험 요청 없이 완료 회차를 반복하지 않는다. 다음 작업은 [전체 MVP 계획](../plans/00_Project_Master_Plan_To_Final_MVP_ko.md)의 전력·배터리·기구·nonzero 통합 중 한 Gate의 선행 조건을 검토하고 선택하는 것이다. 새 하드웨어 조작이나 nonzero 송신은 이 마감으로 승인되지 않는다. 전체 AC-B/S 세부 경로·전력/기계 안전·주행 완료 판정은 유지된 별도 범위다.
