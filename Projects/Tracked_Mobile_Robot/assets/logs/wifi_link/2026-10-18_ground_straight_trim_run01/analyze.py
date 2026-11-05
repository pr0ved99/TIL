"""Deduplicate source TELs and compare absolute CPS after 500ms startup."""
from pathlib import Path
import json
import statistics

here = Path(__file__).resolve().parent
report = json.loads((here / 'browser_report.json').read_text(encoding='utf-8-sig'))
rows, seen, groups = [], set(), []
for row in report['telemetry']:
    key = row['boot_id'], row['tel_count']
    if key not in seen:
        seen.add(key)
        rows.append(row)
for row in rows:
    key = row['state'], tuple(row['command']), tuple(row['pwm'])
    if not groups or groups[-1]['key'] != key:
        groups.append(dict(key=key, rows=[]))
    groups[-1]['rows'].append(row)
motion = []
for group in groups:
    if not any(group['key'][2]):
        continue
    all_rows = group['rows']
    steady = [r for r in all_rows if r['stm_t_ms'] - all_rows[0]['stm_t_ms'] >= 500]
    med = [statistics.median(abs(r['cps'][i]) for r in steady) for i in (0, 1)]
    motion.append(dict(command=group['key'][1], pwm=group['key'][2],
        source_samples=len(all_rows), steady_samples=len(steady),
        steady_abs_cps_median=med,
        right_left_ratio=None if not med[0] else med[1]/med[0],
        steady_zero_cps_counts=[sum(r['cps'][i] == 0 for r in steady) for i in (0, 1)]))
out = dict(test='GROUND_STRAIGHT_TRIM_RUN01', motion=motion,
    telemetry_dropped=report['telemetry_dropped'], unique_source_samples=len(rows),
    unexpected_stop_capture=report['captured'],
    drop_err_values=sorted(set((r['drop'], r['err']) for r in rows)),
    final_tel=rows[-1],
    visual='No video or explicit curvature observation supplied for this run; forward/reverse ground test follows preceding instruction.',
    limits=['CPS measures encoder rotation, not motor torque or ground velocity.',
            'Both encoders remained nonzero after the first 500ms. Forward and reverse wheel-rate mismatch differs; curvature requires physical observation.',
            'CPS ratios are initial tuning evidence; PWM-to-speed response, battery voltage, load and track slip prevent treating them as calibrated gains.'])
(here/'observations.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
print(json.dumps(motion, indent=2))
