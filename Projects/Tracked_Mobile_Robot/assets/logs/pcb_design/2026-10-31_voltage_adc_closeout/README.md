# 2026-10-31 전압 ADC 검토 마감 근거

**전체 작업 진행 중.** 사용자는 오늘 작업만 종료하고 모든 정리를 요청했다. 현재 단계는 회로 계산·부품 조건 및 전원 제어 연결 초안이다. 보호 성능/제작 쉴드/전체 MVP 완료가 아니다.

| 파일 | 근거의 성격 |
| --- | --- |
| [user_reported_results.md](user_reported_results.md) | 사용자 콘솔·화면·독해 보고의 선별 전사. 새 장비 원시 로그/PNG/CSV 아님 |
| [source_manifest.json](source_manifest.json) | 사용자 저장 회로4개·프로젝트4개·지연 helper·워크북의 SHA256 및 저장 속성/설정 |
| [calculate_comparisons.py](calculate_comparisons.py) / [calculations.json](calculations.json) | 해석식과 반올림 대조, SPICE/펌웨어 실행 없음 |
| [closeout_checks.json](closeout_checks.json) | 기존 파일 보존·링크·수치·문서 검사 범위 |
| [publication.json](publication.json) | Notion/Calendar 재조회 및 선택 Git/push 원격 확인 영수증 |

## 파일 상태

`03_10`은 1V/ms 검출 지연 모델, `03_11`은 25V/ms 비교, `03_12`/`03_13`은 보호 부하 포함 ±0.1% 최대/최소 OP다. 모두 S1 RON2Ω/Roff1GΩ와 C2=100pF, B1 비교식 및 고정30µs include를 유지한 학습 모델이다. 실제 TPS3840/TMUX1511 모델이 아니다.

공통 워크북에 저장된 TRAN은 `.tran 100n 10.1m 9.99m 100n`, VADC/VDDA 커서는 모두10.040ms다. 이것은 마지막 빠른 하강 비교의 설정이다. `03_12`/`03_13`을 열어 공차를 비교할 때는 OP 탭을 사용하며, 공통 워크북을 각 파일의 전용 실험 결과로 오해하지 않는다. 이번 마감에서는 원본 회로/워크북을 수정하거나 새 시뮬레이션을 실행하지 않았다.

이전10/30의 중간 저장본 이름 불일치와 정체 미확정 `.kicad_sch` 두 파일은 그대로 보존했다. 전체 연결/ERC 재검증을 수행했다는 주장은 하지 않는다.

## 판단과 재개

빠른 하강의 교차는 임의 조건의 결과이며 실제 전원 고장 증거가 아니다. 저항0.1%는 구매 결정이 아니고, IPOFF의25°C/전 온도 행과 STM 입력 모드·정격을 구분해야 한다. UT210E 설명서 한계만으로 ±0.10V 검증은 부족하다. 실제 VDDA 경로·전원 제어/복귀·부품 적용 조건과 전체 오차 예산은 남았다.

[설계26](../../../../09_Electrical_Design/26_Voltage_ADC_Component_Conditions_and_Control_Draft_2026-10-31_ko.md) · [학습21](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md) · [현재 재개점](../../../../docs/handoff/CURRENT_SESSION_CONTEXT.md) · [진행 기록](../../../../docs/progress/2026-10-31_progress.md).
