# Jetson Orin Nano에서 Docker 배우기 A to Z

## 0. 결론

- 가장 안전한 시작 순서는 `JetPack 정상 부팅 확인 -> Docker 기본 동작 확인 -> NVIDIA runtime 확인 -> 첫 Jetson 컨테이너 실행 -> ROS2/VSLAM 개발환경 컨테이너화` 이다.
- Jetson에서는 일반 PC처럼 아무 Docker 이미지를 막 가져오면 안 된다. `arm64 아키텍처`, `JetPack/L4T 버전`, `GPU runtime 설정`이 맞아야 한다.
- 초보자 기준으로는 처음부터 Dockerfile 최적화나 Kubernetes까지 가지 말고, 먼저 `hello-world`, `l4t-base`, `볼륨 마운트`, `장치 접근`, `GUI`까지 단계적으로 익히는 것이 가장 실용적이다.

## 1. 선행 개념

- `JetPack`: Jetson용 운영체제와 CUDA, TensorRT 같은 NVIDIA 소프트웨어 묶음이다.
- `L4T(Linux for Tegra)`: Jetson용 저수준 Linux 플랫폼 버전이다. JetPack과 연결되어 생각하면 된다.
- `Docker Image`: 컨테이너 실행에 필요한 파일 묶음이다.
- `Container`: 이미지를 실제로 실행한 상태다.
- `Volume / Bind Mount`: 호스트 파일을 컨테이너와 연결하는 방법이다.
- `arm64(aarch64)`: Jetson CPU 아키텍처다. x86_64 이미지와 다르다.
- `NVIDIA Container Runtime`: 컨테이너 안에서 Jetson GPU 관련 라이브러리와 장치를 쓰게 해주는 구성이다.

## 2. Jetson에서 Docker가 일반 PC와 다른 이유

직관:
일반 PC는 CPU만으로도 Docker 실습이 된다. 그런데 Jetson은 GPU 가속, 카메라, 센서, CUDA 라이브러리까지 같이 써야 해서 "컨테이너만 뜬다"로 끝나지 않는다.

핵심 개념:
- Jetson은 `ARM64` 장치다.
- Jetson은 `JetPack/L4T` 버전과 컨테이너 호환성이 중요하다.
- GPU를 쓰려면 Docker 안에서 `NVIDIA runtime`이 보여야 한다.

실무적으로 꼭 기억할 것:

1. x86용 이미지는 Jetson에서 바로 안 돈다.
2. Jetson용 이미지는 `arm64` 또는 NVIDIA NGC의 `l4t-*` 계열을 우선 본다.
3. Jetson에서 CUDA가 된다고 해서 컨테이너 안에서도 자동으로 되는 것은 아니다.

## 3. 추천 학습 경로

가장 실용적인 경로는 아래 순서다.

1. Jetson OS와 JetPack 상태 확인
2. Docker 기본 설치/동작 확인
3. NVIDIA runtime 확인
4. Jetson용 첫 컨테이너 실행
5. 파일 공유, 포트, 볼륨, 네트워크 학습
6. 카메라/USB/GUI 접근 학습
7. ROS2 개발용 Dockerfile 작성
8. Docker Compose로 실행 자동화
9. VSLAM/RealSense 같은 실제 프로젝트에 연결

## 4. Phase 0. 보드와 OS 준비

직관:
보드 펌웨어와 JetPack이 꼬여 있으면 Docker 이전 단계에서 이미 막힌다.

핵심 개념:
- `Firmware`: 하드웨어를 바로 제어하는 낮은 수준 소프트웨어다.
- `microSD image`: Jetson Orin Nano 개발킷에 넣는 부팅 이미지다.

중요:
NVIDIA 공식 Getting Started 가이드는 Jetson Orin Nano 개발킷이 공장 출고 펌웨어 상태일 경우 `JetPack 6.x와 호환되지 않을 수 있다`고 안내한다. 즉, 처음 셋업이라면 Docker보다 먼저 펌웨어/JetPack 상태를 확인해야 한다.

우선 확인:

```bash
uname -m
cat /etc/nv_tegra_release
dpkg -l | grep nvidia-jetpack
```

정상 기대:
- `uname -m` 결과가 `aarch64`
- `cat /etc/nv_tegra_release` 에서 `R36.x` 같은 L4T 정보 확인
- `dpkg -l | grep nvidia-jetpack` 에서 JetPack 메타패키지 확인

처음 보드 세팅이라면:

1. Jetson Orin Nano Developer Kit Getting Started Guide 먼저 확인
2. 필요 시 펌웨어 업데이트
3. JetPack SD card image로 부팅
4. 기본 로그인과 네트워크 연결 완료
5. 그 다음 Docker 확인

## 5. Phase 1. Docker가 이미 있는지 먼저 확인

직관:
JetPack 환경에서는 Docker가 이미 있는 경우가 많다. 무조건 재설치부터 하면 오히려 꼬일 수 있다.

확인 명령:

```bash
docker --version
docker compose version
sudo systemctl status docker
sudo docker info
```

봐야 할 것:
- Docker 버전이 출력되는가
- Docker 데몬이 `active (running)` 인가
- `docker info`에서 에러 없이 정보가 보이는가

정상이라면 바로 다음 단계로 간다.

## 6. Phase 2. Docker 기본 동작 확인

직관:
GPU 이전에 먼저 컨테이너 기본 실행이 되는지 확인해야 한다.

가장 먼저 실행:

```bash
sudo docker run hello-world
```

이 명령이 의미하는 것:
- 이미지 다운로드
- 컨테이너 생성
- 실행 후 종료

실패하면 보는 포인트:
- `Cannot connect to the Docker daemon`
- `permission denied`
- 네트워크 문제로 이미지 pull 실패

초보자용 후속 명령:

```bash
sudo docker ps -a
sudo docker images
sudo docker rm <container_id>
```

## 7. Phase 3. sudo 없이 Docker 쓰기

직관:
매번 `sudo docker ...` 를 쓰면 불편하고, 나중에 파일 권한도 꼬일 수 있다.

Docker 공식 post-install 기준 추천 설정:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world
```

참고:
- `groupadd: group 'docker' already exists` 가 나오면 정상이다. 이미 그룹이 있다는 뜻이다.
- `newgrp docker` 후에도 안 되면 터미널을 다시 열고 재확인한다.

추가 권장:

```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

주의:
- 예전에 `sudo docker`로 먼저 실행했다면 `~/.docker` 권한이 꼬일 수 있다.
- 그 경우 Docker 공식 문서처럼 `chown`으로 사용자 권한을 다시 맞춰야 한다.

## 8. Phase 4. Docker가 없거나 깨졌을 때 설치/복구

직관:
이 단계는 "이미 Docker가 있는데 굳이 다시 설치"하는 단계가 아니라, 없는 경우나 고장난 경우의 복구 경로다.

핵심 개념:
- `docker-ce`: Docker Engine 패키지다.
- `containerd`: 컨테이너 실행 하부 런타임이다.

Docker 공식 Ubuntu 설치 절차 요약:

1. 충돌 패키지 제거
2. Docker apt 저장소 추가
3. Docker Engine 설치
4. 서비스 상태 확인
5. `hello-world`로 검증

명령 예시:

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y $pkg
done

sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl status docker
sudo docker run hello-world
```

현실적인 주의점:
- Jetson에서 Docker가 이미 JetPack과 함께 정상 동작 중이면 굳이 이 경로를 타지 않는 것이 낫다.
- 설치 후에도 GPU가 안 보이면 다음 `NVIDIA runtime` 단계가 필요하다.

## 9. Phase 5. NVIDIA runtime 확인과 복구

직관:
컨테이너가 뜨더라도 GPU 라이브러리 접근이 안 되면 Jetson 장점을 거의 못 쓴다.

핵심 개념:
- `Runtime`: 컨테이너를 어떤 방식으로 실행할지 정하는 설정이다.
- `nvidia-ctk`: NVIDIA Container Toolkit 설정 도구다.

먼저 확인:

```bash
docker info | grep -i runtime
docker info | grep -i nvidia
```

문제가 의심되는 경우:
- Jetson용 컨테이너가 뜨는데 CUDA 관련 라이브러리를 못 찾음
- `--runtime nvidia` 사용 시 에러
- `docker info`에서 `nvidia` 관련 항목이 안 보임

NVIDIA 공식 toolkit 설정 절차:

```bash
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  gnupg2

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

검증:

```bash
docker info | grep -i runtime
```

## 10. Phase 6. Jetson용 첫 컨테이너 실행

직관:
여기서 중요한 것은 "그냥 아무 Ubuntu 컨테이너"가 아니라 "Jetson에 맞는 컨테이너"를 써보는 것이다.

핵심 개념:
- `NGC`: NVIDIA가 제공하는 컨테이너 레지스트리다.
- `l4t-base`: Jetson 컨테이너의 가장 기본 베이스 이미지다.

가장 추천하는 첫 Jetson 컨테이너:

```bash
sudo docker run --rm -it --runtime nvidia \
  nvcr.io/nvidia/l4t-base:<L4T_TAG> \
  bash
```

여기서 `<L4T_TAG>` 는 호스트 Jetson의 L4T 계열과 맞춰야 한다.
예를 들어 호스트가 `R36.x` 계열이면 컨테이너도 같은 큰 버전 계열을 맞추는 것이 안전하다.

컨테이너 안에서 해볼 것:

```bash
uname -m
cat /etc/os-release
ls /
exit
```

이 단계의 목표:
- Jetson에서 ARM64 컨테이너가 뜨는지 확인
- `--runtime nvidia` 옵션이 받아들여지는지 확인
- NGC 이미지 pull이 되는지 확인

## 11. Phase 7. Docker 기본기 익히기

초보자 기준으로 아래 명령은 반드시 손에 익히는 것이 좋다.

```bash
docker ps
docker ps -a
docker images
docker pull <image>
docker run -it <image> bash
docker exec -it <container> bash
docker logs <container>
docker stop <container>
docker rm <container>
docker rmi <image>
```

꼭 알아둘 차이:
- `image`: 실행 전 재료
- `container`: 실행 중 또는 실행했던 인스턴스
- `docker run`: 새 컨테이너 생성 + 실행
- `docker exec`: 이미 실행 중인 컨테이너 안으로 들어감

## 12. Phase 8. 파일 공유와 작업공간 연결

직관:
컨테이너 안에서 만든 파일이 종료 후 사라지면 개발이 불편하다. 그래서 `bind mount`가 매우 중요하다.

실전 예시:

```bash
mkdir -p ~/docker_ws

docker run --rm -it \
  -v ~/docker_ws:/workspace \
  ubuntu:22.04 \
  bash
```

의미:
- 호스트의 `~/docker_ws` 를 컨테이너 `/workspace` 에 연결
- 컨테이너에서 만든 파일을 호스트에서도 그대로 볼 수 있음

Jetson 개발에서 자주 쓰는 패턴:

```bash
-v ~/autonomy_ws:/workspaces/autonomy_ws
```

## 13. Phase 9. Jetson에서 자주 쓰는 실행 옵션

직관:
로봇/비전 프로젝트는 단순 CLI 앱이 아니라 카메라, GUI, 네트워크, 센서를 함께 쓴다.

자주 쓰는 옵션:
- `--network host`: ROS2 통신이나 포트 문제를 줄이기 쉬움
- `--ipc host`: 대용량 shared memory를 쓰는 앱에 유리
- `--runtime nvidia`: NVIDIA runtime 사용
- `--device /dev/...`: 특정 장치 접근 허용
- `-v /tmp/.X11-unix:/tmp/.X11-unix`: GUI 앱 표시
- `-e DISPLAY=$DISPLAY`: X11 화면 전달

예시:

```bash
xhost +local:docker

docker run --rm -it \
  --network host \
  --ipc host \
  --runtime nvidia \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/autonomy_ws:/workspaces/autonomy_ws \
  nvcr.io/nvidia/l4t-base:<L4T_TAG> \
  bash
```

주의:
- `xhost +local:docker` 는 편하지만 보안상 넓게 열어준다.
- 학습 초기에는 편의상 쓰고, 나중에 보안 설정을 더 엄격히 가져가는 편이 좋다.

## 14. Phase 10. 카메라와 USB 장치 접근

직관:
VSLAM에서는 결국 카메라를 컨테이너 안에서 읽어야 한다. 여기서 가장 많이 막힌다.

체크 포인트:

1. 장치가 호스트에서는 보이는가
2. 컨테이너에 해당 `/dev` 가 전달됐는가
3. 권한 문제는 없는가
4. USB 규칙이나 udev 설정이 필요한가

예시:

```bash
ls /dev/video*
lsusb
```

카메라 접근 예시:

```bash
docker run --rm -it \
  --device /dev/video0 \
  ubuntu:22.04 \
  bash
```

RealSense 같이 USB 기반 센서는 경우에 따라 아래가 더 실용적일 수 있다.

```bash
docker run --rm -it \
  --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  ubuntu:22.04 \
  bash
```

주의:
- `--privileged` 는 편하지만 권한을 너무 넓게 준다.
- 처음 디버깅용으로는 유용하지만, 최종 구성에서는 필요한 장치만 열어주는 쪽이 좋다.

## 15. Phase 11. ROS2 개발 컨테이너로 확장

직관:
Docker 학습 목표가 결국 VSLAM/자율주행 개발환경이라면, 최종 목적은 ROS2 workspace를 안정적으로 재현하는 것이다.

추천 순서:

1. `hello-world`
2. `ubuntu:22.04`
3. `l4t-base`
4. ROS2 base image 또는 직접 만든 ROS2 Dockerfile
5. RealSense / OpenCV / VSLAM 의존성 추가

실전용 Dockerfile 예시:

```dockerfile
FROM nvcr.io/nvidia/l4t-base:<L4T_TAG>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    locales \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    build-essential \
    git \
    python3-pip \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
    > /etc/apt/sources.list.d/ros2.list

RUN apt-get update && apt-get install -y \
    ros-humble-ros-base \
    && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc
WORKDIR /workspaces
```

설명:
- 이 Dockerfile은 Jetson용 `l4t-base` 위에 ROS2를 얹는 학습용 예시다.
- 실제 프로젝트에서는 OpenCV, librealsense, Ceres, g2o 등 필요한 패키지를 추가하면 된다.

## 16. Phase 12. Docker Compose로 실행 자동화

직관:
옵션이 길어지면 `docker run ...` 명령이 금방 지저분해진다. Compose를 쓰면 반복 실행이 쉬워진다.

예시 `compose.yaml`:

```yaml
services:
  jetson-dev:
    image: nvcr.io/nvidia/l4t-base:<L4T_TAG>
    container_name: jetson-dev
    stdin_open: true
    tty: true
    network_mode: host
    ipc: host
    environment:
      - DISPLAY=${DISPLAY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix
      - ${HOME}/autonomy_ws:/workspaces/autonomy_ws
    deploy: {}
```

실행:

```bash
docker compose up -d
docker compose exec jetson-dev bash
docker compose down
```

주의:
- Compose에서 GPU 관련 설정은 Docker/Toolkit 버전에 따라 방식이 달라질 수 있다.
- 학습 초기에는 `docker run --runtime nvidia ...` 로 먼저 검증하고 Compose로 옮기는 편이 안전하다.

## 17. Jetson에서 자주 만나는 오류

### 1. `exec format error`

원인 가설:
- x86_64 이미지를 Jetson에서 실행했을 가능성이 큼

확인 방법:

```bash
uname -m
docker image inspect <image> | grep -i arch
```

수정:
- `arm64` 지원 이미지로 변경
- Jetson이면 NGC `l4t-*` 계열 우선 검토

### 2. `Cannot connect to the Docker daemon`

원인 가설:
- Docker 서비스가 죽어 있음

확인 방법:

```bash
sudo systemctl status docker
```

수정:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. GPU 또는 CUDA 관련 기능이 컨테이너에서 안 보임

원인 가설:
- NVIDIA runtime 미설정
- JetPack/L4T와 컨테이너 태그 불일치

확인 방법:

```bash
docker info | grep -i runtime
cat /etc/nv_tegra_release
```

수정:
- `nvidia-container-toolkit` 설치
- `sudo nvidia-ctk runtime configure --runtime=docker`
- Docker 재시작

### 4. 카메라가 컨테이너에서 안 보임

원인 가설:
- `/dev/video*` 또는 `/dev/bus/usb` 전달 누락
- 권한 문제

확인 방법:

```bash
ls /dev/video*
lsusb
```

수정:
- `--device /dev/video0`
- 또는 `-v /dev/bus/usb:/dev/bus/usb`
- 필요 시 `--privileged`

### 5. 디스크가 빨리 찬다

원인 가설:
- 이미지와 빌드 캐시가 많이 쌓임

확인 방법:

```bash
docker system df
```

정리:

```bash
docker image prune
docker container prune
docker system prune
```

## 18. VSLAM 프로젝트로 연결할 때 추천 순서

가장 실용적인 연결 순서는 아래와 같다.

1. Jetson에서 Docker 기본 동작 확인
2. `l4t-base` 컨테이너 정상 실행
3. ROS2 개발 이미지 작성
4. OpenCV / librealsense / colcon 환경 구성
5. 카메라 장치 접근 확인
6. RViz2 또는 GUI 접근 확인
7. VSLAM 패키지 빌드
8. rosbag 재생으로 먼저 검증
9. 실센서 입력으로 전환

이 순서를 추천하는 이유:
- 센서 문제와 Docker 문제를 분리할 수 있다.
- 처음부터 실카메라까지 한 번에 가면 원인 분리가 어렵다.

## 19. 지금 바로 해야 할 첫 액션

지금 Jetson Orin Nano를 실제로 만질 수 있다면 아래 순서로 시작하면 된다.

1. `uname -m`
2. `cat /etc/nv_tegra_release`
3. `docker --version`
4. `sudo systemctl status docker`
5. `sudo docker run hello-world`
6. `docker info | grep -i runtime`
7. `sudo docker run --rm -it --runtime nvidia nvcr.io/nvidia/l4t-base:<L4T_TAG> bash`

## 20. 참고 자료

- NVIDIA Jetson Orin Nano Getting Started: https://developer.nvidia.com/embedded/learn/get-started-jetson-orin-nano-devkit
- NVIDIA Jetson Cloud-Native Overview: https://developer.nvidia.com/embedded/jetson-cloud-native
- Docker Engine Ubuntu 설치 가이드: https://docs.docker.com/engine/install/ubuntu/
- Docker Linux post-install: https://docs.docker.com/engine/install/linux-postinstall/
- NVIDIA Container Toolkit 설치 가이드: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

## 21. 문서 메모

- 이 문서는 `Jetson Orin Nano + Docker` 학습을 빠르게 시작하기 위한 실전 가이드다.
- Dockerfile, Compose, 카메라 장치 전달 예시는 공식 문서를 바탕으로 정리한 실무용 예시이며, 실제 프로젝트에서는 사용 중인 JetPack/L4T/센서 구성에 맞게 조정해야 한다.
