# 시뮬레이션 선검증 기준 공터 쓰레기 수거 로봇 개발 절차

## 0. 결론

- 지금 프로젝트는 `바로 실하드웨어부터 붙이는 방식`보다 `URDF/xacro -> RViz2 TF 검증 -> Gazebo 시뮬레이션 -> Nav2/미션 로직 검증 -> 실제 센서 연동` 순서로 가는 것이 가장 안전하다.
- 공터 환경에서는 `VSLAM 중심 설계`보다 `GPS + 엔코더 + IMU` 중심 설계가 더 현실적이므로, 시뮬레이션에서도 그 구조를 기준으로 먼저 검증하는 것이 맞다.
- 즉, 이번 개발 절차의 핵심은 `먼저 로봇 구조와 소프트웨어를 가상환경에서 맞추고`, 그 다음 `실제 GPS/D435i/구동부 오차를 현장에서 튜닝`하는 것이다.
- `2026-04-25` 기준으로 Mari Onshape 모델에서 `base_link`, 센서 frame, 궤도 중심거리, 가상 구동축 후보를 측정했으므로, 다음 단계는 `Onshape URDF export -> Gazebo virtual wheel diff-drive` 검증이다.
- `2026-04-26` 기준으로 Onshape URDF/GLTF export와 Mari STL export는 보관했지만, Gazebo Classic에서 Mari visual mesh가 아직 보이지 않는다. 따라서 다음 순서는 `Gazebo visual mesh 표시 문제 해결 -> virtual wheel diff-drive 추가`다.

## 1. 이번 프로젝트에서 먼저 정해야 하는 기준

직관:
시뮬레이션이 잘 되려면, 먼저 "우리가 어떤 로봇을 만들고 싶은지"가 고정되어야 한다.

먼저 고정할 것:

1. 로봇 이동 방식
2. 센서 위치
3. 수거 장치 위치
4. 공터에서 어떻게 움직일지
5. 쓰레기를 어떻게 집을지

현재 기준 추천 가정:

- 이동 방식: `차동구동(differential drive)`
- 주 위치추정: `GPS + 엔코더 + IMU`
- 근거리 인지: `D435i`
- 내비게이션: `Nav2`
- 임무 방식: `순찰 -> 쓰레기 탐지 -> 접근 -> 집기 -> 복귀`

## 2. 왜 시뮬레이션부터 해야 하는가

직관:
하드웨어 없이도 먼저 검증할 수 있는 부분이 많다. 이걸 먼저 잡아야 실제 하드웨어 디버깅이 훨씬 쉬워진다.

시뮬레이션으로 먼저 확인 가능한 것:

- 로봇 구조가 논리적으로 맞는지
- 좌표계(TF)가 맞는지
- 바퀴 구동이 맞는지
- `/cmd_vel`, `/odom`, `/tf` 흐름이 맞는지
- Nav2가 목표점까지 가는지
- 상태기계(FSM)가 올바르게 도는지
- 두 로봇을 쓸 경우 namespace 구조가 안 꼬이는지

반대로 시뮬레이션만으로는 부족한 것:

- 실제 GPS 튐
- D435i의 야외 depth 성능
- 햇빛 환경
- 실제 바퀴 미끄러짐
- 흙/잔디 지면 오차
- 집기 정밀도

결론:
- `구조/소프트웨어`: 시뮬레이션 선검증
- `센서 품질/실외 오차`: 실하드웨어 검증

## 3. 전체 진행 절차 한눈에 보기

가장 추천하는 순서는 아래다.

1. 요구사항 고정
2. 로봇 3D 구조 단순화
3. URDF/xacro 작성
4. RViz2에서 TF 검증
5. Gazebo에서 차동구동 시뮬레이션
6. 가상 센서 토픽 연결
7. 가상 오도메트리와 Nav2 검증
8. 순찰/미션 로직 검증
9. 하드웨어 인터페이스 패키지 작성
10. 실제 엔코더/IMU/GPS bring-up
11. 실제 위치추정 튜닝
12. 실제 D435i 탐지/근거리 접근 검증
13. 실제 집기 장치 연동
14. 공터 실험과 반복 튜닝

### 2026-04-25 현재 Mari 적용 계획

현재 Mari 모델은 실제 궤도 belt 물리를 바로 시뮬레이션하지 않는다. 먼저 visual 모델은 Onshape에서 고정하고, Gazebo 주행은 가상 바퀴 기반 차동구동으로 검증한다.

```text
Onshape 정리
-> URDF export 시도
-> export URDF/Xacro 후처리
-> Gazebo visual mesh 표시 문제 해결
-> RViz2 TF 검증
-> Gazebo virtual wheel diff-drive 검증
```

현재 기록된 1차 파라미터는 아래다.

```text
track_width_m              = 0.137553
left_virtual_wheel_xyz_m   = 0.000000 0.0687765 0.000000
right_virtual_wheel_xyz_m  = 0.000000 -0.0687765 0.000000
virtual_wheel_axis_xyz     = 0 1 0
effective_track_radius_m   = 0.021
```

주의할 점은 실제 구동 톱니바퀴 중심축이 좌우 앞뒤로 비대칭이라는 것이다. 따라서 실제 CAD 측정값은 기록으로 남기되, Gazebo/diff-drive는 좌우 가상 바퀴를 같은 `x=0` 위치에 둔 단순 모델로 먼저 검증한다.

### 2026-04-26 Gazebo visual blocker

현재 `mari.urdf.xacro`는 렌더링과 `check_urdf` 파싱을 통과하지만, Gazebo GUI에서는 `mari` entity와 `base_footprint`만 보이고 Mari visual mesh가 화면에 표시되지 않는다.

이 상태에서 바로 diff-drive plugin을 붙이면 구동 문제와 시각화 문제가 섞인다. 따라서 먼저 아래 순서로 visual 문제를 분리한다.

```text
1. gzclient --verbose 로그에서 mesh load error 확인
2. package:// 또는 model:// mesh URI resolve 여부 확인
3. mari_visual_mesh.stl bounds, origin, scale 확인
4. 작은 box 또는 test STL visual이 Gazebo에 보이는지 비교
5. 필요 시 STL 대신 DAE/OBJ/GLTF 변환본으로 visual 표시 재시험
```

visual mesh가 보이는 것을 확인한 뒤에 `left_virtual_drive_wheel_link`, `right_virtual_drive_wheel_link`, `/cmd_vel`, `/odom` 연결로 넘어간다.

## 4. 단계별 상세 절차

### Phase 0. 요구사항과 하드웨어 구성을 먼저 고정

직관:
로봇 모델을 만들기 전에 센서와 링크 구성이 먼저 정해져야 한다.

확정할 항목:

- 바퀴 개수와 배치
- 차체 크기
- D435i 장착 위치
- GPS 안테나 위치
- IMU 위치
- 집게/흡입기 위치
- 배터리와 컴퓨팅 보드 위치

산출물:

- 로봇 대략 스케치
- 링크 이름 목록
- 센서 위치 메모

완료 기준:
- `base_link`, `camera_link`, `imu_link`, `gps_link`, `gripper_link`를 어디에 둘지 정함

### Phase 1. 단순 3D 모델 만들기

직관:
처음부터 예쁜 CAD가 필요하지 않다. 박스와 원통으로 먼저 구조만 맞추면 된다.

핵심 개념:
- `URDF`: 로봇 링크와 조인트 구조를 표현하는 파일 형식
- `xacro`: URDF를 더 편하게 재사용/매개변수화하는 방식

구현:
- 차체는 박스
- 바퀴는 원통
- 카메라는 작은 박스
- GPS/IMU는 단순 박스 또는 고정 링크
- 그리퍼는 단순 링크로 표현

완료 기준:
- RViz2에서 로봇 외형이 대략 보임
- 링크 이름이 정리됨

### Phase 2. URDF/xacro 작성

직관:
이 단계는 로봇의 "뼈대"를 만드는 단계다.

최소 구성:

```text
base_link
├── left_wheel_link
├── right_wheel_link
├── caster_link
├── camera_link
├── imu_link
├── gps_link
└── gripper_link
```

반드시 넣을 것:

- `visual`
- `collision`
- `inertial`
- joint type
- 센서 위치

흔한 실수:

- `inertial` 빼먹기
- 바퀴 축 방향 잘못 정의
- camera 위치를 실제와 다르게 둠
- gripper 위치를 너무 대충 정의함

완료 기준:
- `robot_state_publisher`로 TF가 정상 발행됨

### Phase 3. RViz2에서 TF와 좌표계 먼저 검증

직관:
시뮬레이션 이전에 좌표계가 맞아야 한다.

핵심 개념:
- `TF`: 좌표계 사이 변환 관계
- `base_link`: 로봇 본체 기준
- `camera_link`, `imu_link`, `gps_link`: 센서 기준 좌표계

우선 확인할 것:

- 카메라 방향이 전방을 보는지
- IMU 축이 실제 장착 방향과 맞는지
- GPS 안테나가 차체 중앙인지, 뒤쪽인지
- 그리퍼 기준점이 실제 집는 위치와 비슷한지

완료 기준:
- RViz2에서 센서 방향이 논리적으로 맞음
- 링크가 뒤집혀 있지 않음

### Phase 4. Gazebo에서 기본 주행 시뮬레이션

직관:
이 단계에서는 "로봇이 움직이는지"만 확인하면 된다.

구현:
- Gazebo에 로봇 spawn
- 차동구동 플러그인 또는 제어기 연결
- Mari는 실제 궤도 물리 대신 `left_virtual_drive_wheel_link`, `right_virtual_drive_wheel_link`를 사용
- `/cmd_vel` 입력
- 전진/후진/회전 테스트

완료 기준:
- 가상 환경에서 로봇이 안정적으로 움직임
- 좌우 회전과 직진이 예상대로 됨

### Phase 5. 가상 센서 토픽 연결

직관:
이제부터는 "로봇 모양"이 아니라 "센서 데이터 흐름"을 맞춰야 한다.

가상으로 먼저 넣을 것:

- IMU
- wheel odom
- GPS
- RGB 카메라
- depth 카메라

목적:
- 실제 하드웨어 없이도 ROS2 토픽 구조를 먼저 맞추기

완료 기준:
- `/odom`, `/imu`, `/gps/fix`, `/camera/image_raw` 같은 기본 토픽 구조가 만들어짐

### Phase 6. 위치추정 체인 시뮬레이션 검증

직관:
공터 프로젝트에서는 이 단계가 핵심이다.

추천 구조:

```text
wheel odom + IMU -> EKF -> odom -> base_link
GPS -> navsat_transform -> 전역 위치
```

핵심 개념:
- `EKF`: 여러 센서를 섞어 안정적인 상태를 만드는 필터
- `navsat_transform_node`: GPS를 로봇 기준 좌표와 연결해주는 노드

시뮬레이션에서 볼 것:

- `/odometry/filtered`
- `map -> odom`
- `odom -> base_link`

완료 기준:
- TF 체인이 끊기지 않음
- 회전/직진 시 filtered odom이 부드럽게 나옴

### Phase 7. Nav2를 시뮬레이션에서 먼저 붙이기

직관:
실차에 붙이기 전에 가상 목표점 주행을 먼저 성공시키는 것이 중요하다.

구현:
- global planner
- local controller
- global/local costmap
- waypoint 주행

완료 기준:
- 가상 공터에서 지정한 목표점까지 이동
- 장애물이 있으면 우회

### Phase 8. 순찰과 미션 로직을 시뮬레이션에서 먼저 작성

직관:
자율주행은 이동만 성공한다고 끝이 아니다. 임무 순서가 제대로 돌아야 한다.

추천 상태:

1. `IDLE`
2. `PATROL`
3. `DETECT_TRASH`
4. `APPROACH_TRASH`
5. `ALIGN`
6. `PICKUP`
7. `VERIFY`
8. `GO_TO_BIN`
9. `DROP`
10. `RECOVERY`

먼저 시뮬레이션에서 검증할 것:

- waypoint 순찰
- 탐지 이벤트 발생 시 상태 전이
- 접근 목표점 생성
- 복귀 동작

완료 기준:
- 가짜 탐지 신호만 넣어도 전체 상태 흐름이 돈다

### Phase 9. 두 로봇을 쓸 가능성까지 고려한 소프트웨어 구조 정리

직관:
처음부터 2대를 동시에 돌리지는 않더라도, namespace를 안 잡아두면 나중에 다 뜯어고쳐야 한다.

추천 구조:

- `/robot1/...`
- `/robot2/...`

필수 분리 대상:

- `tf`
- `odom`
- `cmd_vel`
- `gps`
- camera topic
- mission state

완료 기준:
- 단일 로봇 구조를 namespace 친화적으로 설계함

### Phase 10. 하드웨어 인터페이스 패키지 작성

직관:
이제 시뮬레이션 구조를 실제 하드웨어와 연결해야 한다.

필요 패키지 예시:

- `robot_description`
- `robot_bringup`
- `robot_base`
- `robot_localization`
- `robot_nav`
- `robot_perception`
- `robot_pickup`
- `robot_task`

완료 기준:
- 시뮬레이션용 launch와 실기기용 launch를 분리함

### Phase 11. 실제 하드웨어 bring-up

직관:
여기서부터 실제 센서 품질 문제가 드러난다.

실기기에서 우선 볼 순서:

1. 엔코더
2. IMU
3. GPS
4. D435i

이 순서를 추천하는 이유:
- 바퀴와 IMU가 먼저 안정화되어야 GPS와 카메라 오차를 분리해서 볼 수 있다.

완료 기준:
- 모든 센서가 ROS2 토픽으로 안정적으로 출력
- rosbag 기록 가능

### Phase 12. 실제 위치추정 튜닝

직관:
시뮬레이션에서 맞춘 값은 실제 공터에서 그대로 안 맞을 가능성이 크다.

우선 점검:

- 바퀴 반지름
- 바퀴 간 거리
- 엔코더 스케일
- IMU 축 방향
- GPS 위치 튐
- timestamp sync

완료 기준:
- 짧은 구간 주행에서 로봇 위치가 논리적으로 맞음
- 정지 상태에서 자세가 과도하게 흔들리지 않음

### Phase 13. D435i를 근거리 센서로 연동

직관:
D435i는 공터 전체 위치추정보다 마지막 접근과 탐지에서 더 유용하다.

구현:
- RGB 스트림 확인
- depth 품질 확인
- 햇빛 환경에서 usable range 확인
- 근거리 장애물과 쓰레기 후보 탐지 연결

완료 기준:
- 쓰레기까지의 대략 거리 계산 가능
- 마지막 접근용 카메라 입력으로 사용 가능

### Phase 14. 쓰레기 탐지와 접근

직관:
이제 이동 시스템 위에 수거 임무를 붙이는 단계다.

구현:
- detector 연결
- bounding box -> 3D 위치 계산
- 목표 쓰레기 앞 정지점 생성
- 저속 정밀 접근

완료 기준:
- 탐지된 쓰레기 앞으로 반복적으로 접근 가능

### Phase 15. 수거 장치 연동

구현:
- 그리퍼 또는 흡입기 제어
- 성공 여부 확인
- 실패 시 재시도 로직

완료 기준:
- 동일한 쓰레기를 여러 번 반복 수거 가능

### Phase 16. 실외 공터 반복 실험

직관:
실외는 실내보다 훨씬 변동성이 크다. 반복 실험으로 튜닝해야 한다.

반복 점검 항목:

- GPS 튐
- 진동에 의한 IMU 노이즈
- D435i depth 불안정
- 바퀴 미끄러짐
- 접근 정렬 오차
- 집기 실패 원인

완료 기준:
- 순찰 -> 탐지 -> 접근 -> 수거 -> 복귀 흐름이 반복적으로 성공

## 5. 지금 시점에서 가장 먼저 해야 할 실제 작업

지금 바로 시작할 순서는 아래가 가장 좋다.

1. 로봇 링크 구조를 종이에 스케치한다.
2. `xacro`로 `base_link`, 바퀴, D435i, GPS, IMU, 그리퍼를 만든다.
3. RViz2에서 TF를 확인한다.
4. Gazebo에서 차동구동을 먼저 붙인다.
5. Nav2 waypoint 주행을 시뮬레이션에서 먼저 성공시킨다.
6. 그 다음 실제 엔코더/IMU/GPS를 붙인다.
7. 마지막으로 D435i와 쓰레기 탐지를 붙인다.

## 6. 시뮬레이션에서 먼저 검증할 항목 체크리스트

- URDF/xacro가 정상 파싱된다.
- `robot_state_publisher`로 TF가 정상 발행된다.
- RViz2에서 링크 방향이 맞다.
- Gazebo에서 전진/회전이 된다.
- `/cmd_vel`과 `/odom` 흐름이 맞다.
- EKF 구조가 돈다.
- Nav2 목표점 이동이 된다.
- FSM 상태 전이가 동작한다.

## 7. 실제 하드웨어에서 반드시 다시 검증할 항목 체크리스트

- 엔코더 스케일
- IMU 축 방향
- GPS 정확도와 튐
- D435i 실외 depth 성능
- timestamp sync
- 센서 장착 위치 오차
- 바퀴 미끄러짐
- 집기 정렬 오차

## 8. 개발 원칙

- 구조와 소프트웨어는 먼저 시뮬레이션에서 검증한다.
- 실외 센서 성능은 반드시 현장에서 다시 검증한다.
- 공터에서는 GPS 중심 설계를 우선한다.
- D435i는 근거리 인지와 정밀 접근에 먼저 사용한다.
- 두 로봇까지 고려한다면 namespace 구조를 처음부터 분리한다.
- 문제가 생기면 `좌표계 -> 센서 품질 -> timestamp -> 파라미터` 순서로 본다.

## 9. 참고 자료

- ROS 2 URDF Tutorial: https://docs.ros.org/en/ros2_packages/jazzy/api/urdf_tutorial/
- Gazebo ROS 2 Integration: https://gazebosim.org/docs/harmonic/ros2_integration/
- Gazebo ROS 2 Simulation Interfaces: https://gazebosim.org/docs/latest/ros2_sim_interfaces/
- Nav2 Getting Started: https://docs.nav2.org/getting_started/index.html
