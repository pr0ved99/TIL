"""NZ-06 saved capture analysis; reads artifacts only, never sends commands."""
from pathlib import Path
from collections import Counter
from bisect import bisect_left
import hashlib
import json
import re
import statistics
import zipfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
CAPTURE = PROJECT / 'assets/captures/logic_analyzer/2026-10-17_WIFI_NZ06_REVERSE_TURNS_10PCT_run01.sr'
summary = json.loads((HERE / 'summary.json').read_text())
fs = summary['samplerate_hz']


def parse(row):
    parts = row['text'].split(',')
    return dict(row, kind=parts[0], fields=dict(p.split('=', 1) for p in parts[1:]))


raw0 = json.loads((HERE / 'D0_lines.json').read_text())
raw1 = json.loads((HERE / 'D1_lines.json').read_text())
d0 = [parse(r) for r in raw0 if r['text'].startswith(('TEL,', 'ACK,', 'ERR,'))]
commands = [parse(r) for r in raw1 if r['text'].startswith(('ARM,', 'CMD,', 'DISARM,'))]
tels = [r for r in d0 if r['kind'] == 'TEL']
acks = [r for r in d0 if r['kind'] == 'ACK']
ack_by_seq = {r['fields']['seq']: r for r in acks}
groups = []
for row in commands:
    f = row['fields']
    key = (row['kind'], f.get('vx_mmps'), f.get('w_mradps'))
    if not groups or groups[-1]['key'] != key:
        groups.append(dict(key=key, count=0, first=row, last=row))
    groups[-1]['count'] += 1
    groups[-1]['last'] = row
expected_keys = [('ARM', None, None), ('CMD', '0', '0'), ('CMD', '-100', '0'),
                 ('CMD', '0', '0'), ('CMD', '0', '500'), ('CMD', '0', '0'),
                 ('CMD', '0', '-500'), ('CMD', '0', '0'), ('DISARM', None, None)]
assert [g['key'] for g in groups] == expected_keys, 'Unexpected command order; review before analysis'
with zipfile.ZipFile(CAPTURE) as z:
    names = sorted((n for n in z.namelist() if re.fullmatch(r'logic-1-\d+', n)),
                   key=lambda n: int(n.rsplit('-', 1)[1]))
    raw = b''.join(z.read(n) for n in names)
bits = {ch: raw.translate(bytes((v >> ch) & 1 for v in range(256))) for ch in (2, 3, 4, 6, 7)}
runs = {ch: [(m.start(), m.end()) for m in re.finditer(b'\x01+', bits[ch])] for ch in (4, 7)}
motion = []
expected = [('reverse', 2, (1, 0), (-100, -100)), ('left', 4, (1, 1), (-100, 100)),
            ('right', 6, (0, 0), (100, -100))]
for name, group_index, dirs, pwms in expected:
    g = groups[group_index]
    zero = groups[group_index + 1]['first']
    zero_ack = ack_by_seq[zero['fields']['seq']]
    window_start = round(g['first']['start_s'] * fs)
    window_end = round(zero_ack['end_s'] * fs)
    next_start = round(groups[group_index + 2]['first']['start_s'] * fs)
    stats = {}
    for ch in (4, 7):
        selected = [(a, b) for a, b in runs[ch] if window_start <= a < window_end]
        assert len(selected) > 2
        a, b = selected[0][0], selected[-1][1]
        periods = [y[0] - x[0] for x, y in zip(selected, selected[1:])]
        widths = [y - x for x, y in selected]
        stats[f'D{ch}'] = dict(pulses=len(selected), first_rise_s=a / fs, last_fall_s=b / fs,
            span_s=(b - a) / fs, mean_frequency_hz=fs / statistics.mean(periods),
            mean_duty_percent=100 * sum(widths[:-1]) / (selected[-1][0] - a),
            period_range_us=[min(periods) / fs * 1e6, max(periods) / fs * 1e6],
            high_width_range_us=[min(widths) / fs * 1e6, max(widths) / fs * 1e6],
            dir_D2_levels=sorted(set(bits[2][a:b])), dir_D3_levels=sorted(set(bits[3][a:b])),
            high_samples_after_zero_ack_until_next_group=bits[ch][window_end:next_start].count(1))
    first_seq = int(g['first']['fields']['seq'])
    last_seq = int(g['last']['fields']['seq'])
    active_tels = [r for r in tels if first_seq <= int(r['fields']['last_seq']) <= last_seq]
    zero_tel = next(r for r in tels if r['fields']['last_seq'] == zero['fields']['seq'])
    f = zero_tel['fields']
    checks = dict(
        dir_matches=all(v['dir_D2_levels'] == [dirs[0]] and v['dir_D3_levels'] == [dirs[1]] for v in stats.values()),
        duty_ten_percent=all(abs(v['mean_duty_percent'] - 10) < 0.1 for v in stats.values()),
        no_pwm_after_zero_ack=all(v['high_samples_after_zero_ack_until_next_group'] == 0 for v in stats.values()),
        tel_matches=bool(active_tels) and all(r['fields']['state'] == 'ARMED' and
            (int(r['fields']['left_pwm']), int(r['fields']['right_pwm'])) == pwms and
            (r['fields']['vx_mmps'], r['fields']['w_mradps']) == g['key'][1:] for r in active_tels),
        zero_returns_armed=f['state'] == 'ARMED' and all(f[k] == '0' for k in
            ('vx_mmps', 'w_mradps', 'left_pwm', 'right_pwm')))
    signs = tuple(1 if v > 0 else -1 for v in pwms)
    cps = {k:[int(r['fields'][k]) for r in active_tels] for k in ('left_cps','right_cps')}
    for k, sign in zip(('left_cps','right_cps'), signs):
        checks[k+'_expected_sign_seen'] = any(v*sign > 0 for v in cps[k])
        checks[k+'_no_wrong_sign'] = all(v*sign >= 0 for v in cps[k])
    zero_interval = [r for r in tels if zero_ack['end_s'] <= r['start_s'] < groups[group_index+2]['first']['start_s']]
    checks['cps_settles_before_next_group'] = bool(zero_interval) and all(zero_interval[-1]['fields'][k]=='0' for k in ('left_cps','right_cps'))
    motion.append(dict(name=name, checks=checks, pwm=stats, cps=cps, command_count=g['count'],
        first_seq=first_seq, last_seq=last_seq, zero_command=zero, zero_tel=zero_tel))

dir_changes = []
for ch in (2, 3):
    for m in re.finditer(b'\x00\x01|\x01\x00', bits[ch]):
        edge = m.start() + 1
        detail = dict(channel=f'D{ch}', t_s=edge / fs, new_level=bits[ch][edge],
            both_pwm_low=all(bits[p][edge-1] == bits[p][edge] == 0 for p in (4, 7)), gaps={})
        for p in (4, 7):
            starts = [a for a, _ in runs[p]]
            pos = bisect_left(starts, edge)
            detail['gaps'][f'D{p}'] = dict(
                previous_fall_us=None if pos == 0 else (edge - runs[p][pos-1][1]) / fs * 1e6,
                next_rise_us=None if pos == len(starts) else (starts[pos] - edge) / fs * 1e6)
        dir_changes.append(detail)

command_keys = [(r['kind'], r['fields']['seq']) for r in commands]
reply_keys = [(r['fields']['type'], r['fields']['seq']) for r in acks]
unexpected0 = [r for r in raw0 if not r['text'].startswith(('TEL,', 'ACK,', 'ERR,'))]
first_full_tel = tels[0]['start_s']
boundary_stops = summary['channels']['D0']['invalid_stop_times_s']
disarm = commands[-1]
stop_tel = next(r for r in tels if r['fields']['last_seq'] == disarm['fields']['seq'])
after_stop = [r for r in tels if r['start_s'] >= stop_tel['start_s']]
log = (HERE / 'esp_console.txt').read_text(encoding='utf-8-sig')
log_tx = re.findall(r'CONTROL TX: op=(\d+) seq=(\d+) written=(\d+)/(\d+)', log)
log_rx = re.findall(r'CONTROL RX MATCH: (\w+) seq=(\d+)', log)
op_names = {'1': 'ARM', '2': 'CMD', '3': 'DISARM'}
last_zero_ack = ack_by_seq[groups[-2]['first']['fields']['seq']]
checks = dict(
    commands_ack_once=command_keys == reply_keys and len(set(command_keys)) == len(command_keys),
    seq_contiguous=all(int(b[1]) == int(a[1]) + 1 for a, b in zip(command_keys, command_keys[1:])),
    framing_artifacts_only_before_first_full_tel=all(t < first_full_tel for t in boundary_stops) and
        summary['channels']['D1']['invalid_stop_bits'] == 0 and all(r['end_s'] < first_full_tel for r in unexpected0),
    no_malformed_tel=not summary['channels']['D0']['malformed_tel_lines'],
    no_fault_errors=all(r['fields']['state'] != 'FAULT' and all(r['fields'][k] == '0'
        for k in ('drop', 'err')) for r in tels) and not any(r['kind'] == 'ERR' for r in d0),
    pc7_low=bits[6].count(1) == 0,
    all_direction_changes_with_pwm_low=all(r['both_pwm_low'] for r in dir_changes),
    all_motion_checks=all(all(r['checks'].values()) for r in motion),
    no_extra_pwm_bursts=all(sum(r['pwm'][f'D{ch}']['pulses'] for r in motion) == len(runs[ch]) for ch in (4, 7)),
    no_pwm_after_final_zero=all(bits[ch][round(last_zero_ack['end_s'] * fs):].count(1) == 0 for ch in (4, 7)),
    final_disarmed_zero=bool(after_stop) and all(r['fields']['state'] == 'DISARMED' and r['fields']['reason'] == 'DISARM' and
        r['fields']['last_seq'] == disarm['fields']['seq'] and all(r['fields'][k] == '0' for k in
        ('vx_mmps', 'w_mradps', 'left_pwm', 'right_pwm')) for r in after_stop),
    cmd_timeout_300=all(r['fields']['timeout_ms'] == '300' for r in commands if r['kind'] == 'CMD'),
    esp_tx_subset_matches_capture=bool(log_tx) and all((op_names[op], seq) in command_keys and written == size
        for op, seq, written, size in log_tx),
    esp_rx_subset_matches_capture=bool(log_rx) and all(key in reply_keys for key in log_rx))
report = dict(test='NZ-06_REVERSE_TURNS_DIR_PWM', status='PASS' if all(checks.values()) else 'REVIEW',
    scope='Both motors detached from chassis and connected to normal M1/M2 paths; sampled UART/DIR/PWM/PC7 and TEL CPS; user confirmed visual directions', checks=checks,
    capture=CAPTURE.name, capture_sha256=hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
    esp_log_sha256=hashlib.sha256((HERE / 'esp_console.txt').read_bytes()).hexdigest(),
    user_visual_direction_confirmation='User confirmed reverse A-/B-, left A-/B+, right A+/B- matched the table.',
    sample_rate_hz=fs, duration_s=len(raw) / fs, command_counts=dict(Counter(r['kind'] for r in commands)),
    ack_count=len(acks), tel_count=len(tels), command_groups=groups, motions=motion,
    dir_transitions=sorted(dir_changes, key=lambda r: r['t_s']), final_disarm=disarm,
    stopped_tel_observation_s=tels[-1]['end_s'] - stop_tel['end_s'],
    final_pwm_low_tail_s=min((len(raw) - runs[ch][-1][1]) / fs for ch in (4, 7)),
    initial_partial_uart=dict(invalid_stop_times_s=boundary_stops, fragments=unexpected0, first_full_tel_s=first_full_tel),
    esp_log_tx_count=len(log_tx), esp_log_rx_count=len(log_rx),
    limits=['D2=PC8 and D3=PC9 follow the instructed probe map; metadata records D labels only.',
            'Any capture-boundary UART fragments remain in raw decode artifacts.',
            'CPS provides encoder direction evidence; user confirmed matching visual directions.',
            'Pointer timestamps were not recorded; release-to-zero latency is unmeasured.',
            'No calibrated velocity, synchronized mechanical stopping time/distance, or chassis driving acceptance; speed compensation deferred.'])
(HERE / 'observations.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: report[k] for k in ('status', 'checks', 'duration_s', 'command_counts', 'ack_count',
    'tel_count', 'stopped_tel_observation_s', 'final_pwm_low_tail_s')}, indent=2))
for m in motion:
    print(m['name'], json.dumps(m['pwm']), m['checks'])
print('DIR transitions:', json.dumps(report['dir_transitions']))
