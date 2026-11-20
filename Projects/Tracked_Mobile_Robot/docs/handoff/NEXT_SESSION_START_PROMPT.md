# 다음 세션 시작 프롬프트

Tracked_Mobile_Robot 프로젝트를 이어서 진행하자. 루트/프로젝트 AGENTS.md, [현재 인수인계](CURRENT_SESSION_CONTEXT.md) 상단, [11/20 진행 기록](../progress/2026-11-20_progress.md), [Ubuntu 로드맵](../plans/2026-11-17_Ubuntu_Nav2_Simulation_and_RL_Roadmap_ko.md)의 마감 안내를 읽어.

Ubuntu 설치와 기본 초기 설정을 마쳤고 VS Code·Terminator·Chrome을 설치했다. Linux 파일시스템의 TIL 개발 브랜치 `agent/dual-encoder-bringup`을 VS Code/Codex에서 연다. 현재 저장소 경로·브랜치·커밋과 Ubuntu 버전부터 확인하고 ROS 2 Jazzy와 Gazebo Harmonic의 기존 설치 여부를 점검한다. 이어서 기본 설치와 ROS 2 송수신 및 Gazebo 창·월드 실행을 확인하자. [설치 실행서](../plans/2026-11-20_HP_Victus_Windows_Ubuntu_Dual_Boot_Runbook_ko.md)는 수행 이력과 확인 명령 참고용이다.

별도 실물 작업으로 첫 ADC 입력을 확인한다. NUCLEO-F446RE + 저전압 시험 입력·임시 배선 + 시리얼로 실제 raw를 PC CSV에 남기는 것이 초기 목표다. 가상 로봇 구동과 PCB 상세 설계는 ADC 실측을 기다리지 않는다. 보드·핀·입력 조건은 [세부 계획 §8](../plans/2026-11-18_Detailed_Design_to_Final_Completion_Plan_ko.md#8-첫-실제-데이터와-펌웨어표시-구현)을 따른다.

기존 무선 수동 주행과 149초 기능 시연은 확보했다. 추가 MVP 마감 작업은 보류 상태다. 지난 실물 상태는 현재 인수인계의 마지막 사용자 보고를 따르고, 전원 분리 완료를 가정하지 마. 무관한 Git 변경과 기존 검증 근거는 보존한다. 이번 세션은 Ubuntu의 개발 환경 확인부터 시작한다.
