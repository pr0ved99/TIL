# [STM32] 외부 인터럽트(EXTI)를 활용한 버튼 제어 실습

오늘은 STM32의 EXTI(External Interrupt) 기능을 활용하여, 
단순히 `while` 문에서 버튼 입력을 계속 확인(Polling 방식)하는 것이 아니라, 
**버튼(B1)이 눌리는 즉각적인 이벤트(Interrupt)에 반응하여 LED(LD2)가 토글(Toggle)** 되도록 구현해 보았다.

---

## 📌 1. EXTI(External Interrupt)란 무엇인가?

버튼 입력이나 외부 센서 신호처럼, MCU 외부에서 발생하는 이벤트에 즉각적으로 반응하기 위해 사용하는 인터럽트 기능이다.

기존 폴링(Polling) 방식은 `while (1)` 루프 안에서 계속 `버튼이 눌렸는지?` 물어보며 MCU 자원(자원)을 낭비하지만, **인터럽트 방식을 사용하면 버튼이 눌렸을 때만 하드웨어가 MCU에 신호를 보내 미리 설정된 함수(ISR)를 실행**하므로 훨씬 효율적이고 즉각적인 처리가 가능해진다.

---

## 📌 2. 프로젝트 및 환경 설정 (STM32CubeMX)

인터럽트를 사용하기 위해 `F446RE_EXTI`라는 새로운 프로젝트를 생성하고 아래와 같이 핀과 시스템을 설정했다.

### 2.1 GPIO 핀 설정 (PC13 - User Button)
보드의 파란색 유저 버튼(B1)은 `PC13` 핀에 연결되어 있다. 이 핀의 속성을 클릭하여 다음과 같이 설정했다.

* **GPIO mode:** `External Interrupt Mode with Falling edge trigger detection`
  * *이유: 버튼을 '누르는 순간(Falling Edge)'에 인터럽트를 발생시키기 위함.*
* **GPIO Pull-up/Pull-down:** `No pull-up and no pull-down`
  * *NUCLEO 보드는 이미 외부 회로에 풀업 저항이 달려있기 때문에 설정하지 않음.*
* **User Label:** `B1 [Blue PushButton]`

### 2.2 인터럽트 컨트롤러 (NVIC) 활성화
인터럽트 신호가 발생했을 때 실제로 MCU의 코어 시스템 시스템이 이를 받아들이도록 허용해 주어야 한다.

* 좌측 `System Core` ➡️ `NVIC` 탭으로 이동.
* **`EXTI line[15:10] interrupts`** 항목을 체크(Enable)하여, 13번 핀(PC13)이 포함된 그룹의 인터럽트를 활성화했다.

---

## 📌 3. 소스 코드 구현 (main.c)

코드를 작성할 때, 버튼이 인터럽트에 의해 눌렸다는 사실을 메인 루프(`while`)에 알려주기 위해 **플래그(Flag)** 변수를 활용하는 방식을 사용했다.

### 3.1 플래그 전역 변수 선언
어느 함수에서든 상태를 체크할 수 있도록 `main.c` 상단에 1바이트 변수를 만들었다.

```c
/* USER CODE BEGIN 0 */
uint8_t button_flag = 0;
/* USER CODE END 0 */
```

### 3.2 EXTI 콜백(Callback) 함수 작성
버튼이 눌려서 하드웨어 인터럽트가 발생하면 자동으로 호출되는 함수(`HAL_GPIO_EXTI_Callback`)를 재정의(Override)한다. 
*이 함수에서는 복잡하거나 긴 코드를 피하고, 짧게 플래그만 변경하는 것이 원칙이다.*

```c
/* USER CODE BEGIN 4 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  // 인터럽트가 발생한 핀이 우리가 설정한 유저 버튼 핀(B1)이 맞는지 확인
  if (GPIO_Pin == B1___Blue_PushButton_Pin)
  {
    // 메인 루프에게 버튼이 눌렸음을 알림
    button_flag = 1; 
  }
}
/* USER CODE END 4 */
```

### 3.3 메인 루프 (while문) 처리
이제 무한 루프 안에서는 계속 버튼 핀 상태를 읽어올 필요 없이, `button_flag`만 쳐다보고 있으면 된다.

```c
/* Infinite loop */
/* USER CODE BEGIN WHILE */
while (1)
{
  /* USER CODE END WHILE */

  /* USER CODE BEGIN 3 */
  
  // 콜백 함수에 의해 플래그가 1로 바뀌었는지 확인
  if (button_flag == 1)
  {
    // 보드의 초록색 LED (LD2, PA5) 상태를 반전(Toggle)
    HAL_GPIO_TogglePin(LD2_GPIO_Port, LD2_Pin);
    
    // 이벤트를 1회 처리했으므로 플래그를 다시 0으로 초기화
    button_flag = 0;
  }

}
/* USER CODE END 3 */
```

---

## 📌 4. 실습 결과 및 느낀 점

보드에 코드를 다운로드하고 실행한 뒤, 파란색 버튼(B1)을 누를 때마다 초록색 LED(LD2)가 즉시 켜지고 꺼지는 것을 확인했다.
인터럽트를 활용하니, 백그라운드에서 아무 일도 안 하고 있을 때만 CPU가 개입하는 구조를 직관적으로 이해할 수 있었다!
