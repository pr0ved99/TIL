# Jetson Baseline Benchmark 가이드

## 목적

- 현재 성공한 `Jetson` baseline을 다시 실행하면서 `quality`, `delay`, `topic hz`, `tegrastats`, `GUI screenshot`을 한 번에 남긴다.

## 시작 전

- 이 가이드는 `Jetson` 바탕화면에서 직접 연 터미널 기준이다.
- 현재 기준 baseline은 `424x240x15 + DetectionRate 2 + IMU OFF`다.
- 로그와 캡처는 오늘 실험 폴더 아래에 한 번에 모은다.
- 날짜가 다르면 아래 `BENCH_DIR`의 날짜 부분만 바꿔서 쓰면 된다.

## 1. 실험 폴더 만들기

```bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline
mkdir -p "$BENCH_DIR"
echo "$BENCH_DIR"
```

## 2. 기록 템플릿 복사

```bash
if [ ! -f "$BENCH_DIR/README.md" ]; then
  cp /home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/RTABMap_Baseline_Benchmark_Template.md "$BENCH_DIR/README.md"
fi
ls -l "$BENCH_DIR"
```

이미 `README.md`에 결과를 적은 뒤라면 덮어쓰지 않는 편이 맞다.

## 3. 세션 정리

```bash
source /opt/ros/humble/setup.bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view|tegrastats' || true
pgrep -af 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|tegrastats' || true
```

## 4. 터미널 1: D435i 카메라 노드와 로그 저장

```bash
source /opt/ros/humble/setup.bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 false 2>&1 | tee "$BENCH_DIR/01_camera_launch.log"
```

## 5. 터미널 2: RTAB-Map GUI와 로그 저장

```bash
source /opt/ros/humble/setup.bash
export DISPLAY="${DISPLAY:-:0}"
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed false 2>&1 | tee "$BENCH_DIR/02_rtabmap_launch.log"
```

## 6. 터미널 3: ROS 노드와 토픽 목록 저장

```bash
source /opt/ros/humble/setup.bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline
ros2 node list | tee "$BENCH_DIR/03_nodes.txt"
ros2 topic list | tee "$BENCH_DIR/04_topics.txt"
```

## 7. 터미널 3: quality / delay 기록

```bash
source /opt/ros/humble/setup.bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline
timeout 20 ros2 topic echo /rtabmap/odom_info > "$BENCH_DIR/05_odom_info.txt"
```

기대하는 흐름:

- 시작 직후 `quality=0`이 한 번 보일 수 있다.
- 이후 `quality`가 `60~160` 정도로 올라오면 baseline은 살아 있는 편이다.
- 안정 구간에서 `120~150` 정도가 반복되면 현재 `Jetson` 기준으로 양호한 편이다.

## 8. 터미널 3: topic hz 기록

```bash
source /opt/ros/humble/setup.bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline
timeout 15 ros2 topic hz /camera/camera/color/image_raw > "$BENCH_DIR/06_color_hz.txt"
timeout 15 ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw > "$BENCH_DIR/07_aligned_depth_hz.txt"
timeout 15 ros2 topic hz /rtabmap/odom > "$BENCH_DIR/08_odom_hz.txt"
```

`/rtabmap/odom`이나 `/rtabmap/odom_info`가 없으면 먼저 아래로 실제 topic 이름을 확인한다.

```bash
grep odom "$BENCH_DIR/04_topics.txt"
```

## 9. 터미널 4: Jetson 자원 사용량 기록

```bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline
free -h > "$BENCH_DIR/09_memory.txt"
df -h > "$BENCH_DIR/10_disk.txt"
top -b -n 1 | head -n 40 > "$BENCH_DIR/11_top.txt"
timeout 30 tegrastats --interval 1000 > "$BENCH_DIR/12_tegrastats.txt"
```

## 10. GUI 상태에서 짧은 실내 경로 확인

- `rtabmap_viz`가 열린 상태에서 책상 주변이나 방 안에서 짧게 움직인다.
- 너무 빠르게 움직이지 말고, `trajectory`와 `3D Map`이 따라오는지 본다.
- 이때 체감한 끊김이나 부드러움을 `README.md`에 같이 적는다.

## 11. GUI 스크린샷 저장

```bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline
gnome-screenshot -f "$BENCH_DIR/13_rtabmap_viz.png"
ls -l "$BENCH_DIR"
```

## 12. 종료 전 정리

```bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|rqt_image_view|tegrastats' || true
```

## 13. 결과 반영

- `$BENCH_DIR/README.md`에 아래를 꼭 적는다.
  - `quality` 대략 범위
  - `delay` 체감
  - GUI가 부드러웠는지
  - 짧은 경로에서 trajectory가 어땠는지
  - 오늘 기준 계속 쓸 기본 세팅인지
