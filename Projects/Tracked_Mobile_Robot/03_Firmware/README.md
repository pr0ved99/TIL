# 펌웨어 앱과 검사 안내

상태 대조: **2026-10-11**. 마지막 보드 실행, 새 모듈 준비, 다음 구현을 구분한다.
재개 전에는 [현재 인수인계](../docs/handoff/CURRENT_SESSION_CONTEXT.md)와 [최신 진행 기록](../docs/progress/README.md)을 먼저 읽는다.

## 앱 선택과 마지막 실행

| 프로젝트 폴더 | 역할·진입점 | 확인한 상태 |
| --- | --- | --- |
| [stm32_uart_mvp](stm32_uart_mvp/) | [main.c](stm32_uart_mvp/Core/Src/main.c)와 [UART 프로토콜](stm32_uart_mvp/Core/Src/uart_mvp_protocol.c). 명령 검사·상태/timeout·최종 출력 안전 판단 | W5 실제 PONG/ACK·TEL 관측. PA10 pull-up·PONG 시험 hook0U. 전체 전력단·주행 수용과 별개 |
| [esp32_wifi_link](esp32_wifi_link/README.md) | [wifi_link_main.c](esp32_wifi_link/main/wifi_link_main.c). STM TEL을 WebSocket으로 전달하고 브라우저 PING/DISARM을 UART 응답과 연결 | **현재 마지막 실행 ESP 앱**. W4/W5 비구동 PASS. 이후 ARM/CMD 기초 모듈 포함 빌드 성공은 사용자 확인, 새 플래시/보드 실행은 미확인 |
| [esp32_uart_bridge](esp32_uart_bridge/README.md) | [uart_bridge_main.c](esp32_uart_bridge/main/uart_bridge_main.c). 기존 UART bring-up·모터 시험 콘솔 | 별도 앱의9/30 M2_RUN 수동 hook1U와 default-off30 PASS/1 FAIL 이력. Wi-Fi 앱의 설정이 아님. hook 복구·해당 앱 재빌드/플래시·release는 별도 |
| [esp32_examples](esp32_examples/README.md) | Hello World·FreeRTOS·STA·HTTP·WebSocket 단계별 연습 | 각 하위 폴더가 별도 ESP-IDF 프로젝트. 예제 플래시는 ESP의 실행 앱을 바꾸며 실제 Wi-Fi/UART 연동 검증과 구분 |

마지막 W5 시험은 STM·ESP 각각 USB 전원, LiPo 미연결이었다. 종료 후 두 USB 분리 완료는 사용자 확인이다.
UART 탈거·보드 탈거나 다음 연결 상태는 추정하지 않는다. 전원·배선·플래시 작업은 사용자가 해당 Gate 조건에 맞춰 수행한다.

## ARM/CMD 모듈과 실행 경로

세 기초 모듈은 [CMake](esp32_wifi_link/main/CMakeLists.txt)에 등록돼 있다.
**현재 main은 이 모듈을 호출하지 않으며 UART ARM/CMD·브라우저 제어 입력은 미연결이다.**

| 파일 | 담당하는 일 | 현재 증거와 한계 |
| --- | --- | --- |
| [wifi_link_main.c](esp32_wifi_link/main/wifi_link_main.c) | 실제 TEL 파싱·snapshot, W5 입력 검사/큐·UART 응답 대응·notice/result·버튼 | W5 보드 관측과 PAGE JS57·선택 C 함수 PC21은 서로 다른 증거 |
| [wifi_control_contract.h](esp32_wifi_link/main/wifi_control_contract.h) / [.c](esp32_wifi_link/main/wifi_control_contract.c) | ARM/CMD 문자열을 요청 정보로 파싱하고 형식·ID·숫자 범위·zero-only 여부 검사 | 실제 저장본 PC15 PASS. 수락/송신·제어 상태를 결정하지 않음 |
| [wifi_control_ticket.h](esp32_wifi_link/main/wifi_control_ticket.h) / [.c](esp32_wifi_link/main/wifi_control_ticket.c) | boot/연결/control ID/용도에 묶인 일회용 ticket 발급·소비·만료/취소 | 실제 저장본 PC12 PASS. UART·큐·태스크 경합을 검사하지 않음 |
| [wifi_control_owner.h](esp32_wifi_link/main/wifi_control_owner.h) / [.c](esp32_wifi_link/main/wifi_control_owner.c) | 제어 연결 한 개의 식별 기록·새 control ID·대조/취소 | 실제 저장본 PC9 PASS. 예약 성공은 ARM 허가가 아님 |
| 다음 상태·시간 제한 흐름 | ARM→zero ACK/TEL→ACTIVE, 기한·취소·STOPPING/BLOCKED와 정지 확인 | **미구현/미검증**. 기초 모듈 검사 결과로 AC-H 전체·AC-B/S를 PASS 처리하지 않음 |

owner 포함 ESP 전체 빌드 성공은 사용자 보고다. 빌드 원본 로그·바이너리 hash와 새 플래시/보드 실행은 아직 확인하지 않았다.
입력 후보 검사, 실제 저장본 PC 검사, 전체 ESP 빌드, 보드 실행, 전기/기계 관측을 각각 기록한다.

입력 안내: [parser](../docs/plans/2026-10-10_WiFi_ARM_CMD_Parser_Code_Guide_ko.md) ·
[ticket](../docs/plans/2026-10-10_WiFi_ARM_CMD_Ticket_Code_Guide_ko.md) ·
[owner](../docs/plans/2026-10-11_WiFi_ARM_CMD_Owner_Code_Guide_ko.md).

## 빌드와 검사 시작점

- STM32는 `stm32_uart_mvp`를 STM32CubeIDE로 가져온다. 현재 `.ioc`와 USER CODE를 유지하고 사용자 빌드/플래시 결과를 기록한다.
- 현재 ESP 앱은 VS Code에서 **`esp32_wifi_link` 폴더**를 프로젝트로 열고 [해당 빌드 안내](esp32_wifi_link/README.md#빌드검사)를 따른다. UART bridge나 예제 폴더에서 빌드한 결과와 구분한다.
- PC 검사는 [tests README의 종류와 선택](tests/README.md#검사-종류와-선택)을 따른다. native C에는 TCC/GCC, PAGE 검사에는 Node.js가 필요하며 의존성 부재의 SKIP은 PASS가 아니다.
- 빌드/플래시 식별값·원본 로그·화면·관측 조건은 [증거 보존 절차](../docs/verification/EVIDENCE_CAPTURE_GUIDE_ko.md)를 따른다. 개인 Wi-Fi header는 Git에서 제외한다.

## 다음 구현

[ARM/CMD 초기 계약](../docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md)에 따라 상태·시간 제한·ACK/TEL·취소/정지 흐름을 준비한다.
이후 큐/UART·브라우저 zero-only 연결과 AC-H 전체를 검사하고, 실제 장비 조건에 맞춰 AC-B 또는 AC-S로 진행한다.
낱개 보드의 PC7 HIGH/FAULT는 우회하지 않는다. nonzero 구동·전력단·주행은 별도 선행 Gate를 따른다.
코드/배선 변경이나 실패가 없는 완료 시험은 반복하지 않는다.
