# P07 Serial Bridge

## 목표

ROS 2 `/cmd_vel`과 STM32 command/telemetry packet 사이의 bridge 구조를 설계한다.

## 권장 package

```text
tracked_robot_base_bridge
```

## 최소 node 책임

`base_bridge_node`:

- `/cmd_vel` subscribe
- command timeout 관리
- left/right target speed 계산
- serial 또는 CAN packet 전송
- STM32 telemetry 수신
- `/odom` publish
- `odom -> base_footprint` TF publish
- diagnostics publish

## 초기 command packet 예시

```text
START,seq,enable,vx_mps,wz_radps,checksum,END
```

## 초기 telemetry packet 예시

```text
START,seq,left_count,right_count,left_mps,right_mps,battery_v,fault,state,checksum,END
```

## 실행 과제

1. 실제 STM32를 붙이기 전에 fake firmware node를 만든다.
2. fake firmware는 command를 받으면 encoder count가 증가하는 것처럼 telemetry를 돌려준다.
3. bridge node는 fake telemetry를 `/odom`으로 바꾼다.
4. RViz2에서 odometry 이동을 확인한다.

## 확인 기준

- `/cmd_vel`을 publish하면 bridge node가 target speed를 계산한다.
- telemetry가 끊기면 bridge가 fault 또는 warning을 낸다.
- command가 끊기면 timeout으로 0 speed를 보낸다.

## 프로젝트 연결

이 실습은 실제 STM32 UART/CAN 연결 전에 상위 ROS 2 구조를 검증하는 단계다.
