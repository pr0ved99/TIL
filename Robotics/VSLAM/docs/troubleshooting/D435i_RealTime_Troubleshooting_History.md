# D435i 실시간성 트러블슈팅 기록

## 결론

현재까지의 테스트 기준으로는 `D435i + ROS2 Humble` 환경에서 **IMU는 안정적인 실시간 입력을 확인했고**, depth는 **저해상도/저대역폭 설정에서 연속성 확보 방향**을 잡았다.

이번 트러블슈팅에서 가장 중요했던 원인은 아래 4가지였다.

1. `realsense2_camera` 미설치
2. `udev rules` 미적용
3. `realsense-viewer`, `rs_launch.py`, 여러 개의 `realsense2_camera_node`를 동시에 실행한 충돌
4. 큰 depth 이미지 토픽을 다룰 때의 구독/시각화 부담

즉, 처음 의심했던 "D435i 자체가 2초마다만 값을 보낸다"보다는, **실행 환경 충돌과 권한 문제, 그리고 큰 이미지 토픽 처리 부담**이 핵심이었다.

---

## 1. 트러블슈팅 목표

목표는 단순했다.

- D435i가 ROS2에서 정상적으로 붙는지 확인
- depth와 IMU가 연속적으로 들어오는지 확인
- 끊김이 생기면 하드웨어 문제인지, ROS2 드라이버 문제인지, 내 코드 문제인지 분리

여기서 `실시간성`은 하드 실시간 보장이라는 뜻이 아니라, **사용자가 체감하기에 끊기지 않고 연속적으로 안정적으로 들어오는 상태**를 뜻한다.

---

## 2. 초기 증상

처음에는 아래처럼 보였다.

- depth가 잘 뜨는 것 같다가 끊김
- IMU를 켜면 불안정
- `ros2 topic hz`로 보면 어떤 토픽은 `2초 간격으로 한 번씩만 들어오는 것처럼` 보임
- `realsense-viewer`에서도 `UDEV-Rules are missing!` 경고가 보임

이 상태에서는 원인을 바로 단정하면 안 된다.

가능한 원인은 크게 네 가지였다.

1. 카메라/USB/권한 문제
2. `realsense2_camera` 설정 문제
3. 여러 프로세스의 중복 실행 문제
4. 큰 이미지 토픽을 받는 측정/GUI 쪽 병목

---

## 3. 1차 조치: `realsense2_camera` 설치 및 기본 depth 확인

### 3-1. 확인 내용

먼저 ROS2 환경과 `realsense2_camera` 설치 여부를 확인했다.

확인 명령:

```bash
echo $ROS_DISTRO
which ros2
ros2 pkg prefix realsense2_camera
```

초기 상태:

- ROS2 Humble은 사용 가능
- `realsense2_camera`는 설치되어 있지 않음

### 3-2. 조치

사용자가 아래 명령으로 설치를 진행했다.

```bash
sudo apt-get update
sudo apt-get install -y ros-humble-realsense2-camera
```

### 3-3. 결과

아래 launch가 정상 실행되었다.

```bash
ros2 launch realsense2_camera rs_launch.py enable_color:=true enable_depth:=true
```

확인된 것:

- `Intel RealSense D435I` 장치 인식
- depth 토픽 생성
- color 토픽 생성

증빙:

- [`assets/2026-04-09_task59_d435i_depth_check/README.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-09_task59_d435i_depth_check/README.md)

---

## 4. 2차 증상: `realsense-viewer`에서 `UDEV-Rules are missing!`

### 4-1. 의미

`udev rules`는 리눅스에서 USB/HID 장치 접근 권한을 자동으로 잡아주는 규칙이다.

이 경고는 단순한 안내가 아니라, 실제로 아래 문제와 연결될 수 있다.

- `Permission denied`
- IMU/HID 접근 실패
- `scan_element` 열기 실패

### 4-2. 확인 내용

`realsense-viewer` 실행 시 아래 경고가 보였다.

```text
RealSense UDEV-Rules are missing!
```

또한 초기에는 시스템에 RealSense rules 파일이 없었다.

### 4-3. 조치

먼저 `v4l-utils`를 설치했다.

```bash
sudo apt update
sudo apt install -y v4l-utils
```

그 다음 공식 `librealsense` 저장소의 스크립트를 이용해 rules를 설치했다.

```bash
cd /tmp
git clone https://github.com/realsenseai/librealsense.git
cd librealsense
sudo ./scripts/setup_udev_rules.sh
sudo udevadm control --reload-rules
sudo udevadm trigger
```

중요:

- 이 스크립트는 `v4l2-ctl`이 없으면 중간에 실패한다
- 따라서 `v4l-utils` 설치가 선행되어야 한다

### 4-4. 결과

아래 파일이 실제로 생성된 것을 확인했다.

```bash
/etc/udev/rules.d/99-realsense-libusb.rules
```

또한:

```bash
which v4l2-ctl
v4l2-ctl --version
```

도 정상 확인되었다.

---

## 5. 3차 증상: IMU `Permission denied`

### 5-1. 증상

IMU를 켰을 때 초기 로그에서 아래와 같은 에러가 보였다.

```text
Failed to open scan_element ... Permission denied
```

이 때문에 IMU가 불안정하거나, 아예 publish되지 않을 가능성을 의심했다.

### 5-2. 확인 방법

IMU를 켜서 실행했다.

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_gyro:=true \
  enable_accel:=true \
  unite_imu_method:=1
```

그리고 토픽을 확인했다.

```bash
ros2 topic list | grep -E 'gyro|accel|imu'
```

### 5-3. 조치

핵심 조치는 앞 단계의 `udev rules` 적용이었다.

즉, IMU 문제만 따로 고친 것이 아니라:

- `udev rules` 적용
- 카메라 재연결
- 중복 실행 정리

를 통해 환경을 깨끗하게 만든 것이 효과를 냈다.

### 5-4. 결과

이후 IMU 토픽이 정상적으로 보였다.

예:

```text
/camera/camera/gyro/sample
/camera/camera/accel/sample
/camera/camera/imu
```

그리고 `ros2 topic echo --once` 기준으로 실제 값도 수신됐다.

해석:

- `orientation`이 0이고 `orientation_covariance[0] = -1`인 것은 정상이다
- D435i는 자세를 직접 계산해주는 것이 아니라, 자이로/가속도 원시값을 주는 구조다

---

## 6. 4차 증상: IMU가 2초 간격으로 끊겨 보이는 문제

### 6-1. 처음 보였던 현상

처음 `ros2 topic hz`로 IMU를 볼 때는 아래처럼 이상하게 측정됐다.

- 평균 주파수가 낮음
- `max: 2.048s`, `max: 4.029s` 같은 큰 간격이 보임

이때는 IMU 자체가 느리다고 오해하기 쉬웠다.

### 6-2. 실제 원인

원인은 거의 확실히 **중복 실행 충돌**이었다.

실제 당시 확인된 프로세스:

- `rs_launch.py` 여러 개
- `realsense2_camera_node` 여러 개
- `realsense-viewer`
- `depth_imu_local_mapper.py`
- `ros2 topic hz`

실제 로그에서도 아래가 반복됐다.

```text
Device or resource busy
The device has been disconnected!
```

즉, **같은 카메라를 여러 프로세스가 동시에 잡고 있었다.**

### 6-3. 확인 방법

프로세스를 확인했다.

```bash
pgrep -af 'realsense2_camera|rs_launch.py|realsense-viewer|depth_imu_local_mapper|ros2 topic hz'
```

그리고 로그를 봤다.

```bash
grep -E "Device or resource busy|The device has been disconnected" ~/.ros/log/realsense2_camera_node_*.log
```

### 6-4. 조치

모든 관련 프로세스를 정리했다.

```bash
pkill -f 'realsense2_camera|rs_launch.py|realsense-viewer|depth_imu_local_mapper|ros2 topic hz'
```

그리고 **IMU만 단독으로 실행**했다.

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=false \
  enable_depth:=false \
  enable_gyro:=true \
  enable_accel:=true \
  unite_imu_method:=1
```

### 6-5. 결과

이때는 매우 안정적으로 측정됐다.

실제 관찰값:

- `gyro/sample`: 약 `199.8 Hz`
- `accel/sample`: 약 `62.4 Hz`
- `/camera/camera/imu`: 약 `199.8 Hz`

즉, IMU 자체는 정상이었다.

한 줄 요약:

> IMU가 느린 게 아니라, 실행 환경이 충돌하고 있었다.

---

## 7. 5차 증상: depth는 `camera_info`는 정상인데 `image_rect_raw`만 느리게 보이는 문제

### 7-1. 관찰값

depth-only로 다시 나눠서 봤을 때 결과가 이렇게 나왔다.

정상:

- `/camera/camera/depth/camera_info`: 약 `15.0 Hz`

이상:

- `/camera/camera/depth/image_rect_raw`: `4~5 Hz`처럼 낮게 보임
- `max: 2.399s`, `max: 3.468s` 같은 큰 간격이 관찰됨

### 7-2. 해석

이 패턴은 아래를 의미한다.

1. 카메라 설정 자체는 정상
2. 작은 메타데이터 토픽은 정상
3. 큰 이미지 토픽만 느리게 보임

즉, 카메라가 아예 느린 것보다는:

- 큰 이미지 토픽 구독 부담
- Python CLI 측정 한계
- 시각화/구독 노드 backlog

가능성이 더 커진다.

### 7-3. 중요한 주의

`ros2 topic hz`는 큰 이미지 토픽에서 항상 믿을 만한 절대 기준은 아니다.

왜냐하면:

- Python 구독자다
- 역직렬화 비용이 크다
- 큰 `sensor_msgs/Image`에서 병목이 생길 수 있다

즉, `ros2 topic hz` 결과만 보고 "센서가 4Hz밖에 안 나온다"고 단정하면 안 된다.

---

## 8. 6차 조치: depth 처리 코드 최적화

### 8-1. 컬러맵 시각화 노드 추가

사람이 보기 쉽게 depth를 색으로 바꿔주는 노드를 만들었다.

파일:

- [`06_Debugging/depth_colormap_publisher.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py)

역할:

- 입력: `/camera/camera/depth/image_rect_raw`
- 출력: `/camera/camera/depth/image_colormap`

의미:

- 원본 depth는 유지
- 사람 눈으로 확인할 때만 컬러맵 사용

### 8-2. 로컬 맵 GUI 노드 최적화

depth와 IMU를 이용한 로컬 탑뷰 맵 실험용 GUI 노드를 만들고, 나중에 최적화했다.

파일:

- [`06_Debugging/depth_imu_local_mapper.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_imu_local_mapper.py)

개선한 핵심:

1. `sensor_data QoS` 사용
2. depth 콜백에서 무거운 처리를 바로 하지 않음
3. **최신 프레임만 저장**
4. 타이머로 주기적으로 최신 프레임만 처리

이유:

- 모든 프레임을 다 처리하려고 하면 backlog가 쌓인다
- 그러면 실제 실시간성이 아니라 "과거 프레임을 뒤늦게 처리"하게 된다

### 8-3. 부가 도구

진단용으로 아래 스크립트도 추가했다.

- [`06_Debugging/ros2_raw_rate_probe.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/ros2_raw_rate_probe.py)

이건 큰 토픽의 수신률을 더 가볍게 보기 위해 만든 임시 도구였다.

---

## 9. 7차 조치: 해상도와 FPS를 낮춘 저대역폭 실행 모드 추가

### 9-1. 배경

depth는 이미지 크기가 커서:

- USB 대역폭
- ROS2 구독
- Python 처리
- GUI 렌더링

모두에 부담을 준다.

따라서 가장 실용적인 대응은 **해상도와 FPS를 낮춰 연속성을 먼저 확보하는 것**이다.

### 9-2. 추가한 실행 스크립트

파일:

- [`06_Debugging/run_d435i_depth_low_bandwidth.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh)

기본 실행:

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh
```

기본 프로파일:

```text
424x240x15
```

더 낮춘 테스트:

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh 424x240x6
```

### 9-3. 스크립트 수정 이력

처음에는 스크립트에서 아래 오류가 났다.

```text
/opt/ros/humble/setup.bash: line 8: AMENT_TRACE_SETUP_FILES: unbound variable
```

원인:

- `set -u` 상태에서 ROS setup을 `source`했기 때문

조치:

- `source` 전에 `set -u`를 켜지 않도록 스크립트를 수정

### 9-4. 결과

실제로 아래 로그까지 확인했다.

```text
Open profile: stream_type: Depth(0), Format: Z16, Width: 424, Height: 240, FPS: 15
RealSense Node Is Up!
```

즉, 저대역폭 모드 자체는 정상적으로 동작한다.

---

## 10. 현재 안정 실행 절차

현재 기준으로 가장 안전한 실행 순서는 아래다.

### Step 1. 중복 프로세스 정리

```bash
pkill -f 'realsense2_camera|rs_launch.py|realsense-viewer|depth_imu_local_mapper|ros2 topic hz|rqt_image_view|rviz2'
```

### Step 2. depth-only 저대역폭 실행

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh
```

필요하면:

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh 424x240x6
```

### Step 3. 컬러맵 퍼블리셔 실행

```bash
python3 /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py
```

### Step 4. 화면 보기

```bash
ros2 run rqt_image_view rqt_image_view
```

선택 토픽:

```text
/camera/camera/depth/image_colormap
```

주의:

- `realsense-viewer`와 `ros2 launch`를 동시에 켜지 않는다
- `ros2 topic hz`를 여러 개 동시에 켜지 않는다
- 같은 터미널에서 퍼블리셔와 뷰어를 연속 실행하지 않는다

---

## 11. Windows로 바꾸면 해결되는가

결론은 **아니다**.

- Windows에서 D435i SDK 자체는 돌 수 있다
- 하지만 ROS2와 `realsense2_camera` 기준에서 **실시간 보장**을 해주지는 않는다
- 이번 문제의 핵심도 운영체제보다:
  - 중복 실행
  - 권한
  - 이미지 토픽 처리 부담
  쪽이었다

즉, 지금 문제를 Windows로 옮겨서 해결하려는 접근은 우선순위가 낮다.

---

## 12. 최종 정리

이번 트러블슈팅으로 정리된 핵심은 아래다.

1. D435i 자체가 느린 것이 아니었다
2. IMU 끊김은 카메라 충돌과 권한 문제의 영향이 컸다
3. `udev rules` 적용은 실제로 중요했다
4. `realsense-viewer`와 `rs_launch.py` 동시 실행은 피해야 한다
5. 큰 depth 이미지 토픽은 `ros2 topic hz` 결과만 보고 단정하면 안 된다
6. 연속성이 떨어질 때는 해상도/FPS를 낮추는 것이 가장 실용적이다
7. GUI/맵퍼 코드는 **최신 프레임만 처리**하는 구조가 맞다

한 줄 요약:

> 이번 문제의 본질은 "센서가 2초마다만 보내는가?"가 아니라, "실행 환경을 깨끗하게 정리하고, 큰 depth 토픽을 감당할 수 있는 방식으로 다루고 있는가?"였다.
