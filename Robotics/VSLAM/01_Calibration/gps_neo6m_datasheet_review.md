# NEO-6M GPS Datasheet Review

## 결론

사용자가 제공한 이미지의 성능표는 Gazebo에서 `/gps/fix`를 대략 시뮬레이션하고, ROS2 `sensor_msgs/NavSatFix` topic 수신 여부를 검증하는 데는 충분하다.
하지만 실제 Jetson에서 GPS 모듈을 연결하고 드라이버를 안정적으로 띄우기에는 부족하다.

현재 이미지만으로 쓸 수 있는 값:

```text
receiver: u-blox NEO-6 계열, NEO-6M 성능 기준
receiver_type: 50 channels, GPS L1 C/A, SBAS WAAS/EGNOS/MSAS
update_rate: NEO-6M 기준 최대 5 Hz
horizontal_position_accuracy: GPS 2.5 m, SBAS 2.0 m
velocity_accuracy: 0.1 m/s
heading_accuracy: 0.5 deg
TTFF: cold/warm 27 s, hot 1 s, aided < 3 s
sensitivity: tracking -161 dBm, reacquisition -160 dBm
operational_limits: 4 g, 50,000 m, 500 m/s
```

주의:

- 공식 u-blox NEO-6 Data Sheet의 GPS performance 표는 TTFF와 sensitivity에서는 `NEO-6M/V`를 같은 열로 묶는다.
- 하지만 maximum navigation update rate는 `NEO-6G/Q/M/T = 5 Hz`, `NEO-6P/V = 1 Hz`로 나뉜다.
- 따라서 Mari에 NEO-6M을 쓴다는 전제에서는 Gazebo GPS publish rate를 5 Hz로 두는 것이 datasheet 상한과 맞다.
- 실제 breakout board는 보통 기본 출력 설정이 1 Hz일 수 있으므로, 하드웨어 연결 후에는 실제 NMEA/UBX 출력 주기를 다시 확인해야 한다.

Gazebo 초기값:

```text
/gps/fix rate: 5 Hz
position noise: meter-level rough GPS noise
ROS message: sensor_msgs/NavSatFix
```

## 부족한 정보

실제 하드웨어 연결 전에는 아래 정보를 추가로 확인해야 한다.

| 필요 정보 | 왜 필요한가 |
| --- | --- |
| 정확한 모듈명 | NEO-6M, NEO-6MV2 breakout, 호환/클론 보드에 따라 전원/핀/안테나 회로가 다를 수 있음 |
| 인터페이스 | UART, USB, I2C/DDC, SPI 중 실제로 Jetson에 무엇으로 연결할지 결정 필요 |
| 전원 전압/전류 | NEO-6M 칩 전압과 breakout board 입력 전압이 다를 수 있음 |
| 기본 baud rate | ROS driver 또는 serial reader 설정에 필요 |
| 출력 프로토콜 | NMEA sentence를 읽을지, u-blox UBX binary를 읽을지 결정 필요 |
| 기본 출력 sentence | GGA/RMC/VTG/GSA/GSV 등 어떤 메시지가 나오는지 확인 필요 |
| update rate 설정 방법 | 기본 1 Hz인지, 5 Hz로 올릴 수 있는지 확인 필요 |
| antenna 정보 | active/passive antenna, 안테나 전원, 하늘 시야 확보 여부가 fix 품질에 직접 영향 |
| PPS/TIMEPULSE 사용 여부 | timestamp sync를 할 계획이면 필요 |
| 장착 위치 | `gps_link`가 모듈 중심인지 안테나 위상 중심인지 확인 필요 |
| covariance 산정 | `/gps/fix.position_covariance`에 어떤 분산값을 넣을지 결정 필요 |

## ROS2 적용 판단

Gazebo simulation:

- 현재 이미지 정보만으로 충분하다.
- `/gps/fix`를 5 Hz로 publish하고, 위치 오차는 meter-level로 두면 된다.
- 다만 Gazebo GPS plugin은 현재 `frame_id=base_footprint`로 나오므로, antenna lever arm 검증은 별도 보정이 필요하다.

실제 Jetson 연결:

- 이미지 정보만으로는 부족하다.
- 최소한 실제 모듈 라벨/보드 사진, 연결 방식, UART baud, 출력 문장, 실내/실외 fix 여부를 확인해야 한다.
- 연결 후 첫 검증은 `/gps/fix`의 값이 생기는지, `status.status >= 0`인지, `position_covariance`가 들어오는지 확인하는 것이다.

## 추천 ROS topic 계약

```text
topic: /gps/fix
type: sensor_msgs/msg/NavSatFix
frame_id: gps_link 권장
rate: 1-5 Hz
```

GPS 속도까지 별도로 쓰면:

```text
topic: /gps/velocity
type: geometry_msgs/msg/Vector3Stamped
frame_id: gps_link 권장
```

## 출처

- u-blox, `NEO-6 Data Sheet`, document `GPS.G6-HW-09005`.
  - GPS 성능표에 50 channels, GPS L1 C/A, SBAS, NEO-6M/V cold/warm/hot start, sensitivity, maximum navigation update rate, horizontal accuracy, velocity accuracy, heading accuracy, operational limits가 정리되어 있다.
  - 공식 표 기준 maximum navigation update rate는 `NEO-6G/Q/M/T = 5 Hz`, `NEO-6P/V = 1 Hz`이다.
  - 기본 설정에는 Serial Port 1 9600 baud, NMEA/UBX protocol, 시작 시 활성 NMEA message `GGA, GLL, GSA, GSV, RMC, VTG, TXT`가 명시되어 있다.
  - https://content.u-blox.com/sites/default/files/products/documents/NEO-6_DataSheet_%28GPS.G6-HW-09005%29.pdf

- u-blox, `u-blox 6 Receiver Description Including Protocol Specification`, document `GPS.G6-SW-10018`.
  - NMEA/UBX protocol, receiver configuration, navigation platform model, serial communication, message configuration을 확인할 때 필요하다.
  - https://content.u-blox.com/sites/default/files/products/documents/u-blox6_ReceiverDescrProtSpec_%28GPS.G6-SW-10018%29_Public.pdf

- u-blox, `NEO-6 series` product page.
  - NEO-6 계열이 older/EOL 제품군이며, UART/USB/DDC/SPI 인터페이스를 제공한다는 제품군 정보를 확인할 수 있다.
  - https://www.u-blox.com/en/product/neo-6-series?legacy=Current

## 다음 확인 항목

1. 실제 GPS 모듈/보드 사진에서 정확한 제품명을 확인한다.
2. Jetson 연결 방식이 UART인지 USB인지 정한다.
3. 기본 baud rate와 NMEA 출력 문장을 확인한다.
4. 실외에서 fix가 잡히는지 확인한다.
5. `/gps/fix`를 `gps_link` 기준으로 publish하도록 driver 또는 republisher를 정리한다.
