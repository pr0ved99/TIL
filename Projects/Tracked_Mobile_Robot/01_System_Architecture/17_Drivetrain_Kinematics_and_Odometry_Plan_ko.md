# Drivetrain Kinematics and Odometry Plan

**10/20 최신 상태:** 실물 톱니 **14개** 확인. 연속6개 링크 동일 형상1→6의5간격48.1~48.3mm에서 피치9.62~9.66mm, 대표값9.64mm. 기존 실측1560counts/output rev 유지 →134.96mm/rev, 좌우 공통 초기 k=1687/19500≈0.08651282mm/count. 대표값은 측정 범위 중간값이며 수동 checkpoint 회귀 보정값이 아니다. 윗쪽 직선 궤도 수동 이동100/150mm의 좌우 평균 환산은100.138590/150.532308mm다. 기존12톱니 가정이 공통 scale 차이를 대부분 설명한다. 공중 궤도 이동 비교이며 지상 차체 거리 정확도·슬립/전체 MVP PASS는 아니다. 인수 이미지 고정·전용 정지/온도/지상1m는 미완료다.

> 문서 역할·상태 대조: **2026-10-19** — 운동학·오도메트리 목표와 현재 좌우 매핑, 누적 count의 생산 경로 대조. 거리 보정·1 m 시험 완료를 뜻하지 않는다.
> [현재 구현·검증 범위와 문서 안내](README.md) · [최신 검증 판정](../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md). 날짜별 과거 수치·판정은 당시 기록이다.

## 실물14톱니·5피치 측정에 따른 거리 모델 정정 — 2026-10-20

실물 톱니 **14개** 확인. 연속6개 링크 동일 형상1→6의5간격48.1~48.3mm에서 피치9.62~9.66mm, 대표값9.64mm. 기존 실측1560counts/output rev 유지 →134.96mm/rev, 좌우 공통 초기 k=1687/19500≈0.08651282mm/count. 대표값은 측정 범위 중간값이며 수동 checkpoint 회귀 보정값이 아니다.

[정정 모델](../assets/logs/wifi_link/2026-10-20_track_geometry_14t_revision/geometry_model.json), [PC 검증](../assets/logs/wifi_link/2026-10-20_encoder_distance_14t_review/validation.json). 분석기의 기본 모델을 갱신했다. unittest36·실제 CLI3·입력 덮어쓰기/구버전 거부2 PASS. 원본 hash·수용 구간·delta count 불변. 새 모델 공중 전진 평균213.729923mm, 후진-244.052667mm 상당값이다.

윗쪽 직선 궤도 수동 이동100/150mm의 좌우 평균 환산은100.138590/150.532308mm다. 기존12톱니 가정이 공통 scale 차이를 대부분 설명한다. 공중 궤도 이동 비교이며 지상 차체 거리 정확도·슬립/전체 MVP PASS는 아니다. 이상적1m는 약11,559count이며 실제 주행 목표값/정밀도 보증이 아니다. 61링크×9.64=588.04mm는 피치선 둘레다. 기존579mm 보고의 측정 기준/독립성은 미확정이므로 두 값을 같은 기준의 정확한 측정으로 취급하지 않는다. 두께5mm·몸통 지름38mm를 진행량에 더하지 않는다.

기존12톱니/9.5mm 모델과 아래 진단·분석 결과는 **정정 전 이력**으로 보존한다. 현재 기본값에는 위 정정 모델을 사용한다. firmware/모터 출력·1560cpr 변경, 새 빌드/플래시/구동 없음.

다음은 현재 source/실행 이미지의 인수 기준점 대조·고정이다. 이후 전용 유실/timeout 정지·GM-1312 외부 온도·조건 충족 후 지상1m 순서로 진행한다. 이미 통과한 공중 count/부호 시험은 자동 반복하지 않는다. 현재 전원/분해·재조립 상태는 미확인이다.

## 사용자 궤도 측정과 초기 거리 계수 — 정정 전 이력 — 2026-10-20

| 항목 | 사용자 보고 / 초기 계산 | 근거 범위 |
| --- | --- | --- |
| 한 궤도 링크 수 | 61개 | 현재 사용자 보고. 반대편 개수는 별도 확인 전 |
| 링크 피치 p | 약9.5mm | 사용자 피치 보고. 측정 도구/축 중심 사진/오차 미제공 |
| 한 궤도 둘레 | 약579mm | 측정 경로(내측/외측/핀 중심선) 미제공 |
| 궤도 두께 | 약5mm | 참고 형상. 돌기 포함 여부 미제공 |
| 정합 계산 | 61×9.5=579.5mm | 보고 둘레와 차이0.5mm. 산술 정합이며 독립 측정 검증은 아님 |
| output 1회전 초기 이동량 | 12×9.5≈114mm | 기존 톱니12개, 직결·한 톱니당 한 피치·헛돎 없음 조건 |
| 좌우 초기 k | 114/1560≈0.0731mm/count | 같은 초기값으로 시작하며 실측 보정 전 |
| 이상적1m count | 약13,684count | 시작점 대비 delta 기준. 지상 실제1m 도달/정확도 보장은 아님 |

```text
s_left_mm  = (left_count_end  - left_count_start)  × k_left
s_right_mm = (right_count_end - right_count_start) × k_right
s_center_mm = (s_left_mm + s_right_mm) / 2
k_left_initial = k_right_initial = 12 × 9.5 / 1560
```

[사용자 측정·가정·계산 원본](../assets/logs/wifi_link/2026-10-20_track_pitch_initial_model/geometry_model.json). 주어진9.5mm 값의 산술 비율은19/260이지만 실제 정밀도가 그 자릿수까지 검증된 것은 아니다. 두께5mm를 더하거나 지름38mm의 원주로 대체하지 않는다. 좌우 유효 이동량/슬립·하중·장력 영향은 지상 실측으로 뒤에 보정한다.

기존 공중 로그에 이 초기값을 적용하면 전진 delta2567/2374는 encoder 상당 궤도 이동량187.59/173.48mm(평균180.54mm), 후진 delta-2925/-2717은-213.75/-198.55mm(평균-206.15mm)다. 공중 시험이므로 실제 차체 이동거리로 보고하지 않는다. firmware나 command vx를 실측 속도로 바꾼 결과가 아니다.

전원 분리/궤도 분리·재조립 완료는 아직 사용자 보고가 없으므로 측정 수치만으로 현재 구동 준비 상태를 확정하지 않는다. 이후 아래10/19의 피치 미확정 표현은 당시 이력이다.

## 윗쪽 직선 궤도 이동 참조 확인 — 2026-10-20 최신

사용자는 공중 상태의 궤도 윗쪽 평평한 구간에서 특정 링크 이동을 쟀다고 확인했다. [참조 근거](../assets/logs/wifi_link/2026-10-20_manual_upper_track_reference_confirmation/observations.json). 동일 점이 굽힘 구간을 통과하지 않고 직선 이동했다면 count당 궤도 이동량 진단에 사용할 수 있다. 초기모델은15cm/평균1740count를127.15mm로 추정해 사용자 궤도 이동 기준 약15.23% 작다. 실제 지상 차체 이동/슬립 정확도 판정과 구분한다. 후보k≈0.08621은 미적용이다.

다음은 핀 중심 대신 연속6개 동일 링크의 동일 반복 형상 첫째→여섯째 거리L로 p=L/5를 확인한다. 기존1560cpr 근거 유지, 실물 톱니 수/맞물림과 초기9.5mm 기준은 별도 확인 대상이다. 아래 “참조 미확인” 판정은 사용자 설명 전 이력이며 위 확인 조건이 최신이다.

## 수동 시험 참조 거리 정정 — 2026-10-20 최신

사용자는 수동 checkpoint 자료가 좌우 모터 직접 손회전 결과라고 정정했다. [방법 정정](../assets/logs/wifi_link/2026-10-20_manual_rotation_reference_clarification/observations.json).1/5/10/15cm가 궤도 선형 이동/휠 테두리 원호/계산값 중 무엇인지 확인 전까지 아래 실제 차체 거리 약15% 과소·등가 피치≈11.2mm·보정 후보 해석은 **보류**한다. 원자료와 가정 아래의 산술만 이력으로 보존하며 실제 지상 거리 오류 판정으로 사용하지 않는다. 기존1560cpr와 초기 기하 모델/firmware/분석기 계수는 변경하지 않았다. 다음은 측정 방법 설명 확인이다.

## 수동 양쪽 checkpoint 공통 계수 불일치 — 2026-10-20

[추가 회차](../assets/logs/wifi_link/2026-10-20_manual_both_distance_check_run02/observations.json):10cm 좌1153/우1162,15cm 좌1736/우1744. 초기19/260mm/count 평균 추정은84.59/127.15mm로 양쪽 공통 약15% 작다.15cm 차이8count≈0.46%, 돌아온 원점양쪽2count. 같은 nominal 위치 비교이며 동시 raw표본 여부/측정 정확도는 미확인이다.

15cm 기반 공통후보 k≈0.0862069, 전체checkpoint 진단fit≈0.0862677mm/count는 미적용. 피치만 원인일 때의 등가 p≈11.21mm를 실제 피치로 확정하지 않는다. 기존1560cpr는7/30 방향별50회전 실측1559.96~1560.02 근거를 유지한다.9.5mm가 핀 중심 간격인지 링크 끝 길이인지와 둘레 측정 기준을 우선 확인한다. archived 초기 model JSON과 이를 사용한 과거 결과는 그대로 보존한다.

## 수동 left_count 거리 진단 — 2026-10-20

사용자 한쪽(left_count) 수동 checkpoint는 [원자료/계산](../assets/logs/wifi_link/2026-10-20_manual_left_distance_check_run01/observations.json)에 보존했다. 실제10cm 위치1162count와15cm 위치1736count는 초기19/260mm/count로84.92mm/126.86mm여서 약15% 작게 추정된다. 15cm 기준 후보k≈0.0864, 전체checkpoint fit≈0.0865mm/count는 미적용 진단값이다. 돌아올 때 원점1count·동일위치1~8count 차이는 반복성의 참고이며 거리 정확도 PASS가 아니다.

이 관측은 초기 p≈9.5mm 기반 기하 모델에 불일치가 있음을 보인다. 피치만 원인이라 가정하면 p≈11.23mm 상당이지만 이를 실제 피치로 확정하지 않는다. 반대편 count/raw TEL/boot·tick/freshness·슬립/직진성/도구 자료가 아직 없어 원인 분리·좌우 보정은 보류한다. 기존 모델JSON과 그 hash를 사용한 과거 분석은 가정 이력으로 보존하며 변경하지 않는다. 다음은 수동100mm에서 양쪽 start/end raw TEL 동시 기록이다. ARM 기반 도구의 FAULT 거부와 구분되는 수동 진단이다.

## 관찰 v5 offline 구간 거리 분석 — 2026-10-20

구현은 [analyze_encoder_distance.py](../03_Firmware/tests/analyze_encoder_distance.py), 사용법/정책은 [검사 README](../03_Firmware/tests/README.md#관찰-v5-구간-거리-분석--2026-10-20)를 따른다. firmware나 browser 제어 경로를 변경하지 않는 PC 도구다.

ACK된 ARM+최초 유효 정지 sample → 같은 `(ESP boot_id, ARM seq)`의 연속 데이터 → ACK된 DISARM+CMD/PWM/CPS0 sample이 한 창이다. count는 문자열/int로 끝까지 유지하고 delta에19/260mm/count를 적용한다. 출력6자리 소수는 표시 형식이며 약9.5mm 측정값의 정밀도 보장은 아니다.

단절/counter gap/reset/tick wrap/무효 sample/FAULT·비정상 control stop/내용 충돌이 있으면 해당 창 전체를 제외하고 동일 ARM 자동 재개를 하지 않는다. 시작 ACK 후250ms 내 정지 기준점, STM/source·sample200ms, browser receive250ms는 보수적 offline 수용 정책이다. firmware 제한을 변경하지 않는다. 단절 뒤 새 ACK된 ARM/정지 기준점이 필요하다. source TEL 반복은 제거하며 browser ring 제거와 STM drop을 구분한다.

[검증](../assets/logs/wifi_link/2026-10-20_encoder_distance_analysis_review/validation.json): unittest34·실제 CLI3·입력 덮어쓰기/구버전 거부2 PASS. 공중 전진 평균180.536538mm/후진-206.150000mm 상당값을 계산했다. 후진 파일에 남은 이전 ARM은 ACK가 잘려 제외됐고 별도 전진 원본에서는 수용된다. 실제 차체 거리·슬립·속도 정확도와 인수 이미지/1m 판정은 별도다.

## 2026-10-19 거리 데이터 경로 대조

`TK-MVP-05-01` 감사 뒤 `TK-MVP-03-01`을 진행한다. 이번 단계는 거리 모델과 원시 count 전달의 준비이며 firmware 입력/빌드·실물 시험은 하지 않았다.

| 현재 저장본 | 확인한 사실 | 다음 설계의 영향 |
| --- | --- | --- |
| [encoder_speed.h](../03_Firmware/stm32_uart_mvp/Core/Inc/encoder_speed.h), [encoder_speed.c](../03_Firmware/stm32_uart_mvp/Core/Src/encoder_speed.c) | `int64_t accumulated_count`가 있고 init 때0, update에서 modular delta를 누적한다 | 새 누적기를 만들 필요 없음. 기존 계산을 재사용하고 전송 자료형/범위·snapshot을 설계 |
| [main.c](../03_Firmware/stm32_uart_mvp/Core/Src/main.c)의 `encoder_speed_log_process()` | 같은 sample 처리에서 TIM3/TIM5를 갱신. 차량 전진 양수 CPS는 TIM3 반전/TIM5 유지. 누적 total 진단은 raw 부호·`(long)` cast로 USART2 출력 | 생산 경로로 count를 내보낼 때 차량 부호·자료형/포화·sample 시각을 명시. 기존 USART2 진단을 무선 실측 결과로 간주하지 않음 |
| [uart_mvp_protocol.h](../03_Firmware/stm32_uart_mvp/Core/Inc/uart_mvp_protocol.h), [uart_mvp_protocol.c](../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c) | 현재 setter/TEL은 좌우 CPS만 전달하고 누적 count는 없음 | STM TEL→ESP parser/JSON→브라우저/저장 로그의 최소 확장이 필요. 새 배터리 ADC/IMU 기능은 필요 없음 |

거리 모델의 기준 초안:

```text
N_left_vehicle  = -TIM3.accumulated_count
N_right_vehicle = +TIM5.accumulated_count
delta_N_side    = N_side(end) - N_side(start)
k_side_mm_per_count = effective_track_travel_per_output_rev_mm / 1560
s_side_mm       = delta_N_side * k_side_mm_per_count
s_center_mm     = (s_left_mm + s_right_mm) / 2
```

위 부호는 현재 생산 CPS와 같은 차량 기준이다. 거리 계수는 좌우를 구분해 관리하고, 수치가 없으면 임의 바퀴 외경/명령 속도로 채우지 않는다. `s_center`는 encoder 기반 추정이며 실제 차체 거리의 기준값이 아니다. 회전/슬립을 포함한 정밀 궤도 모델·IMU 융합은 후속이다.

- **확정:** 1560 counts/output rev, 현재 A=left/TIM3·B=right/TIM5, 전진 양수 부호, 기존 누적 상태의 존재.
- **기하 자료 확인:** 사용자 모델 보고는 구동휠 톱니12개와 **지름38 mm**다. 반지름38 mm가 아니다. 첨부 스케치의 R19/R22를 피치원 반지름으로 확정하지 않았으며 궤도 피치는 미확정이다. 직결·한 톱니당 한 피치 맞물림 조건에서 초기 계수 후보는 `12 × pitch_mm / 1560`이고 실제 거리 검증을 대신하지 않는다.
- **미확정:** 실제 output 1회전의 궤도 이동량/좌우 계수, 생산 TEL로 count를 전달할 자료형·메시지 길이/호환성·sample 시각과 reset 구분 계약. 궤도 피치 자료 또는 링크 연결 핀 중심 간격을 추가 확인한다. 피치 미확정은 원시 누적 count 전송 설계를 막지 않는다.
- **구간 원칙:** count를 ARM/DISARM마다 임의 리셋하는 설계를 먼저 넣지 않는다. 측정 구간의 시작/끝 기준과 MCU reset을 구분해 기록하는 방법을 데이터 계약에서 정한다. reset을 가로지른 회차를 연속 이동량으로 합산하지 않는다.
- **다음 작업:** `TK-MVP-03-01`에서 필요한 상수/측정 항목과 기록 기준을 마감하고, `TK-MVP-03-02`에서 같은 encoder 갱신 시각의 좌우 count/CPS snapshot·TEL 길이/파서·관측 스크립트 경로를 설계한다. 정확한 사용자 입력 블록은 그 계약과 변경 영향 검토 뒤 제공한다.

### 중국어 원자료 확인 — 2026-10-19

- 로컬 WHEELTEC `履带车产品安装手册`(고급형 궤도차 설치 설명서, A001, 2023-09-05)의3쪽 전체 텍스트와1·3쪽 도해를 확인했다. 1쪽은 궤도2개·구동휠2개 등 부품 목록, 3쪽은 모터/구동휠 고정과 궤도 연결핀 탈착·장착 설명이다. **이 설명서에는 궤도 피치·핀 중심 간격 치수가 없다.** 전체 WHEELTEC 자료에 없다는 결론은 아니다.
- 원본 위치: `C:/Users/eyh12/Desktop/drive-download-20260814T153501Z-1-001/High_Config_Version/R3_High_Config_Version_Tracked_Robot_Car/R3_High_Config_Version_Tracked_Vehicle_Chassis_Installation_Video/High_Config_Tracked_Vehicle_Installation_Manual.pdf`. SHA256: `a9232b273fc77cdccf3d582c35eb39bc9aaae90fa0a8d9850a157ff28f0ac4f3`.
- 같은 묶음의 `High_Config_Tracked_Vehicle_-3D_Model.stp`는 바탕화면 `高配履带车-3D模型.stp`와 SHA256이 일치하며 STEP 길이 단위는 mm다. 모델에서 링크 피치를 측정한 결과는 아직 없다. 과거 문서의 `Desktop/turtle_CAD` 경로는 현재 존재하지 않아 전체 원자료 대신 확인 가능한 위 선별 묶음을 조회했다.

### 피치 확인 대기 중 가능한 전송 설계 — 2026-10-19

사용자는 궤도 피치 확인을 집에서 이어가기로 했다. 기하 상수 확정 전에도 원시 count 전송 설계를 병행한다. 다음은 저장 소스에 근거한 초안이며 firmware 입력 지시나 확정된 wire 계약은 아니다.

| 항목 | 준비 방향 |
| --- | --- |
| 좌우 누적 count | 기존 `int64_t accumulated_count` 재사용. 왼쪽 TIM3 반전·오른쪽 TIM5 유지. CPS와 같은 encoder 갱신 결과로 전달 |
| 측정 시각 | encoder 갱신의 STM tick을 함께 전달. 기존 TEL 생성 `t_ms`와 구분 |
| UART 표현 | 부호 있는10진 정수. ESP에 범위·중복/형식 검사를 하는64비트 parser 필요 |
| JSON/저장 | count는10진 문자열로 보존해 JavaScript Number의 안전 정수 범위를 넘는 값의 손실을 방지. 차분은 BigInt 등 정확한 정수 경로에서 계산하고 원시 로그는 문자열 유지 |
| 유효성·reset | 초기 미갱신과 측정 구간 시작/끝을 구분. 기존 JSON `boot_id`는 ESP 식별값이며 STM reset 증명이 아니다. STM reset/시각 wrap/관측 단절의 구간 무효화 방법은 코드 입력 전 마감 |
| 거리 환산 | `pitch_mm`와 실제 거리 검증은 뒤에 연결. 피치가 없어도 count를 수집할 수 있음 |

변경 영향 확인:

- ESP `stm_parse_tel()`은 현재 필드 수14개를 강제한다. STM 필드만 추가하면 TEL 수신 판정이 실패하므로 STM 송신·ESP 구조체/parser/JSON·브라우저 검증/관찰 로그를 함께 검토해야 한다.
- STM TX와 ESP UART line 버퍼는 각각384 bytes다. 기존 parser 범위의 보수적 필드 폭과 좌우 int64 count·sample tick을 가정한 ASCII 길이 계산은 NUL 포함366 bytes다. 유효성/reset 식별 필드는 아직 포함하지 않았으므로 최종 메시지·버퍼 크기와115200 baud 전송 시간을 다시 계산해야 한다. 실제 프레임이나 runtime 측정 결과가 아니다.
- 기존 STM setter는 CPS 두 값뿐이고 main loop에서 호출된다. 새 snapshot의 count/CPS/시각 일관성과 기존 정지 판정에 쓰는 CPS 갱신 보존을 확인한다. 다음은 유효성/reset 계약 마감 → 사용자 입력용 완결 코드 블록 → 저장본 PC 검사 → 사용자 빌드/플래시 순서다.

### 누적 count 계약 확정 — 2026-10-19

앞의 초안을 STM 입력 후보 기준으로 마감했다. 기하 계수는 집에서 피치를 확인한 뒤 정하며 원시 데이터 구현과 분리한다. **계약 확정/후보 PC 확인은 저장본 구현 완료가 아니다.**

| TEL 추가 필드 | STM 자료형 / UART | ESP JSON 계약 |
| --- | --- | --- |
| `encoder_valid` | bool, `0` 또는 `1` | boolean. 같은 encoder 갱신의 count/CPS/시각을 사용할 수 있는지 |
| `encoder_t_ms` | uint32,10진수 | uint32 number. encoder sample 시각이며 TEL 생성 `stm_t_ms`와 다름 |
| `left_count`, `right_count` | int64,부호 있는10진수 | 원시10진 문자열. Number로 먼저 변환하지 않음 |
| `encoder_arm_valid` | bool, `0` 또는 `1` | boolean. 샘플이 성공한 ARM 구간에 속하는지 |
| `encoder_arm_seq` | uint32,10진수 | uint32 number. `0`도 유효할 수 있어 유효성 flag로 구분 |

- 기존14개+추가6개=TEL20개 필드다. ESP에서 정확한 key 수/중복·숫자 범위/flag 형식과 JSON 버퍼를 검토한다. `encoder_valid=false`/`encoder_arm_valid=false`는 정상 초기 상태이며 **그 자체로 제어 TEL을 거부하거나 ARM을 막는 조건이 아니다.** 잘못된 구조/숫자와 정상적인 측정 무효 상태를 구분한다.
- 구간 기준은 `(현재 ESP boot_id, 성공 ACK된 ARM UART seq)`다. 현재 ESP 단일 allocator는 같은 부팅에서 seq를 재사용하지 않으며 소진 시 거부하고, ARM을 자동 재전송하지 않는다. STM은 ARM 거부 시 구간을 바꾸지 않는다. 다른 UART writer/seq 재사용을 도입하면 이 계약도 다시 검토해야 한다.
- STM init 때 ARM 기준을 지우고 새 ARM 성공 때 이전 sample을 무효화한다. 다음 encoder 갱신에 새 ARM 기준을 복사한다. DISARM 후 같은 기준을 유지해 정지 후 count를 끝점으로 읽을 수 있으며 원래 누적기는 ARM/DISARM으로 리셋하지 않는다.
- 브라우저 거리 창은 sample/ARM flag가 모두 유효하고 ARM 결과 seq와 일치하며 source TEL이 fresh한 경우 시작한다. ESP boot/ARM 기준 변경·무효 sample·통신 단절·FAULT·sample tick 역행/wrap이 끼면 그 창을 종료한다. 단절 후 자동으로 이어 붙이지 않고 새 시작점을 명시한다. 후진에 따른 count 감소는 정상이다. 장시간 tick wrap의 연속 거리 지원은 이번1 m 창에 넣지 않는다.
- `sample_ms`는 양 encoder를 함께 갱신한 main-loop 시각이다. CPS setter와 count snapshot을 같은 함수에서 갱신하고 RX interrupt는 기존 byte enqueue 역할을 유지한다. 측정 flag가 false여도 CPS는 기존 제어/정지 판정으로 계속 전달한다.
- UART 보수적 필드 폭 상한은 LF 포함428 bytes/NUL 포함429 bytes,115200/8N1 이론 전송37.16 ms 이하다. STM TX/ESP line은512 bytes가 필요하다. 이는 허용 숫자/문자 폭의 길이 계산이며 실제 최대 실행 지연/주기 검증은 아니다. STM 모터/timeout 설정과 STM→ESP100 ms TEL 주기는 그대로다.
- [후보 PC 검사 결과](../assets/logs/wifi_link/2026-10-19_encoder_count_candidate_review/stm_candidate.json): 실제 후보 C와 main의 publish 블록을 native TCC/HAL 모의로 실행해14개 PASS. 초기/ARM0/재ARM/거부ARM/DISARM/reset·좌우 부호·int64 끝값·완전한20필드/LF와 기존15%/20%/trim/timeout/E-stop 회귀를 포함한다. 실제 두 보드 저장본/링크·타이밍/주행 PASS는 아니다.

### STM 누적 count 입력 묶음 — 2026-10-19

**10/20 최신:** 오타 수정 후 [실제 STM 저장본 native14 PASS](../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/stm_saved_after_typo_fix.json)·사용자 build/Run 성공 보고를 확인했다. 초기 FAIL과 메모리 수정 후보는 과거 검토 이력이다. 아래 STM 입력 블록은 보존하고 다음 ESP 입력은 뒤의10/20 절을 따른다.

상태: **STM 입력 완료 / 저장본 native14 PASS / 사용자 build·Run 보고**. 아래는10/19 제공한 입력 안내의 보존본이다. 실제 ESP 입력/연동은 뒤의10/20 절에서 이어간다.

목적은 기존 encoder 갱신의 차량 기준 count/CPS/시각을 같은 main-loop 샘플로 보관하고 확장 TEL로 내보내는 것이다. 현재 ESP14필드 parser는 새 TEL20필드를 거부하므로 **지금은 저장까지 진행하고 두 보드 빌드/플래시는 ESP 변경과 저장본 PC 검사가 끝난 뒤** 진행한다.

- 부팅: sample/ARM 유효성 false. 첫 encoder 갱신 뒤 sample은 유효하지만 ARM 구간은 아직 없음.
- ARM 성공: UART seq를 구간 기준으로 보관하고 이전 sample을 무효화. 다음 encoder 갱신부터 새 ARM seq와 count를 연결. ARM이 count를0으로 리셋하지 않음.
- DISARM/timeout/FAULT: 제어의 기존 정지 동작을 유지하고 마지막 ARM 기준/count는 정지 후 샘플에도 보존. FAULT 또는 관측 단절이 낀 구간은 거리 수용에서 제외.
- STM 재시작: sample/ARM 유효성 초기화. 새 ARM은 현재 ESP 단일 UART allocator가 재사용하지 않는 seq를 받음. 거리 구간은 `(ESP boot_id, encoder_arm_seq)`가 같고 ACK된 ARM seq와 일치해야 한다. 이 값은 전역 STM boot ID나 보안 nonce가 아니다.
- 원시 count가 감소하는 것은 후진일 수 있으므로 reset 판정으로 사용하지 않음. 측정 시각 역행/wrap 또는 통신 단절은 구간을 종료하고 사용자 새 기준점부터 측정. 원시 로그는 보존.
- TIM3 raw count가 INT64_MIN이면 부호 반전할 수 없어 sample.valid=false로 전달. CPS는 기존 제어 경로에 계속 갱신. 이 방어는 기존 int64 누적기 자체의 영구 overflow 문제를 해결하지 않음.

아래 번호 순서로 교체한다. 같은 이름의 호출부 대신 **선언 / 함수 정의 / switch case**를 구분한다. 함수/case는 아래 완결 블록 전체를 사용한다.

**1. uart_mvp_protocol.h 전체** — `Inc/uart_mvp_protocol.h`

기존 범위: `#ifndef UART_MVP_PROTOCOL_H`부터 해당 블록 끝까지.

```c
#ifndef UART_MVP_PROTOCOL_H
#define UART_MVP_PROTOCOL_H

#include "main.h"
#include <stdbool.h>
#include <stdint.h>

void uart_mvp_init(UART_HandleTypeDef *huart);
void uart_mvp_start_rx(void);
void uart_mvp_on_rx_complete(UART_HandleTypeDef *huart);
void uart_mvp_on_uart_error(UART_HandleTypeDef *huart);
void uart_mvp_set_encoder_sample(
    int32_t left_cps,
    int32_t right_cps,
    int64_t left_count,
    int64_t right_count,
    uint32_t sample_ms,
    bool valid
);
void uart_mvp_process(void);

#endif // UART_MVP_PROTOCOL_H
```

**2. 표준 헤더 두 줄** — `Src/uart_mvp_protocol.c`

기존 범위: `#include <stdarg.h>`부터 해당 블록 끝까지.

```c
#include <inttypes.h>
#include <stdarg.h>
#include <stdio.h>
```

**3. STM TX 버퍼 정의** — `Src/uart_mvp_protocol.c`

기존 범위: `#define UART_TX_BUFFER_SIZE             384u`부터 해당 블록 끝까지.

```c
#define UART_TX_BUFFER_SIZE             512u
```

**4. CPS 상태 두 줄과 sample 상태** — `Src/uart_mvp_protocol.c`

기존 범위: `static int32_t s_left_cps;`부터 해당 블록 끝까지.

```c
static int32_t s_left_cps;
static int32_t s_right_cps;

typedef struct {
    int64_t left_count;
    int64_t right_count;
    uint32_t sample_ms;
    uint32_t arm_seq;
    bool valid;
    bool arm_valid;
} encoder_sample_t;

static encoder_sample_t s_encoder_sample;
static uint32_t s_encoder_arm_seq;
static bool s_encoder_arm_valid;
```

**5. send_tel() 전체** — `Src/uart_mvp_protocol.c`

기존 범위: `static void send_tel(void){`부터 해당 블록 끝까지.

```c
static void send_tel(void){
    uint32_t now_ms = HAL_GetTick();
    motor_output_applied_t applied =
        motor_output_get_applied();

    uart_sendf("TEL,t_ms=%lu,state=%s,reason=%s,"
               "command_age_ms=%lu,last_seq=%lu,"
               "vx_mmps=%ld,w_mradps=%ld,"
               "left_pwm=%ld,right_pwm=%ld,"
               "left_cps=%ld,right_cps=%ld,"
               "encoder_valid=%u,encoder_t_ms=%lu,"
               "left_count=%" PRId64 ",right_count=%" PRId64 ","
               "encoder_arm_valid=%u,encoder_arm_seq=%lu,"
               "batt_mv=0,drop=%lu,err=%lu\n",
                (unsigned long)now_ms,
                state_name(s_state),
                reason_name(s_reason),
                (unsigned long)command_age_ms(now_ms),
                (unsigned long)s_last_seq,
                (long)s_vx_mmps,
                (long)s_w_mradps,
                (long)applied.left_signed_permille,
                (long)applied.right_signed_permille,
                (long)s_left_cps,
                (long)s_right_cps,
                s_encoder_sample.valid ? 1U : 0U,
                (unsigned long)s_encoder_sample.sample_ms,
                s_encoder_sample.left_count,
                s_encoder_sample.right_count,
                s_encoder_sample.arm_valid ? 1U : 0U,
                (unsigned long)s_encoder_sample.arm_seq,
                (unsigned long)ring_buffer_dropped(&s_rx_rb),
                (unsigned long)s_error_count);
}
```

**6. ARM case 전체: 다음 ESTOP_RESET case 직전까지** — `Src/uart_mvp_protocol.c`

기존 범위: `        case UART_FRAME_TYPE_ARM:`부터 해당 블록 끝까지.

```c
        case UART_FRAME_TYPE_ARM:
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
            s_delayed_disarm_ack.zero_cmd_seen = 0U;
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
            s_cmd_ack_drop_zero_count = 0U;
#endif
            motor_output_stop_all();

            s_vx_mmps = 0;
            s_w_mradps = 0;
            s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
            s_last_cmd_ms = HAL_GetTick();
            s_state = ROBOT_ARMED;
            s_reason = ROBOT_REASON_NONE;
            s_last_seq = frame.seq;
            /* New measurement interval; wait for a post-ARM sample. */
            s_encoder_arm_seq = frame.seq;
            s_encoder_arm_valid = true;
            s_encoder_sample.valid = false;
            s_encoder_sample.arm_valid = false;
            s_encoder_sample.arm_seq = 0U;
            send_ack(frame.seq, "ARM");
            return;
```

**7. uart_mvp_init() 전체** — `Src/uart_mvp_protocol.c`

기존 범위: `void uart_mvp_init(UART_HandleTypeDef *huart){`부터 해당 블록 끝까지.

```c
void uart_mvp_init(UART_HandleTypeDef *huart){
    s_uart = huart;
    s_rx_byte = 0u;

    ring_buffer_init(&s_rx_rb);

    s_line_len = 0u;
    s_line_overflow = 0u;
    s_rx_desync_pending = 0u;
    s_rx_line_mode = UART_RX_COLLECT;

    s_state = ROBOT_DISARMED;
    s_reason = ROBOT_REASON_BOOT;
    s_has_accepted_cmd = 0U;
    s_last_accepted_cmd_ms = 0U;
    s_estop_latched = 0U;
    s_last_seq = 0;
    s_stale_disarm_ack_sent = 0u;
    s_duplicate_disarm_ack_seq_sent = 0u;
    s_trailing_comma_disarm_ack_sent = 0u;
    s_overflow_disarm_ack_seq_sent = 0u;
    s_partial_frame_name_disarm_ack_sent = 0u;
    s_embedded_cr_disarm_ack_sent = 0u;
    s_control_byte_disarm_ack_sent = 0u;
    s_overlong_disarm_ack_sent = 0u;
    s_wrong_disarm_ack_type_sent = 0u;
    s_stale_pong_sent = 0u;
#if UART_MVP_DELAY_DISARM_ACK_ONCE_TEST_ENABLED
    s_delayed_disarm_ack = (delayed_disarm_ack_t){0};
#endif
#if UART_MVP_DROP_CMD_ACK_ONCE_TEST_ENABLED
    s_cmd_ack_drop_used = 0U;
    s_cmd_ack_drop_zero_count = 0U;
#endif
    s_last_tel_ms = 0u;
    s_error_count = 0u;
    s_left_cps = 0;
    s_right_cps = 0;
    s_encoder_sample = (encoder_sample_t){0};
    s_encoder_arm_seq = 0U;
    s_encoder_arm_valid = false;

    s_vx_mmps = 0;
    s_w_mradps = 0;
    s_cmd_timeout_ms = CMD_TIMEOUT_DEFAULT_MS;
    s_last_cmd_ms = 0u;
    (void)estop_enforce_latch();
}
```

**8. 기존 uart_mvp_set_encoder_cps() 전체** — `Src/uart_mvp_protocol.c`

기존 범위: `void uart_mvp_set_encoder_cps(`부터 해당 블록 끝까지.

```c
void uart_mvp_set_encoder_sample(
    int32_t left_cps,
    int32_t right_cps,
    int64_t left_count,
    int64_t right_count,
    uint32_t sample_ms,
    bool valid
){
    /* Both paths run in the main loop, not in the UART RX interrupt. */
    s_left_cps = left_cps;
    s_right_cps = right_cps;

    s_encoder_sample = (encoder_sample_t){
        .left_count = valid ? left_count : 0,
        .right_count = valid ? right_count : 0,
        .sample_ms = sample_ms,
        .arm_seq = s_encoder_arm_valid ? s_encoder_arm_seq : 0U,
        .valid = valid,
        .arm_valid = s_encoder_arm_valid
    };
}
```

**9. encoder_speed_log_process() 전체** — `Src/main.c`

기존 범위: `static void encoder_speed_log_process(void){`부터 해당 블록 끝까지.

```c
static void encoder_speed_log_process(void){
  char tx[256];
  uint32_t now_ms;
  uint32_t raw3_count;
  uint32_t raw5_count;
  bool tim3_updated;
  bool tim5_updated;
  int32_t tim3_millirpm;
  int32_t tim5_millirpm;
  int len;

  now_ms = HAL_GetTick();

  raw3_count = __HAL_TIM_GET_COUNTER(&htim3);
  raw5_count = __HAL_TIM_GET_COUNTER(&htim5);

  tim3_updated = encoder_speed_update(
    &s_encoder_tim3,
    raw3_count,
    now_ms
  );

  tim5_updated = encoder_speed_update(
    &s_encoder_tim5,
    raw5_count,
    now_ms
  );

  if (!tim3_updated || !tim5_updated){
      return;
  }

  if (
    !encoder_speed_cps_to_millirpm(
      s_encoder_tim3.counts_per_second,
      ENCODER_COUNTS_PER_OUTPUT_REV,
      &tim3_millirpm
    ) ||
    !encoder_speed_cps_to_millirpm(
      s_encoder_tim5.counts_per_second,
      ENCODER_COUNTS_PER_OUTPUT_REV,
      &tim5_millirpm
    )
  ){
    Error_Handler();
  }

  /* Vehicle mapping corrected and hand-checked on 2026-09-26.
   * Motor A/left: JENC_1 -> TIM3; invert raw sign for forward-positive CPS.
   * Motor B/right: JENC_2 -> TIM5; keep raw sign for forward-positive CPS.
  */
  /* Vehicle-forward count uses the same sign as production CPS. */
  const bool encoder_sample_valid =
    s_encoder_tim3.accumulated_count != INT64_MIN;

  uart_mvp_set_encoder_sample(
    encoder_cps_to_i32(-s_encoder_tim3.counts_per_second),
    encoder_cps_to_i32(s_encoder_tim5.counts_per_second),
    encoder_sample_valid ? -s_encoder_tim3.accumulated_count : 0,
    s_encoder_tim5.accumulated_count,
    now_ms,
    encoder_sample_valid
  );

  len = snprintf(
    tx,
    sizeof(tx),
    "ENC3,raw=%lu,delta=%ld,total=%ld,cps=%ld,mrpm=%ld,dir=%s;"
    "ENC5,raw=%lu,delta=%ld,total=%ld,cps=%ld,mrpm=%ld,dir=%s\r\n",
    (unsigned long)raw3_count,
    (long)s_encoder_tim3.delta_count,
    (long)s_encoder_tim3.accumulated_count,
    (long)s_encoder_tim3.counts_per_second,
    (long)tim3_millirpm,
    encoder_delta_direction(s_encoder_tim3.delta_count),
    (unsigned long)raw5_count,
    (long)s_encoder_tim5.delta_count,
    (long)s_encoder_tim5.accumulated_count,
    (long)s_encoder_tim5.counts_per_second,
    (long)tim5_millirpm,
    encoder_delta_direction(s_encoder_tim5.delta_count)
  );

  if ((len > 0) && (len < (int)sizeof(tx))){
    (void)HAL_UART_Transmit(
      &huart2,
      (uint8_t *)tx,
      (uint16_t)len,
      50U
    );
  }
}
```

입력 후 확인 기준: 이전 setter 이름0건, 새 setter 선언/정의/호출 각1건, 새 TEL20필드·개행/버퍼 여유, 초기/ARM後/DISARM/reset 구간과 실제 제어 회귀 PC 검사. ESP의 i64 parser·JSON 문자열·유효성/ACK 연계·관찰 로그는 다음 입력 묶음이다. native HAL 모의 결과는 보드 실행 근거가 아니다.

### 2026-10-20 STM 저장본 확인과 ESP 후보 검사

사용자가 오타4곳을 수정하고 STM build/Run 성공을 보고했다. [실제 STM 저장본 native14 PASS](../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/stm_saved_after_typo_fix.json)를 확인했다. 앞의10/20 초기 FAIL/입력 대기 표현은 수정 전 이력이다. 새20필드의 실물 ESP 수신/브라우저 도달은 아직 확인하지 않았다.

[ESP 후보 검사](../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/esp_count_candidate.json): 실제 parser/JSON C native9, 신규 PAGE/관찰 스크립트8, 기존 PAGE46개가 통과했다. [기존 제어 회귀](../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/esp_control_candidate.json)는 PAGE67·기존mode1 C42·mode1/0 adapter 각6·C 문자열 초기화1·오류 주입 탐지2개다. 겹치는 검사가 있어 합계를 독립 사례 수로 해석하지 않는다. JSON 허용 폭 stress 벡터는775 bytes로 기존1024-byte 버퍼에 들어갔다. ESP 입력 소스는 아직 변경하지 않았다.

확인 범위는 signed64 끝값·2^53 초과 보존·중복/누락/초과/flag 검사, ESP_ONLY null/초기 flag=false/기존 freshness, count를 문자열로 표시·저장하면서 제어 동작을 유지하는 것이다. native 모의는 실제 UART 수신 주기·전기/부하·주행 근거가 아니다.

새 관찰 파일은 [console_encoder_observe.js v5](../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/console_encoder_observe.js)다. 기존 v4 원본을 보존하고 새 파일에 count/측정 시각/ARM 기준을 추가했다. 설치/보고가 명령을 보내지 않고 기존 stopLocal 호출을 유지하며2^53 초과 문자열을 보고서에 보존하는 것을 PC에서 확인했다. **실물 연동 후 DISARMED/IDLE와 새 TEL 수신을 확인한 다음 설치**하며 이번에는 아직 설치/주행을 지시하지 않았다.

### ESP 누적 count 입력 묶음 — 2026-10-20

**입력 후 최신 검토:** 수정3곳 반영 후 [실제 저장본 count/PAGE](../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/esp_count_saved.json)와 [제어 회귀](../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/esp_control_saved.json)가 통과했다. 초기 FAIL/임시 수정 후보는 이전 이력이다. 사용자 ESP build/flash/monitor 후 boot/handshake는 성공했으나 STM nano printf가 count를 `ld`로 보내 TEL 수신은 실패했다. [STM 수정 완결 블록](../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/stm_nano_format_typing.md)을 먼저 적용하고 저장본/target를 재검증한다.

상태: **ESP 입력·사용자 build/flash 보고 / PC PASS / STM nano 출력 수정 대기**. 아래6개 블록은 입력 안내의 보존본이다. STM은 사용자 build/Run 보고와 native14 PASS, ESP는 실제 저장본 count/PAGE·제어 PC PASS이며 실제20필드 수신은 아직 미확인이다.

- 데이터 흐름: STM TEL20필드 → 범위/중복/flag 검사 → lock 안의 snapshot → JSON → PAGE 검증/표시. count는 UART에서 int64, JSON/관찰 로그에서10진 문자열을 유지한다.
- 정상 초기 flag=false는 TEL 형식 오류가 아니다. ARM/정지의 기존 CPS/PWM/ticket/ACK·freshness 조건과 모터 제한은 그대로다.
- 잘못된 key/범위/flag/중복 또는14필드 TEL은 거부하며 마지막 정상 snapshot을 유지한다. 기존 TEL age에 따라 제어가 정지한다. flag가 false라는 이유만으로 정상 TEL을 거부하지 않는다.
- 원시 count/ARM seq가 같은 snapshot으로 브라우저에 전달된다. 거리 창의 시작/끝·reset/단절 구분은 앞의 계약을 따르며 이 입력 묶음은 자동 거리 보정이나 주행을 추가하지 않는다.
- 입력·저장 후 Codex가 실제 ESP 저장본을 검사한다. 그 검사가 끝난 뒤 사용자가 ESP build/flash/Run을 수행하며 새 동작 시험은 별도 안내한다.

**1. stm_telemetry_t typedef 전체**

기존 블록 시작: `typedef struct {`. 함수/typedef는 끝까지 교체한다.

```c
typedef struct {
    uint32_t t_ms;
    char state[16];
    char reason[32];
    uint32_t command_age_ms;
    uint32_t last_seq;
    int32_t vx_mmps;
    int32_t w_mradps;
    int32_t left_pwm;
    int32_t right_pwm;
    int32_t left_cps;
    int32_t right_cps;
    bool encoder_valid;
    uint32_t encoder_t_ms;
    int64_t left_count;
    int64_t right_count;
    bool encoder_arm_valid;
    uint32_t encoder_arm_seq;
    uint32_t batt_mv;
    uint32_t drop;
    uint32_t err;

    uint64_t rx_ms;
    bool valid;
} stm_telemetry_t;
```

**2. STM_UART_LINE_SIZE 정의 한 줄**

기존 블록 시작: `#define STM_UART_LINE_SIZE 384U`. 함수/typedef는 끝까지 교체한다.

```c
#define STM_UART_LINE_SIZE 512U
```

**3. 기존 stm_parse_text_field 함수 전체를 아래 두 함수로 교체**

기존 블록 시작: `static bool stm_parse_text_field(`. 함수/typedef는 끝까지 교체한다.

```c
static bool stm_parse_i64_field(
    const char *line, const char *key, int64_t *out)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL) {
        return false;
    }

    const bool negative = *pos == '-';
    if (negative) {
        ++pos;
    }
    if (*pos < '0' || *pos > '9') {
        return false;
    }

    const uint64_t limit = negative
        ? (uint64_t)INT64_MAX + 1U : (uint64_t)INT64_MAX;
    uint64_t magnitude = 0U;
    while (*pos >= '0' && *pos <= '9') {
        const uint64_t digit = (uint64_t)(*pos - '0');
        if (magnitude > (limit - digit) / 10U) {
            return false;
        }
        magnitude = magnitude * 10U + digit;
        ++pos;
    }
    if (*pos != ',' && *pos != '\0') {
        return false;
    }

    *out = negative
        ? (magnitude == (uint64_t)INT64_MAX + 1U
            ? INT64_MIN : -(int64_t)magnitude)
        : (int64_t)magnitude;
    return true;
}

static bool stm_parse_text_field(
    const char *line, const char *key,
    char *out, size_t capacity)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL) {
        return false;
    }

    const size_t length = strcspn(pos, ",");
    if (length == 0U || length >= capacity) {
        return false;
    }

    for (size_t i = 0U; i < length; ++i) {
        const char c = pos[i];
        if (!((c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || c == '_')) {
            return false;
        }
    }

    memcpy(out, pos, length);
    out[length] = '\0';
    return true;
}
```

**4. stm_parse_tel 함수 전체**

기존 블록 시작: `static bool stm_parse_tel(`. 함수/typedef는 끝까지 교체한다.

```c
static bool stm_parse_tel(
    const char *line, stm_telemetry_t *out)
{
    if (line == NULL || out == NULL ||
        strncmp(line, "TEL,", 4) != 0) {
        return false;
    }

    const size_t length = strlen(line);
    if (line[length - 1U] == ',' ||
        strstr(line, ",,") != NULL) {
        return false;
    }

    /* 확장 TEL 계약은 20개 필드다. */
    size_t field_count = 0U;
    for (const char *pos = line; *pos != '\0'; ++pos) {
        if (*pos == ',') {
            ++field_count;
        }
    }
    if (field_count != 20U) {
        return false;
    }

    uint32_t encoder_valid;
    uint32_t encoder_arm_valid;
    const bool fields_ok =
        stm_parse_u32_field(line, "t_ms=", &out->t_ms) &&
        stm_parse_text_field(
            line, "state=", out->state, sizeof(out->state)) &&
        stm_parse_text_field(
            line, "reason=", out->reason, sizeof(out->reason)) &&
        stm_parse_u32_field(
            line, "command_age_ms=", &out->command_age_ms) &&
        stm_parse_u32_field(line, "last_seq=", &out->last_seq) &&
        stm_parse_i32_field(line, "vx_mmps=", &out->vx_mmps) &&
        stm_parse_i32_field(line, "w_mradps=", &out->w_mradps) &&
        stm_parse_i32_field(line, "left_pwm=", &out->left_pwm) &&
        stm_parse_i32_field(line, "right_pwm=", &out->right_pwm) &&
        stm_parse_i32_field(line, "left_cps=", &out->left_cps) &&
        stm_parse_i32_field(line, "right_cps=", &out->right_cps) &&
        stm_parse_u32_field(line, "encoder_valid=", &encoder_valid) &&
        stm_parse_u32_field(line, "encoder_t_ms=", &out->encoder_t_ms) &&
        stm_parse_i64_field(line, "left_count=", &out->left_count) &&
        stm_parse_i64_field(line, "right_count=", &out->right_count) &&
        stm_parse_u32_field(line, "encoder_arm_valid=", &encoder_arm_valid) &&
        stm_parse_u32_field(line, "encoder_arm_seq=", &out->encoder_arm_seq) &&
        stm_parse_u32_field(line, "batt_mv=", &out->batt_mv) &&
        stm_parse_u32_field(line, "drop=", &out->drop) &&
        stm_parse_u32_field(line, "err=", &out->err);

    if (!fields_ok || encoder_valid > 1U || encoder_arm_valid > 1U) {
        return false;
    }

    out->encoder_valid = encoder_valid != 0U;
    out->encoder_arm_valid = encoder_arm_valid != 0U;

    const bool state_ok =
        strcmp(out->state, "DISARMED") == 0 ||
        strcmp(out->state, "ARMED") == 0 ||
        strcmp(out->state, "FAULT") == 0;

    return state_ok &&
        out->left_pwm >= -1000 && out->left_pwm <= 1000 &&
        out->right_pwm >= -1000 && out->right_pwm <= 1000;
}
```

**5. status_json 함수 전체**

기존 블록 시작: `static int status_json(char *json, size_t capacity)`. 함수/typedef는 끝까지 교체한다.

```c
static int status_json(char *json, size_t capacity)
{
    stm_telemetry_t tel;
    uint32_t tel_count;
    const char *startup_state;

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    tel = s_stm_telemetry;
    tel_count = s_stm_tel_count;
    startup_state = s_stm_startup_status;
    xSemaphoreGive(s_stm_lock);

    /* Snapshot을 복사한 뒤 시각을 읽어 rx_ms보다 앞서지 않게 한다. */
    const uint64_t uptime_ms = (uint64_t)esp_timer_get_time() / 1000U;
    const uint64_t age_ms = tel.valid ? uptime_ms - tel.rx_ms : 0U;
    const bool fresh = tel.valid && age_ms <= STM_TEL_STALE_MS;
    int length;

    if (!tel.valid) {
        length = snprintf(
            json, capacity,
            "{\"source\":\"ESP_ONLY\",\"mode\":\"%s\","
            "\"boot_id\":%" PRIu32 ",\"uptime_ms\":%" PRIu64 ","
            "\"free_heap_bytes\":%" PRIu32 ","
            "\"startup_state\":\"%s\","
            "\"stm_connected\":false,\"stm_stale\":false,"
            "\"stm_age_ms\":null,\"stm_age_limit_ms\":%u,"
            "\"tel_count\":0,\"stm_t_ms\":null,"
            "\"state\":null,\"reason\":null,"
            "\"command_age_ms\":null,\"last_seq\":null,"
            "\"vx_mmps\":null,\"w_mradps\":null,"
            "\"left_pwm\":null,\"right_pwm\":null,"
            "\"left_cps\":null,\"right_cps\":null,"
            "\"encoder_valid\":null,\"encoder_t_ms\":null,"
            "\"left_count\":null,\"right_count\":null,"
            "\"encoder_arm_valid\":null,\"encoder_arm_seq\":null,"
            "\"batt_mv\":null,\"battery_available\":false,"
            "\"drop\":null,\"err\":null}",
            WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms,
            esp_get_free_heap_size(), startup_state, STM_TEL_STALE_MS);
    } else {
        length = snprintf(
            json, capacity,
            "{\"source\":\"STM_UART\",\"mode\":\"%s\","
            "\"boot_id\":%" PRIu32 ",\"uptime_ms\":%" PRIu64 ","
            "\"free_heap_bytes\":%" PRIu32 ","
            "\"startup_state\":\"%s\","
            "\"stm_connected\":%s,\"stm_stale\":%s,"
            "\"stm_age_ms\":%" PRIu64 ",\"stm_age_limit_ms\":%u,"
            "\"tel_count\":%" PRIu32 ",\"stm_t_ms\":%" PRIu32 ","
            "\"state\":\"%s\",\"reason\":\"%s\","
            "\"command_age_ms\":%" PRIu32 ",\"last_seq\":%" PRIu32 ","
            "\"vx_mmps\":%" PRIi32 ",\"w_mradps\":%" PRIi32 ","
            "\"left_pwm\":%" PRIi32 ",\"right_pwm\":%" PRIi32 ","
            "\"left_cps\":%" PRIi32 ",\"right_cps\":%" PRIi32 ","
            "\"encoder_valid\":%s,\"encoder_t_ms\":%" PRIu32 ","
            "\"left_count\":\"%" PRId64 "\",\"right_count\":\"%" PRId64 "\","
            "\"encoder_arm_valid\":%s,\"encoder_arm_seq\":%" PRIu32 ","
            "\"batt_mv\":null,\"battery_available\":false,"
            "\"drop\":%" PRIu32 ",\"err\":%" PRIu32 "}",
            WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms,
            esp_get_free_heap_size(), startup_state,
            fresh ? "true" : "false", fresh ? "false" : "true",
            age_ms, STM_TEL_STALE_MS, tel_count, tel.t_ms,
            tel.state, tel.reason, tel.command_age_ms, tel.last_seq,
            tel.vx_mmps, tel.w_mradps, tel.left_pwm, tel.right_pwm,
            tel.left_cps, tel.right_cps,
            tel.encoder_valid ? "true" : "false", tel.encoder_t_ms,
            tel.left_count, tel.right_count,
            tel.encoder_arm_valid ? "true" : "false", tel.encoder_arm_seq,
            tel.drop, tel.err);
    }

    if (length < 0 || (size_t)length >= capacity) {
        return -1;
    }
    return length;
}
```

**6. PAGE의 validStatus 한 줄을 아래 C 문자열 블록으로 교체**

기존 블록 시작: `    "function validStatus(s){ const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295; const i32=v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647; const ms=v=>Number.isSafeInteger(v)&&v>=0; if(!s||typeof s!=='object'||Array.isArray(s)||    !['ESP_ONLY','STM_UART'].includes(s.source)||    !['AP','STA'].includes(s.mode)||    !['SETTLE','SYNC_WAIT','WAIT_DISARM_ACK',      'WAIT_PONG','READY','FAILED'].includes(s.startup_state)||    !u32(s.boot_id)||!ms(s.uptime_ms)||!u32(s.free_heap_bytes)||    !u32(s.tel_count)||!u32(s.stm_age_limit_ms)||s.stm_age_limit_ms===0||    typeof s.stm_connected!=='boolean'||typeof s.stm_stale!=='boolean'||    s.batt_mv!==null||s.battery_available!==false)return false; if(s.source==='ESP_ONLY'){  return !s.stm_connected&&!s.stm_stale&&s.stm_age_ms===null&&   s.tel_count===0&&['stm_t_ms','state','reason','command_age_ms',   'last_seq','vx_mmps','w_mradps','left_pwm','right_pwm',   'left_cps','right_cps','drop','err'].every(k=>s[k]===null); } return ms(s.stm_age_ms)&&  s.stm_connected===(s.stm_age_ms<=s.stm_age_limit_ms)&&  s.stm_stale===!s.stm_connected&&u32(s.stm_t_ms)&&  ['DISARMED','ARMED','FAULT'].includes(s.state)&&  typeof s.reason==='string'&&/^[A-Z0-9_]{1,31}$/.test(s.reason)&&  ['command_age_ms','last_seq','drop','err'].every(k=>u32(s[k]))&&  ['vx_mmps','w_mradps','left_pwm','right_pwm',   'left_cps','right_cps'].every(k=>i32(s[k]))&&  Math.abs(s.left_pwm)<=1000&&Math.abs(s.right_pwm)<=1000;}\n"`. 함수/typedef는 끝까지 교체한다.

```c
    "function validStatus(s){\n"
    " const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;\n"
    " const i32=v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647;\n"
    " const ms=v=>Number.isSafeInteger(v)&&v>=0;\n"
    " const i64text=v=>{\n"
    "  if(typeof v!=='string'||! /^-?(0|[1-9][0-9]{0,18})$/.test(v)||v==='-0')return false;\n"
    "  const negative=v[0]==='-', digits=negative?v.slice(1):v;\n"
    "  const limit=negative?'9223372036854775808':'9223372036854775807';\n"
    "  return digits.length<limit.length||(digits.length===limit.length&&digits<=limit);\n"
    " };\n"
    " if(!s||typeof s!=='object'||Array.isArray(s)||\n"
    "  !['ESP_ONLY','STM_UART'].includes(s.source)||!['AP','STA'].includes(s.mode)||\n"
    "  !['SETTLE','SYNC_WAIT','WAIT_DISARM_ACK','WAIT_PONG','READY','FAILED'].includes(s.startup_state)||\n"
    "  !u32(s.boot_id)||!ms(s.uptime_ms)||!u32(s.free_heap_bytes)||!u32(s.tel_count)||\n"
    "  !u32(s.stm_age_limit_ms)||s.stm_age_limit_ms===0||\n"
    "  typeof s.stm_connected!=='boolean'||typeof s.stm_stale!=='boolean'||\n"
    "  s.batt_mv!==null||s.battery_available!==false)return false;\n"
    " if(s.source==='ESP_ONLY'){\n"
    "  return !s.stm_connected&&!s.stm_stale&&s.stm_age_ms===null&&s.tel_count===0&&\n"
    "   ['stm_t_ms','state','reason','command_age_ms','last_seq','vx_mmps','w_mradps',\n"
    "    'left_pwm','right_pwm','left_cps','right_cps','drop','err',\n"
    "    'encoder_valid','encoder_t_ms','left_count','right_count',\n"
    "    'encoder_arm_valid','encoder_arm_seq'].every(k=>s[k]===null);\n"
    " }\n"
    " return ms(s.stm_age_ms)&&s.stm_connected===(s.stm_age_ms<=s.stm_age_limit_ms)&&\n"
    "  s.stm_stale===!s.stm_connected&&u32(s.stm_t_ms)&&\n"
    "  ['DISARMED','ARMED','FAULT'].includes(s.state)&&\n"
    "  typeof s.reason==='string'&&/^[A-Z0-9_]{1,31}$/.test(s.reason)&&\n"
    "  ['command_age_ms','last_seq','drop','err'].every(k=>u32(s[k]))&&\n"
    "  ['vx_mmps','w_mradps','left_pwm','right_pwm','left_cps','right_cps'].every(k=>i32(s[k]))&&\n"
    "  Math.abs(s.left_pwm)<=1000&&Math.abs(s.right_pwm)<=1000&&\n"
    "  typeof s.encoder_valid==='boolean'&&typeof s.encoder_arm_valid==='boolean'&&\n"
    "  u32(s.encoder_t_ms)&&u32(s.encoder_arm_seq)&&i64text(s.left_count)&&i64text(s.right_count);\n"
    "}\n"
```

## 목적

이 문서는 궤도형 모바일 로봇의 첫 kinematics와 odometry 계획을 정의한다.

로봇은 left/right tracked drivetrain을 사용한다. Low-speed control과 첫 odometry에서는 differential-drive
robot처럼 다룰 수 있다. 즉 left track과 right track의 속도 차이로 전진과 회전을 만든다.

이 문서는 다음 질문에 답한다.

- Command velocity가 left/right track command로 어떻게 바뀌는가
- Encoder count가 distance와 speed estimate로 어떻게 바뀌는가
- Odometry를 시간에 따라 어떻게 적분하는가
- IMU data는 나중에 어디에 추가되는가
- Tracked vehicle odometry의 한계는 무엇인가
- Odometry model이 쓸 만하다는 것을 어떤 test로 증명하는가

## Architecture Decision

첫 tracked drivetrain model은 differential-drive approximation을 사용한다.

Initial command variables:

```text
vx_mmps   : forward velocity in mm/s
w_mradps : yaw rate in millirad/s
```

Initial output variables:

```text
left_track_speed
right_track_speed
left_motor_pwm
right_motor_pwm
```

핵심 결정:

```text
Encoder-based differential odometry를 먼저 사용한다.
Drivetrain과 encoder sign이 안정된 뒤 IMU yaw-rate correction을 추가한다.
```

## 1. 용어

| Term | 이 프로젝트에서의 의미 |
| --- | --- |
| Kinematics | Robot motion과 left/right track motion 사이의 관계 |
| Odometry | Wheel 또는 track encoder data로 robot movement를 추정하는 것 |
| Track width | Left/right contact line 사이의 effective distance |
| Encoder count | Motor 또는 wheel encoder에서 측정한 tick count |
| Counts per revolution | Shaft 또는 output 1회전에 해당하는 encoder count |
| Distance per count | Encoder count 1개가 나타내는 linear travel estimate |
| Yaw | Vertical axis 주변 heading angle |
| Slip | Track이 움직였지만 실제 ground movement로 변환되지 않은 현상 |

## 2. Coordinate Convention

일반 mobile robot body convention을 사용한다.

```text
x axis: forward
y axis: left
z axis: up
positive yaw: 위에서 봤을 때 counter-clockwise turn
```

Robot pose:

```text
x_m     : position x in meters
y_m     : position y in meters
yaw_rad : heading in radians
```

Command convention:

```text
positive vx -> robot moves forward
positive w  -> robot turns left
```

Encoder sign은 이 convention이 성립하도록 조정해야 한다.

### Bench와 vehicle-frame encoder sign convention

**현재 기준 — 2026-09-26 정정:** A=왼쪽/M1/JENC_1/TIM3, B=오른쪽/M2/JENC_2/TIM5.
두 엔코더 커넥터 교환 후 손회전 시 해당 쪽 CPS만 변화하고 전진 양수·후진 음수·정지 0을
사용자가 확인했다. TIM3 부호 반전·TIM5 유지 수식은 그대로 사용한다.
9/29에는 M1→A와 M2→B 동력선이 모두 연결됐고 B는 실제 전진·후진과 CPS 부호를 확인했다.
A의 ±명령 회전·CPS는 관측했으나 양수 명령의 실제 전진 방향 확인은 남아 있다.
[단일 모터 방향 보정 근거](../docs/verification/31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md).
[정정과 새 손회전 근거](../docs/verification/29_Vehicle_Side_Mapping_Correction_and_Hand_Rotation_Check_2026-09-26_ko.md).

**아래는 7월 당시 연결과 측정 이력이다. 현재 모터 A/B의 좌우 배선 지시로 사용하지 않는다.**

2026-07-26 motor-power-off 시험에서는 output shaft end를 정면에서 본 기준으로
clockwise 회전 시 TIM3 count가 증가하고 counter-clockwise 회전 시 감소했다.
이 부호는 `PB4 = CH1/A`, `PB5 = CH2/B`인 bench raw-sign 결과다.

2026-07-30 motor-off 수동 회귀에서는 encoder-side 장착 관계를 다음과 같이
확정했다.

| Vehicle side | Motor / timer | Output-shaft forward rotation | Raw sign on forward | Production normalization |
| --- | --- | --- | --- | --- |
| Right | MG540-A / TIM5 | Clockwise | Positive | Keep |
| Left | MG540-B / TIM3 | Counter-clockwise | Negative | Invert TIM3/left CPS |

따라서 당시 production `left_cps/right_cps`는 모두 차량 전진에서 양수가 되었다. 이
검증은 **당시 encoder-side vehicle-frame mapping과 부호**만 닫는다. MDD10A powered
channel 1/2가 실제 좌·우 motor로 이어지는 관계와 command-driven forward
polarity는 첫 powered drivetrain 시험에서 별도로 확인한다.

## 3. Differential Drive Approximation

정의:

```text
v     = robot forward velocity
w     = robot yaw rate
B     = effective track width
v_l   = left track linear velocity
v_r   = right track linear velocity
```

Forward model:

```text
v = (v_r + v_l) / 2
w = (v_r - v_l) / B
```

Inverse model:

```text
v_l = v - (w * B / 2)
v_r = v + (w * B / 2)
```

Project interpretation:

- Left/right speed가 같으면 직진.
- Right가 left보다 빠르면 left turn.
- Left가 right보다 빠르면 right turn.
- 부호가 반대면 제자리 회전 후보.

## 4. Encoder Distance Model

각 side에 대해:

```text
distance_per_count = output_circumference / counts_per_output_rev
distance = delta_count * distance_per_count
```

여기서:

- `output_circumference`는 effective sprocket 또는 track driving circumference다.
- Encoder가 motor shaft에 있다면 `counts_per_output_rev`에는 encoder resolution과 gearbox ratio가 포함되어야 한다.

측정해야 할 open parameters:

| Parameter | How to obtain |
| --- | --- |
| Encoder counts per output revolution | Motor/encoder datasheet와 반복 bench/주행 measurement |
| Gear ratio | Motor model datasheet 또는 manual count test |
| Output sprocket circumference | 직접 측정 또는 track movement로 추정 |
| Effective track width | Chassis 측정, rotation test로 tune |
| Encoder sign | Encoder-side 수동 회귀는 완료; powered vehicle-forward command에서 재확인 |

Motor label의 nominal 정보만으로 정확한 odometry가 가능하다고 가정하지 않는다.

2026-07-26 TIM3 TI12 x4 hand-rotation에서 얻은 provisional 값은 다음과 같다.

| Bench motor | Shaft-end-view CW | Shaft-end-view CCW | Provisional counts/output rev |
| --- | ---: | ---: | ---: |
| MG540-A | 약 +1560 | 약 -(1560~1570) | 약 1560 |
| MG540-B | +1562 | -1560 | 약 1560 |

`1560 counts/output rev`는 이 시점의 motor-power-off 1회전 수동 측정에서 얻은
provisional scale이었다. Powered/noise 조건과 반복 측정 전에는 final odometry
constant로 고정하지 않았다. Raw serial log는 MG540-A의 정지 안정성과
방향별 count 증감만 직접 보여 주며, 위 1회전 수치와 MG540-B 결과는 같은 bench
session의 별도 측정 보고다. Evidence는
[`../assets/logs/encoder/README.md`](../assets/logs/encoder/README.md)에 정리한다.

### 2026-07-30 50-Revolution Calibration

위 2026-07-26 provisional scale을 보완하기 위해 표시한 출력축을 motor별·방향별
50회전시켰다.

| Bench motor | Direction | Absolute total count | Counts/output rev |
| --- | --- | ---: | ---: |
| MG540-A | CW | 77,998 | 1559.96 |
| MG540-A | CCW | 78,001 | 1560.02 |
| MG540-B | CW | 78,000 | 1560.00 |
| MG540-B | CCW | 78,000 | 1560.00 |

현재 STM32 quadrature x4 기준 firmware 변환 상수는 `1560 counts/output rev`로
확정한다. Signed CPS -> mRPM은 `trunc(CPS * 60000 / 1560)`으로 계산하며 boot
self-test와 305-row dual hand-rotation log에서 계산·방향·정지 복귀가 통과했다.

이 결정은 count-to-output-revolution scale을 닫은 것이다. Track odometry의
`distance_per_count`는 effective sprocket/track travel, track slip과 powered
vehicle-forward command regression을 측정하기 전까지 확정하지 않는다. External tachometer 기반 절대
RPM 정확도와 powered-motor noise도 별도 시험 대상이다. 상세 evidence는
[`../assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md`](../assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md)에 있다.

## 5. Speed Estimation

각 control period마다:

```text
delta_count = current_count - previous_count
distance_m = delta_count * distance_per_count_m
speed_mps = distance_m / dt_s
```

Initial filtering:

- Bench validation 중에는 raw speed부터 사용한다.
- Sign과 scale을 확인한 뒤 simple moving average 또는 low-pass filtering을 추가한다.
- 가능하면 filtered value와 raw value를 모두 debug log에 남긴다.

Filtering이 필요한 이유:

- Encoder count는 discrete하다.
- Low-speed motion에서는 tick이 드물게 발생할 수 있다.
- Motor와 track vibration이 speed estimate noise를 만들 수 있다.

## 6. Odometry Integration

각 odometry update마다:

```text
d_l = left_distance_delta
d_r = right_distance_delta
d_center = (d_r + d_l) / 2
d_yaw = (d_r - d_l) / B
```

Pose update:

```text
yaw_mid = yaw + d_yaw / 2
x = x + d_center * cos(yaw_mid)
y = y + d_center * sin(yaw_mid)
yaw = yaw + d_yaw
```

내부 계산은 radians를 사용한다.

Initial update rate:

```text
50 Hz to 100 Hz
```

같은 100 Hz motor loop에서 basic odometry를 계산할 수 있고, FreeRTOS 도입 이후 별도 lower-priority task로
분리할 수도 있다.

## 7. Tracked Vehicle Limitations

Tracked robot은 ideal wheeled differential-drive robot보다 slip이 크다.

Common error sources:

- Track slip during turns
- Track deformation
- Uneven floor friction
- Different left/right motor response
- Encoder mounted before gearbox
- Backlash 또는 mechanical looseness
- Load-dependent current and speed changes

Implication:

Encoder-only odometry는 short-term motion estimation에는 유용하지만, globally accurate position으로
취급하면 안 된다.

## 8. IMU Fusion Path

BNO08x IMU는 나중에 heading behavior 개선에 사용할 수 있다.

First IMU uses:

- Encoder yaw rate와 IMU yaw rate 비교.
- Turn 중 큰 slip 감지.
- IMU yaw를 heading correction 후보로 사용.
- Yaw 또는 yaw-rate telemetry publish.

처음부터 복잡한 sensor fusion을 시작하지 않는다.

Recommended progression:

```text
encoder-only odometry
    -> compare encoder yaw with IMU yaw
    -> simple complementary heading correction
    -> later ROS2 odometry message and TF integration
```

Simple complementary idea:

```text
yaw_est = alpha * yaw_encoder + (1 - alpha) * yaw_imu
```

이 방식은 time alignment, axis convention, IMU orientation을 확인한 뒤에만 사용한다.

## 9. Command to Motor Output

Command path:

```text
vx_mmps, w_mradps
        |
        v
convert to v_l, v_r
        |
        v
apply speed limits
        |
        v
apply acceleration/ramp limits
        |
        v
open-loop PWM or speed controller
        |
        v
MDD10A PWM + DIR output
```

Initial control mode:

- Low PWM open-loop으로 시작한다.
- Encoder count는 처음에는 observation용으로만 사용한다.
- Speed estimation을 추가한다.
- Encoder sign과 scale이 안정된 뒤 proportional control을 추가한다.
- P control behavior를 이해한 뒤 PID를 추가한다.

## 10. Calibration Tests

### Test 1: Encoder Sign Test

Procedure:

- Track을 들어 올린다.
- Low forward speed를 command한다.
- Left/right encoder count direction을 확인한다.

Expected:

- Forward command에서 양쪽 count가 증가한다.

### Test 2: Distance Scale Test

Procedure:

- Floor start position을 표시한다.
- 짧은 직선 motion을 command한다.
- 실제 이동 거리를 측정한다.
- Encoder-estimated distance와 비교한다.

Expected:

- Scale error가 측정되고 문서화된다.

### Test 3: Rotation Scale Test

Procedure:

- Slow in-place rotation을 command한다.
- 실제 yaw change를 측정한다.
- Odometry yaw와 비교한다.

Expected:

- Effective track width를 tune할 수 있다.

### Test 4: Straight-Line Drift Test

Procedure:

- Straight motion을 command한다.
- Left/right encoder speed를 기록한다.
- Robot이 left/right로 치우치는지 관찰한다.

Expected:

- Motor mismatch와 track friction이 식별된다.

### Test 5: IMU Comparison Test

Procedure:

- 천천히 회전한다.
- Encoder yaw rate와 IMU yaw rate를 비교한다.

Expected:

- Fusion 전에 IMU axis와 sign이 검증된다.

## 11. Telemetry Fields

Recommended odometry telemetry:

```text
left_count
right_count
left_delta
right_delta
left_speed_mmps
right_speed_mmps
vx_est_mmps
w_est_mradps
odom_x_mm
odom_y_mm
odom_yaw_mrad
imu_yaw_mrad
imu_yaw_rate_mradps
```

이 field들은 plotting과 debugging에 유용하다.

## 12. ROS2 Expansion Path

Firmware odometry가 검증된 뒤 higher-level bridge는 다음을 publish할 수 있다.

- `nav_msgs/Odometry`
- `tf`: `odom -> base_link`
- optional `sensor_msgs/Imu`

중요:

- Frame convention과 unit이 일관되기 전에는 ROS2 odometry를 publish하지 않는다.
- ROS2 integration은 STM32 safety ownership model을 유지해야 한다.
- ROS2는 velocity를 요청할 수 있지만 STM32는 command timeout과 motor safety를 계속 소유한다.

## 13. Evidence Targets

Portfolio-quality evidence:

| Evidence | What it proves |
| --- | --- |
| Encoder sign table | Left/right direction convention이 맞음 |
| Distance scale test | Encoder count를 distance로 변환했음 |
| Rotation test | Effective track width를 tune 또는 측정했음 |
| Speed plot | Encoder speed estimate가 동작함 |
| Straight-line drift record | Mechanical/control mismatch를 인식했음 |
| IMU comparison plot | Sensor fusion path가 data 기반임 |
| Odometry formula document | Engineering model이 명시적임 |

## Final Decision

첫 model은 encoder-based differential-drive odometry를 사용한다.

이를 완벽한 position source가 아니라 practical local estimate로 취급한다.

Encoder direction, scale, control behavior가 검증된 뒤 IMU yaw comparison과 correction을 추가한다.
