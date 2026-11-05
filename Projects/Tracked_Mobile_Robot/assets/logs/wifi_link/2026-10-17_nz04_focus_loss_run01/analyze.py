"""Read-only NZ-04 saved UART/PWM capture analysis. No device commands."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import zipfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
CAPTURE = PROJECT / 'assets/captures/logic_analyzer/2026-10-17_WIFI_NZ04_FOCUS_LOSS_NO_REARM_PWM_run01.sr'
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
groups = []
for row in commands:
    f = row['fields']
    key = (row['kind'], f.get('vx_mmps'), f.get('w_mradps'))
    if not groups or groups[-1]['key'] != key:
        groups.append(dict(key=key, count=0, first=row, last=row))
    groups[-1]['count'] += 1
    groups[-1]['last'] = row
expected = [('ARM', None, None), ('CMD', '0', '0'), ('CMD', '50', '0'), ('DISARM', None, None)]
assert [g['key'] for g in groups] == expected, 'Review unexpected command sequence'
stop = commands[-1]
stop_ack = next(r for r in acks if r['fields']['seq'] == stop['fields']['seq'])
stop_tel = next(r for r in tels if r['fields']['last_seq'] == stop['fields']['seq'])
with zipfile.ZipFile(CAPTURE) as z:
    names = sorted((n for n in z.namelist() if re.fullmatch(r'logic-1-\d+', n)), key=lambda n: int(n.rsplit('-', 1)[1]))
    raw = b''.join(z.read(n) for n in names)
bits = {ch: raw.translate(bytes((v >> ch) & 1 for v in range(256))) for ch in (2, 3, 4, 6, 7)}
pwm = {}
for ch in (4, 7):
    runs = [(m.start(), m.end()) for m in re.finditer(b'\x01+', bits[ch])]
    first, last = runs[0][0], runs[-1][1]
    pwm[f'D{ch}'] = dict(pulses=len(runs), first_rise_s=first/fs, last_fall_s=last/fs,
        mean_frequency_hz=(len(runs)-1)*fs/(runs[-1][0]-first),
        mean_duty_percent=100*sum(b-a for a,b in runs[:-1])/(runs[-1][0]-first),
        low_tail_s=(len(raw)-last)/fs,
        last_fall_after_disarm_frame_end_ms=(last/fs-stop['end_s'])*1000,
        max_pulse_gap_us=max(b[0]-a[0] for a,b in zip(runs,runs[1:]))/fs*1e6,
        high_samples_last_50ms_before_disarm=bits[ch][round((stop['start_s']-.05)*fs):round(stop['start_s']*fs)].count(1),
        high_samples_after_disarm_ack=bits[ch][round(stop_ack['end_s']*fs):].count(1),
        dir_levels_during_pwm={f'D{d}':sorted(set(bits[d][first:last])) for d in (2,3)})
keys = [(r['kind'], r['fields']['seq']) for r in commands]
replies = [(r['fields']['type'], r['fields']['seq']) for r in acks]
post = [r for r in tels if r['start_s'] >= stop_tel['start_s']]
nonzero = [r for r in tels if r['fields']['left_pwm'] != '0' or r['fields']['right_pwm'] != '0']
checks = dict(
    command_order_arm_zero_forward_disarm=[g['key'] for g in groups] == expected,
    commands_ack_once=keys == replies and len(set(keys)) == len(keys),
    seq_contiguous=all(int(b[1]) == int(a[1])+1 for a,b in zip(keys,keys[1:])),
    clean_complete_uart=all(summary['channels'][f'D{ch}']['invalid_stop_bits']==0 for ch in (0,1)) and
        not summary['channels']['D1']['trailing_partial_text'] and
        all(r['text'].startswith(('TEL,','ACK,','ERR,')) for r in raw0) and
        not summary['channels']['D0']['malformed_tel_lines'],
    nonzero_tel_forward=bool(nonzero) and all(r['fields']['state']=='ARMED' and
        all(r['fields'][k]==v for k,v in [('vx_mmps','50'),('w_mradps','0'),('left_pwm','50'),('right_pwm','50')]) for r in nonzero),
    pwm_active_before_disarm=all(v['high_samples_last_50ms_before_disarm']>0 and v['max_pulse_gap_us']<60 for v in pwm.values()),
    pwm_five_percent=all(abs(v['mean_duty_percent']-5)<.1 for v in pwm.values()),
    forward_dir=all(v['dir_levels_during_pwm']=={'D2':[0],'D3':[1]} for v in pwm.values()),
    no_pwm_after_disarm_ack=all(v['high_samples_after_disarm_ack']==0 for v in pwm.values()),
    stopped_observed_over_8s=all(v['low_tail_s']>=8 for v in pwm.values()),
    stopped_tel=bool(post) and all(r['fields']['state']=='DISARMED' and r['fields']['reason']=='DISARM' and
        r['fields']['last_seq']==stop['fields']['seq'] and all(r['fields'][k]=='0' for k in ('vx_mmps','w_mradps','left_pwm','right_pwm')) for r in post),
    pc7_low=bits[6].count(1)==0,
    no_fault_errors_cps=not any(r['kind']=='ERR' for r in d0) and all(r['fields']['state']!='FAULT' and
        all(r['fields'][k]=='0' for k in ('drop','err','left_cps','right_cps')) for r in tels),
    command_timeout_300=all(r['fields']['timeout_ms']=='300' for r in commands if r['kind']=='CMD'))
tail = summary['channels']['D0']['trailing_partial_text']
checks['only_capture_end_partial_tel'] = not tail or (tail.startswith('TEL,t_ms=') and
    ',state=DISARMED,reason=DISARM,' in tail and ',last_seq='+stop['fields']['seq']+',' in tail)
log = (HERE/'esp_console.txt').read_text(encoding='utf-8-sig')
ops = {'1':'ARM','2':'CMD','3':'DISARM'}
tx = re.findall(r'CONTROL TX: op=(\d+) seq=(\d+) written=(\d+)/(\d+)',log)
rx = re.findall(r'CONTROL RX MATCH: (\w+) seq=(\d+)',log)
checks['esp_log_matches_capture'] = bool(tx) and bool(rx) and all((ops[op],seq) in keys and n==size for op,seq,n,size in tx) and all(tuple(r) in replies for r in rx)
report = dict(test='NZ-04_FOCUS_LOSS_NO_REARM_PWM',status='PASS' if all(checks.values()) else 'REVIEW',
    scope='Motor-disconnected STM UART/DIR/PWM/PC7 only',checks=checks,capture=CAPTURE.name,
    capture_sha256=summary['sha256'],esp_log_sha256=hashlib.sha256((HERE/'esp_console.txt').read_bytes()).hexdigest(),
    sample_rate_hz=fs,duration_s=len(raw)/fs,trailing_partial_tel=tail,
    command_counts=dict(Counter(r['kind'] for r in commands)),
    ack_count=len(acks),tel_count=len(tels),command_groups=groups,pwm=pwm,
    disarm=stop,disarm_ack=stop_ack,first_disarmed_tel=stop_tel,
    stopped_tel_observation_s=tels[-1]['end_s']-stop_tel['end_s'],
    limits=['Capture ends within a DISARMED TEL; the partial text is retained separately and excluded from full frames.',
            'No browser focus/visibility timestamps: Alt+Tab and return timing follow the user trial; the exact initiating browser event and focus-loss-to-stop latency are not independently measured.',
            'Capture proves nonzero CMD directly followed by DISARM without an intervening zero CMD.',
            'Probe identities follow the instructed map; no actual motor motion/braking acceptance.'])
(HERE/'observations.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','checks','duration_s','command_counts','ack_count','tel_count','pwm','stopped_tel_observation_s')},indent=2))
