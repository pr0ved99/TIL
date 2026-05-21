# 07-02. Interrupt, DMA, Driver

## 결론

Interrupt, DMA, driver는 느린 장치와 빠른 CPU 사이를 효율적으로 연결하는 핵심 장치다.

## 핵심 개념

- `Interrupt`: 장치가 작업 완료나 이벤트를 CPU에 알린다.
- `DMA`: CPU를 거치지 않고 장치와 메모리 사이에 데이터를 전송한다.
- `Driver`: OS가 장치를 사용할 수 있게 하는 장치별 소프트웨어다.

## 흐름

```text
process requests I/O
-> kernel calls driver
-> device starts work
-> DMA transfers data
-> interrupt notifies completion
```

## 확인 질문

1. DMA가 없으면 대용량 I/O에서 CPU가 왜 낭비되는가?
2. Driver bug가 시스템 전체에 영향을 줄 수 있는 이유는 무엇인가?
3. Interrupt storm은 왜 문제가 되는가?

