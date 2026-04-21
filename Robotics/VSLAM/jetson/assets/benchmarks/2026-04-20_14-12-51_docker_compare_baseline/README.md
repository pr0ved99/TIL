# 2026-04-20_14-12-51 Docker compare Baseline Benchmark

## 목적

- `Docker` 분리 서비스 구조에서
- 현재 preset으로 `D435i color/depth + RTAB-Map` backend가 얼마나 가볍게 도는지
- `tegrastats`, `topic hz`, service log 기준으로 남긴다.

## 이번 실행 조건

- preset: `compare`
- duration: `20s`
- color profile: `424x240x15`
- depth profile: `424x240x15`
- detection rate: `3`
- odom profile: `relaxed`
- queue size: `20`
- tmpfs DB/log: `enabled`

## 생성 파일

- `00_compose_ps.txt`: benchmark 당시 compose 서비스 상태
- `01_nodes.txt`: host에서 본 ROS node 목록
- `02_topics.txt`: host에서 본 ROS topic 목록
- `03_odom_info.txt`: 시작 시점 odom_info 샘플
- `10_tegrastats.txt`: Jetson 자원 사용량
- `11_camera.log`: camera service log
- `12_rtabmap.log`: rtabmap service log
- `20_color_hz.txt`: color image topic hz
- `21_aligned_depth_hz.txt`: aligned depth topic hz
- `22_odom_hz.txt`: /rtabmap/odom hz
- `23_mapdata_hz.txt`: /rtabmap/mapData hz
