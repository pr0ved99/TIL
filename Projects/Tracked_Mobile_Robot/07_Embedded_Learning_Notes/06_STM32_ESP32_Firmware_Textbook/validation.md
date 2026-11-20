# 교과서 예제 검증 — 2026-10-13

검사 대상은 이 폴더의 **PC 학습 예제**다. firmware 변경·보드 빌드·플래시·전원 조작·원격 명령 송신은 수행하지 않았다.

## 실제 실행

- Python: `C:/Espressif/tools/python/python.exe`
- C compiler: 로컬 TCC 0.9.27, `-std=c11 -Wall -Werror`
- JavaScript: 로컬 Node.js v22.20.0
- 실행 진입점: `examples/run_examples.py`, `--cc`와 `--node`로 실행 파일 지정.
- C 4개 컴파일/실행 + JavaScript 1개 실행 성공, runner exit code **0**.
- 아래는 도구 출력에서 옮긴 핵심 결과다. 독립적으로 수집한 보드 로그가 아니다.

~~~text
PASS 01: C values and time
PASS 02: byte chunks, strict parser and ring capacity
PASS 03: math only, no hardware output
125 ms CMD ACK only             -> ZERO_PENDING
130 ms fresh matching TEL       -> ACTIVE
165 ms DISARM ACK only          -> STOPPING
170 ms fresh stopped TEL        -> IDLE
issued=1000 expires=1150: at 1149 OK, at 1150 EXPIRED
270 ms 150 ms without ACK       -> BLOCKED
late ACK does not restore IDLE
PASS 04: real modules, simulated clock/transport/TEL
PASS 05: simplified browser timing model
All 5 PC lessons passed. No board, UART or network operation performed.
~~~

## 범위

- 예제 02~04는 현재 저장된 실제 순수 C 모듈을 링크한다. 원본 소스를 복사해 다른 구현으로 바꾼 검사가 아니다.
- 02의 줄 조립기는 학습용이며 실제 ISR·오류 재동기화 전체를 구현하지 않는다.
- 04의 TX 성공·ACK·TEL·시각은 합성 입력이다. 실제 태스크 경합·무선·UART 전기 신호는 검사하지 않는다.
- 05는 설명용 브라우저 축소 모델이다. 기존 실제 PAGE 검사를 새로 실행했다는 뜻이 아니다.
- [source_manifest.json](source_manifest.json)은 분석 대상과 예제 파일의 기준을 기록한다. 소스가 바뀌면 이 결과를 새 버전의 PASS로 자동 승계하지 않는다.

본문과 새 안내 문서의 상대 링크·reference link·목차 anchor·코드 fence·UTF-8 대체 문자·줄 끝 공백을 점검했으며 오류 0건이었다. 기존 색인 수정은 `git diff --check`를 통과했다.

## 학습 흐름 보완 후 확인 — 2026-10-13

학습 단위·연결 수업·예제 04 해설을 보강하고 runner에 `--lesson 01`~`05` 선택을 추가했다. 예제 C/JS와 실제 펌웨어 모듈의 내용은 바꾸지 않았다. 위와 같은 Python·TCC·Node 환경에서 다음을 확인했다.

- 번호 생략: 기존 C 4개 + JS 1개 전체 실행 성공.
- 번호 01~05 각각: 해당 예제만 실행하고 해당 번호의 성공 문구만 표시.
- C 예제 선택 시 존재하지 않는 Node 경로를 줘도 실행 성공, JS 선택 시 존재하지 않는 C compiler 경로를 줘도 실행 성공. 사용하지 않는 도구를 요구하지 않음을 확인했다.
- 잘못된 번호 `99`, 선택한 예제에 필요한 도구 누락: 비정상 종료하며 성공으로 표시하지 않음.
- 예제 04의 임시 복사본 세 개: TEL 생략·옛 seq TEL은 ACTIVE 검사, 입력 정리 알림 생략은 `take_tx` 검사에서 각각 예상대로 실패. 원본 예제와 펌웨어 파일은 바꾸지 않았다.

이는 안내된 PC 실습의 재현 확인이다. 보드·네트워크·동시 태스크에 대한 추가 시험은 아니다. 기준 소스 목록에서는 runner 해시와 PC 예제 재검증 시각만 갱신한다.
