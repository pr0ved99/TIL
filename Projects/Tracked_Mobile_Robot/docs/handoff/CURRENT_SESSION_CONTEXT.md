# Current Session Context

Last updated: **2026-10-20 — 누적 count 실물·14톱니 정정 모델·offline 분석기36 PASS**. 실제 하중의 기본 주행·정지와 외부 온도는 MVP, 정량 전류/전압 ADC 모니터링은 후속이다. 최신 지상 주행 근거는10/18, 최신 공중 count/전후진·놓음 검증은10/20이다.

**10/20 세션 마감:** 사용자가 오늘 작업을 여기까지 마치고 자고 일어나서 이어가기로 했다. 다음 세션 첫 작업은 `TK-MVP-03-04`의 현재 STM/ESP source·기존 build 산출물 식별값 대조와 인수 기준점 정리다. 새로 빌드/플래시하기 전에 현재 증거를 먼저 확인한다. 이후 전용 유실/timeout 정지 → GM-1312 외부 온도 → 조건 충족 후 지상1m 순서다. 완료한 count/부호·기본 방향·놓음 시험은 자동 반복하지 않는다. 종료 전원 분리/궤도 재조립은 미보고이며 마감 문서가 물리 종료를 대신하지 않는다. Git/Notion 게시 결과는 오늘 progress의 마감 기록과 실제 원격 상태를 따른다.

## 현재 기준

- **최신 MVP 종료선:** 기본 주행/정지·엔코더 이동량/1 m·외부 GM-1312 온도 관측과 증거 정리다. MVP-014/REQ-MON/T-MON은 DEFERRED / POST-MVP, MVP-015/T-LOAD는 ADC 없이 수행하는 외부 온도 범위다. [마스터 플랜](../plans/00_Project_Master_Plan_To_Final_MVP_ko.md)과 [검증표](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)를 따른다. 기존 PASS/PARTIAL과 IMU 첫 후속 순서는 유지한다.
- **최신 완료 범위:** 궤도 장착·배터리 단독 지상에서 전진 → 좌회전 → 전진 → 우회전 → 후진의 선택 수동 주행 묶음 완료. [최종 회차](../../assets/logs/wifi_link/2026-10-18_ground_combined_trim_run01/observations.json): 실제 저장 소스에 대응하는 TEL PWM 144/150, -200/+200, 144/150, +200/-200, -140/-150; 매 동작 사이 zero CMD/PWM과 양 CPS0 확인. 사용자 방향 전환·놓음 정지 문제없음 확인. 전체 MVP·정밀 주행 수용 완료로 확대하지 않는다.
- 현재 STM: 일반 CMD cap150‰, 순수 회전(vx=0,w≠0) cap200‰. mapper에서 직진(w=0,vx≠0) 왼쪽만 전진 gain960‰·후진930‰와 부호 대칭 반올림. ESP/PAGE PWM 허용 ±200; 요청 vx±100/w±500은 실측 속도가 아니다. zero-only0, UART 시험 mode0, STM 시험 hook0 유지.
- 15% 지상 회전에서 오른쪽 CPS가 지속 0이었으나 공중에서는 양방향 지속 회전했다. 회전20% 적용 후 [지상 회차](../../assets/logs/wifi_link/2026-10-18_ground_turn20_run02/observations.json)에서 오른쪽 CPS 지속·실제 양방향 차체 회전을 확인했다. 오른쪽이 느린 차이는 남는다. 궤도 구성 변경이나 회전용 고정 속도비 보정은 하지 않는다.
- [직진 보정 전](../../assets/logs/wifi_link/2026-10-18_ground_linear15_baseline_run01/observations.json) → [보정 후](../../assets/logs/wifi_link/2026-10-18_ground_straight_trim_run01/observations.json), 시작500ms 제외·source TEL 중복 제거 후 오른쪽 CPS 부족분: 전진4.1→2.5%, 후진7.1→4.9%. 사용자 휨 감소 확인. 현재960/930 계수 유지; 배터리·부하 변화에서의 정밀 보정은 미검증이다.
- 통신 후속 설정: WS TEL50ms, 브라우저 CMD80ms(티켓/ACK 조건 충족 시), STA WIFI_PS_NONE. TEL250ms·SOURCE200ms·STM300ms 제한은 유지했다. [PS_NONE 회차](../../assets/logs/wifi_link/2026-10-18_unexpected_stop_psnone_run01/observations.json)와 이후 주행에서 누르는 중 비정상 정지는 관측되지 않았으나, 과거 간헐 정지의 영구 해결을 뜻하지 않는다.
- 20% 첫 회차는 STM±200 직후 ESP STM_STATE(reason8) 정지. [원본 및 역어셈블](../../assets/logs/wifi_link/2026-10-18_ground_turn20_stale_esp_run01/observations.json)에서 로컬 ESP 구 ELF가 ±150임을 확인했다. 사용자 재빌드 뒤 ELF±200과 후속 런 지속 회전 확인. 소스 저장·빌드·플래시·실물 검증을 구분한다.
- 최종 boot4138288356/session3, DISARM request374/seq3518121891 OK. 마지막 TEL DISARMED/DISARM·CMD/PWM/CPS0·drop/err0. 종료 전원 분리는 미보고다. PC 결과: [20% 저장본 검사](../../assets/logs/wifi_link/2026-10-18_turn20_saved_review/esp_main.json), [직진 보정 저장본 native C](../../assets/logs/wifi_link/2026-10-18_straight_trim_saved_review/stm_profile.json). 사용자 STM 빌드·플래시/다운로드 검증 후 실물 PWM으로 보정 적용 확인.
- 최신 요약은 [10/20 진행 기록](../progress/2026-10-20_progress.md)을 먼저 읽는다. 아래 이전 gate의 cap10%·공중 시험 전·USB 공급·속도 보정 미실행 표현은 당시 이력이다. 사용자 요청으로 이번 Git 게시 묶음을 정리한다. 실제 게시 결과는 git log와 원격 branch 비교로 확인하며 Notion 반영은 별도다.

## 물리 상태와 장비

- **10/20 초기 전원 정정 이력:** 앞선 정지 count/FAULT 관측 시 LiPo는 분리돼 있었고 S0는 원래 해제 상태였다. 이후 사용자가 LiPo 연결·S1 ON을 보고했다. S2 조작·새 STM TEL은 아직 미보고다. 현재 ESP control_state는 같은 boot1794076624/session1의 IDLE·owner0·reason0. ESTOP_ACTIVE는 STM sense 입력 판정이며 S0 물리 잠금으로 단정하지 않는다. LiPo 분리와 입력 활성의 회로 인과는 이 보고만으로 실측 확정하지 않는다. 이후 S2 복원·reset·공중 전후진까지 진행했으며 아래 최신 상태를 따른다.

- **최신 시험 구성:** A=왼쪽 M1/JENC_1, B=오른쪽 M2/JENC_2, 모터 차체 장착·정상 M1/M2/JENC/J5 연결, 두 궤도 각각 한 링크 단축 상태 유지. 사용자는 sprocket 헛돎 방지 때문에 이 구성을 기준으로 진행하기로 했다. 지상 부하 시험을 수행했으며 장력/마찰의 기여는 정량 분리하지 않았다.
- **배터리 단독:** XL4015 #1의 보드 전원용2핀 두 개 복원, STM JP5 E5V(JP1 기존 OPEN), USB/LA 분리 안내 후 무선 주행 회차 진행. 사용자 LiPo 연결·S1 ON·S0 해제·S2 누름·STM RESET 후 READY/DISARMED/IDLE 확인. 전원 차단 완료 보고는 없다. 마지막 개별 셀 보고3.94/3.97/3.95V(시험 전 값, 현재 전압 아님); LiPo 알람·감독하 운용 유지. 10/19 재판단으로 관측용 ADC와 자동 저전압 정지는 후속이다.
- STM 만능기판, ESP 외부 UART 점퍼. PA9→GPIO18, GPIO17→PA10, 115200/8N1.
- LA 4MHz: D0=JDBG_UART Pin1/PA9 TX, D1=Pin2/PA10 RX, D4=JDBG_CTRL_1 Pin2/PB6, D6=JDBG_CTRL_2 Pin2/PC7, D7=JDBG_CTRL_2 Pin1/PB7. NZ-02부터 D2=JDBG_CTRL_1 Pin1/PC8(left DIR), D3=JDBG_CTRL_1 Pin3/PC9(right DIR). D2/D3를 과거 ESP UART 관측 채널로 디코드하지 않는다. D5 미사용. GND=JDBG_UART Pin3.
- 사용자 지시: 보유 기록에 없는 장비는 없는 것으로 계획. 별도 USB-UART를 전제하거나 다시 묻지 않는다. PC7 FAULT를 우회하지 않는다.
- **10/19 계측 장비 대조:** XL830L·일반 프로브, FX2 8채널 LA, LiPo 셀 알람과 과거5V buck 시험에 사용한 KEWEISI USB Detector/USB 저항 부하 보드가 기록돼 있다. 사용자10/1 이후 추가 구매 없음 확인. 별도 온도계·DC 클램프·션트/RC 와트미터·절연 악어클립/고정 전류 리드는 없는 것으로 계획한다. USB 장비 모델/정격과 XL830L 정확도/허용 전류 측정 시간은 미확정이며3S 전체 전류 측정에 적용하지 않았다. [계측 목록](../../00_Project_Charter/02_Component_Inventory.md#계측-장비--2026-10-19-기록-대조), [10/19 기록](../progress/2026-10-19_progress.md) 참조. GM-1312 선택과 전류/전압 ADC 검토를 거쳐, 전류/전압 회로·기준 계측 검토는 후속이며 온도 관측/잔여 인수와 분리한다.

## 최신 연동 상태 — 2026-10-20

**최신 모델 정정:** 실물 톱니 **14개** 확인. 연속6개 링크 동일 형상1→6의5간격48.1~48.3mm에서 피치9.62~9.66mm, 대표값9.64mm. 기존 실측1560counts/output rev 유지 →134.96mm/rev, 좌우 공통 초기 k=1687/19500≈0.08651282mm/count. 대표값은 측정 범위 중간값이며 수동 checkpoint 회귀 보정값이 아니다. 윗쪽 직선 궤도 수동 이동100/150mm의 좌우 평균 환산은100.138590/150.532308mm다. 기존12톱니 가정이 공통 scale 차이를 대부분 설명한다. 공중 궤도 이동 비교이며 지상 차체 거리 정확도·슬립/전체 MVP PASS는 아니다. [정정 모델](../../assets/logs/wifi_link/2026-10-20_track_geometry_14t_revision/geometry_model.json)·[검증](../../assets/logs/wifi_link/2026-10-20_encoder_distance_14t_review/validation.json). unittest36·CLI3·거부2 PASS, 입력 hash·구간 판정·count 불변. 분석기 기본값 갱신, 공중 평균 전진213.729923/후진-244.052667mm. 아래12톱니/34개 검사/180.54mm 등의 수치는 정정 전 이력이다. firmware/출력 gain 변경·새 보드 시험 없음. 다음은 현재 source/실행 이미지의 인수 기준점 대조·고정이다. 이후 전용 유실/timeout 정지·GM-1312 외부 온도·조건 충족 후 지상1m 순서로 진행한다. 이미 통과한 공중 count/부호 시험은 자동 반복하지 않는다. 현재 전원/분해·재조립 상태는 미확인이다.

누적 count 정지 전달/reset·ARM 구간 생성·전후진/놓음 정지·재ARM 비영 누적 보존 subset 확인 완료. 공중 전진0/0→2567/2374(ARM525914493), 후진 새 ARM525914564에서 같은 시작값 유지→끝점-358/-343(delta-2925/-2717), DISARM525914655 OK 뒤 구간/끝점 보존. 사용자 양쪽 실제 전후진/놓음 정지 확인, STM drop/err0. 마지막 CMD 취소1건은 수동 DISARM 접수 직후 outstanding 취소이며 구동 중 비정상 정지로 세지 않는다. [최신 후진 근거](../../assets/logs/wifi_link/2026-10-20_encoder_count_reverse_air_run01/observations.json). 최종 DISARMED/DISARM·CMD/PWM/CPS0. LiPo/S1 ON·S0 해제·S2 복원·양쪽 공중 지지로 시험했으며 종료 전원 분리는 미보고. 추가 사용자 보고 p≈9.5mm/61개/둘레≈579mm/두께≈5mm, 산술61×9.5=579.5mm. 초기 좌우 k=12×9.5/1560≈0.0731mm/count, 이상적1m delta≈13,684count를 [기록](../../assets/logs/wifi_link/2026-10-20_track_pitch_initial_model/geometry_model.json)했다. 측정 방법/오차·반대편 수·전원 차단/분리/재조립은 미확인이고 지상 보정은 미실행. offline 거리 분석기 구현/검증 완료: [사용법](../../03_Firmware/tests/README.md#관찰-v5-구간-거리-분석--2026-10-20), [검증](../../assets/logs/wifi_link/2026-10-20_encoder_distance_analysis_review/validation.json). unittest34·CLI3·거부2 PASS, 실제 공중 전진 평균180.536538mm/후진-206.150000mm 상당값. ACK/정지 기준·끝점과 연속성을 검사하고 끊긴 ARM은 전체 제외한다. 다음은 현재 source/이미지 인수 기준점 대조. 인수 이미지 고정·전용 정지/온도/지상1m·전체 MVP는 별도 미완료다.

## 다음 작업

**업무 실행 목록:** `TK-MVP-05-01` [미결 감사](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#tk-mvp-05-01-감사-결과--2026-10-19) 완료. REQ-MECH-002는 기존10/17 사용자 근거로 PASS 정합화, REQ-MECH-003/T-MECH-002는 확인된 subset과 미기록을 나눠 PARTIAL로 정정했다. 활성 미결·제외 조사·후속은 감사표에 보존했고 전체 안전/MVP PASS로 올리지 않았다. 현재 `TK-MVP-03-01`은 실물14톱니·피치9.62~9.66mm(대표9.64mm)로 초기 모델을 정정했다(좌우0.08651282mm/count, 지상 보정 전). 지름38mm는 휠 몸통 보고치다. 병행 `TK-MVP-03-02`는 STM 오타 수정 후 [실제 저장본 native14 PASS](../../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/stm_saved_after_typo_fix.json)와 사용자 STM build/Run 성공 보고까지 확인했다. ESP는20필드 입력 후 저장본 PC 검사가 통과했고 실물 수신 검증 전이다. [ESP 입력6개 블록](../../01_System_Architecture/17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md#esp-누적-count-입력-묶음--2026-10-20)의 후보 count/JSON/PAGE·기존 제어 검사가 통과했고 ESP 수정3곳(buffer512, negative, encoder_valid의 독립 저장)을 확인했고 [실제 저장본 count/PAGE·제어 PC 검사](../progress/2026-10-20_progress.md#esp-수정-후-실제-저장본-pass)가 통과했다. 사용자 ESP build/flash/monitor 보고 후 부팅·handshake는 성공했으나 STM의 `left_count=ld,right_count=ld`로 TEL343건 모두 거부됐다. nano.specs/libc_nano long-long printf 미지원에 대응하는 [STM 문자열 변환 입력 안내](../../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/stm_nano_format_typing.md)와 후보 PC 검사를 준비했다. 이후 사용자 STM 입력·저장본 검사·실행 이미지 갱신 후 실제 정지 TEL/브라우저 count 수신을 확인했다. 당시 FAULT/ESTOP_ACTIVE였으며 최신 공중 시험 종료값은 DISARMED/DISARM이다. count는 int64/JSON10진 문자열, sample/ARM 유효성·(ESP boot_id, ARM UART seq) 구간 기준을 사용한다. 측정 flag=false 자체로 제어 TEL을 거부하지 않는다.

**날짜 배치:** [10/19 시작 일자별 초안](../plans/README.md#일자별-실행안--2026-10-19-시작)은 하루 약2시간, 오늘 감사30~60분 가정이다. 10/23 인수 이미지·10/24 정지·10/25 조건부 온도·10/26 조건부1 m·10/28 인수 검토, 10/29~30 보완 기간을 목표로 한다. 사용자 가용 시간·GM-1312 납기·활성 미결 분량은 미확정이며 첫 감사 뒤 수정한다. 계획된 작업을 완료로 표시하지 않았고 외부 일정 등록은 없다.

**계측 최신 상태:** 온도계는 사용자 선택 **BENETECH GM-1312**다. 합계5만 원 제한은 철회됐지만 사용자는 **8만 원대UT210E를 비용으로 거절**하고 **아날로그 전류 센서→STM32 ADC**를 제안했다. 현재 방향은센서/ADC 관측·UART/ESP/브라우저 로그이며 Codex 우선 후보는 **Pololu #5241 ACS71240KEXBLT-030B3(±30A,3.3V)**다. 국내 모듈 표시가VAT 포함9,240원, 배송/부속/실재고/납기는미확정. 첫 위치는K1 87→센서→MDD B+의드라이버 입력 분기, ADC 후보는PC0/ADC1_IN10이다. `.ioc`에ADC/PC0 배정은 없고PA0/PA1은엔코더 사용 중이다. PC0의보드/기판 연결·모듈/RC·샘플링·영점/감도·TEL 계약 검토가 남는다. 모델 구매·코드/배선 변경·새 측정은없다. UT210E와이전5만 원/션트 비교는이력이며 [10/19 ADC 방향 검토](../progress/2026-10-19_progress.md#stm32-adc-전류-센서-방향-검토)를 따른다. 자동 과전류 차단/배터리 저전압/rail 진단의구현 완료를 뜻하지 않는다.

1. 선택 수동 주행 검증 묶음은 완료했다. 현재 전진 gain960/후진930·일반15%/회전20%를 기준으로 유지한다. 같은 조건의 방향/놓음/탭 전환 시험을 자동 반복하지 않는다.
2. 5피치48.1~48.3mm·실물14톱니 확인과 PC 기본 모델 정정을 완료했다. 다음은 현재 source/실행 이미지의 인수 기준점 대조·고정이다. 이후 전용 유실/timeout 정지·GM-1312 외부 온도·조건 충족 후 지상1m 순서로 진행한다. 이미 통과한 공중 count/부호 시험은 자동 반복하지 않는다. 현재 전원/분해·재조립 상태는 미확인이다.

## 기록과 작업 원칙

- 사용자 요청으로 문서·Git·Notion 최신화를 진행한다. 게시 결과는 [10/17 기록](../progress/2026-10-17_progress.md)의 마감 항목과 실제 git log를 따른다.
- branch `agent/dual-encoder-bringup`. Hello World tracked build 산출물과 LA `Session 2` 임시 파일은 기존 작업으로 보존하고 이번 커밋에서 제외한다.
- firmware 입력·STM/ESP 빌드/플래시·물리 조작은 사용자, PC 검사·문서는 Codex. 사용자 요청 없이 subagent 금지.
- 별도 esp32_uart_bridge M2_RUN hook1U는 현재 Wi-Fi 앱이 아니다. 자동 플래시하지 않는다. 과거 자료 전체 대신 이 문서·최신 progress·해당 보고서만 읽는다.

## 이전 단계 이력

아래 문단의 미입력·미연결·미실행·현재 표현은 해당 날짜의 이력이다. 위 현재 기준과 충돌하면 위 내용을 우선한다.

### 10/18 초반 gate의 당시 기준과 재개점 — 과거 이력

- **10/18 최신 전원 전환 보고:** 사용자: 보드 전원용 2핀 두 개 복원, STM JP5를 U5V에서 E5V로 변경. 아래의 보드용2핀 분리·USB 공급 표현은 이전 시험 상태다. 이번 배터리 단독 부팅·USB/LA 제거 완료·전원 투입 결과는 아직 미보고다. LiPo 알람 관측: 전체11.8V, 셀3.94/3.97/3.95V. 문서의 기존 standalone 기준은 XL4015 #1 → STM E5V/GND 및 ESP 5V/GND, JP1 OPEN, 두 보드 USB 분리다.

- UR-02 부분 CMD/ARM 폐기·첫 DISARM 복구와 UR-03 AC-S01~08의 선택한 zero-only 실물 시나리오를 마감했다. 모터 동력 차단 상태에서 UART·실제 PWM·PC7을 대조했다. 전체 오류 분기·nonzero 구동·전력/기계 안전·주행 수용은 별도다.
- 첫 읽기: [보고서37](../verification/37_Zero_Only_ACS_Bench_Closeout_2026-10-17_ko.md)과 [10/17 진행 기록](../progress/2026-10-17_progress.md). 회차별 observations.json과 원시 캡처 링크가 연결돼 있다. 이전 UR-02는 보고서36, 실패 이력은 보고서35를 따른다.
- AC-S02: A 유효 ticket을 B가 쓰면 거부되고 A 동일 ticket은 성공; B ARM 거부 뒤 A 유지; B DISARM에 의해 A 정지. B ARM은 폐기·만료된 ticket 범위이고 owner-only 분기를 분리한 실물 증거는 아니다.
- 다른 연결 DISARM helper의 INCOMPLETE 원본은 유지한다. UART에서 B 정지 ACK/TEL이 A 보호 DISARM보다 먼저 확인돼 핵심 시나리오는 완료다. 수정 helper revision2의 PC 검사는 통과했으며 추가 실물 회차는 미실행이다.
- 현재 ESP WIFI_UART_PARTIAL_TEST_MODE=0U, STM 시험 switch14개=0U. 정상 이미지 복원·수동 ARM/zero/정지는 AC-S04/S06/S08 후속 회차로 확인했다. 마지막 boot3570331004, A6/B7/control8, 최종 DISARM573834470 ACK/TEL·IDLE/DISARMED.
- 소스 hash는 보고서37에 있다. 사용자 빌드/플래시·실물 관측과 소스 식별을 구분하며 플래시 바이너리 readback은 없다.
- 미해결: AC-S06 restore run01의 수동 정지 전 자동 정지/명령 전달 공백(사용자 포커스 전환 없음), ESP reset D1 transient, 이전 UART 양끝 단발0.25µs 차이. 후속 PASS로 원인이 해결됐다고 쓰지 않는다.
- 후속 T005A 관측: 모터 4선·MDD 제어 5핀 분리, B+ 복원 조건에서 S2 후 12.03V, S0 후 5초 1.43V/30초 0.58V. S0 해제 뒤 현재값 0.47V, S1 OFF 10초→ON 5초/S2 미조작 뒤 MDD 0.46V·Bar 12.03V. 사용자 DMM 보고이며 잔류 원인·rail-off 수용 기준/단자 적합성은 미확정, 전체 T005A PARTIAL. 상세와 수치의 경계는 [10/17 진행 기록](../progress/2026-10-17_progress.md#후속-t-estop-005a-전압-관측-마감)을 따른다.

- **최신 물리 상태 — 10/18 궤도 장착 후 사용자 보고:** 궤도 연결 후 LiPo 연결·S1 ON·S0 해제·S2 누름, B+↔B−12.58V. STM RESET 후 DISARMED/BOOT, ESP READY/IDLE. 두 모터는 차체에 장착돼 있고 이제 궤도도 연결됐다. 정상M1/M2/JENC·J5 연결 변경 보고는 없다. #1보드용2핀 두 개 분리·절연 유지로 안내했다. 직전 지시에는 차체 공중 지지가 포함됐으나 이번 메시지에서 지지 여부를 별도로 명시하지 않았으므로, G6-01 ARM 전 양쪽 궤도가 바닥에 닿지 않는 조건을 명시한다. 과거 궤도 미연결·충전 휴식 전원 분리를 현재로 사용하지 않는다.
- **10/17 전압 관측 종료 뒤 전원 분리 완료 사용자 확인:** S0 잠금·S1 OFF·LiPo 분리, STM/ESP USB와 LA USB 분리. **K1 87→MDD B+는 복원된 연결 상태**, B− 공통 GND 유지. 모터 전력선 4개 분리·각각 절연, MDD 제어 5핀 분리, #1 보드용 2핀 두 개 분리·절연. #2·엔코더·sense 배선 변경은 보고되지 않았다. 이전 AC-S 때의 “B+ 분리”를 현재 상태로 재사용하지 않는다. 종료 후 rail 0V를 실측한 것은 아니다.

**최신 재개점:** [G6-01 run02](../../assets/logs/wifi_link/2026-10-18_g6_01_tracks_forward_run02/observations.json) PASS. 새run02.sr는4MHz/17.969초/SHA012ada50415c09a415fdfc7938f84a9809feeeb839754ff77595ef112a3b5095로이전20kHz파일과별개다. ARM1/CMD72/DISARM1·ACK74 모두일치하고새ESP로그와매치. 양PWM약10%·양CPS양수전진→ARMED zeroCMD/PWM0→DISARM전CPS0→최종DISARM122/seq4005823094. 마지막PWM후9.108초재출력없음·PC7LOW·UART오류0·drop/err0. 사용자두궤도전진회전/이후정지보고. 정밀기계정지시간·거리와장력/간섭전체수용/지상주행을뜻하지않는다. run01의20kHz/놓음경로미확보PARTIAL과원본을그대로보존한다. 다음은같은공중상태에서후진·좌/우회전의궤도방향과놓음정지확인이다. 현재궤도장착·정상M1/M2/JENC/J5·통전뒤종료미보고, vx±100/w±500·cap10%/mode0. 속도보정후속/사용자제외범위유지. 새firmware수정·빌드/플래시·Git/Notion게시는없다.

1. 이번 선택 zero-only 시험 묶음은 완료. 코드/배선 변경·새 실패·사용자 요청 없이 같은 회차를 반복하지 않는다.
2. **최신 사용자 결정:** 직전 재검토 항목은 이미 넘어가기로 한 범위다. Codex가 문서의 미결 표시를 근거로 다시 꺼낸 것은 잘못된 재개였다. 사용자가 먼저 요청하지 않으면 다시 언급·조사하거나 다음 작업의 진행 조건으로 걸지 않는다. 과거 검증 판정을 PASS로 바꾸는 의미는 아니다.
3. **G4C 장착 확인 묶음 완료:** 사용자가 섀시 가조립에 “가조립 맞음”, 만능기판·XL4015 2개·MDD10A 고정/휨·납땜면 간격/도체 접촉·STM/ESP USB 및 단자 접근성에 “모두 문제 없어”라고 보고했다. [검사표](../../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md)에 사용자 확인 범위로 기록했다. 치수/제작 revision 식별과 전체 기구 수용으로 확대하지 않는다. 같은 장착 확인은 반복하지 않는다.
   **10/17 합의 반영:** 사용자는 LiPo 알람 보유와 감독하의 시험 운영 방침에 동의했다. `REQ-POWER-004`는 셀 알람·작업자 감독·경고 시 즉시 수동 정지/시험 종료로 구체화했다. 보유만 확인됐으며 설정·정상 동작·회차 적용은 미확인이다. PA4/PB0 ADC와 자동 저전압 정지는 후속 PCB/post-MVP로 둔다. [Wi-Fi nonzero core 세 파일](../plans/2026-10-17_WiFi_Nonzero_Core_Code_Guide_ko.md)과 [PAGE/모드 표시 두 블록](../plans/2026-10-17_WiFi_Nonzero_PAGE_Code_Guide_ko.md)은 사용자 저장·PC 검사와 mode1 ESP 빌드/플래시·화면 확인을 마쳤다. **현재 actual header는 WIFI_CONTROL_ZERO_ONLY=0U**, UART 시험 mode는0U다. 이전 저장본 PASS 대비 firmware 변경은 header의1U→0U 한 줄뿐이다. 새 PC 검사에서 현재 mode0 core13개/adapter6개, 임시 mode1 회귀59+3+42+6개, 브라우저66개, PAGE C 초기화와 negative control3개 PASS. 증거는 [mode0 저장본 검증 폴더](../../assets/logs/wifi_link/2026-10-17_nonzero_mode0_saved_review/)다. **mode0 ESP 빌드·플래시와 `IDLE · 방향 입력 모드` 확인은 사용자 보고로 완료**다. NZ-01 전진 UART/PWM과 NZ-02 후진·회전 UART/DIR/PWM은 위 증거로 확인됐다. NZ-03/04 nonzero 중 정지 경로도 위 보고서38 범위에서 완료했고, 실제 모터 구동은 별도다. 사용자는 변경 부분을 이해하고 싶다고 명시했으므로 변경 함수·전후 동작·이유를 함께 설명한다.
4. 사용자는 확인 절차가 너무 빡빡하다고 지적했다. 준비·측정을 과도하게 한 동작씩 나누지 말고 함께 할 수 있는 단위로 묶는다. 결과에 따라 다음 동작이 달라질 때만 멈춘다. 확인된 연결·전원 상태를 다시 묻지 않는다.
5. 검증 이력과 현재 실행 범위를 구분한다. 사용자 최신 결정을 우선하고, 과거 미결 목록을 자동으로 다음 작업에 복원하지 않는다. 정밀 파형/시간·ADC 진단 T006 및 단일고장 확장 005B는 post-MVP다.

### ARM/CMD 설계 작업 — 구현 상태와 구분

- 소스 대조로 W5 요청500ms와 STM timeout300ms의 차이, 반복 ARM의 타이머 갱신, CMD-only watchdog을 확인했다. 초기 CMD 목표100ms·STM timeout300ms·제어 TEL age250ms를 별도로 제안했다.
- 제어 연결1개를 ACK 뒤에도 유지하고, 연결/control ID에 묶인 일회용150ms ticket으로 늦게 도착한 입력을 거부한다. 접수와 UART 송신 직전에 마감/소유권을 재검사한다. 초기 수치는 실측 전 설계값이다.
- ARM→zero CMD ACK/TEL→ACTIVE. 끊김·만료·fault는 허가/미송신 큐 폐기와 priority DISARM. 재접속 시 자동 ARM/CMD0, 새 수동 ARM 필요. 첫 구현은 zero-only다.
- PC7은 pull-up/HIGH=active다. sense 회로 없는 낱개 보드의 FAULT를 우회하지 않는다. AC-B는 거부 경로, AC-S는 정상 conditioned sense 조건의 별도 비구동 Gate다. AC-H 전체는 미완료며 AC-B/S는 미실행이다.
- ESP ticket은 이미 UART에 보낸 프레임을 회수하거나 STM RX replay ARM+CMD를 막지 않는다. STM epoch/seq freshness와 실제 nonzero 정지/주행 증거는 별도다.
- 설계 단계에서는 소스 변경이 없었고, 이후 사용자가 parser `.h/.c`와 CMake를 입력했다. ESP 전체 빌드 성공은 사용자 확인이다. 새 플래시·하드웨어 상태 변경은 미보고다. W5 마감·후속 구현 시작 기준은 `d9bf801`이다.10/11 기초 모듈·검사·문서27개를 `f791843`으로 커밋·푸시했고 원격 branch hash 일치를 확인했다. 이 마감 결과를 후속 문서 커밋에 기록하며 최신 HEAD는 `git log -1`과 [진행 기록](../progress/2026-10-11_progress.md)을 따른다.
- 후속 parser 저장본 검토: 안내 후보15 PASS → 최초 저장본0 tests/ERROR1 → 사용자 수정본 실제 PC15 PASS 순서다. source의 `boll`·변수명2곳·함수 정의 뒤 `;`·숫자 반복 조건이 수정됐다. Codex가 펌웨어를 직접 수정하지 않았다. owner/deadline/FSM 연결은 다음 구현이다.
- ticket 모듈은 후보12 PASS → 최초 저장본0 tests/ERROR1 → 사용자 수정본 실제 PC12 PASS 순서다.46줄 `UINT32_MAX`·74줄 `purpose`가 수정됐고 header/CMake는 맞다. boot/session/용도/세대·149/150ms·한 번 소비/취소·번호 소진 등을 검사했다.10/11 ticket 포함 ESP 전체 빌드 성공은 사용자 확인이며 원본 로그/바이너리 hash는 미제공이다. 새 플래시·보드 동작은 미확인이다. owner/FSM·UART 송신/큐/경합은 미연결이며 pool은 연결 종료 때 초기화하지 않는다.
- owner 모듈은 후보9 PASS·입력 전 기본0 tests/SKIP1 이후 사용자 저장본 실제9 PASS다. header/source·CMake 네 source 등록은 맞고 공백/끝줄 차이만 있다. 연결 한 개 예약·control ID 비재사용·취소/식별 대조와 저장된 ticket 소비 뒤 기록 유지 범위다.10/11 owner 포함 ESP 전체 빌드 성공은 사용자 확인이며 원본 로그/바이너리 hash는 미제공이다. 새 플래시·보드 동작은 미확인이다. 예약/대조 성공은 제어 허가가 아니며 STOPPING/BLOCKED에서 재예약하지 않도록 후속 FSM이 검사해야 한다. ACK/TEL·기한/큐·UART TX0·경합은 미증명이다.

### W5 마감 상태 — 10/10 당시 이력

- ESP `esp32_wifi_link`의 `/ws`가 상태 JSON과 PING/DISARM 입력·notice/result를 전달한다. 사용자가 코드 입력·빌드·플래시·모니터 성공을 보고했고 실제 왕복/거부/timeout/복구를 확인했다.
- strict TEXT128byte, 같은 연결 요청 간격500ms, 전체1개 소유권, 사용자 응답500ms·자동 retry 없음. UART 담당 태스크가 송신/응답을 소유하고 HTTP는 요청/결과를 값으로 전달한다.
- `command_notice`의 접수/거부와 `command_result`의 완료를 구분한다. 마지막 결과는 요청자별이며 TEL과 독립이다. 브라우저 추가 대기3000ms 만료는 결과 확인 불가로 표시한다.
- STM TEL100ms / WS 상태**100ms** / TEL stale500ms / 브라우저 상태 무응답4000ms. 아래 W4의1000ms는10/8 당시 이력이다.
- W5-24: 같은 boot1058366263, 재접속 후 송신/결과 대기 초기화,3초 새 QUEUED/TX 없음 사용자 확인. 이후 **수동 PING 요청1 OK**, age3ms, TEL28982, STM1908300ms, seq3438979499, READY·fresh·FAULT/ESTOP_ACTIVE, PWM/CPS0·drop0·err0.
- 요청5 TIMEOUT은 요청4 TIMEOUT 뒤 별도 수동 클릭이었다는 사용자 정정을 반영했다. 빠른 연속 클릭이 두 요청을 접수했다는 증거로 쓰지 않는다.
- 실제 PAGE JS57 PASS·실제 C 함수 PC21 PASS. 실제 늦은 UART 주입·동시 태스크 경합·무선 시간 보장·모터 안전 시험을 대신하지 않는다. 상세 W5-01~24 증거 경계는 보고서34를 따른다.
- [마감 manifest](../../assets/logs/wifi_link/2026-10-10_w5_closeout/manifest.json): 공개 소스 snapshot·로그 발췌·화면/사용자 확인 전사. 원본 PNG/전체 serial/binary hash는 미기록. C SHA256 `dfe9a97e77453378a4f5a0cc64b3dfa642244c93ec6d6259cb4742bba8d5d2b4`.

### W4 마감 상태 — 10/8 당시 이력

- 당시 STM·ESP 모두 만능기판 장착, 각각 USB 전원, LiPo 미연결 사용자 확인. 당시 미보고였던 USB 마감과 최신 상태는 위10/10 W5 기준을 따른다.
- 현재 ESP 앱은 `esp32_wifi_link`, STA. 이번 IP는 `192.168.0.17`이며 다음 DHCP/COM 번호로 고정하지 않는다. GPIO17→STM PA10, STM PA9→GPIO18, 공통 GND, 115200/8N1.
- STM TEL100ms / ESP WS 상태1000ms / TEL stale 기준500ms / 브라우저 무응답4000ms. 실제 TEL14필드와 ESP 수신 age를 사용하며 배터리 값은 null/사용 불가다. Dummy Task는 사용하지 않았다.
- DISARM ACK→PING/PONG→READY, ACK/PONG 누락의 최대3회 실패, 실패 후 TEL 수신, STM RESET stale/복구와 WS 재접속을 확인했다. 실제 저장본 브라우저 검사25 PASS는 C 빌드·전기적 증거와 구분한다.
- 마지막 화면: boot_id=102159163, READY, connected=true/stale=false, TEL age51ms, tel_count90, FAULT/ESTOP_ACTIVE, PWM/CPS=0/0, drop0, err1. 모터 구동 허가나 전체 MVP 완료를 뜻하지 않는다.
- PA10 내부 pull-up은 `usart.c` USER CODE에 유지. STM PONG 누락 시험 hook과 stale PONG hook은0U로 복원·확인했다. USB 모니터 재실행 시 boot_id가 바뀌었으나 err은 증가하지 않았다는 사용자 정정을 반영한다.
- 리셋 때 GPIO17 기동 LOW·0xFC/BAD_TYPE/err 증가와 이후 정상 복구를 캡처3개로 기록했다. 완전한 원인/FE·NE·ORE 확정은 아니며 W4에서 추가 조사는 멈췄다. PCB 기동 핀 검토와 구동 중 재기동/통신 유실은 후속 범위다.
- READY/FAILED는 이번 ESP 부팅의 응답 확인 이력이며 TEL freshness와 독립이다.10/8 당시 `/ws`는 상태 전달용이었고, 이후 W5 입력/결과 구현은 위 최신 기준을 따른다.
- 원본/발췌 식별값·화면 전사·마감 소스 hash는 [마감 manifest](../../assets/logs/wifi_link/2026-10-08_w4_closeout/manifest.json). W4의 소스 hash 기록은 byte snapshot 보존이나 플래시 바이너리 동일성을 증명하지 않는다. W5의 별도 byte snapshot과 구분한다.

## 이전 완료 범위와 전원·기구 이력

A의 실제 전진 방향, A active DISARM, A 물리 S0의 PWM/엔코더 관측, A/B 각각10%·3초 제한 구동을 완료했다.
**이 시험들을 처음부터 반복하지 않는다.** 10/1에는 노트북·ESP로 Wi-Fi를 검증했고, 10/2에는 로봇 배선을 재연결한 뒤 기본 전원·접점 점검을 진행했다.

- 먼저 [10/2 진행 기록](../progress/2026-10-02_progress.md)을 따른다. 6핀 방수커넥터/JESTOP 유지, F1→S1→Bar+와 K1 30/F2 분기를 사용자 확인했다.
- 지속 단락음 없음, 연결 도통과 S0/S2 접점 정상 보고. Bar+ 12.11V, XL4015 #1/#2 5.02V/4.95V. MDD는 S0 잠금0.50V→해제만0.48V→S2 후12.11V→S0 잠금5초1.0V/30초0.57V였다.
- S1 OFF 10초 후 **Bar 0.67V**, S0 해제/S1 재투입/S2 미조작 5초 후 **MDD 0.52V**. 낮은 전압 관측을 0V·전체 rail-off PASS로 확대하지 않는다. 잔류 원인/최종 수용 기준은 미확정이다.
- 최종 S1 OFF·S0 잠금·LiPo 분리 안내 뒤 사용자가 "분리했고"라고 답해 전원 분리 완료를 확인했다. 같은 마감 질문을 반복하지 않는다.
- `전선정리` 사진5장을 확인했고, 10/3에 원본을 이름 변경 후 프로젝트의 [배선 사진 폴더](../../assets/photos/wiring/README.md)로 이동했다. 배선 정리1차 마무리로 판단하며 금속 슬롯/노출 S1 단자 보호, 현가·궤도 간섭과 홀더 고정은 조립 마감 때 확인한다. 사진상 모터는 섀시 장착, 궤도·STM/ESP 본체는 미장착이다. 자세한 범위는 당일 기록을 따른다.
- 10/2 전원 점검 때는 새 모터 구동·펌웨어 변경·UART 통합 검증을 하지 않았다. 후속 실제 UART/W4 결과는 위 10/8 마감 상태를 따른다.

1. [10/1 마감 기록](../progress/2026-10-01_progress.md)과 [report32](../verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)에서 완료 범위를 확인한다.
2. 전류·온도는 미측정이다. 저가 계측 구성은 정확도/판매품 확인이 부족해 구매 확정하지 않았다.
   현재10% 무부하의 작은 공급전류를 20A/50mV 션트+XL830L로 정밀하게 잴 수 있다고 단정하지 않는다.
3. [10/1 노트북·ESP 작업 계획](../plans/2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md)은 Wi-Fi·PCB·문서 이해 범위다. 당시 AP HTTP W1 접속·W2 반복 갱신·W3 연결 해제/재접속, 재플래시 boot_id 변경·같은 부팅의 재접속 유지도 확인했다. [10/1 AP 기록](../progress/2026-10-01_progress.md#wi-fi-ap-실측--w1w2w3-결과)과 [10/2 최초 STA 보고](../progress/2026-10-02_progress.md#공유기-sta-연결-확인)는 당시 이력이다.
   10/6 HTTP·두 탭 WebSocket 예제 확인 뒤 실제 앱으로 전환했고 W4는 위 최신 결과로 완료했다. [HTTP 입력 안내](../plans/2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md)와 [ESP 단독 WS 안내](../plans/2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)는 이전 단계 코드이며 현재 실행 소스를 대신하지 않는다. 개인 비밀번호는 출력하지 않는다.
   AP·공유기 STA·노트북 핫스폿 가능성은 유지한다. ADC/CAN PCB는 인터페이스·회로 확정부터 진행하며 새 PCB CAD/제작은 미완료다.

10/2 점검 종료 뒤 전원 분리 완료는 **사용자 확인**이다. 재개 시 새 전원 연결/배선 변경이 있으면 그 상태를 기준으로 진행한다.

## 이전 실행 이미지와 코드 이력

- 10/10 마지막 ESP는 `esp32_wifi_link`: 실제 TEL/STARTUP·WS 상태, 브라우저 PING/DISARM·notice/result·버튼. ARM/CMD 입력은 미구현이다. 사용자 빌드·플래시와 마지막 수동 PING OK를 확인했다.
- STM은 PA10 pull-up·PONG 시험 hook0U와 기존 명령 계약을 유지했다. 시험은 각 USB·LiPo 미연결이며 현재 두 USB 분리 완료다. GUI의 READY는 구동 허가가 아니다.
- 아래는 **별도 `esp32_uart_bridge`의 9/30 소스·마지막 모터 시험 이력**이다. 현재 ESP 플래시 앱으로 해석하지 않는다. 기존 수동 hook의 소스 복원은 별도이며 W4 완료로 UART 전체 release를 PASS 처리하지 않는다.

- UART bridge: BRIDGE_M2_RUN_TEST_ENABLED=1U, 이전 자동 hook4개=0U.
- HELP: RESET_ESTOP, M2_RUN, STOP. M2 양수10%, 3초 제한, 500 ms STM watchdog, 100 ms CMD 재전송.
- CMD(50,+250,500)→left0/right100 permille. 3초 절대 종료 시각은 재전송으로 연장하지 않는다.
- TEL stale250 ms·응답200 ms·무회전500 ms 감시, DISARM 뒤600 ms 정지 관측.
- 부팅당1회, 성공/실패/STOP 뒤 잠금. 자동 ARM/구동 없음. all-hooks0 정상 이미지 복구는 미실행.
- 사용자가 M1→M2 전환만 이번 한 번 Codex 직접 수정을 허용했다. 이후 펌웨어는 기본 사용자 입력 방식.
- 마지막 계약 검사30 PASS/1 FAIL(default-off 검사, 수동 hook1U). 마감 중 소스 수정·빌드·플래시 없음.
- 현재 소스/캡처 해시는 [manifest](../../assets/logs/motor_output/2026-09-30_single_motor_run/manifest.json).
  소스 해시는 마감 작업본이며 각 시험의 바이너리 해시를 대신하지 않는다.

## 완료한 범위

| 항목 | 관측과 경계 |
| --- | --- |
| A 양수10%/300 ms | A 실제 전진 후 정지, B 정지. 이전 A 전진 관찰 공백 완료 |
| A active DISARM | 실제 전진/정지, UART frame end→마지막 PWM 하강364.44 μs. 기계 정지 시간이 아님 |
| A 물리 S0 | PC7 활성 이후 PWM 재발 없음, FAULT/ESTOP_ACTIVE·CPS0. 정밀 rail/기계 정지 시간·거리 미검증 |
| A 3초 | PWM2.99828925 s, 약19.059 kHz/10%; 원시1432 ticks=CPS 적분, B 정지 |
| B 3초 | PWM2.988788 s, 약19.040 kHz/10%; 원시1384 ticks=CPS 적분, A 정지 |
| 범위 | 두 모터 섀시 분리, 각각 단독. 주행·동시 구동·전류/열·폐루프 정속은 미검증 |

B의 구동 중 CPS 상승을 정속 PASS로 쓰지 않는다. A/B 3초 원시 전이에는 반대/동시2비트 전이가 없었다.
S0 시험의 마지막 엔코더 전이는 PC7 최초 HIGH 후127.32 ms이며 분해능 내 관측이다.
500 ms 안에 사람이 S0을 누르도록 한 절차는 짧았다는 사용자 지적을 반영했다. 다음 수동 개입 시험은 충분한 조작 시간을 둔다.
기존 T004 PASS·전체 T005A/T-MOTOR-003 PARTIAL, 정식 T-ESTOP-007 BLOCKED 유지.
기존 기준을 충족한 것으로 소급하지 않으며 관측 범위만 report32에 보존한다.

## 9/30 로봇 시험 연결 기준 — 10/2 전원 점검 조건은 당일 기록 참고

| 항목 | 기준 |
| --- | --- |
| 왼쪽 | A / M1 / JENC_1 / TIM3 PB4(A)·PB5(B) / left; Motor+→M1A, Motor−→M1B |
| 오른쪽 | B / M2 / JENC_2 / TIM5 PA0(A)·PA1(B) / right; Motor+→M2A, Motor−→M2B |
| STM 방향 정의 | 왼쪽 forward LOW/reverse HIGH 유지; **오른쪽 forward HIGH/reverse LOW로 보정 후 양방향 확인** |
| PWM / DIR | M1 PB6/PC8, M2 PB7/PC9 |
| 엔코더 | JENC Pin1~4=GND/B/A/AUX5V; 네 채널1kΩ 직렬+15kΩ 풀다운; TIM3 부호 반전/TIM5 유지;1560 counts/rev |
| 보드 배치 | STM은 만능기판 장착. ESP는 UART USB 간섭 때문에 기판 밖 |
| ESP 연장 / 콘솔 | GPIO17·18·GND만 대응 ESP 헤더로 연장. UART 표기 USB 하나로 공급·UART0 콘솔, 현재COM5/115200 |
| USB 전원 조건 | XL4015 #1 보드용2P 두 개 분리·절연, STM JP5=U5V/JP1=OPEN, #2 AUX5V와 공통GND |
| 전력단 | 두 버스바, MDD B+=K1 87/B−=GND16AWG, K1주선14AWG; Littelfuse F1/F2=10A/1A |

두 모터는 섀시에서 분리한 상태다. 교차 연결은 원래 A/M1·B/M2로 복원했다.
실제 ESP의 왼쪽 BOOT 표기=EN, 오른쪽 RESET 표기=GPIO0였으므로 보통 보드의 버튼 이름으로 재부팅을 단정하지 않는다.
도면·완료한 조정부 검사는 [report28](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md),
손회전 방향은 [report29](../verification/29_Vehicle_Side_Mapping_Correction_and_Hand_Rotation_Check_2026-09-26_ko.md)를 따른다.


## 남은 선택과 사용자 선호

- 전류/온도 구매 후보는 저가 구성의 정확도 문제를 확인해 조건부/보류로 정정했다. 구매·측정 없음.
- Wi-Fi·PCB·문서 이해를 선택했다. W4 상태 전달과 W5 비구동 PING/DISARM은 완료했다. 무선 zero-only ARM/CMD는 위 현재 기준을 따르며 PCB CAD는 미실행이다.
- 무선 제어는 별도 입력/유효시간/연결 유실 검증이 필요하다. PC 명령 유실 시 과거 명령을 계속 재송신하지 않도록 설계.
- 기존 최상층 만능기판·납땜 부품 유지 선호. ADC/CAN 소형 PCB 설계 범위를 정리했으며 외곽/실측/제작 결정은 아직 미확정.
- 확장 PCB 후보는 회로/커넥터/실측이 확정된 부분부터. 전체 MCU 캐리어 교체와 모터 주전류 PCB 통합은 별도 후속 범위.
- 소스 입력·두 보드 빌드·플래시·물리 작업은 사용자. Codex는 설명·저장 파일 검토·Python 검사·문서 보조.
- 결과는 작업 마감 때 묶어 기록. 사용자 요청 없이 subagent/전체 대화 아카이브를 열지 않는다.

## 저장소

- branch agent/dual-encoder-bringup. W5 시험 기준 HEAD는 `77b6a06cdc87c4653177baf68b6484d7120e681c`이며 manifest에 보존했다. 최신 커밋은 `git log -1`로 확인한다.
- 10/10 후속 사용자 요청으로 W5 코드/검사/증거/문서를 커밋·원격 반영 대상으로 정리했다. 상세 범위는10/10 진행 기록의 Git 갱신 절을 따른다. 기존 Hello World tracked build 산출물 변경은 커밋에서 제외하고 작업 폴더에 보존한다.
- 완료한 문서 개편과 과거 핀/전력 이력은 [9/30 기록](../progress/2026-09-30_progress.md), report25~31에 보존돼 있다.
