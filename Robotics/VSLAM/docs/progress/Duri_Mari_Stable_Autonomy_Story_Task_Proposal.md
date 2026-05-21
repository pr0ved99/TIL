# Duri/Mari Stable Autonomy Story Task Proposal

## 결론

기존 `S14P31C205-1279 ~ S14P31C205-1327`은 Duri/Mari 협업 청소 기능까지 넓게 잡혀 있다. 새로 만들 후보는 그보다 앞단의 **안정적인 자율주행 기반을 보강하는 Story/Task**로 잡는 것이 좋다.

추천 신규 Story 묶음은 아래 6개다.

```text
Story A. Duri sensor/TF/topic contract 고정
Story B. Duri encoder odom calibration
Story C. Duri encoder+IMU local EKF 안정화
Story D. RTAB-Map external odom mapping 안정화
Story E. Depth pointcloud obstacle layer 튜닝
Story F. GPS global EKF outdoor smoke test
```

이 문서는 Jira에 바로 생성했다는 뜻이 아니라, copy-ready 초안이다.

## 기존 Backlog와의 관계

이미 있는 협업 청소 후보:

- Duri 쓰레기 흡입 가능성 판단
- Duri가 Mari에게 흡입 불가능 쓰레기 위치 전달
- Mari push-to-bin
- 지도 기반 coverage 주행
- GPS/IMU/encoder 기반 야외 위치추정
- 네트워크 불안정 환경의 trash event 저장/동기화
- Duri/Mari RTAB-Map 세션과 좌표 기준 동기화

새로 제안하는 후보:

- 위 기능을 하기 전에 필요한 주행 안정화 기반이다.
- 특히 `map -> odom`, `odom -> base_footprint`, covariance, depth obstacle, GPS jump 문제를 먼저 줄이는 데 초점을 둔다.

## Story A

Story

- Title: 운영자는 Duri 자율주행 입력을 안정화하기 위하여 sensor, TF, topic 계약을 고정할 것이다.
- Priority: Highest
- Story Points: 5
- Description:
  - Duri 단일 실행과 Duri/Mari 동시 실행에서 topic namespace와 TF prefix를 구분한다.
  - Nav2와 RTAB-Map이 기대하는 topic, frame, QoS, timestamp 기준을 문서화한다.
  - `map -> odom -> base_footprint -> base_link -> camera_link/imu_link/gps_link` 체인을 검증한다.
- Acceptance Criteria:
  - Duri 단일 실행 기준 topic list와 TF tree가 증빙으로 저장된다.
  - `camera_color_optical_frame`, `imu_link`, `gps_link`의 parent frame이 명확하다.
  - `map -> odom` publisher ownership 정책이 문서화된다.
  - Jetson/Laptop 공통 `ROS_DOMAIN_ID`, `ROS_LOCALHOST_ONLY` 기준이 정리된다.

Tasks

- [EM] Duri 단일 실행 topic/frame contract 문서화
  - Story Points: 2
  - Description:
    - `/cmd_vel`, `/odom`, `/imu/data`, `/camera/...`, `/tf`, `/tf_static` 기준을 정리한다.
    - multi-robot namespace와 섞이지 않도록 Duri 단일 기준을 별도 표로 만든다.
- [EM] Duri TF tree 증빙 자동 수집 스크립트 작성
  - Story Points: 3
  - Description:
    - `view_frames`, `tf2_echo`, topic list를 날짜별 assets 폴더에 저장한다.
- [EM] RTAB-Map/Nav2 map->odom ownership 정책 정리
  - Story Points: 2
  - Description:
    - static TF, RTAB-Map, global EKF 중 누가 `map -> odom`을 publish하는지 단계별로 분리한다.

## Story B

Story

- Title: 운영자는 Duri의 실제 이동량을 정확히 추정하기 위하여 encoder odometry를 보정할 것이다.
- Priority: Highest
- Story Points: 8
- Description:
  - Mari 기준 encoder 파라미터를 Duri에 그대로 쓰지 않고, Duri track geometry와 실제 tick 측정값으로 분리한다.
  - `/motor/encoder_ticks -> /wheel/odometry` 변환을 Duri 기준으로 검증한다.
- Acceptance Criteria:
  - Duri 전용 `ticks_per_revolution`, `effective_wheel_radius_m`, `track_width_m` 후보값이 문서화된다.
  - 1m 직진, 제자리 회전, 왕복 주행에서 encoder odom 오차가 기록된다.
  - tick sign과 좌우 scale 보정값이 정리된다.
  - outlier reject 기준이 실제 로그 기반으로 조정된다.

Tasks

- [EM] Duri encoder tick 방향 및 누적 규칙 검증
  - Story Points: 3
  - Description:
    - 전진/후진/좌회전/우회전에서 left/right tick 부호를 기록한다.
- [EM] Duri 1m 직진 기반 wheel radius 보정
  - Story Points: 3
  - Description:
    - 실제 이동 거리와 `/wheel/odometry` 거리 차이로 scale을 산출한다.
- [EM] Duri 제자리 회전 기반 track width 보정
  - Story Points: 3
  - Description:
    - 90도/180도/360도 회전에서 yaw 오차를 기록하고 track width를 조정한다.
- [EM] encoder outlier/gap 방어 기준 튜닝
  - Story Points: 2
  - Description:
    - `max_tick_delta`, `max_encoder_gap_sec`, 속도 제한값을 실제 로그 기준으로 정한다.

## Story C

Story

- Title: 운영자는 Duri의 로컬 위치추정을 안정화하기 위하여 encoder와 IMU를 EKF로 융합할 것이다.
- Priority: Highest
- Story Points: 8
- Description:
  - `/wheel/odometry`와 `/imu/data`를 `robot_localization`으로 융합해 `/odometry/local`과 `odom -> base_footprint`를 안정화한다.
  - Duri 전용 covariance profile을 만든다.
- Acceptance Criteria:
  - `/odometry/local`이 목표 rate로 publish된다.
  - 정지 상태 drift, 직진 yaw drift, 회전 yaw 오차가 측정된다.
  - IMU yaw/yaw_rate 부호가 실제 회전 방향과 일치한다.
  - Nav2가 `/odometry/local` 기반으로 가까운 goal을 처리한다.

Tasks

- [EM] IMU frame/axis/yaw 방향 검증
  - Story Points: 3
  - Description:
    - `base_link -> imu_link` TF와 IMU ENU 방향을 확인한다.
- [EM] Duri local EKF YAML 작성
  - Story Points: 3
  - Description:
    - wheel odom과 IMU에서 사용할 state vector를 분리한다.
- [EM] EKF covariance 튜닝 로그 수집
  - Story Points: 3
  - Description:
    - 정지/직진/회전 bag을 수집하고 covariance 변화를 기록한다.
- [EM] `/odometry/local` Nav2 smoke test
  - Story Points: 2
  - Description:
    - empty map 또는 작은 map에서 가까운 goal 성공률을 확인한다.

## Story D

Story

- Title: 운영자는 RTAB-Map map 품질을 높이기 위하여 Duri RGB-D mapping에 external odom을 연결할 것이다.
- Priority: High
- Story Points: 8
- Description:
  - RTAB-Map visual odometry 단독 의존을 줄이고, EKF가 만든 `/odometry/local`을 입력으로 사용한다.
  - RTAB-Map은 RGB-D map, loop closure, local grid 생성에 집중하게 한다.
- Acceptance Criteria:
  - RTAB-Map launch가 `visual_odometry:=false`, `odom_topic:=/odometry/local`로 실행된다.
  - `/rtabmap/map`, `/rtabmap/mapData`, `/rtabmap/info`가 안정적으로 publish된다.
  - 같은 경로 반복 주행에서 map tearing이 줄어든다.
  - `map -> odom` TF publisher가 하나만 존재한다.

Tasks

- [EM] Duri RTAB-Map external odom launch 작성
  - Story Points: 3
  - Description:
    - Mari 이름 launch를 그대로 쓰지 않고 Duri/generic wrapper로 분리한다.
- [EM] RTAB-Map DB single-session/reuse 검증
  - Story Points: 3
  - Description:
    - `delete_db_on_start` true/false 조건에서 trajectory 누적을 비교한다.
- [EM] RTAB-Map 품질 지표 수집
  - Story Points: 2
  - Description:
    - `/rtabmap/info`, loop closure id, inlier/quality 값을 저장한다.
- [EM] Nav2와 RTAB-Map `map -> odom` 충돌 방지
  - Story Points: 2
  - Description:
    - Nav2 static TF 옵션을 끄는 조건을 launch argument로 명확히 한다.

## Story E

Story

- Title: 운영자는 depth 기반 장애물 회피를 안정화하기 위하여 Duri pointcloud obstacle layer를 튜닝할 것이다.
- Priority: High
- Story Points: 5
- Description:
  - depth image 한 줄 `/scan` 방식 대신 height-filtered PointCloud2를 Nav2 obstacle input으로 사용한다.
  - 바닥점과 로봇 자기 몸체 point를 제거한다.
- Acceptance Criteria:
  - `/duri/filtered_depth_points`가 publish된다.
  - RViz에서 바닥점이 대부분 제거되고 낮은 장애물이 남는다.
  - Nav2 local costmap이 장애물을 반영한다.
  - false obstacle 때문에 goal이 막히는 사례가 감소한다.

Tasks

- [EM] Duri pointcloud height/self filter 파라미터 튜닝
  - Story Points: 3
  - Description:
    - `min_z`, `max_z`, self-filter box를 Gazebo와 실물에서 각각 조정한다.
- [EM] Nav2 obstacle layer topic 연결 검증
  - Story Points: 2
  - Description:
    - local/global costmap에 `/duri/filtered_depth_points`가 반영되는지 확인한다.
- [EM] 장애물 회피 smoke test 증빙 정리
  - Story Points: 2
  - Description:
    - RViz screenshot, costmap topic, `/cmd_vel` 변화를 저장한다.

## Story F

Story

- Title: 운영자는 야외 자율주행을 준비하기 위하여 GPS 기반 global EKF를 구성할 것이다.
- Priority: High
- Story Points: 8
- Description:
  - GPS를 local odom에 직접 넣지 않고 `navsat_transform_node`와 global EKF로 분리한다.
  - outdoor waypoint와 Duri/Mari shared global frame의 기반을 만든다.
- Acceptance Criteria:
  - `/gps/fix`와 covariance가 수집된다.
  - `navsat_transform_node`가 `/odometry/gps`를 publish한다.
  - local EKF와 global EKF가 분리된다.
  - GPS jump가 local controller를 직접 흔들지 않는다.
  - 짧은 outdoor waypoint smoke test 결과가 저장된다.

Tasks

- [EM] GPS NavSatFix topic 및 covariance 점검
  - Story Points: 2
  - Description:
    - fix status, covariance, update rate를 기록한다.
- [EM] navsat_transform_node Duri profile 작성
  - Story Points: 3
  - Description:
    - yaw offset, magnetic declination, datum 정책을 정리한다.
- [EM] local/global dual EKF launch 작성
  - Story Points: 5
  - Description:
    - local EKF는 `world_frame=odom`, global EKF는 `world_frame=map`으로 분리한다.
- [EM] outdoor straight/turn/bag 검증
  - Story Points: 3
  - Description:
    - GPS jump, odom drift, yaw drift를 비교한다.

## 생성 우선순위

추천 순서:

1. Story A: sensor/TF/topic contract
2. Story B: Duri encoder odom calibration
3. Story C: Duri encoder+IMU local EKF
4. Story D: RTAB-Map external odom mapping
5. Story E: depth pointcloud obstacle layer
6. Story F: GPS global EKF

협업 청소 Story는 이 기반이 안정화된 뒤 아래 순서로 진행한다.

```text
trash pose projector
-> trash event schema
-> Duri event to Mari goal
-> map_session_id / GPS pose 포함
-> network/offline queue
```

## 한 줄 요약

새 Story/Task는 쓰레기 협업 기능을 더 늘리기 전에, Duri의 `TF/topic 계약`, `encoder odom`, `local EKF`, `RTAB-Map external odom`, `depth obstacle`, `GPS global EKF`를 안정화하는 순서로 만드는 것이 좋다.
