# 08-02. Access Control

## 결론

Access control은 누가 어떤 자원에 어떤 작업을 할 수 있는지 결정하는 정책이다.

## 핵심 모델

- `Access control matrix`: subject와 object의 권한 관계를 표로 표현한다.
- `ACL`: object마다 접근 가능한 subject 목록을 둔다.
- `Capability`: subject가 가진 접근 token으로 권한을 표현한다.

## 비교

| 방식 | 보기 쉬운 관점 | 주의점 |
| --- | --- | --- |
| ACL | 파일 기준 권한 확인 | 사용자별 전체 권한 파악 어려움 |
| Capability | 주체 기준 권한 확인 | token 보호 필요 |

## 확인 질문

1. Unix file permission은 어떤 access control 모델에 가까운가?
2. Capability가 유출되면 왜 위험한가?
3. 권한 revocation은 왜 어려울 수 있는가?

