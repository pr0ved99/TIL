# 프로젝트 파일 관리 기준

2026-11-14 영향 범위의 자료 최신화 점검을 반영했다. 현재 상태는 [인수인계](CURRENT_SESSION_CONTEXT.md), 실제 작업/게시 범위는 [진행 기록](../progress/2026-11-14_progress.md), 최신 점검은 [11/14 마감](../../assets/logs/pcb_design/2026-11-14_sampling_closeout/README.md)을 따른다. 이전 광범위 점검은 [11/12 전체 자료 감사](../../assets/logs/pcb_design/2026-11-12_material_freshness_audit/README.md)로 보존한다. 아래11/4 수량·초기 조치는 당시 기록이다.

## 저장 위치와 역할

| 위치 | 보관할 것 | 주의할 점 |
| --- | --- | --- |
| 00_Project_Charter / 01_System_Architecture | 목표·채택한 구조·인터페이스 계약 | 한국어 정본 우선, 학습 후보를 채택 결정으로 자동 승격하지 않음 |
| 03_Firmware / 04_PC_Serial_Control | 실제 앱·소스·PC 도구·검사 | build/Debug/Release는 재생성 출력. 기존 추적 산출물은 별도 이관 전까지 보존 |
| 07_Embedded_Learning_Notes | 개념·계산·실습 해설 | 관측·가정·계산·설계 결정을 구분 |
| 08_Mechanical_Design / 09_Electrical_Design | 편집 원본 CAD·회로 계산·설계 검토 | 제작 CAD와 Simulation 모델, 초안과 제작 승인을 구분 |
| assets/datasheets | 부품/계기 원문과 색인 | 로컬 stm32f446mc.pdf의 기존 위치/링크는 유지, 판본/쪽 확인 |
| assets/logs / captures / photos | 날짜별 원본·분석·근거·manifest | 과거 source_snapshot/안내 보관본을 현재 소스로 수정하지 않음 |
| assets/videos/.../raw / final | 원본 촬영 / 완성본 | 원본과 편집 중간 산출물은 삭제 전 사용 관계/해시 확인 |
| docs/progress / plans / handoff | 날짜별 실적 / 실행 계획 / 현재 재개점 | 현재 상태는 상단, 과거 다음 작업은 당시 이력으로 표시 |

## 11/4 점검 당시 보완한 것

- 대표 README·학습/전장/계획/인수인계 색인·PROJECT_MEMORY·다음 세션 안내를 필기30~35 마감/다음36절로 맞췄다.
- 프로젝트 `.gitignore`에 이후 생성되는 MCU build/Debug/Release와 KiCad 잠금/자동저장/백업을 제외했다. 이미 추적 중인 파일에 소급 적용되지는 않는다.
- 전수 목록과 Markdown 상대 경로 검사 도구/결과를 [11/4 관리 점검](../../assets/logs/pcb_design/2026-11-04_document_management_closeout/README.md)에 보관했다.

## 남겨 둔 관리 항목과 이유

1. **기존 추적 빌드 산출물344개:** 과거 실행 이미지/증거가 섞일 수 있다. 현재 dirty12개도 보존한다. 후속 정리 시 evidence manifest와 실행 이미지 참조를 먼저 대조한 뒤 선택적으로 추적 해제한다. 이번에는 삭제/추적 해제하지 않았다.
2. **이름 없는 KiCad wrapper2개:** `03_Voltage_Divider/.kicad_sch`, `.kicad_sch.kicad_sch`는 동일 내용이며03_09를 참조하는 sheet wrapper다. 실습 원본과 별개임을 확인했지만 기존 사용자 미추적 작업이므로 그대로 보존했다. 현재 재개 파일로 안내하지 않는다.
3. **과거 안내 snapshot 상대 링크3개:** 아래 대체 탐색표로 현재 근거를 찾는다. 보관본 본문/해시를 바꾸지 않고 이력으로 유지한다.

| 보관본 위치 | 보관 당시 링크 | 현재 탐색 경로 |
| --- | --- | --- |
| assets/logs/wifi_link/2026-10-12_executor_candidate/guide_final.md:5 | 2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md | [계약](../plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md) |
| 같은 파일:5 | 2026-10-11_WiFi_ARM_CMD_State_Code_Guide_ko.md | [코드 안내](../plans/2026-10-11_WiFi_ARM_CMD_State_Code_Guide_ko.md) |
| 같은 파일:507 | 복사 전 문서 기준의 README 상대 경로 | [동일 근거 폴더 README](../../assets/logs/wifi_link/2026-10-12_executor_candidate/README.md) |

두 계획 문서의 링크가 실제 존재하는지는 관리 점검 후 상대 링크 검사로 확인한다. HTTP/Notion/GitHub 링크의 전체 접속성과 Markdown 앵커, 모든 바이너리 내용/펌웨어 기능을 검증한 점검은 아니다.

## 이후 정리 원칙

현재 자료를 변경할 때는 원본만 저장하거나 로그 링크만 추가하지 않고 아래 파생 자료를 함께 대조한다.

| 변경 | 함께 확인할 현재 자료 |
| --- | --- |
| KiCad 회로도 | 프로젝트 `exports/*_schematic.pdf`, 기본 netlist/ERC·부품 목록/BOM, README의 열람 링크와 검사 범위 |
| PCB | 회로도 대조·미배선·배치 PDF와 검사 기준. 회로도만 바뀐 경우 PCB 완료로 표시하지 않음 |
| 수령/실물 관측 | 부품 대장·관련 준비 계획·하드웨어/기구/펌웨어 색인·검증표. 관측 범위를 넘는 PASS 금지 |
| 현재 학습/다음 작업 | 현재 인수인계·시작 프롬프트·메모리·상위 README·현행 실행 계획 |
| 시연/설명 묶음 | 기준 날짜·출처·복제/업로드/생성 상태. 이미 배포한 날짜별 묶음을 자동으로 최신본으로 간주하지 않음 |

`assets/logs`와 날짜별 PDF는 당시 증거를 보존한다. 기본 열람 경로는 각 프로젝트의 최신 저장본을 반영한다. 새 상단 문단만 붙이고 기존 현재 상태표의 틀린 값을 그대로 두지 않는다. 이번 점검은 새 외부 게시나 실물 시험을 대신하지 않는다.

새 원본은 해당 분야의 날짜별 근거 폴더로 넣고, README에 출처·관측·해석·한계·다음 작업을 연결한다. 파일 이동은 참조와 해시를 확인한 뒤 수행한다. 무관한 dirty 작업을 한 번의 정리 커밋에 포함하지 않으며 `git add .`로 일괄 게시하지 않는다. 현재 안내를 맞추되 과거 날짜별 결과를 최신 결과로 덮어쓰지 않는다.
