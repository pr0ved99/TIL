# Mari D435i Jetson RTAB-Map Handoff

## 목적

- 다른 `Jetson`에 `D435i`가 장착된 `Mari` 하드웨어를 연결해 `RTAB-Map`을 다시 띄우는 절차를 팀원에게 넘긴다.
- 이번 단계의 목표는 자율주행 전체가 아니라, **Mari에 달린 D435i로 RGB-D 기반 3D mapping 화면이 실제로 뜨는지 확인**하는 것이다.
- `RTAB-Map`은 RGB 이미지와 depth 이미지를 이용해 로봇의 이동 추정과 3D map 생성을 같이 수행하는 SLAM 도구다.

## 현재 권장 경로

- 1순위: `Docker backend + Jetson host rtabmap_viz`
- 이유:
  - Docker 안에서는 `D435i camera`, `rgbd_odometry`, `rtabmap` backend를 반복 가능하게 실행한다.
  - Jetson host에서는 `rtabmap_viz`만 실행해 Docker GUI/OpenGL 문제를 피한다.
  - 현재 Jetson 기준 안정 baseline은 `light = 424x240x15 + DetectionRate 2 + IMU OFF`다.

## 현재 하드웨어 전제

- 로봇: `Mari`
- 카메라: `Intel RealSense D435i`
- D435i 장착 상태: Mari 하드웨어에 장착됨
- 시작 기준: `D435i color/depth`만 사용
- IMU 기준: 우선 `IMU OFF`

주의:

- Jetson에서 D435i 내장 IMU는 `HID Motion Sensor Failure`가 날 수 있으므로, 처음부터 IMU를 켜고 시작하지 않는다.
- 외부 `BNO08x`가 붙어 있더라도, 이번 핸드오프의 첫 목표는 `D435i image-only RTAB-Map` 재현이다.
- GUI 확인은 SSH보다 Jetson에 모니터/키보드/마우스를 직접 연결한 로컬 그래픽 세션에서 진행하는 편이 안전하다.

## 이 핸드오프 문서가 다루는 범위

1. Jetson에서 저장소와 Docker 실행 준비 확인
2. Mari에 장착된 D435i가 USB와 ROS 2 topic으로 보이는지 확인
3. Docker backend로 `D435i + RTAB-Map` 실행
4. Jetson host에서 `rtabmap_viz`로 3D map 확인
5. 실패 시 어느 단계가 문제인지 빠르게 분리

## 바로 실행할 문서 묶음

1. [00_Jetson_Session_Start_Guide.md](../guides/00_Jetson_Session_Start_Guide.md)
2. [08_Jetson_Docker_Enablement_Guide.md](../guides/08_Jetson_Docker_Enablement_Guide.md)
3. [09_Jetson_VSLAM_Docker_Bringup_Guide.md](../guides/09_Jetson_VSLAM_Docker_Bringup_Guide.md)
4. [21_Jetson_Docker_RTABMap_Baseline_Guide.md](../guides/21_Jetson_Docker_RTABMap_Baseline_Guide.md)
5. [22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md](../guides/22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md)
6. [02_Jetson_D435i_Native_Bringup_Guide.md](../guides/02_Jetson_D435i_Native_Bringup_Guide.md)
7. [03_Jetson_RTABMap_Baseline_Guide.md](../guides/03_Jetson_RTABMap_Baseline_Guide.md)

## 0. 저장소 위치 전제

기존 Jetson 문서는 아래 경로를 기준으로 작성되어 있다.

```bash
~/yh_ws/TIL/Robotics/VSLAM
```

다른 경로에 clone했다면, 아래 명령의 `~/yh_ws/TIL` 부분만 실제 workspace root로 바꾼다.

## 1. Jetson 세션 시작

이 단계는 이전 실행 프로세스가 남아 RTAB-Map topic이나 TF가 꼬이는 것을 막는 정리 단계다.

```bash
cd ~/yh_ws/TIL
git pull

source /opt/ros/humble/setup.bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view' || true
pgrep -af 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view' || true
```

## 2. D435i가 Jetson에서 보이는지 확인

```bash
lsusb | grep -i realsense
ls /dev/video*
```

기대:

- `Intel RealSense Depth Camera 435i` 또는 비슷한 이름이 보인다.
- `/dev/video0`부터 여러 video device가 보인다.

추가로 ROS 2 패키지가 보이는지 확인한다.

```bash
source /opt/ros/humble/setup.bash
ros2 pkg list | grep realsense2_camera
```

## 3. Jetson 성능 모드와 X11 허용

이 단계는 실시간성이 낮아지는 것을 줄이고, host GUI와 Docker GUI 접근 문제를 줄이는 준비다.

```bash
sudo nvpmodel -m 2
sudo jetson_clocks
xhost +local:docker
echo "DISPLAY=${DISPLAY:-empty}"
```

참고:

- `nvpmodel -m 2`는 Jetson Orin Nano 25W 성능 모드 기준으로 사용했던 값이다.
- 다른 Jetson 모델이면 가능한 power mode 번호가 다를 수 있으므로 `sudo nvpmodel -q`로 먼저 확인한다.

## 4. Docker 상태 확인

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/check_jetson_docker_preflight.sh

docker info | grep -i "Runtimes\\|Default Runtime\\|nvidia"
docker run --rm hello-world
```

기대:

- `Runtimes`에 `nvidia`가 보인다.
- `hello-world`가 정상 종료된다.

`docker daemon access is not ready`가 나오면 아래 문서를 먼저 끝낸다.

- [08_Jetson_Docker_Enablement_Guide.md](../guides/08_Jetson_Docker_Enablement_Guide.md)

## 5. Docker image build

새 Jetson이거나 이미지가 없는 Jetson이면 한 번 빌드한다.

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM/jetson/docker
cp -n .env.example .env
docker compose --env-file .env build
```

실행 스크립트들은 필요할 때 `jetson/docker/.env`를 자동 생성/갱신한다.
그래도 수동으로 `.env`를 먼저 보고 싶으면:

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM/jetson/docker
cat .env
```

## 6. 추천 실행: Docker backend 한 번에 시작

이 단계가 가장 짧은 실행 경로다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
```

이 명령이 하는 일:

- Docker `jetson-vslam-camera` 서비스 실행
- Docker `jetson-vslam-rtabmap` 서비스 실행
- preset `light` 적용
  - color/depth: `424x240x15`
  - `DetectionRate=2`
  - `queue_size=15`
  - `IMU OFF`

로그를 보고 싶으면:

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM/jetson/docker
docker compose --env-file .env logs -f jetson-vslam-camera jetson-vslam-rtabmap
```

## 7. backend topic 확인

새 터미널에서:

```bash
source /opt/ros/humble/setup.bash
ros2 node list | grep -E 'camera|rtabmap'
ros2 topic list | grep -E '/camera/camera/color/image_raw|/camera/camera/aligned_depth_to_color/image_raw|/rtabmap/odom|/rtabmap/odom_info|/rtabmap/mapData'
```

Hz 확인:

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

기대:

- `light` preset이면 대략 `15 Hz` 근처가 보인다.
- `/rtabmap/odom`, `/rtabmap/odom_info`, `/rtabmap/mapData`가 보이면 backend가 살아 있는 것이다.

## 8. host에서 RTAB-Map GUI 실행

새 터미널에서:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

기대 화면:

- 왼쪽 `Odometry` 또는 `Loop closure detection` 영역에 camera frame과 feature가 보인다.
- 오른쪽 `3D Map`에 점군과 trajectory가 누적된다.
- Mari를 천천히 움직이면 trajectory와 map이 같이 변한다.

## 9. 직접 분리 실행이 필요할 때

한 번에 실행하는 stack이 부담되면 camera와 rtabmap을 분리해서 실행한다.

### 터미널 1: camera

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh light
```

### 터미널 2: RTAB-Map backend

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh light
```

### 터미널 3: host viewer

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

## 10. Native fallback

Docker가 아직 준비되지 않았고 빠르게 카메라와 RTAB-Map만 확인해야 하면 native 경로로 간다.

### 터미널 1: D435i RGB-D

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM
source /opt/ros/humble/setup.bash
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 false
```

### 터미널 2: RTAB-Map

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM
source /opt/ros/humble/setup.bash
bash 06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed false
```

Native 경로는 Docker보다 환경 차이를 더 많이 타므로, 팀원 인계용 기준선은 가능하면 Docker 경로로 맞춘다.

## 완료 조건

- `lsusb`에서 D435i 확인
- `/camera/camera/color/image_raw` 확인
- `/camera/camera/aligned_depth_to_color/image_raw` 확인
- `/rtabmap/odom` 확인
- `/rtabmap/mapData` 확인
- `rtabmap_viz`에서 3D map 또는 trajectory가 움직이는 화면 확인

## 실패하면 먼저 볼 것

### D435i가 안 보일 때

```bash
lsusb | grep -i realsense
ls /dev/video*
dmesg | tail -n 50
```

확인할 것:

- USB-C 케이블이 data 지원 케이블인지
- D435i가 USB 3.x로 붙었는지
- 카메라가 `realsense-viewer` 같은 다른 프로세스에 잡혀 있지 않은지

### camera topic은 있는데 RTAB-Map이 비어 있을 때

```bash
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E 'camera|rtabmap|odom'
ros2 topic echo /rtabmap/odom_info --once
```

확인할 것:

- `/camera/camera/color/camera_info`가 보이는지
- `/camera/camera/aligned_depth_to_color/image_raw`가 보이는지
- `quality`가 계속 `0`인지

### GUI만 안 뜰 때

```bash
echo "$DISPLAY"
xhost +local:docker
```

확인할 것:

- SSH 터미널이 아니라 Jetson 로컬 GUI 터미널인지
- Docker backend는 살아 있는데 viewer만 문제인지
- host viewer script를 쓰고 있는지

### 너무 느릴 때

우선 `light` preset을 유지한다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
```

`medium`은 map이 조금 더 조밀하지만 Jetson에서는 부담이 커질 수 있다.

## 결과 기록 권장

성공하면 아래 항목을 팀 공유 문서나 daily에 남긴다.

- Jetson 모델명
- JetPack/L4T 버전
- D435i USB 인식 결과
- 사용 preset: `light` 또는 `medium`
- color/depth Hz
- `/rtabmap/odom_info` quality 값
- `rtabmap_viz` 3D map screenshot 또는 영상

## 한 줄 인계

- Mari에 D435i가 달린 다른 Jetson에서는 먼저 `Docker light + host rtabmap_viz` 경로로 image-only RTAB-Map을 재현하고, color/depth/odom/mapData가 확인된 뒤에 IMU나 자율주행 연동으로 넘어간다.
