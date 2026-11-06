# MVP 기능 회로도 재배치 — 2026-11-06

**최신 도면 안내 · 2026-11-07:** 이 폴더는 당시 배치 스냅샷으로 보존한다. 현재 회로도와 ERC·부품 표기 최신화 결과는 [11/7 CAD 마감](../2026-11-07_cad_closeout/README.md)을 따른다.

사용자가 이전 MVP 작업에서 작성한 회로도의 정돈을 Codex에 위임했다. 전기 설계 README에서 기능 배선 기준으로 지정한 `Tracked_Mobile_Robot_Wiring_RevB`를 대상으로 원본에 적용했다. 현재 학습 중인 Monitor Shield와 별개 작업이다.

## 결과와 파일

- [편집 가능한 원본 회로도](../../../../09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevB/Tracked_Mobile_Robot_Wiring_RevB.kicad_sch)
- [적용 후 PDF](applied.pdf) · [전체 PNG](applied.png)
- [변경 전 PDF](before.pdf) · [원본 백업](before.kicad_sch)
- [검증 결과](validation.json) · [적용 후 ERC](applied_erc.json) · [적용 후 netlist](applied_netlist.xml)

기존 A4 도면을 A2 한 장으로 확장하고 전원/DC-DC, 모터 제어, 엔코더, E-stop 제어, E-stop 감지, UART, 테스트 포인트, 당시 상태표, 도면 주석의9개 구역으로 정돈했다. 실제 부품48개와 전원 심벌19개의 위치를 옮겼으며, 관련 라벨·와이어·접합점·X도 함께 옮겼다. 긴 net 이름과 저항이 겹치던 구간의 배선을 늘리고 필드 위치·회전·글자 크기를 정리했다.

## 확인한 범위

| 항목 | 결과 |
| --- | --- |
| 전체 부품과 연결 | 48부품·35net의 값/풋프린트/데이터시트/참조/UUID와 ref·pin·pinfunction·pintype 목록 동일 |
| 심벌 데이터 | 전원 포함67개, 내장 심벌 정의·인스턴스·원래 방향·필드 내용 동일 |
| 기존 도형 | 와이어32·접합점11·라벨86·미연결 X2의 개수/UUID 보존 |
| 원래 주석·표제 | 기존4개 주석과 상태표 본문, `RevB-WIP`·원래 날짜/표제 보존 |
| ERC | KiCad10.0.5, 원본/후보/적용 후 모두 오류0·경고0 |
| 시각 검토 | 전체와 기능별 확대에서 라벨/필드/본문을 확인. 원본 적용 후 PDF 렌더링은 검토 후보와 픽셀 동일 |
| 보호 파일 | Monitor Shield·다른 CAD/프로젝트/라이브러리와 기존 무관한 변경을 포함한68파일 SHA256 동일 |

ERC의 기존 제외 규칙4개(`single_global_label`, `four_way_junction`, `simulation_model_issue`, `footprint_filter`)와 프로젝트 설정을 유지했다. ERC0/0은 그 설정에서의 결과다. 제외를 추가해 통과시킨 것이 아니다.

## 해석 경계와 다음 작업

도면은 **기존 RevB-WIP의 전기 내용을 보존한 시각 정돈본**이다. 원래 상태표에는 이후 실물 진행으로 달라진 내용이 있어 `HISTORICAL` 표시를 추가했다. 이후의 K2 실물 핀 해석 수정·엔코더 조정부 등과 현재 실물을 일치시킨 최종 도면으로 승인한 것은 아니다. 현재 실물 상태는 [최신 인수인계](../../../../docs/handoff/CURRENT_SESSION_CONTEXT.md)와 해당 검증 보고서를 따른다.

현재 사용자 학습 재개점은 Monitor Shield 배터리측7부품 배치 확인 후 **전단 분압·필터 배선**이다. 이번 작업에서 Shield 회로/PCB·펌웨어·실물은 수정하지 않았고 MCU 빌드/플래시는 실행하지 않았다. Git/Calendar/Notion 마감 게시도 별도다.

## 재현

`rearrange_mvp.py`는 `before.kicad_sch`에서 후보를 생성하며 원본을 덮어쓰지 않는다. 이전 Shield 작업의 보존형 S-expression 파서를 재사용한다. `moves.json`은67개 심벌의 이전/이후 좌표다.

`validate_and_apply.py --apply`는 후보 시각 검토 후 사용한 적용 절차다. 원본 해시가 최초 백업과 일치할 때만 적용하므로 이미 적용한 원본에 재실행하면 중단된다. 현재 검증 영수증을 유지하려면 불필요하게 재실행하지 않는다. 실행 명령/CLI 출력은 `initial_commands.json`, `candidate_commands.json`, `validation_commands.json`에 저장했다.
