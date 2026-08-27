# Production Open-Loop Command Mapper

## 문서 상태

- Work package: `P-02A / P-02B / P-02C-1 / P-02C-2`
- 상태: `PRODUCTION CMD CALLER SOURCE/STATIC/BUILD PASS / BOARD RUNTIME PENDING`
- 작성일: 2026-08-26
- 최종 갱신: 2026-08-27
- 적용 범위: motor/LiPo-disconnected source, host/static test와 이후 저속 output request
- 제외 범위: 실제 속도 보장, PID, track-slip 보정, actual motor enable

이 문서는 UART `CMD(vx_mmps, w_mradps)`를 논리적인 좌우 signed PWM request로 바꾸는
첫 production mapper를 정의한다. 현재 단계에서는 encoder closed loop가 없으므로 출력은
**속도 명령의 저속 open-loop 비율**이다. 예를 들어 `vx_mmps=100`이 실제 주행속도
`100 mm/s`를 보장한다는 뜻은 아니다.

## 1. 현재 확정된 입력 계약

| 항목 | 값 | 처리 |
| --- | ---: | --- |
| `vx_mmps` | `-100~100 mm/s` | 범위 밖이면 `ERR,OUT_OF_RANGE`; clamp 금지 |
| `w_mradps` | `-500~500 mrad/s` | 범위 밖이면 `ERR,OUT_OF_RANGE`; clamp 금지 |
| `timeout_ms` | `50~500 ms` | 범위 밖이면 `ERR,TIMEOUT_OUT_OF_RANGE` |
| `PWM cap` | `100/1000` | 현재 motor-output 절대 상한, 즉 10% duty |
| 좌표계 | `+vx=전진`, `+w=좌회전` | logical vehicle frame |

Parser/state gate가 입력을 먼저 거부하더라도 mapper 자체도 같은 범위를 다시 검사한다.
잘못된 인자나 범위 밖 입력에서는 output을 zero로 만들고 실패를 반환한다.

## 2. 왜 지금 physical track-width 수식을 직접 사용하지 않는가

이상적인 differential-drive 역기구학은 다음과 같다.

```text
v_l = v - wB/2
v_r = v + wB/2
```

여기서 `B`는 effective track width다. 현재 저장소에는 실측·보정된 `B`가 없으며,
tracked vehicle은 바닥과의 slip 때문에 자로 잰 폭만으로 최종 회전 scale을 고정할 수도 없다.
따라서 P-02에서 임의의 `B`를 production constant로 만들지 않는다.

P-02는 먼저 다음을 검증하는 최소 단계다.

1. 전진/후진/좌회전/우회전 부호가 일관된다.
2. 두 축을 함께 요청해도 duty cap을 넘지 않는다.
3. 좌우 비율을 유지한 채 saturation한다.
4. HAL과 무관한 pure function으로 host test가 가능하다.

실측 `B`, track travel/count와 actual speed calibration은 `P-06` 및 chassis 시험에서
추가한다. 그 전까지 이 mapper를 calibrated kinematics 또는 speed controller라고 부르지 않는다.

## 3. 정규화와 differential mixing

입력을 각각 `-1000~1000`의 내부 request scale로 바꾼다.

```text
linear = vx_mmps   * 1000 / 100
yaw    = w_mradps  * 1000 / 500

raw_left  = linear - yaw
raw_right = linear + yaw
```

부호 해석:

- `linear > 0`: 양쪽 전진
- `yaw > 0`: left를 줄이고 right를 늘려 좌회전
- `linear = 0`, `yaw > 0`: left 후진, right 전진의 제자리 좌회전

## 4. Coupled saturation

좌우를 각각 따로 잘라내면 요청한 회전 비율이 바뀐다. 따라서 가장 큰 절댓값을 기준으로
양쪽을 같은 비율로 줄인다.

```text
peak = max(1000, abs(raw_left), abs(raw_right))

left_signed_permille  = raw_left  * duty_cap_permille / peak
right_signed_permille = raw_right * duty_cap_permille / peak
```

초기 `duty_cap_permille=100`이므로 최종 signed output은 항상 `-100~100`이다.
C의 signed integer division은 0 방향으로 버림하므로 `100/3` 계열 결과는 `33`으로
검증한다.

## 5. Pure-function interface

P-02B에 구현한 interface는 다음과 같다.

```c
typedef struct {
    int16_t left_signed_permille;
    int16_t right_signed_permille;
} drive_command_request_t;

bool drive_command_map(
    int32_t vx_mmps,
    int32_t w_mradps,
    uint16_t duty_cap_permille,
    drive_command_request_t *request
);
```

Interface 규칙:

- HAL type과 GPIO/TIM register를 포함하지 않는다.
- `request == NULL`이면 memory에 접근하지 않고 `false`를 반환한다.
- non-NULL output은 계산 전에 zero로 초기화한다.
- 성공하면 `request`에 `-cap~+cap` 계산값을 쓰고 `true`를 반환한다.
- 범위 검사가 실패하면 `false`를 반환하며, 먼저 기록한 zero를 유지해 stale request를 남기지 않는다.
- `duty_cap_permille > 100`은 거부한다. `0`은 명시적인 output-disabled 설정으로 허용한다.

## 6. P-02A 고정 test vectors

아래 값은 `duty_cap_permille=100`일 때의 exact integer 기대값이다.

| `vx` | `w` | 의미 | `raw L / R` | 최종 signed `L / R` |
| ---: | ---: | --- | ---: | ---: |
| 0 | 0 | 정지 | `0 / 0` | `0 / 0` |
| 100 | 0 | 최대 저속 전진 | `1000 / 1000` | `100 / 100` |
| -100 | 0 | 최대 저속 후진 | `-1000 / -1000` | `-100 / -100` |
| 50 | 0 | 절반 전진 | `500 / 500` | `50 / 50` |
| 0 | 500 | 제자리 좌회전 | `-1000 / 1000` | `-100 / 100` |
| 0 | -500 | 제자리 우회전 | `1000 / -1000` | `100 / -100` |
| 0 | 250 | 절반 좌회전 | `-500 / 500` | `-50 / 50` |
| 100 | 250 | 전진+좌회전, saturation | `500 / 1500` | `33 / 100` |
| -100 | 250 | 후진+좌회전, saturation | `-1500 / -500` | `-100 / -33` |
| 100 | 500 | 최대 전진+좌회전 | `0 / 2000` | `0 / 100` |

추가 경계 vector:

| 입력 | 기대 결과 |
| --- | --- |
| `cap=50`, `vx=100`, `w=0` | `true`, `50 / 50` |
| `cap=0`, valid command | `true`, `0 / 0` |
| `vx=101` 또는 `vx=-101` | `false`, output zero |
| `w=501` 또는 `w=-501` | `false`, output zero |
| `cap=101` | `false`, output zero |
| `request=NULL` | `false`, memory access 없음 |

## 7. Signed request와 physical output의 경계

Pure mapper는 GPIO polarity를 알지 못한다. P-02C-1에 구현한 별도 adapter가 다음 변환을 맡는다.

```text
signed request > 0 -> forward DIR 후보 + magnitude PWM
signed request < 0 -> reverse DIR 후보 + abs(request) PWM
signed request = 0 -> PWM 0
```

현재 source naming은 logical left를 `TIM4_CH1/PB6 + PC8`, logical right를
`TIM4_CH2/PB7 + PC9`에 연결한다. 그러나 이는 **provisional software mapping**이다.
MDD10A CH1/CH2가 실제 vehicle left/right motor로 이어지는지와 어느 DIR level이 actual
forward인지는 powered drivetrain evidence가 없다.

P-02C-1은 다음을 상수와 주석으로 명시했으며, lifted low-duty test 전에는 final로
주장하지 않는다.

- logical left -> CH1: `PROVISIONAL`
- logical right -> CH2: `PROVISIONAL`
- left/right forward DIR level: `PROVISIONAL`

## 8. 안전한 production 통합 순서

```text
range/timeout validation
-> ARMED 확인
-> E-stop latch 확인
-> pure mapper 계산
-> output 직전 E-stop 재확인
-> signed request를 PWM/DIR로 적용
-> output 적용 직후 E-stop 재확인
-> 성공한 경우에만 stored CMD/timestamp 갱신과 ACK
```

Mapper 또는 output 적용이 실패하면 PWM을 모두 zero로 만들고 stored command도 zero로
유지해야 한다. 기존 controlled output hook은 production mapper와 분리하고 최종 baseline에서
계속 `0U`여야 한다.

P-02C-2에서 이 순서를 `handle_cmd()`에 연결했다. Controlled hook이 활성화된 경우에는 기존
raw 시험 경로만 실행하고, 현재 release 기본값처럼 hook이 `0U`이면 mapper 결과를
`motor_output_set_signed()`에 전달한다. 두 경로는 `if`/`else if`로 상호 배타적이다.

Mapper 또는 raw/signed output 적용 실패 경로는 다음을 수행한 뒤 ACK 없이 반환한다.

```text
motor_output_stop_all()
-> stored vx/w zero
-> MAPPER_FAILED 또는 MOTOR_OUTPUT_FAILED ERR
-> return
```

## 9. 현재 검증 결과와 다음 단계

2026-08-27 P-02B 결과:

1. `drive_command_mapper.h/.c` HAL-independent source 구현: `PASS`
2. 위 12개 성공 vector와 5개 범위 실패, NULL/stale-output 계약의 독립 Python reference test: `PASS`
3. C source 상수, interface, zero-before-validation, mixing과 coupled-saturation 정적 계약: `PASS`
4. canonical discovery: firmware contract `19/19` + mapper vectors `2/2` + UART frame `2/2`, 합계 `23/23 PASS`
5. STM32CubeIDE full Debug build: `0 errors, 0 warnings`

2026-08-27 P-02C-1 결과:

1. `motor_output_set_signed(int16_t left, int16_t right)` adapter source: `PASS`
2. `-100~100` range guard, sign-to-provisional-DIR, magnitude-to-PWM, raw failure stop contract: `PASS`
3. canonical discovery: firmware contract `20/20` + mapper vectors `2/2` + UART frame `2/2`, 합계 `24/24 PASS`
4. STM32CubeIDE incremental Debug build가 `motor_output.c`를 다시 compile하고 ELF를 relink:
   `0 errors, 0 warnings`
5. CubeIDE bundled ARM toolchain `make -B`: 전체 32 objects 강제 재컴파일, exit `0`,
   compiler/linker diagnostic 0건, ELF `text=28236`, `data=172`, `bss=2832`
6. `motor_output.c` 단독 strict syntax check:
   `-Wall -Wextra -Wconversion -Wsign-conversion -Werror`, exit `0`
7. Link map의 `.text.motor_output_set_signed` address `0`: caller가 없어 `--gc-sections`에서
   제거된 expected no-caller 상태

위 7번은 P-02C-1 당시의 **historical `24/24` checkpoint**다. 이후 P-02C-2 caller 통합으로
해당 no-caller 상태는 해소됐다.

2026-08-27 P-02C-2 결과:

1. Production `handle_cmd()`에 mapper와 signed adapter caller 연결: `PASS`
2. `100 permille = 10%` cap, 세 번의 E-stop guard, controlled raw/production signed 상호 배타
   경로와 success-only state commit/ACK 정적 계약: `PASS`
3. Mapper/output 실패 시 stop-all, stored `vx/w` zero, `ERR`, 즉시 return 계약: `PASS`
4. canonical discovery: firmware contract `21/21` + mapper vectors `2/2` + UART frame `2/2`,
   합계 `25/25 PASS`
5. CubeIDE bundled ARM toolchain forced full build: 전체 32 objects, exit `0`, compiler/linker
   `warning:`/`error:` 진단 0건, ELF `text=29216`, `data=172`, `bss=2832`
6. Final ELF link map: `drive_command_map=0x0800067c`,
   `motor_output_set_signed=0x080015dc`; 두 함수 모두 nonzero address로 production caller에 유지됨

다음 단계:

1. `[SOURCE/STATIC/FULL BUILD COMPLETE] P-03`: pre-RX timeout에서 output/stored command
   zero 후 `DISARMED`로 전이하고, `ARM` 시 default 300 ms first-CMD window를 다시 시작한다.
   Motor/LiPo-disconnected target runtime은 pending이다.
2. `P-04`: 현재 zero placeholder인 TEL PWM/applied-output field를 실제 적용값과 연결한다.
3. 집 `H-02`에서 motor/LiPo를 분리한 채 UART와 MCU PWM/DIR만 검증한다.
4. Physical E-stop 선행 Gate 뒤에만 lifted low-duty motor mapping으로 이동한다.

## Evidence Boundary

P-02B는 mapper source, 독립 수학 reference vector, C source 정적 계약과 STM32 full build를,
P-02C-1은 signed adapter source/static 계약을, P-02C-2는 production caller의 제어 순서와
final ELF linkage를 증명한다.
Python reference test는 C 함수를 직접 실행하는 native unit test가 아니며, 정적 계약이 두 구현의
상수·순서·수식을 연결한다. 두 함수의 nonzero address는 링크 증거일 뿐 실행 증거가 아니다.
따라서 flash, board runtime, PWM/DIR waveform, actual channel mapping, provisional DIR polarity,
actual motor speed와 chassis motion은 증명하지 않는다. TEL PWM/applied-output field도 아직 실제
출력과 연결되지 않고 zero placeholder다. Timeout-to-`DISARMED` source/static/full-build는 P-03에서
PASS했지만 target runtime은 남아 있다.
