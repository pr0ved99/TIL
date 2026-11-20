# Zero-only 제어 벤치 증거

- 시험: 2026-10-15, 문서화·PC 재현: 2026-10-16.
- `01`~`08`: 사용자가 붙여넣은 첨부 로그에서 선택한 **원문 행**이다. TEL은 유지하고 부팅/네트워크 배너는 생략했다. 연속 전체 콘솔 캡처가 아니다.
- [manifest.json](manifest.json)은 첨부 원문 SHA256, 선택한 원문 행 번호, 저장 발췌 SHA256, 문서화 당시 공개 C 소스 SHA256을 기록한다. 소스 해시는 보드에 플래시된 바이너리 식별값이 아니다.
- [chat_excerpts.txt](chat_excerpts.txt)는 파일 첨부가 아닌 대화의 로그를 전사했다. 화면 관측은 [보고서35](../../../../docs/verification/35_WiFi_Zero_Control_Fault_Recovery_2026-10-15_ko.md)에 별도로 기록했다. 원본 PNG는 이 폴더에 보존되지 않았다.
- [host_reproduction.txt](host_reproduction.txt)는 10/16 PC 진단 실행의 결과 부분을 전사했다. **현재 실패를 재현한 결과이며 수정 완료 PASS가 아니다.**

`02`는 사용자가 STM RESET을 누르지 않았다고 정정한 시도다. `04`는 ESP 리셋 전에 이미 DISARM된 시도다. 두 파일을 ACTIVE 리셋 성공 증거로 합치지 않는다. `06`에 보이는 한 ARM 사이클을 사용자 보고의 네 시도 전체로 확대하지 않는다.

실물 판정·잔여 조건은 보고서35를 따른다. 현재 앱은 `esp32_wifi_link`, zero-only이며 이 묶음에는 새로운 모터 구동이나 로직애널라이저 캡처가 없다.
