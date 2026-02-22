# Ubuntu 22.04 환경 STM32CubeIDE 2.0 및 STM32CubeMX 설치 방법

## 📌 개요 및 핵심 변경 사항

* 기존 1.19 버전까지는 IDE 내부에 STM32CubeMX가 통합되어 있었음.
* **2.0 버전부터는 구조가 변경되어 STM32CubeMX가 완전히 독립된(Stand-alone) 별도의 프로그램으로 분리됨.**
* 따라서 2.0 환경에서 개발을 진행하려면, **IDE와 MX를 각각 별도로 다운로드하여 우분투에 설치**해야 핀맵 설정(`.ioc`)부터 코딩까지 정상적으로 작업이 가능함.

---

## 1. 기존 구버전(1.19) 완전히 삭제하기

시스템에 찌꺼기로 남아있는 구버전 설치 디렉토리와 앱 런처(바로가기) 파일을 깔끔하게 지워준다.

```bash
# 1. 기존 IDE 설치 폴더 삭제
sudo rm -rf /opt/st/stm32cubeide_1.19.0

# 2. 바로가기 아이콘(.desktop) 삭제
sudo rm ~/.local/share/applications/stm32cubeide*.desktop
# (만약 위 경로에 없다면 아래 명령어도 확인해 볼 것)
# sudo rm /usr/share/applications/st-stm32cubeide*.desktop

```

---

## 2. STM32CubeIDE 2.0.0 설치

ST 공식 홈페이지에서 리눅스용 데비안 인스톨러(`deb_bundle.sh`가 포함된 압축파일)를 다운로드한 후 터미널에서 진행한다.

```bash
# 1. 다운로드 폴더로 이동
cd ~/Downloads

# 2. 압축 해제 (다운로드한 파일명에 맞게 입력)
unzip st-stm32cubeide_2.0.0_26820_20251114_1348_amd64.deb_bundle.sh.zip

# 3. 설치 스크립트에 실행 권한 부여
chmod +x st-stm32cubeide_2.0.0_26820_20251114_1348_amd64.deb_bundle.sh

# 4. 관리자 권한으로 설치 진행
sudo ./st-stm32cubeide_2.0.0_26820_20251114_1348_amd64.deb_bundle.sh

```

**💡 터미널 설치 진행 팁:**

* 스크립 실행 후 긴 라이선스 약관이 나오면 **`q`**를 눌러 맨 끝으로 스킵 가능.
* 약관 동의 여부 프롬프트가 나오면 **`y`** 입력 후 엔터.
* 이후 ST-LINK, J-Link 디버거 USB 인식을 위한 드라이버 룰(`udev rules`) 설치 여부를 물어볼 때도 모두 **`y`**를 선택한다.

---

## 3. STM32CubeMX 설치 (v6.16.1 기준)

보드 핀맵/클럭 초기화 및 뼈대 코드 생성을 위한 필수 프로그램. IDE와 마찬가지로 리눅스용 설치 파일(.zip)을 받아 진행한다.

```bash
# 1. 다운로드 폴더에서 압축 해제
unzip stm32cubemx-lin-v6-16-1.zip

# 2. 풀려난 리눅스용 셋업 파일에 실행 권한 부여
chmod +x SetupSTM32CubeMX-6.16.1.linux

# 3. GUI 설치 마법사 실행 (관리자 권한)
sudo ./SetupSTM32CubeMX-6.16.1.linux

```

**💡 GUI 설치 진행 팁:**

* 마지막 명령어를 실행하면 터미널이 아니라 **GUI 팝업 창(마법사)**이 나타남.
* 윈도우 프로그램 설치하듯 `Next` 클릭 -> 라이선스 `Accept` -> 기본 설치 경로 유지 후 끝까지 진행.
* 설치가 완료되면 마지막 화면 우측 하단의 초록색 체크 모양 **`Done`** 버튼을 눌러 깔끔하게 마법사를 종료한다.

---

## 4. 실행 테스트 (To-Do)

* 우분투의 `Show Applications(프로그램 표시)`에서 `STM32CubeIDE`와 `STM32CubeMX` 앱 아이콘이 정상적으로 생성되었는지 검색 후 각각 실행해 본다.
