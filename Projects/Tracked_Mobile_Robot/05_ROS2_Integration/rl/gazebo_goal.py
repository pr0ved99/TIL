"""Headless room-B experiment. Use via run_gazebo_goal.py in its private ROS/GZ session."""
import csv
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

sys.path.append("/usr/lib/python3/dist-packages")  # Ubuntu Gazebo Transport bindings

import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from gz.msgs10.pose_v_pb2 import Pose_V
from gz.transport13 import Node as GzNode
from nav_msgs.msg import Odometry
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

from rule_policy import rule_action
from tmr_limits import MAX_ANGULAR, MAX_LINEAR, RAY_ANGLES, SCAN_MAX, SCAN_MIN

PROJECT = Path(__file__).resolve().parents[2]
LOGS = PROJECT / "assets/logs/ros2"
INPUTS = LOGS / "2026-11-23_tmr_nav03_evaluation/inputs"
sys.path.insert(0, str(LOGS / "2026-11-23_tmr_nav03_baseline/p01_contacts"))
from contacts import ContactRecorder, classify, save_raw, summarize, to_ns


def yaw(q):
    return math.atan2(2 * (q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))


def ros_seconds(stamp):
    return stamp.sec + stamp.nanosec / 1e9


def scan24(scan):
    if (scan.header.frame_id != "laser_frame" or len(scan.ranges) != 360
            or not math.isfinite(scan.angle_increment) or scan.angle_increment <= 0
            or abs(scan.angle_increment * (len(scan.ranges)-1) - math.tau) > .03
            or abs(scan.range_min - SCAN_MIN) > .001 or abs(scan.range_max - SCAN_MAX) > .001):
        raise ValueError("unexpected TMR LaserScan frame, geometry or range")
    angles = (RAY_ANGLES - scan.angle_min) % math.tau
    indices = np.rint(angles / scan.angle_increment).astype(int) % len(scan.ranges)
    ranges = np.asarray(scan.ranges)[indices]
    if np.any(np.isnan(ranges)):
        raise ValueError("NaN in sampled laser ray")
    return np.clip(ranges, SCAN_MIN, SCAN_MAX)


def run(route, controller, out, checkpoint=None):
    protocol = json.loads((LOGS / "2026-11-24_tmr_rl05/protocol.json").read_text())
    gx, gy = protocol["routes"][route]
    route_points, path_index = [], 0
    if controller.startswith("guided_map"):
        from grid_route import plan_route, lookahead
        route_points = plan_route(INPUTS/"room_b.yaml", (0.,0.), (gx,gy))
        (out/"global_path.json").write_text(json.dumps(route_points)+"\n")
    action = rule_action
    if checkpoint:
        from numpy_actor import load_actor
        action = load_actor(checkpoint)

    rclpy.init()
    node = rclpy.create_node("tmr_rl05_trial", parameter_overrides=[rclpy.Parameter("use_sim_time", value=True)])
    tf = None
    if controller == "guided_map_amcl":
        from rclpy.time import Time
        from tf2_ros import Buffer, TransformListener
        tf = Buffer()
        listener = TransformListener(tf,node)
    gz = GzNode()
    contacts = ContactRecorder(gz, json.loads((INPUTS / "topics.json").read_text()))
    world, odometry, commands, observation_rows = [], [], [], []
    scans = deque(maxlen=1)
    def world_cb(msg):
        for p in msg.pose:
            if p.name == "tmr":
                world.append([to_ns(msg.header.stamp)/1e9, p.position.x, p.position.y, yaw(p.orientation)])
                break
    def odom_cb(msg):
        p, v = msg.pose.pose, msg.twist.twist
        if msg.header.frame_id != "odom" or msg.child_frame_id != "base_footprint":
            raise ValueError("unexpected odometry frames")
        odometry.append([ros_seconds(msg.header.stamp), p.position.x, p.position.y, yaw(p.orientation),
                         v.linear.x, v.linear.y, v.linear.z, v.angular.x, v.angular.y, v.angular.z])
    if not gz.subscribe(Pose_V, "/world/empty/dynamic_pose/info", world_cb):
        raise RuntimeError("Gazebo world pose subscription")
    node.create_subscription(Odometry, "/rl05/odom", odom_cb, qos_profile_sensor_data)
    node.create_subscription(LaserScan, "/rl05/scan", lambda msg: scans.append(msg), qos_profile_sensor_data)
    pub = node.create_publisher(Twist, "/rl05/cmd_vel", 3)

    def now():
        return node.get_clock().now().nanoseconds / 1e9
    def send(v=0., w=0.):
        msg = Twist()
        msg.linear.x, msg.angular.z = float(v), float(w)
        pub.publish(msg)
        commands.append([now(), float(v), float(w)])
    def wait(pred, limit, why):
        deadline = time.monotonic()+limit
        while not pred():
            if time.monotonic() > deadline:
                raise TimeoutError(why)
            rclpy.spin_once(node, timeout_sec=.025)

    try:
        wait(lambda: world and scans and odometry and now() > 0 and pub.get_subscription_count() >= 1
             and contacts.latest_stamp() and contacts.all_advertised(), 50, "simulator input discovery")
        if os.environ.get("RL05_RECORDING"):
            wait(lambda: all(any("bag" in s.node_name for s in node.get_subscriptions_info_by_topic(t))
                             for t in ("/rl05/scan","/rl05/odom","/rl05/cmd_vel")),15,"recorder discovery")
        if tf is not None:
            wait(lambda: tf.can_transform("map","odom",Time()),30,"initial AMCL map to odom")
        if math.hypot(*world[-1][1:3]) > .02 or math.hypot(*odometry[-1][1:3]) > .02:
            raise ValueError("unexpected starting position")
        initial_scan = scan24(scans[-1])
        if not .94 < initial_scan[0] < 1.04:
            raise ValueError(f"room B initial forward range {initial_scan[0]}")
        # Discovery can block while Gazebo keeps ticking. Warm inference with no
        # publication, then arm on a newer, timestamp-matched pair.
        action(np.array([*initial_scan, math.hypot(gx,gy), 1., 0., 0., 0.], dtype=np.float32))
        ready_stamp = ros_seconds(scans[-1].header.stamp)
        wait(lambda: ros_seconds(scans[-1].header.stamp) > ready_stamp
             and abs(now()-ros_seconds(scans[-1].header.stamp)) < .12
             and abs(now()-odometry[-1][0]) < .10
             and abs(odometry[-1][0]-ros_seconds(scans[-1].header.stamp)) < .075,
             15, "fresh scan and odometry to arm")
        start = now()
        last_scan = -1.
        wall_start = time.monotonic()
        reason = "time_limit"
        while now()-start < protocol["max_sim_s"] and time.monotonic()-wall_start < 150:
            rclpy.spin_once(node, timeout_sec=.025)
            scan = scans[-1]
            ts = ros_seconds(scan.header.stamp)
            if now()-ts > .30 or now()-odometry[-1][0] > .30:
                reason = "stale_input"
                break
            if now()-(last_scan if last_scan >= 0 else start) > .40:
                reason = "unpaired_inputs"
                break
            with contacts.lock:
                hit = any(classify(a,b,"tmr")[0] in ("obstacle","unknown") for a,b in contacts.pairs)
            if hit:
                reason = "contact"
                break
            if ts <= last_scan:
                continue
            odom = min(odometry[-12:], key=lambda row: abs(row[0]-ts))
            if abs(odom[0]-ts) > .075:
                continue
            last_scan = ts
            _, x, y, heading, v, _, _, _, _, w = odom
            if tf is not None:
                correction = tf.lookup_transform("map","odom",Time())
                if ts-ros_seconds(correction.header.stamp) > .20:
                    reason = "stale_map_transform"
                    break
                tr = correction.transform
                a = yaw(tr.rotation)
                x,y = (tr.translation.x + math.cos(a)*x - math.sin(a)*y,
                       tr.translation.y + math.sin(a)*x + math.cos(a)*y)
                heading += a
            tx, ty = gx,gy
            if route_points:
                path_index, (tx,ty) = lookahead(route_points,path_index,(x,y))
            d = math.hypot(tx-x, ty-y)
            bearing = math.atan2(ty-y, tx-x)-heading
            try:
                rays = scan24(scan)
            except ValueError as exc:
                reason = str(exc)
                break
            obs = np.array([*rays, d, math.cos(bearing), math.sin(bearing),
                            np.clip(v,-MAX_LINEAR,MAX_LINEAR), np.clip(w,-MAX_ANGULAR,MAX_ANGULAR)],
                           dtype=np.float32)
            if not np.isfinite(obs).all():
                raise ValueError("invalid policy input")
            if math.hypot(gx-x,gy-y) <= .10:
                reason = "target"
                break
            u = np.asarray(action(obs))
            if u.shape != (2,) or not np.isfinite(u).all() or np.max(abs(u)) > 1.00001:
                raise ValueError("invalid action")
            send(u[0]*MAX_LINEAR, u[1]*MAX_ANGULAR)
            observation_rows.append([ts, odom[0], x, y, heading, *obs.tolist(), *commands[-1][1:], tx,ty])
        end = now()
        send()
        last_zero = end
        def stopped_window_complete():
            nonlocal last_zero
            if now()-last_zero >= .1:
                send()
                last_zero = now()
            return odometry[-1][0] >= end+2.70 and world[-1][0] >= end+2.70
        wait(stopped_window_complete, 15, "stopped observation")
        finish = end+2.70
        wait(lambda: contacts.latest_stamp()/1e9 > finish+.02, 5, "last contact observation")
        raw = contacts.snapshot(round(start*1e9), round(finish*1e9))
        stats = summarize(raw)
        save_raw(out/"contacts.json.gz", raw)
        path = [r for r in world if start <= r[0] <= finish]
        motion = [r for r in odometry if start <= r[0] <= finish]
        quiet = [r for r in motion if r[0] >= end+.60]
        resting = [r for r in path if r[0] >= end+.60]
        if not path or not quiet or not resting:
            raise RuntimeError("incomplete stop observations")
        final = path[-1]
        err = math.hypot(final[1]-gx, final[2]-gy)
        max_twist = max(abs(z) for r in quiet for z in r[4:])
        world_drift = max(math.dist(r[1:3],final[1:3]) for r in resting)
        contact_ok = (stats["max_ground_gap_ms"] <= 100 and not stats["obstacle_episodes"]
                      and not stats["records"].get("unknown"))
        stop_ok = quiet[-1][0]-quiet[0][0] >= 2.0 and max_twist <= .001 and world_drift <= .002
        result = dict(controller=controller,route=route,goal=[gx,gy],gazebo_seed=protocol["gazebo_seed"],
                      reason=reason,world_final=final[1:],world_error_m=err,world_drift_stopped_m=world_drift,
                      stop_window_s=quiet[-1][0]-quiet[0][0],max_stopped_twist=max_twist,stop_ok=stop_ok,
                      contact_ok=contact_ok,obstacle_episodes=len(stats["obstacle_episodes"]),
                      ground_gap_ms=stats["max_ground_gap_ms"],control_steps=len(observation_rows),
                      sim_duration_s=end-start,world_path_m=sum(math.dist(a[1:3],b[1:3]) for a,b in zip(path,path[1:])),
                      pass_goal=bool(reason=="target" and err<=.15 and stop_ok and contact_ok and observation_rows))
        save_raw(out/"trace.json.gz", dict(world=path,odom=motion,commands=commands,interval=[start,end,finish]))
        with (out/"policy.csv").open("w",newline="") as f:
            writer = csv.writer(f,lineterminator="\n")
            writer.writerow(["scan_s","odom_s","x","y","yaw",*[f"ray_{i*15}" for i in range(24)],
                             "goal_distance","cos","sin","linear","angular","cmd_v","cmd_w","target_x","target_y"])
            writer.writerows(observation_rows)
        (out/"result.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
        print(result,flush=True)
    finally:
        send()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    if not os.environ.get("GZ_PARTITION","").startswith("tmr-rl05-"):
        raise SystemExit("use run_gazebo_goal.py to create the private simulation")
    run(sys.argv[1], sys.argv[2], Path(sys.argv[3]), sys.argv[4] if len(sys.argv)>4 else None)
