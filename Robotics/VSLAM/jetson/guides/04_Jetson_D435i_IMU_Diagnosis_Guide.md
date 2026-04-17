# Jetson D435i IMU 진단 가이드

## 목적

- 현재 `Jetson`에서 발생하는 `D435i IMU HID` 이슈를 같은 순서로 다시 진단한다.

## 시작 전

- 이 가이드는 `Jetson`에 `D435i`가 실제 연결되어 있다고 가정한다.
- `realsense-viewer`, `RTAB-Map`, `RViz`는 모두 끈 상태에서 시작한다.
- 현재 기준선 운영은 `IMU OFF`지만, 이 가이드는 왜 `IMU`가 안 뜨는지 확인하는 용도다.

## 1. 세션 정리

```bash
source /opt/ros/humble/setup.bash
pkill -f 'realsense2_camera|rs_launch.py|realsense-viewer|rtabmap|rtabmap_viz|rviz2|rqt_image_view' || true
pgrep -af 'realsense2_camera|rs_launch.py|realsense-viewer|rtabmap' || true
```

## 2. 장치 인식과 커널 로그 확인

```bash
lsusb | grep -i realsense
lsusb -t
journalctl -k -b --no-pager | grep -iE 'realsense|hid|uvc|iio' | tail -n 80
```

`lsusb -t`에 upstream `Hub` 장치가 보여도, 그걸 바로 `외부 허브 사용`으로 단정하지는 않는다.
사용자 기준 물리 연결 상태와 OS 토폴로지 표시는 다를 수 있으므로, 여기서는 우선 `IIO/HID` 노드가 실제로 생기는지에 집중한다.

## 3. IMU 포함 launch 다시 실행

```bash
source /opt/ros/humble/setup.bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_gyro:=true \
  enable_accel:=true \
  unite_imu_method:=1 \
  enable_sync:=true \
  align_depth.enable:=true
```

## 4. 새 터미널에서 node/topic 확인

```bash
source /opt/ros/humble/setup.bash
ros2 node list
ros2 topic list | grep -E 'camera|gyro|accel|imu'
```

## 5. color/depth는 살아 있는지 먼저 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /camera/camera/color/camera_info --once
ros2 topic echo /camera/camera/depth/camera_info --once
```

## 6. IMU topic이 보일 때만 1회 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /camera/camera/imu --once
```

## 7. IMU topic이 안 보이면 launch 로그에서 아래 문구를 찾는다

```text
No HID info provided, IMU is disabled
HID Motion Sensor Failure! bad optional access
```

## 8. IIO/HID 노드 존재 여부 확인

```bash
ls -la /sys/bus/iio/devices || true
find /sys/bus/iio/devices -maxdepth 2 -type f | grep -E 'name|scan_elements' | head -n 40 || true
```

`hidraw`는 보이는데 `/sys/bus/iio/devices`가 비어 있으면, 현재는 `HID` 인터페이스는 잡히지만 IMU sensor node는 안 올라오는 상태로 해석한다.

## 9. 현재 운영 기준으로 되돌아가기

IMU가 계속 안 뜨면 현재 baseline은 아래처럼 유지한다.

```bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 false
```

새 터미널에서:

```bash
source /opt/ros/humble/setup.bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed false
```
