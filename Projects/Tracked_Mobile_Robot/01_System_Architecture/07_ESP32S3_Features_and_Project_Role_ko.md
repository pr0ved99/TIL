# ESP32-S3 기능과 프로젝트 내 역할 분석

## 목적

이 문서는 ESP32-S3의 주요 기능을 정리하고, 궤도형 모바일 로봇 프로젝트에서
ESP32-S3 DevKitC-1을 어떤 역할로 사용할지 정의한다.

목표는 ESP32-S3가 STM32 하위 제어기를 대체하도록 만드는 것이 아니다.
목표는 ESP32-S3를 무선 통신, UI, 센서 프로토타이핑, 개발 편의 기능을 담당하는
보조 컨트롤러로 사용할 수 있는지 판단하는 것이다.

## 출처

- ESP32-S3 Series Datasheet v2.2: `assets/esp32-s3_datasheet_en.pdf`
- 온라인 참고: https://documentation.espressif.com/esp32-s3_datasheet_en.pdf
- ESP32-S3-DevKitC-1 User Guide v1.1: https://documentation.espressif.com/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html
- 프로젝트 ESP32-S3 기록: `Embedded/ESP32-S3/README.md`

## 현재 프로젝트 보드

| 항목 | 현재 상태 |
| --- | --- |
| Board | HG ESP32-S3 DevKitC-1 |
| Toolchain | ESP-IDF v5.4.4 |
| USB detection | Espressif USB JTAG/serial debug unit |
| Serial path | `/dev/ttyACM0` 및 stable by-id path |
| 실습에서 감지된 Flash | 16 MB |
| RGB LED test | 완료 |
| 현재 보드의 RGB LED GPIO | GPIO38 |

주의:

- ESP32-S3-DevKitC-1은 보드 revision에 따라 세부 핀이 다를 수 있다.
- Espressif 공식 문서도 revision에 따라 RGB LED GPIO가 다를 수 있음을 언급한다.
- 이 프로젝트에서는 실제 실습으로 확인한 GPIO38을 현재 보드 기준으로 사용한다.

## 1. ESP32-S3 기능 요약

### CPU와 Runtime

ESP32-S3는 dual-core Xtensa LX7 프로세서를 기반으로 한 Wi-Fi/Bluetooth LE MCU다.

프로젝트 의미:

- Networking, UI, serial parsing, 가벼운 센서 처리에 충분한 성능을 가진다.
- ESP-IDF와 FreeRTOS 기반 애플리케이션을 실행한다.
- 동시 작업에는 유리하지만, 모터 제어처럼 hard real-time 성격이 강한 작업의
  1차 담당자로 두기에는 STM32보다 역할이 맞지 않는다.

1차 역할이 아닌 것:

- 초기 MVP에서 STM32의 low-level motor controller 역할을 대체하지 않는다.
- Wi-Fi/BLE task는 timing variability를 만들 수 있으므로 motor PWM과 encoder
  counting은 STM32에 남긴다.

### Wireless

ESP32-S3는 다음 무선 기능을 제공한다.

- 2.4 GHz Wi-Fi
- Bluetooth Low Energy

프로젝트 활용:

- 무선 설정 페이지
- 원격 명령 인터페이스
- Debug telemetry streaming
- 스마트폰 또는 노트북 기반 제어 UI
- 향후 Wi-Fi 기반 ROS2 bridge 실험

초기 결정:

- 첫 drivetrain MVP에는 wireless를 넣지 않는다.
- STM32 UART 제어와 모터 safety가 안정화된 뒤 Wi-Fi를 추가한다.

### USB

ESP32-S3는 USB Serial/JTAG와 USB OTG 관련 기능을 제공한다. 실제 사용 가능
범위는 보드 배선과 펌웨어 설정에 따라 달라진다.

프로젝트 활용:

- Firmware flashing과 monitor
- USB serial debug
- 내장 USB Serial/JTAG unit을 통한 개발 workflow

초기 결정:

- ESP32-S3 USB workflow는 ESP-IDF 실습과 디버깅에 사용한다.
- USB host/device 기능은 첫 로봇 MVP에 포함하지 않는다.

### GPIO와 Digital Peripherals

ESP32-S3는 여러 programmable GPIO와 UART, I2C, SPI, PWM, RMT, pulse counter,
SD/MMC host, TWAI 같은 일반 임베디드 주변장치를 제공한다.

프로젝트 활용:

- STM32와 UART link
- I2C/SPI sensor prototyping
- Button, LED, status output, 단순 UI
- 향후 TWAI와 외부 transceiver를 통한 CAN 계열 실험

중요 주의:

- ESP32-S3 GPIO는 logic signal용이지 motor power용이 아니다.
- STM32, 센서, 모터 드라이버와 연결하기 전에 GPIO voltage compatibility를 확인해야 한다.

### ADC와 Touch

ESP32-S3는 ADC와 touch sensing 기능을 제공한다.

프로젝트 활용:

- 간단한 analog experiment
- 보조 battery 또는 rail monitoring prototype
- Touch/button UI experiment

초기 결정:

- Primary battery monitoring은 STM32 ADC가 담당한다. STM32가 motor safety를
  소유하기 때문이다.
- ESP32 ADC는 main power safety path가 검증된 뒤 secondary telemetry 용도로만 사용한다.

### Security와 Crypto

ESP32-S3는 secure boot, flash encryption, random number generation,
cryptographic acceleration 같은 hardware security 기능을 제공한다.

프로젝트 활용:

- 첫 MVP에는 필요하지 않다.
- 나중에 Wi-Fi service를 외부에 노출하거나 credential을 저장할 때 유용하다.

초기 결정:

- Wireless 기능이 프로젝트에 들어오기 전까지 security hardening은 미룬다.

## 2. ESP32-S3와 STM32의 역할 분리

이 프로젝트는 STM32와 ESP32-S3에 서로 다른 일을 맡기는 구조가 적절하다.

| 책임 | STM32 NUCLEO-F446RE | ESP32-S3 DevKitC-1 |
| --- | --- | --- |
| Motor PWM | Primary | MVP에서는 피함 |
| Encoder counting | Primary | MVP에서는 피함 |
| Motor fail-safe | Primary | 보조만 가능 |
| Battery low-voltage motor shutdown | Primary | Telemetry만 가능 |
| IMU integration | Primary 후보 | Prototype 후보 |
| PC serial command | 첫 primary path | 나중에 bridge 가능 |
| Wireless control | 부적합 | Primary |
| Web UI 또는 mobile UI | 부적합 | Primary |
| Debug telemetry over Wi-Fi | 부적합 | Primary |
| ROS2 bridge experiment | PC를 통해 후순위 | Wi-Fi/serial bridge 가능 |
| CAN/TWAI expansion | STM32 bxCAN 후보 | ESP32 TWAI 후보, 후순위 |

## 3. 이 프로젝트에서 ESP32-S3 추천 활용 방안

### 활용 1: Wireless Dashboard

Drivetrain MVP가 동작한 뒤 ESP32-S3는 간단한 Wi-Fi dashboard를 제공할 수 있다.

가능 기능:

- Robot armed/disarmed state
- STM32에서 받은 battery voltage telemetry
- 좌/우 motor speed
- IMU yaw 또는 yaw rate
- 저속 test mode용 command button

데이터 경로:

```text
STM32 -> UART -> ESP32-S3 -> Wi-Fi dashboard
```

주의:

- Safety behavior가 검증되기 전에는 Wi-Fi에서 고출력 motor command를 허용하지 않는다.

### 활용 2: STM32 Wireless Serial Bridge

ESP32-S3는 STM32 UART와 PC/스마트폰 사이의 Wi-Fi bridge로 동작할 수 있다.

가능 데이터 경로:

```text
PC/phone -> Wi-Fi -> ESP32-S3 -> UART -> STM32
STM32 -> UART -> ESP32-S3 -> Wi-Fi -> PC/phone
```

용도:

- Remote telemetry
- 저속 command test
- STM32에 USB cable을 직접 연결하지 않는 debugging

위험:

- Wi-Fi latency와 packet loss가 발생할 수 있다.
- STM32는 command timeout과 motor stop behavior를 반드시 자체적으로 강제해야 한다.

### 활용 3: IMU Prototype Platform

ESP32-S3는 BNO08x IMU를 STM32에 붙이기 전에 먼저 시험하는 플랫폼으로 쓸 수 있다.

이유:

- ESP-IDF 개발과 logging이 편하다.
- 모터 제어 펌웨어와 분리해서 I2C/SPI sensor 실험을 할 수 있다.

결정:

- STM32 integration이 막히거나 센서 디버깅을 분리해야 할 때 ESP32-S3를
  IMU bring-up 용도로 사용한다.
- 최종 IMU 소유권은 drivetrain과 odometry test 이후 결정한다.

### 활용 4: UI와 Mode Controller

ESP32-S3는 safety-critical하지 않은 사용자-facing 기능을 담당할 수 있다.

예:

- Mode selection
- Start/stop request
- Web-based parameter setting
- LED status pattern
- BLE-based setup

규칙:

- ESP32-S3는 action을 요청할 수 있다.
- 실제 motor action이 안전한지는 STM32가 판단해야 한다.

### 활용 5: 향후 통신 실험

ESP32-S3에는 TWAI가 있다. TWAI는 CAN 2.0 계열 controller로 볼 수 있지만,
실제 CAN bus에 연결하려면 외부 transceiver가 필요하다.

프로젝트 결정:

- 첫 MVP에서는 TWAI/CAN을 사용하지 않는다.
- UART 기반 control이 동작한 뒤 나중에 통신 실험으로 남긴다.

## 4. ESP32-S3가 처음부터 맡지 말아야 할 일

첫 MVP에서 ESP32-S3가 담당하지 않는 것이 좋은 기능:

- Primary motor PWM generation
- Primary encoder counting
- Primary low-voltage motor shutdown
- Direct motor driver safety logic
- High-priority real-time control loop
- 복잡한 ROS2/Nav2 autonomy role

이유:

- 이 프로젝트의 architecture는 deterministic low-level motor control을 STM32에
  맡기도록 설계되어 있다.
- ESP32-S3는 wireless, UI, support task에 더 적합하다.

## 5. STM32-ESP32 Interface 후보

초기 interface는 UART가 적절하다.

후보 배선:

```text
STM32 TX -> ESP32 RX
STM32 RX <- ESP32 TX
GND      <-> GND
```

중요 확인:

- 양쪽 모두 3.3 V logic 호환인지 확인한다.
- GND를 공통으로 연결한다.
- Baud rate와 frame format을 맞춘다.
- STM32 command timeout을 구현한다.
- ESP32가 유효한 command를 보내지 못하더라도 STM32가 motor를 계속 돌리지 않도록 한다.

초기 protocol 방향:

- Text message로 시작한다.
- 필요하면 나중에 framed binary packet으로 이동한다.

초기 message 예:

```text
STM32 -> ESP32:
TEL,batt_mv=11820,left_cps=120,right_cps=118,armed=0

ESP32 -> STM32:
CMD,linear=0.10,angular=0.00,timeout_ms=300
```

## 6. ESP32-S3 개발 경로

추천 학습 및 검증 순서:

1. ESP-IDF 환경과 보드 연결 확인
2. RGB LED와 BOOT button 확인
3. FreeRTOS two-task example 작성
4. UART loopback test
5. ESP32-to-PC serial logging test
6. ESP32-to-STM32 UART link test
7. Wi-Fi access point 또는 station mode 추가
8. 간단한 telemetry web page 추가
9. Command timeout과 safety gating 추가
10. STM32 motor test가 안정화된 뒤 STM32 telemetry와 통합

## 7. Architecture Decision

ESP32-S3는 이 프로젝트에서 support controller로 적합하다. 첫 low-level motor
controller로 두는 것은 적절하지 않다.

초기 역할:

- Wireless dashboard
- UART bridge
- IMU/sensor prototype platform
- UI 및 개발 편의 controller

후순위 역할:

- Wi-Fi command interface
- BLE setup
- TWAI/CAN experiment
- Advanced telemetry gateway

MVP에서 제외할 역할:

- Primary motor control
- Primary safety shutdown
- Encoder ownership

## 8. 다음 단계

다음 실무 단계는 더 많은 기능 나열이 아니다. 먼저 low-level drivetrain interface를
확정하고, 그 다음 STM32-ESP32 통신 경계를 정의한다.

즉시 이어지는 문서:

- `08_Motor_Driver_and_HBridge_Control.md`

후속 문서 후보:

- `09_STM32_ESP32_UART_Interface_Contract.md`

후속 UART contract에서 정의할 내용:

- UART pins
- Baud rate
- Message direction
- Command timeout
- Telemetry fields
- Safety ownership
- Error handling
