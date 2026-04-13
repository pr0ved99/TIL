# 센서 융합 사전 템플릿

## 결론

- 이 폴더는 `wheel encoder`, `external IMU`, `GPS`가 도착했을 때 바로 실제 ROS2 패키지로 옮겨 쓸 수 있도록 만든 템플릿 모음이다.
- 지금 상태에서는 바로 실행하는 목적이 아니라, **토픽 이름과 설정 구조를 먼저 고정하는 용도**로 쓴다.
- 실제 적용할 때는 이 파일들을 이후 `trashbot_localization` 또는 `trashbot_bringup` 패키지의 `config/`, `launch/` 아래로 복사하면 된다.

## 포함된 파일

- `ekf_local.yaml`: wheel odom + IMU 기반 local EKF 템플릿
- `ekf_global.yaml`: local odom + GPS 기반 global EKF 템플릿
- `navsat_transform.yaml`: GPS를 로봇 기준으로 연결하는 템플릿
- `sensor_fusion_bringup.launch.py`: 위 설정을 묶어 띄우는 launch 템플릿

## 적용 전 확인할 것

1. 실제 토픽 이름이 아래와 일치하는가
   - `/wheel/odometry`
   - `/imu/data`
   - `/gps/fix`
   - `/odometry/local`
   - `/odometry/gps`
2. `imu_link`, `gps_link`, `base_link`가 URDF와 맞는가
3. IMU가 raw 값인지, orientation이 포함된 filtered 값인지
4. differential drive 기준 `two_d_mode`를 유지할 것인지

## 사용 순서

1. 하드웨어 드라이버 bring-up
2. 토픽 존재 확인
3. `ekf_local.yaml` 튜닝
4. `navsat_transform.yaml` 연결
5. `ekf_global.yaml` 튜닝

## 주의

- 이 템플릿은 **시작점**이다.
- 실제 하드웨어 driver의 frame, covariance, 토픽 이름에 맞게 반드시 수정해야 한다.
