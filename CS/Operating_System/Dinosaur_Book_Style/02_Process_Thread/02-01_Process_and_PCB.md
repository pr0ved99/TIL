# 02-01. Process and PCB

## 결론

프로세스는 실행 중인 프로그램이고, PCB는 운영체제가 그 프로세스를 관리하기 위해 저장하는 상태 기록이다.

## 핵심 개념

- `Program`: 디스크에 저장된 실행 파일이다.
- `Process`: 메모리에 올라와 실행 중인 프로그램 인스턴스다.
- `PCB`: process id, register, program counter, scheduling info, memory info 등을 담는다.

## 흐름

```text
program file
-> loader
-> process address space
-> PCB 생성
-> ready queue 진입
```

## 확인 질문

1. 같은 프로그램을 두 번 실행하면 왜 프로세스가 두 개가 되는가?
2. PCB가 사라지면 운영체제는 무엇을 잃는가?
3. process state에는 어떤 것들이 필요한가?

