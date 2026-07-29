# 2026-07-30 Encoder Output-Shaft Calibration and mRPM Verification

## Scope

이 기록은 다음 두 시험을 구분해서 보존한다.

1. 작업자가 출력축을 방향별 50회전시켜 측정한 `counts/output rev` 보정
2. 보정 상수 `1560 counts/output rev`를 사용한 STM32 CPS -> mRPM 변환과 dual-encoder 수동 회전 로그 검증

50회전 총 count는 작업자가 별도로 읽어 보고한 값이며, 아래 동적 raw log 안에
포함된 값이 아니다. 두 시험을 하나의 원본 로그가 모두 증명하는 것으로 해석하지
않는다.

50회전 작업자 관찰 기록:

- Record: [`2026-07-30_50rev_output_shaft_calibration_operator_record.txt`](2026-07-30_50rev_output_shaft_calibration_operator_record.txt)
- SHA-256: `CDCED10359EEB8D9B84BA9660A6772E4849A22C59005EC3D575139C0C4577377`
- Evidence class: `OPERATOR_REPORTED_BENCH_OBSERVATION`
- Raw serial capture: `NO`

## 1. 50-Revolution Output-Shaft Calibration

기준 방향은 출력축 끝을 정면으로 바라본 시계/반시계 방향이다. 반시계 측정값은
계산을 위해 절댓값으로 표기하며 실제 count sign은 음수였다.

| Bench motor | Direction | Revolutions | Observed absolute count | Counts/output rev |
| --- | --- | ---: | ---: | ---: |
| A | Clockwise | 50 | 77,998 | 1559.96 |
| A | Counter-clockwise | 50 | 78,001 | 1560.02 |
| B | Clockwise | 50 | 78,000 | 1560.00 |
| B | Counter-clockwise | 50 | 78,000 | 1560.00 |

Motor A 방향 평균은 `1559.99`, motor B 방향 평균은 `1560.00`이다. 현재 STM32
quadrature x4 decoding과 출력축 기준 변환 상수는 다음으로 확정한다.

```text
ENCODER_COUNTS_PER_OUTPUT_REV = 1560
```

이 값은 현재 motor, gearbox, encoder decoding과 bench wiring을 합친 출력축 실측
상수다. Encoder 자체 datasheet PPR이나 gearbox ratio를 개별적으로 측정한 값은
아니다.

Decision: `50-REV OUTPUT-SHAFT CALIBRATION PASS`

## 2. CPS to mRPM Implementation

Firmware conversion:

```text
mRPM = trunc(CPS * 60000 / 1560)
```

- Signed CPS의 방향 부호를 유지한다.
- `counts_per_revolution == 0`, null output pointer와 `int32_t` mRPM 범위 초과를
  거부한다.
- Boot self-test는 `0`, `+/-780`, `+/-1560 CPS`, invalid CPR, null pointer와
  `INT64_MAX/MIN` 입력을 포함한다.
- 확인된 boot line은 `ENC_SELF_TEST,wrap=PASS,millirpm=PASS`다.
- mRPM은 현재 USART2 bench diagnostic log에만 추가했다. STM32 -> ESP32 production
  `TEL` 계약은 기존 `left_cps/right_cps`를 유지한다.
- 현재 nominal 100 ms sample에서 1 count/sample은 10 CPS, 약 384 mRPM에
  해당한다. CPS를 먼저 정수화하므로 이 값은 현재 저속 mRPM 표시의 양자화
  간격이며, 향후 저속 폐루프 제어에서는 elapsed time과 delta에서 직접 계산하는
  방법을 재검토한다.

## 3. Dynamic Hand-Rotation Log Audit

Evidence:

- Raw log: [`2026-07-30_dual_encoder_millirpm_hand_rotation_pass.txt`](2026-07-30_dual_encoder_millirpm_hand_rotation_pass.txt)
- SHA-256: `D16925EE4331B04726AB54BBBF1640DF72D852684E87B0EFD6C1B46C3AF1636B`
- File size: `37,229 bytes`
- Physical lines: `306` (`1` self-test line + `305` complete dual-channel rows)
- Nominal firmware sample interval: `100 ms`

Automated parse result:

| Check | Result |
| --- | ---: |
| Complete dual-channel rows | 305 |
| Channel samples | 610 |
| Malformed/truncated rows | 0 |
| `mRPM == trunc(CPS * 60000 / 1560)` mismatch | 0 / 610 |
| `CPS == delta * 10` mismatch | 0 / 610 |
| Raw-to-delta continuity mismatch | 0 / 608 transitions |
| CPS sign-to-direction mismatch | 0 |
| Simultaneously active dual-channel rows | 0 |

| Channel | Positive / negative / zero rows | CPS range | mRPM range |
| --- | ---: | ---: | ---: |
| ENC3 / TIM3 | 47 / 47 / 211 | -2380 .. +2850 | -91538 .. +109615 |
| ENC5 / TIM5 | 84 / 51 / 170 | -1710 .. +2750 | -65769 .. +105769 |

마지막 26개 dual-channel row에서 양쪽 모두 `delta=0`, `cps=0`, `mrpm=0`으로
복귀했다. 한 channel이 회전하는 row에서 다른 channel은 0이었으므로 독립 수동
회전 조건도 유지됐다.

Decision: `DUAL HAND-ROTATION CPS -> mRPM FUNCTIONAL PASS`

## Combined Decision

```text
PASS
- 50회전 출력축 보정 상수: 1560 counts/output rev
- signed CPS -> mRPM 산술 변환
- boot self-test, 정지 0, 양방향 부호, dual-channel 독립성과 stop-to-zero

PARTIAL remains
- powered-motor encoder noise와 input filtering
- 실제 차량 left/right와 forward-positive sign
- 외부 tachometer 기준 physical RPM 정확도
- wheel mm/s, odometry와 closed-loop speed control
```

Raw log에는 timestamp/sequence와 전원·motor 구동 상태가 없으므로 실제 sample
period나 frame drop을 독립적으로 증명하지 않는다. 동적 구간에서 counter wrap은
발생하지 않았으며 header의 `wrap=PASS`는 synthetic self-test 결과다. 현재 짧은
bench log의 `(long)`/`%ld` 표시는 범위 안이지만 내부 누적 count는 계속
`int64_t`로 유지한다.
