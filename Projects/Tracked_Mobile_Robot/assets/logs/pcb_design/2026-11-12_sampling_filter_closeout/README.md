# 40-2·40-3 수집·필터 학습 마감 — 2026-11-12

사용자 요청 “그래 이해했어. 일단 오늘은 여기까지만 하자. 마무리하고 정리해”에 따른 다섯 항목 마감이다.11/8 게시 이후의 로컬 학습·계산과11/11~12 질문을 포함한다. 클라이언트 날짜2026-11-12/Asia/Seoul를 기준으로 기록한다.

## 결론과 다음

전압·전류2kHz/200개·100ms와 온도A2kHz/2,000개·1초 평균을 비교 기준으로 유지한다. B는매1초출력직전1,000개·최근0.5초 평균의대안이다. A/B 명목응답극한약1.975/1.487초,0.9Hz ADC전압진폭비10.93%/69.86%,출력alias모두0.1Hz다. 구현/실제성능PASS가아니다.

사용자37-2수기/두시정수원리이해,40-2부분이해,마지막B안의G(f)/alias구분이해보고를구분한다. 다음은포트·전원조건표이며새FFT/PWM실습을추가하지않는다. 기존100Hz DC시험안·전원분리보고·NotebookLM별도·기존MVP판정유지.

## 근거

- [11/12 실적·다음](../../../../docs/progress/2026-11-12_progress.md)
- [현재 인수인계](../../../../docs/handoff/CURRENT_SESSION_CONTEXT.md)
- [40-2 수학 계산](../2026-11-08_sampling_filter_review/README.md)
- [40-3 온도 창 수학 계산](../2026-11-11_temperature_window_comparison/README.md)
- [학습21](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md)
- [Notion 40-3 기존 필기](https://app.notion.com/p/415a7326f87b80be88d2e8c2be58968a)
- [게시 영수증](publication.json), [외부 반영 검증](external_verification.json), [로컬 검증](verification.json), [선택 파일](scoped_paths.json), [시작 상태](baseline.json)

## 경계

문서와 수학 모델의 검산이다. 새 GUI 시뮬레이션·ADC취득·잡음실측·MCU빌드/플래시·실물·CAD편집없음. Notion 원문/하위페이지/이미지/상태와 Calendar 시간·알림·회의링크를 보존한다. 시작시 무관19파일을 해시로 확인하며 게시 성공 범위는 실제 영수증을 따른다.

## 실제 게시 결과

다섯 항목 마감 완료. 내용 커밋 `a01811b9`을 push하고 원격 HEAD 일치를 확인했다. Notion 기존8페이지 및 Calendar 기존5일정의 저장 상태를 재조회했다. Calendar 시간/알림/참석자/회의 링크와 무관19파일은 보존했다. 영수증은 후속 커밋에 저장하며 최신 해시는 이 파일의 Git 이력을 따른다.
