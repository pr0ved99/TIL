# 10-01. Linux Process Lab

## 결론

Linux 명령으로 process 상태, 부모-자식 관계, scheduling 정보를 직접 관찰한다.

## 실습 명령

```bash
ps -ef
pstree -p
top
cat /proc/$$/status
cat /proc/$$/maps
```

## 관찰할 것

- PID와 PPID
- process state
- virtual memory map
- 열린 file descriptor

## 확인 질문

1. Shell process와 현재 실행한 command process의 관계는 무엇인가?
2. `/proc/<pid>/status`에서 process state는 어떻게 보이는가?
3. `/proc/<pid>/maps`는 address space 이해에 어떻게 도움이 되는가?

