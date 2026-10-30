# 전압 ADC 보호 부품 조건·제어 연결 초안

2026-10-31 작업 마감. **진행 중 — 회로 계산·부품 조건 검토 단계**다. 실제 보호 회로 완성, 제작 쉴드 반영, 실물 검증을 의미하지 않는다. [설계25](25_Voltage_ADC_PowerOff_Review_2026-10-30_ko.md)의 후속이며 [학습21의 19절 이후](../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md#19-1031-추가-학습--검출과-차단-사이의-시간), [사용자 결과·저장 파일](../assets/logs/pcb_design/2026-10-31_voltage_adc_closeout/README.md), [진행 기록](../docs/progress/2026-10-31_progress.md)에 근거를 분리했다.

## 오늘 좁힌 판단

| 항목 | 오늘 확인한 범위 | 아직 확정하지 않은 것 |
| --- | --- | --- |
| 검출 지연 | 일반 모델에 고정 30µs를 추가한 사용자 TRAN | 실제 TPS3840의 모든 전원 파형에 대한 최대 지연 |
| 빠른 전원 하강 | 가정한 25V/ms에서 차단 전에 VADC>VDDA인 구간 | 실제 Nucleo 전원 하강 기울기·주입 전류·손상 여부 |
| 저항 공차 | 보호 구조를 포함한 ±0.1% 조합 OP 최대/최소 | 보유 키트의 실제 공차/TCR, 정밀 저항 구매 |
| TMUX1511 | RON·누설·무전원 누설의 조건별 규격 읽기 | 실제 전원 순서·저전압 구간·전체 보호 적합성 |
| STM32 ADC | PA4/PB0 핀 종류, 아날로그 입력 범위, VREFINT/오차 구분 | 무전원 핀 I–V, 실제 ADC 취득·보정·정확도 |
| 기준 계기 | UT210E 설명서의 DC 전압 정확도와 목표 비교 | 실물 교정 상태·상위 기준기 확보 |
| 제어 연결 | VDDA 감시 → TPS3840PL30 RESET → TMUX SEL 논리 초안 | 실제 보드 전원 취출점·MR/CT·미사용 채널·패키지·CAD/ERC |

## 보호 구조를 포함한 환산과 오차

공통 한 채널 모델은 R1/R2=12kΩ, R3=4.7kΩ, R4=1kΩ, R5=47kΩ, S1 RON=2Ω이다. C1=100nF는 VDIV–GND, C2=100pF는 VADC–GND 학습용 등가 용량이다. R5가 부하로 들어가므로 무부하 분압 계수 6.106383 대신 **K=6.747204165**를 쓴다.

- 명목 16V → VADC=2.371352579V.
- ±0.1% 출력 최대 조합: 사용자 OP 2.37547V, 해석식 2.375471679V, 명목 K 환산 오차 **+27.7924mV**.
- 최소 조합: 사용자 OP 2.36724V, 해석식 2.367239232V, 오차 **−27.7536mV**.
- RON만 2→4.5Ω으로 바꾸는 비교: 입력 환산 약−0.7702mV. 2Ω은 최소가 아닌 typical이므로 전체 공차 범위가 아니다.
- ON 누설 ±50nA를 ADC 노드의 단일 등가 전류로 놓는 비교: 약±0.2232mV ADC, ±1.5059mV 입력 환산. 서로 다른 단자 시험의 누설을 두 독립 전류로 중복 합산하지 않는다.
- 무전원 누설 10nA×47kΩ=0.47mV, 2µA×47kΩ=94mV는 단순 등가 계산이다. 제조사 시험은 출력 단자 0V 조건이고 MCU 무전원 I–V를 포함하지 않으므로 보호 PASS가 아니다.

±0.1%는 비교 시나리오다. 저렴한 저항 키트의 실제 TCR은 미상이며 0.1% 부품을 새로 사기로 결정하지 않았다. 보정으로 초기 비율 오차를 줄일 수 있어도 온도 변화·ADC 비선형성·기준 계기 오차는 남는다. UT210E의 20V 범위 설명서 한계는 12.6V에서 ±118.2mV, 16V에서 ±142mV이므로 이것만으로 전체 ±0.10V를 입증할 수 없다. 장비 구매/수령의 새 사실도 없다.

## 전원·제어 논리 초안

```text
실제 STM ADC 전원 VDDA ── TPS3840PL30.VDD
                       └─ TMUX1511.VDD
TPS3840PL30.RESET ───────── TMUX1511.SEL1 / SEL2 (= 실제 VCTRL 후보)

각 채널:
VRAIL ─ 12k ─ 12k ─ VDIV ─ 1k ─ TMUX Sx → Dx ─ VADC → STM ADC
                    ├─ 4.7k ─ GND                 └─ 47k ─ GND
                    └─ 100nF ─ GND
```

이는 **노드 역할의 초안**이다. 실제 Nucleo VDDA/VDD 필터·커넥터 취출 경로를 확인하기 전 두 전원을 임의로 묶지 않는다. 후보 관측 핀은 앞선 계약의 PA4/ADC1_IN4/CN7-32(TTa), PB0/ADC1_IN8/CN7-34(FT)이며 실제 결선 지시가 아니다. PB0의 디지털 FT 성질을 ADC 모드 허용 전압으로 확대하지 않는다.

PL은 정상 HIGH/저전압 LOW인 push-pull active-low RESET이며 TMUX는 SEL HIGH=ON, LOW=OFF다. 별도 V2 전원으로 제어하는 구조가 아니다. RESET을 여기서는 스위치 제어에 사용하며 MCU NRST에 새로 연결한다는 결정도 아니다. TPS 출력 HIGH/LOW와 TMUX 입력 기준의 비교는 유효한 공급·부하 시험 조건 안의 논리 호환성 확인일 뿐 전원 순서 보증은 아니다.

TPS의 MR/CT와 전원 디커플링, TMUX 미사용 채널·SEL 기본 상태, VDDA 복귀 후 측정값 유효화는 후속이다. CT를 비워 두어도 복귀 지연이 0이 아니다. TMUX 내부 SEL 풀다운 6MΩ은 ADC 노드의 R5 47kΩ과 역할이 다르다. C2=100pF를 실제 PCB 부품으로 추가하기로 정하지 않았다.

## 마지막 학습 지점: VIT− / VIT+ / RESET

- VIT−: 전압이 **내려갈 때** 저전압으로 판단하는 경계. 음수 전압이라는 뜻이 아니다.
- VIT+: 전압이 **올라갈 때** 복귀 조건을 만족하는 경계. PL30의 명목값은 각각 3.0V와 3.1V이며 공차가 있다.
- 하강: VIT− 통과 → tP_HL → RESET LOW → 스위치 OFF.
- 복귀: VIT+ 통과 → tD 대기 → RESET HIGH → 스위치 ON. 경계에서 즉시 HIGH가 되는 것은 아니다.
- 완전 무전원에서 시작하는 tSTRT와 이미 동작 중인 복귀 tD는 구분한다. CT-open의 tD를 tSTRT에 중복 가산하지 않는다.

사용자는 tP_HL과 tD의 두 방향 의미를 데이터시트에서 확인했다고 보고했고, VIT−와 히스테리시스 의미를 추가 설명했다. 이 학습 확인을 실물 보호 완료로 표시하지 않는다.

## 데이터시트 읽기 위치

페이지는 문서 인쇄 쪽 번호다. 다른 판본은 제목·행을 함께 대조한다.

| 자료 | 읽을 위치 | 적용 조건과 주의 |
| --- | --- | --- |
| [TI TPS3840 SNVSB03E Rev.E, 2026-05](https://www.ti.com/lit/ds/symlink/tps3840.pdf) | p3 출력 변형, p4 §5 핀, p6 §6.5 VIT−/VHYS/VOH/VOL, p7 §6.6 tP_HL/tD/tSTRT와 각주, p9 Fig6-2 | tP_HL typ15/max30µs는 지정 전압 스텝·CL10pF·slew 조건. CT-open tD nominal50µs; startup100/220/350µs와 중복 가산 금지 |
| 같은 TPS3840 | p18 §7.3.2 CT, p19–20 §7.4 전원 상태, p28 §8.3/8.4 디커플링, p30 Table9-2 PL30 | 명목 VIT−3.0V·히스테리시스100mV. 출력 보증 최저 전압도 부하·slew 조건이 있음 |
| [TI TMUX1511 SCDS390B Rev.B, 2025-03](https://www.ti.com/lit/ds/symlink/tmux1511.pdf) | p3 핀, p4 §5.3, p6 §5.5 RON/IS(ID)/IPOFF/VIH/VIL, p7 tTRAN | RON typ2/max4.5Ω. IPOFF ±10nA는 VDD=0, VS≤3V, TA25°C; ±2µA 행은 VS≤3.6V, −40~125°C. 두 행 모두 VD=0 |
| 같은 TMUX1511 | p14 Fig6-3 누설 시험, p15 Fig6-5 전이, p22 §7.3.4–7.5 및 Table7-1, p26 전원 | 정상 OFF·ON·전원 OFF를 구분. VDD=0 규격으로 0~1.5V 구간 전체를 보증하지 않음 |
| [로컬 STM32F446 DS10693 Rev10, 2021-01](../assets/stm32f446mc.pdf) | p44/47/48 Table9/10 핀, p72 Table13, p73 Table14/각주, p75 Table16, p139 Table74, p140 Table75, p145 Tables83/84 | 절대 최대·정상 입력·ADC 변환 범위를 구분. [온라인 Rev11](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)은 관련 후반 표가 대체로 1쪽 뒤 |
| [ST AN4899 Rev4, 2026-05](https://www.st.com.cn/resource/en/application_note/an4899-guidelines-for-gpio-hardware-settings-and-lowpower-consumption-on-stm32-mcus-stmicroelectronics.pdf) | p12 Fig2, p19 §5.2.2, p26 §6.3 | 아날로그 기능 사용 시 FT 일반화 금지, 무전원 전압은 개별 MCU 조건 우선 |
| [UNI-T UT210E 설명서 MAY2018 REV2](../assets/datasheets/UNI-T_UT210E_User_Manual.pdf) | PDF p2 IX Technical index → 1 DC voltage → 20.00V 행 | 분해능10mV, ±(0.7% reading+3digits), 23±5°C·RH<75%·1년 조건 |

## 다음 재개 순서와 완료 조건

1. **먼저 실제 Nucleo VDDA/VDD 경로와 취출 가능 지점을 문서/회로도로 대조한다.** 감시기와 TMUX가 어느 전원을 실제로 공유할지 결정 근거를 남긴다.
2. MR/CT/SEL/미사용 채널/디커플링과 시작·하강·복귀·완전 OFF 조건표를 완성한다. 정상 동작 영역 밖에서 보장이 끊기는 구간을 명시한다.
3. 실제 전원 파형·총 용량·출력 정착과 ADC 취득에 필요한 검증을 정한다. 필요가 명확한 새 모델만 사용자 GUI로 실행한다. 임의 하강 기울기 비교를 실제 고장 증거로 반복하지 않는다.
4. 후보 보호 구조의 채택/보류를 결정한 뒤 전체 ±0.10V 오차 예산과 부품 근거를 정리하고, 준비된 것만 두 전압 채널의 제작 회로도/ERC로 옮긴다.

전체 오차 예산·실물 무전원 보호·제작 회로도/ERC·PCB는 미완료다. 전류/NTC 전원 순서도 최종 검토가 남는다. MCU 코드·빌드/플래시·배선·구매 변경은 없고, 기존 MVP PARTIAL/OPEN 및 AI/배치 후속 순서를 유지한다.
