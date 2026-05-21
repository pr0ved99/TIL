# 08-03. Security Threats

## 결론

운영체제 보안은 권한 상승, 정보 유출, 서비스 방해를 막기 위해 설계와 운영을 함께 다룬다.

## 핵심 위협

- `Privilege escalation`: 낮은 권한에서 높은 권한을 얻는 공격이다.
- `Malware`: 악성 목적의 소프트웨어다.
- `Denial of service`: 자원을 고갈시켜 정상 서비스를 방해한다.
- `Side channel`: 직접 데이터가 아니라 시간, 캐시, 전력 같은 간접 정보로 비밀을 추정한다.

## 확인 질문

1. Kernel bug가 user program bug보다 위험한 이유는 무엇인가?
2. 최소 권한과 sandboxing은 어떤 문제를 줄이는가?
3. 보안 패치는 왜 성능이나 호환성과 trade-off가 있을 수 있는가?

