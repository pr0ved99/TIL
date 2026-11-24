"""Steer towards the goal through a short corridor clear of scan returns."""

import math

import numpy as np

from tmr_limits import LASER_OFFSET, MAX_ANGULAR, RAY_ANGLES, ROBOT_RADIUS


LOOKAHEAD = 0.75  # metres
CLEARANCE = ROBOT_RADIUS + 0.09  # allow for the gaps between the sparse scan rays
TURN_ONLY_ANGLE = math.radians(40)
SCAN_DIRECTIONS = np.column_stack((np.cos(RAY_ANGLES), np.sin(RAY_ANGLES)))
# Try the goal heading first, then alternate left and right in 15-degree increments.
OFFSETS = np.deg2rad([0] + [sign * a for a in range(15, 180, 15) for sign in (1, -1)] + [180])


def rule_action(observation):
    """Choose a normalized [linear, angular] action from one RL-01 observation."""
    distances = observation[:len(RAY_ANGLES)]
    goal_distance, goal_cos, goal_sin = observation[-5:-2]
    goal_angle = math.atan2(goal_sin, goal_cos)
    hits = distances[:, None] * SCAN_DIRECTIONS + [LASER_OFFSET, 0]

    angles = goal_angle + OFFSETS
    directions = np.column_stack((np.cos(angles), np.sin(angles)))
    # For each proposed path segment, find the closest point to every detected hit.
    along = np.clip(directions @ hits.T, 0, min(LOOKAHEAD, goal_distance))
    separation = hits[None, :, :] - along[:, :, None] * directions[:, None, :]
    clear = np.all(np.sum(separation**2, axis=2) > CLEARANCE**2, axis=1)
    if not np.any(clear):
        return np.zeros(2, dtype=np.float32)

    # At an almost symmetric obstacle, prefer passing on the left. The one-ray
    # bias avoids swapping sides when the nearest echo moves to an adjacent ray.
    headings = np.arctan2(np.sin(angles), np.cos(angles))
    cost = np.abs(OFFSETS) + math.radians(16) * (OFFSETS < 0)
    index = 0 if clear[0] else np.argmin(np.where(clear, cost, np.inf))
    steering = float(headings[index])
    linear = max(0.0, 1.0 - abs(steering) / TURN_ONLY_ANGLE)
    angular = np.clip(1.5 * steering / MAX_ANGULAR, -1.0, 1.0)
    return np.array([linear, angular], dtype=np.float32)
