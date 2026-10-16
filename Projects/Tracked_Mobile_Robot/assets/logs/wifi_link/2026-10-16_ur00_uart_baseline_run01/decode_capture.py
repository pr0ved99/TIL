"""Decode selected bench UART channels and optional sampled logic levels.

Usage: python decode_capture.py capture.sr [output_directory]
       [--uart-channels 0,1] [--level-channels 4,6,7]
Default UART mapping is specific to the original four-channel bench.
"""
import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path, nargs="?",
                    default=Path(__file__).resolve().parent)
parser.add_argument("--uart-channels", default="0,1,2,3")
parser.add_argument("--level-channels", default="")
args = parser.parse_args()


def channel_ids(value):
    ids = [int(item) for item in value.split(",") if item]
    if len(set(ids)) != len(ids) or any(ch not in range(8) for ch in ids):
        parser.error("Channels must be distinct integers from 0 to 7")
    return ids


uart_channels = channel_ids(args.uart_channels)
level_channels = channel_ids(args.level_channels)
source, output = args.source, args.output
output.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(source) as archive:
    metadata = archive.read("metadata").decode()
    rate = re.search(r"samplerate=(\d+(?:\.\d+)?)\s*([kM]?)Hz", metadata)
    fs = float(rate[1]) * {"": 1, "k": 1000, "M": 1000000}[rate[2]]
    assert "unitsize=1" in metadata
    chunks = sorted((name for name in archive.namelist()
                     if re.fullmatch(r"logic-1-\d+", name)),
                    key=lambda name: int(name.rsplit("-", 1)[1]))
    raw = b"".join(archive.read(name) for name in chunks)

roles = {0: "STM PA9 TX / JDBG_UART Pin1",
         1: "STM PA10 RX / JDBG_UART Pin2",
         2: "ESP GPIO18 RX", 3: "ESP GPIO17 TX"}
report = dict(source_name=source.name,
              sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              samplerate_hz=fs, samples=len(raw), duration_s=len(raw)/fs,
              decode="115200 baud, 8N1, LSB-first, non-inverted",
              channels={}, pairs={})
spb = fs / 115200
streams = {}


def parse_tel(text):
    """Validate a whole TEL line; do not merge duplicate fields across reset."""
    if not text.startswith("TEL,"):
        return None
    unsigned = {"t_ms", "command_age_ms", "last_seq", "drop", "err"}
    signed = {"vx_mmps", "w_mradps", "left_pwm", "right_pwm",
              "left_cps", "right_cps", "batt_mv"}
    pairs = [part.split("=", 1) for part in text[4:].split(",")]
    if any(len(pair) != 2 for pair in pairs):
        return None
    fields = dict(pairs)
    if (len(fields) != len(pairs) or
            set(fields) != unsigned | signed | {"state", "reason"}):
        return None
    if fields["state"] not in {"DISARMED", "ARMED", "FAULT"}:
        return None
    if not re.fullmatch(r"[A-Z0-9_]{1,31}", fields["reason"]):
        return None
    for key in unsigned:
        if (not re.fullmatch(r"[0-9]+", fields[key]) or
                int(fields[key]) > 0xFFFFFFFF):
            return None
    for key in signed:
        if (not re.fullmatch(r"-?[0-9]+", fields[key]) or
                not -(1 << 31) <= int(fields[key]) < (1 << 31)):
            return None
    return fields


for ch in uart_channels:
    role = roles.get(ch, "UART; physical probe mapping must be verified")
    bits = raw.translate(bytes((value >> ch) & 1 for value in range(256)))
    cursor = 0
    start = None
    buffer = bytearray()
    stream = bytearray()
    lines = []
    bad_stops = []
    for match in re.finditer(b"\x01\x00", bits):
        edge = match.start() + 1
        if edge < cursor or edge + 10 * spb >= len(raw):
            continue
        if bits[round(edge + .5 * spb)] != 0:
            continue
        cursor = edge + 9.6 * spb
        if bits[round(edge + 9.5 * spb)] != 1:
            bad_stops.append(edge / fs)
            continue
        value = sum(bits[round(edge + (1.5 + j) * spb)] << j
                    for j in range(8))
        stream.append(value)
        if start is None:
            start = edge / fs
        if value == 10:
            lines.append(dict(start_s=start, end_s=(edge + 10 * spb)/fs,
                              text=buffer.decode("ascii", "backslashreplace")
                              .rstrip("\r")))
            buffer.clear()
            start = None
        else:
            buffer.append(value)
    streams[ch] = bytes(stream)
    (output / f"D{ch}.txt").write_text("".join(
        f"{line['start_s']:.9f}\t{line['end_s']:.9f}\t{line['text']}\n"
        for line in lines), encoding="utf-8")
    (output / f"D{ch}_lines.json").write_text(
        json.dumps(lines, indent=2), encoding="utf-8")
    tel_candidates = [(line, parse_tel(line["text"])) for line in lines
                      if line["text"].startswith("TEL,")]
    tels = [fields for _, fields in tel_candidates if fields is not None]
    keys = ("state", "reason", "left_pwm", "right_pwm", "left_cps",
            "right_cps", "drop", "err")
    report["channels"][f"D{ch}"] = dict(
        role=role, decoded_bytes=len(stream), complete_lf_lines=len(lines),
        invalid_stop_bits=len(bad_stops), invalid_stop_times_s=bad_stops,
        trailing_partial_text=buffer.decode("ascii", "backslashreplace"),
        message_counts=dict(Counter(line["text"].split(",", 1)[0]
                                    for line in lines)),
        valid_tel_lines=len(tels),
        malformed_tel_lines=[line for line, fields in tel_candidates
                             if fields is None],
        telemetry_values={key: dict(Counter(t[key] for t in tels if key in t))
                          for key in keys},
        non_tel_lines=[line for line in lines
                       if not line["text"].startswith("TEL,")],
        first_line=lines[:1], last_line=lines[-1:])

for a, b in ((0, 2), (3, 1)):
    if a not in streams or b not in streams:
        continue
    differences = raw.translate(bytes(((value >> a) ^ (value >> b)) & 1
                                     for value in range(256)))
    runs = [(match.start(), match.end())
            for match in re.finditer(b"\x01+", differences)]
    mask = (1 << a) | (1 << b)
    excursions = Counter()
    for start, end in runs:
        if (start > 0 and end < len(raw)
                and raw[start-1] & mask == raw[end] & mask):
            for ch in (a, b):
                if (raw[start] ^ raw[start-1]) & (1 << ch):
                    excursions[f"D{ch}"] += 1
    report["pairs"][f"D{a}_D{b}"] = dict(
        differing_samples=differences.count(1), mismatch_runs=len(runs),
        longest_mismatch_us=max((end-start for start, end in runs), default=0)
        * 1e6/fs, decoded_bytes_equal=streams[a] == streams[b],
        excursion_runs_by_channel=dict(excursions),
        transition_skew_runs=len(runs)-sum(excursions.values()))

if level_channels:
    report["logic_levels"] = {}
    for ch in level_channels:
        bits = raw.translate(bytes((value >> ch) & 1 for value in range(256)))
        high_samples = bits.count(1)
        rising_edges = bits.count(b"\x00\x01")
        falling_edges = bits.count(b"\x01\x00")
        high_runs = []
        for match in re.finditer(b"\x01+", bits):
            high_runs.append(dict(start_s=match.start()/fs,
                                  end_s=match.end()/fs,
                                  samples=match.end()-match.start()))
            if len(high_runs) == 20:
                break
        report["logic_levels"][f"D{ch}"] = dict(
            samples=len(bits), high_samples=high_samples,
            low_samples=len(bits)-high_samples,
            first_level=bits[0], last_level=bits[-1],
            rising_edges=rising_edges, falling_edges=falling_edges,
            high_runs_first_20=high_runs)

report["limits"] = [
    ("Sampled digital levels only; physical endpoints require user verification."
     if level_channels else
     "Digital UART observations only; no PWM, PC7 or analog power probes."),
    "A capture boundary may truncate a line. Bytes are decoded at nominal baud.",
    "Matching sampled logic does not establish analog signal integrity.",
    "Telemetry reports firmware values, not physical motor output measurements."]
(output / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
