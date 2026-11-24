"""Evaluate the rule policy or a saved PPO model under the RL-02 protocol."""

import argparse
import csv
import math
from collections import Counter

from rule_policy import rule_action
from tmr_env import DT, LAYOUTS, MAX_ANGULAR, MAX_LINEAR, SCENARIOS, TmrEnv


# The two named demonstrations are separate from the 20 scored seeded starts.
EVALUATION_SEEDS = range(22000, 22020)


def deterministic_action(model):
    def predict(observation):
        action, _ = model.predict(observation, deterministic=True)
        return action
    return predict


def run_episode(env, policy, scenario, seed, trace=None):
    obs, initial = env.reset(seed=seed, options={"scenario": scenario})
    pose = initial["pose"]
    path = total_reward = 0.0
    while True:
        action = policy(obs)
        if trace is not None:
            trace.append((len(trace) * DT, pose[0], pose[1], float(obs[0]), float(obs[-5]),
                          float(action[0]) * MAX_LINEAR, float(action[1]) * MAX_ANGULAR))
        obs, reward, terminated, truncated, info = env.step(action)
        path += math.dist(pose[:2], info["pose"][:2])
        pose = info["pose"]
        total_reward += reward
        if terminated or truncated:
            break
    x, y, yaw = initial["pose"]
    gx, gy = initial["goal"]
    return dict(scenario=scenario, seed=seed, start_x=x, start_y=y, start_yaw_rad=yaw,
                goal_x=gx, goal_y=gy, outcome=info["outcome"], steps=info["steps"],
                time_s=round(info["steps"] * DT, 1), path_m=round(path, 6),
                final_x=round(pose[0], 6), final_y=round(pose[1], 6),
                goal_error_m=round(float(obs[-5]), 6), total_reward=round(total_reward, 6))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    single_run = parser.add_mutually_exclusive_group()
    single_run.add_argument("--demo", choices=SCENARIOS, help="show one fixed demonstration")
    single_run.add_argument("--seed", type=int, help="trace a seeded random start")
    parser.add_argument("--layout", choices=LAYOUTS, default="single")
    parser.add_argument("--csv", help="write episode results to this CSV file")
    parser.add_argument("--ppo", metavar="MODEL", help="use this saved PPO checkpoint on CPU")
    args = parser.parse_args()
    policy = rule_action
    if args.ppo:
        import torch
        from stable_baselines3 import PPO

        torch.set_num_threads(1)
        policy = deterministic_action(PPO.load(args.ppo, device="cpu"))
    env = TmrEnv(layout=args.layout)
    if args.demo or args.seed is not None:
        trace = []
        results = [run_episode(env, policy, args.demo or "random", args.seed or 0, trace)]
        print("  t(s)     x(m)    y(m)  front(m)  goal(m)   v(m/s)  w(rad/s)")
        for row in trace[::10]:
            print(f"{row[0]:6.1f} {row[1]:8.3f} {row[2]:7.3f} {row[3]:9.3f} "
                  f"{row[4]:8.3f} {row[5]:8.3f} {row[6]:9.3f}")
    else:
        results = [run_episode(env, policy, "random", seed) for seed in EVALUATION_SEEDS]
    env.close()
    for row in results:
        print(f"{row['scenario']} seed={row['seed']} {row['outcome']}  t={row['time_s']:.1f} s  "
              f"path={row['path_m']:.3f} m  goal_error={row['goal_error_m']:.3f} m")
    counts = Counter(row["outcome"] for row in results)
    print(f"episodes={len(results)}  goal={counts['goal']}  collision={counts['collision']}  "
          f"timeout={counts['timeout']}")
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=results[0], lineterminator="\n")
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    main()
