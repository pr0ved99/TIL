# 2026-04-29 Mari RTAB-Map Odom Mode Compare

## 결론

- 이 폴더는 RTAB-Map 입력 odometry를 raw Gazebo `/odom`으로 썼을 때와 local EKF `/odometry/local`로 썼을 때를 비교하는 결과를 보관한다.
- 같은 Gazebo world와 비슷한 teleop 경로에서 두 run을 따로 실행한 뒤, `Tools/check_mari_rtabmap_topics.py`의 JSON/Markdown report를 저장한다.

## 비교 대상

| run | RTAB-Map odom input | 목적 |
| --- | --- | --- |
| raw odom | `/odom` | Gazebo planar_move가 직접 publish한 odom baseline |
| local odom | `/odometry/local` | `/wheel/odometry + /imu/data`를 EKF로 묶은 odom baseline |

## 저장 파일명

| 파일 | 설명 |
| --- | --- |
| `01_raw_odom_rtabmap_check.json` | `/odom` 입력 run의 machine-readable report |
| `01_raw_odom_rtabmap_check.md` | `/odom` 입력 run의 Markdown report |
| `02_local_odom_rtabmap_check.json` | `/odometry/local` 입력 run의 machine-readable report |
| `02_local_odom_rtabmap_check.md` | `/odometry/local` 입력 run의 Markdown report |
| `04_realsense_light_matched_rtabmap_check.json` | RealSense light matched `/odom` run의 machine-readable report |
| `04_realsense_light_matched_rtabmap_check.md` | RealSense light matched `/odom` run의 Markdown report |
| `05_odom_realsense_light_smooth_driving_check.json` | smooth driving `/odom` run의 machine-readable report |
| `05_odom_realsense_light_smooth_driving_check.md` | smooth driving `/odom` run의 Markdown report |
| `06_local_odom_realsense_light_smooth_check.json` | smooth driving `/odometry/local` 후보 run의 machine-readable report |
| `06_local_odom_realsense_light_smooth_check.md` | smooth driving `/odometry/local` 후보 run의 Markdown report |

## Raw `/odom` run

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description mari_rtabmap.launch.py
```

다른 터미널:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label raw_odom \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/01_raw_odom_rtabmap_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/01_raw_odom_rtabmap_check.md
```

## Local `/odometry/local` run

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description mari_rtabmap_local_odom.launch.py
```

다른 터미널:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label local_odom \
  --odom-topic /odometry/local \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/02_local_odom_rtabmap_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/02_local_odom_rtabmap_check.md
```

## 비교 기준

- `depth image input` rate
- `rtabmap info output` rate
- `rtabmap cloud map output` rate
- `rtabmap map data output`의 `poses`, `links`
- `rtabmap info`의 loop/proximity/working memory 상태
- 터미널 graph optimization warning 수
- teleop 중 체감 끊김

## 주의

- 두 run을 동시에 켜지 않는다. 하나를 끝낸 뒤 다른 하나를 실행한다.
- RTAB-Map DB는 launch마다 `--delete_db_on_start`로 초기화된다.
- GUI 부하가 결과에 영향을 줄 수 있으므로, 비교할 때는 가능한 같은 창 구성과 비슷한 이동 경로를 유지한다.

## 2026-04-29 비교 결과

결론:

- 현재 Gazebo + RTAB-Map 매핑 기준에서는 raw Gazebo `/odom` 입력인 후보 A가 더 안정적이다.
- `/odometry/local` 입력인 후보 B도 RTAB-Map map output까지 생성했으므로 구조 smoke test는 통과했다.
- 다만 후보 B는 `Loop/MapToBase_lin_std`가 크게 증가해, 현재 설정 그대로 RTAB-Map 기본 입력으로 쓰기에는 후보 A보다 불안정하다.

| 항목 | 후보 A: `/odom` | 후보 B: `/odometry/local` | 해석 |
| --- | ---: | ---: | --- |
| odom input rate | 49.88 Hz | 9.99 Hz | A가 더 높은 주기로 들어감 |
| RGB image rate | 7.95 Hz | 8.31 Hz | 거의 동일 |
| depth image rate | 4.66 Hz | 4.46 Hz | 거의 동일 |
| RTAB-Map info rate | 2.22 Hz | 2.12 Hz | 거의 동일 |
| mapData rate | 2.22 Hz | 1.92 Hz | A가 약간 높음 |
| cloud_map rate | 0.68 Hz | 0.72 Hz | 거의 동일 |
| graph poses | 14 | 15 | 거의 동일 |
| graph links | 159 | 80 | A가 더 많은 link를 생성 |
| cloud points | 3899 | 3826 | 거의 동일 |
| occupancy map size | 132x161 | 131x176 | 거의 동일 |
| working memory | 14 | 15 | 거의 동일 |
| `Loop/MapToBase_lin_std` | 0.059 m | 1.450 m | B의 map-to-base 불확실성이 큼 |
| `Loop/MapToBase_lin_var` | 0.0035 m2 | 2.1034 m2 | B가 훨씬 불확실함 |
| highest loop hypothesis value | 0.0780 | 0.0604 | 둘 다 낮고 loop closure는 없음 |

## 현재 판정

후보 A:

- Gazebo에서 빠르게 RTAB-Map map 품질을 확인하는 기본 baseline으로 유지한다.
- `/odom`이 50 Hz로 안정적으로 들어오고, RTAB-Map이 낮은 `MapToBase` 불확실성으로 동작했다.

후보 B:

- 실제 robot encoder/IMU 구조를 미리 검증하는 구조 baseline으로 유지한다.
- `/wheel/odometry + /imu/data -> /odometry/local -> RTAB-Map` 경로는 통과했다.
- 하지만 RTAB-Map 입력으로 바로 채택하기 전에는 EKF covariance, publish rate, yaw/position trust 비율을 조정해야 한다.

## 다음 조정 후보

1. `/odometry/local` publish rate가 10 Hz로 나오는 이유를 확인한다.
2. `ekf_local.yaml`의 wheel odom/IMU covariance와 사용 축을 재검토한다.
3. RTAB-Map에 `/odometry/local`을 넣을 때 covariance가 map uncertainty에 미치는 영향을 확인한다.
4. Gazebo RTAB-Map 기본 실험은 일단 후보 A(`/odom`)로 진행하고, 실차 전환 구조 검증은 후보 B(`/odometry/local`)로 분리한다.

## 후보 B 1차 조정

확인한 원인:

- Gazebo `/clock`이 약 `10 Hz`로 publish되어, `use_sim_time=true`인 `robot_localization` EKF timer가 약 `10 Hz`로 제한됐다.
- Gazebo IMU의 `orientation_covariance`가 전부 `0.0`으로 들어와, EKF가 IMU yaw orientation을 과신할 수 있었다.
- Gazebo fake encoder odom은 Gazebo `/odom`에서 만든 값인데도 실제 encoder용 conservative covariance를 쓰고 있었다.

수정:

- `trashbot_description/config/gazebo_ros.yaml`을 추가해 Gazebo `/clock` publish rate를 `100 Hz`로 올렸다.
- `gazebo_mari.launch.py`가 위 params file을 gzserver에 전달하게 했다.
- `ekf_local.yaml`, `ekf_global.yaml`에서 IMU orientation yaw는 쓰지 않고 angular velocity z만 쓰도록 바꿨다.
- Gazebo mock encoder 전용 `encoder_odom_gazebo.yaml`을 추가하고, `mari_gazebo_encoder_odom.launch.py`의 기본 config를 이 파일로 바꿨다.

재검증 순서:

```bash
# 기존 Gazebo/RTAB-Map/local EKF 터미널을 모두 Ctrl-C로 종료한 뒤 실행한다.
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari.launch.py \
  use_mesh_visual:=true \
  world:=$(pwd)/trashbot_description/worlds/mari_camera_test.world
```

다른 터미널:

```bash
ros2 launch trashbot_description mari_rtabmap_local_odom.launch.py
```

다른 터미널:

```bash
ros2 topic hz /clock
ros2 topic hz /odometry/local
```

기대값:

- `/clock`: 기존 약 `10 Hz`보다 높아져야 한다.
- `/odometry/local`: 기존 약 `10 Hz`에서 `ekf_local.yaml`의 `frequency=30 Hz`에 가까워져야 한다.

## Smooth RealSense Light 비교

위치 기반 `/odom` smooth baseline:

```bash
ros2 launch trashbot_description gazebo_mari_realsense_light.launch.py
ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py \
  detection_rate:=3 \
  queue_size:=20 \
  approx_sync_max_interval:=0.08 \
  rtabmap_viz:=true
```

저장 명령:

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label odom_realsense_light_smooth_driving \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/05_odom_realsense_light_smooth_driving_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/05_odom_realsense_light_smooth_driving_check.md
```

Local odom 후보:

```bash
ros2 launch trashbot_description gazebo_mari_realsense_light.launch.py
ros2 launch trashbot_description mari_rtabmap_realsense_light_local_odom.launch.py
```

기본 EKF는 `ekf_local_gazebo_encoder_only.yaml`이다.
Gazebo IMU의 gyro covariance가 너무 작아 회전 보정을 과하게 만들 수 있어서,
이 후보에서는 먼저 encoder-only local odom을 기준으로 비교한다.
fake encoder tick은 `/odom.pose` delta 기반으로 생성한다.
`/odom.twist` 적분은 회전 중/정지 직후 yaw를 덜 반영할 수 있어 local odom이 덜 도는 것처럼 보일 수 있었다.

저장 명령:

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label local_odom_realsense_light_smooth \
  --odom-topic /odometry/local \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/06_local_odom_realsense_light_smooth_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/06_local_odom_realsense_light_smooth_check.md
```

판정 기준:

- `/odom` baseline은 Gazebo 위치 기반 odom이라 map 품질 기준선으로 본다.
- `/odometry/local` 후보는 실제 encoder/IMU 구조 전환 전 topic 구조 검증용으로 본다.
- 같은 camera/RTAB-Map 설정에서 `Loop/MapToBase_lin_std`, poses/links, cloud_map rate, 체감 끊김을 비교한다.
