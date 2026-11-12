# 기본 회로도 PDF 경로 동기화 — 2026-11-12

사용자가 `09_Electrical_Design`의 PDF에서 J7/J8을 찾을 수 없다고 지적했다. 11/7 최신 도면은 검토 로그에만 게시되었고 Shield 기본 `exports`에는 이전 PDF가 남아 있었다. MVP 폴더의 `exports`에도 8월 체크포인트만 있었다. README의 최신 검토 링크만 바꾸고 기본 산출물 경로를 갱신하지 않은 누락이다.

## 수정 결과

- [Shield 기본 PDF](../../../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/exports/TMR_Monitor_Shield_RevA_schematic.pdf): 저장 원본에서 다시 생성. J7/VBAT_SENSE와 J8/VMOTOR_SENSE 및 전압 두 채널 포함.
- [MVP 기본 PDF](../../../../09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevB/exports/Tracked_Mobile_Robot_Wiring_RevB_schematic.pdf): 저장 원본에서 생성해 고정 열람 경로 추가.
- 전기 설계 및 두 CAD 프로젝트 README에 최신 PDF를 직접 연결하고, 회로 변경 뒤 기본 PDF도 함께 갱신하도록 기록했다. Shield README의 초기 22부품 검사와 현재 40부품 회로도도 구분했다.
- 날짜별 과거 PDF는 유지했다. 교체 전 Shield 기본 PDF는 [백업](shield_export_before.pdf)으로 보존했다. PCB 배치 PDF는 22풋프린트 초안이며 회로도 최신화와 구분한다.

## 검증

KiCad CLI 10.0.5의 `sch export pdf --output <기본 PDF 경로> <저장 회로도>`로 재생성했다. 실제 실행은 이 폴더의 `shield_export.pdf`/`mvp_export.pdf`에 먼저 출력하고, 검증 후 기본 경로에 복사했다.

두 PDF 모두 1쪽이며, 11/7 `shield_current.pdf`/`mvp_current.pdf`와 추출 본문 및 108dpi 렌더링 픽셀이 일치했다. Shield의 J7/J8 및 두 커넥터 이름을 확인했다. 원본 CAD의 SHA-256은 보존했다. [검증 JSON](verification.json) · [변경 전 파일 해시](baseline.json).

이번은 기본 내보내기와 안내 문서의 누락 수정이다. 새 ERC/DRC·회로 변경·펌웨어 빌드/플래시·실물 시험 및 Git/Calendar/Notion 게시를 수행한 것이 아니다. 학습 다음 순서는 41-2 정상 입력·공급 조건표로 유지한다.
