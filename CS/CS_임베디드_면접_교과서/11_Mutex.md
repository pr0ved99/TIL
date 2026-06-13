# Mutex

## 분야

- RTOS
- 멀티스레딩
- 공유 자원 보호

## 관련 면접 질문

- mutex는 무엇인가?
- semaphore와 mutex의 차이는?
- shared buffer를 보호해야 하는 이유는?
- priority inversion은 무엇인가?

## 선수지식

- task
- shared resource
- race condition
- critical section
- priority

## 핵심 개념

Mutex는 Mutual Exclusion의 줄임말입니다. 여러 task나 thread가 동시에 같은 공유 자원에 접근하지 못하도록 보호하는 lock입니다.

예를 들어 두 task가 같은 UART 송신 함수에 동시에 접근하면 메시지가 섞일 수 있습니다.

```text
Task A: "TEMP,25"
Task B: "MOTOR,ON"

섞인 결과: "TEMMOTORP,ON,25"
```

이런 문제를 막기 위해 UART 송신 구간을 mutex로 보호할 수 있습니다.

## Critical Section

동시에 실행되면 안 되는 코드 구간을 critical section이라고 합니다.

```c
lock(mutex);
shared_value++;
unlock(mutex);
```

`shared_value++`는 한 줄처럼 보이지만 실제로는 읽기, 증가, 쓰기 단계로 나뉩니다. 두 task가 동시에 접근하면 값이 꼬일 수 있습니다.

## Race Condition

Race condition은 실행 순서에 따라 결과가 달라지는 문제입니다.

예를 들어 sensor callback은 값을 쓰고, control loop는 값을 읽는 상황에서 동시에 접근하면 중간 상태를 읽을 수 있습니다.

## Priority Inversion

Priority inversion은 낮은 priority task가 mutex를 잡고 있는데, 높은 priority task가 그 mutex를 기다리면서 실행되지 못하는 상황입니다.

RTOS mutex는 이를 줄이기 위해 priority inheritance를 제공하는 경우가 많습니다. 낮은 priority task가 높은 priority task를 막고 있으면, 잠시 낮은 priority task의 priority를 올려 mutex를 빨리 반환하게 하는 방식입니다.

## Mutex와 Semaphore 차이

| 항목 | Mutex | Semaphore |
| --- | --- | --- |
| 주 용도 | 공유 자원 보호 | 이벤트 알림, 자원 개수 관리 |
| 소유권 | 있음 | 보통 없음 |
| unlock 주체 | lock한 task | 다른 task/ISR도 가능할 수 있음 |
| priority inheritance | 지원하는 경우 많음 | 일반 semaphore는 보통 없음 |

## 면접 답변으로 연결

### 30초 답변

> Mutex는 여러 task가 shared buffer, UART, sensor state 같은 공유 자원에 동시에 접근하지 못하도록 보호하는 lock입니다. Semaphore가 이벤트 알림이나 자원 개수 관리에 가깝다면, mutex는 소유권이 있는 공유 자원 보호 도구입니다. RTOS에서는 priority inversion 문제가 생길 수 있어 priority inheritance를 지원하는 mutex를 사용하는 경우가 많습니다.

## 내 프로젝트로 연결하는 문장

> ROS 2나 RTOS에서 센서 callback이 값을 갱신하고 제어 loop가 같은 값을 읽는 구조라면, race condition을 막기 위해 mutex나 callback group 설계를 고려해야 합니다.

