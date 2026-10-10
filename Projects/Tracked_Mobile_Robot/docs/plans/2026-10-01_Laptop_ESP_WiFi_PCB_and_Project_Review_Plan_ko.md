# 노트북·ESP로 진행하는 Wi-Fi, PCB 설계와 프로젝트 이해

작성일: 2026-10-01. 상태: **사용자 빌드·플래시 성공, AP HTTP 접속·갱신·연결 해제/복구 확인 / 새 PCB CAD 미실행**.
사용자는 노트북과 ESP32-S3를 가지고 있다. STM32·만능기판·모터는 현재 작업 환경에 없다.
AP·공유기·노트북 핫스폿 가능성을 모두 열어 두었으며 접속 방식은 아직 고정하지 않았다.

## 목표와 가능한 범위

| 작업 | 현재 환경에서 진행할 일 | 다른 장비가 있어야 확인할 일 |
| --- | --- | --- |
| PC↔ESP Wi-Fi | 접속, HTTP 응답, ESP 자체 상태 표시, 해제·재접속 | STM TEL 전달, 무선 명령과 실제 출력/정지 |
| 확장 PCB | ADC·CAN 요구사항, 회로도·계산·커넥터 표, 배치 초안 | CAN 모듈 치수/단자, 층간 높이·장착홀·하네스, 제작 후 시험 |
| 문서·프로젝트 이해 | 코드·배선·검증의 연결 설명, 현재 안내와 근거의 불일치 수정 | 문서 수정만으로 미검증 하드웨어를 PASS로 바꾸지 않음 |

첫 완료 목표는 **ESP 단독 Wi-Fi 상태 페이지**다. 기존 UART bridge와의 통합은 다음 단계다.
펌웨어는 설명과 완결된 코드 블록을 제공하면 사용자가 입력하고 빌드·플래시하는 기존 방식을 따른다.

## 먼저 이해할 두 통신 구간

```text
현재 PC 입력: PC → USB-UART 변환 → ESP UART0 수동 콘솔
현재 보드 통신: ESP UART1 GPIO17/18 ↔ STM USART1 PA10/PA9
추가할 PC 경로: PC 브라우저 ↔ Wi-Fi/IP/HTTP ↔ ESP 네트워크 처리
```

무선으로 바꾸는 대상은 PC↔ESP다. ESP↔STM UART1은 기존 배선을 사용한다.
USB로 ESP에 전원을 공급해도 데이터가 HTTP로 오가면 그 데이터 경로는 무선이다.
USB는 초기 플래시·문제 확인에 계속 사용할 수 있다. USB 케이블 자체를 없앨 때는 로봇의 ESP 공급 경로를 확인한다.

현재 bridge는 STM의 DISARM ACK와 PONG을 받아야 READY가 된다.
STM이 없을 때 기존 코드의 startup 실패를 Wi-Fi 접속 실패로 해석하지 않는다.
단독 단계는 작은 별도 ESP 프로젝트로 준비한 뒤 통합한다.
`03_Firmware/esp32_wifi_link`의 입력본 검토 뒤 사용자가 오타/누락을 수정하고 빌드·플래시했다.
AP 시험 결과는 [10/1 진행 기록](../progress/2026-10-01_progress.md#wi-fi-ap-실측--w1w2w3-결과)을 따른다.

## 1. Wi-Fi 연결과 표시

### 설정으로 접속 방식 선택

| 방식 | 구조·용도 | 확인할 점 |
| --- | --- | --- |
| ESP AP | ESP가 Wi-Fi를 만들어 공유기 없이 노트북이 직접 접속 | 노트북의 기존 Wi-Fi 인터넷 연결이 끊길 수 있음 |
| 공유기 STA | ESP와 노트북이 같은 공유기에 접속 | 2.4 GHz 접속, 게스트/AP 격리, ESP IP |
| 노트북 핫스폿 STA | ESP가 Windows 모바일 핫스폿에 접속 | 어댑터·공유 설정과 실제 접속 가능 여부 |

AP와 STA는 시작 설정으로 선택한다. AP+STA 동시 운용이나 자동 전환은 첫 시험의 필수 기능이 아니다.
실제 접속 비밀번호를 로그나 공개 저장소에 남기지 않는다.

### 단계와 완료 조건

- [x] 현재 UART0/UART1 구분, startup 조건, 로컬 ESP-IDF 6.0.2 예제 확인.
- [x] 별도 프로젝트 scaffold·코드 안내, 입력본 검토와 사용자 수정·빌드·플래시.
- [x] **W1 접속(AP):** 192.168.4.1의 HTTP 상태 페이지에서 실제 ESP JSON 수신.
- [x] **W2 상태 표시(AP):** uptime_ms·수신 시각이 반복 갱신되며 같은 부팅에서 boot_id 유지.
- [x] **W3 재접속(AP):** 연결 해제 표시·마지막 값 보존·재접속 자동 복구를 사용자 통과 보고로 확인. 재플래시 후 boot_id는 바뀌고 이후 해제·재접속에서는 유지.
- [ ] **W4 bridge 통합:** STM UART 수신 결과를 동기화된 snapshot으로 HTTP에 전달한다. STM이 있을 때 실제 TEL·stale·연결 실패를 확인한다.
- [ ] **W5 무선 명령:** 입력 검증·명령 유효시간·연결 유실 처리를 설계한 뒤 STM/모터 장비에서 확인한다.

W1~W3는 노트북·ESP로 검증 가능하다. 이 결과를 W4/W5 완료로 확대하지 않는다.
이번 실측은 AP 구성이다. 공유기/노트북 핫스폿 STA, 별도 전원 재인가 시험과 재부팅 직후 uptime 초기화 수치는 미기록이다.
첫 API 후보는 `GET /api/status`다. STM이 없으면 `stm_connected=false`, 모터 상태와 CPS는 `null`로 표시한다.
시험 데이터를 쓰게 되면 실제 측정과 구분한다. 생성한 `0 CPS`로 모터 정지를 주장하지 않는다.
HTTP 상태 조회부터 검증하고 지속적인 양방향 전달이 필요해질 때 WebSocket을 판단한다.

### 통합할 때의 책임

```text
STM UART 수신 → 기존 parser → 검증된 TEL 보관 → snapshot 갱신
HTTP 상태 요청 → snapshot 읽기 → JSON 응답

후속 명령:
네트워크 입력 → 형식·세션·유효시간 검사 → 전달 큐
→ UART bridge 한 경로에서 seq/ACK/송신 관리 → STM 상태·안전 검사
```

HTTP handler는 별도 ESP-IDF task에서 실행되므로 여러 task가 `s_telemetry`를 그대로 읽고 쓰지 않는다.
snapshot 복사에 필요한 짧은 동기화를 두며 HTTP 응답 동안 UART 처리를 막지 않는다.
handler에서 `bridge_bench_command()`를 직접 호출하지 않는다. 현재 bench는 부팅당 한 번의 제한 시험이다.
PC 명령이 만료되면 과거 명령을 새 seq로 계속 재전송하지 않는다. 재접속·재부팅으로 자동 ARM하거나 구동을 재개하지 않는다.
STM의 timeout·E-stop은 계속 적용한다. 구체적인 유효시간·큐·중지 절차는 명령 단계에서 확정한다.

## 2. 기존 부품을 유지하는 확장 PCB

첫 범위는 **ADC 두 채널 + 보유 CAN 모듈 접속 + 로직 전원·시험점**이다.
기존 STM/ESP 헤더, K2/U1, 엔코더 조정부와 PWM/DIR 풀다운은 현재 기판에 유지하는 안을 따른다.
MDD10A·XL4015·K1·버스바·퓨즈의 주전류 경로는 확장 PCB에 넣지 않는다.

| 기능 | 연결 기준 | 설계에서 정할 것 |
| --- | --- | --- |
| K1 전단 ADC | 보호·분압 출력→PA4 | 최대 입력, 저항 오차/전력, 필터, ADC 샘플 시간, MCU 무전원 입력 경로 |
| K1 후단 ADC | 별도 보호·분압 출력→PB0 | 후단 잔류 전압의 해석과 측정점 |
| CAN MCU 측 | PA12 TX→D/TXD, R/RXD→PA11 RX, 3V3/GND | MCU-230 실제 핀 순서·RS·종단·소비전류 |
| CAN 버스 측 | CANH/CANL 외부 커넥터 | 극성·필요한 기준선, 종단 선택과 보호 |
| 층간 연결 | ADC 신호/GND, CAN 논리 신호/전원 | 커넥터·핀 번호·높이·인출 방향 |

- [x] KiCad 10.0.5 설치와 기존 RevC 확인. RevC `.kicad_pcb`는 헤더만 있는 빈 파일이다.
- [ ] **P1 요구사항:** 기능·입출력·미확정 부품을 표로 고정한다.
- [ ] **P2 회로도:** 별도 확장 프로젝트에 ADC 계산·보호와 CAN 모듈 접속 회로를 작성한다.
- [ ] **P3 논리 검토:** datasheet/현재 핀 계약 대조, ERC와 예외 사유 기록.
- [ ] **P4 배치 초안:** 기능 구역·커넥터 접근·층간 신호 흐름을 정하고 실측 전 치수는 가정으로 표시한다.
- [ ] **P5 제작 검토:** 실측·전원 확인 → 1:1 출력/간섭 → DRC → 제작 파일 검토.

지금 P1~P3와 가정을 명시한 P4를 진행할 수 있다.
기존 10×15 cm 적층 구상은 공간 예산이며 새 PCB 외곽을 고정한 조건은 아니다.
MCU-230 모듈 대신 SN65HVD230 IC 치수로 풋프린트를 확정하지 않는다.

## 3. 문서 수정과 코드 이해

[코드 구조와 함수 지도](../../07_Embedded_Learning_Notes/01_Concept_Notes/09_STM32_ESP32_Source_Structure_and_Function_Map_ko.md)
→ [ESP 실제 소스](../../03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c)
→ [단일 모터 시험 근거](../verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md) 순서로 읽는다.

| 이해할 질문 | 찾아볼 위치 |
| --- | --- |
| PC 입력과 STM 응답은 어떤 UART인가? | `bridge_bench_console_poll()`과 `app_main()` |
| STM이 없으면 왜 READY가 안 되나? | `bridge_uart_startup_step()`과 matching ACK/PONG |
| TEL은 어디서 해석·보관하나? | `bridge_uart_handle_rx_line()`과 `s_telemetry` |
| 무선 페이지가 멈춰도 STM이 정지해야 하는 이유는? | STM timeout/E-stop과 PC 명령 유효시간 |
| PCB와 펌웨어의 역할은? | 분압·보호·CAN 물리 신호와 ADC 진단·CAN protocol |

ESP의 Wi-Fi·HTTP task와 STM의 FreeRTOS 도입은 별개다. 이번 작업 때문에 STM HAL bare-metal 구조를 바꾸지 않는다.

- [x] ESP README의 8월 Current/재개 절차를 역사적 범위로 표시하고 최신 링크 추가.
- [x] 실행 계획 색인의 9/29 “현재 재개” 안내를 당시 계획으로 수정.
- [x] ESP 역할 문서의 A 방향 미완료 안내를 report32 근거로 수정.
- [ ] 다른 불일치는 근거·종류·영향을 확인해 수정한다. 과거 판정을 현재 판정으로 덮어쓰지 않는다.

## 바로 다음 작업

AP HTTP 시험 묶음은 완료했다. 먼저 실제 코드의 `wifi_event → server_start → page_get/status_get → 브라우저 갱신` 흐름을 시험 결과와 연결해 이해한다.
노트북·ESP 환경에서 이어갈 후보는 WebSocket 상태 전송과 STA 접속 시험이다. WebSocket은 추천 후속 방향이며 아직 구현하지 않았다.
STM 장비가 돌아오면 W4의 실제 TEL·stale 검증을 진행한다. W5 무선 구동 명령은 별도 유효시간/안전 검증 뒤에 진행한다.
PCB P1/P2는 독립된 작업 묶음으로 진행할 수 있다.

## 근거

- [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md), [확장 구상](../../09_Electrical_Design/13_Two_Deck_Perfboard_Expansion_Feasibility_2026-09-30_ko.md), [핀 배정](../../01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md).
- 로컬 ESP-IDF 6.0.2의 `examples/wifi/getting_started/softAP`·`station`과 `examples/protocols/http_server/simple`을 확인했다. 코드/API는 이 설치 버전을 기준으로 대조한다.
- [Espressif Wi-Fi](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/wifi-driver/index.html), [HTTP 서버](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/protocols/esp_http_server.html).
  웹 stable은 확인 시 v6.1이며 설치된 6.0.2에 새 API가 있다고 가정하지 않는다.
