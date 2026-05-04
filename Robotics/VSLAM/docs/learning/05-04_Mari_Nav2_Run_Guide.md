# Mari Nav2 Run Guide

## 결론

Mari 자율주행은 바로 센서 기반 odometry부터 시작하지 않고, 먼저 Gazebo `/odom` 기준으로 Nav2가 `/cmd_vel`을 생성하는지 확인한다.

이유는 단순하다. `/odom`은 현재 가장 안정적인 위치 입력이고, 이 기준에서 Nav2가 성공해야 이후 `/odometry/local` 문제를 분리해서 볼 수 있다.

또한 첫 테스트는 큰 공원 world가 아니라 단계별 Nav2 훈련 world에서 시작한다. 큰 공원 world는 데모와 최종 통합 검증용이고, Nav2 초기 디버깅에는 변수가 너무 많다.

## 1차 목표

```text
RViz에서 2D Goal Pose 입력
-> Nav2가 경로 생성
-> Nav2가 /cmd_vel 발행
-> Gazebo에서 Mari 이동
```

이 단계의 목적은 완벽한 자율주행이 아니라, 자율주행 파이프라인이 처음부터 끝까지 연결되는지 확인하는 것이다.

## 기본 구조

```text
Gazebo /odom
RTAB-Map map->odom TF
RGB-D depth image -> depthimage_to_laserscan -> /scan
Nav2 rolling costmap
Nav2 -> /cmd_vel
```

용어 정리:

- Nav2: ROS2의 대표 자율주행 패키지. 목표 위치까지 경로를 만들고 속도 명령을 낸다.
- costmap: 장애물과 지나갈 수 있는 영역을 격자 지도처럼 표현한 것.
- `/scan`: LiDAR처럼 보이는 거리 데이터. 여기서는 depth image를 변환해서 만든다.

1차 Nav2 훈련에서는 RTAB-Map의 `/rtabmap/map`을 Nav2 global costmap의 static map으로 바로 넣지 않는다. RGB-D 기반 occupancy map은 바닥과 원거리 depth noise가 섞이면 화면이 빽빽해질 수 있기 때문이다. RTAB-Map은 `map->odom` TF와 시각화용으로 유지하고, Nav2 장애물 판단은 `/scan` 기반 rolling costmap으로 먼저 안정화한다.

저장된 맵 기반 주행은 그 다음 단계다. 먼저 RTAB-Map으로 `/rtabmap/map`을 충분히 깨끗하게 만든 뒤 파일로 저장하고, 이후에는 RTAB-Map을 끈 상태에서 `map_server + AMCL + Nav2`로 주행한다.

주의할 점은 `/rtabmap/map`을 어떻게 만들었는지다. 전체 RGB-D depth cloud로 occupancy map을 만들면 낮은 카메라가 본 바닥/원거리 depth noise가 장애물처럼 들어갈 수 있다. Nav2 저장 맵을 만들 때는 `mari_nav2_map_builder.launch.py`를 사용한다. 이 launch는 depth image를 얇은 `/scan`으로 바꾼 뒤, RTAB-Map의 2D occupancy grid를 `/scan` 기준으로 만든다.

## Depth-To-Scan 주의점

Mari의 카메라는 낮은 위치에 있어서 depth image의 여러 줄을 한꺼번에 `/scan`으로 압축하면 바닥이나 로봇 몸체가 벽처럼 들어올 수 있다.

그래서 Nav2 기본 launch는 `scan_frame=camera_link`, `scan_height=8`, `range_min=0.30`으로 둔다. `scan_frame`은 LaserScan 좌표계다. LaserScan은 x축 전방, y축 좌우인 2D 평면으로 해석되므로 `camera_color_optical_frame`처럼 z축이 전방인 optical frame을 쓰면 물체 위치가 이상하게 costmap에 투영될 수 있다. `scan_height`는 LaserScan으로 변환할 depth image의 세로 줄 수이고, 값이 너무 크면 바닥면이 장애물 선처럼 costmap에 찍힌다. `range_min`은 너무 가까운 거리값을 버리는 기준이고, 카메라 박스나 차체 일부가 자기 장애물로 들어오는 것을 줄인다.

RViz에서 흰색 점선이 로봇 근처에 계속 생기면 아래 순서로 본다.

```bash
python3 Tools/check_mari_nav2_topics.py --duration 8
ros2 launch trashbot_navigation mari_nav2_rtabmap.launch.py scan_height:=4 range_min:=0.35
```

첫 번째 명령에서 `/scan`의 `lt0.30`, `lt0.45` 값이 계속 크면 가까운 자기 몸체성 포인트가 들어오는 상태다. 두 번째 명령처럼 더 얇은 scan 또는 더 큰 minimum range로 재확인한다.

`/scan`의 frame이 `camera_color_optical_frame`으로 보이면 Terminal 3을 재시작한다. 수정된 기본값에서는 `frame=camera_link`가 나와야 한다.

## 장애물 우회 튜닝

장애물이 보이는데 우회하지 못하면 해상도를 먼저 올리지 않는다. 먼저 아래 항목을 본다.

- `robot_radius`: 로봇을 얼마나 크게 볼지 정하는 값.
- `inflation_radius`: 장애물 주변 안전거리를 얼마나 크게 둘지 정하는 값.
- global costmap 크기: 목표와 장애물을 같이 보고 돌아갈 공간이 충분한지.
- planner: 장애물 옆 경로를 실제로 찾는지.

Mari의 현재 Nav2 훈련 profile은 차체 크기에 맞춰 `robot_radius=0.12`, `inflation_radius=0.18`로 둔다. global costmap은 `16 m x 16 m` rolling window이고, planner는 A*를 켠다. 이 설정은 완전한 최종값이 아니라 Stage 2 장애물 회피를 통과하기 위한 시작점이다.

우회 테스트는 장애물 바로 뒤가 아니라 장애물 옆으로 돌아갈 수 있는 목표부터 찍는다. 다만 scan-only rolling costmap은 정적 지도를 쓰지 않으므로, 16 m 창 밖의 아주 먼 goal은 여전히 바로 계획할 수 없다. 더 먼 goal은 RTAB-Map static map을 Nav2 global costmap에 넣는 별도 profile에서 다룬다.

## 단계별 world

| Stage | World | Launch | 목적 |
| --- | --- | --- | --- |
| 0 | `mari_nav2_stage0_empty.world` | `gazebo_mari_nav2_stage0_empty.launch.py` | `/cmd_vel` 생성과 기본 이동 확인 |
| 1 | `mari_nav2_stage1_straight_path.world` | `gazebo_mari_nav2_stage1_straight_path.launch.py` | 직선 목표 추종과 속도/가속도 튜닝 |
| 2 | `mari_nav2_stage2_obstacles.world` | `gazebo_mari_nav2_stage2_obstacles.launch.py` | depth-to-scan, costmap, 장애물 회피 확인 |
| 3 | `mari_nav2_stage3_small_loop.world` | `gazebo_mari_nav2_stage3_small_loop.launch.py` | 작은 loop형 공원에서 RTAB-Map + Nav2 통합 확인 |
| 4 | `mari_nav2_stage4_repeat_course.world` | `gazebo_mari_nav2_stage4_repeat_course.launch.py` | 촘촘한 장애물 반복주행과 safe-clearance 검증 |
| Demo | `mari_large_park_test.world` | `gazebo_mari_large_park_realsense_light.launch.py` | 발표/데모용 큰 공원 최종 검증 |

처음에는 Stage 0부터 시작한다.

## 실행 명령어

Terminal 1: Gazebo Stage 0

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description gazebo_mari_nav2_stage0_empty.launch.py
```

Stage를 올릴 때는 Terminal 1 명령만 아래 중 하나로 바꾼다.

```bash
ros2 launch trashbot_description gazebo_mari_nav2_stage1_straight_path.launch.py
ros2 launch trashbot_description gazebo_mari_nav2_stage2_obstacles.launch.py
ros2 launch trashbot_description gazebo_mari_nav2_stage3_small_loop.launch.py
ros2 launch trashbot_description gazebo_mari_nav2_stage4_repeat_course.launch.py
ros2 launch trashbot_description gazebo_mari_large_park_realsense_light.launch.py
```

Terminal 2: RTAB-Map `/odom` baseline

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py
```

Terminal 3: Nav2 + depth to scan + RViz

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_rtabmap.launch.py
```

## RViz에서 할 일

1. RTAB-Map map이 어느 정도 쌓일 때까지 Mari를 짧게 움직인다.
2. RViz에서 `2D Goal Pose`를 선택한다.
3. Mari 앞쪽의 가까운 지점을 클릭하고 방향을 드래그한다.
4. Gazebo에서 Mari가 목표 방향으로 움직이는지 본다.

처음에는 먼 목표를 찍지 않는다. 가까운 목표로 `/cmd_vel`이 만들어지는지만 확인한다.

## 확인 명령어

```bash
ros2 topic hz /scan
ros2 topic hz /cmd_vel
ros2 topic echo /cmd_vel --once
ros2 topic hz /global_costmap/costmap
ros2 topic hz /local_costmap/costmap
ros2 topic echo /plan --once
```

한 번에 확인하려면 아래 스크립트를 쓴다.

```bash
python3 Tools/check_mari_nav2_topics.py --duration 8
python3 Tools/check_mari_nav2_topics.py --duration 8 --expect-cmd-vel
```

## 저장된 맵 기반 주행

scan-only rolling costmap은 가까운 goal과 장애물 회피를 보기 좋지만, 아주 먼 goal은 global costmap 창 밖으로 나갈 수 있다. 그래서 넓은 구역을 주행하려면 먼저 맵을 저장하고, 그 맵을 Nav2의 static map으로 써야 한다.

용어 정리:

- `map_server`: 저장된 지도 파일을 `/map` topic으로 다시 올려주는 노드.
- `AMCL`: 저장된 지도와 현재 `/scan`을 비교해서 로봇이 지도 위 어디에 있는지 맞추는 노드.
- static map: 주행 전에 미리 만들어 둔 지도.

1단계: Stage 2 world에서 RTAB-Map 맵을 만든다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description gazebo_mari_nav2_stage2_obstacles.launch.py
```

다른 터미널, Nav2 저장 맵 생성용 RTAB-Map:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py
```

이 launch는 기본적으로 RTAB-Map GUI와 RViz를 같이 띄운다.

- RTAB-Map GUI: 3D point cloud가 잘 쌓이는지 확인한다.
- RViz: `/rtabmap/map` 2D occupancy map, `/scan`, TF, RobotModel을 같이 확인한다.

즉, RTAB-Map 화면에서는 3D로 좋아 보이는데 RViz의 2D 맵이 지저분하면 저장 맵으로 쓰기 전에 다시 필터링해야 한다. RViz까지 띄우는 것이 무거우면 `start_rviz:=false`를 붙인다.

Stage 2에서 맵이 점 형태로 지저분하게 나오면, 처음부터 아래 보수 설정으로 다시 만든다. 현재 clean saved map은 이 계열의 설정으로 확인했다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py \
  scan_height:=2 \
  range_min:=0.45 \
  range_max:=2.50 \
  grid_range_min:=0.45 \
  grid_range_max:=2.50 \
  linear_update:=0.15 \
  angular_update:=0.15
```

이 명령을 실행하면 `mari_rtabmap_2d_map_debug.rviz`가 같이 열린다. 왼쪽 Displays에서 `RTAB-Map 2D Occupancy /rtabmap/map`이 실제 저장 대상이고, `Depth-To-Scan /scan`은 그 2D 맵을 만들기 위한 입력이다.

다른 터미널:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.08 \
  --angular-speed 0.45 \
  --key-timeout 1.2
```

teleop은 기본적으로 즉각 반응하는 step command mode다. 키를 누르면 목표 속도가 바로 `/cmd_vel`로 나간다. 맵이 너무 튀어서 일부러 서서히 움직이고 싶을 때만 `--smooth --linear-accel ... --angular-accel ...`를 붙인다.

2단계: RTAB-Map 화면에서 맵이 충분히 쌓이면 저장한다.

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

2-1단계: 저장 맵에 작은 검은 점 노이즈가 많으면 후처리한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/filter_nav2_saved_map.py \
  assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml \
  --output-prefix assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered \
  --min-occupied-neighbors 1 \
  --min-obstacle-pixels 12
```

3단계: RTAB-Map과 teleop을 종료한다. Gazebo는 그대로 두거나, 같은 stage world로 다시 켠다.

4단계: 저장된 맵 기반 Nav2를 실행한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml
```

후처리 맵을 사용하려면 `map:=...filtered.yaml`로 실행한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered.yaml
```

더 강한 후처리 맵을 비교하려면 아래를 사용한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered_strict.yaml
```

RViz가 뜨면 바로 goal을 찍지 말고 먼저 `2D Pose Estimate`로 Mari의 시작 위치를 맵 위에 맞춘다. 그 다음 `Nav2 Goal`을 찍는다.

확인:

```bash
python3 Tools/check_mari_nav2_topics.py --duration 8 --map-topic /map
python3 Tools/check_mari_nav2_topics.py --duration 8 --map-topic /map --expect-cmd-vel
ros2 topic echo /plan --once
```

현재 Stage 2 saved-map smoke에서 확인된 기준값은 아래다.

```text
/scan: OK, 15.0 Hz, frame=camera_link
/global_costmap/costmap: OK, 0.7 Hz, frame=map
/local_costmap/costmap: OK, 2.7 Hz, frame=odom
/plan: OK, 1.0 Hz, frame=map, poses=37
/cmd_vel: OK, 137.8 Hz, linear_x=0.111, angular_z=0.396
RViz Navigation / Localization / Feedback: active
```

이후 같은 Stage 2 saved map 실행에서 목표 지점까지 만족스럽게 도착하는 것을 확인했다. 따라서 Stage 2는 1차 성공으로 보고, 다음은 Stage 3 small loop world에서 같은 절차를 반복한다.

`/map`이 check script에서 `count=0`으로 나와도 바로 실패로 보지는 않는다. 저장 맵은 static map 성격이라 짧은 확인 시간 동안 새 메시지가 안 잡힐 수 있다. 이때는 RViz에 map이 보이는지, AMCL이 active인지, global costmap과 `/plan`이 생성되는지를 함께 본다.

중요한 전제는 저장 맵 품질이다. 평지가 장애물로 들어간 상태에서 저장하면 Nav2도 그 잘못된 장애물을 그대로 믿는다. 따라서 저장 맵 주행 테스트는 `04_nav2_scan_only_costmap_obstacle_detection_ok.png`처럼 평지 오인식이 줄어든 상태를 기준으로 진행한다.

저장된 맵이 점으로 지저분하게 나오면 아래처럼 더 보수적인 map-builder 값으로 다시 만든다.

```bash
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py \
  scan_height:=2 \
  range_min:=0.45 \
  range_max:=2.50 \
  grid_range_min:=0.45 \
  grid_range_max:=2.50 \
  linear_update:=0.15 \
  angular_update:=0.15
```

이 설정은 가까운 자기 몸체/바닥 포인트와 먼 거리 depth noise를 더 많이 버린다. 단점은 멀리 있는 얇은 장애물은 덜 잡힐 수 있다는 것이다.

## 실패할 때 먼저 볼 것

- `/scan`이 없으면 depth topic과 camera_info topic 이름을 확인한다.
- RViz goal 후 `/cmd_vel`이 없으면 Nav2 lifecycle node가 active인지 확인한다.
- 경로가 안 나오면 `map->odom` TF와 `/global_costmap/costmap`이 있는지 확인한다.
- 저장 맵 profile에서 경로가 안 나오면 `/map`이 있는지, 그리고 RViz `2D Pose Estimate`를 넣었는지 먼저 확인한다.
- Mari가 반응하지 않으면 Gazebo가 `/cmd_vel`을 구독 중인지 확인한다.

## 2차 목표

`/odom` 기준 smoke test가 성공하면, 같은 Nav2 설정에서 odometry input을 `/odometry/local`로 바꾼다.

그때 비교할 기준은 아래다.

- 목표까지 가는지
- 회전이 덜 돌거나 과하게 도는지
- 장애물 앞에서 멈추는지
- `/cmd_vel`이 너무 뚝뚝 끊기지 않는지
- RTAB-Map map이 주행 중 깨지지 않는지

## Stage 3 Small Loop 다음 절차

Stage 2 saved-map goal 주행이 성공했으므로 다음 단계는 Stage 3 작은 loop형 world다. 여기서는 단순 장애물 몇 개가 아니라, loop 경로와 분기 구조가 있는 작은 공원형 환경에서 같은 절차가 통하는지 본다.

1단계: Stage 3 Gazebo world 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description gazebo_mari_nav2_stage3_small_loop.launch.py
```

2단계: Stage 3 map builder 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py \
  scan_height:=2 \
  range_min:=0.45 \
  range_max:=2.50 \
  grid_range_min:=0.45 \
  grid_range_max:=2.50 \
  linear_update:=0.15 \
  angular_update:=0.15
```

이때 RViz에서는 `/rtabmap/map`이 흰색 자유공간과 검은색 장애물로 깨끗하게 나오는지 확인한다. RTAB-Map의 3D point cloud만 보고 저장하지 않는다.

3단계: teleop으로 천천히 loop를 한 바퀴 돌며 맵 생성

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.06 \
  --angular-speed 0.35 \
  --key-timeout 1.2
```

4단계: 맵 저장

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
mkdir -p assets/2026-05-02_mari_nav2_stage3_saved_map_smoke
ros2 run nav2_map_server map_saver_cli \
  -t /rtabmap/map \
  -f assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap \
  --fmt pgm \
  --mode trinary \
  --occ 0.65 \
  --free 0.25
```

5단계: 저장 맵 후처리

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/filter_nav2_saved_map.py \
  assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap.yaml \
  --output-prefix assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap_filtered \
  --min-occupied-neighbors 1 \
  --min-obstacle-pixels 12
```

6단계: Stage 3 저장 맵 기반 Nav2 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap_filtered.yaml
```

RViz에서 `2D Pose Estimate`로 시작 위치를 맞춘 뒤 `Nav2 Goal`을 찍는다.

7단계: safe-clearance profile 비교 실행

장애물 가까이에서 멈추거나 얼어붙는 현상을 비교할 때는 같은 Gazebo world, 같은 저장 맵, 같은 시작 위치, 같은 goal을 유지하고 `params_file`만 바꾼다.

기존 profile:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap_filtered.yaml \
  params_file:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/config/mari_nav2_saved_map_params.yaml
```

safe-clearance profile:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap_filtered.yaml \
  params_file:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/config/mari_nav2_saved_map_safe_clearance_params.yaml
```

safe-clearance profile은 기존 profile보다 약간 더 큰 obstacle buffer를 두되, Stage 4처럼 좁은 gate가 있는 코스에서는 통로가 닫히지 않도록 balanced 값으로 둔다. 현재 기준은 `inflation_radius=0.22`, `cost_scaling_factor=4.5`, `BaseObstacle.scale=0.18`이다. RViz에서는 `/global_costmap/costmap`, `/local_costmap/costmap`, `/plan`이 장애물에서 떨어지면서도 gate 사이 통로를 유지하는지 확인한다.

저장 맵 기반 Nav2 profile의 기본 자율주행 속도는 `max_vel_x=0.40 m/s`, `max_vel_theta=1.60 rad/s`로 둔다. 이전 `0.24 m/s` 설정은 Stage 4 반복 테스트에서 체감상 느렸다. 속도를 더 올릴 때는 `max_vel_x`, `max_speed_xy`, `velocity_smoother.max_velocity`를 같이 바꾸고, 가속도는 `acc_lim_x`, `velocity_smoother.max_accel`을 함께 맞춘다.

확인 명령:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/check_mari_nav2_topics.py --duration 8 --map-topic /map --expect-cmd-vel
ros2 topic echo /plan --once
```

성공 기준:

- RViz `Navigation`, `Localization`, `Feedback`이 active 상태로 들어간다.
- `/plan`이 `map` frame 기준으로 생성된다.
- `/cmd_vel`이 발행된다.
- Gazebo Mari가 goal까지 도착한다.

## Stage 4 반복주행 테스트 코스

Stage 3 맵은 작은 공원형이라 장애물 간격이 비교적 넓다. safe-clearance profile을 더 확실히 검증하려면 장애물이 가까운 훈련 코스가 필요하다.

### 맵 설명

Stage 4는 공원처럼 자연스러운 배경을 보여주기 위한 맵이 아니라, Nav2 주행 profile을 반복해서 검증하기 위한 훈련용 맵이다.

구성 의도는 아래와 같다.

- `main_test_lane`: 시작 지점에서 먼 goal까지 이어지는 주행 기준선이다.
- `slalom_obstacles`: 좌우로 번갈아 배치된 장애물이다. Mari가 직선으로만 가지 않고 S자 회피를 하는지 확인한다.
- `center_pillar`: 코스 중앙에서 회전과 우회 결정을 강제하는 기둥이다.
- `left/right_mid_barrier`: costmap inflation이 커졌을 때 통로가 너무 좁게 막히는지 확인하는 장애물이다.
- `angled_panel`: 비스듬한 큰 장애물이다. 카메라 depth-to-scan과 costmap이 기울어진 물체를 어떻게 잡는지 확인한다.
- `gate_left/right_post`: 먼 goal 직전에 있는 좁은 gate다. 안전 여유가 넓어져도 통과 가능한지 확인한다.
- `left/right_side_wall`: 장애물 바로 옆 goal을 찍었을 때 stuck 또는 과도한 회피가 생기는지 확인한다.
- `left/right_goal_marker`, `far_goal_band`: RViz에서 goal을 찍을 때 참고하기 위한 바닥 표시다.

이 맵에서 보고 싶은 핵심은 "safe-clearance가 장애물 주변을 넓게 보면서도 실제로 지나갈 수 있는 통로는 막지 않는가"이다. 따라서 장애물은 Stage 3보다 촘촘하지만, Mari가 절대 지나갈 수 없을 정도로 막아두지는 않았다.

Stage 4 반복주행 코스는 아래 목적을 가진다.

- 장애물 사이 S자 회피가 되는지 확인한다.
- 장애물 바로 옆 goal을 찍었을 때 stuck이 줄어드는지 확인한다.
- costmap의 적색 위험 영역이 넓어져도 통로가 과하게 막히지 않는지 확인한다.
- baseline profile과 safe-clearance profile을 같은 map, 같은 시작 위치, 같은 goal로 비교한다.

1단계: Stage 4 Gazebo world 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description gazebo_mari_nav2_stage4_repeat_course.launch.py
```

2단계: Stage 4 map builder 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py \
  scan_height:=2 \
  range_min:=0.45 \
  range_max:=2.50 \
  grid_range_min:=0.45 \
  grid_range_max:=2.50 \
  linear_update:=0.15 \
  angular_update:=0.15
```

3단계: teleop으로 코스 전체를 천천히 스캔

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.06 \
  --angular-speed 0.35 \
  --key-timeout 1.2
```

4단계: 맵 저장

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
mkdir -p assets/2026-05-02_mari_nav2_stage4_repeat_course
ros2 run nav2_map_server map_saver_cli \
  -t /rtabmap/map \
  -f assets/2026-05-02_mari_nav2_stage4_repeat_course/stage4_repeat_course_rtabmap \
  --fmt pgm \
  --mode trinary \
  --occ 0.65 \
  --free 0.25
```

5단계: 저장 맵 후처리

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/filter_nav2_saved_map.py \
  assets/2026-05-02_mari_nav2_stage4_repeat_course/stage4_repeat_course_rtabmap.yaml \
  --output-prefix assets/2026-05-02_mari_nav2_stage4_repeat_course/stage4_repeat_course_rtabmap_filtered \
  --min-occupied-neighbors 1 \
  --min-obstacle-pixels 12
```

6단계: safe-clearance profile로 Nav2 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-02_mari_nav2_stage4_repeat_course/stage4_repeat_course_rtabmap_filtered.yaml \
  params_file:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/config/mari_nav2_saved_map_safe_clearance_params.yaml
```

권장 goal 순서는 `가까운 goal -> S자 통과 goal -> 장애물 옆 goal -> 먼 goal -> 반대 방향 복귀 goal`이다.
- recovery가 반복되지 않는다.
