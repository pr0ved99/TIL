# 2026-04-13 작업 일지

## 결론

- D435i RGB-D 카메라가 `640x480x15`로 정상 기동됨을 확인했다.
- USB 타입이 실행마다 달랐다: 과거 실행에서는 `2.1`, 최근 로그에서는 `3.2`로 확인됨.
- 이번 실행은 `IMU 비활성` 상태다.

## 실행 명령

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh 640x480x15 640x480x15 false
```

## 로그 핵심 요약 (필요 부분만)

- `RealSense Node Is Up!`
- `Device Name: Intel RealSense D435I`
- `Device Serial No: 116622071600`
- `Device USB type: 3.2`
- `Device with port number 4-2`
- `Sync Mode: On`
- `Depth: 640x480x15`
- `Color: 640x480x15`
- `IMU enabled: false`

## 다음 체크

1. USB 3.x 포트/케이블로 연결 상태 개선
2. RTAB-Map 실행 후 `quality`, `delay`, `update time` 기록

## 카메라 실행 로그 요약 (IMU ON)

- `IMU enabled: true`
- `Device USB type: 3.2`
- `Sync Mode: On`
- `Depth: 640x480x15`
- `Color: 640x480x15`
- `Accel: 63 FPS`
- `Gyro: 200 FPS`
- `IMU Calibration is not available` 경고 발생

## RTAB-Map 로그 요약 (세팅: 640x480x15, IMU OFF, Rate=3)

- `quality`: 대략 `253 ~ 379`
- `update time`: 약 `0.016 ~ 0.045s`
- `delay`: 약 `0.084 ~ 0.113s`
- `rtabmap Rate`: `0.33s` (≈ 3Hz)
- `rtabmap delay`: 약 `0.12 ~ 0.77s`

## RTAB-Map 로그 요약 (세팅: 640x480x15, IMU ON, Rate=3)

- IMU 경고 다수: `IMU received doesn't have orientation set! It is ignored.`
- 원인: D435i IMU는 `orientation`을 제공하지 않음(값 0, covariance -1).
- 영향: RTAB-Map에서 IMU 입력이 **무시됨**. 즉 IMU ON이어도 실제 보정 효과는 없음.
- `quality`: 대략 `226 ~ 262`
- `update time`: 약 `0.041 ~ 0.050s`
- `delay`: 약 `0.111 ~ 0.120s`
- `rtabmap Rate`: `0.33s` (≈ 3Hz)

## 카메라 실행 로그 요약 (세팅: 424x240x15, IMU OFF)

- `IMU enabled: false`
- `Device USB type: 3.2`
- `Sync Mode: On`
- `Depth: 424x240x15`
- `Color: 424x240x15`

## RTAB-Map 로그 요약 (세팅: 424x240x15, IMU OFF, Rate=2)

- `quality`: 대략 `91 ~ 143`
- `update time`: 약 `0.033 ~ 0.079s`
- `delay`: 약 `0.100 ~ 0.147s`
- `rtabmap Rate`: `0.50s` (≈ 2Hz)
- `rtabmap delay`: 약 `0.118 ~ 0.162s`
- `local map / WM`: `15 / 15`

## 카메라 실행 로그 요약 (세팅: 424x240x15, IMU ON)

- `IMU enabled: true`
- `Device USB type: 3.2`
- `Sync Mode: On`
- `Depth: 424x240x15`
- `Color: 424x240x15`
- `Accel: 63 FPS`
- `Gyro: 200 FPS`
- `IMU Calibration is not available` 경고 발생

## RTAB-Map 로그 요약 (세팅: 424x240x15, IMU ON, Rate=2)

- IMU 경고 다수: `IMU received doesn't have orientation set! It is ignored.`
- 원인: D435i IMU는 `orientation`을 제공하지 않음(값 0, covariance -1).
- 영향: RTAB-Map에서 IMU 입력이 **무시됨**. 즉 IMU ON이어도 실제 보정 효과는 없음.
- `quality`: 대략 `140 ~ 165`
- `update time`: 약 `0.025 ~ 0.030s`
- `delay`: 약 `0.094 ~ 0.110s`
- `rtabmap Rate`: `0.50s` (≈ 2Hz)
- `rtabmap delay`: 약 `0.122s`
- `local map / WM`: `34 / 34`

## 카메라 실행 로그 요약 (세팅: 1280x720x30 / 848x480x30, IMU ON)

- `IMU enabled: true`
- `Device USB type: 3.2`
- `Sync Mode: On`
- `Depth: 848x480x30`
- `Color: 1280x720x30`
- `Accel: 63 FPS`
- `Gyro: 200 FPS`
- `IMU Calibration is not available` 경고 발생

## RTAB-Map 로그 요약 (세팅: 1280x720x30 / 848x480x30, IMU ON, Rate=3)

- IMU 경고 다수: `IMU received doesn't have orientation set! It is ignored.`
- 원인: D435i IMU는 `orientation`을 제공하지 않음(값 0, covariance -1).
- 영향: RTAB-Map에서 IMU 입력이 **무시됨**. 즉 IMU ON이어도 실제 보정 효과는 없음.
- `quality`: `0` 발생 (매칭 실패: inliers 부족)
- `update time`: 약 `0.078 ~ 0.084s`
- `delay`: 약 `0.124 ~ 0.127s`

## 카메라 실행 로그 요약 (세팅: 1280x720x15 / 848x480x15, IMU ON)

- `IMU enabled: true`
- `Device USB type: 3.2`
- `Sync Mode: On`
- `Depth: 848x480x15`
- `Color: 1280x720x15`
- `Accel: 63 FPS`
- `Gyro: 200 FPS`
- `IMU Calibration is not available` 경고 발생

## RTAB-Map 로그 요약 (세팅: 1280x720x15 / 848x480x15, IMU ON, Rate=3)

- IMU 경고 다수: `IMU received doesn't have orientation set! It is ignored.`
- 원인: D435i IMU는 `orientation`을 제공하지 않음(값 0, covariance -1).
- 영향: RTAB-Map에서 IMU 입력이 **무시됨**. 즉 IMU ON이어도 실제 보정 효과는 없음.
- `quality`: `0` 발생 (매칭 실패: inliers 부족)
- `update time`: 약 `0.071 ~ 0.074s`
- `delay`: 약 `0.148 ~ 0.155s`
- `rtabmap delay`: 약 `0.150 ~ 0.690s`
- `local map / WM`: `28 / 28`
