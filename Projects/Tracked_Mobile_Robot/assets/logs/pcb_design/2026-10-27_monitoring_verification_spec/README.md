# 전류·온도 검증 명세 계산 근거

2026-10-27. 실측 데이터가 아닌 시험 설계 기준 v0.1의 명목 계산·원문 시각 대조 자료다.

- [전류 명세22](../../../../09_Electrical_Design/22_Current_Channel_Verification_Spec_2026-10-27_ko.md)
- [온도 명세23](../../../../09_Electrical_Design/23_Temperature_Channel_Verification_Spec_2026-10-27_ko.md)
- `calculate.py`: 기존 SEMITEC 명목 CSV를 읽어 전압점, 저항점, 민감도, 계기 사양 경계를 계산한다. 입력 원본의 SHA256을 남긴다.
- `calculations.json`: 설계 배분과 수치/한계. 부품 사양, 선택한 시험 기준, 실측을 구분한다.
- `current_voltage_points.csv`: 보정점·독립점·범위 확인점과 역할. 모든 행 NOT_RUN.
- `temperature_resistance_points.csv`: 제조사0~100°C 표13점과 오차 민감도. 보정형25°C는 독립 검증점에서 제외한다.
- `ut210e_dc_feasibility.csv`: 정지 DC 계기 사양만의 경계. 계기 교정 불확도나 PWM 성능이 아니다.
- `test_matrix.csv`: 기존 MON-L ID와이번 하위시험의 범위/준비상태.
- `run_template.json`: 실측 회차에 채울 형식. null은 미확보이며0으로 대체하지 않는다.
- `validate.py` / `validation.json`: 계산·문서 링크·현 CAD 해시 대조 결과.
- `notion_publication.json`: 전류/온도 두 명세의 Notion 생성·본문 재조회, 기존 학습 시작점 연결 기록.
- 원문 이미지2개: UT210E 범위별 digits/입력저항, SEMITEC103JT 열의 값 대조용.

저장소 루트에서 재현:

```powershell
C:/Espressif/tools/python/python.exe -X utf8 Projects/Tracked_Mobile_Robot/assets/logs/pcb_design/2026-10-27_monitoring_verification_spec/calculate.py
```

스크립트는 RT 절점 일치·역환산·방향성·판정 경계·보정/독립점 분리를 확인한다. 회로 시뮬레이션이나 MCU 펌웨어 실행/빌드/플래시는 하지 않는다. 새 실물 결과를 생성하지 않는다. 실제 조립/측정은 해당 명세의 준비 조건을 확인한 뒤 별도 회차로 수행한다.

이번 문서 작성이 MON-L01~08 PASS, 기존 MVP 인수 완료, PCB 제작 승인, 계측기 구매를 뜻하지 않는다.
