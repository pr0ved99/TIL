# 17 Jetson BNO08x Temporary Mount and TF Guide

## 목적

- `BNO08x`를 아직 로봇에 정식 장착하지 않은 상태에서, `D435i`와 **임시로 단단히 같이 묶어** `RTAB-Map` 비교 실험을 할 수 있게 만든다.
- 핵심은 "`손으로 같이 들기`"가 아니라, **실험 중 상대 위치가 안 바뀌는 임시 강체 상태**를 만드는 것이다.

## 중요한 현재 판단

- 손으로 `D435i`와 `BNO08x`를 같이 잡고 실험하면, 카메라와 IMU의 상대 자세가 계속 바뀔 수 있다.
- 그 상태에서는 `IMU`가 실제로 도움이 되는지, 아니면 손떨림/상대 움직임이 들어간 건지 분리하기 어렵다.
- 따라서 현재 권장 최소 기준은 아래다.
  - `BNO08x`를 `D435i` 몸체에 테이프 또는 케이블타이로 임시 고정
  - 실험 중 상대 위치/각도를 바꾸지 않음

## 준비물

- 종이 테이프, 마스킹 테이프, 전기 테이프, 또는 케이블타이
- 가능하면 얇은 양면테이프
- 센서 보드가 흔들리지 않게 눌러 줄 작은 보강재가 있으면 더 좋음

## 1. 임시 고정 위치

현재 실험용으로는 아래가 가장 단순하다.

- `D435i` 윗면의 평평한 부분
- USB 케이블을 건드렸을 때 보드가 같이 흔들리지 않는 위치
- 렌즈/IR 창을 가리지 않는 위치

피할 것:

- 케이블에 매달린 상태
- 카메라 몸체 바깥으로 크게 튀어나오는 상태
- 손으로 쥐는 부분 위에 그대로 붙이는 상태

## 2. 권장 축 정렬

임시 실험 기준 추천:

- `BNO08x +X`가 카메라 전방과 최대한 같은 방향
- `BNO08x +Y`가 카메라 왼쪽
- `BNO08x +Z`가 위쪽

즉, 이상적인 목표는 아래와 같다.

```text
camera_link  : +X forward, +Y left, +Z up
imu_link     : +X forward, +Y left, +Z up
```

이렇게 붙이면 임시 비교 실험에서는 `camera_link -> imu_link`를 일단 `0 0 0 0 0 0`으로 두고 시작할 수 있다.

## 3. 지금 단계에서 허용하는 단순화

이번 임시 실험은 정확한 하드웨어 장착 검증이 아니라 "`IMU ON/OFF가 큰 방향으로 도움이 되는가`"를 보는 단계다.

그래서 아래 단순화를 허용한다.

- translation offset은 일단 `0 0 0`
- rotation offset도 **물리적으로 맞춰 붙였다면** 일단 `0 0 0`

주의:

- 이건 어디까지나 임시 비교 실험용이다.
- 나중에 정식 장착/융합 단계에서는 실제 위치와 회전을 다시 잡아야 한다.

## 4. 임시 고정 후 바로 확인할 것

1. 카메라를 기울일 때 IMU viewer도 같이 따라오는지
2. 센서 보드만 따로 흔들리는 느낌이 없는지
3. 케이블을 건드려도 상대 자세가 쉽게 바뀌지 않는지

## 5. static TF 실행

`BNO08x`를 위 권장 방향대로 맞춰 붙였다고 가정하면, 지금 단계에서는 아래처럼 시작한다.

```bash
source /opt/ros/humble/setup.bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 camera_link imu_link
```

의미:

- parent: `camera_link`
- child: `imu_link`
- translation: `0 0 0`
- rotation: `yaw pitch roll = 0 0 0`

## 6. TF가 보이는지 확인

새 터미널:

```bash
source /opt/ros/humble/setup.bash
ros2 run tf2_ros tf2_echo camera_link imu_link
```

기대:

- transform이 바로 보임
- 모두 0 근처로 나옴

## 7. 만약 축을 완전히 못 맞춰 붙였다면

임시로는 아래처럼 정리한다.

- 전방이 맞지만 좌우가 뒤집혔으면: rotation 보정 필요
- 위아래가 뒤집혔으면: `roll` 또는 `pitch` 180도 보정 필요
- 보정을 감으로 많이 넣기보다, 가능하면 **물리적으로 다시 붙이는 쪽이 더 낫다**

즉, 이번 단계에서는 software 보정보다 hardware 방향 맞추기를 우선한다.

## 8. 현재 단계의 성공 기준

- `BNO08x`가 `D435i`에 임시로 단단히 붙어 있다
- `/imu/data`가 계속 publish된다
- `camera_link -> imu_link` static TF가 살아 있다
- 카메라와 IMU를 같이 움직였을 때 viewer 반응이 대체로 일관된다

## 9. 다음 단계

- [16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md](./16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md) 기준 `/imu/data` 유지
- 이 가이드 기준 `static TF` 실행
- 그다음 [18_Jetson_BNO08x_RTABMap_Comparison_Guide.md](./18_Jetson_BNO08x_RTABMap_Comparison_Guide.md)로 `RTAB-Map IMU OFF vs ON` 비교 실험
