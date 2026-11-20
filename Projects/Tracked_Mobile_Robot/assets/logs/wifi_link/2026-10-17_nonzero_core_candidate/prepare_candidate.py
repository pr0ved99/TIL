"""Prepare review copies only. Never write the learning-target firmware."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
MAIN = PROJECT / '03_Firmware/esp32_wifi_link/main'
OUT = HERE / 'source'
OUT.mkdir(exist_ok=True)
names = ('wifi_control_contract.h', 'wifi_control_state.c', 'wifi_control_executor.c')
original = {name: (MAIN / name).read_bytes() for name in names}
if (HERE / 'manifest.json').exists():
    baseline = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    for entry in baseline['files']:
        if hashlib.sha256(original[entry['name']]).hexdigest() != entry['base_sha256']:
            raise SystemExit('Production changed: review the saved files; do not regenerate this candidate.')
units = {name: raw.decode('utf-8').replace('\r\n', '\n') for name, raw in original.items()}


def replace(name, before, after):
    assert units[name].count(before) == 1, (name, before)
    units[name] = units[name].replace(before, after, 1)


replace(names[0], '#define WIFI_CONTROL_ZERO_ONLY 1U', '''#define WIFI_CONTROL_ZERO_ONLY 1U
#if WIFI_CONTROL_ZERO_ONLY != 0U && WIFI_CONTROL_ZERO_ONLY != 1U
#error "WIFI_CONTROL_ZERO_ONLY must be 0 or 1"
#endif
/* Must match the STM production output cap. Not a measured speed limit. */
#define WIFI_CONTROL_PWM_MAX_PERMILLE 100U''')
replace(names[0], '    const wifi_control_request_t *request);\n\n#endif', '''    const wifi_control_request_t *request);

/* Value/mode policy only; owner, ticket, phase and time checks are separate. */
static inline bool wifi_control_request_allows(
    const wifi_control_request_t *request)
{
    if (request == NULL) {
        return false;
    }
    const bool is_zero = request->vx_mmps == 0 && request->w_mradps == 0;
    if (request->type == WIFI_CONTROL_ARM) {
        return is_zero;
    }
    if (request->type != WIFI_CONTROL_CMD ||
        request->vx_mmps < WIFI_CONTROL_VX_MIN_MMPS ||
        request->vx_mmps > WIFI_CONTROL_VX_MAX_MMPS ||
        request->w_mradps < WIFI_CONTROL_W_MIN_MRADPS ||
        request->w_mradps > WIFI_CONTROL_W_MAX_MRADPS) {
        return false;
    }
    return WIFI_CONTROL_ZERO_ONLY == 0U || is_zero;
}

#endif
''')
replace(names[1], 'static bool fresh(', '''/* ACTIVE may carry motion; preparation and stop still require zero. */
static bool active_tel_valid(const wifi_control_tel_t *tel)
{
    const int32_t cap = (int32_t)WIFI_CONTROL_PWM_MAX_PERMILLE;
    return tel->state == WIFI_CONTROL_STM_ARMED &&
        tel->command_age_ms < WIFI_CONTROL_STM_TIMEOUT_MS &&
        tel->vx_mmps >= WIFI_CONTROL_VX_MIN_MMPS &&
        tel->vx_mmps <= WIFI_CONTROL_VX_MAX_MMPS &&
        tel->w_mradps >= WIFI_CONTROL_W_MIN_MRADPS &&
        tel->w_mradps <= WIFI_CONTROL_W_MAX_MRADPS &&
        tel->left_pwm >= -cap && tel->left_pwm <= cap &&
        tel->right_pwm >= -cap && tel->right_pwm <= cap &&
        (WIFI_CONTROL_ZERO_ONLY == 0U || zero(tel)) &&
        ((tel->vx_mmps != 0 || tel->w_mradps != 0) || zero(tel));
}

static bool fresh(''')
replace(names[1], 'r->type != WIFI_CONTROL_ARM || r->expected_boot_id != s->owner.boot_id ||',
        'r->type != WIFI_CONTROL_ARM || !wifi_control_request_allows(r) ||\n        r->expected_boot_id != s->owner.boot_id ||')
replace(names[1], 'if (r->type != WIFI_CONTROL_CMD || r->vx_mmps != 0 || r->w_mradps != 0) {',
        '''if (r->type != WIFI_CONTROL_CMD || !wifi_control_request_allows(r) ||
        (s->phase == WIFI_CONTROL_ZERO_PENDING &&
         (r->vx_mmps != 0 || r->w_mradps != 0))) {''')
replace(names[1], '''} else if (!zero(tel) ||
            (s->phase == WIFI_CONTROL_ACTIVE &&
             (tel->state != WIFI_CONTROL_STM_ARMED ||
              tel->command_age_ms >= WIFI_CONTROL_STM_TIMEOUT_MS))) {''',
        '''} else if ((s->phase != WIFI_CONTROL_ACTIVE && !zero(tel)) ||
            (s->phase == WIFI_CONTROL_ACTIVE && !active_tel_valid(tel))) {''')
replace(names[2], '!wifi_control_zero_only_allows(r)) {', '!wifi_control_request_allows(r)) {')
replace(names[2], '''} else if (!uart_idle ||
        (e->state.phase != WIFI_CONTROL_ZERO_PENDING && e->state.phase != WIFI_CONTROL_ACTIVE) ||''',
        '''} else if (!uart_idle ||
        (e->state.phase != WIFI_CONTROL_ZERO_PENDING && e->state.phase != WIFI_CONTROL_ACTIVE) ||
        (e->state.phase == WIFI_CONTROL_ZERO_PENDING &&
         (accepted.vx_mmps != 0 || accepted.w_mradps != 0)) ||''')
replace(names[2], '''"CMD,seq=%" PRIu32 ",vx_mmps=0,w_mradps=0,timeout_ms=300\\n", seq);''',
        '''"CMD,seq=%" PRIu32 ",vx_mmps=%" PRIi32
            ",w_mradps=%" PRIi32 ",timeout_ms=%" PRIu32 "\\n",
            seq, e->request.vx_mmps, e->request.w_mradps,
            (uint32_t)WIFI_CONTROL_STM_TIMEOUT_MS);''')

manifest = {'scope': 'Review candidate only; production untouched; zero-only remains 1', 'files': []}
for name in names:
    raw = units[name].encode('utf-8')
    (OUT / name).write_bytes(raw)
    manifest['files'].append({'name': name,
        'base_sha256': hashlib.sha256(original[name]).hexdigest(),
        'candidate_sha256': hashlib.sha256(raw).hexdigest()})
    assert (MAIN / name).read_bytes() == original[name]
(HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print('Prepared 3 candidate files; production unchanged.')
