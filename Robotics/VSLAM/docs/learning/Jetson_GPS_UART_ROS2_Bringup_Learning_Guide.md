# Jetson GPS UART ROS2 Bringup Learning Guide

## 결론

GPS bring-up은 바로 `robot_localization`에 넣는 작업이 아니다.
먼저 `UART raw NMEA 수신`이 되는지 확인하고, 그 다음에 ROS 2 `/gps/fix` topic을 publish한 뒤, 마지막에 VSLAM/IMU/wheel odom과 융합을 고민해야 한다.

현재 프로젝트에서는 Jetson 40핀 UART가 R36.5 DMA/DTB 문제로 막혔고, `PIO` 우회 boot entry에서 `/dev/ttyTHS1` loopback과 GPS NMEA 수신까지 성공한 상태다.
아직 GPS fix는 없으므로 다음 단계는 창가나 야외에서 유효한 fix를 잡는 것이다.

## 먼저 읽을 문서

1. [Jetson_RTABMap_Multi_Session_Workflow_Guide.md](./Jetson_RTABMap_Multi_Session_Workflow_Guide.md)
2. [BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md](./BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md)

실제 실행 절차와 기록 원문은 아래 문서에 있다.

- [29_Jetson_GPS_ROS2_Bringup_Guide.md](../../jetson/guides/29_Jetson_GPS_ROS2_Bringup_Guide.md)
- [2026-05-05 Jetson 작업 일지](../../jetson/daily/2026-05-05/README.md)
- [2026-05-06 Jetson 작업 일지](../../jetson/daily/2026-05-06/README.md)
- [2026-05-06 Jetson R36.5 UART DMA/DTB Issue](../../jetson/notes/troubleshooting/2026-05-06_Jetson_R36_5_UART_DMA_DTB_Issue.md)

## 1. GPS가 VSLAM에서 맡는 역할

`GPS`는 지구 기준의 대략적인 위치를 준다.
`VSLAM`은 카메라 기준으로 상대 이동과 주변 지도를 만든다.

둘은 역할이 다르다.

| 센서 | 잘하는 것 | 약한 것 |
| --- | --- | --- |
| VSLAM | 짧은 구간 상대 이동, 주변 구조 | 장거리 drift, 야외 조명 변화 |
| IMU | 빠른 회전/기울기 변화 | 위치 drift |
| wheel odom | 바퀴 기반 이동량 | 미끄러짐, 바닥 상태 |
| GPS | 야외 전역 위치 기준 | 실내, 건물 주변, 낮은 정밀도 |

그래서 GPS는 RTAB-Map을 대체하는 것이 아니라, 야외에서 전역 위치 기준을 주는 보조 센서로 이해해야 한다.

## 2. 용어를 먼저 잡기

`UART`는 두 장치가 TX/RX 선으로 문자를 주고받는 직렬 통신 방식이다.

`NMEA`는 GPS가 위치 정보를 ASCII 문장으로 내보내는 표준 형식이다.
예를 들면 `$GPGGA`, `$GPRMC` 같은 줄이 나온다.

`fix`는 GPS가 위성 신호를 잡아 유효한 위치를 계산한 상태다.
`fix quality 0`은 아직 위치를 못 잡았다는 뜻이다.

`NavSatFix`는 ROS 2에서 GPS 위치를 담을 때 쓰는 메시지 타입이다.
보통 topic 이름은 `/gps/fix`로 둔다.

## 3. 현재 하드웨어 기준

현재 사용한 모듈:

- `GY-GPS6MV2`
- `u-blox NEO-6M`
- 핀 순서: `VCC RX TX GND`
- 기본 목표: GPS 설정 변경 없이 GPS TX만 Jetson RX로 읽기

기본 배선:

```text
GPS VCC -> Jetson 40핀 pin 1 또는 pin 17  (3.3V)
GPS GND -> Jetson 40핀 pin 6              (GND)
GPS TX  -> Jetson 40핀 pin 10             (UART RX)
GPS RX  -> 연결 안 함
```

주의:

- Jetson GPIO UART는 3.3V 로직이다.
- GPS의 TX/RX 신호선에 5V TTL을 직접 넣으면 위험하다.
- 처음에는 GPS RX를 연결하지 않고 읽기만 하는 편이 안전하다.

## 4. raw serial을 먼저 확인하는 이유

ROS 2 driver를 바로 띄우면 문제가 어디인지 모른다.

먼저 아래 순서로 나눈다.

```text
배선 정상?
  -> UART port 정상?
    -> baudrate 정상?
      -> NMEA 문장 정상?
        -> GPS fix 정상?
          -> ROS 2 /gps/fix publish
```

raw NMEA 확인:

```bash
PORT=/dev/ttyTHS1
stty -F "$PORT" 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo
timeout 30 cat "$PORT"
```

정상 NMEA 예시:

```text
$GPRMC,,V,,,,,,,,,,N*53
$GPGGA,,,,,,0,00,99.99,,,,,,*48
$GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
```

이 예시는 UART 수신은 성공했지만 아직 GPS fix는 없는 상태다.

## 5. R36.5 UART DMA/DTB 문제를 어떻게 분리했나

처음에는 GPS 모듈이나 배선 문제처럼 보였다.
하지만 `pin 8 TX`와 `pin 10 RX`를 직접 연결한 loopback에서도 정상 문자열이 아니라 NUL byte가 들어왔다.

테스트:

```bash
PORT=/dev/ttyTHS1
stty -F "$PORT" 9600 raw -echo

rm -f /tmp/uart_loopback.txt
timeout 5 cat "$PORT" > /tmp/uart_loopback.txt &
READER=$!

sleep 1
printf 'hello-gps-test\r\n' > "$PORT"

wait "$READER"
cat -v /tmp/uart_loopback.txt
```

문제 상태:

```text
^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@
```

커널 로그에서는 SMMU/IOMMU fault와 memory controller error가 반복됐다.
그래서 GPS가 아니라 Jetson R36.5 UART DMA/DTB 문제로 분리했다.

`serial@3100000`의 `dmas`, `dma-names`를 제거한 PIO boot entry에서는 loopback이 성공했다.

검증 명령:

```bash
cd ~/yh_ws/TIL
bash Robotics/VSLAM/jetson/scripts/verify_uarta_pio_loopback.sh
```

성공 신호:

```text
serial-tegra 3100000.serial: RX in PIO mode
serial-tegra 3100000.serial: TX in PIO mode
hello-gps-test^M
```

이후 같은 `/dev/ttyTHS1`에서 GPS NMEA도 정상 수신됐다.

## 6. GPS fix가 없다는 말의 의미

아래 문장은 UART와 GPS 출력은 정상이라는 뜻이다.

```text
$GPRMC,,V,,,,,,,,,,N*53
$GPGGA,,,,,,0,00,99.99,,,,,,*48
$GPGSV,1,1,00*79
```

하지만 위치는 아직 없다.

- `GPRMC V`: invalid, 유효한 위치 없음
- `GPGGA ... 0,00`: fix quality 0, 위성 수 0
- `GPGSV ... 00`: 보이는 위성 정보 없음

다음 확인:

- 안테나가 하늘을 볼 수 있는 위치인지
- 창가나 야외에서 몇 분 기다렸는지
- GPS LED 상태가 변하는지
- 전원이 충분한지
- NMEA 문장이 계속 같은 주기로 나오는지

## 7. ROS 2 `/gps/fix`로 넘어가기

raw NMEA와 fix가 확인된 뒤 ROS 2 driver를 붙인다.

```bash
sudo apt update
sudo apt install -y ros-humble-nmea-navsat-driver
```

예상 topic:

```text
/gps/fix
/gps/vel
/gps/time_reference
```

확인:

```bash
source /opt/ros/humble/setup.bash
ros2 topic list | grep gps
ros2 topic echo /gps/fix --once
```

처음 기대하는 것은 센서 융합이 아니라 `/gps/fix` 메시지가 정상적으로 나오는 것이다.

## 8. 이후 sensor fusion으로 연결할 때

GPS가 `/gps/fix`로 나오면 그 다음에 `robot_localization`을 검토한다.

`robot_localization`은 여러 센서의 odom/IMU/GPS를 섞어 더 안정적인 위치 추정을 만드는 ROS 패키지다.

나중에 연결될 구조:

```text
RTAB-Map visual odom
wheel odom
BNO08x IMU
GPS /gps/fix
        |
        v
robot_localization EKF / navsat_transform
        |
        v
map -> odom -> base_link
```

하지만 지금 단계에서는 아래 순서를 지킨다.

1. raw NMEA 수신
2. GPS fix 확인
3. ROS 2 `/gps/fix` publish
4. 기록 저장
5. 그 다음 sensor fusion 검토

## 9. 흔한 실수

### ROS 2부터 켬

raw serial이 안 되면 ROS 2 driver도 안 된다.
항상 `cat /dev/tty...`로 NMEA를 먼저 본다.

### TX/RX를 반대로 꽂음

GPS `TX`는 Jetson `RX`로 간다.
GPS `RX`는 처음에는 연결하지 않아도 된다.

### fix 없음과 UART 실패를 섞어 판단

NMEA 문장이 보이면 UART는 성공이다.
그 안에서 `V`, `fix quality 0`, `satellite 00`이면 위치 fix가 아직 없는 것이다.

### 실내에서 바로 fix를 기대함

NEO-6M 계열은 실내에서 fix가 오래 걸리거나 안 잡힐 수 있다.
창가나 야외 테스트가 필요하다.

## 10. 다음 학습 목표

이 문서를 이해했다면 다음 질문에 답할 수 있어야 한다.

1. GPS NMEA가 보인다는 것과 GPS fix가 있다는 것은 어떻게 다른가?
2. `/dev/ttyTHS1` loopback 실패를 왜 GPS 문제가 아니라 Jetson UART 문제로 분리했는가?
3. `/gps/fix`가 나온 뒤에도 바로 자율주행이 되는 것이 아닌 이유는 무엇인가?
4. GPS는 VSLAM을 대체하는 센서인가, 보조하는 센서인가?
