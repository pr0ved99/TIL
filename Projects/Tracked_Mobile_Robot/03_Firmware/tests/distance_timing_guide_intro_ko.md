# 목표 거리 정지를 위한 엔코더 주기와 UART 송신 입력

`TK-MVP-03-06`의 두 번째 입력 묶음이다. 사용자가 저장한 `distance_move.h/.c`는 독립 모듈 PC 검사를 통과했다. 이번에는 그 모듈이 사용할 **5ms count 발행과 대기 없는 USART1 송신 경로**를 함께 준비한다.

아래 항목을 같은 입력 묶음으로 적용하고 저장한다. 삽입으로 명시한 항목은 기존 선언/정의 앞에 추가하고, 교체 항목은 지정된 기존 범위를 전체 블록으로 바꾼다. 일부 항목은 기존 한 줄을 포함한 블록에 새 선언을 추가하는 형태다. 경로는 모두 `stm32_uart_mvp/Core` 기준이다. 생산 파일 자동 수정은 하지 않았으며, 입력 후 실제 저장본을 다시 검사한다. 이번에는 입력·저장까지만 진행한다.

## count와 CPS의 시간을 나누는 이유

기존 누적 count와 CPS는100ms에 한 번 갱신된다. 그 중간 시점의 count를 얻기 위해 `encoder_speed_snapshot()`을 추가한다. 기존 누적값에 최근 기준 raw counter부터 현재 raw counter까지의 증가량을 더해 현재 count를 계산한다. 이 함수는 기준 counter·누적값·CPS 시간창을 수정하지 않는다. 원래 `encoder_speed_update()`가100ms에 도달하면 같은 증가량을 기준 누적값에 반영하며, snapshot은 새 기준을 사용하므로 이중 누적하지 않는다.

`main.c`에서는5ms 목표 주기로 TIM3/TIM5 raw counter를 읽고 snapshot을 TEL 저장소에 발행한다. 왼쪽은 기존대로 전진 양수로 부호를 바꾼다. CPS는100ms 시간창의 값으로 유지한다. `encoder_t_ms`는 새 count를 읽은 시각이며 CPS가5ms 속도 추정값으로 바뀌는 것은 아니다.

기존 `encoder_speed_log_process()` 이름과 메인 루프 호출은 유지하되, 함수 내부의 반복 `ENC3/ENC5` USB 문자열 출력은 제거한다. 부팅 때의 encoder 자체 검사와 성공/실패 출력은 유지한다. 반복 로그 때문에 구동 중 루프가 UART 송신을 기다리지 않도록 하는 선택이다.

## USART1 송신 흐름과 버퍼 수명

```text
ACK/PONG/ERR → 응답 FIFO 최대4개 ─┐
TEL → 최신 대기 프레임1개 ────────┼→ 고정 송신 버퍼 → HAL_UART_Transmit_IT
                                │                         │
                         응답을 먼저 선택          USART1 IRQ / TX 완료
                                │                         │
                                └──── 다음 main poll ← 완료 flag
```

`HAL_UART_Transmit_IT()`는 데이터를 끝까지 보내고 돌아오는 함수가 아니다. 그래서 stack의 지역 배열을 넘기지 않고, 전송이 끝날 때까지 변경하지 않는 static 송신 버퍼를 사용한다. `uart_sendf()`의 지역 문자열은 먼저 대기 버퍼로 복사한다. 이미 전송 중인 프레임은 중간에 끊거나 섞지 않으며, 다음 프레임부터 응답 FIFO를 TEL보다 먼저 선택한다. 대기 중인 TEL은 최신값 하나로 합치고, 응답 뒤에서50ms 넘게 기다린 TEL은 버린다. 이는 STM 원시 encoder sample 유실이나 RX ring의 drop과 다른 송신 대기 정책이다.

`HAL_UART_TxCpltCallback()`은 완료 flag만 바꾼다. 큐 변경과 출력 상태 변경은 main loop에서 수행한다. 현재 보드에는 USART1 IRQ/NVIC와 `HAL_UART_IRQHandler(&huart1)`가 이미 있으므로 DMA·새 IRQ 설정은 필요하지 않다. 로컬 STM32 HAL 소스에서 `HAL_UART_Transmit_IT()`가 버퍼 포인터를 보관하고, 최종 TC 처리 후 gState를 READY로 바꾸어 callback을 부르는 것을 확인했다.

## 송신 오류와 기존 정지 경로

송신 시작이 HAL_ERROR/HAL_BUSY로 실패하거나, TX 완료가100ms 동안 오지 않거나, 중요한 응답 FIFO가 포화되면 즉시 `motor_output_stop_all()`을 호출하고 속도 요청을0으로 만든다. E-stop latch가 없다면 DISARMED/OUTPUT_ERROR로 표시한다. TX fault는 재부팅까지 유지하며 ARM/CMD로 다시 구동하지 못한다. DISARM이나 ESTOP_RESET이 TX fault를 해제하지 않는다. 전송 중 버퍼는 오류가 나도 재사용하지 않는다. `uart_mvp_init()`은 지금처럼 부팅 시 한 번 호출하는 용도다.

100ms는511byte 이하 프레임의115200baud/8N1 이상적 전송 시간 약44.4ms보다 긴 소프트웨어 감시값이다. 이론 전송 시간이나 PC 검사가 보드의 ISR 지연·정지 지연을 보장하지는 않는다.

수신은 한 번의 `uart_mvp_process()`에서 최대64byte를 처리하고 메인 루프로 돌아온다. 그 안에서도 기존 E-stop과300ms 명령 timeout 검사를 유지한다. TX fault 검사나 TX 완료가 명령 timeout을 갱신하지 않는다. 기존15% 직진·20% 회전 제한과 좌측960/930 gain도 유지한다.

## PC 검사와 실제 검증의 경계

[검사 결과](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/assets/logs/wifi_link/2026-10-21_distance_timing_candidate_review/validation.json)는 실제 후보 C를 native PC에서 실행한 것이다. 기존 mapper→motor 출력/timeout/E-stop, snapshot의16/32bit wrap·역방향·정수 경계,5ms count/100ms CPS 분리, 비동기 버퍼 수명·FIFO·TEL 합치기, 잘못된 UART callback, 응답 포화/전송 실패/완료 누락 시 정지, TX 중 timeout/E-stop, RX64byte 예산을 확인했다.

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_distance_timing_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
```

사용자 입력본은 같은 명령에 `--saved`를 추가한다. 기존 동기 `HAL_UART_Transmit()` mock만 있는 host 검사는 새 비동기 경로를 재현하지 못하므로 이 검사의 adapter로 먼저 확인한다. 동작 자체를 건너뛰거나 옛 PASS를 새 저장본 PASS로 사용하지 않는다.

이번 블록을 저장해도 아직 `distance_move_update()`와 PWM 차단은 호출되지 않는다. 다음 연결 단계에서 목표 명령·정지 기준점·안전 supervisor·출력 소유권·ESP UI를 묶어야 한다. 그 단계에서5ms 호출을 실제 보드에서 유지하는지와 최대 지연, 변경된 UART 응답/텔레메트리,5cm 첫 정지의 실제 잔여 이동량을 확인한다. PC 검사 PASS를 실제 거리 오차 PASS로 확대하지 않는다.

## 입력 순서

아래5개 파일의 지정 범위를 모두 입력한 후 저장한다. 이미 검토한 `distance_move.h/.c`는 그대로 사용한다.

- `Inc/encoder_speed.h`, `Src/encoder_speed.c`
- `Src/main.c`
- `Inc/uart_mvp_protocol.h`, `Src/uart_mvp_protocol.c`

main.c 안의 상수·상태·함수·callback을 포함하여 아래 번호 순서대로 적용하면 된다.
