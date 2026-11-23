"""Plot Gazebo world trajectories on the evaluation map in metres."""
import csv
import gzip
import json
from pathlib import Path
import tarfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    protocol = yaml.safe_load((ROOT/'protocol.yaml').read_text())
    scores = list(csv.DictReader((ROOT/'results.csv').open()))
    fig, axes = plt.subplots(1,5,figsize=(14.5,3.55),sharex=True,sharey=True)
    palette = ['#19639a','#00836c','#c24e26','#6945b0']
    with tarfile.open(ROOT/'runs.tar.gz') as archive:
        for ax,(route,goal) in zip(axes,protocol['goals'].items()):
            for _,x,y,w,h in protocol['map']['boxes']:
                ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor='#a7abb4',edgecolor='#707887',lw=.6,zorder=1))
            for seed,color in zip(protocol['gazebo_seeds'],palette):
                raw = archive.extractfile(f'{route}-{seed}/trace.json.gz')
                trace = json.loads(gzip.decompress(raw.read()))['world_pose']
                ax.plot([r[1] for r in trace],[r[2] for r in trace],color=color,lw=1.25,label=str(seed))
                ax.plot(trace[-1][1],trace[-1][2],'o',color=color,markersize=3)
            ax.plot(0,0,'+',color='black',markersize=9,label='Start')
            ax.plot(goal[0],goal[1],'*',color='#222222',markersize=9,label='Goal')
            ax.set(xlim=(-1.95,2.95),ylim=(-2.05,1.85),aspect='equal',xlabel='x (m)',xticks=[-1,0,1,2],yticks=[-1,0,1])
            rows = [r for r in scores if r['route']==route]
            ax.set_title(f"{route}   {sum(r['status']=='SUCCEEDED' for r in rows)}/4 reached",fontsize=11)
            ax.grid(color='#d3d6da',lw=.4); ax.set_axisbelow(True)
    axes[0].set_ylabel('y (m)')
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.005),ncol=6,frameon=False)
    fig.suptitle('Gazebo world trajectories in evaluation room B',fontsize=14)
    fig.subplots_adjust(left=.05,right=.99,bottom=.22,top=.85,wspace=.16)
    fig.savefig(ROOT/'trajectories.png',dpi=155)
    plt.close(fig)


if __name__ == '__main__':
    main()
