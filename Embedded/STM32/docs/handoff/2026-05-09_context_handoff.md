# 2026-05-09 STM32 Context Handoff

이 문서는 새 대화창에서 STM32 작업을 바로 이어받기 위한 인수인계 문서이다.

## 1. 현재 목표

- STM32에서 LL, FreeRTOS, CAN을 순서대로 학습하고 실습할 로드맵을 정리한다.
- 최종 목표는 FreeRTOS 기반으로 CAN 송수신 구조를 안정적으로 구현하는 것이다.
- 현재는 실제 코드 구현보다 학습 순서와 실습 단계를 잡는 단계이다.

## 2. 관련 저장소/경로

- STM32 작업 루트: `/home/ssafy/my_ws/git_hub/Embedded/STM32`
- 현재 작성 중인 로드맵:
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md`
- 이 handoff 문서:
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/docs/handoff/2026-05-09_context_handoff.md`
- 기존 이론 문서:
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Theory/01_STM32_Basic.md`
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Theory/02_STM32_GPIO.md`
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Theory/03_STM32_UART.md`
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Theory/04_STM32_TIM_PWM_InputCapture_Encoder.md`
- 기존 실습 문서:
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Practice/01_GPIO_Output.md`
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Practice/02_GPIO_EXTI_Button.md`
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Practice/03_UART_Polling_Interrupt.md`
  - `/home/ssafy/my_ws/git_hub/Embedded/STM32/Practice/04_TIM_PWM_InputCapture_Encoder.md`

## 3. 이미 만든 파일

- 새 로드맵 문서:
  - `Embedded/STM32/Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md`
- 새 handoff 문서:
  - `Embedded/STM32/docs/handoff/2026-05-09_context_handoff.md`

## 4. 중요한 결정사항

- 기준 보드는 `NUCLEO-F446RE`이다.
- STM32F446RE는 `FDCAN`이 아니라 `bxCAN` 계열 CAN을 사용한다.
- CAN 통신을 실제 배선으로 확인하려면 외부 CAN transceiver가 필요하다.
- CAN bus에는 종단저항 120 ohm 구성이 필요하다.
- 학습 순서는 다음과 같이 둔다.
  - STM32 기본 구조
  - LL 드라이버
  - FreeRTOS 기본
  - CAN 단독 송수신
  - CAN + FreeRTOS 통합
- CAN은 처음부터 FreeRTOS와 섞지 말고 loopback 또는 단독 송수신으로 먼저 확인한다.
- HAL/LL 선택은 실용적으로 접근한다.
  - CAN 초기 bringup은 HAL이 빠르다.
  - GPIO, TIM, UART 같은 저수준 제어는 LL로 학습 가치가 높다.
  - FreeRTOS 통합 후에는 task, queue, interrupt 경계가 핵심이다.

## 5. 아직 안 끝난 일

- CAN transceiver 모델과 실제 배선 구성을 정해야 한다.
- STM32CubeMX 또는 `.ioc` 기반 CAN 설정 예제를 만들어야 한다.
- CAN loopback 실습 문서를 작성해야 한다.
- CAN normal mode에서 보드 간 송수신 실습을 진행해야 한다.
- FreeRTOS task/queue 기반 CAN 송수신 구조를 설계해야 한다.
- 실제 빌드 결과와 디버깅 로그를 문서에 추가해야 한다.

## 6. 절대 건드리면 안 되는 것

- 기존 STM32 실습 프로젝트의 자동 생성 파일을 의도 없이 대량 수정하지 않는다.
- `Debug/`, 빌드 산출물, IDE 임시 파일을 새 커밋에 섞지 않는다.
- F446RE를 FDCAN 보드처럼 설명하지 않는다.
- 실제 하드웨어가 없는 상태에서 CAN normal mode 성공을 완료로 적지 않는다.
- VSLAM/GitLab 작업과 STM32 학습 문서 변경을 같은 커밋에 섞지 않는다.

## 7. 다음에 바로 실행할 명령/작업

### 현재 Git 상태 확인

```bash
cd /home/ssafy/my_ws/git_hub
git status --short --branch
```

### 로드맵 문서 열기

```bash
cd /home/ssafy/my_ws/git_hub
sed -n '1,220p' Embedded/STM32/Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md
```

### 다음 문서 작업 후보

1. `Embedded/STM32/Theory/06_STM32_CAN_Basic.md` 작성
2. `Embedded/STM32/Practice/05_CAN_Loopback.md` 작성
3. CAN transceiver 배선표 작성
4. CAN + FreeRTOS task/queue 구조 초안 작성

### 다음 실습 후보

```text
1. CubeMX에서 NUCLEO-F446RE CAN 설정
2. CAN loopback으로 송수신 확인
3. CAN normal mode로 보드 간 송수신 확인
4. FreeRTOS task에서 주기 송신
5. CAN RX interrupt에서 queue로 메시지 전달
```
