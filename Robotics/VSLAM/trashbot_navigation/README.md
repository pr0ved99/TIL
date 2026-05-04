# Trashbot Navigation

## 결론

`trashbot_navigation`은 Mari Gazebo + RTAB-Map 결과를 Nav2에 연결하기 위한 1차 자율주행 패키지다.

1차 목표는 안정적인 Gazebo `/odom` 기준으로 RViz에서 `2D Goal Pose`를 찍었을 때 Nav2가 `/cmd_vel`을 만들고 Mari가 움직이는지 확인하는 것이다.

초기 테스트는 큰 공원 world가 아니라 단계별 Nav2 훈련 world에서 시작한다.

## 1차 구조

```text
Gazebo Nav2 stage world
-> /odom
-> RTAB-Map map->odom TF
-> depthimage_to_laserscan /scan
-> scan-only rolling global/local costmaps
-> Nav2
-> /cmd_vel
-> Mari planar move
```

RTAB-Map is still useful for map visualization and `map->odom`, but the first
Nav2 training profile does not feed `/rtabmap/map` directly into the global
costmap. RGB-D occupancy maps can be too noisy for early navigation debugging,
so Nav2 starts with scan-only rolling costmaps.

## Depth-To-Scan Defaults

Mari's camera is low, so a thick depth slice can project the ground or robot body
as a fake LaserScan wall. The default Nav2 launch therefore uses:

- `scan_frame=camera_link`
- `scan_height=8`
- `range_min=0.30`

`scan_frame` must stay in the x-forward camera body frame. Do not use
`camera_color_optical_frame` for Nav2 LaserScan, because optical frames are
z-forward and can make obstacle positions look wrong in the costmap.

If a white dotted wall appears near the robot in RViz, first try:

```bash
ros2 launch trashbot_navigation mari_nav2_rtabmap.launch.py scan_height:=4 range_min:=0.35
```

Then check `/scan` close-range counts:

```bash
python3 Tools/check_mari_nav2_topics.py --duration 8
```

## Obstacle Avoidance Defaults

The Stage 2 avoidance profile is tuned to make the first detour possible, not to
be the final navigation profile.

- `robot_radius=0.12`
- `inflation_radius=0.18`
- global rolling costmap: `16 m x 16 m`
- planner: Navfn with A* enabled
- controller max speed: `0.12 m/s`, max yaw rate: `0.70 rad/s`

If obstacles are detected but Mari does not go around them, first verify that
`/plan` is published after an RViz goal:

```bash
ros2 topic echo /plan --once
python3 Tools/check_mari_nav2_topics.py --duration 8 --expect-cmd-vel
```

This scan-only profile can accept goals inside the rolling global costmap. If a
goal is much farther than the `16 m x 16 m` window, Nav2 may reject it without
planning. Use a closer staged goal or switch to a static-map profile later.

## Saved Map Profile

Saved-map navigation is the next step after the scan-only smoke test.

The flow is:

```text
RTAB-Map /rtabmap/map
-> map_saver_cli
-> saved YAML/PGM map
-> map_server + AMCL
-> Nav2 static global costmap + live /scan obstacle layer
```

Use this when a goal is too far for the rolling global costmap, or when the
test needs to prove that Mari can navigate on a prebuilt map.

Build a Stage 2 map with the map-builder launch:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py
```

This map builder converts depth to a thin `/scan` and tells RTAB-Map to build
the 2D occupancy grid from that scan. It is cleaner for Nav2 than saving the
full depth-cloud occupancy map directly.

Save the Stage 2 map:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
mkdir -p assets/2026-05-01_mari_nav2_saved_map_smoke
ros2 run nav2_map_server map_saver_cli \
  -t /rtabmap/map \
  -f assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap \
  --fmt pgm \
  --mode trinary \
  --occ 0.65 \
  --free 0.25
```

If the saved map still has many random occupied cells, rebuild it with stricter
depth-to-scan limits:

```bash
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py \
  scan_height:=3 \
  range_min:=0.40 \
  grid_range_min:=0.40 \
  grid_range_max:=2.50 \
  linear_update:=0.12 \
  angular_update:=0.12
```

Then stop RTAB-Map and start saved-map Nav2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml
```

In RViz, set `2D Pose Estimate` first. AMCL needs an initial pose before the
saved map can be used reliably for planning.

## 왜 /odom부터 쓰는가

`/odometry/local`은 encoder+IMU 구조 후보로 동작하지만 아직 RTAB-Map 내부 불확실도가 `/odom` baseline보다 크다.

그래서 1차 Nav2 smoke test는 안정적인 `/odom`으로 진행한다. 이 단계가 성공하면 같은 Nav2 설정에서 odometry input을 `/odometry/local`로 바꿔 비교한다.

## 실행 순서

Terminal 1:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description gazebo_mari_nav2_stage0_empty.launch.py
```

Stage를 올릴 때는 Terminal 1만 바꾼다.

```bash
ros2 launch trashbot_description gazebo_mari_nav2_stage1_straight_path.launch.py
ros2 launch trashbot_description gazebo_mari_nav2_stage2_obstacles.launch.py
ros2 launch trashbot_description gazebo_mari_nav2_stage3_small_loop.launch.py
ros2 launch trashbot_description gazebo_mari_large_park_realsense_light.launch.py
```

Terminal 2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py
```

저장 맵을 만들 때는 Terminal 2를 아래 명령으로 바꾼다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py
```

Terminal 3:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_rtabmap.launch.py
```

RViz에서 `2D Goal Pose`를 누르고 Mari 앞쪽의 가까운 지점을 찍는다.

저장 맵 profile을 쓸 때는 Terminal 2의 RTAB-Map을 끄고, Terminal 3을 아래로 바꾼다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml
```

## 확인할 topic

```bash
ros2 topic hz /scan
ros2 topic hz /cmd_vel
ros2 topic echo /cmd_vel --once
ros2 topic hz /global_costmap/costmap
ros2 topic hz /local_costmap/costmap
```

또는 한 번에 확인한다.

```bash
python3 Tools/check_mari_nav2_topics.py --duration 8
python3 Tools/check_mari_nav2_topics.py --duration 8 --expect-cmd-vel
```

## 성공 기준

- `/scan`이 10 Hz 이상으로 나온다.
- Nav2 lifecycle nodes가 active 상태가 된다.
- RViz goal 입력 후 `/cmd_vel`이 발행된다.
- Gazebo에서 Mari가 목표 방향으로 움직인다.

## 단계별 world

| Stage | 목적 | 성공 기준 |
| --- | --- | --- |
| 0 Empty | Nav2 기본 연결 확인 | RViz goal 후 `/cmd_vel` 발행과 Mari 이동 |
| 1 Straight | 직선 추종 확인 | 가까운 직선 goal까지 흔들림 없이 이동 |
| 2 Obstacles | 장애물 감지/회피 확인 | `/scan`과 costmap에 장애물이 찍히고 우회 명령 생성 |
| 3 Small Loop | RTAB-Map + Nav2 통합 확인 | 작은 loop 경로에서 map과 path가 무너지지 않음 |
| 4 Large Park | 데모/최종 확인 | 긴 주행과 발표용 시각 결과 확인 |

## 다음 단계

- `/odom` 기준 Nav2 smoke test 성공
- `/odometry/local` 기준 Nav2 재실행
- 같은 goal에서 주행 흔들림, 회전량, 장애물 회피 품질 비교
