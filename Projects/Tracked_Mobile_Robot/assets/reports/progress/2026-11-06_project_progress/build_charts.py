"""Reproduce the project-wide dated milestone charts (Python + matplotlib + plotly)."""
from __future__ import annotations

import csv
import html
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUT = Path(__file__).resolve().parent
PROJECT = next(p for p in OUT.parents if p.name == "Tracked_Mobile_Robot")
REPO = PROJECT.parent.parent
DATA = json.loads((OUT / "milestones.json").read_text(encoding="utf-8"))
START, END = (date.fromisoformat(DATA[k]) for k in ("start", "end"))
CATEGORIES = {
    "hardware": ("실물·보드 관측", "#139A8B"),
    "demo": ("통합 시연 결과물", "#526ED3"),
    "design": ("설계·모의실험·학습 자료", "#E8A63A"),
}
STACK_ORDER = ["design", "demo", "hardware"]
NAVY, MUTED = "#142C46", "#526478"


def load_evidence():
    events = DATA["milestones"]
    assert events == sorted(events, key=lambda e: e["date"]), "Dates must be sorted"
    seen = set()
    for event in events:
        event_day = date.fromisoformat(event["date"])
        assert START <= event_day <= END
        assert event["category"] in CATEGORIES
        assert (event["date"], event["title"]) not in seen
        seen.add((event["date"], event["title"]))
        source = PROJECT / "docs/progress" / f"{event['date']}_progress.md"
        lines = source.read_text(encoding="utf-8-sig").splitlines()
        matches = [i for i, line in enumerate(lines, 1) if event["anchor"] in line]
        assert matches, f"Missing evidence: {event['title']}"
        event["source_line"] = matches[0]
        event["source_path"] = source.relative_to(REPO).as_posix()
        event["source_excerpt"] = lines[matches[0] - 1].strip()
        event["source_url"] = (
            f"https://github.com/pr0ved99/TIL/blob/{DATA['source_commit']}/"
            f"{event['source_path']}#L{event['source_line']}"
        )
    return events


def main():
    events = load_evidence()
    days = [START + timedelta(days=i) for i in range((END - START).days + 1)]
    records = []
    for path in sorted((PROJECT / "docs/progress").glob("????-??-??_progress.md")):
        day = date.fromisoformat(path.name[:10])
        if START <= day <= END:
            records.append(day)
    count = Counter((e["date"], e["category"]) for e in events)
    daily = {k: [count[(d.isoformat(), k)] for d in days] for k in CATEGORIES}
    cumulative, pace = {}, {}
    for key in CATEGORIES:
        cumulative[key] = [sum(daily[key][:i + 1]) for i in range(len(days))]
        pace[key] = [sum(daily[key][i - 13:i + 1]) / 2 if i >= 13 else None
                     for i in range(len(days))]
    total = [sum(cumulative[k][i] for k in CATEGORIES) for i in range(len(days))]
    total_pace = [sum(pace[k][i] for k in CATEGORIES) if i >= 13 else None
                  for i in range(len(days))]
    assert total[-1] == len(events)
    assert sum(map(sum, daily.values())) == len(events)

    with (OUT / "milestones.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(events[0]))
        writer.writeheader()
        writer.writerows(events)
    with (OUT / "daily_series.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "has_progress_record", "milestones", "cumulative",
                         "milestones_per_week_trailing_14d", *[f"cumulative_{k}" for k in CATEGORIES]])
        for i, day in enumerate(days):
            writer.writerow([day.isoformat(), int(day in records),
                             sum(daily[k][i] for k in CATEGORIES), total[i],
                             "" if total_pace[i] is None else total_pace[i],
                             *[cumulative[k][i] for k in CATEGORIES]])

    font_path = Path("C:/Windows/Fonts/malgun.ttf")
    if font_path.exists():
        font_manager.fontManager.addfont(str(font_path))
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=font_path).get_name()
    else:
        plt.rcParams["font.family"] = ["Noto Sans CJK KR", "NanumGothic", "DejaVu Sans"]
    plt.rcParams.update({"font.size": 11, "axes.unicode_minus": False,
                         "text.color": NAVY, "axes.labelcolor": NAVY,
                         "xtick.color": MUTED, "ytick.color": MUTED})
    fig = plt.figure(figsize=(16, 10.5), facecolor="#F5F8FC")
    gs = fig.add_gridspec(2, 1, left=.075, right=.97, top=.79, bottom=.16,
                         height_ratios=[1.7, 1], hspace=.27)
    ax, speed = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    fig.text(.075, .952, "Tracked Mobile Robot", fontsize=27, weight="bold")
    fig.text(.075, .91, "프로젝트 전체의 날짜별 진도와 진행 속도", fontsize=18)
    fig.text(.075, .873, f"2026.06.08 — 11.06   |   {len(records)}개 날짜의 기록   |   대표 성과 {len(events)}건 선정", color=MUTED)
    handles = [Line2D([0], [0], color=CATEGORIES[k][1], lw=7,
                      label=f"{CATEGORIES[k][0]}  {cumulative[k][-1]}건") for k in CATEGORIES]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.07, .855),
               ncol=3, frameon=False, fontsize=11)
    for target in (ax, speed):
        target.set_facecolor("white")
        target.spines[["top", "right", "left"]].set_visible(False)
        target.spines["bottom"].set_color("#DCE4ED")
        target.grid(axis="y", color="#E9EEF4", zorder=0)
        target.set_axisbelow(True)
        target.set_xlim(START, END + timedelta(days=2))
        target.xaxis.set_major_locator(mdates.MonthLocator())
        target.xaxis.set_major_formatter(mdates.DateFormatter("%m월"))
        target.tick_params(length=0, pad=8)
        target.axvspan(date(2026, 10, 25), END + timedelta(days=2), color="#E8A63A", alpha=.055)

    ax.stackplot(days, *[cumulative[k] for k in STACK_ORDER],
                 colors=[CATEGORIES[k][1] for k in STACK_ORDER], alpha=.82, step="post")
    ax.step(days, total, where="post", color=NAVY, lw=1.7)
    ax.set_title("01  누적 진도  ·  대표 성과가 확인될 때마다 1건", loc="left", pad=16, weight="bold")
    ax.set_ylabel("누적 대표 성과 (건)", labelpad=14)
    ax.set_ylim(0, len(events) + 3)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    for milestone_number, e in enumerate(events, 1):
        d = date.fromisoformat(e["date"])
        ax.scatter(d, milestone_number, s=23, color=CATEGORIES[e["category"]][1],
                   edgecolor="white", linewidth=.7, zorder=4)
    annotations = [
        ("2026-07-09", "7/9  UART 보드 검증", (-36, 34)),
        ("2026-08-12", "8/12  MCU 출력 안전", (-68, 37)),
        ("2026-09-22", "9/22  E-stop → PWM", (-82, 36)),
        ("2026-10-18", "10/18  지상 4방향 주행", (-130, 37)),
        ("2026-11-05", "11/5  관측·PCB 인계 자료", (-182, 25)),
    ]
    for ds, label, offset in annotations:
        d = date.fromisoformat(ds)
        ax.annotate(label, xy=(d, total[(d-START).days]), xytext=offset,
                    textcoords="offset points", fontsize=10,
                    bbox=dict(boxstyle="round,pad=.35", fc="white", ec="#DCE4ED"),
                    arrowprops=dict(arrowstyle="-", color="#7C8B9C", lw=.8), zorder=5)
    ax.text(.992, .09, "6–8월: 통신·출력 안전 → 9월: 전장 제작 → 10월: 주행 통합 → 현재: PCB 설계",
            transform=ax.transAxes, ha="right", fontsize=10, color=NAVY,
            bbox=dict(facecolor="white", alpha=.9, edgecolor="none", pad=5))

    valid_days = days[13:]
    speed.stackplot(valid_days, *[pace[k][13:] for k in STACK_ORDER],
                    colors=[CATEGORIES[k][1] for k in STACK_ORDER], alpha=.65, step="post")
    speed.step(valid_days, total_pace[13:], where="post", color=NAVY, lw=1.7)
    speed.set_title("02  진행 속도  ·  최근 14일의 대표 성과 수 ÷ 2주", loc="left", pad=15, weight="bold")
    speed.set_ylabel("대표 성과 (건/주)", labelpad=14)
    speed.set_ylim(0, max(total_pace[13:]) + 1.15)
    speed.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
    speed.plot(records, [-.15] * len(records), "|", color="#8090A2", ms=5,
               transform=speed.get_xaxis_transform(), clip_on=False)
    speed.text(.002, -.24, "아래 짧은 눈금 = 진행 기록이 있는 날짜", transform=speed.transAxes,
               fontsize=9, color=MUTED)
    peak = max(total_pace[13:])
    peak_dates = [days[i] for i, v in enumerate(total_pace) if v == peak]
    speed.annotate(f"선정 성과가 가장 밀집한 구간\n최대 {peak:g}건/주", (peak_dates[0], peak),
                   xytext=(-160, 9), textcoords="offset points", fontsize=10,
                   arrowprops=dict(arrowstyle="-", color=MUTED),
                   bbox=dict(boxstyle="round,pad=.35", fc="white", ec="#DCE4ED"))
    fig.text(.075, .075, "읽는 기준  |  성과 1건의 난이도·공수는 서로 다릅니다. 이 그래프는 완료율(%)이나 생산성 점수가 아닙니다.",
             fontsize=10, color=MUTED)
    fig.text(.075, .048, "대표 성과가 없는 날에도 작업은 있었을 수 있습니다. 자료 작성·모의실험은 실물 검증과 구분하며, 전체 MVP 인수는 미완료입니다.",
             fontsize=10, color=MUTED)
    fig.savefig(OUT / "project_progress.png", dpi=170, facecolor=fig.get_facecolor())
    fig.savefig(OUT / "project_progress.svg", facecolor=fig.get_facecolor())
    plt.close(fig)

    chart = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[.63, .37],
                          vertical_spacing=.13,
                          subplot_titles=("누적 대표 성과 (건)", "최근 14일 대표 성과 ÷ 2주 (건/주)"))
    xs = [d.isoformat() for d in days]
    for key in STACK_ORDER:
        label, color = CATEGORIES[key]
        chart.add_trace(go.Scatter(x=xs, y=cumulative[key], name=label,
                                  mode="lines", line=dict(color=color, shape="hv", width=1),
                                  stackgroup="cumulative", legendgroup=key,
                                  hovertemplate=f"%{{x}}<br>{label}: %{{y}}건<extra></extra>"), row=1, col=1)
        chart.add_trace(go.Scatter(x=xs[13:], y=pace[key][13:], name=label,
                                  mode="lines", line=dict(color=color, shape="hv", width=1),
                                  stackgroup="pace", showlegend=False, legendgroup=key,
                                  hovertemplate=f"%{{x}}<br>{label}: %{{y:.1f}}건/주<extra></extra>"), row=2, col=1)
    chart.add_trace(go.Scatter(x=[e["date"] for e in events],
                              y=list(range(1, len(events) + 1)),
                              mode="markers", showlegend=False,
                              marker=dict(size=9, color=[CATEGORIES[e["category"]][1] for e in events],
                                          line=dict(color="white", width=1)),
                              customdata=[[e["title"], e["scope"]] for e in events],
                              hovertemplate="%{x}<br><b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>"), row=1, col=1)
    chart.update_layout(height=740, paper_bgcolor="white", plot_bgcolor="#F5F8FC",
                        font=dict(family="Malgun Gothic, Noto Sans KR, sans-serif", color=NAVY),
                        margin=dict(l=60, r=30, t=60, b=50), hovermode="closest",
                        legend=dict(orientation="h", y=1.12), dragmode="zoom")
    chart.update_xaxes(range=[START.isoformat(), (END+timedelta(days=1)).isoformat()],
                       tickformat="%m/%d", showgrid=True, gridcolor="#E6EDF4")
    chart.update_yaxes(rangemode="tozero", gridcolor="#E6EDF4")
    plot = chart.to_html(full_html=False, include_plotlyjs=True,
                         config={"displaylogo": False, "responsive": True,
                                 "toImageButtonOptions": {"filename": "tmr_project_progress"}})
    rows = "".join(
        f"<tr><td>{e['date']}</td><td><span style='color:{CATEGORIES[e['category']][1]}'>{CATEGORIES[e['category']][0]}</span></td>"
        f"<td><b>{html.escape(e['title'])}</b><br>{html.escape(e['scope'])}</td>"
        f"<td><a href='{e['source_url']}' target='_blank' rel='noopener'>근거 L{e['source_line']}</a></td></tr>"
        for e in events)
    page = f"""<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>TMR 프로젝트 전체 진행</title>
<style>body{{margin:0;background:#f5f8fc;color:{NAVY};font:16px/1.7 'Malgun Gothic',sans-serif}}
main{{max-width:1200px;margin:36px auto;padding:24px;background:white;border-radius:18px}}
h1{{font-size:30px;margin:0}}p{{color:{MUTED}}}table{{border-collapse:collapse;width:100%;font-size:14px}}
td,th{{padding:12px;text-align:left;border-bottom:1px solid #e3eaf2}}td:first-child{{white-space:nowrap}}
a{{color:#2461a1}}.note{{padding:16px;background:#f5f8fc;border-radius:10px}}@media(max-width:700px){{main{{margin:0;padding:12px}}table{{font-size:12px}}td,th{{padding:7px}}}}</style>
<main><h1>Tracked Mobile Robot · 날짜별 프로젝트 진행</h1>
<p>2026.06.08 — 11.06 · {len(records)}개 날짜의 기록 · 대표 성과 {len(events)}건</p>
<p class="note">점에 마우스를 올리면 결과와 적용 범위가 나옵니다. 드래그로 확대하고 더블클릭으로 복원할 수 있습니다.
위 그래프의 점은 항상 전체 누적 건수를 표시합니다. 아래 표에서 원본 근거를 확인하세요.</p>
{plot}<p class="note"><b>집계 기준:</b> 진행 기록일 기준 대표 결과 1건 = 1.
속도는 해당 날짜를 포함한 최근 14일 성과 수 ÷ 2주이며, 처음 13일은 표시하지 않습니다.
동일 난이도·공수가 아니므로 완료율·생산성 또는 실제 노동 시간으로 해석하지 않습니다.
기록이 없는 날짜나 선정 성과가 없는 날짜를 휴무·정체로 판단하지 않습니다.
설계·학습 자료 작성은 사용자 필기·이해·실측 완료와 구분합니다. 전체 MVP 인수는 미완료입니다.</p>
<h2>선정한 대표 성과와 원본 기록</h2><table><thead><tr><th>기록일</th><th>종류</th><th>결과·경계</th><th>원본</th></tr></thead><tbody>{rows}</tbody></table>
<p>근거 링크는 게시된 원본 커밋 {DATA['source_commit'][:8]}에 고정했습니다. 11/6 수면 후 CAD 작업은 집계에 포함하지 않았습니다.</p></main></html>"""
    (OUT / "project_progress.html").write_text(page, encoding="utf-8")
    monthly = {}
    for day in days:
        key = day.strftime("%Y-%m")
        monthly.setdefault(key, {"record_dates": 0, "milestones": 0, "hardware": 0, "design": 0, "demo": 0})
        monthly[key]["record_dates"] += int(day in records)
    for e in events:
        monthly[e["date"][:7]]["milestones"] += 1
        monthly[e["date"][:7]][e["category"]] += 1
    summary = {"start": START.isoformat(), "end": END.isoformat(),
               "calendar_dates_inclusive": len(days), "record_dates": len(records),
               "selected_milestones": len(events),
               "category_counts": {k: cumulative[k][-1] for k in CATEGORIES},
               "peak_milestones_per_week_trailing_14d": peak,
               "peak_dates": [d.isoformat() for d in peak_dates],
               "latest_milestones_per_week_trailing_14d": total_pace[-1],
               "monthly": monthly, "source_anchor_checks": len(events),
               "source_commit": DATA["source_commit"]}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
