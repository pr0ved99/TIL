# VSLAM Terms Level 1 Guide

## 결론

이 문서는 VSLAM 학습 자료에 나오는 용어를 한 줄 정의에서 끝내지 않고, 한 단계 더 깊게 이해하기 위한 자료다.
목표는 논문 수준의 수학을 바로 들어가는 것이 아니라, 문서를 읽을 때 "이 용어가 왜 중요하고, 실제 디버깅에서는 무엇을 확인해야 하는지"를 잡는 것이다.

추천 사용법:

1. [01-01_VSLAM_Document_Study_Guide.md](./01-01_VSLAM_Document_Study_Guide.md)를 먼저 읽는다.
2. 모르는 용어가 나오면 이 문서에서 해당 용어를 찾는다.
3. 각 용어의 "처음 확인할 것"을 실제 topic, log, 화면과 연결한다.
4. 나중에 직접 구현할 때는 Frontend -> Backend -> Loop Closure 순서로 다시 읽는다.

## 1. 입력과 센서 용어

### Frame

한 줄 정의:
`Frame`은 카메라가 한 번 찍은 이미지 한 장이다.

왜 중요한가:
VSLAM은 frame 사이의 변화로 움직임을 추정한다.
즉, 한 장의 이미지만 보는 것이 아니라 `이전 frame -> 현재 frame` 사이에서 feature가 어떻게 이동했는지 본다.

처음 확인할 것:

- 이미지 topic이 계속 들어오는가
- frame rate가 갑자기 떨어지지 않는가
- 너무 흔들리거나 blur가 심하지 않은가

흔한 오해:
좋은 카메라 한 장이 있으면 VSLAM이 되는 것이 아니다.
VSLAM은 시간 순서대로 들어오는 frame 흐름이 안정적이어야 한다.

### RGB-D

한 줄 정의:
`RGB-D`는 색상 영상과 깊이 영상을 함께 쓰는 방식이다.

왜 중요한가:
RGB만 있으면 이미지에서 점의 위치는 알 수 있지만, 그 점이 실제로 얼마나 멀리 있는지 바로 알기 어렵다.
Depth가 있으면 이미지의 한 점을 3D 위치로 바꿀 수 있어 초보 단계의 VSLAM 구현과 디버깅이 쉬워진다.

처음 확인할 것:

- color image topic이 들어오는가
- aligned depth image topic이 들어오는가
- color와 depth 경계가 대략 맞는가
- depth 값의 단위가 m인지 mm인지 알고 있는가

흔한 오해:
Depth가 있으면 scale 문제가 완전히 사라진다고 생각하기 쉽다.
실제로는 depth noise, 결측치, 잘못된 camera_info 때문에 scale 문제가 다시 생길 수 있다.

### Depth Image

한 줄 정의:
`Depth image`는 각 픽셀이 카메라에서 얼마나 떨어져 있는지 담은 이미지다.

왜 중요한가:
RGB-D VSLAM에서는 feature의 2D 위치에 depth를 붙여 3D 점을 만든다.
이 3D 점이 있어야 PnP, map point 생성, point cloud 생성이 가능하다.

처음 확인할 것:

- 가까운 물체와 먼 물체의 depth 값이 다르게 나오는가
- 0, NaN, inf 같은 잘못된 depth가 많지 않은가
- 반사면, 유리, 햇빛에서 depth가 무너지지 않는가

흔한 오해:
Depth image는 일반 이미지처럼 모든 픽셀이 항상 믿을 만한 값이라고 생각하면 안 된다.
Depth는 센서 특성상 빠지는 영역과 튀는 값이 자주 있다.

### Aligned Depth

한 줄 정의:
`Aligned depth`는 color image 좌표에 맞춰 정렬된 depth image다.

왜 중요한가:
feature는 보통 color image에서 찾는다.
그 feature 위치의 depth를 읽으려면 color와 depth 좌표가 서로 맞아야 한다.

처음 확인할 것:

- color의 물체 경계와 depth의 물체 경계가 대략 겹치는가
- `aligned_depth_to_color` 계열 topic을 쓰고 있는가
- camera_info가 color 기준인지 depth 기준인지 헷갈리지 않았는가

흔한 오해:
Depth image가 존재하기만 하면 color feature에 바로 붙일 수 있다고 생각하기 쉽다.
정렬되지 않은 depth를 그대로 쓰면 3D 점 위치가 틀어진다.

### Camera Info

한 줄 정의:
`camera_info`는 카메라 내부 파라미터를 담은 ROS2 메시지다.

왜 중요한가:
이미지 픽셀과 실제 3D 방향을 연결하려면 초점거리와 중심점이 필요하다.
이 값이 틀리면 depth가 있어도 3D 점을 잘못 만든다.

처음 확인할 것:

- camera_info의 width, height가 실제 image 해상도와 맞는가
- color image에 맞는 camera_info를 쓰고 있는가
- 해상도 preset을 바꾼 뒤 camera_info도 같이 바뀌는가

흔한 오해:
camera_info는 그냥 보조 정보라고 생각하기 쉽다.
실제로는 PnP, 3D 복원, reprojection error 계산의 기준이 되는 핵심 입력이다.

### Intrinsic Parameter

한 줄 정의:
`Intrinsic parameter`는 카메라 내부 특성을 나타내는 값이다.

왜 중요한가:
대표적으로 `fx`, `fy`, `cx`, `cy`가 있다.
픽셀 위치와 depth를 3D 점으로 바꿀 때 사용한다.

처음 보는 1단계 식:

```text
X = (u - cx) * Z / fx
Y = (v - cy) * Z / fy
Z = depth
```

왜 이 식이 필요한가:
이미지의 픽셀 좌표 `(u, v)`는 화면 위 위치일 뿐이다.
VSLAM은 실제 공간의 점 `(X, Y, Z)`가 필요하므로, camera_info와 depth로 픽셀을 3D로 되돌린다.

흔한 오해:
`fx`, `fy`를 그냥 카메라 해상도와 같은 값으로 생각하면 안 된다.
초점거리와 중심점은 calibration 결과이며, 해상도 변경에 따라 달라질 수 있다.

### Extrinsic Parameter

한 줄 정의:
`Extrinsic parameter`는 두 센서 또는 좌표계 사이의 위치와 방향 관계다.

왜 중요한가:
카메라, IMU, 로봇 본체가 서로 어디에 붙어 있는지 알아야 같은 공간 기준으로 데이터를 합칠 수 있다.

처음 확인할 것:

- camera frame과 base frame 사이 TF가 있는가
- IMU 장착 방향이 실제와 맞는가
- 센서 위치 offset을 0으로 가정하고 있지 않은가

흔한 오해:
센서가 로봇 위에 붙어 있으면 그냥 같은 위치라고 생각하기 쉽다.
작은 offset도 회전하거나 가까운 장애물을 볼 때 큰 오차로 나타날 수 있다.

### IMU

한 줄 정의:
`IMU`는 가속도와 각속도를 측정하는 센서다.

왜 중요한가:
카메라가 흔들리거나 feature가 부족할 때 회전 힌트를 줄 수 있다.
하지만 보정, 축 방향, timestamp, covariance가 맞지 않으면 오히려 VSLAM을 망가뜨릴 수 있다.

처음 확인할 것:

- 정지 상태에서 angular velocity가 0 근처인가
- 중력 방향이 예상 축으로 보이는가
- 회전했을 때 yaw/pitch/roll 방향이 직관과 맞는가
- IMU timestamp가 이미지와 크게 어긋나지 않는가

흔한 오해:
IMU를 붙이면 무조건 좋아진다고 생각하기 쉽다.
초기 VSLAM 학습에서는 RGB-D baseline을 먼저 안정화한 뒤 IMU를 붙이는 편이 원인 분리에 좋다.

### Timestamp Sync

한 줄 정의:
`Timestamp sync`는 서로 다른 센서 데이터의 시간 기준을 맞추는 것이다.

왜 중요한가:
카메라 image와 depth, IMU가 서로 다른 시점의 데이터를 섞으면 실제 움직임과 계산이 어긋난다.

처음 확인할 것:

- color와 depth timestamp 차이가 작은가
- IMU가 과거나 미래 timestamp로 들어오지 않는가
- queue size와 sync 허용 시간이 너무 작거나 크지 않은가

흔한 오해:
topic이 모두 보이면 동기화도 된 것이라고 생각하기 쉽다.
VSLAM에서는 topic 존재보다 "같은 시간의 데이터가 함께 들어오는가"가 더 중요하다.

## 2. 좌표계와 이동 추정 용어

### Coordinate Frame

한 줄 정의:
`Coordinate frame`은 위치와 방향을 표현하는 기준축이다.

왜 중요한가:
카메라 기준 앞쪽, 로봇 기준 앞쪽, 지도 기준 앞쪽이 서로 다를 수 있다.
좌표계를 혼동하면 map이 돌아가거나 로봇이 반대로 움직이는 것처럼 보인다.

처음 확인할 것:

- `map`, `odom`, `base_link`, `camera_link` 관계가 이어지는가
- optical frame과 body frame을 혼동하지 않았는가
- RViz fixed frame을 현재 pipeline에 맞게 설정했는가

흔한 오해:
좌표계 문제는 화면 표시 문제라고만 생각하기 쉽다.
실제로는 PnP, EKF, map 생성, navigation까지 모두 흔드는 핵심 문제다.

### TF

한 줄 정의:
`TF`는 ROS에서 좌표계 사이의 위치와 방향 관계를 전달하는 시스템이다.

왜 중요한가:
VSLAM 결과가 `camera_link` 기준으로 나오더라도 로봇이나 map 기준으로 해석하려면 TF가 필요하다.

처음 확인할 것:

- TF tree가 끊기지 않는가
- 같은 parent-child 관계를 여러 노드가 동시에 publish하지 않는가
- timestamp가 오래된 TF 때문에 extrapolation error가 나지 않는가

흔한 오해:
TF는 단순 시각화용이라고 생각하기 쉽다.
실제로는 여러 센서와 알고리즘 결과를 같은 기준으로 맞추는 계약이다.

### Pose

한 줄 정의:
`Pose`는 위치와 방향을 합친 값이다.

왜 중요한가:
VSLAM의 핵심 출력은 결국 "현재 카메라 또는 로봇의 pose가 어디인가"다.
위치만 맞고 방향이 틀리면 다음 frame과 map이 계속 어긋난다.

처음 확인할 것:

- position이 실제 움직임 방향과 맞는가
- yaw 회전이 실제 회전 방향과 맞는가
- 정지 상태에서 pose가 계속 떠다니지 않는가

흔한 오해:
pose는 위치 좌표만 보면 된다고 생각하기 쉽다.
VSLAM에서는 방향 오차가 누적되어 map 전체를 크게 망가뜨릴 수 있다.

### Odometry

한 줄 정의:
`Odometry`는 시간이 지나며 이동량을 누적해 현재 위치를 추정한 값이다.

왜 중요한가:
VSLAM에서 odometry는 연속된 frame 사이의 상대 이동을 이어 붙인 trajectory의 기본 형태다.

처음 확인할 것:

- 천천히 전진할 때 x/y/z 중 어느 축이 변하는가
- 제자리 회전할 때 yaw가 자연스럽게 변하는가
- 갑자기 큰 pose jump가 생기지 않는가

흔한 오해:
odometry는 완전한 위치 정답이라고 생각하기 쉽다.
대부분의 odometry는 시간이 지날수록 drift가 쌓인다.

### Trajectory

한 줄 정의:
`Trajectory`는 시간 순서대로 이어진 pose의 경로다.

왜 중요한가:
VSLAM 결과를 평가할 때 개별 pose보다 전체 trajectory가 실제 경로와 얼마나 맞는지가 중요하다.

처음 확인할 것:

- 경로가 실제 이동 방향과 비슷한가
- 루프를 돌고 돌아왔을 때 출발점 근처로 오는가
- 특정 구간에서 갑자기 꺾이거나 튀지 않는가

흔한 오해:
짧은 구간이 좋아 보이면 전체도 좋다고 생각하기 쉽다.
VSLAM은 작은 오차가 누적되므로 긴 trajectory에서 문제가 드러나는 경우가 많다.

### Scale Drift

한 줄 정의:
`Scale drift`는 추정한 이동 거리의 크기 비율이 시간이 지나며 틀어지는 현상이다.

왜 중요한가:
실제로 1m 이동했는데 map에서는 0.6m 또는 1.5m처럼 보이면 자율주행 위치 판단이 깨진다.

처음 확인할 것:

- 실제 1m 이동이 map에서도 대략 1m인가
- depth 단위를 잘못 해석하지 않았는가
- 카메라 내부 파라미터가 현재 해상도와 맞는가

흔한 오해:
RGB-D는 scale drift가 절대 없다고 생각하기 쉽다.
Depth와 calibration이 틀리면 RGB-D에서도 scale이 틀어진다.

## 3. Frontend 용어

### Feature

한 줄 정의:
`Feature`는 이미지 안에서 다시 찾기 쉬운 점이다.

왜 중요한가:
VSLAM은 이전 frame의 feature가 다음 frame에서 어디로 이동했는지 보고 카메라 움직임을 추정한다.

처음 확인할 것:

- feature 수가 충분한가
- 벽, 바닥, 하늘처럼 텍스처가 적은 곳에서 feature가 급감하지 않는가
- blur가 생길 때 feature가 사라지지 않는가

흔한 오해:
feature가 많을수록 무조건 좋다고 생각하기 쉽다.
많아도 잘못 매칭되면 오히려 pose 추정을 망칠 수 있다.

### Descriptor

한 줄 정의:
`Descriptor`는 feature 주변 모양을 비교하기 위해 만든 숫자 요약값이다.

왜 중요한가:
feature를 찾은 뒤, 다음 frame에서 같은 feature인지 비교하려면 descriptor가 필요하다.

처음 확인할 것:

- descriptor matching 결과가 너무 적지 않은가
- 비슷한 패턴이 반복되는 곳에서 잘못 matching되지 않는가
- 조명 변화에 너무 민감하지 않은가

흔한 오해:
feature 위치만 있으면 matching할 수 있다고 생각하기 쉽다.
실제로는 각 feature가 어떤 모양인지 비교할 descriptor가 필요하다.

### Feature Tracking

한 줄 정의:
`Feature tracking`은 이전 frame의 feature를 다음 frame에서 따라가는 과정이다.

왜 중요한가:
Tracking이 끊기면 frame 사이 이동을 계산할 재료가 부족해진다.

처음 확인할 것:

- 이전 frame 대비 현재 frame에서 살아남은 feature 수가 충분한가
- 빠른 회전이나 blur에서 tracking이 끊기지 않는가
- 동적 물체 위 feature를 많이 따라가지 않는가

흔한 오해:
한 번 feature를 많이 찾으면 계속 안정적이라고 생각하기 쉽다.
카메라 움직임, 조명, blur, 동적 물체 때문에 tracking 품질은 계속 변한다.

### Matching

한 줄 정의:
`Matching`은 두 frame 또는 두 이미지에서 같은 지점을 짝짓는 과정이다.

왜 중요한가:
잘못된 match가 많으면 카메라 pose를 잘못 계산한다.

처음 확인할 것:

- match 수와 inlier 수를 같이 보는가
- 반복 패턴에서 잘못된 match가 늘지 않는가
- ratio test, cross-check, RANSAC 같은 방어를 쓰는가

흔한 오해:
match 수가 많으면 좋은 결과라고 생각하기 쉽다.
중요한 것은 match 수보다 올바른 match 비율이다.

### PnP

한 줄 정의:
`PnP`는 3D 점과 2D 이미지 점의 대응으로 카메라 pose를 구하는 방법이다.

왜 중요한가:
RGB-D VSLAM에서는 이전 frame의 3D 점과 현재 frame의 2D feature를 이용해 현재 카메라 위치를 추정할 수 있다.

처음 확인할 것:

- depth가 있는 3D 점이 충분한가
- 3D-2D 대응이 한쪽 영역에만 몰려 있지 않은가
- PnP 성공 여부와 reprojection error를 로그로 남기는가

흔한 오해:
PnP는 대응점 몇 개만 있으면 항상 안정적이라고 생각하기 쉽다.
대응점이 적거나 한 평면에 몰리거나 outlier가 많으면 pose가 불안정하다.

### RANSAC

한 줄 정의:
`RANSAC`은 outlier가 섞여 있을 때 그럴듯한 모델을 찾는 방법이다.

왜 중요한가:
Feature matching에는 틀린 대응점이 반드시 섞인다.
RANSAC은 이런 잘못된 대응점이 pose 추정을 망치지 않도록 막는다.

처음 확인할 것:

- RANSAC inlier 수가 충분한가
- inlier 비율이 너무 낮지 않은가
- threshold가 너무 빡빡하거나 느슨하지 않은가

흔한 오해:
RANSAC을 쓰면 outlier 문제가 완전히 해결된다고 생각하기 쉽다.
Outlier가 너무 많거나 좋은 대응점이 적으면 RANSAC도 실패한다.

### Inlier / Outlier

한 줄 정의:
`Inlier`는 추정한 모델과 잘 맞는 정상 데이터이고, `Outlier`는 모델과 맞지 않는 이상 데이터다.

왜 중요한가:
VSLAM에서는 몇 개의 outlier가 pose를 크게 틀어버릴 수 있다.

처음 확인할 것:

- 전체 match 중 inlier 비율이 어느 정도인가
- outlier가 특정 영역이나 동적 물체에 몰려 있는가
- outlier를 제거한 뒤 pose가 안정되는가

흔한 오해:
Outlier는 드문 예외라고 생각하기 쉽다.
실제 카메라 입력에서는 반사, blur, 반복 무늬, 움직이는 물체 때문에 outlier가 자주 생긴다.

### Reprojection Error

한 줄 정의:
`Reprojection error`는 추정한 3D 점을 이미지에 다시 찍었을 때 실제 feature와 얼마나 차이 나는지다.

왜 중요한가:
Pose 추정이 잘됐는지 판단하는 대표적인 품질 지표다.

처음 확인할 것:

- 평균 reprojection error가 너무 크지 않은가
- 특정 frame에서만 error가 급증하지 않는가
- error가 큰 feature를 outlier로 제거하고 있는가

흔한 오해:
Pose 결과가 숫자로 나오면 성공이라고 생각하기 쉽다.
Pose가 나왔더라도 reprojection error가 크면 신뢰하기 어렵다.

## 4. Backend와 지도 용어

### Keyframe

한 줄 정의:
`Keyframe`은 모든 frame 중 map과 최적화에 오래 남겨둘 중요한 frame이다.

왜 중요한가:
모든 frame을 다 저장하고 최적화하면 계산량이 너무 커진다.
Keyframe은 필요한 순간의 정보만 골라 backend가 다룰 수 있게 한다.

처음 확인할 것:

- keyframe이 너무 자주 생기지 않는가
- 반대로 너무 드물게 생겨 map이 빈약하지 않은가
- 회전, 이동, feature 변화가 있을 때 keyframe이 생기는가

흔한 오해:
Frame과 keyframe을 같은 것으로 생각하기 쉽다.
Frame은 매 순간 들어오는 이미지이고, keyframe은 그중 선택된 중요한 frame이다.

### Map Point

한 줄 정의:
`Map point`는 여러 frame에서 관측된 실제 공간의 3D 점이다.

왜 중요한가:
Map point가 있어야 현재 frame의 feature와 비교해 relocalization, PnP, backend 최적화를 할 수 있다.

처음 확인할 것:

- 같은 3D 점이 여러 frame에서 반복 관측되는가
- depth noise 때문에 map point가 흩어지지 않는가
- 동적 물체의 점을 map point로 오래 남기지 않는가

흔한 오해:
Point cloud에 점이 많으면 좋은 map이라고 생각하기 쉽다.
정확하고 반복 관측되는 map point가 중요하다.

### Bundle Adjustment

한 줄 정의:
`Bundle Adjustment`는 여러 카메라 pose와 3D point를 함께 조정해 오차를 줄이는 최적화다.

왜 중요한가:
Frontend의 frame-to-frame 추정은 작은 오차가 계속 쌓인다.
Bundle Adjustment는 여러 관측을 함께 보며 전체 오차를 줄인다.

처음 확인할 것:

- 최적화 전후 reprojection error가 줄어드는가
- 너무 많은 keyframe을 넣어 계산이 느려지지 않는가
- 잘못된 outlier를 넣어 최적화가 망가지지 않는가

흔한 오해:
Backend 최적화가 모든 frontend 오류를 고쳐준다고 생각하기 쉽다.
나쁜 feature match와 outlier가 많으면 backend도 잘못된 방향으로 최적화된다.

### Pose Graph

한 줄 정의:
`Pose graph`는 pose를 노드로, pose 사이 관계를 edge로 표현한 그래프다.

왜 중요한가:
Loop closure가 생겼을 때 전체 trajectory를 한 번에 보정하려면 pose graph가 필요하다.

처음 확인할 것:

- frame 사이 odometry edge가 자연스럽게 연결되는가
- loop closure edge가 잘못 추가되지 않는가
- graph optimization 후 trajectory가 갑자기 찢어지지 않는가

흔한 오해:
Pose graph는 지도 그림이라고 생각하기 쉽다.
정확히는 pose 사이의 제약 조건을 담은 최적화 구조다.

### Noise Model

한 줄 정의:
`Noise model`은 각 측정값을 얼마나 믿을지 정하는 모델이다.

왜 중요한가:
Visual odometry, IMU, wheel odometry, GPS는 각각 오차 특성이 다르다.
모든 센서를 똑같이 믿으면 불안정한 센서가 전체 추정을 흔들 수 있다.

처음 확인할 것:

- covariance가 비현실적으로 작지 않은가
- 센서별로 신뢰도를 다르게 주고 있는가
- 실제 흔들림이 큰 센서를 너무 강하게 믿지 않는가

흔한 오해:
센서를 많이 넣으면 결과가 자동으로 좋아진다고 생각하기 쉽다.
Noise model이 틀리면 센서 fusion은 오히려 나빠질 수 있다.

### Covariance

한 줄 정의:
`Covariance`는 추정값의 불확실성을 숫자로 표현한 것이다.

왜 중요한가:
EKF나 backend는 covariance를 보고 어떤 측정을 더 믿을지 판단한다.

처음 확인할 것:

- covariance가 0에 가깝게 들어오지 않는가
- 실제로 불안정한 축의 covariance를 너무 작게 두지 않았는가
- yaw, position, velocity 각각의 covariance를 구분해서 보고 있는가

흔한 오해:
Covariance는 작을수록 좋은 값이라고 생각하기 쉽다.
작다는 것은 "좋다"가 아니라 "나는 이 값을 매우 확신한다"는 의미다.
틀린 값을 확신하면 결과는 더 위험해진다.

## 5. Loop와 위치 회복 용어

### Loop Closure

한 줄 정의:
`Loop closure`는 예전에 본 장소를 다시 인식해 누적 오차를 줄이는 과정이다.

왜 중요한가:
Odometry는 시간이 지날수록 drift가 쌓인다.
Loop closure는 "여기 다시 왔다"는 제약을 추가해 전체 trajectory를 보정한다.

처음 확인할 것:

- 재방문했을 때 loop 후보가 생기는가
- 잘못된 장소를 같은 장소로 인식하지 않는가
- loop 후 map이 자연스럽게 닫히는가

흔한 오해:
Loop closure는 항상 좋은 보정이라고 생각하기 쉽다.
잘못된 loop closure는 map 전체를 크게 망가뜨릴 수 있다.

### Place Recognition

한 줄 정의:
`Place recognition`은 현재 장면이 이전에 본 장소인지 판단하는 과정이다.

왜 중요한가:
Loop closure와 relocalization의 시작점이다.

처음 확인할 것:

- 같은 장소를 다른 방향에서 봐도 후보가 생기는가
- 비슷하게 생긴 다른 장소를 혼동하지 않는가
- 조명 변화에 너무 민감하지 않은가

흔한 오해:
장소 인식은 이미지가 똑같아야만 된다고 생각하기 쉽다.
실제로는 관점, 조명, 일부 가림이 달라도 같은 장소임을 찾아야 한다.

### Relocalization

한 줄 정의:
`Relocalization`은 현재 위치를 잃었을 때 기존 map 안에서 다시 위치를 찾는 과정이다.

왜 중요한가:
Feature tracking이 끊기거나 odometry가 실패해도, map을 이용해 다시 복구할 수 있다.

처음 확인할 것:

- tracking lost 후 다시 위치를 찾는가
- 기존 map point와 현재 feature가 충분히 매칭되는가
- 잘못된 위치로 relocalize되지 않는가

흔한 오해:
Relocalization은 loop closure와 같은 기능이라고 생각하기 쉽다.
둘 다 장소 인식을 쓰지만, loop closure는 누적 오차 보정이고 relocalization은 잃어버린 현재 위치 복구에 가깝다.

## 6. 평가와 디버깅 용어

### Baseline

한 줄 정의:
`Baseline`은 내가 만든 결과와 비교할 기준 시스템이다.

왜 중요한가:
직접 구현이 실패했을 때 입력 문제인지 알고리즘 문제인지 분리하려면 baseline이 필요하다.

처음 확인할 것:

- 같은 입력에서 RTAB-Map은 정상 동작하는가
- baseline과 직접 구현의 입력 topic이 같은가
- 비교 조건이 해상도, FPS, 경로, 조명까지 비슷한가

흔한 오해:
Baseline은 임시로만 돌려보는 도구라고 생각하기 쉽다.
실제로는 디버깅과 성능 평가의 기준점이다.

### ATE

한 줄 정의:
`ATE`는 전체 trajectory가 정답 경로와 얼마나 다른지 보는 지표다.

왜 중요한가:
지도와 전체 경로가 실제와 얼마나 가까운지 평가할 수 있다.

처음 확인할 것:

- 비교할 ground truth가 있는가
- trajectory의 좌표계와 시간 기준이 맞는가
- 정렬 방법을 알고 비교하는가

흔한 오해:
ATE 하나만 낮으면 모든 것이 좋다고 생각하기 쉽다.
짧은 구간의 움직임 품질은 RPE와 함께 봐야 한다.

### RPE

한 줄 정의:
`RPE`는 짧은 구간의 상대 이동 오차를 보는 지표다.

왜 중요한가:
전체 경로는 괜찮아 보여도 frame 사이 이동이 흔들릴 수 있다.
RPE는 이런 local motion 품질을 보기 좋다.

처음 확인할 것:

- 회전 구간에서 RPE가 커지지 않는가
- 빠른 움직임이나 feature 부족 구간에서 RPE가 튀지 않는가
- ATE와 RPE를 같이 비교하는가

흔한 오해:
ATE와 RPE는 둘 중 하나만 보면 된다고 생각하기 쉽다.
ATE는 전체 경로, RPE는 구간별 움직임 품질을 본다.

### FPS

한 줄 정의:
`FPS`는 초당 처리하는 frame 수다.

왜 중요한가:
VSLAM이 실시간으로 동작하려면 입력 FPS와 처리 FPS가 너무 벌어지면 안 된다.

처음 확인할 것:

- camera FPS가 목표대로 나오는가
- VSLAM 처리 FPS가 입력보다 너무 낮지 않은가
- GUI 때문에 FPS가 떨어지는 것은 아닌가

흔한 오해:
FPS만 높으면 실시간이라고 생각하기 쉽다.
처리 지연인 latency도 같이 봐야 한다.

### Latency

한 줄 정의:
`Latency`는 입력이 들어온 뒤 결과가 나오기까지 걸리는 시간이다.

왜 중요한가:
야외 자율주행에서는 늦게 나온 위치 추정이 실제 현재 위치와 달라질 수 있다.

처음 확인할 것:

- 이미지 timestamp와 odometry output timestamp 차이가 큰가
- queue가 너무 커서 오래된 frame을 처리하고 있지 않은가
- CPU/GPU 부하가 높아지면 latency가 늘어나는가

흔한 오해:
FPS가 유지되면 latency도 낮다고 생각하기 쉽다.
Frame은 계속 처리하지만 몇 초 늦은 데이터를 보고 있을 수도 있다.

### Rosbag

한 줄 정의:
`rosbag`은 ROS2 topic 데이터를 파일로 기록하고 다시 재생하는 도구다.

왜 중요한가:
실시간 문제를 다시 재현하려면 같은 입력을 반복해서 돌릴 수 있어야 한다.

처음 확인할 것:

- color, depth, camera_info, TF, IMU를 함께 기록했는가
- bag 재생에서도 같은 문제가 재현되는가
- 너무 큰 bag으로 저장/재생이 밀리지 않는가

흔한 오해:
실시간 화면만 보면 충분하다고 생각하기 쉽다.
VSLAM 디버깅은 같은 입력을 반복 재생할 수 있어야 원인 분리가 쉽다.

### Observability

한 줄 정의:
`Observability`는 알고리즘이 어떤 상태를 센서 데이터로 실제 구분해낼 수 있는지를 뜻한다.

왜 중요한가:
센서가 특정 정보를 주지 않으면 필터나 최적화가 그 값을 안정적으로 추정하기 어렵다.

처음 확인할 것:

- yaw를 직접 볼 수 있는 입력이 있는가
- scale을 결정할 depth나 거리 정보가 있는가
- 정지 상태에서 추정하려는 값이 실제로 관측 가능한가

흔한 오해:
알고리즘이 좋으면 모든 상태를 알아낼 수 있다고 생각하기 쉽다.
센서 입력에 정보가 없으면 좋은 알고리즘도 안정적으로 추정할 수 없다.

### Numerical Stability

한 줄 정의:
`Numerical stability`는 계산이 작은 오차나 나쁜 입력에도 폭발하지 않고 유지되는 성질이다.

왜 중요한가:
VSLAM은 행렬 계산, 최적화, 반복 계산이 많다.
작은 잘못된 depth나 outlier가 pose를 크게 튀게 만들 수 있다.

처음 확인할 것:

- depth가 0, NaN, inf일 때 제거하는가
- feature 수가 부족할 때 pose 추정을 건너뛰는가
- 최적화가 발산할 때 fallback이 있는가

흔한 오해:
코드가 에러 없이 실행되면 계산도 안정적이라고 생각하기 쉽다.
출력 pose가 나오더라도 수치적으로 불안정하면 map이 서서히 또는 갑자기 무너진다.

## 7. 용어 간 연결 지도

VSLAM 용어는 따로 외우기보다 흐름으로 연결해서 보는 편이 좋다.

```text
Frame
-> Feature / Descriptor
-> Matching / Tracking
-> Depth association
-> PnP + RANSAC
-> Pose / Odometry
-> Keyframe / Map Point
-> Bundle Adjustment / Pose Graph
-> Loop Closure / Relocalization
-> ATE / RPE / FPS / Latency 평가
```

센서와 디버깅 용어는 아래 흐름으로 연결된다.

```text
RGB-D / camera_info / IMU
-> Coordinate frame / TF
-> Timestamp sync
-> Calibration
-> Noise model / Covariance
-> Observability / Numerical stability
```

## 8. 1단계 학습 체크 질문

아래 질문에 답할 수 있으면 VSLAM 문서를 읽을 준비가 된 것이다.

1. RGB-D가 단안 카메라보다 초보자에게 쉬운 이유는 무엇인가?
2. aligned depth가 없으면 feature의 3D 위치 계산이 왜 틀어질 수 있는가?
3. camera_info의 `fx`, `fy`, `cx`, `cy`는 왜 필요한가?
4. Feature match 수보다 inlier 수가 더 중요한 이유는 무엇인가?
5. PnP와 RANSAC은 각각 어떤 문제를 해결하는가?
6. Frontend와 Backend는 왜 역할을 나누는가?
7. Loop closure가 잘못 걸리면 왜 map이 더 나빠질 수 있는가?
8. Covariance가 작다는 말은 왜 "좋다"가 아니라 "강하게 믿는다"에 가까운가?
9. ATE와 RPE는 각각 어떤 오차를 보는가?
10. FPS가 높아도 latency가 크면 왜 자율주행에 위험한가?
