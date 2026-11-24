"""Run the single-seed TMR CPU PPO pilot and save its deterministic evaluations."""

import argparse
import csv
import json
import platform
import resource
import time
from collections import Counter
from importlib.metadata import version
from pathlib import Path

import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor

from evaluate_baseline import EVALUATION_SEEDS, deterministic_action, run_episode
from rule_policy import rule_action
from tmr_env import TmrEnv


SEED = 3101
TOTAL_STEPS = 65_536
WALL_LIMIT_S = 180
RSS_LIMIT_MIB = 2048


def peak_rss_mib():
    # Linux reports the process high-water mark in KiB.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


class TrainingBudget(BaseCallback):
    def _on_training_start(self):
        self.started = time.perf_counter()

    def check_limits(self):
        if time.perf_counter() - self.started >= WALL_LIMIT_S or peak_rss_mib() >= RSS_LIMIT_MIB:
            raise RuntimeError(f"training budget exhausted at {self.num_timesteps} steps")

    def _on_step(self):
        if self.num_timesteps % 128 == 0:
            self.check_limits()
        return True

    def _on_training_end(self):
        self.check_limits()


def evaluate(policy, label):
    env = TmrEnv()
    try:
        rows = [dict(policy=label, **run_episode(env, policy, "random", seed))
                for seed in EVALUATION_SEEDS]
    finally:
        env.close()
    counts = Counter(r["outcome"] for r in rows)
    print(f"{label}: goals={counts['goal']} collisions={counts['collision']} "
          f"timeouts={counts['timeout']}", flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new output directory for this run")
    parser.add_argument("--seed", type=int, default=SEED, help="PPO and training environment seed")
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"choose a new output directory: {args.output}")
    args.output.mkdir(parents=True)

    torch.set_num_threads(1)
    params = dict(n_steps=1024, batch_size=64, n_epochs=6, learning_rate=3e-4,
                  gamma=0.995, gae_lambda=0.95, clip_range=0.2,
                  policy_kwargs=dict(net_arch=[64, 64]))
    run_start = time.perf_counter()
    with Monitor(TmrEnv(), str(args.output / "train.monitor.csv"), info_keywords=("outcome",)) as train_env:
        model = PPO("MlpPolicy", train_env, seed=args.seed, device="cpu", **params)
        baseline = evaluate(rule_action, "rule")
        before = evaluate(deterministic_action(model), "ppo_initial")
        print(f"Training {TOTAL_STEPS} steps, seed={args.seed}, CPU threads=1", flush=True)
        start = time.perf_counter()
        model.learn(total_timesteps=TOTAL_STEPS, callback=TrainingBudget())
        training_seconds = time.perf_counter() - start
        training_peak = peak_rss_mib()
        assert model.num_timesteps == TOTAL_STEPS
        model.save(args.output / "ppo.zip")
    restored = PPO.load(args.output / "ppo.zip", device="cpu")
    after = evaluate(deterministic_action(restored), "ppo_final")
    with (args.output / "evaluation.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=before[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(baseline + before + after)
    summary = dict(
        training_seed=args.seed, evaluation_seeds=list(EVALUATION_SEEDS),
        training_steps=model.num_timesteps, device=str(model.device), torch_threads=torch.get_num_threads(),
        policy="MlpPolicy", params=params, training_limits=dict(seconds=WALL_LIMIT_S, peak_rss_mib=RSS_LIMIT_MIB),
        training_wall_s=round(training_seconds, 3), process_peak_through_training_mib=round(training_peak, 2),
        train_and_evaluate_wall_s=round(time.perf_counter() - run_start, 3),
        process_peak_mib=round(peak_rss_mib(), 2), python=platform.python_version(),
        packages={p: version(p) for p in ("stable-baselines3", "torch", "gymnasium", "numpy")},
    )
    (args.output / "run.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Training wall time {training_seconds:.2f} s, process peak through training "
          f"{training_peak:.1f} MiB. Results: {args.output}")


if __name__ == "__main__":
    main()
