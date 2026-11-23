import json, os, time
from pathlib import Path
from gz.transport13 import Node
from gz.msgs10.pose_v_pb2 import Pose_V
from gz.msgs10.twist_pb2 import Twist
from contacts import ContactRecorder, NSEC, summarize, save_raw

if os.environ.get('GZ_PARTITION') != 'tmr-nav03-contact-inspect':
    raise RuntimeError('Use the dedicated Gazebo calibration partition')
node=Node()
rec=ContactRecorder(node,json.loads(Path('topics.json').read_text()))
pos={}
def on_pose(msg):
    for p in msg.pose:
        if p.name=='tmr':
            pos['xy']=[p.position.x,p.position.y]
node.subscribe(Pose_V,'/world/empty/dynamic_pose/info',on_pose)
cmd=node.advertise('/model/tmr/cmd_vel',Twist)
def send(v):
    message=Twist()
    message.linear.x=v
    if not cmd.publish(message):
        raise RuntimeError('Gazebo rejected command')
def wait_for_ready():
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        if rec.all_advertised() and rec.latest_stamp() and pos and cmd.has_connections():
            return
        time.sleep(.05)
    raise TimeoutError('Gazebo contact, pose or drive channel not ready')
wait_for_ready()
assert abs(pos['xy'][0])<.03 and abs(pos['xy'][1])<.03, pos
phases=[]
try:
    for name,speed,seconds in [('floor_only',0.,.6),('first_approach',.08,4.5),
                              ('back_away',-.08,2.0),('stand_clear',0.,.5),
                              ('second_approach',.08,3.3),('final_back_away',-.08,2.),
                              ('stop_clear',0.,.8)]:
        start=rec.latest_stamp()
        deadline=time.monotonic()+seconds*4+3
        initial=pos['xy']
        while rec.latest_stamp()-start<seconds*NSEC:
            if time.monotonic()>deadline:
                raise TimeoutError(f'No simulated ground-contact clock during {name}')
            send(speed)
            time.sleep(.05)
        phases.append({'name':name,'speed_m_s':speed,'start_ns':start,'end_ns':rec.latest_stamp(),'start_xy':initial,'end_xy':pos['xy']})
finally:
    send(0.)
raw=rec.snapshot(phases[0]['start_ns'],phases[-1]['end_ns'])
save_raw('calibration_contacts.json.gz',raw)
report=summarize(raw)
report['phases']=phases
report['advertised_topics']=rec.topics
report['phase_observations']={p['name']:summarize(rec.snapshot(p['start_ns'],p['end_ns'])) for p in phases}
Path('calibration.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:report[k] for k in ('records','max_ground_gap_ms','obstacle_episodes')},flush=True)
