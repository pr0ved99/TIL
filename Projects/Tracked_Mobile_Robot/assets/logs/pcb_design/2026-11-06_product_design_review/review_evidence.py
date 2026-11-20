"""Export present CAD and calculate bounded review examples without editing CAD."""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import fitz

OUT = Path(__file__).resolve().parent
PROJECT = next(p for p in OUT.parents if p.name == "Tracked_Mobile_Robot")
CAD = PROJECT / "09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA"
NAME = "TMR_Monitor_Shield_RevA"
CLI = Path.home() / "AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe"


def main():
    spec = importlib.util.spec_from_file_location(
        "read_only_parser", OUT.parent / "2026-11-06_voltage_schematic_audit/audit_schematic.py")
    parser = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = parser
    spec.loader.exec_module(parser)
    protected = [p for p in CAD.iterdir() if p.is_file() and p.suffix in
                 {".kicad_sch", ".kicad_pcb", ".kicad_pro", ".kicad_sym", ".csv"}]
    protected += [CAD / "sym-lib-table"]
    def hashes():
        return {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in protected}
    before = hashes()
    commands = []
    for args in [
        ["--version"],
        ["sch", "export", "netlist", "--format", "kicadxml", "--output",
         str(OUT / "current_netlist.xml"), str(CAD / f"{NAME}.kicad_sch")],
        ["sch", "export", "pdf", "--output", str(OUT / "current_schematic.pdf"),
         str(CAD / f"{NAME}.kicad_sch")],
        ["sch", "erc", "--format", "json", "--severity-all", "--output",
         str(OUT / "current_erc.json"), str(CAD / f"{NAME}.kicad_sch")],
    ]:
        run = subprocess.run([str(CLI), *args], capture_output=True, text=True, encoding="utf-8")
        commands.append({"args": args, "returncode": run.returncode,
                         "stdout": run.stdout, "stderr": run.stderr})
        if run.returncode:
            raise RuntimeError(commands[-1])
    root = ET.parse(OUT / "current_netlist.xml").getroot()
    components = [{"ref": c.attrib["ref"], "value": c.findtext("value"),
                   "footprint": c.findtext("footprint") or ""}
                  for c in root.findall("components/comp")]
    nets = {n.attrib["name"]: sorted(f"{p.attrib['ref']}.{p.attrib['pin']}"
            for p in n.findall("node")) for n in root.findall("nets/net")}
    active = {name: pins for name, pins in nets.items() if not name.startswith("unconnected-")}
    pcb = parser.sexp((CAD / f"{NAME}.kicad_pcb").read_text(encoding="utf-8-sig"))
    sch = parser.sexp((CAD / f"{NAME}.kicad_sch").read_text(encoding="utf-8-sig"))
    erc = json.loads((OUT / "current_erc.json").read_text(encoding="utf-8"))
    pdf = fitz.open(OUT / "current_schematic.pdf")
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(OUT / "current_schematic.png")
    violations = [v for sheet in erc.get("sheets", []) for v in sheet.get("violations", [])]
    def parallel(*values):
        return 1 / sum(1 / x for x in values)
    rt = 24000.0
    rb = 4700.0
    rs = 1000.0
    ron = 2.0  # nominal comparison assumption, not all-condition guaranteed value
    load = 47000.0
    c = 100e-9
    lower = parallel(rb, rs + ron + load)
    ratio = lower / (rt + lower) * load / (rs + ron + load)
    rcap = parallel(rt, rb, rs + ron + load)
    fcs = {"current": 1 / (2 * math.pi * 12000 * c),
           "ntc_25C": 1 / (2 * math.pi * (1000 + parallel(10000, 10000)) * c),
           "voltage_planned_on": 1 / (2 * math.pi * rcap * c)}
    attenuation = {channel: {str(f): -10 * math.log10(1 + (f / fc) ** 2)
                            for f in (5, 50, 100, 1000, 19000, 19001)}
                   for channel, fc in fcs.items()}
    data = {
        "scope": "Present schematic readback and first-order calculations; no physical/EMC qualification",
        "components": components, "component_count": len(components), "active_nets": active,
        "unconnected_nets": {k: v for k, v in nets.items() if k.startswith("unconnected-")},
        "explicit_no_connect_count": len(parser.children(sch, "no_connect")),
        "pcb": {kind: len(parser.children(pcb, kind))
                for kind in ("footprint", "segment", "arc", "via", "zone")},
        "erc_counts_by_type": dict(Counter(v.get("type", "unknown") for v in violations)),
        "erc_counts_by_severity": dict(Counter(v.get("severity", "unknown") for v in violations)),
        "erc_excluded_count": sum(bool(v.get("excluded")) for v in violations),
        "erc_export_time_local": erc.get("date"),
        "erc_ignored_checks": erc.get("ignored_checks", []),
        "calculations": {
            "assumptions": "Ideal sources, nominal R/C, RON=2ohm, no leakage/parasitics/ADC dynamic loading",
            "fc_hz": fcs, "attenuation_relative_to_channel_dc_gain_db": attenuation,
            "current_ground_offset_10mV_A": 0.010 / 0.044,
            "current_leakage_example_1uA_V": 12000 * 1e-6,
            "current_leakage_example_1uA_A": 12000 * 1e-6 / 0.044,
            "voltage_adc_at_16V_on_V": 16 * ratio,
            "voltage_adc_at_12p6V_on_V": 12.6 * ratio,
            "voltage_gain_inverse": 1 / ratio,
            "voltage_switch_input_at_16V_off_V": 16 * rb / (rt + rb),
            "voltage_switch_input_3p6V_off_rail_equivalent_V": 3.6 * (rt + rb) / rb,
            "voltage_simple_Ipoff_2uA_47k_V": 2e-6 * load,
            "voltage_simple_Ipoff_10nA_47k_V": 10e-9 * load,
            "voltage_cap_source_resistance_ohm": rcap,
            "adc_acquisition_480cycles_14MHz_us": 480 / 14,
            "adc_conversion_492cycles_14MHz_us": 492 / 14,
            "alias_example_19001Hz_sampled_100Hz_hz": abs(19001 - round(19001 / 100) * 100),
            "alias_report32_19058p568Hz_sampled_100Hz_hz": abs(19058.568 - round(19058.568 / 100) * 100),
        },
        "commands": commands, "protected_before": before, "protected_after": hashes(),
    }
    if data["protected_after"] != before:
        raise RuntimeError("CAD source changed during evidence export")
    (OUT / "evidence.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: data[k] for k in ("component_count", "active_nets", "pcb",
          "erc_counts_by_type", "erc_counts_by_severity", "erc_excluded_count", "calculations")},
          ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
