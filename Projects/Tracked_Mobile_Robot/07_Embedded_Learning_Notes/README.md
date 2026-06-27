# Embedded Learning Notes

이 폴더는 Tracked Mobile Robot 프로젝트를 임베디드 시스템 학습용으로 깊게 정리하는 공간이다.

`01_System_Architecture`는 프로젝트의 공식 설계 결정과 인터페이스 계약을 담고,
이 폴더는 그 결정을 이해하기 위한 개념 노트, 보드 실습 일지, 디버깅 기록을 담는다.

## Folder Map

| Folder | Purpose |
| --- | --- |
| `01_Concept_Notes` | GPIO, Timer, UART, DMA, HAL/LL/Register 같은 개념 정리 |
| `02_STM32_Board_Practice` | NUCLEO-F446RE 기반 실습 일지와 bring-up 기록 |
| `03_ESP32_Board_Practice` | ESP32-S3 보조 컨트롤러 실습 일지 |
| `04_Interface_Protocol_Practice` | UART/CAN/telemetry protocol 설계와 검증 기록 |
| `05_Debugging_Measurement` | DMM, logic analyzer, oscilloscope, serial log 기반 측정 기록 |
| `_templates` | 새 개념 노트와 실습 일지 작성 템플릿 |

## How To Use

새 주제를 배울 때는 다음 순서로 정리한다.

1. `01_Concept_Notes`에 개념과 STM32F446RE 관점의 동작 원리를 정리한다.
2. 실제 보드에서 확인할 수 있으면 `02_STM32_Board_Practice` 또는 `03_ESP32_Board_Practice`에 실습 일지를 만든다.
3. command/telemetry frame, parser, CRC, timeout처럼 interface 성격이 강하면 `04_Interface_Protocol_Practice`에 따로 기록한다.
4. 측정값, 파형, 실패 원인, 재현 조건은 `05_Debugging_Measurement`에 남긴다.
5. 프로젝트 공식 결정으로 확정된 내용만 `01_System_Architecture`나 `PROJECT_MEMORY.md`에 반영한다.

## Learning Rule

빠르게 동작시키는 것보다 다음 질문을 닫는 것을 우선한다.

```text
왜 필요한가?
어떤 peripheral이 담당하는가?
CubeMX/HAL에서는 어떻게 설정되는가?
레지스터 관점에서는 어떤 비트가 바뀌는가?
실제 하드웨어에서는 무엇을 측정해야 하는가?
실패하면 어떤 fault 또는 recovery로 다룰 것인가?
포트폴리오나 면접에서는 어떻게 설명할 것인가?
```

## Current First Topics

| Topic | Note |
| --- | --- |
| GPIO alternate function | `01_Concept_Notes/01_GPIO_Alternate_Function_and_CubeMX_ko.md` |
| UART interrupt and ring buffer | `01_Concept_Notes/02_UART_Interrupt_Ring_Buffer_ko.md` |
| Timer encoder mode | `01_Concept_Notes/03_Timer_Encoder_Mode_ko.md` |
| DMA, interrupt, timer role split | `01_Concept_Notes/04_DMA_Interrupt_Timer_Comparison_ko.md` |
| HAL, LL, direct register | `01_Concept_Notes/05_HAL_LL_Direct_Register_ko.md` |
| I2C vs SPI for IMU | `01_Concept_Notes/06_I2C_SPI_IMU_Interface_Choice_ko.md` |
| CubeMX generated code boundary | `01_Concept_Notes/07_CubeMX_Generated_Code_and_User_Code_Boundary_ko.md` |
