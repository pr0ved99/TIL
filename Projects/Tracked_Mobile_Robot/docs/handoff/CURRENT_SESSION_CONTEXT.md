# Current Session Context

Last updated: 2026-09-27 — 9/26~27 bench 마감, M1 수동 시험 코드 사용자 입력 중 휴식.

## 지금 이어갈 작업

**ESP 펌웨어 입력 중단 지점에서 재개한다. 전동 구동은 아직 하지 않았다.**
[9/27 progress](../progress/2026-09-27_progress.md)와
[M1 코드 안내의 재개 메모](../plans/2026-09-27_M1_One_Shot_Console_Code_Guide_ko.md)를 먼저 읽는다.

- 실제 파일: `03_Firmware/esp32_uart_bridge/main/hello_world_main.c`.
- 입력은 `bridge_bench_command()`까지; `bridge_bench_advance/console_init/console_poll` 몸체는 비어 있다.
  app_main의 init/poll 호출 두 곳도 미추가다. #if 줄 연속 처리, SCRIPED/finished/HLEP 오타는 안내 문서에 기록했다.
- 기존 ESP 네 hook=0U, 새 수동 기능 매크로=1U. 현재 파일은 **미완성·컴파일 오류가 남은 WIP**다.
  기능을 대신 완성하거나 빌드·플래시하지 않는다. Git 저장이 빌드 가능한 이미지라는 뜻은 아니다.
- 설명은 목적·ARM/CMD/timeout 흐름·시간 상수·enum과 s_bench_state까지 했다.
  **다음은 expected_seq/tel_mark 등 상태 변수 설명부터**다. 작성한 부분을 다시 타이핑시키지 않는다.
- 완성 목표: 수동 HELP/RESET_ESTOP/M1_PULSE/STOP, M1 5%·M2 0%, CMD 한 번·STM timeout 300ms,
  종료·실패 뒤 재구동 잠금. 새 소스의 빌드/플래시/HELP/구동은 모두 미실행이다.
- 저장된 파일 검토 → 사용자 ESP 빌드·플래시 → LiPo 분리 상태의 HELP 확인 순서다.
  STM32 실행 코드는 바꾸지 않았으므로 이번 기능만을 위해 STM 재플래시를 요구하지 않는다.

## 현재 연결과 완료 결과

정본: [report 29 좌우 매핑](../verification/29_Vehicle_Side_Mapping_Correction_and_Hand_Rotation_Check_2026-09-26_ko.md),
[report 30 이번 검사 마감](../verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md).

| 항목 | 현재 기준 |
| --- | --- |
| 왼쪽 | 모터 A / M1 / JENC_1 / TIM3 PB4(A)·PB5(B) / left_cps |
| 오른쪽 | 모터 B / M2 계획 / JENC_2 / TIM5 PA0(A)·PA1(B) / right_cps |
| 동력선 | A Motor+→M1A, Motor−→M1B 연결 확인. B 동력선은 분리·절연 유지 |
| 출력 | M1 PB6 PWM·PC8 DIR, M2 PB7 PWM·PC9 DIR |
| 엔코더 커넥터 | 두 JENC 모두 Pin1 GND / Pin2 B raw / Pin3 A raw / Pin4 AUX_5V |
| 입력 조정·환산 | 각 신호 1kΩ 직렬+MCU 측 15kΩ GND, TIM3 부호 반전/TIM5 유지, 1560 counts/rev |

두 모터는 섀시에서 분리해 검사했다. 기존 A=right/B=left는 과거 연결 이력이다.
최종 커넥터 교환 후 전진 양수·후진 음수·정지0·독립성 사용자 보고 PASS.
실제 전동 구동 방향과 기구 고정 상태의 최종 검증은 아직 없다.

- [report 28](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md)의 저항 8곳·전원 6검사·양쪽 +5.05V 완료 유지.
  이후 실제 엔코더 네 입력 LOW0V/HIGH 약2.86V, 정지10초 이상 CPS0·양방향 손회전도 사용자 보고 PASS.
- [warm reset 원본](../../assets/logs/encoder/2026-09-26_actual_encoder_warm_reset/README.md): STM만 RESET,
  엔코더 전원 유지·정지·S0 잠금. TEL169/16.8초, STM200~17000ms, 300/400ms 포함 CPS/PWM0.
  제어문자 거부5회+embedded CR1회 뒤 정상 TEL. 최초0~200ms/cold boot/전동 노이즈는 미검증이다.
- S1 OFF/ON 순간 양쪽 CPS −10/+10은 바로0으로 복귀했다고 확인했다. 이 관측은 마감했으며 재검사·필터 수정으로 돌아가지 않는다.
- 도면은 `09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_ENC_Conditioning_WIP.vrt`와 exports의 같은 이름 PDF다.
  JENC_1=C50/R11~14, JENC_2=C54/R5~8. 좌표·Net·도면 SHA는 report 28을 따른다.

## 전원과 미완료 범위

- 버스바 두 개, MDD B+=K1 87/B−=GND 16AWG, K1 주선14AWG. 사용자의 선재 진행 결정을 반복해서 묻지 않는다.
  Littelfuse F1=10A/F2=1A 사용자 확인. T004 기존 PASS, 전체 T005A PARTIAL은 유지한다.
- 이번 S0 해제 전후/S2 전→후 rail 0.23→11.78V; 다시 S0 잠금 뒤5초1.28/30초0.59V 관측.
  1kΩ은 무전원 방전에만 임시 사용 후 제거했다. 값 감소만으로 rail-off PASS를 만들지 않는다.
- 마지막 보고한 셀 값은4.12/4.16/4.16V다. 시점·앞선 알람/DMM 값은 report 30에 보존했다.
  종료 시 전압을 새로 측정한 것은 아니며, 이미 완료한 배터리 확인을 이유 없이 재시작하지 않는다.
- 마지막 안내는 S0 잠금/S1 OFF/LiPo 분리 후 코드 입력이었다. **최종 전원 분리 완료는 별도 보고되지 않았다.**
  문서만으로 현재 전원이 꺼졌다고 단정하지 않는다.
- USB 개발 구성: #1의 보드용2P 두 개 분리·절연, STM JP5=U5V/JP1=OPEN, 두 보드 USB 공급.
  ESP 콘솔 입력은 보드의 UART 표기 USB 커넥터/UART0. COM 번호는 고정하지 않는다.
- #1은 로직5V 두2P 분기, #2는 AUX5V/실제 엔코더/S0-B. 두 OUT+는 분리하고 GND 공통.
  독립 전원 운전은 USB 제거 후 STM JP5=E5V/JP1=OPEN이다.
- 실제 ESP 보드의 왼쪽 BOOT 표기는 EN LOW, 오른쪽 RESET 표기는 GPIO0 LOW였다.
  버튼 표기를 일반 DevKit과 같다고 가정하지 않는다.

## 작업 방식

- 사용자가 기능 코드 입력과 STM/ESP 빌드·플래시·물리 작업을 한다. Codex는 실제 저장 파일 검토와 설명을 한다.
- 논리적으로 연결된 블록과 정확한 위치를 한 번에 제공한다. 하드웨어는 한 묶음씩, 통과 검사는 변경·실패 없이 반복하지 않는다.
- 과거30/30은 당시 완료 기준선이다. 이번 WIP는 빌드/테스트 통과가 아니다.
- 진행 기록은 마감 때 갱신한다. 사용자 요청 없이 subagent·전체 과거 대화 아카이브를 사용하지 않는다.
- 저장소 `C:/Users/eyh12/workspace/TIL`, 브랜치 `agent/dual-encoder-bringup`.
  이번 마감은 사용자 요청으로 문서·증거·미완성 소스를 함께 Git 체크포인트로 보존한다.
