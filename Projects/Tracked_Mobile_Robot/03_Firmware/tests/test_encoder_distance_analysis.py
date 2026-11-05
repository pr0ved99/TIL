"""Distance-window integrity and replay of archived physical captures (PC only)."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import unittest

from analyze_encoder_distance import analyze, coefficient, count, DEFAULT_MODEL

ROOT = Path(__file__).resolve().parents[2]
# Preserve the original12-tooth arithmetic fixture and archived regression values.
K = Fraction(19, 260)


def ack(cmd, seq, ms, *, boot=1, request=1):
    return dict(ms=ms, event='command_result', data=dict(kind='command_result',
        boot_id=boot, session_id=1, request_id=request, cmd=cmd, seq=seq,
        control_id=0 if cmd == 'DISARM' else 1, status='OK'))


def fixture():
    rows = []
    for i in range(4):
        moving = i == 1
        rows.append(dict(ms=100 * (i + 1), boot_id=1, tel_count=i + 1,
            stm_t_ms=1000 + 100 * i, encoder_t_ms=990 + 100 * i,
            stm_age_ms=10, command_age_ms=10, last_seq=9 if i == 3 else 7,
            state='DISARMED' if i == 3 else 'ARMED', reason='DISARM' if i == 3 else 'NONE',
            command=[100, 0] if moving else [0, 0],
            pwm=[144, 150] if moving else [0, 0], cps=[100, 200] if moving else [0, 0],
            left_count=str(100 + 10 * min(i, 2)), right_count=str(200 + 20 * min(i, 2)),
            encoder_valid=True, encoder_arm_valid=True, encoder_arm_seq=7, drop=0, err=0))
    return dict(version=5, telemetry=rows, telemetry_dropped=0,
        recent_events=[ack('ARM', 7, 90), ack('DISARM', 9, 390, request=2)])


def accepted(result):
    return [w for w in result['windows'] if w['status'] == 'ACCEPTED']


class DistanceAnalysis(unittest.TestCase):
    def rejection(self, report, reason):
        result = analyze(report, K)
        self.assertFalse(accepted(result))
        self.assertIn(reason, result['diagnostics'])
        self.assertTrue(all(w['distance_estimate_mm'] is None for w in result['windows']))

    def test_model_and_delta_formula(self):
        self.assertEqual(coefficient(json.loads(DEFAULT_MODEL.read_text(encoding='utf-8'))), Fraction(1687, 19500))
        r = fixture()
        before = deepcopy(r)
        w, = accepted(analyze(r, K))
        self.assertEqual(w['delta_count'], dict(left='20', right='40'))
        self.assertEqual(w['distance_estimate_mm'], dict(left='1.461538', right='2.923077', center='2.192308'))
        self.assertEqual(r, before)

    def test_count_grammar_and_int64_bounds(self):
        self.assertEqual(count('-9223372036854775808'), -(1 << 63))
        self.assertEqual(count('9223372036854775807'), (1 << 63) - 1)
        for value in ('+1', '01', '-0', ' 1', '1.0', '1e3', '9223372036854775808',
                      '-9223372036854775809', 9007199254740993, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                count(value)

    def test_large_counts_never_pass_through_float(self):
        for baseline in (9007199254740993, (1 << 63) - 4, -(1 << 63)):
            r = fixture()
            for row, offset in zip(r['telemetry'], (0, 1, 3, 3)):
                row['left_count'] = row['right_count'] = str(baseline + offset)
            w, = accepted(analyze(r, K))
            self.assertEqual(w['delta_count'], dict(left='3', right='3'))
            self.assertEqual(w['distance_estimate_mm']['center'], '0.219231')

    def test_reverse_crosses_zero(self):
        r = fixture()
        for row, n in zip(r['telemetry'], (10, 3, -5, -5)):
            row['left_count'] = row['right_count'] = str(n)
        r['telemetry'][1].update(command=[-100, 0], pwm=[-140, -150], cps=[-70, -70])
        w, = accepted(analyze(r, K))
        self.assertEqual(w['delta_count']['left'], '-15')
        self.assertEqual(w['distance_estimate_mm']['center'], '-1.096154')

    def test_arm_sequence_zero_is_valid(self):
        r = fixture()
        r['recent_events'][0]['data']['seq'] = 0
        for row in r['telemetry']:
            row['encoder_arm_seq'] = 0
        self.assertEqual(accepted(analyze(r, K))[0]['arm_seq'], 0)

    def test_expected_pre_first_arm_sample_invalidation(self):
        r = fixture()
        row = deepcopy(r['telemetry'][0])
        row.update(ms=95, tel_count=0, stm_t_ms=990, encoder_t_ms=980,
            encoder_valid=False, encoder_arm_valid=False, encoder_arm_seq=0)
        r['telemetry'].insert(0, row)
        self.assertEqual(len(accepted(analyze(r, K))), 1)

    def test_motion_during_initial_invalid_sample_cannot_be_omitted(self):
        r = fixture()
        row = deepcopy(r['telemetry'][0])
        row.update(ms=95, tel_count=0, stm_t_ms=990, encoder_t_ms=980,
            encoder_valid=False, encoder_arm_valid=False, encoder_arm_seq=0,
            command=[100, 0], pwm=[144, 150])
        r['telemetry'].insert(0, row)
        self.rejection(r, 'HAZARD_SINCE_ARM_ACK')

    def test_repeated_broadcast_ignored_and_source_counter_wrap_rejected(self):
        r = fixture()
        repeated = deepcopy(r['telemetry'][1]); repeated['ms'] = 220; repeated['stm_age_ms'] = 30
        r['telemetry'].insert(2, repeated)
        result = analyze(r, K)
        self.assertEqual(len(accepted(result)), 1)
        self.assertEqual(result['diagnostics']['REPEATED_BROADCAST_IGNORED'], 1)
        r = fixture(); r['telemetry'][1]['tel_count'] = 0
        self.rejection(r, 'SOURCE_TEL_GAP_OR_WRAP')

    def test_conflicting_duplicate_rejects_even_if_conflict_arrives_later(self):
        r = fixture()
        row = deepcopy(r['telemetry'][1]); row.update(ms=450, left_count='111')
        r['telemetry'].append(row)
        self.rejection(r, 'CONFLICTING_SOURCE_TEL')

    def test_source_gap_no_automatic_resume(self):
        r = fixture()
        for row in r['telemetry'][1:]: row['tel_count'] += 1
        self.rejection(r, 'SOURCE_TEL_GAP_OR_WRAP')

    def test_stale_duplicate_breaks_interval(self):
        r = fixture()
        row = deepcopy(r['telemetry'][1]); row.update(ms=250, stm_age_ms=201)
        r['telemetry'].insert(2, row)
        self.rejection(r, 'STALE_STM_TEL')

    def test_browser_gap(self):
        r = fixture()
        for row in r['telemetry'][1:]: row['ms'] += 151
        self.rejection(r, 'BROWSER_RECEIVE_GAP')

    def test_source_time_gap(self):
        r = fixture()
        for row in r['telemetry'][1:]:
            row['stm_t_ms'] += 101; row['encoder_t_ms'] += 101
        self.rejection(r, 'STM_TEL_TIME_GAP')

    def test_reset_and_stm_tick_wrap(self):
        for tick in (5, 0):
            r = fixture()
            r['telemetry'][1].update(stm_t_ms=tick, encoder_t_ms=tick)
            self.rejection(r, 'STM_TIME_BACKWARD_OR_WRAP')

    def test_sample_time_backward_and_future(self):
        r = fixture(); r['telemetry'][1]['encoder_t_ms'] = 980
        self.rejection(r, 'ENCODER_TIME_BACKWARD_OR_WRAP')
        r = fixture(); r['telemetry'][1]['encoder_t_ms'] = 1101
        self.rejection(r, 'INVALID_SAMPLE_TIME_OR_AGE')

    def test_sample_gap(self):
        r = fixture(); r['telemetry'][0]['encoder_t_ms'] = 800
        self.rejection(r, 'ENCODER_SAMPLE_GAP')

    def test_same_sample_tick_cannot_change_counts(self):
        r = fixture(); r['telemetry'][1]['encoder_t_ms'] = 990
        self.rejection(r, 'COUNT_CHANGED_WITHOUT_NEW_SAMPLE')

    def test_mid_interval_invalid_sample_fault_and_uart_counters(self):
        for patch, reason in ((dict(encoder_valid=False), 'INVALID_SAMPLE_OR_ARM'),
                (dict(state='FAULT'), 'FAULT'), (dict(drop=1), 'STM_DROP_OR_ERROR'),
                (dict(err=1), 'STM_DROP_OR_ERROR')):
            r = fixture(); r['telemetry'][1].update(patch)
            self.rejection(r, reason)

    def test_no_stationary_baseline_or_late_baseline(self):
        r = fixture(); r['telemetry'] = r['telemetry'][1:]
        self.rejection(r, 'NO_STATIONARY_ARM_BASELINE')
        r = fixture(); r['recent_events'][0]['ms'] = 0
        for row in r['telemetry']: row['ms'] += 200
        self.rejection(r, 'BASELINE_TOO_LATE_AFTER_ARM_ACK')

    def test_missing_arm_ack_and_missing_disarm_ack(self):
        r = fixture(); r['recent_events'] = r['recent_events'][1:]
        self.rejection(r, 'MISSING_OR_CONFLICTING_ARM_ACK')
        r = fixture(); r['recent_events'] = r['recent_events'][:1]
        self.rejection(r, 'NO_ACKED_STOPPED_DISARM_ENDPOINT')

    def test_waits_for_cps_zero_after_disarm(self):
        r = fixture(); r['telemetry'][-1]['cps'] = [10, 20]
        end = deepcopy(r['telemetry'][-1]); end.update(ms=500, tel_count=5,
            stm_t_ms=1400, encoder_t_ms=1390, cps=[0, 0], left_count='121', right_count='242')
        r['telemetry'].append(end)
        w, = accepted(analyze(r, K))
        self.assertEqual(w['delta_count'], dict(left='21', right='42'))

    def test_no_disarm_endpoint(self):
        r = fixture(); r['telemetry'].pop()
        self.rejection(r, 'NO_ACKED_STOPPED_DISARM_ENDPOINT')

    def test_new_arm_cannot_extend_old_window(self):
        r = fixture(); r['telemetry'][-1].update(state='ARMED', reason='NONE', encoder_arm_seq=8)
        r['recent_events'] = [r['recent_events'][0], ack('ARM', 8, 390, request=3)]
        self.rejection(r, 'ARM_INTERVAL_CHANGED')

    def test_boot_change_no_bridge(self):
        r = fixture()
        for row in r['telemetry'][1:]: row['boot_id'] = 2
        self.rejection(r, 'ESP_BOOT_CHANGED')

    def test_control_fault_but_manual_stop_is_allowed(self):
        for phase, reason in (('BLOCKED', 0), ('STOPPING', 2), ('STOPPING', 0)):
            r = fixture();r['recent_events'].append(dict(ms=250, event='CONTROL_RX',
                phase=phase, control_reason=reason))
            self.rejection(r, 'CONTROL_STOP_OR_BLOCKED')
        r = fixture();r['recent_events'].append(dict(ms=350, event='CONTROL_RX',
            phase='STOPPING', control_reason=1))
        self.assertEqual(len(accepted(analyze(r, K))), 1)

    def test_old_source_replay_and_local_time_backward(self):
        r = fixture(); row=deepcopy(r['telemetry'][0]);row['ms']=250
        r['telemetry'].insert(2,row); self.rejection(r, 'REPLAYED_OLD_TEL')
        r = fixture();r['telemetry'][2]['ms']=150
        self.rejection(r, 'LOCAL_TIME_BACKWARD')

    def test_malformed_count_and_flag_cannot_be_skipped_over(self):
        for patch, reason in ((dict(left_count=110.0), 'INVALID_COUNT'),
                (dict(encoder_valid=1), 'INVALID_VALIDITY_FLAGS')):
            r = fixture();r['telemetry'][1].update(patch)
            self.rejection(r, reason)

    def test_conflicting_ack_identity(self):
        r = fixture();r['recent_events'].append(ack('ARM',7,91,request=99))
        self.rejection(r, 'MISSING_OR_CONFLICTING_ARM_ACK')

    def test_fail_closed_for_bad_report_and_bad_coefficient(self):
        for r in ({}, dict(version=4), dict(version=5,telemetry=None,recent_events=[])):
            with self.assertRaises(ValueError): analyze(r,K)
        with self.assertRaises(ValueError): analyze(fixture(),Fraction(0))

    def test_unbounded_or_nonfinite_local_time_is_rejected(self):
        for timestamp in (10**1000, float('inf'), float('nan'), -1, True):
            r = fixture();r['telemetry'][1]['ms'] = timestamp
            self.rejection(r, 'INVALID_ROW_OR_LOCAL_TIME')

    def test_missing_time_before_first_baseline_is_not_silently_ignored(self):
        r = fixture(); r['telemetry'].insert(0, {'left_count': '0'})
        self.rejection(r, 'HAZARD_SINCE_ARM_ACK')

    def replay(self, name, k=K):
        path=ROOT/f'assets/logs/wifi_link/2026-10-20_encoder_count_{name}_run01/browser_report.json'
        before=hashlib.sha256(path.read_bytes()).hexdigest()
        result=analyze(json.loads(path.read_text(encoding='utf-8')),k)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
        return result

    def test_physical_zero_capture(self):
        w,=accepted(self.replay('arm_zero'))
        self.assertEqual(w['delta_count'],dict(left='0',right='0'))

    def test_physical_forward_capture(self):
        w,=accepted(self.replay('forward_air'))
        self.assertEqual(w['arm_seq'],525914493)
        self.assertEqual(w['delta_count'],dict(left='2567',right='2374'))
        self.assertEqual(w['distance_estimate_mm']['center'],'180.536538')

    def test_physical_reverse_capture_and_old_evicted_ack(self):
        result=self.replay('reverse_air');w,=accepted(result)
        self.assertEqual(w['delta_count'],dict(left='-2925',right='-2717'))
        self.assertEqual(w['distance_estimate_mm']['center'],'-206.150000')
        old=next(x for x in result['windows'] if x['arm_seq']==525914493)
        self.assertEqual(old['reason'],'MISSING_OR_CONFLICTING_ARM_ACK')
        self.assertIsNone(old['distance_estimate_mm'])
        self.assertEqual(result['summary']['command_result_status_counts']['CANCELLED'],1)

    def test_corrected14_tooth_model_replays_same_raw_counts(self):
        model=json.loads(DEFAULT_MODEL.read_text(encoding='utf-8'))
        k=coefficient(model)
        for name, center in (('arm_zero','0.000000'),('forward_air','213.729923'),
                             ('reverse_air','-244.052667')):
            old,=accepted(self.replay(name,K))
            new,=accepted(self.replay(name,k))
            self.assertEqual(old['delta_count'],new['delta_count'])
            self.assertEqual(new['distance_estimate_mm']['center'],center)

    def test_pitch_reading_range_contains_nominal_without_empirical_fit(self):
        model=json.loads(DEFAULT_MODEL.read_text(encoding='utf-8'))
        low,high=map(lambda x:Fraction(str(x)),model['reported']['link_pitch_mm_range'])
        nominal=Fraction(str(model['reported']['link_pitch_mm_approx']))
        self.assertEqual(nominal,(low+high)/2)
        self.assertEqual(model['previously_confirmed']['sprocket_teeth'],14)
        self.assertLess(low*14/1560,coefficient(model))
        self.assertLess(coefficient(model),high*14/1560)


if __name__ == '__main__':
    unittest.main(verbosity=2)
