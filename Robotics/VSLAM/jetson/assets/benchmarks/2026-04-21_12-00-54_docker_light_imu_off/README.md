# 2026-04-21_12-00-54 Docker light IMU off Benchmark

## 목적

- 같은 Docker light 계열 RTAB-Map baseline에서
- BNO08x IMU를 끈 상태와 켠 상태를 같은 방식으로 비교한다.
- 체감 안정성 판단을 보조하기 위해 `topic hz`, odometry quality, delay, 전력 로그를 남긴다.

## 이번 실행 조건

- preset: `light`
- imu mode: `off`
- imu topic: `/imu/disabled`
- wait imu to init: `false`
- duration: `20s`
- color profile: `424x240x15`
- depth profile: `424x240x15`
- detection rate: `2`
- odom profile: `relaxed`
- queue size: `15`
- tmpfs DB/log: `enabled`

## 생성 파일

- `00_compose_ps.txt`: benchmark 당시 compose 서비스 상태
- `01_nodes.txt`: host에서 본 ROS node 목록
- `02_topics.txt`: host에서 본 ROS topic 목록
- `03_odom_info.txt`: 시작 시점 odom_info 샘플
- `04_tf_static.txt`: static TF 샘플
- `05_imu_sample.txt`: IMU 샘플 또는 비활성 상태 확인용 출력
- `10_tegrastats.txt`: Jetson 자원 사용량
- `11_camera.log`: camera service log
- `12_rtabmap.log`: rtabmap service log
- `20_color_hz.txt`: color image topic hz
- `21_aligned_depth_hz.txt`: depth hz
- `22_odom_hz.txt`: /rtabmap/odom hz
- `23_mapdata_hz.txt`: /rtabmap/mapData hz
- `24_imu_hz.txt`: /imu/data hz
- `90_summary.env`: 자동 생성된 핵심 숫자 요약
- `91_summary.md`: 사람이 읽기 쉬운 자동 요약
