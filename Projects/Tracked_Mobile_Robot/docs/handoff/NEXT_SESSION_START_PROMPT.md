# 다음 세션 시작 프롬프트 — 2026-11-06 수면 후 재개

Tracked_Mobile_Robot 프로젝트의11/5 후속PCB학습을11/6에마감했다. 사용자는자고 일어나11월6일작업을이어간다.

## 먼저 읽기

1. 루트/프로젝트 AGENTS.md.
2. docs/handoff/CURRENT_SESSION_CONTEXT.md 상단 현재 재개점.
3. docs/progress/2026-11-06_progress.md와실제 게시 영수증.11/5기록은필요한이력만읽는다.
4. 09_Electrical_Design/26_Voltage_ADC_Component_Conditions_and_Control_Draft_2026-10-31_ko.md 상단판단/인계표.
5. 필요한경우학습21의39-3과6채널계약20.36~39전체를다시읽거나반복설명하지않는다.

## 첫 작업

기존 `09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/TMR_Monitor_Shield_RevA.kicad_sch`를실제로 읽고전압 2채널계약과대조해반영 범위/연결표를만든다. 파일 존재와9.0/RevA.0-DRAFT헤더만확인된 상태이며내부 연결대조/편집/ERC는아직수행하지않았다.

전단S1/D1→PA4/ADC1_IN4/CN7-32·후단S2/D2→PB0/ADC1_IN8/CN7-34후보,채널별12k+12k/4.7k·100nF·1k·TMUX·47k,공통RESET/SEL·AVDD를대조한다. 기존 전류/온도회로와무관한 변경을보존한다. 대조 결과를설명한뒤사용자와 배터리측한 채널→모터 공급측/공통 제어→ERC순서로진행한다.

## 유지할 설계/학습 경계

- 자료 39-3까지작성,사용자필기 완료 보고36-19까지. 진행요청을이해/필기·실측 완료로확대하지않는다.39절은3소챕터로마쳤다.
- 목표0~16V DC·보정후±0.10V·주위20~30°C·10Hz·입력안정후300ms. 현재 회로/내장ADC유지.
- 제작저항±0.1%·TCR25ppm/°C 이하·사용조건0.1W/25V 이상. ADC12bit·14MHz·480cycles,채널당100Hz/유효10개,1V/15V보정은진행 기준이며실제 품목·구현 완료가아니다.
- 보정/검증비교경계각25mV이내를준비한다. G25mV에서차이75mV이하PASS/75초과125이하보류/125초과FAIL,준비부족NOT_READY. 실제 잡음/계수/잔차·정확도/전원OFF보호는후속검증이다.
- 설명은결론→근거→문제발생시변경순서로대화에필기본문을직접제공한다. 목적·용어·가정·계산의맥락을생략하지않으며데이터시트판본·쪽·절/표/행·조건을명시한다.
- 실물은11/5전원 분리완료 보고상태. 빌드/플래시·실물 구동을시작하지않는다. MCU작업은기존사용자수행방식을따른다.
- NotebookLM자료제작은별도. 바탕화면스냅샷은자동 동기화가아니며전체 업로드/최종 영상완료를추정하지않는다.
- 기존MVP PARTIAL/OPEN,T005A PARTIAL/T007 BLOCKED를유지한다. 완료시험/후속제외범위를자동반복하지않는다.11/9·10프로젝트휴무와기존 일정 시간은유지한다.

정리는문서·진행/메모리·선택Git commit/push·기존Calendar·Notion의다섯항목이다. 실제 게시근거는 `assets/logs/pcb_design/2026-11-06_learning_closeout/publication.json`을따른다.
