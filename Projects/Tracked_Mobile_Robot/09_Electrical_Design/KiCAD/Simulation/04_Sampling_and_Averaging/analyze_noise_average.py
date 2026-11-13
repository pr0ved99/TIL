"""Analyze lab B's saved KiCad CSV without running a simulator or adding noise.

Samples at 0.5 ms, 1.0 ms, ... 10 s; 200 samples per nonoverlapping block.
Rounded duplicate CSV times are retained. A sample must lie on a constant
plateau, not across the random source's transition, to be accepted.
"""
import argparse
import bisect
import csv
import hashlib
import json
import math
from pathlib import Path

K = 6.747204164780444
FS, N, STOP = 2000, 200, 10.0
BIAS = 0.005
SIGNALS = ('VADC', 'VRAW', 'VRAW_BIAS')


def describe(values):
    origin = values[0]
    mean = origin + math.fsum(v - origin for v in values) / len(values)
    return dict(count=len(values), mean_V=mean,
                population_sd_V=math.sqrt(math.fsum((v - mean) ** 2 for v in values) / len(values)),
                minimum_V=min(values), maximum_V=max(values))


def read_source(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        first = stream.readline()
        delimiter = max((';', ',', '\t'), key=first.count)
        stream.seek(0)
        reader = csv.reader(stream, delimiter=delimiter)
        header = [v.strip().lower().replace(' ', '') for v in next(reader)]
        required = ['time'] + [f'v(/{s.lower()})' for s in SIGNALS]
        try:
            indices = [header.index(c) for c in required]
        except ValueError as exc:
            raise ValueError('Export time, V(/VADC), V(/VRAW), V(/VRAW_BIAS)') from exc
        rows = []
        for line, cells in enumerate(reader, 2):
            if not cells or all(not c.strip() for c in cells):
                continue
            try:
                row = tuple(float(cells[i]) for i in indices)
            except (IndexError, ValueError) as exc:
                raise ValueError(f'Invalid row {line}') from exc
            if not all(math.isfinite(v) for v in row):
                raise ValueError(f'Nonfinite value at row {line}')
            if rows and row[0] < rows[-1][0]:
                raise ValueError(f'Time decreases at row {line}')
            rows.append(row)
    if len(rows) < 2 or abs(rows[0][0]) > 1e-12 or abs(rows[-1][0] - STOP) > 1e-9:
        raise ValueError('Lab B needs the complete 0..10 second export')
    gaps = [b[0] - a[0] for a, b in zip(rows, rows[1:])]
    if max(gaps) > 100e-6 + 1e-12:
        raise ValueError('CSV has a large time gap; inspect the export/TRAN settings')
    if max(abs(r[1] - 12 / K) for r in rows) > 6e-6:
        raise ValueError('VADC is not the expected constant 12V/K within export rounding')
    max_bias_error = max(abs(r[3] - r[2] - BIAS) for r in rows)
    if max_bias_error > 20e-6:
        raise ValueError('VRAW_BIAS minus VRAW differs from 5mV beyond the CSV guard')
    audit = dict(csv_rows=len(rows), time_start_s=rows[0][0], time_stop_s=rows[-1][0],
                 duplicate_time_rows=sum(gap == 0 for gap in gaps), maximum_time_gap_s=max(gaps),
                 maximum_bias_relation_error_V=max_bias_error,
                 bias_relation_export_guard_V=20e-6)
    return rows, audit


def plateau_sample(rows, times, at):
    left = bisect.bisect_left(times, at)
    right = bisect.bisect_right(times, at)
    if left != right:
        values = rows[left][1:]
        if any(any(abs(a - b) > 1e-12 for a, b in zip(values, r[1:])) for r in rows[left:right]):
            raise ValueError(f'Ambiguous duplicate timestamp at sample {at}')
        return values
    if left == 0 or left == len(times):
        raise ValueError(f'Sample {at} outside CSV coverage')
    previous, following = rows[left - 1], rows[left]
    if any(abs(a - b) > 1e-12 for a, b in zip(previous[1:], following[1:])):
        raise ValueError(f'Sample {at} crosses a transition; do not average edge interpolation')
    # Linear interpolation on an audited constant plateau equals either endpoint.
    return previous[1:]


def calculate(rows):
    times = [r[0] for r in rows]
    samples = [(index, index / FS, *plateau_sample(rows, times, index / FS))
               for index in range(1, round(STOP * FS) + 1)]
    blocks = []
    for start in range(0, len(samples), N):
        segment = samples[start:start + N]
        means = [math.fsum(s[c] for s in segment) / N for c in (2, 3, 4)]
        blocks.append((start // N + 1, segment[-1][1], *means))
    summaries = {}
    for c, name in enumerate(SIGNALS, 2):
        raw, avg = describe([s[c] for s in samples]), describe([b[c] for b in blocks])
        assert abs(raw['mean_V'] - avg['mean_V']) < 1e-12
        summaries[name] = dict(raw_samples=raw, block_means=avg)
    return samples, blocks, summaries


def write_csv(path, header, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file', type=Path)
    args = parser.parse_args()
    source = args.csv_file.resolve()
    rows, audit = read_source(source)
    samples, blocks, summaries = calculate(rows)
    out = source.parent / (source.stem + '_averages')
    out.mkdir(exist_ok=True)
    write_csv(out / 'resampled.csv',
              ('sample_index', 'time_s', 'VADC_V', 'VRAW_V', 'VRAW_BIAS_V'), samples)
    write_csv(out / 'block_average.csv',
              ('block_index', 'output_time_s', 'mean_VADC_V', 'mean_VRAW_V', 'mean_VRAW_BIAS_V',
               'raw_minus_VADC_V', 'bias_minus_VADC_V', 'bias_minus_raw_V',
               'VRAW_rail_estimate_V', 'VRAW_BIAS_rail_estimate_V'),
              [(*b, b[3] - b[2], b[4] - b[2], b[4] - b[3], K * b[3], K * b[4]) for b in blocks])
    reference = summaries['VADC']['raw_samples']['mean_V']
    stat_rows = []
    for name, summary in summaries.items():
        for kind, s in summary.items():
            stat_rows.append((name, kind, s['count'], s['mean_V'], s['population_sd_V'],
                              s['mean_V'] - reference, K * s['mean_V'],
                              K * s['mean_V'] - 12, s['minimum_V'], s['maximum_V']))
    write_csv(out / 'statistics.csv',
              ('signal', 'kind', 'count', 'mean_V', 'population_sd_V', 'mean_minus_stored_VADC_V',
               'mean_rail_estimate_V', 'mean_rail_minus_12V_V', 'minimum_V', 'maximum_V'), stat_rows)
    report = dict(status='PROCESSED_USER_KICAD_CSV_NOT_HARDWARE_EVIDENCE',
                  source_file=source.name, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  source_validation=audit, sampling=dict(fs_Hz=FS, N=N, duration_s=STOP,
                  sample_count=len(samples), block_count=len(blocks),
                  convention='Ts,2Ts,...; nonoverlapping blocks (0,100ms],(100ms,200ms],...',
                  duplicate_time_policy='Retain all rows; sample only unambiguous constant plateaus',
                  accepted_plateau_samples=len(samples)), K=K, nominal_VADC_V=12/K,
                  stored_VADC_V=reference, summaries=summaries,
                  observed_sd_reduction=summaries['VRAW']['raw_samples']['population_sd_V'] /
                                        summaries['VRAW']['block_means']['population_sd_V'],
                  model_comparison=dict(assumed_source_sigma_V=.003,
                                        iid_expected_block_sigma_V=.003/math.sqrt(N)),
                  mean_bias_difference_V=summaries['VRAW_BIAS']['block_means']['mean_V'] -
                                         summaries['VRAW']['block_means']['mean_V'],
                  maximum_block_bias_relation_error_V=max(abs(b[4]-b[3]-BIAS) for b in blocks),
                  first_blocks=blocks[:5],
                  boundaries='No additional noise or offset added. No ADC acquisition, quantization, '
                             'firmware or hardware. CSV rounding retained; no inference of user understanding.')
    (out/'summary.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(validation=audit, summaries=summaries,
                         observed_sd_reduction=report['observed_sd_reduction'],
                         first_blocks=blocks[:3], output=str(out)), indent=2))


if __name__ == '__main__':
    main()
