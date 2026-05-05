# 2026-05-06 Jetson 작업 일지

## 결론

- `Jetson Orin Nano` 40핀 헤더 `pin 8/10` UART loopback 실패 원인을 GPS 모듈이 아니라 `Jetson Linux R36.5.0`의 UART DMA/DTB 문제 쪽으로 분리했다.
- `/dev/ttyTHS1`은 `pin 8 TX`를 실제로 구동하지만, `pin 10 RX`로 돌아온 데이터가 `hello-gps-test`가 아니라 NUL byte로 읽힌다.
- `dmesg`에서 SMMU/IOMMU와 memory controller fault가 반복되어, R36.5 UART DMA/Device Tree 문제 가능성이 높다.
- `serial@3100000`의 `dmas`, `dma-names`를 제거한 PIO 테스트용 DTB로 부팅하자 `/dev/ttyTHS1` loopback이 `hello-gps-test^M`로 성공했다.
- 따라서 현재 원인은 `R36.5`의 UART DMA/DTB 설정 문제로 사실상 확인됐다.
- GPS를 다시 연결하자 `/dev/ttyTHS1`에서 정상 NMEA 문장이 수신됐다.
- 아직 fix는 없지만, GPS UART bring-up 자체는 성공했다.
- 진행 중 Jetson이 갑자기 shutdown되는 현상이 있었다. 원인은 아직 미확정이며 전원/열/커널 fault/물리 접촉 문제로 별도 분리해 기록한다.

## 오늘 작업 한 줄 요약

- Jetson 40핀 UART loopback 실패를 재현하고, 커널 로그와 버전 정보를 근거로 R36.5 UART DMA/DTB 이슈로 문서화했다.

## 현재 작업 형태

- Jetson 로컬 터미널과 SSH 맥락에서 테스트했다.
- GPS 모듈은 일단 문제 원인에서 분리하고, Jetson 자체 `pin 8 <-> pin 10` loopback을 기준으로 판단했다.

## 시간순 기록

### UART loopback 재현

`pin 8`과 `pin 10`을 직접 점퍼로 연결한 상태에서 `/dev/ttyTHS1` loopback을 테스트했다.

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

관찰:

```text
^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@
```

해석:

- `hello-gps-test\r\n`는 16바이트다.
- 수신 결과도 16바이트지만, 내용이 전부 `0x00`이다.
- UART RX가 이벤트는 받지만 정상 데이터를 가져오지 못하는 상태로 본다.

### `/dev/ttyTHS1`, `/dev/ttyTHS2`, `/dev/ttyAMA0` 동시 확인

세 포트를 동시에 읽고 `/dev/ttyTHS1`에 문자열을 보냈다.

관찰:

```text
ttyTHS1: ^@ 16개
ttyTHS2: ^@ 2개
ttyAMA0: empty
```

해석:

- 다른 UART device에 정상 문자열이 숨어 있는 상황은 아니었다.
- `/dev/ttyTHS1`만 보낸 바이트 수만큼 NUL byte를 읽었다.

### Jetson Linux 버전 확인

```bash
head -n 1 /etc/nv_tegra_release
dpkg-query -W nvidia-l4t-core nvidia-jetpack 2>/dev/null
uname -a
```

관찰:

```text
# R36 (release), REVISION: 5.0, GCID: 43688277, BOARD: generic, EABI: aarch64, DATE: Fri Jan 16 03:50:45 UTC 2026
nvidia-l4t-core 36.5.0-20260115194252
Linux ubuntu 5.15.185-tegra #1 SMP PREEMPT Thu Jan 15 19:24:38 PST 2026 aarch64
```

### kernel log 확인

```bash
sudo dmesg -T | grep -iE 'serial|uart|dma|smmu|fault|tegra' | tail -n 100
```

관찰 요약:

```text
arm-smmu 12000000.iommu: Unhandled context fault
tegra-mc 2c00000.memory-controller: EMEM address decode error
tegra-mc 2c00000.memory-controller: VPR violation
tegra-mc 2c00000.memory-controller: Route Sanity error
```

해석:

- 배선이나 GPS 모듈에서 직접 발생하는 로그가 아니다.
- UART RX DMA와 SMMU/IOMMU 메모리 접근 설정 문제와 맞는 신호로 판단한다.

### PIO mode 우회 적용 후 loopback 성공

`serial@3100000`의 `dmas`, `dma-names`를 제거한 테스트용 DTB를 적용하고 `JetsonIO-UARTA-PIO` boot entry로 재부팅했다.

검증:

```bash
cd ~/yh_ws/TIL
bash Robotics/VSLAM/jetson/scripts/verify_uarta_pio_loopback.sh
```

관찰:

```text
DEFAULT JetsonIO-UARTA-PIO
FDT /boot/dtb/kernel_tegra234-p3768-0000+p3767-0005-nv-super-uarta-pio.dtb

status: okay
compatible: nvidia,tegra194-hsuart
dma-names: <missing>
dmas: <missing>

hello-gps-test^M
```

커널 로그:

```text
serial-tegra 3100000.serial: RX in PIO mode
serial-tegra 3100000.serial: TX in PIO mode
3100000.serial: ttyTHS1 at MMIO 0x3100000 (irq = 112, base_baud = 0) is a TEGRA_UART
```

해석:

- `/dev/ttyTHS1` loopback이 정상 문자열로 돌아왔다.
- `R36.5` 기본 DTB의 UART DMA 설정이 문제였다는 가설이 확인됐다.
- 이제 GPS는 CP2102 없이도 Jetson 40핀 UART에 다시 연결해 확인할 수 있다.

### GPS NMEA 수신 성공

loopback 점퍼를 제거하고 GPS를 다시 연결했다.

```text
GPS VCC -> Jetson 3.3V
GPS GND -> Jetson GND
GPS TX  -> Jetson pin 10
GPS RX  -> 연결 안 함
```

실행:

```bash
PORT=/dev/ttyTHS1
stty -F "$PORT" 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo
timeout 30 cat "$PORT"
```

관찰:

```text
$GPRMC,,V,,,,,,,,,,N*53
$GPVTG,,,,,,,,,N*30
$GPGGA,,,,,,0,00,99.99,,,,,,*48
$GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
$GPGSV,1,1,00*79
$GPGLL,,,,,,V,N*64
```

해석:

- NMEA 문장이 정상 ASCII로 반복 출력된다.
- `GPRMC`의 `V`는 invalid, 즉 아직 유효한 위치 fix가 없다는 뜻이다.
- `GPGGA`의 fix quality `0`, satellite count `00`도 아직 fix가 없음을 의미한다.
- `GPGSV,1,1,00`은 현재 위성 정보가 없다는 뜻이다.
- 따라서 UART/GPS raw 수신은 성공했고, 다음 문제는 실내 수신/안테나 위치/fix 대기 문제다.

### 갑작스러운 shutdown 관찰

진행 중 Jetson이 갑자기 shutdown되는 현상이 있었다.

현재 판단:

- 아직 직접 원인은 확인하지 않았다.
- UART DMA/DTB 문제와 별도 현상으로 분리한다.
- 원인 후보는 전원 순간 부족, 열, kernel fault, 40핀 header 배선 중 순간 접촉이다.
- 다음에 재현되면 `journalctl -b -1`, `last -x`, `tegrastats`로 먼저 확인한다.

확인 명령:

```bash
last -x | head -n 30
journalctl --list-boots
journalctl -b -1 -p warning..alert --no-pager | tail -n 120
journalctl -b -1 --no-pager | grep -iE 'shutdown|reboot|power|thermal|overtemp|watchdog|panic|oops|fault|smmu|tegra' | tail -n 160
tegrastats --interval 1000
```

## 오늘 관찰한 핵심 현상

- Jetson-IO에서 `uarta (8,10)`는 활성화되어 있다.
- `/dev/ttyTHS1`은 `pin 8 TX`를 실제로 구동한다.
- `pin 8 <-> pin 10` continuity와 두 핀의 `3.2V` 전압은 확인됐다.
- 기본 DTB에서는 loopback 결과가 정상 ASCII가 아니라 NUL byte였다.
- R36.5.0 기본 DMA 설정에서는 SMMU/IOMMU fault가 반복됐다.
- PIO 우회 DTB에서는 `/dev/ttyTHS1` loopback이 정상 성공했다.
- GPS 재연결 후 `/dev/ttyTHS1`에서 NMEA 문장이 정상 수신됐다.
- 작업 중 갑작스러운 shutdown이 있었고, 원인은 아직 미확정이다.

## 원인 가설

- 낮은 가능성:
  - GPS 실내 수신 실패
  - GPS baudrate 불일치
  - pin 8/10 단순 배선 오류
  - 새 Jetson 보드의 물리적 pin 손상
- 높은 가능성:
  - `Jetson Linux R36.5.0`의 UART DMA/DTB 설정 문제
  - `/dev/ttyTHS1` RX DMA buffer 또는 SMMU/IOMMU mapping 문제
- 확인:
  - PIO 우회 후 loopback 성공으로 DMA/DTB 문제 가설을 확인했다.

## 해결 방향

- 현재는 `JetsonIO-UARTA-PIO` boot entry를 유지하고 내장 UART로 GPS raw NMEA 수신을 다시 시도한다.
- CP2102 또는 FT232 계열 USB-UART bridge는 예비 우회 수단으로 확보한다.
- 내장 UART 장기 운영은 PIO mode 유지 또는 NVIDIA의 `iommus` 수정안 적용 여부를 별도 검토한다.
- 동시에 PIO 우회 실험을 위해 `serial@3100000`의 `dmas`, `dma-names`를 제거한 테스트용 DTB와 적용/검증 스크립트를 준비했다.

초기 GPS 직접 UART 재연결:

```text
GPS VCC -> Jetson 40핀 pin 1 또는 pin 17  (3.3V부터 재시도)
GPS GND -> Jetson 40핀 GND
GPS TX  -> Jetson 40핀 pin 10             (UART RX)
GPS RX  -> 연결 안 함
```

raw NMEA 확인:

```bash
PORT=/dev/ttyTHS1
stty -F "$PORT" 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo
timeout 30 cat "$PORT"
```

예비 CP2102 연결:

```text
GPS VCC -> CP2102 3.3V 또는 GPS 모듈 허용 전압
GPS GND -> CP2102 GND
GPS TX  -> CP2102 RXD
GPS RX  -> 연결 안 함
```

확인 명령:

```bash
ls -l /dev/ttyUSB*
stty -F /dev/ttyUSB0 9600 raw -echo
timeout 30 cat /dev/ttyUSB0
```

내장 UART PIO 우회 실험:

```bash
cd ~/yh_ws/TIL
sudo bash Robotics/VSLAM/jetson/scripts/apply_uarta_pio_dtb.sh
sudo reboot
```

재부팅 후 `pin 8 <-> pin 10` 연결 상태에서:

```bash
cd ~/yh_ws/TIL
bash Robotics/VSLAM/jetson/scripts/verify_uarta_pio_loopback.sh
```

## 오늘 만든/수정한 파일

- [2026-05-06 Jetson 작업 일지](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/daily/2026-05-06/README.md)
- [2026-05-06 Jetson R36.5 UART DMA/DTB Issue](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/notes/troubleshooting/2026-05-06_Jetson_R36_5_UART_DMA_DTB_Issue.md)
- [apply_uarta_pio_dtb.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/apply_uarta_pio_dtb.sh)
- [verify_uarta_pio_loopback.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/verify_uarta_pio_loopback.sh)
- [restore_jetsonio_default_boot.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/restore_jetsonio_default_boot.sh)
- [2026-05-06 Jetson Unexpected Shutdown During UART Debug](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/notes/troubleshooting/2026-05-06_Jetson_Unexpected_Shutdown_During_UART_Debug.md)

## 남은 문제

- CP2102 또는 FTDI USB-UART bridge를 아직 실제 연결하지 않았다.
- USB-UART 우회는 더 이상 필수는 아니며 예비 수단이다.
- `/gps/fix` ROS 2 topic publish는 아직 진행하지 않았다.
- GPS NMEA는 수신되지만 아직 유효한 fix는 잡히지 않았다.
- 갑작스러운 shutdown 원인은 아직 확인하지 않았다.

## 다음 액션

1. GPS 안테나를 창가나 야외에 두고 fix가 잡히는지 확인한다.
2. `/dev/ttyTHS1` raw NMEA에서 `GPRMC A`, `GPGGA fix quality 1`, satellite count 증가를 확인한다.
3. shutdown이 다시 발생하면 `journalctl -b -1`과 `last -x`로 원인을 먼저 확인한다.
4. `nmea_navsat_driver`로 `/gps/fix`를 publish한다.
5. CP2102 또는 FT232 계열 USB-UART는 예비 우회 수단으로 확보한다.

## 한 줄 회고

- 오늘의 핵심은 PIO mode에서 `/dev/ttyTHS1` loopback과 GPS NMEA 수신을 모두 성공시켜, Jetson 내장 UART 경로를 실제로 살렸다는 점이다.
