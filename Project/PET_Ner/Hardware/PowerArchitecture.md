# ⚡ Power Architecture

본 로봇은 3S LiPo 배터리를 메인 전원으로 사용하며, **6-hole FuseHub**를 통해 각 컴포넌트에 독립적인 전원을 공급합니다.

## 🔋 전원 분배 구조
![Power Distribution](./images/전원_분배.drawio.png)

1. **Main Rail (12V Direct)**
   - Jetson Orin Nano
   - MDD10A 모터 드라이버 (2개)
   - LTC3780 Buck-Boost (로봇 팔용 12V 승강압)
2. **Step-Down Rail**
   - **5.1V (XL4016):** Raspberry Pi 5 전용
   - **5.0V (XL4015):** STM32 전원
   - **3.3V (Voltage Divider):** STM32 로직 기준 전압
3. **Charging System**
   - PD 충전기 → PD 트리거 → XL4015 → 숏키 다이오드 → BMS 경로로 충전 진행

## 🛡️ 안전 대책
- **Main Fuse Holder:** 배터리 직후 위치하여 전체 시스템 과전류 차단
- **Schottky Diode:** 충전 및 외부 전원 투입 시 역전류 방지
- **BMS (60C):** 셀 밸런싱 및 배터리 과방전 방지