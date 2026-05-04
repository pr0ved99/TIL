# 2026-05-02 Mari Nav2 Stage 3 Saved Map Smoke

## 결론

Stage 2 saved-map Nav2가 목표 지점까지 만족스럽게 주행했으므로, 다음 검증 대상은 Stage 3 small loop world다.

이 폴더는 `mari_nav2_stage3_small_loop.world`에서 RTAB-Map 2D occupancy map을 만들고, 저장된 map을 `map_server + AMCL + Nav2`로 다시 불러와 주행하는 증빙을 모으는 위치다.

## 목표

```text
Stage 3 Gazebo small loop world
-> RTAB-Map grid from /scan
-> stage3_small_loop_rtabmap.yaml/.pgm
-> optional filtered map
-> map_server + AMCL + Nav2
-> RViz Nav2 Goal
-> Gazebo Mari goal reach
```

## 생성 예정 파일

```text
stage3_small_loop_rtabmap.yaml
stage3_small_loop_rtabmap.pgm
stage3_small_loop_rtabmap_filtered.yaml
stage3_small_loop_rtabmap_filtered.pgm
```

## 실행 절차

Terminal 1, Gazebo:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description gazebo_mari_nav2_stage3_small_loop.launch.py
```

Terminal 2, map builder:

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

Terminal 3, teleop:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.06 \
  --angular-speed 0.35 \
  --linear-accel 0.10 \
  --angular-accel 0.25 \
  --key-timeout 1.2
```

맵 저장:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 run nav2_map_server map_saver_cli \
  -t /rtabmap/map \
  -f assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap \
  --fmt pgm \
  --mode trinary \
  --occ 0.65 \
  --free 0.25
```

후처리:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/filter_nav2_saved_map.py \
  assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap.yaml \
  --output-prefix assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap_filtered \
  --min-occupied-neighbors 1 \
  --min-obstacle-pixels 12
```

저장 맵 기반 Nav2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/stage3_small_loop_rtabmap_filtered.yaml
```

확인:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/check_mari_nav2_topics.py --duration 8 --map-topic /map --expect-cmd-vel
ros2 topic echo /plan --once
```

## 성공 기준

- `Navigation`, `Localization`, `Feedback`이 active 상태로 들어간다.
- `/scan`, `/global_costmap/costmap`, `/local_costmap/costmap`, `/plan`, `/cmd_vel`이 확인된다.
- RViz `Nav2 Goal` 입력 후 Gazebo Mari가 목표 지점까지 도착한다.
- 작은 loop 구조에서 경로가 끊기지 않는다.
- recovery가 반복되지 않는다.

## 기록할 항목

| 항목 | 결과 |
| --- | --- |
| map 생성 품질 | TODO |
| 후처리 필요 여부 | TODO |
| `/plan` 생성 | TODO |
| `/cmd_vel` 발행 | TODO |
| goal reach | TODO |
| recovery 횟수 | TODO |
| 캡처 파일 | TODO |
