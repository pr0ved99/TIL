# GATE-01 · 노트북 시뮬레이션 1차 리뷰

**판정은 GO다.** 로드맵의 사전 기준을 충족해 별도 2D Gymnasium 환경(RL-01) 착수가 가능하다. 앞으로 규칙 제어와 학습 정책을 같은 환경에서 비교한다. 현재 TMR 시뮬레이션의 주행 기준선은 Nav2다.

평가 범위는 가상 TMR의 목표 도달·정지, 센서 좌표계, 모의 주행 요청 처리다. 정식 Nav2 평가는 바퀴 오도메트리로 방 B에서 수행했다. EKF는 별도 주행으로 검증했다. [사전 기준](../plans/2026-11-17_Ubuntu_Nav2_Simulation_and_RL_Roadmap_ko.md#6-평가-기준과-rl-범위)

| 검토 항목 | 확인한 근거 |
|---|---|
| ROS 2·Gazebo·RViz | Ubuntu 24.04, Jazzy, Gazebo Harmonic에서 기존 GUI 목표 도달 기록과 현재 설치 버전을 대조했다. [GUI 실습 기록](../progress/2026-11-20_progress.md) · [환경 버전](../../assets/logs/ros2/2026-11-23_tmr_nav03_evaluation/environment.json) |
| ENV-03 빈 월드 | 설치된 `empty.sdf`를 별도 Gazebo 파티션에서 `gz sim -s -r`로 실행하고 `/world/empty/stats`를 관측했다. 실제 경과 300.032초, 시뮬레이션 경과 299.997초, 통계 메시지 2,983개, 최대 수신 간격 0.102초였다. 관측 중 서버가 실행 중이었고 표본의 일시정지 표시는 모두 false였다. [시계·반복 횟수 CSV](../../assets/logs/ros2/2026-11-24_tmr_env03_empty_world/stats.csv) · [월드 경로와 패키지 버전](../../assets/logs/ros2/2026-11-24_tmr_env03_empty_world/result.json) |
| TF·오도메트리 | 바퀴 모드 대표 bag의 TF 메시지에서 `map → odom → base_footprint → base_link → laser_frame` 경로를 확인했다. EKF 별도 P05의 설치본에서는 `/odom` 발행자가 `ekf_filter_node` 하나였고 `odom → base_footprint` 송신자 추적에서도 같은 노드가 관측됐다. [대표 bag](../../assets/logs/ros2/2026-11-23_tmr_nav03_evaluation/P05-4101_bag/metadata.yaml) · [EKF 배선](../../assets/logs/ros2/2026-11-23_tmr_nav_ekf/installed_p05/wiring.json) · [TF 송신 기록](../../assets/logs/ros2/2026-11-23_tmr_nav_ekf/installed_p05/tf_origin.log) |
| Nav2 주행 재현성 | 고정 5경로 × 4시드에서 목표 도달·정지 20/20, 장애물 접촉 0회였다. 목표 좌표와 Gazebo 최종 자세로 다시 계산한 최대 위치 오차는 0.1451 m, 방향 오차는 5.30°였다. 사전 기준은 성공 18/20 이상, 접촉 0회, 위치 0.20 m·방향 10° 이내다. 실패표는 0행이고 대표 bag의 10개 토픽에서 메시지 40,208개를 다시 읽었다. [평가 조건](../../assets/logs/ros2/2026-11-23_tmr_nav03_evaluation/protocol.yaml) · [회차별 CSV](../../assets/logs/ros2/2026-11-23_tmr_nav03_evaluation/results.csv) · [실패표](../../assets/logs/ros2/2026-11-23_tmr_nav03_evaluation/failures.csv) |
| 취소·센서 유실 | 주행 중 취소 요청 후 0.204초, 마지막 스캔 후 1.090초에 오도메트리 정지가 기록됐다. 시간은 시뮬레이션 시각이며 두 시험의 접촉은 0회였다. [보조 시험 CSV](../../assets/logs/ros2/2026-11-23_tmr_nav03_evaluation/auxiliary.csv) |
| SIM-06 | 전압·전류·온도의 저장 표본으로 16개 시나리오를 재생해 모의 서비스 응답을 대조했다. 최근 유효 표본 3개는 통과, 채널별 무효·중단 및 전체 발행 중단은 보류, 복구는 다시 통과했다. 두 번째 구독자에서 원 측정 시각, 재생 시각, 값·단위·유효 표시를 확인했다. [응답 CSV](../../assets/logs/ros2/2026-11-24_tmr_sim06_replay/requests.csv) · [수신 표본](../../assets/logs/ros2/2026-11-24_tmr_sim06_replay/wire_samples.json) |

P05 시드 4103에서는 주행 중 한 번 복구 동작을 수행한 뒤 도착했다. 결과는 이 방·모델·속도 설정에 한정한다. 모의 서비스는 요청 시점의 표본을 평가해 응답한다. 실물의 단선 검출, 제동, 전류·온도·저전압 임계값은 별도 검증 범위다.
