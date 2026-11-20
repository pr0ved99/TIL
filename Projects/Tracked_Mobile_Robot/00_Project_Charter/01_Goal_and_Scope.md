# Goal and Scope

## 1. Project Summary

STM32 기반 하위 제어기와 엔코더 모터를 사용해 궤도형 모바일 로봇 플랫폼을 만들고, 이후 IMU, FreeRTOS, CAN, LL Driver 전환, ROS2, LiDAR로 확장 가능한 구조로 발전시킨다.

이 프로젝트는 처음부터 완성형 자율주행 로봇을 만드는 것이 아니라, 자율주행으로 확장 가능한 안정적인 하위 구동 플랫폼을 만드는 것을 1차 목표로 한다.

## 2. Motivation

- 단순 RC카가 아니라 검증 가능한 모바일 로봇 플랫폼을 만든다.
- 모터 제어, 엔코더, 전원 안전, 센서 통합을 직접 구현한다.
- CAN 통신, RTOS 기반 task 설계, HAL에서 LL Driver로의 점진적 전환 경험을 확보한다.
- 부품 선택과 아키텍처 구성의 공학적 근거를 문서와 코드에 남긴다.
- 추후 포트폴리오에서 설계 근거, 실패 기록, 검증 결과를 함께 보여줄 수 있게 한다.

## 3. Primary Goal

1차 MVP는 **무선 수동 주행·정지와 엔코더 이동량을 검증할 수 있는 궤도형 하위 구동 플랫폼**이다. ESP32-S3를 통해 STM32가 모터를 제어하고 속도·이동량을 전달한다. GM-1312 외부 온도로 한정된 주행 조건의 발열을 관측한다.

2026-10-19 재판단: 전류 정량 측정·전류/전압 ADC 모니터링은 별도 post-MVP 기능이다. 이를 먼저 완성해야 기존 주행 인수를 끝낼 수 있도록 한 범위를 바로잡았다. IMU는 MVP 이후 첫 기본 검증으로 유지한다. [검증 매트릭스](../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)가 세부 기준이다.

## 4. MVP Scope

- STM32가 좌/우 DC 모터를 PWM으로 제어한다.
- 엔코더로 좌/우 모터 속도를 측정한다.
- open-loop PWM command와 엔코더 속도 추정·telemetry 구조를 만든다.
- ESP32-S3 Wi-Fi/PAGE → UART → STM32 경로로 명령을 수신한다. PC 제어도 ESP32를 경유하며 STM32 USART2는 bench-only다.
- 3S LiPo 전원계를 퓨즈, 스위치, 저전압 알람과 함께 운용한다.
- 궤도 섀시에서 저속 전진, 후진, 제자리 회전을 검증한다.
- 외부 GM-1312로 모터·드라이버·전원부의 온도를 기록해 선언한 부하·시간 조건에서 판정한다. 실시간 온도 telemetry는 이 범위에 포함하지 않는다.

## 5. Out of Scope for MVP

- 정량 전류 측정과 PC0/PA4 기반 전류·전압 ADC/웹 모니터링; 후보·보정 검증 계획은 별도 후속 단계로 보존

- CAN 통신의 로봇 구동 통합
- FreeRTOS 기반 전체 firmware 구조
- LL Driver 기반 최적화
- LiDAR 기반 SLAM
- Nav2 자율주행
- 직접 제작 BMS
- 복잡한 PCB 설계
- 고속 주행
- 실외 주행
- BNO08x firmware integration
- closed-loop PID speed control 고도화
- 자동 과전류/저전압 정지, PA4/PB0 이중 rail 자동 진단
- 온보드 온도 센서와 상시 온도 telemetry
- 전류 파형의 순간 피크/RMS 계측, 장시간 내구성·안전 인증

## 6. System Boundary

초기 시스템에 포함한다.

- 3S LiPo 배터리 전원계
- 퓨즈, 메인 스위치, XL4015 x2
- NUCLEO-F446RE
- ESP32-S3 DevKitC
- 모터 드라이버
- 엔코더 DC 모터
- 궤도차량 섀시
- BNO08x IMU hardware placement candidate; firmware integration은 첫 MVP에서 제외
- UART / USB Serial 통신
- 외부 검증 장비 GM-1312; 로봇에 내장된 온도 센서와 구분

초기 시스템에서 제외한다.

- CAN bus 기반 제어 통합
- LiDAR
- ROS2 navigation stack
- 자체 제작 배터리팩용 BMS

단, CAN 통신과 FreeRTOS, LL Driver 전환은 프로젝트 학습 목표에 포함한다. 첫 구동
MVP를 막지 않기 위해 초기 시스템에서 제외할 뿐, 후속 phase에서 반드시 다룬다.

## 7. Key Engineering Questions

- 선택한 모터와 드라이버가 궤도 섀시 부하를 버틸 수 있는가?
- 3S LiPo 전원계가 안전하고 안정적으로 동작하는가?
- 엔코더가 실제 속도 추정에 충분히 신뢰 가능한가?
- 궤도 미끄러짐 때문에 odometry 오차가 얼마나 발생하는가?
- BNO08x IMU의 yaw rate가 회전 추정 검증에 도움이 되는가?
- UART 기반 명령 프로토콜이 초기 제어에 충분한가?
- FreeRTOS task 구조가 motor control, communication, telemetry, safety를 명확히 분리하는가?
- CAN bus를 통해 command와 telemetry를 안정적으로 주고받을 수 있는가?
- HAL 기반 구현에서 어떤 부분을 LL Driver로 전환할 때 실질적인 이점이 있는가?

## 8. Success Criteria

- 바퀴 공중 테스트에서 좌/우 모터 개별 제어가 가능하다.
- 엔코더 A/B 채널이 안정적으로 측정된다.
- 바닥 주행에서 전진, 후진, 제자리 회전이 가능하다.
- 1m 직진 테스트에서 실제 이동 거리와 추정 이동 거리의 오차를 기록한다.
- 저전압 경고와 모터 정지 기준을 정의한다.
- 모든 테스트 결과와 실패 원인을 문서화한다.

## 9. Development Phases

1. PC/ESP32 UART command와 safety baseline
2. 전원·MDD10A 무전원·buck load 검증
3. 어댑터 플레이트 release와 fabricated fit
4. STM32 PWM/DIR 구현과 pin signal 검증
5. MDD10A logic input 검증
6. encoder 전압 안전성과 한쪽 motor no-load
7. encoder count와 speed telemetry
8. 좌우 drivetrain과 저속 chassis 주행
9. 한정된 저속 주행의 GM-1312 외부 온도 관측
10. 잔여 fault stop와 1 m system acceptance
11. requirement-to-evidence audit와 portfolio release
12. 첫 후속 V-cycle: BNO08x 통신·축·시각 검증 → 짧은 주행의 encoder/IMU 비교
13. 별도 후속: 전류·전압 ADC 회로/수집/보정·브라우저 로그와 정량 부하 분석
14. 이후 PID, FreeRTOS, CAN, LL, ROS2와 LiDAR 확장

상세 Gate와 현재 상태는 [`../docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](../docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md)를 따른다.

## 10. Design Principles

- 기능 추가보다 검증을 우선한다.
- 고전류 라인과 신호 라인을 분리한다.
- BMS 대신 퓨즈, 저전압 감지, 밸런스 충전을 사용한다.
- 초기 통신은 UART / USB Serial로 단순하게 시작하되, CAN은 필수 후속 학습 단계로 둔다.
- HAL로 먼저 동작을 검증하고, 검증된 핵심 경로부터 LL Driver로 전환한다.
- FreeRTOS는 모터/엔코더 기본 검증 후 task 구조화 단계에서 도입한다.
- 각 설계 결정에는 이유와 테스트 결과를 남긴다.
- 요구사항, 설계, 구현, 시험과 실제 증거를 경량 V-model traceability로 연결한다.

## 11. Open Questions

- JGB37-520 엔코더가 모두 정상인가?
- 모터 드라이버의 실제 연속 전류 여유는 충분한가?
- 궤도 섀시의 실제 평균 전류는 얼마인가?
- IMU를 STM32에 직접 붙일지, ESP32-S3에서 먼저 검증할지?
- FreeRTOS 도입 시 motor control task의 주기와 우선순위는 어떻게 둘 것인가?
- CAN transceiver와 USB-CAN adapter를 언제 구매하고 검증할 것인가?
- LL Driver 전환 대상은 timer, encoder, GPIO, ADC, UART, CAN 중 어디부터 시작할 것인가?
- ROS2 연동은 어느 단계에서 시작하는 것이 적절한가?
