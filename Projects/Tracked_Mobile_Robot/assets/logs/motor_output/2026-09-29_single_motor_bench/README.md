# 2026-09-28~29 단일 모터 시험 원본

사용자가 첨부한 ESP 모니터 로그12개를 바이트 변경 없이 복사했다.
총262,862bytes이며 첨부 원본과 SHA-256 일치를 확인했다.
로그는 상대 uptime만 포함한다. 날짜는 대화 세션 기준이다.

- [검증 보고서와 육안 관찰](../../../../docs/verification/31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md)
- [원본 출처·파일 크기·SHA-256·현재 소스 해시](manifest.json)
- [기계 추출 요약](summary.json): TEL 수·시간 범위·값 집합·구동 샘플·첫 timeout·최종0 구간

소스 해시는 시험 마감 당시의 스냅샷이다. 후속 파일명 변경도 원본 manifest에 소급 반영하지 않는다.
2026-09-29 후속 정리에서 ESP 소스를 `hello_world_main.c` →
[uart_bridge_main.c](../../../../03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c)로 변경했다.
ESP 소스 바이트와 SHA-256은 동일하다. Python 검사의 소스 경로 문자열은 변경되어 해당 검사 파일의 현재 해시는 마감 당시와 다르다.

| 번호 | 원본 | 용도 |
| --- | --- | --- |
| 01 | [UART startup](01_uart_startup_ready.txt) | 세 가닥 연장 후 READY |
| 02 | [수동 reset](02_manual_estop_reset.txt) | ESTOP_RESET 응답 |
| 03 | [A/M1 +5%](03_m1_a_positive_5pct.txt) | 소리·떨림, 회전 없음 |
| 04 | [A/M1 +10%](04_m1_a_positive_10pct.txt) | 회전, 실제 전진 방향 미확인 |
| 05 | [A/M1 −10%](05_m1_a_negative_10pct.txt) | 역회전 |
| 06 | [B/M2 첫 시험](06_m2_b_initial_no_rotation.txt) | 소리, 회전 없음 |
| 07 | [연결 해석 미확정 시험](07_m2_uncertain_connector_trial.txt) | 교차시험 판정에서 제외 |
| 08 | [A/M2 교차시험](08_m2_a_cross_test.txt) | 역회전, right 입력 반응 |
| 09 | [B/M1 교차시험](09_m1_b_cross_test.txt) | 정방향, left 입력 반응 |
| 10 | [B/M2 원래 연결 복원](10_m2_b_positive_before_dir_fix.txt) | 양수 명령에 역회전 |
| 11 | [DIR 보정 후 B 정방향](11_m2_b_forward_after_dir_fix.txt) | 실제 전진·right_cps 양수 |
| 12 | [DIR 보정 후 B 역방향](12_m2_b_reverse_after_dir_fix.txt) | 실제 역회전·right_cps 음수 |

육안 관찰은 로그 자체에 기록돼 있지 않은 경우가 있어 보고서에서 사용자 보고와 분리했다.
TEL의 PWM은 직접 계측 파형이 아니며,0 복귀 시간은100ms 주기 관측 범위다.
원본11의err=0과12의err=1439는 각각 일정하나, 그 사이 증가 원인은 미확정이다.
