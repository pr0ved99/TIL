"""Planar TMR goal-reaching environment. Units are metres, seconds and radians."""

import math

import gymnasium as gym
import numpy as np
from gymnasium import spaces


from tmr_limits import DT, GOAL_RADIUS, LASER_OFFSET, MAX_ANGULAR, MAX_LINEAR, RAY_ANGLES, ROBOT_RADIUS, SCAN_MAX, SCAN_MIN
ROOM_HALF = 2.0
POST_RADIUS = 0.30
LAYOUTS = {
    "single": ((0.0, 0.0, POST_RADIUS),),
    "staggered": ((-0.55, 0.35, 0.26), (0.55, -0.35, 0.26)),
}

# Ordered pairs of distinct free points form the seeded start/goal distribution.
WAYPOINTS = np.array([(-1, -1), (0, -1), (1, -1), (1, 0),
                      (1, 1), (0, 1), (-1, 1), (-1, 0)], dtype=float)
SCENARIOS = {
    "straight": ((-1, -1), (1, -1)),
    "blocked": ((-1, 0), (1, 0)),
}


class TmrEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, max_steps=800, *, layout="single"):
        super().__init__()
        if not isinstance(max_steps, int) or max_steps < 1:
            raise ValueError("max_steps must be a positive integer")
        self.max_steps = max_steps
        if layout not in LAYOUTS:
            raise ValueError(f"unknown layout {layout!r}")
        self.posts = [(np.array([x, y]), radius) for x, y, radius in LAYOUTS[layout]]
        self.action_space = spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float32)
        # Scan in metres, goal distance, cos/sin of relative bearing, actual v/w.
        lower = [SCAN_MIN] * len(RAY_ANGLES) + [0, -1, -1, -MAX_LINEAR, -MAX_ANGULAR]
        upper = [SCAN_MAX] * len(RAY_ANGLES) + [math.sqrt(8) * ROOM_HALF, 1, 1, MAX_LINEAR, MAX_ANGULAR]
        self.observation_space = spaces.Box(np.array(lower, np.float32), np.array(upper, np.float32))
        self.needs_reset = True

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        scenario = (options or {}).get("scenario", "random")
        if scenario == "random":
            start, goal = WAYPOINTS[self.np_random.choice(len(WAYPOINTS), size=2, replace=False)]
            yaw = self.np_random.uniform(-math.pi, math.pi)
        elif scenario in SCENARIOS:
            start, goal = SCENARIOS[scenario]
            yaw = 0.0
        else:
            raise ValueError(f"unknown scenario {scenario!r}")
        self.position = np.array(start, dtype=float)
        self.goal = np.array(goal, dtype=float)
        self.yaw = yaw
        self.linear = self.angular = 0.0
        self.steps = 0
        self.needs_reset = False
        return self._observation(), self._info("running")

    def _scan(self):
        angles = self.yaw + RAY_ANGLES
        directions = np.column_stack((np.cos(angles), np.sin(angles)))
        origin = self.position + LASER_OFFSET * directions[0]
        # A ray hits the nearer of its signed x and y room boundaries.
        wall = np.full_like(directions, np.inf)
        np.divide(np.copysign(ROOM_HALF, directions) - origin, directions,
                  out=wall, where=np.abs(directions) > 1e-12)
        distances = wall.min(axis=1)
        for center, radius in self.posts:
            relative = origin - center
            projection = directions @ -relative
            discriminant = radius**2 - (relative @ relative - projection**2)
            near = projection - np.sqrt(np.maximum(discriminant, 0))
            post_distance = np.where((discriminant >= 0) & (near >= 0), near, np.inf)
            distances = np.minimum(distances, post_distance)
        return np.clip(distances, SCAN_MIN, SCAN_MAX)

    def _observation(self):
        dx, dy = self.goal - self.position
        bearing = math.atan2(dy, dx) - self.yaw
        goal_and_speed = [math.hypot(dx, dy), math.cos(bearing), math.sin(bearing),
                          self.linear, self.angular]
        return np.concatenate((self._scan(), goal_and_speed)).astype(np.float32)

    def _info(self, outcome):
        return {"outcome": outcome, "steps": self.steps,
                "pose": (*self.position.tolist(), self.yaw), "goal": tuple(self.goal.tolist())}

    def _hits_obstacle(self, delta):
        end = self.position + delta
        if np.any(np.abs(end) >= ROOM_HALF - ROBOT_RADIUS):
            return True
        length_squared = delta @ delta
        for center, radius in self.posts:
            relative = self.position - center
            fraction = np.clip(-(relative @ delta) / length_squared, 0, 1) if length_squared else 0
            if np.linalg.norm(relative + fraction * delta) <= radius + ROBOT_RADIUS:
                return True
        return False

    def step(self, action):
        if self.needs_reset:
            raise gym.error.ResetNeeded("call reset() to start an episode")
        action = np.asarray(action, dtype=np.float32)
        if not self.action_space.contains(action):
            raise ValueError("action must contain two finite values in [-1, 1]")
        linear = float(action[0]) * MAX_LINEAR
        angular = float(action[1]) * MAX_ANGULAR
        yaw = math.remainder(self.yaw + angular * DT, math.tau)
        delta = linear * DT * np.array([math.cos(yaw), math.sin(yaw)])
        old_distance = np.linalg.norm(self.goal - self.position)
        collision = self._hits_obstacle(delta)
        if collision:
            self.linear = self.angular = 0.0
        else:
            self.position += delta
            self.yaw, self.linear, self.angular = yaw, linear, angular
        self.steps += 1
        distance = np.linalg.norm(self.goal - self.position)
        arrived = bool(distance <= GOAL_RADIUS)
        terminated = bool(collision or arrived)
        truncated = self.steps >= self.max_steps and not terminated
        reward = float(old_distance - distance) - 0.001 - 0.0005 * abs(float(action[1]))
        outcome = "running"
        if collision:
            outcome, reward = "collision", reward - 5.0
        elif arrived:
            outcome, reward = "goal", reward + 5.0
        elif truncated:
            outcome = "timeout"
        self.needs_reset = terminated or truncated
        return self._observation(), reward, terminated, truncated, self._info(outcome)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Apply a constant TMR velocity in the 2D room.")
    parser.add_argument("--linear", type=float, default=0.10, help="linear velocity in m/s")
    parser.add_argument("--angular", type=float, default=0.0, help="angular velocity in rad/s")
    parser.add_argument("--steps", type=int, default=10, help="number of 0.1 s steps")
    parser.add_argument("--scenario", choices=SCENARIOS, default="straight")
    args = parser.parse_args()
    if not (-MAX_LINEAR <= args.linear <= MAX_LINEAR and -MAX_ANGULAR <= args.angular <= MAX_ANGULAR):
        parser.error("use linear velocity in [-0.10, 0.10] and angular velocity in [-0.39, 0.39]")
    if args.steps < 1:
        parser.error("steps must be positive")
    env = TmrEnv()
    obs, initial = env.reset(options={"scenario": args.scenario})
    print(f"start={initial['pose']} goal={initial['goal']} front_scan={obs[0]:.3f} m")
    action = [args.linear / MAX_LINEAR, args.angular / MAX_ANGULAR]
    for _ in range(args.steps):
        obs, _, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
    dx, dy, dyaw = np.subtract(info["pose"], initial["pose"])
    print(f"t={info['steps'] * DT:.1f} s  dx={dx:+.3f} m  dy={dy:+.3f} m  "
          f"yaw_change={math.degrees(dyaw):+.2f} deg  front_scan={obs[0]:.3f} m  {info['outcome']}")
