from pathlib import Path
import json, os, sys
from itertools import combinations
import FreeCAD as A,Part
V=A.Vector
r=Path(__file__).resolve().parent
model=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else r/'keyboard-placement.FCStd'
sys.path.insert(0, str(model.parent))
import pack_harness as P
d=A.openDocument(str(model))
pick=lambda label: next(o.Shape for o in d.Objects if o.Label.startswith(label))
def prism(x,y,z,w,h,t):return Part.makeBox(w,h,t,V(x,y,z))
floor=pick('Left tray section').fuse(pick('Right tray section')).common(prism(99,-66,-18,65,50,28))
expanded=pick('Pack clearance')
exit_window=prism(P.PACK_X-3,P.PACK_Y-4,P.PACK_Z-1.75,4.501,8.0,3.5)
pack=pick('CU-J450-V3')
assert abs(pack.BoundBox.XMax-P.PACK_X)<1.e-4 and abs(pack.BoundBox.YMin+31.-P.PACK_Y)<1.e-4, (pack.BoundBox, P.PACK_X, P.PACK_Y)
roi=prism(102,-70,-8,64,51,8.1)
def local_geoms(label):
    return Part.makeCompound([o for o in pick(label).Solids if o.BoundBox.intersect(roi.BoundBox)])
fixed={'tray':floor,'pack':pack,'expanded (outside lead exit)':expanded.cut(exit_window)}
moving={'PCB':pick('PCB •').common(roi),'switch contacts/pegs':local_geoms('67 switch,'),
        'LED':local_geoms('67 reverse'),'stabilizers':local_geoms('Four stabilizer')}
def board_frame(s,deg,dy):
    a=s.copy();a.translate(V(0,-dy,0));a.rotate(V(0,23,0),V(1,0,0),-deg);return a
states=[(0,0,0),(-3,0,0),(-6,0,0),(-9,0,0),(-12,0,0),(-12,-1,0),(-12,-2,0),(-12,-2,2),(-12,-2,4),(-12,-2,6)]

out={}
for ang,dy,pull in states:
    what=f'{ang}/{dy}/{pull}'
    comp=P.shapes(ang,dy,pull); metrics={}
    for k,sh in comp.items():
        board=board_frame(sh,ang,dy)
        for compare,ob in [*fixed.items(),*moving.items()]:
            test=sh if compare in fixed else board
            if ob.isNull() or not ob.Solids: continue
            touching=(k in P.SIGNALS and compare=='pack') or (k=='Header' and compare=='PCB')
            vol=test.common(ob).Volume if test.BoundBox.intersect(ob.BoundBox) else 0.
            if vol>1.e-5: raise ValueError((what,k,compare,'collision mm³',vol))
            if not touching and len(ob.Solids) and (ang==0 or k in P.SIGNALS):
                # Exact CAD clearance to the nearby geometry. Clipping excludes remote
                # keys, and all relevant bodies near the route remain in the ROI.
                dist=test.distToShape(ob)[0]
                name=('wire ' if k in P.SIGNALS else k+' ')+compare
                metrics[name]=min(metrics.get(name,1000),dist)
    for k1,k2 in combinations(comp,2):
        vol=comp[k1].common(comp[k2]).Volume
        if vol>1.e-5:raise ValueError((what,k1,k2,vol))
        if k1 in P.SIGNALS and k2 in P.SIGNALS:
            v=comp[k1].distToShape(comp[k2])[0]
            metrics['wire to wire']=min(metrics.get('wire to wire',1000),v)
    metrics['min R']=min(P.wire_route(i,ang,dy,pull)[2] for i in (1,2,3))
    out[what]={k:round(v,3) for k,v in metrics.items()}
    print(what,out[what],flush=True)


# Check the clear withdrawal corridor against all nearby board-side solids.
sweep=prism(P.EXIT_X-6,P.JACK_Y-4.05,-7.85,12.5,8.1,5.73)
sweep.rotate(V(P.EXIT_X,P.JACK_Y,0),V(0,0,1),P.YAW)
for name,ob in moving.items():
    if ob.isNull() or not ob.Solids:continue
    assert sweep.common(ob).Volume<1.e-5, name
    print('extraction corridor',name,round(sweep.distToShape(ob)[0],3),flush=True)
# Keep the floor measure separate from clearance to guide walls and other tray features.
flat_floor=prism(P.PACK_X-3,P.PACK_Y-30,-17,82,60,2.6)
floor_gap=float('inf');chord=0.;radius=float('inf')
samples=[(-v/2,0,0) for v in range(25)]+[(-12,-1,0)]+[(-12,-2,n/2) for n in range(13)]
for ang,dy,pull in samples:
    for i in (1,2,3):
        jacket,path,radius_i=P.wire_route(i,ang,dy,pull)
        assert abs(path.Length-P.WIRE_LENGTH)<1e-6
        floor_gap=min(floor_gap,jacket.distToShape(flat_floor)[0])
        chord=max(chord,(path.Edges[-1].Vertexes[-1].Point-path.Edges[0].Vertexes[0].Point).Length)
        radius=min(radius,radius_i)
print('dense pose count',len(samples),'floor clearance',round(floor_gap,3),'straight distance',round(chord,3),
      'excess',round(P.WIRE_LENGTH-chord,3),'bend radius',round(radius,3),flush=True)
