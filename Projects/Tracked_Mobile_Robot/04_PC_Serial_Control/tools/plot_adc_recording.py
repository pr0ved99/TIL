"""Plot ADC samples and PC receipt freshness from a record_adc.py CSV."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recording", type=Path)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    with args.recording.open(newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        parser.error("empty recording")

    states = {"WAITING": 0, "STALE": 1, "FRESH": 2}
    changes = [(float(r["host_s"]), states[r["event"]])
               for r in rows if r["event"] in states]
    samples = [(float(r["host_s"]), int(r["raw"])) for r in rows
               if r["event"] == "SAMPLE" and r["valid"] == "1"]
    if not changes or not samples:
        parser.error("expected freshness transitions and valid samples")
    end = float(rows[-1]["host_s"])
    changes.append((end, changes[-1][1]))

    fig, (signal, status) = plt.subplots(2, 1, sharex=True, figsize=(10, 5),
                                        gridspec_kw={"height_ratios": [3, 1]},
                                        constrained_layout=True)
    signal.set_title("PA4 ADC and PC receipt freshness", loc="left", weight="bold")
    signal.scatter(*zip(*samples), s=8, color="#246b82", alpha=0.75, linewidths=0)
    signal.set_ylabel("ADC raw (counts)")
    status.step(*zip(*changes), where="post", color="#246b82", linewidth=2)
    status.set_yticks([0, 1, 2], ["WAITING", "STALE", "FRESH"])
    status.set_ylim(-0.3, 2.3)
    status.set_xlim(0, end)
    status.set_xlabel("Elapsed time on PC (s)")
    for (begin, state), (finish, _) in zip(changes, changes[1:]):
        if state == states["STALE"]:
            for axis in (signal, status):
                axis.axvspan(begin, finish, color="#edac64", alpha=0.35, linewidth=0)
    for axis in (signal, status):
        axis.set_axisbelow(True)
        axis.grid(axis="y", alpha=0.2)
        axis.spines[["right", "top"]].set_visible(False)
    fig.savefig(args.image, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
