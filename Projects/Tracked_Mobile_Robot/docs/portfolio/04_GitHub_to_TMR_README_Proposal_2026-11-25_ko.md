# GitHub 프로필에서 TMR까지 · 임베디드 로봇 시스템 통합 직무용 README 수정안

**반영 · 2026-11-25.** 프로필의 첫 프로젝트와 TIL 첫 화면을 최신 TMR로 연결했다. TMR에서는 영상의 카펫 주행 장면, 명령과 출력의 연결도, 원본 파형·ADC 비교·시뮬레이션 경로를 결과 옆에 배치했다. TIL 기본 브랜치에는 최신판 안내와 7월 보관본 링크를 두었다. 아래 표와 초안은 변경 전 검토 기록이다. [공개 프로필](https://github.com/pr0ved99) · [TIL](https://github.com/pr0ved99/TIL) · [프로젝트](../../README.md)

2026-11-25 검토. 프로필이 명시한 **Embedded Robotics & Systems Integration Engineer**와 TIL의 데이터시트·저수준 검증 목표를 기준으로 했다. TMR의 역할은 상위 명령, STM32의 최종 출력 판단, 실물 동작과 검증 근거를 한 프로젝트에서 보여주는 것이다. [공개 프로필](https://github.com/pr0ved99) · [학습 목표](../../../../Career-Roadmap/Goal_Roadmap.md) · [기존 직무 기준](01_Robotics_System_Integration_Engineer_Strengths_ko.md)

| 독자가 여는 곳 | 현재 확인한 문제 | 우선 제안 |
|---|---|---|
| GitHub 프로필 | Featured Projects에 Echo Turtle, PetNer, 세탁 자동화, 크레인, 스마트팩토리 5개가 있다. TMR로 바로 가는 행이 없다. | TMR을 첫 행에 놓고 Echo Turtle은 Jetson·ROS 2 인지/항법 사례로 이어 붙인다. PetNer는 기구·전원·상위 제어기 통합 경험으로 구분한다. |
| TIL 기본 브랜치 | 저장소 파일 트리에 TMR이 보이지만 루트 README는 상반기 학습 목표에서 시작한다. 통계 카드 URL 두 곳에 사용자명 자리표시자가 남았다. | 첫 단락 뒤에 대표 프로젝트 링크와 1문장 결과를 둔다. 통계 카드는 빼거나 `pr0ved99`로 고친다. |
| TMR 프로젝트 README | 공개 기본 브랜치는 7월 엔코더 단계다. 작업 브랜치의 최신판에는 149초 영상, 측정·코드 링크가 있지만 여러 날짜의 현황 뒤로 밀려 있다. | 프로필과 TIL은 검토된 작업 브랜치의 프로젝트로 바로 연결한다. 첫 화면은 역할 → 시연 → 대표 검증 3개 순서로 구성하고 날짜별 이력은 진행 색인으로 보낸다. 기본 브랜치 공개본 갱신은 별도 반영 결정을 거친다. |

[공개 TIL](https://github.com/pr0ved99/TIL) · [기본 브랜치 TMR](https://github.com/pr0ved99/TIL/tree/main/Projects/Tracked_Mobile_Robot) · [최신 TMR](https://github.com/pr0ved99/TIL/tree/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot)

## 프로필에 추가할 행

| Project | System Focus | Core Stack |
|---|---|---|
| [Tracked Mobile Robot](https://github.com/pr0ved99/TIL/tree/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot) | 무선 명령에서 모터 출력까지 연결하고, STM32의 정지 판단을 로직 분석기와 실물 주행으로 검증한 궤도 로봇 | STM32F446RE, ESP32-S3, C, UART, PWM, Python |

## TIL 첫 화면에 넣을 문장

> 대표 프로젝트 [Tracked Mobile Robot](https://github.com/pr0ved99/TIL/tree/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot)에서 STM32의 모터 출력 제어와 ESP32 무선 통신을 통합했습니다. 펌웨어 설계 판단을 실제 주행 영상, PWM 파형, ADC 원본 로그로 확인할 수 있습니다.

## TMR 첫 화면 초안

### Tracked Mobile Robot · 무선 궤도 로봇의 구동 제어와 검증

브라우저의 주행 명령을 ESP32-S3가 UART로 전달하고, STM32F446RE가 상태와 명령 유효성을 확인한 뒤에만 모터 출력을 허용하도록 설계했습니다. 명령 유실 뒤에는 새 ARM과 유효한 주행 명령을 모두 받아야 다시 움직입니다. [149초 실물 시연](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/assets/videos/wifi_mvp/2026-10-24/final/TMR_MVP_Final_2026-10-24.mp4) · [상태 머신](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md)

| 검증한 질문 | 결과 | 근거 |
|---|---|---|
| UART 정지 명령 뒤 PWM은 언제 꺼지는가? | 로직 분석기 4 MHz 시험에서 DISARM 프레임 끝부터 두 PWM 출력 비활성까지 23.50 µs. 측정 대상은 제어 핀이다. | [측정 기준점과 파형](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md) |
| ADC가 외부 입력과 내부 기준을 구분하는가? | 세 입력 구간의 유효 표본 2,218개에서 PA4는 입력을 따라 바뀌고 VREFINT 평균은 1500.63~1500.67카운트였다. | [보드 실측과 UART 원본](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/verification/49_PA4_VREFINT_Bench_2026-11-25_ko.md) |
| 상위 주행 스택을 어떻게 검증했는가? | Gazebo의 고정 시험 경로 P05에서 Nav2가 목표까지 4.30 cm 오차로 도착하고 무접촉·2초 이상 정지를 확인했다. 실제 플랫폼의 자율주행은 후속이다. | [경로·실패 회차·재현 명령](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/docs/verification/48_Simulation_Gate02_2026-11-24_ko.md) |

후속 섹션은 시스템 연결도, 상태 머신과 재허가 조건, 빌드·실행 방법, 전체 진행 기록 순으로 둔다. 주행용 앱과 현재 ADC 전용 벤치 이미지의 차이는 실행 안내 첫 줄에 밝힌다. 보호 회로 검증, 실물 Nav2, CAN·FreeRTOS는 각 검증 상태를 붙여 소개한다. 영상과 수치가 보이는 위치까지의 클릭 수는 프로필에서 두 번이면 충분하다.
