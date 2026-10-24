# 작은 C 프로그램에서 두 보드의 로봇 펌웨어까지

## STM32·ESP32 펌웨어를 기초부터 다시 만드는 교과서

**기준일: 2026-10-13 · 대상: NUCLEO-F446RE + ESP32-S3 · 현재 Wi-Fi 제어 범위: 속도 0**

이 책의 목표는 기존 코드를 외우는 것이 아니다. 작은 프로그램에 요구사항을 하나씩 더했을 때 왜 지금의 함수, 자료구조, 상태, 시간 제한이 필요한지 설명하고, 독자가 작은 버전을 직접 재구성할 수 있게 하는 것이다.

분석의 출발점은 실제 저장된 [STM main][stm-main]과 [ESP main][esp-main]이다. STM의 사용자 모듈과 주변장치 초기화, ESP의 다섯 제어 모듈과 내장 브라우저, 이전 UART bridge와 단계별 ESP 예제를 함께 대조했다. 전체 ST HAL·ESP-IDF 내부 구현을 줄마다 해설하는 책은 아니다. 그 라이브러리가 현재 앱과 만나는 지점까지 다룬다.

저장된 소스와 보드에 올라간 바이너리는 다른 대상이다. [소스 목록과 해시](source_manifest.json)는 이 책이 읽은 작업 트리를 식별한다. 시험 통과를 선언하는 문서는 [검증 문서](../../docs/verification/README.md)이며, 이 책의 예제 실행 결과는 보드 검증을 대신하지 않는다.

### 목차

처음 읽을 때는 [12개 학습 단위와 완료 기준](README.md#study-route)을 따라 한 범위씩 읽는다. 아래 목차는 나중에 다시 찾아볼 때 사용한다. 14장 다음에는 [심화로 넘어가는 연결 수업](#bridge-control)이 있다.

| 순서 | 장 | 끝나면 할 수 있는 일 |
| --- | --- | --- |
| 0 | [학습 경로와 시스템 전체 그림](#ch00) | 명령과 관측의 흐름을 그린다 |
| 1 | [펌웨어와 빌드의 기초](#ch01) | 소스·빌드·플래시·실행을 구별한다 |
| 2 | [실제 코드를 읽기 위한 C](#ch02) | 포인터·구조체·static·헤더를 읽는다 |
| 3 | [GPIO·클록·주변장치](#ch03) | 핀 이름과 주변장치 설정을 연결한다 |
| 4 | [무한 루프에서 시간 관리로](#ch04) | delay 없이 주기와 만료를 판단한다 |
| 5 | [UART·인터럽트·링 버퍼](#ch05) | 흩어진 바이트로 한 줄을 만든다 |
| 6 | [문자열을 명령으로 만드는 parser](#ch06) | 형식 오류와 실행 거부를 구별한다 |
| 7 | [STM의 상태·timeout·E-stop](#ch07) | ARM, CMD, DISARM의 차이를 설명한다 |
| 8 | [PWM·DIR·명령 혼합](#ch08) | 명령에서 출력 비교값까지 계산한다 |
| 9 | [엔코더·wrap·CPS](#ch09) | 카운터 차이를 속도로 바꾼다 |
| 10 | [STM 앱 전체 조립](#ch10) | 부팅부터 ACK/TEL까지 추적한다 |
| 11 | [ESP-IDF·태스크·큐·mutex](#ch11) | 누가 어떤 데이터를 소유하는지 설명한다 |
| 12 | [Wi-Fi·HTTP·WebSocket·JavaScript](#ch12) | 브라우저 코드와 ESP 코드를 구분한다 |
| 13 | [상태 전달과 신선도](#ch13) | 통신 정상과 제어 가능을 구별한다 |
| 14 | [PING/DISARM과 요청 식별](#ch14) | 접수·송신·응답·정지 확인을 나눈다 |
| 15 | [ticket·owner·제어 세대](#ch15) | 낡은 요청을 왜 버리는지 설명한다 |
| 16 | [ESP 제어 상태 머신](#ch16) | ACK와 TEL을 사건으로 상태를 진행시킨다 |
| 17 | [executor·동시성·통합](#ch17) | 취소와 UART 송신 경계를 설명한다 |
| 18 | [브라우저 의도·시간 예산·정지](#ch18) | 포커스 상실과 재접속을 처리한다 |
| 19 | [실제 디버깅과 검증](#ch19) | 로그로 가설을 좁히고 증거 범위를 정한다 |
| 20 | [작은 버전부터 재구성하는 종합 과제](#ch20) | 빈 파일에서 핵심 흐름을 재현한다 |
| 부록 | [소스 지도·용어·참고 자료](#appendix) | 원본 함수와 심화 자료를 찾는다 |

<a id="ch00"></a>
## 0장. 완성 코드보다 먼저 알아야 할 전체 그림

### 0.1 이 시스템이 해결하는 문제

브라우저는 사람의 입력을 받는다. ESP는 무선 연결과 요청 처리를 맡는다. STM은 마지막으로 명령을 검사하고 PWM·DIR 출력을 제어한다. 돌아오는 TEL은 STM이 자신에 대해 보고한 상태다.

~~~mermaid
flowchart LR
    B["브라우저: 사용자 의도"] -->|"WebSocket 요청"| E["ESP: 연결·권한·기한 검사"]
    E -->|"UART 명령"| S["STM: 상태·E-stop·timeout"]
    S --> P["PWM·DIR 출력"]
    Q["엔코더 입력"] --> S
    S -->|"ACK / ERR / TEL"| E
    E -->|"JSON"| B
~~~

처음부터 이 그림 전체를 구현하려고 하면 모든 개념이 동시에 등장한다. 대신 다음 질문을 차례로 해결한다.

1. C 변수에 값을 저장하고 함수에 넘길 수 있는가?
2. 외부 바이트가 언제 들어와도 잃지 않고 모을 수 있는가?
3. 받은 문자열이 정확한 명령인지 판단할 수 있는가?
4. 정확한 명령이라도 현재 상태에서 실행해도 되는가?
5. 명령이 끊기거나 뒤늦게 도착하면 어떻게 되는가?
6. 두 실행 흐름이 동시에 상태를 바꾸면 어떻게 되는가?
7. 화면의 성공 표시가 실제 무엇을 증명하는가?

현재 모듈은 이 질문들에 대한 답을 나눈 것이다. 파일 개수가 실력의 척도는 아니다. 작은 실습에서는 한 파일에 만들어도 된다. 요구사항과 검증이 늘면서 책임을 나누는 이유를 이해하면 된다.

### 0.2 이 책의 세 가지 코드 표시

- **개념 예제:** 핵심 한 가지만 보이도록 줄였다. 제품 코드의 교체본이 아니다.
- **실제 소스 발췌/수식:** 저장된 코드의 함수·값·동작을 설명한다.
- **PC 실행 예제:** [examples](examples/README.md)에 전체 파일이 있으며 보드 없이 실행한다.

모터에 비영 속도를 보내는 예제는 실행 절차로 제공하지 않는다. 숫자 예제의 `vx=50` 등은 PC에서 계산만 한다. 현재 Wi-Fi 경로는 `WIFI_CONTROL_ZERO_ONLY=1U`이고 executor도 UART CMD의 두 속도를 0으로 작성한다.

### 0.3 현재 있는 기능과 없는 기능

현재 STM은 HAL 기반 무한 루프와 UART 인터럽트를 사용한다. ESP는 ESP-IDF의 FreeRTOS 태스크와 HTTP 서버를 사용한다. STM에 FreeRTOS가 이미 들어갔다고 읽으면 안 된다.

STM에는 정규화한 개방 루프 명령 혼합과 엔코더 관측이 있다. 아직 엔코더 오차로 PWM을 조절하는 속도 PID나 오도메트리가 이 경로에 연결된 것은 아니다. TEL의 배터리 값도 실제 ADC 측정값으로 제공되지 않는다. CAN·ROS 2·Nav2는 이 책의 현재 코드 완성 지점 이후의 확장이다.

**생각 문제:** 브라우저에 `ARMED`가 보이면 모터가 움직였다는 뜻일까?

**해설:** 아니다. ARMED는 STM의 명령 수락 상태다. 현재 CMD는 속도 0이고, 출력 소프트웨어 값과 실제 핀 파형·모터 운동도 각각 따로 관측해야 한다.

<a id="ch01"></a>
## 1장. 펌웨어는 어떻게 실행되는가

### 1.1 소스 파일은 CPU가 직접 읽는 문서가 아니다

C 소스는 컴파일러가 기계어를 만들기 위한 입력이다. 헤더를 포함하고 매크로를 처리하는 전처리, 각 C 파일을 목적 파일로 만드는 컴파일, 함수와 변수의 참조를 연결하는 링크가 이어진다.

~~~text
.c + .h
  → 전처리 / 컴파일
  → 여러 목적 파일(.o)
  → 링크 스크립트와 라이브러리 결합
  → 실행 이미지(.elf, .bin 등)
  → 플래시 메모리에 기록
  → 리셋 후 실행
~~~

`.h`에 함수 선언이 있어도 그 함수가 들어 있는 `.c`를 빌드하지 않으면 링크 오류가 날 수 있다. 반대로 컴파일·링크가 성공해도 초기화가 틀렸거나 실제 호출 경로가 없으면 원하는 동작은 일어나지 않는다.

### 1.2 main 이전에도 코드가 있다

STM은 리셋 벡터로 시작해 startup 코드와 C 런타임 초기화를 거쳐 `main()`에 들어온다. 초기값이 있는 전역·static 데이터가 준비되고, 0 초기화 영역도 준비된다. CPU가 GPIO 이름을 알아서 해석하는 것이 아니라, 나중에 GPIO 레지스터와 클록을 설정하는 코드가 실행된다.

ESP의 앱 진입점은 `app_main()`이다. ESP-IDF의 초기화와 스케줄러 시작 이후 main 태스크에서 호출된다. 그래서 `app_main` 안에서 `vTaskDelay`와 태스크 API를 사용할 수 있다. 일반 사용자 태스크의 반환 규칙과 `app_main`의 특별한 종료 처리를 혼동하지 않는다. [ESP-IDF FreeRTOS 문서][idf-rtos]

### 1.3 메모리를 세 종류로 먼저 이해하기

| 저장 방식 | 예 | 수명과 주의점 |
| --- | --- | --- |
| 전역/static 저장 | `static stm_telemetry_t s_stm_telemetry;` | 앱 실행 동안 유지된다. 공유하면 동기화가 필요하다 |
| 함수의 자동 변수 | `char line[128];` | 일반적으로 해당 호출의 스택에 있다. 함수가 끝난 뒤 포인터를 보관하면 안 된다 |
| 동적 할당 | `calloc(1, sizeof(*session))` | 할당 실패를 처리하고, 사용 종료 때 `free`해야 한다 |

현재 ESP의 요청·결과 큐는 구조체를 값으로 복사한다. 지역 배열의 주소만 큐에 넣으면 HTTP 처리 함수가 끝난 뒤 UART 태스크가 사라진 데이터를 읽을 수 있다. 복사와 포인터의 차이가 뒤에서 중요한 이유다.

### 1.4 CMake가 해주는 일

실제 [main/CMakeLists.txt][esp-cmake]는 `idf_component_register(SRCS ...)`로 여섯 C 파일을 지정한다. 파일을 만들었다고 이 목록이 자동 작성되는 방식이 아니다. 이 저장소는 명시적으로 소스 목록을 관리한다.

~~~cmake
# 원리를 보여 주는 축약 예. 현재 CMake의 교체본이 아니다.
idf_component_register(
    SRCS "wifi_link_main.c" "wifi_control_contract.c"
    INCLUDE_DIRS "."
)
~~~

현재 목록에는 contract·ticket·owner·state·executor와 main이 들어간다. 헤더는 `#include` 검색 경로에서 찾고, C 파일은 컴파일 대상으로 등록한다.

**연습:** “빌드 성공, 화면 안 바뀜”의 가능한 원인 세 가지를 적어라.

**해설:** 다른 앱 폴더를 빌드했을 수 있고, 새 이미지를 플래시하지 않았을 수 있고, 브라우저가 이전 페이지를 유지할 수 있다. 소스 저장·빌드 대상·플래시 대상·페이지 새로고침을 각각 확인해야 한다.

<a id="ch02"></a>
## 2장. 실제 펌웨어를 읽기 위한 C 문법

### 2.0 변수·조건·반복·함수부터 연결하기

변수는 이름이 붙은 저장 공간이고 대입은 그 값을 바꾸는 일이다. `=`는 대입, `==`는 같은지 비교다. 함수는 입력을 받아 일을 하고 필요하면 결과를 반환한다.

~~~c
/* 문법을 연결하는 개념 예제 */
int clamp_to_ten(int value)
{
    if (value < 0) return 0;
    if (value > 10) return 10;
    return value;
}

/* 함수 안에서 쓰는 반복 예 */
/* for (int i = 0; i < 3; ++i) {
 *     int limited = clamp_to_ten(i * 8);
 *     // limited는 차례로 0, 8, 10이다.
 * }
 */
~~~

`if`는 조건이 참일 때 실행한다. `return`은 지금 함수를 끝내고 호출한 곳으로 돌아간다. `for`는 초기화→조건 확인→본문→증가를 반복한다. `while (1)`은 계속 참이므로 종료시키는 별도 동작이 없는 한 반복한다.

변수를 선언한 블록의 중괄호 밖에서는 그 이름을 사용할 수 없는 경우가 있다. 이름을 볼 수 있는 범위와 값이 살아 있는 수명은 관련 있지만 같은 개념은 아니다. 아래의 static·포인터 수명을 이 관점에서 읽는다.

`#define LIMIT 10U`는 전처리 단계의 치환이고 `enum`은 의미 있는 정수 상수 집합을 만든다. 상태를 0, 1, 2로 직접 쓰는 대신 `ROBOT_DISARMED`처럼 이름 붙이면 조건을 읽기 쉽다. `#if TEST_ENABLED`는 실행 중 조건 검사가 아니라 빌드에 포함할 코드를 고르는 조건이다.

### 2.1 타입과 단위부터 읽는다

`uint32_t`는 부호 없는 32비트 정수다. `int32_t`는 부호 있는 32비트 정수다. 카운터·번호에는 전자가, 전진/후진처럼 음수가 필요한 값에는 후자가 쓰인다. `bool`은 조건을 표현한다.

변수명에서 단위도 읽는다. `vx_mmps`는 mm/s, `w_mradps`는 mrad/s, `accepted_ms`는 ms다. `cps`는 초당 count이고 `permille`는 1/1000 단위다. `100 permille = 10%`다. `100`이라는 숫자만 같다고 서로 대입하면 안 된다.

~~~c
/* 개념 예제 */
uint32_t request_id = 7U;
int32_t vx_mmps = -50;
bool accepted = false;
~~~

`U`는 unsigned 정수 리터럴 접미사, `LL`은 long long 접미사다. 곱셈 전에 충분히 큰 타입을 쓰지 않으면 결과를 큰 변수에 대입해도 이미 발생한 overflow를 되돌리지 못한다.

### 2.2 구조체는 관련된 값의 묶음이다

~~~c
/* 개념 예제 */
typedef struct {
    uint32_t seq;
    int32_t vx_mmps;
    int32_t w_mradps;
} command_t;

command_t command = {0};
command.seq = 10U;
~~~

`{0}`은 멤버를 0으로 초기화한다. 현재 `wifi_control_request_t`는 요청 번호·boot·ticket·속도·ESP 접수 시각을 묶는다. 구조체는 자동으로 올바른 값을 보장하지 않으므로 parser와 상태 검사가 따로 필요하다.

### 2.3 포인터와 출력 인자

~~~c
/* 개념 예제 */
bool make_zero_command(uint32_t seq, command_t *out)
{
    if (out == NULL) return false;
    *out = (command_t){ .seq = seq };
    return true;
}
~~~

`command_t *out`은 command 자체가 아니라 command가 있는 위치다. 호출자는 `make_zero_command(10U, &command)`로 주소를 보낸다. `*out = ...`은 그 위치의 값을 바꾸고, `out->seq`는 포인터가 가리키는 구조체의 멤버를 뜻한다.

반환값은 “성공 여부”, 출력 인자는 “만들어진 자료”로 나누면 호출자가 실패를 쉽게 처리할 수 있다. 실제 parser를 호출한 뒤에는 반드시 반환 상태를 먼저 확인해야 한다.

### 2.4 배열·문자열·길이는 별개다

~~~c
char text[] = "ARM";  /* 'A', 'R', 'M', '\0': 배열 크기는 4 */
~~~

C 문자열은 `'\0'`으로 끝난다. UART나 WebSocket이 준 바이트에는 이 종료 문자가 없을 수 있다. `strlen`은 종료 문자를 찾을 때까지 읽으므로 수신 버퍼에 무조건 적용할 수 없다.

현재 STM parser는 `line + line_len` 범위 안에서 읽는다. ESP control parser는 길이와 허용 문자를 검사한 뒤 내부 `buffer[129]`로 복사하고 `buffer[length]='\0'`을 붙인다. 목적은 같지만 구현 방식은 다르다.

### 2.5 const·static·volatile를 구분한다

| 표현 | 뜻 | 뜻하지 않는 것 |
| --- | --- | --- |
| `const char *p` | 이 포인터를 통해 문자를 수정하지 않는다 | 데이터가 항상 유효하거나 다른 실행 흐름이 못 바꾼다는 보장은 아니다 |
| 파일 범위 `static` | 해당 C 파일 안에서만 이름을 사용한다 | 여러 태스크 사이에서 보호된다는 뜻이 아니다 |
| 함수 안 `static` | 호출이 끝나도 값이 유지된다 | 매 호출마다 0으로 리셋되지 않는다 |
| `volatile` | 접근을 임의로 생략·합치지 않도록 컴파일러에 요구한다 | mutex·원자성·멀티코어 메모리 순서를 대신하지 않는다 |

STM 링 버퍼의 `head/tail`은 ISR과 main이 공유한다. 이 단일 생산자/단일 소비자 구조를 이해한 뒤 읽어야 한다. 같은 코드를 그대로 ESP의 여러 코어/생산자에 적용하면 안 된다.

### 2.6 헤더와 소스의 역할

`.h`는 타입과 함수 사용 약속을 공개하고 `.c`는 계산과 상태 변경을 구현한다. 헤더 가드는 중복 포함을 막는다. 구현 내부 함수에 `static`을 붙이면 모듈 바깥에서 직접 호출할 수 없게 만든다.

`wifi_control_state.h`를 먼저 보면 “어떤 사건을 전달할 수 있는가”가 보인다. `wifi_control_state.c`에서는 “그 사건이 현재 상태에서 무슨 결과를 만드는가”를 읽는다. 두 파일은 중복 문서가 아니라 인터페이스와 구현이다.

### 2.7 bit flag를 읽는 방법

state의 action 값에는 `INVALIDATE_INPUTS=1U`와 `SEND_DISARM=2U`가 있다. `1 | 2 = 3`이면 둘 다 필요하다는 뜻이다.

~~~c
/* 개념 예제 */
if ((actions & WIFI_CONTROL_ACTION_SEND_DISARM) != 0U) {
    /* 송신을 맡은 계층에 정지 명령을 준비시킨다. */
}
~~~

`|`는 비트를 합치고 `&`는 해당 비트가 있는지 검사한다. `||`와 `&&`는 논리 연산이다.

**연습:** 지역 변수 `r`의 주소를 큐에 보관하는 것과 `sizeof(r)` 바이트를 복사하는 것의 차이는?

**해설:** 주소 보관은 원래 객체의 수명과 이후 변경에 영향을 받는다. 값 복사는 별도 사본이다. 단, 구조체 안에 포인터 멤버가 있으면 포인터가 가리키는 내용까지 깊게 복사되는 것은 아니다.

**실행:** [예제 01](examples/01_c_and_time.c)은 구조체를 포인터로 갱신하고 시간 계산까지 연결한다.

<a id="ch03"></a>
## 3장. GPIO·클록·주변장치

### 3.1 핀과 UART는 같은 것이 아니다

GPIO는 핀을 일반 입력/출력으로 쓸 수 있게 한다. UART·타이머 같은 주변장치도 같은 핀을 사용할 수 있는데, 그때는 alternate function(AF)을 설정한다. “PA9에 UART 신호선을 연결했다”만으로 UART가 켜지지 않는다. GPIO·주변장치 클록·AF·baud·인터럽트 설정이 함께 맞아야 한다.

현재 저장 소스의 대응은 다음과 같다. 이것은 코드 읽기용 지도이며 새 배선 작업 지시가 아니다.

| 역할 | STM 설정 | 대응 |
| --- | --- | --- |
| ESP로 명령/응답 연결 | USART1 PA9 TX / PA10 RX | PA9 → ESP GPIO18 RX, ESP GPIO17 TX → PA10 |
| PC 진단 로그 | USART2 PA2 TX / PA3 RX | UART1의 제어 경로와 구분 |
| 좌·우 PWM | TIM4 CH1 PB6 / CH2 PB7 | [motor_output][motor]에서 CCR 변경 |
| 좌·우 DIR | PC8 / PC9 | 부호를 방향 레벨로 바꾼다 |
| E-stop sense | PC7 입력, pull-up | HIGH를 active로 해석 |
| 좌 엔코더 | TIM3 PB4/PB5 | 차량 좌측 CPS에 raw 부호 반전 |
| 우 엔코더 | TIM5 PA0/PA1 | 차량 우측 CPS에 raw 부호 유지 |

### 3.2 pull-up은 무엇을 하는가

입력 핀이 구동되지 않으면 불안정한 값을 읽을 수 있다. pull-up은 약하게 HIGH로 당긴다. PC7의 현재 코드가 HIGH를 fault로 해석하므로, 정상 sense 회로가 연결되지 않은 보드에서 FAULT가 보이는 것은 이 설정과 모순되지 않는다.

현재 USART1 RX PA10도 USER CODE에서 pull-up을 적용한다. GPIO pull-up과 외부 optocoupler·배선·전원 도메인의 역할은 다르다. 소프트웨어 해설에서 PC7을 임의로 LOW로 우회하는 절차를 만들지 않는다.

### 3.3 클록이 있어야 시간이 생긴다

타이머는 입력 클록을 세는 장치다. 현재 `SystemClock_Config`는 HSI·PLL로 SYSCLK 84 MHz, APB1 분주 2를 구성한다. TIM4의 입력 클록을 기본 TIMPRE 설정에서 84 MHz로 계산하면, `PSC=0`과 `ARR=4420`의 주기는 다음과 같다.

~~~text
PWM 주파수 = timer_clock / ((PSC + 1) × (ARR + 1))
           = 84,000,000 / (1 × 4421)
           ≈ 19,000 Hz
~~~

이는 설정으로부터 계산한 값이지 여기서 새로 측정한 파형값은 아니다. STM32F446의 APB 분주·타이머 클록 관계는 단순히 “CPU 클록과 같다”로 일반화하지 말고 RCC/TIMPRE와 TIM 장을 함께 확인한다. [ST의 STM32F446 공식 문서 목록][st-docs]에서 RM0390을 찾을 수 있다.

### 3.4 HAL 핸들은 주변장치의 문맥이다

`UART_HandleTypeDef huart1`은 UART1 설정과 HAL 처리 상태를 묶은 객체다. `HAL_UART_Receive_IT(&huart1, &byte, 1)`은 어떤 UART에서 어느 메모리로 몇 바이트를 받을지 전달한다.

`HAL_GPIO_WritePin`처럼 결과가 void인 API와 `HAL_TIM_PWM_Start`처럼 성공 여부를 반환하는 API는 호출 후 처리도 다르다. 초기화 순서와 반환값을 무시하면 코드가 계속 실행돼도 주변장치는 준비되지 않았을 수 있다.

**연습:** UART RX 선이 PA10에 있는데 USART2 설정만 바꾸면 왜 효과가 없는가?

**해설:** 현재 보드 간 연결은 USART1이다. 먼저 사용하는 주변장치 인스턴스와 핀 AF를 확인해야 한다. 함수 이름의 “UART”만 보고 다른 인스턴스를 수정하면 안 된다.

<a id="ch04"></a>
## 4장. 무한 루프에서 시간 관리로

### 4.1 가장 작은 앱에서 생기는 문제

처음에는 LED를 켜고 `HAL_Delay(1000)`한 뒤 끄는 코드로 충분하다. 하지만 그 대기 중 main에서 해야 할 명령 처리·timeout 검사가 늦어진다. 인터럽트가 동작하는 것과 main이 받은 명령을 처리하는 것은 별개다.

따라서 루프를 “할 일이 있으면 조금 처리하고 돌아오는 함수”로 나눈다.

~~~c
/* 개념 예제. 초기화가 된 앱의 반복부를 설명한다. */
for (;;) {
    read_pending_bytes();
    check_command_timeout();
    if ((uint32_t)(now_ms() - last_tel_ms) >= 100U) {
        last_tel_ms = now_ms();
        publish_telemetry();
    }
}
~~~

이 예제의 함수는 개념 이름이다. 실제 STM은 `encoder_speed_log_process → motor_output_pin_test_process → uart_mvp_process` 순서로 반복한다.

### 4.2 unsigned 시간 차이

32비트 ms 카운터는 언젠가 최대값 다음 0으로 돌아온다. 짧은 구간의 경과 시간은 unsigned 뺄셈으로 계산할 수 있다.

~~~c
uint32_t then = UINT32_MAX - 9U;
uint32_t now = 20U;
uint32_t elapsed = now - then;  /* 30 ms */
~~~

`now >= then + timeout`은 덧셈 쪽 wrap 때문에 틀릴 수 있다. `(uint32_t)(now-then) >= timeout`은 전체 wrap을 한 바퀴 이상 놓치지 않는 등의 전제에서 짧은 주기 비교에 적합하다.

ESP는 `esp_timer_get_time()/1000U`의 64비트 ms를 사용한다. state의 `within(now, then, budget)`은 `now >= then`과 `now-then < budget`을 모두 확인한다. STM 32비트 clock의 wrap 처리와 ESP 시간 역행 검사는 같은 문제로 묶지 않는다.

### 4.3 경계값은 요구사항이다

ticket이 100 ms에 발급되고 150 ms 동안 유효하면 만료 시각은 250 ms다.

| 검사 시각 | 판정 |
| --- | --- |
| 249 ms | 시간 조건 통과 가능 |
| 250 ms | 만료 |
| 251 ms | 만료 |

“약 150 ms”가 아니라 `now < expires`라는 비교가 실제 동작을 결정한다. 예제와 테스트는 임계값 바로 앞·정확한 임계값·바로 뒤를 다룬다.

### 4.4 주기 목표와 보장 시간을 구분하기

100 ms마다 보내도록 작성했다고 항상 정확히 100 ms에 실행되는 것은 아니다. UART 대기·로그 출력·스케줄링·네트워크 지연이 영향을 준다. `HAL_UART_Transmit`과 방향 전환 때의 짧은 `HAL_Delay`가 현재 STM 경로에 실제 존재한다. 이 앱 전체를 “완전 비차단”이라고 부르면 틀린다.

**연습:** 마지막 CMD를 1000 ms에 받은 STM에서 timeout이 300 ms다. 1299와 1300 ms의 판정은?

**해설:** 1299는 timeout 전, 1300은 timeout 조건 충족이다. 실제 PWM이 그 순간에 바뀌었는지는 다음 검사 실행 시점과 출력 갱신·측정 결과까지 봐야 한다.

<a id="ch05"></a>
## 5장. UART 바이트를 잃지 않고 명령 한 줄로 만들기

### 5.1 한 줄은 한 번에 도착하지 않는다

송신 측이 `ARM,seq=7\n`을 한 번에 썼어도 수신 측은 `AR`, `M,seq=`, `7\n`처럼 나눠 받을 수 있다. UART는 이 프로젝트의 명령 구조를 모른다. 바이트의 흐름을 줄 단위로 모으는 것은 앱의 책임이다.

115200/8N1은 데이터 8비트 외에 start/stop을 포함해 한 바이트에 통상 10비트가 필요하다. 100바이트를 선로에 보내는 데만 대략 `100×10/115200 ≈ 8.68 ms`가 든다. 이것은 처리·응답·무선 왕복 시간 전체가 아니다.

### 5.2 ISR에는 짧은 일을 맡긴다

STM의 수신 흐름은 다음과 같다.

~~~text
USART1 IRQ
 → HAL_UART_IRQHandler
 → HAL_UART_RxCpltCallback
 → uart_mvp_on_rx_complete
 → ring_buffer_push(한 바이트)
 → 다음 1바이트 HAL_UART_Receive_IT 예약
~~~

callback 안에서 한 줄을 기다리거나 오래 출력하지 않는다. ISR이 받은 것을 임시 저장하고, main이 나중에 해석한다. [실제 프로토콜 코드][stm-protocol]에서 callback 경로와 main 처리 경로를 나란히 읽어라.

### 5.3 링 버퍼는 끝에서 처음으로 돌아오는 배열이다

`head`는 다음에 쓸 위치, `tail`은 다음에 읽을 위치다. `head==tail`은 비어 있음을 뜻한다. 가득 찼는지와 구분하기 위해 한 칸을 비워 둔다.

현재 배열 크기는 256이므로 실제 저장 가능량은 255바이트다.

~~~c
/* 실제 방식의 핵심을 축약 */
next_head = (head + 1U) % 256U;
if (next_head == tail) {
    /* full: 새 바이트를 버리고 drop을 기록 */
} else {
    buffer[head] = byte;
    head = next_head;
}
~~~

가득 찬 버퍼를 크게 만드는 것만으로 모든 문제가 해결되지는 않는다. 소비 속도가 계속 느리면 더 늦게 가득 찰 뿐이다. 로봇 명령은 오래 대기한 자료를 나중에 전부 실행하는 것도 바람직하지 않다.

### 5.4 줄 조립은 parser 전 단계다

`uart_mvp_process`는 바이트를 꺼내 `'\n'`까지 모은다. 바로 앞의 `'\r'`은 제거해서 CRLF를 허용한다. 유효 명령 본문 한도는 127바이트다.

한 줄을 너무 길게 받거나 바이트 손실을 감지했다면 다음 LF까지 버려 경계를 다시 찾는다. 예를 들어 `DISARM`의 일부가 유실됐는데 뒤의 문자와 합쳐 새 명령으로 해석하면 안 된다.

`begin_rx_resynchronization`에서는 ISR과 동시에 큐를 비우지 않도록 짧게 인터럽트를 막고, 이전 PRIMASK를 복구한다. 무조건 인터럽트를 켜 버리면 호출 전부터 막혀 있던 상태를 훼손할 수 있다.

### 5.5 ESP의 수신은 형태가 다르다

ESP는 IDF UART 드라이버의 수신 버퍼를 두고 `uart_read_bytes`로 최대 64바이트씩 읽는다. 그 뒤 `stm_uart_handle_byte`가 LF까지 모은다. STM에 직접 만든 ISR 링 버퍼를 ESP에 중복 구현한 것은 아니다.

**연습:** `ARM,seq=7`만 도착하고 LF가 오지 않으면 명령을 실행해도 되는가?

**해설:** 아직 한 프레임이 끝났다고 알 수 없다. 현재 조립기는 LF를 기다린다. 길이 초과·수신 오류가 있으면 정상 경계가 올 때까지 폐기한다.

**실행:** [예제 02](examples/02_stream_parser.c)는 실제 STM 링 버퍼와 parser를 링크하고 여러 조각의 문자열을 조립한다. ISR·UART 드라이버를 흉내 낸 실시간 시험은 아니다.

<a id="ch06"></a>
## 6장. 문자열을 명령으로 만드는 parser

### 6.1 “숫자가 있네”만으로 충분하지 않다

`atoi("12junk")`처럼 일부만 숫자로 읽는 접근은 엄격한 명령 형식 검사에 부족하다. `CMD`와 `CMDXYZ`도 같은 명령으로 보면 안 된다. 따라서 타입 이름, 필드 이름과 순서, 숫자, 끝 위치를 모두 확인한다.

현재 STM 명령의 형태는 다음과 같다. 아래 문자열은 protocol 설명이지 보드에 보내라는 지시가 아니다.

~~~text
PING,seq=10
ARM,seq=11
CMD,seq=12,vx_mmps=0,w_mradps=0,timeout_ms=300
DISARM,seq=13
ESTOP_RESET,seq=14
~~~

실제 UART에서는 끝에 LF가 붙는다. STM parser의 인자에는 LF/CRLF를 제거한 본문과 길이를 전달한다.

### 6.2 cursor를 움직여 읽는다

`parser_cursor_t`는 `data, length, position`을 가진다. `consume_literal`은 기대한 글자가 맞으면 position을 진행시키고, 숫자 함수는 숫자의 끝까지 진행시킨다.

~~~text
CMD,seq=12,vx_mmps=0,w_mradps=0,timeout_ms=300
   ↑       ↑         ↑
 타입 끝  seq 끝     다음 필드 시작
~~~

마지막에 `position==length`인지 확인하지 않으면 뒤에 쓰레기나 중복 필드가 붙어도 통과할 수 있다. STM parser는 수신 버퍼 끝을 넘지 않도록 길이를 기준으로 읽는다.

### 6.3 overflow는 계산 전에 검사한다

10진수 숫자 한 자리를 더할 때 새 값은 `value×10+digit`이다. 이 연산이 uint32 범위를 넘지 않게 하려면 다음처럼 미리 검사한다.

~~~c
if (value > (UINT32_MAX - digit) / 10U) {
    return false;
}
value = value * 10U + digit;
~~~

부호 있는 최소값 `-2147483648`은 양수 최대값 `2147483647`의 단순 음수 대칭이 아니다. 현재 두 parser는 부호와 magnitude를 나누어 경계를 처리한다.

### 6.4 문법과 의미를 나누기

STM `uart_frame_parse`가 `vx_mmps=101`을 정수로 읽는 것과 그 속도를 허용하는 것은 다르다. 정상 크기의 정수인지 parser가 읽고, 실제 속도 범위 ±100·각속도 ±500·timeout 50~500 ms는 `handle_cmd`에서 검사한다. parser의 OUT_OF_RANGE 이름 중 일부는 정수 표현 범위 초과를 뜻한다.

ESP `wifi_control_parse`는 WebSocket ARM/CMD의 필드와 속도 범위까지 검사한다. 그러나 범위 안에 있는 `vx_mmps=50`도 `wifi_control_zero_only_allows`를 통과하지 못한다. 그 뒤에도 ticket·연결·현재 상태 검사가 남는다.

~~~text
바이트 유효성 → 문법 → 숫자 표현 범위 → 허용 범위
 → zero-only 정책 → 현재 연결/기한 → 실행 상태
~~~

이 단계를 한 boolean으로 뭉개면 왜 거절됐는지 설명하기 어렵다. 반대로 모듈이 나뉘었다고 모든 잘못된 입력을 서로 다른 UI 메시지로 표시하는 것은 아니다. 실제 main은 일부 parser 실패를 BAD_FORMAT으로 묶는다.

**연습:** `ARM,seq=12,extra=1`, `ARM,seq=4294967296`, `CMD ... vx_mmps=101 ...`의 실패 이유를 구별하라.

**해설:** 첫째는 추가 필드, 둘째는 uint32 overflow, 셋째는 정수 해석 이후 허용 속도 범위 위반이다. 정상 문법이 현재 실행 허가를 뜻하지 않는다는 것이 이 장의 핵심이다.

<a id="ch07"></a>
## 7장. STM의 상태·timeout·E-stop

### 7.1 명령마다 현재 상태를 기억해야 한다

`bool motor_on` 하나만으로 시작할 수 있지만, “아직 ARM하지 않음”, “ARM했지만 명령이 끊김”, “비상정지가 걸림”은 서로 다른 상황이다. 현재 STM은 `DISARMED / ARMED / FAULT`라는 상태와 `BOOT / DISARM / CMD_TIMEOUT / ESTOP_ACTIVE ...`라는 이유를 따로 저장한다.

상태는 “현재 무엇이 가능한가”, 이유는 “왜 여기에 왔는가”를 설명한다.

~~~mermaid
stateDiagram-v2
    [*] --> DISARMED
    DISARMED --> ARMED: 정상 조건에서 ARM
    ARMED --> ARMED: 유효 CMD
    ARMED --> DISARMED: DISARM 또는 CMD_TIMEOUT
    DISARMED --> FAULT: sense active
    ARMED --> FAULT: sense active
    FAULT --> FAULT: sense가 복구되어도 latch 유지
    FAULT --> DISARMED: 정상 sense에서 ESTOP_RESET
~~~

이 그림은 STM 상태의 핵심만 나타낸다. 이후 나오는 ESP의 `IDLE/ACTIVE/BLOCKED`와 서로 다른 상태 머신이다.

### 7.2 ARM은 속도 명령이 아니다

STM의 ARM 처리에는 `motor_output_stop_all`, 속도 0, 기본 timeout 설정, 시간 기준 갱신, `ARMED` 전환이 들어간다. ARM 직후부터 출력이 생기는 것이 아니라 이후 유효 CMD가 들어와야 한다.

현재 STM은 반복 ARM도 시간 기준을 다시 설정한다. 따라서 “ARM은 CMD watchdog에 전혀 영향을 주지 않는다”라고 말하면 틀린다. 반면 PING은 `last_seq`를 바꾸고 PONG을 보내지만 마지막 유효 CMD 시각을 갱신하지 않는다. ESP가 제어 중 진단 PING을 제한하는 이유에도 이 구분이 들어간다.

### 7.3 CMD의 정상 처리 순서

`handle_cmd`를 다음 순서로 읽는다.

1. 속도·각속도·timeout 범위를 검사한다.
2. `ARMED`인지 확인한다.
3. E-stop 입력과 latch를 확인한다.
4. `drive_command_map`으로 좌·우 출력 요청을 계산한다.
5. 출력 적용 전후 E-stop 조건을 다시 확인한다.
6. 출력 적용이 성공했으면 명령값·시각·`last_seq`를 갱신한다.
7. CMD ACK를 보낸다.

실패한 CMD가 watchdog을 연장하면 잘못된 입력만 계속 받아도 출력이 유지될 수 있다. 그래서 “마지막으로 아무 문자열을 받은 시간”과 “마지막으로 정상 CMD를 수락한 시간”은 다른 변수여야 한다.

### 7.4 timeout은 통신 단절의 마지막 대응이다

`command_timeout_enforce`는 ARMED 상태에서 `HAL_GetTick()-s_last_cmd_ms >= s_cmd_timeout_ms`이면 출력을 0으로 만들고 `DISARMED/CMD_TIMEOUT`으로 바꾼다. 현재 Wi-Fi executor가 보내는 CMD의 timeout은 300 ms다.

이후 CMD만 보내면 `NOT_ARMED`로 거부된다. 새 ARM이 필요하다. “통신이 살아났으니 이전 속도를 다시 써 준다”는 로직을 넣지 않은 이유다.

### 7.5 E-stop 입력과 latch는 다르다

`ESTOP_ACTIVE`는 현재 입력이 활성이라는 뜻이다. 입력이 정상으로 돌아와도 `s_estop_latched`는 남을 수 있고, 이때 이유는 `ESTOP_LATCHED`가 된다.

`ESTOP_RESET`은 입력이 여전히 active면 거부된다. 정상 입력에서 latch를 해제해도 결과는 DISARMED이며 자동 ARM이 아니다. 일반 DISARM도 E-stop latch 자체를 해제하지 않는다.

전원·리셋은 RAM 상태를 다시 초기화하지만, 부팅 초기화는 PC7을 다시 검사한다. 물리 입력이 활성인 상태에서 리셋만 반복해도 정상 제어 상태가 되지 않는다. 하드웨어 리셋을 일상적인 E-stop 복구 명령으로 취급하지 않는다.

### 7.6 ACK와 TEL은 왜 둘 다 필요한가

ACK는 특정 명령 `type/seq`에 대한 처리 응답이다. TEL은 그 후의 상태·속도·출력·엔코더·오류 수를 보고한다. 예를 들어 FAULT 중 DISARM ACK는 출력 정지 요청 처리의 증거가 될 수 있지만 FAULT 해제의 증거는 아니다.

`command_age_ms=4294967295`는 이 코드에서 아직 수락한 CMD가 없을 때 쓰는 sentinel이다. 실제로 수십 일 동안 명령이 없었다는 측정값으로 해석하면 안 된다.

**연습:** PING이 100 ms마다 성공하는데 CMD가 끊겼다. ARMED를 유지해야 할까?

**해설:** 아니다. 연결 진단과 제어 명령 갱신은 별개다. STM은 CMD timeout 기준에 따라 DISARMED가 되어야 한다.

<a id="ch08"></a>
## 8장. 명령에서 PWM·DIR까지

### 8.1 duty와 속도는 다르다

PWM은 주기 중 HIGH인 비율로 출력을 조절한다. DIR은 방향 입력이다. duty 10%가 실제 속도 10%라는 뜻은 아니다. 마찰·하중·배터리 전압·모터 특성이 영향을 준다.

현재 `drive_command_mapper`는 정규화한 개방 루프 혼합이다. `vx_mmps`라는 단위가 달려 있어도 현재 출력만으로 실제 50 mm/s를 정확히 만들었다고 주장할 수 없다. 물리 속도 보정과 피드백 제어가 연결되어야 한다.

### 8.2 먼저 두 바퀴의 관계를 생각한다

직진이면 좌·우 같은 방향, 제자리 회전이면 반대 방향이 필요하다. 현재 mapper는 선형 성분과 회전 성분을 각각 1000 기준으로 정규화한 뒤 합친다.

~~~text
linear = vx_mmps × 1000 / 100
yaw    = w_mradps × 1000 / 500
raw_left  = linear - yaw
raw_right = linear + yaw
peak = max(1000, |raw_left|, |raw_right|)
left  = raw_left  × duty_cap / peak
right = raw_right × duty_cap / peak
~~~

이 식은 실제 [drive_command_mapper.c][mapper]에서 읽을 수 있다. 차체 폭을 넣은 차동 구동 역기구학 식 `v_left = v - ωb/2`를 이미 적용한 것은 아니다.

### 8.3 계산해 보기

출력 cap을 100 permille로 두고 PC에서 계산한다.

| vx | w | raw 좌/우 | 최종 좌/우 permille |
| --- | --- | --- | --- |
| 0 | 0 | 0 / 0 | 0 / 0 |
| 50 | 0 | 500 / 500 | 50 / 50 |
| 0 | 250 | -500 / 500 | -50 / 50 |
| 100 | 500 | 0 / 2000 | 0 / 100 |

좌·우를 각각 잘라 버리기보다 같은 peak로 나누어 둘의 비율을 유지한다. 정수 나눗셈의 소수 부분은 버려진다.

### 8.4 permille에서 CCR로

TIM4의 `ARR=4420`이면 주기당 count는 4421이다. `motor_output_permille_to_compare`는 `4421 × duty / 1000`을 계산한다.

~~~text
100 permille → CCR=442
 50 permille → CCR=221
  0 permille → CCR=0
~~~

이 앱의 motor 계층은 최대 100 permille를 검사한다. mapper의 cap과 최종 출력 계층의 한도를 함께 둔 이유는 중간 계층의 실수가 곧바로 높은 duty로 이어지지 않게 하기 위해서다.

### 8.5 방향을 바꿀 때의 순서

현재 `motor_output_set_raw`는 방향이 바뀌면 두 PWM을 먼저 0으로 만들고 1 ms 기다린다. DIR을 변경하고 다시 1 ms 기다린 뒤 새 CCR을 적용한다.

이는 코드가 설정한 전환 순서다. 1 ms가 모든 드라이버·기계 조건에 충분하다는 검증 결과는 아니다. 고전류 상태의 방향 반전이나 실제 정지 거리는 별도 평가 대상이다.

좌측 forward DIR은 LOW, 우측 forward DIR은 HIGH로 정의되어 있다. 소스에는 실제 방향 확인 전제에 관한 주석이 남아 있다. 모터 장착 방향·배선 때문에 논리적 전진과 전기 레벨이 같지 않을 수 있다.

### 8.6 TEL의 PWM은 무엇인가

`motor_output_get_applied`는 소프트웨어가 저장해 둔 duty·방향을 부호 있는 값으로 반환한다. 핀을 측정해 읽는 ADC나 로직 분석기가 아니다.

**연습:** TEL의 좌 PWM이 50이면 50%인가?

**해설:** 아니다. 단위는 permille이므로 5%다. 물리 PWM 파형이나 차체 속도까지 그 값으로 대신할 수 없다.

**실행:** [예제 03](examples/03_output_and_encoder.c)은 실제 mapper를 PC에서 호출한다. motor HAL 코드는 링크하지 않아 실제 출력은 없다.

<a id="ch09"></a>
## 9장. 엔코더 카운터에서 CPS로

### 9.1 엔코더는 속도를 직접 주지 않는다

두 채널 A/B의 변화 순서로 방향을 알 수 있고, 변화를 세어 움직임의 양을 얻는다. STM 타이머의 encoder mode는 이 세기 작업을 주변장치에서 수행한다.

현재 TIM3은 16비트, TIM5는 32비트 범위를 사용한다. `TIM_ENCODERMODE_TI12` 설정과 코드의 x4 count 기준을 함께 읽는다. 엔코더 데이터시트의 PPR 표기와 현재 디코딩 후 count/rev를 같은 값으로 가정하면 안 된다.

### 9.2 wrap을 넘는 차이

16비트 카운터가 `65530 → 5`가 되었다. 평범하게 뺄셈하면 큰 음수처럼 보이지만 실제로 정방향 11 count 진행한 경우일 수 있다.

현재 구현은 우선 16비트 모듈러 차이를 만들고, 절반 범위보다 큰 값은 음수 변화로 해석한다.

~~~text
65530 → 5 : +11
5 → 65530 : -11
~~~

전제는 한 샘플 사이의 변화가 카운터 절반 범위보다 작다는 것이다. 여러 바퀴 wrap을 놓친 자료에서 실제 이동량을 완벽히 복원할 수는 없다. “wrap 대응”은 무제한 복구를 의미하지 않는다.

### 9.3 실제 경과 시간을 나눈다

~~~text
CPS = delta_count × 1000 / elapsed_ms
~~~

샘플 목표가 100 ms라고 항상 10을 곱하지 않는다. 실제 코드 `encoder_speed_update`는 `now_ms-last_sample_ms`를 사용한다. 120 ms가 걸렸는데 100 ms로 가정하면 속도를 과대평가한다.

주기보다 일찍 호출됐을 때 false는 고장이 아니라 “아직 새 샘플을 만들 때가 아님”일 수 있다. 반환값의 의미를 함수 계약에서 읽어야 한다.

### 9.4 count에서 회전수로

현재 STM main의 출력축 기준 보정 상수는 `1560 count/rev`다.

~~~text
RPM = CPS × 60 / 1560
millirpm = CPS × 60000 / 1560
780 CPS → 30 RPM → 30000 millirpm
~~~

현재 `encoder_speed_cps_to_millirpm`은 NULL·0분모·출력 정수 범위를 검사한다. CPS 계산이 맞아도 잘못된 count/rev를 쓰면 RPM은 틀린다.

### 9.5 raw 방향과 차량 방향

현재 main은 TIM3 raw CPS를 음수로 반전해 좌측에 전달하고 TIM5는 그대로 우측에 전달한다. 숫자의 부호를 “타이머가 증가했다”와 “차량 전진이다”라는 두 의미로 나누어 읽는다.

CPS가 튈 때 알고리즘부터 고치면 안 된다. 실제 작업에서는 핀이 바닥에 닿았고 보드를 띄우자 값이 안정됐다는 사용자 관측이 있었다. 이는 접촉 조건과 증상의 상관관계이며 모든 노이즈 원인을 분석했다는 뜻은 아니다.

**연습:** 100 ms 동안 78 count 변화가 있었다. CPS와 RPM은?

**해설:** 780 CPS, 이 프로젝트의 1560 count/rev 기준으로 30 RPM이다. 78 count가 raw TIM3 값이라면 차량 좌측 부호 변환도 따로 적용한다.

<a id="ch10"></a>
## 10장. STM 앱 전체 조립하기

### 10.1 초기화 순서에 이유가 있다

[STM main][stm-main]의 실제 순서를 작은 덩어리로 읽는다.

~~~text
HAL_Init → SystemClock_Config
 → GPIO / USART2 / USART1 / TIM4 / TIM3 / TIM5 초기화
 → motor_output_init(TIM4): 출력 0 후 PWM 시작
 → 엔코더 카운터 초기값 설정, encoder start
 → encoder_speed 상태 초기화와 wrap/RPM 자체 검사
 → uart_mvp_init(USART1), uart_mvp_start_rx
 → 반복 루프
~~~

엔코더 카운터를 중간값에 놓고 시작하는 것과 누적 이동량을 0부터 세는 것은 다른 층이다. 엔코더 모듈의 `previous_raw`가 처음 관측값을 기준으로 잡는다.

### 10.2 각 반복에서 무엇이 일어나는가

`encoder_speed_log_process`가 새 샘플을 만들면 `uart_mvp_set_encoder_cps`로 최신 CPS를 전달하고 USART2에 ENC 진단을 출력한다. 이어지는 `uart_mvp_process`가 명령을 처리하고 USART1로 TEL을 보낸다.

둘 다 100 ms 기준을 쓰더라도 완전히 같은 시각의 측정이라는 뜻은 아니다. 한 TEL은 가장 최근 저장된 CPS를 포함한다.

`motor_output_pin_test_process`는 현재 `MOTOR_OUTPUT_PIN_TEST_ENABLED=0U`라서 반환한다. 파일에 테스트 함수가 있다는 사실과 현재 실행 중이라는 주장을 구분한다.

### 10.3 CMD 한 개의 완전한 경로

~~~text
ESP UART TX
 → STM USART1 RX interrupt
 → ring buffer
 → uart_mvp_process: LF까지 조립
 → uart_frame_parse
 → handle_line / handle_cmd
 → drive_command_map
 → motor_output_set_signed / set_raw
 → ACK 송신
 → 다음 주기 TEL 송신
~~~

소스에서 이 경로의 함수마다 “입력, 실패 조건, 바꾸는 상태, 다음 호출” 네 가지를 적어 보면 함수 이름이 암기 대상이 아니라 데이터 이동 지도가 된다.

### 10.4 Error_Handler와 MCU 예외

main의 `Error_Handler`는 `motor_output_stop_all`을 호출한 뒤 인터럽트를 막고 무한 루프에 들어간다. 이것이 확인하는 것은 해당 함수가 정상적으로 실행 가능한 상황의 처리 순서다.

HardFault나 메모리 손상 같은 모든 고장을 이 함수 하나로 해결한다고 가정하면 안 된다. [stm32f4xx_it.c][stm-it]의 예외 핸들러를 별도로 확인하고, CPU 정지·리셋 중 핀 상태·드라이버 입력·물리 전원 차단을 따로 검증해야 한다. 소프트웨어 상태표만으로 물리 비상정지 설계를 대체하지 않는다.

### 10.5 생성 코드와 사용자 코드

`gpio.c / usart.c / tim.c`는 CubeMX 설정을 반영한다. `USER CODE BEGIN/END`는 재생성 때 사용자 부분을 보존하기 위한 경계다. 현재 PA10 pull-up은 USER CODE 구간에 있다.

링 버퍼·parser·mapper·encoder 계산은 하드웨어 의존성을 줄여 PC에서도 검사하기 쉽게 분리되어 있다. HAL 호출을 모두 한 파일로 합칠 수는 있지만 숫자 계산 하나를 시험할 때 보드가 필요해지는 단점이 생긴다.

**연습:** 엔코더 값이 정상이지만 브라우저에서 ARM이 안 된다. 엔코더 파일부터 수정해야 할까?

**해설:** 아니다. 현재 상태·sense·READY·ticket·권한·기한을 먼저 따라가야 한다. 출력 피드백의 한 부분이 정상이라는 사실만으로 제어 입구가 열리지 않는다.

<a id="ch11"></a>
## 11장. ESP-IDF의 태스크·큐·mutex

### 11.1 한 무한 루프에서 여러 실행 흐름으로

Wi-Fi 연결, HTTP 요청, UART 수신을 한 함수에서 차례로 오래 기다리면 다른 작업이 늦어진다. ESP-IDF는 태스크와 이벤트 기반 API를 제공한다.

현재 앱에서 직접 알아야 할 실행 문맥은 다음과 같다.

| 실행 문맥 | 현재 책임 |
| --- | --- |
| `app_main`의 반복 | 20 ms 목표로 HTTP 작업 예약 시도 |
| `stm_uart_rx_task` | startup·UART RX·제어 송신/응답 진행·진단 요청 처리 |
| HTTP 서버 작업 | 페이지/상태 제공, WS 입력 접수, 상태·결과 전송 |
| Wi-Fi 이벤트 callback | 연결·IP 획득·연결 상실에 따른 서버 관리 |
| 브라우저 이벤트 루프 | ESP 밖에서 버튼·메시지·타이머 처리 |

`stm_uart_rx_task`라는 이름에 RX가 있어도 그 안에서 startup·제어 TX도 진행한다. 이름보다 실제 호출을 확인해야 한다.

### 11.2 태스크 대기는 CPU를 계속 붙잡는 반복과 다르다

~~~c
/* 개념 예제: IDF 안에서 실행되는 태스크 함수 */
static void heartbeat_task(void *arg)
{
    (void)arg;
    for (;;) {
        ESP_LOGI("lesson", "alive");
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
~~~

`vTaskDelay`는 태스크를 일정 tick 동안 대기 상태로 둔다. “정확히 1초 후 실행 보장”이 아니라 이후 스케줄될 수 있게 한다는 의미다. `pdMS_TO_TICKS`는 ms를 OS tick 단위로 바꾸므로 tick 해상도도 영향을 준다.

현재 UART 태스크 생성의 stack 인자 6144는 IDF에서 byte 단위다. 일반 FreeRTOS 자료의 word 단위를 그대로 적용하면 안 된다. [IDF의 태스크 API 설명][idf-rtos]

### 11.3 큐는 자료 전달, mutex는 공유 자료 접근 조정

~~~c
/* 개념 예제 */
xQueueSend(request_queue, &request, 0);
~~~

큐를 만들 때 지정한 항목 크기만큼 값을 복사한다. 마지막 0은 큐가 꽉 찼을 때 기다리지 않겠다는 뜻이다. 반환값을 확인하지 않으면 요청이 사라졌는데 UI에는 접수됐다고 표시할 수 있다.

mutex는 같은 자료를 두 실행 흐름이 동시에 바꾸지 못하도록 한다. 예를 들어 ticket 소비와 요청 저장 사이에 다른 연결이 끼어들면 둘 다 같은 허가를 사용했다고 착각할 수 있다. 따라서 연결 확인·소비·접수를 한 보호 구간에서 처리한다.

### 11.4 현재 앱은 모든 요청을 같은 큐로 보내지 않는다

초기 PING/DISARM 설명만 읽으면 오해하기 쉽다. 현재 main에서 PING은 `s_wifi_command_queue`를 사용한다. ARM/CMD는 mutex 아래 executor의 한 개 요청 보관 슬롯에 들어간다. 수동 DISARM은 stop 경로와 별도 결과 대기 슬롯을 사용한다.

완료 결과는 `s_wifi_command_result_queue`를 통해 HTTP 쪽으로 전달된다. “큐 길이 1”은 현재 앱의 모든 자료구조를 통칭하는 말이 아니다.

### 11.5 잠금을 오래 잡지 않는 이유

공유 상태를 복사하거나 검사하는 동안 잠금을 잡는다. 느릴 수 있는 UART·네트워크 I/O 중에는 가능한 한 풀어 둔다. 대신 잠금을 푼 사이 취소가 들어오는 경우를 설계해야 한다.

`volatile`로 바꾸거나 태스크 우선순위를 높이는 것만으로 이 문제가 없어지지 않는다. 누가 결정하고, 어느 순간 송신이 확정되고, 취소가 어디까지 효력을 가지는지를 17장에서 다룬다.

**연습:** 큐가 요청을 복사해도 왜 mutex가 필요한가?

**해설:** 큐 한 번의 전달은 보호되지만 “현재 owner 검사 → ticket 소비 → executor 상태 변경”이라는 여러 자료구조의 연속 동작까지 자동으로 원자화하지 않는다.

<a id="ch12"></a>
## 12장. Wi-Fi·HTTP·WebSocket·브라우저

### 12.1 네 층을 분리해서 본다

Wi-Fi는 무선 네트워크 연결이다. IP는 네트워크 주소를 제공한다. HTTP는 페이지와 API 요청/응답을 주고받는다. WebSocket은 연결을 유지하며 메시지를 양방향으로 전달한다.

STA 모드에서 ESP는 공유기에 접속한다. AP 모드에서는 ESP가 접속 지점을 제공한다. `WIFI_LINK_USE_AP`는 컴파일 조건이며 현재 사용하는 개인 SSID/password는 별도 비공개 header에 둔다.

현재 `wifi_event`는 STA 시작 때 연결을 요청하고 IP를 얻으면 서버를 시작한다. 연결이 끊기면 서버와 제어 연결을 정리하고 제한된 재접속 시도를 한다. 링크가 돌아온다고 ARM까지 복원하지 않는다.

### 12.2 HTML과 JavaScript는 어디서 실행되는가

`wifi_link_main.c`의 `PAGE[]`는 C 문자열이지만 그 안의 HTML·JavaScript는 브라우저로 전달된 뒤 PC 브라우저에서 실행된다. ESP의 C 함수 `ws_receive`와 브라우저 `sendCommand`는 서로를 직접 함수 호출하지 않는다. 문자열 메시지를 통해 연결된다.

~~~js
// 문법 설명용. 이 줄만으로 로봇 제어 앱이 완성되는 것은 아니다.
const socket = new WebSocket('ws://' + location.host + '/ws');
socket.onmessage = event => {
  const message = JSON.parse(event.data);
  console.log(message);
};
~~~

`const`는 바인딩 재대입을 막고 `let`은 재대입 가능한 변수다. `=>`는 함수 표현식이다. `event.data`는 들어온 메시지 본문이며 `JSON.parse`는 문자열을 객체로 바꾼다. 파싱만 됐다고 필드 타입과 값이 안전한 것은 아니므로 현재 PAGE는 별도의 `validStatus/validControl/validResult`를 사용한다.

### 12.3 send()는 상대방 처리 완료가 아니다

`socket.send`는 데이터를 브라우저의 전송 경로에 넘긴다. 수신·접수·UART 송신·STM 실행을 그 반환으로 알 수 없다. 현재 코드가 notice와 result를 따로 기다리는 이유다. [MDN WebSocket.send][mdn-send]

`setTimeout(fn, 20)`도 20 ms 안에 반드시 함수를 실행한다는 보장은 아니다. 이벤트 루프가 바쁘거나 창 상태가 바뀌면 지연될 수 있다. 그러므로 timer callback 안에서도 현재 시각과 연결을 다시 검사해야 한다.

### 12.4 실제 메시지는 네 종류로 나누어 읽는다

| 메시지 | 전달하는 사실 |
| --- | --- |
| 상태 JSON (`source` 등) | STM TEL 최신 사본과 ESP 상태 |
| `control_state` | 제어 phase·현재 owner·이 연결에 대한 ticket |
| `command_notice` | 이번 요청이 접수되었는지 또는 거부되었는지 |
| `command_result` | 특정 요청의 처리 결과 |

새 WS 연결의 `HELLO`는 연결 등록용이다. UART PING이나 ARM으로 번역되지 않는다. 새로고침만으로 로봇 명령이 나가는 경로를 만들지 않는 중요한 구분이다.

### 12.5 가장 작은 연습에서 실제 앱으로

기존 [ESP 예제들][esp-examples]은 Hello World → FreeRTOS → STA → HTTP → WebSocket 순서다. 각 폴더는 별도 앱이다. 예제 플래시는 현재 Wi-Fi 앱을 대체하므로 이 책을 읽기 위해 매번 보드에 올릴 필요는 없다.

먼저 HTTP handler가 고정 문자열을 돌려주는 코드를 읽는다. 다음 WS 예제에서 두 클라이언트의 메시지 전달을 본다. 이후 실제 앱의 `page_get / status_get / ws_receive / ws_broadcast`로 이동하면 한꺼번에 네트워크 코드를 외우지 않아도 된다.

**연습:** `JSON.parse`가 성공했는데 `boot_id`가 문자열 `"42"`면 현재 검사를 통과할까?

**해설:** 숫자 정수 타입을 요구하는 검사에서는 통과하지 않는다. JSON 문법의 성공과 앱 protocol의 유효성은 별개다.

<a id="ch13"></a>
## 13장. STM 상태가 브라우저에 표시되기까지

### 13.1 원본 TEL에서 snapshot으로

ESP는 한 줄을 조립한 뒤 응답 프레임 처리 경로를 확인하고, TEL이면 `stm_parse_tel`을 호출한다. 필요한 14개 필드, 중복/누락, 정수 범위, 상태 문자열 등을 검사한다.

성공한 TEL은 `stm_telemetry_t`에 저장하고 ESP가 받은 시각 `rx_ms`도 붙인다. HTTP 쪽은 잠금 아래 일관된 사본을 가져와 JSON으로 만든다. 필드 일부는 옛 TEL, 나머지는 새 TEL인 뒤섞인 화면을 피하려는 것이다.

~~~text
UART byte → LF line → TEL parse → 잠금 아래 snapshot 저장
 → status_json → WS TEXT → JSON.parse → validStatus → 화면
~~~

STM이 보낸 `batt_mv=0`은 현재 실측 배터리 전압으로 사용하지 않는다. 브라우저 JSON은 `batt_mv:null, battery_available:false`로 표현한다. “아직 측정 기능 없음”과 “전압 0 V”를 구분한다.

### 13.2 시계는 두 개 이상이다

`stm_t_ms`는 STM의 uptime이고 `uptime_ms`는 ESP의 uptime이다. 브라우저의 `performance.now()`도 별도 기준이다. 서로 다른 시계 숫자를 직접 빼서 지연이라고 주장할 수 없다.

`stm_age_ms`는 ESP의 같은 시계로 `현재 시각 - TEL 수신 시각`을 계산한다. 이것은 ESP가 마지막으로 유효 TEL을 받은 뒤의 시간이다. 엔코더의 정확한 물리 샘플 시각과 일치한다고 단정하지 않는다.

### 13.3 READY·fresh·ACTIVE는 다른 말이다

| 표시 | 의미 | 이것만으로 알 수 없는 것 |
| --- | --- | --- |
| READY | 이번 ESP 부팅의 startup 응답 확인 완료 | 지금 STM이 살아 있는지, 제어 가능한지 |
| STM TEL fresh | 최근 유효 TEL을 받음 | STM이 FAULT인지 아닌지, 해당 요청이 성공했는지 |
| ESP ACTIVE | 제어 handshake와 상태 조건이 충족됨 | 실제 모터 운동 또는 전기적 안전 검증 완료 |

현재 표시용 TEL stale 기준은 500 ms, 제어용 TEL age 제한은 250 ms다. 제어는 더 엄격하다. 화면에 “수신 정상”이라는 문구가 잠깐 남아 있어도 제어 조건은 이미 불충족일 수 있다.

### 13.4 주기가 모두 같지 않다

STM TEL은 100 ms 기준, ESP 상태 JSON은 `WS_PERIOD_MS=100` 기준이다. 반면 `app_main`은 `CONTROL_PUMP_MS=20`으로 HTTP 작업을 예약하고, `control_state`와 결과 처리는 그 작업에서 더 자주 진행될 수 있다.

`s_ws_work_pending`은 이전 작업이 아직 남아 있을 때 같은 작업을 무한히 적재하지 않기 위한 atomic flag다. 느린 클라이언트가 있으면 실제 스케줄은 목표와 달라질 수 있다.

**연습:** READY인데 `stm_age_ms=800`이고 마지막 상태가 ARMED였다. 현재 ARMED라고 확정할 수 있는가?

**해설:** 없다. 마지막 관측이 ARMED였다는 사실만 남는다. 현재 확인 불가와 오래된 데이터를 표시해야 하며, 과거 값을 새 허가로 사용하면 안 된다.

<a id="ch14"></a>
## 14장. PING/DISARM부터 요청과 응답 연결 배우기

### 14.1 첫 왕복은 PING으로 이해한다

~~~text
브라우저: PING,boot_id=42,request_id=1
ESP → STM: PING,seq=100\n
STM → ESP: PONG,seq=100,t_ms=9000\n
ESP → 브라우저: command_result, request_id=1, status=OK
~~~

위 숫자는 이해를 위한 예시다. 브라우저 요청 번호와 UART seq가 일부러 다르다. 브라우저는 한 연결에서의 요청을 구별하고, ESP는 startup·진단·제어를 포함한 UART 요청을 구별해야 한다.

### 14.2 식별자 다섯 종류

| 이름 | 질문 | 수명/역할 |
| --- | --- | --- |
| `boot_id` | 어느 ESP 부팅인가? | ESP가 부팅 때 생성한다 |
| `ws_session_id` | 어느 WS 연결인가? | 서버가 연결에 부여한다 |
| `request_id` | 그 연결의 몇 번째 요청인가? | 브라우저가 증가시키고 서버가 중복/순서를 검사한다 |
| `control_id` | 어느 ARM 제어 세대인가? | owner 예약 때 새로 만든다 |
| `seq` | 어느 UART 명령의 응답인가? | 공통 UART allocator가 부여한다 |

session과 request가 같아도 boot가 바뀌면 과거 실행의 결과일 수 있다. seq만 같아도 응답 타입이 ARM 대신 CMD면 기대한 응답이 아니다.

현재 boot_id는 난수 값이며 수학적으로 절대 중복되지 않는 식별 체계나 인증 수단은 아니다. 이 번호들은 정상 앱의 세대와 대응 관계를 구분하기 위한 장치다.

### 14.3 접수는 결과가 아니다

`ws_receive`는 짧게 형식을 검사하고 접수/거부 notice를 보낸다. UART 응답이 올 때까지 HTTP handler 안에서 기다리지 않는다.

~~~text
브라우저 send
 → ESP ACCEPTED/QUEUED
 → UART 담당 태스크 TX
 → 일치한 응답 RX
 → 완료 결과를 요청 연결에 전달
~~~

어느 단계에서 멈췄는지를 알아야 디버깅이 가능하다. QUEUED만 있으면 실제 송신 전일 수 있고, TX가 있어도 ACK가 없으면 STM 처리 여부를 확정할 수 없다.

### 14.4 DISARM의 완료 기준은 더 강하다

현재 통합 코드의 수동 DISARM은 일반 명령의 rate/busy 검사보다 우선하는 stop 경로를 사용한다. 다만 boot·요청 번호·startup 조건·기존 stop 결과 슬롯 등 기본 검사는 남아 있으므로 “어떤 문자열이든 무조건 정지 명령으로 수락한다”는 뜻은 아니다.

현재 DISARM OK는 일치한 ACK만으로 끝내지 않는다. ACK 이후 새 TEL이 해당 seq, 비무장 상태, 속도/PWM 0을 보여야 한다. FAULT이면서 출력 0인 TEL도 정지 확인이 될 수 있지만 FAULT 해제와는 별개다.

초기 W5 기록의 ACK 기반 설명과 현재 통합 코드의 정지 완료 조건을 같은 버전으로 읽지 않는다.

### 14.5 startup과 사용자 요청

ESP startup은 잠시 안정화를 기다리고 LF로 줄 경계를 정리한 뒤 DISARM/ACK, PING/PONG을 확인한다. 응답 제한과 최대 시도 횟수가 있다. 성공하면 READY, 실패하면 FAILED다.

startup의 제한적 재시도와 사용자의 ARM 자동 재시도 금지는 서로 다른 정책이다. “앱은 어떤 명령도 재시도하지 않는다”로 뭉뚱그리면 틀린다.

**연습:** 새 연결에서 request_id가 다시 1이 되어도 과거 결과와 구분할 수 있는 이유는?

**해설:** 요청 번호 하나만 보지 않고 boot와 session을 함께 비교하기 때문이다. 현재 서버는 결과를 살아 있는 요청 연결에만 전달한다.

<a id="bridge-control"></a>
### 연결 수업. 한 요청에 질문을 하나씩 더하기

여기까지는 “문자열을 받아 STM으로 보내고 응답을 표시한다”를 이해했다. 이제 오래된 명령, 두 창의 경쟁, 응답 지연이 끼어든다. 다섯 파일을 동시에 외우기 전에 **같은 ARM 요청에 확인 질문을 하나씩 추가한다**고 생각해 보자.

**첫 단계 — 문장을 읽을 수 있는가?** `ARM,boot_id=42,request_id=1,ticket=8`에서 숫자와 필드를 읽어 구조체를 만든다. 이것이 contract의 일이다. 형식이 맞아도 지금 실행해도 되는지는 아직 모른다. 6장의 parser와 같은 구분이다.

**둘째 — 이 제출 기회가 아직 유효한가?** 화면을 받은 뒤 한참 지난 요청이라면 새 명령처럼 받아서는 안 된다. ticket은 발급 시각·만료 시각·대상 연결·용도 등을 묶어 확인한다. 접수가 확정되면 한 번 소비한다. 이 책의 비유로는 ‘기한이 적힌 일회용 접수표’다. 신원 인증을 대신하는 표는 아니다.

**셋째 — 누가 이어서 제어하는가?** 접수표는 이미 소비했는데 다음 CMD를 보낼 창은 계속 구별해야 한다. owner는 현재 제어 연결과 `control_id`를 기억하는 ‘담당자 기록’에 가깝다. 같은 창이 다시 ARM하더라도 새 제어 세대를 부여한다. 그래서 옛 CMD가 새 제어에 섞이지 않는다.

**넷째 — 지금 무엇을 확인하는 중인가?** ARM을 보냈어도 ACK가 아직 없을 수 있다. ACK를 받았어도 첫 zero CMD와 새 TEL이 아직 없을 수 있다. state는 이 차이를 `ARM_PENDING`, `ZERO_PENDING`, `ACTIVE` 같은 상태로 기억한다. `PENDING`은 필요한 확인을 기다린다는 뜻이다.

**다섯째 — 판단을 누가 실행으로 옮기는가?** state가 UART에 쓰는 것은 아니다. executor가 접수된 요청을 보관하고, 송신할 프레임을 준비하고, 송신 결과·ACK·TEL을 상태 판단과 연결한다. main의 UART 태스크가 실제 드라이버를 호출한다. executor라는 별도 태스크가 하나 더 생기는 것은 아니다.

| 새로 생긴 문제 | 맡은 모듈 | 그 모듈만 성공해도 아직 모르는 것 |
| --- | --- | --- |
| 문자열이 잘못됐다 | contract | 실행 가능한 상태인가 |
| 오래된 요청이 늦게 도착했다 | ticket | 현재 제어권과 출력 조건이 맞는가 |
| 두 창 또는 옛 제어가 섞인다 | owner | STM의 응답과 상태가 확인됐는가 |
| 접수·응답·확인을 혼동한다 | state | 실제 UART 쓰기가 성공했는가 |
| 판단과 실제 입출력을 연결해야 한다 | executor + main | 물리 출력까지 측정됐는가 |

위 표는 **역할을 배우는 순서**다. 실제 함수가 항상 이 순서로 한 번씩 호출된다는 뜻은 아니다. 접수와 송신 직전에는 조건을 다시 확인하고, 실패하면 중간에서 거부하거나 정지 경로로 간다.

처음에는 정상 경로의 아래 네 질문만 따라간다. 모든 시간 상수와 오류 종류는 다음 읽기에서 붙인다.

~~~mermaid
flowchart LR
    A[ARM 접수] --> B[ARM 송신과 ACK]
    B --> C[zero CMD 송신과 ACK]
    C --> D[새 일치 TEL]
    D --> E[ACTIVE]
~~~

“표를 받았다”, “제어자로 예약됐다”, “STM 응답을 받았다”, “새 상태를 확인했다”는 서로 다른 사건이다. 이 차이를 기억하면 뒤의 상태 이름이 단순한 암기 목록이 되지 않는다.

**잠깐 확인:** ticket을 한 번 쓴 뒤에도 owner가 남아 있어야 하는 이유를 말해 보자. 답이 어렵다면 둘째·셋째 단계를 다시 읽는다. 설명할 수 있으면 15장으로 넘어간다.

<a id="ch15"></a>
## 15장. ticket과 owner가 생기는 과정

**이번 질문:** 한 번 제출할 기회와 계속 제어할 권한은 어떻게 다른가?

**첫 읽기:** 연결 수업을 읽은 뒤 15.1·15.2·15.4부터 읽는다. 번호 소진과 함수별 성공 의미는 15.3·15.5에서 두 번째로 확인한다. [예제 04 안내의 만료 비교](examples/README.md#ticket04)를 함께 본다.

### 15.1 가장 단순한 제어의 빈틈

처음에는 “현재 IDLE이고 ARM 문자열이면 실행”이라고 만들 수 있다. 그런데 브라우저가 본 IDLE 화면은 과거 자료이고, 두 창이 동시에 클릭하거나 오래된 패킷이 늦게 도착할 수 있다.

그래서 두 질문이 필요해진다.

1. 지금 이 요청을 제출할 짧은 기회가 유효한가?
2. 지속 제어 중이라면 이 요청자가 현재 제어자인가?

첫째를 ticket, 둘째를 owner와 control_id가 담당한다.

### 15.2 ticket은 짧은 제출 기회다

현재 [ticket 모듈][ticket]은 boot·session·용도 ARM/CMD·control_id·번호·발급/만료 시각을 묶는다. 유효 시간은 발급부터 150 ms이고 성공적으로 소비하면 `valid=false`가 된다.

~~~text
ESP에서 ticket 8 발급: boot42 / session7 / ARM / control0
 → 브라우저가 받은 제안에 ticket8 포함
 → 브라우저의 수동 ARM 요청에 ticket8 포함
 → ESP에서 동일성 + 만료 + 현재 상태 검사
 → 접수되면 ticket8 소비
~~~

ticket을 가지고 있다는 것만으로 UART 송신이 허용되는 것은 아니다. 정상 sense·새 TEL·IDLE·startup 완료·큐 상태 등의 조건이 더 필요하다. ticket은 로그인 인증이나 암호학적 권한 토큰도 아니다.

### 15.3 번호를 재사용하지 않는 이유

pool은 ESP 부팅 동안 유지되고 연결 종료 때 초기화하지 않는다. 같은 연결에 유효 ticket이 남아 있으면 새로 덮어쓰지 않고 BUSY를 반환한다. 번호가 uint32 범위를 소진하면 실패하며 조용히 1부터 재사용하지 않는다.

학습 실습에서 번호가 “충분히 크니 괜찮다”로 끝내지 말고, 소진 시 어떻게 거부하는지 읽어라. 드문 사건도 정의되어 있어야 테스트할 수 있다.

### 15.4 owner는 ticket보다 오래 산다

[owner 모듈][owner]은 어느 session이 어느 control_id로 제어를 예약했는지 보관한다. ticket은 한 번 제출하면 사라지지만 owner는 ACK 뒤에도 유지된다.

~~~text
ARM: session7이 control3을 예약
CMD1: session7/control3 + 새 ticket
CMD2: session7/control3 + 또 새 ticket
DISARM: owner 해제
다음 ARM: 같은 session7이어도 새 control4
~~~

control3의 오래된 큐 항목이 다음 control4를 제어해서는 안 된다. 연결 번호와 제어 세대를 모두 검사하는 이유다. 다른 연결의 잘못된 요청이 현재 정상 owner를 함부로 취소하지 못하도록 executor도 세대를 대조한다.

### 15.5 parse·consume·reserve는 다른 성공이다

| 성공한 함수 | 그때 확보한 사실 |
| --- | --- |
| `wifi_control_parse` | 요청 문자열이 허용 형식이다 |
| `wifi_control_ticket_consume` | 제출 ticket이 지금 유효하고 일회 소비되었다 |
| `wifi_control_owner_reserve` | 제어 연결과 새 세대 번호가 예약되었다 |
| `wifi_control_state_begin_arm` | 현재 상태 조건 아래 ARM 진행을 시작했다 |
| `wifi_control_executor_take_tx` | 지금 보낼 UART 프레임이 확정되었다 |

각 성공을 한꺼번에 “로봇 동작 성공”으로 번역하지 않는다.

**연습:** ticket 번호는 같지만 session이 다르면 허용해야 할까?

**해설:** 거부해야 한다. 번호 일치만으로 용도·연결·boot·제어 세대가 같아지지 않는다. [예제 04](examples/04_control_flow.c)에서 실제 모듈의 정상 흐름과 만료를 확인한다.

**여기서 멈춰도 되는 기준:** ticket이 소비된 뒤 owner가 남는 이유와, 같은 session의 새 ARM에도 새 control_id가 필요한 이유를 설명한다. 다음 16장에서는 접수가 끝난 뒤 무엇을 기다리는지 본다.

<a id="ch16"></a>
## 16장. ESP 제어 상태 머신을 사건으로 읽기

**이번 질문:** ACK를 받았는데도 왜 ACTIVE가 아닐 수 있는가?

**첫 읽기:** 16.1~16.3과 [예제 04 따라 읽기 1회차](examples/README.md#walkthrough04)에 집중한다. 정상 흐름을 설명한 뒤 16.4~16.6의 기한·STM 시계·함수 구현으로 돌아온다.

### 16.1 왜 STM 말고 ESP에도 상태가 필요한가

STM은 실제 출력 가까이에서 판단한다. ESP는 브라우저 연결·제어권·미송신 요청·응답 대기를 안다. STM은 브라우저가 사라졌는지 모르고, ESP는 실제 핀 출력이 바뀌었는지 직접 측정하지 않는다. 서로 다른 관측과 책임 때문에 각각 상태가 필요하다.

~~~mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> ARM_PENDING: 유효 ARM 접수
    ARM_PENDING --> ZERO_PENDING: 일치한 ARM ACK
    ZERO_PENDING --> ACTIVE: zero CMD ACK와 새 일치 TEL
    ARM_PENDING --> STOPPING: 취소 또는 실패
    ZERO_PENDING --> STOPPING: 취소 또는 실패
    ACTIVE --> STOPPING: 정지 또는 조건 상실
    STOPPING --> IDLE: DISARM ACK와 새 비무장/출력0 TEL
    STOPPING --> BLOCKED: 정지 확인 실패
    BLOCKED --> STOPPING: 새 수동 DISARM
~~~

### 16.2 상태별 의미

| phase | 의미 | 다음에 필요한 것 |
| --- | --- | --- |
| IDLE | 제어권 없음 | 새 수동 ARM과 정상 조건 |
| ARM_PENDING | ARM 진행 중 | 송신 기한과 ACK |
| ZERO_PENDING | ARM ACK 뒤 준비 확인 | 첫 zero CMD와 ACK 이후 새 TEL |
| ACTIVE | zero 제어 조건 확인 | 계속 신선한 CMD와 TEL |
| STOPPING | 허가 폐기·정지 진행 | DISARM 송신/ACK/새 TEL |
| BLOCKED | 정지 완료를 확인하지 못함 | 새 수동 정지 확인 절차 |

BLOCKED는 “물리적으로 계속 움직인다”는 확정도 아니고 “이미 멈췄다”는 확정도 아니다. 확인 실패 때문에 새 제어를 허용하지 않는 상태다.

### 16.3 정상 handshake를 숫자로 따라가기

다음은 PC 예제 04의 합성 시간표다. 실제 보드 측정 로그가 아니다.

| ESP ms | 사건 | phase |
| --- | --- | --- |
| 100 | DISARMED/출력0 TEL, ARM ticket 발급·접수 | ARM_PENDING |
| 110 | ARM seq11 송신 준비 | ARM_PENDING |
| 115 | ARM seq11 ACK | ZERO_PENDING |
| 116 | CMD ticket 발급·zero CMD 접수 | ZERO_PENDING |
| 120 | CMD seq12 송신 준비 | ZERO_PENDING |
| 125 | CMD seq12 ACK | 여전히 ZERO_PENDING |
| 130 | ACK 이후 새 ARMED/zero TEL, last_seq12 | ACTIVE |
| 160 | 수동 stop | STOPPING |
| 162 | DISARM seq13 송신 준비 | STOPPING |
| 165 | DISARM seq13 ACK | 여전히 STOPPING |
| 170 | 새 DISARMED/zero TEL, last_seq13 | IDLE |

ACK만 보고 ACTIVE로 바꾸면 아직 옛 TEL을 화면에 들고 있을 수 있다. 그래서 state는 `confirm_seq / confirm_stm_ms / confirm_tel_generation`을 저장해 새 관측을 요구한다.

### 16.4 시간 검사는 매 사건의 앞에서 한다

현재 state의 `event_time`은 시계 확인과 deadline 검사를 먼저 수행한다. ACK가 왔다는 이유만으로 이미 만료된 대기를 되살리지 않는다.

예를 들어 ARM을 110 ms에 보냈고 ACK 제한이 150 ms라면 260 ms의 ACK는 늦었다. 함수 호출 시점에 timeout 처리가 먼저 실행되므로 그 ACK가 원래 상태를 복원하지 못한다.

### 16.5 STM 시간도 확인한다

TEL이 계속 들어와도 STM의 `t_ms`가 이상하게 되돌아가거나 진행하지 않으면 새로운 정상 관측으로 보기 어렵다. `stm_clock_bad`는 STM 시간 진행과 ESP 수신 간격을 비교하고 250 ms 허용 차이를 둔다.

STM 32비트 uptime의 정상 wrap과 리셋을 구별하려는 구현이며, 전용 STM boot epoch가 있는 protocol은 아니다. 모든 replay를 해결했다고 주장하지 않는다.

### 16.6 state 파일을 읽는 순서

처음부터 전체를 읽기보다 `init → begin_arm → arm_sent → reply → cmd_sent → tel`을 따라 정상 경로를 읽는다. 그 다음 `deadlines → stop_now → disarm_sent → blocked`를 읽는다.

state는 UART를 직접 쓰지 않는다. “입력을 폐기하라”, “DISARM이 필요하다”라는 action을 내놓고 외부 계층이 실행한다. 그래서 실제 시간을 기다리거나 보드를 켜지 않고 사건과 시간을 주입할 수 있다.

**연습:** CMD ACK를 받았지만 TEL의 `last_seq`가 이전 값이다. ACTIVE로 바꿔도 되는가?

**해설:** 첫 zero 확인에서는 안 된다. 해당 CMD 이후의 일치한 상태 보고가 필요하다. 이미 ACTIVE인 주기 제어의 처리와 최초 ACTIVE 진입 조건도 구분한다.

**여기서 멈춰도 되는 기준:** 125 ms와 130 ms에 각각 무엇이 새로 확인됐는지 설명한다. 정지 쪽에서도 165 ms와 170 ms의 차이를 말해 본다. 다음 17장은 이 사건들을 코드 호출로 연결한다.

<a id="ch17"></a>
## 17장. executor가 상태 판단을 UART 실행으로 바꾸기

**이번 질문:** 요청을 접수한 순간과 UART로 보낸 순간 사이에는 어떤 일이 있는가?

**첫 읽기:** 17.1~17.3을 [예제 04 따라 읽기 2회차](examples/README.md#functions04)와 대조한다. 그 뒤 17.4~17.7과 3회차에서 취소·정지·결과 회수를 추가한다. state는 판단하고 main은 실제 드라이버를 호출한다는 구분을 유지한다.

### 17.1 책임을 말로 나누면 파일이 이해된다

| 모듈 | 한 문장 책임 |
| --- | --- |
| contract | 문자열을 정해진 요청 자료로 읽는다 |
| ticket | 이 요청의 짧은 제출 기회를 확인한다 |
| owner | 현재 제어 연결과 세대를 기억한다 |
| state | 사건·시각에 따라 다음 제어 상태를 판단한다 |
| executor | 한 요청을 보관하고 UART 프레임·결과로 연결한다 |
| main | 실제 태스크·mutex·소켓·UART·JSON을 연결한다 |

이 분리는 유일한 정답은 아니다. 하나의 파일에 넣는 설계도 가능하지만 현재는 순수 C 판단을 PC에서 시험할 수 있다는 이점이 있다. 파일 수를 늘리기 위해 새 책임을 만드는 것은 목표가 아니다.

### 17.2 submit은 실제 UART 송신이 아니다

`wifi_control_executor_submit`은 요청을 검사하고, ticket 사본을 검증한 뒤 현재 상태에서 접수가 가능한지 확인한다. 성공했을 때 ticket 소비와 요청 슬롯 예약을 확정한다.

ticket부터 무조건 소비한 다음 “큐가 이미 차 있음”을 발견하면 사용자에게 유효한 기회를 불필요하게 잃게 할 수 있다. 현재 구현은 copy→검사→commit 형태로 이를 다룬다. 전체 동작은 main의 mutex로 직렬화한다.

### 17.3 take_tx와 tx_complete

`take_tx`는 최신 기한과 상태를 다시 확인하고 seq가 들어간 프레임을 만든다. `prepared=true`인 동안 다른 송신을 겹치지 않는다.

~~~text
mutex 획득
 → poll / 입력 폐기 / take_tx
mutex 해제
 → uart_write_bytes
mutex 획득
 → tx_complete(실제 반환 바이트 수)
 → 결과 정리
mutex 해제
~~~

쓰기 요청 길이와 반환값이 다르면 부분 송신이다. `tx_complete`는 이를 실패로 처리하며, 다음 DISARM 앞에 LF가 필요하다는 상태를 남길 수 있다. 반쪽 ARM 문자열 뒤에 DISARM을 바로 이어 붙이는 일을 피하기 위해서다.

### 17.4 취소할 수 있는 마지막 지점

송신 확정 전의 대기 요청은 폐기할 수 있다. `take_tx` 뒤 잠금을 푼 다음 연결 종료가 들어오면 이미 확정/진행 중인 프레임을 소급해서 회수할 수는 없다. 이후 입력을 취소하고 DISARM을 진행한다.

따라서 “연결 종료 즉시 UART 프레임이 단 한 바이트도 나갈 수 없다”는 보장은 현재 구조에 없다. 어떤 프레임이 이미 확정됐는지와 후속 stop을 같이 시험해야 한다.

### 17.5 폐기 전에 DISARM부터 보내면 왜 안 되는가

대기 CMD가 남아 있는데 DISARM만 보내면 다음 반복에서 오래된 CMD가 나갈 수 있다. 현재 stop 경로는 owner를 해제하고 모든 연결의 ticket과 미송신 ingress 자료를 정리한 뒤 `inputs_cleared`를 알린다.

executor는 이 확인 전에는 DISARM 송신을 준비하지 않는다. 정지의 목적은 단지 정지 문자열 하나를 보내는 것이 아니라 과거 허가가 나중에 살아나지 않도록 하는 것이다.

### 17.6 실제 함수로 추적하는 ARM 버튼 한 번

~~~text
브라우저 requestArm / sendCommand
 → WS TEXT
 → ws_receive
 → wifi_control_parse
 → wifi_command_admit_locked
 → wifi_control_executor_submit
 → wifi_control_state_begin_arm
 → UART 태스크 wifi_control_step
 → wifi_control_executor_take_tx
 → uart_write_bytes
 → wifi_control_executor_tx_complete
 → STM ARM 처리 / ACK
 → stm_uart_handle_line
 → wifi_control_handle_response
 → wifi_control_executor_reply
 → 결과 큐 / ws_command_results
 → 브라우저 handleResult
~~~

ARM OK를 받은 브라우저는 현재 intent와 control_id가 맞을 때 zero CMD를 이어간다. 첫 zero CMD 뒤 새 TEL이 확인되어야 제어 phase가 ACTIVE가 된다.

### 17.7 결과를 읽어 가는 것도 흐름의 일부

executor의 `have_result`가 남아 있으면 새 요청을 OUTPUT_PENDING으로 거부할 수 있다. “ACK를 받았는데 다음 요청이 안 들어간다”면 결과를 상위 계층이 꺼내 갔는지도 확인해야 한다.

현재 ARM/CMD result OK는 해당 ACK 대응을 뜻하고, phase 전환은 state/TEL 조건을 따로 따른다. DISARM result OK는 main의 수동 stop 처리에서 IDLE 확인까지 기다린다. 모든 OK가 같은 깊이의 보장은 아니다.

**연습:** 이미 UART write를 시작한 ARM을 취소하려면 왜 브라우저 변수 하나를 false로 바꾸는 것으로 부족한가?

**해설:** 브라우저 변수는 ESP의 확정된 작업이나 선로의 바이트를 없애지 못한다. ESP의 취소·우선 DISARM과 STM의 독립 timeout이 함께 필요하다.

**여기서 멈춰도 되는 기준:** `submit → take_tx → tx_complete`의 차이와, 미송신 입력을 폐기한 뒤 DISARM을 준비하는 이유를 설명한다. 다음 18장에서는 브라우저가 어떤 사용자 의도로 이 요청들을 만드는지 본다.

<a id="ch18"></a>
## 18장. 브라우저의 제어 의도와 시간 예산

**이번 질문:** 연결이 살아 있어도 사용자가 창을 떠나면 왜 정지해야 하는가?

**첫 읽기:** 18.1·18.2·18.6으로 클릭→제어→창 전환→재접속을 먼저 따라간다. [예제 05](examples/05_browser_timing.js)를 읽고 18.3~18.5에서 ticket 수명과 수동 클릭 대기 시간을 구분한다. 시간표는 암기표보다 디버깅할 때 찾는 표로 사용한다.

### 18.1 intent는 연결 상태가 아니다

브라우저가 연결됐다는 사실은 사용자가 지금 제어하기 원한다는 뜻이 아니다. 현재 PAGE는 `intent`를 따로 둔다. 사용자가 ARM을 요청하면 true가 되고, 정지·포커스 상실·연결 종료 때 false가 된다.

zero CMD는 intent, focus, 새 control_state, 현재 owner/control_id, 유효한 CMD ticket, 미처리 요청 없음 등의 조건이 맞을 때만 보낸다. `controlTick`은 20 ms 목표로 조건을 살피고 CMD는 100 ms 목표 간격을 둔다.

### 18.2 포커스를 잃으면 왜 정지하는가

`window.blur`는 창이 입력 포커스를 잃었을 때 발생한다. 탭이 숨겨지는 visibility 상태와 완전히 같은 사건은 아니다. 현재 PAGE는 blur와 hidden 두 경로를 모두 정지 의도에 연결한다. [MDN blur 설명][mdn-blur]

~~~js
// 현재 정책을 설명하는 축약 예제
function onFocusLost() {
  cancelUnsentArmWait();
  const wasControlling = intent;
  intent = false;
  if (wasControlling && transportUsable()) requestDisarm();
}
~~~

VS Code로 창을 바꾸었을 때 IDLE로 돌아간 실제 현상은 이 정책과 일치한다. 통신 고장으로 먼저 단정할 필요가 없다. 돌아온 포커스는 새 수동 ARM이 아니므로 자동 재개하지 않는다.

### 18.3 TTL은 왕복 시간을 없애 주지 않는다

서버가 snapshot을 만들 때 남은 수명을 `ttl_ms`로 보낸다. 메시지가 브라우저에 도착하는 동안에도 서버의 만료 시계는 계속 간다.

~~~text
ESP ticket 발급 ───── snapshot 생성 ── 전송 ── 브라우저 수신 ── 클릭 ── 요청 도착
                     ttl 계산                           ↑
                                         여기서 ttl 전체를 새로 주면 과대평가
~~~

현재 브라우저는 `수신 시각 + max(0, ttl_ms-50)`을 로컬 송신 기한으로 둔다. 같은 ticket이 다시 오면 기존 기한과 새 계산값 중 더 이른 것을 사용한다. 같은 번호를 다시 받았다는 이유로 수명을 연장하지 않는다.

50 ms는 경험에 기반한 여유 설정이며 무선 지연의 상한 보장이 아니다. 최종 수락 여부는 ESP의 150 ms 기한이 결정한다. 브라우저가 괜찮다고 판단해 보냈어도 ESP가 만료로 거부할 수 있다.

### 18.4 버튼 표시와 실제 송신 조건 분리

ticket이 교체되는 짧은 틈마다 버튼을 켰다 껐다 하면 사용자는 눌러야 할 시점을 알기 어렵다. 현재 `armReady`는 최근 제어 제안과 IDLE 조건을 보고 버튼을 표시하고, 실제 보내기 직전 `ticketFor`가 기한을 재검사한다.

클릭 순간 ticket이 너무 오래됐다면 그 **한 번의 클릭**을 최대 200 ms 동안 보관해 다음 유효 제안을 기다린다. 기다리는 동안 버튼을 잠그고, 같은 연결·boot·session·IDLE·focus 조건을 재검사한다. 반복 클릭으로 기한을 늘리지 않는다.

200 ms가 지나거나 blur/hidden/DISARM/연결 변경/상태 상실이 생기면 대기를 취소한다. 이미 보냈다가 거부된 ARM을 자동 재시도하는 기능이 아니다.

### 18.5 숫자가 여러 개인 이유

| 값 | 현재 코드의 의미 | 기준 시점 |
| --- | --- | --- |
| 20 ms | 제어 작업/브라우저 조건 확인의 목표 주기 | 스케줄 반복 |
| 100 ms | CMD 송신 목표 간격, TEL/상태 주기 | 각 계층의 자체 기준 |
| 150 ms | ticket 수명 | ESP 발급 시각 |
| 50 ms | 접수된 ARM/CMD 큐 체류 제한 | ESP accepted_ms |
| 150 ms | 제어 ACK 제한 | 송신 준비 시각 |
| 250 ms | 첫 CMD 필요 기한 | ARM 송신 시각 |
| 200 ms | source timeout | ESP의 마지막 CMD 송신 시각 |
| 250 ms | 제어 TEL age 제한 | ESP TEL 수신 시각 |
| 300 ms | STM CMD timeout | STM의 ARM/유효 CMD 시간 기준 |
| 150 ms | stop 송신 시작 제한 | STOPPING 시작 시각 |
| 300 ms | stop ACK 뒤 TEL 확인 제한 | stop ACK 수신 시각 |
| 500 ms | 표시용 STM stale 기준, 별도의 PING 응답 대기 | 서로 다른 기준 |
| 50 ms | 브라우저 ticket 전송 여유 | snapshot TTL에서 뺌 |
| 200 ms | 한 수동 ARM 클릭의 미송신 대기 | 클릭 시각 |
| 400 ms | 브라우저 ARM/CMD 결과 대기 | 브라우저 send 시각 |
| 4000 ms | 일반 상태 수신 watchdog | 브라우저 상태 수신 |

같은 200 ms라도 다른 변수와 사건을 기준으로 한다. 한 값을 키워 다른 계층의 문제를 덮으면 낡은 입력을 더 오래 허용할 수 있다.

수신 직후만 확인해도 부족하다. 예를 들어 ticket 만료는 1150, 접수는 1120이면 큐 50 ms 제한보다 ticket의 남은 30 ms가 먼저 끝난다. 실제 TX 시각이 1150이면 보낼 수 없다.

### 18.6 재접속은 새 시작이다

`disconnect/resetControl/connect`는 intent·대기 ARM·미처리 요청·control_id·ticket 등 과거 제어 자료를 정리한다. 새 연결은 HELLO로 등록하고 새 상태를 받는다.

브라우저의 정지 메시지가 실제로 전달되지 않을 수도 있다. 그래서 ESP의 owner/시간 감시와 STM의 CMD timeout도 존재한다. UI 하나가 전체 정지를 책임지는 구조로 설명하지 않는다.

**연습:** 클릭 후 200 ms timer가 브라우저 부하 때문에 350 ms에 실행되었다. 250 ms에 온 새 ticket으로 ARM을 보내도 되는가?

**해설:** 안 된다. callback 실행이 늦었다고 사용자 의도의 기한이 연장되지 않는다. `performance.now() >= wait.until`을 재검사해야 한다.

**실행:** [예제 05](examples/05_browser_timing.js)는 기한과 취소의 작은 모델이다. 실제 PAGE 전체의 검사는 기존 [브라우저 검사][page-tests]가 담당한다.

**여기서 멈춰도 되는 기준:** 포커스 복귀가 새 수동 ARM을 대신하지 않는 이유와, ticket 150 ms와 수동 클릭 대기 200 ms의 시작 사건이 다른 이유를 설명한다. 다음 19장에서 지금 배운 구분을 실제 로그에 적용한다.

<a id="ch19"></a>
## 19장. 실제 문제를 코드와 연결해 디버깅하기

### 19.1 먼저 네 줄을 구분한다

~~~text
WS QUEUED       : ESP 접수
CONTROL TX      : UART 쓰기 호출과 반환값
CONTROL RX MATCH: 기대한 type/seq 응답 대응
STM TEL         : 그 뒤 보고된 상태·출력·오류
~~~

TX의 `written=22/22`는 요청한 길이와 드라이버 반환값이 같다는 뜻이다. 그것만으로 선로 파형과 STM의 실행이 증명되지는 않는다. 반대로 응답 로그가 없다는 사실만으로 STM에서 전혀 실행되지 않았다고 단정할 수도 없다.

### 19.2 사례 A — 같은 ticket인데 왜 거절됐는가

실제 사용자 로그 발췌:

~~~text
TICKET DEBUG: cmd=ARM request=1 got=1614 expected=1614
valid=1/0 check_ms=134901..134902
issued_ms=134741 expires_ms=134891
boot=3832666542/3832666542 session=3/3 control=0/0 purpose=0/0
~~~

해석 순서는 다음과 같다.

1. got/expected·boot·session·control·purpose는 서로 맞았다.
2. 검사 시각은 만료 시각보다 10~11 ms 늦었다.
3. 발급부터 검사까지 약 160 ms가 지났지만, 이 전체를 무선 지연이라고 부를 수 없다. snapshot 대기·사용자 클릭 대기도 포함할 수 있다.
4. 따라서 동일성 불일치보다 만료 경계가 직접적인 거부 원인으로 확인됐다.

현재 수정은 서버 수명을 늘리는 대신 브라우저에 전송 여유를 두고 같은 ticket의 기한을 연장하지 않도록 한 것이다. 이어서 표시용 버튼 조건을 실제 송신 기한과 분리해 깜빡임을 줄였다.

### 19.3 사례 B — ARM 후 로그가 많아졌다가 IDLE이 됨

실제 후속 로그에는 ARM request33, CMD request34~46, DISARM request47이 있었다. 사용자는 VS Code로 전환했을 때 IDLE이 된다고 확인했다.

따라서 “13개 CMD를 보냈으니 오류”가 아니라 정상적인 zero CMD 반복을 먼저 읽고, 마지막 DISARM이 어느 사건에서 나왔는지 조사한다. PAGE의 blur handler와 사용자 행동이 연결되면 의도된 정지로 설명된다.

로그만 보아서는 수동 DISARM과 자동 blur DISARM의 원인을 항상 구별할 수 없다. 실제로 이전 request42는 사용자가 DISARM 버튼을 눌렀다고 별도로 확인했다. 번호가 비슷해도 서로 다른 시험의 원인을 합치지 않는다.

### 19.4 사례 C — RESET 뒤 TEL 시각이 작아짐

STM uptime이 큰 값에서 200 ms로 바뀌면 STM 재부팅과 일치하는 관측이다. ESP의 boot_id는 별개라 그대로일 수 있다. UART 줄이 중간에 끊겨 invalid line이 나올 수도 있다.

이 관측 하나로 특정 전원 고장을 확정하지 않는다. 리셋 버튼 조작, 실제 전원 조건, UART 파형, 이후 부팅 로그를 함께 본다.

### 19.5 가설을 검증 가능한 질문으로 바꾸기

“통신이 이상하다” 대신 다음처럼 적는다.

| 가설 | 확인할 값 | 반박되는 경우 |
| --- | --- | --- |
| ticket 번호가 틀림 | got/expected, boot/session/purpose | 모두 일치 |
| 접수 뒤 너무 오래 대기 | accepted/expires/TX 시각 | 모든 기한 안에 송신 |
| 응답이 다른 요청에 붙음 | pending type/seq와 수신 type/seq | 정확히 대응 |
| UI만 옛 상태 | TEL count, ESP 수신 age, WS 메시지 | 값이 계속 갱신 |
| 창 전환이 자동 정지 유발 | 사용자 동작, blur 경로, DISARM 로그 | focus 유지 중 같은 현상 |

한 번에 많은 수치를 바꾸면 어느 수정이 원인을 해결했는지 모른다. 원인 범위를 줄인 뒤 가장 작은 수정과 경계 검사를 적용한다.

### 19.6 증거의 층

| 검사 | 얻는 증거 | 얻지 못하는 증거 |
| --- | --- | --- |
| 소스 검토 | 설계 의도·분기·책임 관계 | 실제 실행 성공 |
| 순수 C PC 실행 | 주어진 입력·시간에서 계산/상태 결과 | HAL·UART·RTOS 실제 동작 |
| 실제 PAGE 모의 실행 | JS 이벤트/대기/취소 조건 | 실제 무선 지연·브라우저 스케줄 상한 |
| 보드 빌드 | target 컴파일·링크 가능 | 올바른 플래시·런타임 동작 |
| 보드 ACK/TEL 로그 | 명령 왕복과 보고 상태 | 핀 출력·전력단·기계 정지 전체 |
| 파형 측정 | 측정 지점의 실제 신호/시간 | 다른 지점·다른 부하 조건 |
| 실제 기계 시험 | 해당 조건의 동작 | 모든 장애 조건의 보장 |

현재 기존 host tests를 무조건 전부 돌리는 것이 학습 목표는 아니다. parser를 바꿨으면 parser·그 계약을 쓰는 관련 경로를, PAGE를 바꿨으면 PAGE의 상태/취소 조건을 검사한다. 변경 없는 과거 통과 시험을 학습 진도 때문에 반복할 필요도 없다.

### 19.7 기존 검사를 읽는 법

[검사 폴더][tests]에는 Python driver, C fixture, Node PAGE 검사가 있다. Python은 C 소스를 선택·컴파일·실행하는 역할도 하므로 “Python으로 작성됐으니 C를 검사하지 않는다”라고 생각하면 안 된다.

state fixture에서 실제 시간을 기다리지 않고 `now_ms=149 / 150`을 넣는 이유는 경계를 빠르고 재현 가능하게 검사하기 위해서다. 실제 RTOS 동시성을 증명하려면 별도 실행 조건이 필요하다.

**연습:** “ticket 거부가 나왔으므로 FAULT 차단 시험도 통과”라는 판정이 잘못된 이유는?

**해설:** ticket 검사에서 먼저 거부됐다면 그 뒤 FAULT 조건을 실제로 평가해 거부했는지 증명되지 않는다. FAULT 차단을 확인하려면 다른 선행 조건은 유효하게 만들어 해당 분기가 결과를 결정하게 해야 한다.

<a id="ch20"></a>
## 20장. 작은 프로그램부터 현재 구조까지 재구성하기

이 장의 과제는 보드 플래시 없이 PC에서 진행한다. 실차 main을 지우고 처음부터 다시 쓰라는 뜻이 아니다. 기존 예제 옆의 개인 연습 파일에서 핵심을 만들어 보고 원본과 비교한다.

### 20.1 버전 0 — 값 하나 저장하기

**요구사항:** `seq`와 속도 두 개를 구조체로 만들고, 함수를 통해 속도 0 요청을 만든다.

**직접 할 일:** 헤더 없이 한 파일에 작성한다. NULL 출력 포인터를 거부한다. 구조체 복사 뒤 원본을 바꿔 사본이 유지되는지 확인한다.

**완료 기준:** `&`, `*`, `->`를 각각 설명하고 코드를 보지 않고 다시 작성할 수 있다. 예제 01을 확인한다.

**다음 요구가 생기는 이유:** 외부에서 들어오는 것은 구조체가 아니라 바이트다.

### 20.2 버전 1 — PING 한 줄 읽기

**요구사항:** `PING,seq=7`만 정확히 인식하고 PINGX, 빈 숫자, overflow, 남는 문자를 거부한다.

**직접 할 일:** 처음에는 수신 없이 고정 문자열로 시작한다. 이후 문자열을 세 조각으로 나눠 주고 LF 전에는 실행하지 않는다. 성공한 parser 결과와 입력 문자열을 따로 보관한다.

**완료 기준:** 예제 02의 개행/분할 입력을 설명하고, `4294967296`을 uint32로 계산하기 전에 거부할 수 있다.

**다음 요구:** 명령이 문법상 맞아도 항상 실행하면 안 된다.

### 20.3 버전 2 — STM의 작은 상태 머신

**요구사항:** DISARMED에서 CMD 거부, ARM 뒤 CMD 수락, 300 ms 중단 뒤 DISARMED, sense active면 latch.

**직접 할 일:** HAL 대신 `now_ms`와 `sense_active`를 함수 인자로 준다. `step(command, now, sense)`가 상태와 출력 요청을 바꾸도록 만든다. 출력 요청은 숫자일 뿐 핀에 연결하지 않는다.

**필수 예상표:**

| 입력 순서 | 기대 |
| --- | --- |
| 부팅 → CMD0 | NOT_ARMED |
| 부팅 → ARM → CMD0 | ARMED, 출력0 |
| 마지막 갱신 1000 → poll1300 | DISARMED/CMD_TIMEOUT |
| active sense → normal sense | FAULT/latch 유지 |
| normal sense → reset latch | DISARMED, 자동 ARM 없음 |

**완료 기준:** PING 처리에 watchdog 갱신을 추가하면 어떤 문제가 생기는지 말할 수 있다. 실제 [프로토콜 코드][stm-protocol]와 다른 부분을 직접 표시한다.

### 20.4 버전 3 — 출력 계산과 관측 추가

**요구사항:** 두 명령값을 좌우 permille로 바꾸고, count 차이를 CPS로 바꾼다.

**직접 할 일:** 먼저 직진만 계산한다. 다음 회전을 더하고, cap을 넘는 혼합 입력에서 좌우 비율을 유지하도록 바꾼다. 엔코더는 정상 차이, forward wrap, reverse wrap을 순서대로 처리한다.

**완료 기준:** `vx100/w500 → 0/100`, `65530→5 → +11`을 손으로 계산한 뒤 실제 예제 03과 비교한다.

**다음 요구:** 사용자 입력과 관측을 PC 브라우저까지 전달해야 한다.

### 20.5 버전 4 — 화면과 요청 결과 분리

**요구사항:** 상태 화면의 최신성, 요청 접수, 요청 결과를 다른 값으로 둔다.

**직접 할 일:** 네트워크 없이 JavaScript 객체를 입력으로 쓰는 작은 handler부터 만든다. request1이 완료되기 전에 request2를 접수했을 때, 옛 request1 결과가 새 결과를 덮지 않도록 한다.

**완료 기준:** boot·session·request를 바꾼 입력의 결과가 적용되지 않는 이유를 설명한다. 이후 실제 PAGE와 서버의 message 종류를 연결한다.

**다음 요구:** 응답 번호만으로는 지속 제어의 소유권과 낡은 요청을 막을 수 없다.

### 20.6 버전 5 — ticket·owner·기한 추가

**요구사항:** 150 ms짜리 일회 ticket과 제어 세대를 둔다. 다른 session, 같은 ticket 재사용, 만료 시각의 요청을 거부한다.

**직접 할 일:** 처음에는 UART와 JSON을 빼고 구조체만으로 만든다. ticket이 유효하지만 owner가 이미 있을 때 어떻게 실패할지 결정한다. 실패 시 어느 값이 바뀌어야 하는지 먼저 표로 쓴다.

**완료 기준:** 소비한 ticket과 계속 유지하는 owner가 왜 별개인지 설명한다. 실제 ticket/owner 소스와 비교한다.

**다음 요구:** ARM ACK와 상태 확인 사이, 취소와 송신 사이를 관리해야 한다.

### 20.7 버전 6 — zero handshake와 취소

**요구사항:** ARM ACK → zero CMD ACK → 새 ARMED/zero TEL에서 ACTIVE, DISARM ACK → 새 stopped TEL에서 IDLE.

**직접 할 일:** 예제 04의 정상 시간표를 먼저 종이에 그린다. 이후 첫 zero TEL을 빼고 결과가 어떻게 바뀌는지 예상한다. stop ACK를 늦추고 BLOCKED를 관측한다.

**완료 기준:** 임계값 바로 전·정확한 임계값·직후의 테스트를 직접 만들 수 있고, 미송신 요청 폐기와 이미 보낸 프레임 회수 불가를 설명한다.

### 20.8 버전 7 — 실제 앱과 대응시키기

이제 새로 구현한 작은 함수 옆에 현재 앱의 함수명을 적는다.

| 내가 만든 작은 기능 | 실제 대응 |
| --- | --- |
| 바이트 보관 | `ring_buffer_push/pop` |
| 문자열 해석 | `uart_frame_parse / wifi_control_parse` |
| 마지막 명령 timeout | `command_timeout_enforce` |
| 두 바퀴 계산 | `drive_command_map` |
| 최신 관측 저장 | `stm_uart_handle_line / status_json` |
| 제출 기한 | `wifi_control_ticket_issue/consume` |
| 제어자 기억 | `wifi_control_owner_*` |
| 사건 처리 | `wifi_control_state_*` |
| 송신 준비·결과 | `wifi_control_executor_*` |
| 하드웨어·네트워크 연결 | `wifi_link_main.c` |
| 사용자 의도 취소 | PAGE의 `stopLocal/resetControl` |

한 번에 현재 2천 줄 main을 다시 작성할 필요는 없다. 이 표의 한 줄씩 작은 입력과 출력으로 재현하는 것이 실력 확인에 더 유용하다.

### 20.9 심화 방향은 현재 구현 이후로 표시한다

- **STM RTOS 전환:** 순환 루프를 태스크로 나누기 전에 안전 판단의 주기와 데이터 소유권을 정한다. 단지 태스크 수를 늘리지 않는다.
- **속도 제어:** 엔코더 속도 목표·측정 오차·출력 제한·적분 포화와 실제 주기를 정의한 뒤 PID를 붙인다.
- **CAN/ROS 2:** 전송 방식이 바뀌어도 “새 명령인지, 누가 보냈는지, 언제 만료되는지, 끊기면 무엇을 하는지”를 다시 연결한다.
- **STM freshness protocol:** 현재 seq는 응답 대응이지 STM의 엄격한 anti-replay 정책이 아니다. epoch/순서 검사는 별도 protocol 변경이다.
- **인증·보안:** 지금의 ticket/boot/session은 인터넷 공개용 인증·접근 제어를 대신하지 않는다. 네트워크 신뢰 모델은 별도 설계다.

이것들은 새로 구현됐다는 주장이 아니라 현재 코드에서 이어지는 학습 방향이다.

### 20.10 설명 능력 확인

다음 질문에 답할 수 있으면 단순 복사를 넘어 코드를 이해하기 시작한 것이다.

1. UART ISR에서 parser를 바로 실행하지 않는 이유는?
2. parser 성공과 ARM 허가는 무엇이 다른가?
3. ticket은 소비되는데 owner는 왜 유지되는가?
4. ARM/CMD OK인데 왜 아직 ZERO_PENDING일 수 있는가?
5. 마지막 TEL이 ARMED인데 연결이 끊기면 화면은 어떻게 표현해야 하는가?
6. CTRL TX 로그가 있어도 실제 출력 파형이 필요할 때는 언제인가?
7. 왜 timeout을 크게 늘리는 것으로 ticket 만료를 해결하지 않았는가?
8. 이 코드의 PWM은 왜 실제 속도 제어가 아닌가?

**짧은 해설:** 1은 ISR 작업량과 수신 분리, 2는 문법/상태/기한의 차이, 3은 한 요청의 기회와 지속 제어권의 차이, 4는 ACK 이후 새 TEL 조건, 5는 마지막 관측/현재 확인 불가 구분, 6은 핀·정지 시간·전력단 판단, 7은 낡은 허가를 연장하는 부작용, 8은 엔코더 오차 피드백이 출력 계산에 연결되지 않았기 때문이다.

<a id="appendix"></a>
## 부록 A. 실제 소스 찾아보기

행 번호는 편집으로 바뀌므로 파일과 함수명을 기준으로 찾는다. VS Code의 정의로 이동 또는 `rg -n "함수명" 파일경로`를 이용한다.

### A.1 STM

| 파일 | 읽을 위치 | 관련 장 |
| --- | --- | --- |
| [main.c][stm-main] | `main, SystemClock_Config, encoder_speed_log_process, Error_Handler` | 1, 3, 9, 10 |
| [main.h](../../03_Firmware/stm32_uart_mvp/Core/Inc/main.h) | 핀 이름 | 3 |
| [gpio.c](../../03_Firmware/stm32_uart_mvp/Core/Src/gpio.c) | PC7 pull-up·DIR 초기 레벨 | 3, 7 |
| [usart.c](../../03_Firmware/stm32_uart_mvp/Core/Src/usart.c) | USART1/2 초기화·PA10 USER CODE | 3, 5 |
| [tim.c](../../03_Firmware/stm32_uart_mvp/Core/Src/tim.c) | TIM3/4/5·PSC·ARR·encoder mode | 3, 8, 9 |
| [stm32f4xx_it.c][stm-it] | IRQ와 예외 진입 | 5, 10 |
| [ring_buffer.h](../../03_Firmware/stm32_uart_mvp/Core/Inc/ring_buffer.h) / [.c][ring] | 단일 생산자/소비자 버퍼 | 2, 5 |
| [uart_frame_parser.h](../../03_Firmware/stm32_uart_mvp/Core/Inc/uart_frame_parser.h) / [.c][stm-parser] | 구조체·cursor·정수 읽기 | 6 |
| [uart_mvp_protocol.h](../../03_Firmware/stm32_uart_mvp/Core/Inc/uart_mvp_protocol.h) / [.c][stm-protocol] | 상태·CMD·latch·timeout·TEL | 7, 10 |
| [drive_command_mapper.h](../../03_Firmware/stm32_uart_mvp/Core/Inc/drive_command_mapper.h) / [.c][mapper] | 정규화 혼합 | 8 |
| [motor_output.h](../../03_Firmware/stm32_uart_mvp/Core/Inc/motor_output.h) / [.c][motor] | PWM/DIR·stop·applied snapshot | 8 |
| [encoder_speed.h](../../03_Firmware/stm32_uart_mvp/Core/Inc/encoder_speed.h) / [.c][encoder] | delta·CPS·millirpm | 9 |
| [.ioc](../../03_Firmware/stm32_uart_mvp/stm32_uart_mvp.ioc) | CubeMX 설정 자료 | 3, 10 |
| [startup ASM](../../03_Firmware/stm32_uart_mvp/Core/Startup/startup_stm32f446retx.s) | reset/vector 진입 | 1 |
| [linker script](../../03_Firmware/stm32_uart_mvp/STM32F446RETX_FLASH.ld) | 실행 이미지의 메모리 배치 | 1 |

`system_stm32f4xx.c`, `stm32f4xx_hal_msp.c`, `syscalls.c`, `sysmem.c`는 시스템/런타임 지원이다. 처음에는 startup→main과 주변장치 연결 관점에서 읽고, 드라이버 내부·heap 확장은 별도 심화로 읽는다.

### A.2 ESP

| 파일 | 읽을 위치 | 관련 장 |
| --- | --- | --- |
| [wifi_link_main.c][esp-main] | `app_main, wifi_event, stm_uart_rx_task` | 11, 12 |
| 같은 main의 수신·표시 | `stm_uart_handle_byte/line, stm_parse_tel, status_json` | 5, 13 |
| 같은 main의 WS 처리 | `ws_receive, wifi_command_admit_locked, wifi_control_snapshot` | 14, 15, 17 |
| 같은 main의 UART 처리 | `wifi_control_step, wifi_control_handle_response, wifi_uart_allocate_seq` | 14, 17 |
| 같은 main의 PAGE 문자열 | `requestArm, handleControl, handleResult, stopLocal, controlTick` | 12, 18 |
| [contract.h](../../03_Firmware/esp32_wifi_link/main/wifi_control_contract.h) / [.c][contract] | WebSocket ARM/CMD parser | 6 |
| [ticket.h](../../03_Firmware/esp32_wifi_link/main/wifi_control_ticket.h) / [.c][ticket] | 일회 ticket | 15 |
| [owner.h](../../03_Firmware/esp32_wifi_link/main/wifi_control_owner.h) / [.c][owner] | 연결·제어 세대 | 15 |
| [state.h](../../03_Firmware/esp32_wifi_link/main/wifi_control_state.h) / [.c][state] | 시간 상수·상태 전이·ACK/TEL 확인 | 16 |
| [executor.h](../../03_Firmware/esp32_wifi_link/main/wifi_control_executor.h) / [.c][executor] | 요청 슬롯·TX·결과 | 17 |
| [main/CMakeLists.txt][esp-cmake] | 실제 소스 등록 | 1 |
| [sdkconfig.defaults](../../03_Firmware/esp32_wifi_link/sdkconfig.defaults) | WS 기능 등 설정 | 1, 12 |
| [설정 예시 header](../../03_Firmware/esp32_wifi_link/main/wifi_link_config.h.example) | AP/STA·개인 설정의 형식 | 12 |
| [기존 UART bridge](../../03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c) | Wi-Fi 이전 UART 중계·startup·시험 script | 14 |
| [ESP 단계별 예제][esp-examples] | Hello World부터 WebSocket까지의 별도 앱 | 11, 12 |

UART bridge와 Wi-Fi link는 별도 앱이다. bridge의 시험 hook 상태를 Wi-Fi 앱의 동작으로 해석하지 않는다. 이 책은 이전 bridge의 모든 시험 시나리오를 새로운 실행 절차로 재배포하지 않는다.

## 부록 B. 용어를 자기 말로 바꾸기

| 용어 | 이 책에서 쓰는 뜻 |
| --- | --- |
| firmware | 보드에서 실행하는 소프트웨어 |
| peripheral | UART·timer·GPIO 같은 MCU 하드웨어 기능 |
| HAL | 주변장치 접근을 돕는 드라이버 계층 |
| handle | 어떤 주변장치를 어떤 설정/상태로 다루는지 묶은 객체 |
| ISR | 하드웨어 인터럽트에 응답하는 실행 문맥 |
| callback | 사건이 발생했을 때 다른 코드가 호출해 주는 함수 |
| task | 스케줄러가 실행을 관리하는 함수 흐름 |
| mutex | 공유 자료를 한 번에 하나의 실행 흐름이 다루게 하는 잠금 |
| queue | 나중에 처리할 자료를 넘기는 통로 |
| ring buffer | 배열의 끝에서 처음으로 돌아오는 FIFO |
| parser | 바이트/문자열을 약속된 구조로 해석하는 코드 |
| frame | 한 번의 명령/응답 단위 |
| ACK / ERR | 특정 요청의 수락 처리/오류 응답 |
| TEL | 상태·명령·출력·관측을 보고하는 telemetry |
| snapshot | 여러 필드를 같은 관측 묶음으로 복사한 자료 |
| stale | 허용한 시간보다 오래된 관측 |
| timeout | 필요한 사건이 기한 내에 오지 않음 |
| deadline | 어느 시각부터 더 이상 허용하지 않는다는 경계 |
| latch | 입력이 정상화되어도 별도 해제까지 기억하는 상태 |
| owner | 현재 제어를 맡은 연결과 세대 |
| ticket | 한 요청을 제한된 시간 안에 제출할 일회 식별 자료 |
| FSM | 상태와 사건으로 다음 행동을 정하는 유한 상태 머신 |
| executor | 판단을 송신/결과 처리 단계로 연결하는 계층 |
| invariant | 어떤 순서의 사건에서도 지켜야 하는 조건 |
| race | 실행 순서가 달라져 결과가 바뀔 수 있는 경쟁 상황 |
| commit | 되돌릴 수 있는 준비를 넘어 실행하기로 확정하는 지점 |
| watchdog | 갱신/진행이 끊겼는지 감시하는 장치 또는 로직 |
| PWM / DIR | 출력 비율 신호 / 방향 신호 |
| CPS / RPM | 초당 count / 분당 회전수 |
| open loop | 관측 오차로 출력을 보정하지 않는 제어 |
| mock | 하드웨어/시간 등의 의존성을 시험용으로 대신한 대상 |
| assert | 예상 조건이 틀리면 즉시 실행 실패로 알리는 검사 |

## 부록 C. 공식 계약·일반 학습·공식 참고 자료

### 프로젝트 안의 기준

- [UART 계약](../../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md): UART 필드와 책임.
- [개방 루프 mapper 계약](../../01_System_Architecture/27_Production_Open_Loop_Command_Mapper_ko.md): 정규화와 출력 제한.
- [Wi-Fi ARM/CMD 계약](../../docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md): 제어 식별·기한·AC-H/B/S 검증 항목.
- [main 통합 코드 안내](../../docs/plans/2026-10-13_WiFi_ARM_CMD_Main_Integration_Code_Guide_ko.md): 당시 입력 블록과 후속 수정. 책은 원본 안내 첫 블록 대신 실제 최신 저장 소스를 분석했다.
- [PC 검사 안내][tests]: 검사 종류와 각 증거의 범위.
- [본문 예제 검증 기록](validation.md): 이 책에 새로 붙인 PC 예제 결과.

### 프로젝트 밖의 기존 학습 경로

- [STM32 기본 학습](../../../../Embedded/STM32/README.md): GPIO·EXTI·PWM 등 낱개 개념.
- [ESP32-S3 기본 학습](../../../../Embedded/ESP32-S3/README.md): 보드 설치와 단독 실습. 오래된 환경 기록을 현재 프로젝트의 IDF 버전으로 착각하지 않는다.
- [STM32 RTOS 학습 지도](../../../../Embedded/STM32/RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md): 이후 STM RTOS 심화.
- [STM32 CAN 학습 지도](../../../../Embedded/STM32/CAN/00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md): 이후 CAN 심화.

### 공식 참고 자료

다음 링크는 일반 API/하드웨어 의미를 확인할 때 사용했다. 프로젝트 동작에 대한 설명은 위의 실제 소스를 우선한다. 외부 문서 전체를 번역한 자료는 아니다.

- [ST STM32F446 문서 목록][st-docs]: RM0390의 RCC/GPIO/USART/TIM 장으로 이동하는 공식 시작점.
- [ESP-IDF v6.0.2 FreeRTOS][idf-rtos]: IDF 태스크·stack 단위·main 태스크·동기화 의미.
- [MDN WebSocket.send][mdn-send]: 브라우저 전송 요청의 의미.
- [MDN Window.blur][mdn-blur]: 포커스 상실 사건.

## 부록 D. 이 판의 기준과 유지 방법

이 책은 2026-10-13 저장본을 읽은 학습용 첫 판이다. 당시 문서 일부에는 “main 미연결” 같은 과거 설명이 남아 있었지만 실제 저장 main은 executor와 브라우저 ARM/CMD를 호출한다. 이 책은 현재 소스 동작과 과거 검증 이력을 구분한다.

사용자 관측으로 정상 ARM/zero 제어, 수동 DISARM, 포커스 상실 정지와 복귀 후 자동 재개 없음, 버튼 깜빡임 해소가 보고되었다. ACTIVE 중 WS close, 여러 장애·전기적 검증 전체를 통과했다고 기록하지 않는다. 물리 장치의 현재 전원 상태를 이 학습서로 판단하지 않는다.

소스가 바뀌면 [source_manifest.json](source_manifest.json)과 비교하고 영향 받은 장·예제·상수 표를 갱신한다. 특히 timeout, ACK/TEL 완료 조건, 출력 cap, 핀 배치, zero-only 정책이 바뀌면 설명을 먼저 재검토한다. 해시는 파일 일치 확인용이지 시험 통과의 증명서가 아니다.

[stm-main]: ../../03_Firmware/stm32_uart_mvp/Core/Src/main.c
[stm-protocol]: ../../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c
[stm-parser]: ../../03_Firmware/stm32_uart_mvp/Core/Src/uart_frame_parser.c
[stm-it]: ../../03_Firmware/stm32_uart_mvp/Core/Src/stm32f4xx_it.c
[ring]: ../../03_Firmware/stm32_uart_mvp/Core/Src/ring_buffer.c
[mapper]: ../../03_Firmware/stm32_uart_mvp/Core/Src/drive_command_mapper.c
[motor]: ../../03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c
[encoder]: ../../03_Firmware/stm32_uart_mvp/Core/Src/encoder_speed.c
[esp-main]: ../../03_Firmware/esp32_wifi_link/main/wifi_link_main.c
[esp-cmake]: ../../03_Firmware/esp32_wifi_link/main/CMakeLists.txt
[contract]: ../../03_Firmware/esp32_wifi_link/main/wifi_control_contract.c
[ticket]: ../../03_Firmware/esp32_wifi_link/main/wifi_control_ticket.c
[owner]: ../../03_Firmware/esp32_wifi_link/main/wifi_control_owner.c
[state]: ../../03_Firmware/esp32_wifi_link/main/wifi_control_state.c
[executor]: ../../03_Firmware/esp32_wifi_link/main/wifi_control_executor.c
[esp-examples]: ../../03_Firmware/esp32_examples/README.md
[tests]: ../../03_Firmware/tests/README.md
[page-tests]: ../../03_Firmware/tests/test_wifi_control_main_page.js
[st-docs]: https://www.st.com/en/microcontrollers-microprocessors/stm32f446/documentation.html
[idf-rtos]: https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/api-reference/system/freertos_idf.html
[mdn-send]: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/send
[mdn-blur]: https://developer.mozilla.org/en-US/docs/Web/API/Window/blur_event
