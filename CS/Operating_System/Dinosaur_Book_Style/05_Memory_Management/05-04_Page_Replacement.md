# 05-04. Page Replacement

## 결론

Page replacement는 메모리가 부족할 때 어떤 page를 내보낼지 결정하는 정책이다.

## 핵심 알고리즘

- `FIFO`: 가장 오래된 page를 내보낸다.
- `Optimal`: 앞으로 가장 오래 쓰지 않을 page를 내보낸다.
- `LRU`: 최근에 가장 오래 사용하지 않은 page를 내보낸다.
- `Clock`: reference bit로 LRU를 근사한다.

## 비교 관점

| 알고리즘 | 장점 | 단점 |
| --- | --- | --- |
| FIFO | 단순 | 성능 예측 어려움 |
| Optimal | 기준선으로 좋음 | 실제 구현 불가 |
| LRU | 직관적 | 정확한 구현 비용 |
| Clock | 현실적 | 근사 정책 |

## 확인 질문

1. Optimal은 왜 실제 시스템에서 바로 구현하기 어려운가?
2. LRU는 왜 locality를 활용하는가?
3. Page fault rate가 높아지면 시스템은 어떻게 느려지는가?

