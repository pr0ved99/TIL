# 03-03. Multicore and Real-Time Scheduling

## 결론

멀티코어 스케줄링은 작업을 어느 CPU에 배치할지까지 결정하고, 실시간 스케줄링은 deadline을 지키는 것을 우선한다.

## 핵심 개념

- `Load balancing`: CPU core 사이 부하를 고르게 맞춘다.
- `Processor affinity`: 같은 작업을 같은 core에서 실행해 cache 효과를 유지한다.
- `Real-time task`: 정해진 시간 안에 결과가 나와야 하는 작업이다.
- `Deadline`: 결과가 필요한 시간 제한이다.

## 확인 질문

1. 작업을 계속 다른 core로 옮기면 cache 관점에서 왜 손해인가?
2. 실시간 시스템에서 평균 성능보다 deadline이 중요한 이유는 무엇인가?
3. soft real-time과 hard real-time은 어떻게 다른가?

