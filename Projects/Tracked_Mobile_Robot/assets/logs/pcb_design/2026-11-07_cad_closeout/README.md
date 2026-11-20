# 11/6 CAD 작업 — 11/7 마감 근거

사용자 직접 Shield 작성/검사와 Codex 위임 도면 최신화를 구분한다. 이번은 문서/CAD 마감이며 새 실물·MCU 빌드/플래시는 없다.

| 최신 결과 | 파일 |
| --- | --- |
| Shield 전압2채널/공통 완성본 | [PDF](shield_current.pdf) · [netlist](shield_current.xml) · [ERC](shield_current.erc.json) |
| MVP 기록 부품 최신화 | [PDF](mvp_current.pdf) · [netlist](mvp_current.xml) · [ERC](mvp_current.erc.json) |
| 전압 연결표 적용 근거 | [적용 표](applied_voltage_nets.csv) |
| 변경·보존 검증 | [validation.json](validation.json) · [원본 작업 상태/무관19파일](baseline.json) |
| 게시 영수증 | [publication.json](publication.json) |
| 재현 코드 | [update_cad.py](update_cad.py) · [update_docs.py](update_docs.py) |

Shield40부품+PWR_FLAG2개, 전체91net(활성22+의도적미연결69). MVP48부품·전체35net(활성33+미연결2). 두 도면 모두기존설정ERC0/0이며무시4규칙은유지했다. 새제외없음. `*_before.kicad_sch`/PDF/netlist/ERC는이번수정직전백업, `*_candidate.*`는검토본, `*_current.*`는원본반영후재추출이다. candidates폴더는복사한설정/라이브러리로재현검사한중간본이다.

MVP값12건/이름1건외핀연결·전기타입·심벌정의는보존했다. [설계29](../../../../09_Electrical_Design/29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md)에원본관측과확정/미결을대조했다. Shield는전기내용그대로주석/제목란을갱신했고후보BOM40행으로맞췄다.

이전 `2026-11-06_schematic_layout_review/applied.pdf`는24부품과거스냅샷이다. [새진행/재개](../../../../docs/progress/2026-11-07_progress.md)를따른다. 열린KiCad편집기에이전내용이남아있으면덮어저장하지말고디스크최신본으로다시연다.

다음은수집·필터표와포트·전원조건표다. 기본구조유지/ADC구현전/정확도·보호실측전/MVP PARTIAL·OPEN/11월9·10일휴무/NotebookLM별도를유지한다.
