# Concept Notes

이 폴더는 보드 실습 전에 개념을 분해해서 이해하는 곳이다.

각 파일은 다음 관점으로 작성한다.

- 개념의 역할
- STM32F446RE peripheral 관점
- CubeMX/HAL 설정과 direct register 대응
- 이 프로젝트에서의 사용 위치
- 실수, 고장, 디버깅 포인트
- 포트폴리오/면접 설명 문장

## Index

| File | Topic |
| --- | --- |
| `01_GPIO_Alternate_Function_and_CubeMX_ko.md` | GPIO mode, alternate function, CubeMX code generation |
| `02_UART_Interrupt_Ring_Buffer_ko.md` | UART RX interrupt, ISR, ring buffer, parser split |
| `03_Timer_Encoder_Mode_ko.md` | A/B quadrature, timer encoder mode, hardware counting |
| `04_DMA_Interrupt_Timer_Comparison_ko.md` | DMA, interrupt, timer hardware role differences |
| `05_HAL_LL_Direct_Register_ko.md` | HAL, LL, direct register 접근 전략 |
| `06_I2C_SPI_IMU_Interface_Choice_ko.md` | BNO08x IMU에서 I2C 우선, SPI fallback 판단 |
