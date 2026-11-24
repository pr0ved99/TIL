"""Recompute room-B scores from world poses, commands, twist and Gazebo contacts."""
import csv
import gzip
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"2026-11-23_tmr_nav03_baseline/p01_contacts"))
from contacts import summarize

RUNS = ["nav2_P01","rule_P01","guided_P01_numpy","nav2_P05","rule_P05_run",
        "guided_P05_numpy","guided_map_P05","guided_map_amcl_P05"]


def read_gz(path):
    with gzip.open(path,"rt") as f:
        return json.load(f)


def verify(name):
    folder = HERE/name
    result = json.loads((folder/"result.json").read_text())
    trace = read_gz(folder/"trace.json.gz")
    contact = summarize(read_gz(folder/"contacts.json.gz"))
    nav2 = name.startswith("nav2")
    world = trace["world_pose" if nav2 else "world"]
    decision = (result["sim_interval"] if nav2 else trace["interval"])[1]
    target = result["goal"][:2]
    stopped = [r for r in trace["odom"] if r[0]>=decision+.6]
    max_speed = max(abs(v) for r in stopped for v in r[1 if nav2 else 4:])
    stop_span = stopped[-1][0]-stopped[0][0]
    stable_poses = [r for r in world if r[0]>=decision+.6]
    drift = max(math.dist(p[1:3],world[-1][1:3]) for p in stable_poses)
    commands = trace["cmd_vel" if nav2 else "commands"]
    stop_ok = stop_span>=2.0 and max_speed<=.001 and max(map(abs,commands[-1][1:]))<=.001 and drift<=.002
    contacts = len(contact["obstacle_episodes"])
    covered = contact["max_ground_gap_ms"]<=100 and not contact["records"].get("unknown")
    if not covered:
        raise ValueError(f"{name}: missing collision evidence")
    error = math.dist(world[-1][1:3], target)
    distance = sum(math.dist(a[1:3],b[1:3]) for a,b in zip(world,world[1:]))
    if nav2:
        accepted = result["action_status"]==4 and result["nav_error_code"]==0 and not result["timeout"]
        reason = "nav_succeeded" if accepted else "nav_failed"
    else:
        reason = result["reason"]
        accepted = reason=="target"
        assert all(abs(v)<=.100001 and abs(w)<=.390001 for _,v,w in commands)
        with (folder/"policy.csv").open() as f:
            rows = list(csv.DictReader(f))
        assert len(rows)==result["control_steps"] and all(abs(float(r["scan_s"])-float(r["odom_s"]))<=.075001 for r in rows)
    passed = accepted and error<=.15 and stop_ok and contacts==0
    assert math.isclose(error,result["xy_error_m" if nav2 else "world_error_m"],abs_tol=1e-8)
    assert stop_ok == result["stop_verified" if nav2 else "stop_ok"]
    if not nav2:
        assert passed == result["pass_goal"]
    return dict(run=name,route=result["route"],reason=reason,world_x_m=world[-1][1],world_y_m=world[-1][2],
                xy_error_m=error,sim_s=result["sim_s" if nav2 else "sim_duration_s"],path_m=distance,
                obstacle_episodes=contacts,ground_gap_ms=contact["max_ground_gap_ms"],
                stopped_sim_s=stop_span,max_stopped_twist=max_speed,stopped_drift_m=drift,passed=passed)


if __name__ == "__main__":
    runs = RUNS + sorted(p.name for p in HERE.glob("guided_map_amcl_P05_repeat*") if (p/"result.json").exists())
    rows = [verify(name) for name in runs]
    with (HERE/"results.csv").open("w",newline="") as f:
        writer = csv.DictWriter(f,fieldnames=rows[0],lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print("Verified",len(rows),"scored trials from original observations")
