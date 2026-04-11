# 왜 RealSense Viewer는 실시간처럼 보이는데 RTAB-Map은 그렇지 않을까

## 결론

- `realsense-viewer`는 **센서가 방금 보낸 프레임을 바로 화면에 그리는 도구**라서 부드럽게 보이기 쉽다.
- `RTAB-Map`은 **프레임 동기화 + 오도메트리 + 3D 맵 누적**까지 해야 해서, 같은 카메라를 써도 훨씬 무겁고 실패 조건도 많다.
- 따라서 `viewer`가 부드럽다고 해서 `RTAB-Map`도 자동으로 부드러워지는 것은 아니다.
- 반대로 `viewer`는 정상인데 `RTAB-Map`만 느리거나 끊기면, 센서 자체보다 **SLAM 파이프라인 설정/연산량/동기화** 쪽을 먼저 의심하는 것이 맞다.

---

## 1. 먼저 개념부터

- `depth`: 카메라와 물체 사이의 거리값이다.
- `point cloud`: depth를 3차원 점들의 집합으로 바꾼 것이다.
- `odometry`: 바로 직전 프레임과 현재 프레임 사이에서 카메라가 얼마나 움직였는지 추정하는 것이다.
- `SLAM`: 위치 추정과 맵 생성을 동시에 하는 것이다.

즉, `viewer`는 주로 **센서가 지금 무엇을 보고 있는지**를 보여주고,  
`RTAB-Map`은 **센서가 보던 장면을 시간에 따라 연결해서 지도화**한다.

---

## 2. 처리 파이프라인 차이

### 2-1. RealSense Viewer

```text
D435i
-> librealsense
-> 현재 프레임 표시
-> depth / point cloud 시각화
```

특징:

- 장치 SDK에 직접 붙는다
- 현재 프레임이 잘 들어오면 화면은 계속 갱신된다
- 이전 프레임과 현재 프레임이 "잘 연결되는지"는 크게 중요하지 않다

즉, **센서 품질 확인용** 도구에 가깝다.

### 2-2. RTAB-Map

```text
D435i
-> librealsense
-> realsense2_camera
-> ROS2 topic(color/depth/camera_info)
-> 동기화(sync)
-> rgbd_odometry
-> RTAB-Map
-> 3D 맵 / 그래프 / GUI
```

특징:

- ROS2 토픽으로 한 번 더 거친다
- `color`, `depth`, `camera_info` 시간이 맞아야 한다
- 특징점 추출, 매칭, 자세 추정까지 해야 한다
- 오도메트리가 실패하면 맵에 프레임을 넣지 못한다

즉, **센서 확인을 넘어서 실제 VSLAM 일을 하는 시스템**이다.

---

## 3. 왜 viewer는 부드럽고 RTAB-Map은 실패할 수 있는가

### 3-1. Viewer는 "현재 프레임"만 보면 된다

`viewer`는 지금 들어온 프레임 하나만 잘 보여주면 된다.

그래서:

- depth가 들어오고
- point cloud가 보이고
- 3D 장면이 부드럽게 갱신되면

겉으로는 아주 안정적으로 보일 수 있다.

하지만 이건 **맵이 누적되고 있다**는 뜻은 아니다.

### 3-2. RTAB-Map은 "연속 프레임 연결"이 성공해야 한다

`RTAB-Map`은 아래가 모두 성공해야 한다.

1. `color/depth/camera_info`가 같은 시점으로 맞음
2. 특징점이 충분히 검출됨
3. 이전 프레임과 현재 프레임에서 특징점 매칭이 됨
4. 그 중에서 정상 매칭점(`inlier`)이 충분히 남음
5. 그걸로 카메라 움직임 추정에 성공함
6. 그제야 맵에 새 프레임을 누적함

그래서 로그에 아래가 뜨면 맵이 멈추기 쉽다.

```text
Registration failed: "Not enough inliers ..."
Odom: quality=0
RGB-D SLAM mode is enabled, memory is incremental but no odometry is provided.
```

이건 센서가 망가진 뜻이 아니라,  
**SLAM이 프레임 사이 움직임을 신뢰성 있게 계산하지 못했다**는 뜻이다.

---

## 4. 실제로 RTAB-Map 쪽이 더 어려운 이유

### 4-1. 동기화 문제

`RTAB-Map`은 `color`, `depth`, `camera_info`가 같이 들어와야 한다.

즉:

- timestamp 차이가 너무 크거나
- queue가 작거나
- `approx_sync`가 너무 엄격하면

콜백 자체가 잘 안 불릴 수 있다.

### 4-2. 오도메트리 문제

카메라를 손으로 빨리 흔들면:

- motion blur(흔들림 blur)가 생기고
- 프레임 간 변화가 커지고
- 특징점이 안정적으로 매칭되지 않는다

그러면 `inlier`가 부족해서 오도메트리가 실패한다.

### 4-3. 연산량 문제

RTAB-Map은 viewer보다 훨씬 많이 계산한다.

예:

- 특징점 추출
- depth 기반 3D 변환
- 프레임 간 정합
- 그래프 갱신
- GUI 갱신

그래서 CPU가 바쁘거나 GUI를 여러 개 띄우면 더 느려진다.

### 4-4. ROS2 파이프라인 부담

viewer는 SDK 기반으로 바로 장치를 본다.  
RTAB-Map은 ROS2 토픽으로 받으니 아래 부담이 추가된다.

- 메시지 복사
- QoS 영향
- subscribe/deserialize 비용
- 여러 노드 간 전달

---

## 5. 이번 D435i 실험에 적용하면 어떻게 해석해야 하는가

이번 테스트에서 `realsense-viewer`는 잘 보였고, `RTAB-Map`은 오도메트리 실패가 있었다.

이 해석은 아래가 맞다.

### 맞는 해석

- 센서 자체와 USB/SDK는 대체로 정상일 가능성이 높다
- 문제는 `RTAB-Map`의 입력 조건과 설정 쪽일 가능성이 높다

### 틀리기 쉬운 해석

- viewer가 부드러우니 RTAB-Map도 당연히 부드러워야 한다
- RTAB-Map이 느리니 D435i가 느린 카메라다

둘 다 정확하지 않다.

---

## 6. 그럼 지금 무엇을 먼저 봐야 하나

우선순위는 아래 순서가 실용적이다.

1. `viewer`가 정상인지
   - 센서와 USB 자체 점검
2. `color/depth/camera_info` 토픽이 정상인지
   - 토픽 존재, Hz, frame_id
3. `rgbd_odometry`가 성공하는지
   - `quality`, `inliers`
4. 그 다음에야 맵 누적 속도를 본다

즉, **맵이 느리다**보다 먼저  
**오도메트리가 살아 있느냐**를 봐야 한다.

---

## 7. 지금 단계에서의 실용적 결론

- `realsense-viewer`는 센서 확인용으로 매우 좋다
- `RTAB-Map`은 실제 RGB-D SLAM 검증용이다
- 둘은 역할이 다르므로 체감 실시간성도 다르게 보이는 것이 자연스럽다
- `viewer는 정상, RTAB-Map은 불안정`이면 보통 하드웨어보다 **오도메트리/동기화/연산량**을 먼저 조정하면 된다

한 줄 요약:

> `viewer`는 "지금 프레임 보기", `RTAB-Map`은 "프레임을 이어서 위치와 맵 만들기"라서 훨씬 어렵고 무겁다.
