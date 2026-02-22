# [STM32] LL(Low-Layer) 드라이버를 이용한 LED 제어 및 환경 구축

## 📌 1. 개요

STM32 개발 시 높은 추상화 수준을 제공하는 HAL 대신, 레지스터에 직접 접근하여 성능을 최적화하고 코드 크기를 줄일 수 있는 **LL(Low-Layer) API**를 사용하여 LED 깜빡이기(Blink)를 구현함.

## 📌 2. 개발 환경 설정

LL 드라이버를 정상적으로 사용하기 위해서는 단순한 코드 작성 외에 IDE 레벨의 추가 설정이 필수적임.

### 2.1 STM32CubeMX 드라이버 전환

* `Project Manager` ➡️ `Advanced Settings` ➡️ `Driver Selector`에서 **GPIO** 항목을 **LL**로 변경함.
* 이 설정을 통해 `MX_GPIO_Init()` 함수가 LL 전용 초기화 코드로 생성됨.

### 2.2 전처리기 심볼(Preprocessor Symbols) 추가

LL 드라이버의 구조체와 함수 정의를 컴파일러가 인식할 수 있도록 심볼을 추가해야 함.

* **경로:** `Properties` ➡️ `C/C++ Build` ➡️ `Settings` ➡️ `Preprocessor`.
* **추가 심볼:** `USE_FULL_LL_DRIVER` (이 설정이 누락될 경우 `unknown type name` 에러가 발생함).

## 📌 3. 소스 코드 구현 (Hybrid 방식)

제어 성능이 중요한 GPIO 제어는 LL을 사용하고, 편의성이 중요한 시간 지연은 HAL을 혼용하는 효율적인 전략을 사용함.

### 3.1 헤더 포함 (main.h)

LL 드라이버는 기능별로 헤더가 분리되어 있어 필요한 모듈을 직접 포함해야 함.

```c
/* USER CODE BEGIN Includes */
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"
#include "stm32f4xx_ll_utils.h"
#include "stm32f4xx_ll_system.h"
/* USER CODE END Includes */
```

### 3.2 메인 루프 (main.c)

```c
while (1)
{
  /* LL API를 사용하여 하드웨어 레지스터를 직접 제어 (오버헤드 최소화) */
  LL_GPIO_TogglePin(LD2_GPIO_Port, LD2_Pin);

  /* 딜레이는 편리한 HAL 함수를 유지하여 개발 효율성 확보 */
  HAL_Delay(500); 
}
```

## 📌 4. 학습 결과 요약

| 항목 | HAL 방식 | LL 방식 |
| --- | --- | --- |
| **추상화 수준** | 높음 (함수 호출 중심) | 낮음 (레지스터 직접 제어 중심) |
| **성능/속도** | 상대적으로 느림 (오버헤드 존재) | 매우 빠름 (최적화 성능) |
| **코드 크기** | 큼 | 작음 (최소 용량 구현 가능) |
| **난이도** | 낮음 | 높음 (MCU 구조 이해 필요) |
