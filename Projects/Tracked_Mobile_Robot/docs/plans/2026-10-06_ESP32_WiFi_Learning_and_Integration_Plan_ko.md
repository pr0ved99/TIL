# ESP32 Wi-Fi 학습 및 통합 계획

작성일: **2026-10-06**, 갱신일: **2026-10-08**. 상태: **학습 예제 실행 확인 / 실제 앱 W4 읽기 전용 PASS / W5 미구현**.
완료 근거는 [W4 보고서33](../verification/33_W4_STM_UART_WebSocket_and_Startup_Status_2026-10-08_ko.md)와 [10/8 마감 기록](../progress/2026-10-08_progress.md)을 따른다.

## 1. 목적 및 배경

이 문서는 프로젝트 내 ESP32-S3의 역할과 그에 따른 펌웨어 학습 비중 및 통합 순서를 정의한다.

### 1.1 프로젝트 내 ESP32의 역할
프로젝트 아키텍처에 따르면 ESP32는 **"무선 창구"** 역할을 담당하며, 다음과 같이 역할이 명확히 분리된다.
*   **STM32 (메인 컨트롤러):** 모터 출력, 명령 타임아웃, 배터리 안전 감시, 엔코더 리딩, **최종 안전 게이트**
*   **ESP32-S3 (보조 컨트롤러):** 무선 통신(Wi-Fi), 웹페이지 호스팅, 상태(TEL) 전달, 명령 중계
*   **통신 경로:** UART (STM ↔ ESP)가 첫 브링업 경로이며, 향후 CAN으로 확장 예정.

ESP32가 다운되거나 Wi-Fi 연결이 유실되더라도, STM32가 자체 타임아웃 룰에 따라 로봇을 안전하게 정지시켜야 한다.

배터리 안전 감시는 STM의 설계 책임이다. 현재 TEL의 `batt_mv=0`은 고정 자리표시자이며 배터리 ADC 구현 완료를 뜻하지 않는다.

### 1.2 전체 프로젝트 학습 비중 제안
ESP32 학습은 "Wi-Fi 링크를 이해하고 안전하게 다룰 수 있는 최소선"으로 제한한다.
*   **STM32 / 안전 / 하드웨어 (약 50%):** 프로젝트의 핵심 가치. (HAL, 모터 제어, 엔코더, FreeRTOS, CAN)
*   **ESP32 / 무선 링크 (약 15~20%):** 기본 Wi-Fi 연결, WebSocket, STM 연동.
*   **시스템 통합 및 검증 (약 20%):** 벤치 시험, 신뢰성 검증, 물리적 안전 테스트.
*   **상위 계층 (약 10%):** 하위 레이어 검증 완료 후 ROS 2 연동 등.

이 비중은 학습 우선순위 제안이며 실제 투입 시간 측정이나 고정 일정은 아니다.

---

## 2. ESP32 학습 및 검증 우선순위

`03_Firmware/esp32_examples`의 학습용 코드들을 기반으로, 프로젝트 목표 달성에 필요한 필수 지식과 후순위 지식을 분류한다.

### 2.1 필수 지식 (먼저 진행)
| 항목 | 내용 | 관련 예제 |
|---|---|---|
| **기본 환경** | ESP-IDF 빌드/플래시/모니터 실행 흐름, 로그(ESP_LOGx) 출력, `app_main` 구조 | 01_hello_world |
| **OS 기본** | FreeRTOS 태스크(Task) 생성, 주기적 딜레이(`vTaskDelay`), 공유 자원 보호(Mutex) | 02_freertos_task |
| **Wi-Fi 기본** | Wi-Fi STA 모드 연결 과정, 이벤트 루프(WIFI_EVENT, IP_EVENT), 재접속 흐름 | 03_wifi_sta |
| **서버 기본** | HTTP 서버 구동, URI 핸들러 등록, 클라이언트 요청에 대한 텍스트 응답 | 04_http_server |
| **양방향 통신** | WebSocket 핸드셰이크, 프레임 수신 및 브로드캐스트 | 05_websocket |

### 2.2 프로젝트 본 작업(W4, W5) 중 학습할 지식
*   **UART 프로토콜:** 기존 `esp32_uart_bridge`의 줄 조립·필드·범위·sequence 검증과 timeout 처리. 현재 줄바꿈 ASCII 계약에 CRC/체크섬 구현이 있다고 가정하지 않는다.
*   **명령 유효시간 및 Stale 처리:** 기존 bench의 250ms는 ESP의 TEL age 감시 값이다. STM 기본 CMD timeout 300ms·bench 요청 500ms와 구분한다. W4는 TEL stale500ms·WebSocket 상태1000ms·브라우저 무응답4000ms로 구현·검증했다. 이 값들을 STM 명령 timeout과 혼동하지 않는다.
*   **Broadcast 방식:** 05의 `broadcast_text()`로 두 탭 기본 전송을 확인했다. 본 작업에서는 UART task와 HTTP task의 공유 snapshot·작업 예약·전송 오류를 다룬다.

### 2.3 후순위 지식 (현재 보류)
*   웹 인터페이스(UI/UX) 고도화 (HTML/CSS/JS 미관 작업)
*   SPIFFS/LittleFS 파일시스템을 이용한 정적 파일 서빙
*   OTA(Over-The-Air) 펌웨어 업데이트
*   블루투스(BLE), 고급 전력 관리(Deep Sleep) 등 기타 ESP 기능

---

## 3. 다음 실행 계획 (Next Actions)

학습 예제 단계를 마무리하고 실제 로봇 제어 코드(`esp32_wifi_link`)로 넘어가기 위한 순서다.

### 3.1 완료한 예제와 실제 앱 적용

04 `/hello` HTTP 응답과 05 브라우저 탭 A→B 메시지 전달은 [오늘 기록](../progress/2026-10-06_progress.md)의 사용자 실행 보고로 완료했다. 기본 시험을 처음부터 반복하지 않는다. 두 탭 기본 전달을 장시간·재접속·운용 코드 전체 PASS로 확대하지 않는다.

`03_Firmware/esp32_wifi_link`에서 WebSocket 상태 전송·재접속과 실제 UART TEL을 결합해 W4를 완료했다.
사용자가 입력·빌드·플래시하고 Codex가 실제 저장 파일과 브라우저 검사25개를 검토했다.
[WebSocket 입력 안내](2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)는 ESP 단독 단계의 이력이다. 최신 구현은 실제 C 소스와 W4 보고서를 따른다.

### 3.2 W4 (텔레메트리 연동) — 2026-10-08 완료
대상은 `esp32_wifi_link`다. 목표는 기존 STM TEL을 파싱한 최신 상태와 ESP 수신 시각을 snapshot으로 보관하고 브라우저에 전달하는 것이다.

| 데이터 | 현재 계약과 표시 의미 |
| --- | --- |
| `t_ms/state/reason` | STM 시각·상태·안전 사유 |
| `left_pwm/right_pwm` | 적용된 부호 있는 PWM, permille |
| `left_cps/right_cps` | 엔코더 counts/s. RPM·누적 tick과 구분 |
| `command_age_ms/last_seq/err/drop` | 명령·통신 진단. 현재 ESP parser의 읽는 항목과 수신 원문을 대조 |
| `batt_mv=0` | 고정 자리표시자. 배터리 미구현/사용 불가로 표시 |

`BAT: 12.4V, RPM: 150`은 설명용 예시이며 실제 프레임으로 도입하지 않는다. 기준은 [`send_tel()`](../../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c)과 [UART 계약](../../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md)이다. 실제 TEL은 `vx_mmps/w_mradps`도 포함한다.

실제 시험은 STM·ESP 만능기판 장착, 각각 USB 전원·LiPo 미연결 조건이었다.
신호 계약은 **ESP GPIO17→STM PA10, STM PA9→ESP GPIO18, 공통 GND, 115200/8N1**이다.
전원 핀을 추가로 묶는 연결은 하지 않는다. PA10 내부 pull-up과 PONG 시험 hook0U 복원 상태를 유지한다.

아래 구현 순서를 완료하고 실제 정상 TEL·중단/복구·재접속·응답 누락 실패를 확인했다.

1. 기존 UART 줄 조립·parser·부팅 DISARM/PING/응답 matching 계약을 재사용한다. 무효 프레임은 snapshot과 마지막 유효 수신 시각을 갱신하지 않는다.
2. snapshot의 짧은 동기화·서버 시작/종료·제한된 HTTP 작업 예약·payload 수명·전송 오류를 설계한다. 05의 handler용 `broadcast_text()`를 UART task에서 그대로 호출하는 것으로 통합을 끝내지 않는다. 05의 128-byte 버퍼와 `%s`/`strlen()` 사용은 길이·NUL 종료 검토가 필요하다.
3. 실제 TEL과 화면의 상태·PWM·CPS를 대조한다. STM `t_ms`와 ESP/브라우저 시계를 직접 빼지 않고 ESP의 유효 수신 age로 stale을 판정한다.
4. UART 수신 중단과 Wi-Fi/브라우저 연결 해제를 구분해 표시하고 복구 후 새 값을 받는지 확인한다. 재접속으로 자동 ARM·구동하지 않는다.

W4는 상태 전달이다. 부팅 안전 동기화의 DISARM/PING과 별개로 ARM/CMD·모터 구동은 W5에서 다룬다. 기존 수동 bench hook을 새 앱에 그대로 옮기지 않는다.

### 3.3 모의 데이터 제안의 상태

10/6에는 점퍼선이 없어 모의 데이터가 제안됐으나, 10/7~8 두 보드가 만능기판에 장착돼 실제 UART를 사용했다. Dummy Task·100ms 가짜 TEL은 만들지 않았으며 다음 필수 작업에도 추가하지 않는다.

모의 실험이 필요하면 실제 TEL 형식과 `MOCK` 출처를 사용한다. TEL을 parser에 넣으면 그 이후 경로를, JSON을 직접 보내면 화면·전송만 시험한다. 배선·실제 UART 수신·stale·복구 검증을 대신하지 않으며 “수신 함수 한 줄 교체로 전체 연동 완료”라고 가정하지 않는다.

### 3.4 W5 (무선 명령 및 안전 설계) — 다음 작업

첫 범위는 두 보드 USB·LiPo 미연결 상태의 **브라우저 PING/DISARM**이다.
입력 형식·최대 크기·세션·rate limit·단일 UART 송신 소유자·seq/응답 matching·timeout을 정한 뒤
정상 응답, 무효 입력·중복·과속·끊김을 검증한다. ARM/CMD와 실제 모터 구동은 이후 별도 범위다.

W4의 READY/FAILED는 이번 ESP 부팅의 응답 확인 이력이다. 현재 STM 세션의 유효성이나 구동 허가로 쓰지 않는다.
구동 전에는 최신 TEL·현재 세션·PC 명령 유효시간·명시적 재허가와 하드웨어 선행 조건을 검증한다.

1.  목표: 클라이언트에서 WebSocket으로 명령 전송 → ESP32 수신 → UART 릴레이 → STM32에서 명령 실행.
2.  핵심 검증:
    *   클라이언트 접속 해제 시 동작.
    *   잘못된 명령 프레임 수신 시 무시 여부.
    *   명령 유효시간 경과(stale) 시 정지 여부.

브라우저 입력은 형식·세션·유효시간 검사와 전달 큐를 거쳐 단일 UART bridge의 seq/ACK 관리에 들어간다. 만료된 PC 명령을 새 seq로 계속 재전송하지 않는다. 실제 구동은 하드웨어 선행 조건을 충족한 뒤 진행한다.

---

## 4. 주기와 시간 보장

실제 코드에서 STM의 `TEL_PERIOD_MS=100`과 엔코더 CPS 계산 기준 100ms를 확인했다. TEL 약 10Hz는 보고 설정이며 모든 UART 패킷의 주기나 보편적 표준은 아니다. ACK/ERR/PONG은 사건에 대한 응답이다.

W4 WebSocket 상태 전송은1000ms, STM TEL은100ms로 별도 설정했다. 이 설정은 1µs·1ms·수십 ms 이내 도착이나 하드 실시간성을 보장하지 않는다. 현재 STM의1ms PID·0.1ms 전력 차단 구현/실측으로 기록하지 않는다.

계산·실제 소스·공식 프로토콜 근거는 [타이밍과 W4 데이터 흐름 노트](../../07_Embedded_Learning_Notes/01_Concept_Notes/10_ESP32_WiFi_WebSocket_Timing_and_W4_Dataflow_ko.md)를 따른다. 배터리 ADC·RPM/누적 tick 추가는 별도 계약 확장이다.

## 5. 학습 완료 판단 기준

다음 질문들에 대해 프로젝트 아키텍처에 맞게 답할 수 있다면 ESP32 기본 학습은 충분하다.

1.  Wi-Fi 연결이 끊겼을 때 ESP32 시리얼 로그에는 어떤 이벤트와 reason 코드가 기록되는가?
2.  사용자가 웹 브라우저 버튼을 누르면, 그 명령은 어떤 경로와 프로토콜을 거쳐 실제 STM32 모터 제어 핀까지 도달하는가?
3.  스마트폰 화면이 꺼지거나 통신이 두절되어 새로운 명령이 들어오지 않는 경우, **어느 MCU가** 타임아웃을 감지하고 로봇을 정지시키는가?
4.  ESP32 칩이 다운되거나 재부팅 중일 때, 로봇의 구동부 상태는 어떻게 유지되어야 하는가?
