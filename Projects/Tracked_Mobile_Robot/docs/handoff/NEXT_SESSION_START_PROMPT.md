# Next Session Start Prompt

새 대화에서는 아래 내용으로 이어간다. 전체 대화 아카이브를 다시 읽지 않는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행해라.
저장소 C:/Users/eyh12/workspace/TIL, 브랜치 agent/dual-encoder-bringup.

2026-09-30 현재: 노트북에서 검증 매트릭스 → 전체 실행 계획 → README → 진행 기록 형식의 문서 개편 4단계를 마쳤다.
9/29 측정·상세 기록은 보존했고 9/30에는 문서만 정리했다. 현재 사용자는 노트북만 있는 상태다.
이후 진행 기록은 docs/progress/README.md의 공통 템플릿으로 목표·기준점·결과·결정·다음 행동을 먼저 적는다.

마지막 하드웨어 기록은 2026-09-28~29: M1/M2 단일 모터 교차시험과 오른쪽 DIR 보정을 진행했고,
원래 배선의 B/M2 정방향·역방향10%/300ms 실제 회전/정지/CPS 부호/A 무동작을 확인했다.
장비 재개 시 다음 관찰 목표는 A/M1 양수10% 명령의 실제 차량 전진 방향이다.
A/M1 ±10%의 회전과CPS 부호는 이미 확인했지만 양수 시험 때 실제 방향은 보지 못했다.
B 교차시험을 A의 원래 배치 방향 검증으로 대신하지 마라.

현재 ESP는 M2 역방향 시험 이미지다.
M2_PULSE는 CMD(-50,-250,300), PWM0/-100을 만든다.
BRIDGE_M2_PULSE_TEST_ENABLED=1U, 기존 자동hook 네 개=0U다.
한 번 종료 후BENCH_FINISHED여서 RESET_ESTOP도 막힌다. 새 시도는 ESP 재부팅이 필요하다.
STM motor_output.c는 오른쪽 forward HIGH/reverse LOW, 왼쪽 forward LOW/reverse HIGH다.
정적31개 중30 PASS, 시험hook 모두0 요구1개 FAIL이며 default-off 복구 완료가 아니다.
사용자가 기능 코드를 입력하고 두 보드 빌드·플래시를 직접 한다.
수정할 때는 실제 소스를 읽고 정확한 위치와 완전한 연결 블록으로 설명해라.

A=왼쪽/M1/JENC_1/TIM3/left, B=오른쪽/M2/JENC_2/TIM5/right로 복원했고 두 동력선이 연결됐다.
두 모터는 섀시에서 분리했다. STM은 만능기판 장착, ESP는 UART USB 간섭 때문에 밖에 있다.
ESP GPIO17/18/GND만 대응 헤더로 연장했으며5V/3.3V 연장은 없다.
콘솔은UART 표기USB/COM5/115200. #1 보드용2P 두 개 분리·절연, STM U5V/JP1 OPEN의USB 구성이다.
1560 counts/rev, TIM3 부호 반전/TIM5 유지, 조정부와 손회전 검사를 다시 시작하지 마라.

마지막 역방향 로그49TEL/4.8초, CPS0 유지4.1초다.
정방향err=0과역방향err=1439는 각각 일정했고 그 사이 증가 위치는 미확정이다.
다음 준비의 부팅~READY/안정TEL을 저장해 기준과 증가 여부를 확인해라.
누적err 비영점만으로 시험 실패를 선언하거나 근거 없이 원인을 추정하지 마라.
전체T005A PARTIAL과 실제 S0 구동 중 차단/부하/주행 미완료를 유지한다.
마감 전원 분리 완료 응답은 아직 없다. 실제 상태를 확인해라.

먼저 작은 자료만 읽어라.
1. Projects/Tracked_Mobile_Robot/AGENTS.md
2. docs/handoff/CURRENT_SESSION_CONTEXT.md
3. docs/progress/README.md와 최신 docs/progress/2026-09-30_progress.md
4. 요청된 작업에 직접 필요한 자료 1개. 장비 재개라면 docs/plans/2026-09-29_Next_Session_M1_Direction_and_Bench_Closeout_ko.md
ESP 진입 파일명은 main/uart_bridge_main.c다. 이름 변경 뒤 사용자 보드 빌드는 아직 확인하지 않았다.
필요한 증거는report31과assets/logs/motor_output/2026-09-29_single_motor_bench에 있다.
9/27 코드 입력 WIP는 완료됐으므로 다시 시작하지 마라.
git status와최근커밋을 확인하고 진행 기록은 마감 때 모아서 갱신해라.
9/30 사용자가 누적 작업의 Git 커밋·푸시를 요청했다. 대상은 origin/agent/dual-encoder-bringup이며 main 병합은 포함하지 않는다.
Git 마감 전 Python 재검사도 30 PASS/1 FAIL(M2 시험 hook=1U)이었다. 최신 커밋과 원격 동기화 상태는 git으로 확인해라.
```
