# 2026-05-05 Jetson 작업 일지

## 결론

- `GY-GPS6MV2 / u-blox NEO-6M` GPS 모듈을 Jetson Orin Nano에 직접 UART 핀으로 연결하는 방향으로 정했다.
- 첫 확인은 GPS 설정 변경 없이 `GPS TX -> Jetson UART RX` 단방향 수신으로 진행한다.
- `dialout` 그룹 추가와 SSH 재접속으로 serial 포트 접근 권한은 해결했다.
- 현재 `/dev/ttyTHS1`에서 깨진 문자가 들어오는 것은 확인했지만, 아직 정상 NMEA 문장(`$GPGGA`, `$GPRMC`)은 확인하지 못했다.
- 다음 1순위는 `/dev/ttyTHS1` 기준으로 전원, 배선, baudrate를 다시 분리해 정상 NMEA 문장을 받는 것이다.

## 오늘 작업 한 줄 요약

- GPS 모듈 실물을 확인하고, CP2102 없이 Jetson 40핀 헤더 UART에 직접 연결하는 bring-up 절차를 정리했다.

## 현재 작업 형태

- 작업은 SSH 터미널 기준으로 진행 중이다.
- GUI는 Jetson에서 띄우지 않고, 이후 ROS 2 topic은 노트북에서 구독해 확인하는 구조를 유지한다.
- GPS 모듈은 사진 기준 `VCC RX TX GND` 핀이 있는 `GY-GPS6MV2 / NEO-6M` 보드다.

## 시간순 기록

### GPS 모듈 확인

- 사용 모듈:
  - `[Voltly] 아두이노 GY-GPS6MV2 GPS 수신 모듈 NEO-6M [VLT-GPS001]`
  - 보드 실크: `GY-GPS6MV2`
  - 핀 순서: `VCC RX TX GND`
- 안테나는 u.FL 케이블로 연결된 외장 패치 안테나 형태다.
- NMEA UART 출력 모듈로 보고 `nmea_navsat_driver` 연동을 우선한다.

### 직접 GPIO UART 연결 방향 확정

처음 테스트 배선:

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

판단:

- Jetson GPIO UART는 3.3V 로직이다.
- 위험한 지점은 `VCC 5V` 자체보다 `RX/TX` 신호선에 5V TTL이 들어가는 경우다.
- 첫 bring-up에서는 GPS가 내보내는 NMEA만 읽으면 되므로 `GPS RX`는 연결하지 않는 편이 안전하다.

### Jetson serial device 후보 확인

실행:

```bash
ls -l /dev/ttyTHS* /dev/ttyS* 2>/dev/null
dmesg | grep -i tty | tail -n 50
```

관찰:

```text
crw-rw---- 1 root dialout   4, 64 Mar 24 22:52 /dev/ttyS0
crw-rw---- 1 root dialout   4, 65 Mar 24 22:52 /dev/ttyS1
crw-rw---- 1 root dialout   4, 66 Mar 24 22:52 /dev/ttyS2
crw-rw---- 1 root dialout   4, 67 Mar 24 22:52 /dev/ttyS3
crw-rw---- 1 root dialout 240,  1 Mar 24 22:52 /dev/ttyTHS1
crw-rw---- 1 root dialout 240,  2 Mar 24 22:52 /dev/ttyTHS2
dmesg: read kernel buffer failed: Operation not permitted
```

해석:

- 포트 후보는 `/dev/ttyTHS1`, `/dev/ttyTHS2`, `/dev/ttyS0`~`/dev/ttyS3`다.
- `dmesg`는 일반 사용자 권한에서 막혀 있으므로 필요하면 `sudo dmesg`로 본다.

### 사용자 그룹 확인

실행:

```bash
groups
```

관찰:

```text
jetson adm cdrom sudo audio dip video plugdev render i2c lpadmin gdm sambashare docker weston-launch gpio
```

해석:

- `dialout` 그룹이 없다.
- serial device가 `root:dialout` 권한이므로, 다음 단계 전에 `dialout` 추가가 필요하다.

### dialout 그룹 추가 후 재접속

실행:

```bash
sudo usermod -aG dialout "$USER"
```

SSH 재접속 후 확인:

```bash
groups
```

관찰:

```text
jetson adm dialout cdrom sudo audio dip video plugdev render i2c lpadmin gdm sambashare docker weston-launch gpio
```

해석:

- `dialout`이 추가되어 serial device 접근 권한은 해결됐다.
- 이후 `stty`, `cat`을 일반 사용자로 실행할 수 있는 상태가 됐다.

### GPS 연결 후 포트별 raw 수신 테스트

GPS 연결 후 실행:

```bash
GPS_BAUD=9600

for p in /dev/ttyTHS1 /dev/ttyTHS2 /dev/ttyS0 /dev/ttyS1 /dev/ttyS2 /dev/ttyS3; do
  echo "=== $p ==="
  stty -F "$p" "$GPS_BAUD" raw -echo
  timeout 5 cat "$p"
done
```

관찰:

```text
=== /dev/ttyTHS1 ===





=== /dev/ttyTHS2 ===
=== /dev/ttyS0 ===
stty: /dev/ttyS0: Input/output error
cat: /dev/ttyS0: Input/output error
=== /dev/ttyS1 ===
stty: /dev/ttyS1: Input/output error
cat: /dev/ttyS1: Input/output error
=== /dev/ttyS2 ===
stty: /dev/ttyS2: Input/output error
cat: /dev/ttyS2: Input/output error
=== /dev/ttyS3 ===
stty: /dev/ttyS3: Input/output error
cat: /dev/ttyS3: Input/output error
```

해석:

- `/dev/ttyS0`~`/dev/ttyS3`는 현재 테스트 대상으로 적합하지 않다.
- `/dev/ttyTHS1`, `/dev/ttyTHS2`가 실제 후보이며, 이후 로그상 `/dev/ttyTHS1`에 집중하는 것이 맞다.

### `/dev/ttyTHS1` baudrate sweep

실행:

```bash
for baud in 4800 9600 19200 38400 57600 115200; do
  echo "##### /dev/ttyTHS1 baud=$baud #####"
  stty -F /dev/ttyTHS1 "$baud" cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo
  timeout 5 cat /dev/ttyTHS1
  echo
done
```

관찰:

```text
##### /dev/ttyTHS1 baud=4800 #####
b�
bb
##### /dev/ttyTHS1 baud=9600 #####






##### /dev/ttyTHS1 baud=19200 #####
`怘��`怘�怘�3�
##### /dev/ttyTHS1 baud=38400 #####
�x�x�x�x�x
##### /dev/ttyTHS1 baud=57600 #####
�����������������������������������
##### /dev/ttyTHS1 baud=115200 #####
```

해석:

- `/dev/ttyTHS1`에서 신호가 완전히 없는 것은 아니다.
- 정상 NMEA ASCII 문장 대신 깨진 문자가 들어오므로 아래 가능성을 우선 본다.
  - baudrate 불일치
  - GPS 전원 불안정
  - GPS `TX`와 Jetson `RX` 배선 위치 오류
  - GPS 모듈의 핀 순서 오인
  - Jetson pin 10이 아닌 다른 UART RX에 연결됨

### 3.3V 전원 상태에서 `/dev/ttyTHS1` 장시간 cat

아직 `VCC`는 3.3V에 연결된 상태이며, `/dev/ttyTHS1`을 조금 더 길게 확인했다.

실행:

```bash
stty -F /dev/ttyTHS1 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo
timeout 30 stdbuf -o0 cat /dev/ttyTHS1
```

관찰:

```text
B
A
9
8
7
6
E
F
C
D
A
B
8
9
6
7
C
D
E
F
8
9
A
B
4
5
D
C
F
E
```

해석:

- 3.3V 전원 상태에서도 `/dev/ttyTHS1`에서 문자는 들어오지만 정상 NMEA 문장은 아니다.
- `$GPGGA`, `$GPRMC`처럼 `$`로 시작하는 완전한 ASCII 문장이 없으므로 아직 GPS UART 수신 성공으로 볼 수 없다.
- 반복되는 hex 문자 조각만 보이므로, baudrate보다 배선/핀 위치/접촉 문제 또는 floating 입력 가능성을 우선 확인한다.
- GPS LED가 아직 켜지지 않는다면, 다음 단계에서 `VCC`만 5V로 바꾸어 전원 문제를 분리한다.

### `cat -v`로 control character 확인

GPS LED는 3.3V 전원에서도 깜빡이는 상태라고 확인했다.

실행:

```bash
stty -F /dev/ttyTHS1 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo
timeout 30 cat -v /dev/ttyTHS1
```

관찰 요약:

```text
^@
^@^F^X^@^@^P^@)^@...
...
,D*6F^M
...
,D*64^M
...
*67^M
*68^M
```

해석:

- `^@`는 NUL byte가 대량으로 들어온다는 뜻이다.
- NMEA라면 `$GPGGA`, `$GPRMC`, `$GNGGA`처럼 `$`로 시작하는 printable ASCII 문장이 반복되어야 한다.
- `,D*64`나 `*67` 같은 checksum 조각처럼 보이는 부분은 있지만, 문장 앞부분이 대부분 NUL로 들어오므로 정상 NMEA 수신으로 볼 수 없다.
- GPS LED가 깜빡이므로 전원 자체는 들어온 것으로 보이며, 다음에는 `TX/RX 배선`, `Jetson pin 10 위치`, `RX line floating`, `UART port/pinmux`를 우선 확인한다.

### Jetson pin 8-10 UART loopback 확인

GPS 모듈을 UART 선에서 분리하고, Jetson 40핀 헤더의 `pin 8`과 `pin 10`을 서로 직접 연결해 loopback을 확인했다.

첫 번째 `/dev/ttyTHS1` 테스트:

```bash
stty -F /dev/ttyTHS1 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo

cat /dev/ttyTHS1 &
CAT_PID=$!

printf 'hello-gps-test\r\n' > /dev/ttyTHS1
sleep 1

kill "$CAT_PID"
```

관찰:

```text
[1]+  Terminated              cat /dev/ttyTHS1
[1] 4620
```

두 번째 `/dev/ttyTHS2` 파일 방식 테스트:

```bash
PORT=/dev/ttyTHS2

stty -F "$PORT" 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo

rm -f /tmp/uart_loopback.txt
timeout 5 cat "$PORT" > /tmp/uart_loopback.txt &
sleep 1

printf 'hello-gps-test\r\n' > "$PORT"
sleep 1

cat -v /tmp/uart_loopback.txt
```

관찰:

```text
^@^@
```

해석:

- 기대한 `hello-gps-test`가 돌아오지 않았으므로 `/dev/ttyTHS1`, `/dev/ttyTHS2` 모두 loopback 성공으로 볼 수 없다.
- pin 8-10을 실제로 연결했는데도 loopback이 실패했으므로, 다음에는 GPS보다 Jetson header UART 경로를 먼저 확정해야 한다.
- 우선 확인할 것:
  - 40핀 헤더 physical pin 번호 방향
  - pin 8/10이 실제로 OS에서 어떤 `/dev/tty*`로 매핑되는지
  - Jetson header UART pinmux 활성화 여부
  - loopback 점퍼 접촉 상태

세 번째 `/dev/ttyTHS1`, `/dev/ttyTHS2`, `/dev/ttyAMA0` 전체 후보 loopback 테스트:

```bash
for PORT in /dev/ttyTHS1 /dev/ttyTHS2 /dev/ttyAMA0; do
  echo "===== $PORT ====="
  stty -F "$PORT" 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo 2>/tmp/stty_err || {
    cat /tmp/stty_err
    continue
  }

  rm -f /tmp/uart_loopback.txt
  timeout 4 cat "$PORT" > /tmp/uart_loopback.txt &
  READER=$!

  sleep 0.5
  printf 'hello-gps-test\r\n' > "$PORT"
  wait "$READER"

  cat -v /tmp/uart_loopback.txt
  echo
done
```

관찰:

```text
===== /dev/ttyTHS1 =====
Exit 124
^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@
===== /dev/ttyTHS2 =====
Exit 124
^@^@
===== /dev/ttyAMA0 =====
stty: /dev/ttyAMA0: unable to perform all requested operations
```

해석:

- `/dev/ttyTHS1`, `/dev/ttyTHS2` 모두 `hello-gps-test`가 돌아오지 않았다.
- `/dev/ttyAMA0`는 같은 `stty` 옵션을 적용하지 못했다.
- 40핀 헤더 UART가 현재 활성화되지 않았거나, physical pin 번호를 잘못 잡았거나, 해당 핀이 `/dev/ttyTHS1/2`와 연결되지 않은 상태일 수 있다.

리부트 후 `/dev/ttyTHS1`, `/dev/ttyTHS2`를 `9600`, `115200`에서 다시 loopback 테스트했다.

실행:

```bash
for PORT in /dev/ttyTHS1 /dev/ttyTHS2; do
  for BAUD in 9600 115200; do
    echo "===== $PORT baud=$BAUD ====="

    stty -F "$PORT" "$BAUD" cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo

    rm -f /tmp/uart_loopback.txt
    timeout 5 cat "$PORT" > /tmp/uart_loopback.txt &
    READER=$!

    sleep 1
    printf 'hello-gps-test\r\n' > "$PORT"

    wait "$READER"
    cat -v /tmp/uart_loopback.txt
    echo
  done
done
```

관찰:

```text
===== /dev/ttyTHS1 baud=9600 =====
^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@
===== /dev/ttyTHS1 baud=115200 =====
^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@
===== /dev/ttyTHS2 baud=9600 =====
^@^@
===== /dev/ttyTHS2 baud=115200 =====
^@
```

해석:

- `9600`, `115200` 모두 `hello-gps-test`가 돌아오지 않았다.
- 반복되는 `^@`는 UART NUL byte로, loopback 성공 신호가 아니다.
- pin 8/10 점퍼 상태에서도 같은 결과이므로 baudrate 문제가 아니라 physical pin 위치, 점퍼 접촉, 또는 `/dev/ttyTHS*` 매핑 문제를 먼저 확인한다.

Python `termios`로 같은 포트를 한 번만 열어 loopback을 재확인했다.

실행:

```bash
python3 - <<'PY'
import os, termios, time, select

ports = ["/dev/ttyTHS1", "/dev/ttyTHS2", "/dev/ttyAMA0"]
msg = b"hello-gps-test\r\n"

for port in ports:
    print(f"===== {port} =====")
    try:
        fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except OSError as e:
        print("open failed:", e)
        continue

    try:
        attrs = termios.tcgetattr(fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attrs[3] = 0
        attrs[4] = termios.B9600
        attrs[5] = termios.B9600
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        termios.tcflush(fd, termios.TCIOFLUSH)

        os.write(fd, msg)
        end = time.time() + 3
        data = b""

        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.2)
            if r:
                chunk = os.read(fd, 1024)
                if chunk:
                    data += chunk

        print(repr(data))
    finally:
        os.close(fd)
PY
```

관찰:

```text
===== /dev/ttyTHS1 =====
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
===== /dev/ttyTHS2 =====
b''
===== /dev/ttyAMA0 =====
b''
```

해석:

- `/dev/ttyTHS1`은 데이터를 읽지만, 기대한 `hello-gps-test`가 아니라 NUL byte만 들어온다.
- `/dev/ttyTHS2`, `/dev/ttyAMA0`는 loopback 데이터가 없다.
- `uarta (8,10)`는 Jetson-IO에서 활성화되어 있으므로, 다음에는 TX pin이 실제로 high/idle 상태인지와 RX가 low로 당겨지는 원인을 물리적으로 확인해야 한다.

### Jetson-IO 화면 확인

Jetson-IO의 `Select desired functions (for pins)` 화면을 확인했다.

관찰:

```text
[*] uarta          (8,10)
[*] unused         uarta-cts/rts (11,36)
```

해석:

- `pin 8 / pin 10`의 `uarta` 기능은 Jetson-IO 상에서 이미 활성화되어 있다.
- `CTS/RTS` 하드웨어 flow control은 사용하지 않는 상태라 GPS UART 수신에는 맞는 설정이다.
- 따라서 다음 우선순위는 Jetson-IO 활성화가 아니라, `uarta`가 실제 어떤 `/dev/tty*`와 매핑되는지와 pin 8/10 물리 위치 및 점퍼 접촉을 다시 확인하는 것이다.

## 오늘 관찰한 핵심 현상

- GPS 모듈은 UART 직접 연결 가능한 형태다.
- Jetson에는 UART device 후보가 이미 보인다.
- `dialout` 추가 후 serial device 권한은 해결됐다.
- `/dev/ttyTHS1`에서 깨진 문자와 hex 문자 조각이 들어오므로 신호는 일부 들어오는 것으로 보인다.
- pin 8-10 loopback이 아직 성공하지 않았으므로 GPS 테스트보다 Jetson UART 경로 검증이 먼저다.
- 아직 정상 raw NMEA 출력은 확인하지 않았다.
- 아직 ROS 2 `/gps/fix` topic publish는 진행하지 않았다.

## 해결 방법

`jetson` 사용자를 `dialout` 그룹에 추가했다.

```bash
sudo usermod -aG dialout "$USER"
```

그다음 SSH를 끊고 다시 접속한 뒤 확인한다.

```bash
groups
```

`dialout` 확인 후 포트별 raw NMEA 확인을 진행했다.

```bash
GPS_BAUD=9600

for p in /dev/ttyTHS1 /dev/ttyTHS2 /dev/ttyS0 /dev/ttyS1 /dev/ttyS2 /dev/ttyS3; do
  echo "=== $p ==="
  stty -F "$p" "$GPS_BAUD" raw -echo
  timeout 5 cat "$p"
done
```

기대:

```text
$GPGGA,...
$GPRMC,...
$GNGGA,...
$GNRMC,...
```

다음에는 `/dev/ttyTHS1` 기준으로 배선과 전원을 다시 확인한다.

```text
GPS VCC -> Jetson 40핀 pin 1 또는 pin 17  (3.3V)
GPS GND -> Jetson 40핀 pin 6              (GND)
GPS TX  -> Jetson 40핀 pin 10             (UART RX)
GPS RX  -> 연결 안 함 또는 Jetson pin 8   (UART TX)
```

3.3V 전원에서 LED가 약하거나 출력이 계속 깨지면 `VCC`만 5V로 바꾸어 확인할 수 있다. 단, `RX/TX` 신호선은 Jetson 3.3V UART에만 연결한다.

## 오늘 만든/수정한 파일

- [2026-05-05 Jetson 작업 일지](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/daily/2026-05-05/README.md)
- [29_Jetson_GPS_ROS2_Bringup_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/29_Jetson_GPS_ROS2_Bringup_Guide.md)
- [daily README](/home/jetson/yh_ws/TIL/Robotics/VSLAM/daily/README.md)
- [jetson README](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/README.md)

## 남은 문제

- 정상 NMEA가 나오지 않고 `/dev/ttyTHS1`에서 깨진 문자와 hex 문자 조각만 관찰됐다.
- 실제 사용 포트는 `/dev/ttyTHS1`일 가능성이 높지만 아직 확정은 아니다.
- Jetson pin 8-10 loopback에서 `/dev/ttyTHS1`, `/dev/ttyTHS2` 모두 `hello-gps-test`가 돌아오지 않았다.
- Jetson-IO에서는 `uarta (8,10)`가 이미 활성화되어 있다.
- 리부트 후 `9600`, `115200` loopback 재테스트에서도 `/dev/ttyTHS1`, `/dev/ttyTHS2` 모두 NUL byte만 관찰됐다.
- Python `termios` loopback에서도 `/dev/ttyTHS1`은 NUL byte만 읽히고 `/dev/ttyTHS2`, `/dev/ttyAMA0`는 비어 있었다.
- GPS raw NMEA 문장 수신 성공 여부가 아직 미확인이다.
- `ros-humble-nmea-navsat-driver` 설치와 `/gps/fix` publish는 다음 단계다.

## 다음 액션

1. Jetson 40핀 헤더 physical pin 8/10 방향 재확인
2. pin 8-10 loopback을 `/dev/ttyTHS1`, `/dev/ttyTHS2`에서 다시 검증
3. loopback이 성공하는 `/dev/tty*`를 먼저 확정
4. 그다음 GPS `TX -> Jetson RX`를 연결해 NMEA 확인
5. NMEA가 나오면 `nmea_navsat_driver`로 `/gps/fix` publish

## 한 줄 회고

- 오늘은 GPS를 바로 ROS 2에 붙이기 전, Jetson serial 권한을 해결하고 `/dev/ttyTHS1`에서 신호가 들어오는 단계까지 확인했다.
