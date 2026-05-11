# Jetson RTAB-Map Multi-Session Workflow Guide

## 결론

Jetson에서 RTAB-Map을 안정적으로 볼 때는 한 터미널에서 전부 실행하려고 하지 말고, `camera`, `RTAB-Map backend`, `상태 확인`, `host GUI`를 세션별로 나누는 편이 가장 이해하기 쉽다.

이 문서의 목표는 명령어를 외우는 것이 아니라, "왜 여러 터미널을 열어야 하는지", "각 세션이 어떤 역할인지", "어디가 고장났는지 어떻게 분리하는지"를 이해하는 것이다.

## 먼저 읽을 문서

1. [D435i_RTABMap_VSLAM_Manual.md](./D435i_RTABMap_VSLAM_Manual.md)
2. [D435i_Jetson_Docker_Prerequisites.md](./D435i_Jetson_Docker_Prerequisites.md)
3. [Jetson_Docker_Host_Checklist.md](./Jetson_Docker_Host_Checklist.md)
4. [Jetson_Orin_Nano_Power_Mode_Guide.md](./Jetson_Orin_Nano_Power_Mode_Guide.md)

실제 실행 절차 원문은 아래 문서에 있다.

- [00_Jetson_Session_Start_Guide.md](../../jetson/guides/00_Jetson_Session_Start_Guide.md)
- [21_Jetson_Docker_RTABMap_Baseline_Guide.md](../../jetson/guides/21_Jetson_Docker_RTABMap_Baseline_Guide.md)
- [22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md](../../jetson/guides/22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md)
- [23_Jetson_Docker_Preset_and_Benchmark_Guide.md](../../jetson/guides/23_Jetson_Docker_Preset_and_Benchmark_Guide.md)
- [GitLab edge 36_Jetson_RTABMap_MultiSession_DB_Reuse_Guide.md](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/docs/guides/36_Jetson_RTABMap_MultiSession_DB_Reuse_Guide.md)

## 1. 멀티세션이란 무엇인가

`세션`은 여기서는 터미널 하나에서 계속 살아 있는 실행 단위를 뜻한다.

RTAB-Map 작업에서는 한 프로세스가 계속 카메라를 읽고, 다른 프로세스가 map을 계산하고, 또 다른 프로세스가 화면을 보여준다.
그래서 모두 한 터미널에 몰아넣으면 로그가 섞이고, 어떤 단계가 죽었는지 파악하기 어렵다.

멀티세션은 아래처럼 역할을 나누는 방식이다.

```text
세션 0: 시작 전 정리
세션 1: D435i camera backend
세션 2: RTAB-Map backend
세션 3: ROS topic 상태 확인
세션 4: host rtabmap_viz GUI
```

## 2. backend와 frontend를 나눠서 생각한다

`backend`는 화면을 보여주는 쪽이 아니라 실제 계산을 하는 쪽이다.
여기서는 `D435i image`, `rgbd_odometry`, `rtabmap`이 backend다.

`frontend`는 사람이 보는 화면이다.
여기서는 `rtabmap_viz`가 frontend다.

현재 프로젝트의 실용적인 기준은 아래 구조다.

```text
Docker backend
  realsense2_camera
  rgbd_odometry
  rtabmap
        |
        | ROS 2 topic, network_mode=host
        v
Jetson host frontend
  rtabmap_viz
```

이 구조를 쓰는 이유는 Docker 안에서 센서와 RTAB-Map 계산은 재현하기 쉽고, GUI는 Jetson host에서 직접 띄우는 편이 OpenGL 문제를 피하기 쉽기 때문이다.

## 3. 가장 먼저 하는 세션 정리

이 단계는 이전 실행이 남아 새 실험과 섞이는 것을 막는다.

```bash
cd ~/yh_ws/TIL
source /opt/ros/humble/setup.bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view' || true
pgrep -af 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view' || true
```

이 명령이 중요한 이유:

- 예전 `rtabmap`이 살아 있으면 새 map인지 예전 map인지 헷갈린다.
- 예전 `camera node`가 USB 장치를 잡고 있으면 새 camera 실행이 실패할 수 있다.
- 예전 GUI가 같은 namespace를 보고 있으면 service 연결 오류가 날 수 있다.

## 4. 추천 멀티세션 구조

### 방법 A. detached stack 기준

처음에는 이 방법이 가장 단순하다.
`detached`는 터미널을 붙잡지 않고 Docker service를 뒤에서 계속 실행한다는 뜻이다.

세션 1:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
```

세션 2:

```bash
source /opt/ros/humble/setup.bash
ros2 node list | grep -E 'camera|rtabmap'
ros2 topic list | grep -E '/camera/camera/color/image_raw|/camera/camera/aligned_depth_to_color/image_raw|/rtabmap/odom|/rtabmap/odom_info|/rtabmap/mapData'
```

세션 3:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

끝낼 때:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
pkill -f rtabmap_viz || true
```

### 방법 B. camera와 RTAB-Map을 분리

어느 단계가 문제인지 더 자세히 보려면 camera와 RTAB-Map을 나눈다.

세션 1:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh light
```

세션 2:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh light
```

세션 3:

```bash
source /opt/ros/humble/setup.bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
ros2 topic hz /rtabmap/odom
```

세션 4:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

## 5. 각 세션에서 보는 신호

| 세션 | 핵심 질문 | 정상 신호 |
| --- | --- | --- |
| camera | D435i image가 들어오는가 | `/camera/camera/color/image_raw`, aligned depth |
| RTAB-Map backend | odom과 map이 계산되는가 | `/rtabmap/odom`, `/rtabmap/odom_info`, `/rtabmap/mapData` |
| topic 확인 | ROS graph가 살아 있는가 | `ros2 node list`, `ros2 topic hz` |
| host GUI | 사람이 map을 볼 수 있는가 | `3D Map`, trajectory, feature 표시 |

여기서 중요한 순서는 `GUI보다 topic 먼저`다.
화면이 안 보일 때 바로 GUI를 의심하지 말고, backend topic이 살아 있는지 먼저 본다.

## 6. rtabmap_viz 화면을 어떻게 해석할까

`rtabmap_viz`는 카메라 이미지 자체를 긴 벽지처럼 이어 붙이는 프로그램이 아니다.
VSLAM은 카메라가 움직이며 본 장면을 `keyframe`, `feature`, `point cloud`, `trajectory`로 누적한다.

그래서 화면에서 봐야 할 것은 아래다.

- 왼쪽에 현재 frame과 feature가 보이는가
- `/rtabmap/odom_info`의 quality가 계속 0인지 아닌지
- 오른쪽 `3D Map`에 점군과 trajectory가 쌓이는가
- 카메라를 천천히 움직였을 때 trajectory가 따라오는가
- 같은 장소를 다시 봤을 때 loop closure 후보가 생기는가

## 7. 자주 헷갈리는 문제

### GUI 창은 뜨는데 검은 화면

Docker 안 GUI 문제일 수 있다.
현재 운영 기준에서는 Docker 안 `rtabmap_viz`보다 host `rtabmap_viz`를 우선한다.

확인할 것:

```bash
echo "$DISPLAY"
groups
docker compose --env-file Robotics/VSLAM/jetson/docker/.env ps
```

### map이 안 쌓임

GUI보다 topic을 먼저 본다.

```bash
ros2 topic list | grep -E 'rtabmap|odom|mapData'
ros2 topic echo /rtabmap/odom_info --once
```

`/rtabmap/mapData`가 없으면 viewer 문제가 아니라 backend 계산 문제일 가능성이 높다.

### 이전 실행 결과와 섞임

세션 시작 전 정리를 다시 한다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
pkill -f 'rtabmap|rtabmap_viz|realsense2_camera' || true
```

## 8. benchmark 세션으로 넘어가는 기준

화면으로 "된다"를 확인한 뒤에는 숫자로 비교해야 한다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_benchmark.sh light 20
```

이 명령은 아래를 남긴다.

- `tegrastats`: Jetson 전력, 온도, CPU/GPU 상태
- `/camera/...` topic hz
- `/rtabmap/odom`, `/rtabmap/mapData` topic hz
- `camera`, `rtabmap` Docker log
- `90_summary.env`
- `91_summary.md`

결과 위치:

- [jetson/assets/benchmarks/README.md](../../jetson/assets/benchmarks/README.md)

## 9. 다음에 연결되는 학습

멀티세션 구조가 이해되면 다음 순서로 보면 된다.

1. [RTABMap_MultiSession_DB_Reuse_Learning_Guide.md](./RTABMap_MultiSession_DB_Reuse_Learning_Guide.md)
2. [BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md](./BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md)
3. [Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md](./Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md)

## 10. RTAB-Map DB 세션 재사용 검증

위의 `멀티세션`은 여러 터미널 실행 단위를 나누는 운영 방식이다.
여기서 말하는 RTAB-Map DB 세션 재사용은 `~/.ros/rtabmap/*.db` 파일에 저장된 이전 mapping 결과를 다음 실행에서 다시 여는 절차를 뜻한다.

2026-05-06에는 Mari Gazebo simulation에서 같은 DB를 새로 생성한 뒤 다시 재사용하는 흐름을 확인했다.

검증 기준:

- 첫 번째 실행은 `delete_db_on_start:=true`로 기존 DB를 지우고 새 DB를 생성한다.
- 두 번째 실행은 `delete_db_on_start:=false`로 같은 DB를 유지한 상태에서 다시 연다.
- `rtabmap-databaseViewer`에서 이전 run의 node와 RGB-D frame이 보이면 DB 재사용이 된 것으로 본다.
- `/rtabmap/info`, `/rtabmap/mapData`, `/rtabmap/mapGraph`, `/odometry/local` 계열 topic이 살아 있으면 backend도 동작 중인 것으로 본다.

검증 결과:

- DB 경로: `~/.ros/rtabmap/mari_multisession.db`
- 첫 실행 백업: `~/.ros/rtabmap/mari_multisession_first_20260506_220704.db`
- 최종 DB 크기: 약 `119M`
- 결과: 같은 DB 재사용 확인

증빙:

- [2026-05-06 RTAB-Map Multi-Session DB Reuse](../../assets/2026-05-06_rtabmap_multisession_db_reuse/README.md)

주의할 점:

- 이 결과는 같은 DB 파일을 다시 여는 재사용 검증이다.
- 서로 다른 로봇 또는 서로 다른 독립 DB를 합치는 map merge 검증은 별도 단계로 남긴다.
- YOLO로 검출한 쓰레기 위치는 RTAB-Map DB 안에 직접 넣기보다, `map` frame 좌표를 가진 별도 trash registry/API 데이터로 관리하는 편이 명확하다.

자세한 학습 정리는 [RTABMap_MultiSession_DB_Reuse_Learning_Guide.md](./RTABMap_MultiSession_DB_Reuse_Learning_Guide.md)에 따로 분리했다.
