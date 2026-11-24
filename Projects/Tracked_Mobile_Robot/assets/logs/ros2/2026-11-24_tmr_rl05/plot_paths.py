"""Render the measured P05 trajectories with the frozen room-B wall geometry."""
import gzip
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Rectangle
import yaml

folder = Path(__file__).resolve().parent
room = yaml.safe_load((folder.parent/"2026-11-23_tmr_nav03_evaluation/protocol.yaml").read_text())
font = font_manager.FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams.update({"font.family":font.get_name(), "axes.unicode_minus":False})
fig, axes = plt.subplots(1,2,figsize=(10,4.6),sharey=True)
panels = [
    ("최종 목표만 입력", [("rule_P05_run","규칙 · 시간 초과","#6b57a1"),
                     ("guided_P05_numpy","학습 정책 · 접촉","#b3472b")]),
    ("지도 경로와 위치 보정", [("nav2_P05","Nav2 · 도착","#215a87"),
                         ("guided_map_amcl_P05","A* + AMCL + 학습 정책 · 도착","#00805c")]),
]
gx,gy,_ = room["goals"]["P05"]
for ax,(title,runs) in zip(axes,panels):
    for _,cx,cy,w,h in room["map"]["boxes"]:
        ax.add_patch(Rectangle((cx-w/2,cy-h/2),w,h,color="#59626a"))
    ax.add_patch(Circle((gx,gy),.15,facecolor="#caeadb",edgecolor="#27735c"))
    for run,label,color in runs:
        with gzip.open(folder/run/"trace.json.gz","rt") as f:
            trace = json.load(f)
        poses = trace.get("world",trace.get("world_pose"))
        xs,ys = [p[1] for p in poses],[p[2] for p in poses]
        ax.plot(xs,ys,color=color,lw=2.4,label=label)
        ax.scatter(xs[-1],ys[-1],color=color,s=35,zorder=4)
    ax.scatter(0,0,color="#1d2c36",marker="*",s=60,zorder=5)
    ax.annotate("출발",(0,0),xytext=(-18,-14),textcoords="offset points")
    ax.annotate("목표",(gx,gy),xytext=(13,-3),textcoords="offset points")
    ax.set(xlim=(-.5,2),ylim=(-.45,1.52),aspect="equal",xlabel="x (m)")
    ax.set_title(title,loc="left",fontsize=12)
    ax.legend(loc="upper left",frameon=False,fontsize=9)
    ax.set_axisbelow(True)
    ax.grid(color="#e1e6e9",lw=.6)
axes[0].set_ylabel("y (m)")
fig.suptitle("Gazebo P05  ·  벽 뒤 목표까지의 실제 차체 중심 경로",fontweight="bold")
fig.tight_layout()
fig.savefig(folder/"p05_paths.png",dpi=160)
