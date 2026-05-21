# 05-02. Paging and Page Table

## 결론

Paging은 메모리를 고정 크기 단위로 나누어 연속된 물리 메모리가 없어도 프로세스를 실행할 수 있게 한다.

## 핵심 개념

- `Page`: virtual address space의 고정 크기 블록이다.
- `Frame`: physical memory의 고정 크기 블록이다.
- `Page table`: page 번호를 frame 번호로 매핑한다.
- `TLB`: page table lookup을 빠르게 하기 위한 cache다.

## 흐름

```text
virtual address = page number + offset
-> page table lookup
-> frame number + offset
-> physical address
```

## 확인 질문

1. Paging이 external fragmentation을 줄이는 이유는 무엇인가?
2. TLB miss가 생기면 왜 느려지는가?
3. Page table이 너무 커지는 문제는 어떻게 줄일 수 있는가?

