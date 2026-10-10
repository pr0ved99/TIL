# Motor Output Verification Records

STM32/MDD10A 출력 시험의 작업자 관찰·계측 기록과 실제 단일 모터 구동 로그를 보관한다.

| Date | File | Result |
| --- | --- | --- |
| 2026-09-28~29 | [단일 모터 시험 원본12개](2026-09-29_single_motor_bench/README.md) | 교차시험, 오른쪽 DIR 보정 후 B 양방향10%/300ms 회전·timeout·CPS0 복귀 |
| 2026-07-30 | [`2026-07-30_fault_injection_output_zero_latch_verification.md`](2026-07-30_fault_injection_output_zero_latch_verification.md) | Software fault injection 뒤 MDD10A LED all-off, PB6/PB7/PC8/PC9 0 V, reset 전 재활성화 차단 및 기본 설정 복귀 PASS |

7/30 작업자 관찰 문서는 raw serial/oscilloscope capture가 아니다. 9/29 폴더는 첨부 원본 serial 로그와 해시·요약을 포함한다.
각 문서의 시험 범위와 미검증 항목을 함께 확인한다.
