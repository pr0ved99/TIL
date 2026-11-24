"""Reproduce the RL-01 environment checks on a CPU."""

import math

import gymnasium
import numpy as np
from gymnasium.utils.env_checker import check_env

from tmr_env import ROBOT_RADIUS, WAYPOINTS, TmrEnv


def check_staggered_layout():
    with TmrEnv(layout="staggered") as env:
        check_env(env, skip_render_check=True)
        # Put the sensor west of each measured post centre, facing east.
        for x, y in [(-0.55, 0.35), (0.55, -0.35)]:
            assert np.all(np.linalg.norm(WAYPOINTS - [x, y], axis=1) > ROBOT_RADIUS + 0.26)
            env.reset(options={"scenario": "blocked"})
            env.position = np.array([x - 0.70, y])
            obs, *_ = env.step([0, 0])
            np.testing.assert_allclose(obs[0], 0.375, atol=1e-6)
            for step in range(1, 26):
                _, _, terminated, truncated, info = env.step([1, 0])
                assert terminated == (step == 25) and not truncated
            assert info["outcome"] == "collision"
    print("Staggered layout: free waypoints, both front ranges and contact steps PASS")


def rollout(env, scenario, action):
    obs, _ = env.reset(options={"scenario": scenario})
    total = 0.0
    while True:
        obs, reward, terminated, truncated, info = env.step(action)
        assert env.observation_space.contains(obs)
        total += reward
        if terminated or truncated:
            print(f"{scenario:8} action={action} outcome={info['outcome']:9} steps={info['steps']:3} "
                  f"terminated={terminated} truncated={truncated} return={total:.4f}")
            return info, terminated, truncated, total


def main():
    env = TmrEnv()
    check_env(env, skip_render_check=True)
    print(f"Gymnasium {gymnasium.__version__} check_env PASS | NumPy {np.__version__}")
    scan, _ = env.reset(options={"scenario": "blocked"})
    # Forward hits the post, left hits the wall, backward hits the opposite wall.
    np.testing.assert_allclose(scan[[0, 6, 12]], [0.635, 2.0, 1.065], atol=1e-6)
    np.testing.assert_allclose(scan[-5:], [2.0, 1.0, 0.0, 0.0, 0.0])
    print("scan front/left/rear (m):", *[f"{x:.3f}" for x in scan[[0, 6, 12]]])

    for action, expected, label in [
        ([1, 0], (0.10, 0, 0), "forward"), ([-1, 0], (-0.10, 0, 0), "reverse"),
        ([0, 1], (0, 0, 0.39), "left"), ([0, -1], (0, 0, -0.39), "right"),
    ]:
        _, initial = env.reset(options={"scenario": "straight"})
        for _ in range(10):
            obs, _, terminated, truncated, info = env.step(action)
            assert not terminated and not truncated
        change = np.subtract(info["pose"], initial["pose"])
        np.testing.assert_allclose(change, expected, atol=1e-10)
        np.testing.assert_allclose(obs[-2:], [action[0] * 0.10, action[1] * 0.39], atol=1e-7)
        print(f"{label:8} 1 s: dx={change[0]:+.3f} m, dy={change[1]:+.3f} m, "
              f"yaw change={math.degrees(change[2]):+.2f} deg")

    goal, term, trunc, goal_return = rollout(env, "straight", [1, 0])
    assert (goal["outcome"], term, trunc) == ("goal", True, False)
    assert math.dist(goal["pose"][:2], goal["goal"]) <= 0.15
    for scenario, action in [("blocked", [1, 0]), ("straight", [-1, 0])]:
        collision, term, trunc, collision_return = rollout(env, scenario, action)
        assert (collision["outcome"], term, trunc) == ("collision", True, False)
        assert collision_return < -0.8
    timeout, term, trunc, idle_return = rollout(env, "straight", [0, 0])
    assert (timeout["outcome"], term, trunc, timeout["steps"]) == ("timeout", False, True, 800)
    _, _, _, spin_return = rollout(env, "straight", [0, 1])
    assert spin_return < idle_return < 0 < goal_return
    try:
        env.step([0, 0])
    except gymnasium.error.ResetNeeded:
        pass
    else:
        raise AssertionError("step after timeout did not require reset")

    # A goal reached on the final permitted step is a termination.
    _, term, trunc, _ = rollout(TmrEnv(max_steps=goal["steps"]), "straight", [1, 0])
    assert term and not trunc
    env.reset(options={"scenario": "straight"})
    returns = [env.step(action)[1] for action in ([1, 0], [-1, 0])]
    np.testing.assert_allclose(sum(returns), -0.002, atol=1e-10)

    twin = TmrEnv()
    starts = set()
    for seed in range(32):
        obs, info = env.reset(seed=seed)
        same, duplicate = twin.reset(seed=seed)
        starts.add((info["pose"][:2], info["goal"]))
        assert info == duplicate and info["pose"][:2] != info["goal"]
        np.testing.assert_array_equal(obs, same)
        for action in np.random.default_rng(seed).uniform(-1, 1, (20, 2)):
            obs, *result = env.step(action)
            same, *repeated = twin.step(action)
            assert env.observation_space.contains(obs) and result == repeated
            np.testing.assert_array_equal(obs, same)
    assert len(starts) > 1
    print(f"32 seeded resets and 640 repeated steps PASS ({len(starts)} different start/goal pairs)")
    print("Reward, terminal flags and reset checks PASS")
    check_staggered_layout()


if __name__ == "__main__":
    main()
