"""Audit the archived traces and write one row for each predeclared goal."""
import csv
import gzip
import json
import math
from pathlib import Path
import sys
from tarfile import open as open_tar
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent/'2026-11-23_tmr_nav03_baseline/p01_contacts'))
from contacts import summarize

STATUS = {4:'SUCCEEDED', 5:'CANCELED', 6:'ABORTED'}


def write_csv(path, rows, keys):
    with path.open('w', newline='') as stream:
        w = csv.DictWriter(stream, fieldnames=keys, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def obs(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def first_sustained_stop(samples, trigger, cutoff, limit):
    samples = [r for r in samples if trigger <= r[0] < cutoff]
    last_motion = max((i for i,r in enumerate(samples) if max(map(abs,r[1:])) > limit), default=-1)
    zero = samples[last_motion+1:]
    return zero[0][0] if zero else None


def evaluate(directory, protocol, route, seed):
    d = json.loads((directory/'result.json').read_text())
    dispatch = json.loads((directory/'dispatch.json').read_text())
    assert d['route'] == dispatch['route'] == route and d['seed'] == dispatch['seed'] == seed
    assert d['goal'] == dispatch['goal'] == protocol['goals'][route]
    trace = obs(directory/'trace.json.gz')
    contact = summarize(obs(directory/'contacts.json.gz'),round(protocol['contact']['episode_release_gap_s'] * 1e9))
    assert contact == d['contact']
    world = trace['world_pose']
    start, done, end = d['sim_interval']
    goal = d['goal']
    xy = math.dist(world[-1][1:3], goal[:2])
    yaw = abs(math.degrees(math.remainder(world[-1][3]-goal[2],math.tau)))
    assert math.isclose(xy,d['xy_error_m']) and math.isclose(yaw,d['yaw_error_deg'])
    assert max(world[0][0]-start,end-world[-1][0]) <= .1
    assert d['last_cmd'] == trace['cmd_vel'][-1][1:]
    stop = protocol['stop']
    settled = [r for r in trace['odom'] if r[0] >= done + stop['settle_delay_sim_s']]
    span = settled[-1][0]-settled[0][0] if settled else 0
    stopped = (span >= stop['observed_sim_s'] and max(abs(v) for r in settled for v in r[1:]) <= stop['max_abs_component']
               and max(map(abs,d['last_cmd'])) <= stop['max_abs_component'])
    episodes = len(contact['obstacle_episodes'])
    coverage = (contact['ground_physics_stamps'] > 0 and contact['max_ground_gap_ms'] <= 1000*protocol['contact']['max_ground_heartbeat_gap_s']
                and not contact['records'].get('unknown',0))
    status = STATUS.get(d['action_status'],str(d['action_status']))
    faults = []
    if status != 'SUCCEEDED': faults.append(status)
    if d['timeout']: faults.append('TIMEOUT')
    if episodes: faults.append('CONTACT')
    if not coverage: faults.append('CONTACT_COVERAGE')
    if xy > protocol['max_final_world_xy_m']: faults.append('XY')
    if yaw > protocol['max_final_world_yaw_deg']: faults.append('YAW')
    if not stopped: faults.append('STOP')
    row = dict(route=route,seed=seed,status=status,timeout=d['timeout'],obstacle_episodes=episodes,
               contact_valid=coverage,ground_gap_ms=contact['max_ground_gap_ms'],stopped=stopped,
               stop_window_s=round(span,4),xy_error_m=round(xy,6),yaw_error_deg=round(yaw,5),
               goal_x_m=goal[0],goal_y_m=goal[1],goal_yaw_deg=round(math.degrees(goal[2]),4),
               world_x_m=round(world[-1][1],6),world_y_m=round(world[-1][2],6),world_yaw_deg=round(math.degrees(world[-1][3]),5),
               map_x_m=round(d['map_final'][0],6),map_y_m=round(d['map_final'][1],6),map_yaw_deg=round(math.degrees(d['map_final'][2]),5),
               sim_s=round(d['sim_s'],4),wall_s=round(d['wall_s'],4),rtf=round(d['rtf'],5),
               path_m=round(d['path_m'],6),plan_updates=d['plan_updates'],recoveries=d['recoveries'],nav_error_code=d['nav_error_code'],
               goal_uuid=d['goal_id'],reasons=' '.join(faults))
    if d['case'] in ('cancel','scan_loss'):
        trigger = d['trigger_sim']
        assert trigger is not None
        loss = d['case']=='scan_loss'
        cutoff = d['cancel_sim'] if loss and d['cancel_sim'] is not None else end + 1e-6
        ref = max(t for t in trace['scan_stamps'] if t < cutoff) if loss else trigger
        cmd = first_sustained_stop(trace['cmd_vel'],trigger,cutoff,stop['max_abs_component'])
        odom = first_sustained_stop(trace['odom'],trigger,cutoff,stop['max_abs_component'])
        return dict(case=d['case'],route=route,seed=seed,status=status,trigger_sim_s=trigger,
                    reference_sim_s=ref,zero_cmd_sim_s=cmd,stopped_odom_sim_s=odom,
                    cmd_delay_s=round(cmd-ref,4) if cmd is not None else None,
                    odom_delay_s=round(odom-ref,4) if odom is not None else None,
                    action_end_sim_s=done, observation_end_sim_s=end,
                    observed_stopped_s=round(min(end,cutoff)-odom,4) if odom is not None else None,
                    cancel_request_sim_s=d['cancel_sim'],post_action_stopped=stopped,obstacle_episodes=episodes,contact_valid=coverage,
                    goal_uuid=d['goal_id'])
    return row


def main():
    protocol = yaml.safe_load((ROOT/'protocol.yaml').read_text())
    archive = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'runs.tar.gz'
    scored, aux = [], []
    with tempfile.TemporaryDirectory() as temp, open_tar(archive) as tar:
        tar.extractall(temp,filter='data')
        runs = Path(temp)
        for route in protocol['goals']:
            for seed in protocol['gazebo_seeds']:
                scored.append(evaluate(runs/f'{route}-{seed}',protocol,route,seed))
        a = protocol['auxiliary']
        for case in a['cases']:
            aux.append(evaluate(runs/f'aux-{case}',protocol,a['route'],a['seed']))
    write_csv(ROOT/'results.csv',scored,scored[0].keys())
    write_csv(ROOT/'auxiliary.csv',aux,aux[0].keys())
    keys = ['route','seed','status','reasons','xy_error_m','yaw_error_deg','recoveries']
    failures = [{k:r[k] for k in keys} for r in scored if r['reasons']]
    write_csv(ROOT/'failures.csv',failures,keys)
    succeeded = sum(r['status']=='SUCCEEDED' for r in scored)
    summary = dict(completed=len(scored),succeeded=succeeded,all_conditions=sum(not r['reasons'] for r in scored),
                   obstacle_episodes=sum(r['obstacle_episodes'] for r in scored),valid_contact_runs=sum(r['contact_valid'] for r in scored),
                   verified_stop_runs=sum(r['stopped'] for r in scored),max_xy_m=max(r['xy_error_m'] for r in scored),
                   max_yaw_deg=max(r['yaw_error_deg'] for r in scored),
                   main_gate=(succeeded>=protocol['minimum_succeeded'] and all(set(r['reasons'].split()) <= {'CANCELED','ABORTED','TIMEOUT'} for r in scored)),
                   auxiliary=aux)
    (ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':
    main()
