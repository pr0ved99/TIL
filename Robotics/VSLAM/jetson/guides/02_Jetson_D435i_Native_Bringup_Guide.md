# Jetson D435i Native Bring-up 가이드

## 목적

- `Jetson`에서 `D435i`가 native ROS 2 환경에서 정상 동작하는지 확인한다.

## 시작 전

- 이 가이드는 `Jetson`에 `D435i`가 연결되어 있다고 가정한다.
- `realsense-viewer`는 ROS 2 launch와 동시에 켜지 않는다.
- `2026-04-17` 실측 기준으로 color/depth는 재현됐지만, 현재 `Jetson`에서는 IMU가 `HID` 오류로 안 뜰 수 있다.

## 1. 세션 정리

```bash
source /opt/ros/humble/setup.bash
pkill -f 'realsense2_camera|rs_launch.py|realsense-viewer|rtabmap|rtabmap_viz|rviz2|rqt_image_view' || true
pgrep -af 'realsense2_camera|rs_launch.py|realsense-viewer' || true
```

## 2. D435i 장치 인식 확인

```bash
lsusb | grep -i realsense
```

## 3. RealSense ROS 패키지 확인

```bash
ros2 pkg list | grep realsense2_camera
```

## 4. 카메라 launch 실행

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_gyro:=true \
  enable_accel:=true \
  unite_imu_method:=1 \
  enable_sync:=true \
  align_depth.enable:=true
```

## 5. 새 터미널에서 토픽 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E 'camera|gyro|accel|imu'
```

## 6. color/depth 확인과 IMU 존재 여부 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /camera/camera/color/camera_info --once
ros2 topic echo /camera/camera/depth/camera_info --once
ros2 topic list | grep -E 'gyro|accel|imu'
```

현재 `Jetson` 실측 기준으로 IMU topic이 안 뜰 수 있다.
이 경우 launch 로그에서 아래 문구를 확인한다.

```text
No HID info provided, IMU is disabled
HID Motion Sensor Failure! bad optional access
```

IMU topic이 실제로 보일 때만 아래처럼 추가 확인한다.

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /camera/camera/imu --once
```

## 7. 토픽 Hz 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

IMU topic이 실제로 존재할 때만 아래를 추가 실행한다.

```bash
source /opt/ros/humble/setup.bash
ros2 topic hz /camera/camera/imu
```

## 8. 필요 시 GUI 확인

### 터미널 1

```bash
source /opt/ros/humble/setup.bash
ros2 run rqt_image_view rqt_image_view
```

### 볼 토픽

```text
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
```

## 9. 종료 전 정리

```bash
pkill -f 'realsense2_camera|rs_launch.py|rqt_image_view' || true
```
