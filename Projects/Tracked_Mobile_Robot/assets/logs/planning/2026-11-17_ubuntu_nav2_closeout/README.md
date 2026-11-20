# 11/17 마감·환경 조회·최신화/게시 영수증

대상:11/15 이후 보호/하네스 논의, Ubuntu 듀얼부팅·가상 센서/Nav2·선택적 RL 계획. 기준일은2026-11-17 Asia/Seoul이며 실제 작업 시각은 추정하지 않는다.

- [진행 기록](../../../../docs/progress/2026-11-17_progress.md)
- [단계·일자별 계획](../../../../docs/plans/2026-11-17_Ubuntu_Nav2_Simulation_and_RL_Roadmap_ko.md)
- [Notion 계획](https://app.notion.com/p/41aa7326f87b81768d92dea6564f277d)
- [환경 읽기 전용 조회](environment_readonly.json): 내부1TB SSD/여유 공간 확인, 암호화 상태 UNKNOWN. 파티션/OS 변경 없음.
- [일자별 산출물](daily_plan.json): 모두 NOT_STARTED,12/3 이후는 조건부 초안.
- [갱신 문서 목록](updated_documents.json), [문서·링크·기존 변경 검증](verification.json), [CAD/기본 PDF 대조](export_freshness.json).
- [외부 게시 읽기 검증](external_verification.json): 기존Notion6개 갱신/새계획1개, 기존11/15 일정설명 갱신(시간/참석자/알림/회의 보존),11/17 마감 기록+11/19~12/2 제안 일정. 모두 종일/한가함이며 실제 작업시간이 아니다.
- [Git/게시 상태](publication.json): 실제 commit/push/remote 확인 결과를 기록한다.

## 발견·수정한 최신화 누락

보유24AWG의 실리콘 피복/연선 보고, 보호 전류 제한과 ADC 고장 진단의 구분, TCR 검토 범위, 신규 듀얼부팅의 내부 SSD 사용 방향, 현재1TB 디스크와 과거256GB 기록의 구분, 기존 Humble 시작 고정 문구/YOLO 우선순위, 오도메트리 문서의10/23 이전 미완료 안내를 현재 경로와 맞췄다. README·계획·인수인계·메모리·전기/학습·아키텍처·부품대장을 점검했다.

## 보존/미반영 범위

- 기존21개 무관 변경은 원본 해시로 보존 대조하며 이번 commit에 포함하지 않는다.
- 제작 Shield/MVP의 CAD와 기본 exports PDF를11/15 확인본과 대조한다. 소스 변경이 없으면 PDF/ERC/DRC를 재생성하지 않는다. 회로/실물 성능 PASS를 추가하지 않는다.
- 11/6 applied.pdf, 날짜별 진도 그래프·과거 로그/스냅샷은 이력으로 유지한다. NotebookLM 패키지/업로드·영상 갱신은 별도이며 이번에 갱신하지 않았다.
- 실제 PCB 보호/ADC/IMU/LiDAR·속도 추종·실물 자율주행은 미완료다. Ubuntu 설치/ROS/Gazebo/Nav2/RL 신규 실행도 없다.
- 점검한 영향 범위의 최신화이며 저장소 전체 과거 자료를 모두 재검증했다는 의미가 아니다.
