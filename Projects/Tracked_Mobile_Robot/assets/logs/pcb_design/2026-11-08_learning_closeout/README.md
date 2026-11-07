# 11/8 학습 마감 — 14장·37-2와 Notion 필기

사용자 요청 `정리해`와 `노션에 작성하던 필기도 너가 작성 다 해`에 따른 문서/게시 마감이다. [진행 기록](../../../../docs/progress/2026-11-08_progress.md)과 [현재 재개점](../../../../docs/handoff/CURRENT_SESSION_CONTEXT.md)을 우선한다.

## 보존한 근거와 완료 범위

- [14장 사용자 관측/원본 검증](../2026-11-07_discharge_check/README.md): 1τ 872.468678mV, 약99% 23.8408803mV. 워크북/PNG/CSV를 보존했다.
- [37-2 모델·관측 전사](../2026-11-07_input_settling_check/README.md): 저장 회로/워크북과 대화 커서값. 원본 PNG/CSV는 미확인이다.
- [37-2 Notion 완료본](37_2_Notion_Completed.md): 사용자 기존1~6절/이미지 보존, 빠진 계산·결론 및 E/K·두 성분·a,b 유도 보충. 원본은 [Notion](https://app.notion.com/p/411a7326f87b80299d49ff79364f13ac)이다.
- [해석식 재현](second_order_calculation.py) / [계산 결과](second_order_calculation.json): 두 노드 방정식 계수와1차 극한을 정확한 분수로 교차 대조하고 두 시정수·유한 입력 상승의 정착 시간을 계산한다. 새 시뮬레이터 실행이 아니다.
- [외부 반영 확인](external_verification.json): Notion7페이지와Calendar2일정의 조회/보존 검사.
- [무관 변경의 시작 기준](baseline.json) / [로컬 검증](verification.json) / [게시 영수증](publication.json).

14장 음수 지수는 재조회 때 이미 맞아 있었다. Codex는 남은 단위·문장 오타와 과거 미기록 상태를 고쳤다. 37-2는 마감 당시 목적만 있는 페이지가 아니라 관측표까지 작성된 페이지였으며, 이를 읽은 뒤 이어 썼다. 이전 검토 기록은 해당 시점의 이력이다.

## 다음 시작

사용자는 두 성분과 a,b 유도에서 어려움을 보고했다. 노트 작성은 완료했지만 이해 완료로 기록하지 않는다. 37-2의 최종값/허용 잔차→C2 제외 근사와 포함 모델→VADC 전류식 하나부터 복습한다. 40-2/새 실습으로 바로 넘어가지 않는다.

자료40-1의2kHz는 후보, 실제 ADC 구현/잡음/보정/보호는 검증 전이다. 새 MCU 빌드·플래시/실물 시험 없음. 기존 MVP 판정과11/9·10휴무, NotebookLM 별도를 유지한다.

## 로컬 재현

프로젝트 루트에서 `python -X utf8 assets/logs/pcb_design/2026-11-08_learning_closeout/second_order_calculation.py`를 실행하면 같은 폴더의 JSON에 계산 결과를 저장한다. 소수점이 긴 계산은 명목 가정에 대한 수학 결과이며 실물 정확도가 아니다.

## 게시 확인

문서·진행/인수인계·Git·Calendar·Notion 다섯 항목을 완료했다. 내용 커밋 `05fee59ab64de6756dd8e5e02bbba93041ac5e24`의 원격 반영을 확인했으며 게시 영수증은 후속 커밋으로 저장한다. 무관19파일 보존과 계산/실물/이해 경계를 유지했다.
