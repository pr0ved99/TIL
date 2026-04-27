# 현재 진행상황 및 문제점 정리

## 결론

- 현재 프로젝트는 `센서 bring-up(Stage 0)`의 후반부에 있다.
- 기존 PC 기준으로는 `D435i depth`와 `IMU`를 ROS2에서 안정적으로 읽는 상태까지 갔다.
- `D435i IMU`의 축 해석도 직접 관찰로 1차 정리했다.
- 지금 새로 시도 중인 것은 `D435i 단독 RGB-D 3D 맵핑`이다.
- 현재 `RTAB-Map rgbd_odometry`는 품질값이 대체로 `130~190` 수준으로 살아나는 상태까지 왔다.
- 다만 `RTAB-Map` 기반 3D 맵은 아직 "오도메트리는 살아났지만 TF 경고와 체감 부드러움은 더 점검이 필요한 상태"다.
- 장비 미도착 상태를 고려해, `IMU / wheel encoder / GPS` 연동 방식은 구현 전에 구조 설계를 먼저 정리하는 단계로 넘어갈 준비가 됐다.
- 현재는 `Jetson`에서 실제로 `VSLAM`을 돌리기 위한 환경으로 작업 범위를 옮기고 있다.
- `Jetson` 작업은 `SSH` 접속으로 시작했지만, 지금은 `모니터 + 키보드 + 마우스`를 직접 연결한 상태에서 현장형 bring-up을 진행 중이다.
- `Jetson` native 기준으로는 `D435i color/depth`와 `RTAB-Map` baseline이 실제로 다시 기동하는 데 성공했다.
- `Jetson`의 `Docker CE`, `Compose`, `NVIDIA Container Toolkit`은 이미 설치돼 있고 `nvidia` runtime도 등록돼 있다.
- 현재는 `jetson` 사용자의 `docker` 그룹 권한까지 열린 상태고, `jetson-vslam:humble` 개발 이미지 1차 build도 완료했다.
- 다만 현재 `Jetson`에서는 `D435i` 내장 IMU가 `HID Motion Sensor Failure`로 비활성화되어 있어, 운영 기준은 우선 `IMU OFF`다.
- `rtabmap_viz`는 GUI display가 있는 직접 연결 세션에서 실제로 확인됐고, non-GUI shell에서는 `xcb` 오류가 날 수 있다.
- 외부 `GY-BNO08x`는 `Jetson`의 `i2c-1 / 0x4B`에서 실제 인식됐고, host `venv` 기준으로 `accel / gyro / mag / quaternion` raw 값 확인까지 완료했다.
- 현재는 `BNO08x`를 host에서 `/imu/data`로 publish하고, Docker 컨테이너 안에서는 그 topic을 실제로 읽을 수 있는 상태까지 확인했다.
- Docker 안에서도 `D435i color/depth` bring-up이 다시 재현됐으므로, 당분간 실전 경로는 `host BNO08x publisher + Docker RTAB-Map`으로 잡는 편이 맞다.
- 다만 `2026-04-19` 기준으로 가장 먼저 확보한 Docker 기준선은 `IMU OFF image-only RTAB-Map baseline`이다.
- 실제 재시험에서 Docker 안 `rgbd_odometry`, `rtabmap`은 정상 기동했고 `quality`도 빠르게 회복됐다.
- `2026-04-20` 후반 재검증에서는 Docker 내부 `rtabmap_viz`의 핵심 blocker가 `video/render` 그룹 누락과 image-only IMU remap 버그였음을 확인했고, 이를 수정한 뒤 parameter/service binding까지 정상 재확인했다.
- 현재 Jetson에서 가장 실용적인 운영 기준은 여전히 `Docker backend + host rtabmap_viz frontend` 구조지만, 내부 GUI도 다시 시도 가능한 상태로 정리됐다.
- 같은 날짜 기준으로 `Docker` 구조도 `camera / rtabmap / dev-shell` 서비스 분리, `dev/runtime image` 분리, `tmpfs` DB/log, preset 파일, benchmark 자동 수집 구조까지 1차 정리했다.
- `2026-04-20` 후반에는 Docker benchmark가 끝날 때 결과 폴더별 `90_summary.env`, `91_summary.md`와 root `docker_benchmark_index.csv`, benchmark `README` 인덱스까지 자동 갱신되게 정리했다.
- `2026-04-20` preset benchmark 비교 결과, 현재 `Jetson Docker` 기본 baseline은 `light`가 가장 적합하고, `compare`는 후보 비교용, `medium`은 현재 실시간 baseline으로는 무거운 편으로 정리했다.
- 따라서 다음 `BNO08x IMU ON` 비교도 `light` baseline을 유지한 채 `Docker backend + host rtabmap_viz` 구조에서 반복하는 것이 현재 기준선이다.
- 앞으로 `Jetson` 전용 진행 기록은 별도 폴더에서 분리 관리한다.
- 추가로 `Jetson + Docker + ROS 2 Humble + D435i` 경로에서는 color/depth 토픽과 depth 약 `30 Hz`까지 확인해, Jetson 실기기 bring-up도 1차 완료했다.
- 반면 `Jetson publish -> 노트북 RTAB-Map GUI` cross-machine 경로는 현재 학교 Wi-Fi에서 DDS discovery가 막혀 실패했고, 이는 네트워크 계층 이슈로 분리된 상태다.
- 발표용 3D 맵은 우선 **노트북에 D435i를 직접 연결한 RTAB-Map 경로**로 확보했고, 결과 DB는 `assets/2026-04-16_laptop_rtabmap_demo/rtabmap_demo_map.db`에 저장했다.
- `2026-04-25` 기준으로는 Mari 로봇의 `Onshape -> URDF/Xacro -> Gazebo` 준비 단계로 넘어갔다.
- Mari `base_link`, D435i `camera_link`, BNO08x `imu_link`, GPS `gps_link`, 궤도 중심거리, 실제/가상 구동축 후보값을 1차 측정해 `mari.urdf.xacro`와 준비 문서에 기록했다.
- `2026-04-26` 기준으로 Onshape URDF/GLTF export 결과와 새 Mari STEP/STL export 결과를 repository asset으로 보관했다.
- `mari.urdf.xacro`는 `xacro` 렌더링과 `check_urdf` 파싱을 통과했고, Gazebo에는 `mari` entity가 생성되는 단계까지 확인했다.
- 다만 Gazebo 화면에는 아직 Mari visual mesh가 보이지 않는다. 현재 blocker는 `URDF 파싱 실패`가 아니라 `Gazebo visual mesh 표시/로딩 문제`로 분리됐다.
- `2026-04-27` 기준으로 Gazebo blocker와 별개로 RViz2에서 Mari visual mesh, `base_link`, `camera_link`, `imu_link`, `gps_link`가 정상 표시되는 것을 확인했다.
- `map -> odom -> base_footprint -> base_link` 구조의 동적 TF 테스트와 `/odom` publish 스크립트를 추가해, RViz2에서 Mari가 움직이는 장면까지 확인했다.
- 다음 계획은 RViz2 기준 TF baseline 위에 virtual wheel link를 추가하고, `/cmd_vel -> /odom -> odom -> base_footprint` 흐름을 구성하는 것이다.

즉, 지금 단계는 `센서가 들어오는지 확인하는 수준`은 넘었고,
`실제로 3D 맵을 만들되 속도와 안정성을 맞추는 단계`로 들어간 상태다.

---

## 0. 2026-04-27 최신 업데이트

최근 상태를 짧게 정리하면 아래와 같다.

1. **Mari RViz2 모델/TF 검증**
   - `mari.urdf.xacro`의 visual mesh yaw와 z offset을 보정해 RViz2에서 Mari 외형이 정상적으로 보이는 상태를 확인했다.
   - `base_footprint -> base_link -> chassis_link/camera_link/imu_link/gps_link` 구조가 끊기지 않는 것을 확인했다.
2. **TF tree 증빙 보관**
   - `tf2_tools view_frames` 결과를 `assets/robot_model_exports/mari_view/02_mari_tf_tree_view_frames.pdf`로 보관했다.
   - RViz2 mesh/TF alignment screenshot을 `01_mari_urdf_rviz_mesh_tf_alignment_check.png`로 보관했다.
3. **RViz2 동적 이동 테스트 추가**
   - `Tools/test_mari_moving_tf.py`를 추가해 `map -> odom -> base_footprint` 동적 TF와 `/odom` 토픽을 publish하도록 했다.
   - RViz2에서 `Fixed Frame=map`, `Target Frame=map` 설정으로 Mari가 원형 경로를 도는 것을 확인했다.
4. **D435i 장착 높이 보정**
   - 리얼센스 장착 높이가 `(80 - 65.44216) mm = 14.55784 mm` 높아진 것을 반영했다.
   - `mari.urdf.xacro`의 `camera_z`를 `0.107616 m`에서 `0.122174 m`로 갱신했다.
5. **`/cmd_vel` 기반 odom 테스트 추가**
   - `Tools/test_mari_cmd_vel_odom.py`를 추가해 `/cmd_vel`을 받아 `/odom`과 `odom -> base_footprint` TF를 publish하도록 했다.
   - 이는 실제 엔코더 odom 전 단계의 RViz2 명령-이동 검증용이다.

현재 실용적인 해석은 다음과 같다.

- **URDF/Xacro 검증**: RViz2 기준 visual mesh와 sensor TF 확인 완료
- **TF 구조**: `map -> odom -> base_footprint -> base_link -> sensor frames` 구조의 시각 검증 가능
- **시뮬레이션 준비**: `/cmd_vel -> /odom` 테스트 노드는 추가됐고, 다음 단계는 virtual wheel link 추가
- **남은 blocker**: Gazebo Classic visual mesh 표시 문제는 별도로 남아 있음

---

## 0-1. 2026-04-26 업데이트

최근 상태를 짧게 정리하면 아래와 같다.

1. **Mari/Duri asset 명칭 정리**
   - `turtle_small`은 `Mari`, `turtle_big`은 `Duri` 기준으로 repository asset과 URDF 파일명을 정리했다.
   - Mari/Duri 캡처 이미지를 `mari_view`, `duri_view`로 분리했고, Mari는 `with_sensors`, `without_sensors`를 따로 보관했다.
2. **Onshape export 결과 보관**
   - Onshape에서 export한 Mari URDF/GLTF zip과 unpacked 결과를 `assets/robot_model_exports/onshape_urdf_exports`에 보관했다.
   - 새 Mari STEP/STL export 결과도 `assets/robot_model_exports`와 `trashbot_description/meshes`에 반영했다.
3. **Gazebo spawn 시도와 blocker 분리**
   - `trashbot_description` 빌드, `mari.urdf.xacro` 렌더링, `check_urdf` 파싱은 통과했다.
   - Gazebo model tree에 `mari`와 `base_footprint`가 표시되지만, 실제 visual mesh는 화면에 보이지 않는다.
   - 현재 blocker는 `mesh URI`, `mesh scale/origin`, `Gazebo Classic STL 처리`, `client view`를 순서대로 확인해야 하는 visual 표시 문제다.

현재 실용적인 해석은 다음과 같다.

- **로봇 모델링**: Mari frame/sensor 좌표와 visual asset 정리 완료
- **URDF/Xacro 검증**: Xacro 렌더링과 URDF 파싱은 통과
- **시뮬레이션 준비**: Gazebo entity spawn은 진행됐지만 visual mesh 표시 blocker 해결 필요
- **다음 작업**: `gzclient --verbose` 로그 확인, mesh bounds/scale 확인, 단순 visual baseline 비교, 이후 virtual wheel diff-drive 추가

---

## 0-2. 2026-04-25 업데이트

최근 상태를 짧게 정리하면 아래와 같다.

1. **Mari URDF/Xacro 준비**
   - Onshape에서 궤도/구동부 기준 `base_link_mc`를 만들고, ROS 기준 `+X 전방`, `+Y 왼쪽`, `+Z 위쪽` 방향을 정했다.
   - D435i, BNO08x, GPS의 `base_link` 기준 1차 상대 위치를 측정해 `mari.urdf.xacro` 변수로 기록했다.
2. **궤도/구동축 파라미터 정리**
   - 좌우 궤도 중심거리 `0.137553 m`, 가상 구동축 `y=±0.0687765 m`, 유효 궤도 반지름 후보 `0.021 m`를 기록했다.
   - 실제 구동축은 좌우 앞뒤 위치가 비대칭이므로 CAD 기준 기록으로 남기고, Gazebo/diff-drive에는 `x=0` 가상 바퀴를 쓰는 방향으로 정했다.
3. **저녁 이후 작업 계획**
   - Onshape에서 불필요한 `Revolute mate`를 제거하고 구동부 visual을 `Group`으로 고정한다.
   - Onshape URDF export를 시도한다.
   - Export 결과를 후처리해 Gazebo용 virtual wheel 기반 diff-drive 모델로 넘어간다.

현재 실용적인 해석은 다음과 같다.

- **로봇 모델링**: 센서 frame과 주행 파라미터 1차 측정 완료
- **시뮬레이션 준비**: Onshape URDF export와 Gazebo virtual wheel 구성이 다음 단계
- **남은 문제**: IMU 축 방향, GPS 안테나 중심, Xacro 렌더링/RViz2 검증, Gazebo 회전 부호 검증

---

## 0-3. 2026-04-16 기준 업데이트

최근 상태를 짧게 정리하면 아래와 같다.

1. **노트북 직결 경로**
   - `D435i + RTAB-Map`으로 발표용 3D 맵 생성과 `rtabmap.db` 저장까지 완료했다.
2. **Jetson Docker 경로**
   - `ROS 2 Humble + realsense2_camera` 환경 고정, color/depth 토픽 확인, `depth/image_rect_raw` 약 `30 Hz` 확인까지 끝냈다.
3. **Jetson -> 노트북 원격 GUI 경로**
   - 학교 Wi-Fi에서는 `ROS_DOMAIN_ID`, `ROS_DISCOVERY_SERVER`, `ROS_SUPER_CLIENT`를 맞춰도 discovery 실패였다.
   - 따라서 현재 병목은 카메라나 RTAB-Map이 아니라 **cross-machine ROS 2 네트워크**다.

현재 실용적인 해석은 다음과 같다.

- **발표 자료 확보**: 노트북 직결 경로로 우선 해결 가능
- **Jetson 실기기 검증**: Docker 기반 RGB-D 경로는 정상
- **남은 문제**: Jetson publish -> 외부 GUI subscribe 경로 재검증

---

## 1. 현재 프로젝트 위치

전체 로드맵 기준으로 보면 지금은 아래 위치다.

- `Stage 0`: 센서 입력 확인과 실행 환경 준비
  - Jetson/D435i/RTAB-Map baseline은 1차 완료, 추가 튜닝과 반복 검증 단계
- `Stage 1`: 로봇 모델링과 시뮬레이션
  - Onshape 기준 Mari `base_link`, 센서 frame, 궤도/구동축 파라미터 측정까지 시작

현재 Stage 0 안에서도 세부적으로는 이렇게 나뉜다.

1. D435i depth 입력 확인
2. D435i depth 시각화
3. D435i IMU 입력 확인
4. D435i 연속성/실시간성 문제 해결
5. D435i 단독 3D 맵핑 첫 시도

즉, 지금은 `센서 bring-up` 안에서도 거의 마지막 단계인 `실사용 수준 검증`에 가까워지고 있다.

---

## 2. 설치/적용 누락과 영향

이번 bring-up에서 실제로 막혔던 것은 아래 3가지였다.

### 2-1. `realsense2_camera` 미설치

- 쉬운 말:
  - D435i 데이터를 ROS2 토픽으로 바꿔주는 드라이버가 없었던 상태다.
- 왜 문제였나:
  - 이게 없으면 D435i를 연결해도 `/camera/...` 토픽이 생성되지 않는다.
  - 즉, `depth`, `color`, `IMU` 확인 자체를 시작할 수 없다.

### 2-2. `v4l-utils` 미설치

- 쉬운 말:
  - `v4l2-ctl` 같은 카메라 진단 도구가 들어 있는 패키지가 없었던 상태다.
- 왜 문제였나:
  - 공식 `setup_udev_rules.sh` 스크립트가 내부적으로 `v4l2-ctl`을 확인하는데, 이게 없어서 스크립트가 중간에 멈췄다.
  - 결과적으로 `udev rules` 설치가 진행되지 않았다.

### 2-3. `udev rules` 미적용

- 쉬운 말:
  - 리눅스가 RealSense USB/HID 장치에 어떤 권한으로 접근할지 정하는 규칙이 시스템에 없었던 상태다.
- 왜 문제였나:
  - `realsense-viewer`에서 `UDEV-Rules are missing!` 경고가 떴다.
  - IMU/HID 쪽에서 `Permission denied`, `scan_element` 접근 실패가 발생할 수 있었다.
  - 즉, IMU publish 불안정과 권한 문제의 직접 원인 후보였다.

정리하면:

- `realsense2_camera` 없음 -> ROS2 토픽 자체를 못 봄
- `v4l-utils` 없음 -> `udev rules` 설치 스크립트가 실패함
- `udev rules` 없음 -> IMU/HID 권한 문제가 생김

---

## 3. 현재까지 완료된 것

### 3-1. D435i 기본 입력 확인

완료된 것:

- `realsense2_camera` 설치
- D435i 장치 인식 확인
- color/depth 토픽 생성 확인
- depth 시각화 확인

확인된 대표 토픽:

- `/camera/camera/color/image_raw`
- `/camera/camera/color/camera_info`
- `/camera/camera/depth/image_rect_raw`
- `/camera/camera/aligned_depth_to_color/image_raw`

증빙:

- [`assets/2026-04-09_task59_d435i_depth_check/README.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-09_task59_d435i_depth_check/README.md)

### 3-2. D435i IMU 확인

완료된 것:

- `gyro`, `accel`, `imu` 토픽 확인
- 실제 값 수신 확인
- 주파수 안정성 확인
- 축 방향 1차 해석 확인

관찰값:

- `gyro`: 약 `199.8 Hz`
- `accel`: 약 `62.4 Hz`
- `/camera/camera/imu`: 약 `199.8 Hz`

해석:

- 이전 PC 기준에서는 IMU가 정상 동작했다
- 이전의 끊김은 센서 자체보다 실행 환경 충돌 영향이 컸음
- 다만 `2026-04-17` Jetson native bring-up에서는 `No HID info provided, IMU is disabled`와 `HID Motion Sensor Failure! bad optional access` 로그가 확인됐고 IMU topic이 뜨지 않았다
- 따라서 현재 운영 기준은 `Jetson baseline = IMU OFF`로 두고, IMU는 별도 진단 과제로 분리해 보는 편이 맞다

직접 관찰한 축 해석:

- 오른쪽 회전 -> `angular_velocity.y` 증가
- 위로 회전 -> `angular_velocity.x` 증가
- 렌즈 정면 축 기준 비틀기 -> `angular_velocity.z` 증가

관련 문서:

- [`docs/learning/D435i_IMU_Axis_Interpretation.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/D435i_IMU_Axis_Interpretation.md)

### 3-3. D435i 실시간성/연속성 문제 1차 해결

완료된 것:

- `udev rules` 적용
- 중복 실행 프로세스 정리
- `realsense-viewer`와 ROS2 동시 실행 금지 규칙 정리
- depth 저대역폭 실행 스크립트 추가

추가한 실행 스크립트:

- [`run_d435i_depth_low_bandwidth.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh)

현재 안정적으로 쓰는 방식:

- `424x240x15` 또는 `424x240x6`
- `depth-only`
- 컬러맵 시각화 별도 실행

### 3-4. 시각화/디버깅 도구 정리

추가/수정한 코드:

- [`depth_colormap_publisher.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py)
- [`depth_imu_local_mapper.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_imu_local_mapper.py)
- [`ros2_raw_rate_probe.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/ros2_raw_rate_probe.py)

### 3-5. Jetson native baseline 확인

완료된 것:

- `Jetson`에서 `D435i` native bring-up 재현
- color/depth topic 확인
- `USB type 3.2` 확인
- `424x240x15 + DetectionRate 2 + IMU OFF` 조합으로 `RTAB-Map` baseline 1차 기동 확인

관찰값:

- `rgbd_odometry` 품질값은 시작 직후 `0`에서 올라온 뒤 대체로 `60~160`
- 안정 구간에서는 `120~150` 정도가 반복 관찰됨
- `rtabmap_viz`는 GUI display 없는 shell에서 `qt.qpa.xcb` 오류로 종료됨
- `Jetson` 로컬 그래픽 세션에서는 `rtabmap_viz`가 실제로 열리고 `3D Map`과 trajectory가 표시되는 스크린샷도 확보함
- `2026-04-18` benchmark 기준으로 `quality 0~299`, 평균 `174.2`, `delay 0.099~0.270s`, 평균 `0.150s`가 확인됐다
- color와 aligned depth는 둘 다 약 `15 Hz` 수준으로 유지됐다
- `Docker` 쪽은 `daemon.json`에 `nvidia` runtime이 등록돼 있었고, 현재는 `VSLAM` 개발용 `compose` 뼈대와 `jetson-vslam:humble` 이미지 build까지 완료한 상태다
- `2026-04-20` 기준으로는 `Docker` 안 `rtabmap_viz`가 아니라 host `rtabmap_viz`가 `Docker` topic을 직접 읽는 우회 구조가 실제로 더 잘 맞았다

해석:

- `Jetson`에서도 `D435i + RTAB-Map` baseline은 IMU 없이 1차 동작한다
- GUI 세션 조건까지 포함한 baseline 확인은 1차 완료됐다
- 이제 핵심은 "`되나`"보다 "`이 baseline이 반복 가능하고 실용적인가`"를 더 정량적으로 고정하는 쪽이다
- 현재 남은 핵심 이슈는 `Jetson`의 `D435i IMU HID` 문제, baseline 품질 비교, 그리고 native 기준선을 Docker 안에서도 다시 재현하는 것이다
- `Docker` baseline은 이제 "`backend가 도나`" 수준은 넘었고, 현재는 "`Docker backend + host GUI` 구조를 운영 기준으로 고정할지`"를 보는 단계다
- 다만 `2026-04-19` 기준으로는 `D435i` 내장 IMU를 계속 파는 것보다, 이미 host에서 살아 있는 외부 `BNO08x`를 `ROS 2 /imu/data`로 연결해 실제 비교 실험을 먼저 진행하는 편이 더 우선순위가 높다
- `2026-04-19` 기준으로 외부 `BNO08x`는 host `venv`에서 `ROS 2` publisher 스모크 테스트까지 통과했고, `/imu/data`, `/imu/mag` topic이 실제로 올라오는 단계까지 왔다
- 아직 정식 장착 전이므로, 다음 비교 실험은 `BNO08x`를 `D435i` 몸체에 임시로 단단히 고정하고 `camera_link -> imu_link` static TF를 둔 상태에서 진행하는 것이 현재 기준선이다

### 3-6. Jetson 외부 BNO08x IMU bring-up 확인

완료된 것:

- 외부 `GY-BNO08x`를 `Jetson` 40핀 헤더에 `I2C`로 연결
- `i2c-1 / 0x4B` 인식 확인
- host `venv`에서 `accel / gyro / mag / quaternion` raw 값 확인
- host 기준 `live plot`과 `aircraft viewer` 시각화 스크립트/가이드 정리
- 팀원 재현용 handoff 문서 정리

관찰값:

- `i2cdetect` 기준으로 `i2c-1`에서 `0x4B`가 확인됐다
- host `venv`에서 센서를 움직였을 때 `gyro`, `accel`, `quat` 변화가 실제로 확인됐다
- Linux/Jetson 특성상 `I2C frequency is not settable in python` 경고는 보였지만, raw 값 수신 자체는 성공했다
- Docker 안 첫 재시험에서는 `/dev/i2c-1`에 `Permission denied`가 발생했다
- 이에 따라 `compose.yaml`에 host `i2c` group(`gid 116`)을 추가해, 컨테이너 재시험 준비까지 마친 상태다

해석:

- 외부 `BNO08x`는 하드웨어/배선 관점에서 일단 살아 있다
- 현재 병목은 센서 자체보다 `Docker 장치 권한`과 이후 `ROS 2 sensor_msgs/Imu` publish 연결이다
- 즉, `Jetson`에서는 `D435i` 내장 IMU 대안 후보를 실제로 확보하기 시작한 단계로 볼 수 있다

---

## 4. 지금 새로 진행 중인 것

현재는 `D435i 단독 RGB-D 3D 맵핑`을 시도하고 있다.

사용 중인 방향:

- `RGB + aligned depth`
- `RTAB-Map`
- `camera_link` 기준 프레임 사용

관련 새 스크립트:

- [`run_d435i_rgbd_mapping_camera.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh)
- [`run_d435i_rtabmap_light.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh)

현재 목표:

- 실내에서 D435i만으로 3D 맵이 실제로 쌓이는지 확인
- 맵이 너무 느리거나 끊기지 않는지 확인

최근 실측 결과:

- `rgbd_odometry` 품질값이 대부분 `130~190` 수준으로 연속 출력됨
- 즉, 이전의 `no odometry is provided` 중심 문제는 1차로 벗어남
- 남은 주요 점검 항목은 `TF 시작 시점 경고`, `체감 부드러움`, `실내 경로 누적 안정성`

Jetson native 1차 결과:

- `424x240x15`, `DetectionRate=2`, `IMU OFF` 조합으로 `RTAB-Map` baseline 재현
- `D435i color/depth`는 정상, `USB type 3.2` 확인
- `Jetson` 로컬 GUI에서도 `rtabmap_viz`가 실제로 열리는 것까지 확인
- 관련 증빙: [`2026-04-18_jetson_rtabmap_viz_gui_baseline_424x240x15_detectionrate2_imuoff.png`](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/screenshots/2026-04-18_jetson_rtabmap_viz_gui_baseline_424x240x15_detectionrate2_imuoff.png)
- 현재 남은 핵심 이슈는 `Jetson IMU HID failure`와 baseline 품질 비교다

---

## 5. 현재 문제점

### 문제 1. RTAB-Map 맵 갱신 속도가 느림

현재 가장 큰 문제다.

원인 후보:

1. `RTAB-Map` 기본 `DetectionRate=1Hz`
2. RGB-D 입력 자체가 무거움
3. GUI를 두 개 띄우면 더 느려짐
4. PC CPU 부하가 높음

실제 확인된 내용:

- launch 기본 상태에서 `RTAB-Map detection rate = 1.000000 Hz`
- 이후 경량 launch에서는 `3 Hz`로 올리는 방향 적용

### 문제 2. PC CPU 사용량이 높음

실제 확인:

- VS Code 프로세스가 CPU를 많이 사용 중
- `realsense2_camera_node` 자체보다 개발 도구 점유율이 더 큼

영향:

- `RTAB-Map`
- `rtabmap_viz`
- 이미지 구독

같은 GUI/영상 처리 노드에 부담이 갈 수 있음

### 문제 3. RGB 토픽도 생각보다 무거움

관찰:

- `ros2 topic hz /camera/camera/color/image_raw`가 기대보다 낮게 보였음

해석:

- color + depth + 정렬(aligned depth)까지 같이 쓰면 초반 실험치로는 무거울 수 있음

### 문제 4. 아직 "맵 완성 성공" 판정까지는 못 감

지금은:

- RTAB-Map이 실행됨
- odometry가 잡힘
- 3D 맵을 그릴 준비는 됨

하지만 아직 아래는 확정되지 않았다.

- 짧은 실내 구간에서 맵이 충분히 부드럽게 누적되는지
- loop 없이도 초기 구간이 안정적인지
- 현재 PC에서 실용적인 속도로 계속 쓸 수 있는지

즉, `실행 성공`과 `실사용 가능` 사이에서 아직 튜닝 중이다.

### 문제 5. 시작 시점 TF 경고

최근 로그에서 아래 경고를 1회 확인했다.

```text
Lookup would require extrapolation into the past
We received odometry message, but we cannot get the corresponding TF odom->camera_link ...
```

해석:

- `odom` TF와 센서 데이터 timestamp가 시작 시점에 완전히 맞지 않는 구간이 있었다.
- 현재는 오도메트리 전체 실패로 이어지지는 않았지만, 좌표계와 시간 동기화 관점에서 다음 점검 후보다.

### 문제 6. Jetson native 환경에서 D435i IMU가 비활성화됨

Jetson 실측 로그:

```text
No HID info provided, IMU is disabled
HID Motion Sensor Failure! bad optional access
```

영향:

- `/camera/camera/imu`, `gyro`, `accel` topic이 현재 기준선에서는 올라오지 않음
- `Jetson`에서 visual-inertial 조합은 아직 바로 진행할 수 없음

현재 판단:

- 기준선 운영은 우선 `IMU OFF`
- IMU는 별도 진단 과제로 분리
- 사용자 확인상 물리 연결은 이미 `SS USB` 케이블 직결 상태다
- `hidraw` 권한과 `udev` 규칙도 실제로 점검했고, `/dev/hidraw2`는 현재 `root:plugdev 660`까지 정리했다
- 하지만 `sudo`로 `realsense2_camera`를 올려도 동일하게 `No HID info provided, IMU is disabled`, `HID Motion Sensor Failure! bad optional access`가 재현됐고 `/camera/camera/imu`도 뜨지 않았다
- 따라서 지금은 단순 user permission 문제가 아니라 `Jetson`의 `HID/IIO/kernel path` 쪽이 더 핵심 원인 후보다
- 추가로 현재 Jetson 커널 config를 직접 확인한 결과 `# CONFIG_HID_SENSOR_HUB is not set`가 확인됐다
- `/lib/modules/$(uname -r)` 아래에도 `hid_sensor_hub`, `hid_sensor_accel_3d`, `hid_sensor_gyro_3d` 모듈이 보이지 않았다
- 반면 사용자가 확인한 바에 따르면 같은 `D435i` IMU는 노트북에서 `yaw / pitch / roll`까지 정상 동작했다
- 따라서 현재 판단은 `D435i` 센서 불량보다 `Jetson kernel/HID/IIO support 부재` 쪽이 훨씬 강하다
- 다음 1순위는 여전히 `IIO/HID sensor node`와 `USB control` 경로를 중심으로 재현하는 것이다

운영 판단:

- 이 이슈는 계속 기록하되, 현재 실험 우선순위는 외부 `BNO08x` 기준으로 `ROS 2 /imu/data`를 만들고 `RTAB-Map IMU OFF`와 비교하는 쪽으로 이동한다

### 문제 7. GUI display 없는 shell에서 `rtabmap_viz` 실행 실패

Jetson 실측 로그:

```text
qt.qpa.xcb: could not connect to display
Could not load the Qt platform plugin "xcb"
```

영향:

- `SSH`나 비GUI shell에서는 `rtabmap_viz`를 기준선 확인 도구로 바로 쓰기 어렵다
- GUI 검증은 직접 연결한 그래픽 세션에서 진행해야 한다

### 문제 8. 외부 `BNO08x`는 host 성공, Docker는 장치 권한 재시험 필요

현재 상태:

- host `venv`에서는 `i2c-1 / 0x4B` 기준 raw 값 확인에 성공
- Docker 첫 재시험에서는 `/dev/i2c-1` `Permission denied` 발생

영향:

- 외부 IMU를 바로 Docker/ROS 2 노드로 올리기 전에 컨테이너 장치 권한을 한 번 더 확인해야 한다
- 따라서 지금은 `host에서 센서 동작 확인`과 `Docker에서 운영 경로 확인`을 분리해서 보는 편이 맞다

현재 판단:

- `compose.yaml`에 host `i2c` group(`gid 116`)을 추가해 두었으므로, 다음 재시험에서 먼저 `/dev/i2c-1` 접근성만 다시 확인하면 된다
- 이 단계가 끝나면 다음은 `sensor_msgs/Imu` publisher 작성으로 넘어가는 흐름이 자연스럽다

### 문제 6. `flow` 프로필 이름과 실제 동작 불일치

최근 로그에서 아래를 확인했다.

```text
Vis/CorType=1 is not supported by OdometryF2M, using Features matching approach instead (type=0).
```

해석:

- 기존 `flow` 프로필 이름은 실제 동작을 정확히 설명하지 못했다.
- 그래서 현재는 기본 프로필을 `relaxed`로 바꾸고, `flow`는 backward-compatible alias로만 유지했다.

---

## 6. 현재 가장 유력한 원인 정리

지금까지의 로그와 관찰 기준으로 보면,
현재 느림의 우선순위는 아래처럼 본다.

1. `RTAB-Map detection rate` 기본값이 너무 낮음
2. `rviz + rtabmap_viz` 동시 사용 가능성
3. `640x480x15` RGB-D 조합이 현재 PC에는 무거움
4. VS Code 등 외부 CPU 부하
5. 시작 시점 TF 외삽 경고
6. 프로필 이름과 실제 오도메트리 backend 동작 불일치

즉, 지금은 센서 권한 문제보다 **처리량과 시각화 부하 최적화**가 핵심이다.

---

## 7. 현재 적용한 대응

### 7-1. 카메라 쪽 경량화

현재 기본 시도 방향:

- `RGB`: `640x480x6`
- `Depth`: `640x480x6`
- `align_depth`: 켬
- IMU: 끔

실행 스크립트:

- [`run_d435i_rgbd_mapping_camera.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh)

### 7-2. RTAB-Map 쪽 경량화

적용한 것:

- `rtabmap_viz`만 사용
- `rviz:=false`
- `qos_image:=2`
- `qos_camera_info:=2`
- `Rtabmap/DetectionRate = 3Hz`

실행 스크립트:

- [`run_d435i_rtabmap_light.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh)

현재 권장 프로필:

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh 3 relaxed
```

---

## 7. 현재 기준 추천 실행 절차

1. 기존 관련 프로세스 종료

```bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view'
```

2. RGB-D 카메라 경량 실행

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh
```

3. RTAB-Map 경량 실행

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh
```

또는 DetectionRate를 더 올려서 실험:

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh 5
```

---

## 8. 다음 액션

현재 가장 실용적인 다음 액션은 아래다.

1. Gazebo에서 `mari_visual_mesh.stl`이 보이지 않는 원인을 `gzclient --verbose`, mesh path, mesh scale/origin 기준으로 분리
2. 필요하면 STL 대신 DAE/OBJ/GLTF 변환본으로 Gazebo visual 표시를 재시험
3. `mari.urdf.xacro`에 `left_virtual_drive_wheel_link`, `right_virtual_drive_wheel_link`와 diff-drive용 joint/plugin 후보를 추가
4. Gazebo에서 `track_width = 0.137553 m`, `effective_track_radius = 0.021 m` 기준으로 `/cmd_vel` 전진/회전이 되는지 확인
5. BNO08x 보드 silk의 x/y/z 방향과 ROS `imu_link` 축 방향을 비교해 `imu_roll/pitch/yaw` 보정값 정리
6. GPS 안테나 중심과 현재 `gps_link_mc` 기준점이 맞는지 확인
7. `xacro` 렌더링과 RViz2 표시로 `base_link`, `camera_link`, `imu_link`, `gps_link` 위치와 방향 검증

관련 문서:

- [`docs/progress/AI_Assisted_Algorithm_Switching_Workflow.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/AI_Assisted_Algorithm_Switching_Workflow.md)

---

## 9. 지금 상태 한 줄 요약

지금은 `Jetson` native/Docker RTAB-Map baseline과 외부 `BNO08x` 확인을 바탕으로, **Mari 로봇의 URDF/Xacro 모델링을 Gazebo spawn 단계까지 확장했고, visual mesh 표시 blocker를 해결한 뒤 virtual wheel 주행 검증으로 넘어가는 상태**에 있다.

---

## 10. Jetson 작업 전환 현황

현재는 `PC`에서 개념 정리와 1차 실험을 진행하던 단계에서 한 걸음 더 나아가,
**`Jetson`에서 직접 `VSLAM`을 돌리는 실행 환경 검증 단계**로 넘어가고 있다.

지금 작업 방식은 아래와 같다.

1. 먼저 `SSH`로 `Jetson`에 접속해 기본 환경과 저장소 접근을 정리한다.
2. 그 다음 `Jetson`에 `모니터`, `키보드`, `마우스`를 직접 연결해 GUI와 장치 상태를 현장에서 확인한다.
3. 이 상태에서 `D435i`, `RTAB-Map`, `realsense-viewer`, `RViz`, `rtabmap_viz`처럼 화면과 장치 상태를 함께 봐야 하는 작업을 진행한다.

이 전환이 중요한 이유는 아래와 같다.

- `Jetson` 실제 연산 성능 기준으로 `RTAB-Map`이 어느 정도까지 실용 속도로 도는지 확인해야 한다.
- `USB`, `udev`, `GUI`, `device busy`, `viewer` 같은 문제는 `Jetson` 현장에서 직접 보는 편이 훨씬 빠르다.
- 이후 `D435i + Jetson + 로봇 본체` 조합으로 넘어갈 때, 지금 정리한 실행 절차가 그대로 기반이 된다.

기록 원칙도 같이 정리한다.

- 전체 프로젝트 상태 요약은 계속 이 문서에서 관리한다.
- `Jetson` 현장 작업 기록은 [`jetson/README.md`](../../jetson/README.md)와 [`jetson/daily/2026-04-17/README.md`](../../jetson/daily/2026-04-17/README.md)부터 분리 관리한다.

즉, 지금 시점의 상태는
`D435i 실험이 개념 검증 단계에서 끝난 것이 아니라, Jetson 실기 환경으로 옮겨가며 실제 운영 가능성을 확인하기 시작한 상태`라고 정리할 수 있다.
