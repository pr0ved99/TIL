"""Run the frozen evaluation in isolated ROS domains and Gazebo partitions."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOPICS = '/clock /scan /odom /cmd_vel /tf /tf_static /map /plan /amcl_pose /navigate_to_pose/_action/status'.split()


def start(args, env, log):
    with log.open('w') as stream:
        return subprocess.Popen(args, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)


def stop(process):
    try:
        os.killpg(process.pid, signal.SIGINT)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def attempt(route, seed, case, directory, index):
    env = dict(os.environ, ROS_DOMAIN_ID=str(40+index), GZ_PARTITION=f'tmr-eval-{os.getpid()}-{index}-{directory.name}',
               EVAL_SEED=str(seed), ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST', PYTHONDONTWRITEBYTECODE='1')
    env['ROS_LOG_DIR'] = str(directory/'ros-log')
    processes = []
    try:
        processes.append(start(['ros2','launch',str(ROOT/'runner/stack.launch.py')],env,directory/'stack.log'))
        scan = start(['ros2','run','ros_gz_bridge','parameter_bridge','--ros-args','-r','__node:=eval_scan_bridge',
                      '-p','use_sim_time:=true','-p',f'config_file:={ROOT}/inputs/scan_bridge.yaml'],env,directory/'scan.log')
        processes.append(scan)
        env['EVAL_SCAN_PID'] = str(scan.pid)
        if case == 'bag':
            processes.append(start(['ros2','bag','record','-s','mcap','--storage-preset-profile','zstd_fast',
                                    '--use-sim-time','--include-hidden-topics','-o',str(directory/'bag'),'--topics',*TOPICS],env,directory/'bag.log'))
        trial = start([sys.executable,'-u',str(ROOT/'runner/trial.py'),route,str(seed),case,str(directory)],env,directory/'trial.log')
        processes.append(trial)
        deadline = time.monotonic() + 220
        while trial.poll() is None and processes[0].poll() is None and time.monotonic() < deadline:
            time.sleep(.25)
    finally:
        for process in reversed(processes):
            stop(process)


def main():
    dest = Path(sys.argv[1]).resolve()
    subprocess.run(['sha256sum','-c','--quiet','frozen_inputs.sha256'],cwd=ROOT,check=True)
    protocol = yaml.safe_load((ROOT/'protocol.yaml').read_text())
    cases = [(r,s,'bag' if f'{r}-{s}' == protocol['representative_bag'] else 'regular')
             for r in protocol['goals'] for s in protocol['gazebo_seeds']]
    aux = protocol['auxiliary']
    cases.extend((aux['route'],aux['seed'],case) for case in aux['cases'])
    for index,(route,seed,case) in enumerate(cases):
        ident = f'{route}-{seed}' if case in ('regular','bag') else f'aux-{case}'
        base = dest/ident
        if list(base.glob('attempt-*/dispatch.json')):
            print('retained dispatched goal', ident, flush=True)
            continue
        for _ in range(2):
            directory = base/f'attempt-{1+len(list(base.glob("attempt-*")))}'
            directory.mkdir(parents=True)
            print(time.strftime('%T'),ident,directory.name,'start',flush=True)
            attempt(route,seed,case,directory,index)
            if (directory/'dispatch.json').exists():
                print(time.strftime('%T'),ident,'recorded' if (directory/'result.json').exists() else 'dispatched; inspect incomplete outcome',flush=True)
                break
            print(ident,'infrastructure error before dispatch',flush=True)
        else:
            raise SystemExit(f'{ident}: inspect pre-dispatch setup before continuing')


if __name__ == '__main__':
    main()
