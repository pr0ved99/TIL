# 하드웨어 도착 전 센서 융합 구조 설계

## 결론

- `IMU`, `wheel encoder`, `GPS`가 아직 없어도 **연동 구조는 지금 미리 고정해두는 것이 맞다**.
- 가장 실용적인 구조는 `wheel encoder + 외부 IMU -> local EKF`, `GPS + local odom -> global EKF`, `D435i는 보조 시각 정보`로 두는 것이다.
- 즉, 최종 구조는 아래처럼 생각하면 된다.

```text
wheel encoder + external IMU -> ekf_local -> odom -> base_link
GPS + ekf_local              -> ekf_global -> map -> odom
D435i                        -> visual odom / perception / local map assist
```

- 지금 해야 할 일은 하드웨어를 기다리면서
  1. 토픽 이름
  2. TF 구조
  3. `robot_localization` 입력 구조
  4. ROS2 패키지 분리 기준
  를 먼저 고정하는 것이다.

## 1. 먼저 알아둘 것

- `TF`: 좌표계 사이 변환 관계다.
- `EKF`: 여러 센서를 합쳐 더 안정적인 상태 추정을 만드는 필터다.
- `local odom`: 짧은 구간에서 부드럽게 이어지는 위치 추정이다.
- `global odom`: `map` 기준으로 전역 위치까지 반영한 추정이다.
- `robot_localization`: ROS2에서 `IMU`, `odom`, `GPS`를 융합할 때 자주 쓰는 패키지다.

핵심은 이렇다.

- `wheel encoder`는 짧은 구간 이동량에 강하다.
- `IMU`는 회전과 기울기 변화에 강하다.
- `GPS`는 전역 위치 기준에 강하다.
- `D435i`는 근거리 시각 정보와 보조 odom에 유리하다.

즉, **각 센서가 잘하는 역할을 분리해서 설계해야 한다.**

## 2. 최종 추천 구조

추천 구조는 아래다.

```text
wheel encoder ----------> /wheel/odometry
external IMU -----------> /imu/data
GPS --------------------> /gps/fix
D435i ------------------> /camera/camera/...

/wheel/odometry + /imu/data ----------> ekf_local ----------> /odometry/local
/gps/fix + /odometry/local + /imu/data -> navsat_transform -> /odometry/gps
/odometry/local + /odometry/gps -------> ekf_global --------> /odometry/global

TF:
map -> odom -> base_link -> camera_link
                         -> imu_link
                         -> gps_link
```

역할 분리는 이렇게 보면 된다.

- `ekf_local`: 로봇이 부드럽게 움직이도록 `odom -> base_link`를 안정화
- `navsat_transform`: GPS를 로봇 기준 좌표계와 연결
- `ekf_global`: GPS를 포함해 `map -> odom`을 보정
- `D435i`: 최종 메인 위치추정이 아니라, 근거리 perception과 보조 시각 odom에 사용

## 3. 토픽 구조를 먼저 고정

하드웨어가 오기 전에도 토픽 이름은 먼저 고정해두는 것이 좋다.

추천 토픽은 아래와 같다.

| 센서/노드 | 토픽 | 메시지 타입 | 역할 |
| --- | --- | --- | --- |
| wheel encoder driver | `/wheel/odometry` | `nav_msgs/Odometry` | 바퀴 기반 로컬 odom 원본 |
| external IMU driver | `/imu/data_raw` | `sensor_msgs/Imu` | IMU raw 값 |
| IMU filter | `/imu/data` | `sensor_msgs/Imu` | 필터링된 IMU |
| GPS driver | `/gps/fix` | `sensor_msgs/NavSatFix` | GPS 위치 |
| D435i color | `/camera/camera/color/image_raw` | `sensor_msgs/Image` | RGB 영상 |
| D435i depth | `/camera/camera/aligned_depth_to_color/image_raw` | `sensor_msgs/Image` | 정렬된 depth |
| local EKF | `/odometry/local` | `nav_msgs/Odometry` | 로컬 융합 odom |
| navsat_transform | `/odometry/gps` | `nav_msgs/Odometry` | GPS를 odom 형태로 변환한 결과 |
| global EKF | `/odometry/global` | `nav_msgs/Odometry` | 전역 융합 결과 |

지금 단계에서 중요한 것은 **토픽 이름을 나중에 바꾸지 않도록 미리 고정하는 것**이다.

## 4. TF 구조를 먼저 고정

센서 융합에서 가장 흔한 실패 원인 중 하나가 TF다.

지금부터 아래 구조를 최종 구조로 생각하는 것이 좋다.

```text
map
└── odom
    └── base_link
        ├── camera_link
        ├── camera_color_optical_frame
        ├── camera_depth_optical_frame
        ├── imu_link
        └── gps_link
```

규칙:

- `map -> odom`: global EKF 또는 SLAM 쪽
- `odom -> base_link`: local EKF 쪽
- `base_link -> sensor_link`: 고정 transform

중요:

- `camera_gyro_optical_frame`를 바로 `base_link` 기준 IMU처럼 쓰면 안 된다.
- D435i 내장 IMU와 나중에 도착할 외부 IMU는 **다른 frame**으로 다뤄야 한다.
- 추천은 외부 IMU 기준 frame을 따로 두는 것이다.

예:

```text
base_link -> d435i_link
base_link -> imu_link
base_link -> gps_link
```

즉, 나중에 `robot_localization`에 메인으로 넣을 IMU는 `imu_link` 기준 외부 IMU가 되도록 설계하는 것이 맞다.

## 5. ROS2 패키지 구조 추천

하드웨어 도착 전에도 패키지 역할을 미리 분리해두는 것이 좋다.

추천 패키지 구조:

```text
trashbot_description/
  urdf/
  xacro/

trashbot_sensors/
  launch/
  config/
  scripts/

trashbot_localization/
  launch/
  config/

trashbot_bringup/
  launch/

trashbot_navigation/
  launch/
  config/
```

역할:

- `trashbot_description`: `base_link`, `camera_link`, `imu_link`, `gps_link` 정의
- `trashbot_sensors`: D435i, 외부 IMU, GPS, encoder 드라이버/adapter
- `trashbot_localization`: `EKF`, `navsat_transform`, odom fusion
- `trashbot_bringup`: 전체 bring-up launch
- `trashbot_navigation`: Nav2 관련

## 6. 지금 만들어둘 설정 파일

하드웨어가 없어도 아래 설정 파일은 미리 만들어둘 수 있다.

1. `ekf_local.yaml`
2. `ekf_global.yaml`
3. `navsat_transform.yaml`
4. `sensor_fusion_bringup.launch.py`

이번 저장소에는 나중에 복사해서 쓸 수 있도록 템플릿을 같이 둔다.

템플릿 위치:

- [`templates/sensor_fusion_prebuild/README.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/templates/sensor_fusion_prebuild/README.md)

## 7. D435i만 있는 지금 단계에서 할 수 있는 것

지금은 외부 IMU, encoder, GPS가 없으므로 아래만 먼저 고정하는 것이 맞다.

### 7-1. camera frame 이름 고정

현재 이미 확인한 것:

- `camera_link`
- `camera_color_optical_frame`
- `camera_depth_optical_frame`

지금 해야 할 것:

- 이 이름을 이후 `URDF/xacro`와 맞출 계획을 세운다.

### 7-2. D435i는 메인 IMU로 쓰지 않는다고 전제

중요:

- D435i 내장 IMU는 실시간 회전 변화 확인에는 쓸 수 있다.
- 하지만 최종 메인 `robot_localization` 입력 IMU로는 외부 IMU를 우선하는 구조가 더 안전하다.

즉, 지금 D435i IMU는:

- 축 해석 확인
- 회전 변화 감지 실험
- 시각 odom 보조 가능성 검토

정도까지만 두는 것이 맞다.

### 7-3. topic contract 먼저 확정

하드웨어가 도착하면 토픽 이름 때문에 다시 흔들리지 않도록 아래를 먼저 확정한다.

- encoder -> `/wheel/odometry`
- external IMU filtered -> `/imu/data`
- GPS -> `/gps/fix`
- local EKF -> `/odometry/local`
- global EKF -> `/odometry/global`

### 7-4. D435i visual odom은 보조 입력으로만 고려

지금 단계에서는 `RTAB-Map` 또는 visual odom 결과를 메인 로컬 odom으로 확정하지 않는다.

이유:

- 실외 공터 최종 구조는 `GPS + encoder + IMU` 중심이기 때문
- 카메라 odom은 환경 의존성이 크기 때문

즉, D435i는 우선:

- perception
- local map
- 보조 시각 odom

으로 두는 것이 현실적이다.

## 8. 하드웨어 도착 후 실제 연동 순서

하드웨어가 오면 아래 순서로 붙이는 것이 가장 안전하다.

### 1단계. wheel encoder만 연결

확인:

- `/wheel/odometry`가 뜨는지
- 직진/회전 시 odom이 자연스러운지

### 2단계. external IMU 연결

확인:

- `/imu/data_raw` 또는 `/imu/data`가 뜨는지
- frame이 `imu_link`와 맞는지
- 중력 방향과 yaw rate 부호가 맞는지

### 3단계. local EKF 연결

입력:

- `/wheel/odometry`
- `/imu/data`

출력:

- `/odometry/local`
- `odom -> base_link`

### 4단계. GPS 연결

입력:

- `/gps/fix`

### 5단계. navsat_transform 연결

입력:

- `/gps/fix`
- `/imu/data`
- `/odometry/local`

출력:

- `/odometry/gps`

### 6단계. global EKF 연결

입력:

- `/odometry/local`
- `/odometry/gps`

출력:

- `/odometry/global`
- `map -> odom`

### 7단계. D435i 보조 odom/perception 추가

이 단계에서만 visual odom 또는 RTAB-Map을 다시 연결하는 것이 좋다.

## 9. 지금 미리 막아야 하는 흔한 실수

### 실수 1. IMU frame을 하나로 섞어버림

- D435i IMU와 외부 IMU를 같은 frame처럼 다루면 안 된다.

### 실수 2. GPS를 local EKF에 바로 넣음

- 보통은 `navsat_transform`을 거친 뒤 global EKF에 넣는 구조가 더 맞다.

### 실수 3. `map -> odom`과 `odom -> base_link` 역할을 섞음

- local과 global 역할이 섞이면 Nav2와 TF가 불안정해진다.

### 실수 4. encoder 토픽 이름과 메시지 타입을 늦게 정함

- 나중에 드라이버가 바뀌면 launch와 YAML을 다 고쳐야 한다.

### 실수 5. D435i를 메인 위치추정 센서로 과신

- D435i는 중요한 센서지만, 최종 실외 위치추정의 메인은 `encoder + external IMU + GPS` 구조가 더 현실적이다.

## 10. 다음 액션

지금 바로 할 다음 액션은 아래다.

1. 이후 실제 패키지 이름을 `trashbot_*`로 갈지 확정
2. `base_link`, `camera_link`, `imu_link`, `gps_link` naming rule 확정
3. 템플릿 YAML/launch를 이후 실제 패키지에 복사할 기준으로 리뷰
4. 하드웨어 도착 후 bring-up 순서를 이 문서 기준으로 진행

한 줄 요약:

- 지금은 하드웨어가 없어도 **토픽, TF, EKF 구조를 먼저 고정**하는 게 맞다.
- 실제 구현은 나중에 하더라도, **설계가 먼저 흔들리지 않게 하는 것이 지금 단계의 핵심**이다.
