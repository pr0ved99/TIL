# 05-03. Virtual Memory

## 결론

Virtual memory는 실제 RAM보다 큰 주소 공간을 제공하고, 필요한 page만 메모리에 올려 실행하는 방식이다.

## 핵심 개념

- `Demand paging`: 실제로 필요할 때 page를 메모리에 올린다.
- `Page fault`: 필요한 page가 메모리에 없어 OS가 개입하는 사건이다.
- `Swap`: 메모리 내용을 보조 저장장치로 내보내거나 다시 가져오는 과정이다.

## 흐름

```text
access virtual address
-> page not present
-> page fault
-> OS loads page
-> instruction retry
```

## 확인 질문

1. Virtual memory가 프로그램 작성자를 편하게 하는 이유는 무엇인가?
2. Page fault는 왜 일반 memory access보다 훨씬 비싼가?
3. Working set이 메모리보다 커지면 어떤 현상이 생기는가?

