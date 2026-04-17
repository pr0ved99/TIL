# Jetson 시스템 인벤토리 가이드

## 목적

- 지금 `Jetson`이 어떤 상태인지 기준선을 잡는다.

## 1. 시스템 기본 정보 확인

```bash
uname -a
uname -m
hostnamectl
```

## 2. JetPack / L4T 정보 확인

```bash
cat /etc/nv_tegra_release
dpkg -l | grep -E 'nvidia-jetpack|nvidia-l4t'
```

## 3. ROS 2 정보 확인

```bash
source /opt/ros/humble/setup.bash
echo "$ROS_DISTRO"
ros2 doctor --report
```

## 4. 디스크와 메모리 확인

```bash
df -h
free -h
```

## 5. Docker 상태 확인

```bash
docker --version
docker compose version
systemctl status docker --no-pager
```

## 6. 연결된 USB 장치 확인

```bash
lsusb
```

## 7. 작업 경로 확인

```bash
ls -la /home/jetson
ls -la /home/jetson/yh_ws
ls -la /home/jetson/yh_ws/TIL
```
