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

현재 STM·ESP 구조가 먼저 필요하면 [09 코드 구조와 함수 지도](09_STM32_ESP32_Source_Structure_and_Function_Map_ko.md)를 읽고,
이후 [08 단일 모터 시험 해설](08_Single_Motor_Bench_Dataflow_and_Evidence_Review_ko.md)에서 실제 시험 흐름과 연결한다.

| File | Topic |
| --- | --- |
| `01_GPIO_Alternate_Function_and_CubeMX_ko.md` | GPIO mode, alternate function, CubeMX code generation |
| `02_UART_Interrupt_Ring_Buffer_ko.md` | UART RX interrupt, ISR, ring buffer, parser split |
| `03_Timer_Encoder_Mode_ko.md` | A/B quadrature, timer encoder mode, hardware counting |
| `04_DMA_Interrupt_Timer_Comparison_ko.md` | DMA, interrupt, timer hardware role differences |
| `05_HAL_LL_Direct_Register_ko.md` | HAL, LL, direct register 접근 전략 |
| `06_I2C_SPI_IMU_Interface_Choice_ko.md` | BNO08x IMU에서 I2C 우선, SPI fallback 판단 |
| `07_CubeMX_Generated_Code_and_User_Code_Boundary_ko.md` | CubeMX 생성 파일, HAL 초기화 코드, 사용자 protocol 코드 경계 |
| [08 단일 모터 시험 해설](08_Single_Motor_Bench_Dataflow_and_Evidence_Review_ko.md) | PC→ESP→STM→모터→엔코더 흐름, 상태·timeout·DIR 보정, 실제 로그와 자기 점검 |
| [09 STM·ESP 코드 구조와 함수 지도](09_STM32_ESP32_Source_Structure_and_Function_Map_ko.md) | 파일별 역할, 초기화·반복문·UART 인터럽트 호출 흐름, 핵심 모듈 함수 사전 |
