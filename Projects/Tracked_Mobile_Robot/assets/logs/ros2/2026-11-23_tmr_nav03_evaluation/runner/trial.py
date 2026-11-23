"""Send one predeclared ROS goal and save its action, motion, contact and stop observations."""
from collections import deque
from pathlib import Path
import gzip
import json
import math
import os
import signal
import sys
import time

import rclpy
import yaml
from geometry_msgs.msg import Twist
from gz.msgs10.pose_v_pb2 import Pose_V
from gz.transport13 import Node as GzNode
from lifecycle_msgs.srv import GetState
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import SetInitialPose
from nav_msgs.msg import Odometry, OccupancyGrid, Path as NavPath
from rcl_interfaces.srv import GetParameters
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, DurabilityPolicy, qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'2026-11-23_tmr_nav03_baseline/p01_contacts'))
from contacts import ContactRecorder, save_raw, summarize, to_ns

def ros_seconds(stamp):
    return stamp.sec + stamp.nanosec / 1e9

def yaw(q):
    return math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))

def twist(t):
    return [t.linear.x,t.linear.y,t.linear.z,t.angular.x,t.angular.y,t.angular.z]

def save(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    tmp.replace(path)

def run():
    route,seed,case,out = sys.argv[1:]
    out=Path(out)
    proto=yaml.safe_load((ROOT/'protocol.yaml').read_text())
    goal=proto['goals'][route]
    rclpy.init()
    node=rclpy.create_node('tmr_evaluator',parameter_overrides=[rclpy.Parameter('use_sim_time',value=True)])
    gz=GzNode()
    contacts=ContactRecorder(gz,json.loads((ROOT/'inputs/topics.json').read_text()))
    tf=Buffer()
    listener=TransformListener(tf,node)
    odom=[]; commands=[]; scans=[]; poses=[]; feedback=[]; plan_lengths=[]; maps=deque(maxlen=1)
    def pose_cb(m):
        for p in m.pose:
            if p.name=='tmr':
                poses.append([to_ns(m.header.stamp)/1e9,p.position.x,p.position.y,yaw(p.orientation)])
                break
    gz.subscribe(Pose_V,'/world/empty/dynamic_pose/info',pose_cb)
    node.create_subscription(Odometry,'/odom',lambda m:odom.append([ros_seconds(m.header.stamp),*twist(m.twist.twist)]),qos_profile_sensor_data)
    node.create_subscription(Twist,'/cmd_vel',lambda m:commands.append([node.get_clock().now().nanoseconds/1e9,*twist(m)]),30)
    def scan_cb(m):
        i=round(-m.angle_min/m.angle_increment)
        scans.append([ros_seconds(m.header.stamp),len(m.ranges),m.ranges[i]])
    node.create_subscription(LaserScan,'/scan',scan_cb,qos_profile_sensor_data)
    node.create_subscription(OccupancyGrid,'/map', lambda m:maps.append((m.info.width,m.info.height)),QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
    def plan_cb(m):
        xy=[(p.pose.position.x,p.pose.position.y) for p in m.poses]
        if xy: plan_lengths.append([ros_seconds(m.header.stamp),len(xy),sum(math.dist(a,b) for a,b in zip(xy,xy[1:]))])
    node.create_subscription(NavPath,'/plan',plan_cb,10)
    def wait(pred,secs,why):
        until=time.monotonic()+secs
        while not pred():
            if time.monotonic()>until: raise TimeoutError(why)
            rclpy.spin_once(node,timeout_sec=.04)
    def get(future,secs,why):
        wait(future.done,secs,why)
        return future.result()
    def map_pose():
        p=tf.lookup_transform('map','base_footprint',Time()).transform
        return [p.translation.x,p.translation.y,yaw(p.rotation)]
    init=node.create_client(SetInitialPose,'/set_initial_pose')
    life=node.create_client(GetState,'/bt_navigator/get_state')
    nav=ActionClient(node,NavigateToPose,'/navigate_to_pose')
    cfg=node.create_client(GetParameters,'/controller_server/get_parameters')
    wait(lambda:bool(scans and odom and poses and maps and init.service_is_ready() and cfg.service_is_ready() and tf.can_transform('odom','base_footprint',Time())),65,'initial scan/map/pose/services')
    req=SetInitialPose.Request()
    req.pose.header.frame_id='map';req.pose.pose.pose.orientation.w=1.
    req.pose.header.stamp=Time(seconds=max(0.,odom[-1][0]-.1)).to_msg()
    get(init.call_async(req),8,'initialize localization')
    wait(lambda:tf.can_transform('map','base_footprint',Time()),15,'localization TF')
    wait(lambda:bool(life.service_is_ready() and nav.server_is_ready()),45,'navigator discovery')
    limit=time.monotonic()+50
    while get(life.call_async(GetState.Request()),12,'lifecycle call').current_state.label!='active':
        if time.monotonic()>limit: raise TimeoutError('navigator activation')
    wait(lambda:contacts.latest_stamp()>0 and contacts.all_advertised(),15,'contact sensor discovery')
    names=['general_goal_checker.xy_goal_tolerance','general_goal_checker.yaw_goal_tolerance','FollowPath.GoalAngleCritic.threshold_to_consider','progress_checker.required_movement_radius','progress_checker.movement_time_allowance','FollowPath.vx_max','FollowPath.wz_max']
    params=[v.double_value for v in get(cfg.call_async(GetParameters.Request(names=names)),8,'read parameters').values]
    assert params==[.15,.12,.15,.5,10.,.10,.39],params
    assert maps[-1]==tuple(proto['map']['size_pixels']) and scans[-1][1]==360 and .94<scans[-1][2]<1.04, (maps[-1],scans[-1])
    assert math.hypot(*poses[-1][1:3])<.01 and abs(poses[-1][3])<.03
    mp=map_pose(); assert math.hypot(*mp[:2])<.03 and abs(mp[2])<math.radians(5)
    if case=='bag':
        wait(lambda:all(any('bag' in x.node_name for x in node.get_subscriptions_info_by_topic(t)) for t in ['/odom','/scan','/tf','/cmd_vel','/map']),15,'representative bag subscriptions')
    sim_start=odom[-1][0]; wall_start=time.monotonic()
    request=NavigateToPose.Goal();request.pose.header.frame_id='map'
    p=request.pose.pose;p.position.x,p.position.y=goal[:2]
    p.orientation.z=math.sin(goal[2]/2);p.orientation.w=math.cos(goal[2]/2)
    def on_feedback(msg):
        f=msg.feedback
        feedback.append([f.number_of_recoveries,f.distance_remaining])
    save(out/'dispatch.json',{'route':route,'seed':int(seed),'case':case,'goal':goal,'epoch':time.time(),'parameters':dict(zip(names,params))})
    handle=get(nav.send_goal_async(request,feedback_callback=on_feedback),8,'goal response')
    if not handle.accepted:
        save(out/'rejected.json',{'reason':'goal rejected'})
        return
    future=handle.get_result_async()
    trigger=None;last_scan=None;timeout=False;cancel_sim=None
    while not future.done():
        rclpy.spin_once(node,timeout_sec=.04)
        elapsed=odom[-1][0]-sim_start
        if case in ('cancel','scan_loss') and trigger is None and elapsed>=2 and abs(odom[-1][1])>.025:
            trigger=odom[-1][0]
            if case=='scan_loss':
                os.killpg(int(os.environ['EVAL_SCAN_PID']),signal.SIGINT)
            else:
                cancel_sim=trigger
                get(handle.cancel_goal_async(),5,'cancel')
        if case=='scan_loss' and trigger is not None and cancel_sim is None and odom[-1][0]-trigger>=4.:
            cancel_sim=odom[-1][0];last_scan=scans[-1][0]
            get(handle.cancel_goal_async(),5,'cleanup cancel following loss observation')
        if time.monotonic()-wall_start>=proto['action_timeout_wall_s'] and not future.done():
            timeout=True
            if cancel_sim is None:
                cancel_sim=odom[-1][0];get(handle.cancel_goal_async(),5,'timeout cancel')
            break
    result=get(future,10,'action result');wall_s=time.monotonic()-wall_start;sim_end=odom[-1][0]
    wait(lambda:odom[-1][0]>=sim_end+2.65,12,'post-action observation')
    end=odom[-1][0]
    wait(lambda:contacts.latest_stamp()>=round(end*1e9)+15_000_000,5,'post-action contact coverage')
    contact_raw=contacts.snapshot(round(sim_start*1e9),round(end*1e9))
    save_raw(out/'contacts.json.gz',contact_raw)
    c=summarize(contact_raw)
    motion=[v for v in poses if sim_start<=v[0]<=end]
    if not motion: raise RuntimeError('No Gazebo ground truth during run')
    final=motion[-1][1:]
    target_odom=[v for v in odom if sim_end+.6<=v[0]<=end]
    speeds=[max(abs(s) for s in v[1:]) for v in target_odom]
    cs=[v for v in commands if sim_start-.01<=v[0]<=end+.04]
    checked=bool(speeds and target_odom[-1][0]-target_odom[0][0]>=1.99 and max(speeds)<=.001 and cs and max(map(abs,cs[-1][1:]))<=.001)
    row=dict(route=route,seed=int(seed),case=case,goal=goal,world_final=final,map_final=map_pose(),
             action_status=result.status,nav_error_code=result.result.error_code,timeout=timeout,goal_id=bytes(handle.goal_id.uuid).hex(),
             recoveries=max((v[0] for v in feedback),default=0),wall_s=wall_s,sim_s=sim_end-sim_start,rtf=(sim_end-sim_start)/wall_s,
             path_m=sum(math.dist(a[1:3],b[1:3]) for a,b in zip(motion,motion[1:])),
             xy_error_m=math.dist(final[:2],goal[:2]),yaw_error_deg=abs(math.degrees(math.remainder(final[2]-goal[2],math.tau))),
             stop_verified=checked,stop_odom_samples=len(target_odom),stop_window_s=target_odom[-1][0]-target_odom[0][0] if target_odom else None,
             max_abs_stopped_odom=max(speeds,default=None),last_cmd=cs[-1][1:] if cs else None,
             contact=c,world_samples=len(motion),plan_updates=len(plan_lengths),first_plan_m=plan_lengths[0][2] if plan_lengths else None,
             sim_interval=[sim_start,sim_end,end],trigger_sim=trigger,cancel_sim=cancel_sim,last_scan_before_cleanup=last_scan)
    trace=dict(world_pose=motion,odom=[v for v in odom if sim_start<=v[0]<=end],cmd_vel=cs,scan_stamps=[v[0] for v in scans if sim_start<=v[0]<=end],plan=plan_lengths)
    save_raw(out/'trace.json.gz',trace)
    save(out/'result.json',row)

if __name__=='__main__': run()
