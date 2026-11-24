# HP Victus Windows·Ubuntu 듀얼부팅 실행서

2026-11-20 · HP Victus 15-fb0xxx · Ubuntu Desktop 24.04.4 LTS (amd64)

**2026-11-20 후속 상태:** Ubuntu 설치와 기본 초기 설정 완료는 사용자 보고로 확인했다. Windows 조회에서는 C: 약 480.4 GiB, Linux 파일시스템 유형 파티션 450 GiB, 기존 EFI·MSR·복구 파티션을 확인했다. 최신 작업은 [Ubuntu 세션 시작 프롬프트](../handoff/NEXT_SESSION_START_PROMPT.md)를 따른다. 아래는 설치 때 사용한 절차다.

**설치 절차의 첫 작업은 USB에서 Ubuntu를 체험하는 것이다.** 화면과 Wi-Fi를 확인한 뒤 Windows에서 공간을 확보하고 Ubuntu를 설치한다. 전원을 끄기 전에 이 파일을 휴대전화에 복사해 두면 USB로 부팅한 뒤에도 볼 수 있다.

## 설치 후 개발 도구 · 2026-11-22

| 작업 | 확인한 도구 |
| --- | --- |
| ROS와 시뮬레이션 | Ubuntu 24.04.5, ROS 2 Jazzy, Gazebo Harmonic 8.15.0, RViz2, Nav2와 ROS–Gazebo 브리지 |
| 회로와 계측 | KiCad 10.0.8과 라이브러리, VeroRoute 2.40, PulseView 0.4.2와 FX2 펌웨어 |
| STM32 개발 | STM32CubeIDE 2.1.1, STM32CubeMX 6.17.0, CubeF4 1.28.3, ST-LINK 도구 |
| ESP32-S3 개발 | EIM 0.22.0, ESP-IDF 6.0.2, Xtensa 컴파일러와 Python 필수 패키지 |
| 공통 | Chrome, VS Code와 ROS·STM32·ESP-IDF 확장, CMake, pySerial, `python3-venv`, ripgrep 14.1.0 |

CubeF4 패치는 1.28.0 기본 패키지 설치 후 진행했다. 오프라인 패치에 필요한 기본 ZIP을 `~/STM32Cube/Repository`에 두고 CubeMX의 `From Local…`에서 1.28.3 패치 ZIP을 선택했다. ESP-IDF는 EIM 환경에서 `idf.py --version`과 ESP32-S3 컴파일러를 실행해 확인했다. 보드 빌드·플래시·연결 시험은 해당 작업에서 검증한다.

Onshape 진단에서 Chrome이 RTX 3050 Ti로 WebGL을 렌더링하는 것을 확인했다. NVIDIA 고정 모드에서 화면 멈춤·영상 버벅임이 보고돼 `on-demand`로 복원했다. 멈춤 원인은 확정되지 않았다. Onshape에서 RTX로 시험할 때는 `switcherooctl list`에서 번호를 확인하고 Chrome 종료 후 `switcherooctl launch -g 1 google-chrome https://cad.onshape.com/check`를 실행한다. 실습 당시 RTX 번호는 1이었다.

## 0. 설치 전에 확인한 값

| 항목 | 이 노트북의 상태 |
| --- | --- |
| 설치 대상 | **WD Blue SN5000 1TB NVMe**, Windows 디스크 0, GPT/UEFI |
| 기존 파티션 | EFI 약 100 MiB / MSR 16 MiB / C: NTFS 약 930.4 GiB / Windows 복구 약 976 MiB |
| C: 여유 공간과 축소 한도 | 여유 약 747 GB. 관리자 PowerShell에서 실제 축소 한도 **465.2 GiB** 확인 |
| 암호화와 복구 | C: 암호화 0%, 보호 해제, **Windows RE Enabled** |
| 그래픽과 펌웨어 | AMD 내장 GPU 및 **RTX 3050 Ti Laptop GPU**. Windows에서 Secure Boot 꺼짐 확인 |
| 외장 백업 | **D:\TIL_Backup_2026-11-20_131829\TIL**, 17,986개/3.21 GB SHA-256 대조 및 Shield 회로도 1개 복원 성공. 외장 디스크 분리 확인 |
| 설치 USB | **32GB Generic Flash Disk**, Windows E:, 라벨 **UBUNTU 24_0**. Ubuntu 24.04.4 LTS와 UEFI 부팅 파일 확인, 커널·initrd의 체크섬 일치 |
| 설치 당시 작업 순서 | Live USB 부팅 → C: 축소 → 설치 → Windows와 Ubuntu 각각 부팅 → Ubuntu 초기 설정 |

백업 확인 범위는 TIL 폴더 전체다. 다른 위치의 개인 문서나 작업 자료도 보존해야 한다면 파티션을 바꾸기 전에 외장 저장장치에 복사한다. 설치할 때 외장 백업 디스크는 분리해 둔다.

## 1. USB에서 Ubuntu 체험하기

1. 노트북에 전원 어댑터와 **32GB Ubuntu USB**를 연결한다. 작업 중인 파일을 저장한다.
2. Windows에서 다시 시작하거나 정상 종료 후 켠다. 켜자마자 **Esc를 여러 번 → Startup Menu → F9 Boot Device Options**를 누른다.
3. **UEFI: Generic Flash Disk** 또는 USB의 UEFI 항목을 고른다. 부팅 메뉴에서는 Windows 드라이브 문자 E:가 보이지 않는다.
4. **Try or Install Ubuntu → Try Ubuntu(우분투 체험하기)**를 선택한다. 화면이 검게 멈추면 재시작해 USB 메뉴의 **safe graphics**를 한 번 시도한다.
5. 바탕화면, 키보드·터치패드, Wi-Fi 연결과 웹페이지 열기를 확인한다. Ctrl+Alt+T로 터미널을 열어 아래를 실행한다.

```bash
test -d /sys/firmware/efi && echo 'UEFI OK' || echo 'UEFI 확인 필요'
lsblk -d -o NAME,SIZE,MODEL,TRAN
nmcli device status
```

**다음 단계로 갈 기준**은 UEFI 부팅, 사용 가능한 화면·입력, **약 931 GiB의 WD Blue NVMe**와 **약 29 GiB의 USB**가 구분되는 것이다. Wi-Fi가 실패해도 유선이나 USB 테더링으로 연결 상태를 확인할 수 있다. 내부 SSD가 보이지 않거나 UEFI 확인이 실패하면 디스크를 변경하기 전에 원인을 확인한다. Live 확인이 끝나면 재시작해 F9의 **Windows Boot Manager**로 돌아간다.

[HP 부팅 장치 선택](https://support.hp.com/sk-en/document/ish_6930187-6931079-16) · [Ubuntu Desktop 설치·체험 안내](https://ubuntu.com/desktop/docs/en/24.04/tutorial/install-ubuntu-desktop/)

## 2. Windows에서 C: 축소

**추천 배정은 Ubuntu 450 GiB, Windows C: 약 480 GiB**다. 11/20 측정 한도보다 약 15 GiB 작은 배정이다. 작업 시점의 실제 한도를 디스크 관리에서 다시 본다.

1. **Win+R → diskmgmt.msc → Enter.** 디스크 0의 **C: NTFS**를 오른쪽 클릭해 **볼륨 축소**를 선택한다.
2. 최대 축소 가능 공간을 확인한다. 450 GiB를 배정하려면 Windows가 MB로 표시하는 입력칸에 **460800**을 입력한다. 450 × 1024 = 460800 MiB다. 화면의 한도가 이보다 작으면 배정량을 줄여서 결정한다.
3. 대상이 **WD Blue 내부 SSD의 C:**인 것을 확인하고 축소한다. 약 450 GiB의 검은색 **할당되지 않음** 공간이 표시되면 그대로 둔다. Windows에서 새 볼륨을 만들거나 포맷할 필요가 없다.
4. 디스크 0에 기존 **EFI·MSR·C:·복구 파티션**과 새 미할당 영역이 각각 남아 있는지 확인한다.

[Microsoft 기본 볼륨 축소 안내](https://learn.microsoft.com/en-us/windows-server/storage/disk-management/shrink-a-basic-volume)

## 3. 확보한 공간에 Ubuntu 설치

1. Esc → F9로 **32GB USB의 UEFI 항목**으로 재부팅하고 **Install Ubuntu**를 선택한다. 언어·키보드를 고르고 인터넷을 연결한다. **Interactive installation(대화형 설치) → Default selection(기본 선택)**을 고른다.
2. **Disk setup(디스크 설정) → Manual installation(수동 설치)**로 들어간다. **WD Blue SN5000 1TB**를 모델·크기로 식별한다. Linux 장치명은 보통 /dev/nvme0n1이며, 화면에 따라 이름이 달라질 수 있다.
3. **WD Blue의 약 450 GiB 미할당 공간**에 새 **ext4** 파티션을 하나 만들고 루트 **/**를 마운트 위치로 지정한다. Ubuntu 설치기가 십진 단위로 표시하면 약 **483 GB**다.
4. 부팅 파일은 같은 내부 SSD의 **기존 EFI 시스템 파티션**에 둔다. 자동으로 인식·선택됐으면 유지한다. 마운트 위치를 지정할 수 있는 화면이면 **/boot/efi**로 설정한다. **기존 EFI 포맷은 선택하지 않는다.**
5. 시간대 **Asia/Seoul**, 사용자 이름과 비밀번호를 지정한다. 최종 설치 요약에서 아래 세 가지를 확인한 뒤 **Install**을 누른다.
   - 새 포맷 대상이 미할당 공간에서 만든 **ext4 /** 파티션이다.
   - **Windows NTFS·EFI·MSR·복구 파티션**에 삭제나 포맷이 표시되지 않는다.
   - 설치 및 부팅 대상이 내부 **WD Blue NVMe**다.
6. 설치 완료 후 **Restart now**를 누른다. 설치 미디어 제거 안내가 나오면 USB를 뽑고 Enter를 누른다.

**Erase disk and install Ubuntu(디스크 지우기)** 및 **New partition table(새 파티션 테이블)**은 기존 Windows를 유지하는 이 구성에서는 선택하지 않는다. 설치기가 EFI를 인식하지 못하거나 포맷을 요구하면 적용 전 화면에서 멈춘다. EFI가 약 100 MiB라는 사실만으로 실제 남은 공간이 충분하다고 판단할 수는 없다.

[Ubuntu 디스크 설정](https://ubuntu.com/desktop/docs/en/24.04/tutorial/install-ubuntu-desktop/#disk-setup) · [Canonical 기존 EFI 사용 안내](https://github.com/canonical/subiquity/blob/main/doc/howto/configure-storage.rst#uefi-mode)

## 4. 설치 USB 없이 Windows·Ubuntu 양쪽 부팅 확인

1. Ubuntu에 로그인한다. Ubuntu 항목을 직접 고르려면 시작 직후 **Esc → F9 → ubuntu**로 들어간다. 아래 명령으로 **/**와 **/boot/efi**가 내부 SSD인지 확인한다.

```bash
grep -E '^(PRETTY_NAME|VERSION_CODENAME)=' /etc/os-release
findmnt /
findmnt /boot/efi
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,MODEL
```

2. 재시작해 GRUB 또는 **Esc → F9 → Windows Boot Manager**를 고른다. Windows에 로그인해 C:의 파일과 디스크 관리 상태를 확인한다.
3. 다시 Ubuntu를 부팅한다. **USB 없이 두 OS 모두 로그인**했으면 듀얼부팅을 확인한 것이다. GRUB에 한쪽 OS가 보이지 않더라도 F9에서 부팅 가능한지 먼저 확인한다. F9에서도 항목이 없거나 오류가 뜨면 오류 문구를 남겨서 부팅 경로부터 확인한다.

## 5. Ubuntu 초기 설정

### 5.1 네트워크·입력·업데이트

Wi-Fi, 화면 해상도·밝기, 키보드, 시간대를 확인한다. 한글 입력이 필요하면 **설정 → 키보드 → 입력 소스**에서 한국어를 추가한다. 입력 방식이 목록에 없으면 한국어 언어 지원을 추가하고 다시 로그인한다.

```bash
sudo apt update
sudo apt upgrade
sudo apt install git curl build-essential
```

업데이트 오류가 뜨면 원인을 확인한 뒤 이어간다. 재시작 안내가 있으면 재시작 후 화면과 네트워크를 다시 확인한다. [Ubuntu 기본 업데이트 안내](https://ubuntu.com/desktop/docs/en/24.04/tutorial/install-ubuntu-desktop/#dont-forget-to-update)

### 5.2 NVIDIA 드라이버

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
nvidia-smi
```

nvidia-smi에 RTX 3050 Ti Laptop GPU가 표시되면 NVIDIA 드라이버가 동작한다. 명령이 없거나 드라이버 통신 오류가 나오면 **Software & Updates → Additional Drivers(추가 드라이버)**에서 Ubuntu가 권장하는 NVIDIA 드라이버를 고른 뒤 재시작하고 다시 확인한다. 바탕화면은 AMD 내장 GPU가 담당할 수도 있다. [Ubuntu 추가 드라이버 안내](https://ubuntu.com/desktop/docs/en/24.04/tutorial/install-ubuntu-desktop/#type-of-installation)

### 5.3 프로젝트 작업 공간

Ubuntu 파일시스템에 개발 브랜치를 받는다. 기존 Ubuntu 작업 폴더가 있다면 새로 복제하기 전에 그 작업 폴더의 브랜치와 변경 상태를 확인한다.

```bash
mkdir -p "$HOME/workspace"
cd "$HOME/workspace"
git clone --branch agent/dual-encoder-bringup https://github.com/pr0ved99/TIL.git
cd TIL
git branch --show-current
git log -1 --oneline
```

Windows에서만 작업했던 파일은 외장 백업에서 필요한 것만 골라 이어간다. Ubuntu의 ROS 빌드 결과는 Ubuntu 작업 공간에 생성한다.

## 6. 완료 기준

Ubuntu 설치와 초기 설정은 사용자 완료 보고다. 아래 체크는 개별 증거가 확인된 항목에 표시한다.

- [x] Live USB에서 UEFI, 내부 NVMe, 화면·키보드 입력과 Wi-Fi 연결 확인
- [ ] Windows·EFI·복구 파티션 보존 및 Ubuntu 루트와 EFI의 위치 확인
- [ ] USB 없이 Windows·Ubuntu 각각 로그인
- [ ] Ubuntu 시간대·키보드·네트워크와 기본 업데이트 완료
- [ ] NVIDIA 인식 결과 또는 남은 오류 기록
- [ ] Ubuntu 작업 폴더에 TIL 개발 브랜치 확인

노트북에서 SIM-06 세 채널 재생과 RL-05·GATE-02 주행을 마쳤고 다음 설계 작업은 ELEC-01 보호 저항·분기 퓨즈 검토다. [Gazebo 도착 근거](../verification/48_Simulation_Gate02_2026-11-24_ko.md) 집에서는 PA4 한 채널 G1을 마쳤다. 다음은 E07/M01의 PA4·VREFINT 읽기 순서와 로그 필드 설계다. [11/23 시험 기록](../progress/2026-11-23_progress.md) · [11/24 실측과 재개점](../progress/2026-11-24_progress.md)
