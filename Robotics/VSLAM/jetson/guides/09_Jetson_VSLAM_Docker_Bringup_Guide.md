# 09 Jetson VSLAM Docker Bring-up Guide

## 목적

- `Jetson` 로컬 GUI 세션에서 `VSLAM` 개발 컨테이너를 빌드하고 들어간다.
- host의 `~/yh_ws/TIL`을 그대로 마운트해서, 소스는 host에 두고 실행환경만 컨테이너로 고정한다.

## 전제

- [`08_Jetson_Docker_Enablement_Guide.md`](./08_Jetson_Docker_Enablement_Guide.md)를 먼저 끝낸다.
- `docker run --rm hello-world`가 성공해야 한다.
- `Jetson` 바탕화면에서 직접 연 터미널이어야 GUI 검증이 쉽다.

## 1. X11 허용

```bash
xhost +local:docker
echo "DISPLAY=${DISPLAY:-empty}"
```

## 2. .env 파일 준비

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM/jetson/docker
cp .env.example .env
sed -i "s/^UID=.*/UID=$(id -u)/" .env
sed -i "s/^GID=.*/GID=$(id -g)/" .env
sed -i "s/^USER_NAME=.*/USER_NAME=$(id -un)/" .env
sed -i "s|^DISPLAY=.*|DISPLAY=${DISPLAY:-:0}|" .env
sed -i "s|^HOST_TIL_ROOT=.*|HOST_TIL_ROOT=/home/jetson/yh_ws/TIL|" .env
sed -i "s|^HOST_WS_ROOT=.*|HOST_WS_ROOT=/home/jetson/yh_ws|" .env
cat .env
```

## 3. 이미지 빌드

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM/jetson/docker
docker compose --env-file .env build
```

## 4. 개발 컨테이너 진입

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_jetson_vslam_docker.sh
```

## 5. 컨테이너 안에서 기본 확인

```bash
source /opt/ros/humble/setup.bash
ros2 pkg list | rg "rtabmap|realsense2_camera|rviz2"
python3 --version
```

## 6. GUI 테스트

```bash
source /opt/ros/humble/setup.bash
rviz2
```

또는:

```bash
xeyes
```

## 7. D435i 접근 테스트

```bash
lsusb | rg "Intel|RealSense"
source /opt/ros/humble/setup.bash
ros2 launch realsense2_camera rs_launch.py enable_color:=true enable_depth:=true
```

## 8. 종료

```bash
exit
xhost -local:docker
```

## 9. 다음 단계

- 컨테이너 안에서 `D435i`가 정상적으로 뜨면
  native benchmark와 같은 기준으로 topic/GUI/RTAB-Map 비교를 진행한다.
- 그 다음에야 native vs Docker 중 어떤 쪽을 기본 운영 방식으로 둘지 판단한다.
- 외부 `BNO08x`는 [`12_Jetson_BNO08x_Docker_Check_Guide.md`](./12_Jetson_BNO08x_Docker_Check_Guide.md) 기준으로 같은 컨테이너 안에서 값 확인을 이어간다.
