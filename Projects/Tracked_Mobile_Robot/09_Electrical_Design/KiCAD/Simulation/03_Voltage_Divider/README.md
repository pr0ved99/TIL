# 전압 분압과 RC — 사용자 GUI 실습

**현재 · 2026-11-14 마감:** 실습 A·B의 사용자 KiCad 원본과 CSV 후처리 결과를 확보했다. B는 VADC 뒤에 가상 잡음을 더해 평균의 효과를 관찰한 학습 모델이며, 실제 RC 잡음 억제·ADC 잡음 예산 검증이 아니다. 사용자가 B의 의미가 불분명하다고 밝혀 목적을 다시 설명했으며 수기·이해 완료는 미보고다. 다음은 B의 목적·결론을 짧게 연결해 확인한 뒤 기존 C(주기성 성분·alias) → 03_15 감지선 단락 실습 → 하네스·보호 정격 검토다. B 반복 실행이나 새 HTML/FFT 실습을 자동 추가하지 않는다.  [마감·재개 근거](../../../../docs/progress/2026-11-14_progress.md).

**이전 우선순위:** 사용자가미뤄진37-4/40-2실습부터요청했다. [04폴더통합실습](../04_Sampling_and_Averaging/README.md)을먼저하고03_15단락은이후다.03_14는원본으로보존한다.

**이전 · 2026-11-13:** 사용자 요청으로 [감지 케이블 단락 실습](03_15_Sense_Cable_Short_Lab_ko.md)을 추가했다. 정상→단락→복귀를03_14복사본에서 구성하는 안내 단계이며 새03_15회로/워크북 저장·실행·관측은 아직 확인 전이다. 기존03_14자료는 보존한다.

## 최신 — 2026-11-08 입력 정착·필기 마감

[03_14 회로](03_14_Voltage_ADC_InputSettling_TRAN.kicad_sch) / [워크북](03_14_InputSettling_Check_2026-11-07.wbk)의분석5와 사용자 커서3.680ms/2.36985654V,3.690ms/약2.36990V를 확인했다. 입력 변화 시작1.000ms 기준2.680~2.690ms 사이에 입력 환산 잔차10mV를 만족한다. [원본 조건/전사](../../../../assets/logs/pcb_design/2026-11-07_input_settling_check/README.md) · [완료 필기/두 노드 계산](../../../../assets/logs/pcb_design/2026-11-08_learning_closeout/README.md).

V1 PWL은`0 0 1m 0 1.001m 16 6m 16`,V3는고정3.3V,TRAN은`.tran 1u 6m 0 100n`. 다음은 C1 근사/C2 포함 모델과VADC 전류식 복습이다. 03_14 PNG/CSV 내보내기·1τ 커서 관측은 미확인이며 새 실행/실물 검증을 했다고 기록하지 않는다. 아래는 이전 이력이다.

## 최신 — 2026-11-07 방전 정량 보완

사용자가03_09를 실행해1τ/약99% 지점의 VADC872.468678mV/23.8408803mV를 관측했다. [워크북](03_09_Discharge_Check_2026-11-07.wbk) 분석4의TRAN과 두 커서 위치, [PNG](03_09_Discharge_Check_2026-11-07.png), [CSV](03_09_Discharge_Check_2026-11-07.csv)701행을 확인했다. 워크북의 분석3은 이전 빠른 하강 설정으로 구분한다. CSV의 시간 반올림 한계와 커서 원문은 [검증 기록](../../../../assets/logs/pcb_design/2026-11-07_discharge_check/README.md)에 남겼다. 기존 두 커서 전압 미보고를 이번 관측으로 보완했으며 아래는 과거 이력이다. 다음은37-2 정상 ON 입력 정착의 새 복사본 준비다.

## 최신 — 2026-10-31 부품 조건·제어 초안 검토 마감

[설계26](../../../26_Voltage_ADC_Component_Conditions_and_Control_Draft_2026-10-31_ko.md) · [학습21 19~29절](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md) · [오늘 근거/해시](../../../../assets/logs/pcb_design/2026-10-31_voltage_adc_closeout/README.md).

| 저장 회로(.kicad_sch) | 저장 값 / 사용자 결과 |
| --- | --- |
| 03_10_Voltage_ADC_DetectDelay_TRAN | V3 10~13.3ms에3.3→0V(1V/ms), VTRIP→VCTRL 고정30µs. 사용자 전이 약10.300/10.330ms |
| 03_11_Voltage_ADC_FastFall_TRAN | V3 10~10.132ms(25V/ms). 사용자10.040ms에서 VADC2.37135258V/VDDA2.3V |
| 03_12_Voltage_ADC_Loaded_Tolerance_Max_OP | R1/2=11988,R3=4704.7,R4=999,R5=47047Ω. 사용자 OP VADC2.37547V |
| 03_13_Voltage_ADC_Loaded_Tolerance_Min_OP | R1/2=12012,R3=4695.3,R4=1001,R5=46953Ω. 사용자 OP VADC2.36724V |

네 회로 모두 일반 스위치 ron2/roff1G, B1 비교, C1=100nF(VDIV), C2=100pF(VADC), [고정 지연 helper](detector_delay_30us.cir)를 사용한다. 실제 TPS3840/TMUX 제조사 모델이 아니다. 원본 회로는 마감 중 수정하지 않았다.

공통 워크북의 현재 TRAN은 `.tran 100n 10.1m 9.99m 100n`, VADC/VDDA 커서 둘 다10.040ms다. 03_12/13은 OP를 선택한다. 과거 AC/TRAN 설정이 모든 파일에 맞는 것은 아니며 새 실행은 하지 않았다.

다음은 반복 실습이 아니라 실제 보드 VDDA/VDD 전원 경로와 후보 부품의 MR/CT/SEL/전원 순서 검토다. 임의 하강 조건은 실제 고장 증거가 아니고 0.1%는 구매 결정이 아니다. 아래10/30 재개점은 당시 이력이다.

## 이전 — 2026-10-30 차단·방전 실습 마감

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
