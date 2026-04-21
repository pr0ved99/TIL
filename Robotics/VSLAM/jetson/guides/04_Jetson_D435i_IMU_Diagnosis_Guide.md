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

## 9. Jetson 커널이 HID sensor hub를 지원하는지 확인

```bash
cd /home/jetson/yh_ws/TIL
chmod +x ./Robotics/VSLAM/jetson/scripts/check_d435i_imu_kernel_support.sh
./Robotics/VSLAM/jetson/scripts/check_d435i_imu_kernel_support.sh
```

특히 아래가 핵심이다.

```text
# CONFIG_HID_SENSOR_HUB is not set
```

이 문구가 현재 Jetson 커널 config에 실제로 보이면, `D435i` 내장 IMU가 의존하는 `HID sensor hub` 경로가 아예 꺼져 있는 상태로 해석한다.

즉, 이 경우에는:

- `udev`
- `hidraw` 권한
- `sudo`

같은 사용자 공간 조치만으로는 해결되기 어렵다.

## 10. 이 경우의 현재 판단

- 현재 `Jetson`에서는 `D435i` IMU가 안 되는 이유를 단순 권한 문제로 보기 어렵다.
- 특히 `노트북에서는 D435i IMU가 잘 동작`하는데 `Jetson`에서만 안 된다면, 최우선 원인은 `Jetson kernel/HID/IIO support`다.
- 이 경우 다음 선택지는 아래 둘 중 하나다.
  1. `Jetson` 커널을 `CONFIG_HID_SENSOR_HUB` 포함 상태로 다시 준비
  2. 그 전까지는 외부 `BNO08x`로 IMU 비교 실험을 먼저 진행

## 11. 현재 운영 기준으로 되돌아가기

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
