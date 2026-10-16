# 펌웨어 앱과 검사 안내

상태 대조: **2026-10-17**. 정상 이미지 복원과 선택 zero-only 실물시험 완료, 전체 구동 수용은 구분한다.
재개 전에는 [현재 인수인계](../docs/handoff/CURRENT_SESSION_CONTEXT.md)와 [최신 진행 기록](../docs/progress/README.md)을 먼저 읽는다.

## 앱 선택과 마지막 실행

| 프로젝트 폴더 | 역할·진입점 | 확인한 상태 |
| --- | --- | --- |
| [stm32_uart_mvp](stm32_uart_mvp/) | [main.c](stm32_uart_mvp/Core/Src/main.c)와 [UART 프로토콜](stm32_uart_mvp/Core/Src/uart_mvp_protocol.c). 명령 검사·상태/timeout·최종 출력 안전 판단 | W5 실제 PONG/ACK·TEL 관측. PA10 pull-up·PONG 시험 hook0U. 전체 전력단·주행 수용과 별개 |
| [esp32_wifi_link](esp32_wifi_link/README.md) | [wifi_link_main.c](esp32_wifi_link/main/wifi_link_main.c). STM TEL을 WebSocket으로 전달하고 브라우저 PING/DISARM을 UART 응답과 연결 | **현재 마지막 실행 ESP 앱**. W4/W5 완료 이후 zero-only ARM/CMD 연결·사용자 빌드/플래시·일부 보드 관측. 전체 수용은 미완료 |
| [esp32_uart_bridge](esp32_uart_bridge/README.md) | [uart_bridge_main.c](esp32_uart_bridge/main/uart_bridge_main.c). 기존 UART bring-up·모터 시험 콘솔 | 별도 앱의9/30 M2_RUN 수동 hook1U와 default-off30 PASS/1 FAIL 이력. Wi-Fi 앱의 설정이 아님. hook 복구·해당 앱 재빌드/플래시·release는 별도 |
| [esp32_examples](esp32_examples/README.md) | Hello World·FreeRTOS·STA·HTTP·WebSocket 단계별 연습 | 각 하위 폴더가 별도 ESP-IDF 프로젝트. 예제 플래시는 ESP의 실행 앱을 바꾸며 실제 Wi-Fi/UART 연동 검증과 구분 |

마지막 W5 시험은 STM·ESP 각각 USB 전원, LiPo 미연결이었다. 종료 후 두 USB 분리 완료는 사용자 확인이다.
UART 탈거·보드 탈거나 다음 연결 상태는 추정하지 않는다. 전원·배선·플래시 작업은 사용자가 해당 Gate 조건에 맞춰 수행한다.

## ARM/CMD 모듈과 실행 경로

다섯 제어 모듈과 main이 [CMake](esp32_wifi_link/main/CMakeLists.txt)에 등록돼 있고, 브라우저→HTTP 접수→executor→UART→ACK/TEL→브라우저 흐름이 연결돼 있다. 현재 Wi-Fi 제어는 **속도 0 전용**이다.

| 파일 | 담당하는 일 | 근거와 범위 |
| --- | --- | --- |
| [wifi_link_main.c](esp32_wifi_link/main/wifi_link_main.c) | 실제 태스크·소켓·UART·내장 PAGE 연결 | 최신 선택 C 함수42·PAGE46 PC PASS; 사용자 보드 관측은 별도 |
| [contract](esp32_wifi_link/main/wifi_control_contract.c) | 문자열·필드·범위 검사 | 저장본 PC15 이력 |
| [ticket](esp32_wifi_link/main/wifi_control_ticket.c) | 일회용 제출 기회·식별·만료 검사 | 저장본 PC12 이력 |
| [owner](esp32_wifi_link/main/wifi_control_owner.c) | 제어 연결·세대 예약/대조/해제 | 저장본 PC9 이력 |
| [state](esp32_wifi_link/main/wifi_control_state.c) | ARM→zero 확인→ACTIVE, 취소·STOPPING/BLOCKED | 저장본 PC27 이력 |
| [executor](esp32_wifi_link/main/wifi_control_executor.c) | 접수·프레임 준비·송신 결과·응답 연결 | 저장본 PC17 이력 |

10/16 STM CAN 줄 폐기와 ESP DISARM CAN+LF를 적용하고 부분 CMD/ARM 실물 폐기·복원을 확인했다. 10/17 AC-S01~08 선택 zero-only 실물 시나리오를 마감했다. [보고서37](../docs/verification/37_Zero_Only_ACS_Bench_Closeout_2026-10-17_ko.md) 참조. 현재 ESP mode0·STM 시험 switch14개0U이며 source hash와 바이너리 readback은 구분한다. 전체 세부 오류·nonzero 구동 수용은 별도다.

구현 이유와 예제는 [STM·ESP 교과서](../07_Embedded_Learning_Notes/06_STM32_ESP32_Firmware_Textbook/README.md)에 있다. 날짜별 코드 입력 안내는 해당 당시 판본이며 최신 소스를 덮어쓰는 용도로 사용하지 않는다.

## 빌드와 검사 시작점

- STM32는 `stm32_uart_mvp`를 STM32CubeIDE로 가져온다. 현재 `.ioc`와 USER CODE를 유지하고 사용자 빌드/플래시 결과를 기록한다.
- 현재 ESP 앱은 VS Code에서 **`esp32_wifi_link` 폴더**를 프로젝트로 열고 [해당 빌드 안내](esp32_wifi_link/README.md#빌드검사)를 따른다. UART bridge나 예제 폴더에서 빌드한 결과와 구분한다.
- PC 검사는 [tests README의 종류와 선택](tests/README.md#검사-종류와-선택)을 따른다. native C에는 TCC/GCC, PAGE 검사에는 Node.js가 필요하며 의존성 부재의 SKIP은 PASS가 아니다.
- 빌드/플래시 식별값·원본 로그·화면·관측 조건은 [증거 보존 절차](../docs/verification/EVIDENCE_CAPTURE_GUIDE_ko.md)를 따른다. 개인 Wi-Fi header는 Git에서 제외한다.

## 다음 작업

학습은 [교과서 단위 1](../07_Embedded_Learning_Notes/06_STM32_ESP32_Firmware_Textbook/README.md#study-route)에서 시작한다. 실물 검증은 [현재 인수인계](../docs/handoff/CURRENT_SESSION_CONTEXT.md)에 따라 미완료 항목만 이어간다. 전체 AC-B/S·nonzero 구동·전력단·주행은 별도이며 PC7 FAULT를 우회하지 않는다.

코드/배선 변경이나 실패가 없는 완료 시험은 반복하지 않는다.
