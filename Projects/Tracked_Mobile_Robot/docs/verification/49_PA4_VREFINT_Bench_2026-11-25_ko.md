# STM32 PA4와 VREFINT 두 채널 벤치 결과

11월 24일 밤에 보드에서 수집했고 25일 자정 이후 프로브 위치와 종료 상태를 확인했다(한국 시각). E07/M01 중 **차례로 읽은 두 채널을 식별하고 분압 입력만 바뀌는지** 시험했다. 입력 쪽 배선을 바꾼 세 구간에서 PA4 평균은 2223.54 → 1872.01 → 3.92카운트, VREFINT 평균은 1500.63~1500.67카운트였다.

## 시험 구성과 원본

NUCLEO-F446RE, A2/PA4, 11.82 kΩ 및 9.95 kΩ 저항과 USB 전원을 사용했다. S0 잠금, S1 OFF, 배터리와 보드 외부 전원 두 2핀 분리, JP5 U5V 및 JP1 OPEN 조건이었다. 두 보드는 UART로 연결돼 있어 측정 중에는 두 USB로 전원을 공급했다. 사용자 보고로 CubeIDE 빌드 오류·경고 0건, Debug 다운로드 후 Resume를 거쳐 USART2 115200에서 두 필드를 수신했다. 당시 로컬 Debug ELF의 SHA-256은 `22ac7ae8254b002a3f0e82ec82f435df472f6abdb3526b00de048f2c9828d27c`다. 보드 플래시 전체를 읽어 ELF와 대조한 기록은 없다.

| A2 분압 구성 (공급 쪽 → A2 → GND 쪽) | DMM 표시와 프로브 위치 | 유효/수집 · seq | PA4 평균 | VREFINT 평균 | 고정 3.30 V 환산 | VREFINT 보정 환산 |
|---|---|---:|---:|---:|---:|---:|
| 3V3 → 9.95 kΩ → A2 → 11.82 kΩ → GND | 중간점–GND 1.797 V, 별도 3V3–GND 3.31 V | 589/589 · 5879~6467 | 2223.54 | 1500.63 | 1.79187 V | 1.80066 V |
| 3V3 → 11.82 kΩ → A2 → 9.95 kΩ → GND | 중간점–GND 1.513 V | 608/608 · 3~610 | 1872.01 | 1500.67 | 1.50858 V | 1.51594 V |
| 3V3 점퍼 분리, A2 → 9.95 kΩ → GND | 9.95 kΩ 양단 0 V, 같은 GND–A2 점퍼 끝 0.4 mV | 1021/1021 · 3~1023 | 3.92 | 1500.66 | 3.160 mV | 3.176 mV |

세 비교 구간 2,218개 표본에 구간 내 순번 누락은 없었다. 상·중간 구간은 106 ms 간격, 영점 구간은 105~106 ms였다. 첫 통신 확인 21쌍은 별도 구간이다. DMM의 범위·표시 분해능·ADC와 동기화된 시각은 확보하지 않아 구간 평균과 사용자 판독값을 비교했다. [첫 수신 원본](../../assets/logs/mvp_measurements/2026-11-24_e07_m01_pa4_vrefint/first_uart.log) · [1.797 V 원본](../../assets/logs/mvp_measurements/2026-11-24_e07_m01_pa4_vrefint/pa4_dmm_uart.log) · [1.513 V 원본](../../assets/logs/mvp_measurements/2026-11-24_e07_m01_pa4_vrefint/pa4_mid_dmm_uart.log) · [영점 원본](../../assets/logs/mvp_measurements/2026-11-24_e07_m01_pa4_vrefint/pa4_low_dmm_uart.log)

## 변환과 판정

ADC1은 12비트·14 MHz, 각 rank의 취득 시간은 480사이클이다. 소프트웨어 시작 후 rank 1 PA4, rank 2 VREFINT의 변환 완료를 각각 폴링한다. 두 변환이 끝나고 overrun이 없으며 Stop에 성공해야 `valid=1`이다. 문제 발생 시 양쪽 모두 −1과 `valid=0`을 송신하도록 작성했다. 실패 분기의 실보드 고장 주입은 후속이다. 벤치 루프가 모터 초기화보다 앞에 있다. [CubeMX 설정](../../03_Firmware/stm32_uart_mvp/stm32_uart_mvp.ioc) · [ADC 설정](../../03_Firmware/stm32_uart_mvp/Core/Src/adc.c) · [벤치 루프](../../03_Firmware/stm32_uart_mvp/Core/Src/main.c)

디버거에서 읽은 칩별 공장 보정값은 1508카운트다. 각 유효 표본에 대해 `VDDA = 3.30 V × 1508 / vrefint_raw`, `V_PA4 = VDDA × pa4_raw / 4095`로 PC에서 계산하고 전압을 평균했다. 1.797 V와 1.513 V에서 절대 차이는 각각 5.13 → 3.66 mV, 4.42 → 2.94 mV로 줄었다. 보드 펌웨어가 보내는 값은 두 raw다. [STM32F446 데이터시트 Rev 10, 145쪽 표 84](../../assets/stm32f446mc.pdf#page=145) · [높은 입력 계산값](../../assets/logs/mvp_measurements/2026-11-24_e07_m01_pa4_vrefint/pa4_dmm_comparison.json) · [중간 입력 계산값](../../assets/logs/mvp_measurements/2026-11-24_e07_m01_pa4_vrefint/pa4_mid_dmm_comparison.json)

영점에서 1,021개 중 450개는 0, 최대값은 seq 783의 73카운트였다. 0.4 mV는 약 반 카운트에 해당한다. ADC의 약 3.18 mV 평균, DMM의 두 표시, 순간 최대값을 서로 같은 시각의 전압으로 보거나 점퍼 전압강하·영점 오차의 원인을 특정할 수 없다. 두 측정 모두 3V3 점퍼를 뺀 상태였다는 사용자 확인을 원본 메타데이터에 반영했다. [프로브 위치와 영점 통계](../../assets/logs/mvp_measurements/2026-11-24_e07_m01_pa4_vrefint/pa4_low_dmm_comparison.json)

**판정.** 두 rank의 식별성과 저전압 입력 추종을 확인했다. 여섯 외부 입력의 정확도, 실배터리 환산·자동 저전압 정지, 타이머/DMA 수집률과 오류 처리는 미검증이다. 다음에는 지금 원본을 기준선으로 두고 2-rank 타이머 트리거·DMA 버퍼 순서, 블록 수집률, 누락·overrun 판정 기준을 먼저 설계한다. 사용자는 마감 시 두 USB·배터리·외부 전원 두 2핀이 모두 분리돼 있다고 확인했다. 3V3 분압 점퍼도 분리 상태다.
