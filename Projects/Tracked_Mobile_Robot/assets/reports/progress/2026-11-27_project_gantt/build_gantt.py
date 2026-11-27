"""Render the two dated Markdown tables as a standalone, offline SVG."""
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from html import escape
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
SOURCE = PROJECT / "docs/plans/2026-11-27_TMR_Project_Gantt_ko.md"
OUTPUT = HERE / "tmr_gantt.svg"
DAY = timedelta(days=1)
COLORS = {"실적": "#137465", "계획": "#315bbc", "조건부": "#995315", "예비": "#64748b"}
LEFT, RIGHT, WIDTH, ROW = 309, 1038, 1248, 30


@dataclass(frozen=True)
class Task:
    label: str
    start: date
    end: date
    kind: str
    note: str


def read_tasks():
    tasks = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| 작업 |"):
            continue
        label, start, end, kind, note = map(str.strip, line.strip("|").split("|"))
        task = Task(label, date.fromisoformat(start), date.fromisoformat(end), kind,
                    note.split(" [", 1)[0])
        if task.end < task.start or kind not in COLORS:
            raise ValueError(f"Invalid task: {line}")
        tasks.append(task)
    return tasks


def text(x, y, value, size=15, color="#24394a", weight=400, align="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{align}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{escape(value)}</text>')


def panel(parts, tasks, y, title, accent):
    start = min(t.start for t in tasks)
    stop = max(t.end for t in tasks) + DAY

    def x(day):
        return LEFT + (day - start).days / (stop - start).days * (RIGHT - LEFT)

    bar_top = y + 54
    bottom = bar_top + len(tasks) * ROW
    parts.extend([f'<rect x="35" y="{y-17}" width="4" height="23" rx="2" fill="{accent}"/>',
                  text(53, y+2, title, 22, "#182f41", 700),
                  text(1206, y+2, f'{start:%Y.%m.%d} – {stop-DAY:%Y.%m.%d}',
                       16, "#43586b", 500, "end"),
                  text(38, bar_top-11, "작업", 13, "#546a79", 600),
                  text(1206, bar_top-11, "기록일 / 계획일", 13, "#546a79", 600, "end")])
    # Show partial months at the ends without extending the time scale.
    day = start
    while day < stop:
        next_month = day.replace(day=monthrange(day.year, day.month)[1]) + DAY
        end = min(next_month, stop)
        col = "#f0f4f7" if day.month % 2 == 0 else "#f8fafb"
        parts.extend([f'<rect x="{x(day):.2f}" y="{bar_top-28}" width="{x(end)-x(day):.2f}" '
                      f'height="{bottom-bar_top+28}" fill="{col}"/>',
                      text((x(day)+x(end))/2, bar_top-11, f"{day.month}월", 13,
                           "#415c6b", 600, "middle")])
        day = end
    for index, task in enumerate(tasks):
        row_y = bar_top + index * ROW
        center = row_y + ROW / 2
        left, right = x(task.start), x(task.end + DAY)
        color = COLORS[task.kind]
        dates = task.start.strftime("%m/%d")
        if task.start != task.end:
            dates += " – " + task.end.strftime("%m/%d")
        parts.extend([f'<g><title>{escape(task.label)} · {dates} · {task.kind}. '
                      f'{escape(task.note)}</title>',
                      f'<path d="M 35 {row_y} H 1206" stroke="#dce4e9" stroke-width=".8"/>',
                      text(38, center+5.4, task.label, 15, "#263d4b", 500),
                      text(1206, center+5.2, dates, 15, "#425968", 500, "end")])
        if task.start == task.end:
            middle = (left + right) / 2
            parts.append(f'<path d="M {middle:.2f} {center-7} l 7 7 -7 7 -7 -7 z" fill="{color}"/>')
        elif task.kind in ("조건부", "예비"):
            parts.append(f'<rect x="{left:.2f}" y="{center-6}" width="{right-left:.2f}" '
                         f'height="12" rx="3" fill="url(#stripe-{task.kind})" '
                         f'stroke="{color}" stroke-width="1.5" stroke-dasharray="5 3"/>')
        else:
            parts.append(f'<rect x="{left:.2f}" y="{center-6}" width="{right-left:.2f}" '
                         f'height="12" rx="3" fill="{color}"/>')
        parts.append('</g>')
    parts.append(f'<path d="M 35 {bottom} H 1206" stroke="#cdd9df"/>')
    return bottom


def main():
    tasks = read_tasks()
    actual = [t for t in tasks if t.kind == "실적"]
    planned = [t for t in tasks if t.kind != "실적"]
    cutoff = max(t.end for t in actual)
    if min(t.start for t in planned) <= cutoff:
        raise ValueError("A planned row overlaps the historical panel. Check its dates.")
    parts = []
    for kind in ("조건부", "예비"):
        color = COLORS[kind]
        parts.append(f'<defs><pattern id="stripe-{kind}" width="7" height="7" '
                     f'patternUnits="userSpaceOnUse"><rect width="7" height="7" fill="#fff"/>'
                     f'<path d="M-2 2l4 -4 M0 7l7 -7 M5 9l4 -4" stroke="{color}" '
                     f'opacity=".35" stroke-width="1.3"/></pattern></defs>')
    parts.extend([text(35, 57, "궤도형 모바일 로봇 개발 일정", 34, "#132f40", 700),
                  text(35, 90, f"프로젝트 첫 기록부터 실물 자율주행·최종 인수까지   ·   기준일 {cutoff:%Y.%m.%d}",
                       16, "#42606e")])
    legend = [("실적", "기록으로 확인", 35), ("계획", "예정 작업", 215),
              ("조건부", "조건부 발주·입고", 375), ("예비", "재시험 예비", 583)]
    for kind, label, at in legend:
        fill = COLORS[kind] if kind in ("실적", "계획") else f"url(#stripe-{kind})"
        parts.extend([f'<rect x="{at}" y="115" width="23" height="10" rx="3" '
                      f'fill="{fill}" stroke="{COLORS[kind]}"/>',
                      text(at+33, 126, label, 14, "#38505c", 500)])
    parts.append(text(1206, 126, "◆ 하루짜리 기록·목표", 14, "#526775", 500, "end"))
    end = panel(parts, actual, 176, "프로젝트 시작부터 현재까지", COLORS["실적"])
    end = panel(parts, planned, end+54, "PCB 발주 준비부터 최종 인수까지", COLORS["계획"])
    parts.append(text(35, end+29, "두 패널은 월 눈금 간격이 다릅니다. 실적 구간의 양 끝은 대표 기록일이며, 계획 구간은 달력상의 목표입니다.",
                      14, "#475d6c"))
    height = end + 52
    header = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
              f'width="{WIDTH}" height="{height}" role="img" aria-labelledby="title desc">\n'
              '<title id="title">TMR 전체 간트 차트</title>\n'
              '<desc id="desc">위 패널은 저장소 기록으로 확인한 작업 구간, 아래 패널은 발주부터 '
              '실물 주행·인수와 예비 기간까지의 계획이다. 각 행에서 날짜를 확인할 수 있다.</desc>\n'
              '<rect width="100%" height="100%" fill="#ffffff"/>\n'
              '<g font-family="Noto Sans CJK KR, Malgun Gothic, Apple SD Gothic Neo, sans-serif">')
    OUTPUT.write_text("\n".join([header, *parts, "</g></svg>\n"]), encoding="utf-8")


if __name__ == "__main__":
    main()
