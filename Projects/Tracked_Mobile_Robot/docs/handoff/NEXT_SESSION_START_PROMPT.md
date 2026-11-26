# 다음 세션 시작 프롬프트

TMR 작업을 이어서 진행하자. 루트와 프로젝트 AGENTS.md, [현재 인수인계](CURRENT_SESSION_CONTEXT.md), [11/27 재개 순서와 이유](../progress/2026-11-27_progress.md)를 읽어.

집에서는 [7채널 ADC 실측](../verification/50_ADC_DMA_7_Channel_Bench_2026-11-27_ko.md)에서 재개해. 직전 상태 B에서 CubeIDE Terminate 후 NUCLEO USB 분리를 확인했다. ESP32는 만능기판에서 분리돼 있다. 배터리와 외부 전원 두 2핀은 이 USB 벤치에서 사용하지 않았다. 마지막 B 배선은 PA4·PB0·PC0·PC1이 GND, PC2·PC3가 같은 분압점이야. 기존 이미지에서 보드 시각 60초 이상 연속 수신을 먼저 확인하고 TIM2 중단·재시작으로 넘어가.

노트북에서는 [GATE-02 결과](../verification/48_Simulation_Gate02_2026-11-24_ko.md)를 기준으로 재개해. 시뮬레이션 기본 주행은 Nav2로 두고, 다음은 ELEC-01 보호 저항·분기 퓨즈·환산 오차 검토야. 주행을 재현할 때는 보고서의 P05 명령과 15 cm·무접촉·2초 정지 기준을 사용해.
