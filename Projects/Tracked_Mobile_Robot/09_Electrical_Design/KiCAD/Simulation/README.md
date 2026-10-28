# 모니터링 입력 KiCad 실습

학습 회차 2026-10-28 · 마감 2026-10-29. 사용자가 GUI에서 직접 작성·실행한 OP/AC/TRAN 결과다. **실물 NOT_RUN, 제작 쉴드와 별도 모델**이다. 01의 `reports/`는 학습 진행 방식 정정 전의 Codex 직접 DLL 실행 이력으로 구분한다.

| 폴더 | 설정·결과 | 상태 |
| --- | --- | --- |
| [01_Current_RC](01_Current_RC/README.md) | 12k/100nF, AC·계단/1τ·99% | 사용자 GUI 완료, PNG/CSV/워크북 저장 |
| [02_NTC](02_NTC/README.md) | 25°C·50°C 상당 저항 대입의 OP·전원 AC 응답 | 사용자 GUI 완료, 최종 회로 R7=4147Ω |
| [03_Voltage_Divider](03_Voltage_Divider/README.md) | 12k+12k/4.7k, 분압 노드100nF·이후1k, OP·AC | 사용자 GUI 완료, 전압 TRAN 미실행 |

[상세 학습 노트](../../../07_Embedded_Learning_Notes/01_Concept_Notes/20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md) · [설계 판단24](../../24_Monitoring_Input_Simulation_and_Design_Review_2026-10-28_ko.md) · [원본·검사](../../../assets/logs/pcb_design/2026-10-28_simulation_closeout/README.md).

다음은 전압 정확도 오차 예산·보정/기준 전압·누설과 고장/무전원 보호 조건이다. 사용자 작성·실행을 Codex가 대신하지 않는다. 완료한 기본 실습을 자동 반복하거나 기존 스크립트로 사용자 회로를 재생성하지 않는다. 모델에는 실제 MCU ADC와 배선/서지/온도 오차가 없다.

`.wbk`는 분석 설정을 보존한다. 실제 결과는 PNG·세미콜론 CSV로 함께 저장했다. 프로젝트가 생성한 작은 `.kicad_pcb`는 부품을 배치하지 않은 빈 보드이며 제작용 PCB가 아니다. `.history`·백업·로컬 설정·잠금 파일은 게시하지 않고 로컬에 보존한다.
