# W4 마감 증거 — 2026-10-08

실제 STM TEL→ESP UART→WebSocket과 STARTUP READY/FAILED 분리 시험을 보존한다.
조건·판정·수치·남은 한계는 [보고서33](../../../../docs/verification/33_W4_STM_UART_WebSocket_and_Startup_Status_2026-10-08_ko.md)을 따른다.

| 파일 | 출처와 범위 |
| --- | --- |
| [manifest.json](manifest.json) | 원본 첨부·발췌 해시, 마감 소스 해시, 빌드/시뮬레이션 증거 경계와 전원 조건. 소스 해시와 플래시 바이너리 동일성은 미확인 |
| [browser_observations.json](browser_observations.json) | 사용자가 보낸 화면의 선택 필드를 수동 전사. 원본 이미지 파일이나 완전한 JSON 응답이 아님 |
| [logic_capture_summary.json](logic_capture_summary.json) | 이전 분석 캐시에서 필요한 TX LOW·EN·UART 응답·TEL 분포 추출. 원본 sr/pvs의 경로·해시 포함. 마감 시 파형 해석을 다시 실행하지 않음 |
| [startup_disarm_ack_missing_user_excerpt.txt](startup_disarm_ack_missing_user_excerpt.txt) | 사용자의 인라인 UART 발췌 전사. 전체 raw monitor log 아님 |
| [startup_ready_recovery_uart_excerpt.txt](startup_ready_recovery_uart_excerpt.txt) | 첨부 로그에서 wifi_link 로그와 USB 재접속 안내 추출 |
| [startup_pong_missing_uart_excerpt.txt](startup_pong_missing_uart_excerpt.txt) | 첨부 로그에서 wifi_link 로그와 USB 재접속 안내 추출 |

두 첨부 발췌는 부트로더/Wi-Fi 식별 정보 등의 줄을 제외했으며, 선택 규칙과 원본 해시는 manifest에 기록했다. 개인 Wi-Fi 설정 header·비밀번호는 포함하지 않는다.

최종 브라우저는 READY·TEL fresh·PWM/CPS=0, drop=0, err=1이었다. USB 전원 분리 완료는 아직 보고되지 않았다. W4 범위를 W5 무선 구동·전류/열·전체 MVP 완료로 확대하지 않는다.

- [Git 직전 계약 검사](git_preflight_contract_tests.txt):31개 중30 PASS/1 FAIL. 별도 UART bridge M2_RUN hook1U의 default-off 미충족이며 W4 브라우저25 PASS와 다른 검사다.
