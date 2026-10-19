# 실행 계획

**10/20 최신 연동 상태:** 실물 톱니 **14개** 확인. 연속6개 링크 동일 형상1→6의5간격48.1~48.3mm에서 피치9.62~9.66mm, 대표값9.64mm. 기존 실측1560counts/output rev 유지 →134.96mm/rev, 좌우 공통 초기 k=1687/19500≈0.08651282mm/count. 대표값은 측정 범위 중간값이며 수동 checkpoint 회귀 보정값이 아니다. PC 분석기36·CLI3·거부2 PASS. 윗쪽 직선 궤도 수동 이동100/150mm의 좌우 평균 환산은100.138590/150.532308mm다. 기존12톱니 가정이 공통 scale 차이를 대부분 설명한다. 공중 궤도 이동 비교이며 지상 차체 거리 정확도·슬립/전체 MVP PASS는 아니다. 다음은 인수 이미지 기준점 대조·고정이다.

이 폴더는 전체 로드맵과 날짜별 작업 계획을 보관한다. 실제 수행 결과는 진행 기록과 시험 보고서를 따른다.

## 현재 시작점 — 2026-10-19

배터리 단독 지상의 선택 수동 주행·놓음/DISARM·1차 직진 보정은10/18 증거를 유지한다. 현재 MVP에는 잔여 실제 정지·1 m 거리 비교·GM-1312 외부 온도 관측과 최종 증거 정리가 남는다. 정량 전류 측정·전류/전압 ADC 모니터링은 post-MVP다. 범위와 판정은 [마스터 플랜](00_Project_Master_Plan_To_Final_MVP_ko.md), [검증 매트릭스](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md), 실물 기준점은 [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md)를 따른다.

실행할 작업은 아래 **스토리·태스크 백로그**에서 찾는다. `TK-MVP-05-01`의 [미결 감사](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#tk-mvp-05-01-감사-결과--2026-10-19)는 완료했다. `TK-MVP-03-01`의14톱니 초기 거리 모델과 STM→ESP→브라우저 누적 count 경로를 준비·subset 검증했다. 지상 보정은 미완료이며 현재는 인수 이미지 기준점 대조·고정이 다음이다. 정지/온도 시험 설계는 장비 대기 중에도 준비 가능하다.

아래 날짜별 코드 입력 안내는 당시 판본이며 최신 소스를 덮어쓰는 용도로 사용하지 않는다. 학습 자료는 [STM·ESP 교과서](../../07_Embedded_Learning_Notes/06_STM32_ESP32_Firmware_Textbook/README.md)다.

## 10/20 마감과 다음 세션 실행안

STM→ESP→브라우저의 누적 count·시각·ARM 구간 전달과 공중 전후진/놓음·DISARM 보존 subset을 확인했다. 실물14톱니·5피치48.1~48.3mm(대표 피치9.64mm), 기존1560counts/output rev로 초기 k≈0.08651282mm/count를 정정했고 PC 분석기36개 검사와 실제 로그3회차 재계산이 통과했다. 지상 거리 보정·최종 실행 이미지 고정·전용 유실/timeout 정지·외부 온도·1m 인수는 미완료다.

| 세션 | 작업 | 종료 시 남길 근거 |
| --- | --- | --- |
| 자고 일어난 뒤 첫 작업(10/21 목표, 실제 가용 시간에 따름) | TK-MVP-03-04의 source·기존 이미지 대조/기준점 정리, TK-MVP-02-01/02의 전용 정지 조건·최소 시험 수단 검토 | source/image hash와 build/flash/runtime 증거를 구분한 기준점. 새 빌드는 필요성이 확인될 때만 사용자 수행 |
| 후속 준비 세션 | 전용 유실/timeout 시험 절차 및 외부 온도 위치/기록표 정리, GM-1312 구매/수령 상태 확인 | 첫 물리 시험의 진입/정지/복구·PASS 기준; 미보유 장비 가정 금지 |
| 선행 조건 완료 뒤 | 전용 정지 → 외부 온도 → 지상1m → 최종 요구사항/README/demo 대조 | 각 실물 회차의 raw 로그·사용자 실제 관측·오차·한계. 전류/전압 ADC는 MVP 선행이 아님 |

10/19 날짜별 초안 중10/21~23의 count 구현/PC 검사는10/20에 앞서 진행됐다. 완료분을 일정 때문에 반복하지 않고 위 재개점으로 옮긴다.10/24 이후 날짜는 기존 조건부 목표이며 새 확정 일정/Calendar 등록이 아니다. 전체 MVP를 완료로 바꾸지 않는다.

## 스토리·태스크 백로그

이 목록은 저장소의 실행 관점이다. 외부 Jira에 이슈를 생성한 기록이 아니다. 상태 기준은10/19 문서와10/18 실물 증거이며, 여기서 말하는 태스크는 업무 단위다. FreeRTOS task와 구분한다.

| 계층 | 의미 | 이 프로젝트의 대응 |
| --- | --- | --- |
| 에픽 | 여러 결과를 묶는 목표 | 이번 `EP-MVP` 하위 구동 플랫폼 인수, 후속 센서/모니터링·제어·통신 확장 |
| 스토리 | 사용자나 검증자가 확인할 수 있는 결과 | 명령 유실 시 실제 궤도가 정지한다; 실제 거리와 추정 오차를 확인한다 |
| 태스크 | 그 결과를 만드는 구체 작업 | 데이터 계약 정의, 구현/PC 검사, 사용자 빌드·실물 시험, 결과 분석 |
| 요구사항·Test ID | 결과의 수용 기준과 검증 근거 | 기존 `MVP-*`, `REQ-*`, `T-*`를 그대로 연결 |

작업 ID `ST-*`/`TK-*`는 요구사항 ID를 대체하지 않는다. 완료는 그 작업에 명시한 범위만 뜻한다. 기존 Gate/보고서의 PARTIAL을 스토리 상태로 PASS 처리하지 않는다.

### EP-MVP — 한정된 저속 하위 구동 플랫폼을 인수한다

| 스토리 | 검증자가 얻는 결과 | 완료 조건·연결 | 현재 상태 |
| --- | --- | --- | --- |
| `ST-MVP-01` 수동 주행 기준선 | 현재 구성으로 전후진·좌우회전·놓음/DISARM 결과와 설정을 확인한다 | 10/18 선택 지상 회차·PWM/CPS·사용자 관측 연결. MVP-006/010, REQ-DRIVE-001/002 | **선택 범위 완료**; 전체 통신·안전 인수와 구분 |
| `ST-MVP-02` 명령 유실 정지 | 입력이 끊겨도 현재 실제 궤도가 정지하며 자동으로 다시 움직이지 않는다 | 최종 firmware의 UART 단절/명령 timeout·실제 정지 증거. REQ-DRIVE-003, MVP-009 관련 subset, T-DRIVE-001 | **부분 완료** — 놓음/DISARM은 기존 근거 사용, 전용 유실/timeout 시험 남음 |
| `ST-MVP-03` 이동량 검증 | 실제 1 m와 엔코더 추정 거리의 차이를 수치로 확인한다 | 거리 모델·누적 count/시각과 실제 거리·절대/백분율 오차. MVP-011, REQ-ODO-001, T-ODO-001 | **진행 중** — 누적 count 전송·공중 부호/정지 subset과14톱니 초기 모델 준비, 지상1m 미완료 |
| `ST-MVP-04` 외부 온도 관측 | 정해진 짧은 주행에서 모터·드라이버·전원부의 온도 변화를 확인한다 | 위치/부착·주위 온도·구동/휴지 시간·출력과 온도 결과표. MVP-015, REQ-THERM-001, T-LOAD-001 | **장비 대기** — GM-1312 선택, 구매/수령·측정 미확인; ADC 의존성 없음 |
| `ST-MVP-05` 최종 인수와 재현 | 적용 요구사항과 증거·한계가 맞고 제3자가 결과를 따라 확인한다 | 전체 적용 MUST의 판정/증거 audit, 기준점·README/demo·재현 절차. MVP-012, T-DOC-001 및 잔여 전원/기구/안전 항목 | **대기** — 기존 부분 판정은 보존; 첫 감사 태스크는 지금 가능 |

### MVP 개별 태스크

`바로 가능`은 현재 문서/PC 작업이 가능하다는 뜻이다. 물리 작업은 구체 실행 절차의 조건과 실제 상태 확인 후 사용자가 수행한다. firmware 입력·두 보드 빌드/플래시는 사용자, 설계 설명·PC 검사·로그 분석·문서는 Codex가 맡는다.

| 태스크 | 부모 스토리 | 실행할 작업과 남길 산출물 | 선행 조건 | 현재 상태 |
| --- | --- | --- | --- | --- |
| `TK-MVP-01-01` | ST-MVP-01 | A=left/M1, B=right/M2·궤도 상태·cap150/200·gain960/930 기준점 연결 | 기존 저장본/실물 기록 | 완료 — [인수인계](../handoff/CURRENT_SESSION_CONTEXT.md) |
| `TK-MVP-01-02` | ST-MVP-01 | 네 방향·동작 사이 zero/PWM/CPS0·최종 DISARM의 선택 통합 근거 보존 | 기존 회차 | 완료 — [최종 지상 회차](../../assets/logs/wifi_link/2026-10-18_ground_combined_trim_run01/observations.json) |
| `TK-MVP-01-03` | ST-MVP-01 | 육안 휨 감소·CPS 차이, 간헐 정지의 영구 해결 미확정이라는 한계 연결 | 기존 분석 | 완료 — [10/18 기록](../progress/2026-10-18_progress.md) |
| `TK-MVP-02-01` | ST-MVP-02 | UART 연결 유실과 유효 CMD 중단을 구분한 시험 설계: trigger·마지막 유효 명령·시간 기준·실제 궤도 정지·재시작 금지의 수용/종료 기준 | TK-MVP-05-01; 기존 timeout 계약 | 바로 가능 — 아직 실물 조작 지시 아님 |
| `TK-MVP-02-02` | ST-MVP-02 | 기존 시험 수단을 대조하고 필요한 최소 주입/관찰 방법·로그 항목을 확정. 코드 변경이 필요하면 영향·PC 검사·사용자 입력 블록 준비 | TK-MVP-02-01 | 선행 작업 대기 |
| `TK-MVP-02-03` | ST-MVP-02 | 최신 인수 이미지에서 사용자 전용 유실/timeout 시험. 같은 회차의 명령·TEL·실제 정지 관측/영상·복구 동작 수집 | TK-MVP-02-02, TK-MVP-03-04; 장비/전원·실행 절차 확정 | 선행 작업 대기 |
| `TK-MVP-02-04` | ST-MVP-02 | PWM 적용값/실제 정지·CPS·자동 재구동 여부와 계약을 대조하고 보고서/REQ-DRIVE-003 판정 갱신 | TK-MVP-02-03 | 선행 작업 대기 |
| `TK-MVP-03-01` | ST-MVP-03 | 기존1560 counts/output rev와 실제 sprocket/track 이동량을 연결할 distance-per-count 모델·단위·기준점을 정의. 필요한 기하/실측 항목과 반복/종료 기준 작성 | TK-MVP-05-01; 기존 encoder 증거 | **정정 기하 초기 모델 준비** — 실물14톱니·5피치48.1~48.3mm, 대표9.64mm로 PC 기본 k≈0.08651282. 지상 보정/1m 미완료 |
| `TK-MVP-03-02` | ST-MVP-03 | 실제 누적 count 구현/가용 데이터를 확인하고 STM→ESP→브라우저/저장 로그의 count·측정 시각·reset/boot 구분 계약과 최소 구현 준비 | TK-MVP-03-01의 부호/기준점 설계와 병행 가능; 피치 확정은 거리 환산 전 | **입력 완료 / 저장본 PC PASS** — [실제 저장본 결과](../progress/2026-10-20_progress.md#esp-수정-후-실제-저장본-pass). STM native14·ESP count/PAGE·제어 회귀 PASS. 실제 정지 데이터 연동은 다음 태스크에서 subset 확인 |
| `TK-MVP-03-03` | ST-MVP-03 | 부호·wrap/누적·단위/변환·reset·메시지 길이/파서의 변경 영향 PC 검사와 원시 로그 저장 확인 | 사용자 저장본 TK-MVP-03-02 | **관련 PC 검사·offline 분석기 PASS** — 기존 STM/ESP 검사와 [거리 분석 검증](../../assets/logs/wifi_link/2026-10-20_encoder_distance_14t_review/validation.json). unittest36·실제CLI3·거부2. 지상 보정과 구분 |
| `TK-MVP-03-04` | ST-MVP-03 | 사용자 STM/ESP 빌드·플래시 후 source/이미지 기준점·READY/IDLE·zero 및 새 데이터 경로 확인. 기존 결과와 변경 영향 구분 | TK-MVP-03-03 | **진행 중 / 데이터 경로 subset PASS** — 실물 정지/reset·ARM/재ARM·공중 전후진/놓음·DISARM 보존 확인. 인수 이미지 고정과 전체 수용은 별도 |
| `TK-MVP-03-05` | ST-MVP-03 | 정한 방법으로 사용자 1 m 주행. 실제/추정 거리·원시 count·절대/백분율 오차·반복 조건을 분석하고 T-ODO-001 판정 | TK-MVP-03-04, TK-MVP-02-04, TK-MVP-04-04의 기본 온도 판정 | 선행 작업 대기 — 임의 정확도 목표를 새로 만들지 않음 |
| `TK-MVP-04-01` | ST-MVP-04 | GM-1312·K형 프로브 구성·전기적 절연/고정 부속 확보와 실제 사용 확인. 모델 선택을 구매/수령으로 처리하지 않음 | 사용자 구매/수령·실물 확인 | 장비 대기 |
| `TK-MVP-04-02` | ST-MVP-04 | 위치별 측정법, 주위 온도·구동/휴지 시간·반복 수·온도 기준·중단 조건·기록표를 부품 근거로 확정 | 문서 계획은 지금 가능; 실물 probe 방식은 TK-MVP-04-01 | 바로 가능 — ADC/전류계 불필요 |
| `TK-MVP-04-03` | ST-MVP-04 | 최신 이미지의 정한 짧은 주행에서 사용자 외부 온도·시간·PWM/CPS·차체 동작/이상 관측 수집. 2채널로 나눠 측정하면 회차별 조건 기록 | TK-MVP-04-01/02, TK-MVP-02-04 | 선행 작업/장비 대기 |
| `TK-MVP-04-04` | ST-MVP-04 | 위치별 온도·상승량과 조건/기준 비교, 미측정 전류·장시간/정격 한계를 남겨 T-LOAD-001 판정 | TK-MVP-04-03 | 선행 작업 대기 |
| `TK-MVP-05-01` | ST-MVP-05 | 현재 MUST와 과거 PARTIAL/제외 이력을 먼저 대조해 활성 미결·기존 증거로 닫을 항목·후속/제외 항목의 처리 근거를 표로 작성 | 현재 마스터/검증표·기존 사용자 결정 | **완료 — 10/19 [감사 결과표](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#tk-mvp-05-01-감사-결과--2026-10-19)**. 활성 미결 해소·전체 인수 완료와 구분 |
| `TK-MVP-05-02` | ST-MVP-05 | 위 감사에서 확인된 전원/기구/엔코더·안전의 활성 미결만 실행 가능한 단위로 분리해 시험 또는 증거 연결. 새 기능은 별도 후속으로 분류 | TK-MVP-05-01 | 선행 작업 대기 — 과거 제외 검토 자동 재개 금지 |
| `TK-MVP-05-03` | ST-MVP-05 | ST-MVP-02/03/04와 활성 미결의 결과를 요구사항/Test ID·원본 증거로 연결 | TK-MVP-02-04, TK-MVP-03-05, TK-MVP-04-04, TK-MVP-05-02 | 선행 작업 대기 |
| `TK-MVP-05-04` | ST-MVP-05 | README/demo·시스템 구성/역할·기준 firmware/배선·운용 조건·재현 절차·한계를 정리 | TK-MVP-05-03 | 선행 작업 대기 |
| `TK-MVP-05-05` | ST-MVP-05 | 최종 적용 MUST와 제외/후속의 명시적 근거·링크·공개할 파일을 대조하고 인수 판정/커밋 묶음 정리 | TK-MVP-05-02/03/04 완료 | 선행 작업 대기 — 전체 MVP 완료 선언은 여기서 판단 |

`TK-MVP-05-01/02`가 필요한 이유: 이 다섯 스토리가 기존 검증표 전체를 자동으로 대체하지 않는다. 오래된 전원/기구/통신·E-stop PARTIAL은 여전히 존재한다. 실행 범위에서 제외한 항목도 PASS로 바꾸지 않으며, 최종 판정과 실제 제외 근거가 충돌하면 먼저 명시적으로 정리한다. 감사에서 실물 선행 조건이 확인되면 해당 태스크에 연결한 뒤 실행 준비 상태를 정한다. 본 백로그는 새 제외 결정을 만들지 않는다.

### 실행 순서와 대기 중 할 일

```text
TK-MVP-05-01 기존 요구사항/미결 감사
  ├─ 02-01/02 정지 시험 설계·최소 시험 수단 준비
  ├─ 03-01 → 03-02 → 03-03 → 03-04 거리 데이터·검사·인수 이미지
  ├─ 04-01 장비 확보 / 04-02 외부 온도 관측 설계
  └─ 05-02 확인된 활성 미결 보완(다른 준비 작업과 병행)
인수 이미지 확정 → 02-03/04 실제 명령 유실 정지 검증
→ 04-03/04 한정된 주행 외부 온도 관측
→ 03-05 1 m 거리 비교
→ 05-03/04/05 전체 증거·재현·인수 마감
```

거리 TEL 확장으로 firmware가 바뀔 수 있으므로 전용 실물 정지 시험은 **그 이미지가 확정된 뒤** 수행하도록 배치한다. 이후 관련 경로를 다시 바꾸면 영향이 있는 검증만 갱신한다. 온도계 대기 중에는 요구사항 감사·거리/로그 계약·정지/온도 시험 설계를 진행한다. 현재 같은 조건의 네 방향/놓음/탭 전환을 전부 다시 하는 계획이 아니다.

### 일자별 실행안 — 2026-10-19 시작

**계획 가정:** KST 기준10/19(월) 시작, 하루 약2시간의 작업 블록이다. 오늘은 저녁이므로30~60분의 감사/정리만 배치한다. 사용 가능 시간은 확인되지 않았으므로 이 시간은 배치 가정이며 날짜별 완료 약속이 아니다. 주말에도 같은 작업 블록을 쓰는 초안이다. 모든 행은 PLANNED이며 새 실행 결과를 뜻하지 않는다.

**목표:** 10/28(수) MVP 인수 검토, 10/29~30 보완 여유. GM-1312 구매/수령·부속 준비와 기존 활성 미결의 분량은 미확정이다. 10/19 첫 감사에서 실제 미결을 확인한 뒤10/20 계획을 재조정한다. 전류 센서/ADC 작업은 이번 일정에 넣지 않는다.

| 날짜 | 작업 블록·연결 태스크 | 그날 남길 결과/완료 기준 |
| --- | --- | --- |
| **10/19(월)** 30~60분 | `TK-MVP-05-01` 현재 MUST·증거·제외 이력 대조. GM-1312 준비 상태/예상 확보일은 확인되는 대로 기록 | 활성 미결·기존 증거 연결·후속/제외 근거 표. 실물 선행 조건과 이번 일정의 수정 필요점 식별 |
| **10/20(화)** 약2시간 | `TK-MVP-03-01` 거리 모델·단위/기준점·필요 실측, `TK-MVP-02-01` 정지 시험 조건 정의. `TK-MVP-04-02` 온도 기록표/조건 설계 시작 | 거리 환산/로그 계약 초안, 마지막 유효 명령/trigger/정지 관측 기준. TK-MVP-05-02 활성 미결은 영향/선행 순서로 배치 |
| **10/21(수)** 약2시간 | `TK-MVP-03-02` 전반: 실제 누적 count 가용성 확인, STM count·시각·reset/boot 계약과 사용자 입력/저장본 검토 | STM 데이터 경로와 단위/부호/리셋 처리 검토 결과. 이미 구현된 부분은 재작성하지 않음; 전체 데이터 경로 완료와 구분 |
| **10/22(목)** 약2시간 | `TK-MVP-03-02` 후반: ESP parser/JSON·브라우저 저장 로그 연결. `TK-MVP-02-02` 기존 시험 수단 대조·최소 주입/관찰 수단 준비 | count/시각이 보존되는 통신/저장 계약과 사용자 저장본. 메시지 길이·호환성·정지 시험 수단의 준비 상태 |
| **10/23(금)** 약2시간 | `TK-MVP-03-03/04` 변경 영향 PC 검사 → 사용자 두 보드 빌드/플래시 → 새 데이터/zero·기준점 확인. `TK-MVP-04-02` 온도 관측 절차 마감 | 검사 결과, 인수 이미지/소스 기준점, READY/IDLE·새 로그 확인. 실패 시 다음 실물 회차를 진행 상태로 넘기지 않음 |
| **10/24(토)** 약2시간 | `TK-MVP-02-03/04` 그 이미지에서 UART 유실/명령 timeout 전용 실물 시험·분석. 필요 거리 상수 실측은 정한 절차로 보완 | 같은 회차의 마지막 명령·TEL·실제 궤도 정지/복구 근거와 요구사항 판정. 미결은 원인/다음 작업으로 남김 |
| **10/25(일)** 약2시간, 장비 조건부 | `TK-MVP-04-01` 확보/사용 확인 후 `TK-MVP-04-03/04` GM-1312 외부 온도 관측·분석 | 선언한 짧은 주행의 위치/시간·주위 온도·PWM/CPS·최고 관측값/상승량·기준 비교. ADC 불필요. 미수령 시 아래 대체 작업 |
| **10/26(월)** 약2시간, 정지·기본 온도 판정 조건부 | `TK-MVP-03-05` 1 m 실제/추정 거리 비교와 오차 분석 | 원시 count/시각·실제 거리·추정 거리·절대/백분율 오차·반복/환경 조건. 보정에 쓴 회차와 최종 오차 검증 회차 구분 |
| **10/27(화)** 약2시간 | `TK-MVP-05-02/03` 확인된 활성 미결·실패 항목 보완과 관련 경로만 재검증, 결과-요구사항 연결 | 열린 항목별 판정/근거 갱신. 인수 선행 조건인 미결은 해당 실물 시험 전에 처리하며 이날까지 뒤로 미루지 않음. 추가 미결 없으면 결과표/README 정리 |
| **10/28(수)** 약2시간, 선행 시험 완료 조건부 | `TK-MVP-05-04/05` README/demo·재현 절차·한계, 전체 적용 MUST·공개 파일 대조 | 최종 인수 판정과 커밋 묶음. 미완료가 있으면 열린 목록과 수정 일정으로 마감하며 날짜만으로 MVP 완료 처리하지 않음 |
| **10/29(목)~10/30(금)** 각 약2시간, 보완 기간 | 장비/실험 지연·발견 결함의 수정/관련 회귀·증거 보완에 사용 | 미결 해소 여부 재판정. 새 기능을 끼워 넣어 사용하지 않고, 보완이 불필요하면 앞선 결과 정리/후속 준비에 사용 |

장비·결함 때문에 날짜가 바뀔 때:

- 온도계가10/25까지 준비되지 않으면 `TK-MVP-04-03`을 장비 대기로 둔다. 그날은 준비된 로그 분석·거리 시험 환경/기록표·README/demo 구성과 TK-MVP-05-02의 가능한 미결을 처리한다. 장비 미확보를 온도 PASS로 대신하지 않는다.
- 온도 회차는 **장비/프로브 준비와 전용 정지 검증이 완료된 뒤 첫 가능한 세션**에 배치한다. 이후 1 m 비교와 최종 인수도 순서대로 이동한다. 배송일을 추정해 고정하지 않는다.
- 첫 감사에서 실물 선행 미결이 드러나거나 코드/PC 검사·빌드/정지 시험이 실패하면 해당 단계의 수정 세션을 먼저 잡고 종속 일정만 이동한다. 기존 제외 항목은 자동으로 재개하지 않는다.
- 인수 이미지 확정 후 count/통신·정지 관련 firmware를 바꾸면 영향 검증을 다시 배치한다. 같은 이미지의 완료 시험을 날짜가 바뀌었다는 이유로 반복하지 않는다.
- 매 세션 끝에는 실제 완료 태스크·증거·열린 항목·다음 날짜의 첫 작업을 progress에 남긴다. 현재 표를 실적표로 덮어쓰지 않는다. 문서 감사와 firmware 입력·실물 작업은 역할 원칙을 따른다.

MVP 인수 뒤 첫 후속의 날짜 후보:

| 날짜 후보 | 스토리/작업 | 시작 조건·산출물 |
| --- | --- | --- |
| **10/31(토)** | ST-POST-01: 보유 BNO08x의 실제 모델/배선·통신/데이터 계약 검토 | MVP 인수 뒤 첫 후속 세션. 기존 헤더 배선을 센서 동작 증거로 확대하지 않음; 초기화/로그 구현 범위 확정 |
| **11/1(일)** | ST-POST-01: 사용자 초기화·수집 코드와 PC/저장본 검사·사용자 빌드 | 앞선 계약/입력 준비 완료. 센서 식별·샘플 시각/유효성·축/부호를 확인할 데이터 경로 |
| **11/2(월)** | ST-POST-01: 정지·정해진 회전의 축/시각·데이터 동작 검증 | 실물 수집 가능 상태. 정상/실패·원시 로그·한계 판정; 이 날짜만으로 IMU 완료 처리하지 않음 |
| **11/3(화)~11/4(수)** | ST-POST-02: 시간/좌표계 정렬과 encoder/IMU 비교 회차 설계·착수 | ST-POST-01 수용 뒤. 비교 방법·필요 실제 회전 기준과 로그/분석 항목부터 정함 |

위 후속 날짜는 MVP가10/30까지 마감되고 필요한 구현/실물 조건이 충족된 경우의 후보이다. MVP가 밀리면 첫 후속 세션도 이동한다. 전류/전압 모니터링·PID·RTOS/CAN·LL·ROS 단계의 일자별 계획은 각 스토리 착수 때 부품/인터페이스·검증 범위를 확정한 뒤 만든다. 현재 근거로 장기 완료일을 확정하지 않는다.

### 후속 에픽과 스토리 초안

아래는 모두 `BACKLOG / POST-MVP`다. 이번 MVP의 선행 조건이 아니며, 착수 시 세부 태스크·수치 기준을 확정한다. IMU 기본 검증을 첫 후속으로 두되, 나머지를 모두 직렬로 완료해야 다음에 갈 수 있는 구조로 만들지 않는다.

| 에픽 | 스토리와 얻는 결과 | 개별 태스크 초안 | 진입 조건 |
| --- | --- | --- | --- |
| EP-SENSOR 센서 관측 | `ST-POST-01` BNO08x 데이터를 믿고 해석한다 | 01.1 실제 배선·센서 식별/통신 계약; 01.2 사용자 init·수집과 축/부호·샘플 시각/유효성 로그; 01.3 정지·정해진 회전 비교로 동작 검증 | MVP 인수 뒤 첫 확장; 보유 IMU 사용 |
| EP-SENSOR 센서 관측 | `ST-POST-02` encoder와 IMU의 회전 차이를 설명한다 | 02.1 시간/좌표계 정렬; 02.2 동일 회차 양 센서·실제 회전 기록; 02.3 오차/지연·슬립 해석과 한계 정리 | ST-POST-01, 엔코더/거리 기준선; 자동 융합·보정은 별도 결정 |
| EP-MON 전기 상태 관측 | `ST-POST-03` 주전원 전압·드라이버 입력 전류를 브라우저/로그로 확인한다 | 03.1 모듈/분압·보호/필터·기준 계측 방법 확정; 03.2 전압/전류 보정·ADC raw/시각/유효성; 03.3 TEL/ESP/UI·로그 통합과 정지 경로 회귀; 03.4 전기 부하/외부 온도 비교 | MVP-014/REQ-MON/T-MON의 기존 후보·기준 사용. 구매/구현 미완료 |
| EP-CONTROL 속도 제어 | `ST-POST-04` 좌우 목표 속도 추종과 직진 변화를 확인한다 | 04.1 측정 속도/target·포화/출력 제한과 지표 정의; 04.2 한쪽부터 feedforward/PI 또는 PID 비교; 04.3 양쪽 step/직진 결과와 reset/정지 검증 | 엔코더 속도 기준선. 전류 모니터링 완료를 무조건 선행 조건으로 묶지 않음 |
| EP-RUNTIME 실행 구조 | `ST-POST-05` STM32 주기 작업과 안전 처리를 FreeRTOS로 분리한다 | 05.1 주기/우선순위·공유 데이터·지연 예산; 05.2 현재 기능을 task/queue로 이관; 05.3 실행 주기/부하와 timeout/정지 회귀 | 기능·시각 기준선, 이관 전후 비교 가능 상태. 기존 ESP-IDF RTOS 사용과 구분 |
| EP-LINK 통신 | `ST-POST-06` CAN으로 command/telemetry를 교환한다 | 06.1 보유 transceiver·종단/배선/USB-CAN 확정 및 단독 통신; 06.2 ID·주기·상태/명령 소유권 계약과 통합; 06.3 단절/복구·정지 검증 | 별도 CAN 검증 단계. 현재 UART production 경로의 전환 영향 재검토 |
| EP-RUNTIME 실행 구조 | `ST-POST-07` 선택한 HAL 경로의 LL 전환 효과를 수치로 설명한다 | 07.1 대상/지표와 HAL baseline 측정; 07.2 한 경로 이관; 07.3 시간·기능/안전 회귀 비교 | 비교할 HAL baseline. 전면 LL 재작성 자체를 목표로 두지 않음 |
| EP-ROS 상위 연동 | `ST-POST-08` ROS 2에서 상태를 보고 기존 안전 경로로 명령한다 | 08.1 timestamp/frame/topic과 ESP 경유 bridge 계약; 08.2 노트북 bridge·시각화; 08.3 기록/재생·명령 유실 정지 | 하위 상태/명령 계약 안정. USART2 bench-only를 production 우회로 사용하지 않음 |
| EP-NAV 자율주행 확장 | `ST-POST-09` SLAM/Nav2 착수 조건을 충족한다 | 09.1 odometry/TF/제어와 센서·컴퓨팅 요구 정의; 09.2 필요한 LiDAR/전원/장착 선정; 09.3 rosbag/SLAM 기초 검증 뒤 Nav2 범위 결정 | ST-POST-08 및 실제 요구사항. Jetson/RealSense 선구매를 전제하지 않음 |

후속 장기 구조의 정본은 [아키텍처 로드맵](../../01_System_Architecture/10_System_Architecture_Roadmap_CAN_RTOS_LL_ko.md)이다. 위 태스크 초안은 구현 완료나 구매 확정이 아니다. 현재 요구사항 감사에서 발생한 추가 작업은 부모 스토리·기존 Requirement/Test ID·종료 조건을 붙여 등록한다.

### 태스크를 진행/완료로 바꾸는 규칙

- 착수 전에 부모 스토리, 산출물, 수용 기준, 필요한 장비와 선행 작업을 적는다. 날짜/시간은 해당 작업 범위를 확정한 뒤 추정하며 과거 전체 시간표를 재사용하지 않는다.
- 코드 저장·PC 검사·사용자 빌드/플래시·실물 시험을 분리해 기록한다. PC PASS로 실물 태스크를 완료 처리하지 않는다.
- `완료`에는 파일/commit 기준점과 log·결과표·보고서 중 해당 증거를 연결한다. 전체 스토리는 모든 필수 태스크와 수용 기준을 충족할 때 닫는다.
- 새 결함은 발생 조건·원본 로그·영향 스토리를 연결하고 관측하지 못한 원인/해결을 확정하지 않는다. 단발 정상 회차로 간헐 정지의 영구 해결을 선언하지 않는다.
- firmware나 배선이 관련 경로에 영향을 주면 그 태스크의 검증만 다시 연다. 완료한 과거 시험을 일괄 재시작하지 않는다.
- 현재 상세 지시는 이 백로그가 아닌 해당 태스크의 실행 절차/코드 안내에서 제공한다. 외부 도구에 이슈 게시·구매·보드 실행을 수행한 목록이 아니다.

## 과거 시작점 — 2026-10-17

당시 Wi-Fi nonzero core/PAGE 통합·mode0 사용자 빌드/플래시와 NZ-01~04 모터 분리 UART/DIR/PWM 선택 시험을 마감했다. [보고서38](../verification/38_WiFi_Nonzero_Disconnected_Motor_Bench_Closeout_2026-10-17_ko.md)의 범위이며, 당시의 실제 주행 대기 상태는10/18 지상 증거로 갱신됐다. 아래 자료의 다음 행동을 현재 지시로 재사용하지 않는다.

## Index — 날짜별 자료와 과거 입력 이력

| Date range | File | Scope |
| --- | --- | --- |
| 2026-10-16~17 / UR-02 및 선택 UR-03 마감 | [UR 실행 계획](2026-10-16_WiFi_UART_Recovery_Bench_Plan_ko.md) | 부분 CMD/ARM·정상 복원 및 AC-S 선택 실물 근거는 보고서36/37 |
| 2026-10-16 / 입력·PC·빌드·플래시 완료 | [UART 줄 폐기 코드 안내](2026-10-16_UART_Line_Cancel_Recovery_Code_Guide_ko.md) | STM CAN 폐기·ESP DISARM prefix, saved PC513+17+42, 실물 수용 경계는 보고서36 |
| 2026-10-13 / 저장본 C42·JS27·ESP 빌드 확인 | [main·브라우저 전체 교체 안내](2026-10-13_WiFi_ARM_CMD_Main_Integration_Code_Guide_ko.md) | HTTP/ticket·UART/seq·ACK/TEL·기한/취소·zero-only UI. 실제 main 저장/PC 검사·ESP 빌드 확인, 새 플래시/보드 시험 대기 |
| 2026-10-12 / 후보PC17 PASS | [UART executor 입력 안내](2026-10-12_WiFi_ARM_CMD_Executor_Code_Guide_ko.md) | ticket 접수·한 슬롯·송신 계획·취소/우선 DISARM·결과. 사용자 파일/ESP 빌드·main 연결은 미실행 |
| 2026-10-12 / 수정 대기 | [ARM/CMD state 일괄 수정 안내](2026-10-12_WiFi_ARM_CMD_State_Corrections_ko.md) | 최초 실제 저장본 컴파일 실패 0 tests/ERROR1. 정확한 위치·이유·header/source 완성본, CMake 유지 |
| 2026-10-11 / 후보 PC27 PASS | [ARM/CMD state 코드 안내](2026-10-11_WiFi_ARM_CMD_State_Code_Guide_ko.md) | phase·기한·ACK/TEL·취소/정지 판단. 사용자 파일 미입력·실제 저장본/전체 ESP 빌드·실행 adapter 미검증 |
| 2026-10-11 / PC·빌드 확인 완료 | [ARM/CMD owner 코드 안내](2026-10-11_WiFi_ARM_CMD_Owner_Code_Guide_ko.md) | 한 연결 예약·control ID·대조/취소. 실제PC9 PASS, ESP 전체 빌드 성공 사용자 확인. FSM/기한·UART 미연결 |
| 2026-10-10 작성 / 10/11 빌드 확인 | [ARM/CMD ticket 코드 안내](2026-10-10_WiFi_ARM_CMD_Ticket_Code_Guide_ko.md) | 연결/용도·150ms·한 번 소비·번호 소진. 실제PC12 PASS, ESP 전체 빌드 성공 사용자 확인 |
| 2026-10-10 / parser 확인 완료 | [ARM/CMD parser 코드 안내](2026-10-10_WiFi_ARM_CMD_Parser_Code_Guide_ko.md) | 새 header/source·CMake, 실제PC15 PASS·ESP 빌드 성공 사용자 확인. UART 미연결 |
| 2026-10-10 작성 / 10/11 갱신 | [Wi-Fi ARM/CMD 제어 계약](2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md) | 지속 소유권·ticket·기한·priority DISARM·zero-only, AC-H/B/S 기준. 기초 모듈PC15/12/9 PASS·ESP 빌드 성공 사용자 확인, 제어 실행 경로 미연결 |
| 2026-10-08 계획 / 10/10 마감 | [두 보드 W5 PING/DISARM 계획](2026-10-08_W5_Two_Board_PING_DISARM_Plan_ko.md) | 당시 준비/실행 순서 보존, 완료 근거는 report34의 비구동 범위 |
| 2026-10-06 작성 / 10/11 갱신 | [ESP 학습·W4·W5 통합 계획](2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md) | W4/W5 완료와 ARM/CMD 기초 모듈 이후 상태/기한·실행 연결의 경계 |
| 2026-10-02 / 코드 입력 | [ESP 단독 WebSocket 안내](2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md) | 실제 앱 적용 후보, HTTP 작업 예약·버퍼 수명·재접속·WS-1~4 |
| 2026-10-01 / 작업 범위 | [노트북·ESP 작업 계획](2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md) | ESP 단독 Wi-Fi, ADC/CAN PCB 설계 범위, 문서 수정과 코드 이해 |
| 2026-10-01 / 코드 입력 | [ESP 단독 Wi-Fi·HTTP 코드](2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md) | AP/STA 설정, 앱 전문·이벤트/HTTP 설명, 사용자 입력·검토·빌드 순서 |
| 2026-09-30 / 완료 시험의 입력 이력 | [M1 active DISARM 안내](2026-09-30_M1_Active_DISARM_Console_Code_Guide_ko.md) | 당시 입력 블록. 실제 관측은 report32, 현재 앱의 대체 소스나 재실행 지시가 아님 |
| 2026-09-30 / 완료 시험의 입력 이력 | [M1 물리 S0 정지 안내](2026-09-30_M1_Physical_S0_Stop_Console_Code_Guide_ko.md) | 당시 S0 관측 절차. report32 범위와 정식 T-ESTOP-007 BLOCKED 구분 |
| 2026-09-30 / 완료 시험의 입력 이력 | [M1 3초 구동 안내](2026-09-30_M1_Three_Second_Run_Console_Code_Guide_ko.md) | A/B 제한 구동의 시작 코드 이력. 현재 UART bridge의 M2_RUN 소스 상태와 구분 |
| 2026-09-29 / 당시 재개 계획 | [휴식 후 방향 확인 계획](2026-09-29_Next_Session_M1_Direction_and_Bench_Closeout_ko.md) | 당시 M2 역방향 이미지와 A 방향 확인 계획. 후속 완료 결과는 report32 |
| 2026-09-27 / 입력 이력 | [M1 수동 1회 시험 코드](2026-09-27_M1_One_Shot_Console_Code_Guide_ko.md) | 당시 WIP와 최초5% 안내. 최신 실행 설정은 현재 인수인계를 따름 |
| 2026-09-23 / 검사 이력 | [엔코더 조정부 검사와 다음 작업](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md) | 당시 저항·도통·전원 PASS; 후속 실제 엔코더 결과는 reports 29/30 |
| 2026-09-22 / 후속 결과 있음 | [전원 경로와 T005A 계획](2026-09-22_Next_Session_Power_Path_and_T_ESTOP_005A_Plan_ko.md) | 실행 결과는 report 27; 전체 T005A는 PARTIAL |
| 2026-09-16 plan / updated through 9/19 | [납땜 체크리스트](2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md) | 당시 배선·무전원 검사·마감 기록; 후속 T004 결과는 report 26 |
| 2026-09-11 plan / updated through 9/19 | [`2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md`](2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md) | UART·측정 헤더 도면 검토 및 제작 이력 |
| 2026-09-08 / T004 완료 이력 | [T004 실행 절차](2026-09-08_T_ESTOP_004_Firmware_PWM_Integration_Runbook_ko.md) | 당시 MDD B+/모터 분리 조건의 절차; 9/22 report 26에 latch/reset/wire-open/PWM/safe restore PASS 기록 |
| 2026-09-05 / Gates 1~4 completed, historical predecessor | [`2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md`](2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md) | Corrected K2 mapping, S0-A/S0-B independence and conditioned PC7 baseline; Gate 5 moved to the 2026-09-08 runbook |
| 2026-09-03 / execution closed, historical | [`2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md`](2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md) | 2026-09-05에 실행 종료; rail/U1 subset과 후속 control-only results는 progress에 보존, K2 frozen coordinate table은 bottom-view 해석 오류로 비정본이며 남은 formal gates는 새 runbook으로 이관 |
| Project-wide / current | [전체 MVP 로드맵](00_Project_Master_Plan_To_Final_MVP_ko.md) | 현재 단계·작업별 완료 조건·MVP 종료선, 펼쳐 읽는 상세 Gate와 과거 계획 |
| 2026-08-26 to 2026-09-15 / historical | [`2026-08-26_Pre_Arrival_Schedule_ko.md`](2026-08-26_Pre_Arrival_Schedule_ko.md) | Historical dated schedule: `P-01~P-09`, received-subset screen, HOME-first checkpoint, milestones and buffers |
| 2026-08-25 / 범위 결정 이력 | [`2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md) | 당시 P-01~P-09와 MVP/후속 범위 결정; 완료 상태와 재개 순서는 위 최신 시작점을 따름 |
| Completed 2026-08-18 | [`2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md`](2026-08-16_next_session_perfboard_active_dir_pwm_plan_ko.md) | Historical completed runbook: final perfboard MDD10A-input active 6-step, hook-0 restore and all-LOW evidence |
| 2026-06-08 to 2026-06-10 | [`2026-06-08_to_2026-06-10_hardware_execution_plan.md`](2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A multimeter inspection, Wednesday parts follow-up |
| 2026-07-10 | [`2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md) | STM32 + ESP32 board-only UART command bridge plan |
