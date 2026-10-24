"""Prepare/test a nano-compatible TEL formatter; never edit firmware sources."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import test_encoder_count_candidate as review
from encoder_count_candidate import CORE

HELPER = r'''/* int64 needs at most 20 decimal characters, including its sign. */
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

'''


def replacement(source):
    start = source.index('static void send_tel(void)')
    end = source.index('\nstatic const char *parse_error_code(', start)
    old = source[start:end].rstrip()
    assert 'i64_to_decimal' not in source, 'Already entered: use saved-source review instead'
    new = old.replace('    uart_sendf("TEL,', '''    char left_count[21];
    char right_count[21];
    i64_to_decimal(s_encoder_sample.left_count, left_count);
    i64_to_decimal(s_encoder_sample.right_count, right_count);

    uart_sendf("TEL,''', 1)
    new = new.replace('"left_count=%" PRId64 ",right_count=%" PRId64 ","',
                      '"left_count=%s,right_count=%s,"')
    new = new.replace('                s_encoder_sample.left_count,', '                left_count,')
    new = new.replace('                s_encoder_sample.right_count,', '                right_count,')
    assert new != old and 'PRId64' not in new
    block = HELPER + new
    return source[:start] + block + '\n' + source[end:], block


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--guide', type=Path)
    parser.add_argument('--saved', action='store_true')
    args = parser.parse_args()
    path = CORE / 'Src/uart_mvp_protocol.c'
    before = path.read_bytes()
    source = before.decode('utf-8')
    if args.saved:
        candidate = source
        helper_start = source.index('static void i64_to_decimal(')
        helper_end = source.index('static void send_tel(void)', helper_start)
        helper = source[helper_start:helper_end]
        block = source[helper_start:source.index('\nstatic const char *parse_error_code(', helper_end)]
        assert '"left_count=%s,right_count=%s,"' in block
        assert 'PRId64' not in block
    else:
        assert args.guide, '--guide required for candidate input instructions'
        candidate, block = replacement(source)
        helper = HELPER
    vectors = [(0, '0'), (1, '1'), (-1, '-1'),
        (2147483648, '2147483648'), (-2147483649, '-2147483649'),
        (9007199254740993, '9007199254740993'),
        (-9007199254740993, '-9007199254740993'),
        (9223372036854775807, '9223372036854775807'),
        (-9223372036854775808, '-9223372036854775808')]
    tests = '\n'.join('check(%s, "%s");' %
        ('INT64_MIN' if n == -(1 << 63) else f'INT64_C({n})', expected)
        for n, expected in vectors)
    fixture = '''#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>
''' + helper + '''
static void check(int64_t n, const char *expected) {
    struct { char before; char text[21]; char after; } b;
    memset(&b, 0x5a, sizeof(b));
    i64_to_decimal(n, b.text);
    assert(strcmp(b.text, expected) == 0);
    assert(b.before == 0x5a && b.after == 0x5a);
}
int main(void) {
''' + tests + '\nreturn 0;\n}\n'
    with tempfile.TemporaryDirectory(prefix='encoder-nano-') as tmp:
        work = Path(tmp)
        (work / 'test.c').write_text(fixture, encoding='utf-8')
        subprocess.run([args.cc, '-Wall', '-Werror', str(work / 'test.c'),
                        '-o', str(work / 'test.exe')], check=True, capture_output=True)
        subprocess.run([str(work / 'test.exe')], check=True, capture_output=True)
    review.prepare = lambda: {path: candidate}
    sys.argv = [sys.argv[0], '--cc', args.cc, '--output', str(args.output)]
    if args.saved:
        sys.argv.append('--saved')
    review.main()
    report = json.loads(args.output.read_text(encoding='utf-8'))
    report.update(formatter_vectors=len(vectors), formatter_guard_bytes='PASS',
        target_runtime='PENDING: native PC only; no STM build or flash',
        nano_compatibility='Count formatting uses manual decimal conversion and %s; no long-long printf')
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if args.saved:
        assert path.read_bytes() == before
        print(f'PASS SAVED: {len(vectors)} actual formatter vectors/guards and STM native regression; firmware unchanged')
        return
    args.guide.parent.mkdir(parents=True, exist_ok=True)
    args.guide.write_text('''# STM 누적 count 출력 수정 — 2026-10-20

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
''' + block + '''
```

입력 후 저장본 재검토가 먼저다. 사용자 STM build/flash 이후 실제 ESP monitor에서
count가 십진 숫자로 수신되고 `STM TEL #`로 수락되며 `STM TEL rejected`가
해소되는지 확인해야 target PASS다. 현재 ESTOP_ACTIVE는 유지하고 ARM/주행은 진행하지 않는다.
이 수정으로 ESP를 다시 수정/플래시할 필요는 없다.
''', encoding='utf-8')
    assert path.read_bytes() == before
    print(f'PASS: {len(vectors)} formatter vectors/guards and existing STM native regression; firmware unchanged')


if __name__ == '__main__':
    main()
