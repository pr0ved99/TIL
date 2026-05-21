# 02-02. Context Switch

## 결론

Context switch는 CPU가 실행하던 프로세스의 상태를 저장하고 다른 프로세스 상태를 복원하는 작업이다.

## 핵심 개념

- `Context`: register, program counter, stack pointer처럼 다시 실행하기 위해 필요한 상태다.
- `Ready queue`: CPU를 기다리는 프로세스 목록이다.
- `Scheduler`: 다음에 CPU를 줄 프로세스를 고른다.

## 흐름

```text
running process 중단
-> current context 저장
-> scheduler 선택
-> next context 복원
-> next process 실행
```

## 확인 질문

1. context switch는 왜 비용이 있는가?
2. CPU를 자주 바꾸면 응답성은 좋아질 수 있지만 throughput은 왜 떨어질 수 있는가?
3. process switch와 thread switch의 비용은 왜 다를 수 있는가?

