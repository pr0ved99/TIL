# 2026-04-26 작업 일지

## 결론

- 오늘 가장 중요한 결과는 Mari 모델을 `Gazebo`에 올리는 단계까지 진행했고, 현재 blocker가 **URDF 파싱 문제가 아니라 Gazebo visual mesh 표시 문제**라는 점을 분리한 것이다.
- `Onshape`에서 export한 Mari URDF/GLTF 결과와 새로 export한 Mari STEP/STL 파일을 repository asset으로 보관했다.
- `mari.urdf.xacro`는 `xacro` 렌더링과 `check_urdf` 파싱까지 통과했다.
- Gazebo에서는 `mari` entity와 `base_footprint` link가 생성되지만, 현재 화면에는 visual mesh가 보이지 않는 상태다.
- 다음 작업의 1순위는 Gazebo에서 `mari_visual_mesh.stl`이 보이지 않는 원인을 `mesh 경로`, `scale/origin`, `Gazebo Classic STL 처리`, `camera view/frustum` 순서로 분리하는 것이다.

## 오늘 작업 한 줄 요약

- Mari/Duri 모델 asset을 정리하고, Mari URDF/GLTF/STL export를 보관한 뒤, `trashbot_description`의 Mari Gazebo spawn을 시도했으나 visual mesh 미표시 문제를 확인했다.

## 시간순 기록

### 16:00

- Onshape에서 `turtle_small`은 `Mari`, `turtle_big`은 `Duri`로 명칭을 바꾸는 방향을 확정했다.
- repository 안의 기존 `turtle_small`, `turtle_big` 계열 파일명을 `mari`, `duri` 기준으로 정리했다.
- Mari/Duri 캡처 이미지도 아래 구조로 분리했다.

```text
assets/robot_model_exports/mari_view/without_sensors/
assets/robot_model_exports/mari_view/with_sensors/
assets/robot_model_exports/duri_view/without_sensors/
```

### 17:00

- Onshape에서 Mari URDF를 GLTF mesh 기반으로 export했다.
- export 결과 zip과 unpacked 결과를 repository asset에 보관했다.

```text
assets/robot_model_exports/onshape_urdf_exports/mari.zip
assets/robot_model_exports/onshape_urdf_exports/mari_unpacked/pkg_/urdf/pkg_.urdf
assets/robot_model_exports/onshape_urdf_exports/mari_unpacked/pkg_/meshes/*.gltf
```

- Onshape export 결과는 link가 많이 쪼개진 visual reference 성격이 강하므로, 바로 Gazebo 물리 모델로 쓰기보다는 후처리/참고용으로 관리하기로 했다.

### 18:00

- Onshape에서 Mari 모델을 STEP/STL로 다시 export했다.
- 새 Mari STEP과 STL을 아래 위치에 보관했다.

```text
assets/robot_model_exports/Mari.step
assets/robot_model_exports/mari_visual_mesh.stl
trashbot_description/meshes/mari_visual_mesh.stl
```

- `trashbot_description`에서 Gazebo Classic이 `package://` mesh를 `model://` URI처럼 찾는 상황에 대비해 `package.xml`에 `gazebo_model_path` export를 추가했다.

### 18:10

- `trashbot_description` 패키지를 다시 빌드하고, Mari Xacro 렌더링과 URDF 파싱을 확인했다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
colcon build --packages-select trashbot_description --symlink-install
xacro trashbot_description/urdf/mari.urdf.xacro > /tmp/mari.urdf
check_urdf /tmp/mari.urdf
```

- 확인 결과:
  - `colcon build`: 통과
  - `xacro`: 통과
  - `check_urdf`: 통과

### 18:20

- Gazebo Classic에서 Mari 모델 spawn을 시도했다.
- Gazebo 좌측 model tree에는 `mari`와 `base_footprint`가 표시됐다.
- 하지만 화면에는 Mari visual mesh가 보이지 않았다.

현재 관찰 결과는 아래와 같다.

```text
Gazebo entity 생성 여부  = 생성됨
Gazebo link tree 표시     = mari > LINKS > base_footprint 표시
visual mesh 표시 여부    = 표시 안 됨
현재 blocker             = Gazebo visual mesh 표시 문제
```

## 오늘 관찰한 핵심 현상

- `mari.urdf.xacro` 자체는 XML/URDF 문법 관점에서 깨지지 않았다.
- Gazebo에 entity가 생성되므로 spawn 단계 전체가 실패한 것은 아니다.
- 화면에 아무것도 보이지 않는 문제는 `visual mesh 경로`, `mesh scale/origin`, `Gazebo Classic STL 로딩`, `client view` 중 하나로 좁혀졌다.
- Onshape URDF/GLTF export 결과는 시각적으로는 풍부하지만, 링크가 너무 잘게 나뉘어 있어 곧바로 주행 물리 모델로 쓰기에는 무겁다.
- Gazebo 주행 검증은 여전히 단순 collision + virtual wheel 기반 diff-drive 모델로 진행하는 것이 맞다.

## 원인 가설

- 1순위 가설: Gazebo client가 `package://trashbot_description/meshes/mari_visual_mesh.stl` 경로를 visual mesh로 제대로 resolve하지 못하고 있다.
- 2순위 가설: 새 STL의 원점, scale, bounds가 Gazebo camera view 바깥에 놓였거나 지나치게 크거나 작다.
- 3순위 가설: Gazebo Classic이 큰 STL visual mesh를 읽는 과정에서 실패하거나 표시를 생략하고 있다.
- 4순위 가설: `base_footprint`만 보이는 것은 `base_link` 이하 fixed joint tree가 Gazebo GUI에서 접혀 있거나 visual이 비활성화된 상태일 수 있다.

## 확인 방법

- `xacro`와 `check_urdf`로 URDF 파싱 문제를 먼저 배제했다.
- Gazebo GUI model tree에서 `mari` entity 생성 여부를 확인했다.
- asset 경로와 mesh 파일 위치를 repository에 정리했다.
- 다음 확인은 `gzclient --verbose` 로그에서 mesh load error를 직접 보는 방식으로 진행한다.

## 해결 방법

- 아직 완전 해결은 아니다.
- 오늘 적용한 것은 다음 단계 디버깅을 위한 정리 작업이다.
  - `mari_visual_mesh.stl`을 `assets`와 `trashbot_description/meshes`에 동기화
  - `package.xml`에 Gazebo model path export 추가
  - Onshape URDF/GLTF export 결과 보관
  - Mari/Duri asset 명칭 정리
  - Gazebo blocker를 별도 이슈로 기록

## 오늘 배운 것

- Gazebo에 entity가 생기는 것과 visual mesh가 보이는 것은 별개의 문제다.
- URDF 파싱이 성공해도 mesh URI, mesh scale, mesh origin이 맞지 않으면 화면에는 아무것도 안 보일 수 있다.
- Onshape에서 export한 full visual 모델은 발표/참고용으로는 좋지만, Gazebo 물리 시뮬레이션에는 단순 collision과 가상 바퀴 모델이 더 안전하다.
- `base_link`, `camera_link`, `imu_link`, `gps_link` 같은 frame 설계와 Gazebo visual mesh 표시는 분리해서 검증해야 한다.

## 오늘 만든/수정한 파일

- [2026-04-26 작업 일지](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/daily/2026-04-26/README.md)
- [VSLAM Daily Index](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/daily/README.md)
- [Current Progress and Open Issues](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md)
- [Simulation First Procedure](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Simulation_First_Outdoor_Trash_Robot_Procedure.md)
- [Mari URDF/Xacro Preparation Checklist](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/Mari_URDF_Xacro_Preparation_Checklist.md)
- [trashbot_description README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/README.md)
- [mari.urdf.xacro](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/urdf/mari.urdf.xacro)
- [mari_visual_mesh.stl](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/meshes/mari_visual_mesh.stl)

## 증빙 자료

- [Mari STEP export](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/Mari.step)
- [Mari visual mesh STL](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_visual_mesh.stl)
- [Onshape URDF/GLTF export archive](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/onshape_urdf_exports/mari.zip)
- [Mari with sensors captures](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_view/with_sensors)
- [Mari without sensors captures](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_view/without_sensors)
- [Duri without sensors captures](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/duri_view/without_sensors)

## 남은 문제

- Gazebo에서 `mari_visual_mesh.stl`이 아직 화면에 표시되지 않는다.
- Onshape full URDF/GLTF export 결과는 보관했지만, `trashbot_description`의 단순 Xacro와 통합하지 않았다.
- `left_virtual_drive_wheel_link`, `right_virtual_drive_wheel_link`는 아직 Xacro에 실제 link/joint로 추가하지 않았다.
- Gazebo diff-drive plugin, `/cmd_vel`, `/odom` 연결은 아직 시작하지 않았다.
- IMU/GPS frame은 위치만 1차 반영됐고 실제 축/안테나 중심 검증은 남아 있다.

## 다음 액션

1. `gzclient --verbose` 로그로 mesh URI load error가 있는지 확인한다.
2. `mari_visual_mesh.stl` bounds와 scale을 다시 확인한다.
3. Gazebo에서 작은 test STL 또는 box visual이 보이는지 비교해 mesh 문제와 Gazebo 표시 문제를 분리한다.
4. 필요하면 Mari visual mesh를 STL 대신 DAE/OBJ/GLTF 변환본으로 테스트한다.
5. visual 표시가 해결되면 `left_virtual_drive_wheel_link`, `right_virtual_drive_wheel_link`를 추가하고 diff-drive plugin을 붙인다.

## 한 줄 회고

- 오늘 작업은 Mari 모델을 Gazebo 단계까지 올리며, 현재 문제가 URDF 작성 자체가 아니라 Gazebo visual mesh 표시 문제임을 분리한 날이었다.
