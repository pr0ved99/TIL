"""Analyze retained v5.2 forward capture offline; never contact the robot."""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import math
import runpy

HERE = Path(__file__).resolve().parent
helpers = runpy.run_path(str(HERE.parent / '2026-10-24_handler_timing_armed_zero_run01'
                            / 'analyze.py'))
stats, payload = helpers['stats'], helpers['payload']


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
    commands = [e for e in sends if e['payload']['cmd'] == 'CMD']
    forward = [e for e in commands if (e['payload']['vx_mmps'], e['payload']['w_mradps']) == (100, 0)]
    results = [e for e in h if e['event'] == 'command_result']
    notices = [e for e in h if e['event'] == 'command_notice']
    arm, = [e for e in sends if e['payload']['cmd'] == 'ARM']
    disarm, = [e for e in sends if e['payload']['cmd'] == 'DISARM']
    release, = [e for e in h if e['event'] == 'lostpointercapture' and e['target'] == 'forward']
    click, = [e for e in h if e['event'] == 'BUTTON_CLICK' and e['button'] == 'disarm']
    start, end = forward[0]['ms'], release['ms']
    ft = [e for e in t if start <= e['ms'] < end]
    fc = [e for e in c if start <= e['ms'] < end]
    fr = [r for r in rows if start <= r[2] < end]
    afterzero = next(e for e in commands if e['ms'] > end and
                     e['payload']['vx_mmps'] == e['payload']['w_mradps'] == 0)
    pwmzero = next(e for e in t if e['ms'] > end and e['pwm'] == [0, 0])
    cpszero = next(e for e in t if e['ms'] >= pwmzero['ms'] and e['cps'] == [0, 0])
    stopped = next(e for e in t if e['ms'] >= disarm['ms'] and e['state'] == 'DISARMED')
    idle = next(e for e in c if e['ms'] >= disarm['ms'] and e['phase'] == 'IDLE')
    post = [e for e in t if e['ms'] >= stopped['ms']]
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
    assert {(e['payload']['vx_mmps'], e['payload']['w_mradps']) for e in commands} == {(0, 0), (100, 0)}
    assert all(start <= e['ms'] < end for e in forward)
    assert all(e['state']['intent'] and e['state']['focused'] and
               e['state']['motion']['button'] == 'forward' for e in forward)
    assert all(e['payload']['vx_mmps'] == 100 for e in commands if start <= e['ms'] < end)
    assert release['state']['motion'] is None and release['state']['intent']
    assert all((e['drop'], e['err']) == (0, 0) and e['encoder_valid'] for e in t)
    forward_tel = [e for e in t if e['command'] == [100, 0]]
    assert all(e['state'] == 'ARMED' and e['reason'] == 'NONE' and e['pwm'] == [144, 150]
               for e in forward_tel)
    assert all(int(b[k]) >= int(a[k]) for a, b in zip(ft, ft[1:])
               for k in ('left_count', 'right_count'))
    negative_steps = []
    for a, b in zip(t, t[1:]):
        delta = [int(b[k]) - int(a[k]) for k in ('left_count', 'right_count')]
        if min(delta) < 0:
            negative_steps.append({'before_ms': a['ms'], 'after_ms': b['ms'],
                                   'delta_left_right': delta, 'command': b['command'],
                                   'pwm': b['pwm'], 'cps': b['cps'],
                                   'counts_after': [b['left_count'], b['right_count']]})
    assert all(e['command'] == e['pwm'] == e['cps'] == [0, 0] for e in post)
    assert len({(e['left_count'], e['right_count']) for e in post}) == 1
    assert click['trusted'] and click['state']['focused'] and end < click['ms'] <= disarm['ms']
    assert all(not s['intent'] and s['motion'] is None and s['ms'] > idle['ms'] for s in d['stops'])
    after = next(e['after'] for e in h if e['event'] == 'APP_COMMAND' and e['cmd'] == 'DISARM')
    assert not after['intent'] and all(after['buttons_disabled'][x]
                                     for x in ('forward', 'reverse', 'left', 'right'))
    edges = []
    for e in c:
        if not edges or edges[-1]['phase'] != e['phase']:
            edges.append({k: e[k] for k in ('ms', 'phase', 'control_reason')})
    assert [e['phase'] for e in edges] == ['IDLE', 'ARM_PENDING', 'ZERO_PENDING', 'ACTIVE', 'STOPPING', 'IDLE']
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
    comparison = {}
    for label, folder in [('idle', '2026-10-24_handler_timing_idle_run01'),
                           ('armed_zero', '2026-10-24_handler_timing_armed_zero_run01')]:
        ref = json.loads((HERE.parent / folder / 'summary.json').read_text(encoding='utf-8'))
        comparison[label] = {k: ref[k] for k in ('handler_duration', 'observer_duration',
                                                'tel_receive_gap', 'control_receive_gap')}
    result = {
        'date': '2026-10-24', 'status': 'FORWARD_TIMING_CAPTURE_CONSISTENT_MANUAL_RELEASE_AND_DISARM',
        'scope': 'ACC-COM-01 A v5.2 forward observation; no general reliability/ground-distance acceptance',
        'raw_sha256': manifest['raw_sha256'],
        'capture_tel_span_s': round((t[-1]['ms'] - t[0]['ms']) / 1000, 3),
        'forward_window_ms': [start, end], 'first_forward_send_to_release_s': round((end - start) / 1000, 3),
        'window_definition': 'First forward WS_SEND record to forward lostpointercapture with motion=null; not exact physical motion duration. Gap samples may begin before window entry.',
        'event_counts': dict(Counter(e['event'] for e in h)),
        'timing_metadata': {k: v for k, v in mt.items() if k != 'rows'},
        'handler_duration': handler, 'observer_duration': observer, 'by_kind': by_kind,
        'tel_receive_gap': stats(e['gap_ms'] for e in t), 'control_receive_gap': stats(e['gap_ms'] for e in c),
        'forward': {'timing_rows': len(fr), 'telemetry_samples': len(ft), 'control_samples': len(fc),
                    'handler_duration': stats(r[3] - r[2] for r in fr),
                    'observer_duration': stats(r[5] - r[4] for r in fr),
                    'tel_receive_gap': stats(e['gap_ms'] for e in ft),
                    'control_receive_gap': stats(e['gap_ms'] for e in fc),
                    'command_age': stats(e['command_age_ms'] for e in ft),
                    'commanded_forward_samples': len(forward_tel), 'pwm_per_mille': [144, 150]},
        'commands_sent': dict(Counter(e['payload']['cmd'] for e in sends)),
        'CMD_values': dict(Counter(str([e['payload']['vx_mmps'], e['payload']['w_mradps']]) for e in commands)),
        'result_status': dict(Counter(e['data']['status'] for e in results)),
        'cmd_send_gap': stats(b['ms'] - a['ms'] for a, b in zip(commands, commands[1:])),
        'cmd_send_record_to_result_record': stats(e['ms'] - send_map[e['data']['request_id']]['ms']
                                                 for e in results if e['data']['cmd'] == 'CMD'),
        'phase_edges': edges,
        'counts_first_last': [[t[0]['left_count'], t[0]['right_count']], [t[-1]['left_count'], t[-1]['right_count']]],
        'count_delta': [int(t[-1][k]) - int(t[0][k]) for k in ('left_count', 'right_count')],
        'negative_count_steps_whole_capture': negative_steps,
        'release_observations_ms': {'to_zero_CMD_send': round(afterzero['ms'] - end, 3),
                                    'to_zero_PWM_TEL': round(pwmzero['ms'] - end, 3),
                                    'to_zero_CPS_TEL': round(cpszero['ms'] - end, 3)},
        'disarm': {'request_id': disarm['payload']['request_id'],
                   'seq': result_map[disarm['payload']['request_id']]['data']['seq'],
                   'click_to_send_ms': round(disarm['ms'] - click['ms'], 3),
                   'send_to_result_ms': round(result_map[disarm['payload']['request_id']]['ms'] - disarm['ms'], 3),
                   'send_to_IDLE_ms': round(idle['ms'] - disarm['ms'], 3),
                   'send_to_DISARMED_TEL_ms': round(stopped['ms'] - disarm['ms'], 3),
                   'post_DISARMED_tel_span_s': round((t[-1]['ms'] - stopped['ms']) / 1000, 3),
                   'directions_disabled_after_command': True},
        'stops': [{k: s.get(k) for k in ('ms', 'intent', 'focused', 'motion', 'stack')} for s in d['stops']],
        'observer_final': d['observer'], 'previous_v5_2_captures': comparison,
        'checks': {'raw_archive_hashes_verified': True, 'all_timing_pairs_present': True,
                   'sequence_and_timestamp_order_valid': True, 'timing_events_matched': True,
                   'all_sent_commands_matched_to_OK_results_and_notices': True,
                   'counts_monotonic_within_forward_send_to_release_window': True,
                   'post_disarm_outputs_zero_counts_fixed': True},
        'limits': ['Prior long-gap failure was not reproduced; ACC-COM-01 cause remains OPEN',
                   'Synchronous JS durations exclude pre-dispatch queueing, deferred layout/paint and export',
                   'Zero-duration records reflect clock resolution, not zero cost',
                   'Send/result and release/TEL intervals are not pure network or physical stop latency',
                   'One right-count decrement of 1 after release/PWM zero; no waveform evidence to identify rebound versus signal error',
                   'No independent physical support, voltage/current/temperature or ground-distance measurement',
                   'No new firmware/build/flash/limit changes or overall MVP acceptance'],
        'next': 'End this three-condition observation block. No automatic repeat or ESP instrumentation B; continue from existing MVP acceptance boundaries in report39 without waiving MUST requirements.',
    }
    (HERE / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'capture_tel_span_s', 'first_forward_send_to_release_s',
                     'commands_sent', 'result_status', 'count_delta', 'release_observations_ms', 'disarm', 'checks')}, indent=2))


if __name__ == '__main__':
    main()
