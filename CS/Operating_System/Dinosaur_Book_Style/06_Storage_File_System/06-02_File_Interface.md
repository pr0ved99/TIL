# 06-02. File Interface

## 결론

파일은 운영체제가 저장장치를 byte stream이나 record처럼 다룰 수 있게 제공하는 추상화다.

## 핵심 개념

- `File descriptor`: 열린 파일을 가리키는 process-local handle이다.
- `Open file table`: 열린 파일의 상태를 관리한다.
- `Seek`: 파일 내부 offset을 이동한다.
- `Permission`: 누가 읽고 쓰고 실행할 수 있는지 정한다.

## 확인 질문

1. 파일 이름과 file descriptor는 무엇이 다른가?
2. 같은 파일을 두 프로세스가 열면 어떤 상태를 공유하고 무엇은 따로 가질 수 있는가?
3. Sequential access와 random access는 어떤 차이가 있는가?

