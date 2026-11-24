# Tracked Mobile Robot

브라우저로 조종하는 궤도 로봇입니다. ESP32-S3가 무선 명령을 전달하고, STM32F446RE가 주행 상태를 검사해 좌우 모터의 출력을 결정합니다. **[최신 프로젝트 README · 실물 시연, 계측 결과와 구현 코드](https://github.com/pr0ved99/TIL/tree/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot)**

[![카펫 위에서 전진하는 차체와 좌우 모터의 실시간 피드백](https://raw.githubusercontent.com/pr0ved99/TIL/refs/heads/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/portfolio/figures/carpet_drive_80s.jpg)](https://raw.githubusercontent.com/pr0ved99/TIL/refs/heads/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/assets/videos/wifi_mvp/2026-10-24/final/TMR_MVP_Final_2026-10-24.mp4)

[실물 주행 MP4 · 2분 29초](https://raw.githubusercontent.com/pr0ved99/TIL/refs/heads/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/assets/videos/wifi_mvp/2026-10-24/final/TMR_MVP_Final_2026-10-24.mp4) · [STM32 정지 명령과 PWM 파형](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md) · [ADC 두 채널의 실보드 측정](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/verification/49_PA4_VREFINT_Bench_2026-11-25_ko.md) · [Gazebo 장애물 우회 경로](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/verification/48_Simulation_Gate02_2026-11-24_ko.md)

이 브랜치의 소스는 7월 엔코더 검증 단계입니다. 위 링크는 무선 주행과 계측까지 담긴 작업 브랜치를 엽니다. 초기 하드웨어 구성과 당시 문서 목록은 [7월 README 보관본](https://github.com/pr0ved99/TIL/blob/f26d2679f22d5baca9d51f9a9e6abfc8067a5a8a/Projects/Tracked_Mobile_Robot/README.md)에서 볼 수 있습니다.
