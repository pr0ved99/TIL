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

1차 MVP에서는 로봇이 PC 또는 ESP32 상위 제어기로부터 속도 명령을 받아 안전하게 전진, 후진, 회전하고, 엔코더 기반 속도와 이동량을 계산하게 한다. BNO08x IMU 기반 회전 검증은 하위 구동계와 엔코더 telemetry가 안정된 뒤의 후속 V-cycle로 진행한다.

## 4. MVP Scope

- STM32가 좌/우 DC 모터를 PWM으로 제어한다.
- 엔코더로 좌/우 모터 속도를 측정한다.
- open-loop PWM command와 엔코더 속도 추정·telemetry 구조를 만든다.
- UART 또는 USB Serial로 명령을 수신한다.
- 3S LiPo 전원계를 퓨즈, 스위치, 저전압 알람과 함께 운용한다.
- 궤도 섀시에서 저속 전진, 후진, 제자리 회전을 검증한다.

## 5. Out of Scope for MVP

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
9. fault stop와 1 m system acceptance
10. requirement-to-evidence audit와 portfolio release
11. 후속 V-cycle: PID, IMU, FreeRTOS, CAN, LL, ROS2와 LiDAR

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
