# 프로젝트 파일 관리 기준

**11/25 재개점.** Gazebo GATE-02와 SIM-06 세 채널 재생을 마쳤다. 집에서는 PA4와 VREFINT 두 채널을 폴링해 세 입력에서 구분을 확인했다. 다음은 타이머 트리거·DMA 버퍼와 오류 판정 설계다. [PA4·VREFINT 실측](../verification/49_PA4_VREFINT_Bench_2026-11-25_ko.md) [현재 인수인계](CURRENT_SESSION_CONTEXT.md) [11/24 실측과 재개점](../progress/2026-11-24_progress.md)

**11/17 마감 이력:** 보호 저항의 목적은 합선 판별이 아닌 전류 제한이다. 지속 단락 정격/설치 조건을 확인하고 TCR는 오차 상한 비교로 검토 깊이를 제한한다. 보유24AWG는 실리콘 피복 연선이라는 사용자 보고를 반영했다. 내부1TB SSD 절반을 Ubuntu 듀얼부팅에 배정할 계획이며11/19 백업·점검→조건 충족 시11/20 전환을 권고한다. PCB와 가상 IMU/LiDAR·odom/TF·Nav2를 병행하고 RL은 기준선 이후 선택적으로 비교한다. 새 설치/구현·실측 완료는 아니다. [새 단계·일자별 계획](../plans/2026-11-17_Ubuntu_Nav2_Simulation_and_RL_Roadmap_ko.md) · [11/17 기록](../progress/2026-11-17_progress.md) · [검증/게시](../../assets/logs/planning/2026-11-17_ubuntu_nav2_closeout/README.md). 아래 날짜별 설명은 당시 범위다.

**이전 · 2026-11-15 마감:** B Retry01의 평균 효과와5mV 편향 잔류를 확인했고 사용자는 편향이 평균으로 제거되지 않음을 이해했다고 보고했다. C는 사용자 선택으로 실행 생략.03_15 감지선 단락의 R7 유무 비교 회로·CSV·워크북을 확보했다(공급7.266mA 대8.000A). 실제 ADC 잡음/보호/열 검증이나 제작 CAD 반영은 아니다. 다음은 J7/J8 하네스·설치 조건 → 보호 저항 정격 대조이며 새 감지선 사양은 미정이다. 수기 전체 완료는 미보고, NotebookLM 별도. [진행·근거](../progress/2026-11-15_progress.md) · [배터리 ADC 제조사 근거](../../09_Electrical_Design/31_Battery_Voltage_ADC_Reference_Basis_2026-11-15_ko.md).

2026-11-15 영향 범위의 최신화 점검을 반영했다. 현재 상태는 [인수인계](CURRENT_SESSION_CONTEXT.md), 실적은 [11/15 진행](../progress/2026-11-15_progress.md), 최신 감사/게시 상태는 [11/15 영수증](../../assets/logs/pcb_design/2026-11-15_battery_adc_closeout/README.md)을 따른다. 아래 이전 날짜 수량·조치는 당시 기록이다.

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
