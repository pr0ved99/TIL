# 배터리 전압 측정 회로의 제조사 근거와 프로젝트 적용 범위

**11/23 재개점.** 가상 TMR 주행 평가를 마쳤고 SIM-06 모의 전압 감시를 진행 중이다. 집에서는 NUCLEO-F446RE의 단일 ADC 시험 준비(A11)부터 진행한다. [현재 인수인계](../docs/handoff/CURRENT_SESSION_CONTEXT.md)

**11/17 마감 이력:** 보호 저항의 목적은 합선 판별이 아닌 전류 제한이다. 지속 단락 정격/설치 조건을 확인하고 TCR는 오차 상한 비교로 검토 깊이를 제한한다. 보유24AWG는 실리콘 피복 연선이라는 사용자 보고를 반영했다. 내부1TB SSD 절반을 Ubuntu 듀얼부팅에 배정할 계획이며11/19 백업·점검→조건 충족 시11/20 전환을 권고한다. PCB와 가상 IMU/LiDAR·odom/TF·Nav2를 병행하고 RL은 기준선 이후 선택적으로 비교한다. 새 설치/구현·실측 완료는 아니다. [새 단계·일자별 계획](../docs/plans/2026-11-17_Ubuntu_Nav2_Simulation_and_RL_Roadmap_ko.md) · [11/17 기록](../docs/progress/2026-11-17_progress.md) · [검증/게시](../assets/logs/planning/2026-11-17_ubuntu_nav2_closeout/README.md). 아래 날짜별 설명은 당시 범위다.

2026-11-15 작성. 사용자 요청에 따라 배터리 전압을 저항 분압·필터·MCU ADC로 측정하는 방식의 근거를 정리한다. **기본 측정 구조는 제조사 레퍼런스에서도 사용된다. 출발점 보호 저항과 TPS/TMUX 전체 조합은 프로젝트 조건에 맞춘 추가 설계이며, 아래 사례가 그 조합 전체의 검증을 대신하지 않는다.**

## 1. 목적과 근거 구분

- 제조사 자료에서 확인한 사실: 공개 레퍼런스의 분압 저항, 필터, MCU 입력과 ADC 설계 지침.
- 프로젝트 사실: 제작용 Shield에는 전압 두 채널이 있고, 실습03_15에서 출발점2.2kΩ 유무를 비교했다. 새 출발점 저항은 제작 CAD/BOM에 아직 없다.
- 계산/가정: 아래 명목 분압식은 저항 공차·입력 누설·부하·기준전압 오차를 생략한 설명이다. 최종 회로는 전체 저항망으로 계산한다.
- 검증 경계: 실제 ADC 잡음·보정 잔차·전원 전이·고장 보호·온도 상승/파손은 미검증이다. 배터리 팩 전압 측정과 셀별 BMS/잔량 추정은 같은 기능이 아니다.

## 2. 제조사 레퍼런스 읽는 위치

### 2-1. ST Drone Kit: 회로와 환산 코드가 함께 있는 예제

문서: **Getting Started with ST Drone Kit, v0.97**, 슬라이드 표기65쪽 **Battery voltage monitoring**. 발표 자료의 버전 표기를 사용하며 별도 데이터시트 개정 번호를 만들어 붙이지 않는다. [공식 PDF, 65쪽](https://www.st.com/content/ccc/resource/sales_and_marketing/presentation/product_presentation/group0/bd/cc/11/15/14/d4/4a/85/STEVAL-DRONE01_GETTING_STARTED_GUIDE/files/steval-drone01_getting_started_guide.pdf/jcr:content/translations/en.steval-drone01_getting_started_guide.pdf#page=65).

| 확인할 항목 | 문서의 구성 | 프로젝트에서 참고할 점 |
| --- | --- | --- |
| 상단 R14 / 하단 R15 | 10kΩ / 20kΩ | 입력 범위에 맞춘 저항 분압 |
| C34 | 100nF, 감지 노드와 기준 GND 사이 | ADC 입력의 필터/전하 저장 |
| VBAT_SENSE | STM32F401 PB1, ADC1 채널9 | 분압된 전압을 일반 ADC 채널로 취득 |
| 예제 코드 | ADC 코드→핀 전압→분압 역환산 | 핀 전압과 원래 배터리 전압을 구분 |

적용 조건: STEVAL-DRONE01 키트의 배터리는 공칭3.7V/600mAh LiPo다. [ST 데이터 브리프 DB3749 Rev 2, 2018-11, 1쪽 Features](https://www.st.com/resource/en/data_brief/steval-drone01.pdf#page=1). 이 저항비를 프로젝트의16V 입력에 그대로 쓰지 않는다. 예를 들어16V에 적용하면 명목 출력이10.67V이므로3.3V급 ADC 입력에 맞지 않는다.

### 2-2. STEVAL-ESC001V1: 모터 구동 배터리 전압 감지 사례

문서: **UM2197 Rev 3, November 2021**, Electronic speed controller for BLDC and PMSM three phase brushless motor. [공식 PDF](https://www.st.com/resource/en/user_manual/um2197-electronic-speed-controller-for-bldc-and-pmsm-three-phase-brushless-motor-stmicroelectronics.pdf).

| 위치 (인쇄 쪽 = PDF 쪽, 1부터 계산) | 확인 대상 |
| --- | --- |
| 2쪽 §1 Main features | 3S~6S LiPo 사용, 명목11.1~22.2V. 명목 전압을 만충 최대전압으로 해석하지 않는다. |
| 16쪽 §4 Figure 17, 전압 감지 부분 | R62/R68 분압과 VBUS 감지 경로 |
| 19쪽 §5 BOM 항목60·63 | R62=169kΩ±1%, R68=18kΩ±1% |
| 14쪽 Figure15 / 8쪽 Table1 PB13 행 | STM32F303에 연결되는 VBUS 신호 |

부하를 생략한 명목 분압을16V 입력에 계산하면:

$$
V_{sense}=16V\frac{18k\Omega}{169k\Omega+18k\Omega}\approx1.5401V
$$

이 값은 문서 부품값으로 계산한 예시이며 해당 보드의 실측값이 아니다. 모터 전원 감지에도 분압→MCU 입력이라는 구조를 사용한다는 근거다. STM32F303과 프로젝트의F446는 ADC 세부 특성이 다르므로 샘플링 설정을 복사하지 않는다.

### 2-3. STM32 ADC 입력 조건: 왜 저항·커패시터·취득 시간을 함께 보는가

문서: **AN2834 Rev 10, October 2024**, How to optimize the ADC accuracy in the STM32 MCUs. **16쪽 §3.2.7, Effect of the analog signal source resistance**. [공식 PDF, 16쪽](https://www.st.com/resource/en/application_note/an2834-how-to-optimize-the-adc-accuracy-in-the-stm32-mcus-stmicroelectronics.pdf#page=16).

신호원 저항과 ADC 내부 스위치 저항은 내부 샘플링 커패시터 충전에 영향을 준다. 따라서 분압 출력이 범위 안에 있다는 사실만으로 정확도가 확보되지는 않는다. 분압망의 소스 저항, 외부 커패시터, 취득 시간을 해당 MCU 데이터시트 조건과 함께 검토한다. 이 문서의 내부 샘플링 커패시터는 실습의 외부 C1/C2와 다른 요소다. F446의 수치 조건은 기존 [설계25](25_Voltage_ADC_PowerOff_Review_2026-10-30_ko.md), [설계26](26_Voltage_ADC_Component_Conditions_and_Control_Draft_2026-10-31_ko.md)의 판본/조건 구분을 따른다.

## 3. 기본 원리와 우리 회로의 차이

일반적인 공통 GND 분압의 명목식은 다음과 같다.

$$
V_{ADC}=V_{BAT}\frac{R_{bottom}}{R_{top}+R_{bottom}},\qquad
V_{BAT}=V_{ADC}\frac{R_{top}+R_{bottom}}{R_{bottom}}
$$

ADC 코드에서 핀 전압으로 바꾸는 단계에는 ADC 기준전압·분해능·전달특성이 추가된다. 위 식은 분압 관계만 나타낸다. 코드 환산의4095/4096 표기 관행을 곧바로 정확도 보증으로 사용하지 않는다.

프로젝트의 정상 ON 저항망에는24kΩ,4.7kΩ,직렬1kΩ,TMUX ON저항,ADC측47kΩ이 함께 있다. 따라서 단순24kΩ/4.7kΩ 분압만으로 계산하지 않는다. 출발점 Rp까지 추가하면:

$$
R_B=4.7k\Omega\parallel(1k\Omega+2\Omega+47k\Omega)
$$

$$
V_{ADC}=V_{source}\frac{R_B}{R_p+24k\Omega+R_B}\frac{47k\Omega}{1k\Omega+2\Omega+47k\Omega}
$$

여기서2Ω은 정상 ON 비교에 사용한 모델값이다. 제조사 최대값/온도 의존성까지 포함한 최악조건 계산은 별도다. [설계30 §5](30_Voltage_Sense_Branch_Protection_Comparison_2026-11-13_ko.md#5-정상-측정-계산--출발점-저항도-분압에-포함된다)의 Rp=2.2kΩ 명목 결과는16V→2.200196738V, K=7.272076958이다. 실습03_15는 추가 가상 전원저항 R6=1Ω 및 스위치 누설을 포함하므로16V 이상 전원 기준 VADC≈2.200120V로 조금 다르다.

## 4. 기본 측정과 추가 보호의 역할 분리

| 기능 | 프로젝트 구성/검토안 | 근거와 적용 범위 |
| --- | --- | --- |
| ADC 범위로 축소 | 저항 분압 | 위 ST 레퍼런스와 같은 기본 방식. 입력 최대값·공차·누설·부하 반영 필요 |
| 필터/정착 | C1 및 ADC측 회로 | RC 학습/ADC 설계 지침과 연결. 실제 PWM 잡음 억제 성능은 미측정 |
| MCU 무전원·전원 전이 | TPS3840/TMUX1511/방전 경로 | 프로젝트 별도 설계25·26. 위 레퍼런스 전체와 동일한 회로라고 주장하지 않음 |
| 외부 감지선 단락 전류 제한 | 출발점 직렬 Rp=2.2kΩ 후보 | 실습03_15/설계30. 실습R7과 제작 Shield의R7은 서로 다른 reference |
| 포트 ESD·역극성·오접속·과도 | 후속 조건/보호 검토 | 분압 또는 Rp 하나로 모두 해결됐다고 판단하지 않음 |

Rp는 보호하려는 감지 케이블의 출발점 가까이에 둬야 한다. Rp 앞 구간은 그 저항으로 보호되지 않으므로 짧은 접속·절연·고정이 필요하다. 주전류 공급선에2.2kΩ을 넣는 제안이 아니다. 두 감지 분기는 서로 독립적으로 보호한다.

## 5. 이번 실습이 보탠 근거

[03_15 실습 결과](KiCAD/Simulation/03_Voltage_Divider/03_15_Sense_Cable_Short_Lab_ko.md)의 약9ms 저장값:

| 항목 | Rp=2.2kΩ 있음 | Rp 없음 |
| --- | --- | --- |
| 공급 전류 | 7.26612mA | 8.00014A |
| VRAIL | 15.9927V | 7.99986V |
| PCB 분압 전류 I(R1) | 0.255353µA | 282.871µA |
| 저항 소비 전력 | Rp=0.116152W | R6=64.0023W |

R6=1Ω,접촉 S2의ON저항1Ω은 가상 조건이다. 8A가 전부 PCB 분압 경로를 흐르는 것은 아니며 실제 배터리의 단락전류 예측도 아니다. 전기적 소비 전력은 확인했지만 온도/파손/난연성은 모델에 없다. 제조사 레퍼런스는 기본 측정 방식의 근거, 이번 시뮬레이션은 선택한 조건에서의 고장 경로 비교 근거다.

기존 [유사 프로젝트 측정 구조 비교21](21_External_Project_Monitoring_Architecture_Review_2026-10-27_ko.md)는 별도 선행 자료이며, 이번 문서는 제조사 ADC 측정 예제의 읽는 위치와03_15 실습의 적용 범위를 보완한다.

## 6. 설계 판단과 남은 작업

**분압·필터·STM32 ADC라는 기본 구조를 유지한다.** 출발점 직렬 저항 방식은 계속 검토하되, 부품과 배선 조건을 확인한 뒤 CAD/BOM/환산 계수에 반영한다.

다음 첫 작업은 J7/J8 감지선의 출발점·편도 길이·굵기·커넥터·절연/고정 조건표를 채우는 것이다. 사용자 보고는 아직 미정이다. 이어2.2kΩ/±1%/0.5W급 이상이라는 검토 출발 조건을 실제 부품의 허용 전력·온도 디레이팅·전압·펄스·TCR와 대조한다.0.5W 표기만으로 열수축튜브/밀폐 설치를 통과 처리하지 않는다.

출처는 공식 온라인 자료의 해당 판본을 기준으로 정리했다. 로컬 PDF 복제본은 확보하지 않았으며 새 실물 시험이나 회로 채택/구매 승인은 수행하지 않았다.

## 11/16~17 후속 — 통상적 구성의 근거 범위

분압을MCU ADC로읽는방식은제조사/공개프로젝트에도있다. [ODrive v3.5 공식회로](https://github.com/odriverobotics/ODriveHardware/blob/master/v3/v3.5docs/schematic_v3.5.pdf)의Main p1 R6=10kΩ/R7=1kΩ/C1=270pF, [VESC6+ RevB 2018-02-27](https://vesc-project.com/sites/default/files/Benjamin%20Posts/VESC_6_plus.pdf)의PDF3쪽DRV8301 R15=39kΩ/R16=2.2kΩ 등은실제사례다. ODrive/VESC원문은기존assets/logs/pcb_design/2026-10-27_external_benchmark에보존된자료와대조했다.

이사례들이**외부케이블출발점2.2kΩ+TPS/TMUX까지우리와동일한조합의표준성/검증**을증명하지는않는다. 보드내버스전압과외부하네스의고장경로를구분해야한다.

[Orion BMS2 Wiring Manual](https://www.orionbms.com/manuals/pdf/orionbms2_wiring_manual.pdf), Rev1.1/표기일1/9/2018, 인쇄/PDF64쪽Fuses on voltage tap wires는외부전압탭배선보호를다룬다. 해당제품은내부퓨즈가외부배선간고장을보호하지못하는조건을설명하고외부퓨즈를논하지만,그제품의직렬저항금지/퓨즈값을우리단일팩ADC에그대로적용하지않는다. **“모든감지회로가저항방식”이라는근거로사용하지않는다.**

우리의TPS/TMUX는보드무전원시에도배터리측입력이남는조건의분리목적이고,Rp/퓨즈는감지배선고장전류대책이다. 서로대체되는소자가아니다. 다음선정판단은[설계30](30_Voltage_Sense_Branch_Protection_Comparison_2026-11-13_ko.md)의정상분압/지속고장/설치조건으로한다. 최종부품선정·실물보호검증은아직없다.
