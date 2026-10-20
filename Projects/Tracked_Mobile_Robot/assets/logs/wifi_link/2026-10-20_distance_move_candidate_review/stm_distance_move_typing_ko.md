# 공중 궤도 목표 거리 정지 모듈 입력

5·10·15·20cm 전진을 명령하고 STM이 좌우 엔코더 목표를 각각 판정하여 출력을 끄는 기능의 첫 입력 블록이다. 기존 `analyze_encoder_distance.py`는 PC 로그 분석기이며 목표 거리 명령을 보내거나 모터를 멈추지 않는다.

**현재 단계:** 독립 C 모듈 후보의 PC 검증 완료, 사용자 입력 대기. 아래 두 파일을 새로 만드는 것으로 이번 입력을 마친다. `main.c`, `uart_mvp_protocol.c`, ESP 파일은 이번에 수정하지 않는다. 아직 실행 경로에 연결되지 않아 새 파일을 입력해도 거리 명령이나 실제 자동 정지가 생기지는 않는다. 현재 전원 분리 상태를 유지하고 빌드·플래시·구동은 연결 블록 검토 후 진행한다.

작업은 `TK-MVP-03-06` 공중 목표 거리 보조 시험 준비다. 기존 지상1m 시험 `T-ODO-001`의 완료 판정과 구분한다.

## 이번 모듈의 역할

입력은 목표 길이(mm), 전진 양수로 정규화된 좌우 누적 count, 샘플 시각, 현재 시각, 상위 안전 조건의 허용 여부다. 출력은 좌우를 각각 계속 구동해도 되는지 나타내는 두 boolean이다. PWM 크기는 기존 mapper의 전진144/150‰를 사용하도록 다음 연결 단계에서 처리한다. 이 모듈 자체는 HAL, UART, PWM 레지스터를 호출하지 않는다.

거리 환산은 현재 기하 초기 모델 `1687/19500 mm/count`를 사용한다. 이는14톱니·피치9.64mm·1560counts/rev에서 계산하고 수동 측정과 대조한 값이며, 좌우 수동 측정 회귀값이나 PWM 보정 gain이 아니다.

| 목표 링크 이동량 | 시작 count로부터 목표 증가량 |
| --- | --- |
| 5cm = 50mm | 578 |
| 10cm = 100mm | 1156 |
| 15cm = 150mm | 1734 |
| 20cm = 200mm | 2312 |

`round(distance_mm × 19500 / 1687)`로 계산한다. 전체 누적 count를0으로 만드는 대신 명령 시작점과의 차이를 사용하므로 이전 시험 count가 남아 있어도 된다. 처음에는 이 네 가지 전진 거리만 허용한다.

## 상태와 종료 조건

```text
IDLE
  └─ 새 목표 + 정지 기준점 + 안전 조건 허용 → RUNNING
       ├─ 왼쪽 목표 도달 → 왼쪽 출력 허용 해제, 오른쪽은 자기 목표까지
       ├─ 오른쪽 목표 도달 → 오른쪽 출력 허용 해제, 왼쪽은 자기 목표까지
       ├─ 양쪽 도달 → TARGET_REACHED → 양쪽 출력 허용 해제 유지
       └─ 취소 / 안전 조건 소실 / 데이터 이상 / 기한 초과 → ABORTED
```

한쪽 도달 상태는 유지한다. 같은 명령이 계속 들어오거나 버튼을 계속 누르고 있어도 해당 쪽이 재구동되지 않게 한다. `start()`는 IDLE에서만 성공한다. 반복/중복 시작 요청은 기준점을 바꾸지 않는다. 새 실행은 상위 제어기가 정지·명시적 새 사용자 요청을 확인한 뒤에만 `init()`으로 허용한다. 기존 CMD 수신마다 `init()` 또는 `start()`를 호출하면 안 된다.

`TARGET_REACHED`는 **목표 count에서 출력 차단을 요청했다는 뜻**이다. 기계적 정지, 정밀 위치 유지, 실측 거리 PASS를 뜻하지 않는다. PWM0 이후 관성으로 더 움직인 count와 링크 최종 위치까지 기록해야 한다. 첫 버전은 감속·위치 PID 없이 출력 차단 오차를 관측하며, 결과를 얻기 전에 정밀도를 보장하지 않는다.

## 오류와 안전 책임

- `motion_permitted=false`는 양쪽 출력 허용을 해제하고 ABORTED로 끝낸다. 다음 단계에서 STM의 ARM, E-stop, 최신 keepalive/timeout, 현재 거리 실행 소유권을 반영해야 한다. 기존 E-stop/DISARM 경로는 모듈 상태와 무관하게 즉시 `motor_output_stop_all()`을 호출한다.
- 샘플 무효/누락, 미래·역행 시각, 같은 시각의 count 충돌, 전진 중 count 감소, 상대 count 범위 이상이면 양쪽을 중단한다. 방향 반대/역회전 노이즈도 보수적으로 중단하는 첫 버전이다. 작은 정상방향 count 점프까지 물리적으로 진짜인지 판별하는 센서 진단기는 아니다.
- 제안한 소프트웨어 경계는 샘플 age20ms 이하, 판정 호출 간격20ms 이하, 전체 실행3000ms 미만, 아직 도달하지 않은 각 궤도의 무진행500ms 미만이다. 실측된 모터 열 한계나 정격이 아니다.
- 타이머 차이는 uint32 뺄셈으로 짧은 tick rollover를 처리한다. signed count 차이는 unsigned 산술로 계산하고 범위를 확인해 signed overflow를 피한다.
- `update()`와 출력 반영은 새 샘플이 없을 때도 주기적으로 실행해야 한다. 루프 자체가 멈추면 이 모듈도 실행되지 않는다.20ms 검사는 복귀했을 때 위반을 알아내는 기준이며20ms 이내 실제 차단을 보장하는 하드웨어 장치가 아니다.

## 연결 전에 반드시 해결할 부분

현재 `main.c`의 encoder 누적/CPS 갱신은100ms 주기이고, UART TEL 송신과 디버그 출력은 blocking 호출이다. **현재 sample을 이 모듈에 그대로 넣으면 stale 또는 poll-gap 중단이 발생할 수 있다.** 빠른 주기로 count를 읽는 경로와 기존 CPS/로그 경로를 분리하고, 긴 송신이 정지 판정을 막지 않도록 구조를 검토해야 한다. 실제 제어 주기와 최대 지연은 보드에서 검증한다.

다음 연결 블록에는 다음 책임이 함께 들어가야 한다.

1. STM의 빠른 count/정지 판정과 안전 supervisor. 출력 직전에 E-stop/timeout 확인 → `update()` → mapper 출력을 좌우 허용값으로 차단한다. 일반 `handle_cmd()`가 거리 차단 이후 출력을 다시 쓰지 않도록 제어 경로를 하나로 합친다.
2. 새 목표 거리 명령·응답·실행 ID와 명시적 재시작 조건. 정지 상태의 기준점, ARM/부팅 변경과 취소, 중복 요청을 처리한다. 통신이 끊겼을 때 기존 timeout을 유지하며, 이동 모듈이 스스로 timeout을 갱신해서는 안 된다.
3. ESP/브라우저의 거리 선택·실행과 정지 상태 표시. 기존 누르는 동안 실행 권한을 유지하는 조작을 보존하되 목표에 도달하면 누르고 있어도 자동 정지한다. 놓음·포커스 이탈·DISARM은 중단으로 연결한다.
4. 거리 목표·시작/차단/최종 count·종료 이유를 기록하고, 공중5cm 첫 회차부터 실제 좌우 링크 이동량과 비교한다. 독립적인 좌우 도달 정지는 공중 보조 시험용이며 지상 궤적 제어로 바로 일반화하지 않는다.

## 입력할 파일

STM32CubeIDE의 `stm32_uart_mvp` 프로젝트에서 다음 두 파일을 **새로 만들고 각 전체 코드를 입력**한다. 기존 함수의 일부를 바꾸는 작업이 아니다.

- `Core/Inc/distance_move.h`
- `Core/Src/distance_move.c`

저장 후 Codex가 실제 파일을 다시 읽고 동일 PC 검사를 `--saved`로 수행한다. 사용자 저장본 검토와 STM 빌드는 별도다.

## 검증 방법과 PASS 범위

PC에서 후보 C를 직접 컴파일하여25개 시나리오 묶음(120개 합성 구동 포함)을 검사했다. 네 목표값의 환산, 목표 직전/도달/초과, 서로 다른 좌우 도달 시점, 비영점·음수 시작값, 중복 시작/취소/종료 후 재시작 거부, stale/invalid/역행, 개별 무진행·전체 기한, uint32 시각 rollover, int64 경계를 포함한다.

PASS 조건은 도달한 쪽 출력 허용이false로 유지되고, 어느 중단 조건에서도 양쪽false이며, 명시적 초기화 없는 새 시작이 거부되는 것이다. [PC 결과](validation.json)는 생산 펌웨어 변경 없이 얻은 후보 모듈 근거다. 기존 STM 안전 supervisor와의 통합 회귀, 보드 빌드, 실제 정지/거리 오차는 아직 별도 검증 대상이다.

PC 재검사 명령:

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_distance_move_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
```

사용자 입력본에는 같은 명령에 `--saved`를 추가한다. 테스트는 실제 C를 PC에서만 실행하며 보드 빌드/flash/serial 명령을 수행하지 않는다.

## distance_move.h 전체 코드

```c
/* Encoder target cutoff for short forward track-distance tests. */
#ifndef DISTANCE_MOVE_H
#define DISTANCE_MOVE_H

#include <stdbool.h>
#include <stdint.h>

/* Initial geometry: 14 teeth * 9.64 mm / 1560 counts = 1687/19500. */
#define DISTANCE_MOVE_MM_NUMERATOR       1687U
#define DISTANCE_MOVE_MM_DENOMINATOR    19500U

/* Software bounds for the proposed short airborne test, not motor ratings. */
#define DISTANCE_MOVE_MAX_SAMPLE_AGE_MS    20U
#define DISTANCE_MOVE_MAX_POLL_GAP_MS      20U
#define DISTANCE_MOVE_MAX_RUN_MS        3000U
#define DISTANCE_MOVE_NO_PROGRESS_MS     500U

typedef enum {
    DISTANCE_MOVE_IDLE = 0,
    DISTANCE_MOVE_RUNNING,
    DISTANCE_MOVE_TARGET_REACHED,
    DISTANCE_MOVE_ABORTED
} distance_move_phase_t;

typedef enum {
    DISTANCE_MOVE_REASON_NONE = 0,
    DISTANCE_MOVE_REASON_BAD_TARGET,
    DISTANCE_MOVE_REASON_NOT_PERMITTED,
    DISTANCE_MOVE_REASON_BAD_SAMPLE,
    DISTANCE_MOVE_REASON_STALE_SAMPLE,
    DISTANCE_MOVE_REASON_POLL_GAP,
    DISTANCE_MOVE_REASON_COUNT_REVERSED,
    DISTANCE_MOVE_REASON_COUNT_RANGE,
    DISTANCE_MOVE_REASON_RUN_TIMEOUT,
    DISTANCE_MOVE_REASON_NO_PROGRESS,
    DISTANCE_MOVE_REASON_CANCELLED
} distance_move_reason_t;

typedef struct {
    int64_t left_count;
    int64_t right_count;
    uint32_t sample_ms;
    bool valid;
} distance_move_sample_t;

typedef struct {
    distance_move_phase_t phase;
    distance_move_reason_t reason;
    uint32_t target_counts;
    int64_t start_left;
    int64_t start_right;
    int64_t last_left;
    int64_t last_right;
    uint32_t started_ms;
    uint32_t last_poll_ms;
    uint32_t last_sample_ms;
    uint32_t left_progress_ms;
    uint32_t right_progress_ms;
    bool left_reached;
    bool right_reached;
} distance_move_t;

typedef struct {
    bool left_run;
    bool right_run;
} distance_move_output_t;

/* Caller may reset only at boot or a new explicitly authorized stopped run. */
void distance_move_init(distance_move_t *move);
bool distance_move_target_counts(uint32_t distance_mm, uint32_t *counts);

/* Start requires a stationary baseline and the caller's current safety permit. */
bool distance_move_start(
    distance_move_t *move,
    uint32_t distance_mm,
    const distance_move_sample_t *sample,
    uint32_t now_ms,
    bool motion_permitted
);

/* Call even between new samples so stale/stall/deadline checks still run. */
void distance_move_update(
    distance_move_t *move,
    const distance_move_sample_t *sample,
    uint32_t now_ms,
    bool motion_permitted
);
void distance_move_cancel(distance_move_t *move);
distance_move_output_t distance_move_output(const distance_move_t *move);

#endif
```

## distance_move.c 전체 코드

```c
/* Encoder target cutoff logic; no HAL, UART or motor writes. */
#include "distance_move.h"

#include <stddef.h>

static void abort_move(distance_move_t *move, distance_move_reason_t reason)
{
    move->phase = DISTANCE_MOVE_ABORTED;
    move->reason = reason;
}

static bool sample_is_usable(
    distance_move_t *move,
    const distance_move_sample_t *sample,
    uint32_t now_ms
)
{
    if (sample == NULL || !sample->valid) {
        abort_move(move, DISTANCE_MOVE_REASON_BAD_SAMPLE);
        return false;
    }
    if ((uint32_t)(now_ms - sample->sample_ms) >
        DISTANCE_MOVE_MAX_SAMPLE_AGE_MS) {
        abort_move(move, DISTANCE_MOVE_REASON_STALE_SAMPLE);
        return false;
    }
    return true;
}

void distance_move_init(distance_move_t *move)
{
    if (move != NULL) {
        *move = (distance_move_t){0};
    }
}

bool distance_move_target_counts(uint32_t distance_mm, uint32_t *counts)
{
    if (counts == NULL) {
        return false;
    }
    *counts = 0U;
    if (distance_mm != 50U && distance_mm != 100U &&
        distance_mm != 150U && distance_mm != 200U) {
        return false;
    }
    /* Round to nearest count; maximum product here is only 3,900,000. */
    *counts = (distance_mm * DISTANCE_MOVE_MM_DENOMINATOR +
        DISTANCE_MOVE_MM_NUMERATOR / 2U) / DISTANCE_MOVE_MM_NUMERATOR;
    return true;
}

bool distance_move_start(
    distance_move_t *move,
    uint32_t distance_mm,
    const distance_move_sample_t *sample,
    uint32_t now_ms,
    bool motion_permitted
)
{
    uint32_t target;
    if (move == NULL || move->phase != DISTANCE_MOVE_IDLE) {
        return false;
    }
    if (!motion_permitted) {
        abort_move(move, DISTANCE_MOVE_REASON_NOT_PERMITTED);
        return false;
    }
    if (!distance_move_target_counts(distance_mm, &target)) {
        abort_move(move, DISTANCE_MOVE_REASON_BAD_TARGET);
        return false;
    }
    if (!sample_is_usable(move, sample, now_ms)) {
        return false;
    }
    move->target_counts = target;
    move->start_left = move->last_left = sample->left_count;
    move->start_right = move->last_right = sample->right_count;
    move->started_ms = move->last_poll_ms = now_ms;
    move->last_sample_ms = sample->sample_ms;
    move->left_progress_ms = move->right_progress_ms = now_ms;
    move->left_reached = false;
    move->right_reached = false;
    move->reason = DISTANCE_MOVE_REASON_NONE;
    move->phase = DISTANCE_MOVE_RUNNING;
    return true;
}

void distance_move_update(
    distance_move_t *move,
    const distance_move_sample_t *sample,
    uint32_t now_ms,
    bool motion_permitted
)
{
    uint32_t sample_step;
    uint64_t left_delta;
    uint64_t right_delta;
    if (move == NULL || move->phase != DISTANCE_MOVE_RUNNING) {
        return;
    }
    if (!motion_permitted) {
        abort_move(move, DISTANCE_MOVE_REASON_NOT_PERMITTED);
        return;
    }
    if (!sample_is_usable(move, sample, now_ms)) {
        return;
    }
    if ((uint32_t)(now_ms - move->last_poll_ms) >
        DISTANCE_MOVE_MAX_POLL_GAP_MS) {
        abort_move(move, DISTANCE_MOVE_REASON_POLL_GAP);
        return;
    }
    if ((uint32_t)(now_ms - move->started_ms) >= DISTANCE_MOVE_MAX_RUN_MS) {
        abort_move(move, DISTANCE_MOVE_REASON_RUN_TIMEOUT);
        return;
    }
    move->last_poll_ms = now_ms;
    sample_step = sample->sample_ms - move->last_sample_ms;
    if (sample_step >= 0x80000000U ||
        (sample_step == 0U &&
         (sample->left_count != move->last_left ||
          sample->right_count != move->last_right))) {
        abort_move(move, DISTANCE_MOVE_REASON_BAD_SAMPLE);
        return;
    }
    if (sample->left_count < move->last_left ||
        sample->right_count < move->last_right) {
        abort_move(move, DISTANCE_MOVE_REASON_COUNT_REVERSED);
        return;
    }
    /* Unsigned subtraction avoids signed overflow even across zero. */
    left_delta = (uint64_t)sample->left_count - (uint64_t)move->start_left;
    right_delta = (uint64_t)sample->right_count - (uint64_t)move->start_right;
    if (left_delta > (uint64_t)INT32_MAX ||
        right_delta > (uint64_t)INT32_MAX) {
        abort_move(move, DISTANCE_MOVE_REASON_COUNT_RANGE);
        return;
    }
    if (sample->left_count > move->last_left) {
        move->left_progress_ms = now_ms;
    }
    if (sample->right_count > move->last_right) {
        move->right_progress_ms = now_ms;
    }
    move->last_left = sample->left_count;
    move->last_right = sample->right_count;
    move->last_sample_ms = sample->sample_ms;

    /* Each cutoff is latched. Continued input cannot enable that side again. */
    move->left_reached = move->left_reached ||
        left_delta >= move->target_counts;
    move->right_reached = move->right_reached ||
        right_delta >= move->target_counts;
    if (move->left_reached && move->right_reached) {
        move->phase = DISTANCE_MOVE_TARGET_REACHED;
        return;
    }
    if ((!move->left_reached &&
         (uint32_t)(now_ms - move->left_progress_ms) >=
             DISTANCE_MOVE_NO_PROGRESS_MS) ||
        (!move->right_reached &&
         (uint32_t)(now_ms - move->right_progress_ms) >=
             DISTANCE_MOVE_NO_PROGRESS_MS)) {
        abort_move(move, DISTANCE_MOVE_REASON_NO_PROGRESS);
    }
}

void distance_move_cancel(distance_move_t *move)
{
    if (move != NULL && move->phase == DISTANCE_MOVE_RUNNING) {
        abort_move(move, DISTANCE_MOVE_REASON_CANCELLED);
    }
}

distance_move_output_t distance_move_output(const distance_move_t *move)
{
    distance_move_output_t output = {false, false};
    if (move != NULL && move->phase == DISTANCE_MOVE_RUNNING) {
        output.left_run = !move->left_reached;
        output.right_run = !move->right_reached;
    }
    return output;
}
```
