# D435i Ubuntu YOLO Depth Handoff

## 결론

팀원이 Ubuntu 노트북에서 `Intel RealSense D435i`를 사용해 YOLO 객체탐지와 depth 기반 위치 계산을 하려면, 아래 순서로 진행하는 것이 가장 안전하다.

1. Ubuntu에서 D435i가 USB 3.x로 인식되는지 확인한다.
2. `realsense-viewer`로 카메라와 depth가 SDK 단계에서 정상인지 확인한다.
3. `realsense2_camera`로 ROS2 color/depth 토픽을 publish한다.
4. YOLO는 color image에서 객체를 찾고, 위치 계산은 aligned depth와 `camera_info`로 한다.
5. 처음에는 IMU를 끄고 RGB-D만 안정화한다.

---

## 대상

이 문서는 아래 작업을 맡은 팀원에게 전달하기 위한 handoff 자료다.

- Ubuntu 노트북에서 D435i 사용
- RealSense color/depth 스트림 확인
- YOLO 객체탐지 입력으로 color image 사용
- depth image를 이용한 객체 거리 또는 3D 위치 계산

---

## 먼저 알아야 하는 용어

- `D435i`: RGB 카메라, depth 카메라, IMU가 들어 있는 Intel RealSense 카메라다.
- `depth image`: 각 픽셀에 색이 아니라 거리값이 들어 있는 영상이다.
- `aligned depth`: color image 좌표에 맞춰 정렬된 depth image다. YOLO bbox와 depth를 같이 쓰려면 이것을 써야 한다.
- `camera_info`: 카메라 내부 파라미터다. 픽셀 좌표를 3D 좌표로 바꿀 때 필요하다.
- `realsense2_camera`: D435i 데이터를 ROS2 토픽으로 publish해주는 ROS2 드라이버다.
- `YOLO bbox`: YOLO가 찾은 객체의 사각형 영역이다.

---

## 전제 환경

권장 기준:

```text
Ubuntu 22.04
ROS2 Humble
Intel RealSense D435i
USB 3.x 포트/케이블
```

ROS2 Humble이 이미 설치되어 있다는 전제로 진행한다.

ROS2가 설치되어 있는지 확인한다.

```bash
source /opt/ros/humble/setup.bash
echo $ROS_DISTRO
which ros2
```

기대 결과:

```text
humble
/opt/ros/humble/bin/ros2
```

---

## 1. 필요한 패키지 설치

ROS2에서 D435i를 쓰기 위한 기본 패키지를 설치한다.

```bash
sudo apt update
sudo apt install -y \
  ros-humble-realsense2-camera \
  ros-humble-cv-bridge \
  ros-humble-image-transport \
  ros-humble-rqt-image-view \
  v4l-utils \
  git
```

각 패키지 역할:

- `ros-humble-realsense2-camera`: D435i를 ROS2 토픽으로 바꿔주는 드라이버
- `ros-humble-cv-bridge`: ROS2 image와 OpenCV image를 변환
- `ros-humble-rqt-image-view`: ROS2 image 토픽을 화면으로 확인
- `v4l-utils`: `/dev/video*`와 카메라 장치 확인

---

## 2. udev rules 적용

`udev rules`는 USB 장치 권한을 자동으로 잡아주는 Linux 규칙이다.

이게 없으면 `realsense-viewer`에서 아래와 같은 경고가 나올 수 있다.

```text
UDEV-Rules are missing!
Permission denied
```

적용 방법:

```bash
cd /tmp
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
sudo ./scripts/setup_udev_rules.sh
sudo udevadm control --reload-rules
sudo udevadm trigger
```

적용 후 D435i USB를 뺐다가 다시 꽂는다.

확인:

```bash
ls /etc/udev/rules.d | grep realsense
```

---

## 3. D435i 장치 인식 확인

카메라가 OS에서 보이는지 먼저 확인한다.

```bash
lsusb | grep -i realsense
v4l2-ctl --list-devices
ls /dev/video*
```

USB 속도도 확인한다.

```bash
lsusb -t
```

확인 포인트:

- `Intel RealSense D435I`가 보여야 한다.
- USB가 `5000M` 또는 `USB 3.x` 계열로 잡히는 것이 좋다.
- `/dev/video0`, `/dev/video1` 같은 video device가 여러 개 생긴다.

주의:

- USB 2.x로 잡히면 color/depth 동시 사용에서 프레임 저하가 생길 수 있다.
- 케이블과 포트를 먼저 바꿔보는 것이 가장 빠른 해결책이다.

---

## 4. realsense-viewer로 하드웨어 먼저 확인

`realsense-viewer`는 ROS2를 거치지 않고 RealSense SDK 단계에서 카메라를 확인하는 도구다.

```bash
which realsense-viewer
realsense-viewer
```

설치되어 있지 않으면, 일단 ROS2 토픽 확인으로 넘어가도 된다. 다만 하드웨어 문제 분리에는 viewer가 가장 좋다.

viewer에서 확인할 것:

- 장치가 자동으로 인식되는가
- RGB 스트림이 켜지는가
- depth 스트림이 켜지는가
- 30초 이상 끊기지 않는가

판단 기준:

- viewer도 끊기면 USB, 권한, SDK, 하드웨어 문제 가능성이 크다.
- viewer는 정상인데 ROS2만 끊기면 ROS2 드라이버 설정, QoS, 구독 처리 병목 가능성이 크다.

---

## 5. ROS2로 D435i RGB-D 실행

처음에는 IMU를 끄고 color/depth만 켠다.

```bash
source /opt/ros/humble/setup.bash

ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  align_depth.enable:=true \
  enable_gyro:=false \
  enable_accel:=false \
  rgb_camera.color_profile:=640x480x15 \
  depth_module.depth_profile:=640x480x15
```

중요한 설정:

- `align_depth.enable:=true`
  - color image 좌표와 depth image 좌표를 맞춘다.
  - YOLO bbox와 depth를 같이 쓰려면 켜야 한다.
- `enable_gyro:=false`, `enable_accel:=false`
  - 처음에는 IMU를 꺼서 문제를 단순하게 만든다.
- `640x480x15`
  - 처음 테스트용으로 적당한 해상도와 FPS다.
  - 느리면 `424x240x15`로 낮춘다.

현재 repo에 있는 실행 스크립트를 사용할 수도 있다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash

bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh 640x480x15 640x480x15 false
```

---

## 6. ROS2 토픽 확인

새 터미널에서 확인한다.

```bash
source /opt/ros/humble/setup.bash

ros2 topic list | grep '^/camera/camera'
```

YOLO + depth에 필요한 핵심 토픽:

```text
/camera/camera/color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/aligned_depth_to_color/camera_info
```

프레임 주기를 확인한다.

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

기대 결과:

- `640x480x15`로 실행했다면 대략 15Hz 근처
- `424x240x15`로 실행했다면 대략 15Hz 근처

---

## 7. 영상 확인

```bash
source /opt/ros/humble/setup.bash
ros2 run rqt_image_view rqt_image_view
```

확인할 토픽:

```text
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
```

주의:

- raw depth는 회색조처럼 보일 수 있다.
- 이것은 정상이다. raw depth는 사람이 보기 위한 컬러 영상이 아니라 거리값 영상이다.

---

## 8. YOLO와 depth를 결합하는 기본 구조

YOLO는 color image에서 객체를 찾고, depth는 해당 객체의 실제 거리를 구하는 데 사용한다.

전체 흐름:

```text
color image
  -> YOLO detection
  -> bbox center pixel 계산
  -> aligned depth에서 같은 픽셀의 depth 읽기
  -> camera_info로 3D 좌표 계산
```

반드시 `aligned_depth_to_color/image_raw`를 사용한다.

이유:

- YOLO bbox는 color image 기준 좌표다.
- 일반 depth image는 color image와 픽셀 좌표가 다를 수 있다.
- aligned depth는 color image 좌표계에 맞춰진 depth라서 bbox와 바로 대응된다.

---

## 9. 픽셀 좌표를 3D 좌표로 바꾸는 방법

YOLO bbox 중심 픽셀을 `(u, v)`라고 한다.

`camera_info`에서 아래 값을 읽는다.

```text
fx, fy: 초점거리
cx, cy: 이미지 중심점
```

aligned depth에서 `(u, v)`의 거리값을 `Z`라고 하면, 카메라 기준 3D 좌표는 아래처럼 계산한다.

```text
X = (u - cx) * Z / fx
Y = (v - cy) * Z / fy
Z = depth
```

주의:

- ROS optical frame에서는 보통 `Z`가 카메라 전방, `X`가 오른쪽, `Y`가 아래쪽이다.
- 로봇 기준 `base_link` 좌표로 바꾸려면 TF 변환이 필요하다.

---

## 10. depth 값을 읽을 때 주의할 점

객체 bbox 중심 한 픽셀만 읽으면 노이즈가 클 수 있다.

권장 방식:

1. bbox 중심 주변 `5x5` 또는 `11x11` 영역을 잡는다.
2. depth가 `0`인 픽셀은 제외한다.
3. 너무 가까운 값이나 너무 먼 값은 제외한다.
4. 남은 값의 median을 사용한다.

예시 판단:

```text
depth == 0       -> invalid
depth < 0.15 m   -> 너무 가까워서 제외
depth > 5.0 m    -> 실내/근거리 작업에서는 제외 가능
```

---

## 11. YOLO 쪽 권장 시작점

처음부터 고해상도로 가지 않는다.

추천 시작값:

```text
color: 640x480x15
depth: 640x480x15
```

노트북이 느리면:

```text
color: 424x240x15
depth: 424x240x15
```

성능 확인 기준:

- YOLO 추론 FPS
- color/depth topic hz
- CPU/GPU 사용량
- detection 결과가 depth와 안정적으로 매칭되는지

---

## 12. 흔한 실수

### 1. realsense-viewer와 ROS2 launch를 동시에 실행

같은 카메라를 두 프로세스가 동시에 잡으면 문제가 생길 수 있다.

정리 명령:

```bash
pkill -f 'realsense2_camera|rs_launch.py|realsense-viewer|rqt_image_view|rviz2'
```

### 2. raw depth와 aligned depth를 헷갈림

YOLO bbox와 결합할 때는 아래를 사용한다.

```text
/camera/camera/aligned_depth_to_color/image_raw
```

### 3. camera_info를 안 씀

단순 거리는 depth만으로 가능하지만, 3D 좌표 계산에는 `camera_info`가 필요하다.

### 4. USB 2.x 연결

프레임 드랍이 생기면 먼저 확인한다.

```bash
lsusb -t
```

### 5. IMU부터 켬

D435i IMU는 추가 권한/드라이버 이슈가 생길 수 있다.

처음 목표가 YOLO + depth면 IMU는 끄고 시작한다.

---

## 13. 팀원이 최소로 확인해야 하는 체크리스트

- [ ] `lsusb | grep -i realsense`에서 D435i가 보인다.
- [ ] `lsusb -t`에서 USB 3.x로 잡힌다.
- [ ] `realsense-viewer`에서 color/depth가 정상이다.
- [ ] `ros2 launch realsense2_camera ...`가 실행된다.
- [ ] `/camera/camera/color/image_raw`가 보인다.
- [ ] `/camera/camera/aligned_depth_to_color/image_raw`가 보인다.
- [ ] `rqt_image_view`에서 color/depth를 볼 수 있다.
- [ ] YOLO bbox 중심 픽셀에서 depth를 읽을 수 있다.
- [ ] depth `0` 값과 노이즈를 필터링한다.
- [ ] 필요하면 `camera_info`로 3D 좌표를 계산한다.

---

## 14. 관련 repo 자료

기존 자료 중 팀원이 같이 보면 좋은 문서:

- [2026-04-11 D435i 트러블슈팅 일지](../../daily/2026-04-11/README.md)
- [D435i RealSense Viewer Triage Checklist](../troubleshooting/D435i_RealSense_Viewer_Triage_Checklist.md)
- [D435i RealTime Troubleshooting History](../troubleshooting/D435i_RealTime_Troubleshooting_History.md)
- [How realsense2_camera converts D435i to ROS2 Topics](./How_realsense2_camera_converts_D435i_to_ROS2_Topics.md)
- [D435i RTAB-Map VSLAM Manual](./D435i_RTABMap_VSLAM_Manual.md)
- [D435i Depth Check Evidence](../../assets/2026-04-09_task59_d435i_depth_check/README.md)

실행 스크립트:

- [run_d435i_rgbd_mapping_camera.sh](../../06_Debugging/run_d435i_rgbd_mapping_camera.sh)
- [run_d435i_depth_low_bandwidth.sh](../../06_Debugging/run_d435i_depth_low_bandwidth.sh)
- [depth_colormap_publisher.py](../../06_Debugging/depth_colormap_publisher.py)

---

## 15. 다음 작업 제안

팀원이 YOLO 코드까지 붙인다면 다음 순서로 진행한다.

1. color image subscriber 작성
2. YOLO inference 적용
3. aligned depth subscriber 추가
4. color/depth timestamp가 너무 벌어지지 않는지 확인
5. bbox 중심 주변 depth median 계산
6. `camera_info`로 3D 좌표 계산
7. 결과를 `/trash_detections` 같은 토픽으로 publish

처음부터 목표는 완성된 객체탐지 시스템이 아니라, 아래 한 줄을 출력하는 것이다.

```text
class=bottle confidence=0.91 depth=1.23m camera_xyz=(0.12, -0.03, 1.23)
```

이게 되면 YOLO + depth 결합의 핵심 경로는 열린 것이다.
