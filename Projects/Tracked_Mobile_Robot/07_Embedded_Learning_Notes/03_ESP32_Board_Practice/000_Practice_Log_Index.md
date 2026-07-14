# ESP32 Practice Log Index

## Planned Sequence

| No. | Practice | Board | Status | Notes |
| --- | --- | --- | --- | --- |
| 001 | [`ESP32 UART command bridge`](001_ESP32_UART_Command_Bridge_ko.md) | ESP32-S3 DevKitC | Planned | loopback -> PING/PONG -> scripted command -> telemetry relay |
| 002 | [`ESP32-S3 ESP-IDF environment bring-up`](002_ESP32_IDF_Environment_Bringup_ko.md) | ESP32-S3 DevKitC | Done | ESP-IDF v6.0.2, COM4, hello_world build/flash/monitor PASS |
| 003 | ESP32 to STM32 UART link | ESP32-S3 + NUCLEO-F446RE | Planned | common GND, 3.3 V logic |
| 004 | Telemetry forwarding mock | ESP32-S3 | Planned | STM32 TEL frame을 PC 또는 Wi-Fi로 전달 |
| 005 | Simple web dashboard mock | ESP32-S3 | Later | motor command authority는 STM32에 유지 |

## Safety Rule

ESP32는 command request를 보낼 수 있지만 motor PWM, DIR, final safety gate를 직접 소유하지 않는다.
