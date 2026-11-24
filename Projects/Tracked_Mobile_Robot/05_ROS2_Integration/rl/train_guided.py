"""Warm-start a standalone PPO actor with rule demonstrations from the training room."""
import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from evaluate_baseline import deterministic_action, run_episode
from rule_policy import rule_action
from tmr_env import TmrEnv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    out = parser.parse_args().output
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    torch.set_num_threads(1)
    rng = np.random.default_rng(5101)
    env = TmrEnv()
    model = PPO("MlpPolicy", Monitor(TmrEnv(), str(out / "ppo.monitor.csv")), seed=5101,
                device="cpu", n_steps=1024, batch_size=128, n_epochs=4, learning_rate=0.00002,
                gamma=0.995, policy_kwargs=dict(net_arch=[128, 128], log_std_init=-2.0))
    policy = model.policy
    inputs, actions = [], []
    for seed in range(51000, 51256):
        obs, _ = env.reset(seed=seed)
        for _ in range(800):
            expert = rule_action(obs)
            inputs.append(obs)
            actions.append(expert)
            # Perturb the executed command to include off-course recovery examples.
            obs, _, term, trunc, _ = env.step(np.clip(expert + rng.normal(0, 0.30, 2), -1, 1))
            if term or trunc:
                break
    x = torch.tensor(np.array(inputs))
    y = torch.tensor(np.array(actions))
    teacher_fit = torch.optim.Adam(list(policy.mlp_extractor.policy_net.parameters())
                                   + list(policy.action_net.parameters()), lr=0.001)
    for epoch in range(36):
        for idx in torch.randperm(len(x)).split(256):
            pred = policy.action_net(policy.mlp_extractor.forward_actor(x[idx]))
            loss = torch.nn.functional.mse_loss(pred, y[idx])
            teacher_fit.zero_grad()
            loss.backward()
            teacher_fit.step()
    print(f"Fitted {len(x)} state/action pairs; starting PPO updates", flush=True)
    model.learn(total_timesteps=16_384)
    model.save(out / "ppo.zip")
    model.get_env().close()
    model = PPO.load(out / "ppo.zip", device="cpu")
    rows = [run_episode(env, deterministic_action(model), "random", seed) for seed in range(52000, 52020)]
    env.close()
    with (out / "qualification.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = dict(demo_seeds=[51000, 51255], demo_samples=len(x), fit_epochs=36, training_seed=5101,
                   ppo_steps=model.num_timesteps, room="single", qualification_seeds=[52000, 52019],
                   goals=sum(r["outcome"] == "goal" for r in rows),
                   collisions=sum(r["outcome"] == "collision" for r in rows),
                   timeouts=sum(r["outcome"] == "timeout" for r in rows),
                   elapsed_wall_s=round(time.monotonic()-start, 3))
    (out / "run.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(summary)


if __name__ == "__main__":
    main()
