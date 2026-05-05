# 29 Jetson GPS ROS2 Bringup Guide

## 목적

- `Jetson Orin Nano`에 GPS를 연결해 먼저 raw 위치 값을 확인한다.
- 그다음 ROS 2에서 `/gps/fix` topic으로 `sensor_msgs/NavSatFix`를 publish한다.
- 이번 단계의 목표는 센서 융합이 아니라, **GPS 단독 bring-up과 ROS 2 topic 발행 성공**이다.

## 현재 기준

- 확인일: 2026-05-05
- ROS 2: `humble`
- 현재 Jetson에서 GPS USB 장치는 아직 보이지 않는다.
- 이번 실물 모듈은 `GY-GPS6MV2 / u-blox NEO-6M`이고, 핀 순서는 `VCC RX TX GND`다.
- 2026-05-06 기준 Jetson 40핀 헤더 UART 직접 연결은 `R36.5` 기본 UART DMA/DTB 설정에서 loopback 실패가 확인됐다.
- `serial@3100000`의 DMA 설정을 제거한 PIO boot entry에서는 `/dev/ttyTHS1` loopback이 성공했다.
- `JetsonIO-UARTA-PIO` boot entry에서 `/dev/ttyTHS1` GPS raw NMEA 수신까지 성공했다.
- 아직 GPS fix는 없으므로 다음 단계는 창가/야외에서 fix를 잡고 ROS 2 `/gps/fix`를 publish하는 것이다.
- 아래 패키지는 설치 후보가 있으나 아직 설치되어 있지 않다.
  - `ros-humble-nmea-navsat-driver`
  - `ros-humble-ublox-gps`
  - `ros-humble-robot-localization`

## 필요한 것

### 하드웨어

- GPS 모듈
  - USB GPS면 가장 쉽다.
  - UART GPS면 `3.3V TTL` 출력인지 확인해야 한다.
- 안테나
  - 세라믹 안테나 또는 외장 안테나
  - 실내에서는 fix가 늦거나 안 잡힐 수 있으므로 창가나 야외 테스트가 필요하다.
- 연결 케이블
  - USB GPS: USB 케이블
  - UART GPS: `TX`, `RX`, `GND`, 전원선
- 안정적인 전원
  - GPS 모듈 요구 전압과 전류 확인
  - Jetson GPIO UART에 `5V TTL` 신호를 직접 넣지 않는다.

### 소프트웨어

- ROS 2 Humble
- generic NMEA GPS용 ROS 2 driver
  - `ros-humble-nmea-navsat-driver`
- u-blox 전용 설정이 필요할 때 쓸 driver
  - `ros-humble-ublox-gps`
- 이후 GPS 융합용
  - `ros-humble-robot-localization`
- serial 권한
  - `jetson` 사용자가 `dialout` 그룹에 들어 있어야 한다.

## 먼저 결정할 것

1. GPS 연결 방식
   - USB GPS: `/dev/ttyUSB0` 또는 `/dev/ttyACM0`
   - UART GPS: `/dev/ttyTHS*` 또는 보드 설정에 따른 UART device
   - 현재 실물 테스트: Jetson 40핀 헤더 UART 직접 연결은 `JetsonIO-UARTA-PIO` boot entry에서 재시도
2. GPS 출력 프로토콜
   - NMEA: `nmea_navsat_driver`로 바로 시작
   - u-blox UBX: `ublox_gps` 사용 검토
3. 기본 baudrate
   - 흔한 값: `9600`, `38400`, `115200`
   - 모듈 datasheet나 판매 페이지 기준으로 먼저 확인
4. ROS 2 topic 이름
   - 위치: `/gps/fix`
   - 속도: `/gps/vel`
   - GPS 시간: `/gps/time_reference`
   - frame: `gps_link`

## 1. 기본 세션 확인

```bash
cd ~/yh_ws/TIL
source /opt/ros/humble/setup.bash
echo "$ROS_DISTRO"
which ros2
git status --short
```

## 2. serial 권한 확인

```bash
groups
```

`dialout`이 없으면 아래를 실행한 뒤 로그아웃했다가 다시 접속한다.

```bash
sudo usermod -aG dialout "$USER"
```

## 3. GPS 연결 후 장치 확인

GPS를 Jetson에 연결한 뒤 실행한다.

현재 실물 모듈을 직접 연결할 때 첫 테스트 배선:

```text
GPS VCC -> Jetson 40핀 pin 1 또는 pin 17  (3.3V)
GPS GND -> Jetson 40핀 pin 6              (GND)
GPS TX  -> Jetson 40핀 pin 10             (UART RX)
GPS RX  -> 연결 안 함
```

나중에 GPS 설정 변경이 필요할 때만 추가:

```text
GPS RX  -> Jetson 40핀 pin 8              (UART TX)
```

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* /dev/ttyTHS* /dev/ttyS* 2>/dev/null || true
lsusb
dmesg | tail -n 80
```

기대:

- USB GPS면 `/dev/ttyUSB0` 또는 `/dev/ttyACM0` 같은 장치가 생긴다.
- UART GPS면 보드 UART 설정에 맞는 `/dev/ttyTHS*` 장치를 사용한다.

## 4. raw NMEA 값 확인

USB GPS 또는 USB-UART bridge가 `/dev/ttyUSB0`, baudrate가 `9600`이라고 가정한 예시다.

CP2102/FT232 계열 USB-UART bridge를 사용하는 경우 첫 테스트 배선:

```text
GPS VCC -> USB-UART 3.3V 또는 GPS 모듈 허용 전압
GPS GND -> USB-UART GND
GPS TX  -> USB-UART RXD
GPS RX  -> 연결 안 함
```

```bash
GPS_PORT=/dev/ttyUSB0
GPS_BAUD=9600

stty -F "$GPS_PORT" "$GPS_BAUD" raw -echo
timeout 10 cat "$GPS_PORT"
```

Jetson 40핀 UART에 직접 연결한 경우에는 후보 포트를 순서대로 확인한다.

```bash
GPS_BAUD=9600

for p in /dev/ttyTHS1 /dev/ttyTHS2 /dev/ttyS0 /dev/ttyS1 /dev/ttyS2 /dev/ttyS3; do
  echo "=== $p ==="
  stty -F "$p" "$GPS_BAUD" raw -echo
  timeout 5 cat "$p"
done
```

기대:

- `$GPGGA`, `$GNGGA`, `$GPRMC`, `$GNRMC` 같은 문장이 반복 출력된다.
- 위도, 경도 값이 비어 있으면 아직 fix가 안 잡힌 상태일 수 있다.
- 실내에서는 몇 분 기다려도 fix가 불안정할 수 있다.

## 4-1. 깨진 문자만 보일 때

현재 실물 테스트에서는 `/dev/ttyTHS1`에서 깨진 문자가 관찰됐다.

```text
4800: b� / bb
19200: `怘��`...
38400: �x�x�x
57600: ����...
```

이 경우 `/dev/ttyTHS1`에 신호가 일부 들어오는 것으로 보고 아래를 먼저 확인한다.

```text
GPS VCC -> Jetson 40핀 pin 1 또는 pin 17  (3.3V)
GPS GND -> Jetson 40핀 pin 6              (GND)
GPS TX  -> Jetson 40핀 pin 10             (UART RX)
GPS RX  -> 연결 안 함 또는 Jetson pin 8   (UART TX)
```

확인 순서:

1. GPS 보드 핀 순서가 `VCC RX TX GND`인지 다시 본다.
2. GPS의 `TX` 핀이 Jetson `pin 10`에 연결됐는지 본다.
3. GND가 반드시 공통인지 본다.
4. 3.3V 전원에서 GPS LED가 약하거나 출력이 계속 깨지면 `VCC`만 5V로 바꿔본다.
5. `RX/TX` 신호선에는 5V TTL을 넣지 않는다.

## 4-2. Jetson R36.5 40핀 UART loopback 이슈와 PIO 우회

2026-05-06 기준 현재 Jetson은 아래 환경이다.

```text
Jetson Linux R36.5.0
nvidia-l4t-core 36.5.0-20260115194252
kernel 5.15.185-tegra
```

`pin 8`과 `pin 10`을 직접 연결한 loopback에서 `/dev/ttyTHS1`에 `hello-gps-test\r\n`를 쓰면 정상 문자열 대신 NUL byte 16개가 들어왔다.

```text
^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@
```

동시에 `dmesg`에서 SMMU/IOMMU fault와 memory controller error가 반복됐다.

```text
arm-smmu 12000000.iommu: Unhandled context fault
tegra-mc 2c00000.memory-controller: EMEM address decode error
```

따라서 GPS bring-up은 내장 40핀 UART가 아니라 USB-UART bridge를 우선한다.

이후 `serial@3100000`의 `dmas`, `dma-names`를 제거한 PIO 테스트용 DTB로 부팅하자 `/dev/ttyTHS1` loopback이 정상 성공했다.

```text
serial-tegra 3100000.serial: RX in PIO mode
serial-tegra 3100000.serial: TX in PIO mode
hello-gps-test^M
```

따라서 현재 GPS 직접 UART 테스트는 `JetsonIO-UARTA-PIO` boot entry 기준으로 진행한다.

GPS 재연결 후 아래 NMEA 문장이 정상 수신됐다.

```text
$GPRMC,,V,,,,,,,,,,N*53
$GPVTG,,,,,,,,,N*30
$GPGGA,,,,,,0,00,99.99,,,,,,*48
$GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
$GPGSV,1,1,00*79
$GPGLL,,,,,,V,N*64
```

현재 의미:

- `GPRMC V`: 아직 유효한 fix가 없다.
- `GPGGA ... 0,00`: fix quality `0`, 위성 수 `00`.
- UART 수신은 성공했고, 이제 GPS fix 대기/위치 문제다.

상세 기록:

- [2026-05-06 Jetson R36.5 UART DMA/DTB Issue](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/notes/troubleshooting/2026-05-06_Jetson_R36_5_UART_DMA_DTB_Issue.md)

## 5. ROS 2 GPS driver 설치

```bash
sudo apt update
sudo apt install -y ros-humble-nmea-navsat-driver
```

나중에 sensor fusion까지 진행할 때 설치한다.

```bash
sudo apt install -y ros-humble-robot-localization
```

u-blox 전용 설정이 필요해지면 그때 설치한다.

```bash
sudo apt install -y ros-humble-ublox-gps
```

## 6. `/gps/fix` publish

USB GPS가 `/dev/ttyUSB0`, baudrate가 `9600`인 NMEA GPS라고 가정한 예시다.
Jetson 40핀 UART에 직접 연결했다면 raw NMEA가 확인된 포트를 `GPS_PORT`에 넣는다.

```bash
cd ~/yh_ws/TIL
source /opt/ros/humble/setup.bash

GPS_PORT=/dev/ttyUSB0
GPS_BAUD=9600

ros2 run nmea_navsat_driver nmea_serial_driver \
  --ros-args \
  -p port:="$GPS_PORT" \
  -p baud:="$GPS_BAUD" \
  -p frame_id:=gps_link \
  -p time_ref_source:=gps \
  -p useRMC:=false \
  -r fix:=/gps/fix \
  -r vel:=/gps/vel \
  -r heading:=/gps/heading \
  -r time_reference:=/gps/time_reference
```

## 7. topic 확인

다른 터미널에서 실행한다.

```bash
source /opt/ros/humble/setup.bash

ros2 topic list | grep -E '^/gps'
ros2 topic type /gps/fix
ros2 topic echo /gps/fix --once
ros2 topic hz /gps/fix
ros2 topic echo /gps/vel --once
```

기대:

- `/gps/fix`가 보인다.
- `header.frame_id`가 `gps_link`다.
- `latitude`, `longitude`, `altitude` 값이 들어온다.
- fix가 없으면 `status.status`가 `-1`일 수 있다.

## 8. 노트북에서 topic 보기

Jetson과 노트북이 같은 네트워크에 있고 `ROS_DOMAIN_ID`가 같아야 한다.

Jetson:

```bash
source /opt/ros/humble/setup.bash
echo "$ROS_DOMAIN_ID"
ros2 topic list | grep -E '^/gps'
```

노트북:

```bash
source /opt/ros/humble/setup.bash
echo "$ROS_DOMAIN_ID"
ros2 topic list | grep -E '^/gps'
ros2 topic echo /gps/fix --once
```

노트북에서 topic이 안 보이면 먼저 네트워크 discovery 문제로 본다.

## 9. 이번 단계 성공 기준

- raw serial에서 NMEA 문장이 보인다.
- ROS 2에서 `/gps/fix`가 보인다.
- `/gps/fix` 타입이 `sensor_msgs/msg/NavSatFix`다.
- `header.frame_id`가 `gps_link`다.
- 야외 또는 창가에서 `status.status`가 fix 상태로 바뀐다.
- 노트북에서 Jetson의 `/gps/fix`를 echo할 수 있다.

## 10. 다음 단계

1. `gps_link` 위치 실측
   - 이미 `trashbot_description`에 `gps_link` frame placeholder가 있다.
   - 실제 안테나 위치가 정해지면 `base_link -> gps_link` 값을 갱신한다.
2. `/imu/data`와 `/gps/fix`를 함께 확인
   - IMU는 기존 `BNO08x` publisher 기준으로 사용한다.
3. `navsat_transform_node` 연결
   - 기존 템플릿: `templates/sensor_fusion_prebuild/navsat_transform.yaml`
4. global EKF 구성
   - 기존 템플릿: `templates/sensor_fusion_prebuild/ekf_global.yaml`

## 주의할 점

- GPS는 실내에서 실패하는 것이 정상에 가깝다. 첫 fix 확인은 가능한 야외에서 한다.
- `gpsd`와 `nmea_navsat_driver`가 같은 serial port를 동시에 잡으면 충돌할 수 있다.
- GPS를 local EKF에 바로 넣기보다, 보통은 `navsat_transform_node`를 거쳐 global EKF에 넣는다.
- GPS 단독 위치는 튈 수 있으므로, 자율주행 위치추정에서는 wheel odom, IMU, GPS를 함께 봐야 한다.
