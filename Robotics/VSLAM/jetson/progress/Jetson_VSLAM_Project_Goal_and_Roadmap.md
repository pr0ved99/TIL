# Jetson에서의 VSLAM 최종 목표와 단계별 로드맵

## 결론

- `Jetson`에서의 최종 목표는 단순히 `RTAB-Map` 창이 한 번 뜨는 것이 아니다.
- 프로젝트 관점에서의 진짜 목표는 **`Jetson`이 로봇 탑재용 실전 실행 보드로서 `D435i + ROS 2 + RTAB-Map` 기준선을 안정적으로 돌리고, 이후 `encoder + external IMU + GPS + Nav2`까지 확장 가능한 실행 기반이 되는 것**이다.
- 즉, `Jetson`은 이번 프로젝트에서 `테스트용 PC 대체품`이 아니라, **로봇 위에서 실제로 돌아갈 온보드 컴퓨팅 기준점**이다.

---

## 1. 왜 Jetson 목표를 따로 봐야 하는가

직관:
지금까지 `PC`에서는 개념 정리와 1차 bring-up, 세팅 비교가 가능했다. 하지만 실제 프로젝트는 최종적으로 로봇 위에서 돌아가야 하므로, `Jetson`에서의 실행 가능성이 따로 검증되어야 한다.

프로젝트 관점에서 `Jetson`이 맡는 역할:

1. 센서 입력을 실제로 받는 보드
2. `ROS 2` 노드를 실제로 올리는 보드
3. `VSLAM`, `localization`, `navigation`, `perception`이 함께 올라갈 보드
4. 나중에 로봇 본체에 실장되는 온보드 컴퓨터

즉, `Jetson`에서 확인해야 하는 것은 "돌아간다"가 아니라 아래에 가깝다.

- 반복 실행 가능한가
- 장치 접근이 안정적인가
- GUI 포함 작업과 headless 작업을 모두 운영할 수 있는가
- 현재 자원(`CPU`, `memory`, `temperature`) 안에서 실용 속도가 나오는가
- 다음 단계 센서 융합과 자율주행 확장이 가능한 구조인가

---

## 2. Jetson에서의 최종 목표 정의

이번 프로젝트 기준으로 `Jetson`에서의 최종 목표를 단계적으로 정의하면 아래와 같다.

### 목표 A. 실행 환경 기준선 확보

- `Jetson`에 접속하고 개발할 수 있다.
- `SSH`와 직접 연결(`모니터 + 키보드 + 마우스`)을 상황에 맞게 병행할 수 있다.
- 저장소, 워크스페이스, ROS 2, 장치 접근, Docker 같은 기본 환경이 정리돼 있다.

### 목표 B. D435i 기반 VSLAM 기준선 확보

- `D435i`가 `Jetson`에서 안정적으로 인식된다.
- `realsense2_camera`로 color/depth/IMU 토픽을 재현 가능하게 올릴 수 있다.
- `RTAB-Map`을 `Jetson` 자원 안에서 실용 속도로 돌릴 수 있는 기본 세팅을 고정한다.

### 목표 C. 운영 가능한 실행 절차 확보

- 누가 다시 와도 같은 절차로 실행할 수 있게 스크립트와 문서가 정리돼 있다.
- 장애물은 어디서 먼저 확인해야 하는지(`USB`, `udev`, `device busy`, `GUI load`, `thermal`) 체크리스트가 있다.

### 목표 D. 로봇 통합 준비 완료

- `Jetson` 기준으로 이후 `encoder`, `external IMU`, `GPS`, `Nav2`를 붙일 준비가 돼 있다.
- 즉, `Jetson`은 `VSLAM 데모 머신`이 아니라 **실차 통합용 기반 시스템**이 된다.

---

## 3. 이번 프로젝트에서 Jetson의 현실적인 최종 역할

현재 프로젝트 전체 목표는 공터 환경 쓰레기 수거 로봇이다. 이 기준에서 `Jetson`의 역할은 아래처럼 보는 것이 가장 현실적이다.

```text
Jetson
├── D435i bring-up
├── ROS 2 실행 환경
├── RTAB-Map baseline
├── later: robot_localization
├── later: Nav2
├── later: trash perception
└── later: mission integration
```

중요:

- 최종 주 위치추정은 `VSLAM 단독`이 아니라 `encoder + external IMU + GPS` 중심이 될 가능성이 높다.
- 그래도 `Jetson`에서 `VSLAM baseline`을 잡아두는 이유는 아래와 같다.
  - 근거리 시각 보조
  - 실내/초기 맵핑
  - 장애물 및 시각 디버깅
  - 보조 오도메트리 실험

즉, `Jetson`에서의 VSLAM 목표는 **최종 시스템의 유일한 위치추정 수단을 만드는 것**이 아니라,
**최종 시스템에 들어갈 시각 기반 실행 블록을 안정적으로 확보하는 것**이다.

---

## 4. 큰 단계 로드맵

### Stage 0. Jetson 작업 기반 정리

목표:

- `SSH`와 직접 연결 작업 방식을 정리한다.
- 저장소 경로, 워크스페이스, 사용자 권한, 기본 개발 도구를 고정한다.

완료 기준:

- `Jetson`에서 작업 경로와 저장소 접근이 흔들리지 않는다.
- 어떤 작업을 `SSH`로 하고, 어떤 작업을 직접 화면으로 할지 구분된다.

### Stage 1. Jetson 하드웨어/시스템 기준선 점검

목표:

- `JetPack`, `L4T`, `ROS 2`, `Docker`, 디스크, 네트워크, 장치 인식 상태를 점검한다.

완료 기준:

- 시스템 정보와 장치 상태가 문서화돼 있다.
- 이후 실험에서 재확인해야 할 기준값이 정리돼 있다.

### Stage 2. D435i Native Bring-up on Jetson

목표:

- `Jetson`에서 `D435i`를 native ROS 2 환경에서 안정적으로 올린다.

확인 항목:

- `USB 3.x`
- `udev rules`
- color/depth/IMU 토픽
- `realsense-viewer`와 ROS 2 실행 충돌 여부

완료 기준:

- `D435i` bring-up 절차가 재현 가능하다.
- 장치 충돌과 권한 문제의 기본 대응 절차가 정리돼 있다.

### Stage 3. RTAB-Map Baseline on Jetson

목표:

- `Jetson` 자원 기준으로 실용적인 `RTAB-Map` 세팅을 선정한다.

확인 항목:

- 해상도/FPS
- `DetectionRate`
- GUI 부하
- `quality`, `delay`, `update time`
- 체감 부드러움

완료 기준:

- "현재 Jetson 기준 기본 세팅"이 하나 고정된다.
- 같은 세팅으로 다시 실행했을 때 큰 흔들림 없이 재현된다.

### Stage 4. 실행 절차와 증빙 체계 고정

목표:

- 스크립트, 로그 저장 위치, 캡처 규칙, 성능 측정 항목을 고정한다.

완료 기준:

- 새 세션에서도 같은 절차로 바로 테스트를 시작할 수 있다.
- 실패했을 때 어디를 먼저 볼지 체크리스트가 있다.

### Stage 5. 로봇 통합 준비 단계

목표:

- `Jetson`에서 이후 붙을 `encoder`, `external IMU`, `GPS`, `Nav2` 확장을 고려한 실행 기반을 만든다.

완료 기준:

- `Jetson`은 단순 VSLAM 실험 환경을 넘어, 로봇 통합용 온보드 실행 기준점이 된다.

---

## 5. 각 단계에서 꼭 남겨야 하는 산출물

### Stage 0~1 산출물

- 환경 정보 문서
- 접속/작업 방식 정리
- `Jetson` 전용 명령 모음

### Stage 2 산출물

- `D435i` launch 명령
- 토픽 확인 결과
- USB/권한 관련 증빙
- `realsense-viewer` 또는 `RViz` 캡처

### Stage 3 산출물

- `RTAB-Map` 후보 세팅 비교표
- 최종 기준 세팅
- `quality`, `delay`, `update time` 로그
- GUI 체감 기록

### Stage 4 산출물

- 실행 스크립트
- 체크리스트
- 로그/캡처 저장 규칙

### Stage 5 산출물

- 이후 `robot_localization`, `Nav2`, 센서 융합과 연결되는 확장 메모

---

## 6. 지금 시점 기준 우선순위

현재는 Stage 0~5를 한 번에 다 하는 것이 아니라, 아래 순서가 가장 자연스럽다.

1. `Jetson` 작업 기반 정리
2. `D435i` native bring-up 재현
3. `RTAB-Map` 기본 세팅 고정
4. 실행 절차 문서화
5. 이후 통합 준비

즉, 지금 제일 중요한 것은
**`Jetson`에서 "한 번 성공"이 아니라 "다시 와도 같은 절차로 재현되는 baseline"을 만드는 것**이다.

---

## 7. 한 줄 요약

- `Jetson`에서의 최종 목표는 `RTAB-Map 데모 1회 성공`이 아니다.
- 진짜 목표는 **`Jetson`을 로봇 탑재용 VSLAM/자율주행 실행 기반으로 안정화하는 것**이다.
