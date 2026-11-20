# Wi-Fi nonzero 명령 통합 실행 범위

작성: 2026-10-17. 상태: **mode0 사용자 빌드/플래시·NZ-01~04 모터 분리 선택 시나리오 PASS / 실제 Wi-Fi 모터 구동 전**.

## 목표

완료한 ARM/zero CMD의 연결 소유권·ticket·만료·우선 정지를 유지하면서, ACTIVE에서 현재 사용자의 nonzero 입력을 STM으로 전달한다. 기존 zero-only 회차를 자동 반복하거나 후속 PCB 기능을 선행 조건으로 추가하지 않는다.

배터리 ADC·자동 저전압 정지는 후속 PCB 단계다. 현재 MVP의 통전 주행은 셀 알람과 작업자 감독, 경고 시 즉시 수동 정지·시험 종료의 운영 범위다. 알람 보유는 사용자 확인이며 설정·정상 동작 확인과 실제 적용은 별도다.

## 변경 전 저장본을 기준으로 정한 확장 지점

| 위치 | 변경 전 동작 | 확장 시 지킬 조건 |
| --- | --- | --- |
| `wifi_control_contract.h/.c` | 범위는 vx ±100mm/s·w ±500mrad/s지만 mode는 zero-only이며 적합성 함수가 nonzero 거부 | 기존 범위 유지; 설정·표시·PC 검사와 허용 정책 일치 |
| `wifi_control_state.c` | CMD sent에서 nonzero를 거부하며 TEL/상태 검증도 zero 중심 | ARM/첫 zero 확인은 유지; ACTIVE nonzero와 정지 확인의 조건을 구분 |
| `wifi_control_executor.c` | 송신 문자열을 `vx_mmps=0,w_mradps=0`으로 생성 | 허가·기한을 통과한 해당 요청의 값을 송신; 저장값의 자동 반복 송신 금지 |
| `wifi_link_main.c` PAGE/adapter | 브라우저 CMD가 zero 고정, offer의 `zero_only=true`를 요구 | 사용자 조작 중에만 현재 값을 새 ticket으로 생성; 수신/표시 계약도 함께 확장 |

이 값은 명령 단위다. 현재 open-loop 구동을 실측 속도 제어로 설명하지 않는다. `WIFI_CONTROL_ZERO_ONLY` 한 줄만 해제해서 통합 완료로 취급하지 않는다.

## 구현 순서와 안전 불변조건

1. **제어 core:** 입력 허용 정책·상태머신·executor를 한 흐름으로 검토한다. ARM → 새 zero CMD ACK/새 TEL → ACTIVE 순서는 유지하고, nonzero는 ACTIVE의 현재 owner만 허용한다. ACTIVE의 정상 nonzero TEL을 zero 위반으로 오판하지 않도록 한다.
2. **브라우저와 adapter:** 명시적 ARM과 누르고 있는 조작을 구분한다. 조작 해제는 zero, focus/visibility/연결 유실·거부/만료는 기존 정지 경로로 이어진다. 재접속·재ARM으로 이전 조작값을 복원하지 않는다. 구체적인 조작 UI와 이벤트 계약은 코드 입력 전에 정한다.
3. **PC 검증:** 정상 zero→nonzero→zero, 첫 zero 이전 nonzero 거부, 다른 owner/오래된 ticket 거부, 만료·ACK 유실·끊김 후 정지, UART 문자열 값 일치, 정지 뒤 미송신 명령 폐기를 검사한다. 기본 zero-only 설정의 기존 동작도 보존한다.
4. **사용자 빌드/실물:** PC 검사와 사용자 STM/ESP 빌드 뒤, 모터 동력을 차단한 조건에서 UART·실제 PWM·정지 경로를 대조한다. 이후 별도 회차에서 lifted 단일 모터/차량 구동으로 이어간다. 소프트웨어 검사를 실제 회전·정지 증거로 확대하지 않는다.

기존 명령 유효시간·소유권/취소·UART 줄 복구와 STM timeout은 유지한다. STM 최종 출력 권한과 PC7 fault 입력을 우회하지 않는다. 수정으로 영향받은 동작을 검증하되 완료한 전체 zero-only 묶음을 이유 없이 다시 수행하지 않는다.

## 현재 재개점

Wi-Fi nonzero core/PAGE 통합·mode0 사용자 빌드/플래시와 NZ-01~04 모터 분리 UART/DIR/PWM 시험을 완료했다. 방향 입력·놓음 zero·출력 중 DISARM·창 전환 정지/자동 재무장 방지의 선택 시나리오 PASS다. 실제 모터 부하·주행은 다음 별도 회차다. [보고서38](../verification/38_WiFi_Nonzero_Disconnected_Motor_Bench_Closeout_2026-10-17_ko.md) 참조. 현재 ZERO_ONLY=0U/UART시험mode0. 다음은 종료 전원 분리 확인과 별도 lifted 단일 모터 회차 준비다. 아래는 완료된 준비 당시 기록이다.

## NZ-01 모터 분리 UART/PWM 시험 준비 당시 기록

목적은 변경된 PAGE→ESP→STM의 방향 요청값과 실제 PWM, 놓음 뒤 zero 및 DISARM을 모터가 분리된 상태에서 대조하는 것이다. 준비 단계의 목표는 정상 감지 입력에서 fresh `DISARMED`/출력0 복귀까지다.

- 최신 사용자 확인: STM·ESP USB 연결, LiPo 분리. 마지막 배선 기록의 모터 전력4선·MDD 제어5핀·#1 보드용2핀 두 개 분리/절연을 유지한다. MDD B+는 복원돼 있으며 이를 분리된 것으로 가정하지 않는다.
- #2 AUX_5V와 S0-B/옵토커플러 감지 배선은 기존 구성을 사용한다. 두 USB를 유지하면서 #1 보드용2핀 두 개를 연결하지 않는다.
- 안내 순서: S1 OFF/S0 잠금 상태에서 LiPo 연결→S1 ON→S0 해제→STM RESET 한 번. 보유 LiPo 알람을 사용하고 경고·발열·냄새 등 이상 시 S1 OFF 후 LiPo를 분리한다. S2는 누르지 않는다.
- 기대 결과: fresh STM TEL `DISARMED / BOOT` 또는 `DISARMED / DISARM`, vx/w·PWM/CPS 모두0, ESP 제어IDLE. `ESTOP_ACTIVE`/`ESTOP_LATCHED`가 남거나 출력이0이 아니면 ARM으로 진행하지 않고 그대로 결과를 보고한다.
- 이번 준비 단계에는 ARM/방향 입력이 없다. 복귀 결과 후 LA D0/PA9·D1/PA10·D4/PB6·D6/PC7·D7/PB7 캡처와 실제 방향 입력 회차를 안내한다. 과거 rail 관측이나 완료한 zero-only 시험 전체를 반복하지 않는다.

준비 후 실행 결과는 위 현재 재개점과 보고서38을 따른다.
