# 두 보드 재연결과 state 입력 후보 검사 — 2026-10-11

- 사용자 조건: ESP32·STM32만 보유, UART 교차 연결 완료 보고. USB 공급을 안내했으며 공급 방식/종료 상태는 별도 확인되지 않았다.
- 제공 로그: DISARM seq678490831 ACK, PING seq678490832 PONG, STARTUP READY. TEL #6~120은 t_ms482800~494200, FAULT/ESTOP_ACTIVE·PWM0/0·drop/err0/0이다.
- 제공 로그의 CPS는 왼쪽 일부±10, 오른쪽−200~−240이다. 후속 사용자가 **핀들이 바닥에 닿았으며 보드를 띄우자 값의 튐이 사라졌다**고 확인했다. [사용자 확인](cps_floor_contact_user_confirmation.txt)을 따른다. 앞선 부동 입력 잡음 추정 대신 접촉 조건 변화와 증상 해소를 기록하며, 해소 후 정확한 CPS 수치는 별도 미보고다. 엔코더 미연결 조건으로 실제 속도/기계 정지 증거가 아니다.
- [UART 발췌](uart_reentry_user_excerpt.txt)는 사용자 attachment에서 wifi_link 줄만 추출했다. Wi-Fi SSID/BSSID·stack·favicon 요청을 제외했다. 제공 구간을 전체 연속 모니터 원본으로 확대하지 않는다.
- [후보 PC 출력](pc_state_candidate.txt): 안내의 state C를 저장된 owner C와 TCC `-Wall -Werror`로 컴파일·실행, **27 tests/PASS**.
- [저장본 미입력 출력](pc_state_saved_unavailable.txt): 후보 환경 변수 제거 후 **0 tests/SKIP1**. 새 state 실제 저장본·ESP 전체 빌드·보드 적용 결과가 아니다.
- [source_snapshot](source_snapshot/)은 검사한 C 두 후보·실제 의존 파일·검사 fixture/runner의 byte 보존본이다. 전체 안내 Markdown hash는 실행 출력에 기록되며 이후 설명 갱신과 C 블록 동일성을 구분한다.
- [manifest](manifest.json)의 파일 byte/SHA256은 보존 내용의 식별값이다. 새 플래시/바이너리 hash·UART TX/RTOS 경합·AC-H 전체·AC-B/S는 증명하지 않는다.

다음: [state 입력 안내](../../../../docs/plans/2026-10-11_WiFi_ARM_CMD_State_Code_Guide_ko.md)의 두 파일과 CMake를 사용자 입력 → 실제 저장본 검사 → 사용자 ESP 전체 빌드 → 실행 adapter 연결.
