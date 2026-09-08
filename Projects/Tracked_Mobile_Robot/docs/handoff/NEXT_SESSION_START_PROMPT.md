# Next Session Start Prompt

새 Codex 대화에서는 아래 짧은 프롬프트를 사용한다. 과거 세션 원문이나 전체 프로젝트 문서를
처음부터 모두 읽게 하지 않는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행해라.

저장소: C:\Users\eyh12\workspace\TIL
프로젝트: Projects/Tracked_Mobile_Robot
브랜치: agent/dual-encoder-bringup

먼저 git status와 최신 project commit을 확인하고 기존 변경을 보존해라. 그다음 아래 자료만 먼저
읽어라.

1. Projects/Tracked_Mobile_Robot/AGENTS.md
2. Projects/Tracked_Mobile_Robot/docs/handoff/CURRENT_SESSION_CONTEXT.md
3. Projects/Tracked_Mobile_Robot/docs/progress/README.md
4. 최신 progress 1개

현재 한 가지 작업에 직접 필요한 plan/report/source만 추가로 읽어라. PROJECT_MEMORY 전체,
과거 progress/handoff, D:의 대화 archive는 현재 문서에 사실이 없거나 충돌할 때만 검색해라.

펌웨어는 작은 블록과 정확한 위치를 먼저 설명하고 내가 직접 입력·저장하면 실제 파일을 다시 읽어
검토해라. 내가 직접 수정을 명시적으로 맡긴 범위만 대신 수정해라.

Bench는 현재 gate와 최종 목적을 먼저 말하고 한 번에 한 동작만 안내해라. 내가 `통과 다음`이라고
하면 그 범위만 완료로 기록하고, 변경이나 실패가 없는 완료 시험을 반복하지 마라. 연결되지 않은
부품을 probe endpoint로 지시하지 마라.

진행 문서는 작업 블록이 끝났을 때 대화 결과를 모아 한 번에 갱신해라. 수치·PASS·배선 상태를
추정하지 말고 build/static, board runtime, electrical evidence를 구분해라.
```
