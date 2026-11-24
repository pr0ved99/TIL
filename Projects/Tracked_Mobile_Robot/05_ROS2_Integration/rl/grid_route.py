"""Static room-B occupancy-grid A* for the map-assisted policy experiment."""
import heapq
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
import yaml

from tmr_limits import ROBOT_RADIUS


def plan_route(map_yaml, start, goal):
    cfg = yaml.safe_load(Path(map_yaml).read_text())
    grid = np.flipud(np.asarray(Image.open(Path(map_yaml).parent / cfg["image"])))
    res = cfg["resolution"]
    ox, oy, heading = cfg["origin"]
    if heading != 0 or cfg["negate"] or cfg["mode"] != "trinary":
        raise ValueError("expected axis-aligned room-B trinary map")
    # The dark walls and unknown area are both blocked. Half a cell diagonal
    # accounts for the extent of occupied pixels in the clearance calculation.
    free = (1 - grid.astype(float)/255) < cfg["free_thresh"]
    clearance = distance_transform_edt(free)*res - res/math.sqrt(2)
    valid = clearance >= ROBOT_RADIUS + .09
    def cell(p):
        return math.floor((p[1]-oy)/res), math.floor((p[0]-ox)/res)
    def allowed(i,j):
        return 0 <= i < valid.shape[0] and 0 <= j < valid.shape[1] and valid[i,j]
    first, last = cell(start), cell(goal)
    if not allowed(*first) or not allowed(*last):
        raise ValueError("endpoint blocked at planning clearance")
    pending = [(0.,0.,first)]
    costs, previous = {first: 0.}, {}
    while pending:
        _, cost, here = heapq.heappop(pending)
        if here == last:
            break
        if cost != costs[here]:
            continue
        i,j = here
        for di,dj in ((0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)):
            ni,nj = i+di,j+dj
            if not (allowed(ni,nj) and allowed(i,nj) and allowed(ni,j)):
                continue
            # Prefer room to turn beyond the hard footprint clearance.
            step = math.hypot(di,dj)*res*(1 + 5*max(0., .65-clearance[ni,nj]))
            new = cost+step
            if new < costs.get((ni,nj),math.inf):
                previous[ni,nj], costs[ni,nj] = here, new
                heapq.heappush(pending,(new+math.dist((ni,nj),last)*res,new,(ni,nj)))
    if last != first and last not in previous:
        raise ValueError("no free grid route")
    cells = [last]
    while cells[-1] != first:
        cells.append(previous[cells[-1]])
    path = [(ox+(j+.5)*res,oy+(i+.5)*res) for i,j in reversed(cells)]
    return [tuple(start), *path, tuple(goal)]


def lookahead(path, start_index, pos):
    near = min(range(start_index, min(len(path),start_index+18)), key=lambda i:math.dist(pos,path[i]))
    target = near
    along = 0.
    while target+1 < len(path) and along < .45:
        along += math.dist(path[target],path[target+1])
        target += 1
    return near, path[target]
