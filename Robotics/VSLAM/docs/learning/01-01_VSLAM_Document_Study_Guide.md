# VSLAM Document Study Guide

## 결론

이 문서는 현재 `Robotics/VSLAM` 안에 있는 VSLAM 관련 문서를 교과서처럼 읽기 위한 학습서다.
목표는 코드 구현 기록이나 작업 회고를 정리하는 것이 아니라, VSLAM을 이해하기 위해 어떤 개념을 어떤 순서로 봐야 하는지 잡는 것이다.

지금 집중할 범위는 아래 네 가지다.

```text
1. D435i RGB-D 입력을 이해한다.
2. RTAB-Map baseline이 왜 필요한지 이해한다.
3. VSLAM 내부 구조인 Frontend, Backend, Loop Closure, Evaluation을 이해한다.
4. 디버깅할 때 좌표계, 보정, 시간 동기화, 노이즈를 먼저 확인하는 습관을 만든다.
```

지금은 시뮬레이션, 로봇 모델, 자율주행 패키지 구조는 부가 주제로 둔다.
VSLAM 문서 안의 개념을 먼저 잡는 것이 우선이다.

## 1. 먼저 읽을 문서

현재 VSLAM 학습의 중심 문서는 아래 순서로 읽는다.

| 순서 | 문서 | 읽는 목적 |
| --- | --- | --- |
| 1 | [`docs/progress/D435i_VSLAM_A_to_Z_Plan.md`](../progress/D435i_VSLAM_A_to_Z_Plan.md) | VSLAM 전체 로드맵을 잡는다. |
| 2 | [`docs/learning/02-01_D435i_RTABMap_VSLAM_Manual.md`](./02-01_D435i_RTABMap_VSLAM_Manual.md) | D435i RGB-D와 RTAB-Map baseline 흐름을 이해한다. |
| 3 | [`docs/learning/02-02_How_realsense2_camera_converts_D435i_to_ROS2_Topics.md`](./02-02_How_realsense2_camera_converts_D435i_to_ROS2_Topics.md) | 실제 카메라 데이터가 ROS2 topic으로 바뀌는 과정을 이해한다. |
| 4 | [`docs/learning/02-03_D435i_IMU_Topics_and_Enable_Guide.md`](./02-03_D435i_IMU_Topics_and_Enable_Guide.md) | IMU를 언제 켜고 왜 처음에는 끄는지 이해한다. |
| 5 | [`docs/learning/02-04_D435i_IMU_Axis_Interpretation.md`](./02-04_D435i_IMU_Axis_Interpretation.md) | IMU 축과 회전 방향을 헷갈리지 않게 잡는다. |
| 6 | [`docs/learning/02-05_D435i_Odometry_Accuracy_Comparison.md`](./02-05_D435i_Odometry_Accuracy_Comparison.md) | 카메라, IMU, wheel encoder 조합의 odom 차이를 비교한다. |
| 7 | [`docs/progress/RTABMap_Tuning_Experiment_Plan.md`](../progress/RTABMap_Tuning_Experiment_Plan.md) | RTAB-Map 결과를 어떻게 비교할지 기준을 잡는다. |
| 8 | [`D435i_RealTime_Troubleshooting_History.md`](../troubleshooting/D435i_RealTime_Troubleshooting_History.md), [`D435i_RealSense_Viewer_Triage_Checklist.md`](../troubleshooting/D435i_RealSense_Viewer_Triage_Checklist.md), [`Why_RealSense_Viewer_Looks_RealTime_But_RTABMap_Does_Not.md`](../troubleshooting/Why_RealSense_Viewer_Looks_RealTime_But_RTABMap_Does_Not.md) | D435i/RTAB-Map이 실시간으로 안 될 때 원인을 분리한다. |

용어가 막히면 [`docs/learning/01-02_VSLAM_Terms_Level1_Guide.md`](./01-02_VSLAM_Terms_Level1_Guide.md)를 함께 본다.
이 문서는 각 용어를 한 줄 정의에서 끝내지 않고, 왜 중요한지와 처음 확인할 항목까지 정리한다.

## 2. VSLAM을 한 문장으로 이해하기

VSLAM은 카메라 영상으로 로봇 또는 카메라가 어디로 움직였는지 추정하면서, 동시에 주변 지도를 만드는 기술이다.

조금 더 풀면 아래 흐름이다.

```text
카메라 입력
-> 프레임 사이 움직임 추정
-> 여러 움직임을 이어 붙여 trajectory 생성
-> 주변 3D/2D map 생성
-> 예전에 본 장소를 다시 보면 누적 오차 보정
```

여기서 자주 나오는 용어는 아래처럼 잡으면 된다.

- `Frame`: 카메라가 한 번 찍은 이미지 한 장이다.
- `Feature`: 이미지 안에서 다시 찾기 쉬운 점이다.
- `Visual Odometry`: 연속된 이미지로 카메라 이동량을 추정하는 과정이다.
- `Map`: feature, 3D 점, occupancy grid처럼 주변 환경을 저장한 결과다.
- `Loop Closure`: 예전에 지나간 장소를 다시 알아보고 누적 오차를 줄이는 과정이다.
- `Relocalization`: 현재 위치를 잃었을 때 이미 만든 map 안에서 다시 위치를 찾는 과정이다.

## 3. D435i RGB-D부터 시작하는 이유

D435i는 color image와 depth image를 함께 제공한다.
`RGB-D`는 RGB 색상 영상과 Depth 깊이 영상을 같이 쓰는 방식이다.

처음 VSLAM을 배울 때 RGB-D가 유리한 이유는 scale 문제를 줄여주기 때문이다.
`Scale`은 지도와 이동 거리의 실제 크기 비율이다.
단안 카메라만 쓰면 "앞으로 움직인 것"은 알 수 있어도 "몇 m 움직였는지"를 바로 알기 어렵다.
반면 RGB-D는 각 픽셀의 깊이를 알 수 있으므로, 처음 학습과 디버깅이 훨씬 단순하다.

현재 문서에서 권장하는 시작점은 아래다.

```text
D435i color image
D435i aligned depth image
D435i camera_info
-> RTAB-Map RGB-D baseline
```

처음부터 IMU, wheel encoder, GPS를 모두 붙이지 않는다.
센서가 많아질수록 문제가 생겼을 때 원인이 좌표계인지, 시간 동기화인지, 노이즈인지 분리하기 어려워진다.

## 4. D435i에서 반드시 확인할 입력

VSLAM은 입력이 나쁘면 뒤쪽 알고리즘을 아무리 고쳐도 안정화되지 않는다.
그래서 첫 단계는 알고리즘이 아니라 입력 검증이다.

필수 입력:

```text
color image
aligned depth image
camera_info
TF frame
timestamp
```

각 입력의 의미:

| 입력 | 의미 | 실패하면 생기는 문제 |
| --- | --- | --- |
| `color image` | feature와 장면 인식에 쓰는 컬러 영상 | feature tracking 실패 |
| `aligned depth image` | color 좌표에 맞춘 깊이 영상 | 3D 위치 계산 오류 |
| `camera_info` | 초점거리, 중심점 같은 카메라 내부 파라미터 | PnP, 3D 복원 오류 |
| `TF frame` | 센서와 로봇 좌표계 관계 | map이 돌아가거나 뒤집힘 |
| `timestamp` | 데이터가 찍힌 시간 | color/depth/IMU가 서로 어긋남 |

가장 먼저 볼 증상:

- color와 depth 경계가 서로 맞는가
- topic rate가 갑자기 떨어지지 않는가
- timestamp가 불연속으로 튀지 않는가
- 정지 상태에서 odom이 계속 미끄러지지 않는가
- TF tree가 끊기지 않는가

## 5. RTAB-Map baseline의 역할

`Baseline`은 내가 만든 구현과 비교하기 위한 기준 시스템이다.
RTAB-Map은 ROS2에서 RGB-D SLAM을 빠르게 실행해볼 수 있는 대표적인 baseline이다.

RTAB-Map을 쓰는 목적은 "RTAB-Map 자체를 최종 목표로 삼기 위해서"만이 아니다.
더 중요한 목적은 현재 입력과 환경이 SLAM 가능한 상태인지 먼저 확인하는 것이다.

RTAB-Map baseline이 통과해야 직접 구현으로 넘어갈 수 있다.

```text
D435i 입력 정상
-> RTAB-Map odometry 생성
-> mapData / cloud_map 생성
-> trajectory가 크게 튀지 않음
-> 같은 장소 재방문 시 loop closure 후보 발생
```

확인할 topic:

```text
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
/rtabmap/odom
/rtabmap/mapData
/rtabmap/cloud_map
/rtabmap/map
```

RTAB-Map 결과를 볼 때 중요한 기준:

- FPS: color/depth가 목표 주기로 들어오는가
- latency: 화면과 처리가 심하게 늦지 않는가
- odom quality: odometry가 자주 끊기지 않는가
- map quality: point cloud가 찢어지거나 회전하지 않는가
- loop closure: 같은 장소를 다시 봤을 때 누적 오차가 줄어드는가

## 6. VSLAM 내부 구조

VSLAM은 크게 네 덩어리로 나누면 이해하기 쉽다.

```text
Frontend
-> Backend
-> Loop Closure
-> Evaluation
```

### Frontend

`Frontend`는 새 이미지가 들어올 때마다 현재 움직임을 빠르게 추정하는 앞단이다.

주요 작업:

```text
feature extraction
feature tracking / matching
depth association
outlier rejection
relative pose estimation
```

초보자 관점에서 Frontend는 "이번 프레임이 직전 프레임보다 얼마나 움직였는가"를 계산하는 부분이다.

RGB-D Frontend의 기본 흐름:

```text
color image에서 feature를 찾는다.
다음 frame에서 같은 feature를 찾는다.
depth image로 feature의 3D 위치를 얻는다.
PnP + RANSAC으로 카메라 이동을 계산한다.
inlier 수와 reprojection error로 결과 품질을 판단한다.
```

용어:

- `ORB`: 빠르게 찾고 비교할 수 있는 feature 방식이다.
- `PnP`: 3D 점과 2D 이미지 점 대응으로 카메라 pose를 구하는 방법이다.
- `RANSAC`: 틀린 대응점을 버리면서 그럴듯한 모델을 찾는 방법이다.
- `Inlier`: 추정한 pose와 잘 맞는 정상 대응점이다.
- `Reprojection error`: 3D 점을 다시 이미지에 찍었을 때 실제 feature와 얼마나 떨어지는지다.

Frontend에서 남겨야 할 로그:

```text
detected feature count
matched feature count
valid depth feature count
RANSAC inlier count
reprojection error
estimated translation / rotation
processing time
```

### Backend

`Backend`는 여러 프레임의 pose와 map point를 전체적으로 다시 맞춰 오차를 줄이는 뒷단이다.

Frontend는 빠르지만 짧은 구간 기준으로만 판단한다.
작은 오차가 계속 쌓이면 trajectory가 점점 틀어진다.
Backend는 이 누적 오차를 줄이는 역할을 한다.

주요 개념:

- `Bundle Adjustment`: 카메라 pose와 3D point를 함께 최적화해 reprojection error를 줄인다.
- `Pose Graph`: 각 keyframe pose를 노드로 두고, pose 사이 관계를 edge로 둔 그래프다.
- `Noise Model`: 각 측정값을 얼마나 믿을지 정하는 모델이다.

초보자 관점에서 Backend는 "지금까지 지나온 경로 전체를 다시 정리하는 단계"다.

### Loop Closure

`Loop Closure`는 예전에 본 장소를 다시 알아보는 기능이다.

VSLAM은 계속 이동하면 작은 오차가 누적된다.
하지만 출발점 근처로 돌아왔을 때 "여기 전에 봤던 곳이다"라고 알 수 있으면, 전체 trajectory를 다시 당겨 맞출 수 있다.

Loop Closure에서 확인할 것:

```text
장소 인식 후보가 생기는가
잘못된 loop가 너무 많이 생기지 않는가
loop 후 map이 갑자기 찢어지지 않는가
pose graph가 안정적으로 보정되는가
```

### Evaluation

`Evaluation`은 결과가 좋아졌는지 숫자로 판단하는 단계다.

주요 지표:

- `ATE`: 전체 trajectory가 정답 경로와 얼마나 다른지 보는 지표다.
- `RPE`: 짧은 구간의 상대 이동 오차를 보는 지표다.
- `FPS`: 초당 처리 프레임 수다.
- `Latency`: 입력부터 결과까지 걸리는 지연 시간이다.
- `CPU/GPU 사용량`: 실시간 동작 가능성을 보는 자원 지표다.
- `Memory`: 장시간 실행 시 누적 메모리 문제가 있는지 보는 지표다.

## 7. 직접 구현으로 넘어가는 순서

문서 기준으로 가장 안전한 구현 순서는 아래다.

```text
1. D435i 입력 검증
2. rosbag 기록과 재생
3. RTAB-Map baseline 검증
4. RGB-D Frontend 직접 구현
5. 짧은 시퀀스 Visual Odometry 확인
6. Backend 최적화 추가
7. Loop Closure 추가
8. ATE/RPE/FPS/latency로 평가
```

이 순서를 지키는 이유는 원인 분리를 쉽게 하기 위해서다.

예를 들어 직접 구현한 VO가 실패했을 때, RTAB-Map baseline도 실패한다면 입력 문제일 가능성이 크다.
반대로 RTAB-Map baseline은 정상인데 직접 구현만 실패한다면 feature tracking, PnP, outlier rejection 문제로 좁힐 수 있다.

## 8. VSLAM 디버깅 우선순위

VSLAM 문제는 겉으로는 모두 "map이 이상하다"처럼 보일 수 있다.
하지만 원인은 매우 다를 수 있으므로 아래 순서로 본다.

### 1. 좌표계

좌표계는 위치와 방향을 표현하는 기준축이다.

확인할 것:

- camera frame이 올바른가
- optical frame과 body frame을 혼동하지 않았는가
- `map`, `odom`, `base_link`, `camera_link` 관계가 이어지는가
- x/y/z축 방향이 실제 움직임과 맞는가

### 2. Calibration

Calibration은 센서의 내부값과 센서 사이 위치 관계를 맞추는 과정이다.

확인할 것:

- color와 depth가 정렬되어 있는가
- camera_info가 실제 해상도와 맞는가
- IMU나 외부 센서의 장착 방향이 문서와 맞는가
- 센서 위치 offset을 무시하고 있지 않은가

### 3. Timestamp Sync

Timestamp sync는 서로 다른 센서 데이터의 시간 기준을 맞추는 것이다.

확인할 것:

- color/depth timestamp 차이가 크지 않은가
- IMU timestamp가 불연속으로 튀지 않는가
- ROS2 topic queue가 너무 작거나 너무 크지 않은가
- approximate sync를 쓸 때 허용 시간이 과하게 넓지 않은가

### 4. Scale Drift

Scale drift는 시간이 지날수록 이동 거리 비율이 틀어지는 현상이다.

RGB-D에서는 depth가 있으므로 단안보다 덜하지만, depth noise와 잘못된 camera_info가 있으면 여전히 문제가 생긴다.

확인할 것:

- 실제 1m 이동이 map에서도 대략 1m로 보이는가
- 회전 후 같은 장소가 어긋나지 않는가
- depth 단위가 m인지 mm인지 혼동하지 않았는가

### 5. Outlier Rejection

Outlier rejection은 잘못된 대응점이나 이상한 센서값을 버리는 과정이다.

확인할 것:

- feature match 중 틀린 대응점이 많지 않은가
- RANSAC inlier 비율이 너무 낮지 않은가
- 반사면, 유리, 사람 움직임 때문에 depth가 튀지 않는가
- 한 번의 잘못된 pose가 trajectory 전체를 망가뜨리지 않는가

### 6. Noise Model

Noise model은 각 측정값을 얼마나 믿을지 정하는 방식이다.

확인할 것:

- covariance를 너무 작게 줘서 센서를 과신하지 않는가
- IMU yaw, wheel odom, visual odom이 서로 충돌하지 않는가
- 실제로 불안정한 센서를 안정적이라고 가정하지 않았는가

### 7. Observability

Observability는 필터나 최적화가 어떤 상태를 실제 센서로 구분해낼 수 있는지를 뜻한다.

확인할 것:

- yaw를 직접 관측할 센서가 있는가
- 깊이가 없는 feature만으로 scale을 추정하려고 하지 않는가
- 정지 상태와 저속 이동에서 필요한 상태가 충분히 드러나는가

### 8. Numerical Stability

Numerical stability는 계산이 작은 오차에도 폭발하지 않고 안정적으로 유지되는 성질이다.

확인할 것:

- 행렬 계산에서 조건이 나쁜 경우를 처리하는가
- depth가 0이거나 NaN일 때 제거하는가
- 너무 적은 feature로 pose를 추정하지 않는가
- 최적화 반복이 발산하지 않는가

## 9. 문서를 읽으며 만들어야 할 개인 요약

각 문서를 읽을 때 아래 네 줄을 남기면 된다.

```text
이 문서의 핵심 입력:
이 문서의 핵심 출력:
이 문서가 막으려는 대표 문제:
내가 다음에 확인해야 할 명령 또는 로그:
```

예시:

- 문서: [02-01_D435i_RTABMap_VSLAM_Manual.md](./02-01_D435i_RTABMap_VSLAM_Manual.md)
- 핵심 입력: color image, aligned depth image, camera_info
- 핵심 출력: /rtabmap/odom, /rtabmap/mapData, /rtabmap/cloud_map
- 대표 문제: IMU를 너무 빨리 붙여 원인 분리가 어려워지는 문제
- 다음 확인: ros2 topic hz color/depth/rtabmap odom

## 10. 지금 단계의 학습 목표

지금은 직접 VSLAM 코드를 크게 작성하기보다, 아래 질문에 답할 수 있으면 된다.

1. 왜 D435i에서는 RGB-D baseline부터 시작하는가?
2. RTAB-Map baseline이 통과했다는 말은 어떤 topic과 화면으로 확인하는가?
3. Frontend와 Backend의 역할은 어떻게 다른가?
4. Loop Closure는 왜 누적 오차를 줄일 수 있는가?
5. VSLAM이 실패했을 때 왜 좌표계, calibration, timestamp를 먼저 봐야 하는가?
6. 성능을 FPS만 보지 않고 latency, ATE, RPE, CPU/GPU, memory로 나눠 봐야 하는 이유는 무엇인가?

이 질문에 답할 수 있으면, 그 다음에 코드 구조나 통합 실행 문서를 읽는 것이 훨씬 쉬워진다.
