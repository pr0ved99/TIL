# [ESP32-S3] 내장 RGB LED 제어

## 목표

HG ESP32-S3 DevKitC-1 보드의 내장 RGB LED를 ESP-IDF `blink` 예제로 제어한다.

이번 실습의 핵심은 `hello_world`처럼 로그만 보는 것이 아니라, 보드 위 LED가 실제로 깜빡이는지 확인하는 것이다.

## 선행 상태

- ESP-IDF: `v5.4.4`
- Target: `esp32s3`
- Serial port: `/dev/ttyACM0`
- Board: HG ESP32-S3 DevKitC-1
- 이전 실습: `hello_world` build/flash/monitor 성공

## 핵심 개념

내장 RGB LED는 일반 LED와 다르게 색상 데이터를 받아서 동작하는 주소 지정 LED다.

- 일반 LED: GPIO 전압을 `HIGH` 또는 `LOW`로 바꿔서 켜고 끈다.
- 주소 지정 RGB LED: 하나의 데이터 핀으로 색상 값을 보내서 빨강, 초록, 파랑 밝기를 정한다.
- `led_strip`: ESP-IDF에서 주소 지정 LED를 다루기 위해 사용하는 컴포넌트다.
- RMT: ESP32의 정밀한 타이밍 신호 생성 주변장치다. 주소 지정 LED는 신호 타이밍이 중요해서 RMT를 자주 사용한다.

따라서 ESP32-S3 DevKitC-1의 내장 RGB LED는 단순 `gpio_set_level()`보다 `led_strip` 방식으로 제어하는 편이 맞다.

## 프로젝트 생성

새 터미널에서는 먼저 ESP-IDF 환경을 적용한다.

```bash
cd ~/esp/esp-idf
. ./export.sh
```

`blink` 예제를 실습용 프로젝트로 복사한다.

```bash
cd ~/esp
cp -r $IDF_PATH/examples/get-started/blink esp32s3_rgb_led
cd esp32s3_rgb_led
```

대상 칩을 ESP32-S3로 설정한다.

```bash
idf.py set-target esp32s3
```

## 프로젝트 설정

설정 UI를 연다.

```bash
idf.py menuconfig
```

Flash size를 실제 보드에 맞춘다.

```text
Serial flasher config -> Flash size -> 16 MB
```

LED 타입을 LED strip으로 설정한다.

```text
Example Configuration -> Blink LED type -> LED strip
```

내장 RGB LED GPIO를 설정한다.

```text
Example Configuration -> Blink GPIO number -> 38
```

이번 보드에서는 `GPIO38`에서 내장 RGB LED 점멸이 정상 확인되었다. 만약 같은 계열 보드에서 LED가 보이지 않으면 `GPIO48`도 후보로 확인한다.

## 빌드

```bash
idf.py build
```

성공 기준:

```text
Generated /home/ssafy/esp/esp32s3_rgb_led/build/blink.bin
Project build complete.
```

이번 빌드에서는 flash size가 16MB로 반영되었다.

```text
--flash_size 16MB
```

빌드 중 다음 메시지가 나올 수 있다.

```text
fatal: not a git repository (or any of the parent directories): .git
Could not use 'git describe' to determine PROJECT_VER.
```

이는 `~/esp/esp32s3_rgb_led`가 Git 저장소가 아니라서 프로젝트 버전 이름을 Git으로 만들지 못했다는 뜻이다. 빌드가 완료되면 문제 없다.

## Flash

빌드한 펌웨어를 보드에 업로드한다.

```bash
idf.py -p /dev/ttyACM0 flash
```

성공 기준:

```text
Hash of data verified.
Hard resetting via RTS pin...
Done
```

## Monitor

보드 로그를 확인한다.

```bash
idf.py -p /dev/ttyACM0 monitor
```

모니터 종료:

```text
Ctrl + ]
```

## 실습 결과

- Date: 2026-05-22
- Project path: `~/esp/esp32s3_rgb_led`
- LED type: `LED strip`
- Confirmed GPIO: `GPIO38`
- Flash size: `16MB`
- Result: 내장 RGB LED 점멸 확인

## 트러블슈팅

LED가 보이지 않을 때 먼저 확인할 것:

1. `Blink LED type`이 `LED strip`인지 확인한다.
2. GPIO 번호가 `38`인지 확인한다.
3. 같은 설정에서 보이지 않으면 GPIO 번호를 `48`로 바꿔 다시 빌드/flash한다.
4. 보드가 `/dev/ttyACM0`로 잡혀 있는지 확인한다.
5. USB 허브 전원이 불안정하면 PC에 직접 연결해서 비교한다.

## 다음 단계

다음 실습은 BOOT 버튼 입력 처리다. LED 출력까지 확인했으므로, 다음에는 버튼 입력을 읽고 그 입력으로 LED 상태를 바꾸는 흐름으로 확장한다.
