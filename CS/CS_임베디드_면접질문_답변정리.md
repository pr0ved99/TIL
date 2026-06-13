# CS/임베디드 면접 질문 답변 정리

## 1. C 메모리 영역 / MCU 동적 할당

### 질문

C에서 stack, heap, static 영역의 차이는 무엇이고, MCU에서 동적 할당을 조심해야 하는 이유는 무엇인가?

### 답변

C 프로그램의 메모리 영역은 크게 code, data/static, stack, heap으로 나눌 수 있습니다. code 영역에는 실행 코드가 저장되고, static/global 영역에는 전역 변수와 static 변수가 저장됩니다. stack은 함수 호출 시 생성되는 지역 변수와 return address 등이 저장되는 영역이고, 함수가 끝나면 자동으로 해제됩니다. heap은 `malloc`, `free`처럼 실행 중에 동적으로 메모리를 할당하고 해제하는 영역입니다.

MCU에서는 RAM 크기가 제한적이고 실시간성이 중요하기 때문에 동적 할당을 조심해야 합니다. heap을 반복적으로 할당/해제하면 fragmentation이 생길 수 있고, 할당 시간이 일정하지 않아 latency가 예측 불가능해질 수 있습니다. 또한 메모리 부족이 발생하면 시스템이 불안정해질 수 있기 때문에, MCU에서는 가능하면 정적 할당이나 고정 크기 buffer를 사용하는 편이 안전합니다.

### 짧은 답변

stack은 함수 호출 중 생기는 지역 변수 영역이고, heap은 실행 중 동적으로 할당하는 영역입니다. MCU는 RAM이 작고 실시간성이 중요하기 때문에 heap fragmentation, 메모리 부족, 예측 불가능한 할당 시간 문제가 생길 수 있어 동적 할당을 조심해야 합니다.

---

## 2. Interrupt vs Polling

### 질문

인터럽트와 폴링의 차이는 무엇이고, 센서 입력 처리에서는 무엇을 선택할 것인가?

### 답변

Polling은 CPU가 주기적으로 상태를 확인하면서 데이터가 들어왔는지 검사하는 방식입니다. 구현이 단순하고 주기를 제어하기 쉽지만, 이벤트가 없을 때도 계속 확인해야 하므로 CPU 자원을 사용할 수 있습니다. Interrupt는 이벤트가 발생했을 때 하드웨어가 CPU에 알려주고 ISR을 실행하는 방식입니다. 응답성이 좋고 CPU를 효율적으로 사용할 수 있지만, ISR 안에서는 짧고 빠르게 처리해야 하며 공유 자원 관리에 주의해야 합니다.

센서 입력 처리에서는 센서 특성에 따라 선택합니다. 버튼, 외부 이벤트, UART 수신처럼 비동기적으로 들어오는 입력은 interrupt가 적합하고, 온도나 거리 센서처럼 일정 주기로 읽어도 되는 데이터는 timer 기반 polling이 적합합니다. 실제 프로젝트에서는 UART 수신은 interrupt/DMA로 받고, 주기적인 센서 값은 timer 주기에 맞춰 polling하는 방식으로 분리하겠습니다.

### 짧은 답변

폴링은 CPU가 주기적으로 확인하는 방식이고, 인터럽트는 이벤트가 발생했을 때 CPU에 알려 처리하는 방식입니다. 비동기 입력이나 UART 수신은 interrupt가 적합하고, 일정 주기로 읽는 센서는 timer 기반 polling이 적합합니다.

---

## 3. UART / I2C / SPI / CAN 비교

### 질문

UART, I2C, SPI, CAN을 속도와 통신 방식 관점에서 비교해보라.

### 답변

UART는 TX/RX 두 선을 사용하는 비동기 직렬 통신입니다. clock 선 없이 baudrate를 맞춰 통신하며, 1:1 통신에 단순하게 쓰기 좋습니다. I2C는 SCL, SDA 두 선을 사용하는 동기식 버스 통신이고, 하나의 bus에 여러 slave를 주소 기반으로 연결할 수 있습니다. 다만 pull-up 구조라 속도와 거리에는 한계가 있습니다.

SPI는 SCLK, MOSI, MISO, CS를 사용하는 동기식 통신입니다. I2C보다 빠르고 full-duplex 통신이 가능하지만, slave가 늘어나면 CS 선이 추가로 필요합니다. CAN은 자동차나 산업 환경에서 많이 쓰는 multi-master bus 통신이고, 메시지 ID 기반 arbitration과 오류 검출 기능이 있어 노이즈가 있는 환경이나 여러 노드가 연결되는 시스템에 적합합니다.

### 짧은 답변

UART는 TX/RX 기반 비동기 1:1 통신, I2C는 SCL/SDA 기반 주소형 다중 slave 버스, SPI는 clock과 chip select를 쓰는 빠른 동기식 통신, CAN은 여러 노드가 bus를 공유하며 arbitration과 오류 검출을 제공하는 차량/산업용 통신입니다.

---

## 4. RTOS task / priority / semaphore / mutex

### 질문

RTOS에서 task, priority, semaphore, mutex는 어떤 역할을 하는가?

### 답변

RTOS에서 task는 독립적으로 실행되는 작업 단위입니다. 예를 들어 센서 읽기 task, 통신 task, 제어 task처럼 기능별로 나눌 수 있습니다. Priority는 task의 우선순위이며, 더 중요한 작업이 먼저 실행되도록 스케줄러가 판단하는 기준입니다.

Semaphore는 task 간 이벤트 전달이나 자원 개수 관리에 사용됩니다. 예를 들어 UART 수신 완료 interrupt가 발생했을 때 통신 task에 semaphore를 주어 처리하도록 만들 수 있습니다. Mutex는 공유 자원에 동시에 접근하지 못하도록 보호하는 lock입니다. 예를 들어 여러 task가 같은 UART나 shared buffer에 접근할 때 race condition을 막기 위해 사용합니다. Mutex는 priority inversion을 줄이기 위해 priority inheritance 같은 기능을 제공하는 경우도 있습니다.

### 짧은 답변

task는 RTOS에서 실행되는 작업 단위이고, priority는 어떤 task를 먼저 실행할지 결정하는 기준입니다. semaphore는 이벤트 알림이나 자원 개수 관리에 쓰고, mutex는 shared buffer나 UART 같은 공유 자원을 동시에 접근하지 못하게 보호할 때 사용합니다.

---

## 5. ROS에서의 동시성 / Mutex 관련 답변

### 질문

ROS에도 semaphore나 mutex와 비슷한 개념이 있을 텐데 설명 가능한가?

### 답변

ROS 자체가 RTOS처럼 semaphore나 mutex를 직접 전면에 내세우는 구조는 아니지만, node 내부에서 callback이 동시에 실행되거나 shared data에 접근하면 일반적인 멀티스레딩 문제가 발생할 수 있습니다. ROS 2에서는 executor, callback group, multi-threaded executor를 사용할 때 여러 callback이 병렬로 실행될 수 있기 때문에 공유 변수 접근 시 mutex로 보호해야 합니다.

예를 들어 센서 callback이 최신 센서 값을 갱신하고, 제어 loop가 그 값을 읽는 구조라면 두 작업이 동시에 같은 데이터를 접근할 수 있습니다. 이때 mutex를 사용하거나 callback group을 분리/제한해 race condition을 방지할 수 있습니다.

### 짧은 답변

ROS 2에서는 multi-threaded executor나 여러 callback이 shared data에 접근할 때 동시성 문제가 생길 수 있습니다. 이 경우 C++의 mutex나 callback group 설정으로 race condition을 막아야 합니다.

---

## 6. STM32 - UART command frame 구조

### 질문

STM32와 상위 시스템을 UART 115200 bps로 연결했다면 command frame 구조를 어떻게 잡았는가? delimiter, fixed length, checksum 중 무엇을 썼고 왜 그렇게 썼는가?

### 답변

프로젝트에서는 구현 단순성과 디버깅 편의성을 위해 문자열 기반 frame과 delimiter 방식을 사용했습니다. 예를 들어 `CMD,ID,VALUE\r\n`처럼 payload 끝에 `\r\n`을 붙이고, 상위 시스템에서는 delimiter를 기준으로 한 줄씩 읽어 parsing했습니다. 이 방식은 serial monitor로 사람이 직접 확인하기 쉽고 초기 검증 단계에서 빠르게 적용할 수 있다는 장점이 있습니다.

다만 실제 제품 수준의 안정성을 고려하면 delimiter만으로는 부족할 수 있습니다. 데이터 중간이 깨지거나 일부 byte가 유실되었을 때 frame 경계를 잘못 잡을 수 있기 때문입니다. 개선한다면 start byte, payload length, command ID, payload, checksum 또는 CRC를 포함한 구조로 바꾸겠습니다. 예를 들어 `[STX][LEN][CMD][PAYLOAD][CRC][ETX]` 형태로 만들면 수신 측에서 길이와 checksum을 검증해 잘못된 frame을 버릴 수 있습니다.

### 짧은 답변

초기 구현은 디버깅이 쉬운 문자열 frame과 `\r\n` delimiter를 사용했습니다. 다만 안정성을 높이려면 start byte, length, command, payload, checksum/CRC를 포함한 fixed 또는 hybrid frame으로 개선하는 것이 맞습니다.

---

## 7. 메카넘 휠 속도 계산 / Saturation

### 질문

메카넘 휠에서 전진, 횡이동, 회전 명령이 동시에 들어오면 각 바퀴 속도를 어떻게 계산하고 saturation은 어떻게 처리하는가?

### 답변

메카넘 휠은 로봇의 전진 속도 `Vx`, 횡이동 속도 `Vy`, 회전 속도 `omega`를 조합해서 네 바퀴 속도를 계산합니다. 일반적인 형태는 다음과 같습니다.

```text
front_left  = Vx - Vy - (L + W) * omega
front_right = Vx + Vy + (L + W) * omega
rear_left   = Vx + Vy - (L + W) * omega
rear_right  = Vx - Vy + (L + W) * omega
```

여기서 `L`과 `W`는 로봇 중심에서 바퀴까지의 거리 성분입니다. 실제 바퀴 각속도로 바꾸려면 wheel radius `r`로 나눠줍니다.

계산된 값 중 하나라도 모터 최대 속도를 넘으면 전체 비율을 유지한 채 scale down합니다. 예를 들어 네 바퀴 명령의 최대 절댓값이 허용 최대값보다 크면, 모든 바퀴 속도에 `max_allowed / max_abs_command` 비율을 곱합니다. 이렇게 하면 이동 방향은 유지하면서 saturation을 처리할 수 있습니다.

### 짧은 답변

`Vx`, `Vy`, `omega`를 조합해 네 바퀴 속도를 계산하고, 최대값을 넘는 바퀴가 있으면 네 바퀴 명령 전체를 같은 비율로 줄여 방향성을 유지합니다.

---

## 8. 모터 보정 / Calibration

### 질문

서보나 DC 모터는 누적 오차와 calibration 문제가 생길 수 있는데 실제 동작을 어떻게 보정했는가?

### 답변

모터 보정은 open-loop로 PWM만 주는 방식과 closed-loop로 encoder feedback을 받는 방식으로 나눌 수 있습니다. 초기 검증에서는 PWM duty와 direction을 주고 실제 이동 거리나 회전 방향을 확인하는 방식으로 동작을 검증했습니다. 하지만 더 정확한 제어를 위해서는 encoder tick, wheel radius, gear ratio를 이용해 목표 속도와 실제 속도의 차이를 계산하고 PI/PID 제어로 보정하는 것이 필요합니다.

실제 답변에서는 "제가 진행한 범위에서는 PWM과 direction 기반으로 동작을 확인했고, 정밀 보정까지는 제한적이었습니다. 개선한다면 encoder feedback을 받아 목표 속도와 실제 속도의 오차를 계산하고, wheel별 calibration coefficient 또는 PID gain을 적용해 보정하겠습니다."라고 말하는 것이 적절합니다.

### 짧은 답변

초기 검증은 PWM/direction으로 실제 동작을 확인했고, 정밀 보정은 encoder tick과 wheel radius를 이용해 목표 속도와 실제 속도 차이를 구한 뒤 PI/PID 또는 wheel별 보정 계수로 처리하는 방식이 적절합니다.

---

## 9. ADC/GPIO 100ms 샘플링 주기

### 질문

ADC/GPIO를 100ms마다 샘플링한 이유는 무엇이고, 더 빠르거나 느리면 어떤 문제가 생기는가?

### 답변

100ms는 10Hz에 해당하는 주기입니다. 이 값을 선택할 때는 센서의 output data rate, 측정 대상의 변화 속도, MCU 처리 부하, 통신 주기, 화면 표시 주기를 함께 고려해야 합니다. 예를 들어 장비 상태 모니터링처럼 빠른 제어보다 상태 확인이 중요한 센서라면 10Hz 정도로도 충분할 수 있습니다. 반대로 빠른 제어 loop에 들어가는 IMU나 encoder라면 100ms는 너무 느릴 수 있습니다.

주기를 너무 빠르게 잡으면 ADC 변환, filtering, UART 전송, 상위 시스템 parsing 부하가 커지고 MCU가 다른 작업을 처리할 여유가 줄어듭니다. 너무 느리게 잡으면 센서 변화 감지가 늦어지고 이상 상태를 놓칠 수 있습니다. 따라서 100ms는 센서의 데이터시트상 갱신 주기와 시스템에서 요구하는 latency를 기준으로 선택했다고 설명하는 것이 좋습니다.

### 짧은 답변

100ms는 10Hz 주기이며, 상태 모니터링 목적에서는 센서 변화 속도와 MCU 부하를 고려한 타협값입니다. 더 빠르면 MCU와 통신 부하가 커지고, 더 느리면 이상 상태 감지가 늦어질 수 있습니다. 근거로는 센서 ODR, 요구 latency, MCU 처리 주기를 제시해야 합니다.

---

## 10. 모르는 질문이 나왔을 때 답변 방식

### 나쁜 흐름

죄송합니다. 공부하지 못했습니다. 넘어가겠습니다.

### 좋은 흐름

정확한 구현 경험은 제한적이지만, 개념적으로는 이 부분까지 이해하고 있습니다. 제가 진행한 프로젝트에서는 이 범위까지 적용했고, 실제로 개선한다면 이 방향으로 보완하겠습니다.

### 예시

세마포어와 뮤텍스를 깊게 구현해 본 경험은 제한적입니다. 다만 세마포어는 task 간 이벤트 전달이나 자원 개수 관리에 쓰이고, 뮤텍스는 shared buffer 같은 공유 자원을 보호하는 데 사용한다고 이해하고 있습니다. 제가 UART 수신 task를 RTOS 구조로 개선한다면 interrupt에서 semaphore를 주고, 통신 task가 buffer를 처리하는 구조로 설계하겠습니다.

---

## 11. 우선 암기할 핵심 문장

1. MCU에서 동적 할당은 heap fragmentation과 예측 불가능한 latency 때문에 조심해야 합니다.
2. 비동기 이벤트는 interrupt, 주기적 센서 읽기는 timer 기반 polling이 적합합니다.
3. UART는 단순한 1:1 비동기 통신, I2C는 주소 기반 다중 slave, SPI는 빠른 동기식 통신, CAN은 오류 검출과 arbitration이 있는 multi-master bus입니다.
4. Semaphore는 이벤트 전달, mutex는 공유 자원 보호에 사용합니다.
5. UART frame은 delimiter 방식으로 시작할 수 있지만, 안정성을 위해 length와 checksum/CRC를 포함하는 구조가 좋습니다.
6. 메카넘 휠은 `Vx`, `Vy`, `omega`를 조합해 네 바퀴 속도를 계산하고, 최대값 초과 시 전체를 같은 비율로 scale down합니다.
7. 100ms 샘플링은 10Hz이며, 센서 ODR, MCU 부하, 요구 latency를 근거로 설명해야 합니다.
