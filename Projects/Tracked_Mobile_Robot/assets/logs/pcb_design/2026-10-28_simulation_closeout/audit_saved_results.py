"""Audit saved user exports and CAD connectivity; never run a simulation or edit CAD."""
from pathlib import Path
import bisect
import csv
import hashlib
import json
import math
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
SIM = PROJECT / "09_Electrical_Design/KiCAD/Simulation"
CLI = Path.home() / "AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe"

def write_json(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream, delimiter=";"))
    return rows[0], [[float(v) for v in row if v != ""] for row in rows[1:] if row]

def interpolate(rows, x, column=1, logarithmic=False):
    xs = [r[0] for r in rows]
    i = max(1, min(len(rows)-1, bisect.bisect_left(xs, x)))
    a, b = rows[i-1], rows[i]
    transform = math.log if logarithmic else (lambda t: t)
    fraction = (transform(x)-transform(a[0]))/(transform(b[0])-transform(a[0]))
    return a[column] + fraction*(b[column]-a[column])

checks = []
conditions = [
    ("01_Current_RC/Current_RC_AC.csv", 1.0, .0012),
    ("02_NTC/NTC_25C_AC.csv", .5, .0006),
    ("02_NTC/NTC_50C_AC.csv", 4147/14147, (1000+10000*4147/14147)*1e-7),
    ("03_Voltage_Divider/Voltage_Divider_AC.csv", 4700/28700, (24000*4700/28700)*1e-7),
]
for filename, a0, tau in conditions:
    header, rows = read_csv(SIM / filename)
    fc = 1/(2*math.pi*tau)
    expected = lambda f: 20*math.log10(a0)-10*math.log10(1+(2*math.pi*f*tau)**2)
    error = max(abs(r[1]-expected(r[0])) for r in rows)
    checks.append({"file": filename, "rows": len(rows), "header": header,
                   "a0": a0, "tau_s": tau, "fc_theory_hz": fc,
                   "low_frequency_gain_theory_db": 20*math.log10(a0),
                   "gain_at_fc_theory_db": expected(fc),
                   "gain_at_fc_csv_log_interpolation_db": interpolate(rows, fc, logarithmic=True),
                   "maximum_gain_error_vs_theory_db": error,
                   "csv_rounding_check_limit_db": .002, "pass": error < .002})

header, rows = read_csv(SIM / "01_Current_RC/Current_RC_Step.csv")
tau = .0012
segments = [(0, .001, 1.43, 0), (.001, .001001, 1.43, 440000),
            (.001001, .021001, 1.87, 0), (.021001, .021002, 1.87, -440000),
            (.021002, .03, 1.43, 0)]
def advance(y, u, slope, elapsed):
    return u+slope*(elapsed-tau)+(y-u+slope*tau)*math.exp(-elapsed/tau)
def expected_step(t):
    y = 1.43
    for start, end, u, slope in segments:
        if t <= end+1e-12:
            return advance(y, u, slope, max(0, t-start))
        y = advance(y, u, slope, end-start)
    return y
error = max(abs(r[1]-expected_step(r[0])) for r in rows)
checks.append({"file": "01_Current_RC/Current_RC_Step.csv", "rows": len(rows),
               "maximum_error_vs_finite_ramp_solution_v": error,
               "csv_rounding_and_solver_limit_v": .00002, "pass": error < .00002,
               "interpolated_cursor_values_v": {str(t): interpolate(rows, t)
                   for t in (.0022, .022201, .0065262, .0265262, .02653)}})

netlists = []
for folder, stem in [("01_Current_RC", "Current_RC_AC"), ("01_Current_RC", "Current_RC_Step"),
                     ("02_NTC", "02_NTC"), ("03_Voltage_Divider", "03_Voltage_Divider")]:
    source = SIM / folder / (stem + ".kicad_sch")
    out = HERE / "netlists" / (stem + ".xml")
    out.parent.mkdir(exist_ok=True)
    subprocess.run([str(CLI), "sch", "export", "netlist", "--format", "kicadxml", "--output", str(out), str(source)], check=True, capture_output=True)
    tree = ET.parse(out).getroot()
    netlists.append({"source": str(source.relative_to(PROJECT)),
                     "components": {c.get("ref"): c.findtext("value") for c in tree.findall("./components/comp")},
                     "nets": {n.get("name"): sorted(node.get("ref")+"."+node.get("pin") for node in n.findall("node")) for n in tree.findall("./nets/net")}})
voltage = netlists[-1]
assert voltage["nets"]["/VDIV"] == ["C1.1", "R2.2", "R3.1", "R4.2"]
assert voltage["nets"]["/VADC"] == ["R4.1"]
assert voltage["nets"]["0"] == ["C1.2", "R3.2", "V1.2"]
write_json("saved_connectivity.json", netlists)

files = []
for p in sorted(SIM.rglob("*")):
    rel = p.relative_to(SIM)
    if not p.is_file() or any(part.startswith(".") or part.endswith("-backups") for part in rel.parts):
        continue
    if p.suffix in (".lck", ".kicad_prl") or p.name.startswith("~"):
        continue
    files.append({"path": str(p.relative_to(PROJECT)), "bytes": p.stat().st_size,
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
write_json("manifest.json", {"date": "2026-10-28", "timezone": "Asia/Seoul", "files": files,
           "source_scope": "User GUI exports and saved models; 01_Current_RC/reports is the earlier assistant DLL run.",
           "hardware": "NOT_RUN", "this_audit_simulation_execution": "NOT_PERFORMED"})

baseline = json.loads((HERE / "baseline.json").read_text(encoding="utf-8"))
repo = PROJECT.parents[1]
preservation = []
for item in baseline["unrelated"]:
    p = repo / item["path"]
    preservation.append({"path": item["path"], "unchanged": hashlib.sha256(p.read_bytes()).hexdigest() == item["sha256"]})
for path, sha in baseline["shield"].items():
    preservation.append({"path": path, "unchanged": hashlib.sha256((repo/path).read_bytes()).hexdigest() == sha})
write_json("validation.json", {"result": "PASS" if all(x["pass"] for x in checks) and all(x["unchanged"] for x in preservation) else "FAIL",
           "checks": checks, "original_shield_and_unrelated_preservation": preservation,
           "meaning": "CSV/theory and saved-connectivity audit only; not a simulation rerun or hardware acceptance."})
print(json.dumps({"checks": [{"file": x["file"], "rows": x["rows"], "pass": x["pass"],
             "max_error": x.get("maximum_gain_error_vs_theory_db", x.get("maximum_error_vs_finite_ramp_solution_v"))} for x in checks],
             "preserved": all(x["unchanged"] for x in preservation), "files": len(files)}, ensure_ascii=False))
assert all(x["pass"] for x in checks) and all(x["unchanged"] for x in preservation)
