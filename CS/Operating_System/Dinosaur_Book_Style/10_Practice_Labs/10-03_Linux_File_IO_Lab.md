# 10-03. Linux File I/O Lab

## 결론

Linux file I/O를 관찰하면 file descriptor, buffer cache, system call 흐름을 실제로 연결할 수 있다.

## 실습 명령

```bash
lsof -p $$
ls -li
stat README.md
df -h
mount
```

선택 실습:

```bash
strace -e openat,read,write,close ls >/tmp/os_strace.log 2>&1
sed -n '1,40p' /tmp/os_strace.log
```

## 관찰할 것

- inode 번호
- file descriptor
- filesystem mount point
- open/read/write/close system call

## 확인 질문

1. 파일 이름과 inode는 어떤 관계인가?
2. 같은 파일을 여러 이름으로 가리킬 수 있는 이유는 무엇인가?
3. `strace`로 system call을 보면 file abstraction이 어떻게 드러나는가?

