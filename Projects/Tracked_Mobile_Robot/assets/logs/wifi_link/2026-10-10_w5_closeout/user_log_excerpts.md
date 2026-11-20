# 사용자 serial 로그 선택 발췌

출처: 이번 W5 대화에 사용자가 붙여 넣은 로그. 전체 serial 원본이나 시간 연속 기록이 아니다. 각 묶음의 `(숫자)`는 ESP uptime(ms)이며 벽시각/날짜가 아니다.

## W5-02, W5-04, W5-11 — 초기 UART 명령 경로

```text
I (367625) wifi_link: W5 QUEUED: DISARM request=2 session=2
I (367635) wifi_link: W5 TX UART1: DISARM,seq=3993059313 request=2 session=2
I (367655) wifi_link: W5 RX MATCH: seq=3993059313 t_ms=22918658
I (367655) wifi_link: W5 RESULT: request=2 session=2 seq=3993059313 status=OK
I (729615) wifi_link: W5 QUEUED: PING request=3 session=2
I (729615) wifi_link: W5 TX UART1: PING,seq=3993059314 request=3 session=2
W (729615) wifi_link: WS rejected: RATE_LIMIT request=4
I (729645) wifi_link: W5 RX MATCH: seq=3993059314 t_ms=23281326
I (729645) wifi_link: W5 RESULT: request=3 session=2 seq=3993059314 status=OK
I (3829235) wifi_link: W5 QUEUED: PING request=1 session=5
I (3829245) wifi_link: W5 TX UART1: PING,seq=3993059319 request=1 session=5
I (3829485) wifi_link: W5 RESULT: request=1 session=5 seq=3993059319 status=CONNECTION_CLOSED
I (3829575) wifi_link: W5 QUEUED: PING request=11 session=3
I (3829585) wifi_link: W5 TX UART1: PING,seq=3993059320 request=11 session=3
I (3830085) wifi_link: W5 RESULT: request=11 session=3 seq=3993059320 status=TIMEOUT
```

W5-11은 순차 정리 관측이다. 마지막 정리와 새 요청 사이90ms가 있어 실제 동시 경합 증거로 쓰지 않는다.

## W5-14, W5-15 — 결과 표시와 요청자 분리

```text
I (526956) wifi_link: STM TEL #5273 t_ms=6819400 state=FAULT reason=ESTOP_ACTIVE pwm=0/0 cps=0/0 drop=0 err=0
W (527206) wifi_link: STM RX invalid line; discard until LF
I (532646) wifi_link: W5 QUEUED: PING request=3 session=1
I (532666) wifi_link: W5 TX UART1: PING,seq=3777917591 request=3 session=1
I (533166) wifi_link: W5 RESULT: request=3 session=1 seq=3777917591 status=TIMEOUT
I (659146) wifi_link: W5 QUEUED: PING request=1 session=2
I (659166) wifi_link: W5 TX UART1: PING,seq=3777917592 request=1 session=2
I (659176) wifi_link: W5 RX MATCH: seq=3777917592 t_ms=113498
I (659176) wifi_link: W5 RESULT: request=1 session=2 seq=3777917592 status=OK
```

## W5-17, W5-18 — PING/DISARM 버튼

```text
I (100347) wifi_link: STM TEL #999 t_ms=4953300 state=FAULT reason=ESTOP_ACTIVE pwm=0/0 cps=0/0 drop=0 err=0
I (100407) wifi_link: W5 QUEUED: PING request=1 session=1
I (100427) wifi_link: W5 TX UART1: PING,seq=3438979494 request=1 session=1
I (100437) wifi_link: STM TEL #1000 t_ms=4953400 state=FAULT reason=ESTOP_ACTIVE pwm=0/0 cps=0/0 drop=0 err=0
I (100457) wifi_link: W5 RX MATCH: seq=3438979494 t_ms=4953416
I (100457) wifi_link: W5 RESULT: request=1 session=1 seq=3438979494 status=OK
I (100547) wifi_link: STM TEL #1001 t_ms=4953500 state=FAULT reason=ESTOP_ACTIVE pwm=0/0 cps=0/0 drop=0 err=0
I (159957) wifi_link: STM TEL #1596 t_ms=5013000 state=FAULT reason=ESTOP_ACTIVE pwm=0/0 cps=0/0 drop=0 err=0
I (159957) wifi_link: W5 QUEUED: DISARM request=2 session=1
I (159977) wifi_link: W5 TX UART1: DISARM,seq=3438979495 request=2 session=1
I (159997) wifi_link: W5 RX MATCH: seq=3438979495 t_ms=5013052
I (159997) wifi_link: W5 RESULT: request=2 session=1 seq=3438979495 status=OK
I (160057) wifi_link: STM TEL #1597 t_ms=5013100 state=FAULT reason=ESTOP_ACTIVE pwm=0/0 cps=0/0 drop=0 err=0
```

## W5-19~21 — 거부 안내

```text
W (326197) wifi_link: WS rejected: DUPLICATE request=2
W (427567) wifi_link: W5 rejected: BAD_FORMAT
W (507447) wifi_link: W5 rejected: BOOT_MISMATCH request=3
```

해당 발췌만으로 전후 전체 TX 부재를 증명하지 않는다. parser/거부 경로와 화면 전사를 함께 따른다.

## W5-22 — STM RESET 유지 중 요청4 timeout

```text
I (966977) wifi_link: STM TEL #9679 t_ms=5821300 state=FAULT reason=ESTOP_ACTIVE pwm=0/0 cps=0/0 drop=0 err=0
W (967157) wifi_link: STM RX invalid line; discard until LF
I (968827) wifi_link: W5 QUEUED: PING request=4 session=1
I (968837) wifi_link: W5 TX UART1: PING,seq=3438979496 request=4 session=1
W (969177) wifi_link: STM RX invalid line; discard until LF
I (969347) wifi_link: W5 RESULT: request=4 session=1 seq=3438979496 status=TIMEOUT
I (969407) wifi_link: STM TEL #9680 t_ms=200 state=FAULT reason=ESTOP_ACTIVE pwm=0/0 cps=0/0 drop=0 err=0
```

510ms는 로그 송신~완료 간격이며500ms 한계 후 태스크가 처리한 관측이다. 무선/전력 차단 실시간 보장이 아니다. 요청5는 이 TIMEOUT 이후 별도 수동 클릭이라는 사용자 정정이 있다. 요청5/6/재접속 후1의 TX/MATCH 원문은 제공되지 않았다.
