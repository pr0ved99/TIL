# Next Session Start Prompt

새 대화에서는 아래 프롬프트로 이어간다. 전체 과거 대화/문서를 처음부터 불러오지 않는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행해라.
저장소 C:\Users\eyh12\workspace\TIL, 브랜치 agent/dual-encoder-bringup.

9/23 종료: 엔코더 1kΩ 직렬+15kΩ 풀다운 네 채널을 만능기판에 납땜했고,
저항 8곳·전원 연결/단락 6곳 모두 통과했다. JENC_1/2 공급은 둘 다 +5.05V다.
실제 엔코더 연결과 수동 회전부터 다음에 하기로 했다. 완료 검사를 반복하지 마라.
첫 단계는 실제 전원 OFF 상태와 엔코더 4선 케이블 준비 여부/핀 방향 확인이다.
모터 동력선은 계속 분리한다. STM32를 꽂기 전에 엔코더 A/B의 LOW/HIGH를 측정한다.

9/23 monitor는 STM 부팅 4.2초 이후 약 40초/TEL400의 양쪽 CPS=0을 확인했다.
부팅 직후 300/400ms 튐이 해결됐다고 단정하지 마라. err=7 고정/RX_DESYNC 이력도 있다.

T004는 완료했고 T005A run01~06은 report 27로 정리됐다. T005A 전체는 PARTIAL이다.
현재 MDD B+=K1 87, B−=GND 16 AWG, K1 주선 14 AWG, 버스바 두 개를 사용한다.
두 모터는 분리했다. ESP 네 hook은 모두 0U이며 복구 runtime과 당시 static 30/30 PASS다.
완료한 T004나 복구 시험/펌웨어 입력을 다시 시키지 마라.

먼저 git status와 최신 project commit을 확인하고 다음 작은 자료만 읽어라.
1. Projects/Tracked_Mobile_Robot/AGENTS.md
2. Projects/Tracked_Mobile_Robot/docs/handoff/CURRENT_SESSION_CONTEXT.md
3. Projects/Tracked_Mobile_Robot/docs/progress/README.md와 2026-09-23_progress.md
4. 현재 측정에 필요한 report 28의 핀/Net 표와 다음 단계

현재 도면은 ...ENC_Conditioning_WIP.vrt와 exports의 동일 이름 PDF다.
과거 CTRL수정본/addIMU를 현재 배선 기준으로 사용하지 마라.
펌웨어 입력과 양쪽 보드 빌드·플래시는 내가 직접 한다.
한 번에 논리적으로 연결된 작업 묶음을 안내하고, 통과 결과는 반복하지 마라.
progress는 작업 종료 때 대화 결과를 모아 갱신한다. 실제 관측과 추정을 구분해라.
사용자 요청 없이 subagent를 생성하거나 D: 전체 과거 대화를 불러오지 마라.
```
