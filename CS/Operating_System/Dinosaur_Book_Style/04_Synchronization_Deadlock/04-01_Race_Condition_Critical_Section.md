# 04-01. Race Condition and Critical Section

## 결론

Race condition은 실행 순서에 따라 결과가 달라지는 버그이고, critical section은 공유 자원에 접근하는 위험 구간이다.

## 핵심 개념

- `Shared data`: 여러 thread/process가 함께 접근하는 데이터다.
- `Atomicity`: 중간에 끊기지 않고 한 번에 수행되는 성질이다.
- `Critical section`: 동시에 들어가면 안 되는 코드 구간이다.

## 흐름

```text
read shared value
-> modify
-> write back
```

이 세 단계가 원자적으로 보장되지 않으면 lost update가 생길 수 있다.

## 확인 질문

1. `count++`가 왜 항상 atomic하지 않은가?
2. critical section에 필요한 세 조건은 무엇인가?
3. 동기화가 없으면 테스트에서는 통과하고 운영에서는 실패할 수 있는 이유는 무엇인가?

