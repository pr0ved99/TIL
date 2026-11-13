# 01 Hello World — 코드 가이드

대상 소스: [`main/hello_world_main.c`](main/hello_world_main.c)

이 예제는 ESP-IDF 프로젝트의 가장 작은 형태입니다. 로그 3종을 한 번씩 출력하고, 이후 1초마다 카운터를 출력합니다.

## 전체 구조

```text
부팅 → (ESP-IDF 시작 코드) → app_main() 호출
        ├─ ESP_LOGI / ESP_LOGW / ESP_LOGE 한 번씩 출력
        └─ for(;;) 1초마다 카운트 출력 + vTaskDelay
```

## 1. 헤더 포함 (14~17행)

| 헤더 | 역할 |
|------|------|
| `stdio.h` | 표준 C 입출력. 이 예제는 `printf`를 직접 쓰지 않지만 기본으로 포함합니다. |
| `esp_log.h` | `ESP_LOGI/W/E` 로그 매크로를 제공합니다. |
| `freertos/FreeRTOS.h`, `freertos/task.h` | `vTaskDelay`, `pdMS_TO_TICKS`를 쓰기 위해 필요합니다. |

## 2. `TAG` (20행)

```c
static const char *TAG = "hello";
```

- **역할**: 시리얼 모니터에서 "어느 모듈이 찍은 로그인지" 구분하는 이름표입니다.
- 출력 형식은 `I (1234) hello: 메시지`입니다. 괄호 안은 부팅 후 경과 ms입니다.
- `static`이므로 이 파일 안에서만 보입니다. 파일마다 다른 TAG를 쓰면 로그를 필터링하기 쉽습니다.

## 3. `app_main()` (22~40행)

ESP-IDF는 시스템 초기화를 마친 뒤 FreeRTOS 태스크 하나를 만들어 `app_main()`을 실행합니다. 즉, 일반 C의 `main()`과 비슷한 진입점이지만 **FreeRTOS 태스크 안에서 실행됩니다**.

### 3-1. 로그 레벨 3종 (24~31행)

| 매크로 | 레벨 | 쓰는 상황 |
|--------|------|-----------|
| `ESP_LOGI` | INFO | 정상 동작 정보 |
| `ESP_LOGW` | WARNING | 주의가 필요하지만 계속 동작 가능 |
| `ESP_LOGE` | ERROR | 문제 발생 |

- 터미널에서 레벨마다 색이 다르게 나옵니다(I=녹색, W=노랑, E=빨강).
- **`ESP_LOGE`는 메시지만 출력합니다.** 프로그램을 멈추거나 재부팅하지 않습니다.

### 3-2. 카운터 루프 (33~39행)

```c
int count = 0;
for (;;) {
    ESP_LOGI(TAG, "카운트: %d", count);
    count++;
    vTaskDelay(pdMS_TO_TICKS(1000));
}
```

- `for (;;)`: 무한 루프입니다. 임베디드의 `app_main`은 보통 반환하지 않고 계속 동작합니다.
- `vTaskDelay(pdMS_TO_TICKS(1000))`: 이 태스크를 1초 동안 **블록(대기) 상태**로 두고 CPU를 다른 태스크에 양보합니다.
  - `pdMS_TO_TICKS`는 ms를 FreeRTOS 틱 수로 바꿔 줍니다.
  - 이 줄이 없으면 로그가 최대 속도로 쏟아지고, 다른 태스크가 실행될 틈이 줄어듭니다.
- `count`는 지역 변수이므로 재부팅하면 0부터 다시 시작합니다.

## 이후 예제와의 연결
- 이후 모든 예제의 `TAG`, `ESP_LOGx`, `app_main`, `vTaskDelay` 패턴이 이 파일에서 나옵니다.

## 확인 기준 (PASS)
- 시작 로그 3줄(I/W/E) 뒤에 `카운트: 0`, `1`, `2`...가 약 1초 간격으로 증가합니다.
- 보드를 재부팅하면 카운트가 다시 0부터 시작합니다.
