# Jetson Docker 호스트 점검 체크리스트

## 결론

- Jetson Docker 작업의 1단계는 **호스트 상태 확인**이다.
- 여기서 먼저 봐야 하는 것은 `JetPack`, `Ubuntu`, `Docker`, `NVIDIA Container Toolkit`, `D435i 장치 인식`이다.
- 이 단계가 안 맞으면, 뒤에서 `ROS 2`, `realsense2_camera`, `RTAB-Map`을 붙여도 원인 분리가 어렵다.

## 용어 한 줄 설명

- `호스트(host)`: Docker 컨테이너 바깥의 실제 Jetson 운영체제다.
- `JetPack`: Jetson용 운영체제와 드라이버, CUDA 같은 개발 구성요소 묶음이다.
- `Docker runtime`: 컨테이너를 실제로 실행시키는 계층이다.
- `NVIDIA Container Toolkit`: 컨테이너 안에서 Jetson GPU와 관련 라이브러리를 쓸 수 있게 해주는 도구다.
- `D435i`: RGB 영상, depth, IMU를 함께 주는 Intel RealSense 센서다.

## 왜 이 점검이 먼저 필요한가

직관:
카메라가 안 뜨거나 Docker 안에서 ROS 2가 안 도는 원인은 코드보다 환경인 경우가 많다.

핵심:

1. Jetson 버전이 맞는지 확인
2. Docker가 실제로 동작하는지 확인
3. NVIDIA runtime이 붙는지 확인
4. D435i가 호스트에서 먼저 보이는지 확인

이 4개가 맞아야 다음 단계가 안전하다.

## 권장 기준

- `JetPack 6.1`
- `Ubuntu 22.04`
- `Docker`
- `NVIDIA Container Toolkit`
- `ROS 2 Humble`

지금은 `ROS 2`와 `RTAB-Map`을 바로 확인하는 단계가 아니라, 그 전에 필요한 호스트 기반을 확인하는 단계다.

## 실행 방법

Jetson 터미널에서 아래 스크립트를 실행하면 된다.

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/Tools/check_jetson_host_docker.sh
```

## 체크 항목

### 1. Jetson 기본 정보

확인 명령:

```bash
uname -m
cat /etc/nv_tegra_release
cat /etc/os-release
```

기대하는 방향:

- `uname -m` 결과가 `aarch64`
- `cat /etc/nv_tegra_release`에 `R36.x`
- Ubuntu가 `22.04`

### 2. Docker 설치 상태

확인 명령:

```bash
docker --version
docker compose version
systemctl is-active docker
groups
```

기대하는 방향:

- Docker 버전이 출력됨
- compose 버전이 출력됨
- `docker` 서비스가 `active`
- 현재 사용자 그룹에 `docker`가 있으면 편하다

### 3. NVIDIA Container Toolkit 상태

확인 명령:

```bash
dpkg -l | grep -E 'nvidia-container|nvidia-ctk|nvidia-docker'
docker info | grep -A5 Runtimes
```

기대하는 방향:

- 관련 패키지가 설치되어 있음
- `docker info`에서 `nvidia` runtime이 보이면 좋다

주의:
`docker info`는 사용자 권한 상태에 따라 안 될 수 있다.
그 경우는 `docker` 그룹 문제나 데몬 접근 문제를 먼저 봐야 한다.

### 4. D435i 호스트 인식 상태

확인 명령:

```bash
lsusb
ls /dev/video*
```

기대하는 방향:

- `lsusb`에 Intel RealSense 관련 장치가 보임
- `/dev/video*` 장치가 보임

선택 확인:

```bash
rs-enumerate-devices
```

이 명령이 되면 `librealsense` 도구까지 이미 잡힌 상태다.

## 결과 해석

### 바로 다음 단계로 넘어가도 되는 경우

- Jetson이 `aarch64`
- JetPack / Ubuntu 축이 예상과 맞음
- Docker가 정상 동작
- `nvidia` runtime 또는 관련 toolkit 패키지가 보임
- D435i가 `lsusb`에서 보임

이 경우 다음 단계는 **Docker 이미지 빌드와 컨테이너 실행 확인**이다.

### 아직 다음 단계로 가면 안 되는 경우

- `JetPack` 버전이 애매하거나 다름
- Ubuntu가 `20.04` 기반임
- Docker 명령이 실패함
- `docker info` 접근이 안 됨
- D435i가 `lsusb`에서도 안 보임

이 경우는 `ROS 2`나 `RTAB-Map`으로 가지 말고, 호스트 상태부터 고쳐야 한다.

## 다음 액션

1. Jetson에서 점검 스크립트를 실행한다.
2. 결과를 보고 `JetPack / Docker / Toolkit / D435i` 4가지를 먼저 판정한다.
3. 모두 통과하면 Docker 이미지 빌드 단계로 넘어간다.
