# 03-02. Scheduling Algorithms

## 결론

스케줄링 알고리즘은 공정성, 평균 대기 시간, 응답성 사이의 trade-off를 선택하는 방법이다.

## 핵심 알고리즘

- `FCFS`: 먼저 온 작업을 먼저 실행한다.
- `SJF`: 실행 시간이 짧은 작업을 먼저 실행한다.
- `Round Robin`: 정해진 time quantum마다 CPU를 교체한다.
- `Priority`: 우선순위가 높은 작업을 먼저 실행한다.

## 비교 관점

| 알고리즘 | 장점 | 단점 |
| --- | --- | --- |
| FCFS | 단순 | convoy effect |
| SJF | 평균 대기 시간 감소 | 실행 시간 예측 필요 |
| RR | 응답성 좋음 | quantum 선택 중요 |
| Priority | 정책 반영 쉬움 | starvation 위험 |

## 확인 질문

1. RR에서 quantum이 너무 작으면 어떤 비용이 커지는가?
2. priority scheduling에서 starvation을 어떻게 줄일 수 있는가?
3. SJF는 왜 이론적으로 좋지만 실제 구현이 어려운가?

