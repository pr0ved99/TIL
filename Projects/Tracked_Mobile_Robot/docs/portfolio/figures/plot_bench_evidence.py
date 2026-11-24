"""Rebuild the README figures from the recorded UART and logic-analyzer samples."""
from pathlib import Path
import re
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

OUT = Path(__file__).resolve().parent
ASSETS = OUT.parents[2] / "assets"
FONT = font_manager.findfont("Noto Sans CJK JP", fallback_to_default=False)
plt.rcParams.update({"font.family": font_manager.FontProperties(fname=FONT).get_name(),
                     "font.size": 12, "axes.unicode_minus": False})
BLUE, ORANGE, INK, MUTED = "#15577c", "#a44315", "#182d3d", "#566776"


def tidy(ax):
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, pad=7, colors=INK)
    ax.set_axisbelow(True)


def plot_adc():
    folder = ASSETS / "logs/mvp_measurements/2026-11-24_e07_m01_pa4_vrefint"
    series = [("1.797 V", "pa4_dmm_uart.log"), ("1.513 V", "pa4_mid_dmm_uart.log"),
              ("3V3 분리", "pa4_low_dmm_uart.log")]
    pattern = rb"ADC,seq=\d+,ms=\d+,pa4_raw=(\d+),vrefint_raw=(\d+),valid=1\b"
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    for row, (condition, name) in enumerate(series):
        pairs = np.asarray(re.findall(pattern, (folder / name).read_bytes()), dtype=int)
        for channel, (color, marker, offset) in enumerate([(BLUE, "o", .11), (ORANGE, "D", -.14)]):
            avg = pairs[:, channel].mean()
            y = 2 - row + offset
            ax.scatter(avg, y, color=color, marker=marker, s=82, zorder=3,
                       label=("PA4 · 외부 입력", "VREFINT · 내부 기준")[channel] if row == 0 else None)
            ax.annotate(f"{avg:,.2f}", (avg, y), xytext=(8, 0),
                        textcoords="offset points", va="center", color=color, fontsize=12)
        ax.text(-.017, 2-row, f"{condition}\n{len(pairs):,}쌍",
                transform=ax.get_yaxis_transform(), ha="right", va="center", color=INK)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), ncol=2, frameon=False,
              borderaxespad=0, handletextpad=.3)
    ax.set(xlim=(-50, 2690), ylim=(-.55, 2.55), yticks=[], xticks=range(0, 2501, 500),
           xlabel="구간 평균 ADC 값 (카운트)")
    ax.grid(axis="x", color="#d7dfe4", linewidth=.8)
    for y in [.5, 1.5]:
        ax.axhline(y, color="#e7edf0", linewidth=.9)
    tidy(ax)
    fig.subplots_adjust(left=.16, right=.985, bottom=.20, top=.85)
    fig.savefig(OUT / "pa4_vrefint_means.png", dpi=160, facecolor="white")
    plt.close(fig)


def plot_stop():
    capture = ASSETS / "captures/logic_analyzer/2026-08-04_stm32_disarm_active_pwm_stop_pass.sr"
    with ZipFile(capture) as z:
        chunks = sorted((n for n in z.namelist() if n.startswith("logic-1-")),
                        key=lambda n: int(n.rsplit("-", 1)[1]))
        samples = np.frombuffer(b"".join(z.read(n) for n in chunks), dtype=np.uint8)
    rate = 4  # samples per microsecond
    reference = int(2_287_888.50 * rate)  # Final LF stop bit, as decoded in report 10.
    start, end = -55, 138
    times = np.arange(start * rate, end * rate + 1) / rate
    window = samples[reference + start * rate:reference + end * rate + 1]
    fig, ax = plt.subplots(figsize=(8.2, 3.65))
    for row, (bit, label, color) in enumerate([(4, "UART RX", MUTED), (1, "PWM 1", BLUE),
                                               (3, "PWM 2", BLUE), (5, "UART TX", MUTED)]):
        bits = (window >> bit) & 1
        ax.step(times, 3-row + bits * .46, where="post", color=color, linewidth=1.9)
        ax.text(-.015, 3-row+.22, label, transform=ax.get_yaxis_transform(),
                ha="right", va="center", color=INK)
        falls = times[1:][np.diff(bits.astype(int)) == -1]
        if bit in (1, 3):
            assert falls[-1] == 23.5
        if bit == 5:
            assert falls[falls > 0][0] == 86.25
    for x, label, color, align in [(0, "DISARM 수신 완료", MUTED, "right"),
                                   (23.5, "두 PWM 차단", BLUE, "left"),
                                   (86.25, "ACK 송신 시작", MUTED, "left")]:
        ax.axvline(x, color=color, linestyle=":", linewidth=1.05)
        ax.text(x, 3.72, label, ha=align, va="bottom", fontsize=11, color=color)
    ax.set(xlim=(start, end), ylim=(-.3, 4.15), yticks=[], xticks=[-50, 0, 23.5, 50, 86.25, 125],
           xticklabels=["−50", "0", "23.50", "50", "86.25", "125"],
           xlabel="DISARM 프레임 끝을 기준으로 한 시간 (µs)")
    tidy(ax)
    fig.subplots_adjust(left=.145, right=.98, bottom=.23, top=.96)
    fig.savefig(OUT / "disarm_pwm_edges.png", dpi=160, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    plot_stop()
    plot_adc()
