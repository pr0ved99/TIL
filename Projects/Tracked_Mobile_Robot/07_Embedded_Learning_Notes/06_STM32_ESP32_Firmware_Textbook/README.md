# STM32·ESP32 로봇 펌웨어 교과서

**[교과서 본문 열기](STM32_ESP32_Firmware_Textbook_ko.md)**

작성 기준: 2026-10-13 작업 트리. 두 보드의 실제 소스를 읽고, 기초에서 현재 구현까지 재구성한 학습서다. 본문 한 파일에 설명·예제·연습 문제·해설·소스 지도를 모았다.

## 이곳에 둔 이유

프로젝트 밖의 [STM32 학습 폴더](../../../../Embedded/STM32/README.md)와 [ESP32-S3 학습 폴더](../../../../Embedded/ESP32-S3/README.md)는 보드별 일반 학습에 적합하다. 이번 책의 중심은 이 로봇의 STM 출력 판단, ESP 중계, 브라우저 제어를 함께 이해하는 것이므로 프로젝트의 기존 학습 노트 아래에 둔다. 외부 학습 폴더에는 이 책의 링크만 추가해 복사본이 갈라지는 것을 피한다.

공식 인터페이스 계약을 대체하는 문서는 아니다. 학습용 단순화, 현재 구현, 아직 없는 기능을 본문에서 구분한다.

<a id="study-route"></a>
## 한 번에 한 단위씩 읽기

본문은 하나의 교과서로 유지하고, 아래 링크로 필요한 부분부터 펼친다. 한 행이 한 학습 단위이며 하루에 여러 행을 끝낼 필요는 없다. 시간보다 **책을 덮고 설명할 수 있는지**를 다음 단위로 넘어가는 기준으로 삼는다.

| 단위 | 이번에 읽을 범위 | 작은 활동 | 끝내도 되는 기준 |
| --- | --- | --- | --- |
| 1 | [0~2장: 전체 그림·빌드·C](STM32_ESP32_Firmware_Textbook_ko.md#ch00) | 예제 01에서 값 복사와 포인터 부분 읽기 | 값 복사와 원본 수정의 차이를 설명한다 |
| 2 | [3~4장: 핀·클록·시간](STM32_ESP32_Firmware_Textbook_ko.md#ch03) | 예제 01 실행, timeout 직전/경계 값 예상 | 주기 실행과 기한 만료를 구분한다 |
| 3 | [5~6장: UART·parser](STM32_ESP32_Firmware_Textbook_ko.md#ch05) | 예제 02에서 분할 수신 추적 | 개행 전 처리하지 않는 이유와 문법/범위 검사를 구분한다 |
| 4 | [7장: STM 상태](STM32_ESP32_Firmware_Textbook_ko.md#ch07) | ARM·CMD·timeout을 종이에 순서대로 적기 | 명령이 없어지면 왜 정지하는지 설명한다 |
| 5 | [8~10장: 출력·엔코더·STM 통합](STM32_ESP32_Firmware_Textbook_ko.md#ch08) | 예제 03의 좌우 출력과 CPS 예상 | PWM 명령과 측정된 속도를 구분한다 |
| 6 | [11~12장: 태스크·웹 통신](STM32_ESP32_Firmware_Textbook_ko.md#ch11) | 브라우저·HTTP 태스크·UART 태스크의 일을 나눠 적기 | `send()`가 STM 처리 완료가 아님을 설명한다 |
| 7 | [13~14장: TEL·요청과 응답](STM32_ESP32_Firmware_Textbook_ko.md#ch13) | 요청→접수→송신→ACK→TEL 그리기 | READY·신선한 TEL·제어 가능을 구분한다 |
| 8 | [연결 수업과 15장: ticket·owner](STM32_ESP32_Firmware_Textbook_ko.md#bridge-control) | 예제 04의 만료 사례만 먼저 읽기 | 일회 제출 기회와 지속 제어권의 차이를 설명한다 |
| 9 | [16장: 제어 상태](STM32_ESP32_Firmware_Textbook_ko.md#ch16) | [예제 04 따라 읽기](examples/README.md#walkthrough04)의 1회차 | CMD ACK 뒤에도 TEL을 기다리는 이유를 설명한다 |
| 10 | [17장: executor와 송신](STM32_ESP32_Firmware_Textbook_ko.md#ch17) | 예제 04 따라 읽기의 2~3회차 | 접수·실제 송신·입력 폐기·정지 확인을 구분한다 |
| 11 | [18장: 브라우저 의도·기한](STM32_ESP32_Firmware_Textbook_ko.md#ch18) | 예제 05 실행, blur 이후 흐름 예상 | 재접속이나 포커스 복귀가 ARM을 대신하지 않는 이유를 설명한다 |
| 12 | [19~20장: 디버깅·재구성](STM32_ESP32_Firmware_Textbook_ko.md#ch19) | 종합 과제 버전 0부터 하나씩 작성 | 막힌 지점을 입력·상태·기한·출력으로 좁힌다 |

예제 실행 방법은 [실습 안내](examples/README.md#run)를 따른다. 예를 들어 `python run_examples.py --lesson 01`은 예제 01만 실행한다. 번호를 생략하면 전체를 실행한다.

### 후반부가 어려울 때

15~18장을 한 번에 읽지 않는다. 먼저 [연결 수업](STM32_ESP32_Firmware_Textbook_ko.md#bridge-control)에서 모듈이 생긴 이유를 이해하고, 16장의 정상 흐름 → 17장의 실행 연결 → 실패·시간 경계 → 18장의 브라우저 순으로 돌아본다. 각 장 시작의 ‘첫 읽기’ 안내가 이번에 집중할 부분을 알려 준다.

모르는 용어는 [본문 부록](STM32_ESP32_Firmware_Textbook_ko.md#appendix)에서 찾는다. 시간 상수를 모두 외우기보다 **어느 사건부터 시간을 재는지**를 먼저 말해 본다.

### 다음에 다시 시작할 때 남길 메모

아래 네 줄만 개인 메모에 남긴다. 예제의 `PASS`는 실행 결과이고, 이해 여부는 별도로 확인한다.

~~~text
마친 단위 / 절:
코드를 보지 않고 설명할 수 있는 것:
아직 헷갈리는 질문 하나:
다음에 펼칠 절 / 실행할 예제:
~~~

## 예제와 기준 소스

- [실행 예제 안내](examples/README.md): 보드 없이 실행하는 C 예제 4개와 JavaScript 예제 1개.
- [분석 기준 소스 목록](source_manifest.json): 파일별 SHA256. 플래시된 바이너리를 식별하는 값은 아니다.
- [기존 함수 지도](../01_Concept_Notes/09_STM32_ESP32_Source_Structure_and_Function_Map_ko.md): 파일을 빨리 찾을 때 참고. 날짜가 다른 설명은 이 책의 기준 소스와 대조한다.

예제 runner는 PC용 실행 파일만 임시 폴더에 만든다. 보드 빌드·플래시·UART·네트워크 접속을 하지 않는다.
