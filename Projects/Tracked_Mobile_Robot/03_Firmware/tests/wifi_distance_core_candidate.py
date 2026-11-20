"""Prepare ESP distance request/transport changes in memory, never in firmware."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE.parent / 'esp32_wifi_link/main'

POLICY = '''/* Distance is optional: zero means an ordinary CMD, not a zero-length move. */
static inline bool wifi_control_distance_goal_valid(uint32_t distance_mm)
{
    return distance_mm == 50U || distance_mm == 100U ||
        distance_mm == 150U || distance_mm == 200U;
}

/* Value/mode policy only; owner, ticket, phase and time checks are separate. */
static inline bool wifi_control_request_allows(
    const wifi_control_request_t *request)
{
    if (request == NULL) {
        return false;
    }
    const bool is_zero = request->vx_mmps == 0 && request->w_mradps == 0;
    if (request->type == WIFI_CONTROL_ARM) {
        return is_zero && request->distance_mm == 0U;
    }
    if (request->type != WIFI_CONTROL_CMD ||
        request->vx_mmps < WIFI_CONTROL_VX_MIN_MMPS ||
        request->vx_mmps > WIFI_CONTROL_VX_MAX_MMPS ||
        request->w_mradps < WIFI_CONTROL_W_MIN_MRADPS ||
        request->w_mradps > WIFI_CONTROL_W_MAX_MRADPS) {
        return false;
    }
    if (request->distance_mm != 0U &&
        (!wifi_control_distance_goal_valid(request->distance_mm) ||
         request->vx_mmps != 100 || request->w_mradps != 0)) {
        return false;
    }
    return WIFI_CONTROL_ZERO_ONLY == 0U ||
        (is_zero && request->distance_mm == 0U);
}
'''


def prepare():
    candidates, changes = {}, []

    def replace(name, label, old, new):
        path = MAIN / name
        text = candidates.get(path, path.read_text(encoding='utf-8'))
        assert text.count(old) == 1, (name, label, text.count(old))
        candidates[path] = text.replace(old, new, 1)
        changes.append((name, label, old, new))

    replace('wifi_control_contract.h', '요청 구조체의 속도 필드 구간 교체',
            '    int32_t vx_mmps;\n    int32_t w_mradps;\n',
            '    int32_t vx_mmps;\n    int32_t w_mradps;\n'
            '    uint32_t distance_mm; /* 0: ordinary CMD; 50/100/150/200: forward goal. */\n')
    header = (MAIN / 'wifi_control_contract.h').read_text(encoding='utf-8')
    start = header.index('/* Value/mode policy only;')
    end = header.index('\n#endif', start)
    replace('wifi_control_contract.h', '정책 함수 전체 교체와 거리 검사 helper 추가',
            header[start:end], POLICY.rstrip())

    source = (MAIN / 'wifi_control_contract.c').read_text(encoding='utf-8')
    start = source.index('wifi_control_parse_status_t wifi_control_parse(')
    end = source.index('\nbool wifi_control_zero_only_allows(', start)
    old = source[start:end]
    needle = '''            return WIFI_CONTROL_PARSE_BAD_FORMAT;
        }
    }

    if (*cursor != '\\0')'''
    addition = '''            return WIFI_CONTROL_PARSE_BAD_FORMAT;
        }
        if (*cursor != '\\0') {
            if (!control_take_literal(&cursor, ",distance_mm=") ||
                !control_read_u32(&cursor, &parsed.distance_mm) || *cursor != '\\0') {
                return WIFI_CONTROL_PARSE_BAD_FORMAT;
            }
            if (!wifi_control_distance_goal_valid(parsed.distance_mm) ||
                parsed.vx_mmps != 100 || parsed.w_mradps != 0) {
                return WIFI_CONTROL_PARSE_OUT_OF_RANGE;
            }
        }
    }

    if (*cursor != '\\0')'''
    assert old.count(needle) == 1
    replace('wifi_control_contract.c', 'wifi_control_parse 함수 전체 교체',
            old, old.replace(needle, addition))
    start = source.index('bool wifi_control_zero_only_allows(')
    old = source[start:]
    assert old.rstrip().endswith('}')
    new = old.replace('request->vx_mmps == 0 && request->w_mradps == 0;',
                      'request->vx_mmps == 0 && request->w_mradps == 0 &&\n'
                      '        request->distance_mm == 0U;')
    assert old != new
    replace('wifi_control_contract.c', 'wifi_control_zero_only_allows 함수 전체 교체', old, new)

    source = (MAIN / 'wifi_control_executor.c').read_text(encoding='utf-8')
    start = source.index('bool wifi_control_executor_take_tx(')
    end = source.index('\nbool wifi_control_executor_tx_complete(', start)
    old = source[start:end]
    a = old.index('        n = snprintf(tx.bytes, sizeof(tx.bytes),')
    b = old.index('\n    } else {', a)
    ordinary = old[a:b]
    distance = '''        if (e->request.distance_mm != 0U) {
            n = snprintf(tx.bytes, sizeof(tx.bytes),
                "CMD,seq=%" PRIu32 ",vx_mmps=%" PRIi32
                ",w_mradps=%" PRIi32 ",timeout_ms=%" PRIu32
                ",distance_mm=%" PRIu32 "\\n",
                seq, e->request.vx_mmps,
                e->request.w_mradps, (uint32_t)WIFI_CONTROL_STM_TIMEOUT_MS,
                e->request.distance_mm);
        } else {
''' + '\n'.join('    ' + line for line in ordinary.splitlines()) + '\n        }'
    replace('wifi_control_executor.c', 'wifi_control_executor_take_tx 함수 전체 교체',
            old, old[:a] + distance + old[b:])
    return candidates, changes
