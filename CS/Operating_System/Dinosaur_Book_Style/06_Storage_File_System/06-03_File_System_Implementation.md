# 06-03. File System Implementation

## 결론

파일 시스템 구현은 파일 이름, metadata, 실제 data block을 안정적으로 연결하는 문제다.

## 핵심 개념

- `Directory`: 파일 이름과 파일 metadata를 연결한다.
- `Inode`: 파일의 metadata와 block 위치 정보를 담는 구조다.
- `Block allocation`: 파일 데이터를 어느 block에 둘지 결정한다.
- `Free space management`: 빈 block을 추적한다.

## 비교 관점

- Contiguous allocation: 빠르지만 확장과 단편화 문제가 있다.
- Linked allocation: 확장은 쉽지만 random access가 느릴 수 있다.
- Indexed allocation: index block으로 위치를 관리한다.

## 확인 질문

1. 파일 이름이 inode 자체가 아닌 이유는 무엇인가?
2. Hard link와 symbolic link는 어떻게 다른가?
3. 큰 파일과 작은 파일에 같은 allocation 정책이 항상 좋은가?

