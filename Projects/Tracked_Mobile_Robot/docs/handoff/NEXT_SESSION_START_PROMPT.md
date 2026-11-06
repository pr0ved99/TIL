# 다음 세션 시작 프롬프트 — 2026-11-07 수면 후 재개

Tracked_Mobile_Robot 프로젝트의11/6 CAD 작업을11/7에 마감했다. 작업 폴더는 C:\Users\eyh12\workspace\TIL이다.

1. 루트/프로젝트 AGENTS.md.
2. docs/handoff/CURRENT_SESSION_CONTEXT.md의 현재 재개점.
3. docs/progress/2026-11-07_progress.md와 assets/logs/pcb_design/2026-11-07_cad_closeout/publication.json.
4. 09_Electrical_Design/28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md. 상단 최신 상태와 본문의 이전 스냅샷을 구분한다.

Shield는40부품+PWR_FLAG2개, 전압2채널·공통 제어 연결표 대조와 기존 설정 ERC0/0까지 완료했다. MVP 기능 도면의 Candidate 최신화도 완료했고 설계29에 부품별 근거가 있다. 예전 applied.pdf를 최신 도면으로 사용하지 않는다. KiCad를 디스크 최신본으로 다시 연다.

**첫 작업은 수집·필터 표**다. 기존 측정 목적·응답 목표를 읽고 채널별 원시 수집률→아날로그/디지털 필터→출력 주기를 설명/계산한다.100Hz·10개 평균은 첫 DC 비교용이며 모터 운용 확정값이 아니다. 이어 포트·전원 조건표(정상→고장/전원 상태→보호→확인 기준)를 작성한다. 기본 분압/TPS/TMUX/STM 내장ADC 구조는 유지하고 필요한 변경을 판단한 후 풋프린트/PCB로 진행한다.

목적→용어/원리→가정/계산→설계 판단→남은 검증의 번호 있는 필기 형식을 유지한다. 결론을 먼저 제시하고 데이터시트 판본·쪽·절/표/행·조건을 알려준다. 자료39-3 작성과 사용자 필기 보고36-19·실측 완료를 구분한다.

기존 Git 변경을 확인하고 무관한 변경을 보존한다. 실물은11/5전원 분리 보고 상태이며 새 빌드/플래시·실물·구매를 시작하지 않는다. NotebookLM은 별도. 전체MVP PARTIAL/OPEN, T005A PARTIAL/T007 BLOCKED와11/9·10휴무 유지. 완료한 회로도 작성/ERC·이전 시험을 자동 반복하지 않는다.
