# 현재 소스·로컬 빌드·실물 근거 대조

기준: 2026-10-22, `TK-MVP-03-04` 후속. [재현 스크립트](review.py), [식별값/대조 결과](manifest.json).

## 결과

**로컬 기준점 대조 완료. 보드 실행 이미지의 해시 신원은 미확인이다.** 새 코드 수정·MCU 빌드/플래시·통전·구동은 없다.

| 구분 | 확인 결과 | 해석 범위 |
| --- | --- | --- |
| 현재 핵심 소스 | 10/21 source manifest 13/13 byte hash 일치 | 거리 기능·PAGE를 검사한 저장본과 동일 |
| 기존 PC 검사 입력 | STM 24개·ESP core 10개·PAGE 11개, 중복 제거 35개 모두 hash 일치 | 당시 PASS의 입력 일치 확인. 오늘 검사 재실행은 하지 않음 |
| STM 로컬 ELF | `224e21dd8a86ba35c65467db969dcb2ab679d2d1d57424b16248e33c5486ab0d` | 10/20 ELF와 다름. 거리 모듈 6개 함수·HAL_UART_Transmit_IT symbol 포함. 전체 소스/ELF 일치 증명이나 flash readback은 아님 |
| ESP 로컬 ELF | `02234cc1c96616c276b9b32d2cb1704abe18564ece218d7dd7331a16bf69944b` | BIN app description의 ELF hash와 일치 |
| ESP 로컬 BIN | `7bc30a13d78a86595a02b553ffde1a23a1e14a56f1010bcef70bcb00bf41144f` | ELF의 PAGE와 BIN segment의 PAGE byte가 일치 |
| 현재 PAGE | 현재 C initializer를 해석한 전체 PAGE와 ELF 내 PAGE byte 일치 | 거리 버튼 교정·JSON 복사·반응형 UI가 로컬 빌드에 포함됨 |
| 공중 10·15cm 원본 | browser_report byte hash가 observations의 기록값과 각각 일치 | ESP boot/control/ARM 식별·목표/정지 관측 근거. 두 MCU 펌웨어 hash 식별 필드는 없음 |

ESP app description은 `esp32_wifi_link`, `9bc9e97-dirty`, `Oct 21 2026 03:11:02`, IDF `v6.0.2`다. 버전 문자열은 빌드 시점 메타데이터이므로 현재 Git HEAD와 다르다는 이유만으로 오래된 실행 코드라고 판단하지 않는다. 파일 시각도 빌드/flash 증명으로 사용하지 않았다. Bootloader·partition table·flasher args는10/20 대조본과 동일하다.

## 10/20 정지 근거와 변경 영향

[10/20 기준점](../2026-10-20_acceptance_image_identity_review/manifest.json)은 당시 로컬 ESP ELF/BIN과 boot log의 hash prefix 연결 및 사용자 STM Run/TEL 근거를 기록했다. 현재 앱 ELF/BIN은 그 기준점과 달라졌으므로 당시 hash prefix를 현재 앱 식별로 재사용하지 않는다.

게시된10/20 소스 `f11dabc`와 현재 STM protocol을 함수 단위로 비교했다.

- `estop_enforce_latch()`는 동일하다. `command_timeout_enforce()`와 `estop_latch_and_force_safe()`는 기존 본문에 `distance_move_cancel()` 호출을 추가했다. 기존 출력 차단과 상태/사유 전이를 보존하면서 거리 동작을 취소한다.
- `uart_mvp_process()`에는 RX 처리 예산64byte, 비동기 TX poll, E-stop/300ms timeout 뒤 거리 supervisor가 추가됐다. 송신 완료 지연/실패·큐 포화에 대한 새로운 중단 경로가 있어 이전 실행과 동일한 스케줄링이라고 주장하지 않는다.
- [10/21 STM PC 결과](../2026-10-21_session_closeout/stm_distance_validation.json)는 비동기 TX 중 timeout/E-stop, 송신100ms 기한·실패/포화 정지, 거리 취소/재시작 차단 등을 모의 실행했다. 오늘 입력 hash 일치로 해당 근거를 연결했다. 이는 실제 IRQ 부하·물리 정지 시간 검증과 다르다.
- [10/20 실제 단절/timeout 정지](../2026-10-20_uart_tx_disconnect_timeout_air_run01/observations.json)와 [재연결/수동 복구](../2026-10-20_uart_tx_reconnect_recovery_air_run01/observations.json)는 당시 조건의 기능 근거로 유지한다.10/21 거리 도달/DISARM은 별도 정상 거리 경로 근거다. 새 이미지의 모든 오류 경로 PASS로 합치지 않는다.

일반150‰·회전200‰·기본 timeout300ms와 STM/ESP 시험 모드0 설정은10/20 기록과 동일하다. 현재 확인은 기록 대조이며 실물 고장이나 새 코드 결함을 발견한 것은 아니다. 완료한 거리/단절 시험을 자동 반복하거나 재빌드/재flash를 요구하지 않는다.

## 다음 작업

1. 이 로컬 소스·ELF/BIN 해시를 다음 계측 회차의 파일 기준점으로 사용한다. 다음 정상 부팅/관측 때 확보 가능한 ESP ELF hash와 사용자 STM 다운로드/Run 기록을 함께 남기고, 확보하지 못한 것은 미확인으로 표시한다.
2. 장비 수령 여부와 실제 센서 모델·프로브 구성을 확인한다. 미수령이면 계측 위치·연결/절연·기록표·수치 중단 기준 준비를 진행한다.
3. 로컬 식별 대조만으로 통전·계측·지상1m를 승인하지 않는다. 실제 회차는 기존 계측/정지·물리 조건을 확인한 뒤 사용자 수행이다. 추가20cm·무근거 전체 재시험은 없다.
