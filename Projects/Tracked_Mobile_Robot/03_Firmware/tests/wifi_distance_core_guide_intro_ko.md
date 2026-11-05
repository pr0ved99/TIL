# ESP 목표 거리 명령 — 공통 계약·UART 전송 입력

## 목적과 이번 범위

`TK-MVP-03-06`: 브라우저에서5·10·15·20cm를 선택하여 명령하고, STM이 엔코더 count로 좌우 출력을 각각 차단한 뒤 공중 궤도의 링크 이동량을 실측한다. 이번에는 그 명령을 운반할 ESP 공통 계층을 준비한다. **검토 후보이며 아직 생산 소스에 적용하지 않았다.**

대상은 `03_Firmware/esp32_wifi_link/main`의 `wifi_control_contract.h/.c`, `wifi_control_executor.c`3개 파일/5개 교체 구간이다. 사용자 직접 입력·저장 후 실제 저장본 검사가 필요하다. 브라우저 입력·완료 표시는 다음 묶음이며 지금 새 보드 빌드/flash/구동을 하지 않는다.

## 상태와 데이터 흐름

1. 거리 명령도 기존 `CMD,boot_id=...,request_id=...,control_id=...,ticket=...,vx_mmps=100,w_mradps=0` 뒤에 `,distance_mm=50/100/150/200`만 추가한다. 단위는 mm다. 일반 CMD에는 이 필드가 없고 구조체 값은0이다.
2. parser는 성공한 경우에만 임시 구조체를 out으로 복사한다. 잘못된 거리·방향·필드 순서·중복·overflow·개행은 거부한다. 명시적 `distance_mm=0`도 거부한다. zero 정지 CMD는 거리 필드를 **생략**한다.
3. `wifi_control_request_allows()`는 값/모드 정책을 담당한다. ARM에 거리 필드를 허용하지 않고 zero-only 모드도 거리 명령을 거부한다. parser 성공은 제어 허가가 아니다.
4. 기존 executor가 부팅·owner·control ID·ticket·만료·ACTIVE 조건을 확인한다. ARM 직후 첫 CMD는 기존처럼 zero다. 큐에서 전송할 때도 상태/유효기한을 검사한다. 새 우회 경로를 만들지 않는다.
5. UART에는 `CMD,seq=...,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=...`을 보낸다. STM은 현재 ARM의 목표/시작점을 고정하고, 같은 목표 반복은 keepalive로 처리한다. 도달 이후 반복으로 재시작하지 않는다.
6. 버튼 해제의 zero CMD는 suffix를 생략하여 STM 거리 동작을 취소한다. 목표 변경/일반 주행으로의 전환은 STM의 거리 latch를 우회하지 못한다. 다음 시도는 DISARM과 새 ARM을 사용한다.

ESP는 전송·수명·제어권을 관리하고 **거리 판정·좌우 PWM 차단·최종 안전 정지는 STM 책임**으로 유지한다. 동일 명령 종류를 확장하여 기존 ACK/ERR·ticket·owner/state 검증을 재사용한다. 새로운 MOVE 명령이나 별도 UART 송신 경로를 추가하지 않는다.

## 실패와 증거 경계

잘못된 요청은 UART 출력 전에 거부한다. 기존 queue 만료·연결 종료·short TX·ACK timeout·STM ERR는 기존 STOPPING과 부분 줄 취소/DISARM 경로를 유지한다. 유효한 거리 요청의 UART ACK는 접수 근거이며 실제 거리 도달/기계적 정지 PASS가 아니다. count 차단 뒤 관성 이동량도 이후 실측에 포함한다.

Web 최대 ID 조합의 거리 CMD는123byte로 기존128byte 제한 안이다. STM UART 최대 seq의 목표 CMD도 기존96byte 버퍼 안이다. 제한이나 PWM gain/cap을 늘릴 필요가 없다. `vx=100`은 현재 매퍼의 요청값이며 실측100mm/s를 뜻하지 않는다.

PC PASS 기준: 기존 일반 주행·zero-only 회귀,4개 목표의 parser→ticket/owner/state→정확한 UART 필드 보존, invalid/overflow/방향 오류 거부, 첫 zero 강제, 잘못된 owner/boot/control/ticket·만료 거부, 전송 실패 정지, 의도적으로 거리 필드명을 바꾼 오류 주입 검출. PC 모의 검사는 실제 ESP build·FreeRTOS/UART 주기·STM 정지거리 검증을 대체하지 않는다.

아래5개 구간을 순서대로 교체한다. 기존 정책 함수나 전송 함수를 남겨 중복 정의하지 않는다.
