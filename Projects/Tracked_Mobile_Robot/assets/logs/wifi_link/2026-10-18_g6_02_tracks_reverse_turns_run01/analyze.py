"""Read-only G6-02 analysis, including the unexpected first DISARM."""
from pathlib import Path
from collections import Counter
import json, re, zipfile

HERE = Path(__file__).resolve().parent
summary = json.loads((HERE / 'summary.json').read_text())
capture = HERE.parents[3] / 'assets/captures/logic_analyzer' / summary['source_name']
def parse(row):
    p = row['text'].split(',')
    return dict(row, kind=p[0], fields=dict(x.split('=', 1) for x in p[1:]))
d0 = [parse(r) for r in json.loads((HERE/'D0_lines.json').read_text()) if r['text'].startswith(('ACK,','TEL,','ERR,'))]
cmd = [parse(r) for r in json.loads((HERE/'D1_lines.json').read_text()) if r['text'].startswith(('ARM,','CMD,','DISARM,'))]
ack = [r for r in d0 if r['kind']=='ACK']
tel = [r for r in d0 if r['kind']=='TEL']
groups = []
for r in cmd:
    key = (r['kind'], r['fields'].get('vx_mmps'), r['fields'].get('w_mradps'))
    if not groups or groups[-1]['key'] != key:
        groups.append(dict(key=key,count=0,first=r,last=r))
    groups[-1]['count'] += 1
    groups[-1]['last'] = r
fs = summary['samplerate_hz']
assert fs == 4000000
with zipfile.ZipFile(capture) as z:
    chunks = sorted((n for n in z.namelist() if re.fullmatch(r'logic-1-\d+',n)), key=lambda n:int(n.rsplit('-',1)[1]))
    raw = b''.join(z.read(n) for n in chunks)
bits = {ch:raw.translate(bytes((v>>ch)&1 for v in range(256))) for ch in (2,3,4,6,7)}
motion = []
for i,g in enumerate(groups):
    if g['key'][0]!='CMD' or g['key'][1:]==('0','0'): continue
    end = groups[i+1]['first']['start_s']
    lo,hi = round(g['first']['start_s']*fs),round(end*fs)
    samples = [r['fields'] for r in tel if int(g['first']['fields']['seq']) <= int(r['fields']['last_seq']) <= int(g['last']['fields']['seq'])]
    stats = {}
    for ch in (4,7):
        pulses = [(lo+m.start(),lo+m.end()) for m in re.finditer(b'\x01+',bits[ch][lo:hi])]
        a,b = pulses[0][0],pulses[-1][0]
        stats['D'+str(ch)] = dict(duty_percent=100*sum(y-x for x,y in pulses[:-1])/(b-a),dir_levels={str(k):sorted(set(bits[k][a:pulses[-1][1]])) for k in (2,3)})
    motion.append(dict(command=g['key'],start_s=g['first']['start_s'],end_s=end,next_command=groups[i+1]['key'],pwm=stats,cps_range={k:[min(int(r[k]) for r in samples),max(int(r[k]) for r in samples)] for k in ('left_cps','right_cps')}))
last = cmd[-1]
tail = [r['fields'] for r in tel if r['start_s']>last['end_s']]
checks = dict(ordered_ack_match=[(r['kind'],r['fields']['seq']) for r in cmd]==[(r['fields'].get('type'),r['fields']['seq']) for r in ack],uart_no_framing_errors=all(summary['channels']['D'+str(ch)]['invalid_stop_bits']==0 for ch in (0,1)),no_fault=all(r['fields']['state']!='FAULT' for r in tel),drop_err_zero=all(r['fields'][k]=='0' for r in tel for k in ('drop','err')),estop_low=not any(bits[6]),final_disarmed_zero=bool(tail) and all(r['state']=='DISARMED' and all(r[k]=='0' for k in ('left_pwm','right_pwm','left_cps','right_cps')) for r in tail))
out = dict(test='G6-02',status='MOTION_OBSERVED_UNEXPECTED_DISARM_TRIGGER_UNRESOLVED',capture_sha256=summary['sha256'],samplerate_hz=fs,duration_s=summary['duration_s'],counts=dict(Counter(r['kind'] for r in cmd)),ack_count=len(ack),checks=checks,groups=groups,motion=motion,final_tel=tel[-1],user_observation='Reverse succeeded; stopped during first left turn. Manually re-ARM, right then left worked, followed by DISARM.',limits=['First left turn ends with a WebSocket-queued DISARM request193, not STM FAULT. Browser trigger is not logged; cause requires user clarification.','Direction and motion observations do not establish calibrated speed or ground driving.'])
(HERE/'observations.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ('status','counts','ack_count','checks','motion')},ensure_ascii=False,indent=2))
