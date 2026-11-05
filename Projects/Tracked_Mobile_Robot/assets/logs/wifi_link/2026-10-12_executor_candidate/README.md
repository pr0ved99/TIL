# UART executor 후보 검사 — 2026-10-12

- [입력 안내](../../../../docs/plans/2026-10-12_WiFi_ARM_CMD_Executor_Code_Guide_ko.md)의 두 C 후보와 실제 저장된 parser/ticket/owner/state C를 TCC `-Wall -Werror`로 컴파일·실행했다.
- [후보 검사 원본](pc_executor_candidate_initial.txt): **17 tests/PASS**, 모드 `CANDIDATE EXECUTOR WITH SAVED CONTROL MODULES`.
- [기본 저장본 검사](pc_executor_saved_unavailable.txt): **0 tests/SKIP1**. 사용자 executor 파일이 아직 없으며 실제 저장본/ESP 빌드 결과가 아니다.
- [검사 당시 안내](guide_tested_before_explanation.md)는 원본 출력에 찍힌 Markdown hash의 byte 보존본이다. 이후 설명/CMake를 추가한 [최종 안내 보존본](guide_final.md)은 C 블록 두 개가 검사 당시 내용과 동일하다.
- [source_snapshot](source_snapshot/)에 후보 executor .h/.c, 사용한 실제 의존 파일, runner/fixture를 보존했다. [manifest](manifest.json)는 파일 byte/SHA256을 기록한다.
- 사례는 정상 zero-only 제어/정지, gate·ticket/queue/ACK 만료, 취소/폐기 확인 순서, 값 복사·결과 역압, 연결/seq/type 대조, 부분 송신 LF 계획, source timeout·BLOCKED 수동 복구 등을 검사했다.
- 프레임은 반환된 UART 계획 값이다. 실제 uart_write_bytes 호출, STM parser/출력, HTTP/FreeRTOS 경합·큐/필수 메시지 전달은 이 결과로 증명하지 않는다. main과 브라우저 연결·AC-H 전체·AC-B/S는 후속 작업이다.
- 기존 main/학습 대상 펌웨어·CMake를 직접 수정하거나 ESP/STM 빌드·플래시·Git commit/push를 수행하지 않았다.
