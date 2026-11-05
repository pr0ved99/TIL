# 전압 ADC 실습 마감 근거 — 2026-10-30

저항 공차/보정·누설·일반 스위치 ON/OFF·VDDA 연동·C2 방전까지의 사용자 실습을 마감한다. 실제 수행 시작/종료 시각은 추정하지 않는다. 이 폴더는 실물 또는 실제 보호 IC의 성능 PASS 자료가 아니다.

## 근거의 종류

| 파일 | 출처와 범위 |
| --- | --- |
| [user_discharge_tran_console.txt](user_discharge_tran_console.txt) | 사용자 첨부 텍스트 원본을 바이트 그대로 복사. 성공 TRAN 701행, 초기 동작점 포함. 파형 데이터 자체가 아님 |
| [user_reported_results.md](user_reported_results.md) | 대화 속 OP/계산 보고와 화면 관찰을 전사한 기록. 원본 CSV나 자동 측정 결과가 아님 |
| [source_manifest.json](source_manifest.json) | 저장된 회로11개/프로젝트11개·워크북/첨부 원본 SHA256, 내보낸 netlist와 워크북 설정 |
| [netlists/](netlists/) | KiCad CLI가 현재 저장 회로에서 내보낸 SPICE 연결. 마감 중 시뮬레이션 실행 없음 |
| [calculations.json](calculations.json) | 저항망/공차/누설/방전의 해석식 재계산. 시뮬레이터 출력과 구분 |
| [publication.json](publication.json) | 이번 Git·Notion·Calendar 반영과 readback 영수증 |

최종 TRAN 화면은 대화 첨부로 관찰했다. 해당 첨부 폴더에는 텍스트 하나만 있어 화면 PNG 원본이나 파형 CSV를 이 폴더에 만들지 않았다. 이전10/28 AC PNG/CSV는 기존 실습 폴더에 보존한다.

## 저장 모델 감사에서 발견한 차이

파일 이름을 근거로 실험 조건을 확정하지 않는다. 실제 연결/값은 [실습 README](../../../../09_Electrical_Design/KiCAD/Simulation/03_Voltage_Divider/README.md)의 대조표와 manifest를 따른다.

- `03_01_01`, `03_03`은 이름의0.1% Max와 달리 ±1% 출력 최소값이다.
- `03_04`는 이름의0.1% Min과 달리 ±0.1% 출력 최대값이다.
- `03_07`은 V3가 없고, `03_08`은 V3와 고정V2가 있는 baseline이다.
- **03_09만 B1 연동·V3·C2=100pF가 함께 저장되어 있으며 다음 재개 파일이다.**

사용자 원본 회로/프로젝트/워크북은 마감 중 수정하지 않았다. 기록된 실험과 최종 저장 파일의 차이를 없애려고 과거 파일을 재생성하지 않는다. 워크북의 두 커서는 시각만 저장되어 있어 전압 관측값의 증거가 아니다.

## 확인과 미결

사용자 ON/OFF OP는2.37135V/123.143µV, VDDA 연동 화면과 C2 방전 화면·콘솔701행을 확인했다. 100pF·1V/ms·3.0V 무지연 감시는 학습용 가정이다. τ4.7µs와99%21.6443µs는 계산값이며 두 커서 전압의 정량 보고는 없다. 실제 보호 IC·MCU OFF 안전/정확도·보드 시험은 미완료다.

다음은 **실제 ADC 쪽 용량과 감지/차단 지연의 근거·적용 조건 정리**, 이후 변경된 입력계의 ±0.10V 예산이다. [학습21](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md) · [설계25](../../../../09_Electrical_Design/25_Voltage_ADC_PowerOff_Review_2026-10-30_ko.md) · [마감 진행](../../../../docs/progress/2026-10-30_progress.md).
