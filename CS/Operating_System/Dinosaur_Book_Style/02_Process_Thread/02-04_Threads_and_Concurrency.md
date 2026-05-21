# 02-04. Threads and Concurrency

## 결론

스레드는 한 프로세스 안에서 실행 흐름을 여러 개로 나누는 단위이고, 동시성은 여러 작업이 겹쳐 진행되는 성질이다.

## 핵심 개념

- `Thread`: 같은 process address space를 공유하는 실행 단위다.
- `Concurrency`: 작업들이 시간적으로 겹쳐 진행되는 구조다.
- `Parallelism`: 실제로 여러 CPU core에서 동시에 실행되는 구조다.

## 장점과 위험

- 장점: 응답성, 자원 공유, 병렬 처리 가능성
- 위험: race condition, deadlock, 디버깅 난도 증가

## 확인 질문

1. 스레드는 왜 프로세스보다 가벼울 수 있는가?
2. 스레드가 같은 메모리를 공유하면 어떤 문제가 생기는가?
3. concurrency와 parallelism은 어떻게 다른가?

