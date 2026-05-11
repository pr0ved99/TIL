# BNO08x RTAB-Map IMU Comparison Learning Guide

## 결론

BNO08x IMU 비교는 "IMU를 붙이면 무조건 좋아진다"를 증명하는 실험이 아니라, `D435i RGB-D only` baseline에 외부 IMU를 추가했을 때 맵 기울기와 자세 안정성이 눈에 띄게 좋아지는지 확인하는 1차 실험이다.

핵심 원칙은 preset, 해상도, DetectionRate, queue, 이동 경로를 최대한 고정하고 `IMU OFF`와 `IMU ON`만 바꿔 비교하는 것이다.

## 먼저 읽을 문서

1. [Jetson_RTABMap_Multi_Session_Workflow_Guide.md](./Jetson_RTABMap_Multi_Session_Workflow_Guide.md)
2. [BNO08x_IMU_Placement_Guide.md](./BNO08x_IMU_Placement_Guide.md)
3. [D435i_IMU_Axis_Interpretation.md](./D435i_IMU_Axis_Interpretation.md)

실제 실행 절차 원문은 아래 문서에 있다.

- [16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md](../../jetson/guides/16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md)
- [17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md](../../jetson/guides/17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md)
- [18_Jetson_BNO08x_RTABMap_Comparison_Guide.md](../../jetson/guides/18_Jetson_BNO08x_RTABMap_Comparison_Guide.md)
- [20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md](../../jetson/guides/20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md)
- [23_Jetson_Docker_Preset_and_Benchmark_Guide.md](../../jetson/guides/23_Jetson_Docker_Preset_and_Benchmark_Guide.md)

## 1. 왜 D435i 내장 IMU가 아니라 BNO08x인가

`IMU`는 가속도와 회전 속도, 또는 자세를 알려주는 센서다.
VSLAM에서는 카메라가 흔들리거나 회전할 때 자세 안정화 힌트로 쓸 수 있다.

현재 Jetson 기준에서는 D435i 내장 IMU가 HID/IIO 제약 때문에 안정적인 기준으로 쓰기 어렵다.
그래서 비교 실험은 외부 BNO08x를 `/imu/data`로 publish하는 방식으로 진행한다.

중요한 전제:

- 첫 baseline은 무조건 `IMU OFF`다.
- BNO08x는 카메라에 단단히 고정되어 있어야 한다.
- `camera_link -> imu_link` 관계가 있어야 RTAB-Map이 IMU 방향을 해석할 수 있다.

## 2. 비교에서 바꾸면 안 되는 것

IMU 효과를 보려면 다른 조건이 바뀌면 안 된다.

| 항목 | 고정 기준 |
| --- | --- |
| preset | `light` |
| color/depth | `424x240x15` |
| DetectionRate | `2` |
| odom profile | `relaxed` |
| queue | `15` |
| 이동 경로 | 가능한 같은 짧은 경로 |
| 이동 속도 | 천천히, 비슷하게 |

`DetectionRate`는 RTAB-Map이 초당 몇 번 새 위치/맵 계산을 시도할지에 가까운 설정이다.
비교 중 이 값이 바뀌면 IMU 효과인지 계산 주기 효과인지 헷갈린다.

## 3. IMU OFF run

이 단계는 D435i color/depth만으로 RTAB-Map이 어느 정도 안정적인지 확인하는 기준선이다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
pkill -f '[r]tabmap_viz' || true
pkill -f '[b]no08x_ros2_imu_publisher.py' || true
pkill -f '[s]tatic_transform_publisher.*imu_link' || true

./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

관찰할 것:

- 맵이 기울어지는지
- 제자리 회전 때 trajectory가 과하게 흔들리는지
- `/rtabmap/odom_info` quality가 계속 0인지
- `/rtabmap/mapData`가 계속 나오는지

## 4. IMU ON run

IMU ON은 최소 3개 실행이 필요하다.
`BNO08x publisher`, `static TF`, `RTAB-Map backend with IMU`가 서로 다른 역할을 하기 때문이다.

세션 1:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_bno08x_ros2_imu_publisher.sh
```

세션 2:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_camera_to_imu_static_tf.sh
```

세션 3:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack_with_external_imu.sh light 2 relaxed /imu/data 15
```

세션 4:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

## 5. 자동 benchmark 비교

눈으로 보는 비교와 별개로 숫자 로그를 남긴다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_imu_comparison.sh both light 20
```

이 명령이 남기는 것:

- `IMU OFF` benchmark 폴더
- `IMU ON` benchmark 폴더
- `*_imu_on_off_comparison.md` 비교 문서
- `/rtabmap/odom`, `/rtabmap/mapData`, `/imu/data` hz
- odometry quality와 delay 요약
- `tegrastats` 로그

대표 결과:

- [2026-04-21_12-00-54_docker_light_imu_on_off_comparison.md](../../jetson/assets/benchmarks/2026-04-21_12-00-54_docker_light_imu_on_off_comparison.md)

## 6. 현재 결과를 어떻게 해석할까

2026-04-21 benchmark 기준으로는 숫자상 차이가 크지 않았다.

```text
IMU OFF quality avg: 56.4
IMU ON  quality avg: 57.1
```

이 결과만 보면 BNO08x가 odometry quality를 크게 끌어올렸다고 말하기는 어렵다.
하지만 사용자가 직접 본 RTAB-Map 화면에서는 IMU ON에서 맵 자세가 더 안정적으로 느껴졌다.

따라서 현재 결론은 아래처럼 잡는다.

- 숫자 성능 개선은 아직 작다.
- 회전/기울기 상황에서 자세 안정성 보조 효과 후보는 있다.
- 정식 센서 융합이라고 단정하면 안 된다.
- 임시 장착, 축 정렬, `camera_link -> imu_link` 오차를 더 줄인 뒤 다시 봐야 한다.

## 7. 흔한 실수

### BNO08x publisher를 두 개 띄움

BNO08x는 I2C 장치다.
여러 프로세스가 동시에 읽으면 오류가 나거나 값이 불안정할 수 있다.

정리:

```bash
pkill -f '[b]no08x_ros2_imu_publisher.py' || true
```

### static TF를 빼먹음

`TF`는 좌표계 사이의 위치와 회전 관계다.
RTAB-Map이 `/imu/data`를 받아도, 그 IMU가 카메라 기준으로 어디에 붙었는지 모르면 해석이 흔들릴 수 있다.

확인:

```bash
ros2 run tf2_ros tf2_echo camera_link imu_link
```

### IMU만 켰는데 경로도 달라짐

IMU ON/OFF를 비교할 때 이동 경로와 회전량이 달라지면 결과를 해석하기 어렵다.
가능하면 같은 짧은 경로를 천천히 반복한다.

### RTAB-Map quality 숫자만 봄

quality가 비슷해도 회전 구간의 체감 안정성이 다를 수 있다.
숫자 benchmark와 화면 관찰을 같이 본다.

## 8. 다음에 할 학습

BNO08x 비교를 이해했다면 다음은 야외 자율주행을 위해 GPS를 연결하는 흐름이다.

- [Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md](./Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md)
