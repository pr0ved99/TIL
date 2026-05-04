# 2026-05-01 Mari Nav2 Saved Map Smoke

## 결론

이 폴더는 RTAB-Map으로 만든 2D occupancy map을 파일로 저장한 뒤, Nav2가 그 저장 맵을 기반으로 경로를 계획하고 `/scan`으로 실시간 장애물을 보는지 확인하기 위한 산출물 위치다.

현재 Stage 2 장애물 world에서는 clean map 생성과 saved-map Nav2 goal 주행까지 확인했다. 즉, 저장 맵을 불러온 뒤 AMCL localization, global plan, `/cmd_vel` 발행, Gazebo Mari goal reach까지 이어지는 기본 pipeline은 연결된 상태다.

## 목표

```text
RTAB-Map /rtabmap/map
-> nav2_map_server map_saver_cli
-> stage map YAML/PGM 저장
-> map_server + AMCL + Nav2
-> RViz Nav2 Goal
-> /cmd_vel
```

용어 정리:

- `map_server`: 저장된 지도 파일을 ROS2 `/map` topic으로 다시 올려주는 노드.
- `AMCL`: 저장된 지도와 `/scan`을 비교해서 로봇이 지도 위 어디에 있는지 맞추는 위치추정 노드.
- `static map`: 주행 전에 미리 만들어 저장해 둔 지도.

## 생성 파일

Stage 2 장애물 world에서 아래 파일을 생성했다.

```text
stage2_obstacles_rtabmap.yaml
stage2_obstacles_rtabmap.pgm
stage2_obstacles_rtabmap_filtered.yaml
stage2_obstacles_rtabmap_filtered.pgm
stage2_obstacles_rtabmap_filtered_strict.yaml
stage2_obstacles_rtabmap_filtered_strict.pgm
```

Stage 3 작은 loop world까지 확장하면 아래 이름을 쓴다.

```text
stage3_small_loop_rtabmap.yaml
stage3_small_loop_rtabmap.pgm
```

## 주의

이 저장 맵 방식은 RTAB-Map이 만든 `/rtabmap/map` 품질을 그대로 가져간다. 평지가 장애물처럼 들어간 상태에서 저장하면 Nav2도 그 지저분한 맵을 그대로 믿는다.

따라서 저장은 RTAB-Map/RViz에서 맵이 충분히 깨끗해 보이는 시점에 수행한다.

## 필터링

저장된 map에 작은 검은 점 노이즈가 많으면 아래 후처리를 먼저 적용한다.

```bash
python3 Tools/filter_nav2_saved_map.py \
  assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml \
  --output-prefix assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered \
  --min-occupied-neighbors 1 \
  --min-obstacle-pixels 12
```

그 다음 Nav2는 filtered map으로 실행한다.

```bash
ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered.yaml
```

현재 생성된 후처리 결과:

```text
stage2_obstacles_rtabmap_filtered.yaml/.pgm
- min_occupied_neighbors=1
- min_obstacle_pixels=12
- occupied cells: 7602 -> 5348

stage2_obstacles_rtabmap_filtered_strict.yaml/.pgm
- min_occupied_neighbors=2
- min_obstacle_pixels=20
- occupied cells: 7602 -> 4786
```

먼저 일반 filtered map을 확인하고, 여전히 점 노이즈가 많으면 strict map을 확인한다.

## 현재 smoke 결과

사용 기준 맵:

```text
stage2_obstacles_rtabmap_filtered.yaml
```

확인된 상태:

```text
RViz Navigation: active
RViz Localization: active
RViz Feedback: active

/scan: OK, 15.0 Hz, frame=camera_link
/global_costmap/costmap: OK, 0.7 Hz, frame=map
/local_costmap/costmap: OK, 2.7 Hz, frame=odom
/plan: OK, 1.0 Hz, frame=map, poses=37
/cmd_vel: OK, 137.8 Hz, linear_x=0.111, angular_z=0.396
```

`/plan`은 `map` frame 기준으로 연속 pose를 생성했다. 예시 경로는 `x=4.025, y=0.230` 부근에서 시작해 `x=4.170, y=0.765` 부근으로 이어졌다.

해석:

- 저장 맵 기반 Nav2가 목표를 받아 global path를 만들고 controller가 `/cmd_vel`을 발행하는 데 성공했다.
- `check_mari_nav2_topics.py`에서 `/map` count가 0으로 보일 수 있다. 저장 맵은 transient/static 성격이라 짧은 sample window에 새 메시지가 잡히지 않을 수 있으며, RViz map 표시와 global costmap/path 생성을 함께 보고 판단한다.
- 이후 같은 실행 조건에서 목표 지점까지 만족스럽게 도착하는 것을 사용자 주행으로 확인했다.
- Stage 2 saved-map Nav2는 1차 성공으로 본다.
- 다음 검증은 Stage 3 small loop world에서 같은 map 생성/저장/주행 절차를 반복하는 것이다.
