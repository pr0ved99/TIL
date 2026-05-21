# 06-04. Journaling and Reliability

## 결론

Journaling은 파일 시스템 변경 내용을 먼저 기록해 crash 후에도 일관성을 복구하기 쉽게 만드는 방법이다.

## 핵심 개념

- `Consistency`: metadata와 data 관계가 말이 되는 상태다.
- `Journal`: 실제 반영 전 변경 계획을 기록하는 영역이다.
- `Crash recovery`: 갑작스러운 종료 후 손상된 상태를 복구하는 과정이다.

## 흐름

```text
write intent to journal
-> apply changes
-> mark transaction complete
```

## 확인 질문

1. 파일 쓰기 중 전원이 나가면 어떤 불일치가 생길 수 있는가?
2. Journaling은 왜 성능 비용이 있는가?
3. Metadata journaling과 data journaling은 무엇이 다른가?

