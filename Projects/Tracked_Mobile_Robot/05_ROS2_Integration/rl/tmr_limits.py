"""Shared planar sensor and command limits for Gymnasium and the Gazebo adapter."""
import math
import numpy as np

DT = 0.1
MAX_LINEAR = 0.10
MAX_ANGULAR = 0.39
ROBOT_RADIUS = math.hypot(0.135, 0.134)
GOAL_RADIUS = 0.15
LASER_OFFSET = 0.065
SCAN_MIN, SCAN_MAX = 0.10, 8.0
RAY_ANGLES = np.arange(24) * math.tau / 24
