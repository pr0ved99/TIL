# E07/M01 · STM32F446RE ADC1 설정표

**2026-11-26 벤치 진행 상태.** TIM2가 0.5 ms마다 ADC1을 시작하면 외부 입력 6개와 내부 기준전압 VREFINT를 아래 순서로 읽는다. 7개 rank와 DMA 인덱스를 펌웨어에 적용했고 보드에서 100 ms 간격의 7채널 출력을 확인했다. 외부 입력 여섯 곳 **A2(PA4), A3(PB0), A5(PC0), A4(PC1), CN7-35(PC2), CN7-37(PC3)**에 같은 분압 신호를 차례로 넣어 해당 슬롯의 ADC 값과 멀티미터 표시를 대조했다. [현재 CubeMX 설정](../../03_Firmware/stm32_uart_mvp/stm32_uart_mvp.ioc) · [7채널 벤치 기록](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_adc7_dma/README.md) · [이전 2채널 정상 재시작 로그](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/normal_restart_after_fix_7u_nsk35.log)

## 신호에서 DMA 버퍼까지

Rank는 한 스캔 안에서 ADC가 읽는 순서다. `k`는 0부터 시작하는 스캔 번호로, 그 스캔의 첫 원소는 `raw[7*k]`다. 기존 두 채널을 rank 1·2에 유지해 분압 벤치 결과를 같은 위치에서 비교할 수 있게 했다. 쉴드의 J1은 NUCLEO의 CN7과 맞물린다.

| Rank | 측정 신호 | 쉴드 입력 → ADC 쪽 네트 | J1/CN7 접점 → MCU 핀 | ADC1 채널 | DMA 원소 | 확인 범위 |
|---:|---|---|---|---|---|---|
| 1 | K1 전단 전압 | J7-2 → V_UP_ADC | 32 → PA4 (A2) | IN4 | `raw[7*k]` | PA4 분압 벤치 확인, K1 전단 경로는 실측 전 |
| 2 | 내부 기준전압 | MCU 내부 VREFINT | 내부 연결 | IN17 | `raw[7*k+1]` | 2채널·7채널 벤치에서 수신 확인 |
| 3 | K1 후단 전압 | J8-2 → V_DOWN_ADC | 34 → PB0 (A3) | IN8 | `raw[7*k+2]` | PB0 분압 벤치 확인, K1 후단 경로는 실측 전 |
| 4 | 왼쪽 모터 전류 | J3-3 → I_LEFT_ADC | 38 (A5) → SB51 → PC0¹ | IN10 | `raw[7*k+3]` | A5 분압 벤치 확인. 실제 전류 센서 경로는 실측 전 |
| 5 | 오른쪽 모터 전류 | J4-3 → I_RIGHT_ADC | 36 (A4) → SB56 → PC1¹ | IN11 | `raw[7*k+4]` | A4 분압 벤치 확인. 실제 전류 센서 경로는 실측 전 |
| 6 | 왼쪽 모터 케이스 온도 | J5-1 → T_LEFT_ADC | 35 → PC2 | IN12 | `raw[7*k+5]` | CN7-35 분압 벤치 확인. 실제 온도 센서 경로는 실측 전 |
| 7 | 오른쪽 모터 케이스 온도 | J6-1 → T_RIGHT_ADC | 37 → PC3 | IN13 | `raw[7*k+6]` | CN7-37 분압 벤치 확인. 실제 온도 센서 경로는 실측 전 |

각 화살표는 해당 채널의 신호 경로를 나타낸다. 특히 J7/J8에는 원전압이 들어오고, MCU에는 분압·보호 회로를 거친 전압이 들어간다. 현재 쉴드 회로도에서 넷리스트를 다시 내보내 여섯 ADC 네트와 J1 접점을 저장된 넷리스트와 대조했다. MCU 핀의 ADC 기능은 ST DS10693 Rev 10, 46~48쪽 표 10의 PC0~PC3·PA4·PB0 행에서 확인했다. [쉴드 회로도](../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/TMR_Monitor_Shield_RevA.kicad_sch) · [회로도 포트 대조표](../../assets/logs/pcb_design/2026-11-12_port_inventory/README.md) · [STM32F446 핀 기능](../../assets/stm32f446mc.pdf#page=46)

¹ 2026-11-26 무전원 상태에서 촬영한 보드 뒷면에 `MB1136 rev C`가 보인다. SB51·SB56에는 `0` 표시 점퍼가 장착되어 있고, SB46·SB52는 양쪽 패드가 떨어져 있다. ST 회로도와 대조하면 A5·A4는 각각 PC0·PC1의 아날로그 경로를 선택하며, PB8·PB9의 I²C 경로는 이 두 접점에서 분리된다. 사진으로 확인한 범위는 브리지 배치까지다. [실물 사진](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/IMG_3283_adc_bridges.jpg) · [ST MB1136 C04 회로도 5쪽, CN8 주변](../../assets/datasheets/mb1136-default-c04_schematic.pdf#page=5) · [UM1724 Rev 17, 27쪽 표 10의 A4/A5 브리지 행](../../assets/datasheets/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf#page=27) · [59쪽 표 29의 CN7 접점](../../assets/datasheets/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf#page=59)

## 0.5 ms 주기와 버퍼 크기

| 항목 | 7채널 설계값과 해석 |
|---|---|
| 타이머 | TIM2 입력 84 MHz, PSC 83, ARR 499 → 500 µs마다 TRGO 한 번. 채널당 2,000표본/s, ADC 전체 14,000변환/s |
| 변환 시간 | ADC 14 MHz, 12비트, 모든 rank에 취득 480사이클을 가정. 채널당 (480 + 12) / 14 MHz = 35.14 µs. 7개 합계 246 µs, 다음 트리거까지 명목 여유 254 µs |
| 한 스캔의 시간차 | ADC1이 순서대로 읽으므로 첫 채널과 마지막 채널의 취득 시점은 약 211 µs 차이 난다. 246 µs는 트리거 지연·DMA 처리 시간을 제외한 계산값이다. |
| 원형 DMA | DMA2 Stream0, 16비트 전송. 100 ms에 200스캔 × 7개 = **1,400원소/절반**. 전체 버퍼는 **2,800원소 = 5,600바이트**. 기존 2채널 버퍼는 800원소다. |
| 결과 갱신 후보 | 전류·전압은 채널당 200표본으로 100 ms 평균을 낸다. 온도는 같은 스캔에서 취득하되 2,000표본(10블록)을 모아 1초 평균을 내는 안이다. |

480사이클에서 취득 시간은 34.29 µs다. 보유 데이터시트의 VREFINT 최소 취득 시간 10 µs를 충족한다. 외부 입력은 각 회로의 소스 임피던스와 필터가 다르므로 인접 rank의 전압 차이가 큰 조건에서 정착 오차를 확인한다. [ST DS10693 Rev 10, 139쪽 §6.3.21 표 74의 tS·tCONV](../../assets/stm32f446mc.pdf#page=139) · [145쪽 표 83의 TS_vrefint](../../assets/stm32f446mc.pdf#page=145) · [채널별 수집·평균 목표](../../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md)

## PC2 변경 시 다른 채널의 응답

2026-11-27, PA4·PB0·PC0·PC1을 GND에, PC3를 1.797 V 분압점에 고정하고 PC2만 GND에서 분압점으로 옮겼다. 상태별 30블록을 비교한 결과 PC2 다음에 읽는 PC3 평균은 −0.114 mV 변했고, 고정된 다섯 외부 채널의 평균 변화 절댓값은 모두 0.13 mV 이내였다. 이 판정 범위는 해당 분압기와 시험한 두 배선 상태다. [상태 A·B 결과표와 원본 로그](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_adc7_dma/README.md) [현재 블록 처리 코드](../../03_Firmware/stm32_uart_mvp/Core/Src/main.c)

## 기상 후 재개

상태 B에서 NUCLEO 디버그를 종료하고 USB를 분리했다. 같은 배선에서 60초 연속성, 7채널 TIM2 중단과 재시작 순으로 확인한다. [시험 기준과 이유](../progress/2026-11-27_progress.md)
