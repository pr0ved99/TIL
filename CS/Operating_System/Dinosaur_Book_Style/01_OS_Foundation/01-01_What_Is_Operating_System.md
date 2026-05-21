# 01-01. What Is Operating System

## 결론

운영체제는 하드웨어를 직접 다루기 어려운 프로그램들에게 안전하고 일관된 실행 환경을 제공하는 중간 관리자다.

## 핵심 개념

- `Resource manager`: CPU, memory, storage, I/O 장치를 나누어 관리한다.
- `Abstraction`: 복잡한 하드웨어를 process, file, virtual memory 같은 쉬운 모델로 감싼다.
- `Protection`: 한 프로그램의 오류가 다른 프로그램이나 커널을 망가뜨리지 않게 막는다.

## 흐름

```text
Application
-> system call
-> kernel
-> hardware
```

## 확인 질문

1. 운영체제가 없으면 프로그램이 직접 해결해야 하는 문제는 무엇인가?
2. 운영체제를 자원 관리자라고 부르는 이유는 무엇인가?
3. 추상화와 보호는 서로 어떻게 연결되는가?

