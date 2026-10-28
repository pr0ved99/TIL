# 전압 분압과 RC — 사용자 GUI 실습

2026-10-28. [회로도](03_Voltage_Divider.kicad_sch) / [프로젝트](03_Voltage_Divider.kicad_pro) / [워크북](03_Voltage_Divider.wbk).

K1 Pin30 배터리 측과 Pin87 모터드라이버 공급 측을 각각 공통 GND 기준으로 관측할 두 채널의 **공통 한 채널 모델**이다. 실제 PA4/PB0 연결·두 채널 제작 결과가 아니다.

```text
VRAIL ─ R1 12k ─ R2 12k ─● VDIV
                         ├─ R3 4.7k ─ 0
                         ├─ C1 100nF ─ 0
                         └─ R4 1k ─ VADC (무부하)
```

| 사용자 실행 | 결과 |
| --- | --- |
| 분압만, DC12.6V | VDIV2.06341V,I439.024µA |
| 분압만, DC16V | VDIV2.62021V,I557.491µA |
| C1/R4 추가, DC16V | VDIV=VADC2.62021V,I(C1)=I(R4)=0A |
| AC, V1 DC16V/AC1V/0°,200 points/decade,1Hz~1MHz | 1Hz/−15.7157dB,404.942Hz/−18.7260dB,차이−3.01027dB |

[AC PNG](Voltage_Divider_AC.png) · [AC CSV](Voltage_Divider_AC.csv) · [OP 사용자 원문](../../../../assets/logs/pcb_design/2026-10-28_simulation_closeout/user_reported_op.txt).

C1이R4앞에 있고 ADC무부하이므로 Req=24k||4.7k≈3930.313589Ω, τ≈0.393031359ms, fc≈404.942098Hz다. A0=4.7/28.7≈0.163763066, G0≈−15.715681dB, 차단점≈−18.725981dB다. C를R4뒤로 옮기거나 ADC부하를 추가하면 이 계산을 다시 검토해야 한다.

16V에서12kΩ각각3.72956mW·4.7kΩ1.46074mW다. ±1%저항최악조합은출력2.57668~2.66433V이며, 무보정으로±0.10V목표달성은확인되지않았다. **다음은 공차·VDDA·누설·보정 오차 예산과 고장/무전원 보호 조건**이다. 전압 TRAN은 미실행이며 필요성에 따라 후속으로 판단한다.

[상세 학습 노트](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md) · [설계 판단](../../../24_Monitoring_Input_Simulation_and_Design_Review_2026-10-28_ko.md). 원래 제작 쉴드CAD·MCU·실물·구매 변경 없음, 제작용 아님.
