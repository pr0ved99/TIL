# 귀가 후 통신 관측과 최종 MVP 잔여 인수 대조

2026-10-23 · `TK-MVP-05-02/03` 증거 연결·잔여 항목 대조.

**10/24 후속:** 아래4절의 코드 경로 검토는 [보고서40](40_WS_Delivery_Path_and_Minimal_Observation_2026-10-23_ko.md), 브라우저 계측A는 [v5.2 실제3조건 관측](../../assets/logs/wifi_link/2026-10-24_handler_timing_air_forward_run01/README.md)으로 완료했다. 이어 [운용·재현 절차](../handoff/CURRENT_MVP_OPERATION_RUNBOOK_ko.md)와 [시연 구성안](../plans/2026-10-24_MVP_Demo_Outline_ko.md)을 작성했다. 새 영상/공개는 없으며 아래 인수 경계·원인OPEN을 유지한다. 본문의 “다음”은10/23 당시 계획이다.

**오늘 세 관측의 분석과 증거 연결은 완료했다. 기본 주행·정지·거리 기록의 기존 판정을 유지하며 전체 MVP 인수는 미완료다.** 이번 작업은 추가 주행·펌웨어 수정이나 요구사항 면제가 아니다. [검증표](05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)가 요구사항 판정의 정본이다.

## 1. 오늘 새로 연결한 증거

| 기록 | 수용한 구간과 결과 | 주요 수치 | 보존 한계 |
| --- | --- | --- | --- |
| [IDLE 기준](../../assets/logs/wifi_link/2026-10-23_home_idle_baseline_run01/summary_ko.md) | DISARMED/IDLE·명령/PWM/CPS0·count0/0의 수신 관측 | TEL span74.702초, TEL 최대125.4ms·제어78.5ms | history/TEL 삭제0. 명령 송신 경로 미실행 |
| [ARM·속도0](../../assets/logs/wifi_link/2026-10-23_home_armed_zero_run01/summary_ko.md) | ACTIVE70.945초·CMD724회OK, window blur로 DISARM726→OK/IDLE | TEL 최대124.3ms·제어80.0ms, CMD 왕복 최대150.3ms | 앞선 기록기 계속 사용. 오래된 history30000/TEL3900개 삭제, 이번 ARM~종료 구간은 보존. 독립 시행으로 합산하지 않음 |
| [공중 전진](../../assets/logs/wifi_link/2026-10-23_home_air_forward_run01/summary_ko.md) | 첫 전진 송신~capture 해제24.274초, 자동 DISARM0. 입력 해제→명령/PWM/CPS0→수동 DISARM267 OK/IDLE | 전진 TEL 최대120.9ms·제어81.8ms. 전체267개 명령OK. DISARM 왕복201.3ms | 전체 TEL span37.071초·버퍼 삭제0. 지상 부하/장시간 수용 아님 |

세 파일 모두 원본 gzip을 풀어 raw SHA256과 archive SHA256을 출처 manifest와 대조했다. [대조 기록](../../assets/logs/wifi_link/2026-10-23_home_acceptance_review/review.json)에 원본 해시·분석 파일 해시와 기존 MUST 표행 스냅샷을 보존했다.

마지막 관측은 boot331448985/session2, DISARM request267/seq2142829116 OK, IDLE·DISARMED/DISARM이다. 명령/PWM/CPS0과 count25291/24968 고정이 DISARMED TEL 이후8.256초 보존됐다. 방향 버튼4개는 비활성화였다. 최종 전원 분리·종료 셀 전압은 미보고다. 마지막 관측값을 현재 실물 상태의 실시간 확인으로 표현하지 않는다.

전원은 사용자가 앞선 배터리→XL4015 #1→두 보드·USB 급전 분리 안내에 따라 연결한 구성이다. 이번 전압/전류를 새로 보고하지 않았으므로 과거5.02V를 이번 측정으로 쓰지 않는다. 중량 최종 사용자 보고3.25kg은 유지한다.

## 2. 완료 근거와 유지할 판정

| 범위 | 현재 근거 | 이번 대조의 결론 |
| --- | --- | --- |
| `REQ-DRIVE-001~003` | 기존 공중/지상 방향, 놓음·DISARM,10/20 UART 단절→실제 궤도 정지·재연결 무동작. 이번 공중 전진/수동 종료 추가 | 기존 PASS 기능 범위 유지. 단절 시험·네 방향을 다시 필수로 요구하지 않음 |
| `MVP-011 / REQ-ODO-001 / T-ODO-001` | 지상 run03/04 실측1002mm·평균1002.640333/1000.953333mm·오차 기록 | 기존 PASS 기록 범위 유지. 이번 공중 count를 새 지상 거리·직진성 자료로 쓰지 않음 |
| `REQ-POWER-004 / T-PWR-004` | BX100 설정/표시와 과거 주행 중 경고음→사용자 전원 차단 보고 | USER-REPORTED PASS 유지. 새 저전압 시험 불필요 |
| 오늘 통신 관측3개 | 위 원본·분석·종료 응답 | 각 보존 구간 분석과 최신 검증표 연결 완료. 연속 운전 신뢰성 전체 PASS로 확대하지 않음 |
| MCU 안전 제한·실행 코드 | 기존 control200ms/TEL250ms/STM command300ms, cap150/200‰·gain960/930·k1687/19500 유지 | 코드·timeout·빌드/플래시 변경 없음. 보드 firmware hash를 새로 읽은 증거도 아님 |

## 3. 잔여 항목 확정

아래 ACC ID는 이번 대조의 관리 표식이며 기존 Requirement/Test ID를 대체하지 않는다. **모든 OPEN/PARTIAL이 지금 다시 수행할 실물 시험이라는 뜻은 아니다.** 특히 사용자 제외 조사와 미재현 이력을 자동으로 새 작업 조건으로 되돌리지 않는다.

| 관리 ID / 분류 | 연결 범위와 현재 상태 | 남은 처리·완료에 필요한 근거 |
| --- | --- | --- |
| **ACC-COM-01 · 현재 조사** | 전진 TEL age265.2≥250ms·좌회전 control age204.9≥200ms의 과거 보호 정지. 전달 지연 원인OPEN | 기존 프레임 생성 시각과 브라우저 도착 사이에서 ESP 전송 대기·네트워크 전달·브라우저 처리 중 관측 가능한 구간을 먼저 특정한다. 근거에 따른 수정이나 검증된 운용 조건/수용 기준이 없으므로 이번 정상 표본만으로 해결 처리하지 않음 |
| **ACC-UI-01 · 과거 미재현 이력** | ground run02 수동 DISARM 뒤 버튼 활성 보고OPEN. 당시 v5의 새 소켓 응답/클릭 이력 없음 | 이후 정상 수동 경로와 별도 보존. 당시 누락된 클릭을 복원하거나 원인을 확정할 수 없음. 재현되면 v5.1 클릭→송신→결과→UI 상태로 조사하며, 현재 수정 근거 없이 임의 수정/반복 클릭 시험을 추가하지 않음 |
| **ACC-REL-01 · 기존 인수 경계** | `MVP-001/002/004/009`, UART/bridge 전체release PARTIAL | 기존 source/image·실행 앱·setup·파형/로그의 연결과 미확인 범위를 마감 자료에 명시. 이번 브라우저 ACK가 과거 누락된 파형/reset marker/전체 오류 분기를 대체하지 않음 |
| **ACC-PWR-01 · 기존 인수 경계** | `REQ-POWER-002` CONDITIONAL, `REQ-POWER-003 / MVP-003` PARTIAL | 기존 buck 부하·두 보드 공급·USB 개발/배터리 단독 규칙과 최종 하네스 미수용 범위를 구분. 이번 새 전압/파형 없음.10/17 제외한 정격/도면 조사 재개나 전체 전원 PASS로의 변경 없음 |
| **ACC-MOT-01 · 기존 인수 경계** | `REQ-MOTOR-004/005`, 전체 no-load/실구동 조건 CONDITIONAL/PARTIAL | 기존 MCU 핀/드라이버 입력·단일 모터·지상/공중 subset을 유지하고 전체 no-load 신호/소음·반복 조건의 미확인을 명시. 온도·정량 전류는 후속 결정 유지 |
| **ACC-ENC-01 · 기존 인수 경계** | `REQ-ENC-001` CONDITIONAL, `REQ-ENC-002` PARTIAL | 기존 영구 조정부 HIGH/LOW·부호/독립성·회전 count와 미확인 출력형식/파형/phase/구동 노이즈를 구분. 거리 오차 기록이나 이번 count 정상으로 신호 전체를 PASS 처리하지 않음 |
| **ACC-ESTOP-01 · 기존 인수 경계·제외 조사** | `MVP-013`, `REQ-ESTOP-001~011/016~020`, T005A PARTIAL/T007 BLOCKED | T004의 sense/latch/PWM과 단발 S0·rail DMM 근거를 전체 rail-off/실모터/수동 재투입 수용과 분리.10/17 제외한 정격/도면 재검토를 복원하지 않으며 제외를 전체 PASS/면제로 바꾸지도 않음 |
| **ACC-DOC-01 · 최종 산출물** | `MVP-012 / T-DOC-001 / TK-MVP-05-03~05` 진행 중 | 현재 README·기준 firmware/배선·운용 조건·재현 순서·대표 시연·공개 파일/커밋 묶음을 맞춘 뒤 최종 적용 MUST 판정을 대조. 새 최종 demo 영상과 공개 묶음은 이번에 만들거나 게시한 것이 아님 |

기구 `REQ-MECH-002/003`은 기존 USER-REPORTED PASS를 유지한다. 전체 T-MECH-002의 제작 identity·치수/사진 미기록은 기존 한계이며 오늘 새 장착 확인을 요구하지 않는다. 관련 과거 근거와 세부 요구사항은 검증표를 따른다.

## 4. 지금 실행할 다음 작업

**다음 한 묶음은 ACC-COM-01의 PC 코드 경로 검토와 관측 지점 설계다.** 추가 주행 전에 ESP의 WS 상태/TEL 생성→전송 요청→전송 대기/실행 경로와 브라우저 message 수신→처리 순서를 대조한다. 현재 기록기의 수신 시각과 ESP uptime만으로 알 수 없는 구간을 명시하고, 필요한 최소 관측값·저장량·기존 정지 경로 영향부터 검토한다.

이 보고서에서는 그 코드 검토나 새 진단 코드를 구현한 것으로 기록하지 않는다. 특정 구간의 근거가 나온 뒤 수정 여부와 관련 경로만의 검증을 결정한다. MCU 코드가 필요하면 기존 사용자 입력→저장본 재검토→사용자 빌드/플래시 흐름을 따른다. 기존 제한 완화·원인 미확정 상태의 무기한 재주행·완료91 PC 감사 재실행은 다음 작업이 아니다.

ACC-UI-01은 별도 미재현 이력, ACC-REL/PWR/MOT/ENC/ESTOP는 기존 인수 경계다. 해당 경계를 어떻게 최종 수용할지에 관한 근거/범위 변경은 아직 확정하지 않았다. 따라서 “문서만 쓰면 전체 MVP 완료” 또는 “남은 실물 시험은 정확히 N개”라고 말할 수 없다. 이번 작업으로 기존 MUST를 새로 면제하지 않는다.

## 5. 후속·게시 경계

- 온도 `MVP-015 / REQ-THERM-001 / T-LOAD-001 / ST-MVP-04`는 DEFERRED / NOT_RUN이다. 전류·ADC·자동 저전압·IMU/PID/RTOS/CAN/ROS2와 별도 확장 PCB도 기존 후속 범위다. 센서 배송·PCB 제작을 현재 MVP 선행으로 추가하지 않는다.
- 이번에 검증표·현재 진행/인수인계·계획/README·메모리의 현재 포인터를 맞췄다. 원본3개와 판정/한계는 위 링크로 추적한다. 기존 MUST 표행의 판정은 변경하지 않았다.
- 이번 요청은 잔여 인수 대조 진행이며 전체 마감 게시 요청은 아니다. Git commit/push·Calendar·Notion 추가 게시는 수행하지 않았다. 직전 전원 조정 마감 게시 영수증을 이번 게시 증거로 사용하지 않는다.

관련 근거: [이전 전원 조정 비교](../../assets/logs/wifi_link/2026-10-23_power_adjusted_drive_run01/comparison_ko.md), [전진 자동 정지](../../assets/logs/wifi_link/2026-10-23_forward_auto_disarm_run01/observations.json), [좌회전 자동 정지](../../assets/logs/wifi_link/2026-10-23_left_auto_disarm_run01/observations.json), [검증표의 기존 인수 대조](05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#현재-완료-범위와-남은-판단).
