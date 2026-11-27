# 독립 검토 대조 결과

11월 28일 수신한 검토서는 현재 저장 PCB와 같은 SHA-256 `2d9137acc41da4927c122165093d573265f0fc44528822748f292dbfbaa12ab3`를 사용했다. [받은 원문](TMR_Monitor_Shield_RevA_Independent_Design_Review_2026-11-28_ko.md)

## 외곽 이격을 실제 KiCad에서 재현

| KiCad 10.0.8 검사 상태 | 구리 외곽 이격 설정 | DRC 위반 / 미배선 / 회로도 대조 오류 |
| --- | ---: | ---: |
| [현재 저장 PCB와 프로젝트 규칙](baseline.json) | 0.00 mm | 0 / 0 / 0 |
| [복사본에 이격만 적용](edge_0p5_before_refill.json) | 0.50 mm | 1 / 0 / 0 |
| [복사본에서 B.Cu GND 면을 다시 채움](edge_0p5_after_refill.json) | 0.50 mm | 0 / 0 / 0 |

왼쪽 Edge.Cuts X=101.5000 mm, 기존 GND 채움 X=101.5005 mm로 KiCad가 확인한 간격은 **0.0005 mm**다. 기존 1.335 mm 수치는 트랙 기준이라 접지면이 외곽에 닿을 위험을 보여주지 못했다. 복사본에서 지적된 B.Cu의 구리 외곽 이격 위반은 접지면을 다시 채워 해소했다. 외접 범위에서 확인한 좌우·상하 이격은 각각 0.5005 mm이며 GND 면적은 2,893.524 → 2,767.726 mm²였다. GND 패드 28개와 모든 참조번호·패드·네트 연결이 유지됐다. 0.50 mm는 시험값이며 발주 규칙은 제조 공정에 맞춘다. 시험은 복사본에 적용했고 정식 PCB와 프로젝트 규칙의 해시는 그대로다.

재현하려면 PCB·회로도·프로젝트·라이브러리 표와 로컬 라이브러리를 복사한 경로에서 프로젝트의 `min_copper_edge_clearance`를 0.50 mm로 설정한다. 채움 전 DRC를 저장하고, 복사본에 아래 명령을 사용해 접지면을 다시 채운 결과와 비교한다.

```bash
kicad-cli pcb drc --all-track-errors --schematic-parity --severity-all \
  --refill-zones --save-board --exit-code-violations --format json \
  -o edge_0p5_after_refill.json TMR_Monitor_Shield_RevA.kicad_pcb
```

## 11월 28일 재검토

같은 PCB에서 KiCad 10.0.8의 DRC·미배선·회로도 대조가 모두 0건이고 ERC도 0건이었다. 0.50 mm 시험을 새 복사본에서 반복해 채움 전 외곽 위반 1건, 재채움 후 0건을 재현했다. 세 DRC의 위반 목록과 무시 항목은 위 표의 저장 결과와 일치한다. pcbnew로 패드 중심을 잇는 선분을 다시 합산한 결과 R6.2→TP6.1은 7.3297 mm, R6.2→C4.1은 24.0924 mm, C4.1→J1.37은 8.6637 mm였다. [재실행 ERC](erc_repeat.json)

K1 전·후단에 각각 16 V DC가 들어온 경우를 독립 검토서 §10.1의 식으로 다시 계산했다. 아래는 U2가 켜졌을 때의 채널별 결과다. 상단 12 kΩ 두 개, 하단 4.7 kΩ, 직렬 1 kΩ, 풀다운 47 kΩ 및 스위치 온저항 2 Ω을 사용했다. 마지막 열은 보드 저항 각각 ±0.1%, 차체 저항 ±1%의 극값 조합에서 **해당 행의 공칭 계수**로 복원한 출발점 전압이다.

| 차체 분기 저항 | ADC 공칭 | 입력 환산 계수 | 저항 공차만 고려한 16 V 표시 범위 |
| --- | ---: | ---: | ---: |
| 없음 | 2.37135 V | 6.74720 | 15.9722~16.0278 V |
| 2.2 kΩ 후보 | 2.20020 V | 7.27208 | 15.9615~16.0386 V |

2.2 kΩ을 추가한 회로에 기존 계수 6.74720을 쓰면 16 V 입력이 14.8452 V로 표시된다. 공차표에는 ADC·기준전압·온도 변화·누설·배선 오차가 빠져 있다. U2 전원이 꺼지고 스위치가 열린 경우에는 16 V 입력에서 신호 입력 핀이 각각 약 2.620 V, 2.434 V다(누설 무시). TI의 VDD < 1.5 V 조건에서 권장 신호 범위 상한은 3.6 V다. 이 계산은 0~16 V 정상 범위의 비교이며 차체 과도전압·역극성 내성은 미확정이다. [보호 방식 비교 §5~6](../../../../../09_Electrical_Design/30_Voltage_Sense_Branch_Protection_Comparison_2026-11-13_ko.md) · [TI TMUX1511 Rev. B, p.4 §5.3](https://www.ti.com/lit/ds/symlink/tmux1511.pdf#page=4)

## 남은 판단

- **발주 전.** 제조사 외곽 규칙을 확정하고 채움·DRC·Gerber/드릴을 같은 파일로 대조한다. K1 전·후단 감지선의 출발점 보호와 PCB 입력 보호는 별도로 판단한다. NUCLEO의 A5·A4를 통한 PC0·PC1 입력 반응은 이미 확인했다. 쉴드 소켓의 1:1 핀 1 방향·적층, 하네스 실물 극성과 IMU를 포함한 결합 상태는 후속이다. 현재 J3·J4 쉴드 핀은 1=3V3, 2=GND, 3=OUT이다. [NUCLEO 실측](../../../../../docs/verification/50_ADC_DMA_7_Channel_Bench_2026-11-27_ko.md) · [ST UM1724](https://www.st.com/resource/en/user_manual/dm00105823.pdf)
- **국부 배선 비교.** 오른쪽 온도 R6.2→C4.1은 24.09 mm, C4.1→TP6.1은 31.42 mm로 확인했다. TP6까지의 31.42 mm는 필터 노드 내 전체 경로다. 저장 PCB의 좌표를 따라 R6.2에서 TP6까지 분기만 계산하면 2.38 mm + 4.95 mm = 약 7.33 mm다. C4→ADC의 8.66 mm를 기준으로 R6·TP6 후보를 비교하며, 필터 앞 배선·접지·프로브 접근이 동시에 좋아지는지 본다. 왼쪽 온도 R3.2→R4.1은 22.31 mm다. B.Cu 위의 이 구간과 접지 슬롯을 함께 보되, 길이로 실제 잡음을 판정하지 않는다. [패드 경로 CSV](../../../../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/reports/functional_placement_paths.csv)
- **ADC 설정 근거 보완.** 제공한 독립 검토 자료에 빠졌던 벤치 펌웨어는 APB2 84 MHz / 6으로 ADC 14 MHz, 각 rank의 샘플링 480사이클, 500 µs마다 7채널 스캔이다. 입력 채널 순서는 PA4 → VREFINT → PB0 → PC0 → PC1 → PC2 → PC3이다. 획득 시간은 채널당 약 34.29 µs이고 12비트 변환까지 포함하면 약 35.14 µs다. 기존 임시 분압 실측의 범위를 보존하며, 조립 후 센서와 하네스가 연결된 상태에서 정착·편차·누화·보호 동작을 측정한다. [CubeMX 설정](../../../../../03_Firmware/stm32_uart_mvp/stm32_uart_mvp.ioc) · [STM32F446 ADC 특성](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)
