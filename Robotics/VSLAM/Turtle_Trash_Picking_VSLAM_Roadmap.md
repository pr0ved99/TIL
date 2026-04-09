# VSLAM으로 쓰레기 줍는 거북이 로봇 만들기 단계별 진행방안

## 0. 결론

- 가장 실용적인 방법은 `VSLAM만 단독으로` 자율주행을 만들려 하지 말고, `VSLAM + 바퀴 오도메트리 + IMU + Nav2 + 쓰레기 탐지 + 수거 상태기계`로 시스템을 나누는 것이다.
- 초보자 기준으로는 `직접 VSLAM 알고리즘 구현`보다 `검증된 패키지로 먼저 성공`하는 경로가 훨씬 안전하다.
- 추천 순서는 `수동주행 가능한 로봇 만들기 -> 센서/좌표계 정리 -> 베이스라인 VSLAM 성공 -> Nav2로 주행 성공 -> 쓰레기 탐지 추가 -> 수거 행동 추가 -> 성능 개선`이다.

## 1. 먼저 큰 그림부터

직관:
VSLAM은 "로봇이 지금 어디 있는지"를 알려주는 기술이다. 하지만 자율주행은 위치만 안다고 끝나지 않는다. 어디로 갈지 계획하고, 장애물을 피하고, 쓰레기를 발견하면 접근하고, 집으면 다시 이동해야 한다.

핵심 개념:
- `VSLAM`: 카메라 영상으로 위치와 지도를 추정하는 기술
- `Odometry(오도메트리)`: 바퀴, IMU, 비전 등으로 짧은 구간 움직임을 계속 추적하는 기술
- `Nav2`: ROS2에서 경로 계획과 주행 제어를 담당하는 내비게이션 스택
- `Perception(인지)`: 카메라로 쓰레기를 찾는 단계
- `State Machine(상태기계)`: 탐색, 접근, 집기, 복귀 같은 임무 순서를 관리하는 로직

쓰레기 줍는 거북이 로봇에 필요한 최소 블록:

1. 주행 베이스
2. 카메라와 IMU
3. 바퀴 엔코더
4. VSLAM
5. Nav2
6. 쓰레기 탐지
7. 집는 장치
8. 임무 제어 노드

## 2. 왜 VSLAM만으로는 부족한가

직관:
카메라만 보고도 맵은 만들 수 있다. 하지만 실제 자율주행은 "부드러운 단기 움직임"과 "전역 기준 위치"가 둘 다 필요하다.

핵심 개념:
- `map -> odom`: 전역 위치 보정. 보통 SLAM/VSLAM이 담당
- `odom -> base_link`: 부드러운 단기 자세 추정. 보통 바퀴, IMU, VIO, EKF가 담당
- `base_link`: 로봇 본체 기준 좌표계

중요:
Nav2 공식 문서는 `map -> odom -> base_link -> sensor frames` 형태의 TF tree가 필요하다고 설명한다. 또한 `odom -> base_link`와 `nav_msgs/Odometry`가 필요하다고 명시한다.

실무 추천:
- `VSLAM`: 전역 위치와 맵
- `wheel encoder + IMU + robot_localization(EKF)`: 부드러운 로컬 오도메트리
- `Nav2`: 경로 계획과 추종

즉, 추천 구조는 아래와 같다.

```text
wheel encoder + IMU ---> EKF ---> odom -> base_link
camera ----------------> VSLAM -> map -> odom
map + odom + obstacle -> Nav2
camera image ----------> trash detector
detector + nav state --> mission manager
```

## 3. 현재 단계에서 가정할 로봇 구성

아래 구성으로 가정하고 계획한다. 다르면 나중에 조정하면 된다.

- 이동 방식: 차동구동(differential drive)
- 카메라: D435i 같은 RGB-D 카메라
- 센서: IMU, wheel encoder
- 컴퓨팅: Jetson Orin Nano
- 미들웨어: ROS2 Humble
- 목적: 실내에서 쓰레기를 발견하고 접근한 뒤 집어서 지정 위치로 이동

센서 구성이 아직 확정되지 않았다면 우선 아래 4개를 먼저 확인해야 한다.

1. 카메라 모델
2. IMU 유무
3. wheel encoder 유무
4. 집는 장치가 흡입형인지, 집게형인지

## 4. 추천 기술 선택안

### 추천 1안: 가장 실용적인 선택

- `VSLAM`: RTAB-Map RGB-D
- `Odometry Fusion`: robot_localization EKF
- `Navigation`: Nav2
- `Trash Detection`: YOLO 계열 또는 간단한 색/형태 기반 detector
- `Task Logic`: 상태기계(FSM)

장점:
- 가장 빨리 성공 가능
- ROS2 연동이 쉽다
- 디버깅 포인트를 단계별로 분리하기 좋다

단점:
- "VSLAM 직접 구현" 학습 효과는 낮다

### 추천 2안: 공부용 확장 선택

- 위 1안으로 먼저 성공
- 이후 Frontend/VO/Backend를 직접 구현하며 교체

장점:
- 실제 동작과 학습을 동시에 잡을 수 있다

단점:
- 시간이 오래 걸린다

결론:
지금 너한테는 `추천 1안`이 맞다.

## 5. 최종 목표를 먼저 정의

최종 목표를 애매하게 잡으면 중간에 계속 흔들린다. 아래처럼 구체적으로 정하는 게 좋다.

### 목표 A. 이동

- 실내 공간에서 맵 생성
- 맵 저장 후 재시작해도 자기 위치 인식
- 지정한 목표점까지 충돌 없이 이동

### 목표 B. 쓰레기 인식

- 카메라로 쓰레기 후보를 인식
- 2D 박스만이 아니라 대략적인 3D 위치까지 계산

### 목표 C. 수거

- 쓰레기까지 접근
- 집는 위치로 자세 정렬
- 집기 성공 여부 확인

### 목표 D. 미션

- 탐색
- 쓰레기 발견
- 접근
- 수거
- 적재 위치 또는 복귀 위치로 이동

## 6. 전체 단계 요약

가장 추천하는 순서는 아래다.

1. 로봇을 수동조작으로 안정적으로 움직이기
2. ROS2에서 센서 토픽과 TF tree 정리
3. wheel encoder + IMU 기반 오도메트리 만들기
4. VSLAM으로 map 생성과 localization 성공
5. Nav2로 목표점 주행 성공
6. 카메라로 쓰레기 탐지 성공
7. 쓰레기 위치를 로봇 좌표계로 변환
8. 접근 및 정렬 동작 추가
9. 집기 장치 제어 추가
10. 전체 미션 상태기계 통합
11. 성능 측정과 실패 복구 추가

## 7. 단계별 진행방안

### Step 1. 로봇 베이스부터 먼저 안정화

직관:
로봇이 똑바로 못 가면 VSLAM이 잘 돼도 의미가 없다.

핵심 개념:
- `Differential Drive`: 좌우 바퀴 속도 차이로 회전하는 구동 방식
- `cmd_vel`: ROS2에서 로봇 속도 명령을 보내는 기본 토픽

구현:
- 수동조작으로 전진, 후진, 제자리 회전 가능하게 만들기
- 일정 속도 명령에서 실제 속도가 크게 흔들리지 않게 하기
- 바퀴 반지름, 바퀴 간 거리(`wheel separation`) 측정

완료 기준:
- 2m 직진 시 심한 좌우 쏠림이 없음
- 제자리 회전이 반복 실행 시 비슷하게 나옴
- `/cmd_vel` 입력에 안정적으로 반응

### Step 2. 좌표계와 TF tree 정리

직관:
VSLAM과 Nav2가 망가지는 가장 흔한 원인이 좌표계다.

핵심 개념:
- `TF`: 좌표계 사이 변환 관계
- `base_link`: 로봇 본체 중심
- `camera_link`, `imu_link`: 센서 기준 좌표계

필수 좌표계:

```text
map -> odom -> base_link -> camera_link
                         -> imu_link
                         -> gripper_link
```

우선 확인할 것:
- 카메라 방향이 실제와 맞는가
- IMU 축 방향이 문서와 맞는가
- 카메라가 base_link에서 얼마나 떨어져 있는가
- gripper 기준점이 정의되어 있는가

흔한 실수:
- optical frame 축을 일반 frame처럼 생각함
- IMU 축 방향 반전
- base_link 위치를 로봇 앞쪽에 잡아 회전 반경 계산이 틀어짐

완료 기준:
- RViz2에서 TF tree가 끊기지 않음
- 센서 위치가 시각적으로 맞아 보임

### Step 3. 센서 bring-up과 기록

직관:
좋은 알고리즘보다 먼저 좋은 입력이 필요하다.

핵심 개념:
- `Bring-up`: 하드웨어 드라이버와 ROS2 노드를 정상 실행시키는 단계
- `rosbag2`: 센서 데이터를 기록하는 도구

구현:
- RGB, depth, IMU, encoder 토픽 확인
- frame rate 확인
- rosbag 기록
- 정지 상태 데이터와 주행 데이터를 모두 수집

특히 먼저 볼 것:
- timestamp sync
- depth와 RGB 정렬
- IMU 드롭
- encoder 누락

완료 기준:
- 3분 이상 센서 토픽이 안정적으로 유지
- rosbag 재생 시 같은 토픽이 재현

### Step 4. 바퀴 오도메트리 만들기

직관:
VSLAM은 전역 위치에 강하고, 바퀴 오도메트리는 짧은 구간 움직임을 부드럽게 추적하는 데 강하다.

핵심 개념:
- `Odometry`: 이동 거리와 회전을 누적해서 자세를 추정하는 것
- `nav_msgs/Odometry`: ROS2에서 위치/속도 추정치를 담는 메시지

구현:
- wheel encoder로 `/odom` 생성
- `odom -> base_link` TF 발행
- 속도와 방향이 실제 움직임과 맞는지 확인

현실적인 추천:
- 가능하면 `ros2_control + diff_drive_controller`
- 최소 구현이라면 직접 odom 계산 노드 작성

완료 기준:
- 저속 주행에서 odom 궤적이 대충 맞음
- 정지 상태에서 odom이 크게 흔들리지 않음

### Step 5. IMU를 붙이고 EKF로 융합

직관:
바퀴만 쓰면 미끄러짐에 약하고, IMU만 쓰면 드리프트가 크다. 둘을 합치면 더 안정적이다.

핵심 개념:
- `EKF(Extended Kalman Filter)`: 여러 센서 값을 섞어서 더 안정적인 상태 추정을 만드는 필터
- `robot_localization`: ROS2에서 센서 융합에 자주 쓰는 패키지

구현:
- encoder odom + IMU를 EKF로 융합
- `/odometry/filtered` 출력
- `odom -> base_link`를 EKF 결과로 사용

우선 확인:
- IMU 중력 방향
- yaw 방향 부호
- covariance 설정
- 정지 상태 노이즈 크기

완료 기준:
- 정지 상태에서 자세 흔들림이 감소
- 회전 시 encoder 단독보다 더 자연스러움

### Step 6. 베이스라인 VSLAM 성공

직관:
처음부터 직접 구현하지 말고, 검증된 VSLAM으로 먼저 맵과 위치 추정을 성공시켜야 한다.

핵심 개념:
- `Baseline`: 비교 기준이 되는 기본 시스템
- `RGB-D SLAM`: 컬러 영상과 depth를 함께 쓰는 SLAM

추천:
- 첫 번째: `RTAB-Map RGB-D`
- 두 번째 비교용: `ORB-SLAM3 RGB-D`

구현:
- RGB-D 카메라를 VSLAM에 연결
- 실내 맵 생성
- 한 바퀴 돌아 출발점 복귀
- map 저장과 localization 모드 확인

여기서 제일 먼저 체크:
- 좌표계
- calibration
- timestamp sync
- scale drift
- outlier rejection

완료 기준:
- 한 공간을 돌고 돌아왔을 때 맵이 크게 벌어지지 않음
- localization 모드에서 시작 위치를 다시 찾음

### Step 7. VSLAM과 오도메트리 역할 분리

직관:
실제로는 "VSLAM이 모든 걸 다 한다"보다 "VSLAM은 전역 보정, EKF 오도메트리는 로컬 부드러움" 구조가 안정적이다.

핵심 개념:
- `map -> odom`: VSLAM 또는 localization 시스템이 제공
- `odom -> base_link`: EKF가 제공

권장 구조:

```text
RTAB-Map(or VSLAM) -> map -> odom
EKF                -> odom -> base_link
Nav2               -> path planning / control
```

완료 기준:
- TF tree가 안정적
- VSLAM이 순간적으로 튀어도 Nav2 제어가 완전히 무너지지 않음

### Step 8. Nav2로 목표점 주행

직관:
이제 "어디 있는지"를 알았으니 "어디로 갈지"를 계산해야 한다.

핵심 개념:
- `Global Planner`: 큰 경로를 짜는 모듈
- `Local Controller`: 바로 앞 구간을 따라가는 제어기
- `Costmap`: 장애물 회피용 지도

구현:
- 맵 기반 주행 구성
- global costmap, local costmap 설정
- 목표점 하나를 주고 자동 이동

중요:
- VSLAM 맵이 정적 지도 역할
- depth 또는 lidar가 local obstacle source 역할
- inflation radius는 로봇 실제 크기보다 여유 있게 설정

완료 기준:
- 클릭한 목표점까지 자동 이동
- 의자, 벽, 박스 같은 장애물을 피해 감

### Step 9. 쓰레기 탐지 추가

직관:
주행과 쓰레기 인식은 분리해서 개발하는 게 좋다.

핵심 개념:
- `Detection`: 물체가 어디 있는지 찾는 것
- `Classification`: 그것이 무엇인지 구분하는 것

추천 순서:

1. 색상/형태가 단순한 테스트 쓰레기부터 시작
2. 규칙 기반 또는 간단한 detector
3. 그 다음 YOLO 같은 학습 기반 detector

구현:
- 카메라 영상에서 쓰레기 bounding box 검출
- depth와 결합해서 3D 위치 추정
- `base_link` 기준 쓰레기 좌표 계산

완료 기준:
- 화면에서 쓰레기를 찾으면 로봇 기준 `(x, y, z)` 추정 가능

### Step 10. 쓰레기 접근 행동 만들기

직관:
탐지했다고 바로 집을 수는 없다. 먼저 안전하게 가까이 가고 자세를 맞춰야 한다.

핵심 개념:
- `Goal Pose`: 목표 위치와 자세
- `Approach Behavior`: 대상 근처까지 접근하는 행동

구현:
- 쓰레기 앞 일정 거리 지점을 임시 목표점으로 생성
- Nav2로 접근
- 마지막 30~50cm는 저속 정밀 제어
- 쓰레기가 카메라 중심에 오도록 yaw 정렬

완료 기준:
- 쓰레기 근처까지 반복적으로 접근 가능
- 접근 직전 자세가 크게 틀어지지 않음

### Step 11. 집는 장치 제어

직관:
집는 동작은 SLAM과 별개로 보이지만, 실제로는 위치 오차와 깊이 오차 영향을 많이 받는다.

핵심 개념:
- `End-effector`: 집게나 흡입기처럼 실제로 물체를 집는 끝단
- `Pickup Window`: 집기가 성공하는 허용 위치/자세 범위

구현:
- gripper 또는 suction 제어 노드 작성
- 집기 직전 정지
- 집기 성공 센서 확인
- 실패 시 재시도 조건 정의

완료 기준:
- 동일한 쓰레기 물체를 여러 번 반복 수거 가능

### Step 12. 전체 미션 상태기계 통합

직관:
이제부터는 알고리즘보다 "순서 제어"가 중요해진다.

핵심 개념:
- `FSM(Finite State Machine)`: 상태와 전이 규칙으로 동작을 제어하는 방식

추천 상태:

1. `IDLE`
2. `EXPLORE`
3. `DETECT_TRASH`
4. `APPROACH_TRASH`
5. `ALIGN_FOR_PICKUP`
6. `PICKUP`
7. `VERIFY_PICKUP`
8. `GO_TO_BIN`
9. `DROP_TRASH`
10. `RECOVERY`

구현:
- 단순 Python 노드로 먼저 FSM 작성
- 상태 전환 조건을 로그로 남기기
- timeout과 recovery 경로 넣기

완료 기준:
- 사람 개입 없이 한 번의 수거 사이클 수행

### Step 13. 실패 복구와 안전장치

직관:
실전에서는 성공 로직보다 실패 복구가 더 중요하다.

필수 복구 시나리오:

1. VSLAM tracking lost
2. Nav2 path planning 실패
3. 쓰레기 탐지 후 재검출 실패
4. 집기 실패
5. 센서 토픽 끊김

반드시 넣을 것:
- emergency stop
- battery low 처리
- sensor timeout
- stuck detection

## 8. 추천 ROS2 패키지 구조

```bash
~/autonomy_ws/src/
├── turtle_description
├── turtle_bringup
├── turtle_base
├── turtle_localization
├── turtle_slam
├── turtle_nav
├── turtle_perception
├── turtle_pickup
├── turtle_task
└── turtle_eval
```

### 패키지 역할

- `turtle_description`
  - URDF, TF, 센서 위치 정의
- `turtle_bringup`
  - 하드웨어 드라이버 launch
- `turtle_base`
  - 모터, encoder, `/cmd_vel`, `/odom`
- `turtle_localization`
  - IMU + encoder EKF
- `turtle_slam`
  - RTAB-Map 또는 다른 VSLAM
- `turtle_nav`
  - Nav2 설정
- `turtle_perception`
  - 쓰레기 탐지
- `turtle_pickup`
  - 그리퍼/흡입기 제어
- `turtle_task`
  - 상태기계
- `turtle_eval`
  - 로그, trajectory, 성능 측정

## 9. 권장 launch 구조

```bash
turtle_bringup/launch/
├── sensors.launch.py
├── base.launch.py
├── ekf.launch.py
├── slam.launch.py
├── nav.launch.py
└── full_system.launch.py
```

### 실행 순서 예시

```bash
cd ~/autonomy_ws
colcon build --symlink-install
source install/setup.bash

ros2 launch turtle_bringup base.launch.py
ros2 launch turtle_bringup sensors.launch.py
ros2 launch turtle_bringup ekf.launch.py
ros2 launch turtle_bringup slam.launch.py
ros2 launch turtle_bringup nav.launch.py
```

전체 통합 예시:

```bash
ros2 launch turtle_bringup full_system.launch.py
```

## 10. 8주 기준 추천 일정

### 1주차

- 로봇 수동주행 안정화
- TF tree 초안 완성
- encoder, IMU, camera 토픽 확인

산출물:
- 로봇 기본 주행 영상
- TF 스크린샷

### 2주차

- encoder odom 완성
- IMU 확인
- EKF 융합

산출물:
- `/odom`, `/odometry/filtered`

### 3주차

- RTAB-Map 또는 베이스라인 VSLAM 연결
- map 생성
- localization 테스트

산출물:
- 첫 맵
- rosbag

### 4주차

- Nav2 연결
- 목표점 주행
- costmap 튜닝

산출물:
- 자동 목표점 이동 데모

### 5주차

- 쓰레기 탐지
- depth 기반 3D 위치 추정

산출물:
- 쓰레기 좌표 출력

### 6주차

- 접근 행동
- yaw 정렬
- 집기 위치 보정

산출물:
- 접근 데모

### 7주차

- 집기 장치 제어
- 미션 FSM 통합

산출물:
- 1회 수거 사이클

### 8주차

- recovery
- 성능 측정
- 반복 실험

산출물:
- 최종 데모
- 평가표

## 11. 평가 기준

자율주행이 잘 되는지 볼 때는 아래를 같이 봐야 한다.

### VSLAM/주행 성능

- `ATE`
- `RPE`
- `FPS`
- `latency`
- `CPU/GPU 사용량`
- `memory`
- tracking lost 횟수
- relocalization 성공률

### 미션 성능

- 쓰레기 탐지 정확도
- 쓰레기 접근 성공률
- 집기 성공률
- 전체 수거 성공률
- 평균 미션 시간

## 12. 가장 먼저 확인해야 할 디버깅 우선순위

너처럼 처음 시작하는 경우, 문제가 생기면 아래 순서로 확인하는 게 가장 효율적이다.

1. `좌표계 정의`
2. `Calibration`
3. `Timestamp Sync`
4. `Encoder 방향과 바퀴 파라미터`
5. `IMU 축 방향`
6. `VSLAM tracking 상태`
7. `Outlier Rejection`
8. `Noise Model`
9. `Observability`
10. `Numerical Stability`

## 13. 지금 바로 해야 할 첫 액션

지금 당장 시작할 때는 아래 순서가 가장 좋다.

1. 로봇 센서 목록을 확정한다.
2. `base_link`, `camera_link`, `imu_link`, `gripper_link`를 정의한다.
3. 수동주행과 encoder odom부터 먼저 완성한다.
4. 그 다음 D435i 같은 RGB-D 카메라로 RTAB-Map을 붙인다.
5. map 생성과 localization이 되면 Nav2를 연결한다.
6. 마지막에 쓰레기 탐지와 집기 행동을 붙인다.

## 14. 추천하는 현실적인 개발 원칙

- 처음부터 모든 걸 동시에 붙이지 않는다.
- VSLAM은 먼저 `패키지로 성공`, 그 다음 `직접 구현`으로 간다.
- 센서 문제가 의심되면 알고리즘보다 `좌표계/보정/시간`을 먼저 본다.
- 실시간 디버깅만 하지 말고 항상 rosbag를 남긴다.
- 쓰레기 탐지와 주행은 분리해서 검증한다.
- 수거 실패 복구를 초기에 넣는다.

## 15. 참고 자료

- Nav2 Getting Started: https://docs.nav2.org/getting_started/index.html
- Nav2 Transform Setup: https://docs.nav2.org/setup_guides/transformation/setup_transforms.html
- Nav2 Concepts: https://docs.nav2.org/concepts/index.html
- Nav2 Mapping and Localization: https://docs.nav2.org/setup_guides/sensors/mapping_localization.html
- Nav2 Odometry Setup: https://docs.nav2.org/setup_guides/odom/setup_odom_gz.html
- RTAB-Map ROS2 launch 문서: https://docs.ros.org/en/ros2_packages/rolling/api/rtabmap_launch/index.html
- RealSense ROS Wrapper: https://github.com/realsenseai/realsense-ros
- robot_localization 패키지: https://index.ros.org/p/robot_localization/
