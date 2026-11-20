"""G6-01 console observations; capture20kHz is unsuitable for UART/PWM decode."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
text = (HERE / 'esp_console.txt').read_text(encoding='utf-8-sig')
summary = json.loads((HERE / 'summary.json').read_text())
pattern = (r'I \((\d+)\) wifi_link: STM TEL #(\d+) t_ms=(\d+) '
           r'state=(\w+) reason=(\w+) pwm=(-?\d+)/(-?\d+) '
           r'cps=(-?\d+)/(-?\d+) drop=(\d+) err=(\d+)')
tels = []
for m in re.finditer(pattern, text):
    t = m.groups()
    tels.append(dict(esp_log_ms=int(t[0]), tel_count=int(t[1]), stm_t_ms=int(t[2]),
        state=t[3], reason=t[4], left_pwm=int(t[5]), right_pwm=int(t[6]),
        left_cps=int(t[7]), right_cps=int(t[8]), drop=int(t[9]), err=int(t[10])))
tx = [dict(esp_log_ms=int(ms), op=int(op), seq=int(seq), written=int(n), size=int(size))
      for ms, op, seq, n, size in re.findall(
          r'I \((\d+)\) wifi_link: CONTROL TX: op=(\d+) seq=(\d+) written=(\d+)/(\d+)', text)]
rx = [(kind, int(seq)) for kind, seq in re.findall(r'CONTROL RX MATCH: (\w+) seq=(\d+)', text)]
names = {1:'ARM', 2:'CMD', 3:'DISARM'}
keys = [(names[r['op']], r['seq']) for r in tx]
moving = [t for t in tels if t['left_pwm'] or t['right_pwm']]
assert moving, 'No nonzero console TEL; inspect original log'
last_motion = moving[-1]
zero = next(t for t in tels if t['esp_log_ms'] > last_motion['esp_log_ms'] and
            t['left_pwm'] == t['right_pwm'] == 0)
settled = next((t for t in tels if t['esp_log_ms'] >= zero['esp_log_ms'] and
                t['left_cps'] == t['right_cps'] == 0), None)
stop = tx[-1]
first_disarmed = next((t for t in tels if t['esp_log_ms'] > stop['esp_log_ms'] and t['state']=='DISARMED'), None)
post = [] if first_disarmed is None else [t for t in tels if t['esp_log_ms'] >= first_disarmed['esp_log_ms']]
checks = dict(
    tx_ack_match_in_console=keys == rx and len(set(keys)) == len(keys),
    writes_complete=all(t['written'] == t['size'] for t in tx),
    arm_cmd_disarm_order=[names[t['op']] for i,t in enumerate(tx)
        if i == 0 or t['op'] != tx[i-1]['op']] == ['ARM','CMD','DISARM'],
    console_pwm_100_both=all(t['state'] == 'ARMED' and t['left_pwm'] == t['right_pwm'] == 100 for t in moving),
    both_forward_encoder_seen=any(t['left_cps'] > 0 and t['right_cps'] > 0 for t in moving),
    armed_zero_before_disarm=zero['state'] == 'ARMED' and zero['esp_log_ms'] < stop['esp_log_ms'],
    cps_zero_before_disarm=settled is not None and settled['esp_log_ms'] < stop['esp_log_ms'],
    post_disarm_pwm_zero=bool(post) and all(t['state'] == 'DISARMED' and t['reason'] == 'DISARM' and
        t['left_pwm'] == t['right_pwm'] == 0 for t in post),
    post_disarm_cps_settles=settled is not None and all(t['left_cps'] == t['right_cps'] == 0
        for t in post if t['esp_log_ms'] >= settled['esp_log_ms']),
    no_console_fault_errors=all(t['state'] != 'FAULT' and t['drop'] == t['err'] == 0 for t in tels))
report = dict(test='G6-01_TRACKS_LIFTED_FORWARD_RELEASE_10PCT',
    status='PARTIAL_CAPTURE_UNSUITABLE_RELEASE_PATH_UNCONFIRMED',
    scope='User visual observation and ESP console TX/RX/TEL only; no valid sampled UART/PWM evidence for this run',
    user_observation='Both tracks rotated in forward direction and stopped afterward; exact pointer release timestamp not recorded.',
    checks=checks, tx_counts=dict(Counter(names[t['op']] for t in tx)), rx_count=len(rx), tel_count=len(tels),
    moving_cps_ranges={k:[min(t[k] for t in moving),max(t[k] for t in moving)] for k in ('left_cps','right_cps')},
    first_zero_tel=zero, first_zero_cps_tel=settled, final_disarm=stop,
    console_post_disarm_observation_s=(post[-1]['esp_log_ms']-post[0]['esp_log_ms'])/1000 if post else 0,
    capture=dict(name=summary['source_name'], sha256=summary['sha256'],
        sample_rate_hz=summary['samplerate_hz'], duration_s=summary['duration_s'],
        suitable_for_115200_uart_or_19khz_pwm=False,
        note='20kHz means50us/sample, versus UART8.68us/bit and PWM about52.5us/period. Decode errors are sampling artifacts, not evidence of real UART failure.'),
    esp_console_sha256=hashlib.sha256((HERE/'esp_console.txt').read_bytes()).hexdigest(),
    limits=['Actual PWM duty, UART byte identities/timing and PC7 waveform are not established by this capture.',
            'No measured mechanical stopping time/distance or ground-driving acceptance.',
            'User has not separately reported absence of track binding/derailment.'])
(HERE/'observations.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','checks','tx_counts','rx_count','tel_count','moving_cps_ranges','console_post_disarm_observation_s')},indent=2))
