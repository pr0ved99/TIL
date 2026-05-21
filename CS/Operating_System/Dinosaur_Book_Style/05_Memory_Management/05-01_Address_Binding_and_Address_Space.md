# 05-01. Address Binding and Address Space

## 결론

메모리 관리는 프로그램이 보는 주소와 실제 물리 메모리 주소를 안전하게 연결하는 작업이다.

## 핵심 개념

- `Logical address`: 프로그램이 사용하는 주소다.
- `Physical address`: 실제 메모리 하드웨어 주소다.
- `Address space`: 한 프로세스가 사용할 수 있다고 보는 주소 범위다.
- `MMU`: logical address를 physical address로 변환하는 하드웨어다.

## 확인 질문

1. 프로세스마다 0번지부터 시작하는 것처럼 보일 수 있는 이유는 무엇인가?
2. 주소 변환이 없으면 보호가 왜 어려운가?
3. Compile time, load time, execution time binding은 무엇이 다른가?

