# 2026-04-14 작업 일지

## 결론

- 동일 회전 속도와 동일 동선으로 재시험한 결과, 현재 기준 최적 세팅은 `후보 3`으로 판단했다.
- 최종 우선순위는 `후보 3 > 후보 4 > 후보 2 > 후보 1`이다.
- 후보 2와 후보 4는 `IMU ON` 설정이지만, D435i IMU 메시지에 `orientation`이 없어 RTAB-Map에서 실제 IMU 자세 보정은 적용되지 않았다.
- 완성형 로봇에서 `BNO08x`가 `orientation`을 제공하면 VSLAM과 자율주행에서 자세 안정화에 충분히 활용 가치가 있다. 다만 절대 `yaw` 신뢰도와 프레임 정합은 별도 검증이 필요하다.

## 오늘 작업 한 줄 요약

- 후보 1~4를 동일 회전 조건으로 다시 비교해 공정한 기준으로 우선순위를 재정리했다.
- 왜 이 작업을 먼저 했는가?
  - 이전 비교는 후보 3에서 더 빠르게 회전해 조건이 달랐고, 그 상태로는 세팅 차이와 조작 차이를 분리할 수 없었기 때문이다.

## 시간순 기록

### 09:04

- 후보 1을 동일 회전 조건으로 재시험했다.
- 초반에는 동작했지만 약 48초 이후부터 `quality=0`과 `Image 0 is ignored`가 반복되기 시작했다.
- 같은 동선 기준에서도 후보 1은 장기 안정성이 부족하다고 판단했다.

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh 640x480x15 640x480x15 false
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh 3 relaxed false 2>&1 | tee ~/rtabmap_candidate1_retest.log
```

### 09:08

- 후보 3을 동일 회전 조건으로 재시험했다.
- 이번에는 거의 끝까지 non-zero `quality`가 유지되었고, `quality=0`은 초기 1회만 확인됐다.
- 속도도 후보 1보다 빨랐고, 프레임 무시도 없었다.

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 false
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed false 2>&1 | tee ~/rtabmap_candidate3_retest.log
```

### 09:14

- 후보 2를 재시험해 `IMU ON`이 실제로 의미가 있는지 확인했다.
- 로그상 `IMU received doesn't have orientation set, it is ignored`가 대량 발생했다.
- 후보 1보다는 낫지만, IMU 효과가 아니라 동일 조건 재시험 결과로 보는 것이 맞다.

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh 640x480x15 640x480x15 true
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh 3 relaxed true 2>&1 | tee ~/rtabmap_candidate2_retest.log
```

### 09:19

- 후보 4를 재시험해 후보 3과 `IMU ON/OFF` 차이만 비교했다.
- 후보 4도 안정적으로 동작했지만, IMU는 계속 ignored 상태였다.
- 숫자상 후보 3과 거의 비슷했으나, 로그가 훨씬 지저분해 후보 3을 최종 1순위로 유지했다.

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 true
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed true 2>&1 | tee ~/rtabmap_candidate4_retest.log
```

## 오늘 관찰한 핵심 현상

- 재시험 기준 비교 결과:

| 후보 | 세팅 | `quality=0` | `Registration failed` | `Image 0 is ignored` | IMU ignored 로그 | 평균 `quality` | 평균 `update time` | 평균 `delay` | non-zero 유지 시간 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `640x480x15`, IMU OFF, Rate=3 | 363 | 376 | 141 | 0 | 324.4 | `0.027321s` | `0.093696s` | `47.557s` |
| 2 | `640x480x15`, IMU ON, Rate=3 | 172 | 201 | 29 | 74133 | 334.4 | `0.026016s` | `0.094932s` | `184.393s` |
| 3 | `424x240x15`, IMU OFF, Rate=2 | 1 | 1 | 0 | 0 | 186.8 | `0.016864s` | `0.080959s` | `184.586s` |
| 4 | `424x240x15`, IMU ON, Rate=2 | 1 | 0 | 0 | 73580 | 192.1 | `0.017037s` | `0.083310s` | `183.994s` |

- 후보 3과 후보 4는 모두 안정적이었지만, 후보 4는 IMU ignored 경고가 매우 많았다.
- 후보 1은 평균 `quality` 자체는 높지만, 동일 조건 재시험에서는 빠르게 붕괴했다.
- 후보 2는 후보 1보다 좋아졌지만, IMU가 실제로 쓰인 결과는 아니었다.

## 원인 가설

- 초기에는 `640x480x15`가 무조건 더 좋다고 생각했다.
- 하지만 이전 비교에서 후보 3을 더 빠르게 회전시켜 세팅 차이와 조작 차이가 섞여 있었다.
- 동일 회전 조건으로 다시 보니, 저해상도 세팅이 더 빠르고 안정적으로 유지될 수 있다는 점이 드러났다.
- 또한 IMU ON 후보가 나아 보이는 구간이 있어도, 그 원인을 IMU 효과로 해석하면 안 된다는 점을 확인했다.

## 확인 방법

- 각 후보를 동일 동선, 동일 회전 속도, 동일 테스트 시간으로 재실행했다.
- 비교 로그에서 아래 항목을 직접 셌다.
  - `quality=0`
  - `Registration failed`
  - `Image 0 is ignored`
  - `Did not receive data since 5 seconds`
  - `IMU received doesn't have orientation set`
- 또한 non-zero `quality` 구간의 평균 `quality`, 평균 `update time`, 평균 `delay`, 유지 시간을 계산해 비교했다.

## 해결 방법

- 로그 비교 기준을 `순간 속도`에서 `연속 운용 안정성`으로 명확히 바꿨다.
- 최종 기준 세팅을 `후보 3`으로 정리했다.
  - `424x240x15`
  - IMU OFF
  - `Rtabmap/DetectionRate=2`
- IMU ON 후보는 raw IMU는 들어오지만 `orientation`이 없어 RTAB-Map에서 무시된다는 해석 기준을 문서화했다.

## 오늘 배운 것

- D435i IMU는 raw 값(`gyro`, `accel`)은 들어와도, 현재 메시지에는 `orientation`이 없어서 RTAB-Map이 자세 보정에 바로 쓰지 못한다.
- 따라서 현재 후보 2, 4의 결과는 IMU 성능 비교가 아니라 `IMU ON 설정 상태의 실험` 정도로만 해석해야 한다.
- 평균 `quality`가 높다고 해서 항상 더 좋은 세팅은 아니다.
  - 오래 버티는지
  - 프레임 무시가 없는지
  - `quality=0`이 얼마나 적은지
  를 함께 봐야 한다.

## BNO08x 활용 메모

- `BNO08x`는 센서 내부에서 자세 추정(fusion)을 수행해 `orientation`을 직접 줄 수 있는 IMU다.
- 이 값이 안정적으로 들어오면 다음 용도로 활용 가치가 높다.
  - `roll`, `pitch` 안정화
  - 회전 시작/종료 구간의 자세 보조
  - VSLAM 또는 EKF에서 단기 자세 추정 보강
- 특히 자율주행에서는 다음에 도움이 된다.
  - 경사로/턱 등에서 기울기 인식
  - 회전 중 자세 변화 보조
  - 비전이 약한 순간의 자세 추정 보완
- 다만 주의할 점도 있다.
  - `yaw`는 절대 방향 기준이 약하면 시간이 지나며 틀어질 수 있다.
  - IMU 프레임과 `base_link` 프레임이 정확히 맞아야 한다.
  - timestamp 동기화가 안 맞으면 오히려 추정이 흔들릴 수 있다.
- 실무 권장 해석:
  - `BNO08x orientation`은 **매우 유용하다**
  - 하지만 **비전/휠/GPS와 함께 융합할 때 가장 효과적**이고, IMU 단독 절대 자세로 과신하면 안 된다.

## BNO08x 하드웨어 배치 권장

- 현재 구조에서는 `BNO08x`를 **차체 중심부의 단단한 상판**, 즉 `base_link`에 가까운 위치에 두는 것이 가장 실용적이다.
- 센서 축은 가능하면 ROS 기준인 `x` 전방, `y` 좌측, `z` 상방과 물리적으로 맞추는 것이 좋다.
- 모터, 모터 드라이버, 고전류 전원선, 자성체 브래킷 근처는 피해야 한다.
- 카메라 암 끝단처럼 흔들리는 곳보다, 차체 중심에 가까운 강체 프레임이 낫다.
- 이유:
  - body IMU로 해석하기 쉽다
  - EKF와 `base_link` 정합이 단순하다
  - `yaw` 자기장 간섭 위험을 줄일 수 있다
  - 자세 기준이 흔들리지 않는다
- 예외:
  - 나중에 카메라-IMU 강결합 VIO를 할 계획이면, 그때는 카메라 가까운 별도 IMU를 두는 것이 더 유리하다.
- 관련 정리 문서:
  - [BNO08x IMU 배치 가이드](../../docs/learning/BNO08x_IMU_Placement_Guide.md)

## 오늘 만든/수정한 파일

- [재시험 로그 폴더 README](../../assets/2026-04-14_rtabmap_retest_logs/README.md)
- [BNO08x IMU 배치 가이드](../../docs/learning/BNO08x_IMU_Placement_Guide.md)
- [2026-04-14 일지](./README.md)
- [2026-04-13 일지](../2026-04-13/README.md)

## 증빙 자료

- [후보 1 재시험 로그](../../assets/2026-04-14_rtabmap_retest_logs/rtabmap_candidate1_retest.log)
- [후보 2 재시험 로그](../../assets/2026-04-14_rtabmap_retest_logs/rtabmap_candidate2_retest.log)
- [후보 3 재시험 로그](../../assets/2026-04-14_rtabmap_retest_logs/rtabmap_candidate3_retest.log)
- [후보 4 재시험 로그](../../assets/2026-04-14_rtabmap_retest_logs/rtabmap_candidate4_retest.log)

## 남은 문제

- 현재 D435i IMU는 `orientation`이 없어 RTAB-Map에서 계속 ignored 된다.
- 후보 3이 현 기준 최선이지만, 장시간 주행과 다른 동선에서도 같은 결과가 나오는지 추가 확인이 필요하다.
- 완성형 로봇에서 BNO08x를 붙였을 때, 실제 `yaw` 안정성과 좌표계 정합이 얼마나 좋은지 아직 검증하지 않았다.

## 다음 액션

1. 후보 3을 기준 세팅으로 고정하고 다른 동선에서도 재현되는지 추가 검증한다.
2. 완성형 로봇에서 BNO08x `orientation`을 ROS 2 `sensor_msgs/Imu`로 publish해 실제 RTAB-Map 또는 EKF에 연결한다.
3. 하드웨어 팀과 BNO08x 실제 장착 위치를 확정하고, 다음 회고에서는 `IMU 프레임`, `base_link`, timestamp sync, `yaw` drift를 우선 확인한다.

## 한 줄 회고

- 공정한 재시험을 해보니, 이번 기준에서는 고해상도보다 저해상도 저부하 세팅이 더 실용적이었다.
