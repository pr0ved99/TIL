# NTC 분압과 RC — 사용자 GUI 실습

2026-10-28. [02_NTC.kicad_sch](02_NTC.kicad_sch) / [프로젝트](02_NTC.kicad_pro) / [워크북](02_NTC.wbk).

R3=10kΩ, R4=1kΩ, C3=100nF, V1 DC3.3V/AC1V. R7은 고정 저항으로 NTC의 명목 R-T 표를 모사하며 **최종 저장값은4147Ω(50°C 상당)**이다. 25°C 조건은10kΩ으로 변경해야 한다. 자동 온도 모델이나 실제 열응답 시험이 아니다.

| 조건 | 사용자 OP | 사용자 AC 커서 | 저장 원본 |
| --- | --- | --- | --- |
| 25°C 상당10kΩ | 1.65V,165µA | 1.19828Hz/−6.02069dB,265.258Hz/−9.0309dB,차이−3.01021dB | [PNG](NTC_25C_AC.png) · [CSV](NTC_25C_AC.csv) |
| 50°C 상당4147Ω | 967.35mV,233.265µA | 1Hz/−10.6586dB,404.834Hz/−13.6689dB,차이−3.01027dB | [PNG](NTC_50C_AC.png) · [CSV](NTC_50C_AC.csv) |

Req=1k+(10k||R7), A0=R7/(10k+R7). C3가 R4 뒤에 있으므로 시정수 계산에 R4를 포함한다.

AC 200 points/decade, 1Hz~1MHz. 전원 AC 입력의 전달 특성이며 NTC의 열응답은 아니다. 두 조건에서 I(C3)와 I(R4)의 DC 값은 모두0이다. OP 원문은 [사용자 보고](../../../../assets/logs/pcb_design/2026-10-28_simulation_closeout/user_reported_op.txt)에 저장했다.

[학습 노트](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md)에서 계산·해석·공급/보호 미결을 설명한다. 실물·센서 정확도·ADC 부하·공차·무전원 보호 검증은 미실행이다.
