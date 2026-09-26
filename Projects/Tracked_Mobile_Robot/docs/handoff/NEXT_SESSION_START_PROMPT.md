# Next Session Start Prompt

새 대화에서는 아래 프롬프트로 이어간다. 전체 대화나 과거 문서를 처음부터 불러오지 않는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행해라.
저장소 C:/Users/eyh12/workspace/TIL, 브랜치 agent/dual-encoder-bringup.

2026-09-27 종료: M1 수동 시험 코드를 내가 입력하다가 중단했다.
hello_world_main.c는 bridge_bench_command()까지 입력했고,
bridge_bench_advance/console_init/console_poll은 빈 함수다. app_main의 init/poll 두 호출도 미추가다.
#if 줄 연속 처리 누락과 SCRIPED/finished/HLEP 오타가 있으니 안내 문서의 재개 메모를 확인해라.
기존 네 ESP hook은0U, 새 수동 시험 매크로는1U다. 소스는 미완성 WIP이며 새 빌드·플래시·HELP·모터 구동은 하지 않았다.
기능 코드를 네가 대신 완성하지 말고, 연결된 블록으로 설명하면 내가 입력한다.
설명은 enum과 s_bench_state까지 했으니 expected_seq/tel_mark 등 상태 변수부터 이어가라.
이미 입력한 코드를 처음부터 다시 타이핑시키지 마라. 양쪽 보드 빌드·플래시도 내가 직접 한다.
완성 후 실제 파일 검토 → 사용자 ESP 빌드·플래시 → LiPo 분리 상태 HELP부터 진행한다.

현재 A=왼쪽/M1/JENC_1/TIM3/left, B=오른쪽/M2/JENC_2/TIM5/right다.
A+→M1A/A−→M1B 연결했고 B 동력선은 분리·절연 유지다. 두 모터는 섀시에서 분리한 상태다.
커넥터 교환 뒤 채널 독립성·전진 양수/후진 음수·정지0 손회전 PASS다. 1560 counts/rev는 유지한다.
네 실제 A/B LOW0V/HIGH 약2.86V, 정지10초 이상 CPS0 검사도 완료했다.
STM 단독 warm reset 로그 TEL169개에서200~17000ms CPS/PWM0, 300/400ms도0이다.
최초0~200ms와 cold boot는 미검증이고 초기 ESP parser 경고6회도 원본에 보존했다.
S1 OFF/ON 순간 양쪽CPS −10/+10은 바로0으로 돌아왔다. 같은 문제 진단이나 저항/필터 변경으로 돌아가지 마라.

T004 기존 PASS, 전체 T005A PARTIAL 유지. MDD B+=K1 87/B−=GND16AWG, K1주선14AWG다.
F1/F2 Littelfuse10A/1A 사용자 확인, 14AWG로 진행한다는 결정을 다시 묻지 마라.
이번 rail 0.23→11.78V, S0잠금 후5초1.28/30초0.59V는 관측값이며 전체 rail-off PASS가 아니다.
마지막 셀 보고4.12/4.16/4.16V와 상세 이력은 report30이다. 실제 전동 구동은 아직 하지 않았다.
최종 전원 분리 완료는 보고되지 않았으므로 실제 상태를 확인해라.
USB 개발은 #1 두2P 분리·절연, JP5=U5V/JP1=OPEN. 실제 회전은 별도 조건 확인 뒤 진행한다.

먼저 git status/최근 commit과 다음 작은 자료만 읽어라.
1. Projects/Tracked_Mobile_Robot/AGENTS.md
2. docs/handoff/CURRENT_SESSION_CONTEXT.md
3. docs/progress/2026-09-27_progress.md
4. docs/plans/2026-09-27_M1_One_Shot_Console_Code_Guide_ko.md와 실제 ESP main
상세 하드웨어 사실이 필요할 때만 report29/30을 읽어라.
완료한 검사와50회전 보정을 반복하지 말고, progress는 작업 마감 때 모아서 갱신해라.
사용자 요청 없이 subagent나 D: 전체 대화 아카이브를 사용하지 마라.
```
