# 제품 관점 회로 검토 근거 — 2026-11-06

[검토 보고서](../../../../09_Electrical_Design/28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md).

- `current_schematic.pdf` / `current_schematic.png`: 실제 저장 회로도의 새 추출·렌더링. IDE에 열린 이전 `schematic_layout_review/applied.pdf`와 구분한다.
- `current_netlist.xml`: 40부품·활성21net. 전압 두 채널 신호와AVDD/C7/C8 연결, RESET→SEL·의도적 개방/미사용 핀 처리 미완료를 확인했다.
- `current_erc.json`: KiCad10.0.5 기존 설정/전체 심각도 검사, 오류18·개별 제외0·기존 무시 규칙4개. 미연결11·미구동5·전원미구동2이며 같은 미완성 핀이 복수 진단에 포함된다.
- `evidence.json`: 부품/풋프린트·모든 net·PCB 객체 수·필터/오차 민감도 계산·명령/실행 결과·CAD6파일 실행 전후 SHA256.
- `review_evidence.py`: 새 추출/계산을 재현하는 읽기 전용 스크립트. 실행 시 증거 파일은 최신 CAD 기준으로 갱신된다.

검토 도중 저장본이38→40부품으로 바뀌어 재추출했다. 위 수량은최종 증거 추출 시점의 스냅샷이며 이후 편집 상태를 자동 반영하지 않는다. 추출 실행 전후의CAD6파일 해시는같았으며 Codex는 회로도·PCB·프로젝트/심벌 설정과 후보 BOM을 편집하지 않았다. PCB는22풋프린트, 트랙/비아/영역0의 이전 상태다. 이번 ERC는 Shield 초안 결과이며 기존 MVP RevB의ERC0/0과 혼동하지 않는다. 실물·EMC·보호·정량 정확도 검증은 수행하지 않았다.
