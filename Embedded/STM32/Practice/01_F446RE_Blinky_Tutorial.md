# [STM32] NUCLEO-F446RE LED 깜빡이기 (Blink) 예제 구현

## 📌 개발 환경

* **OS:** Ubuntu 22.04 LTS
* **IDE:** STM32CubeIDE v2.0.0
* **Code Generator:** STM32CubeMX v6.16.1 (Stand-alone)
* **Target Board:** NUCLEO-F446RE

---

## 1. STM32CubeMX 프로젝트 세팅 및 코드 생성

버전 2.0부터는 IDE 밖에서 독립된 STM32CubeMX를 통해 `.ioc` 파일을 설정하고 뼈대 코드를 생성해야 한다.

1. **보드 선택:** `STM32CubeMX` 실행 후 `ACCESS TO BOARD SELECTOR`에서 `NUCLEO-F446RE`를 검색하여 선택.
2. **기본 핀 초기화:** 팝업창(Initialize all peripherals with their default Mode?)에서 **`Yes`**를 선택하여 보드의 기본 LED(PA5)와 유저 버튼(PC13) 설정을 자동으로 불러온다.
3. **Project Manager 설정:**
   * **Project Name:** `F446RE_Blinky` (원하는 이름 지정)
   * **Project Location:** 로컬 작업 경로 지정 (Git 추적 폴더 하위 권장)
   * **Toolchain / IDE:** 반드시 **`STM32CubeIDE`**로 변경.
   * **주의:** `Generate Under Root` 옵션의 체크를 **해제**한다. (해제 시 `STM32CubeIDE`라는 하위 폴더가 생성되어 설정 파일 꼬임을 방지할 수 있음)

4. 우측 상단의 **`GENERATE CODE`**를 클릭하여 뼈대 코드를 추출한다.

---

## 2. STM32CubeIDE 프로젝트 Import 및 .gitignore 설정

생성된 코드를 IDE로 불러와 작업 환경을 구성한다.

1. `STM32CubeIDE` 실행 후 `File` ➡️ `Import` ➡️ `Existing Projects into Workspace` 선택.
2. `Select root directory`에서 CubeMX가 코드를 생성한 폴더(`F446RE_Blinky`)를 선택하고 `Finish` 클릭.
3. **Git 사용 시 주의사항:** 루트 폴더에 `.gitignore`를 생성할 때, IDE 설정 파일인 **`.project`**와 **`.cproject`**는 추적되도록 남겨두고, 빌드 부산물인 `Debug/`, `Release/`, `.metadata/` 등만 무시하도록 설정해야 다른 PC에서도 정상적으로 불러올 수 있다.

---

## 3. main.c 코드 작성

좌측 Project Explorer에서 `Core/Src/main.c` 파일을 열고, `while (1)` 루프 내부의 `/* USER CODE BEGIN 3 */` 영역에 LED 제어 코드를 작성한다. (주석 영역을 벗어나면 코드 재생성 시 삭제되므로 주의)

```c
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    
    // NUCLEO-F446RE 보드의 내장 초록색 LED(LD2, PA5) 상태 반전
    HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
    
    // 500ms(0.5초) 대기 (1500으로 변경 시 1.5초 간격 제어 가능)
    HAL_Delay(500);

  }
  /* USER CODE END 3 */
```

---

## 4. 빌드 및 보드 업로드

1. 보드를 PC에 USB로 연결한다.
2. 상단 툴바의 망치 아이콘(**Build**)을 눌러 에러 없이 컴파일되는지 확인한다 (`0 errors`).
3. 재생 아이콘(**Run**)을 눌러 보드에 펌웨어를 업로드(`Download verified successfully`)하면 LED가 정상적으로 점멸한다.
