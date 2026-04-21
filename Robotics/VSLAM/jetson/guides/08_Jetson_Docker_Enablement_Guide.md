# 08 Jetson Docker Enablement Guide

## 목적

- 이미 설치된 `Docker CE`, `Compose`, `NVIDIA Container Toolkit`을 그대로 활용해
  `jetson` 사용자가 일반 사용자 권한으로 Docker를 쓰게 만든다.
- `hello-world`와 runtime 확인까지 끝내서, 이후 `VSLAM` 컨테이너 실행을 준비한다.

## 현재 판단

- `Docker CE 29.4.0` 설치됨
- `Docker Compose v5.1.2` 설치됨
- `nvidia-container-toolkit 1.16.2` 설치됨
- `/etc/docker/daemon.json`에 `nvidia` runtime 등록됨
- 현재 막힌 부분: `jetson` 사용자가 `docker` 그룹에 없음

## 1. 현재 상태 빠른 확인

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/check_jetson_docker_preflight.sh
```

## 2. docker 그룹 권한 부여

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

참고:

- `group 'docker' already exists` 는 정상이다.
- `newgrp docker` 이후 현재 shell group이 갱신된다.
- 그래도 반영이 애매하면 터미널을 완전히 새로 열고 다시 확인한다.

## 3. daemon 접근 확인

```bash
docker info | grep -i "Runtimes\\|Default Runtime\\|nvidia"
docker run --rm hello-world
```

기대:

- `Runtimes` 쪽에 `nvidia`가 보인다.
- `hello-world`가 정상 종료된다.

## 4. 서비스 자동 시작 확인

```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
systemctl status docker --no-pager
```

## 5. 권한 꼬임이 보이면 정리

```bash
sudo chown "$USER":"$USER" ~/.docker -R
sudo chmod g+rwx ~/.docker -R
```

## 6. 다음 단계

- 권한과 기본 실행이 끝나면 바로 [`09_Jetson_VSLAM_Docker_Bringup_Guide.md`](./09_Jetson_VSLAM_Docker_Bringup_Guide.md)로 넘어간다.
