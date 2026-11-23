# SIM-05 Nav2에 EKF 오도메트리 연결

별도 EKF 주행 런처로 바퀴 원본을 `/wheel/odom`에 연결하고 EKF 출력은 `/odom`으로 보냈다. Nav2의 `controller_server`와 `bt_navigator`가 그 출력을 구독했고, 실제 `odom → base_footprint` 송신자는 EKF 하나였다. 고정 지도에서 P05를 29.10초 만에 복구 없이 완주했다. Gazebo 기준 최종 오차는 5.76 cm와 3.16°였다.

| 역할 | ROS 연결 |
| --- | --- |
| 원래 바퀴 오도메트리 | `tmr_drive_bridge` → `/wheel/odom` → `ekf_filter_node` |
| IMU Z축 각속도 | `tmr_drive_bridge` → `/imu/data` → `ekf_filter_node` |
| 융합한 오도메트리 | `ekf_filter_node` → `/odom` → Nav2 |
| 동적 `odom → base_footprint` | EKF가 `/tf`로 송신한다. 원래 바퀴 변환은 진단용 `/wheel/tf`에 분리했다. |

[시험에 쓴 런처](drive_ekf.launch.py)는 기존 패키지의 기본 주행 런처를 포함하고 브리지 노드에만 두 토픽 remap을 적용한다. 같은 `ekf.yaml`을 읽은 뒤 EKF 모드에서 `odom0=/wheel/odom`과 `publish_tf=true`를 적용한다. 기본 바퀴 주행은 `drive.launch.py`를 사용한다.

## 시험 범위

실제 패키지에 새 런처를 넣기 전, 별도 Gazebo 파티션과 로컬 ROS 도메인 75에서 후보 파일을 절대 경로로 기동했다. `headless:=true`, 시드 4101, [11/22 실습 방과 지도](../2026-11-22_tmr_lidar_amcl/README.md)를 사용했다. 원점에서 AMCL을 초기화하고 기본 `tmr_sim navigation.launch.py`로 P05 목표 (1.50 m, 0.55 m, 0°)를 전송했다. 주행 중 Gazebo 모델 중심은 안쪽 벽의 중심선 x=1.115 m를 y=0.837 m에서 통과했다(벽 끝 y=+0.30 m). 이동 거리는 2.061 m였다. 도착 후 2.06초 이상 바퀴 및 필터의 전진·회전 속도 절댓값이 각각 0.001 m/s, 0.001 rad/s 이내였고 최종 명령은 0이었다. 이 1회는 EKF 연결 확인이며 장애물 물리 접촉 횟수는 계측하지 않았다.

[실행 시 토픽 및 파라미터](wiring.json) · [수신한 TF 메시지의 발행자 ID 대조](tf_origin.log) · [목표 결과](result.json) · [월드 및 속도 표본](trace.json.gz)

## 설치된 패키지 런처로 재현

사용자가 EKF 런처와 실행 의존성을 등록했다. 패키지 명령으로 P05를 재현해 복구 없이 도착했고 실제 `odom → base_footprint` 발행자는 EKF 하나였다. 도메인 76의 별도 Gazebo 파티션에서 `ros2 launch tmr_sim drive_ekf.launch.py headless:=true seed:=4101`로 기동했다. P05 목표까지 시뮬레이션 시간은 27.00초, 최종 Gazebo 위치·방향 오차는 1.52 cm와 2.95°였다. 런타임 마스크에서 바퀴 입력은 vx(인덱스 6), IMU 입력은 wz(인덱스 11)만 활성화됐고 `/wheel/tf` 구독자는 없었다. [주행 결과](installed_p05/result.json) · [토픽과 입력 마스크](installed_p05/wiring.json) · [월드·오도메트리 표본](installed_p05/trace.json.gz)
