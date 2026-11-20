"""Reproduce the graphical reorganization from the preserved pre-layout snapshot.

Writes a candidate only.  The live schematic is updated separately after comparing
electrical connectivity, component identities, protected files, and rendered PDFs.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET

import fitz

OUT = Path(__file__).resolve().parent
PROJECT = next(p for p in OUT.parents if p.name == "Tracked_Mobile_Robot")
REPO = PROJECT.parent.parent
CAD = PROJECT / "09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA"
NAME = "TMR_Monitor_Shield_RevA"
CLI = Path.home() / "AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe"


@dataclass
class Atom:
    value: str
    start: int
    end: int


@dataclass
class Node:
    items: list
    start: int
    end: int = 0

    @property
    def kind(self):
        return self.items[0].value

    def children(self, kind):
        return [x for x in self.items if isinstance(x, Node) and x.kind == kind]

    def child(self, kind):
        return self.children(kind)[0]


def parse(source):
    stack = []
    root = None
    for token in re.finditer(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', source):
        text = token.group()
        if text == "(":
            n = Node([], token.start())
            if stack:
                stack[-1].items.append(n)
            else:
                root = n
            stack.append(n)
        elif text == ")":
            stack.pop().end = token.end()
        else:
            stack[-1].items.append(Atom(json.loads(text) if text.startswith('"') else text,
                                       token.start(), token.end()))
    assert not stack
    return root


def plain(node):
    return [plain(i) if isinstance(i, Node) else i.value for i in node.items]


def coords(node):
    return tuple(float(x.value) for x in node.child("at").items[1:3])


def prop(symbol, name):
    return next(p for p in symbol.children("property") if p.items[1].value == name)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(args):
    run = subprocess.run([str(CLI), *args], capture_output=True, text=True, encoding="utf-8")
    assert run.returncode == 0, (args, run.stdout, run.stderr)
    return {"args": args, "exit_code": run.returncode, "stdout": run.stdout, "stderr": run.stderr}


def net_signature(path):
    tree = ET.parse(path).getroot()
    components = {}
    for c in tree.findall("components/comp"):
        components[c.attrib["ref"]] = {
            "value": c.findtext("value"), "footprint": c.findtext("footprint"),
            "datasheet": c.findtext("datasheet"), "libsource": c.find("libsource").attrib,
            "tstamps": [n.text for n in c.findall("tstamps/tstamp")],
        }
    nets = {n.attrib["name"]: sorted((p.attrib["ref"], p.attrib["pin"],
                                    p.attrib.get("pinfunction"), p.attrib.get("pintype"))
                                   for p in n.findall("node"))
            for n in tree.findall("nets/net")}
    return components, nets


def main():
    source = (OUT / "before.kicad_sch").read_text(encoding="utf-8-sig")
    root = parse(source)
    edits = {}
    moves = []

    def set_atom(atom, text):
        edits[(atom.start, atom.end)] = text

    def number(atom, value):
        set_atom(atom, f"{value:.6f}".rstrip("0").rstrip(".") or "0")

    def position(node, x, y):
        at = node.child("at")
        number(at.items[1], x)
        number(at.items[2], y)

    def font(node, size):
        f = node.child("effects").child("font").child("size")
        number(f.items[1], size)
        number(f.items[2], size)

    def translate(node, dx, dy):
        if node.kind in ("at", "xy"):
            number(node.items[1], float(node.items[1].value) + dx)
            number(node.items[2], float(node.items[2].value) + dy)
            return
        for c in node.items:
            if isinstance(c, Node):
                translate(c, dx, dy)

    # Each connected circuit is translated as a complete group on a 50 mil grid.
    transforms = {
        "J1": (2.54, 1.27), "J2": (-7.62, 1.27),
        "current_left": (-31.75, 10.16), "current_right": (-31.75, -1.27),
        "ntc_left": (-15.24, 5.08), "ntc_right": (-15.24, -11.43),
        "U1": (154.94, -53.34), "U2": (175.26, -53.34),
    }
    refs = {"J1": "J1", "J2": "J2", "U1": "U1", "U2": "U2"}
    for group, members in {
        "current_left": ["J3", "R1", "C1"], "current_right": ["J4", "R2", "C2"],
        "ntc_left": ["J5", "R3", "R4", "C3"], "ntc_right": ["J6", "R5", "R6", "C4"],
    }.items():
        refs.update({ref: group for ref in members})
    tp_old = [25.4, 83.82, 142.24, 200.66, 259.08, 317.5]
    tp_new = [30.48, 78.74, 127.0, 175.26, 223.52, 271.78]
    for i, (old, new) in enumerate(zip(tp_old, tp_new), 1):
        transforms[f"TP{i}"] = (round(new-old, 6), 85.09)
        refs[f"TP{i}"] = f"TP{i}"

    def group_for_xy(x, y):
        if 177 < y < 200:
            index = min(range(6), key=lambda i: abs(x-tp_old[i]))
            assert abs(x-tp_old[index]) < 0.001
            return f"TP{index+1}"
        if y < 151 and x < 135:
            return "J1" if x < 80 else "J2"
        if y < 151 and 150 < x < 282:
            return "current_left" if y < 100 else "current_right"
        if y < 151 and x >= 282:
            return "ntc_left" if y < 93 else "ntc_right"
        raise ValueError((x, y))

    for n in root.items:
        if not isinstance(n, Node):
            continue
        if n.kind == "symbol":
            ref = prop(n, "Reference").items[2].value
            dx, dy = transforms[refs[ref]]
            x, y = coords(n)
            translate(n, dx, dy)
            moves.append({"ref": ref, "from_mm": [x, y], "to_mm": [round(x+dx, 6), round(y+dy, 6)]})
            for name in ("Reference", "Value"):
                font(prop(n, name), 1.27)
            if ref in ("J3", "J4", "J5", "J6"):
                position(prop(n, "Reference"), x+dx, y+dy-10.16)
                position(prop(n, "Value"), x+dx, y+dy-7.62)
            if ref.startswith("TP"):
                position(prop(n, "Reference"), x+dx, y+dy-6.35)
            if ref in ("U1", "U2"):
                # Undo auto-placement's side offset, keep both IC field stacks centered.
                field_y = 185.42 if ref == "U1" else 172.72
                position(prop(n, "Reference"), x+dx, field_y)
                position(prop(n, "Value"), x+dx, field_y+2.54)
                for name in ("Reference", "Value"):
                    eff = prop(n, name).child("effects")
                    for just in eff.children("justify"):
                        edits[(just.start, just.end)] = ""
        elif n.kind in ("wire", "junction", "no_connect", "label"):
            if n.kind == "wire":
                pts = n.child("pts").children("xy")
                groups = [group_for_xy(float(p.items[1].value), float(p.items[2].value)) for p in pts]
                assert len(set(groups)) == 1, groups
                group = groups[0]
            else:
                group = group_for_xy(*coords(n))
            translate(n, *transforms[group])
            if n.kind == "label":
                font(n, 1.27)
        elif n.kind == "text":
            text = n.items[1].value
            new_text = text
            size = 1.016
            if text.startswith("1. NUCLEO"):
                x,y,size,new_text = 17.78,31.75,1.524,"01  NUCLEO-F446RE INTERFACE"
            elif text.startswith("2. CURRENT"):
                x,y,size,new_text = 128.27,31.75,1.524,"02  CURRENT INPUTS"
            elif text.startswith("3. NTC"):
                x,y,size,new_text = 266.7,31.75,1.524,"03  NTC INPUTS"
            elif text.startswith("4. TEST"):
                x,y,size,new_text = 17.78,256.54,1.524,"06  TEST POINTS"
            elif text.startswith("CN7:"):
                x,y = 17.78,114.3
            elif text.startswith("12k +"):
                x,y = 175.26,96.52 if coords(n)[1] < 100 else 140.97
            elif text.startswith("OPEN ELECTRICAL"):
                x,y = 266.7,227.33
            elif text.startswith("OPEN MECHANICAL"):
                x,y = 266.7,237.49
            elif text.startswith("DRAFT -"):
                x,y,size = 12.7,19.05,1.016
            elif text.startswith("TMR MONITOR"):
                x,y,size,new_text = 12.7,12.7,2.032,"TMR MONITOR SHIELD | RevA.0 FUNCTIONAL LAYOUT"
            else:
                raise ValueError(text)
            position(n,x,y)
            font(n,size)
            set_atom(n.items[1],json.dumps(new_text))

    additions = []

    def text_item(value, x, y, size=1.016):
        additions.append(f'''\n\t(text {json.dumps(value)}
        (at {x} {y} 0)
        (effects (font (size {size} {size})) (justify left top))
        (uuid "{uuid.uuid5(uuid.NAMESPACE_URL, 'tmr/layout20261106/text/'+value)}")
    )''')

    def line(points, name, width=0.254, style="default"):
        pts = " ".join(f"(xy {x} {y})" for x,y in points)
        additions.append(f'''\n\t(polyline (pts {pts})
        (stroke (width {width}) (type {style})) (fill (type none))
        (uuid "{uuid.uuid5(uuid.NAMESPACE_URL, 'tmr/layout20261106/line/'+name)}")
    )''')

    panels = {
        "interface": (12.7,26.67,116.84,148.59),
        "current": (123.19,26.67,255.27,148.59),
        "ntc": (261.62,26.67,406.4,148.59),
        "voltage_inputs": (12.7,153.67,255.27,247.65),
        "voltage_control": (261.62,153.67,406.4,247.65),
        "test_points": (12.7,251.46,292.1,281.94),
    }
    for name, (x1,y1,x2,y2) in panels.items():
        line([(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)],name+"_border",0.127)
        line([(x1,y1+10.16),(x2,y1+10.16)],name+"_header",0.127)
    # Test point labels start below their panel heading.
    text_item("04  VOLTAGE INPUTS - RESERVED FOR NEXT STEP",17.78,158.75,1.524)
    text_item("05  VOLTAGE SUPERVISOR / SWITCH",266.7,158.75,1.524)
    text_item("BATTERY SIDE  |  J7 / R7-R11 / C5 - TO BE ADDED",17.78,170.18,1.27)
    text_item("MOTOR SUPPLY SIDE  |  J8 / R12-R16 / C6 - TO BE ADDED",17.78,210.82,1.27)
    text_item("Layout space only. Voltage dividers and their nets are not placed yet.",17.78,243.84)
    line([(17.78,203.2),(250.19,203.2)],"voltage_channels",0.127,"dash")
    # Explicitly separate the historical review notes from the new, unwired ICs.
    line([(266.7,224.79),(401.32,224.79)],"control_notes",0.127)

    candidate = source
    for (start,end), value in sorted(edits.items(),reverse=True):
        candidate = candidate[:start]+value+candidate[end:]
    end = candidate.rfind(")")
    candidate = candidate[:end]+"".join(additions)+"\n"+candidate[end:]
    target = OUT / "candidate" / f"{NAME}.kicad_sch"
    target.parent.mkdir(exist_ok=True)
    target.write_text(candidate,encoding="utf-8",newline="\n")

    after = parse(candidate)
    assert plain(root.child("lib_symbols")) == plain(after.child("lib_symbols"))
    for kind in ("symbol","wire","junction","no_connect","label"):
        assert len(root.children(kind)) == len(after.children(kind)), kind
    for a,b in zip(root.children("symbol"),after.children("symbol")):
        assert plain(a.child("uuid")) == plain(b.child("uuid"))
        assert plain(a.child("lib_id")) == plain(b.child("lib_id"))
        assert plain(a.child("instances")) == plain(b.child("instances"))
        assert [(p.items[1].value,p.items[2].value) for p in a.children("property")] == [
            (p.items[1].value,p.items[2].value) for p in b.children("property")]
    commands = [run_cli(["sch","export","netlist","--format","kicadxml","--output",
                         str(OUT/"after_netlist.xml"),str(target)]),
                run_cli(["sch","export","pdf","--output",str(OUT/"after.pdf"),str(target)])]
    before_components,before_nets = net_signature(OUT/"before_netlist.xml")
    after_components,after_nets = net_signature(OUT/"after_netlist.xml")
    assert before_components == after_components, "Component identity changed"
    assert before_nets == after_nets, "Connectivity changed"
    assert len(before_components) == 24
    for stage in ("before","after"):
        with fitz.open(OUT/f"{stage}.pdf") as pdf:
            assert len(pdf)==1
            pdf[0].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(OUT/f"{stage}.png")
    baseline = json.loads((OUT/"baseline.json").read_text(encoding="utf-8"))
    assert sha(CAD/f"{NAME}.kicad_sch") == baseline["source_sha256"], "Live source changed during preparation"
    assert all(sha(REPO/p)==h for p,h in baseline["protected"].items()), "Protected file changed"
    result = {
        "date":"2026-11-06", "status":"CANDIDATE_VALIDATED_NOT_APPLIED",
        "component_count":len(after_components), "net_count_including_unconnected":len(after_nets),
        "active_net_count":sum(not name.startswith("unconnected-") for name in after_nets),
        "component_identity_unchanged":True, "all_nets_and_pin_types_unchanged":True,
        "embedded_library_symbols_unchanged":True, "symbol_uuids_and_instances_unchanged":True,
        "wire_count":len(after.children("wire")), "no_connect_count":len(after.children("no_connect")),
        "junction_count":len(after.children("junction")), "label_count":len(after.children("label")),
        "protected_file_count":len(baseline["protected"]),
        "source_sha256_before":baseline["source_sha256"], "candidate_sha256":sha(target),
        "new_erc_run":False, "new_drc_run":False, "commands":commands,
        "moves":sorted(moves,key=lambda m:m["ref"]), "panels_mm":panels,
    }
    (OUT/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","component_count","active_net_count",
                     "all_nets_and_pin_types_unchanged","protected_file_count")},ensure_ascii=False))


if __name__ == "__main__":
    main()
