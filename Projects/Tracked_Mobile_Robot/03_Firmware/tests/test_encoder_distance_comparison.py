"""Synthetic external-distance comparisons; no new physical measurements."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from analyze_encoder_distance import analyze, compare_actual_distance, coefficient, DEFAULT_MODEL
from test_encoder_distance_analysis import fixture

SCRIPT = Path(__file__).with_name('analyze_encoder_distance.py')


class DistanceComparison(unittest.TestCase):
    def compare(self, result, actual, boot=1, arm=7):
        return compare_actual_distance(result, actual, boot_id=boot, arm_seq=arm)

    def test_forward_exact_zero_and_fractional_errors_without_mutation(self):
        result = analyze(fixture(), Fraction(1))
        before = deepcopy(result)
        comparison = self.compare(result, '25')
        self.assertEqual(comparison['distance_estimate_mm'],
                         dict(left='20.000000', right='40.000000', center='30.000000'))
        self.assertEqual(comparison['center_signed_error_mm'], '5.000000')
        self.assertEqual(comparison['center_absolute_error_percent'], '20.000000')
        self.assertEqual(self.compare(result, '30')['center_absolute_error_percent'], '0.000000')
        self.assertEqual(self.compare(result, '37.5')['center_signed_error_mm'], '-7.500000')
        self.assertEqual(result, before)

    def test_reverse_signed_displacement_and_wrong_sign_remain_visible(self):
        report = fixture()
        for row, n in zip(report['telemetry'], (0, -10, -30, -30)):
            row['left_count'] = row['right_count'] = str(n)
        report['telemetry'][1].update(command=[-100, 0], pwm=[-140, -150], cps=[-100, -100])
        result = analyze(report, Fraction(1))
        comparison = self.compare(result, '-25')
        self.assertEqual(comparison['center_signed_error_mm'], '-5.000000')
        self.assertEqual(comparison['center_absolute_error_mm'], '5.000000')
        self.assertEqual(comparison['center_absolute_error_percent'], '20.000000')
        self.assertEqual(self.compare(result, '25')['center_absolute_error_percent'], '220.000000')

    def test_percentage_uses_exact_fraction_not_display_rounding(self):
        comparison = self.compare(analyze(fixture(), Fraction(19, 260)), '2')
        self.assertEqual(comparison['center_absolute_error_percent'], '9.615385')

    def test_invalid_actual_distance_and_identity(self):
        result = analyze(fixture(), Fraction(1))
        for actual in ('0', '-0.000', 'NaN', 'Infinity', '1e3', '1/2', ' 25', '25mm',
                       '', '1' * 65, 25, None):
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                self.compare(result, actual)
        for boot, arm in ((True, 7), (-1, 7), (1, 1 << 32), (1, None)):
            with self.subTest(boot=boot, arm=arm), self.assertRaises(ValueError):
                self.compare(result, '25', boot, arm)

    def test_explicit_selection_across_boots_and_duplicate_or_missing_identity(self):
        result = analyze(fixture(), Fraction(1))
        second = deepcopy(result['windows'][0])
        second.update(boot_id=2, delta_count=dict(left='50', right='50'))
        result['windows'].append(second)
        self.assertEqual(self.compare(result, '25', boot=2)['center_signed_error_mm'], '25.000000')
        with self.assertRaises(ValueError):
            self.compare(result, '25', arm=8)
        result['windows'].append(deepcopy(second))
        with self.assertRaises(ValueError):
            self.compare(result, '25', boot=2)

    def test_arm_zero_is_a_valid_selector(self):
        report = fixture()
        report['recent_events'][0]['data']['seq'] = 0
        for row in report['telemetry']:
            row['encoder_arm_seq'] = 0
        self.assertEqual(self.compare(analyze(report, Fraction(1)), '25', arm=0)['arm_seq'], 0)

    def test_rejected_window_never_receives_error_result(self):
        report = fixture()
        report['telemetry'][1]['stm_age_ms'] = 201
        result = analyze(report, Fraction(1))
        before = deepcopy(result)
        with self.assertRaisesRegex(ValueError, 'not ACCEPTED'):
            self.compare(result, '25')
        self.assertEqual(result, before)

    def test_cli_comparison_and_default_output_preservation(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / 'synthetic_observer.json'
            output = Path(folder) / 'comparison.json'
            source.write_text(json.dumps(fixture()), encoding='utf-8')
            before = source.read_bytes()
            command = [sys.executable, str(SCRIPT), str(source), '--output', str(output)]
            baseline = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            old = json.loads(output.read_text(encoding='utf-8'))
            run = subprocess.run(command + ['--actual-distance-mm', '2.5',
                '--boot-id', '1', '--arm-seq', '7', '--measurement-note', 'synthetic fixture only'],
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            new = json.loads(output.read_text(encoding='utf-8'))
            comparison = new.pop('external_distance_comparison')
            self.assertEqual(new, old)
            self.assertEqual(comparison['measurement']['note'], 'synthetic fixture only')
            self.assertEqual(comparison['center_absolute_error_percent'], '3.815385')
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(old['coefficient']['numerator'], '1687')

    def test_cli_invalid_comparison_preserves_existing_output_and_input(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / 'synthetic_observer.json'
            output = Path(folder) / 'comparison.json'
            report = fixture()
            source.write_text(json.dumps(report), encoding='utf-8')
            valid_selectors = ['--boot-id', '1', '--arm-seq', '7']
            for flags in (['--actual-distance-mm', '25'],
                          ['--boot-id', '1', '--arm-seq', '7'],
                          ['--actual-distance-mm', 'NaN'] + valid_selectors,
                          ['--actual-distance-mm', '25', '--boot-id', '2', '--arm-seq', '7']):
                output.write_text('keep-existing-output', encoding='utf-8')
                run = subprocess.run([sys.executable, str(SCRIPT), str(source),
                    '--output', str(output)] + flags, capture_output=True, text=True)
                self.assertEqual(run.returncode, 2, run.stderr)
                self.assertEqual(output.read_text(encoding='utf-8'), 'keep-existing-output')
                self.assertEqual(json.loads(source.read_text(encoding='utf-8')), report)
            run = subprocess.run([sys.executable, str(SCRIPT), str(source), '--output', str(source),
                '--actual-distance-mm', '25'] + valid_selectors, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2, run.stderr)
            self.assertEqual(json.loads(source.read_text(encoding='utf-8')), report)


if __name__ == '__main__':
    unittest.main()
