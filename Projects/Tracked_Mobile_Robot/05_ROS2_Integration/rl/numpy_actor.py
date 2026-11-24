"""Export and replay the deterministic, two-tanh-layer SB3 actor on system NumPy."""
import argparse
from pathlib import Path

import numpy as np


def load_actor(path):
    with np.load(path, allow_pickle=False) as data:
        layers = [(data[f"w{i}"], data[f"b{i}"]) for i in range(3)]

    def predict(obs):
        x = np.asarray(obs, dtype=np.float32)
        for weights, bias in layers[:-1]:
            x = np.tanh(x @ weights.T + bias)
        weights, bias = layers[-1]
        return np.clip(x @ weights.T + bias, -1, 1)
    return predict


if __name__ == "__main__":
    from torch import nn
    from stable_baselines3 import PPO
    import torch
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    torch.set_num_threads(1)
    model = PPO.load(args.checkpoint, device="cpu")
    net = list(model.policy.mlp_extractor.policy_net) + [model.policy.action_net]
    if [type(layer) for layer in net] != [nn.Linear, nn.Tanh, nn.Linear, nn.Tanh, nn.Linear]:
        raise ValueError("unsupported policy architecture")
    arrays = {}
    for i, layer in enumerate(net[::2]):
        arrays[f"w{i}"] = layer.weight.detach().numpy()
        arrays[f"b{i}"] = layer.bias.detach().numpy()
    np.savez_compressed(args.output, **arrays)
    obs = np.random.default_rng(5101).uniform(model.observation_space.low, model.observation_space.high, (1024,29)).astype(np.float32)
    diff = abs(load_actor(args.output)(obs) - model.predict(obs, deterministic=True)[0]).max()
    print("1024 observation export check, max absolute action difference:", float(diff))
    assert diff < 2e-5
