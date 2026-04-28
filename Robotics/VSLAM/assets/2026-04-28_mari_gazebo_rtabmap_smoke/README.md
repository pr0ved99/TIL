# Mari Gazebo RTAB-Map Smoke Evidence

## 결론

- 이 폴더는 Mari Gazebo RGB-D/odom baseline을 RTAB-Map에 연결한 증빙을 보관한다.
- `2026-04-29` 기준으로 Gazebo 입력 topic과 RTAB-Map map output topic이 `Tools/check_mari_rtabmap_topics.py`에서 `[OK]`로 확인됐다.
- RTAB-Map GUI에서는 3D map이 생성되는 것을 확인했지만, graph optimization과 loop closure 경고는 추가 튜닝 대상으로 남아 있다.

## 파일 목록

- `01_gazebo_rtabmap_runtime_logs_and_teleop.png`
  - Gazebo, RTAB-Map, teleop 실행 로그를 함께 남긴 화면
- `02_gazebo_world_and_rtabmap_3d_map_view.png`
  - Gazebo camera test world와 RTAB-Map 3D Map GUI 확인 화면
- `03_mari_rtabmap_topic_check_ok.png`
  - `Tools/check_mari_rtabmap_topics.py`의 필수 topic `[OK]` 확인 화면
- `04_mari_rtabmap_detectionrate5_live_map.png`
  - `DetectionRate=5` 기준 RTAB-Map live map 확인 화면

## 실행 기준

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash
```

Gazebo:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py \
  use_mesh_visual:=true \
  world:=$(pwd)/trashbot_description/worlds/mari_camera_test.world
```

Teleop:

```bash
python3 Tools/teleop_mari_keyboard.py
```

RTAB-Map:

```bash
ros2 launch trashbot_description mari_rtabmap.launch.py
```

Topic smoke check:

```bash
python3 Tools/check_mari_rtabmap_topics.py
```
