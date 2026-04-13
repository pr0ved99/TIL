# RTAB-Map 세팅 비교 실험 계획

## 결론

- 다양한 세팅을 비교하려면 **실험 표준화**가 먼저다.
- 비교 기준은 `속도(FPS/Hz)`, `안정성(quality/끊김)`, `정확도(드리프트 체감)`로 단순화한다.
- 오늘은 아래 실험 매트릭스와 기록 양식으로 진행한다.

## 1. 용어 정리 (짧게)

- `DetectionRate`: RTAB-Map이 맵을 갱신하는 주기(Hz).
- `quality`: rgbd_odometry가 출력하는 매칭 품질 지표(높을수록 좋음).
- `드리프트`: 제자리 회전/직진 후 위치가 틀어지는 현상.
- `끊김`: 맵이 멈추거나 프레임이 버려지는 현상.

## 2. 실험 기본 조건 고정

아래는 **모든 실험에서 동일하게 유지**한다.

- 동일한 실내 구간, 동일한 조명
- 동일한 이동 패턴(직진 10초 → 좌회전 10초 → 제자리 회전 10초)
- RTAB-Map GUI는 `rtabmap_viz`만 사용
- `realsense-viewer`, `rviz2`는 모두 끔

## 3. 비교 변수

이번 실험에서 바꿀 변수는 아래 4개만 쓴다.

1. 해상도/FPS
2. IMU ON/OFF
3. DetectionRate
4. odom profile(`relaxed` 고정)

## 4. 실험 매트릭스

### A. 기본 4개

1. `640x480x15`, IMU OFF, DetectionRate=3
2. `640x480x15`, IMU ON, DetectionRate=3
3. `424x240x15`, IMU OFF, DetectionRate=2
4. `424x240x15`, IMU ON, DetectionRate=2

### B. 무거운 비교군 2개

5. `1280x720x30(color) / 848x480x30(depth)`, IMU ON, DetectionRate=3
6. `1280x720x15(color) / 848x480x15(depth)`, IMU ON, DetectionRate=3

## 5. 실행 명령 템플릿

### 카메라 실행

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh <COLOR> <DEPTH> <IMU>
```

예:
```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh 640x480x15 640x480x15 false
```

### RTAB-Map 실행

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh <RATE> relaxed <IMU>
```

예:
```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh 3 relaxed false
```

## 6. 평가 기준 (정량 + 정성)

### 정량 기준

- `quality` 범위: 예) `150~250`
- `quality=0` 발생 빈도
- `RTAB-Map detection rate` 로그 (1Hz/2Hz/3Hz)
- CPU 사용률(대략): `top`에서 rtabmap/rtabmap_viz 확인

### 정성 기준

- 맵 끊김 여부
- 제자리 회전 시 맵 찢어짐
- 직진/회전 시 추정이 튀는지

## 7. 기록 양식 (한 줄씩)

아래 포맷으로 기록한다.

```
세팅: <COLOR>/<DEPTH> | IMU=<ON/OFF> | Rate=<Hz>
결과: quality=<min~max>, 끊김=<있음/없음>, 체감속도=<빠름/보통/느림>, CPU=<높음/보통/낮음>
```

## 8. 최적 세팅 선정 규칙

가장 우선하는 조건:

1. 끊김이 없는 세팅
2. `quality`가 안정적으로 유지되는 세팅
3. 체감 속도가 빠른 세팅
4. CPU 부담이 과하지 않은 세팅

즉, **속도보다 안정성을 먼저**, 그 다음에 속도와 부하를 본다.

## 9. 다음 액션

1. 매트릭스 A부터 4개 실험 실행
2. 기록 양식으로 결과 남기기
3. 가장 좋은 1개를 후보로 선정
4. 후보 1개에 대해 5분 이상 연속 주행 테스트
