"""Resample a user's KiCad CSV and compare nonoverlapping block averages.
No ADC quantization/acquisition model, KiCad execution, or hardware operation.
"""
import argparse
import bisect
import csv
import hashlib
import json
import math
from pathlib import Path

K = 6.747204164780444
FS_VALUES = (100, 1000, 2000)
STOP = 0.300
BLOCK = 0.100

def interpolate(times, values, at):
    if at < times[0] - 1e-12 or at > times[-1] + 1e-12:
        raise ValueError("Requested sample lies outside CSV time coverage")
    if at <= times[0]: return values[0]
    if at >= times[-1]: return values[-1]
    i = bisect.bisect_right(times, at) - 1
    f = (at - times[i]) / (times[i + 1] - times[i])
    return values[i] + f * (values[i + 1] - values[i])

def analyze(times, adc, rail):
    samples, blocks = [], []
    for fs in FS_VALUES:
        n = round(fs * BLOCK)
        bucket = []
        for index in range(1, round(fs * STOP) + 1):
            t = index / fs
            vadc = interpolate(times, adc, t)
            estimate = K * vadc
            bucket.append(estimate)
            samples.append((fs, index, t, vadc, estimate))
            if index % n == 0:
                blocks.append((fs, n, index // n, t, math.fsum(bucket) / n,
                               interpolate(times, rail, t)))
                bucket.clear()
    return samples, blocks

def read_csv(path):
    text = path.read_text(encoding="utf-8-sig")
    first = text.splitlines()[0]
    delimiter = max((";", ",", "\t"), key=first.count)
    rows = csv.reader(text.splitlines(), delimiter=delimiter)
    header = [x.strip() for x in next(rows)]
    normalized = [x.lower().replace(" ", "") for x in header]
    def col(options):
        for option in options:
            if option in normalized: return normalized.index(option)
        raise ValueError("Required CSV column missing: " + "/".join(options))
    ti = col(("time", "time(s)"))
    ai = col(("v(/vadc)", "v(vadc)"))
    ri = col(("v(/vrail)", "v(vrail)"))
    t, a, r = [], [], []
    for line, row in enumerate(rows, 2):
        if not row or all(not x.strip() for x in row): continue
        try: vals = [float(row[i]) for i in (ti, ai, ri)]
        except (ValueError, IndexError) as exc:
            raise ValueError(f"Invalid numerical data at row {line}") from exc
        if not all(math.isfinite(x) for x in vals):
            raise ValueError(f"Non-finite data at row {line}")
        if t and vals[0] <= t[-1]:
            raise ValueError("CSV time must increase strictly; check export precision")
        t.append(vals[0]); a.append(vals[1]); r.append(vals[2])
    if len(t) < 2 or t[0] > 0 or t[-1] < STOP - 1e-12:
        raise ValueError("Export the full interval 0 to 0.300 s")
    if max(y-x for x,y in zip(t,t[1:])) > 10e-6 * 1.01:
        raise ValueError("CSV spacing too coarse for this lab; use TRAN max step 5u")
    if abs(interpolate(t,r,0.050)-12.6) > .001 or abs(interpolate(t,r,.080)-12.0) > .001:
        raise ValueError("VRAIL does not match this lab's 12.6 -> 12.0 V step")
    return t,a,r

def write_csv(path, columns, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer=csv.writer(f);writer.writerow(columns);writer.writerows(rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    args=parser.parse_args()
    source=args.csv_file.resolve()
    t,a,r=read_csv(source)
    samples,blocks=analyze(t,a,r)
    out=source.parent/(source.stem+"_averages")
    out.mkdir(exist_ok=True)
    write_csv(out/"resampled.csv",
        ("fs_Hz","sample_index","time_s","VADC_V","rail_estimate_V"),samples)
    write_csv(out/"block_average.csv",
        ("fs_Hz","N","block_index","output_time_s","average_rail_estimate_V","VRAIL_at_output_V"),blocks)
    report=dict(status="PROCESSED_USER_CSV_NOT_HARDWARE_EVIDENCE",
        source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        rows=len(t),K=K,sample_convention="Ts,2Ts,...; blocks (0,100ms],(100,200ms],...",
        interpolation="linear; not a physical ADC acquisition or quantization model",
        assumptions="Fixed nominal K; no offsets or additional noise introduced",
        outputs=[dict(fs_Hz=b[0],N=b[1],block=b[2],t_s=b[3],average_V=b[4],VRAIL_V=b[5]) for b in blocks])
    (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"Processed {len(t)} CSV rows; output folder: {out}")
    for b in blocks:
        print(f"{b[0]:4d} Hz, N={b[1]:3d}, t={b[3]*1000:.1f} ms: {b[4]:.9f} V")

if __name__=="__main__": main()
