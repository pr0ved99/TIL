"""Build a matching occupancy grid and SDF world from the frozen evaluation geometry."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[3]
INPUT = ROOT / 'inputs'
SIM = PROJECT / '05_ROS2_Integration/src/tmr_sim'
CONTACT = ROOT.parent / '2026-11-23_tmr_nav03_baseline/p01_contacts'
sys.path.insert(0, str(CONTACT))
from instrument_sdf import instrument
import json

def generate():
    protocol = yaml.safe_load((ROOT/'protocol.yaml').read_text())
    layout = protocol['map']
    limits = layout['bounds_free_m']
    cols, rows = layout['size_pixels']
    ox, oy = layout['origin_xy_m']
    res = layout['resolution_m']
    boxes = layout['boxes']
    raster = bytearray()
    for row in reversed(range(rows)):
        for col in range(cols):
            x, y = ox+(col+.5)*res, oy+(row+.5)*res
            occupied = any(abs(x-cx)<w/2 and abs(y-cy)<h/2 for _,cx,cy,w,h in boxes)
            inside = limits[0] < x < limits[1] and limits[2] < y < limits[3]
            raster.append(0 if occupied else (254 if inside else 205))
    (INPUT/'room_b.pgm').write_bytes(f'P5\n{cols} {rows}\n255\n'.encode()+raster)
    (INPUT/'room_b.yaml').write_text(yaml.safe_dump(dict(image='room_b.pgm',mode='trinary',resolution=res,origin=[ox,oy,0.],negate=0,occupied_thresh=.65,free_thresh=.25),sort_keys=False))
    context = ET.parse(SIM/'worlds/drive.sdf')
    world = context.find('world')
    for name,x,y,w,h in boxes:
        model = ET.SubElement(world,'model',name='eval_'+name)
        ET.SubElement(model,'static').text='true'
        ET.SubElement(model,'pose').text=f'{x} {y} 0.20 0 0 0'
        link = ET.SubElement(model,'link',name='body')
        for tag in ['visual','collision']:
            part=ET.SubElement(link,tag,name=tag)
            ET.SubElement(ET.SubElement(ET.SubElement(part,'geometry'),'box'),'size').text=f'{w} {h} 0.40'
    description=PROJECT/'05_ROS2_Integration/src/tmr_description/urdf/tmr.urdf.xacro'
    urdf=subprocess.check_output(['xacro',str(description),'gazebo_drive:=true'])
    (INPUT/'tmr.urdf').write_bytes(urdf)
    with TemporaryDirectory() as temp:
        sdf=Path(temp)/'base.sdf'
        sdf.write_bytes(subprocess.check_output(['gz','sdf','-p',str(INPUT/'tmr.urdf')]))
        observed=Path(temp)/'instrumented.sdf'
        topics=instrument(sdf,observed)
        assert len(topics)==5
        (INPUT/'topics.json').write_text(json.dumps(topics,indent=2)+'\n')
        robot=deepcopy(ET.parse(observed).getroot().find('model'))
        ET.SubElement(robot,'pose').text='0 0 0.02 0 0 0'
        world.append(robot)
    context.write(INPUT/'room_b.sdf',encoding='utf-8',xml_declaration=True)
    cfg=yaml.safe_load((SIM/'config/nav2_params.yaml').read_text())
    ctl=cfg['controller_server']['ros__parameters']
    c=protocol['candidate']
    ctl['general_goal_checker'].update(xy_goal_tolerance=c['xy_tolerance_m'],yaw_goal_tolerance=c['yaw_tolerance_rad'])
    ctl['FollowPath']['GoalAngleCritic']['threshold_to_consider']=c['goal_angle_distance_m']
    (INPUT/'navigation.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
    bridge=yaml.safe_load((SIM/'config/drive_bridge.yaml').read_text())
    for key,parts in [('bridge',[x for x in bridge if x['ros_topic_name']!='/scan']),('scan_bridge',[x for x in bridge if x['ros_topic_name']=='/scan'])]:
        (INPUT/f'{key}.yaml').write_text(yaml.safe_dump(parts,sort_keys=False))
if __name__=='__main__':
    generate()
