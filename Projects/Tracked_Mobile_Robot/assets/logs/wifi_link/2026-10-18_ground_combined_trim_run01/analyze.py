"""Source-TEL deduplication and bounded combined-drive review; no physical I/O."""
from pathlib import Path
import json, itertools, statistics
here = Path(__file__).resolve().parent
r = json.loads((here/'browser_report.json').read_text(encoding='utf-8-sig'))
seen, rows = set(), []
for t in r['telemetry']:
    key = t['boot_id'], t['tel_count']
    if key not in seen:
        seen.add(key); rows.append(t)
groups = []
for key, group in itertools.groupby(rows, lambda t: (t['state'], tuple(t['command']), tuple(t['pwm']))):
    a = list(group)
    steady = [t for t in a if t['stm_t_ms'] - a[0]['stm_t_ms'] >= 500]
    groups.append(dict(state=key[0], command=key[1], pwm=key[2], source_samples=len(a),
        source_duration_ms=a[-1]['stm_t_ms']-a[0]['stm_t_ms'],
        steady_samples=len(steady),
        steady_abs_cps_median=[statistics.median(abs(t['cps'][i]) for t in steady) if steady else None for i in (0,1)],
        steady_zero_cps_counts=[sum(t['cps'][i]==0 for t in steady) for i in (0,1)],
        both_zero_cps_samples=sum(t['cps']==[0,0] for t in a), tail_cps=a[-1]['cps']))
motion = [g for g in groups if any(g['pwm'])]
expected = [[100,0],[0,500],[100,0],[0,-500],[-100,0]]
assert [list(g['command']) for g in motion] == expected
assert [list(g['pwm']) for g in motion] == [[144,150],[-200,200],[144,150],[200,-200],[-140,-150]]
for i, g in enumerate(groups):
    if any(g['pwm']):
        assert g['steady_samples'] > 0 and g['steady_zero_cps_counts'] == [0,0]
        following = groups[i+1]
        assert list(following['pwm']) == [0,0] and following['both_zero_cps_samples'] > 0 and following['tail_cps'] == [0,0]
held = [x for x in r['stops'] if x.get('intent') and x.get('motion') and x.get('focused')]
assert not held and r['captured'] is None
assert rows[-1]['state']=='DISARMED' and rows[-1]['pwm']==[0,0] and rows[-1]['cps']==[0,0]
obs = dict(test='GROUND_COMBINED_TRIM_RUN01', status='SELECTED_MANUAL_DRIVE_SEQUENCE_CONFIRMED_TELEMETRY_AND_OPERATOR',
    unique_source_samples=len(rows), telemetry_dropped=r['telemetry_dropped'], groups=groups,
    held_unexpected_stops=held, captured=r['captured'], final_tel=rows[-1],
    drop_err_values=sorted(set((x['drop'],x['err']) for x in rows)),
    operator_confirmation=dict(direction_changes_ok=True, release_stops_ok=True, source='User confirmed no problems after review'),
    visual='User confirmed direction changes and release stops had no observed problems. No new video supplied.',
    limits=['CPS describes encoder rotation; chassis displacement, yaw angle and track slip are not quantified.',
            'Intermediate zero PWM and settled zero CPS are sampled observations, not precise stopping-time measurements.',
            'No unexpected held stop captured in this run; this does not establish permanent fault resolution.'])
(here/'observations.json').write_text(json.dumps(obs,indent=2)+'\n',encoding='utf-8')
print('PASS recorded five-motion sequence, bounded PWM, both encoders moving, settled intermediate stops and final DISARM')
