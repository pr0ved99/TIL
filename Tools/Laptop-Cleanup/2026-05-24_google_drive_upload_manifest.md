# Google Drive Upload Manifest

Date: 2026-05-24
Drive root folder: `Laptop_Return_Backup_2026-05`

## Conclusion

아래 표의 `Local source`를 Google Drive의 `Drive destination` 위치로 업로드한다.
Google Drive가 현재 로컬에 마운트되어 있지 않고 `rclone`도 없으므로, 브라우저에서 Drive 폴더를 만든 뒤 파일/폴더 업로드로 진행한다.

## 0. Create These Folders First

```text
Laptop_Return_Backup_2026-05/
  01_Private_Admin/
    Finance/
    SSAFY_Admin/
  02_Project_Evidence/
    Duri_RTABMap/
    Mari_RTABMap/
    VSLAM_Demos/
    Echo_Turtle_Presentation/
    Jeokjaejeokso_Presentation/
  03_CAD_and_Hardware_Refs/
    turtle_CAD/
    WHEELTEC/
    R3_Tracked_Chassis/
  04_Videos/
    Desktop_SendAnywhere/
    Screencasts/
    Raw_Mobile/
  05_Simulation_Assets/
    S14P21C206_SmartFactory/
  06_Installers_Optional/
    ROS2/
    STM32/
    VSCode/
```

## 1. Private/Admin First

이 폴더는 공개 공유하지 않는다.

| Upload order | Local source | Drive destination |
|---:|---|---|
| 1 | `/home/ssafy/Desktop/토스뱅크_거래내역.xlsx` | `Laptop_Return_Backup_2026-05/01_Private_Admin/Finance/토스뱅크_거래내역.xlsx` |
| 2 | `/home/ssafy/Desktop/현대카드_소비패턴_분석.md` | `Laptop_Return_Backup_2026-05/01_Private_Admin/Finance/현대카드_소비패턴_분석.md` |
| 3 | `/home/ssafy/Desktop/보조배터리_가격별_6월까지_지출계획.md` | `Laptop_Return_Backup_2026-05/01_Private_Admin/Finance/보조배터리_가격별_6월까지_지출계획.md` |
| 4 | `/home/ssafy/Desktop/최근 이용 내역-현대카드.pdf` | `Laptop_Return_Backup_2026-05/01_Private_Admin/Finance/최근_이용_내역-현대카드.pdf` |
| 5 | `/home/ssafy/Downloads/14기 자율프로젝트 결과물 활용 동의서_광주_C205_이영현.docx` | `Laptop_Return_Backup_2026-05/01_Private_Admin/SSAFY_Admin/14기_자율프로젝트_결과물_활용_동의서_광주_C205_이영현.docx` |
| 6 | `/home/ssafy/Downloads/14기 자율프로젝트 결과물 활용 동의서_광주_C205_은태현.docx` | `Laptop_Return_Backup_2026-05/01_Private_Admin/SSAFY_Admin/14기_자율프로젝트_결과물_활용_동의서_광주_C205_은태현.docx` |
| 7 | `/home/ssafy/Downloads/260303_진료확인서_이영현[광주_2반].jpg` | `Laptop_Return_Backup_2026-05/01_Private_Admin/SSAFY_Admin/260303_진료확인서_이영현_광주_2반.jpg` |

## 2. Project Evidence

| Upload order | Local source | Size | Drive destination |
|---:|---|---:|---|
| 8 | `/home/ssafy/duri_rtabmap_db/` | `1.6G` | `Laptop_Return_Backup_2026-05/02_Project_Evidence/Duri_RTABMap/duri_rtabmap_db/` |
| 9 | `/home/ssafy/rtabmap_maps/` | `1.9G` | `Laptop_Return_Backup_2026-05/02_Project_Evidence/Mari_RTABMap/rtabmap_maps/` |
| 10 | `/home/ssafy/Desktop/VSLAM.mov` | `185M` | `Laptop_Return_Backup_2026-05/02_Project_Evidence/VSLAM_Demos/VSLAM.mov` |
| 11 | `/home/ssafy/Desktop/echo_turtle.pptx` | `101M` | `Laptop_Return_Backup_2026-05/02_Project_Evidence/Echo_Turtle_Presentation/echo_turtle.pptx` |
| 12 | `/home/ssafy/Desktop/Echo Trutle 반 발표.pdf` | `96M` | `Laptop_Return_Backup_2026-05/02_Project_Evidence/Echo_Turtle_Presentation/Echo_Trutle_반_발표.pdf` |
| 13 | `/home/ssafy/Desktop/Echo Turtle Project.pdf` | `112M` | `Laptop_Return_Backup_2026-05/02_Project_Evidence/Echo_Turtle_Presentation/Echo_Turtle_Project.pdf` |
| 14 | `/home/ssafy/Downloads/적재적소_발표자료/` | `41M` | `Laptop_Return_Backup_2026-05/02_Project_Evidence/Jeokjaejeokso_Presentation/적재적소_발표자료/` |
| 15 | `/home/ssafy/Downloads/적재적소.mp4` | `144M` | `Laptop_Return_Backup_2026-05/02_Project_Evidence/Jeokjaejeokso_Presentation/적재적소.mp4` |

## 3. CAD and Hardware References

| Upload order | Local source | Size | Drive destination |
|---:|---|---:|---|
| 16 | `/home/ssafy/Desktop/turtle_CAD/` | `6.1G` | `Laptop_Return_Backup_2026-05/03_CAD_and_Hardware_Refs/turtle_CAD/` |
| 17 | `/home/ssafy/Downloads/WHEELTEC R1.R3.R3X.TT马达系列底盘客户资料.zip` | `5.5G` | `Laptop_Return_Backup_2026-05/03_CAD_and_Hardware_Refs/WHEELTEC/WHEELTEC_R1_R3_R3X_TT_motor_chassis_customer_materials.zip` |
| 18 | `/home/ssafy/Desktop/R3_Tracked_Chassis_Selected_20260423/` | `169M` | `Laptop_Return_Backup_2026-05/03_CAD_and_Hardware_Refs/R3_Tracked_Chassis/R3_Tracked_Chassis_Selected_20260423/` |

## 4. Videos

| Upload order | Local source | Size | Drive destination |
|---:|---|---:|---|
| 19 | `/home/ssafy/Videos/Screencasts/` | `2.8G` | `Laptop_Return_Backup_2026-05/04_Videos/Screencasts/` |
| 20 | `/home/ssafy/Desktop/Send Anywhere (2026-05-20 21-44-56).zip` | `5.1G` | `Laptop_Return_Backup_2026-05/04_Videos/Desktop_SendAnywhere/Send_Anywhere_2026-05-20_21-44-56.zip` |
| 21 | `/home/ssafy/Desktop/IMG_1880.mov` | `1.7G` | `Laptop_Return_Backup_2026-05/04_Videos/Raw_Mobile/IMG_1880.mov` |

Optional duplicate check:

| Local source | Size | Decision |
|---|---:|---|
| `/home/ssafy/Desktop/Send Anywhere (2026-05-20 21-44-56)/` | `5.1G` | zip 업로드가 성공하면 이 폴더는 중복일 수 있음. 필요한 경우에만 업로드 |

## 5. Simulation Assets

이 단계는 용량이 크므로 앞 단계가 끝난 뒤 진행한다.

| Upload order | Local source | Size | Drive destination |
|---:|---|---:|---|
| 22 | `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/docs/videos/` | `26M` | `Laptop_Return_Backup_2026-05/05_Simulation_Assets/S14P21C206_SmartFactory/docs_videos/` |
| 23 | `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/assets/simulation_env_v1.usd` | `506M` | `Laptop_Return_Backup_2026-05/05_Simulation_Assets/S14P21C206_SmartFactory/simulation_env_v1.usd` |
| 24 | `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/assets/smart_flow_env_v1_arm6.usda` | `1.8G` | `Laptop_Return_Backup_2026-05/05_Simulation_Assets/S14P21C206_SmartFactory/smart_flow_env_v1_arm6.usda` |
| 25 | `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/assets/smart_flow_env_v2_arm6.usda` | `1.8G` | `Laptop_Return_Backup_2026-05/05_Simulation_Assets/S14P21C206_SmartFactory/smart_flow_env_v2_arm6.usda` |
| 26 | `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/assets/maps/` | `9.3G` | `Laptop_Return_Backup_2026-05/05_Simulation_Assets/S14P21C206_SmartFactory/assets_maps/` |

## 6. Optional Installers

설치파일은 다시 받을 수 있으므로 가장 마지막에 업로드한다. Drive 용량이 부족하면 생략해도 된다.

| Upload order | Local source | Size | Drive destination |
|---:|---|---:|---|
| 27 | `/home/ssafy/Downloads/ROS2 설치파일.zip` | `1.5G` | `Laptop_Return_Backup_2026-05/06_Installers_Optional/ROS2/ROS2_설치파일.zip` |
| 28 | `/home/ssafy/Downloads/stm32cubemx-lin-v6-16-1.zip` | `691M` | `Laptop_Return_Backup_2026-05/06_Installers_Optional/STM32/stm32cubemx-lin-v6-16-1.zip` |
| 29 | `/home/ssafy/Downloads/st-stm32cubeide_2.0.0_26820_20251114_1348_amd64.deb_bundle.sh` | `776M` | `Laptop_Return_Backup_2026-05/06_Installers_Optional/STM32/st-stm32cubeide_2.0.0_amd64.deb_bundle.sh` |
| 30 | `/home/ssafy/Downloads/st-stm32cubeide_2.0.0_26820_20251114_1348_amd64.deb_bundle.sh.zip` | `776M` | `Laptop_Return_Backup_2026-05/06_Installers_Optional/STM32/st-stm32cubeide_2.0.0_amd64.deb_bundle.sh.zip` |
| 31 | `/home/ssafy/Downloads/code_1.120.0-1778619059_amd64.deb` | `142M` | `Laptop_Return_Backup_2026-05/06_Installers_Optional/VSCode/code_1.120.0-1778619059_amd64.deb` |

Older VS Code installers can be skipped:

```text
/home/ssafy/Downloads/code_1.115.0-1775600353_amd64.deb
/home/ssafy/Downloads/code_1.116.0-1776214182_amd64.deb
/home/ssafy/Downloads/code_1.117.0-1776814346_amd64.deb
/home/ssafy/Downloads/code_1.118.1-1777474985_amd64.deb
/home/ssafy/Downloads/code_1.119.1-1778521423_amd64.deb
```

## Upload Verification

For each uploaded top-level folder, verify:

1. Google Drive shows the uploaded folder or file.
2. The visible file size roughly matches the local size.
3. One representative file opens or downloads correctly.
4. Do not delete local files until this verification is done.

