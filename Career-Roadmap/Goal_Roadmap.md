# 🚀 기술 자립 로드맵 (Technical Independence Roadmap)

> **"AI 의존도를 낮추고 데이터시트 기반의 분석 능력을 확보하여, 시스템의 근본을 이해하는 로봇 엔지니어로 성장한다."**

## 🎯 최종 목표
- STM32 Reference Manual을 독자적으로 해석하고 하드웨어를 제어할 수 있는 역량 확보
- AI가 생성한 코드의 동작 원리를 레지스터 수준에서 검증할 수 있는 능력 배양
- 'Office-Guardian' 프로젝트에 최적화된 저수준 제어 시스템 도입

---

## 📅 단계별 실행 계획

### 🚩 Phase 1: 시스템의 심장과 뇌 이해하기 (Architecture)
- **핵심 과제**: Clock Tree 구조 파악, PLL 계산, Interrupt(NVIC) 메커니즘 이해
- **실습 목표**: CubeMX 자동 생성 코드 없이 클럭 설정 및 시스템 초기화 구현
- **검증**: `Phase1_Clock_Tree_Analysis.md` 작성 및 시뮬레이션 성공

### 🚩 Phase 2: 로봇의 신경과 근육 통제하기 (Peripherals)
- **핵심 과제**: GPIO, PWM, ADC, Timer의 레지스터 직접 제어
- **실습 목표**: HAL 라이브러리 최소화, LL(Low-Layer) 라이브러리 혹은 레지스터 직접 접근으로 모터 및 센서 제어
- **검증**: 데이터시트의 타이밍 차트에 맞춘 신호 생성 확인

### 🚩 Phase 3: 소통의 언어 마스터하기 (Connectivity)
- **핵심 과제**: UART, I2C, SPI, CAN 통신의 프로토콜 레벨 이해
- **실습 목표**: 센서 데이터시트를 보고 통신 드라이버 직접 작성 및 로직 분석기 검증
- **검증**: 장치 간 데이터 송수신 신뢰성 수치화

### 🚩 Phase 4: 실전 융합 및 최적화 (Synthesis & Optimization)
- **핵심 과제**: RTOS 기반 멀티태스킹, Jetson Orin과의 고속 데이터 동기화
- **실습 목표**: Office-Guardian 로봇에 최적화된 펌웨어 아키텍처 적용
- **검증**: 기존 시스템 대비 반응 속도 및 인식률 향상 데이터 기록

---

## 🛠️ 학습 원칙 (Definition of Done)
1. **Source First**: AI에게 묻기 전, 반드시 Reference Manual의 관련 섹션을 먼저 읽는다.
2. **Why, not How**: 코드가 '어떻게' 돌아가는지가 아니라 '왜' 그렇게 설정해야 하는지를 기록한다.
3. **Weekly Review**: 매주 일요일, 한 주간의 학습 기록을 TIL에 커밋하며 회고한다.