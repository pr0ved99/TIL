# D435i RealSense Viewer 기준 실시간성 문제 분리 체크리스트

## 결론

지금 D435i의 실시간성 문제가 있을 때, **가장 먼저 해야 할 일은 `realsense-viewer`로 하드웨어/SDK 단계가 안정적인지 분리 확인하는 것**이다.

이 문서는 아래 질문에 답하기 위한 체크리스트다.

1. 지금 문제는 `하드웨어/USB/librealsense` 단계 문제인가?
2. 아니면 `ROS2 드라이버/구독/GUI 처리` 단계 문제인가?

판단 기준은 아주 단순하다.

- `realsense-viewer`도 끊긴다:
  - 하드웨어, USB, 권한, librealsense 쪽 문제 가능성 큼
- `realsense-viewer`는 안정적이다:
  - ROS2 드라이버, QoS, Python GUI 처리 쪽 문제 가능성 큼

---

## 1. 왜 이 체크리스트가 필요한가

직관:
지금은 `ROS2에서 depth가 끊겨 보이는 문제`가 있다.  
이때 바로 코드 최적화만 하면, 실제 원인이 USB/장치 문제였을 때 시간을 낭비할 수 있다.

그래서 먼저 아래를 분리해야 한다.

```text
카메라/USB/librealsense 문제
vs
ROS2/realsense2_camera/구독 처리 문제
```

---

## 2. 블로그에서 참고할 것 / 그대로 따라하지 말 것

참고할 것:

- `realsense-viewer`로 하드웨어를 먼저 본다
- `setup_udev_rules.sh`는 권한 문제 해결 힌트가 될 수 있다
- USB 3.x 연결이 중요하다

지금 바로 따라하지 말 것:

- `patch-realsense-ubuntu-lts-hwe.sh`
- 커널 패치
- 소스 전체 재빌드 후 `make install`

이유:

- 지금은 아직 문제 분리가 끝나지 않았다
- 커널 패치는 영향 범위가 커서 마지막 수단에 가깝다

---

## 3. 지금 할 것

### 3-1. `realsense-viewer` 설치 여부 확인

```bash
which realsense-viewer
realsense-viewer --version
```

둘 중 하나라도 안 되면 미설치 가능성이 있다.

### 3-2. 설치가 안 되어 있으면

가장 먼저 확인:

```bash
dpkg -l | grep -E 'librealsense|realsense'
```

이미 `librealsense`가 시스템에 있으면, 무조건 소스 빌드부터 갈 필요는 없다.

---

## 4. `realsense-viewer`로 분리 진단하는 순서

### Step 1. 카메라 연결 상태 확인

```bash
lsusb -t
```

봐야 할 것:

- D435i가 USB 3.x로 잡히는지
- `5000M` 또는 그에 준하는 SuperSpeed 링크인지

현재 네 환경에서는 한 번 이렇게 확인됐다.

```text
Driver=uvcvideo, 5000M
```

### Step 2. `realsense-viewer` 실행

```bash
realsense-viewer
```

### Step 3. Viewer에서 확인할 것

확인 순서:

1. 장치가 자동 감지되는가
2. RGB 스트림이 안정적으로 나오는가
3. Depth 스트림이 안정적으로 나오는가
4. 30초 이상 끊김 없이 유지되는가
5. 뷰어가 멈추거나 장치가 사라지지 않는가

### Step 4. 판단

#### 경우 A. viewer도 끊긴다

가능성 높은 원인:

1. USB 케이블/포트 문제
2. 장치 전원/연결 불안정
3. librealsense/권한 문제
4. 펌웨어 문제

#### 경우 B. viewer는 안정적이다

가능성 높은 원인:

1. ROS2 `realsense2_camera` 드라이버 사용 방식
2. QoS 문제
3. `ros2 topic hz`나 GUI 노드 처리 병목
4. Python 콜백에서 프레임을 순차 처리하는 구조

---

## 5. 지금 환경에 맞는 추천 진단 순서

### 1단계. depth-only ROS2 실행

```bash
source /opt/ros/humble/setup.bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=false \
  enable_depth:=true \
  depth_module.depth_profile:=640x480x15 \
  publish_tf:=false \
  tf_publish_rate:=0.0
```

### 2단계. 원본 토픽 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic hz /camera/camera/depth/image_rect_raw
ros2 topic hz /camera/camera/depth/camera_info
```

해석:

- `camera_info`는 안정적이고
- `image_rect_raw`만 유실되면
- 큰 이미지 구독/처리 쪽 병목 가능성이 크다

### 3단계. `realsense-viewer` 테스트

```bash
realsense-viewer
```

### 4단계. Viewer 결과와 ROS2 결과 비교

- viewer 안정 + ROS2 불안정:
  - ROS2 쪽 최적화/설정 우선
- viewer 불안정 + ROS2 불안정:
  - 하드웨어/USB/librealsense 우선

---

## 6. 지금 하지 말 것

아래는 아직 이르다.

1. 커널 패치
2. librealsense 소스 재빌드
3. 펌웨어 업데이트부터 바로 진행
4. IMU까지 같이 켜고 문제를 더 복잡하게 만들기

이유:

- 지금은 depth-only로 먼저 안정성을 봐야 한다
- IMU는 현재 환경에서 `Permission denied`가 있어 별도 불안정 요소다

---

## 7. 권한 관련으로 참고할 것

블로그에서 나온 아래 항목은 지금 IMU 문제와 관련 있을 수 있다.

```bash
sudo ./scripts/setup_udev_rules.sh
```

이건 특히 아래 증상과 연결된다.

```text
Failed to open scan_element ... Permission denied
```

즉, 나중에 IMU 문제를 풀 때는 `udev rules` 확인이 도움이 될 수 있다.

다만 지금은 먼저 **depth 스트림 안정성 분리**가 우선이다.

---

## 8. 최종 체크리스트

- [ ] `lsusb -t`에서 USB 3.x 링크 확인
- [ ] `realsense-viewer` 설치 여부 확인
- [ ] `realsense-viewer`에서 30초 이상 연속 스트림 확인
- [ ] ROS2 depth-only 실행
- [ ] `/camera/camera/depth/camera_info` 주파수 확인
- [ ] `/camera/camera/depth/image_rect_raw` 주파수 확인
- [ ] viewer와 ROS2 결과 비교
- [ ] 그 다음에야 권한/udev/IMU 문제로 확장

---

## 9. 한 줄 판단 기준

- `viewer도 끊긴다` -> 하드웨어/USB/librealsense 먼저
- `viewer는 멀쩡한데 ROS2만 끊긴다` -> ROS2 구독/처리/QoS 먼저

