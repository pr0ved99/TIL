# 다음 세션 시작 프롬프트 — 2026-11-12 학습 마감 후 재개

마지막 마감: **2026-11-13**. docs/progress/2026-11-13_progress.md와 assets/logs/pcb_design/2026-11-13_ports_and_materials_closeout/publication.json을 우선한다.41-1~41-5 자료와 도면/보고서 최신화 누락 수정까지가 이번 마감 범위다.

Tracked_Mobile_Robot 프로젝트를 이어서 진행하자. 작업 폴더는 C:\Users\eyh12\workspace\TIL이다.

먼저 루트/프로젝트 AGENTS.md, docs/handoff/CURRENT_SESSION_CONTEXT.md 상단, docs/progress/README.md와 2026-11-12_progress.md를 읽어라. 실제 게시 범위는 assets/logs/pcb_design/2026-11-12_sampling_filter_closeout/publication.json으로 확인한다. 이전 이력의 당시 다음 작업을 현재 지시로 해석하지 않는다.

41-5 포트별 고장·오접속 설명 자료까지 작성했다. NTC 단선/단락의 전압 방향, 전압 RAW선 단선과실제0V의 중복, 전류 OUT선 단선의 불확정성과진단/보호 차이를 구분한다. 현재 필기/질문 뒤 다음 진행 요청에는 **41-6 보호 경로·검증 기준**으로 넘어간다. 사용자 수기/이해 완료를 추정하지 않는다. 41-1~5나과거 실습을 자동 반복하지 않는다. 현재 포트 연결과추가 계산은 assets/logs/pcb_design/2026-11-12_port_inventory/README.md 및 fault_conditions.json을 따른다. 기존NTC100Hz·3회 진단 시험안과2kHz 검토안을 혼합하지 않는다. 조건 검토→보호 경로·검증 기준→필요한 회로 변경→기구·풋프린트→PCB 순서다. 실물 고장 주입·빌드·플래시는 시작하지 않는다.

40-2 시간·진폭비·두 alias, 40-3 조건표·온도 평균 창 비교 자료를 작성했다. 사용자는 37-2 수기/두 시정수 원리 이해, 이후 40-2 부분 이해, 마지막 온도 B안의 G(f)와 alias 구분 이해를 보고했다. 이를 40장 전체 수기/이해 완료로 확대하지 말고 이미 이해한 37-2를 자동 반복하지 않는다.

전압·전류 2kHz/200개·100ms, 온도 A 2kHz/2,000개·1초 평균은 비교 기준이다. B는 출력1Hz를 유지하며 직전1,000개·0.5초만 평균하는 대안이다. 명목 응답 약1.975/1.487초, 0.9Hz ADC 전압 진폭비 10.93%/69.86%, 두 안의 출력 alias는 모두0.1Hz다. A를 유지하고 B는 실제 응답·잡음·구간 대표성을 함께 판단할 때 비교한다. 기존100Hz DC 시험안도 유지한다. 계산은 실제 PASS/설정 구현이 아니다.

근거: assets/logs/pcb_design/2026-11-08_sampling_filter_review/와 2026-11-11_temperature_window_comparison/, 학습21의40-2·40-3. 원래 순서대로 진행하며 새로운 정현파/PWM/FFT 실습을 추가하지 않는다. 고정 수집·평균·환산 후보를 실시간 FFT/자동 필터링 구현 계획으로 바꾸지 않는다.

실물은11/5 전원 분리 보고 상태다. 11/12 자료 감사에서 Shield40부품+플래그2개/ERC0/0(기존 무시4규칙)을 재확인했다. PCB는22풋프린트/배선·영역0이며 회로도 대조21건(부품18+net3), 미배선32가 남는다. 기본 PDF는09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/exports/TMR_Monitor_Shield_RevA_schematic.pdf, 현재 검사 결과는같은프로젝트reports/README.md다. IDE applied.pdf는11/6 과거 스냅샷이다. 실제 잡음·보정 잔차·전원 전이·보호 검증은 남아 있다. MVP PARTIAL/OPEN·T005A PARTIAL·T007 BLOCKED·TMR-04 NOT TESTED, 기존 Git 변경 보존, NotebookLM 별도를 유지한다.

번호 있는 필기 형식으로 결론 → 목적 → 용어·원리 → 가정·계산 → 설계 판단 → 남은 검증 순서를 따른다. 기호·단위·계산 맥락을 생략하지 않고, 데이터시트는 판본/쪽/절·표·행/적용 조건을 안내한다.
