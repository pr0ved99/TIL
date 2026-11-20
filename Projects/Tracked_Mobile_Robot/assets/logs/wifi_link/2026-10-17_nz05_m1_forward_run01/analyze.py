"""Analyze saved NZ-01 UART decodes and raw PWM; no device access or commands."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import statistics
import zipfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
CAPTURE = PROJECT / 'assets/captures/logic_analyzer/2026-10-17_WIFI_NZ05_M1_FORWARD_RELEASE_run01.sr'


def parse(line):
    parts = line['text'].split(',')
    fields = dict(part.split('=', 1) for part in parts[1:])
    return dict(line, kind=parts[0], fields=fields)


summary = json.loads((HERE / 'summary.json').read_text())
d0 = [parse(r) for r in json.loads((HERE / 'D0_lines.json').read_text())]
d1_raw = json.loads((HERE / 'D1_lines.json').read_text())
commands = [parse(r) for r in d1_raw if r['text'].startswith(('ARM,', 'CMD,', 'DISARM,'))]
acks = [r for r in d0 if r['kind'] == 'ACK']
tels = [r for r in d0 if r['kind'] == 'TEL']
groups = []
for r in commands:
    f = r['fields']
    key = (r['kind'], f.get('vx_mmps'), f.get('w_mradps'))
    if not groups or key != groups[-1]['key']:
        groups.append(dict(key=key, count=0, first=r, last=r))
    groups[-1]['count'] += 1
    groups[-1]['last'] = r
moving = [r for r in commands if r['kind'] == 'CMD' and r['fields']['vx_mmps'] == '50']
zero = next(r for r in commands if r['kind'] == 'CMD' and r['start_s'] > moving[-1]['start_s'])
disarm = next(r for r in commands if r['kind'] == 'DISARM')
reply_keys = [(r['fields']['type'], r['fields']['seq']) for r in acks]
command_keys = [(r['kind'], r['fields']['seq']) for r in commands]
with zipfile.ZipFile(CAPTURE) as archive:
    chunks = sorted((n for n in archive.namelist() if re.fullmatch(r'logic-1-\d+', n)),
                    key=lambda n: int(n.rsplit('-', 1)[1]))
    raw = b''.join(archive.read(n) for n in chunks)
fs = summary['samplerate_hz']
pwm = {}
for channel in (4, 7):
    bits = raw.translate(bytes((v >> channel) & 1 for v in range(256)))
    runs = [(m.start(), m.end()) for m in re.finditer(b'\x01+', bits)]
    periods = [b[0] - a[0] for a, b in zip(runs, runs[1:])]
    widths = [b - a for a, b in runs]
    total_period = runs[-1][0] - runs[0][0]
    pwm[f'D{channel}'] = dict(
        pulses=len(runs), first_rise_s=runs[0][0] / fs, last_fall_s=runs[-1][1] / fs,
        burst_span_s=(runs[-1][1] - runs[0][0]) / fs,
        mean_frequency_hz=fs / statistics.mean(periods),
        mean_duty_percent=100 * sum(widths[:-1]) / total_period,
        period_range_us=[min(periods) / fs * 1e6, max(periods) / fs * 1e6],
        high_width_range_us=[min(widths) / fs * 1e6, max(widths) / fs * 1e6],
        high_samples_after_zero_ack=None,
        low_tail_s=(len(raw) - runs[-1][1]) / fs)
    zero_ack = next(r for r in acks if r['fields']['seq'] == zero['fields']['seq'])
    pwm[f'D{channel}']['high_samples_after_zero_ack'] = bits[round(zero_ack['end_s'] * fs):].count(1)
zero_tel = next(r for r in tels if r['fields']['last_seq'] == zero['fields']['seq'])
stop_tel = next(r for r in tels if r['fields']['last_seq'] == disarm['fields']['seq'])
checks = dict(
    uart_no_stop_bit_errors=all(v['invalid_stop_bits'] == 0 for v in summary['channels'].values()),
    all_commands_acknowledged_once=command_keys == reply_keys and len(set(command_keys)) == len(command_keys),
    sequence_contiguous=all(int(b[1]) == int(a[1]) + 1 for a, b in zip(command_keys, command_keys[1:])),
    expected_command_groups=[g['key'] for g in groups] == [
        ('ARM', None, None), ('CMD', '0', '0'), ('CMD', '50', '0'), ('CMD', '0', '0'), ('DISARM', None, None)],
    cmd_timeout_300=all(r['fields']['timeout_ms'] == '300' for r in commands if r['kind'] == 'CMD'),
    zero_keeps_armed=zero_tel['fields']['state'] == 'ARMED' and
        all(zero_tel['fields'][k] == '0' for k in ('vx_mmps', 'w_mradps', 'left_pwm', 'right_pwm')),
    final_disarmed=stop_tel['fields']['state'] == 'DISARMED' and stop_tel['fields']['reason'] == 'DISARM',
    tel_no_fault_or_errors=all(r['fields']['state'] != 'FAULT' and r['fields']['drop'] == '0' and
        r['fields']['err'] == '0' for r in tels),
    cps_zero_observed=all(r['fields']['left_cps'] == r['fields']['right_cps'] == '0' for r in tels),
    pc7_low=summary['logic_levels']['D6']['high_samples'] == 0,
    pwm_five_percent=all(abs(v['mean_duty_percent'] - 5) < 0.1 for v in pwm.values()),
    no_pwm_after_zero_ack=all(v['high_samples_after_zero_ack'] == 0 for v in pwm.values()),
    no_uart_commands_after_disarm=commands[-1] == disarm,
    stopped_tel_through_capture=all(r['fields']['last_seq'] == disarm['fields']['seq'] and
        r['fields']['state'] == 'DISARMED' and all(r['fields'][k] == '0' for k in
        ('vx_mmps', 'w_mradps', 'left_pwm', 'right_pwm')) for r in tels if r['start_s'] >= stop_tel['start_s']))
report = dict(test='NZ-05_M1_FORWARD_RELEASE_5_PERCENT', status='NO_ROTATION', signal_checks_status='PASS' if all(checks.values()) else 'REVIEW', user_observation='Motor A did not rotate; slight high-pitched sound; B motor-side connector disconnected',
    scope='Motor A connected to M1, motor B disconnected at motor-side connector; sampled STM UART/PWM/PC7, no motor-terminal voltage/current measurement',
    capture=CAPTURE.name, capture_sha256=hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
    esp_log_sha256=hashlib.sha256((HERE / 'esp_console.txt').read_bytes()).hexdigest(),
    sample_rate_hz=fs, duration_s=len(raw) / fs, checks=checks,
    command_counts=dict(Counter(r['kind'] for r in commands)), ack_count=len(acks),
    tel_count=len(tels), command_groups=groups, first_zero_after_motion=zero,
    zero_tel=zero_tel, disarm=disarm, disarm_tel=stop_tel, pwm=pwm,
    stopped_tel_observation_s=tels[-1]['end_s'] - stop_tel['end_s'],
    limits=['Probe identities follow the established channel map; capture metadata contains D labels only.',
            'Pointer release time was not recorded, so user-release-to-zero latency is unmeasured.',
            'Motor rotation acceptance failed: user observed no rotation and all sampled CPS remained zero.',
            'No motor-terminal voltage/current measurement; insufficient startup duty is a hypothesis, not an established root cause.'])
(HERE / 'observations.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: report[k] for k in ('status', 'checks', 'command_counts', 'ack_count', 'tel_count',
    'pwm', 'stopped_tel_observation_s')}, indent=2))
print('groups', [(g['key'], g['count'], g['first']['fields']['seq'], g['last']['fields']['seq']) for g in groups])
print('first post-motion zero:', zero['text'], zero['start_s'])
print('final stop:', disarm['text'], disarm['start_s'])
