"""Analyze retained IDLE browser evidence only; no robot or firmware access."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent


def stats(values):
    values = sorted(v for v in values if isinstance(v, (int, float)))
    if not values:
        return None

    def quantile(q):
        index = (len(values) - 1) * q
        low = int(index)
        return round(values[low] + (values[min(low + 1, len(values) - 1)]
                                   - values[low]) * (index - low), 3)

    return dict(samples=len(values), min_ms=round(values[0], 3),
                median_ms=quantile(.5), p95_ms=quantile(.95),
                p99_ms=quantile(.99), max_ms=round(values[-1], 3),
                gaps_ge_200_ms=sum(v >= 200 for v in values),
                gaps_ge_250_ms=sum(v >= 250 for v in values))


def main():
    raw = gzip.decompress((HERE / 'browser_report.json.gz').read_bytes())
    manifest = json.loads((HERE / 'source_manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(raw).hexdigest() == manifest['raw_sha256']
    data = json.loads(raw.decode('utf-8-sig'))
    tel, history = data['telemetry'], data['recent_events']
    controls = [e for e in history if e['event'] == 'CONTROL_RX']
    assert tel and controls
    # Readback consistency, not a general release or reliability assertion.
    assert all(t['command'] == t['pwm'] == t['cps'] == [0, 0] for t in tel)
    assert all((t['left_count'], t['right_count']) == ('0', '0') for t in tel)
    assert all(t['state'] == 'DISARMED' and t['reason'] == 'DISARM' for t in tel)
    assert all(c['phase'] == 'IDLE' for c in controls)
    assert data['telemetry_dropped'] == data['history_dropped'] == 0
    events = Counter(e['event'] for e in history)
    age_bound = max(a['stm_age_ms'] + b['ms'] - a['ms']
                    for a, b in zip(tel, tel[1:]))
    top = sorted(tel[1:], key=lambda t: t['gap_ms'], reverse=True)[:5]
    comparison = json.loads((HERE.parent / '2026-10-23_power_adjusted_drive_run01'
                             / 'comparison.json').read_text(encoding='utf-8'))
    previous = comparison['new_run']
    result = {
        'date': '2026-10-23',
        'status': 'IDLE_BASELINE_CAPTURE_ACCEPTED_NO_LONG_GAP_OBSERVED',
        'scope': 'DISARMED/IDLE no-motion receive baseline; not ACTIVE command/drive acceptance',
        'telemetry_samples': len(tel), 'control_samples': len(controls),
        'telemetry_span_s': round((tel[-1]['ms'] - tel[0]['ms']) / 1000, 3),
        'capture_first_last_ms': [tel[0]['ms'], tel[-1]['ms']],
        'tel_receive_gap': stats(t.get('gap_ms') for t in tel),
        'control_receive_gap': stats(c.get('gap_ms') for c in controls),
        'esp_timestamp_step': stats(t.get('esp_step_ms') for t in tel),
        'stm_age_at_esp': stats(t['stm_age_ms'] for t in tel),
        'stm_age_plus_interarrival_upper_bound_max_ms': round(age_bound, 3),
        'age_bound_scope': 'Previous reported STM age plus next browser interarrival; excludes after final TEL; not measured controlTick age or one-way latency',
        'boot_ids': sorted({t['boot_id'] for t in tel}),
        'connections_seen': data['observer']['connections_seen'],
        'observer_trace_errors': data['observer']['trace_errors'],
        'history_dropped': data['history_dropped'],
        'telemetry_dropped': data['telemetry_dropped'],
        'event_counts': dict(events),
        'drop_err_values': sorted({(t['drop'], t['err']) for t in tel}),
        'encoder_valid_values': sorted({t['encoder_valid'] for t in tel}),
        'encoder_arm_valid_values': sorted({t['encoder_arm_valid'] for t in tel}),
        'command_age_values': sorted({t['command_age_ms'] for t in tel}),
        'all_command_pwm_cps_zero': True, 'counts_fixed_at': ['0', '0'],
        'state_reason': dict(Counter(t['state'] + '/' + t['reason'] for t in tel)),
        'control_phases': dict(Counter(c['phase'] for c in controls)),
        'top_tel_gaps': [{k: t[k] for k in ('ms', 'gap_ms', 'esp_uptime_ms',
                         'esp_step_ms', 'stm_age_ms', 'tel_count', 'stm_t_ms')}
                         for t in top],
        'stops': [{k: s.get(k) for k in ('ms', 'intent', 'focused', 'motion',
                   'sendStop', 'tel_local_age_ms')} for s in data['stops']],
        'observer_final_state': data['observer']['state'],
        'previous_adjusted_drive_reference': {
            'telemetry_span_s': previous['telemetry_span_s'],
            'tel_receive_gap': previous['tel_receive_gap'],
            'control_receive_gap': previous['control_receive_gap'],
            'note': 'Different boot/session, duration and operating state; descriptive comparison only',
        },
        'interpretation': [
            'No >=200ms TEL/control receive gap in retained idle capture',
            'ESP timestamps advance 58..62ms while browser arrivals vary; aggregate does not identify ESP send queue, network, TCP or browser as cause',
            'One focus-loss stop callback occurred with intent false and motion null; no command send/result events; not an unexpected driving DISARM',
            'command_age UINT32_MAX and encoder_arm_valid false are compatible with no ARM/CMD in this capture',
        ],
        'limits': [
            'No active command or ACK path exercised; no motion/power under load assessment',
            'No new supply voltage/current/3.3V transient measurement',
            'No synchronized host/ESP clock or per-stage send/receive timestamps; not absolute one-way latency',
            'No firmware/timeout change, build, flash, physical action, Git or external publication by this script',
        ],
    }
    (HERE / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)
                                      + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'telemetry_span_s',
                     'tel_receive_gap', 'control_receive_gap',
                     'stm_age_plus_interarrival_upper_bound_max_ms')}, indent=2))


if __name__ == '__main__':
    main()
