# RTOS Task와 Priority

## 분야

- RTOS
- 실시간 시스템
- 임베디드 소프트웨어 구조

## 관련 면접 질문

- RTOS에서 task란 무엇인가?
- priority는 어떤 역할을 하는가?
- super loop와 RTOS 구조는 무엇이 다른가?

## 선수지식

- 함수와 while loop
- interrupt
- scheduler
- 실시간성
- stack

## 핵심 개념

RTOS에서 task는 독립적으로 실행되는 작업 단위입니다. PC의 thread와 비슷하게 생각할 수 있습니다.

예를 들어 로봇 펌웨어를 task로 나누면 아래처럼 구성할 수 있습니다.

- Sensor Task: 센서 읽기
- Control Task: 모터 제어 계산
- Communication Task: UART/CAN 송수신
- Monitor Task: 상태 LED나 로그 처리

## Scheduler

RTOS scheduler는 어떤 task를 언제 실행할지 결정합니다. 대부분의 RTOS는 priority 기반 preemptive scheduling을 지원합니다.

Preemptive scheduling은 높은 priority task가 준비되면 낮은 priority task를 멈추고 높은 priority task를 먼저 실행하는 방식입니다.

## Priority

Priority는 task의 중요도입니다.

예시:

| Task | Priority 예시 | 이유 |
| --- | --- | --- |
| Motor Control | 높음 | 주기 지연이 제어 품질에 직접 영향 |
| Sensor Read | 중간 | 일정 주기 필요 |
| Communication | 중간 | 데이터 유실 방지 |
| Debug Log | 낮음 | 지연되어도 시스템 안전에 영향 적음 |

## Task Stack

각 task는 자기 stack을 가집니다. 따라서 task를 많이 만들거나 각 task에서 큰 지역 변수를 사용하면 RAM 사용량이 증가합니다.

면접에서는 "RTOS를 쓰면 task별 stack 크기도 고려해야 한다"고 말하면 좋습니다.

## Super Loop와 비교

Super loop:

```c
while (1) {
    read_sensor();
    control_motor();
    send_uart();
}
```

RTOS:

```text
Sensor Task
Control Task
Communication Task
```

Super loop는 단순하지만 작업이 많아지면 주기 관리가 어려워집니다. RTOS는 task를 분리하고 priority를 줄 수 있어 복잡한 시스템을 구조화하기 좋지만, 동시성 문제와 stack 관리가 필요합니다.

## 면접 답변으로 연결

### 30초 답변

> RTOS에서 task는 독립적으로 실행되는 작업 단위이고, priority는 scheduler가 어떤 task를 먼저 실행할지 결정하는 기준입니다. 예를 들어 모터 제어 task는 높은 priority로 두고, debug log task는 낮은 priority로 둘 수 있습니다. RTOS를 쓰면 기능별로 구조화하기 좋지만 task 간 공유 자원, priority inversion, task별 stack 사용량을 함께 관리해야 합니다.

## 내 프로젝트로 연결하는 문장

> STM32 프로젝트를 RTOS로 확장한다면 센서 task, UART communication task, control task를 분리하고, 제어 주기가 중요한 task에 더 높은 priority를 주는 구조를 생각할 수 있습니다.

