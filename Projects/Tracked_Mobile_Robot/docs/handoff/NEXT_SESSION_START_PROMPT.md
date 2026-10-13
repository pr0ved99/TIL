# Next Session Start Prompt

최신 기준: **2026-10-13 — zero-only 통합·사용자 관측, 최신 main C42/JS46, 교과서 작성·학습 흐름 보완**.
현재 대화에서 계속해도 된다. 나중에 재개할 때 아래 내용을 사용한다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행해라.
저장소 C:/Users/eyh12/workspace/TIL, branch agent/dual-encoder-bringup.
AGENTS.md, docs/handoff/CURRENT_SESSION_CONTEXT.md,
docs/progress/2026-10-13_progress.md부터 읽어라. 전체 대화 아카이브는 재탐색하지 마라.

parser/ticket/owner/state/executor와 main/브라우저 zero-only 제어는 연결돼 있다.
사용자는 통합 빌드·플래시·모니터를 수행했고, ARM/zero ACTIVE와 수동/창 전환 정지 등을 보고했다.
최신 바이너리 식별값은 확보하지 않았다. 전체 AC-B/S와 실제 nonzero 구동 안전은 미완료다.
최신 저장 main C42·PAGE JS46 PASS 근거:
assets/logs/wifi_link/2026-10-13_git_closeout/manifest.json.
이는 PC mock 검사이며 실제 RTOS/무선/전기적 동작을 증명하지 않는다.

STM·ESP 교과서는 07_Embedded_Learning_Notes/06_STM32_ESP32_Firmware_Textbook/README.md에서 시작한다.
0~20장 본문, 12개 학습 단위, 예제 5개가 있고 run_examples.py --lesson 01로 하나씩 실행한다.
학습 시작은 단위 1. 사용자 요청 없이 새 제어 모듈 파일을 계속 늘리지 마라.

전원 조건은 초기 USB·LiPo/모터 전원 분리 이후 변경 보고가 있었다.
사용자는 PC7 조건 때문에 LiPo가 필요하다고 설명하고 '#1만 분리'를 보고했다.
이후 ESTOP_LATCHED, STM reset 뒤 DISARMED/BOOT 관측이 있다.
시험 종료 시 전원 상태는 미보고이므로 초기 분리 상태를 현재로 가정하지 마라.
실물 시험은 다음 미완료 항목의 조건과 증거를 확인해서 이어가라.

ARM은 수동 시작, 이후 zero CMD만 허용한다. 포커스 상실·연결 종료는 취소/정지다.
재접속/포커스 복귀 시 자동 ARM 없음. DISARM OK는 ACK와 새 정지 TEL 확인을 요구한다.
READY/PING OK는 구동 허가가 아니다. 별도 UART bridge hook 복구와 전체 안전 잔여 조건은 유지한다.

펌웨어 입력·보드 빌드/플래시·물리 작업은 기본 사용자 수행이다.
Codex는 승인된 문서/PC 검사 작업을 수행하며 사용자 요청 없이 subagent를 쓰지 않는다.
교과서와 관련 코드/검사/근거는 사용자 요청으로 Git 반영 대상으로 정리했다.
동기화 상태는 git status/log와 원격 hash로 확인해라. Hello World tracked build 산출물은 보존한다.
```
