# E07/M01 실물 시험 · 7채널 ADC와 원형 DMA

11월 26일 시작해 27일 새벽 마감했다. NUCLEO-F446RE의 외부 입력 여섯 곳에 같은 시험 전압을 차례로 넣자, 여섯 번 모두 예상한 UART 필드가 반응했다. 각 시험에서 받은 30개 블록은 순번이 연속이었고 보드 시각 간격은 100 ms였다. 실제 센서와 제작 쉴드의 정량 성능은 후속 시험에서 측정한다. [핀·ADC rank·DMA 인덱스 대응표](../plans/2026-11-26_E07_M01_ADC_Scan_Table_ko.md)

## 두 채널에서 일곱 채널까지

| 확인한 동작 | 관측 및 근거 |
|---|---|
| TIM2에서 ADC 시작 | 84 MHz 타이머에 PSC 83, ARR 499를 적용해 500 µs마다 ADC 스캔을 시작한다. 7채널에서 DMA 절반은 200스캔 × 7개 = 1,400원소이며 100 ms마다 완성된다. [CubeMX 설정](../../03_Firmware/stm32_uart_mvp/stm32_uart_mvp.ioc) |
| 두 채널 DMA 정상 경로 | PA4 풀다운, 1.512 V, 1.797 V 조건에서 블록을 수집했다. [풀다운](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/zero_blocks_qch_2cge.log) · [1.512 V](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/pa4_1512mV_blocks_99zoxgvn.log) · [1.797 V](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/pa4_1797mV_blocks_3l_qz0kx.log) |
| 두 채널 DMA 오류 경로 | 디버거로 블록 처리 중 교체, 순번 누락, 타이머 중단을 유도했다. DMA 스트림 중단 때 유효한 0값이 출력되던 사례도 발견했다. 콜백에서 스트림 활성 상태를 검사한 뒤 같은 중단에서 오류 한 줄이 출력됐고, 별도 재시작에서는 정상 출력이 복귀했다. [블록 교체](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/block_changed_lmdlybj6.log) · [누락](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/missed_block_injection_efug05qj.log) · [타임아웃](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/tim2_trigger_timeout_1hm90bu3.log) · [수정 전](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/dma_stream_disabled_jwdxsjqj.log) · [수정 후](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/dma_disabled_after_fix_6xs0neol.log) · [재시작](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_pa4_dma/normal_restart_after_fix_7u_nsk35.log) |
| 일곱 채널 정상 경로 | PA4 → VREFINT → PB0 → PC0 → PC1 → PC2 → PC3 순서다. 사용자가 CubeIDE에서 오류·경고 0건과 디버그 실행을 확인했다. USART2에서 받은 각 채널 값은 200표본의 평균 카운트 × 100이다. [ADC 설정](../../03_Firmware/stm32_uart_mvp/Core/Src/adc.c) · [평균 계산과 오류 출력](../../03_Firmware/stm32_uart_mvp/Core/Src/main.c) |

## 멀티미터와 UART를 대조한 결과

| 시험 | 멀티미터 직류 전압 | VREFINT로 환산한 블록 평균 |
|---|---:|---|
| PA4–GND, 12 kΩ 풀다운 | 0.3 mV | 2.08 mV |
| A2, A3, A5, A4, CN7-35, CN7-37에 분압점 하나씩 연결 | 각각 1.797 V | 1.80133~1.80160 V. 차이는 +4.33~+4.60 mV |
| 상태 A → B, PC2만 GND에서 분압점으로 이동 | 분압점 A·B 모두 1.797 V | PC2 +1799.097 mV, PC3 −0.114 mV. 고정한 다섯 외부 채널의 평균 변화 절댓값 ≤ 0.13 mV |

각 구간을 독립적으로 계산했다. ADC와 멀티미터의 관측 시각은 동기화하지 않았다. 마지막 비교는 이 분압기의 두 정적 조건에서 얻은 평균 변화다. 전체 입력 범위의 정확도, 순간 간섭, 포화, 센서별 소스 임피던스는 여기서 판정할 수 없다. [핀별 결과와 UART 원본](../../assets/logs/mvp_measurements/2026-11-26_e07_m01_adc7_dma/README.md) · [재계산값과 원본 해시](../../assets/logs/planning/2026-11-27_e07_closeout/verification.json)

## 종료와 재개

사용자가 CubeIDE에서 Terminate를 누르고 마지막 NUCLEO USB를 분리했다. ESP32는 만능기판에서 분리한 채로 시험했다. 배터리 및 외부 전원 2핀 두 개는 이번 USB 벤치에서 사용하지 않았다. 마지막으로 확인한 배선은 상태 B다. PA4·PB0·PC0·PC1은 공통 GND, PC2(CN7-35)·PC3(CN7-37)는 같은 분압점이다. 마지막 확인 이후 점퍼를 옮겼다는 보고는 없다.

기상 후에는 이 배선에서 먼저 60초 연속 수집을 하고, 통과하면 같은 7채널 이미지에서 TIM2 중단과 재시작을 확인한다. [준비 상태·판정 기준·다음 단계의 이유](../progress/2026-11-27_progress.md)
