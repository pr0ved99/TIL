# MVP 기능 회로도 — 실제 부품 기록과 과거 Candidate 표기 대조

2026-11-07 마감. 11/6 작업 후 사용자가 앞서 보류했던 과거 회로도 최신화를 명시적으로 위임했다. 대상은 기존 MVP 기능 회로도 `Tracked_Mobile_Robot_Wiring_RevB`이며, 새로운 실물 작업 없이 저장된 관측·구매·조립 기록을 도면에 반영했다.

## 1. 반영 결과

**확인된 부품명/값 12개와 XL4015 #1 출력 net 이름, 상태표·핀 대응·제목란을 갱신했다.** 48부품·전체35net(활성33+명시적 미연결2)의 핀 구성과 전기적 연결은 유지했다. net 이름은 `XL4015_1_5V_OUT_CANDIDATE`에서 `XL4015_1_5V_OUT`으로 바꿨고 연결된 핀 집합은 동일하다.

| Ref | 이전 표기 | 현재 표기 | 근거와 경계 |
| --- | --- | --- | --- |
| S0 | A22NE-M-PD02-N_CANDIDATE | SF2ER-E2R2B | report19 실물 body. 주문 -A 접미사 사진 확인은 별도 |
| S2 | REENABLE_MOMENTARY_NO_CANDIDATE | ABW110G | report19/24 입고·조립·제한 동작 |
| K1 | 12V_COIL_POWER_RELAY_TBD | V23134J1052D642 | 선정26/report24. 정격·단자 release와 구분 |
| K2 | TX2-12V_CANDIDATE | TX2-12V | report18/24. 기능 핀과 실물 핀은 아래 대응 |
| F1 | FUSE_TBD | Littelfuse_10A | report30 사용자 확인. report18의257 각인과287 주문 차이는 OPEN |
| F2 | 0.5A_TIME_DELAY_CANDIDATE | Littelfuse_1A | report30 사용자 확인. exact SKU/시간-전류 coordination은 OPEN |
| U1 | VO617A-3_CANDIDATE | VO617A-3 | report19 입고/report25 conditioned 경로 |
| R13 | 680R_CANDIDATE | 680R | report18 측정670.1Ω. 명목값을 측정값으로 교체하지 않음 |
| R14 | 10k_CANDIDATE | 10k | report18 측정9.97kΩ, report25 conditioned 경로 |
| J13 | XL4015_1_OUT_CANDIDATE | XL4015_1_OUT | report25 전원 경로. 기능 인터페이스 핀 순서는 유지 |
| J17 | K1_COIL_INTERFACE_TBD | K1_COIL_INTERFACE | 기능 접속점, 실제 하네스 품번 확정으로 해석하지 않음 |
| J19 | K1_MAIN_CONTACT_INTERFACE_TBD | K1_MAIN_CONTACT_INTERFACE | 주전류 외부 인터페이스. 단자 정격 release 미완료 |

## 2. K2 기능 핀과 실물 핀 대응

KiCad의 `Relay:Relay_DPDT` 기능 심벌을 유지했다. 아래 실물 번호는 기존 report24·선정26에 기록된 TX2 **BOTTOM VIEW** 기준이며 새 배선 지시가 아니다.

| 회로도 기능 핀 | 실물 핀 | 역할 |
| --- | --- | --- |
| A1 | 1 (+) | K2_COIL_P |
| A2 | 12 (-) | GND |
| 11 → 14 | 9 COM → 8 NO | 자기유지, 8은 K2_COIL_P |
| 21 → 24 | 4 COM → 5 NO | K1 허가, 5는 K1_COIL_P |
| 12 / 22 | 여기서 실물 번호로 사용하지 않음 | 기능 심벌의 미사용 NC 접점 |

회로도의 `12` NC 표기를 실물 coil pin12와 혼동하지 않는다. 일반 릴레이 심벌에 실제 PCB 풋프린트를 바로 배정하면 안 된다. K1 `85–86` 병렬 P6KE16CA 설치 기록은 주석에 반영했으며 clamp 소자를 이번 기능 netlist에 새로 추가하지 않았다. 실제 조립 경로는 VeroRoute와 report24/25를 함께 따른다.

## 3. 검증과 문서 경계

- KiCad10.0.5, 기존 프로젝트 설정: 적용 후 ERC 오류0·경고0. 기존 무시 규칙4개 유지, 새 제외 추가 없음.
- 변경 전후 모든 net의 ref/pin/pinfunction/pintype는 이름 변경1건을 대응시키면 동일하다. 내장 심벌·배선·접합점·미연결 표시도 동일하다.
- 부품 메타데이터는 표의 Value 12건 외 동일하다. 원본8월 checkpoint 상태표는 새 현재 문서 상태표로 교체하고 이전 원본/PDF에 보존했다.
- 엔코더/기능 커넥터 원래 토폴로지는 유지했다. 실물과의 전면 대조를 마친 as-built 도면이나 부품 정격 승인으로 확대하지 않는다.
- Shield R1/R2의 `12k candidate`와 미선정 풋프린트는 현재 설계 미결이므로 유지했다. 역사적 RevA/RevC·8월 exports와11/6 applied.pdf를 최신 도면으로 덮어쓰지 않았다.

[현재 MVP PDF](../assets/logs/pcb_design/2026-11-07_cad_closeout/mvp_current.pdf) · [현재 Shield PDF](../assets/logs/pcb_design/2026-11-07_cad_closeout/shield_current.pdf) · [백업·재현·검증](../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md).

## 4. 원본 근거

- [부품 선정26](../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md)
- [report18: F1 각인·K2·저항](../docs/verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md)
- [report19: S0·S2·VO617·F2·TVS 입고](../docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md)
- [report24: 조립·K2 극성·clamp](../docs/verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md)
- [report25: XL4015·conditioned sense](../docs/verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md)
- [report30: F1/F2 제조사·정격 보고](../docs/verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md)

새 실물·빌드·플래시 없음. 전체 MVP PARTIAL/OPEN, T005A PARTIAL/T007 BLOCKED 유지.
