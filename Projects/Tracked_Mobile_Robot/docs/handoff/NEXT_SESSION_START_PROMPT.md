# 다음 세션 시작 프롬프트

2026-10-31 작업만 마감했으며 **전체 작업은 진행 중**이다. CURRENT_SESSION_CONTEXT.md, 최신2026-10-31_progress.md와 설계26/학습21의19~29절 중 필요한 부분만 읽고 이어가라.

## 멈춘 지점

사용자 TRAN에서 고정30µs 검출 지연과 가정한 빠른 하강을 확인했고, 보호 부하 포함 ±0.1% OP 최대/최소 VADC2.37547/2.36724V를 확인했다. TMUX1511·STM32·TPS3840의 조건별 규격, 기준 계기/온도 오차, VIT−/VIT+·하강/복귀 지연을 학습했다.

마지막에는 TPS3840PL30의 VIT−/VIT+와 tP_HL/tD, 완전 OFF 시작의 tSTRT를 설명했다. VIT+를 넘는 즉시 RESET HIGH가 아니라 복귀 지연 후 HIGH다. 기존 두 점 보정/RC 설명을 반복하지 않는다.

## 다음 첫 작업

Nucleo의 실제 VDDA/VDD 전원 경로와 취출 지점을 확인하고, TPS3840PL30–TMUX1511 연결 초안의 MR/CT/SEL/디커플링·시작/하강/복귀 조건을 정리한다. 이후 후보 채택/남은 실측 조건 → 전체 ±0.10V 오차 예산 → 준비된 제작 회로도/ERC로 이어간다.

첫 작업은 문서/보드 회로도 대조다. 직전의 임의 PWL 기울기를 실제 하강 측정으로 간주하거나 더 많은 가정 실습으로 자동 확장하지 않는다. 실제 회로 초안은 VDDA→TPS3840PL30.VDD/TMUX1511.VDD, RESET→SEL1/2다. 전원 취출 경로는 미확인이며 기존 MCU NRST 연결 변경은 없다.

## 보존할 근거와 경계

- 회로 계산·부품 조건 검토 단계로 진행 중이다. 실제 VDDA 파형·무전원 핀 보호·전체 정확도·제작 회로도는 미완료다. 0.1% 저항은 비교 조건이며 구매 결정이 아니고, C2=100pF와 전원 하강 기울기는 학습용 가정이다. 제작 쉴드/MCU·빌드/플래시·실물·구매 변경 없이 기존 MVP PARTIAL/OPEN과 AI/배치 후속을 유지한다.
- 저장 모델03_10/11은30µs delay helper가 있는 비교 모델, 03_12/13은 ±0.1% 최대/최소 OP다. 공통 워크북에는 빠른 하강 TRAN/10.040ms 두 커서가 남아 있다. 회로도 이름과 분석 탭을 구분한다.
- K6.747204165, 공차 OP2.37547/2.36724V, 환산 +27.7924/−27.7536mV. 사용자 결과와 해석값 반올림 대조 완료.
- IPOFF10nA@25°C/VS≤3V와2µA@−40~125°C/VS≤3.6V는 다른 행이다. VDD=0/VD=0 시험을 중간 공급/MCU OFF 핀으로 확대하지 않는다.
- 저항 키트 TCR미상; 0.1% 구매 미결. UT210E 기준 한계와 실제 교정 불확도 구분. VREFINT 취득/실물 두 점 보정 미실시.
- C2=100pF는 총 ADC 입력 용량이나 최악 상한이 아닌 학습용이다. 스위치 지연55ns도 시스템 방전/전원 OFF 시간과 다르다.
- PB0 FT의 디지털 전압 내성을 ADC 모드에 그대로 적용하지 않는다. 로컬 STM DS10693 Rev10과 온라인 Rev11의 쪽 차이를 명시한다.

[학습21 · 19~29절](../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md) · [설계26](../../09_Electrical_Design/26_Voltage_ADC_Component_Conditions_and_Control_Draft_2026-10-31_ko.md) · [근거/저장 모델](../../assets/logs/pcb_design/2026-10-31_voltage_adc_closeout/README.md) · [10/31 마감](../progress/2026-10-31_progress.md) · [Notion 학습](https://app.notion.com/p/408a7326f87b8115b9aac4609cb40455)

## 작업 방식

사용자가 회로 작성·GUI 실행·펌웨어 입력/빌드/플래시·물리 조작을 수행한다. Codex는 목적·값의 출처·단위·식·시간 원점·데이터시트 판본/쪽/표/조건을 설명하고 결과를 검토한다. 명시 요청 없는 subagent/독자 시뮬레이션/완료 시험 반복 없음.

정리는 문서·진행상황·선택 Git/push·기존 Calendar 시간 보존·Notion 학습/진행 갱신까지다. 10/31 publication.json으로 게시 범위를 확인한다.
