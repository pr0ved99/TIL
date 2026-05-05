# 2026-05-06 Jetson R36.5 UART DMA/DTB Issue

## 증상

- `Jetson Orin Nano` 40핀 헤더의 `pin 8`, `pin 10`을 `uarta`로 활성화했다.
- `pin 8`과 `pin 10`을 직접 점퍼로 연결한 loopback에서도 보낸 문자열이 그대로 돌아오지 않는다.
- `/dev/ttyTHS1`에 `hello-gps-test\r\n` 16바이트를 쓰면, 수신 파일에는 printable ASCII가 아니라 NUL byte 16개가 들어온다.

```text
^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@
```

## 환경

```text
Jetson Linux: R36.5.0
nvidia-l4t-core: 36.5.0-20260115194252
Kernel: 5.15.185-tegra
```

확인 명령:

```bash
head -n 1 /etc/nv_tegra_release
dpkg-query -W nvidia-l4t-core nvidia-jetpack 2>/dev/null
uname -a
```

## 확인된 것

- Jetson-IO 기준 `uarta (8,10)`가 활성화되어 있다.

```text
Enabled functions:
uarta (8,10)
```

- `config-by-pin.py`에서도 `pin 8`, `pin 10`이 모두 `uarta`로 나온다.

```text
pin 8  -> uarta
pin 10 -> uarta
```

- device tree에서 `serial@3100000`은 `okay` 상태이며, `/dev/ttyTHS1`에 매핑된다.

```text
serial@3100000 -> /dev/ttyTHS1
serial@3140000 -> /dev/ttyTHS2
serial@31d0000 -> /dev/ttyAMA0
```

- `/dev/ttyTHS1`로 `U` 문자를 반복 송신하면 `pin 8` 전압이 약 `3.2V`에서 `3.0V` 정도로 변한다.
- `/dev/ttyTHS2`로 같은 송신을 해도 `pin 8` 전압 변화가 없다.
- 따라서 `pin 8 TX`는 `/dev/ttyTHS1`과 연결된 것으로 판단한다.
- `pin 8`과 `pin 10`을 점퍼로 연결한 상태에서 두 핀 모두 약 `3.2V`가 측정됐다.
- 전원 OFF 상태 continuity test:

```text
pin 8 <-> pin 10 : beep
pin 8 <-> GND    : no beep
pin 10 <-> GND   : no beep
```

## 재현 명령

`pin 8`과 `pin 10`을 직접 연결한 상태에서 실행했다.

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

`/dev/ttyTHS1`, `/dev/ttyTHS2`, `/dev/ttyAMA0`를 동시에 읽어도 `hello-gps-test`는 어느 포트에서도 확인되지 않았다.

```text
ttyTHS1: NUL byte 16개
ttyTHS2: NUL byte 2개
ttyAMA0: empty
```

## 커널 로그

UART loopback 테스트 시간대에 아래 로그가 반복됐다.

```text
arm-smmu 12000000.iommu: Unhandled context fault
tegra-mc 2c00000.memory-controller: EMEM address decode error
tegra-mc 2c00000.memory-controller: VPR violation
tegra-mc 2c00000.memory-controller: Route Sanity error
```

확인 명령:

```bash
sudo dmesg -T | grep -iE 'serial|uart|dma|smmu|fault|tegra' | tail -n 100
```

## 현재 판단

- GPS 모듈, baudrate, 실내 수신 문제로 보기 어렵다.
- `pin 8` TX는 실제로 동작하고, `pin 8`과 `pin 10`의 전기적 연결도 확인됐다.
- 그런데 RX 수신 결과가 `hello-gps-test`가 아니라 NUL byte로 고정된다.
- 동시에 SMMU/IOMMU 관련 kernel fault가 반복된다.
- 따라서 현재 1순위 가설은 `Jetson Linux R36.5.0`의 UART DMA/DTB 설정 문제다.
- 2026-05-06 PIO 우회 적용 후 loopback이 성공했으므로, 이 가설은 사실상 확인됐다.

## 왜 DMA/DTB 쪽을 의심하는가

- UART TX pad는 움직인다.
- loopback 물리 연결도 확인됐다.
- 수신 이벤트는 발생하지만 데이터 내용이 전부 `0x00`이다.
- 이 패턴은 단순 배선 실수보다 UART RX DMA buffer 또는 SMMU/IOMMU 매핑 문제와 더 잘 맞는다.
- NVIDIA Developer Forum에도 `R36.5 / JetPack 6.2.2` 계열에서 UART DMA/Device Tree 문제로 `ttyTHS1`이 깨지는 사례가 있다.

참고:

- [NVIDIA Developer Forums - UART serial port not working after upgrading to JetPack 6.2.2](https://forums.developer.nvidia.com/t/solved-uart-serial-port-not-working-after-upgradint-to-jetpack-6-2-2-orin-nano-nx/363837)
- [NVIDIA Jetson Linux Developer Guide - Configuring the Jetson Expansion Headers](https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/HR/ConfiguringTheJetsonExpansionHeaders.html)

## 우회 방법

GPS bring-up은 내장 40핀 UART 대신 USB-UART bridge를 사용한다.

추천 흐름:

```text
GPS UART TX/RX -> CP2102 또는 FT232 계열 USB-UART -> Jetson USB -> /dev/ttyUSB0
```

초기 수신 전용 연결:

```text
GPS VCC -> USB-UART 3.3V 또는 GPS 모듈 허용 전압
GPS GND -> USB-UART GND
GPS TX  -> USB-UART RXD
GPS RX  -> 연결 안 함
```

확인 명령:

```bash
ls -l /dev/ttyUSB*
stty -F /dev/ttyUSB0 9600 raw -echo
timeout 30 cat /dev/ttyUSB0
```

기대:

```text
$GPGGA,...
$GPRMC,...
$GNGGA,...
$GNRMC,...
```

## 정석 해결 후보

내장 UART를 꼭 사용해야 한다면, DTB를 백업한 뒤 아래 중 하나를 검토한다.

1. `serial@3100000`의 `dmas`, `dma-names`를 제거해 UART를 PIO mode로 우회
2. `serial@3100000`에 누락된 `iommus` 설정을 추가해 DMA/SMMU 매핑을 정상화

## PIO 우회 실험 준비

현재 부팅 DTB를 decompile해 `serial@3100000`에서 아래 속성만 제거한 PIO 테스트용 DTB 후보를 만들었다.

```dts
dmas = <...>;
dma-names = "rx\0tx";
```

생성 파일:

- `/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/logs/2026-05-06_uart_pio/kernel_tegra234-p3768-0000+p3767-0005-nv-super-uarta-pio.dtb`

적용 스크립트:

- `/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/apply_uarta_pio_dtb.sh`

검증 스크립트:

- `/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/verify_uarta_pio_loopback.sh`

복구 스크립트:

- `/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/restore_jetsonio_default_boot.sh`

적용 흐름:

```bash
cd ~/yh_ws/TIL
sudo bash Robotics/VSLAM/jetson/scripts/apply_uarta_pio_dtb.sh
sudo reboot
```

재부팅 후 `pin 8 <-> pin 10`을 연결한 상태에서 확인:

```bash
cd ~/yh_ws/TIL
bash Robotics/VSLAM/jetson/scripts/verify_uarta_pio_loopback.sh
```

기대:

```text
hello-gps-test^M
```

## PIO 우회 검증 결과

재부팅 후 `DEFAULT JetsonIO-UARTA-PIO` entry로 부팅된 것을 확인했다.

```text
DEFAULT JetsonIO-UARTA-PIO
FDT /boot/dtb/kernel_tegra234-p3768-0000+p3767-0005-nv-super-uarta-pio.dtb
OVERLAYS /boot/jetson-io-hdr40-user-custom.dtbo
```

runtime device tree에서 `serial@3100000`의 DMA 속성이 제거된 것도 확인했다.

```text
status: okay
compatible: nvidia,tegra194-hsuart
dma-names: <missing>
dmas: <missing>
```

커널 로그에서도 PIO mode가 명시됐다.

```text
serial-tegra 3100000.serial: RX in PIO mode
serial-tegra 3100000.serial: TX in PIO mode
3100000.serial: ttyTHS1 at MMIO 0x3100000 (irq = 112, base_baud = 0) is a TEGRA_UART
```

`pin 8 <-> pin 10` loopback 결과:

```text
hello-gps-test^M
```

판단:

- 기존 실패 원인은 GPS 모듈이나 배선보다 `serial@3100000`의 DMA 설정 문제로 보는 것이 맞다.
- `dmas`, `dma-names`를 제거한 PIO mode에서는 `/dev/ttyTHS1` RX/TX가 정상 동작한다.
- 이제 GPS를 다시 Jetson 40핀 UART에 직접 연결해 raw NMEA 수신을 확인할 수 있다.

## GPS raw NMEA 재확인 결과

GPS를 다시 `GPS TX -> Jetson pin 10`으로 연결한 뒤 `/dev/ttyTHS1`에서 NMEA 문장이 정상 수신됐다.

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

판단:

- NMEA 문장이 정상적으로 들어오므로 Jetson 내장 UART RX/TX 경로는 복구됐다.
- 현재 `V`, `fix quality 0`, `satellite count 00`이므로 아직 GPS fix는 없다.
- 다음 문제는 UART가 아니라 GPS 안테나 위치, 실내 수신, cold start 대기 시간이다.

기본 boot entry를 원래대로 되돌릴 때:

```bash
cd ~/yh_ws/TIL
sudo bash Robotics/VSLAM/jetson/scripts/restore_jetsonio_default_boot.sh
sudo reboot
```

주의:

- DTB 수정은 부팅 설정에 영향을 줄 수 있으므로 GPS bring-up과 분리해서 진행한다.
- 실제 적용 전 현재 부팅 DTB와 `/boot/extlinux/extlinux.conf`를 백업한다.
- 이번 적용 스크립트는 기존 `JetsonIO` entry를 지우지 않고 `JetsonIO-UARTA-PIO` entry를 추가한다.
- 문제가 생기면 부팅 메뉴에서 기존 `JetsonIO` entry를 선택한다.

## 다음 액션

1. 현재 `JetsonIO-UARTA-PIO` boot entry를 유지한다.
2. GPS 안테나를 창가나 야외에 두고 `GPRMC A`, `GPGGA fix quality 1`, satellite count 증가를 확인한다.
3. NMEA 확인 후 `nmea_navsat_driver`로 `/gps/fix`를 publish한다.
4. CP2102 또는 FT232 계열 USB-UART는 예비 우회 수단으로 확보한다.
