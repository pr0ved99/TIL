# 06-01. Storage Stack

## 결론

저장장치 계층은 application의 file operation이 실제 block device 명령으로 내려가는 여러 층의 구조다.

## 핵심 개념

- `Block device`: 고정 크기 block 단위로 읽고 쓰는 장치다.
- `Buffer cache`: 자주 쓰는 block을 메모리에 보관한다.
- `File system`: 파일 이름과 block 배치를 관리한다.
- `Device driver`: 하드웨어별 명령을 처리한다.

## 흐름

```text
read(file)
-> VFS
-> file system
-> block layer
-> driver
-> storage device
```

## 확인 질문

1. File read가 항상 디스크 접근을 의미하지 않는 이유는 무엇인가?
2. HDD와 SSD에서 성능 병목은 어떻게 다를 수 있는가?
3. Buffer cache는 왜 중요하지만 위험할 수도 있는가?

