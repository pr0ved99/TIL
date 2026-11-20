# 모니터링 입력 — 시뮬레이션 결과와 설계 판단

학습 회차 2026-10-28 · 마감 2026-10-29. **사용자 KiCad GUI 실습 완료 / 회로 기본안 검토 / 실물 NOT_RUN / 제작용 아님**.

## 결과와 원본

| 범위 | 원본·결과 | 판정의 경계 |
| --- | --- | --- |
| 전류 한 채널 | [AC·TRAN](KiCAD/Simulation/01_Current_RC/README.md): 12kΩ/100nF, 약133Hz/−3.01dB·19kHz/−43.1dB, 상승/하강 1τ와 변화량99% | 이상 RC와 입력 파형 안의 결과 |
| 온도 한 채널 | [NTC](KiCAD/Simulation/02_NTC/README.md): 25°C 상당1.65V/fc265.258Hz, 50°C 상당967.35mV/fc404.834Hz | 고정 저항 대입·전원 AC 전달. NTC 열응답·센서 정확도 아님 |
| 전압 한 채널 공통 모델 | [분압](KiCAD/Simulation/03_Voltage_Divider/README.md): 12.6V→2.06341V,16V→2.62021V, fc404.942Hz, 저주파−15.7157dB, 차단점−18.7260dB | PA4/PB0 실물 두 채널 구현 아님 |

[상세 학습 노트](../07_Embedded_Learning_Notes/01_Concept_Notes/20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md)와 [마감 근거](../assets/logs/pcb_design/2026-10-28_simulation_closeout/README.md)에 계산·사용자 보고·PNG/CSV·최종 저장 연결을 구분했다. 원본 CSV의 대조는 새 시뮬레이션 실행이나 실물 합격이 아니다.

## NTC 공급 기본안과 보호 미결

- NTC 두 채널만 **CN7-5의 MCU VDD**에서 공급하는 안으로 좁혔다. 현재 쉴드의 실제 공급은 CN7-16 STM_3V3이며 아직 수정하지 않았다. 전류센서/CAN의 EXP 공급 계약을 함께 변경하지 않는다.
- ADC 기준은 정확히 VDDA다. VDD→VDDA 경로와 CN7-5/16·JP6/SB57·실물 보드 리비전 및 공급 추종 오차를 대조한다. CN7-5와16을 연결해 JP6를 우회하지 않는다.
- 10kΩ 분압·1kΩ/100nF를 기본안으로 유지한다. C3 잔류 전하만을 이유로 추가 다이오드 품번을 선정하지 않았다. 작은 에너지는 안전 보증이 아니며, FT의 일반 디지털 입력 조건을 ADC 샘플링·전원 하강 조건으로 확대하지 않는다.
- 제작 전 정상/NTC 단선의 전원 하강과 ADC 핀 허용 조건을 정리한다. 미해결이면 VDD·VDDA·입력의 실제 파형 및 추가 방전/분리 대책이 필요하다. 일반 다이오드 모델만으로 안전을 선언하지 않는다.

자료: [STM32F446 DS10693](https://www.st.com/resource/en/datasheet/stm32f446re.pdf), [NUCLEO UM1724 §7.8·표29](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf#page=59), [AN4899 Rev4 §5.3.6](https://www.st.com/resource/en/application_note/an4899-stm32-microcontroller-gpio-hardware-settings-and-lowpower-consumption-stmicroelectronics.pdf#page=23). 실제 보드 상태는 미확인이다.

## 전압 채널의 첫 상세 후보

K1 Pin30 전단은 PA4, Pin87 후단은 PB0 후보로 각각 공통 GND 기준의 독립 측정이다. 모터 주전류는 기존 경로이며 분압에는 감지 분기만 들어간다.

```text
VRAIL ─ 12k ─ 12k ─● VDIV
                    ├─ 4.7k ─ GND
                    ├─ 100nF ─ GND
                    └─ 1k ─ VADC (현재 무부하)
```

- 분압비4.7/28.7≈0.163763, 역비6.106383. C가 분압 노드에 있어서 Req=24k||4.7k≈3.93031kΩ, τ≈0.393031ms다. ADC 무부하 모델에서는 이후1kΩ을 fc 계산에 더하지 않는다.
- 16V에서 분압 전류557.491µA, 상단 저항 각각3.72956mW·하단1.46074mW. 부품의 최종 전력/전압/온도·과도 정격을 정한 것은 아니다.
- 저항±1%의 최악 조합은 출력2.57668~2.66433V, 명목 분압비로 환산하면 약±0.27V 오차 가능. [요구15](15_Expansion_PCB_Requirements_2026-10-23_ko.md)의 보정 후±0.10V 달성은 아직 미검증이다.
- 상단 두 저항은 기존 [CD-ESTOP-005](../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md)의 분할 구조를 따른다. 단일 상단 저항 단락·하단 개방 등에서 ADC가 안전하다고 보장하지 않는다.
- K1 전단 전압은 MCU OFF에도 남을 수 있다. NTC의 공급 추종 대책을 전압 감지 입력의 무전원 보호 완료로 확대하지 않는다. 과도·역극성·배선 단락 에너지 제한·키/커넥터·GND 경로는 후속이다.

## 다음 설계 순서

1. 전압±0.10V에 대한 저항 정밀도·보정 독립점·VDDA·ADC/보호 누설·온도 오차 배분을 계산한다.
2. 정상0~16V와 허용 과도/역극성/단선·단락/MCU OFF 조건을 정해 보호·ADC 획득 조건을 좁힌다. 전류·온도의 남은 항목도 통합 대조한다.
3. 준비된 설계 변경만 실제 쉴드 두 채널·공급 net·시험점에 반영하고 ERC·기구/전체 배치 단계로 진행한다. 실물 시험은 별도 준비 회차다.

이번에는 독립 시뮬레이션 회로·학습/판단 문서가 추가됐다. 기존 제작 쉴드 CAD/BOM·MCU 코드/빌드/플래시·실물 배선·구매는 변경하지 않았다. AI는 후속 문서 상태, 전체 MVP는 기존 진행 중/PARTIAL·OPEN을 유지한다.
