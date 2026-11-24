# TIL · 이영현의 기술 학습 기록

SSAFY 임베디드 로봇 트랙에서 시작한 학습 기록입니다. 데이터시트에서 읽은 동작을 보드에서 확인하고, 실험을 다시 해 볼 수 있도록 코드와 관측 결과를 함께 남깁니다.

## 대표 프로젝트 · Tracked Mobile Robot

브라우저의 무선 주행 명령이 STM32를 거쳐 좌우 궤도를 움직이는 로봇입니다. 프로젝트 README에서 실제 차체의 움직임, 펌웨어의 정지 판단, Gazebo 속 자율주행을 각각 확인할 수 있습니다. **[프로젝트 열기](https://github.com/pr0ved99/TIL/tree/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot)**

| 궁금한 점 | 바로 보기 |
| --- | --- |
| 실제 로봇은 어떻게 움직이나요? | [카펫 주행·비상정지·복구 영상 (2분 29초)](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/assets/videos/wifi_mvp/2026-10-24/final/TMR_MVP_Final_2026-10-24.mp4) |
| 정지 명령을 받으면 출력이 언제 꺼지나요? | [STM32 두 PWM의 차단 파형과 측정 기준](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md) |
| 시뮬레이션에서 로봇은 벽을 어떻게 우회하나요? | [Nav2와 학습 기반 제어의 경로 비교](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/verification/48_Simulation_Gate02_2026-11-24_ko.md) |

## 주제별 기록

| 주제 | 찾아볼 내용 |
| --- | --- |
| 임베디드 | [STM32 보드 실습](Embedded/STM32/) · [CAN](Embedded/STM32/CAN/) · [FreeRTOS](Embedded/STM32/RTOS/) · [ESP32-S3](Embedded/ESP32-S3/) · [Jetson](Embedded/Jetson/) |
| 로보틱스 | [ROS 2](Robotics/ROS2/) · [VSLAM](Robotics/VSLAM/) |
| 인공지능 | [강화학습](AI/Reinforcement_Learning/) |
| 개발 기초와 도구 | [Git](CS/Git/) · [운영체제](CS/Operating_System/) · [개발 도구](Tools/) |
| 알고리즘 | [Daily Algorithm](https://github.com/pr0ved99/daily-algorithm)에서 C++ 문제 풀이와 구현 연습을 관리합니다. |

2026년 상반기에 세운 목표는 AI 의존도를 줄이고 데이터시트를 직접 읽어 기술적 판단을 내리는 것입니다. 매일 배운 것을 제 언어로 기록하고, 다른 사람이 동작 원리와 선택 이유를 따라갈 수 있게 쓰려고 합니다. [학습 로드맵](Career-Roadmap/Goal_Roadmap.md)
