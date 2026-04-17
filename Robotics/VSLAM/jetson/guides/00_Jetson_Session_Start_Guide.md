# Jetson 세션 시작 가이드

## 목적

- `Jetson`에서 작업을 시작할 때 매번 같은 순서로 기본 상태를 정리한다.

## 1. 현재 경로와 저장소 확인

```bash
cd /home/jetson
pwd
ls -la
cd /home/jetson/yh_ws/TIL
git status --short
```

## 2. ROS 2 환경 확인

```bash
source /opt/ros/humble/setup.bash
echo "$ROS_DISTRO"
which ros2
```

## 3. 기존 충돌 가능 프로세스 정리

```bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view' || true
```

## 4. 현재 관련 프로세스가 없는지 확인

```bash
pgrep -af 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view' || true
```

## 5. 오늘 기록할 파일 열기

```bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/daily/2026-04-17
pwd
```
