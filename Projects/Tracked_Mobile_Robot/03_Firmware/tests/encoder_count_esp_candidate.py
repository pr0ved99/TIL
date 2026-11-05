"""ESP typing candidate only; production firmware is never edited here."""
from pathlib import Path
import json
import re
from test_wifi_w5_uart_contract import c_type

ESP = Path(__file__).resolve().parent.parent / 'esp32_wifi_link/main/wifi_link_main.c'


def c_function(source, name):
    """Exact source range; these functions close at column zero."""
    definitions = list(re.finditer(r'^static[^\n]*\b'+name+r'\s*\([^;{}]*\)\s*\{', source, re.M))
    if len(definitions) != 1:
        raise ValueError('Expected one function definition: '+name)
    start = definitions[0]
    end = re.search(r'^}', source[start.end():], re.M)
    if end is None:
        raise ValueError('Function close missing: '+name)
    return source[start.start():start.end()+end.end()]+'\n'

I64_PARSER = r'''static bool stm_parse_i64_field(
    const char *line, const char *key, int64_t *out)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL) {
        return false;
    }

    const bool negative = *pos == '-';
    if (negative) {
        ++pos;
    }
    if (*pos < '0' || *pos > '9') {
        return false;
    }

    const uint64_t limit = negative
        ? (uint64_t)INT64_MAX + 1U : (uint64_t)INT64_MAX;
    uint64_t magnitude = 0U;
    while (*pos >= '0' && *pos <= '9') {
        const uint64_t digit = (uint64_t)(*pos - '0');
        if (magnitude > (limit - digit) / 10U) {
            return false;
        }
        magnitude = magnitude * 10U + digit;
        ++pos;
    }
    if (*pos != ',' && *pos != '\0') {
        return false;
    }

    *out = negative
        ? (magnitude == (uint64_t)INT64_MAX + 1U
            ? INT64_MIN : -(int64_t)magnitude)
        : (int64_t)magnitude;
    return true;
}'''

VALID_STATUS = r'''function validStatus(s){
 const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;
 const i32=v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647;
 const ms=v=>Number.isSafeInteger(v)&&v>=0;
 const i64text=v=>{
  if(typeof v!=='string'||! /^-?(0|[1-9][0-9]{0,18})$/.test(v)||v==='-0')return false;
  const negative=v[0]==='-', digits=negative?v.slice(1):v;
  const limit=negative?'9223372036854775808':'9223372036854775807';
  return digits.length<limit.length||(digits.length===limit.length&&digits<=limit);
 };
 if(!s||typeof s!=='object'||Array.isArray(s)||
  !['ESP_ONLY','STM_UART'].includes(s.source)||!['AP','STA'].includes(s.mode)||
  !['SETTLE','SYNC_WAIT','WAIT_DISARM_ACK','WAIT_PONG','READY','FAILED'].includes(s.startup_state)||
  !u32(s.boot_id)||!ms(s.uptime_ms)||!u32(s.free_heap_bytes)||!u32(s.tel_count)||
  !u32(s.stm_age_limit_ms)||s.stm_age_limit_ms===0||
  typeof s.stm_connected!=='boolean'||typeof s.stm_stale!=='boolean'||
  s.batt_mv!==null||s.battery_available!==false)return false;
 if(s.source==='ESP_ONLY'){
  return !s.stm_connected&&!s.stm_stale&&s.stm_age_ms===null&&s.tel_count===0&&
   ['stm_t_ms','state','reason','command_age_ms','last_seq','vx_mmps','w_mradps',
    'left_pwm','right_pwm','left_cps','right_cps','drop','err',
    'encoder_valid','encoder_t_ms','left_count','right_count',
    'encoder_arm_valid','encoder_arm_seq'].every(k=>s[k]===null);
 }
 return ms(s.stm_age_ms)&&s.stm_connected===(s.stm_age_ms<=s.stm_age_limit_ms)&&
  s.stm_stale===!s.stm_connected&&u32(s.stm_t_ms)&&
  ['DISARMED','ARMED','FAULT'].includes(s.state)&&
  typeof s.reason==='string'&&/^[A-Z0-9_]{1,31}$/.test(s.reason)&&
  ['command_age_ms','last_seq','drop','err'].every(k=>u32(s[k]))&&
  ['vx_mmps','w_mradps','left_pwm','right_pwm','left_cps','right_cps'].every(k=>i32(s[k]))&&
  Math.abs(s.left_pwm)<=1000&&Math.abs(s.right_pwm)<=1000&&
  typeof s.encoder_valid==='boolean'&&typeof s.encoder_arm_valid==='boolean'&&
  u32(s.encoder_t_ms)&&u32(s.encoder_arm_seq)&&i64text(s.left_count)&&i64text(s.right_count);
}'''


def changes(source):
    old_type = c_type(source, 'stm_telemetry_t')
    new_type = old_type.replace('    uint32_t batt_mv;', '''    bool encoder_valid;
    uint32_t encoder_t_ms;
    int64_t left_count;
    int64_t right_count;
    bool encoder_arm_valid;
    uint32_t encoder_arm_seq;
    uint32_t batt_mv;''')
    old_tel = c_function(source, 'stm_parse_tel').rstrip()
    new_tel = old_tel.replace('현재 TEL 계약은 14개 필드다.', '확장 TEL 계약은 20개 필드다.')
    new_tel = new_tel.replace('field_count != 14U', 'field_count != 20U')
    new_tel = new_tel.replace('    const bool fields_ok =', '''    uint32_t encoder_valid;
    uint32_t encoder_arm_valid;
    const bool fields_ok =''')
    new_tel = new_tel.replace('        stm_parse_u32_field(line, "batt_mv=", &out->batt_mv) &&', '''        stm_parse_u32_field(line, "encoder_valid=", &encoder_valid) &&
        stm_parse_u32_field(line, "encoder_t_ms=", &out->encoder_t_ms) &&
        stm_parse_i64_field(line, "left_count=", &out->left_count) &&
        stm_parse_i64_field(line, "right_count=", &out->right_count) &&
        stm_parse_u32_field(line, "encoder_arm_valid=", &encoder_arm_valid) &&
        stm_parse_u32_field(line, "encoder_arm_seq=", &out->encoder_arm_seq) &&
        stm_parse_u32_field(line, "batt_mv=", &out->batt_mv) &&''')
    new_tel = new_tel.replace('    if (!fields_ok) {', '    if (!fields_ok || encoder_valid > 1U || encoder_arm_valid > 1U) {')
    new_tel = new_tel.replace('    const bool state_ok =', '''    out->encoder_valid = encoder_valid != 0U;
    out->encoder_arm_valid = encoder_arm_valid != 0U;

    const bool state_ok =''')
    old_status = c_function(source, 'status_json').rstrip()
    new_status = old_status.replace('            "\\"batt_mv\\":null,\\"battery_available\\":false,"',
        '            "\\"encoder_valid\\":null,\\"encoder_t_ms\\":null,"\n'
        '            "\\"left_count\\":null,\\"right_count\\":null,"\n'
        '            "\\"encoder_arm_valid\\":null,\\"encoder_arm_seq\\":null,"\n'
        '            "\\"batt_mv\\":null,\\"battery_available\\":false,"', 1)
    # The remaining battery line is in the STM_UART branch.
    marker='            "\\"left_cps\\":%" PRIi32 ",\\"right_cps\\":%" PRIi32 ","'
    new_status = new_status.replace(marker, marker+'\n'
        '            "\\"encoder_valid\\":%s,\\"encoder_t_ms\\":%" PRIu32 ","\n'
        '            "\\"left_count\\":\\"%" PRId64 "\\",\\"right_count\\":\\"%" PRId64 "\\","\n'
        '            "\\"encoder_arm_valid\\":%s,\\"encoder_arm_seq\\":%" PRIu32 ","')
    new_status = new_status.replace('            tel.left_cps, tel.right_cps, tel.drop, tel.err);', '''            tel.left_cps, tel.right_cps,
            tel.encoder_valid ? "true" : "false", tel.encoder_t_ms,
            tel.left_count, tel.right_count,
            tel.encoder_arm_valid ? "true" : "false", tel.encoder_arm_seq,
            tel.drop, tel.err);''')
    old_js = next(line for line in source.splitlines() if line.startswith('    "function validStatus(s){'))
    new_js = '\n'.join('    '+json.dumps(line+'\n',ensure_ascii=False) for line in VALID_STATUS.splitlines())
    text_function = c_function(source, 'stm_parse_text_field').rstrip()
    return [
        ('1. stm_telemetry_t typedef 전체',old_type,new_type),
        ('2. STM_UART_LINE_SIZE 정의 한 줄','#define STM_UART_LINE_SIZE 384U','#define STM_UART_LINE_SIZE 512U'),
        ('3. 기존 stm_parse_text_field 함수 전체를 아래 두 함수로 교체',text_function,I64_PARSER+'\n\n'+text_function),
        ('4. stm_parse_tel 함수 전체',old_tel,new_tel),
        ('5. status_json 함수 전체',old_status,new_status),
        ('6. PAGE의 validStatus 한 줄을 아래 C 문자열 블록으로 교체',old_js,new_js),
    ]


def prepare(source=None):
    source=ESP.read_text(encoding='utf-8') if source is None else source
    for label,old,new in changes(source):
        # c_function extraction normalizes only the first/last body newlines.
        if source.count(old)!=1 or old==new:
            raise ValueError('Replacement anchor changed: '+label)
        source=source.replace(old,new,1)
    return source


def guide():
    source=ESP.read_text(encoding='utf-8')
    lines=['### ESP 누적 count 입력 묶음 — 2026-10-20','',
        '상태: **후보 준비 / 사용자 입력 대기**. 대상은 `03_Firmware/esp32_wifi_link/main/wifi_link_main.c` 한 파일이다. 아래6개 블록을 순서대로 입력한다. STM은 사용자가 build/Run 성공을 보고했고 실제 저장본 native14 PASS다. ESP 저장본과 실제20필드 수신은 아직 확인 전이다.','',
        '- 데이터 흐름: STM TEL20필드 → 범위/중복/flag 검사 → lock 안의 snapshot → JSON → PAGE 검증/표시. count는 UART에서 int64, JSON/관찰 로그에서10진 문자열을 유지한다.',
        '- 정상 초기 flag=false는 TEL 형식 오류가 아니다. ARM/정지의 기존 CPS/PWM/ticket/ACK·freshness 조건과 모터 제한은 그대로다.',
        '- 잘못된 key/범위/flag/중복 또는14필드 TEL은 거부하며 마지막 정상 snapshot을 유지한다. 기존 TEL age에 따라 제어가 정지한다. flag가 false라는 이유만으로 정상 TEL을 거부하지 않는다.',
        '- 원시 count/ARM seq가 같은 snapshot으로 브라우저에 전달된다. 거리 창의 시작/끝·reset/단절 구분은 앞의 계약을 따르며 이 입력 묶음은 자동 거리 보정이나 주행을 추가하지 않는다.',
        '- 입력·저장 후 Codex가 실제 ESP 저장본을 검사한다. 그 검사가 끝난 뒤 사용자가 ESP build/flash/Run을 수행하며 새 동작 시험은 별도 안내한다.','']
    for label,old,new in changes(source):
        lines += ['**'+label+'**','', '기존 블록 시작: `'+old.splitlines()[0]+'`. 함수/typedef는 끝까지 교체한다.','', '```c',new,'```','']
    return '\n'.join(lines)
