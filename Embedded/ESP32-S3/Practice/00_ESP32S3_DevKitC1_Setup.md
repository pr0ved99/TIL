# [ESP32-S3] DevKitC-1 연결 확인과 첫 실습 준비

## 목표

HG ESP32-S3 DevKitC-1 보드가 PC에 정상 연결되는지 확인하고, ESP-IDF로 첫 예제인 `hello_world`를 올릴 준비를 한다.

ESP-IDF는 Espressif에서 제공하는 ESP32 계열 공식 개발 도구 모음이다. 빌드, 플래시, 시리얼 모니터, FreeRTOS, Wi-Fi, BLE 예제를 한 번에 다룰 수 있다.

## 준비물

- HG ESP32-S3 DevKitC-1
- 데이터 전송 가능한 USB 케이블
- USB 허브
- Ubuntu/Linux PC

충전 전용 USB 케이블은 전원만 공급하고 데이터 통신이 안 될 수 있다. 보드가 켜져도 `/dev/ttyACM0` 또는 `/dev/ttyUSB0`가 안 보이면 케이블부터 의심한다.

## 현재 연결 확인 결과

USB 장치 확인:

```bash
lsusb
```

확인된 장치:

```text
ID 303a:1001 Espressif USB JTAG/serial debug unit
```

USB 허브 경유 연결 확인:

```bash
lsusb -t
```

확인된 구조:

```text
Huasheng Electronics USB2.0 HUB
└─ Espressif USB JTAG/serial debug unit
```

시리얼 포트 확인:

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* /dev/serial/by-id/*
```

현재 포트:

```text
/dev/ttyACM0
```

고정 경로:

```text
/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_20:6E:F1:B4:B5:5C-if00
```

## ESP-IDF 설치

필수 패키지 설치:

```bash
sudo apt update
sudo apt install git wget flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
```

ESP-IDF 다운로드:

```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.4.4 --recursive https://github.com/espressif/esp-idf.git
```

ESP32-S3용 도구 설치:

```bash
cd ~/esp/esp-idf
./install.sh esp32s3
```

터미널 환경 적용:

```bash
. ~/esp/esp-idf/export.sh
```

자주 쓸 alias 등록:

```bash
echo "alias get_idf='. \$HOME/esp/esp-idf/export.sh'" >> ~/.bashrc
source ~/.bashrc
```

이후 새 터미널에서는 다음 명령으로 ESP-IDF 환경을 불러온다.

```bash
get_idf
```

## Hello World 예제 준비

예제 복사:

```bash
cd ~/esp
cp -r $IDF_PATH/examples/get-started/hello_world .
cd hello_world
```

대상 칩 설정:

```bash
idf.py set-target esp32s3
```

빌드:

```bash
idf.py build
```

플래시와 모니터:

```bash
idf.py -p /dev/ttyACM0 flash monitor
```

성공 기준:

```text
Hello world!
```

모니터 종료:

```text
Ctrl + ]
```

## 실습 결과

- Date: 2026-05-22
- Board: HG ESP32-S3 DevKitC-1
- Port: `/dev/ttyACM0`
- ESP-IDF: `v5.4.4`
- Project path: `~/esp/hello_world`
- Result: `build`, `flash`, `monitor` 성공

빌드 성공 기준:

```text
Project build complete.
Generated /home/ssafy/esp/hello_world/build/hello_world.bin
```

플래시 성공 기준:

```text
Chip is ESP32-S3 (QFN56) (revision v0.2)
USB mode: USB-Serial/JTAG
MAC: 20:6e:f1:b4:b5:5c
Hash of data verified.
Hard resetting via RTS pin...
Done
```

실행 성공 기준:

```text
Hello world!
This is esp32s3 chip with 2 CPU core(s), WiFi/BLE, silicon revision v0.2, 2MB external flash
Minimum free heap size: 388640 bytes
```

`hello_world` 예제는 10초 카운트다운 후 자동으로 재시작한다. monitor에서 반복 부팅 로그가 보여도 정상 동작이다.

## Flash size 메모

monitor에서 다음 경고가 확인되었다.

```text
Detected size(16384k) larger than the size in the binary image header(2048k). Using the size in the binary image header.
```

의미:

- 실제 보드의 외부 flash는 `16384k`, 즉 16MB로 감지되었다.
- 현재 `hello_world` 펌웨어 이미지 헤더에는 flash size가 `2048k`, 즉 2MB로 설정되어 있다.
- 그래서 ESP-IDF는 현재 프로젝트를 2MB flash 보드처럼 취급한다.

Flash는 ESP32-S3가 프로그램과 데이터를 저장하는 비휘발성 저장공간이다. PC의 디스크처럼 전원이 꺼져도 내용이 남는다.

Flash size와 직접 연관되는 것:

- firmware image: 빌드한 프로그램 본체
- partition table: flash 안을 `app`, `nvs`, `factory`, `ota`, `spiffs` 같은 구역으로 나누는 표
- NVS: Wi-Fi 설정이나 작은 값을 저장하는 영역
- filesystem: SPIFFS, LittleFS, FATFS 같은 파일 저장 영역
- OTA: 펌웨어를 무선 업데이트할 때 필요한 앱 저장 슬롯

현재 영향:

- `hello_world`, GPIO, 버튼, FreeRTOS 기초 실습에는 거의 영향이 없다.
- 기본 partition table에서 앱 영역이 1MB이고 `hello_world.bin`은 약 190KB라 충분하다.

앞으로 영향이 생기는 경우:

- Wi-Fi 웹서버에서 정적 파일을 flash에 저장할 때
- NVS에 설정을 많이 저장할 때
- SPIFFS/LittleFS 파일시스템 실습을 할 때
- OTA 업데이트 실습을 할 때
- BLE/Wi-Fi/웹서버 등으로 펌웨어 크기가 커질 때

이후 저장공간을 많이 쓰는 실습 전에는 flash size를 16MB로 맞춘다.

설정 위치:

```bash
idf.py menuconfig
```

메뉴에서 다음 항목을 확인한다.

```text
Serial flasher config -> Flash size -> 16 MB
```

필요하면 partition table도 16MB에 맞춰 다시 설계한다.

## 권한 문제 해결

`Permission denied`로 포트를 열 수 없으면 현재 사용자가 `dialout` 그룹에 들어가 있는지 확인한다.

```bash
id
```

없으면 추가한다.

```bash
sudo usermod -aG dialout $USER
```

그 뒤 로그아웃/로그인 또는 재부팅한다.

현재 환경에서는 사용자 `ssafy`가 `dialout` 그룹에 포함되어 있고 `/dev/ttyACM0` 접근도 가능했다.

## 다음 실습 순서

1. `hello_world` flash/monitor 성공 확인 - 완료
2. 내장 RGB LED 색상 제어
3. BOOT 버튼 입력 처리
4. FreeRTOS task 분리
5. NVS에 설정 저장
6. Wi-Fi scan
7. 보드 웹서버로 LED 제어

## 주의할 점

- ESP32-S3 DevKitC-1 내장 RGB LED GPIO는 보드 버전에 따라 `GPIO38` 또는 `GPIO48`일 수 있다.
- 내장 RGB LED는 일반 LED가 아니라 주소 지정 RGB LED이므로 단순 `gpio_set_level()`만으로는 제어되지 않을 수 있다.
- 처음에는 USB-to-UART 포트와 USB/JTAG 포트가 헷갈릴 수 있다. 현재 잡힌 `/dev/ttyACM0`는 `Espressif USB JTAG/serial debug unit`이다.
- USB 허브를 쓰는 경우 전원이 부족하면 플래시 중 연결이 끊길 수 있다. 문제가 반복되면 PC에 직접 연결해서 비교한다.
