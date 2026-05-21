# 2026-05-12 작업 일지

## 결론

- 오늘 핵심은 Duri에서 RTAB-Map map이 지저분하게 생성되는 원인을 `/scan` 단일 라인 변환 방식으로 분리하고, RTAB-Map은 3D ground segmentation 기반으로 되돌린 것이다.
- Nav2 costmap은 `/scan` 대신 높이 필터링된 PointCloud2(`/duri/filtered_depth_points`)를 장애물 입력으로 쓰는 방향으로 정리했다.
- 아직 실제 화면에서 최종 튜닝이 끝난 것은 아니며, 다음 1순위는 RViz에서 filtered point cloud를 보고 `cloud_filter_min_z`, `cloud_filter_max_z`, self-filter box를 조정하는 것이다.

## 오늘 작업 한 줄 요약

- Duri RTAB-Map/Nav2 map distortion 문제를 정리하고, `/scan` 중심 구조에서 3D point cloud 필터링 구조로 전환했다.

## 시간순 기록

### 오전

- Duri Nav2를 Gazebo/RViz에서 실행해 `Nav2 Goal`로 이동하는 장면을 확인했다.
- RViz에서 노란색 costmap inflation 영역이 너무 크고, Duri가 움직일수록 로봇 주변 장애물 표현이 짙어지는 현상을 관찰했다.
- safe clearance는 `inflation_radius`, `cost_scaling_factor`, footprint padding 계열 값으로 조정해야 한다고 판단했다.

### 오후

- RTAB-Map으로 Duri map을 새로 만들 때, 바닥 영역이 벽처럼 누적되는 문제를 확인했다.
- 기존 `/scan` 한 줄 변환은 2D lidar처럼 보이게 만들 수는 있지만, 카메라가 아래를 향할수록 바닥을 장애물로 오인하기 쉬운 구조라고 판단했다.
- 특히 카메라 pitch를 10도, 15도, 25도로 낮추는 문제는 시야 확보에는 도움이 될 수 있지만, `/scan` 한 줄을 그대로 쓰면 바닥선 위치가 바뀌어 map 왜곡이 반복될 수 있다.

### 저녁

- RTAB-Map map 생성은 RGB-D 기반 3D grid와 ground segmentation을 사용하도록 방향을 바꿨다.
- Nav2 obstacle layer는 `/duri/filtered_depth_points`를 사용하도록 분리했다.
- `pointcloud_height_filter.py`를 추가해 `base_footprint` 기준 높이 범위와 로봇 자기 몸체 근처 point를 필터링하는 구조를 만들었다.

## 오늘 관찰한 핵심 현상

- RTAB-Map 자체는 3D 점군을 만들 수 있지만, 그 점군을 2D map/costmap으로 내릴 때 바닥과 장애물을 구분하지 못하면 바닥이 벽처럼 보인다.
- depth image 한 줄을 `/scan`으로 바꾸는 방식은 단순하지만, 카메라 각도와 바닥면 위치에 매우 민감하다.
- Duri/Mari 모두 카메라 각도를 낮추면 가까운 바닥을 더 많이 보게 되므로, 2D scan 변환보다 3D ground segmentation과 height filtering이 더 안전하다.

## 원인 가설

- 바닥이 벽처럼 누적된 직접 원인은 `/scan` 변환 라인이 바닥 점을 장애물 점으로 포함했기 때문으로 판단했다.
- RTAB-Map 화면이 비어 보였던 시점은 depth row scan 설정이 이미지 높이와 맞지 않아 `scan_height` 오류가 발생했고, 그 결과 RTAB-Map 입력이 제대로 들어가지 않은 상태였을 가능성이 높다.
- RViz/Gazebo/RTAB-Map을 동시에 띄웠을 때 끊기는 현상은 RTAB-Map 3D 처리, RViz rendering, Gazebo physics/rendering이 동시에 GPU/CPU를 쓰기 때문으로 본다.

## 확인 방법

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 topic list -t | grep -E 'filtered_depth_points|rtabmap/map|camera/.+points'
ros2 topic hz /duri/filtered_depth_points
ros2 topic echo /duri/filtered_depth_points --once
```

## 해결 방법

- RTAB-Map map 생성에서 `/scan` 단일 라인 의존도를 제거했다.
- RTAB-Map은 RGB-D 3D grid와 ground segmentation을 사용하도록 설정했다.
- Nav2 obstacle layer는 `/duri/filtered_depth_points`를 사용하도록 설정했다.
- RViz에서 filtered point cloud를 볼 수 있도록 display를 추가했다.

## 오늘 배운 것

- `PointCloud2`는 카메라가 본 3D 점들의 묶음이다. 바닥과 장애물을 높이 기준으로 나눌 수 있어 2D scan 한 줄보다 튜닝 여지가 크다.
- `ground segmentation`은 3D 점들 중 바닥으로 보이는 점과 장애물로 보이는 점을 분리하는 처리다.
- `costmap`은 Nav2가 길을 찾을 때 쓰는 2D 위험도 지도다. 장애물 입력이 지저분하면 경로가 돌아가거나 로봇 주변이 막힌 것처럼 보인다.

## 오늘 만든/수정한 파일

- [Duri RTAB-Map/Nav2 guide](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/docs/navigation/Duri_RTABMap_To_Nav2_Map_Guide.md)
- [Duri Nav2 Gazebo bringup guide](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/docs/navigation/Duri_Nav2_Gazebo_Bringup_Guide.md)
- [pointcloud_height_filter.py](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws/src/trashbot_navigation/scripts/pointcloud_height_filter.py)
- [duri_rtabmap_mapping.launch.py](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_rtabmap_mapping.launch.py)
- [duri_nav2_map_builder.launch.py](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_nav2_map_builder.launch.py)
- [duri_nav2_saved_map.launch.py](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_nav2_saved_map.launch.py)
- [nav2_duri_gazebo.yaml](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws/src/trashbot_navigation/config/nav2_duri_gazebo.yaml)

## 증빙 자료

- 아직 최종 캡처는 남기지 않았다.
- 다음 캡처 후보:
  - `Duri filtered point cloud RViz`
  - `Duri RTAB-Map rebuilt occupancy map`
  - `Duri Nav2 saved-map goal driving`

## 남은 문제

- `/duri/filtered_depth_points`가 실제로 바닥을 충분히 제거하는지 RViz에서 확인해야 한다.
- `cloud_filter_min_z`는 우선 `0.06`, `0.08`, `0.10` 순서로 비교해야 한다.
- 카메라 pitch는 시야 확보와 바닥 왜곡 사이의 trade-off가 있으므로, Duri/Mari 공통 기준을 다시 정해야 한다.
- RTAB-Map/Viz/RViz/Gazebo 동시 실행이 무거우면 GUI 조합을 줄여 재검증해야 한다.

## 다음 액션

1. Duri map builder를 다시 실행한다.
2. RViz에서 `Height Filtered PointCloud` display를 켜고 바닥 제거 상태를 확인한다.
3. filtered cloud가 안정적이면 RTAB-Map map을 새로 저장한다.
4. saved map 기반으로 Nav2 goal 주행을 다시 실행한다.

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_navigation duri_nav2_map_builder.launch.py \
  gui:=true \
  launch_rviz:=true \
  rtabmap_viz:=true \
  camera_pitch:=0.1745 \
  start_depth_scan:=false \
  start_cloud_filter:=true \
  cloud_filter_min_z:=0.06 \
  cloud_filter_max_z:=0.60 \
  verbose:=false
```

## 한 줄 회고

- Duri 자율주행 검증은 단순히 goal을 찍어 움직이는 단계에서, RTAB-Map map 입력과 Nav2 costmap 입력을 분리해 안정화해야 하는 단계로 넘어갔다.
