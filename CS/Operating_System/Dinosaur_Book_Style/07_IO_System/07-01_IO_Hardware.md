# 07-01. I/O Hardware

## 결론

I/O 시스템은 CPU와 메모리 밖의 장치들을 일관된 방식으로 다루기 위한 계층이다.

## 핵심 개념

- `Device controller`: 장치를 제어하는 하드웨어 인터페이스다.
- `Port`: CPU가 장치와 통신하는 주소나 endpoint다.
- `Memory-mapped I/O`: 장치 register를 메모리 주소처럼 접근한다.
- `Polling`: CPU가 장치 상태를 반복 확인한다.

## 확인 질문

1. CPU가 장치를 직접 계속 기다리면 왜 비효율적인가?
2. Memory-mapped I/O는 어떤 장점이 있는가?
3. 장치 속도가 CPU보다 느릴 때 OS는 무엇을 고려해야 하는가?

