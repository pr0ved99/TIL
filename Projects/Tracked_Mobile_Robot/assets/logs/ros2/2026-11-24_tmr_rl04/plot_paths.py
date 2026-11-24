"""Draw the preselected RL-04 example from the recorded episode CSVs."""

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Circle


folder = Path(__file__).resolve().parent
protocol = json.loads((folder / "protocol.json").read_text())
seed = protocol["trajectory_example_seed"]
with (folder / "results/example_trajectory.csv").open() as f:
    paths = list(csv.DictReader(f))
with (folder / "results/evaluation.csv").open() as f:
    episodes = [r for r in csv.DictReader(f) if int(r["seed"]) == seed]

font = font_manager.FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams.update({"font.family": font.get_name(), "axes.unicode_minus": False})
fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.9), sharey=True)
colors = {"": "#106984", "3101": "#b74522", "3102": "#6354a5", "3103": "#538030"}
markers = {"goal": "o", "collision": "X", "timeout": "s"}
titles = {"single": "학습한 배치 · 중앙 기둥", "staggered": "새 배치 · 엇갈린 기둥 두 개"}
for ax, (layout, posts) in zip(axes, protocol["layouts"].items()):
    for x, y, radius in posts:
        ax.add_patch(Circle((x, y), radius, color="#4a545d"))
    rows = [r for r in episodes if r["layout"] == layout]
    for row in rows:
        training_seed = row["training_seed"]
        points = [r for r in paths if r["training_seed"] == training_seed and r["layout"] == layout]
        xs = [float(r["x_m"]) for r in points]
        ys = [float(r["y_m"]) for r in points]
        ax.plot(xs, ys, color=colors[training_seed], lw=1.8)
        ax.scatter(xs[-1], ys[-1], marker=markers[row["outcome"]], s=32,
                   color=colors[training_seed], edgecolors="white", linewidths=.35, zorder=3)
    row = rows[0]
    start = (float(row["start_x"]), float(row["start_y"]))
    goal = (float(row["goal_x"]), float(row["goal_y"]))
    ax.scatter(*start, marker="*", color="#22313b", s=92, zorder=5)
    ax.annotate("출발", start, xytext=(-2, 10), textcoords="offset points", fontsize=9)
    ax.add_patch(Circle(goal, .15, facecolor="#cbe8db", edgecolor="#286249", alpha=.65, zorder=0))
    ax.annotate("목표", goal, xytext=(9, -14), textcoords="offset points", fontsize=9)
    ax.set(xlim=(-2, 2), ylim=(-2, 2), aspect="equal", xlabel="x (m)",
           xticks=[-2, -1, 0, 1, 2], yticks=[-2, -1, 0, 1, 2])
    ax.set_axisbelow(True)
    ax.grid(color="#e2e6e8", lw=.5)
    ax.set_title(titles[layout], loc="left", fontsize=11)
axes[0].set_ylabel("y (m)")
legend = [Line2D([], [], color=c, lw=2.3, label=f"PPO {s}" if s else "규칙 제어")
          for s, c in colors.items()]
fig.legend(handles=legend, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(.5, .065))
fig.text(.5, .038, "마지막 위치      ● 도착      × 충돌 판정      ■ 시간 초과", ha="center", fontsize=9)
fig.suptitle(f"같은 출발점과 목표에서의 주행 경로  ·  평가 시드 {seed}", fontsize=14, fontweight="bold")
fig.subplots_adjust(left=.09, right=.97, top=.85, bottom=.26, wspace=.15)
fig.savefig(folder / "example_paths.png", dpi=160)
