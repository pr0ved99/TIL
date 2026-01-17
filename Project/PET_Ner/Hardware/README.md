# 🤖 Project PET_Ner Hardware

반려봇의 기구부 설계 및 시스템 통합 정보를 관리합니다.

## 🏗️ Overall Design
![Overall Assembly](./images/mech_assembly_isometric.png)

### 🌟 System Architecture
로봇은 안정적인 주행과 연산을 위해 3층 레이어 구조로 설계되었습니다.
![Exploded View](./images/mech_exploded_view.png)

- **Tier 1 (Bottom):** 97mm 메카넘 휠 구동부 및 고출력 배터리 배치
  ![Tier 1](./images/Tier1_5T.png)
- **Tier 2 (Middle):** STM32 제어기, Raspberry Pi 5, LiDAR 센서 탑재
  ![Tier 2](./images/Tier2_3T.png)
- **Tier 3 (Top):** Jetson Orin Nano 및 비전 센서 배치
  ![Tier 3](./images/Tier3_5T.png)