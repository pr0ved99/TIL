# 03-01. Scheduling Goals and Metrics

## 결론

CPU 스케줄링은 제한된 CPU 시간을 어떤 작업에 먼저 줄지 결정하는 문제다.

## 핵심 개념

- `CPU utilization`: CPU가 놀지 않고 일한 비율이다.
- `Throughput`: 단위 시간당 완료한 작업 수다.
- `Turnaround time`: 제출부터 완료까지 걸린 시간이다.
- `Waiting time`: ready queue에서 기다린 시간이다.
- `Response time`: 요청 후 첫 반응까지 걸린 시간이다.

## 관점

대화형 시스템은 response time이 중요하고, batch 시스템은 throughput과 turnaround time이 중요할 수 있다.

## 확인 질문

1. 모든 지표를 동시에 최적화하기 어려운 이유는 무엇인가?
2. 대화형 프로그램에서 response time이 중요한 이유는 무엇인가?
3. throughput이 높아도 사용자가 느리다고 느낄 수 있는 이유는 무엇인가?

