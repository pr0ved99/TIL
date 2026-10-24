# 다음 세션 시작 프롬프트

10/24 학습 회차를 10/25에 정리했다. 아래 내용을 새 대화의 시작점으로 사용한다.

```text
Tracked Mobile Robot의 노트북 PCB 모니터링 입력 설계를 이어가자.
먼저 docs/handoff/CURRENT_SESSION_CONTEXT.md와 최신 progress를 읽고 필요한 계산 자료만 확인해라.

오늘 목표는 채널별 수집 주기·순서, PWM/aliasing, 평균 지연, 보정 후 오차 예산을 연결해
전류 입력 12kΩ/100nF 후보를 판단하는 것이다. 계산 목적·값의 출처·단위·가정을 생략하지 마라.
07_Embedded_Learning_Notes/01_Concept_Notes/11_Monitoring_ADC_Requirements_RC_and_Sampling_ko.md의
14절이 재개점이다. NTC 기본 설명을 처음부터 반복하지 말고 필요한 부분만 다시 연결해라.

외부 C 없는 ADC 획득 모델과 외부 C의 전하 공유 모델을 섞어 정확도 PASS라고 하지 마라.
14MHz/480cycles, NTC STM 공급 B안, 요구 수치는 후보이며 아직 구현/채택/실측 완료가 아니다.
현재 CAD는 전류2·온도2, 22부품·미배선32다. 전체 ADC6+CAN 범위와 IMU 기존 위치를 유지한다.
공간/배치는 후속이며 합의 없이 CAD/BOM·보호 부품·전원 계약을 먼저 변경하지 마라.

149초 통합 영상은 제작 완료. 전체 MVP 인수는 미완료, T005A PARTIAL/T007 BLOCKED,
과거 통신/UI 원인 OPEN과 사용자 제외 조사를 유지한다. 완료 시험·촬영을 자동 반복하지 마라.
MCU 입력/빌드/플래시·실물은 사용자, subagent는 사용자 명시 요청 없이 사용하지 마라.
정리는 문서·진행·해당 Git·기존 Calendar/Notion 전체다. 무관한 기존 변경17개를 보존해라.
```
