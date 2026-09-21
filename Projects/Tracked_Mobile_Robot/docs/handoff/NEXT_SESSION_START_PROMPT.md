# Next Session Start Prompt

새 Codex 대화에서는 아래 짧은 프롬프트를 사용한다. 과거 세션 원문이나 전체 프로젝트 문서를
처음부터 모두 읽게 하지 않는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행해라.

저장소: C:\Users\eyh12\workspace\TIL
프로젝트: Projects/Tracked_Mobile_Robot
브랜치: agent/dual-encoder-bringup

9/22 종료 지점: T-ESTOP-004 모터 분리 조건의 conditioned PWM/latch/reset/wire-open과
all-hooks-0U 복구까지 PASS다. 정적 검사 30/30, run07 25초 PWM HIGH0/자동 ARM·CMD0이다.
완료한 T004/배선/코드 입력을 반복하지 마라. 빌드·플래시는 내가 직접 한다.
다음은 전원 분배·퓨즈·K1 단자 release 미결 항목을 정리하고 T-ESTOP-005A를 준비하는 것이다.
실행 순서는 docs/plans/2026-09-22_Next_Session_Power_Path_and_T_ESTOP_005A_Plan_ko.md을 따른다.
이미 실물에서 해결한 항목은 기록으로 닫고, 완료한 검사를 반복하지 마라.
Git 종료 중 새 VRT 저장본이 추가됐으니, 도면으로 측정점을 안내하기 전에 검증 당시 파일과
관련 Net 변경을 확인해라. 최신 hash와 검토 경계는 CURRENT_SESSION_CONTEXT에 있다.
아직 MDD10A B+나 모터를 연결하지 마라. 왼쪽 PB4/PB5 임시 15kΩ GND pull-down은 유지 중이다.
9/22 Git 저장 요청 범위는 문서·검증 증거·다음 세션 계획·ESP hook0 복구다.
최신 커밋과 원격 동기화 상태를 확인하고 기존 변경을 보존해라.

먼저 git status와 최신 project commit을 확인하고 기존 변경을 보존해라. 그다음 아래 자료만 먼저
읽어라.

1. Projects/Tracked_Mobile_Robot/AGENTS.md
2. Projects/Tracked_Mobile_Robot/docs/handoff/CURRENT_SESSION_CONTEXT.md
3. Projects/Tracked_Mobile_Robot/docs/progress/README.md
4. 최신 progress 1개

현재 한 가지 작업에 직접 필요한 plan/report/source만 추가로 읽어라. PROJECT_MEMORY 전체,
과거 progress/handoff, D:의 대화 archive는 현재 문서에 사실이 없거나 충돌할 때만 검색해라.

펌웨어는 내가 직접 입력한다. 서로 연결된 함수나 scheduler 수정은 깨작깨작 나누지 말고 정확한
교체 범위, 검토된 코드 전문과 상태 흐름의 이유를 한 번에 제시해라. 저장 뒤 실제 파일을 다시 읽어
검토하고, 내가 직접 수정을 명시적으로 맡긴 범위만 대신 수정해라.

Bench는 현재 gate와 최종 목적을 먼저 말하고 한 번에 한 동작만 안내해라. 내가 `통과 다음`이라고
하면 그 범위만 완료로 기록하고, 변경이나 실패가 없는 완료 시험을 반복하지 마라. 연결되지 않은
부품을 probe endpoint로 지시하지 마라.

진행 문서는 작업 블록이 끝났을 때 대화 결과를 모아 한 번에 갱신해라. 수치·PASS·배선 상태를
추정하지 말고 build/static, board runtime, electrical evidence를 구분해라.
```
