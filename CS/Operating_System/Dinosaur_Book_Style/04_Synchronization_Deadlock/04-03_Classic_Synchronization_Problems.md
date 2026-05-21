# 04-03. Classic Synchronization Problems

## 결론

고전 동기화 문제는 실제 동시성 버그를 단순한 모델로 압축한 연습 문제다.

## 핵심 문제

- `Producer-Consumer`: 생산 속도와 소비 속도를 buffer로 조율한다.
- `Readers-Writers`: 읽기는 동시에 허용하고 쓰기는 배타적으로 처리한다.
- `Dining Philosophers`: 자원 획득 순서가 deadlock을 만들 수 있음을 보여준다.

## 학습 포인트

- 공유 자원은 무엇인가?
- 동시에 접근해도 되는 작업은 무엇인가?
- 대기 조건은 무엇인가?
- starvation을 막을 방법은 있는가?

## 확인 질문

1. Producer-consumer에서 empty/full semaphore가 필요한 이유는 무엇인가?
2. Readers-writers에서 writer starvation은 어떻게 생기는가?
3. Dining philosophers 문제에서 자원 획득 순서를 통일하면 왜 도움이 되는가?

