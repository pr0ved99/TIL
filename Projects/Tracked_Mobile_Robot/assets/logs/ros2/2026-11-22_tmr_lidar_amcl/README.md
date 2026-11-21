# 2026-11-22 TMR LiDAR·고정 지도·AMCL

[진행 기록](../../../../docs/progress/2026-11-22_progress.md) · [시뮬레이션 인터페이스](../../../../05_ROS2_Integration/README.md)

- [scan_one_meter.yaml](scan_one_meter.yaml)은 벽을 LiDAR 정면 1.000m에 뒀을 때 ROS에서 받은 스캔 원본이다.
- [final_readback.json](final_readback.json)과 [final_gazebo_pose.txt](final_gazebo_pose.txt)는 두 번 전진하고 정지한 뒤 조회한 ROS 메시지·TF 요약과 Gazebo 모델 위치다. JSON의 거리 `null`은 유한한 반환값이 없는 빔을 표시한다.
- [room.sdf](room.sdf), [scan_test_wall.sdf](scan_test_wall.sdf), [room.yaml](room.yaml), [room.pgm](room.pgm)은 검증에 쓴 방 경계, 안쪽 벽과 지도다. 지도 해상도는 5cm/셀이다.

## 같은 시험 조건 다시 열기

TMR 프로젝트 루트에서 ROS 환경과 워크스페이스가 로드된 Bash를 사용한다. 아래 명령을 넣을 각 터미널에서 두 통신 값을 동일하게 설정한다.

```bash
export ROS_DOMAIN_ID=85 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export GZ_PARTITION=tmr-sim04
export TMR_NAV_ROOM="$PWD/assets/logs/ros2/2026-11-22_tmr_lidar_amcl"
```

첫 터미널에서는 `ros2 launch tmr_sim drive.launch.py`를 실행한다. 새 Gazebo 월드에서 두 모델을 한 번씩 생성한다.

```bash
ros2 run ros_gz_sim create -world empty -name tmr_nav_test_room -file "$TMR_NAV_ROOM/room.sdf"
ros2 run ros_gz_sim create -world empty -name scan_test_wall -file "$TMR_NAV_ROOM/scan_test_wall.sdf" -x 1.115 -y 0 -z 0.2
```

지도 서버와 AMCL은 각각 별도 터미널에서 실행한다. AMCL 초기값은 새 월드의 시작 위치 (0, 0, 방향 0°)다.

```bash
ros2 run nav2_map_server map_server --ros-args -p use_sim_time:=true -p yaml_filename:="$TMR_NAV_ROOM/room.yaml"
```

```bash
ros2 run nav2_amcl amcl --ros-args -p use_sim_time:=true -p base_frame_id:=base_footprint \
  -p global_frame_id:=map -p odom_frame_id:=odom -p scan_topic:=/scan -p tf_broadcast:=true \
  -p set_initial_pose:=true -p initial_pose.x:=0.0 -p initial_pose.y:=0.0 -p initial_pose.yaw:=0.0
```

두 노드가 실행된 뒤 별도 터미널에서 활성화한다.

```bash
ros2 lifecycle set /map_server configure && ros2 lifecycle set /map_server activate
ros2 lifecycle set /amcl configure && ros2 lifecycle set /amcl activate
ros2 run tf2_ros tf2_echo map base_footprint
```

RViz에서는 `use_sim_time=true`와 `Fixed Frame=map`을 사용한다. `Map`은 `/map`을 `Transient Local`로 구독하고, `LaserScan`은 `/scan`을 구독한다. 기존 실습에서 별도로 실행했던 임시 노드 이름은 `tmr_nav01_map_server`, `tmr_nav01_amcl`이었다.
