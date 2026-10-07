# 03 Wi-Fi STA 연결 + 이벤트 핸들러 — 코드 가이드

대상 소스: [`main/wifi_sta_main.c`](main/wifi_sta_main.c), 설정: `main/wifi_config.h`

ESP32가 공유기나 핫스팟에 접속(STA 모드)하는 초기화 순서와, 접속 상태 변화를 이벤트 핸들러로 처리하는 방법을 다룹니다.

## 전체 구조

```text
app_main
 ├─ 설정 검증 → NVS → netif/이벤트 루프 → Wi-Fi 드라이버 → 핸들러 등록 → 접속 설정
 ├─ esp_wifi_start()
 │     └─ (이후는 이벤트가 진행)
 │         STA_START → connect → STA_CONNECTED → GOT_IP
 │         STA_DISCONNECTED → 최대 5회 재시도
 └─ 5초마다 연결 상태/RSSI 출력
```

## 1. 설정 파일 `wifi_config.h`

- `WIFI_STA_SSID`, `WIFI_STA_PASSWORD`를 정의합니다.
- **역할**: 개인 정보(비밀번호)를 소스 본문에서 분리합니다. 공유용 예시는 `wifi_config.h.example`입니다.
- 실제 값은 소스 저장소에 올리지 않는 것이 원칙입니다.

## 2. 상수와 상태 변수 (39~46행)

| 이름 | 역할 |
|------|------|
| `MAX_RETRY 5U` | 접속 실패 후 재시도 최대 횟수 |
| `STATUS_PERIOD_MS` | 메인 루프의 상태 점검 주기(5초) |
| `s_retry_count` | 현재까지 재시도한 횟수 |

- `s_retry_count`는 **이벤트 루프 태스크에서만** 읽고 씁니다. `app_main`은 건드리지 않으므로 Mutex가 필요 없습니다.

## 3. `wifi_event_handler()` (54~93행)

직접 호출하지 않습니다. `esp_event_handler_register`로 등록하면 Wi-Fi 스택이 상태가 바뀔 때 **시스템 이벤트 태스크**에서 대신 호출합니다.

| 이벤트 | 동작 | 역할 |
|--------|------|------|
| `WIFI_EVENT_STA_START` | `esp_wifi_connect()` | 드라이버가 시작되면 접속 요청 |
| `WIFI_EVENT_STA_CONNECTED` | 로그만 출력 | AP와 연결됨. **아직 IP는 없음** |
| `WIFI_EVENT_STA_DISCONNECTED` | reason 로그 + 재시도 | 끊김 원인 확인, 5회까지 재접속 |
| `IP_EVENT_STA_GOT_IP` | IP 출력, 재시도 카운터 리셋 | **이 시점부터 통신 가능** |

### 끊김 reason 코드 (67~74행)

| 코드 | 의미 | 흔한 원인 |
|------|------|-----------|
| 201 | `NO_AP_FOUND` | SSID 오타, 5GHz 전용 공유기, 범위 밖 |
| 202 | `AUTH_FAIL` | 비밀번호 오류 가능 |
| 15 | `4WAY_HANDSHAKE_TIMEOUT` | 핸드셰이크 실패, 비밀번호 오류 가능 |
| 2 | `AUTH_EXPIRE` | 인증 만료 |
| 205 | `CONNECTION_FAIL` | 연결 실패 |

- 재시도 한도(5회)를 넘으면 에러 로그를 남기고 더 이상 연결을 시도하지 않습니다. 이때는 보드를 재부팅해야 합니다.
- `ESP_ERROR_CHECK`는 반환값이 에러이면 로그를 남기고 **재부팅(abort)** 시킵니다.

## 4. `app_main()` 초기화 순서 (95~169행)

순서가 중요합니다. 앞 단계가 되어 있어야 뒤 단계를 할 수 있습니다.

| 단계 | 코드 | 역할 |
|------|------|------|
| 1 | SSID/비밀번호 길이 검증 | 비어 있거나 길이가 틀리거나 `CHANGE_ME` 그대로면 실행하지 않음 |
| 2 | `nvs_flash_init()` | Wi-Fi 드라이버가 쓰는 비휘발 저장소 초기화. 공간 부족/버전 불일치 시 지우고 재초기화 |
| 3 | `esp_netif_init()`, `esp_event_loop_create_default()` | TCP/IP 스택과 기본 이벤트 루프 생성 |
| 4 | `esp_netif_create_default_wifi_sta()` | STA용 네트워크 인터페이스 생성 |
| 5 | `esp_wifi_init()`, `esp_wifi_set_storage(RAM)` | Wi-Fi 드라이버 초기화, 설정은 RAM에만 보관 |
| 6 | `esp_event_handler_register()` ×2 | Wi-Fi 이벤트 전체와 IP 획득 이벤트에 핸들러 연결 |
| 7 | `wifi_config_t` 채우기 | SSID, 비밀번호, 인증 방식 설정 |
| 8 | `esp_wifi_start()` | **이 호출 이후의 진행은 이벤트 핸들러가 담당** |
| 9 | 상태 점검 루프 | 5초마다 `esp_wifi_sta_get_ap_info()`로 연결 여부와 RSSI 출력 |

### 접속 설정 상세 (139~149행)
- `authmode = WIFI_AUTH_WPA2_PSK`: WPA2 **이상**만 접속 대상으로 허용합니다.
- `sae_pwe_h2e = WPA3_SAE_PWE_BOTH`: WPA3(SAE) 공유기에도 맞춰 자동으로 방식을 선택합니다.
- `pmf_cfg.capable = true`, `required = false`: 보호된 관리 프레임(PMF)을 지원하지만 필수로 요구하지는 않습니다. WPA3는 PMF가 필요합니다.

## 5. 실험 목록 (171~179행)
- 비밀번호 오류 시 reason 확인, 없는 SSID(201), 공유기 재시작 시 재시도 흐름, `MAX_RETRY` 변경, 거리에 따른 RSSI 변화를 소스 하단에 제시합니다.

## 이후 예제와의 연결
- 04와 05의 `wifi_event_handler`는 이 구조에 `GOT_IP` 시 서버를 시작하는 코드가 추가된 형태입니다.

## 확인 기준 (PASS)
- 로그 순서: `STA started -> connecting` → `Associated with AP` → `Got IP: x.x.x.x`.
- 5초마다 `connected ssid=... rssi=... dBm`이 출력됩니다.
- 공유기를 껐다 켜면 `Disconnected, reason=...`과 재시도 로그가 나옵니다.
