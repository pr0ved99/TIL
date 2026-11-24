"""Evaluate all frozen RL-04 policies on paired starts in two room layouts."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean

import torch
from stable_baselines3 import PPO

from evaluate_baseline import deterministic_action, run_episode
from rule_policy import rule_action
from tmr_env import LAYOUTS, TmrEnv


def load_policies(protocol, folder):
    policies = [("rule", "", rule_action)]
    recipe = json.loads((folder / protocol["training_recipe"]).read_text())
    for seed in protocol["training_seeds"]:
        checkpoint = folder / protocol["checkpoints"][str(seed)]
        run = json.loads(checkpoint.with_name("run.json").read_text())
        if run["training_seed"] != seed or run["params"] != recipe["params"]:
            raise ValueError(f"training recipe mismatch for {checkpoint}")
        model = PPO.load(checkpoint, device="cpu")
        if model.seed != seed or model.num_timesteps != protocol["training_steps_each"]:
            raise ValueError(f"unexpected model seed or training budget: {checkpoint}")
        policies.append(("ppo", seed, deterministic_action(model)))
    return policies


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("--output", type=Path, help="write CSVs into a new directory")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error(f"choose a new directory: {args.output}")
    protocol = json.loads(args.protocol.read_text())
    torch.set_num_threads(1)
    policies = load_policies(protocol, args.protocol.parent)
    results, summaries, trajectories = [], [], []
    starts = {}
    for layout, posts in protocol["layouts"].items():
        if tuple(tuple(post) for post in posts) != LAYOUTS[layout]:
            raise ValueError(f"layout differs from protocol: {layout}")
        with TmrEnv(protocol["max_steps"], layout=layout) as env:
            for name, train_seed, action in policies:
                group = dict(layout=layout, policy=name, training_seed=train_seed)
                rows = []
                for seed in protocol["evaluation_seeds"]:
                    trace = [] if seed == protocol["trajectory_example_seed"] else None
                    row = run_episode(env, action, protocol["scenario"], seed, trace)
                    start = tuple(row[k] for k in ("start_x", "start_y", "start_yaw_rad", "goal_x", "goal_y"))
                    if starts.setdefault(seed, start) != start:
                        raise ValueError(f"unpaired start/goal for seed {seed}")
                    rows.append({**group, **row})
                    if trace is not None:
                        points = [(t, x, y) for t, x, y, *_ in trace]
                        points.append((row["time_s"], row["final_x"], row["final_y"]))
                        trajectories.extend(dict(**group, seed=seed, time_s=round(t, 1), x_m=x, y_m=y)
                                            for t, x, y in points)
                results.extend(rows)
                counts = Counter(r["outcome"] for r in rows)
                summary = dict(**group, episodes=len(rows), goals=counts["goal"],
                               collisions=counts["collision"], timeouts=counts["timeout"],
                               mean_time_s=round(mean(r["time_s"] for r in rows), 4),
                               mean_path_m=round(mean(r["path_m"] for r in rows), 6))
                summaries.append(summary)
                print(f"{layout:10s} {name:4s} {str(train_seed):4s}  "
                      f"goal={summary['goals']:2d} collision={summary['collisions']:2d} "
                      f"timeout={summary['timeouts']:2d}  mean {summary['mean_time_s']:.2f} s, "
                      f"{summary['mean_path_m']:.3f} m", flush=True)
    if args.output:
        args.output.mkdir(parents=True)
        for filename, rows in [("evaluation.csv", results), ("summary.csv", summaries),
                               ("example_trajectory.csv", trajectories)]:
            with (args.output / filename).open("w", newline="") as target:
                writer = csv.DictWriter(target, fieldnames=rows[0], lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)


if __name__ == "__main__":
    main()
