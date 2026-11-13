# 외부 포트·보드 접점 목록 대조 — 2026-11-12

## 1. 결론과 범위

현재 저장된 TMR_Monitor_Shield_RevA 회로도에서 외부 측정 커넥터6개(J3~J8), Nucleo 접속 헤더2개(J1/J2)를 확인했다. 기존 설계20의 전류/NTC 포트 순서와 별도전원 제안은 현재CAD와 다르다. **이번에는 현재 연결을 작업 기준으로 명시하고 차이를 미결로 추적하며 회로를 바꾸지 않는다.**

KiCad CLI10.0.5로 현재 .kicad_sch를 읽어 [새 netlist](current_netlist.xml)를 추출했다. [핀 목록 CSV](port_pins.csv) · [해시/연결 비교](inventory.json). 40부품·91net의 이름/핀 집합은11/7 게시본과 동일하다. 회로도·PCB·프로젝트·심벌 라이브러리 해시는 유지했다. 새ERC/DRC·시뮬레이션·MCU빌드/플래시·실물시험은 실행하지 않았다.

## 2. 현재 외부 측정 포트

| Ref/값 | 핀1 | 핀2 | 핀3 | ADC측 경로와 접점 |
| --- | --- | --- | --- | --- |
| J3 CURRENT_LEFT | STM_3V3 | GND | I_LEFT_RAW | R1 12k candidate/C1 100nF → I_LEFT_ADC → J1-38 |
| J4 CURRENT_RIGHT | STM_3V3 | GND | I_RIGHT_RAW | R2 12k candidate/C2 100nF → I_RIGHT_ADC → J1-36 |
| J5 NTC_LEFT | T_LEFT_RAW | GND | 없음 | R3 10k 여기/R4 1k/C3 100nF → T_LEFT_ADC → J1-35 |
| J6 NTC_RIGHT | T_RIGHT_RAW | GND | 없음 | R5 10k 여기/R6 1k/C4 100nF → T_RIGHT_ADC → J1-37 |
| J7 VBAT_SENSE | GND | VBAT_PROTECTED_SENSE_RAW | 없음 | R7~R11/C5/U2통로1 → V_UP_ADC → J1-32 |
| J8 VMOTOR_SENSE | GND | MOTOR_VBAT_SAFE_SENSE_RAW | 없음 | R12~R16/C6/U2통로2 → V_DOWN_ADC → J1-34 |

전압 포트의 K1전단/후단 외부 연결 의도는 [설계27](../../../../09_Electrical_Design/27_Voltage_2Ch_Schematic_Contract_Comparison_2026-11-06_ko.md)와 비교했다. 외부하네스 실물 연결을 확인한 결과가 아니다. 센서 #5241의 주전류단자는 J3/J4의3P 포트에 포함되지 않는다.

## 3. 헤더·공급·기준

- J1값CN7_SOCKET: 16=STM_3V3,20=GND,38=I_LEFT_ADC,36=I_RIGHT_ADC,35=T_LEFT_ADC,37=T_RIGHT_ADC,32=V_UP_ADC,34=V_DOWN_ADC.
- J2값CN10_SOCKET: 활성 접점7=STM_AVDD. 이 net은U1 TPS3840의2번, U2 TMUX1511의14번 및C7/C8에 연결된다.
- STM_3V3는 전류센서 공급J3/J4-1과NTC고정저항R3/R5에 연결된다. STM_AVDD와별도net이며쉴드에서두net를이어놓지않았다. 이것이Nucleo내부두전원이갈바닉절연됐다는뜻은아니다.
- 모든측정포트의GND는동일/GND에연결되고J1-20으로연결된다. 전류/NTC는2번,전압은1번이GND다. 같은net이실제배선의전압차0을보장하지는않는다.
- 기존계약/도면의 MCU접점대응: J1-38→PC0,36→PC1,35→PC2,37→PC3,32→PA4,34→PB0. 특히38/36은PC0/PB8·PC1/PB9 solder bridge조건이주석에있으며이번에는실물접점/bridge를검증하지않았다.
- TP1=STM_3V3,TP2=GND,TP3/4=전류ADC,TP5/6=온도ADC. 현재netlist에전압ADC전용TP는없다. 접근성과추가필요성은후속검증계획에서판단한다.
- 헤더의기타no-connect표시는이쉴드회로에서미사용이라는뜻이다. Nucleo/기존기판의기능이나배선을없애는지시가아니다.

## 4. 이전 제안과 현재 CAD 차이

[설계20 §채널과커넥터계약제안](../../../../09_Electrical_Design/20_Analog_6Ch_Contract_and_Stage2_Review_2026-10-23_ko.md)은쉴드측제안이며센서모듈패드순서와별도대조하도록명시한다.

| 항목 | 설계20 제안 | 현재 저장 CAD | 이번 판단 |
| --- | --- | --- | --- |
| 전류3P | 1=SIG_GND,2=EXP_3V3,3=OUT | 1=STM_3V3,2=GND,3=OUT | 핀1/2역순과공급원차이를명시;자동교체안함 |
| NTC2P | 1=SIG_GND,2=NTC노드 | 1=NTC노드,2=GND | 핀역순을명시;하네스/제품대조후처리 |
| 전압2P | 1=SENSE_GND,2=RAW | 1=GND,2=RAW | 역할/순서일치;실물보호검증과별개 |
| 공급원 | 별도EXP_3V3 검토 | STM_3V3 및STM_AVDD 사용 | 별도LDO/CAN공급구현완료로표기하지않음 |

핀1을항상GND로하는보편규칙을가정하지않는다. 커넥터품목·키·핀1방향·하네스·모듈패드를대조한뒤최종번호를맞춰야한다. J5/6와J7/8는모두2P이지만저항센서입력과미분압rail입력으로역할이다르므로상호오접속방지검토대상이다.

## 5. 다음 한 단계

41-1은포트목록/기준정의와계약차이확인이다. 다음41-2에서각포트의정상입력·공급범위와근거를표로정리한다. 이후MCU/외부전원조합→차단·복귀/고장→보호경로/검증기준으로진행한다. CAN·별도LDO는현재CAD에없는후속설계이며이번에포트를자동추가하지않았다. 실물결선지시나최종제작핀계약이아니다.
