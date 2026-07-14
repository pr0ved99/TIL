# ESP32-S3 ESP-IDF Environment Bring-up

Date: 2026-07-14

## Purpose

ESP32-S3를 STM32 command bridge로 사용하기 전에, PC 개발 환경에서 ESP-IDF 프로젝트가 정상적으로 생성, 빌드, 플래시, 모니터링되는지 먼저 검증한다.

이번 검증은 아직 STM32와 UART command를 주고받는 단계가 아니다. ESP32-S3 보드와 ESP-IDF toolchain 자체가 정상 동작하는지 확인하는 bring-up 단계다.

## Environment

| Item | Value |
| --- | --- |
| ESP-IDF | v6.0.2 |
| Python | 3.11.15 |
| VS Code extension | ESP-IDF extension |
| ESP-IDF path | `C:\esp\v6.0.2\esp-idf` |
| ESP-IDF tools path | `C:\Espressif\tools` |
| Project path | `Projects/Tracked_Mobile_Robot/03_Firmware/esp32_uart_bridge` |
| Template | ESP-IDF `hello_world` |
| Target | `esp32s3` |
| Serial port | `COM4` |
| OpenOCD config | `board/esp32s3-builtin.cfg` |

## Setup Notes

처음에는 STM32 ST-LINK Virtual COM Port가 `COM3`으로 잡혀 있었다.

ESP32-S3는 충전 전용 USB 케이블로 연결했을 때 Windows 장치 관리자에 serial port가 뜨지 않았다. 데이터 통신 가능한 USB 케이블로 교체한 뒤 `COM4`가 새로 나타났고, 이를 ESP32-S3 포트로 사용했다.

정리하면 현재 포트 역할은 다음과 같다.

```text
COM3 = STM32 ST-LINK Virtual COM Port
COM4 = ESP32-S3 serial port
```

ESP32-S3 작업에서는 `COM4`를 사용한다. `COM3`를 선택하면 STM32 쪽 포트에 붙게 되므로 ESP32 flash/monitor 대상이 맞지 않는다.

## Project Creation Settings

VS Code ESP-IDF extension에서 새 프로젝트를 생성할 때 사용한 설정은 다음과 같다.

```text
Project Name: esp32_uart_bridge
Project Directory: ...\Tracked_Mobile_Robot\03_Firmware\esp32_uart_bridge
ESP-IDF Target: esp32s3
ESP-IDF Board: Custom board
Serial Port: COM4
OpenOCD Configuration: board/esp32s3-builtin.cfg
Component Directory: empty
```

`Custom board`를 선택한 이유는 이번 단계의 핵심이 외부 디버거 기반 JTAG debugging이 아니라 USB serial을 통한 build/flash/monitor 검증이기 때문이다.

![ESP-IDF project settings](../../assets/screenshots/esp32_uart_bridge/2026-07-14_01_esp32_idf_project_settings.png)

이 스크린샷은 VS Code ESP-IDF extension이 현재 프로젝트를 어떤 환경으로 인식하는지 보여준다. 특히 `idf.portWin`이 `COM4`, `IDF_TARGET`이 `esp32s3`, OpenOCD 설정이 `board/esp32s3-builtin.cfg`로 잡혀 있으므로 STM32의 `COM3`가 아니라 ESP32-S3 보드가 작업 대상이라는 점을 증명한다.

## Build Result

`ESP-IDF: Build your project` 실행 결과 빌드가 완료되었다.

확인된 메모리 요약의 핵심은 다음과 같다.

```text
Total image size: 145313 bytes
DIRAM used: 44815 bytes
Minimum runtime log free heap: 401084 bytes
```

빌드 완료 메시지:

```text
Project build complete.
```

![ESP-IDF build success](../../assets/screenshots/esp32_uart_bridge/2026-07-14_02_esp32_idf_build_success.png)

이 스크린샷은 `hello_world` 프로젝트가 ESP32-S3 target으로 컴파일되고 link까지 완료되었음을 보여준다. 메모리 사용량 요약이 출력되었다는 것은 `CMake/Ninja/toolchain/idf.py` 흐름이 정상 동작했고, firmware image를 만들 수 있는 상태라는 증거다.

## Flash Result

`ESP-IDF: Flash your project`를 `COM4` 대상으로 실행했다.

결과:

```text
Flash Done
Flash has finished. You can monitor your device with 'ESP-IDF: Monitor Device'
```

따라서 ESP32-S3 보드에 기본 `hello_world` firmware가 정상적으로 기록되었다.

![ESP-IDF flash done](../../assets/screenshots/esp32_uart_bridge/2026-07-14_03_esp32_idf_flash_done.png)

이 스크린샷은 생성된 firmware image가 `COM4`를 통해 ESP32-S3 flash에 기록되었음을 보여준다. `Flash Done`은 단순 빌드 성공을 넘어서 PC와 ESP32-S3 보드 사이의 USB serial download 경로가 실제로 동작했다는 검증 증거다.

## Monitor Result

`ESP-IDF: Monitor Device` 실행 후 다음 로그를 확인했다.

```text
This is esp32s3 chip with 2 CPU core(s), WiFi/BLE, silicon revision v0.2, 2MB external flash
Minimum free heap size: 401084 bytes
Restarting in 10 seconds...
Restarting in 9 seconds...
Restarting in 8 seconds...
Restarting in 7 seconds...
Restarting in 6 seconds...
```

이 로그는 ESP32-S3 chip 정보, flash 정보, heap 정보를 정상적으로 읽었음을 의미한다. `hello_world` 예제는 10초 후 재시작하도록 작성되어 있으므로 countdown과 재부팅은 정상 동작이다.

![ESP32-S3 monitor hello world](../../assets/screenshots/esp32_uart_bridge/2026-07-14_04_esp32s3_monitor_hello_world.png)

이 스크린샷은 flash된 firmware가 ESP32-S3에서 실제로 부팅되고, serial monitor로 runtime log가 수신되었음을 보여준다. chip 정보, flash 정보, heap 정보, `Hello world!` 로그가 보이므로 build와 flash뿐 아니라 실행 및 UART monitor 경로까지 검증되었다.

## Result

ESP32-S3 개발 환경 bring-up은 PASS로 기록한다.

확인된 항목:

- ESP-IDF v6.0.2 설치 정상
- VS Code ESP-IDF extension 설정 정상
- `esp32s3` target 설정 정상
- ESP32-S3 serial port `COM4` 확인
- `hello_world` build 성공
- `COM4` flash 성공
- monitor log 확인 성공

## Screenshot Evidence

이번 단계에서 확보한 스크린샷 증거는 다음과 같다.

저장 위치:

```text
Projects/Tracked_Mobile_Robot/assets/screenshots/esp32_uart_bridge
```

| No. | Filename | Required | Content | Evidence Meaning |
| --- | --- | --- | --- | --- |
| 01 | `2026-07-14_01_esp32_idf_project_settings.png` | Captured | `esp32s3`, `COM4`, `board/esp32s3-builtin.cfg` 설정 화면 | ESP32-S3 프로젝트 설정과 대상 포트가 올바름 |
| 02 | `2026-07-14_02_esp32_idf_build_success.png` | Captured | build 성공 또는 memory usage summary | ESP-IDF toolchain으로 firmware image 생성 가능 |
| 03 | `2026-07-14_03_esp32_idf_flash_done.png` | Captured | `Flash Done` 로그 | PC에서 ESP32-S3로 firmware download 가능 |
| 04 | `2026-07-14_04_esp32s3_monitor_hello_world.png` | Captured | `This is esp32s3 chip...` monitor 로그 | flash된 firmware가 실제 보드에서 실행되고 serial monitor로 확인됨 |

## Next Step

다음 실습은 `hello_world`를 유지한 상태에서 바로 복잡한 bridge로 가지 않고, ESP32 UART 동작을 단계적으로 확인한다.

1. ESP32-S3 UART pin 확정: `GPIO17 TX`, `GPIO18 RX`.
2. ESP32 단독 UART loopback으로 TX/RX 동작 확인.
3. STM32 USART1 `PA9 TX`, `PA10 RX`와 교차 연결.
4. ESP32에서 `PING,seq=1\n` 전송.
5. STM32에서 `PONG,seq=1,...` 응답 수신 여부 확인.
6. 이후 `ARM -> CMD -> DISARM` scripted command source로 확장.

## Safety Notes

- USB hub에 STM32와 ESP32를 함께 연결해도 된다.
- 보드 간 UART 통신은 USB hub가 대신해주지 않으므로 TX/RX/GND 점퍼선은 별도로 연결해야 한다.
- `ESP32 TX -> STM32 RX`, `ESP32 RX <- STM32 TX`로 교차 연결한다.
- 보드 간 common GND는 직접 연결한다.
- 두 보드가 USB 전원을 받고 있을 때 `5V`, `VIN`, `VBUS` 전원핀끼리는 연결하지 않는다.
