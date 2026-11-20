"""Read-only schematic comparison; exports evidence without editing the CAD source."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
PROJECT = next(p for p in OUT.parents if p.name == "Tracked_Mobile_Robot")
REPO = PROJECT.parent.parent
CAD = PROJECT / "09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA"
NAME = "TMR_Monitor_Shield_RevA"
CLI = Path.home() / "AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def children(node, kind):
    return [c for c in node if isinstance(c, list) and c and c[0] == kind]


def child(node, kind):
    return next(c for c in node if isinstance(c, list) and c and c[0] == kind)


def sexp(text):
    stack, result = [], None
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == "(":
            node = []
            if stack:
                stack[-1].append(node)
            else:
                result = node
            stack.append(node)
        elif token == ")":
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert not stack
    return result


def nets(path):
    root = ET.parse(path).getroot()
    return root, {n.attrib["name"]: sorted(f"{p.attrib['ref']}.{p.attrib['pin']}" for p in n.findall("node"))
                  for n in root.findall("nets/net")}


def main():
    protected = [CAD / f"{NAME}{ext}" for ext in (".kicad_sch", ".kicad_pcb", ".kicad_pro")]
    protected += [CAD / "bom_candidates.csv", CAD / "reports/netlist.xml",
                  CAD / "reports/erc.json", CAD / "reports/drc_unrouted.json"]
    receipt = PROJECT / "assets/logs/pcb_design/2026-11-06_learning_closeout/preserved_worktree.json"
    unrelated = json.loads(receipt.read_text(encoding="utf-8-sig"))["files"]
    protected += [REPO / item["path"] for item in unrelated]
    before = {p.relative_to(REPO).as_posix(): sha(p) for p in protected}
    commands = []
    for args in [["--version"],
                 ["sch", "export", "netlist", "--format", "kicadxml", "--output", str(OUT/"current_netlist.xml"), str(protected[0])],
                 ["sch", "export", "pdf", "--output", str(OUT/"current_schematic.pdf"), str(protected[0])]]:
        run = subprocess.run([str(CLI), *args], capture_output=True, text=True, encoding="utf-8")
        commands.append({"args": args, "exit_code": run.returncode, "stdout": run.stdout, "stderr": run.stderr})
        assert run.returncode == 0, commands[-1]
    fresh, current_nets = nets(OUT / "current_netlist.xml")
    _, previous_nets = nets(CAD / "reports/netlist.xml")
    active = {k: v for k, v in current_nets.items() if not k.startswith("unconnected-")}
    previous_active = {k: v for k, v in previous_nets.items() if not k.startswith("unconnected-")}
    assert active == previous_active, "Existing active net connections changed; review the new source"
    components = [{"ref": c.attrib["ref"], "value": c.findtext("value"), "footprint": c.findtext("footprint")}
                  for c in fresh.findall("components/comp")]
    assert len(components) == 22 and len(active) == 10
    tree = sexp(protected[0].read_text(encoding="utf-8-sig"))
    symbols = children(tree, "symbol")
    instances = {next(p[2] for p in children(s, "property") if p[1] == "Reference"): s for s in symbols}
    lib = {s[1]: s for s in children(child(tree, "lib_symbols"), "symbol")}
    ncs = {tuple(map(float, child(n, "at")[1:3])) for n in children(tree, "no_connect")}
    pin_nets = {p: name for name, pins in current_nets.items() for p in pins}
    header_checks = []
    for ref, pin, function in [("J1", "32", "CN7-32 / PA4 / ADC1_IN4"),
                               ("J1", "34", "CN7-34 / PB0 / ADC1_IN8"),
                               ("J2", "7", "CN10-7 / AVDD")]:
        instance = instances[ref]
        at = child(instance, "at")
        assert float(at[3]) == 0 and not children(instance, "mirror")
        definition = lib[child(instance, "lib_id")[1]]
        pins = [p for unit in children(definition, "symbol") for p in children(unit, "pin")]
        item = next(p for p in pins if child(p, "number")[1] == pin)
        offset = child(item, "at")
        position = (round(float(at[1])+float(offset[1]), 6), round(float(at[2])-float(offset[2]), 6))
        nc = any(abs(position[0]-x) < 1e-5 and abs(position[1]-y) < 1e-5 for x, y in ncs)
        assert nc and pin_nets[f"{ref}.{pin}"].startswith("unconnected-")
        header_checks.append({"ref": ref, "pin": pin, "contract_function": function,
                              "net": pin_nets[f"{ref}.{pin}"], "schematic_xy_mm": position,
                              "explicit_no_connect": nc})
    occupied = {c["ref"] for c in components}
    proposed = {"upstream": ["J7", "R7", "R8", "R9", "R10", "R11", "C5"],
                "downstream": ["J8", "R12", "R13", "R14", "R15", "R16", "C6"],
                "shared": ["U1", "U2", "C7", "C8"]}
    assert not occupied.intersection(r for group in proposed.values() for r in group)
    symbol_matches = []
    lib_dir = CLI.parent.parent / "share/kicad/symbols"
    for f in lib_dir.glob("*.kicad_sym"):
        found = re.findall(r'\(symbol "([^"\n]*(?:TPS3840|TMUX1511)[^"\n]*)"', f.read_text(encoding="utf-8"))
        if found:
            symbol_matches.append({"library": f.name, "symbols": sorted(set(found))})
    pdf = fitz.open(OUT / "current_schematic.pdf")
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.45, 1.45)).save(OUT / "current_schematic.png")
    pdf.close()
    st_path = PROJECT / "assets/datasheets/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf"
    st = fitz.open(st_path)
    st[58].get_pixmap(matrix=fitz.Matrix(1.6, 1.6)).save(OUT / "UM1724_Rev17_p59_Table29.png")
    (OUT / "UM1724_Rev17_p59_Table29.txt").write_text(st[58].get_text(), encoding="utf-8")
    st.close()
    after = {p.relative_to(REPO).as_posix(): sha(p) for p in protected}
    assert before == after, "Protected source files changed"
    assert all(sha(REPO/item["path"]) == item["sha256"].lower() for item in unrelated)
    result = {
        "work_date": "2026-11-06", "status": "CAD_CONTRACT_COMPARISON_COMPLETE_NO_CAD_EDIT",
        "cad_title_revision": "RevA.0-DRAFT", "cad_generator_version": "9.0",
        "export_tool_version": commands[0]["stdout"].strip(),
        "component_count": len(components), "active_net_count": len(active),
        "unchanged_from_previous_active_netlist": True,
        "components": components, "active_nets": active,
        "target_header_checks": header_checks, "no_connect_count": len(ncs),
        "proposed_references_not_applied": proposed,
        "installed_standard_library_matches": symbol_matches,
        "library_search_scope": str(lib_dir),
        "source_hashes_before": before, "source_hashes_after": after,
        "unrelated_files_preserved": len(unrelated),
        "new_erc_run": False, "new_drc_run": False,
        "firmware_or_hardware_work": False,
        "st_source": {"file": st_path.relative_to(REPO).as_posix(), "sha256": sha(st_path),
                       "revision": "UM1724 Rev17", "printed_page": 59, "table": 29},
        "commands": commands,
    }
    (OUT / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["status", "export_tool_version", "component_count", "active_net_count",
                                          "target_header_checks", "installed_standard_library_matches",
                                          "unrelated_files_preserved"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
