# Semaphore

## 분야

- RTOS
- 동시성 제어
- task 간 신호 전달

## 관련 면접 질문

- semaphore는 무엇인가?
- binary semaphore와 counting semaphore의 차이는?
- interrupt와 task 사이에서 semaphore를 어떻게 쓰는가?

## 선수지식

- RTOS task
- interrupt
- shared resource
- blocking과 wake-up

## 핵심 개념

Semaphore는 task 사이에서 "이벤트가 발생했다"거나 "사용 가능한 자원이 몇 개 있다"는 것을 알려주는 동기화 도구입니다.

쉽게 말하면 semaphore는 신호등이나 카운터에 가깝습니다.

## Binary Semaphore

Binary semaphore는 값이 0 또는 1인 semaphore입니다. 주로 이벤트 알림에 사용합니다.

예를 들어 UART 수신 interrupt가 발생하면 communication task를 깨우는 구조입니다.

```text
UART ISR
  -> semaphore give

Communication Task
  -> semaphore take
  -> received data processing
```

ISR에서는 오래 걸리는 parsing을 하지 않고, semaphore만 주고 빠져나올 수 있습니다.

## Counting Semaphore

Counting semaphore는 여러 개의 자원 개수를 표현할 수 있습니다.

예를 들어 사용 가능한 buffer block이 4개라면 counting semaphore 초기값을 4로 둘 수 있습니다. task가 block을 가져가면 count가 줄고, 반환하면 count가 늘어납니다.

## Semaphore와 Mutex 차이

Semaphore는 주로 이벤트 알림이나 자원 개수 관리에 사용합니다. Mutex는 특정 공유 자원의 소유권을 보호하는 데 사용합니다.

중요한 차이:

- Semaphore는 소유권 개념이 약합니다.
- Mutex는 lock을 잡은 task가 unlock해야 합니다.
- 공유 자원 보호에는 보통 mutex가 더 적합합니다.

## 면접 답변으로 연결

### 30초 답변

> Semaphore는 RTOS에서 task 간 이벤트 전달이나 자원 개수 관리에 사용하는 동기화 도구입니다. Binary semaphore는 UART 수신 완료처럼 이벤트를 알릴 때 사용할 수 있고, counting semaphore는 사용 가능한 buffer 개수처럼 여러 자원을 관리할 때 사용할 수 있습니다. 공유 자원 보호에는 semaphore보다 mutex를 쓰는 것이 일반적입니다.

## 내 프로젝트로 연결하는 문장

> UART RX interrupt가 발생하면 ISR에서는 semaphore만 give하고, communication task가 깨어나 수신 buffer를 parsing하는 구조로 개선할 수 있습니다.

