# 📌 Pin Mapping & Wiring (회로 연결도)

본 로봇의 메인 제어기(STM32F401RE)와 각 컴포넌트 간의 핀 연결 정의서입니다.

## 1. STM32 Nucleo-64 Pinout Overview

| Function | STM32 Pin | Target Device | Description |
| :--- | :--- | :--- | :--- |
| **UART1_TX** | PA9 | Jetson Orin Nano | AI 추론 데이터 수신 (VLA/YOLO) |
| **UART1_RX** | PA10 | Jetson Orin Nano | |
| **UART2_TX** | PA2 | Raspberry Pi 5 | 시스템 통합 제어 및 상태 보고 |
| **UART2_RX** | PA3 | Raspberry Pi 5 | |
| **UART6_TX** | PA11 | PC / Debug | 디버깅용 시리얼 통신 |
| **UART6_RX** | PA12 | PC / Debug | |
| **I2C1_SCL** | PB8 | BNO085 (IMU) | 로봇 자세 및 방향 데이터 |
| **I2C1_SDA** | PB9 | BNO085 (IMU) | |
| **ADC1_IN1** | PA1 | Battery Monitoring | 전압 분배 회로를 통한 잔량 확인 |

## 2. 모터 및 인코더 (Actuators)
MDD10A(2ch) 드라이버 2개를 사용하여 4개의 메카넘 휠을 제어합니다.

| Motor | PWM Pin | Dir Pin | Encoder A | Encoder B | Timer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FL (앞왼)** | PA6 (TIM3_CH1) | PC7 | PA0 | PA1 | TIM2 |
| **FR (앞오)** | PA7 (TIM3_CH2) | PC8 | PB6 | PB7 | TIM4 |
| **RL (뒤왼)** | PB0 (TIM3_CH3) | PC9 | PA15 | PB3 | TIM2(Ext) |
| **RR (뒤오)** | PB1 (TIM3_CH4) | PC10 | PC6 | PC11 | TIM3(Ext) |

## 3. 전원 공급 (Power Lines)
| Source | Output | Target | Cable Spec |
| :--- | :--- | :--- | :--- |
| **Fuse Box #1** | 12V | Jetson Orin Nano | AWG 18 (Red/Black) |
| **Fuse Box #2** | 12V | MDD10A Motor Driver | AWG 16 (Red/Black) |
| **Buck(XL4016)** | 5.1V | Raspberry Pi 5 | AWG 18 (Red/Black) |
| **Buck(XL4015)** | 5.0V | STM32 / Sensors | AWG 22 (Various) |

---

## ⚠️ 주의사항
- **공통 접지(GND):** 모든 보드와 전원 모듈의 GND는 반드시 하나로 묶여야 통신 노이즈가 발생하지 않습니다.
- **로직 레벨:** STM32는 3.3V 로직을 사용하므로, 5V 소자와 통신 시 레벨 시프터 사용 여부를 확인하세요.