# 다음 세션 시작 프롬프트

Tracked_Mobile_Robot 프로젝트를 이어서 진행하자. 루트/프로젝트 AGENTS.md, [현재 인수인계](CURRENT_SESSION_CONTEXT.md) 상단, [11/22 진행 기록](../progress/2026-11-22_progress.md), [Ubuntu 로드맵](../plans/2026-11-17_Ubuntu_Nav2_Simulation_and_RL_Roadmap_ko.md)의 마감 안내를 읽어.

Ubuntu 24.04.5·ROS 2 Jazzy·Gazebo Harmonic에서 TMR 기본 주행, 가상 2D LiDAR, 고정 지도와 AMCL을 확인했다. 다음은 **NAV-02 첫 목표 이동**이다. [실습 월드·지도 재현](../../assets/logs/ros2/2026-11-22_tmr_lidar_amcl/README.md)으로 도메인 85에서 먼저 `/scan`, `/map`, `map → base_footprint`를 확인한다. Nav2의 최종 속도 출력 타입·단위, 단일 `/cmd_vel` 발행 경로, TMR 외곽과 LiDAR 장애물 반영을 확인한 뒤 사용자가 RViz에서 처음 한 목표를 지정한다. 목표·시작·종료 좌표와 정지를 남긴다. 가상 IMU/EKF, 취소와 경로 차단 비교는 후속이다. [TMR 모델과 인터페이스](../../05_ROS2_Integration/README.md)

별도 실물 작업으로 첫 ADC 입력을 확인한다. NUCLEO-F446RE + 저전압 시험 입력·임시 배선 + 시리얼로 실제 raw를 PC CSV에 남기는 것이 초기 목표다. 가상 로봇 구동과 PCB 상세 설계는 ADC 실측을 기다리지 않는다. 보드·핀·입력 조건은 [세부 계획 §8](../plans/2026-11-18_Detailed_Design_to_Final_Completion_Plan_ko.md#8-첫-실제-데이터와-펌웨어표시-구현)을 따른다.

기존 무선 수동 주행과 149초 기능 시연은 확보했다. 추가 MVP 마감 작업은 보류 상태다. 지난 실물 상태는 현재 인수인계의 마지막 사용자 보고를 따르고, 전원 분리 완료를 가정하지 마. 무관한 Git 변경과 기존 검증 근거는 보존한다.
