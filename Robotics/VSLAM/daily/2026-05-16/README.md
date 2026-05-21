# 2026-05-16 Duri Real RTAB-Map Mapping and Drive Check

## 결론

- Duri의 실제 모터 드라이버 문제를 하드웨어 교체로 분리했고, 웹 조종과 `/cmd_vel` 기반 직진/회전 동작을 확인했다.
- Jetson `~/.bashrc`에는 Duri ROS 2 환경을 자동으로 source하도록 정리했고, 새 터미널에서 `ROS_DOMAIN_ID=14`, `ROS_LOCALHOST_ONLY=0`, `trashbot_*` 패키지 인식까지 확인했다.
- RTAB-Map 실시간 맵을 Jetson에서 만들고, 노트북 RViz에서 `/rtabmap/map`, `/rtabmap/odom`, `/rtabmap/mapPath`, RGB image를 같이 보는 흐름을 확인했다.
- 새로 딴 RTAB-Map 2D occupancy map을 Nav2용 `yaml/pgm`으로 저장했다.
- RTAB-Map DB도 backup service로 백업했다.
- 아직 남은 핵심 검증은 저장한 map으로 Nav2 localization과 goal 주행을 안정화하는 것이다.

## 오늘 확인한 사실

### 1. 모터/수동 주행

기존 주행 불능의 주원인은 소프트웨어보다 모터 드라이버 쪽 하드웨어 문제였다.
정상 동작하는 드라이버로 교체한 뒤 웹 조종기로 움직임을 확인했고, ROS 2 `/cmd_vel` 명령도 모터 브릿지를 통해 직진/회전으로 이어지는 것을 확인했다.

맵핑 중에는 회전 속도를 낮추는 쪽이 안정적이었다.
RTAB-Map은 연속 카메라 프레임 사이에서 특징점을 맞춰 위치를 추정하므로, 제자리 회전이 너무 빠르면 매칭이 깨지기 쉽다.

추천 teleop 시작값:

```bash
python3 src/trashbot_description/scripts/teleop_duri_keyboard.py \
  --cmd-vel-topic /cmd_vel \
  --linear-speed 0.06 \
  --angular-speed 0.08 \
  --max-linear-speed 0.12 \
  --max-angular-speed 0.20 \
  --linear-accel 0.15 \
  --angular-accel 0.20
```

### 2. Jetson ROS 2 환경 자동화

Jetson의 `~/.bashrc`에는 `cd` 없이 ROS 2 환경만 자동 source하도록 정리했다.

현재 적용된 방향:

```bash
source /opt/ros/humble/setup.bash
source /home/jetson/S14P31C205/edge/jetson/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
```

확인 결과:

```text
ROS_DOMAIN_ID=14
ROS_LOCALHOST_ONLY=0
trashbot_description
trashbot_localization
trashbot_navigation
trashbot_perception
```

주의할 점은 `sudo -E bash -lc '...'` 안에서 실행하는 모터 브릿지는 별도 shell이므로 내부에서 다시 `source`하는 편이 안전하다는 것이다.

### 3. RTAB-Map 실시간 맵 확인

Jetson에서 Duri real mapping stack을 실행하고, 노트북에서는 RViz monitor를 실행했다.

Jetson mapping stack:

```bash
cd /home/jetson/S14P31C205/edge/jetson/ros2_ws
./src/trashbot_navigation/scripts/start_duri_real_mapping_stack.sh
```

노트북 RViz:

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
./src/trashbot_navigation/scripts/run_laptop_rviz_monitor.sh --restart
```

RViz에서 확인한 주요 display:

- `RTAB Live Map`: `/rtabmap/map`
- `RTAB Odom`: `/rtabmap/odom`
- `RTAB Map Path`: `/rtabmap/mapPath`
- `RGB Image`: RealSense RGB image

### 4. 새 map 저장

처음에는 아래 오류로 저장이 실패했다.

```text
Failed to spin map subscription
```

원인은 `/rtabmap/map` publisher의 QoS가 `TRANSIENT_LOCAL`인데, 저장 명령에서 `map_subscribe_transient_local:=false`를 줘서 `map_saver`가 기존 map 메시지를 받지 못한 것이었다.

성공한 저장 방식은 transient local 구독을 기본값으로 두는 것이다.

저장 결과:

```text
/home/jetson/S14P31C205/edge/jetson/maps/duri_rtabmap_20260516_222106.yaml
/home/jetson/S14P31C205/edge/jetson/maps/duri_rtabmap_20260516_222106.pgm
```

노트북 GitLab 작업 경로에도 복사했다.

```text
/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/maps/duri_rtabmap_20260516_222106.yaml
/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/maps/duri_rtabmap_20260516_222106.pgm
```

YAML 핵심값:

```yaml
image: duri_rtabmap_20260516_222106.pgm
mode: trinary
resolution: 0.05
origin: [-7.28, -9.19, 0]
occupied_thresh: 0.65
free_thresh: 0.25
```

### 5. RTAB-Map DB 백업

RTAB-Map DB는 아래 service로 백업했다.

```bash
ros2 service call /rtabmap/rtabmap/backup std_srvs/srv/Empty "{}"
```

결과:

```text
/home/jetson/.ros/rtabmap/duri_mapping_20260516_220443.db
/home/jetson/.ros/rtabmap/duri_mapping_20260516_220443.db.back
```

## 현재 남은 문제

### Nav2 goal 주행 안정화

Nav2 goal 주행은 아직 완료로 보지 않는다.

확인된 흐름:

- planner는 path를 만들 수 있다.
- controller와 velocity smoother는 active 상태까지 올라갈 수 있다.
- `/cmd_vel`이 실제 모터 브릿지로 갈 수 있다.
- 수동 teleop과 웹 조종은 실제 주행된다.

아직 닫히지 않은 부분:

- 저장한 최신 map으로 localization을 재시작했을 때 초기 위치 추정이 안정적인지 확인해야 한다.
- local/global costmap에서 로봇 위치 주변이 막혀 있지 않은지 확인해야 한다.
- goal 클릭 후 `/plan -> /local_plan -> /cmd_vel_nav -> /cmd_vel` 흐름이 끊기지 않는지 봐야 한다.
- RTAB-Map visual odometry만으로 `odom -> base_footprint`가 실제 이동을 충분히 따라가는지 확인해야 한다.

## 다음 액션

1. 저장한 map으로 map_server/Nav2를 재시작한다.
2. RViz에서 `2D Pose Estimate`로 Duri 초기 위치를 맞춘다.
3. `/rtabmap/odom_info`가 `lost: false`이고 inliers가 충분한지 확인한다.
4. 빈 직선 구간에 짧은 goal을 찍는다.
5. goal 중 `/plan`, `/local_plan`, `/cmd_vel_nav`, `/cmd_vel`, `map -> base_footprint` 변화를 동시에 모니터링한다.
6. 실패하면 planner 문제인지, controller 문제인지, localization 문제인지, motor bridge 문제인지 분리한다.

## 한 줄 요약

Duri는 이제 실물 모터와 RTAB-Map mapping이 되는 상태까지 왔고, `duri_rtabmap_20260516_222106` map을 기준으로 Nav2 goal 주행 안정화만 다음 핵심 과제로 남았다.
