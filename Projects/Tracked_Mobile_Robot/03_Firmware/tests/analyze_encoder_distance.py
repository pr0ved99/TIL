"""Offline observer-v5 distance estimates. No network, serial or motor I/O."""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re

U32 = (1 << 32) - 1
DEFAULT_MODEL = (Path(__file__).resolve().parents[2] /
    'assets/logs/wifi_link/2026-10-20_track_geometry_14t_revision/geometry_model.json')
SOURCE_FIELDS = ('boot_id', 'tel_count', 'stm_t_ms', 'command_age_ms', 'last_seq',
    'state', 'reason', 'command', 'pwm', 'cps', 'encoder_valid', 'encoder_t_ms',
    'left_count', 'right_count', 'encoder_arm_valid', 'encoder_arm_seq', 'drop', 'err')


def u32(value):
    return type(value) is int and 0 <= value <= U32


def local_ms(value):
    return (type(value) in (int, float) and 0 <= value <= (1 << 53) - 1
        and math.isfinite(value))


def count(text):
    if not isinstance(text, str) or not re.fullmatch(r'-?(0|[1-9][0-9]{0,18})', text) or text == '-0':
        raise ValueError('Count must be a canonical signed decimal string')
    value = int(text)
    if not -(1 << 63) <= value < (1 << 63):
        raise ValueError('Count outside int64 range')
    return value


def decimal_text(value, places=6):
    with localcontext() as ctx:
        ctx.prec = 80
        return format(Decimal(value.numerator) / Decimal(value.denominator), f'.{places}f')


def coefficient(model):
    pitch = Fraction(str(model['reported']['link_pitch_mm_approx']))
    teeth = model['previously_confirmed']['sprocket_teeth']
    cpr = model['previously_confirmed']['encoder_counts_per_output_rev']
    if pitch <= 0 or type(teeth) is not int or teeth <= 0 or type(cpr) is not int or cpr <= 0:
        raise ValueError('Positive pitch, integer tooth count and counts/rev required')
    return pitch * teeth / cpr


def schema_error(row):
    if not isinstance(row, dict) or not local_ms(row.get('ms')):
        return 'INVALID_ROW_OR_LOCAL_TIME'
    if not all(u32(row.get(k)) for k in ('boot_id', 'tel_count', 'stm_t_ms',
            'encoder_t_ms', 'encoder_arm_seq', 'last_seq', 'stm_age_ms', 'drop', 'err')):
        return 'INVALID_UINT32_METADATA'
    if type(row.get('encoder_valid')) is not bool or type(row.get('encoder_arm_valid')) is not bool:
        return 'INVALID_VALIDITY_FLAGS'
    if row.get('state') not in ('ARMED', 'DISARMED', 'FAULT') or not isinstance(row.get('reason'), str):
        return 'INVALID_STATE'
    for k in ('command', 'pwm', 'cps'):
        values = row.get(k)
        if not isinstance(values, list) or len(values) != 2 or not all(
                type(v) is int and -(1 << 31) <= v < (1 << 31) for v in values):
            return 'INVALID_COMMAND_OR_OUTPUT'
    if any(abs(v) > 1000 for v in row['pwm']):
        return 'INVALID_PWM'
    try:
        count(row.get('left_count'))
        count(row.get('right_count'))
    except ValueError:
        return 'INVALID_COUNT'
    return None


def endpoint(row):
    return {k: row[k] for k in ('ms', 'tel_count', 'stm_t_ms', 'encoder_t_ms',
        'left_count', 'right_count', 'state', 'reason', 'last_seq')}


def analyze(report, mm_per_count, *, source_limit_ms=200, local_limit_ms=250):
    """A broken ARM interval is rejected in full; only a new ARM can start again."""
    if not isinstance(report, dict) or report.get('version') != 5:
        raise ValueError('Observer version 5 required')
    rows, events = report.get('telemetry'), report.get('recent_events')
    if not isinstance(rows, list) or not isinstance(events, list):
        raise ValueError('telemetry and recent_events arrays required')
    if not isinstance(mm_per_count, Fraction) or mm_per_count <= 0 or source_limit_ms <= 0 or local_limit_ms <= 0:
        raise ValueError('Positive coefficient and freshness limits required')

    # Repeated status broadcasts must describe exactly the same STM TEL payload.
    payloads, conflicts = {}, set()
    for row in rows:
        if isinstance(row, dict) and u32(row.get('boot_id')) and u32(row.get('tel_count')):
            key = (row['boot_id'], row['tel_count'])
            payload = json.dumps([row.get(k) for k in SOURCE_FIELDS], sort_keys=True)
            if key in payloads and payloads[key] != payload:
                conflicts.add(key)
            payloads[key] = payload

    acks, ack_conflicts, ack_identity = {}, set(), {}
    timeline_events = []
    result_counts = Counter()
    for event in events:
        if not isinstance(event, dict) or not local_ms(event.get('ms')):
            raise ValueError('Malformed diagnostic event')
        if event.get('event') == 'CONTROL_RX':
            if event.get('phase') == 'BLOCKED' or (event.get('phase') == 'STOPPING'
                    and event.get('control_reason') != 1):
                timeline_events.append(event)
        if event.get('event') != 'command_result':
            continue
        data = event.get('data', {})
        if not isinstance(data, dict):
            raise ValueError('Malformed command result')
        result_counts[str(data.get('status'))] += 1
        if data.get('status') != 'OK' or data.get('cmd') not in ('ARM', 'DISARM'):
            continue
        if not u32(data.get('boot_id')) or not u32(data.get('seq')):
            raise ValueError('Malformed ARM/DISARM ACK identity')
        key = (data['boot_id'], data['cmd'], data['seq'])
        identity = (data.get('session_id'), data.get('request_id'), data.get('control_id'))
        if key in ack_identity and ack_identity[key] != identity:
            ack_conflicts.add(key)
        ack_identity[key] = identity
        if key not in acks or event['ms'] < acks[key]['ms']:
            acks[key] = event

    windows, done, diagnostics = [], set(), Counter()
    active = None
    previous_source = previous_row = None
    last_source_key = None
    seen = set()
    last_hazard_ms = -math.inf
    last_row_ms = -math.inf

    def reject(reason, row=None):
        nonlocal active
        diagnostics[reason] += 1
        if active is not None:
            active.update(status='REJECTED', reason=reason,
                end=endpoint(row) if row is not None else None)
            windows.append(active)
            done.add((active['boot_id'], active['arm_seq']))
            active = None

    # Keep source order, including malformed/backwards timestamps, rather than
    # sorting telemetry into an apparently continuous sequence.
    event_index = 0
    timeline_events.sort(key=lambda e: e['ms'])
    for row in rows:
        error = schema_error(row)
        if error:
            reject(error)
            if isinstance(row, dict) and local_ms(row.get('ms')):
                last_hazard_ms = max(last_hazard_ms, row['ms'])
            else:
                # Unknown ordering relative to ACKs cannot establish any later
                # baseline safely in this malformed capture.
                last_hazard_ms = math.inf
            continue
        now = row['ms']
        while event_index < len(timeline_events) and timeline_events[event_index]['ms'] <= now:
            event = timeline_events[event_index]
            reject('CONTROL_STOP_OR_BLOCKED')
            last_hazard_ms = max(last_hazard_ms, event['ms'])
            event_index += 1
        if now < last_row_ms:
            reject('LOCAL_TIME_BACKWARD', row)
            last_hazard_ms = max(last_hazard_ms, last_row_ms)
            continue
        last_row_ms = now
        if previous_row is not None and now - previous_row['ms'] > local_limit_ms:
            reject('BROWSER_RECEIVE_GAP', row)
            last_hazard_ms = now
        previous_row = row

        if row['stm_age_ms'] > source_limit_ms:
            reject('STALE_STM_TEL', row)
            last_hazard_ms = now
            continue
        source_key = (row['boot_id'], row['tel_count'])
        if source_key in conflicts:
            reject('CONFLICTING_SOURCE_TEL', row)
            last_hazard_ms = now
            continue
        if source_key in seen:
            if source_key != last_source_key:
                reject('REPLAYED_OLD_TEL', row)
                last_hazard_ms = now
            else:
                diagnostics['REPEATED_BROADCAST_IGNORED'] += 1
            continue
        seen.add(source_key)
        last_source_key = source_key

        boundary = None
        if previous_source is not None:
            old = previous_source
            if row['boot_id'] != old['boot_id']:
                boundary = 'ESP_BOOT_CHANGED'
            elif row['stm_t_ms'] <= old['stm_t_ms']:
                boundary = 'STM_TIME_BACKWARD_OR_WRAP'
            elif row['tel_count'] != old['tel_count'] + 1:
                boundary = 'SOURCE_TEL_GAP_OR_WRAP'
            elif row['stm_t_ms'] - old['stm_t_ms'] > source_limit_ms:
                boundary = 'STM_TEL_TIME_GAP'
            elif row['encoder_t_ms'] < old['encoder_t_ms']:
                boundary = 'ENCODER_TIME_BACKWARD_OR_WRAP'
            elif row['encoder_t_ms'] - old['encoder_t_ms'] > source_limit_ms:
                boundary = 'ENCODER_SAMPLE_GAP'
            elif (row['encoder_t_ms'] == old['encoder_t_ms'] and
                    row['encoder_valid'] and old['encoder_valid'] and
                    (row['left_count'], row['right_count']) != (old['left_count'], old['right_count'])):
                boundary = 'COUNT_CHANGED_WITHOUT_NEW_SAMPLE'
        previous_source = row
        if boundary:
            reject(boundary, row)
            last_hazard_ms = now

        arm_key = (row['boot_id'], row['encoder_arm_seq'])
        ack_key = (arm_key[0], 'ARM', arm_key[1])
        if active and (row['boot_id'], row['encoder_arm_seq']) != (active['boot_id'], active['arm_seq']):
            reject('ARM_INTERVAL_CHANGED', row)
        valid = row['encoder_valid'] and row['encoder_arm_valid']
        invalid_reason = ('FAULT' if row['state'] == 'FAULT' else
            'STM_DROP_OR_ERROR' if row['drop'] or row['err'] else
            'INVALID_SAMPLE_OR_ARM' if not valid else
            'INVALID_SAMPLE_TIME_OR_AGE' if not 0 <= row['stm_t_ms'] - row['encoder_t_ms'] <= source_limit_ms else None)
        if invalid_reason:
            had_active = active is not None
            reject(invalid_reason, row)
            # Pre-first-sample ARM invalidation is expected; it isn't a gap.
            if (invalid_reason != 'INVALID_SAMPLE_OR_ARM' or had_active or
                    any(row['command'] + row['pwm'] + row['cps'])):
                last_hazard_ms = now
            continue
        if active is None:
            if row['state'] != 'ARMED' or arm_key in done:
                continue
            ack = acks.get(ack_key)
            # A TEL may arrive just before the independently delivered ACK.
            if ack is not None and now < ack['ms']:
                continue
            reason = ('MISSING_OR_CONFLICTING_ARM_ACK' if ack is None or ack_key in ack_conflicts else
                'BASELINE_TOO_LATE_AFTER_ARM_ACK' if now - ack['ms'] > local_limit_ms else
                'NO_STATIONARY_ARM_BASELINE' if any(row['command'] + row['pwm'] + row['cps']) else
                'HAZARD_SINCE_ARM_ACK' if last_hazard_ms >= ack['ms'] else None)
            active = dict(boot_id=arm_key[0], arm_seq=arm_key[1], status='OPEN',
                reason=None, arm_ack_ms=ack['ms'] if ack else None,
                start=endpoint(row), end=None, source_samples=0,
                delta_count=None, distance_estimate_mm=None)
            if reason:
                reject(reason, row)
                continue
        active['source_samples'] += 1
        active['last_valid'] = endpoint(row)
        if row['state'] == 'DISARMED':
            disarm_key = (row['boot_id'], 'DISARM', row['last_seq'])
            disarm_ack = acks.get(disarm_key)
            if row['reason'] != 'DISARM':
                reject('DISARMED_WITHOUT_MANUAL_DISARM', row)
                continue
            if any(row['command'] + row['pwm'] + row['cps']):
                continue  # Wait for stopped endpoint, not the ACK alone.
            if (disarm_ack is None or disarm_key in ack_conflicts or
                    not active['arm_ack_ms'] <= disarm_ack['ms'] <= now):
                continue
            left = count(row['left_count']) - count(active['start']['left_count'])
            right = count(row['right_count']) - count(active['start']['right_count'])
            active.update(status='ACCEPTED', reason='ACKED_ARM_TO_STOPPED_DISARM',
                end=endpoint(row), disarm_seq=row['last_seq'],
                delta_count=dict(left=str(left), right=str(right)),
                distance_estimate_mm=dict(left=decimal_text(left * mm_per_count),
                    right=decimal_text(right * mm_per_count),
                    center=decimal_text(Fraction(left + right, 2) * mm_per_count)))
            windows.append(active)
            done.add(arm_key)
            active = None

    # A retained terminal control failure also invalidates an unfinished window.
    if active and event_index < len(timeline_events):
        reject('CONTROL_STOP_OR_BLOCKED')
    if active:
        reject('NO_ACKED_STOPPED_DISARM_ENDPOINT')
    evicted = report.get('telemetry_dropped', 0)
    return dict(format_version=1, observer_version=5,
        interpretation='Initial encoder-equivalent track travel; not measured chassis displacement',
        coefficient=dict(status='INITIAL_GEOMETRIC_NOT_GROUND_CALIBRATED',
            numerator=str(mm_per_count.numerator), denominator=str(mm_per_count.denominator),
            display_mm_per_count=decimal_text(mm_per_count, 12), same_initial_value_for_both_sides=True),
        policy=dict(stm_source_and_sample_limit_ms=source_limit_ms,
            browser_receive_gap_limit_ms=local_limit_ms,
            start='ACKed ARM plus first fresh stationary valid sample',
            end='ACKed DISARM plus first fresh valid zero-command/PWM/CPS sample',
            gaps='Reject whole ARM window; never resume it automatically'),
        summary=dict(telemetry_rows=len(rows), unique_source_tel=len(seen),
            browser_evicted_rows=evicted,
            accepted_windows=sum(w['status'] == 'ACCEPTED' for w in windows),
            rejected_windows=sum(w['status'] == 'REJECTED' for w in windows),
            command_result_status_counts=dict(result_counts)),
        diagnostics=dict(diagnostics), windows=windows,
        warnings=(['Older browser rows were evicted; this is not the STM UART drop counter'] if evicted else []),
        limitations=['No actual-distance calibration or physical stop-time measurement',
            'No window spans resets, source gaps, tick wrap or ARM identity changes',
            'Truncated ACK/baseline/endpoint evidence is not reconstructed',
            'Encoder displacement cannot detect track/surface or sprocket slip'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model', type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args()
    if args.output.resolve() in (args.input.resolve(), args.model.resolve()):
        parser.error('Output must differ from input and model')
    try:
        raw = args.input.read_bytes()
        model_raw = args.model.read_bytes()
        model = json.loads(model_raw.decode('utf-8-sig'))
        result = analyze(json.loads(raw.decode('utf-8-sig')), coefficient(model))
        result['input'] = dict(path=str(args.input), sha256=hashlib.sha256(raw).hexdigest())
        result['model'] = dict(path=str(args.model), sha256=hashlib.sha256(model_raw).hexdigest())
        result['model'].update(pitch_mm_nominal=model['reported']['link_pitch_mm_approx'],
            pitch_mm_reading_range=model['reported'].get('link_pitch_mm_range'),
            sprocket_teeth=model['previously_confirmed']['sprocket_teeth'],
            counts_per_output_rev=model['previously_confirmed']['encoder_counts_per_output_rev'])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f'Analysis failed: {error}\n')
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
