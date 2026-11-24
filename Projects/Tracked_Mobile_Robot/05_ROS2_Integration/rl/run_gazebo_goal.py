"""Launch one isolated, fresh Gazebo trial and retain measurements. Run with system Python."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import yaml


HERE = Path(__file__).resolve().parent
LOGS = HERE.parents[1] / "assets/logs/ros2"
PREVIOUS = LOGS / "2026-11-23_tmr_nav03_evaluation"
CURRENT = LOGS / "2026-11-24_tmr_rl05"
sys.path.insert(0, str(PREVIOUS/"runner"))
from run_series import attempt, start, stop


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("policy", choices=["rule", "guided", "guided_map", "guided_map_amcl", "nav2"])
    parser.add_argument("route", choices=["P01", "P05"])
    parser.add_argument("output", type=Path, help="new directory for this trial")
    parser.add_argument("--bag", action="store_true", help="record ROS topics during a policy trial")
    args = parser.parse_args()
    if args.bag and args.policy == "nav2":
        parser.error("the frozen NAV-03 runner has its own representative Nav2 bag")
    checkpoint = CURRENT/"guided/actor.npz"
    protocol = json.loads((CURRENT/"protocol.json").read_text())
    seed = protocol["gazebo_seed"]
    if args.policy.startswith("guided"):
        admission = protocol["guided_ppo_admission"]
        recorded = json.loads(checkpoint.with_name("run.json").read_text())
        if recorded["goals"] < admission["min_goals_of_20"] or recorded["collisions"] > admission["max_collisions"]:
            parser.error("guided policy did not meet the documented 2D qualification")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    subprocess.run(["sha256sum","--quiet","-c","frozen_inputs.sha256"],cwd=PREVIOUS,check=True)
    with tempfile.TemporaryDirectory(prefix="tmr-rl05-") as tmp:
        work = Path(tmp)
        if args.policy == "nav2":
            try:
                attempt(args.route,seed,"regular",work,63)
            finally:
                for name in ("dispatch.json","result.json","contacts.json.gz","trace.json.gz","trial.log","stack.log"):
                    if (work/name).exists():
                        shutil.copyfile(work/name,out/name)
            if not (out/"result.json").exists():
                raise RuntimeError(f"incomplete Nav2 trial; inspect {out}")
            print((out/"result.json").read_text())
            return
        domain = {("guided_map_amcl","P01"):93, ("guided_map_amcl","P05"):94,
                  ("guided_map","P01"):95, ("guided_map","P05"):96, ("rule","P01"):97, ("guided","P01"):98,
                  ("rule","P05"):99, ("guided","P05"):100}[args.policy,args.route]
        env = dict(os.environ, ROS_DOMAIN_ID=str(domain), ROS_AUTOMATIC_DISCOVERY_RANGE="LOCALHOST",
                   GZ_PARTITION=f"tmr-rl05-{os.getpid()}", ROS_LOG_DIR=str(work/"ros-log"),
                   OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
        bridge = HERE.parent/"src/tmr_sim/config/drive_bridge.yaml"
        processes = []
        try:
            processes.append(start(["gz","sim","-r","-s","--headless-rendering","--seed",str(seed),
                                    str(PREVIOUS/"inputs/room_b.sdf")], env, out/"gazebo.log"))
            processes.append(start(["ros2","run","ros_gz_bridge","parameter_bridge","--ros-args",
                                    "-p",f"config_file:={bridge}","-r","/cmd_vel:=/rl05/cmd_vel",
                                    "-r","/odom:=/rl05/odom","-r","/scan:=/rl05/scan"],env,out/"bridge.log"))
            if args.policy == "guided_map_amcl":
                from ament_index_python.packages import get_package_share_directory
                nav = Path(get_package_share_directory("nav2_bringup"))
                cfg = yaml.safe_load((nav/"params/nav2_params.yaml").read_text())
                cfg["amcl"]["ros__parameters"].update(scan_topic="/rl05/scan", set_initial_pose=True,
                        initial_pose=dict(x=0., y=0., z=0., yaw=0.), update_min_d=.05, update_min_a=.07)
                params = work/"amcl.yaml"
                params.write_text(yaml.safe_dump(cfg))
                processes.append(start(["ros2","run","robot_state_publisher","robot_state_publisher",
                                        str(PREVIOUS/"inputs/tmr.urdf"),"--ros-args","-p","use_sim_time:=true"],
                                       env,out/"transforms.log"))
                processes.append(start(["ros2","launch",str(nav/"launch/localization_launch.py"),
                                        "use_sim_time:=true","autostart:=true","use_composition:=False",
                                        f"map:={PREVIOUS}/inputs/room_b.yaml",f"params_file:={params}"],
                                       env,out/"localization.log"))
            if args.bag:
                env["RL05_RECORDING"] = "1"
                processes.append(start(["ros2","bag","record","-s","mcap","--storage-preset-profile","zstd_fast",
                                        "--use-sim-time","-o",str(out/"bag"),"--topics","/clock","/rl05/scan",
                                        "/rl05/odom","/rl05/cmd_vel","/tf","/tf_static","/map"],env,out/"bag.log"))
            cmd = [sys.executable,"-B",str(HERE/"gazebo_goal.py"),args.route,args.policy,str(out)]
            if args.policy.startswith("guided"):
                cmd.append(str(checkpoint))
            with (out/"trial.log").open("w") as trial_log:
                subprocess.run(cmd, env=env, check=True, timeout=235, stdout=trial_log, stderr=subprocess.STDOUT)
            print((out/"result.json").read_text())
        finally:
            for process in reversed(processes):
                stop(process)


if __name__ == "__main__":
    main()
