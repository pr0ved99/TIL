# 07-03. I/O Performance

## 결론

I/O 성능은 CPU 연산보다 latency, queue, cache, device 특성의 영향을 크게 받는다.

## 핵심 개념

- `Latency`: 요청 후 결과가 오기까지 걸리는 시간이다.
- `Throughput`: 단위 시간당 처리한 데이터 양이다.
- `Buffering`: 속도가 다른 계층 사이에 임시 공간을 둔다.
- `Caching`: 반복 접근 데이터를 빠른 계층에 보관한다.

## 확인 질문

1. 작은 파일을 많이 읽을 때와 큰 파일 하나를 읽을 때 병목은 어떻게 다를 수 있는가?
2. Cache는 왜 성능을 높이지만 일관성 문제를 만들 수 있는가?
3. Throughput과 latency 중 어느 지표가 더 중요한 상황인가?

