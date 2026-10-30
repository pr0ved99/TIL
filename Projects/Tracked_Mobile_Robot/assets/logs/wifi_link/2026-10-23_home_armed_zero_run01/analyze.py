"""Analyze saved zero-speed ARM traffic. No hardware, build or firmware writes."""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent


def stats(values):
    values = sorted(v for v in values if isinstance(v, (int, float)))
    if not values:
        return None

    def q(fraction):
        pos = (len(values) - 1) * fraction
        lo = int(pos)
        return round(values[lo] + (values[min(lo + 1, len(values) - 1)]
                                  - values[lo]) * (pos - lo), 3)

    return {'samples': len(values), 'min_ms': round(values[0], 3),
            'median_ms': q(.5), 'p95_ms': q(.95), 'p99_ms': q(.99),
            'max_ms': round(values[-1], 3),
            'ge_200_ms': sum(v >= 200 for v in values),
            'ge_250_ms': sum(v >= 250 for v in values)}


def main():
    manifest = json.loads((HERE / 'source_manifest.json').read_text(encoding='utf-8'))
    packed = (HERE / 'browser_report.json.gz').read_bytes()
    raw = gzip.decompress(packed)
    assert hashlib.sha256(raw).hexdigest() == manifest['raw_sha256']
    assert hashlib.sha256(packed).hexdigest() == manifest['archive_sha256']
    data = json.loads(raw.decode('utf-8-sig'))
    tel, history = data['telemetry'], data['recent_events']
    controls = [e for e in history if e['event'] == 'CONTROL_RX']
    sends = [e for e in history if e['event'] == 'WS_SEND']
    results = [e for e in history if e['event'] == 'command_result']
    notices = [e for e in history if e['event'] == 'command_notice']
    arm = next(e for e in sends if e['text'].startswith('ARM,'))
    disarm = next(e for e in sends if e['text'].startswith('DISARM,'))
    stop = next(s for s in data['stops'] if s['intent'])
    active = next(c for c in controls if c['ms'] > arm['ms'] and c['phase'] == 'ACTIVE')
    idle = next(c for c in controls if c['ms'] > disarm['ms'] and c['phase'] == 'IDLE')
    stopped_tel = next(t for t in tel if t['ms'] > disarm['ms'] and t['state'] == 'DISARMED')
    blur = next(e for e in history if e['event'] == 'blur'
                and e.get('window_target') and e['ms'] >= stop['ms'])
    active_tel = [t for t in tel if active['ms'] <= t['ms'] < stop['ms']]
    active_control = [c for c in controls if active['ms'] <= c['ms'] < stop['ms']]
    cmd_sends = [s for s in sends if s['text'].startswith('CMD,')]
    send_by_key = {}
    for s in sends:
        fields = dict(field.split('=', 1) for field in s['text'].split(',')[1:])
        if s['text'].startswith('CMD,'):
            assert fields['vx_mmps'] == fields['w_mradps'] == '0'
            assert s['state']['intent'] and s['state']['focused']
            assert s['state']['motion'] is None
        key = (int(fields['boot_id']), s['state']['session'], int(fields['request_id']))
        assert key not in send_by_key
        send_by_key[key] = s

    rtts = []
    for r in results:
        message = r['data']
        key = (message['boot_id'], message['session_id'], message['request_id'])
        s = send_by_key.get(key)
        rtts.append({'request_id': message['request_id'], 'cmd': message['cmd'],
                     'status': message['status'], 'send_ms': s['ms'] if s else None,
                     'result_ms': r['ms'],
                     'round_trip_ms': r['ms'] - s['ms'] if s else None})
    assert len(rtts) == len(sends) == len(send_by_key)
    assert all(r['round_trip_ms'] is not None and r['round_trip_ms'] >= 0 for r in rtts)
    assert len({r['request_id'] for r in rtts}) == len(rtts)
    arm_result = next(r for r in rtts if r['cmd'] == 'ARM')
    disarm_result = next(r for r in rtts if r['cmd'] == 'DISARM')
    phase_changes, previous = [], None
    for c in controls:
        current = (c['phase'], c['control_reason'])
        if current != previous:
            phase_changes.append(c)
            previous = current

    # Validate the retained interval; these assertions do not generalize to a release.
    assert arm['ms'] < active['ms'] < stop['ms'] <= disarm['ms'] < idle['ms']
    assert history[0]['ms'] < arm['ms'] and tel[0]['ms'] < arm['ms']
    assert all(t['command'] == t['pwm'] == t['cps'] == [0, 0] for t in tel)
    assert all((t['left_count'], t['right_count']) == ('0', '0') for t in tel)
    assert all(t['state'] == 'ARMED' and t['reason'] == 'NONE' for t in active_tel)
    assert all(c['phase'] == 'ACTIVE' for c in active_control)
    assert all(r['status'] == 'OK' for r in rtts)
    assert all(s['failed'] is False for s in sends)
    assert len([s for s in sends if s['text'].startswith('ARM,')]) == 1
    assert len([s for s in sends if s['text'].startswith('DISARM,')]) == 1
    disarm_buttons = [e for e in history if e['event'].startswith('BUTTON_')
                      and e.get('button') == 'disarm']
    assert not disarm_buttons
    assert not stop['focused'] and stop['motion'] is None
    assert blur['ms'] - stop['ms'] < 5
    assert all(t['drop'] == t['err'] == 0 and t['encoder_valid'] for t in tel)

    project = HERE.parents[3]
    source = project / '03_Firmware/esp32_wifi_link/main/wifi_link_main.c'
    source_bytes = source.read_bytes()
    source_text = source_bytes.decode('utf-8')
    body = re.search(r'static const char PAGE\[\] =([\s\S]*?);\r?\n\r?\nstatic ',
                     source_text).group(1)
    page = ''.join(json.loads(s) for s in re.findall(r'"(?:\\.|[^"\\])*"', body))
    page_lines = page.splitlines()
    stack_line = int(re.search(r'http://[^\n]+/:(\d+):\d+', stop['stack']).group(1))
    callback = page_lines[stack_line - 1]
    assert "window.addEventListener('blur',()=>stopLocal(true));" in callback

    def age_proxy(field):
        pairs = [(a, b) for a, b in zip(tel, tel[1:])
                 if active['ms'] <= a['ms'] < b['ms'] < stop['ms']
                 and a[field] != 4294967295]
        return stats(a[field] + b['ms'] - a['ms'] for a, b in pairs)

    idle_summary = json.loads((HERE.parent / '2026-10-23_home_idle_baseline_run01'
                              / 'summary.json').read_text(encoding='utf-8'))
    idle_raw = gzip.decompress((HERE.parent / '2026-10-23_home_idle_baseline_run01'
                               / 'browser_report.json.gz').read_bytes())
    idle_data = json.loads(idle_raw.decode('utf-8-sig'))
    assert idle_data['stops'] and data['stops'][0] == idle_data['stops'][0]
    summary = {
        'date': '2026-10-23',
        'status': 'RETAINED_ARMED_ZERO_INTERVAL_ACCEPTED_FOCUS_LOSS_DISARM_CONFIRMED',
        'scope': 'Zero-speed command/response observation, not movement or manual DISARM acceptance',
        'active_until_focus_loss_s': round((stop['ms'] - active['ms']) / 1000, 3),
        'arm_send_until_focus_loss_s': round((stop['ms'] - arm['ms']) / 1000, 3),
        'telemetry_retained_span_s': round((tel[-1]['ms'] - tel[0]['ms']) / 1000, 3),
        'history_retained_span_s': round((history[-1]['ms'] - history[0]['ms']) / 1000, 3),
        'retained_history_first_last_ms': [history[0]['ms'], history[-1]['ms']],
        'retained_telemetry_first_last_ms': [tel[0]['ms'], tel[-1]['ms']],
        'history_dropped': data['history_dropped'],
        'telemetry_dropped': data['telemetry_dropped'],
        'arm_to_disarm_interval_retained': True,
        'same_recorder_as_idle_baseline': True,
        'samples': {'tel': len(tel), 'control': len(controls),
                    'active_tel': len(active_tel), 'active_control': len(active_control)},
        'active_tel_receive_gap': stats(t['gap_ms'] for t in active_tel),
        'active_control_receive_gap': stats(c['gap_ms'] for c in active_control),
        'active_esp_timestamp_step': stats(t['esp_step_ms'] for t in active_tel),
        'active_command_age_at_stm_sample': stats(t['command_age_ms'] for t in active_tel
                                                  if t['command_age_ms'] != 4294967295),
        'active_stm_age_at_esp': stats(t['stm_age_ms'] for t in active_tel),
        'active_stm_age_plus_next_interarrival_proxy': age_proxy('stm_age_ms'),
        'active_command_age_plus_next_interarrival_proxy': age_proxy('command_age_ms'),
        'age_proxy_limit': 'Not sampled by controlTick; excludes time after final selected TEL and stop interval',
        'command_counts': dict(Counter(r['cmd'] for r in rtts)),
        'result_status_counts': dict(Counter(r['status'] for r in rtts)),
        'notice_stage_reason_counts': dict(Counter(e['data']['stage'] + '/' + e['data']['reason']
                                                   for e in notices)),
        'cmd_send_intervals': stats(b['ms'] - a['ms'] for a, b in zip(cmd_sends, cmd_sends[1:])),
        'cmd_send_to_result_round_trip': stats(r['round_trip_ms'] for r in rtts if r['cmd'] == 'CMD'),
        'top_cmd_round_trips': sorted((r for r in rtts if r['cmd'] == 'CMD'),
                                     key=lambda r: r['round_trip_ms'], reverse=True)[:5],
        'arm_round_trip': arm_result, 'disarm_round_trip': disarm_result,
        'disarm_send_to_idle_observed_ms': round(idle['ms'] - disarm['ms'], 3),
        'disarm_send_to_disarmed_tel_observed_ms': round(stopped_tel['ms'] - disarm['ms'], 3),
        'post_disarmed_tel_retained_s': round((tel[-1]['ms'] - stopped_tel['ms']) / 1000, 3),
        'stop': stop, 'window_blur': blur,
        'stack_source_crosscheck': {'source': str(source.relative_to(project)),
                                   'source_sha256': hashlib.sha256(source_bytes).hexdigest(),
                                   'embedded_page_sha256': hashlib.sha256(page.encode('utf-8')).hexdigest(),
                                   'page_line': stack_line, 'callback': callback,
                                   'limit': 'Matches local PAGE and captured stack; not a new board firmware readback'},
        'phase_changes': phase_changes,
        'event_counts': dict(Counter(e['event'] for e in history)),
        'all_retained_command_pwm_cps_zero': True,
        'counts_fixed_at': ['0', '0'], 'drop_err_values': [[0, 0]],
        'boot_ids': sorted({t['boot_id'] for t in tel}),
        'control_session_ids': sorted({c['session_id'] for c in controls}),
        'connections_seen': data['observer']['connections_seen'],
        'observer_trace_errors': data['observer']['trace_errors'],
        'disarm_button_events': len(disarm_buttons),
        'observer_final_state': data['observer']['state'],
        'idle_reference': {k: idle_summary[k] for k in ('telemetry_span_s', 'tel_receive_gap',
                                                      'control_receive_gap')},
        'interpretation': [
            'User reports no manual DISARM; no DISARM button event is retained',
            'Stop snapshot was unfocused while intent true, motion null, with fresh control and TEL',
            'Stack points to window blur handler; original handler runs before diagnostic blur recorder',
            'DISARM request 726 was sent and returned OK, followed by IDLE and DISARMED telemetry',
            'No unexpected ACTIVE interruption before focus loss in the retained ARM interval',
        ],
        'limits': [
            'Bounded buffers trimmed earlier IDLE history; not a full ten-minute continuous evidence set',
            'Not a fresh recorder or independent baseline trial; old IDLE sample overlaps this report',
            'No manual DISARM click tested; old manual-button issue remains OPEN',
            'No motor driving, electrical waveform or new supply-voltage measurement',
            'Zero-speed motion=null path does not exercise motionReady TEL/command-age gates as held direction does',
            'Round trips combine browser, ESP, UART/STM and return transport; they do not locate latency cause',
            'No timeout/code/build/flash change; no Git or external publication performed',
        ],
    }
    (HERE / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n',
                                      encoding='utf-8')
    keys = ('status', 'active_until_focus_loss_s', 'command_counts', 'result_status_counts',
            'active_tel_receive_gap', 'active_control_receive_gap',
            'active_command_age_at_stm_sample', 'cmd_send_intervals',
            'cmd_send_to_result_round_trip', 'arm_round_trip', 'disarm_round_trip',
            'disarm_send_to_idle_observed_ms', 'disarm_send_to_disarmed_tel_observed_ms',
            'post_disarmed_tel_retained_s', 'stack_source_crosscheck')
    print(json.dumps({key: summary[key] for key in keys}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
