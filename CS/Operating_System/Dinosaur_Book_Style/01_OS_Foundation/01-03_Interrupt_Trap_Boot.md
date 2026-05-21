# 01-03. Interrupt, Trap, Boot

## 결론

운영체제는 interrupt와 trap을 통해 CPU 실행 흐름을 제어하고, boot 과정에서 커널을 메모리에 올려 시스템을 시작한다.

## 핵심 개념

- `Interrupt`: 외부 장치나 타이머가 CPU에 알리는 비동기 이벤트다.
- `Trap`: 프로그램 실행 중 발생한 예외나 system call처럼 의도적으로 커널에 진입하는 이벤트다.
- `Boot`: firmware가 커널을 찾아 메모리에 적재하고 실행을 넘기는 과정이다.

## 흐름

```text
power on
-> firmware
-> bootloader
-> kernel load
-> init process
```

## 확인 질문

1. 타이머 interrupt가 없으면 CPU 스케줄링이 왜 어려워지는가?
2. trap과 interrupt는 무엇이 다른가?
3. bootloader와 kernel의 역할은 어떻게 나뉘는가?

