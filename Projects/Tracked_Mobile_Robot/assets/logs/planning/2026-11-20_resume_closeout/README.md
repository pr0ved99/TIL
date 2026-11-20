# 2026-11-20 마감 — MVP 근거 보존 및 확장 작업 재개

- [현재 인수인계](../../../../docs/handoff/CURRENT_SESSION_CONTEXT.md) · [다음 세션 프롬프트](../../../../docs/handoff/NEXT_SESSION_START_PROMPT.md) · [11/20 진행 기록](../../../../docs/progress/2026-11-20_progress.md).
- [초기 실행 순서와 최종 범위](../../../../docs/plans/2026-11-18_Detailed_Design_to_Final_Completion_Plan_ko.md) · [Ubuntu/Nav2 로드맵](../../../../docs/plans/2026-11-17_Ubuntu_Nav2_Simulation_and_RL_Roadmap_ko.md) · [MVP 비실물 근거](../../../../docs/verification/46_MVP_Nonphysical_Closeout_2026-11-20_ko.md).

다음 작업 세션은 12시 이후 집에서 Ubuntu 듀얼부팅 준비부터 시작한다. 설치 여부는 준비 상태에 따라 결정한다. 첫 실제 ADC 기록은 NUCLEO·저전압 시험 입력·임시 배선·시리얼을 쓰는 별도 실물 작업이다. 자체 Shield 제작 전에도 진행할 수 있다. 첫 가상 주행은 PCB·ADC 실측·계측 mock 없이 진행한다.

## 확인한 문서와 파생 자료

- 새 세션 프롬프트, 인수인계, 진행·계획·검증 색인, 프로젝트 및 펌웨어·아키텍처·전기 설계 안내, 메모리를 맞췄다. MVP 재시험 및 11/17 제안 일정은 당시 이력으로 표시했다.
- Shield 안내의 31부품 및 전압 채널 미추가 문구를 과거 시점으로 표시했다. 기본 Shield 회로도 PDF는 J7/J8 포함 40부품이고 MVP 기능 회로도 PDF는 48부품이다. [대조 결과](verification.json)에 원본·PDF·Shield 검사 입력의 해시를 남겼다. 22풋프린트 배치 PDF와 11/6 applied.pdf는 당시 파일이다.
- 계획의 초기 세션을 환경 준비로 앞당기고, 첫 ADC 기록 조건과 첫 가상 이동/반복 평가의 경계를 수정했다. Ubuntu 설치, 실제 ADC/IMU/LiDAR 계측 및 Nav2 실행은 시작 전이다. 기존 검증 판정을 적용 범위 밖으로 확대하지 않는다.
- 변경이 있는 현재 안내와 관련 계획·증거의 링크 및 기본 도면 경로를 점검했다. 날짜별 로그·학습 자료의 당시 결과와 NotebookLM 패키지는 별도로 보존한다.

## 게시 및 재조회

- [본문·근거 커밋](https://github.com/pr0ved99/TIL/commit/2f90218650018f6290f20014788e2862fa4cae3b)을 개발 브랜치에 게시하고 원격 SHA를 확인했다.
- Notion 8페이지와 기존 Calendar 7일정을 재조회했다. 일정 시작/종료 경계가 유지됐다. [게시 증거](publication.json).
- 후속 대조에서 파일 관리·학습/시뮬레이션·설계 근거의 11/17 현재형 안내를 찾아 이력으로 표시했고 현재 인수인계를 연결했다.
