# D435i 기반 VSLAM 구현 A to Z 계획

## 0. 결론

- 가장 실용적인 시작점은 `D435i + ROS2 + RealSense ROS + RTAB-Map`으로 전체 파이프라인을 먼저 검증한 뒤, `RGB-D Visual Odometry`와 `Backend`를 직접 구현하는 방식이다.
- 처음부터 `카메라 + IMU`를 한 번에 묶은 `Visual-Inertial SLAM`으로 들어가지 않는 것을 추천한다. D435i에서는 좌표계, 보정, 시간 동기화, 노이즈 설정이 함께 꼬이면 디버깅 난도가 급격히 올라간다.
- 구현 순서는 `센서 bring-up -> 데이터 검증 -> 베이스라인 SLAM -> Frontend 직접 구현 -> Backend 최적화 -> Loop Closure -> 평가`가 가장 안전하다.

## 1. 선행 개념

- `좌표계(frame)`: 센서나 로봇의 위치와 방향을 표현하는 기준축이다.
- `Calibration(보정)`: 카메라 내부 파라미터와 센서 사이 위치 관계를 추정하는 과정이다.
- `Visual Odometry(VO)`: 연속된 영상만 보고 카메라의 상대 이동을 추정하는 기술이다.
- `Bundle Adjustment(번들 조정)`: 여러 프레임과 3D 점을 동시에 다시 맞춰 오차를 줄이는 최적화다.
- `Loop Closure(루프 클로저)`: 예전에 지나간 장소를 다시 인식해서 누적 오차를 줄이는 과정이다.

## 2. 왜 D435i에서는 RGB-D부터 시작하는가

직관:
단안 카메라(monocular)는 깊이를 직접 모르기 때문에 `scale` 문제, 즉 "얼마나 멀리 이동했는지"를 바로 알기 어렵다. D435i는 깊이(depth)를 같이 주기 때문에 시작 난도가 훨씬 낮다.

핵심 개념:
- `RGB-D`: 컬러 영상과 깊이 영상을 함께 사용한다.
- `IMU`: 가속도계와 자이로 센서다. 빠른 움직임에 강하지만 보정과 동기화가 중요하다.
- `Scale Drift`: 실제 거리 비율이 서서히 틀어지는 현상이다.

추천 전략:

| 방법 | 장점 | 단점 | 추천도 |
| --- | --- | --- | --- |
| RGB-D SLAM | 절대 스케일 확보가 쉽고 디버깅이 단순함 | 깊이 노이즈와 결측치 영향을 받음 | 가장 추천 |
| Monocular + IMU | 센서가 가볍고 연구 확장성이 좋음 | 초기화와 시간 동기화가 어려움 | 초반 비추천 |
| Stereo / Stereo-Inertial | 빠르고 강건할 수 있음 | D435i에서 IR 스테레오 활용 난도가 높음 | 중급 이후 |
| RGB-D + Backend 직접 구현 | 학습 효과가 큼 | 구현량이 많음 | 2단계 추천 |

## 3. 최종 목표 정의

이 문서에서는 아래 목표를 기준으로 계획한다.

- 실내 환경에서 D435i로 실시간 위치 추정
- 누적 지도를 저장하고 다시 불러오기
- 재방문 시 loop closure 수행
- 최종적으로 `ATE`, `RPE`, `FPS`, `latency`, `CPU/GPU 사용량`, `memory`로 평가

완료 기준:

1. 카메라와 IMU 토픽이 안정적으로 나온다.
2. RGB와 depth 정렬이 맞고 timestamp가 크게 흔들리지 않는다.
3. 베이스라인 SLAM이 끊기지 않고 map과 trajectory를 만든다.
4. 직접 구현한 VO가 최소한 짧은 시퀀스에서는 안정적으로 돈다.
5. Backend와 loop closure를 붙인 뒤 ATE/RPE가 개선된다.

## 4. 전체 로드맵

### Phase 0. 개발 환경 준비

직관:
센서가 잘 연결되고, ROS2에서 데이터가 안정적으로 보이기 전에는 알고리즘을 만져도 대부분 헛수고다.

핵심 개념:
- `ROS2`: 센서 데이터와 노드를 연결하는 미들웨어다.
- `RealSense ROS Wrapper`: D435i를 ROS2 토픽으로 내보내는 드라이버다.

구현 항목:
- Ubuntu + ROS2 환경 준비
- `realsense2_camera` 설치
- RViz2, rosbag2, rqt_graph 준비
- 테스트용 전용 workspace 생성

권장 환경:
- Ubuntu 22.04 + ROS2 Humble
- USB 3.x 포트 직접 연결
- 기록용 저장소와 실행용 workspace 분리

예시 workspace:

```bash
~/autonomy_ws/
└── src/
```

### Phase 1. D435i Bring-up

직관:
VSLAM은 "좋은 입력"이 절반이다. 카메라가 끊기거나 depth가 흔들리면 뒤 단계는 전부 무너진다.

핵심 개념:
- `aligned depth`: color 영상 좌표계에 맞춰 정렬된 depth다.
- `timestamp sync`: color/depth/imu의 시간 기준이 서로 맞는지 확인하는 과정이다.

구현 항목:
- color, depth, IMU 토픽 확인
- depth를 color에 정렬
- 프레임 이름과 TF tree 확인
- rosbag 기록 가능 여부 확인

공식 RealSense ROS 예시 명령:

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_rgbd:=true \
  enable_sync:=true \
  align_depth.enable:=true \
  enable_color:=true \
  enable_depth:=true \
  enable_gyro:=true \
  enable_accel:=true
```

확인할 것:
- `ros2 topic list`에 color/depth/imu 토픽이 모두 보이는지
- `ros2 topic hz`로 프레임 드롭이 심하지 않은지
- `rviz2`에서 color와 aligned depth가 같은 물체 경계를 대략 따라가는지
- `tf2_tools` 또는 RViz2 TF 표시로 프레임 구조가 이상하지 않은지

실패 신호:
- depth가 color와 어긋남
- IMU는 나오는데 방향이 뒤집혀 보임
- 움직이지 않아도 pose가 미끄러짐
- 카메라 시작 후 토픽 이름이 예상과 다름

### Phase 2. 데이터 검증과 기록

직관:
실시간에서 바로 디버깅하면 원인을 놓치기 쉽다. rosbag를 남겨야 같은 문제를 반복 재현할 수 있다.

핵심 개념:
- `rosbag2`: ROS2 토픽을 파일로 기록하는 도구다.
- `재현성`: 같은 입력으로 같은 문제를 다시 확인할 수 있는 성질이다.

구현 항목:
- 짧은 실내 주행 bag 기록
- 정지 상태 bag 기록
- 빠른 회전, 느린 이동, 조명 변화, 텍스처 부족 구간 포함
- bag 재생 시에도 동일한 결과가 나오는지 확인

권장 bag 시나리오:

1. 정지 10초
2. 천천히 전진 5m
3. 좌우 회전
4. 출발 지점 복귀
5. 조명 어두운 구간 통과

우선 체크할 디버깅 항목:
- color/depth timestamp 차이
- IMU timestamp 불연속
- depth 결측치 비율
- 반사면, 유리, 햇빛에서 depth 붕괴 여부

### Phase 3. 베이스라인 SLAM 구축

직관:
직접 구현 전에 이미 검증된 시스템으로 센서와 환경 자체가 SLAM 가능한지 먼저 확인해야 한다.

핵심 개념:
- `Baseline`: 비교 기준이 되는 기본 시스템이다.
- `RTAB-Map`: RGB-D, lidar, stereo 등을 지원하는 ROS 친화적 SLAM 패키지다.

추천:
- 첫 번째 베이스라인은 `RTAB-Map RGB-D`
- 두 번째 비교 후보는 `ORB-SLAM3 RGB-D`

이유:
- RTAB-Map은 ROS2 연동이 쉬워 전체 파이프라인 점검에 좋다.
- ORB-SLAM3는 연구/성능 기준선으로 좋지만 ROS2 통합과 빌드 난도가 더 높을 수 있다.

RTAB-Map 적용 순서:

1. D435i 토픽 이름 확인
2. `rgb_topic`, `depth_topic`, `camera_info_topic` 연결
3. mapping 모드로 짧은 시퀀스 실행
4. 같은 공간을 다시 돌며 loop closure 발생 여부 확인
5. DB 저장과 재로컬라이제이션 확인

주의:
아래 RTAB-Map launch 형태는 RealSense ROS 토픽 구조와 RTAB-Map 공식 README를 바탕으로 구성한 예시다. 실제 토픽 이름은 반드시 `ros2 topic list`로 다시 확인해야 한다.

```bash
ros2 launch rtabmap_launch rtabmap.launch.py \
  rgb_topic:=/camera/camera/color/image_raw \
  depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/camera/color/camera_info \
  frame_id:=camera_link \
  approx_sync:=false \
  rviz:=true
```

베이스라인 완료 기준:
- 실내 한 바퀴 경로에서 map이 대체로 닫힌다.
- pose jump가 자주 일어나지 않는다.
- 재실행해도 결과가 완전히 랜덤하지 않다.

### Phase 4. 직접 구현 1단계: RGB-D Frontend

직관:
Frontend는 "지금 프레임에서 어디로 움직였는지"를 빠르게 계산하는 앞단이다.

핵심 개념:
- `Feature`: 프레임마다 반복해서 찾기 쉬운 점이다.
- `Tracking`: 이전 프레임의 feature를 다음 프레임에서 따라가는 과정이다.
- `Outlier Rejection`: 잘못된 대응점을 버리는 과정이다.

구현 항목:
- color image 입력
- feature 검출: ORB 또는 FAST + BRIEF
- feature matching 또는 optical flow
- depth association으로 2D-3D 또는 3D-3D 대응 생성
- `PnP + RANSAC` 또는 ICP 계열로 상대 pose 계산

추천 순서:

1. ORB feature 검출
2. descriptor matching
3. depth가 유효한 keypoint만 사용
4. `solvePnPRansac`으로 pose 계산
5. inlier 수, reprojection error 기반 품질 판정

필수 로그:
- 추적된 feature 수
- PnP inlier 수
- 평균 reprojection error
- depth valid ratio
- keyframe 삽입 여부

실패 원인 가설:
- depth가 color와 정렬되지 않음
- texture가 부족해 feature 수가 적음
- motion blur로 matching 실패
- RANSAC threshold가 너무 크거나 작음

### Phase 5. 직접 구현 2단계: Keyframe와 Map Point 관리

직관:
모든 프레임을 다 최적화하면 너무 느리다. 중요한 프레임만 keyframe으로 남겨야 한다.

핵심 개념:
- `Keyframe`: 지도를 유지하는 기준 프레임이다.
- `Map Point`: 여러 프레임에서 관측된 3D 점이다.

구현 항목:
- keyframe 삽입 조건 정의
- map point 생성과 가시성 관리
- 오래 추적 실패한 point 제거
- 시야각과 depth 범위를 이용한 품질 필터링

추천 keyframe 조건 예시:
- 추적 inlier 수가 일정 비율 이하로 감소
- 이동 거리 또는 회전량이 임계값 이상
- 현재 프레임이 기존 keyframe과 시야 차이가 큼

### Phase 6. 직접 구현 3단계: Backend 최적화

직관:
Frontend만으로는 오차가 계속 쌓인다. Backend는 여러 프레임을 함께 다시 맞춰 누적 오차를 줄인다.

핵심 개념:
- `Nonlinear Optimization(비선형 최적화)`: 오차가 가장 작아지도록 pose와 point를 반복적으로 조정하는 방법이다.
- `Noise Model(노이즈 모델)`: 센서 오차를 수학적으로 어떤 크기로 볼지 정하는 규칙이다.
- `Numerical Stability(수치 안정성)`: 계산 중 행렬이 불안정해져 결과가 튀지 않게 하는 성질이다.

추천 구현:
- 첫 단계: sliding window local BA
- 라이브러리: `Ceres` 또는 `g2o`
- 변수: recent keyframe poses + visible map points
- 비용함수: reprojection error

반드시 확인할 것:
- Jacobian 폭주 여부
- Huber loss 같은 강건 커널 적용 여부
- depth가 너무 가까운 점, 너무 먼 점 제거
- 관측 수가 적은 map point 제거

디버깅 우선순위:
- 좌표계 부호 반전
- pose update 순서 오류
- 단위 불일치(m, mm 혼용)
- 초기값이 너무 나빠 optimizer 발산

### Phase 7. Loop Closure와 Pose Graph

직관:
한 바퀴 돌아 시작점으로 와도 누적 오차 때문에 지도가 벌어진다. loop closure는 이 벌어짐을 다시 묶는 과정이다.

핵심 개념:
- `Place Recognition`: 예전에 본 장소인지 찾는 단계다.
- `Pose Graph`: keyframe들을 노드로 보고 상대 관계를 연결한 그래프다.

구현 항목:
- BoW 또는 image retrieval 기반 후보 검색
- 기하 검증으로 거짓 loop 제거
- pose graph optimization 수행
- loop 후 local map 갱신

권장 순서:

1. DBoW2 류 place recognition 적용
2. 후보 keyframe 검색
3. feature re-match 및 기하 검증
4. loop edge 추가
5. pose graph optimize

성공 기준:
- 왕복 경로에서 trajectory 끝점이 시작점 근처로 수렴
- map이 갑자기 뒤집히지 않음

### Phase 8. Relocalization과 Map 재사용

직관:
추적이 끊겨도 이미 만들어둔 지도에서 다시 위치를 찾을 수 있어야 실사용성이 높아진다.

핵심 개념:
- `Relocalization`: tracking을 잃었을 때 기존 map에서 현재 위치를 다시 찾는 과정이다.

구현 항목:
- tracking lost 상태 정의
- place recognition으로 후보 keyframe 찾기
- PnP 재초기화
- 성공 시 local map 재연결

### Phase 9. IMU 통합은 마지막에 추가

직관:
IMU는 빠른 회전과 짧은 순간 움직임에 강하지만, 잘못 붙이면 오히려 pose가 더 흔들린다.

핵심 개념:
- `Preintegration`: IMU 데이터를 프레임 사이 구간별로 누적해 사용하는 기법이다.
- `Bias`: IMU 센서가 항상 조금씩 틀리게 측정하는 오프셋이다.
- `Observability`: 현재 데이터만으로 어떤 상태를 구분할 수 있는지 여부다.

IMU를 나중에 붙이는 이유:
- color/depth만으로도 기본 SLAM 파이프라인 검증 가능
- IMU 문제는 calibration, 시간 동기화, bias 추정이 같이 필요
- 초기화 실패 시 원인이 카메라인지 IMU인지 분리하기 어려움

IMU 통합 체크리스트:
- 카메라와 IMU frame 정의 문서화
- IMU noise density, random walk 설정
- gyro/accel bias 초기화
- 정지 상태에서 gravity 방향 일관성 확인
- 카메라 timestamp와 IMU timestamp offset 측정

### Phase 10. 평가와 벤치마크

직관:
눈으로 "대충 잘 되는 것 같다"는 절대 기준이 아니다. 숫자로 평가해야 한다.

핵심 개념:
- `ATE`: 전체 궤적이 GT와 얼마나 떨어지는지 보는 오차다.
- `RPE`: 인접 구간 상대 이동이 얼마나 틀리는지 보는 오차다.
- `Latency`: 입력부터 pose 출력까지 걸리는 시간이다.

평가 항목:
- `ATE`
- `RPE`
- `FPS`
- `latency`
- `CPU/GPU usage`
- `memory`
- tracking lost 횟수
- loop closure 성공 횟수

테스트 시나리오:

1. 실내 복도
2. 책상/의자 많은 실내
3. 텍스처 적은 벽면 위주 구간
4. 빠른 회전 포함 구간
5. 조명 변화 구간

권장 기록 형식:

| 실험명 | 센서 설정 | 평균 FPS | 평균 latency | ATE | RPE | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| baseline_rtabmap_room1 | 640x480@30 | - | - | - | - | 초기 기준 |
| rgbd_vo_v1 | 640x480@30 | - | - | - | - | depth filtering 없음 |

## 5. ROS2 패키지 구조 추천

실행용 workspace는 기록용 저장소와 분리하는 것을 추천한다.

```bash
~/autonomy_ws/src/
├── realsense-ros
├── d435i_slam_bringup
├── d435i_vo
├── d435i_backend
├── d435i_loop
└── d435i_eval
```

노드 구성 예시:

- `d435i_slam_bringup`
  - 역할: RealSense launch, TF, 파라미터 로딩
- `d435i_vo`
  - 역할: feature extraction, matching, PnP, keyframe 선택
- `d435i_backend`
  - 역할: local BA, map point 관리
- `d435i_loop`
  - 역할: place recognition, loop edge 추가, graph optimization
- `d435i_eval`
  - 역할: trajectory 저장, ATE/RPE 계산, 성능 로그 정리

launch 파일 예시:

```bash
~/autonomy_ws/src/d435i_slam_bringup/
├── launch/
│   ├── d435i_camera.launch.py
│   ├── d435i_rtabmap.launch.py
│   └── d435i_full_slam.launch.py
└── config/
    ├── realsense.yaml
    ├── vo.yaml
    ├── backend.yaml
    └── loop.yaml
```

## 6. 구현 순서 추천

가장 실용적인 개발 순서는 아래와 같다.

1. D435i raw data 정상 출력
2. aligned depth와 color 정합 확인
3. rosbag 기록/재생 검증
4. RTAB-Map baseline 성공
5. RGB-D VO 최소 구현
6. keyframe/map point 관리
7. local BA 추가
8. loop closure 추가
9. relocalization 추가
10. IMU preintegration 추가
11. 정량 평가와 튜닝

## 7. 주차별 계획 예시

### 1주차

- D435i 드라이버 설치
- 토픽 구조 확인
- rosbag 기록
- 기본 TF 구조 정리

산출물:
- 센서 연결 문서
- 토픽 목록
- 첫 bag 파일

### 2주차

- RTAB-Map baseline 실행
- mapping / localization 실험
- 성능 병목 확인

산출물:
- baseline trajectory
- map DB
- 실패 로그

### 3주차

- ORB feature 기반 frontend 구현
- depth association
- PnP + RANSAC pose 추정

산출물:
- 프레임 간 상대 pose
- feature/inlier 로그

### 4주차

- keyframe 삽입
- map point 생성/삭제
- 짧은 구간 누적 추정

산출물:
- keyframe 시각화
- local map

### 5주차

- local BA 구현
- robust kernel 적용
- 잘못된 point pruning

산출물:
- BA 전후 오차 비교

### 6주차

- loop 후보 탐색
- pose graph 최적화
- 재방문 시나리오 실험

산출물:
- loop closure 성공 사례
- graph optimize 결과

### 7주차

- relocalization
- tracking loss recovery
- 파라미터 튜닝

산출물:
- 재초기화 성공률

### 8주차

- IMU 통합 또는 성능 최적화
- 최종 ATE/RPE/FPS 측정
- 문서화

산출물:
- 최종 보고서
- 성능 표

## 8. 가장 먼저 확인해야 할 디버깅 체크리스트

우선순위 순서대로 본다.

1. `좌표계 정의`
   - `camera_link`, optical frame, imu frame의 축 방향이 문서와 실제가 맞는가
2. `Calibration`
   - camera intrinsics, depth-to-color 정렬, camera-imu extrinsic이 신뢰 가능한가
3. `Timestamp Sync`
   - color, depth, imu timestamp 차이가 누적되지 않는가
4. `Outlier Rejection`
   - RANSAC inlier 수가 갑자기 급락하는가
5. `Noise Model`
   - optimizer에서 depth와 IMU 오차를 과신하고 있지 않은가
6. `Observability`
   - 정지 상태, 텍스처 부족, 순수 회전 구간에서 추정이 불안정하지 않은가
7. `Numerical Stability`
   - Hessian이 불안정하거나 pose가 발산하지 않는가

## 9. 지금 바로 해야 할 첫 액션

실무적으로는 아래 순서로 시작하면 된다.

1. D435i를 ROS2에서 띄운다.
2. color/depth/imu 토픽과 TF를 캡처한다.
3. 1분짜리 실내 rosbag를 기록한다.
4. RTAB-Map baseline으로 해당 bag를 돌려본다.
5. baseline이 안정적이면 그 다음에 RGB-D VO를 직접 구현한다.

## 10. 참고 자료

- RealSense ROS 공식 저장소: https://github.com/realsenseai/realsense-ros
- RTAB-Map ROS2 launch README: https://github.com/introlab/rtabmap_ros/tree/ros2/rtabmap_launch
- ORB-SLAM3 공식 저장소: https://github.com/UZ-SLAMLab/ORB_SLAM3
- D435i 제품 페이지: https://www.realsenseai.com/products/depth-camera-d435i/
