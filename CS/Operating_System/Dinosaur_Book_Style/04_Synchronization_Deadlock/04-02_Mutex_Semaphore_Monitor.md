# 04-02. Mutex, Semaphore, Monitor

## 결론

Mutex, semaphore, monitor는 공유 자원 접근을 조절하기 위한 동기화 도구다.

## 핵심 개념

- `Mutex`: 한 번에 하나의 thread만 들어가게 하는 lock이다.
- `Semaphore`: 정수 counter로 접근 가능한 자원 수를 표현한다.
- `Monitor`: shared data와 그 data에 접근하는 함수를 묶고 조건 변수로 대기를 관리한다.

## 비교

| 도구 | 주 용도 | 주의점 |
| --- | --- | --- |
| Mutex | 상호 배제 | unlock 누락 |
| Semaphore | 개수 제한, 신호 전달 | 의미가 흐려지기 쉬움 |
| Monitor | 구조화된 동기화 | 조건 대기 규칙 필요 |

## 확인 질문

1. Binary semaphore와 mutex는 언제 비슷하고 언제 다른가?
2. Semaphore를 잘못 쓰면 왜 디버깅이 어려운가?
3. Condition variable은 왜 while 조건과 함께 쓰는가?

