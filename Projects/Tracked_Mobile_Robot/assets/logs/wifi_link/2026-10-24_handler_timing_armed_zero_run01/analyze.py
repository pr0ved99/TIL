"""Reproduce the retained v5.2 ARM-zero evidence offline; no robot access."""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import math
import runpy

HERE = Path(__file__).resolve().parent
# Shared descriptive statistics from the immediately preceding baseline.
stats = runpy.run_path(str(HERE.parent / '2026-10-24_handler_timing_idle_run01'
                          / 'analyze.py'))['stats']


def payload(event):
    parts = event['text'].split(',')
    return dict(cmd=parts[0], **{k: int(v) for k, v in
                               (part.split('=', 1) for part in parts[1:])})


def main():
    manifest = json.loads((HERE / 'source_manifest.json').read_text(encoding='utf-8'))
    archive = (HERE / manifest['archive']).read_bytes()
    raw = gzip.decompress(archive)
    assert len(raw) == manifest['raw_bytes']
    assert hashlib.sha256(raw).hexdigest() == manifest['raw_sha256']
    assert hashlib.sha256(archive).hexdigest() == manifest['archive_sha256']
    d = json.loads(raw.decode('utf-8-sig'))
    h, t, mt = d['recent_events'], d['telemetry'], d['message_timing']
    rows = mt['rows']
    c = [e for e in h if e['event'] == 'CONTROL_RX']
    sends = [dict(e, payload=payload(e)) for e in h if e['event'] == 'WS_SEND']
    results = [e for e in h if e['event'] == 'command_result']
    notices = [e for e in h if e['event'] == 'command_notice']
    commands = [e for e in sends if e['payload']['cmd'] == 'CMD']
    arm, = [e for e in sends if e['payload']['cmd'] == 'ARM']
    disarm, = [e for e in sends if e['payload']['cmd'] == 'DISARM']
    click, = [e for e in h if e['event'] == 'BUTTON_CLICK' and e['button'] == 'disarm']
    active_at = next(e['ms'] for e in c if e['phase'] == 'ACTIVE')
    active_end = disarm['ms']
    active_t = [e for e in t if active_at <= e['ms'] < active_end]
    active_c = [e for e in c if active_at <= e['ms'] < active_end]
    active_rows = [r for r in rows if active_at <= r[2] < active_end]
    stopped_t = next(e for e in t if e['ms'] >= active_end and e['state'] == 'DISARMED')
    idle_c = next(e for e in c if e['ms'] >= active_end and e['phase'] == 'IDLE')
    send_map = {e['payload']['request_id']: e for e in sends}
    result_map = {e['data']['request_id']: e for e in results}
    notice_map = {e['data']['request_id']: e for e in notices}
    assert d['observer_revision'] == '5.2-handler-timing'
    assert mt['columns'] == ['rx_sequence', 'connection_id', 'handler_enter_ms',
                            'handler_exit_ms', 'observer_enter_ms', 'observer_exit_ms',
                            'kind_code', 'esp_uptime_ms']
    assert len(rows) == mt['written'] == len(t) + len(c) + len(results) + len(notices)
    assert all(len(r) == 8 and all(isinstance(x, (int, float)) and math.isfinite(x)
                                 for x in r[:7]) for r in rows)
    assert all(r[2] <= r[3] <= r[4] <= r[5] and r[1] == 1 for r in rows)
    assert [r[0] for r in rows] == list(range(1, len(rows) + 1))
    assert mt['overwritten'] == mt['missing_handler_pairs'] == 0
    assert d['history_dropped'] == d['telemetry_dropped'] == d['observer']['trace_errors'] == 0
    assert d['observer']['connections_seen'] == 1 and d['captured'] is None
    assert len(send_map) == len(sends) == len(results) == len(notices)
    assert set(send_map) == set(result_map) == set(notice_map)
    assert list(send_map) == list(range(1, len(sends) + 1))
    assert all(not e['failed'] for e in sends)
    for rid, send in send_map.items():
        result, notice = result_map[rid], notice_map[rid]
        assert result['data']['cmd'] == notice['data']['cmd'] == send['payload']['cmd']
        assert result['data']['status'] == 'OK'
        assert notice['data']['stage'] == 'ACCEPTED' and notice['data']['reason'] == 'QUEUED'
        assert result['ms'] >= send['ms'] and notice['ms'] >= send['ms']
    assert all(e['payload']['vx_mmps'] == e['payload']['w_mradps'] == 0 for e in commands)
    assert all(e['command'] == e['pwm'] == e['cps'] == [0, 0] for e in t)
    counts = sorted({(e['left_count'], e['right_count']) for e in t})
    assert len(counts) == 1 and all((e['drop'], e['err']) == (0, 0) for e in t)
    assert click['trusted'] and click['state']['focused'] and click['ms'] <= active_end
    assert all(not s['intent'] and s['motion'] is None and s['ms'] > idle_c['ms']
               for s in d['stops'])
    after = next(e['after'] for e in h if e['event'] == 'APP_COMMAND' and e['cmd'] == 'DISARM')
    assert not after['intent'] and all(after['buttons_disabled'][x]
                                     for x in ('forward', 'reverse', 'left', 'right'))
    edges = []
    for e in c:
        if not edges or edges[-1]['phase'] != e['phase']:
            edges.append({k: e[k] for k in ('ms', 'phase', 'control_reason')})
    assert [e['phase'] for e in edges] == ['IDLE', 'ARM_PENDING', 'ZERO_PENDING',
                                        'ACTIVE', 'STOPPING', 'IDLE']
    by_kind = {}
    for kind, name, events in [(1, 'STM_UART', [e for e in h if e['event'] == 'TEL_RX']),
                               (2, 'control_state', c), (3, 'command_notice', notices),
                               (4, 'command_result', results)]:
        selected = [r for r in rows if r[6] == kind]
        assert len(selected) == len(events)
        assert all(r[4] <= e['ms'] <= r[5] for r, e in zip(selected, events))
        if kind == 1:
            assert all(r[7] == e['esp_uptime_ms'] == sample['esp_uptime_ms']
                       and r[4] <= sample['ms'] <= e['ms']
                       for r, e, sample in zip(selected, events, t))
        by_kind[name] = {'handler_duration': stats(r[3] - r[2] for r in selected),
                         'observer_duration': stats(r[5] - r[4] for r in selected)}
    handler = stats(r[3] - r[2] for r in rows)
    observer = stats(r[5] - r[4] for r in rows)
    assert handler['max_ms'] == round(mt['retained_max_handler_ms'], 3)
    assert observer['max_ms'] == round(mt['retained_max_observer_ms'], 3)
    baseline = json.loads((HERE.parent / '2026-10-24_handler_timing_idle_run01'
                           / 'summary.json').read_text(encoding='utf-8'))
    result = {
        'date': '2026-10-24', 'status': 'ARM_ZERO_TIMING_CAPTURE_CONSISTENT_MANUAL_DISARM_CONFIRMED',
        'scope': 'ACC-COM-01 A active zero-command processing observation; not moving/physical stop acceptance',
        'raw_sha256': manifest['raw_sha256'],
        'capture_tel_span_s': round((t[-1]['ms'] - t[0]['ms']) / 1000, 3),
        'active_window_ms': [active_at, active_end],
        'active_to_disarm_send_s': round((active_end - active_at) / 1000, 3),
        'window_definition': 'First received ACTIVE control state inclusive to WS_SEND DISARM exclusive; active gap samples can begin just before window entry',
        'event_counts': dict(Counter(e['event'] for e in h)),
        'timing_metadata': {k: v for k, v in mt.items() if k != 'rows'},
        'handler_duration': handler, 'observer_duration': observer, 'by_kind': by_kind,
        'tel_receive_gap': stats(e['gap_ms'] for e in t),
        'control_receive_gap': stats(e['gap_ms'] for e in c),
        'active': {'timing_rows': len(active_rows), 'telemetry_samples': len(active_t),
                   'control_samples': len(active_c),
                   'handler_duration': stats(r[3] - r[2] for r in active_rows),
                   'observer_duration': stats(r[5] - r[4] for r in active_rows),
                   'tel_receive_gap': stats(e['gap_ms'] for e in active_t),
                   'control_receive_gap': stats(e['gap_ms'] for e in active_c),
                   'command_age': stats(e['command_age_ms'] for e in active_t)},
        'commands_sent': dict(Counter(e['payload']['cmd'] for e in sends)),
        'result_status': dict(Counter(e['data']['status'] for e in results)),
        'cmd_send_gap': stats(b['ms'] - a['ms'] for a, b in zip(commands, commands[1:])),
        'cmd_send_record_to_result_record': stats(e['ms'] - send_map[e['data']['request_id']]['ms']
                                                 for e in results if e['data']['cmd'] == 'CMD'),
        'phase_edges': edges, 'all_command_pwm_cps_zero': True, 'counts_fixed_at': list(counts[0]),
        'disarm': {'request_id': disarm['payload']['request_id'],
                   'seq': result_map[disarm['payload']['request_id']]['data']['seq'],
                   'trusted_click_ms': click['ms'], 'send_ms': active_end,
                   'click_to_send_ms': round(active_end - click['ms'], 3),
                   'send_to_result_ms': round(result_map[disarm['payload']['request_id']]['ms'] - active_end, 3),
                   'send_to_IDLE_ms': round(idle_c['ms'] - active_end, 3),
                   'send_to_DISARMED_TEL_ms': round(stopped_t['ms'] - active_end, 3),
                   'post_DISARMED_tel_span_s': round((t[-1]['ms'] - stopped_t['ms']) / 1000, 3),
                   'directions_disabled_after_command': True},
        'stops': [{k: s.get(k) for k in ('ms', 'intent', 'focused', 'motion', 'stack')}
                  for s in d['stops']],
        'observer_final': d['observer'],
        'checks': {'raw_archive_hashes_verified': True, 'all_timing_pairs_present': True,
                   'sequence_and_timestamp_order_valid': True, 'timing_events_matched': True,
                   'all_sent_commands_matched_to_OK_results_and_notices': True,
                   'all_outputs_zero_counts_fixed': True},
        'idle_reference': {k: baseline[k] for k in ('telemetry_span_s', 'handler_duration',
                           'observer_duration', 'tel_receive_gap', 'control_receive_gap')},
        'limits': ['No long-gap failure reproduced; past communication cause remains OPEN',
                   'No nonzero command or held-motion motionReady path exercised',
                   'Synchronous JS timing excludes pre-dispatch queueing and deferred layout/paint',
                   'Recorded zero duration is limited by clock resolution, not zero cost',
                   'Send/result intervals include multiple stages and are not pure network latency',
                   'DISARMED/IDLE response times are not physical stop latency; output was already zero',
                   'No new voltage/current measurement; no firmware/build/flash/limit changes'],
        'next': 'Subsequent forward capture is archived in ../2026-10-24_handler_timing_air_forward_run01. Three-condition observation block ended; no automatic repeat.',
    }
    (HERE / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)
                                      + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'capture_tel_span_s',
                     'active_to_disarm_send_s', 'commands_sent', 'result_status',
                     'disarm', 'checks')}, indent=2))


if __name__ == '__main__':
    main()
