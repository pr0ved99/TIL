# Jetson 로컬 RTAB-Map GUI 확인 가이드

## 목적

- `Jetson` 화면에 직접 연결한 상태에서 `D435i` 카메라 노드를 켜고 `rtabmap_viz` GUI가 실제로 뜨는지 확인한다.

## 시작 전

- 이 가이드는 `SSH` 터미널이 아니라 `Jetson` 로컬 그래픽 세션에서 직접 연 터미널을 기준으로 한다.
- `VS Code Remote` 터미널이나 비GUI shell에서는 `rtabmap_viz`가 `xcb` 오류로 실패할 수 있다.
- 현재 기준선은 `424x240x15 + DetectionRate 2 + IMU OFF`다.

## 1. Jetson 로컬 GUI 세션 확인

```bash
echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-empty}"
echo "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-empty}"
echo "DISPLAY=${DISPLAY:-empty}"
export DISPLAY="${DISPLAY:-:0}"
echo "DISPLAY=$DISPLAY"
```

## 2. 세션 정리

```bash
source /opt/ros/humble/setup.bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view' || true
pgrep -af 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz' || true
```

## 3. 작업 경로로 이동

```bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
pwd
```

## 4. 터미널 1: D435i 카메라 노드 실행

```bash
source /opt/ros/humble/setup.bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 false
```

## 5. 터미널 2: RTAB-Map GUI 실행

```bash
source /opt/ros/humble/setup.bash
export DISPLAY="${DISPLAY:-:0}"
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed false
```

이 스크립트는 현재 설정상 `rtabmap_viz:=true`, `rviz:=false`로 실행된다.

## 6. 터미널 3: 노드와 토픽 확인

```bash
source /opt/ros/humble/setup.bash
ros2 node list
ros2 topic list | grep -E 'odom|rtabmap|camera'
ros2 topic echo /odom_info --once
```

## 7. GUI에서 확인할 것

- `rtabmap_viz` 창이 실제로 떠야 한다.
- color/depth 입력이 들어오면 화면이 멈추지 않고 갱신돼야 한다.
- 시작 직후 `quality=0`이 한 번 보일 수 있지만, 이후 `60~160` 정도로 올라오면 baseline은 살아 있는 편이다.
- 안정 구간에서 `120~150` 정도가 반복되면 현재 `Jetson` 기준으로는 양호한 편이다.

## 8. GUI가 안 뜨면 바로 확인

### 터미널 3

```bash
echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-empty}"
echo "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-empty}"
echo "DISPLAY=${DISPLAY:-empty}"
env | grep -E 'DISPLAY|WAYLAND|QT'
pgrep -af 'rtabmap|rtabmap_viz'
```

### 터미널 2에서 다시 실행

```bash
source /opt/ros/humble/setup.bash
export DISPLAY="${DISPLAY:-:0}"
export QT_QPA_PLATFORM=xcb
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed false
```

## 9. 그래도 `xcb` 오류가 나면

- `Jetson` 바탕화면에서 직접 연 기본 터미널인지 다시 확인한다.
- `SSH` 세션, `tmux`, 원격 IDE 터미널이 아닌지 확인한다.
- 이미 떠 있는 `rtabmap_viz` 프로세스를 정리하고 다시 시작한다.

정리 명령:

```bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|rqt_image_view' || true
```

## 10. 종료 전 정리

```bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|rqt_image_view' || true
```
