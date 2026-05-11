# 2026-05-09 VSLAM Context Handoff

이 문서는 새 대화창에서 VSLAM 작업을 바로 이어받기 위한 인수인계 문서이다.

## 1. 현재 목표

- Mari/Duri 로봇의 URDF/Xacro 기반 모델링을 정리하고 RViz/Gazebo에서 검증한다.
- Duri는 새로 만든 3D 모델과 센서 위치 기준을 반영하는 단계이다.
- RTAB-Map 멀티세션은 Gazebo 기반으로 DB 생성, 재사용, 결과 캡처까지 검증하는 흐름으로 진행 중이다.
- 실제 하드웨어 연동은 아직 준비되지 않았으므로 현재 범위는 simulation-first이다.

## 2. 관련 저장소/경로

- 개인 GitHub/TIL 작업 경로: `/home/ssafy/my_ws/git_hub/Robotics/VSLAM`
- 프로젝트 GitLab 작업 경로: `/home/ssafy/my_ws/git_lab/S14P31C205`
- GitLab ROS2 패키지 경로: `/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws/src/trashbot_description`
- GitHub ROS2 패키지 경로: `/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description`
- 모델/캡처 자산 경로: `/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports`
- Mari/Duri RViz 캡처 정리 경로:
  - `/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_view`
  - `/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/duri_view`

## 3. 이미 만든 파일

- Duri 새 visual mesh:
  - `Robotics/VSLAM/assets/robot_model_exports/duri_visual_mesh.stl`
  - `Robotics/VSLAM/assets/robot_model_exports/duri_visual_mesh_without_housing.stl`
- Mari 추가 visual mesh:
  - `Robotics/VSLAM/assets/robot_model_exports/mari_visual_mesh_without_housing.stl`
- Duri URDF/Xacro:
  - `Robotics/VSLAM/trashbot_description/urdf/duri.urdf.xacro`
- Duri Gazebo 관련 파일:
  - `Robotics/VSLAM/trashbot_description/launch/gazebo_duri.launch.py`
  - `Robotics/VSLAM/trashbot_description/launch/gazebo_duri_realsense_light.launch.py`
  - `Robotics/VSLAM/trashbot_description/worlds/duri_empty.world`
  - `Robotics/VSLAM/trashbot_description/worlds/duri_camera_test.world`
- Duri 캡처 자료:
  - `Robotics/VSLAM/assets/robot_model_exports/duri_view/`
  - `Robotics/VSLAM/assets/robot_model_exports/duri_view/README.md`
- RTAB-Map/Jetson/GPS/IMU 학습 문서:
  - `Robotics/VSLAM/docs/learning/RTABMap_MultiSession_DB_Reuse_Learning_Guide.md`
  - `Robotics/VSLAM/docs/learning/BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md`
  - `Robotics/VSLAM/docs/learning/Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md`
  - `Robotics/VSLAM/docs/learning/00_LEARNING_INDEX.md`
- GitLab target에도 최신 Duri 모델 반영 작업을 진행했다.
  - `edge/jetson/ros2_ws/src/trashbot_description/meshes/duri_visual_mesh.stl`
  - `edge/jetson/ros2_ws/src/trashbot_description/meshes/duri_visual_mesh_without_housing.stl`
  - `edge/jetson/ros2_ws/src/trashbot_description/urdf/duri.urdf.xacro`

## 4. 중요한 결정사항

- ROS 좌표계 기준은 `x=전방`, `y=왼쪽`, `z=위쪽`으로 둔다.
- `base_footprint`는 지면 기준 프레임이고, `base_link`는 차체 중심 기준 프레임이다.
- URDF에서는 `base_footprint -> base_link`가 위쪽으로 올라가야 하므로 z offset은 양수로 작성한다.
- Duri Onshape 기준 주요 상대 위치는 mm 단위로 다음과 같이 측정했다.
  - `camera_link_mc` relative to `base_link_mc`: `+245.385, +000.000, +120.895`
  - `imu_link_mc` relative to `base_link_mc`: `+010.724, -001.608, +089.039`
  - `gps_link_mc` relative to `base_link_mc`: `-276.881, -000.000, +005.984`
  - `base_link_mc` relative to `base_footprint_mc`: `+000.000, +000.000, -038.536`
  - `track_left` relative to `base_link_mc`: `+000.000, +109.858, -038.536`
  - `track_right` relative to `base_link_mc`: `+000.000, -109.858, -038.536`
- 위 측정값을 URDF에 넣을 때는 m 단위로 변환한다.
- Duri의 새 mesh는 기존 임시 placeholder mesh가 아니다. 파일 크기 기준 약 49 MB인 새 모델을 사용한다.
- Duri housing 제거 mesh는 `mesh_file:=package://trashbot_description/meshes/duri_visual_mesh_without_housing.stl`로 선택한다.
- Gazebo에서 mesh가 무겁거나 보이지 않으면 `use_mesh_visual:=false`로 박스형 visual부터 검증한다.
- GitLab은 프로젝트 코드/검증 결과를 먼저 올리고, GitHub/TIL은 회고와 학습 기록을 나중에 정리한다.

## 5. 아직 안 끝난 일

- 2026-05-11 업데이트:
  - GitLab `trashbot_description`에서 `colcon build --symlink-install --packages-select trashbot_description --allow-overriding trashbot_description` 통과.
  - Duri xacro 기본형과 `frame_prefix:=duri/ topic_prefix:=/duri` 적용형 모두 `check_urdf` 통과.
  - GitLab에 Duri 단독 Gazebo launch/world를 추가했고, `gazebo_duri.launch.py gui:=false use_mesh_visual:=false`에서 Duri spawn 성공 확인.
  - `gazebo_mari_duri_realsense_light.launch.py gui:=false use_mesh_visual:=false`에서 Mari/Duri 동시 spawn 성공 확인.
  - 동시 spawn에서 Duri 카메라/IMU/odom/cmd_vel은 `/duri/...` 토픽으로 분리했고, TF는 `duri/odom -> duri/base_footprint`로 확인.
  - Duri TF tree는 `assets/robot_model_exports/duri_view/02_duri_tf_tree_view_frames.pdf`와 `.gv`로 갱신.
  - Duri full mesh의 yaw와 z offset을 RViz에서 보정했다. 현재 visual mesh는 `chassis_mesh_yaw=${pi / 2.0}`, `chassis_mesh_z=0.0` 기준이다.
  - Duri housing 제거 mesh를 GitLab 패키지 `meshes/`에 추가했고, `gazebo_duri.launch.py gui:=false use_mesh_visual:=true mesh_file:=package://trashbot_description/meshes/duri_visual_mesh_without_housing.stl`에서 spawn 성공 확인.
  - Duri RViz/Gazebo 결과 캡처 정리를 완료했다.
    - `03_duri_urdf_rviz_mesh_tf_alignment_check.png`
    - `04_duri_gazebo_full_housing_spawn_check.png`
    - `05_duri_gazebo_without_housing_spawn_check.png`
    - `06_duri_ros2_topic_list_gazebo_spawn_check.txt`
    - `07_duri_tf_tree_gazebo_spawn_check.pdf`
    - `07_duri_tf_tree_gazebo_spawn_check.gv`
- Duri visual mesh는 RViz와 Gazebo에서 full housing / without housing 모두 표시 확인을 마쳤다.
- RTAB-Map 멀티세션은 DB 재사용 확인 이후 map merge/결과 비교 문서화가 남아 있다.
- GitLab에 반영한 최신 Duri 모델 변경은 커밋/푸시 상태를 다시 확인해야 한다.

## 6. 절대 건드리면 안 되는 것

- 사용자가 만들었거나 아직 분류하지 않은 변경을 임의로 되돌리지 않는다.
- `/home/ssafy/my_ws/git_hub`와 `/home/ssafy/my_ws/git_lab/S14P31C205`를 혼동하지 않는다.
- GitLab 프로젝트 코드에 GitHub TIL 전용 회고 문서를 섞지 않는다.
- 실제 하드웨어 연동이 준비되지 않은 상태에서 하드웨어 의존 결과를 완료로 적지 않는다.
- `git reset --hard`, `git checkout -- <file>` 같은 파괴적 명령은 사용하지 않는다.
- `.codex`, 임시 frames 파일, unrelated CS/STM32 파일을 VSLAM 커밋에 섞지 않는다.

## 7. 다음에 바로 실행할 명령/작업

### Duri URDF 파싱 확인

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash

colcon build --symlink-install --packages-select trashbot_description \
  --allow-overriding trashbot_description
source install/setup.bash

xacro src/trashbot_description/urdf/duri.urdf.xacro > /tmp/duri.urdf
check_urdf /tmp/duri.urdf
```

### Duri RViz 실행

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description display.launch.py \
  model:=$(pwd)/src/trashbot_description/urdf/duri.urdf.xacro \
  use_gui:=false \
  use_rviz:=true
```

### TF tree 생성

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run tf2_tools view_frames
ls -lah frames_*.pdf frames_*.gv
```

### Duri housing 제거 mesh Gazebo 실행

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description gazebo_duri.launch.py \
  gui:=true \
  use_mesh_visual:=true \
  mesh_file:=package://trashbot_description/meshes/duri_visual_mesh_without_housing.stl
```

### Git 상태 확인

```bash
git -C /home/ssafy/my_ws/git_lab/S14P31C205 status --short --branch
git -C /home/ssafy/my_ws/git_hub status --short --branch
```

### 다음 작업 우선순위

1. GitLab 변경 범위 확인 후 story/Jira 키 기반 브랜치/커밋 정리
2. Duri `/cmd_vel` 직진/회전 smoke test 실행
3. Mari/Duri 동시 spawn launch에서 topic/TF namespace 최종 확인
4. 결과 캡처와 변경 내용을 기준으로 MR 설명 작성
5. RTAB-Map 멀티세션 DB 재사용 이후 map merge/결과 비교 문서화
