# 전압 분압과 RC — 사용자 GUI 실습

## 최신 — 2026-10-30 차단·방전 실습 마감

다음에 열 회로는 [03_09_Voltage_ADC_Discharge_TRAN.kicad_sch](03_09_Voltage_ADC_Discharge_TRAN.kicad_sch)다. B1 VDDA연동·V3 PWL·C2=100pF가 저장되어 있다. [워크북](03_Voltage_Divider.wbk)의TRAN은 `.tran 100n 10.35m 10.28m 100n`이며, 기존OP/AC탭은각회차이력이다. 워크북커서시각은실측전압기록이아니다.

사용자ON/OFF2.37135V/123.143µV와전원연동/방전그래프·701행로그를확인했다. 100pF·1V/ms·3V무지연감시는학습용가정,실제부품최악보증아님. 다음은실제입력용량/차단지연근거와전체오차예산이다.

### 저장된 파일명과 실제 조건 대조

공통접미사는 `.kicad_sch`이며파일을마감중수정하지않았다. 아래는netlist읽기검사이고시뮬레이션재실행이아니다.

| 파일 접두사 | 실제 저장 조건 | 해석 |
| --- | --- | --- |
| 03_Voltage_Divider | 12k/12k/4.7k,16V | 기본 명목회로 |
| 03_01_Voltage_Divider_Tolerance_Max_OP | 11.88k/11.88k/4.747k,16V | ±1% 출력 최대 |
| 03_01_01…0p1pct_Max | 12.12k/12.12k/4.653k,16V | **이름 불일치: ±1% 출력 최소** |
| 03_02…Tolerance_Min | 12.12k/12.12k/4.653k,16V | ±1% 출력 최소 |
| 03_03…0p1pct_Max | 12.12k/12.12k/4.653k,16V | **이름 불일치: ±1% 출력 최소** |
| 03_04…0p1pct_Min | 11.988k/11.988k/4.7047k,16V | **이름 불일치: ±0.1% 출력 최대** |
| 03_05…Leakage_OP | 명목+VADC→0의1µA | 누설 가정 |
| 03_06…Isolation_OP | V2=3.3V,S1/R5 | ON 저장본;OFF결과는대화보고 |
| 03_07…PowerDown_Baseline_TRAN | V2=3.3V, **V3 없음** | baseline 준비 이전 저장 상태 |
| 03_08…UV_Control_TRAN | V3 PWL+V2=3.3V | **B1 없는 고정ON baseline** |
| 03_09…Discharge_TRAN | V3+B1+C2=100pF | 최신 재개 모델 |

0.1% Min과12.6V보정OP의사용자보고는대화기록으로보존한다. 그실험상태가동명파일에저장되었다고주장하지않는다. 파일명변경/원본재생성은하지않았다. `.kicad_sch`와`.kicad_sch.kicad_sch`라는정체미확정로컬파일도정리대상에서제외했다.

참조: [학습21](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md) · [원본/해시/netlist](../../../../assets/logs/pcb_design/2026-10-30_voltage_adc_closeout/README.md).

## 이전 기본 OP/AC — 2026-10-28

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

16V에서12kΩ각각3.72956mW·4.7kΩ1.46074mW다. ±1%저항최악조합은출력2.57668~2.66433V이며, 무보정으로±0.10V목표달성은확인되지않았다. 이후 공차·누설·차단·방전 실습은 본문 상단10/30 기록을 따른다. 이 절은10/28 기본회로 이력이다.

[상세 학습 노트](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md) · [설계 판단](../../../24_Monitoring_Input_Simulation_and_Design_Review_2026-10-28_ko.md). 원래 제작 쉴드CAD·MCU·실물·구매 변경 없음, 제작용 아님.
