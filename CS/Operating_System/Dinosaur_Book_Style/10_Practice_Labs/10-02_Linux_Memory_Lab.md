# 10-02. Linux Memory Lab

## 결론

Linux에서 메모리 사용량과 가상 메모리 상태를 관찰해 paging과 address space 개념을 연결한다.

## 실습 명령

```bash
free -h
vmstat 1
cat /proc/meminfo
pmap $$
ulimit -a
```

## 관찰할 것

- total/free/available memory
- swap 사용량
- page fault 관련 지표
- process별 memory map

## 확인 질문

1. free memory와 available memory는 왜 다를 수 있는가?
2. Swap 사용이 늘면 어떤 성능 문제가 생길 수 있는가?
3. Process의 virtual size와 resident size는 어떻게 다른가?

