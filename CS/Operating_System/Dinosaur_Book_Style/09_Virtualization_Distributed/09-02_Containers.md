# 09-02. Containers

## 결론

컨테이너는 같은 커널을 공유하면서 process, filesystem, network 같은 OS 자원을 격리하는 방식이다.

## 핵심 개념

- `Namespace`: process, network, mount 등을 분리해서 보이게 한다.
- `cgroup`: CPU, memory, I/O 같은 자원 사용량을 제한한다.
- `Image`: 실행 환경을 재현하기 위한 filesystem template이다.

## 확인 질문

1. 컨테이너는 왜 VM보다 가볍게 시작될 수 있는가?
2. 같은 kernel을 공유한다는 것은 어떤 보안 의미를 갖는가?
3. Namespace와 cgroup은 각각 어떤 문제를 해결하는가?

