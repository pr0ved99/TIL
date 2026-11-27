# RevA 세 문서 대조 · 2026-11-28

[검토 결과 7쪽](../2026-11-28_filter_relayout/before/exports/TMR_Monitor_Shield_RevA_quality_audit.pdf)에는 공통 기준 30항목, 배선 품질 가이드, 전용 검토표 22개 CAD·5개 실측 항목의 처리 결과가 있다. 도면상의 우선순위는 J3/J4의 공통 GND와 C3의 배치다. 전기적 성능과 차체 하네스는 실측 전이다.

- [checks.json](checks.json)에는 기준이 된 세 PDF와 CAD의 SHA-256, 새 회로 넷리스트 대조와 PCB 연결 검사 결과, 검토용 Gerber 작업 파일 내용·드릴 공구별 홀 수가 있다.
- [geometry.json](geometry.json)에는 실제 경로의 좌표·길이·층, 평행 구간, 구리 간격, 비아 드릴–SMD 패드 중첩 검사가 있다. PCB 파이썬 모듈이 설치된 환경에서 `/usr/bin/python3 inspect_board.py 보드파일.kicad_pcb`로 다시 출력할 수 있다. 경로 길이는 패드 중심과 구리 선분 중심선 기준이며 수직 길이는 제외했다. 평행 구간 검색은 두 선분의 방향이 같고 투영 구리 간격이 1 mm 이하인 경우다. 제조 또는 누화 허용 한계로 사용하지 않는다.
- KiCad 10.0.8에서 `kicad-cli pcb drc --schematic-parity --all-track-errors --severity-all --exit-code-violations --format json`과 `kicad-cli sch erc --severity-all --exit-code-violations --format json`을 실행했다. [DRC](drc.json)와 [ERC](erc.json)에 활성 검사 결과와 제외된 검사 종류가 있다.
- 원시 회로·배선은 그대로 검토했다. 작업용 Gerber/드릴은 검토용 복사 출력이며 주문본 발행과 하드웨어 시험은 별도다.
