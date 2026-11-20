# main 연결 후보 PC 검사 — 2026-10-13

- [전체 교체본](../../../../docs/plans/2026-10-13_WiFi_ARM_CMD_Main_Integration_Code_Guide_ko.md)의 C 블록이 검사 대상이다. 실제 main에는 미적용이다.
- [C 출력](pc_main_adapter.txt): W5 21 + adapter 21 = 42 PASS. 실제 후보 함수와 저장 모듈을 PC에서 컴파일·실행했다. RTOS/UART/HTTP 호출은 mock이다.
- [PAGE 출력](pc_browser.txt): 27 PASS. 후보의 내장 JS와 모의 DOM·시계·WebSocket을 실행했다.
- [manifest](manifest.json): 후보 C·안내·기존 main·모듈·검사 코드 SHA256. 기존 모듈 byte snapshot은 executor 저장본 검토 artifact를 참조한다.
- ESP 전체 빌드·실제 UART·동시 태스크·무선 지연·출력/주행은 미검증. 실제 보드 PASS로 확대하지 않는다.
