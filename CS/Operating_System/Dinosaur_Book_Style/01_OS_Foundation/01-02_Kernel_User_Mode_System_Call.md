# 01-02. Kernel Mode, User Mode, System Call

## 결론

운영체제는 위험한 작업을 커널 모드에 제한하고, 일반 프로그램은 사용자 모드에서 실행시켜 시스템 전체를 보호한다.

## 핵심 개념

- `Kernel mode`: 하드웨어와 메모리에 강한 권한으로 접근할 수 있는 모드다.
- `User mode`: 일반 애플리케이션이 실행되는 제한된 모드다.
- `System call`: 사용자 프로그램이 커널 기능을 요청하는 공식 입구다.

## 흐름

```text
user code
-> system call wrapper
-> trap
-> kernel handler
-> return to user mode
```

## 확인 질문

1. 파일 읽기나 프로세스 생성은 왜 system call을 거쳐야 하는가?
2. 모든 코드가 kernel mode에서 실행되면 어떤 문제가 생기는가?
3. system call과 일반 함수 호출은 무엇이 다른가?

