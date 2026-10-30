# 만능기판 엔코더 조정부 납땜 후 ESP 모니터

- [원본](esp32_stationary_monitor.txt): 사용자가 제공한 ESP monitor 전체 텍스트, 84,822 bytes.
- SHA-256: `970c17c2de8722bc579067b23da83e2cb5e411aa3d5d0f69941c6549ee32cb36`.
- [분석 요약](monitor_summary.json): STM t_ms 4200~44100, TEL 400개, 양쪽 CPS 모두 0.
- [검사 보고서](../../../../docs/verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md).

보드 두 개를 장착한 상태의 사용자 로그다. 실제 엔코더 케이블과 임시 빵판 저항 상태는
촬영 시 별도 확인되지 않았다. 저항·커넥터 검사와 +5.05V 측정은 이 로그 이후 사용자 보고다.
첫 4.2초 미포함, err=7 고정 및 초기 RX_DESYNC 1회를 보존한다.
전 구간 FAULT/ESTOP_ACTIVE, PWM 보고값 0이며 실제 PWM 파형이나 S0 조작의 증거는 아니다.
