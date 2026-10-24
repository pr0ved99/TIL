"""Reproduce this v5.2 IDLE capture analysis offline; no robot access."""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent


def stats(values):
    values = sorted(v for v in values if isinstance(v, (int, float))
                    and math.isfinite(v))
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
                recorded_zero_samples=sum(v == 0 for v in values),
                samples_ge_200_ms=sum(v >= 200 for v in values),
                samples_ge_250_ms=sum(v >= 250 for v in values))


def main():
    manifest = json.loads((HERE / 'source_manifest.json').read_text(encoding='utf-8'))
    compressed = (HERE / manifest['archive']).read_bytes()
    raw = gzip.decompress(compressed)
    assert len(raw) == manifest['raw_bytes']
    assert hashlib.sha256(raw).hexdigest() == manifest['raw_sha256']
    assert hashlib.sha256(compressed).hexdigest() == manifest['archive_sha256']
    data = json.loads(raw.decode('utf-8-sig'))
    tel, history = data['telemetry'], data['recent_events']
    controls = [e for e in history if e['event'] == 'CONTROL_RX']
    tel_events = [e for e in history if e['event'] == 'TEL_RX']
    timing = data['message_timing']
    rows = timing['rows']
    assert data['observer_revision'] == '5.2-handler-timing'
    assert timing['columns'] == [
        'rx_sequence', 'connection_id', 'handler_enter_ms', 'handler_exit_ms',
        'observer_enter_ms', 'observer_exit_ms', 'kind_code', 'esp_uptime_ms']
    assert rows and tel and controls
    assert all(len(r) == 8 and all(isinstance(x, (int, float)) and math.isfinite(x)
                                 for x in r[:7]) for r in rows)
    tel_rows = [r for r in rows if r[6] == 1]
    control_rows = [r for r in rows if r[6] == 2]
    events = Counter(e['event'] for e in history)
    counts = sorted({(t['left_count'], t['right_count']) for t in tel})
    time_order_ok = all(r[2] <= r[3] <= r[4] <= r[5] for r in rows)
    sequence_ok = [r[0] for r in rows] == list(range(1, len(rows) + 1))
    assert time_order_ok and sequence_ok
    assert len(tel_rows) == len(tel_events) == len(tel)
    assert len(control_rows) == len(controls)
    assert len(rows) == len(tel) + len(controls) == timing['written']
    assert all(r[1] == 1 for r in rows)
    assert timing['overwritten'] == timing['missing_handler_pairs'] == 0
    assert data['history_dropped'] == data['telemetry_dropped'] == 0
    assert data['observer']['trace_errors'] == 0
    assert data['observer']['connections_seen'] == 1
    assert data['captured'] is None and not data['stops']
    assert set(events) == {'OBSERVER_SOCKET_CHANGE', 'CONTROL_RX', 'TEL_RX'}
    assert all(t['command'] == t['pwm'] == t['cps'] == [0, 0] for t in tel)
    assert len(counts) == 1
    assert all(t['state'] == 'DISARMED' and t['reason'] == 'DISARM' for t in tel)
    assert all(c['phase'] == 'IDLE' for c in controls)
    assert all((t['drop'], t['err']) == (0, 0) for t in tel)
    # Match by retained order and ESP timestamp, then check the diagnostic
    # event's internal timestamp lies inside its listener measurement.
    for row, sample, event in zip(tel_rows, tel, tel_events):
        assert row[7] == sample['esp_uptime_ms'] == event['esp_uptime_ms']
        assert row[4] <= sample['ms'] <= event['ms'] <= row[5]
    assert all(r[4] <= c['ms'] <= r[5] for r, c in zip(control_rows, controls))
    for samples in (tel, controls):
        assert samples[0]['gap_ms'] is None
        assert all(math.isclose(b['gap_ms'], b['ms'] - a['ms'], abs_tol=.5)
                   for a, b in zip(samples, samples[1:]))
    handler = stats(r[3] - r[2] for r in rows)
    observer = stats(r[5] - r[4] for r in rows)
    assert round(timing['retained_max_handler_ms'], 3) == handler['max_ms']
    assert round(timing['retained_max_observer_ms'], 3) == observer['max_ms']
    by_kind = {}
    for name, selected in [('STM_UART', tel_rows), ('control_state', control_rows)]:
        by_kind[name] = {
            'handler_duration': stats(r[3] - r[2] for r in selected),
            'observer_duration': stats(r[5] - r[4] for r in selected),
            'handler_entry_gap': stats(b[2] - a[2] for a, b in zip(selected, selected[1:])),
        }
    result = {
        'date': '2026-10-24',
        'status': 'IDLE_TIMING_CAPTURE_CONSISTENT_NO_LONG_GAP_OBSERVED',
        'scope': 'ACC-COM-01 A v5.2 IDLE instrumentation baseline, not active/motion acceptance',
        'raw_sha256': manifest['raw_sha256'],
        'telemetry_span_s': round((tel[-1]['ms'] - tel[0]['ms']) / 1000, 3),
        'first_last_tel_ms': [tel[0]['ms'], tel[-1]['ms']],
        'telemetry_samples': len(tel), 'control_samples': len(controls),
        'timing_metadata': {k: v for k, v in timing.items() if k != 'rows'},
        'checks': {'timestamp_order_valid': time_order_ok,
                   'sequence_contiguous': sequence_ok,
                   'timing_events_telemetry_matched': True,
                   'report_maxima_match_recalculation': True,
                   'raw_archive_sha256_verified': True},
        'handler_duration': handler, 'observer_duration': observer,
        'handler_exit_to_observer_entry': stats(r[4] - r[3] for r in rows),
        'handler_entry_to_observer_exit': stats(r[5] - r[2] for r in rows),
        'by_kind': by_kind,
        'tel_receive_gap': stats(t['gap_ms'] for t in tel),
        'control_receive_gap': stats(c['gap_ms'] for c in controls),
        'esp_timestamp_step': stats(t['esp_step_ms'] for t in tel),
        'stm_age_at_esp': stats(t['stm_age_ms'] for t in tel),
        'event_counts': dict(events),
        'observer_final': data['observer'],
        'history_dropped': data['history_dropped'],
        'telemetry_dropped': data['telemetry_dropped'],
        'boot_ids': sorted({t['boot_id'] for t in tel}),
        'control_sessions': sorted({c['session_id'] for c in controls}),
        'state_reason': dict(Counter(t['state'] + '/' + t['reason'] for t in tel)),
        'control_phases': dict(Counter(c['phase'] for c in controls)),
        'all_command_pwm_cps_zero': True, 'counts_fixed_at': list(counts[0]),
        'encoder_valid_values': sorted({t['encoder_valid'] for t in tel}),
        'encoder_arm_valid_values': sorted({t['encoder_arm_valid'] for t in tel}),
        'drop_err_values': sorted({(t['drop'], t['err']) for t in tel}),
        'captured': data['captured'], 'stop_count': len(data['stops']),
        'interpretation': [
            '6324 rows paired with original handlers; no capture drops, overwrite or trace errors',
            'Retained IDLE handler max 0.6ms and diagnostic listener max 0.3ms; no >=200ms TEL/control gap',
            'No ARM, CMD, DISARM, command_result or motion in this capture',
            'Final focused=false has no corresponding blur/stop event; do not infer a focus-loss DISARM',
            'Fixed encoder totals within this capture only; do not splice deltas across unrecorded intervals',
        ],
        'limits': [
            'No reproduction of the prior long-gap failure; its cause remains OPEN',
            'Synchronous handler durations exclude pre-dispatch waiting and deferred layout/paint',
            'Listener timing excludes final cell write/return, export and other diagnostic callbacks',
            'Recorded zero duration is bounded by clock resolution; not zero execution cost',
            'ESP and browser clocks are not synchronized; no absolute one-way network delay claim',
            'No new voltage/current/3.3V transient measurement or power-causality proof',
            'This analysis performs no firmware edits, build, flash, physical action or external publication',
        ],
        'next': 'Fresh v5.2 capture, supported tracks, ARM speed zero for 30s with robot page focused; manual DISARM then export. Do not use direction/distance controls.',
    }
    (HERE / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)
                                      + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'telemetry_span_s',
                     'handler_duration', 'observer_duration', 'tel_receive_gap',
                     'control_receive_gap', 'checks')}, indent=2))


if __name__ == '__main__':
    main()
