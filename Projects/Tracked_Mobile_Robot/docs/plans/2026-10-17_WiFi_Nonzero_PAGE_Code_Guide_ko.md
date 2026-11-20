# Wi-Fi 방향 입력 — PAGE와 모드 표시 연결

상태: **mode0 사용자 빌드/플래시와 NZ-01~04 모터 분리 시험 PASS**. 현재 `WIFI_CONTROL_ZERO_ONLY=0U`, `WIFI_UART_PARTIAL_TEST_MODE=0U`. 아래 최초 입력의1U 지시는 완료 이력이다. [보고서38](../verification/38_WiFi_Nonzero_Disconnected_Motor_Bench_Closeout_2026-10-17_ko.md)을 따른다.

## 이번 변경의 목적

core가 요청값을 UART로 전달할 준비를 마쳤으므로, 브라우저에서 현재 누르는 방향을 CMD 값으로 만들고 ESP가 실제 설정을 알리도록 연결한다. ARM은 명시적 사용자 클릭이고 첫 CMD는0이다. ACTIVE가 된 뒤 방향 입력을 받는다.

초기 조작은 방향 버튼 네 개로 제한한다. 전진/후진은 `vx=±50, w=0`, 좌/우 회전은 `vx=0, w=±250`이다. 기존 입력 한계 ±100mm/s·±500mrad/s 안의 고정 요청값이며 실측 속도가 아니다. 실제 모터 방향·회전·정지 특성은 후속 실물 시험 범위다.

```text
수동 ARM → ARM ACK → 첫 zero CMD ACK/새 TEL → ACTIVE
  → 누름: 현재 방향 저장 → 다음 송신 시점/새 ticket/단일 pending 조건 → CMD
  → 놓음 또는 버튼 영역 이탈: 방향 폐기 → 다음 가능한 CMD는0
  → zero ACK 전: 새 방향 입력 금지
  → zero ACK 뒤: 새 누름이 있어야 방향 입력 재개
focus/visibility/포인터 취소/소유권 유실/명령 실패 → 방향 폐기·DISARM
연결 유실/모드 변경 → 연결 종료·의도 폐기 → 재연결은 HELLO만, 수동 ARM 필요
```

버튼을 놓으면 zero 요청으로 복귀하며 ARM 상태 자체는 유지한다. DISARM은 별도 정지/무장 해제 요청이다. zero ACK는 실제 바퀴 정지 증거와 구분한다.

## 정확한 교체 범위

대상은 `03_Firmware/esp32_wifi_link/main/wifi_link_main.c` 한 파일의 두 블록이다. 아래 `.c.txt` 파일에는 해당 블록 전체가 들어 있다. C 문자열의 따옴표와 마지막 세미콜론을 포함해 교체한다.

| 입력 블록 | 실제 교체 범위 |
| --- | --- |
| [PAGE.c.txt](../../assets/logs/wifi_link/2026-10-17_nonzero_page_candidate/PAGE.c.txt) | `static const char PAGE[] =`부터 `"</script></body></html>\n";`까지 선언 전체. 바로 다음 `static int status_json(...)`은 포함하지 않는다. 입력 전 기준 232줄 시작. |
| [wifi_control_snapshot.c.txt](../../assets/logs/wifi_link/2026-10-17_nonzero_page_candidate/wifi_control_snapshot.c.txt) | `static int wifi_control_snapshot(...)`의 선언부터 함수 닫는 `}`까지 전체. 다음 HTTP 핸들러 주석/함수는 포함하지 않는다. 입력 전 기준 746줄 시작이며 PAGE 교체 후 줄 번호는 달라진다. |

두 블록 모두 저장한 다음 실제 저장본을 다시 읽고 PC 검사한다. **`WIFI_CONTROL_ZERO_ONLY=1U`를 유지한다.** 이 상태에서는 새 방향 버튼이 표시돼도 비활성이고, 기존 ARM/zero 제어만 가능하다. mode0은 이번 후보의 PC 임시 복사본에서만 검사했다.

[전체 후보 C](../../assets/logs/wifi_link/2026-10-17_nonzero_page_candidate/source/wifi_link_main.c)는 대조용이다. C 문자열 표기를 빼고 읽고 싶으면 [page.js](../../assets/logs/wifi_link/2026-10-17_nonzero_page_candidate/page.js)를 참고한다. 이 JavaScript 파일을 C 소스나 DevTools에 직접 붙여넣는 절차는 아니다.

## 어디가 어떻게 바뀌는가

| 위치 | 변경 전 | 변경 후·이유 |
| --- | --- | --- |
| PAGE HTML·`motionValues` | PING/ARM/DISARM | 방향 버튼4개와 고정 요청값 추가. 숫자 입력/슬라이더에 저장된 값을 자동 재사용하지 않는다. |
| `motionReady()` 추가 | 방향 입력 조건 없음 | nonzero 모드·내 ACTIVE 소유권·focus·fresh offer/TEL·ARMED·범위/PWM 조건이 갖춰져야 입력 가능하다. |
| `beginMotion()`/`endMotion()` 추가 | CMD 값이 항상0 | 실제 포인터 누름만 방향을 기록한다. 놓으면 방향을 버리고 `releaseZero`를 설정한다. 이전 CMD 응답 대기 중에도 zero 의도를 보존한다. |
| `clearMotion()`·취소 이벤트 | zero stream의 intent만 취소 | 방향/포인터 상태도 폐기한다. 예상치 못한 capture 유실·pointercancel은 DISARM, 정상 pointerup/영역 이탈은 zero다. |
| `sendCommand()` | `vx_mmps=0,w_mradps=0` 고정 | ACTIVE의 현재 방향값 또는0을 넣는다. 송신 주기·pending·ticket 검사를 통과한 시점에 값을 결정한다. |
| `controlTick()`·`handleResult()` | 주기적 zero | 100ms 목표 주기로 현재 값을 전송한다. release zero의 matching OK 뒤에만 다음 방향을 받는다. 실패 시 기존 정지 경로를 사용한다. |
| `validControl()`/`handleControl()` | `zero_only===true`만 허용 | boolean 모드를 받고 화면을 맞춘다. 같은 연결에서 모드가 바뀌면 연결을 닫고 제어 의도를 폐기한다. 다른 owner/control ID가 ACTIVE여도 내 입력을 유지하지 않는다. |
| `wifi_control_snapshot()` | JSON에 `zero_only:true` 고정 | `WIFI_CONTROL_ZERO_ONLY`에서 true/false를 생성한다. 값은 JSON boolean이며 문자열이 아니다. |

입력 이벤트에서 송신 시각을 강제로 당기지 않는 이유는 ESP CMD 접수의 최소 간격50ms와 충돌할 수 있기 때문이다. 입력값은 즉시 바꾸되 기존100ms 목표 주기·새 ticket·응답 대기를 지킨다. release 뒤 첫 가능한 CMD는0이며, ACK 전 새 방향으로 덮어쓰지 않는다. 네트워크/브라우저 지연까지 포함한 물리 정지 시간을100ms로 보장한다는 뜻은 아니다. DISARM은 일반 CMD 간격 제한을 우회하는 기존 우선 정지 경로다.

포인터 capture를 사용해 버튼 밖에서 놓는 입력도 관측하며, 영역 밖 이동은 zero로 처리한다. 동시에 여러 방향을 합성하거나 키 입력을 추가하지 않았다. 마우스/터치 기반 첫 조작 범위다. 재접속·새 ARM에는 과거 누름 상태를 넘기지 않는다.

## PC 검증과 다음 단계

[검증 기록](../../assets/logs/wifi_link/2026-10-17_nonzero_page_candidate/validation.json)과 [출력](../../assets/logs/wifi_link/2026-10-17_nonzero_page_candidate/validation.txt):

- 기존 C42개 + mode1/mode0 adapter 각6개 = C54개 PASS.
- 기존 PAGE46개 + 방향 입력20개 = 브라우저66개 PASS.
- PAGE 전체 C 문자열 초기화 native 컴파일/문자열 확인 PASS.
- zero_only 표시를 true로 고정한 오류와 PAGE 송신값을0으로 고정한 오류를 각각 검출.
- 실제 main/core 입력 hash는 불변. mode0은 PC 임시 디렉터리에만 적용.

PASS 기준은 첫 zero 보존, signed 방향값 전달, 짧은 누름/놓음·응답 대기 중 놓음·영역 이탈 처리, zero 응답 전 새 방향 차단, 만료 ticket/owner 유실/timeout/취소 뒤 명령 중단, 재접속 시 재무장·방향 복원 없음이다. 검사 중 발견한 요청 간격 충돌은 후보에서 바로잡았고 최종 결과를 기록했다.

실제 저장본의 PAGE 선언과 snapshot 함수는 후보와 내용이 일치한다. 함수 앞 설명 주석 한 줄이 빠진 것 외에 추가 변경은 없다. 저장본으로 C54개·브라우저66개·PAGE C 초기화와 negative control2개를 별도 실행해 통과했다. [저장본 검증 기록](../../assets/logs/wifi_link/2026-10-17_nonzero_page_saved_review/validation.json)과 [출력](../../assets/logs/wifi_link/2026-10-17_nonzero_page_saved_review/validation.txt)에 source hash와 결과를 보존했다.

사용자는 mode1 빌드·플래시 후 강력 새로고침과 `속도 0 전용`·방향 버튼4개 표시/비활성 확인 안내에 “확인 완료”라고 보고했다. 이후 `wifi_control_contract.h`의 `#define WIFI_CONTROL_ZERO_ONLY 1U`를 `0U`로 저장했다. 이전 저장본 PASS의 hash와 비교해 firmware 변경은 이 한 줄뿐임을 확인했다. 이 값은 ACTIVE의 nonzero 허용을 켜며 ARM/첫 zero 확인을 생략하지 않는다.

현재 mode0 저장본으로 core13개·adapter6개, 임시 mode1 복사본으로 기존/추가 회귀59+3+42+6개, 브라우저66개와 PAGE C 초기화 PASS. UART 값0 고정·PAGE 값0 고정·mode 표시 true 고정의 negative control3개도 검출했다. 검사 도구는 입력 모드를 기록하고 현재 모드의 firmware 복사본은 byte 단위로 보존하며 기존 zero-only 회귀는 임시1U에서만 실행한다. 실제 firmware 입력은 변경하지 않았다. [core 증거](../../assets/logs/wifi_link/2026-10-17_nonzero_mode0_saved_review/core_validation.json)와 [PAGE/main 증거](../../assets/logs/wifi_link/2026-10-17_nonzero_mode0_saved_review/main_validation.json)를 참조한다.

**mode0 화면 확인 완료:** 사용자는 ESP 빌드·플래시→강력 새로고침→`제어 상태 · IDLE · 방향 입력 모드` 확인 안내에 “완료 다음”이라고 보고했다. USB-only/LiPo 분리에서 `FAULT / ESTOP_ACTIVE` 및 ARM/방향 비활성은 예상되는 동작이며, 통신 정상 표시는 fresh TEL 수신이라는 뜻이다. 당시 다음은 [NZ-01 준비](2026-10-17_WiFi_Nonzero_Control_Integration_Plan_ko.md#nz-01-모터-분리-uartpwm-시험-준비)의 감지 전원 복원과 DISARMED/출력0 확인이다. 후속 NZ-01~04의 nonzero UART/DIR/PWM·정지 근거는 보고서38에 있다. 실제 모터 동작은 별도다.
