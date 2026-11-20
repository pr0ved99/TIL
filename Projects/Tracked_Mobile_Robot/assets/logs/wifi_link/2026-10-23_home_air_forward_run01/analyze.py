"""Reproduce saved forward/release/manual-DISARM observations without robot access."""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent


def stats(values):
    values = sorted(v for v in values if isinstance(v, (int, float)))
    if not values:
        return None

    def q(f):
        pos = (len(values) - 1) * f
        lo = int(pos)
        return round(values[lo] + (values[min(lo + 1, len(values) - 1)]
                                  - values[lo]) * (pos - lo), 3)

    return dict(samples=len(values), min_ms=round(values[0], 3), median_ms=q(.5),
                p95_ms=q(.95), p99_ms=q(.99), max_ms=round(values[-1], 3),
                ge_200_ms=sum(v >= 200 for v in values),
                ge_250_ms=sum(v >= 250 for v in values))


def main():
    manifest = json.loads((HERE / 'source_manifest.json').read_text(encoding='utf-8'))
    packed = (HERE / 'browser_report.json.gz').read_bytes()
    raw = gzip.decompress(packed)
    assert hashlib.sha256(raw).hexdigest() == manifest['raw_sha256']
    assert hashlib.sha256(packed).hexdigest() == manifest['archive_sha256']
    data = json.loads(raw.decode('utf-8-sig'))
    history, tel = data['recent_events'], data['telemetry']
    controls = [e for e in history if e['event'] == 'CONTROL_RX']
    sends = [e for e in history if e['event'] == 'WS_SEND']
    results = [e for e in history if e['event'] == 'command_result']
    notices = [e for e in history if e['event'] == 'command_notice']
    send_by_key, parsed = {}, []
    for s in sends:
        fields = dict(item.split('=', 1) for item in s['text'].split(',')[1:])
        cmd = s['text'].split(',')[0]
        key = (int(fields['boot_id']), s['state']['session'], int(fields['request_id']))
        assert key not in send_by_key
        send_by_key[key] = s
        parsed.append((cmd, fields, s))
    arm = next(s for cmd, _, s in parsed if cmd == 'ARM')
    disarm = next(s for cmd, _, s in parsed if cmd == 'DISARM')
    forward_sends = [s for cmd, fields, s in parsed
                     if cmd == 'CMD' and fields['vx_mmps'] == '100']
    release = next(e for e in history if e['event'] == 'lostpointercapture'
                   and e.get('target') == 'forward')
    zero_send = next(s for cmd, fields, s in parsed if cmd == 'CMD'
                     and s['ms'] > release['ms'] and fields['vx_mmps'] == '0')
    zero_tel = next(t for t in tel if t['ms'] > release['ms']
                    and t['command'] == t['pwm'] == [0, 0])
    stationary = next(t for t in tel if t['ms'] > release['ms']
                      and t['command'] == t['pwm'] == t['cps'] == [0, 0])
    click = next(e for e in history if e['event'] == 'BUTTON_CLICK'
                 and e.get('button') == 'disarm')
    idle = next(c for c in controls if c['ms'] > disarm['ms'] and c['phase'] == 'IDLE')
    stopped_tel = next(t for t in tel if t['ms'] > disarm['ms'] and t['state'] == 'DISARMED')
    forward_tel = [t for t in tel if t['command'] == [100, 0]]
    forward_control = [c for c in controls if forward_tel[0]['ms'] <= c['ms'] < zero_tel['ms']]
    rtts = []
    for e in results:
        r = e['data']
        key = (r['boot_id'], r['session_id'], r['request_id'])
        s = send_by_key[key]
        rtts.append(dict(cmd=r['cmd'], request_id=r['request_id'], status=r['status'],
                         send_ms=s['ms'], result_ms=e['ms'],
                         round_trip_ms=round(e['ms'] - s['ms'], 3)))

    # These validate only this retained evidence set, not a firmware release.
    assert data['history_dropped'] == data['telemetry_dropped'] == 0
    assert len(sends) == len(results) == len({r['request_id'] for r in rtts})
    assert all(r['status'] == 'OK' and r['round_trip_ms'] >= 0 for r in rtts)
    assert all(not s['failed'] for s in sends)
    assert all(t['drop'] == t['err'] == 0 and t['encoder_valid'] for t in tel)
    assert all(t['pwm'] == [144, 150] and t['state'] == 'ARMED' and t['reason'] == 'NONE'
               for t in forward_tel)
    assert all(s['state']['intent'] and s['state']['focused']
               and s['state']['motion']['button'] == 'forward' for s in forward_sends)
    assert all(c['phase'] == 'ACTIVE' for c in forward_control)
    assert arm['ms'] < forward_sends[0]['ms'] < release['ms'] < zero_send['ms']
    assert zero_send['ms'] < zero_tel['ms'] < stationary['ms'] < click['ms'] <= disarm['ms']
    assert click['trusted'] and click['state']['focused'] and click['state']['intent']
    assert data['captured'] is None and not any(s['intent'] for s in data['stops'])
    assert all(e['event'] not in ('APP_DISCONNECT', 'WS_CLOSE', 'WS_ERROR', 'TIMER_DELAY')
               for e in history)
    final_counts = [tel[-1]['left_count'], tel[-1]['right_count']]
    assert all(t['command'] == t['pwm'] == t['cps'] == [0, 0]
               and [t['left_count'], t['right_count']] == final_counts
               for t in tel if t['ms'] >= stationary['ms'])
    assert all(t['state'] == 'DISARMED' and t['reason'] == 'DISARM'
               for t in tel if t['ms'] >= stopped_tel['ms'])
    assert all(disabled for key, disabled in data['observer']['state']['buttons_disabled'].items()
               if key in ('forward', 'reverse', 'left', 'right'))
    phase_changes, previous = [], None
    for c in controls:
        key = (c['phase'], c['control_reason'])
        if key != previous:
            phase_changes.append(c)
            previous = key
    proxies = [(a, b) for a, b in zip(tel, tel[1:])
               if forward_tel[0]['ms'] <= a['ms'] < b['ms'] < release['ms']]
    idle_ref = json.loads((HERE.parent / '2026-10-23_home_idle_baseline_run01/summary.json')
                          .read_text(encoding='utf-8'))
    zero_ref = json.loads((HERE.parent / '2026-10-23_home_armed_zero_run01/summary.json')
                          .read_text(encoding='utf-8'))
    summary = {
        'date': '2026-10-23',
        'status': 'BOUNDED_FORWARD_OBSERVATION_ACCEPTED_RELEASE_ZERO_AND_MANUAL_DISARM_CONFIRMED',
        'scope': 'Supported-tracks short forward communication comparison, not ground-load reliability acceptance',
        'capture_span_s': round((tel[-1]['ms'] - tel[0]['ms']) / 1000, 3),
        'first_forward_send_to_capture_release_s': round((release['ms'] - forward_sends[0]['ms']) / 1000, 3),
        'first_forward_tel_to_first_zero_tel_s': round((zero_tel['ms'] - forward_tel[0]['ms']) / 1000, 3),
        'forward_telemetry_samples': len(forward_tel), 'forward_send_count': len(forward_sends),
        'sample_counts': {'telemetry': len(tel), 'history': len(history), 'control': len(controls)},
        'history_dropped': data['history_dropped'], 'telemetry_dropped': data['telemetry_dropped'],
        'boot_ids': sorted({t['boot_id'] for t in tel}),
        'session_ids': sorted({c['session_id'] for c in controls}),
        'connections_seen': data['observer']['connections_seen'],
        'trace_errors': data['observer']['trace_errors'],
        'event_counts': dict(Counter(e['event'] for e in history)),
        'command_counts': dict(Counter(r['cmd'] for r in rtts)),
        'status_counts': dict(Counter(r['status'] for r in rtts)),
        'notice_stage_reason_counts': dict(Counter(e['data']['stage'] + '/' + e['data']['reason'] for e in notices)),
        'tel_receive_gap': stats(t['gap_ms'] for t in tel),
        'control_receive_gap': stats(c['gap_ms'] for c in controls),
        'forward_tel_receive_gap': stats(t['gap_ms'] for t in forward_tel),
        'forward_control_receive_gap': stats(c['gap_ms'] for c in forward_control),
        'forward_control_scope': 'First forward TEL arrival through first zero-command TEL arrival',
        'forward_esp_timestamp_step': stats(t['esp_step_ms'] for t in forward_tel),
        'forward_stm_age_at_esp': stats(t['stm_age_ms'] for t in forward_tel),
        'forward_command_age_at_stm_sample': stats(t['command_age_ms'] for t in forward_tel),
        'forward_stm_age_plus_next_interarrival_proxy': stats(a['stm_age_ms'] + b['ms'] - a['ms'] for a, b in proxies),
        'forward_command_age_plus_next_interarrival_proxy': stats(a['command_age_ms'] + b['ms'] - a['ms'] for a, b in proxies),
        'proxy_limit': 'Not controlTick samples; excludes after last selected TEL and release interval',
        'cmd_send_to_result_round_trip': stats(r['round_trip_ms'] for r in rtts if r['cmd'] == 'CMD'),
        'forward_cmd_send_to_result_round_trip': stats(r['round_trip_ms'] for r in rtts
                                                     if r['request_id'] in {s['state']['pending']['id'] for s in forward_sends}),
        'arm_round_trip': next(r for r in rtts if r['cmd'] == 'ARM'),
        'disarm_round_trip': next(r for r in rtts if r['cmd'] == 'DISARM'),
        'release_to_zero_send_observed_ms': round(zero_send['ms'] - release['ms'], 3),
        'release_to_zero_pwm_tel_observed_ms': round(zero_tel['ms'] - release['ms'], 3),
        'release_to_zero_cps_tel_observed_ms': round(stationary['ms'] - release['ms'], 3),
        'click_to_disarm_send_ms': round(disarm['ms'] - click['ms'], 3),
        'disarm_send_to_idle_observed_ms': round(idle['ms'] - disarm['ms'], 3),
        'disarm_send_to_disarmed_tel_observed_ms': round(stopped_tel['ms'] - disarm['ms'], 3),
        'post_disarmed_tel_span_s': round((tel[-1]['ms'] - stopped_tel['ms']) / 1000, 3),
        'final_counts': final_counts, 'phase_changes': phase_changes,
        'timeline': {'first_forward_send': forward_sends[0], 'last_forward_send': forward_sends[-1],
                     'capture_release': release, 'first_zero_send': zero_send,
                     'first_zero_pwm_tel': zero_tel, 'first_zero_cps_tel': stationary,
                     'disarm_click': click, 'disarm_send': disarm,
                     'first_idle': idle, 'first_disarmed_tel': stopped_tel},
        'observer_final_state': data['observer']['state'],
        'idle_reference': {k: idle_ref[k] for k in ('telemetry_span_s', 'tel_receive_gap', 'control_receive_gap')},
        'armed_zero_reference': {k: zero_ref[k] for k in ('active_until_focus_loss_s', 'active_tel_receive_gap',
                                                        'active_control_receive_gap', 'cmd_send_to_result_round_trip')},
        'limits': [
            'Supported-tracks setup follows instructions but was not independently observed; no ground-load claim',
            'Forward capture duration is about24s, not exactly20s; no distance measurement performed',
            'Capture-release event follows motion clear; raw forward pointer-up was not recorded, so physical release time is not directly measured',
            'Stop observations include command/telemetry transport and CPS sample-window delay; not exact mechanical stop latency',
            'DISARM result round trip is distinct from200ms control-state age threshold',
            'Same ESP boot, different application session and operating window; descriptive comparison only',
            'No new voltage/current/oscilloscope or brownout evidence, no voltage causality conclusion',
            'No direction-held automatic stop reproduced; old intermittent delay and manual-button incident remain OPEN',
            'No code, timeout, build or flash changes; no Git or external publication',
        ],
    }
    (HERE / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    keys = ('status', 'capture_span_s', 'first_forward_send_to_capture_release_s',
            'forward_tel_receive_gap', 'forward_control_receive_gap', 'cmd_send_to_result_round_trip',
            'disarm_round_trip', 'release_to_zero_send_observed_ms', 'release_to_zero_pwm_tel_observed_ms',
            'release_to_zero_cps_tel_observed_ms', 'disarm_send_to_idle_observed_ms',
            'disarm_send_to_disarmed_tel_observed_ms', 'post_disarmed_tel_span_s')
    print(json.dumps({k: summary[k] for k in keys}, indent=2))


if __name__ == '__main__':
    main()
