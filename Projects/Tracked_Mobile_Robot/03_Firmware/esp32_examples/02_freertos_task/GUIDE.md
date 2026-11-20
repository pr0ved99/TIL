# 02 FreeRTOS Task + Mutex — 코드 가이드

대상 소스: [`main/freertos_task_main.c`](main/freertos_task_main.c)

같은 함수(`counter_task`)로 주기가 다른 태스크 2개를 만들고, 둘이 하나의 공유 변수를 안전하게 쓰도록 Mutex로 보호하는 예제입니다.

## 전체 구조

```text
app_main (태스크)
 ├─ Mutex 생성
 ├─ fast_task 생성 (100 ms 주기) ┐
 ├─ slow_task 생성 (2000 ms 주기) ┤ 모두 s_shared_counter를 증가
 └─ 5초마다 heartbeat 로그       ┘ (Mutex로 보호)
```

## 1. 공유 변수와 Mutex (27~29행)

```c
static uint32_t s_shared_counter;
static SemaphoreHandle_t s_lock;
```

- `s_shared_counter`: 모든 태스크가 함께 증가시키는 변수입니다.
- `s_lock`: 이 변수를 보호하는 Mutex 핸들입니다.
- **왜 필요한가**: `counter++`는 "읽기 → 더하기 → 쓰기" 3단계입니다. 두 태스크가 동시에 하면 한쪽의 증가가 사라질 수 있습니다. Mutex로 "한 번에 한 태스크만" 접근하게 만듭니다.

## 2. 태스크 설정 구조체 (31~38행)

```c
typedef struct { const char *name; uint32_t period_ms; } task_config_t;
static const task_config_t FAST_TASK = {.name = "fast", .period_ms = 100};
static const task_config_t SLOW_TASK = {.name = "slow", .period_ms = 2000};
```

- **역할**: 태스크마다 이름과 주기를 다르게 주기 위한 데이터입니다.
- 태스크 함수는 하나만 쓰고, 생성할 때 **인자(arg)로 설정을 넘겨** 동작을 달리합니다.
- `const`이므로 읽기 전용이고, 전역으로 존재해서 태스크가 살아 있는 동안 포인터가 유효합니다.

## 3. `counter_task()` (40~57행)

태스크 본체입니다.

| 행 | 동작 | 역할 |
|----|------|------|
| 43 | `config = (const task_config_t *)arg` | `void *`로 받은 인자를 원래 타입으로 복원 |
| 45 | `for (;;)` | **태스크 함수는 반환하면 안 됩니다.** 무한 루프여야 합니다. |
| 47 | `xSemaphoreTake(s_lock, portMAX_DELAY)` | Mutex 획득. 다른 태스크가 잡고 있으면 풀릴 때까지 대기 |
| 48~49 | 증가 후 지역 변수 `value`에 복사 | **임계 구역**: 이 안에서만 공유 변수를 읽고 씀 |
| 50 | `xSemaphoreGive(s_lock)` | Mutex 반환 |
| 52 | `ESP_LOGI` | 로그는 임계 구역 **밖**에서 출력 |
| 55 | `vTaskDelay(...)` | 주기 대기 + CPU 양보 |

- **로그를 락 밖에 두는 이유**: 로그 출력은 느립니다. 락을 쥔 채 출력하면 다른 태스크가 오래 기다립니다. 그래서 값만 복사해 두고 락을 푼 뒤 출력합니다.
- **`vTaskDelay`가 없으면**: 이 태스크가 CPU를 계속 잡아 다른 태스크가 굶거나 워치독 경고가 날 수 있습니다.

## 4. `app_main()` (59~88행)

### 4-1. Mutex 생성 (61~65행)
- `xSemaphoreCreateMutex()`가 `NULL`을 반환하면 메모리 부족입니다. 에러 로그를 남기고 종료합니다.

### 4-2. 태스크 생성 (67~76행)

```c
xTaskCreate(counter_task, "fast_task", 3072, (void *)&FAST_TASK, 5, NULL);
```

| 인자 | 의미 |
|------|------|
| `counter_task` | 실행할 함수 |
| `"fast_task"` | 디버깅용 태스크 이름 |
| `3072` | 스택 크기(바이트). 너무 작으면 스택 오버플로로 비정상 동작 |
| `&FAST_TASK` | 태스크 함수에 넘길 인자 |
| `5` | 우선순위(숫자가 클수록 높음) |
| `NULL` | 핸들을 받지 않음 |

- 반환값이 `pdPASS`가 아니면 생성 실패입니다.

### 4-3. heartbeat 루프 (78~87행)
- `app_main` 자체도 하나의 태스크입니다. 5초마다 Mutex를 잡고 값을 읽은 뒤 `ESP_LOGW`로 상태를 출력합니다.
- **역할**: 시스템이 살아 있다는 신호(heartbeat)이자, 메인 태스크도 같은 규칙으로 공유 변수에 접근한다는 예시입니다.

## 5. 실험 목록 (90~98행)
소스 하단 주석에 한 번에 하나씩 바꿔 볼 실험이 있습니다. 주기, `vTaskDelay` 제거, 우선순위, 스택 크기 변경이 대상입니다.

## 이후 예제와의 연결
- **등록만 하면 시스템이 대신 실행**하는 구조(태스크)는 03의 이벤트 핸들러와 04·05의 HTTP 핸들러에서도 같은 개념입니다.
- 이후 여러 태스크가 서버 핸들 등 공유 상태를 만질 때 Mutex가 필요합니다.

## 확인 기준 (PASS)
- `[fast]` 로그가 `[slow]` 로그보다 훨씬 자주 나옵니다.
- 공유 카운터 값이 두 태스크 모두에서 하나의 숫자로 이어서 증가합니다.
- 5초마다 `[main] heartbeat` 경고가 나옵니다.
