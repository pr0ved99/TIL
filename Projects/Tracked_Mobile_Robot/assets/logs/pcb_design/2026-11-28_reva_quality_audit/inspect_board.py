"""Inspect as-saved KiCad copper, without changing the project. Usage: /usr/bin/python3 inspect_board.py BOARD > report.json"""
import collections, hashlib, heapq, itertools, json, math, sys
from pathlib import Path
import pcbnew as k

path = Path(sys.argv[1])
board = k.LoadBoard(str(path))
layers = [k.F_Cu, k.B_Cu]
def point(v):
    return (round(v.x/1e6, 6), round(v.y/1e6, 6))
def copper_layers(item):
    return [layer for layer in layers if item.IsOnLayer(layer)]
def label(item):
    return item.GetNetname().removeprefix('/')
pads = {f.GetReference()+'.'+p.GetNumber():p for f in board.GetFootprints() for p in f.Pads()}
holes = {s:p for s,p in pads.items() if p.GetAttribute()==k.PAD_ATTRIB_NPTH}
pads = {s:p for s,p in pads.items() if p.GetAttribute()!=k.PAD_ATTRIB_NPTH}
segments = [s for s in board.GetTracks() if s.GetClass()=='PCB_TRACK']
vias = [t for t in board.GetTracks() if t.GetClass()=='PCB_VIA']
tracks = [(label(s),s.GetLayer(),point(s.GetStart()),point(s.GetEnd()),s.GetWidth()/1e6) for s in segments]
inventory = {name:{'xy':point(p.GetPosition()),'net':label(p),'layer':[board.GetLayerName(l) for l in copper_layers(p)],'drill_mm':point(p.GetDrillSize())} for name,p in pads.items() if label(p) and not label(p).startswith('unconnected-')}
# Split traces at collinear endpoints/pad centres then join layers at plated pads/vias.
graph = collections.defaultdict(dict)
points = collections.defaultdict(set)
for net, layer, start, end, width in tracks:
    points[net,layer].update((start,end))
def join(a,b,w):
    graph[a][b]=graph[b][a]=w
def pin(name):
    p=pads[name]; return (label(p),copper_layers(p)[0],point(p.GetPosition()))
for p in [*pads.values(), *vias]:
    pos=point(p.GetPosition()); ls=copper_layers(p); name=label(p)
    for layer in ls: points[name,layer].add(pos)
    if len(ls)==2: join((name,ls[0],pos),(name,ls[1],pos),0)
for net,layer,start,end,_ in tracks:
    dx=end[0]-start[0];dy=end[1]-start[1]; length=math.hypot(dx,dy)
    if not length: continue
    mid=[]
    for pt in points[net,layer]:
        x,y=pt[0]-start[0],pt[1]-start[1];u=(x*dx+y*dy)/length
        if -1e-6<=u<=length+1e-6 and abs(dx*y-dy*x)/length<1e-5: mid.append((u,pt))
    mid.sort()
    for (u,p),(v,q) in zip(mid,mid[1:]): join((net,layer,p),(net,layer,q),v-u)
def route(a,b):
    start,end=pin(a),pin(b); heap=[(0,start)]; dist={start:0}; parents={}
    while heap:
        d,n=heapq.heappop(heap)
        if d>dist[n]:continue
        if n==end:
            nodes=[end]
            while nodes[-1]!=start:nodes.append(parents[nodes[-1]])
            nodes.reverse(); return {'mm':round(d,4),'straight_mm':round(math.dist(start[2],end[2]),4),'nodes':[[board.GetLayerName(l),*xy] for _,l,xy in nodes]}
        for v,w in graph[n].items():
            if d+w<dist.get(v,math.inf):
                dist[v]=d+w;parents[v]=n;heapq.heappush(heap,(d+w,v))
    return {'mm':None}
pairs=[('C7.1','U1.2'),('C7.2','U1.3'),('C8.1','U2.14'),('C8.2','U2.7'),('J2.7','C7.1'),('J2.7','U1.2')]
for i,p,j in [(1,38,3),(2,36,4),(3,35,5),(4,37,6)]:
    pairs.extend([(f'C{i}.1',f'J1.{p}'),(f'C{i}.1',f'TP{i+2}.1'),(f'C{i}.2','J1.20'),(f'J{j}.2','J1.20')])
pairs += [('J3.3','R1.1'),('J4.3','R2.1'),('J5.1','R4.1'),('J6.1','R6.1'),('U2.3','J1.32'),('U2.6','J1.34'),('C5.2','J1.20'),('C6.2','J1.20'),('C7.2','J1.20'),('C8.2','J1.20'),('J7.1','J1.20'),('J8.1','J1.20')]
routes={a+'-'+b:route(a,b) for a,b in pairs}

# Straight segment pairs. Report maximum projected overlap for each net pair;
# same-layer gap is edge-to-edge. Opposite-layer values are XY only.
overlap={}
for (n,l,a,b,w),(m,k2,c,d,v) in itertools.combinations(tracks,2):
    if m==n: continue
    length=math.dist(a,b); length2=math.dist(c,d)
    dx,dy=(b[0]-a[0])/length,(b[1]-a[1])/length
    if abs(dx*(d[1]-c[1])-dy*(d[0]-c[0]))>length2*1e-5:continue
    def projection(p):return (p[0]-a[0])*dx+(p[1]-a[1])*dy
    t1,t2=sorted([projection(c),projection(d)]); t0=max(t1,0);tend=min(length,t2); s=tend-t0
    gap=abs(dx*(c[1]-a[1])-dy*(c[0]-a[0]))-(w+v)/2
    if s<=0 or gap>1.0: continue
    key=','.join(sorted([n,m]))+('/same' if l==k2 else '/opposite')
    if key not in overlap or s>overlap[key]['parallel_mm']:
        overlap[key]={'parallel_mm':round(s,4),'xy_edge_gap_mm':round(gap,4),'nets':[n,m],'layers':[board.GetLayerName(l),board.GetLayerName(k2)],'from_xy':[round(a[0]+t0*dx,4),round(a[1]+t0*dy,4)],'to_xy':[round(a[0]+tend*dx,4),round(a[1]+tend*dy,4)],'segments':[[a,b],[c,d]]}

pad_items=[(key,p) for key,p in pads.items()]
line_items=[(label(s),s) for s in segments+vias]
def clearance(a,b,layer):return a.GetEffectiveShape(layer).GetClearance(b.GetEffectiveShape(layer))/1e6
def nearest(item,candidates,ignore_net):
    return min((clearance(item,other,l),name,board.GetLayerName(l)) for name,other in candidates if other!=item and (not ignore_net or not item.GetNetname() or item.GetNetCode()!=other.GetNetCode()) for l in copper_layers(other) if item.IsOnLayer(l))
via_pad=[]
for vi in vias:
    for name,p in pad_items:
        if p.GetAttribute()!=k.PAD_ATTRIB_SMD:continue
        l=copper_layers(p)[0]; hole=k.SHAPE_CIRCLE(vi.GetPosition(),vi.GetDrillValue()//2)
        if hole.GetClearance(p.GetEffectiveShape(l))==0:
            via_pad.append([name,label(vi),point(vi.GetPosition()),'hole intersects SMD copper'])
# Approximate curved outline with chords at <= 2 degree intervals (sagitta < 0.001 mm here).
outlines=[]
for shape in board.GetDrawings():
    if shape.GetLayer()!=k.Edge_Cuts:continue
    if shape.GetShapeStr()=='Line':
        points_edge=[shape.GetStart(),shape.GetEnd()]
    elif shape.GetShapeStr()=='Arc':
        c=shape.GetCenter(); a=shape.GetStart()
        start_angle=math.atan2(a.y-c.y,a.x-c.x); radius=math.hypot(a.x-c.x,a.y-c.y)
        sweep=shape.GetArcAngle().AsRadians(); steps=math.ceil(abs(math.degrees(sweep))/2)
        points_edge=[k.VECTOR2I(round(c.x+radius*math.cos(start_angle+sweep*i/steps)),round(c.y+radius*math.sin(start_angle+sweep*i/steps))) for i in range(steps+1)]
    else:raise ValueError(shape.GetShapeStr())
    outlines.extend(k.SHAPE_SEGMENT(a,b,0) for a,b in zip(points_edge,points_edge[1:]))
edge=min((obj.GetEffectiveShape(l).GetClearance(sh)/1e6,name,board.GetLayerName(l)) for name,obj in pad_items+line_items for l in copper_layers(obj) for sh in outlines)
drills=sorted(set((v.GetWidth(k.F_Cu)/1e6,v.GetDrillValue()/1e6) for v in vias))
# Exact KiCad shape separation for unlike networks on layers with both conductors.
materials=pad_items+line_items
minimum=min((clearance(a,b,l),n,m,board.GetLayerName(l)) for (n,a),(m,b) in itertools.combinations(materials,2) if a.GetNetCode()!=b.GetNetCode() for l in copper_layers(a) if b.IsOnLayer(l))
hole_dists={n:nearest(p,pad_items+line_items,False) for n,p in holes.items()}
tp_dists={n:nearest(p,pad_items+line_items,True) for n,p in pads.items() if n.startswith('TP')}
centres={(label(p),l,point(p.GetPosition())) for p in [*pads.values(),*vias] for l in copper_layers(p)}
corners=[]
for node,nb in graph.items():
    if len(nb)!=2 or node in centres:continue
    a,b=nb; p=node[2]
    dx,dy=a[2][0]-p[0],a[2][1]-p[1];ex,ey=b[2][0]-p[0],b[2][1]-p[1]
    if abs(dx*ex+dy*ey)<1e-6:corners.append((node[0],board.GetLayerName(node[1]),p))
data={'board_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'segment_count':len(segments),'via_count':len(vias),'zones':board.GetAreaCount(),'hole_drill_vs_smd':via_pad,'vias_diameter_drill':drills,'hole_edge_to_copper_mm':hole_dists,'min_edge_to_copper_mm':edge,'min_different_net_mm':minimum,'nearest_other_net_to_testpad_mm':tp_dists,'free_trace_90degree_bends':corners,'routes':routes,'longest_single_segment_parallel_within_1mm':overlap,'pads':inventory,'tracks':tracks}
json.dump(data,sys.stdout,indent=1)
