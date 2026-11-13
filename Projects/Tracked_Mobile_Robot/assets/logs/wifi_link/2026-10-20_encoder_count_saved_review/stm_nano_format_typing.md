# STM 누적 count 출력 수정 — 2026-10-20

상태: 후보 PC 검사 PASS, 사용자 입력/STM build/flash/실제 TEL 확인 대기.

`Core/Src/uart_mvp_protocol.c`의 `static void send_tel(void)` 정의부터
그 함수의 닫는 `}`까지를 아래 전체 블록으로 교체한다.
다음 `static const char *parse_error_code(...)`는 교체 범위에 포함하지 않는다.

원인: STM Debug는 nano.specs/libc_nano를 사용한다. 실제 wire에서
`left_count=ld,right_count=ld`가 나와 ESP가 거부했다. PC printf PASS는
target libc 지원을 보장하지 못했다. ESP parser를 완화하지 않는다.

흐름: int64 누적값 → 고정 21-byte 문자열 → 기존 uart_sendf의 %s → 기존 TEL.
최소값은 value+1을 먼저 부호 반전해 signed overflow를 피한다.
최대 19자리 magnitude/부호/NUL이 들어간다. 동적 할당은 없다.
샘플/ARM flag, 상태/출력/timeout/정지 경로와 512-byte buffer는 유지한다.
전체 newlib 전환보다 변경 범위가 작으며 32비트 축소에 따른 손실도 없다.

```c
/* int64 needs at most 20 decimal characters, including its sign. */
static void i64_to_decimal(int64_t value, char out[21])
{
    char reversed[20];
    unsigned int digits = 0U;
    unsigned int pos = 0U;
    const bool negative = value < 0;
    uint64_t magnitude = negative
        ? (uint64_t)(-(value + 1)) + 1U
        : (uint64_t)value;

    do {
        reversed[digits++] = (char)('0' + magnitude % 10U);
        magnitude /= 10U;
    } while (magnitude != 0U);

    if (negative) {
        out[pos++] = '-';
    }
    while (digits != 0U) {
        out[pos++] = reversed[--digits];
    }
    out[pos] = '\0';
}

static void send_tel(void){
    uint32_t now_ms = HAL_GetTick();
    motor_output_applied_t applied =
        motor_output_get_applied();

    char left_count[21];
    char right_count[21];
    i64_to_decimal(s_encoder_sample.left_count, left_count);
    i64_to_decimal(s_encoder_sample.right_count, right_count);

    uart_sendf("TEL,t_ms=%lu,state=%s,reason=%s,"
               "command_age_ms=%lu,last_seq=%lu,"
               "vx_mmps=%ld,w_mradps=%ld,"
               "left_pwm=%ld,right_pwm=%ld,"
               "left_cps=%ld,right_cps=%ld,"
               "encoder_valid=%u,encoder_t_ms=%lu,"
               "left_count=%s,right_count=%s,"
               "encoder_arm_valid=%u,encoder_arm_seq=%lu,"
               "batt_mv=0,drop=%lu,err=%lu\n",
                (unsigned long)now_ms,
                state_name(s_state),
                reason_name(s_reason),
                (unsigned long)command_age_ms(now_ms),
                (unsigned long)s_last_seq,
                (long)s_vx_mmps,
                (long)s_w_mradps,
                (long)applied.left_signed_permille,
                (long)applied.right_signed_permille,
                (long)s_left_cps,
                (long)s_right_cps,
                s_encoder_sample.valid ? 1U : 0U,
                (unsigned long)s_encoder_sample.sample_ms,
                left_count,
                right_count,
                s_encoder_sample.arm_valid ? 1U : 0U,
                (unsigned long)s_encoder_sample.arm_seq,
                (unsigned long)ring_buffer_dropped(&s_rx_rb),
                (unsigned long)s_error_count);
}
```

입력 후 저장본 재검토가 먼저다. 사용자 STM build/flash 이후 실제 ESP monitor에서
count가 십진 숫자로 수신되고 `STM TEL #`로 수락되며 `STM TEL rejected`가
해소되는지 확인해야 target PASS다. 현재 ESTOP_ACTIVE는 유지하고 ARM/주행은 진행하지 않는다.
이 수정으로 ESP를 다시 수정/플래시할 필요는 없다.
