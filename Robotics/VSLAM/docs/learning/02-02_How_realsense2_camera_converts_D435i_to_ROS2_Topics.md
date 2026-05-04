# realsense2_camera가 D435i를 ROS2 토픽으로 바꾸는 방법

## 결론

`realsense2_camera`는 **D435i 장치 데이터를 읽어서 ROS2 표준 메시지와 토픽으로 다시 내보내는 드라이버 노드**다.  
쉽게 말하면, **D435i 전용 데이터 -> ROS2 토픽**으로 바꿔주는 번역기다.

핵심 흐름은 이렇다.

```text
D435i 센서
-> USB 통신
-> librealsense SDK
-> realsense2_camera_node
-> ROS2 표준 메시지 publish
```

---

## 1. 왜 이 문서가 필요한가

직관:
지금은 `ros2 launch ...`만 치면 카메라가 뜨는 것처럼 보이지만, 실제로는 중간에 여러 단계가 있다.  
이 구조를 알아야 나중에 문제가 생겼을 때 `카메라 문제인지`, `드라이버 문제인지`, `ROS2 토픽 문제인지`를 나눠서 볼 수 있다.

특히 VSLAM 관점에서는 아래를 구분할 수 있어야 한다.

- 장치가 실제로 인식됐는지
- 영상이 ROS2 토픽으로 나오는지
- `camera_info`, `timestamp`, `frame_id`가 같이 맞는지

---

## 2. 먼저 알아야 하는 용어

- `드라이버(driver)`: 장치와 소프트웨어를 연결해주는 프로그램이다.
- `SDK`: 장치를 읽고 제어하는 개발 도구 묶음이다.
- `librealsense`: Intel RealSense 공식 SDK다.
- `ROS2 메시지`: ROS2가 데이터를 주고받을 때 쓰는 표준 형식이다.
- `토픽(topic)`: 노드끼리 메시지를 주고받는 채널이다.

---

## 3. 실제 동작 구조

### 3-1. 하드웨어 단계

`D435i`는 단순 웹캠이 아니다.

- `RGB 카메라`
- `Depth 카메라`
- `IMU`

이 센서들이 만든 데이터가 USB를 통해 컴퓨터로 들어온다.

### 3-2. SDK 단계

컴퓨터가 D435i를 읽을 때는 보통 `librealsense`를 사용한다.

이 SDK가 하는 일:

- 장치 연결
- color/depth/IMU 프레임 읽기
- 장치 정보 읽기
- 스트림 설정 적용

즉, `realsense2_camera`는 장치를 직접 맨바닥부터 제어하는 게 아니라, 보통 `librealsense`를 이용해 장치 데이터를 받는다.

### 3-3. ROS2 드라이버 단계

네가 실행한 명령:

```bash
ros2 launch realsense2_camera rs_launch.py enable_color:=true enable_depth:=true
```

이 명령이 하는 일:

1. `rs_launch.py`가 실행된다
2. 내부에서 `realsense2_camera_node`를 띄운다
3. 이 노드가 `librealsense`로 D435i에 연결한다
4. 읽어온 데이터를 ROS2 메시지로 변환한다
5. ROS2 토픽으로 publish한다

---

## 4. 무엇이 어떻게 토픽이 되는가

### 4-1. 영상 데이터

예를 들어 아래 토픽:

```text
/camera/camera/color/image_raw
/camera/camera/depth/image_rect_raw
```

이 토픽들은 보통 `sensor_msgs/msg/Image` 메시지다.

의미:

- `color/image_raw`: 컬러 영상
- `depth/image_rect_raw`: depth 거리 영상

### 4-2. 카메라 파라미터

아래 토픽:

```text
/camera/camera/color/camera_info
/camera/camera/depth/camera_info
```

이 토픽들은 보통 `sensor_msgs/msg/CameraInfo` 메시지다.

의미:

- 카메라 내부 파라미터
- 왜곡 계수
- 해상도 정보

중요:
VSLAM, 3D 위치 계산, 투영, 역투영에는 `image`만이 아니라 `camera_info`도 필요하다.

### 4-3. 좌표계와 TF

드라이버는 경우에 따라 `tf_static` 같은 좌표계 정보도 제공한다.

이건 나중에 아래를 연결할 때 중요하다.

- `camera_link`
- `camera_depth_optical_frame`
- `base_link`

즉, 영상이 잘 나와도 좌표계가 틀리면 VSLAM이나 위치 계산은 틀어질 수 있다.

---

## 5. 왜 raw depth가 회색조처럼 보이는가

`/camera/camera/depth/image_rect_raw`는 색깔 영상이 아니라 거리값 영상이다.

즉:

- 각 픽셀마다 "몇 m 거리인지" 숫자가 들어 있다
- 그래서 뷰어는 이를 회색조처럼 보여줄 수 있다

이건 이상한 게 아니다. 정상이다.

사람이 보기 쉽게 하려면 컬러맵(colormap)을 씌운 시각화용 토픽을 추가하면 된다.

현재 추가한 스크립트:

- [depth_colormap_publisher.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py)

---

## 6. 디버깅할 때 어디를 나눠서 봐야 하는가

문제가 생기면 아래처럼 나눠서 보면 된다.

### 6-1. 장치 인식 문제

확인:

- D435i가 실제로 꽂혀 있는가
- USB 3.x로 연결됐는가
- launch 로그에 장치명이 보이는가

예:

```text
Device with name Intel RealSense D435I was found.
Device USB type: 3.2
```

### 6-2. 드라이버 실행 문제

확인:

- `realsense2_camera_node`가 떴는가
- launch 중 `device busy` 같은 에러가 없는가

자주 있는 문제:

- 같은 카메라를 두 번 실행함
- USB 대역폭 부족

### 6-3. ROS2 토픽 문제

확인 명령:

```bash
ros2 topic list
```

꼭 보려는 토픽:

```text
/camera/camera/depth/image_rect_raw
/camera/camera/color/image_raw
```

### 6-4. 시각화 문제

확인 명령:

```bash
ros2 run rqt_image_view rqt_image_view
```

그리고 선택:

```text
/camera/camera/depth/image_rect_raw
```

즉:

- 토픽이 있으면 publish는 되고 있는 것
- `rqt_image_view`에서 보이면 시각화까지 성공한 것

---

## 7. VSLAM 관점에서 특히 중요한 것

이건 초보자가 많이 놓치는 부분이다.

### 7-1. `image`만 보면 안 된다

`camera_info`도 같이 봐야 한다.

이유:

- 내부 파라미터가 있어야 투영/역투영이 가능하다
- 특징점의 2D-3D 관계 계산에 필요하다

### 7-2. `timestamp`가 중요하다

영상만 잘 보여도 시간이 어긋나면 문제가 생긴다.

예:

- IMU와 영상 시간이 안 맞음
- encoder와 camera 시간이 안 맞음

그럼 추적과 융합이 흔들린다.

### 7-3. `frame_id`와 TF가 중요하다

토픽이 잘 떠도 좌표계가 틀리면 결과가 틀어진다.

나중에 꼭 같이 봐야 하는 것:

- `frame_id`
- `tf_static`
- `camera_link`, `camera_depth_optical_frame`, `base_link`

---

## 8. 한 줄 정리

- `D435i`: 실제 센서 측정
- `librealsense`: 장치 데이터 읽기
- `realsense2_camera`: ROS2 토픽으로 변환
- `네 응용 노드`: 그 토픽을 받아서 VSLAM, 탐지, 장애물 회피 수행

즉, `realsense2_camera`는 D435i를 ROS2에서 쓸 수 있게 만드는 공식 ROS2 드라이버 계층이다.

