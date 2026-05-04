# D435i IMU 토픽 확인과 활성화 가이드

## 결론

D435i는 IMU가 들어 있는 모델이라 `realsense2_camera`에서 IMU 관련 토픽을 볼 수 있다.  
다만 기본 실행에서는 IMU가 꺼져 있을 수 있어서, **`enable_gyro:=true`, `enable_accel:=true`를 명시해서 켜는 것이 안전하다.**

현재 이 환경에서 확인한 기준:

- IMU 활성화 파라미터 이름은 `enable_gyro`, `enable_accel`, `unite_imu_method`가 맞다
- IMU 활성화 시 `Motion Module`이 시작되는 로그를 확인했다
- 다만 현재 PC 환경에서는 IMU 쪽에서 `Permission denied`가 발생해 정상 publish까지는 확인되지 않았다

즉, **파라미터와 실행 방법은 확인됐고, 실제 IMU publish는 권한 문제를 먼저 해결해야 할 수 있다.**

---

## 1. 먼저 알아야 하는 개념

- `IMU`: 가속도계와 자이로를 묶어서 부르는 센서다
- `가속도(accel)`: 얼마나 가속되는지 측정한다
- `자이로(gyro)`: 얼마나 회전하는지 측정한다
- `unite_imu_method`: accel과 gyro를 하나의 IMU 스트림으로 합치는 방법이다

---

## 2. 기본 launch에서는 왜 IMU 토픽이 안 보일 수 있는가

우리가 처음 쓴 명령은 아래였다.

```bash
ros2 launch realsense2_camera rs_launch.py enable_color:=true enable_depth:=true
```

이 명령은 color와 depth만 명시적으로 켠다.  
즉, IMU는 기본값이 `false`일 수 있어서 토픽이 안 보이는 것이 이상한 상황이 아니다.

실제로 현재 설치된 launch 파일에서 확인한 기본값:

- `enable_gyro`: `false`
- `enable_accel`: `false`
- `unite_imu_method`: `0`

---

## 3. IMU를 켜는 정확한 명령

현재 설치된 `rs_launch.py` 기준으로 IMU까지 켜는 명령은 아래와 같다.

```bash
source /opt/ros/humble/setup.bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_gyro:=true \
  enable_accel:=true \
  unite_imu_method:=1
```

각 파라미터 의미:

- `enable_gyro:=true`: 자이로 스트림 켜기
- `enable_accel:=true`: 가속도 스트림 켜기
- `unite_imu_method:=1`: IMU 통합 방법 설정
  - `0`: 합치지 않음
  - `1`: copy
  - `2`: linear interpolation

초보자 기준 추천:

- 먼저 `gyro`, `accel` 토픽이 각각 뜨는지 확인
- 그 다음 필요하면 `unite_imu_method`를 조정

---

## 4. 기대하는 IMU 토픽

환경에 따라 조금 다를 수 있지만, 보통 아래를 먼저 기대하면 된다.

```text
/camera/camera/gyro/sample
/camera/camera/accel/sample
```

추가로 환경과 설정에 따라 아래 토픽이 붙을 수도 있다.

```text
/camera/camera/imu
```

중요:
토픽 이름은 버전과 설정에 따라 달라질 수 있으니, **반드시 실제 환경에서 `ros2 topic list`로 확인**하는 것이 맞다.

---

## 5. IMU 토픽 확인 방법

### 5-1. 토픽 목록 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E 'gyro|accel|imu'
```

### 5-2. 메시지 한 번 보기

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /camera/camera/gyro/sample --once
ros2 topic echo /camera/camera/accel/sample --once
```

### 5-3. 토픽 타입 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic info /camera/camera/gyro/sample
ros2 topic info /camera/camera/accel/sample
```

---

## 6. 현재 환경에서 실제로 확인된 로그

IMU를 켜고 실행했을 때 아래 로그가 확인됐다.

```text
Set ROS param gyro_fps to default: 200
Set ROS param accel_fps to default: 63
Starting Sensor: Motion Module
```

이건 의미상 다음을 뜻한다.

- launch 파라미터는 정상 인식됐다
- Motion Module 시작도 시도됐다

즉, **IMU 활성화 명령 자체는 맞다.**

---

## 7. 현재 환경에서 막힌 지점

현재 PC 환경에서는 IMU 쪽에서 아래와 같은 에러가 확인됐다.

```text
Failed to open scan_element ... Permission denied
```

쉽게 말하면:

- D435i IMU 장치 접근은 시도했지만
- 현재 사용자 권한 또는 장치 접근 권한 때문에 IMU publish가 막힐 수 있다는 뜻이다

즉, 지금은 **토픽 이름과 활성화 방법은 문서화 가능하지만, 실제 IMU 메시지 publish까지는 권한 문제를 먼저 확인해야 한다.**

---

## 8. 디버깅할 때 먼저 볼 것

IMU가 안 보이면 아래 순서로 확인한다.

1. launch에 `enable_gyro:=true`, `enable_accel:=true`를 넣었는가
2. launch 로그에 `Starting Sensor: Motion Module`이 보이는가
3. `ros2 topic list | grep -E 'gyro|accel|imu'` 결과가 있는가
4. 권한 에러(`Permission denied`)가 있는가
5. USB 연결이 불안정하지 않은가

---

## 9. VSLAM 관점에서 IMU를 볼 때 주의할 점

IMU 토픽이 보인다고 바로 잘 쓰는 것은 아니다.

꼭 같이 봐야 하는 것:

1. `timestamp`
   - 카메라와 시간이 맞는가
2. `frame_id`
   - 어떤 좌표계 기준인가
3. 축 방향
   - x, y, z가 내가 기대한 방향과 같은가
4. 노이즈
   - 정지 상태에서도 흔들림이 큰가

즉, IMU는 **토픽 존재 확인 -> 시간 확인 -> 축 방향 확인 -> 융합** 순서로 보는 게 맞다.

---

## 10. 최소 확인 명령 모음

### IMU 포함 launch

```bash
source /opt/ros/humble/setup.bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_gyro:=true \
  enable_accel:=true \
  unite_imu_method:=1
```

### IMU 토픽 검색

```bash
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E 'gyro|accel|imu'
```

### gyro 메시지 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /camera/camera/gyro/sample --once
```

### accel 메시지 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /camera/camera/accel/sample --once
```

