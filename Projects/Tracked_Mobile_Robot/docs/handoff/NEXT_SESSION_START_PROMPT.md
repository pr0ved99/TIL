# 다음 세션 시작 프롬프트 — 2026-11-08 학습 마감 후 재개

Tracked_Mobile_Robot 프로젝트를 이어서 진행하자. 작업 폴더는 C:\Users\eyh12\workspace\TIL이다.

먼저 루트/프로젝트 AGENTS.md, docs/handoff/CURRENT_SESSION_CONTEXT.md의 상단 현재 재개점, docs/progress/2026-11-08_progress.md를 읽어라. 게시 완료 범위는 assets/logs/pcb_design/2026-11-08_learning_closeout/publication.json으로 확인한다.

이번 첫 작업은 **37-2 입력 정착 실습의 이해 보완**이다. 필기는 사용자 위임으로 Codex가 완성했으며 사용자 이해 완료와 다르다. 사용자는 두 커패시터의 빠른/느린 성분과 a,b 유도에서 어렵다고 하여 중단했다.

- Notion 원본: https://app.notion.com/p/411a7326f87b80299d49ff79364f13ac
- 로컬 완료본: assets/logs/pcb_design/2026-11-08_learning_closeout/37_2_Notion_Completed.md
- 계산 재현: 같은 폴더 second_order_calculation.py/.json
- 사용자 관측/모델: assets/logs/pcb_design/2026-11-07_input_settling_check/README.md

먼저 필기5~7절의 최종 VADC2.371352579V·허용 잔차1.482095mV·입력 환산10mV와 관측2.680~2.690ms를 짧게 연결한다. 그다음9절의 C2 제외1차 근사와 C2 포함 모델을 설명하고,10-1~10-3의 **VADC 노드 전류식 하나**부터 천천히 진행한다. i=C dV/dt의 의미가 연결된 뒤 VDIV 식과 소거로 넘어간다. 초반 가파름/후반 완만함을 빠른/느린 성분으로 나누지 않는다.

회로를 열 필요가 있으면 09_Electrical_Design/KiCAD/Simulation/03_Voltage_Divider/03_14_Voltage_ADC_InputSettling_TRAN.kicad_sch와 03_14_InputSettling_Check_2026-11-07.wbk를 사용한다. V1 PWL은0 0 1m 0 1.001m 16 6m 16, V3는고정3.3V, TRAN은.tran 1u 6m 0 100n이다. 새 실행 없이 기존 결과로 복습할 수 있다.

14장1τ/99% 관측과37-2 입력 정착 사용자 관측은 이미 완료했다. 37-2의1τ 전압은 계산값이며 PNG/CSV 내보내기는 미확인이다. 전체37~40 필기/이해 완료를 추정하지 않는다. 이후 선택36·38→37-4/40-2 수집·평균 비교→포트·전원 조건표 순서다. 40-1의2kHz는 비교 후보이며 채택/구현이 아니다.

실제 Shield40부품+PWR_FLAG2개/ERC0/0와 MVP 도면 최신화는 이전 마감 상태다. IDE의11/6 applied.pdf는 과거 스냅샷이다. 실물은11/5 전원 분리 보고 상태이며 MCU 빌드/플래시·실물·구매를 시작하지 않는다. 기존 Git 변경 보존, MVP PARTIAL/OPEN·T005A PARTIAL·T007 BLOCKED·TMR-04 NOT TESTED,11/9·10휴무, NotebookLM 별도 작업을 유지한다.

결론→목적→용어·원리→가정과 계산→설계 판단→남은 검증 순서로 번호 있는 필기 형식으로 안내한다. 수식의 기호·단위와 계산 맥락을 생략하지 않는다.
