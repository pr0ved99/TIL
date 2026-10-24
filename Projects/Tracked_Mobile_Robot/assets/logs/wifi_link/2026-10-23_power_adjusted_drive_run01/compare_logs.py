"""Read-only comparison of retained browser evidence; never controls hardware."""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def stats(values):
    values = sorted(v for v in values if isinstance(v, (int, float)))
    if not values:
        return None

    def quantile(q):
        index = (len(values) - 1) * q
        low = int(index)
        return round(values[low] + (values[min(low + 1, len(values) - 1)] - values[low]) * (index - low), 3)

    return {'samples': len(values), 'median_ms': quantile(.5), 'p95_ms': quantile(.95),
            'p99_ms': quantile(.99), 'max_ms': round(values[-1], 3),
            'gaps_ge_200_ms': sum(v >= 200 for v in values),
            'gaps_ge_250_ms': sum(v >= 250 for v in values)}


def summarize(data):
    telemetry, history = data['telemetry'], data['recent_events']
    moving = [t for t in telemetry if t['command'] != [0, 0]]
    controls = [e for e in history if e['event'] == 'CONTROL_RX']
    segments, durations = collections.Counter(), collections.defaultdict(float)
    previous = None
    for a, b in zip(telemetry, telemetry[1:]):
        command = tuple(a['command'])
        durations[str(command)] += (b['ms'] - a['ms']) / 1000
        if command != previous and command != (0, 0):
            segments[str(command)] += 1
        previous = command
    bound = [a['stm_age_ms'] + b['ms'] - a['ms'] for a, b in zip(telemetry, telemetry[1:])]
    return {
        'telemetry_span_s': round((telemetry[-1]['ms'] - telemetry[0]['ms']) / 1000, 3),
        'history_span_s': round((history[-1]['ms'] - history[0]['ms']) / 1000, 3),
        'telemetry_samples': len(telemetry), 'history_samples': len(history),
        'history_first_ms': history[0]['ms'], 'telemetry_first_ms': telemetry[0]['ms'],
        'history_dropped': data['history_dropped'], 'telemetry_dropped': data['telemetry_dropped'],
        'tel_receive_gap': stats(t.get('gap_ms') for t in telemetry[1:]),
        'moving_tel_receive_gap': stats(t.get('gap_ms') for t in moving),
        'control_receive_gap': stats(e.get('gap_ms') for e in controls),
        'stm_age_at_esp': stats(t['stm_age_ms'] for t in telemetry),
        'tel_age_interarrival_upper_bound_max_ms': round(max(bound), 3),
        'tel_age_bound_note': 'Previous advertised STM age plus time until next TEL arrival; excludes after final sample, not a sampled controlTick value.',
        'nonzero_command_segments': dict(segments),
        'sampled_command_seconds': {k: round(v, 3) for k, v in durations.items()},
        'duration_note': 'Zero-order hold of browser TEL command labels; not exact physical movement time.',
        'boot_ids': sorted(set(t['boot_id'] for t in telemetry)),
        'drop_values': sorted(set(t['drop'] for t in telemetry)),
        'err_values': sorted(set(t['err'] for t in telemetry)),
        'connections_seen': data['observer']['connections_seen'],
        'trace_errors': data['observer']['trace_errors'],
        'connection_events': [e for e in history if e['event'] in ['APP_DISCONNECT', 'WS_OPEN', 'WS_CLOSE', 'WS_ERROR']],
        'timer_delays': [e for e in history if e['event'] == 'TIMER_DELAY'],
        'stops': [{k: s.get(k) for k in ['ms', 'intent', 'focused', 'motion', 'motionReady', 'offer_age_ms', 'tel_local_age_ms', 'stack']} for s in data['stops']],
        'observer_final_state': data['observer']['state'],
    }


def main():
    data = read(HERE / 'browser_report.json.gz')
    result = {'date': '2026-10-23', 'status': 'IMPROVED_DELIVERY_OBSERVED_POWER_CAUSALITY_UNRESOLVED',
              'user_report': '두 보드 전원공급 세팅 끝내고 연결하니깐 5.02V 찍힘. 문제 있었던 로그랑 비교해봐.',
              'new_run': summarize(data), 'previous_trigger_windows': {}}
    for label in ['forward', 'left']:
        folder = HERE.parent / f'2026-10-23_{label}_auto_disarm_run01'
        old = read(folder / 'browser_report.json.gz')
        snapshot = read(folder / 'trigger_snapshot.json')
        observation = read(folder / 'observations.json')
        near = [e for e in old['recent_events'] if abs(e['ms'] - snapshot['ms']) <= 1500]
        result['previous_trigger_windows'][label] = {
            'window': 'trigger +/-1500ms; not independent whole-run latency statistics',
            'tel_receive_gap_max_ms': round(max(e['gap_ms'] or 0 for e in near if e['event'] == 'TEL_RX'), 3),
            'control_receive_gap_max_ms': round(max(e['gap_ms'] or 0 for e in near if e['event'] == 'CONTROL_RX'), 3),
            'browser_trigger': observation['browser_trigger'],
            'retained_whole_log': summarize(old),
        }
    history, telemetry = data['recent_events'], data['telemetry']
    disarm = [e for e in history if e['event'] == 'command_result' and e['data'].get('cmd') == 'DISARM']
    last = disarm[-1]
    final = telemetry[-1]
    stopped = [t for t in telemetry if t['last_seq'] == last['data']['seq'] and t['state'] == 'DISARMED']
    assert last['data']['status'] == 'OK'
    assert all(t['command'] == t['pwm'] == t['cps'] == [0, 0] and
               (t['left_count'], t['right_count']) == (final['left_count'], final['right_count']) for t in stopped)
    source = ROOT / '03_Firmware/esp32_wifi_link/main/wifi_link_main.c'
    result['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    result['final_stop'] = {
        'cause': 'Window focus loss; motion already null and command/PWM/CPS already zero before stopLocal.',
        'disarm_result': last, 'final_tel': final,
        'fixed_stopped_stm_s': round((stopped[-1]['stm_t_ms'] - stopped[0]['stm_t_ms']) / 1000, 3),
        'focused_held_motion_stops': sum(bool(s['intent'] and s['focused'] and s['motion']) for s in data['stops']),
        'cmd_cancelled': [e for e in history if e['event'] == 'command_result' and e['data'].get('status') == 'CANCELLED'],
        'timing_note': 'Browser arrival times are not physical stop latency.'}
    result['power_observations'] = {
        'connected_boards_voltage_user_report_v': 5.02,
        'exact_probe_points_restated': False,
        'requested_no_load_target_v': 5.10,
        'final_no_load_actual_v': None,
        'preceding_dummy_load': {'buck_out_v': 5.00, 'usb_display_v': [4.85, 4.87],
                                 'usb_current_a': .93, 'cc_led_user_report': 'off'},
        'before_adjustment_report': {'unloaded_v': 5.03, 'boards_connected_v': 4.96},
        'electrical_transients_recorded': False, 'current_limit_setting_a': None,
        'note': 'User-reported observations, not voltage samples synchronized with browser logs. LED interpretation assumes the supplied diagram matches and the LED works.'}
    result['limits'] = [
        'New TEL window 153s; control/send/event history starts at38.4s after3600 events were evicted. ARM click/result is not retained there.',
        'Old left cumulative report includes earlier forward event; old reports are not independent samples.',
        'New boot ID differs, so restart/reconnection accompanied voltage adjustment. Wi-Fi/host conditions and repeated matched runs are not controlled.',
        'Steady TEL p95 is about90ms before and after; improvement is absence of prior long outliers in this observed run.',
        'No brownout/3.3V waveform/boot-reason evidence or exact target image readback. A local source hash is not runtime-image proof.',
        'No voltage-causality conclusion, continuous-operation acceptance, thermal acceptance or distance-accuracy claim.',
        'No MCU source/threshold edit, build, flash or additional physical test performed by this analysis.'
    ]
    conditions = HERE / 'session_observations.json'
    if conditions.exists():
        result['reported_session_conditions'] = read(conditions)
    (HERE / 'comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'new_run': {k: v for k, v in result['new_run'].items() if k in ['telemetry_span_s', 'tel_receive_gap', 'moving_tel_receive_gap', 'control_receive_gap', 'nonzero_command_segments']},
                      'final_stop_fixed_s': result['final_stop']['fixed_stopped_stm_s'],
                      'focused_held_motion_stops': result['final_stop']['focused_held_motion_stops'],
                      'source_sha256': result['source_sha256']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
