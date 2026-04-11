# 현재 진행상황 및 문제점 정리

## 결론

- 현재 프로젝트는 `센서 bring-up(Stage 0)`의 후반부에 있다.
- `D435i depth`와 `IMU`는 ROS2에서 안정적으로 읽히는 상태까지 왔다.
- 지금 새로 시도 중인 것은 `D435i 단독 RGB-D 3D 맵핑`이다.
- 다만 `RTAB-Map` 기반 3D 맵은 아직 "성공적으로 돌아는 가지만 충분히 부드럽지는 않은 상태"다.

즉, 지금 단계는 `센서가 들어오는지 확인하는 수준`은 넘었고,
`실제로 3D 맵을 만들되 속도와 안정성을 맞추는 단계`로 들어간 상태다.

---

## 1. 현재 프로젝트 위치

전체 로드맵 기준으로 보면 지금은 아래 위치다.

- `Stage 0`: 센서 입력 확인과 실행 환경 준비
  - 현재 진행 중
- `Stage 1`: 로봇 모델링과 시뮬레이션
  - 아직 본격 시작 전

현재 Stage 0 안에서도 세부적으로는 이렇게 나뉜다.

1. D435i depth 입력 확인
2. D435i depth 시각화
3. D435i IMU 입력 확인
4. D435i 연속성/실시간성 문제 해결
5. D435i 단독 3D 맵핑 첫 시도

즉, 지금은 `센서 bring-up` 안에서도 거의 마지막 단계인 `실사용 수준 검증`에 가까워지고 있다.

---

## 2. 설치/적용 누락과 영향

이번 bring-up에서 실제로 막혔던 것은 아래 3가지였다.

### 2-1. `realsense2_camera` 미설치

- 쉬운 말:
  - D435i 데이터를 ROS2 토픽으로 바꿔주는 드라이버가 없었던 상태다.
- 왜 문제였나:
  - 이게 없으면 D435i를 연결해도 `/camera/...` 토픽이 생성되지 않는다.
  - 즉, `depth`, `color`, `IMU` 확인 자체를 시작할 수 없다.

### 2-2. `v4l-utils` 미설치

- 쉬운 말:
  - `v4l2-ctl` 같은 카메라 진단 도구가 들어 있는 패키지가 없었던 상태다.
- 왜 문제였나:
  - 공식 `setup_udev_rules.sh` 스크립트가 내부적으로 `v4l2-ctl`을 확인하는데, 이게 없어서 스크립트가 중간에 멈췄다.
  - 결과적으로 `udev rules` 설치가 진행되지 않았다.

### 2-3. `udev rules` 미적용

- 쉬운 말:
  - 리눅스가 RealSense USB/HID 장치에 어떤 권한으로 접근할지 정하는 규칙이 시스템에 없었던 상태다.
- 왜 문제였나:
  - `realsense-viewer`에서 `UDEV-Rules are missing!` 경고가 떴다.
  - IMU/HID 쪽에서 `Permission denied`, `scan_element` 접근 실패가 발생할 수 있었다.
  - 즉, IMU publish 불안정과 권한 문제의 직접 원인 후보였다.

정리하면:

- `realsense2_camera` 없음 -> ROS2 토픽 자체를 못 봄
- `v4l-utils` 없음 -> `udev rules` 설치 스크립트가 실패함
- `udev rules` 없음 -> IMU/HID 권한 문제가 생김

---

## 3. 현재까지 완료된 것

### 3-1. D435i 기본 입력 확인

완료된 것:

- `realsense2_camera` 설치
- D435i 장치 인식 확인
- color/depth 토픽 생성 확인
- depth 시각화 확인

확인된 대표 토픽:

- `/camera/camera/color/image_raw`
- `/camera/camera/color/camera_info`
- `/camera/camera/depth/image_rect_raw`
- `/camera/camera/aligned_depth_to_color/image_raw`

증빙:

- [`assets/2026-04-09_task59_d435i_depth_check/README.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-09_task59_d435i_depth_check/README.md)

### 3-2. D435i IMU 확인

완료된 것:

- `gyro`, `accel`, `imu` 토픽 확인
- 실제 값 수신 확인
- 주파수 안정성 확인

관찰값:

- `gyro`: 약 `199.8 Hz`
- `accel`: 약 `62.4 Hz`
- `/camera/camera/imu`: 약 `199.8 Hz`

해석:

- IMU는 현재 환경 기준으로 정상 동작
- 이전의 끊김은 센서 자체보다 실행 환경 충돌 영향이 컸음

### 3-3. D435i 실시간성/연속성 문제 1차 해결

완료된 것:

- `udev rules` 적용
- 중복 실행 프로세스 정리
- `realsense-viewer`와 ROS2 동시 실행 금지 규칙 정리
- depth 저대역폭 실행 스크립트 추가

추가한 실행 스크립트:

- [`run_d435i_depth_low_bandwidth.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh)

현재 안정적으로 쓰는 방식:

- `424x240x15` 또는 `424x240x6`
- `depth-only`
- 컬러맵 시각화 별도 실행

### 3-4. 시각화/디버깅 도구 정리

추가/수정한 코드:

- [`depth_colormap_publisher.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py)
- [`depth_imu_local_mapper.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_imu_local_mapper.py)
- [`ros2_raw_rate_probe.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/ros2_raw_rate_probe.py)

---

## 4. 지금 새로 진행 중인 것

현재는 `D435i 단독 RGB-D 3D 맵핑`을 시도하고 있다.

사용 중인 방향:

- `RGB + aligned depth`
- `RTAB-Map`
- `camera_link` 기준 프레임 사용

관련 새 스크립트:

- [`run_d435i_rgbd_mapping_camera.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh)
- [`run_d435i_rtabmap_light.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh)

현재 목표:

- 실내에서 D435i만으로 3D 맵이 실제로 쌓이는지 확인
- 맵이 너무 느리거나 끊기지 않는지 확인

---

## 5. 현재 문제점

### 문제 1. RTAB-Map 맵 갱신 속도가 느림

현재 가장 큰 문제다.

원인 후보:

1. `RTAB-Map` 기본 `DetectionRate=1Hz`
2. RGB-D 입력 자체가 무거움
3. GUI를 두 개 띄우면 더 느려짐
4. PC CPU 부하가 높음

실제 확인된 내용:

- launch 기본 상태에서 `RTAB-Map detection rate = 1.000000 Hz`
- 이후 경량 launch에서는 `3 Hz`로 올리는 방향 적용

### 문제 2. PC CPU 사용량이 높음

실제 확인:

- VS Code 프로세스가 CPU를 많이 사용 중
- `realsense2_camera_node` 자체보다 개발 도구 점유율이 더 큼

영향:

- `RTAB-Map`
- `rtabmap_viz`
- 이미지 구독

같은 GUI/영상 처리 노드에 부담이 갈 수 있음

### 문제 3. RGB 토픽도 생각보다 무거움

관찰:

- `ros2 topic hz /camera/camera/color/image_raw`가 기대보다 낮게 보였음

해석:

- color + depth + 정렬(aligned depth)까지 같이 쓰면 초반 실험치로는 무거울 수 있음

### 문제 4. 아직 "맵 완성 성공" 판정까지는 못 감

지금은:

- RTAB-Map이 실행됨
- odometry가 잡힘
- 3D 맵을 그릴 준비는 됨

하지만 아직 아래는 확정되지 않았다.

- 짧은 실내 구간에서 맵이 충분히 부드럽게 누적되는지
- loop 없이도 초기 구간이 안정적인지
- 현재 PC에서 실용적인 속도로 계속 쓸 수 있는지

즉, `실행 성공`과 `실사용 가능` 사이에서 아직 튜닝 중이다.

---

## 6. 현재 가장 유력한 원인 정리

지금까지의 로그와 관찰 기준으로 보면,
현재 느림의 우선순위는 아래처럼 본다.

1. `RTAB-Map detection rate` 기본값이 너무 낮음
2. `rviz + rtabmap_viz` 동시 사용 가능성
3. `640x480x15` RGB-D 조합이 현재 PC에는 무거움
4. VS Code 등 외부 CPU 부하

즉, 지금은 센서 권한 문제보다 **처리량과 시각화 부하 최적화**가 핵심이다.

---

## 7. 현재 적용한 대응

### 7-1. 카메라 쪽 경량화

현재 기본 시도 방향:

- `RGB`: `640x480x6`
- `Depth`: `640x480x6`
- `align_depth`: 켬
- IMU: 끔

실행 스크립트:

- [`run_d435i_rgbd_mapping_camera.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh)

### 7-2. RTAB-Map 쪽 경량화

적용한 것:

- `rtabmap_viz`만 사용
- `rviz:=false`
- `qos_image:=2`
- `qos_camera_info:=2`
- `Rtabmap/DetectionRate = 3Hz`

실행 스크립트:

- [`run_d435i_rtabmap_light.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh)

---

## 7. 현재 기준 추천 실행 절차

1. 기존 관련 프로세스 종료

```bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view'
```

2. RGB-D 카메라 경량 실행

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh
```

3. RTAB-Map 경량 실행

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh
```

또는 DetectionRate를 더 올려서 실험:

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh 5
```

---

## 8. 다음 액션

현재 가장 실용적인 다음 액션은 아래다.

1. `640x480x6` 기준으로 RTAB-Map 체감 속도 재확인
2. 아직 느리면 `424x240x6` RGB-D 설정으로 더 낮춰보기
3. VS Code 창/무거운 프로세스를 줄인 상태에서 다시 비교
4. 맵이 충분히 쌓이면 그때 실내 3D 맵 성공 증빙 캡처 정리

---

## 9. 지금 상태 한 줄 요약

지금은 `D435i 센서 bring-up`은 거의 끝났고, **`D435i 단독 3D 맵핑을 실용 속도로 돌리기 위한 경량화/튜닝 단계`**에 있다.
