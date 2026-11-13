# 모니터링 입력 KiCad 실습

**현재 · 2026-11-14 마감:** 실습 A·B의 사용자 KiCad 원본과 CSV 후처리 결과를 확보했다. B는 VADC 뒤에 가상 잡음을 더해 평균의 효과를 관찰한 학습 모델이며, 실제 RC 잡음 억제·ADC 잡음 예산 검증이 아니다. 사용자가 B의 의미가 불분명하다고 밝혀 목적을 다시 설명했으며 수기·이해 완료는 미보고다. 다음은 B의 목적·결론을 짧게 연결해 확인한 뒤 기존 C(주기성 성분·alias) → 03_15 감지선 단락 실습 → 하네스·보호 정격 검토다. B 반복 실행이나 새 HTML/FFT 실습을 자동 추가하지 않는다.  [마감·재개 근거](../../../docs/progress/2026-11-14_progress.md).

**이전 · 2026-11-13:** [04 수집·평균 통합 실습](04_Sampling_and_Averaging/README.md)을먼저진행한다. 사용자A-1회로복사/입력설정안내단계,아직실행/CSV관측없음.03_15단락은이후로이동했다.

**이전 · 11/8 마감:** 14장 방전과37-2 입력 정착 사용자 관측을 완료했다. [03_14 회로·워크북/관측](../../../assets/logs/pcb_design/2026-11-07_input_settling_check/README.md)과 [완료 필기·두 노드 해석](../../../assets/logs/pcb_design/2026-11-08_learning_closeout/README.md)을 보존했다. 다음은37-2 이해 보완이며 새 실행을 요구하지 않는다. 03_14 PNG/CSV·1τ 관측은 미확인이다. 아래 미실행/준비 문구는 당시 이력이다.

**11/7 추가 실습 완료:** [14장 방전 정량 관측](../../../assets/logs/pcb_design/2026-11-07_discharge_check/README.md).03_09 사용자 실행의1τ/약99% 전압872.468678mV/23.8408803mV, 별도 워크북·PNG·CSV701행을 확인했다. CSV 출력 시간 반올림과 정밀 커서값을 구분한다. 다음은37-2 정상 ON 입력 정착을 위한 사용자03_14 복사본/입력원 설정이며 아직 실행하지 않았다. 아래 미확보 기록은 보완 전 이력이다.

## 최신 점검 — 2026-11-07

[40장 이전 실습 상태](../../../assets/logs/pcb_design/2026-11-07_pre40_practice_audit/README.md)를 대조했다.14장 방전 두 커서 전압의 정량 기록 보완과37-2 정상 ON 입력 정착 GUI 비교를 먼저 권고한다.36·38은 선택 수치 실습,37-4는40-2와 통합한다.30~35 문서 검토와 이후 완료한 회로도/ERC를 실습 누락으로 처리하지 않는다. 새 모델 작성/실행은 아직 하지 않았다.03의 공통 워크북은 빠른 하강용 설정으로 저장돼 있어 이전 방전 설정과 구분해야 한다. 아래 재개점은 각 작성 당시 기록이다.

## 현재 읽기 위치 — 2026-11-04

새 시뮬레이션 없이 [학습21](../../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md)의30~35절 전원/핀/상태/후보 판단을 작성했다. 다음36절 전체 전압 오차 예산이다. 최근 사용자 실습은10/31의03_10/11 검출 지연 TRAN과03_12/13 보호 부하 포함 공차 OP이며 [근거](../../../assets/logs/pcb_design/2026-10-31_voltage_adc_closeout/README.md)를 따른다. 학습 모델과 제작 쉴드를 구분한다.

## 이전 전압 실습 — 2026-10-30

전압 분압의 공차·보정·가정한1µA 누설과 일반 스위치 ON/OFF·VDDA 연동·C2 방전을 사용자 GUI에서 확인했다. ON/OFF VADC는2.37135V/123.143µV, 마지막 TRAN은701행과 지수형 하강을 관찰했다. 100pF·1V/ms·3V 무지연 감시는 학습용 가정이다. τ4.7µs/99%21.6443µs는 계산값이고 두 커서 전압은 미보고다. 실제 보호 성능·ADC 정확도·실물은 미검증이며 제작 쉴드/MCU/구매 변경과 새 시뮬레이션 실행은 없다. 기존 MVP PARTIAL/OPEN·AI/배치 후속을 유지한다.

[학습21](../../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md) · [근거](../../../assets/logs/pcb_design/2026-10-30_voltage_adc_closeout/README.md). 재개파일은03_Voltage_Divider/03_09_Voltage_ADC_Discharge_TRAN.kicad_sch. 최신TRAN은콘솔/화면보고근거이며이전PNG/CSV와구분한다. 아래10/28기록은기본실습이력이다.

학습 회차 2026-10-28 · 마감 2026-10-29. 사용자가 GUI에서 직접 작성·실행한 OP/AC/TRAN 결과다. **실물 NOT_RUN, 제작 쉴드와 별도 모델**이다. 01의 `reports/`는 학습 진행 방식 정정 전의 Codex 직접 DLL 실행 이력으로 구분한다.

| 폴더 | 설정·결과 | 상태 |
| --- | --- | --- |
| [01_Current_RC](01_Current_RC/README.md) | 12k/100nF, AC·계단/1τ·99% | 사용자 GUI 완료, PNG/CSV/워크북 저장 |
| [02_NTC](02_NTC/README.md) | 25°C·50°C 상당 저항 대입의 OP·전원 AC 응답 | 사용자 GUI 완료, 최종 회로 R7=4147Ω |
| [03_Voltage_Divider](03_Voltage_Divider/README.md) | 12k+12k/4.7k, 분압 노드100nF·이후1k, OP·AC | 기본OP/AC 완료. 추가 공차/누설/차단·방전TRAN은10/30 마감 |

[상세 학습 노트](../../../07_Embedded_Learning_Notes/01_Concept_Notes/20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md) · [설계 판단24](../../24_Monitoring_Input_Simulation_and_Design_Review_2026-10-28_ko.md) · [원본·검사](../../../assets/logs/pcb_design/2026-10-28_simulation_closeout/README.md).

03_09 저장 모델에서 실제 ADC 쪽 정전용량과 감지/차단 지연의 근거·적용 조건부터 정리한다. 이후 보호 구조에 맞는 환산비와 ±0.10V 오차 예산으로 복귀한다. 사용자 작성·실행을 Codex가 대신하지 않는다. 완료한 기본 실습을 자동 반복하거나 기존 스크립트로 사용자 회로를 재생성하지 않는다. 모델에는 실제 MCU ADC와 배선/서지/온도 오차가 없다.

`.wbk`는 분석 설정을 보존한다. 실제 결과는 PNG·세미콜론 CSV로 함께 저장했다. 프로젝트가 생성한 작은 `.kicad_pcb`는 부품을 배치하지 않은 빈 보드이며 제작용 PCB가 아니다. `.history`·백업·로컬 설정·잠금 파일은 게시하지 않고 로컬에 보존한다.
