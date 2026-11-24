"""Alpine Pass. Millimetres in assembled keyboard coordinates.

The right lid stands on its rear edge. The left skin and carrier share flat print datums. Mountains, firs and the
cabin are faceted solids with sloping skirts. The tray prints floor down.
"""
import FreeCAD as App
import Part

V = App.Vector
FACE = 8.4

def _face(points):
    return Part.Face(Part.makePolygon(points + [points[0]]))

def _solid(faces):
    shell = Part.makeShell(faces)
    solid = Part.makeSolid(shell)
    if solid.Volume < 0:
        solid.reverse()
    return solid

def _terrain(mapper, outline, centre):
    """One convex faceted landform. The rim penetrates the substrate by 0.08."""
    rim = [mapper(x,y,-.08) for x,y in outline]
    peak = mapper(*centre)
    faces = [_face(list(reversed(rim)))]
    faces.extend(_face([a,b,peak]) for a,b in zip(rim,rim[1:]+rim[:1]))
    return _solid(faces)

def _crag(mapper,x,y,w,h,z,lean):
    # A slanted summit, a shoulder and two differently oriented foreground facets.
    outer=[(-.51,-.42),(-.16,-.53),(.22,-.48),(.52,-.27),(.47,.12),
           (.20,.35),(lean,.53),(-.34,.36),(-.53,.00)]
    ring=[mapper(x+w*u,y+h*v,-.08) for u,v in outer]
    ridge=[mapper(x+w*u,y+h*v,z*t) for u,v,t in
           [(-.16,-.23,.39),(.12,-.15,.57),(.18,.14,.63),(lean,.30,1),
            (-.19,.10,.66)]]
    # Ordered inner points correspond to these perimeter vertices.
    idx=[0,0,1,1,2,2,3,4,4]
    faces=[_face(list(reversed(ring)))]
    for i in range(len(ring)):
        j=(i+1)%len(ring)
        faces.append(_face([ring[i],ring[j],ridge[idx[i]]]))
        if idx[i]!=idx[j]:
            faces.append(_face([ring[j],ridge[idx[j]],ridge[idx[i]]]))
    for i in range(1,len(ridge)-1):
        faces.append(_face([ridge[0],ridge[i],ridge[i+1]]))
    return _solid(faces)

def _fir(mapper,x,y,h,z):
    # Three skirted branches share a raised central rib. Substrate is visible
    # between adjacent boughs at the outside edges of each crown.
    half=h*.27
    pieces=[_terrain(mapper,[(x-h*.075,y),(x+h*.075,y),(x+h*.075,y+h*.35),
                             (x-h*.075,y+h*.35)],(x,y+h*.20,z*.54))]
    for bottom,tip,width,depth in ((.16,.67,1,1),(.38,.84,.80,.89),(.59,1,.59,.71)):
        b=y+bottom*h; t=y+tip*h; r=half*width
        outer=[(x-r,b+.08*h),(x-.43*r,b+.035*h),(x,b),
               (x+.55*r,b+.04*h),(x+r,b+.10*h),(x+.07*r,t)]
        pieces.append(_terrain(mapper,outer,(x-.06*r,b+(t-b)*.37,z*depth)))
    return pieces

def _gable(mapper,x,y):
    # Five-sided gable projects toward the typing edge. Rear roof slope rises
    # gradually from its sky edge when printed on the long rear rim.
    w,h=8.0,5.6
    ground=[(x-w/2,y),(x+w/2,y),(x+w/2,y+h),(x-w/2,y+h)]
    return [_terrain(mapper,ground,(x,y+2.8,2.4)),
            _terrain(mapper,[(x-4.7,y+.9),(x+4.7,y+.9),(x+1.8,y+5.9),(x-1.9,y+6.2)],
                    (x-.5,y+3.3,3.15))]

def _fuse(base, sculpt):
    result=base.multiFuse(sculpt).removeSplitter()
    assert len(result.Solids)==1 and result.isValid(), 'relief must be one valid solid'
    return result

def _sleeve_ramp(x,y):
    # A triangular gusset blends the full sleeve width into the plate.
    # A circular boss growing outward from an edge-on skin needs support
    # across its full rim. Span the complete 6 mm drop with a 45° ramp.
    r=3.30
    pts=[V(x-r,y,0),V(x-r,y+r,0),V(x-r,y+r+6.10,6.10),V(x-r,y,6.10)]
    wedge=_face(pts).extrude(V(2*r,0,0))
    # Fore/aft section retains the mating screw bore at its original location.
    bore=Part.makeCylinder(1.40,6.4,V(x,y,-.1))
    return wedge.cut(bore)

def build_cover(shape, side):
    # Lean the exposed ridge and bough crests toward the typing edge so the
    # rear-edge-down print overlaps the preceding layer along every art facet.
    top=lambda x,y,d:V(x,y-.4*max(0,d),FACE+d)
    if side=='left':
        crags=[(27,16,22,13,2.4,-.10),(42,17.9,31,13,3.85,.10),
               (57,16.8,25,12,3.0,-.09),(72,17,31,14,4.35,.10),
               (90,17.4,28,13,3.55,-.08),(105,15.6,27,13,3.2,.12),
               (117.7,16.3,16,11.4,2.3,-.04)]
        firs=[(17,5.2,8,1.85),(24,4.1,10.8,2.6),(32.4,4.9,8.2,2.05),
              (44,4.5,10.1,2.45),(49.8,6.1,7,1.6),(58,3.7,10.9,2.7),
              (78.1,5.2,9.3,2.35),(84,3.8,7.6,2.05),(96,4.25,12.1,3.05),
              (102.1,6.2,7.4,1.8),(114.3,4.6,9.6,2.5),(121,10.3,6.3,1.6)]
        mounts=[(8,13),(126,5),(181,13)]
    else:
        crags=[(219,17,22,13,2.65,-.12),(234.3,17.3,30,14,3.95,.11),
               (252,15.9,22,13,3.20,-.08)]
        firs=[(214.2,4.6,8.9,2.1),(222.6,3.8,10.1,2.6),(230.2,5,7.7,1.9),
              (243,4.1,11.6,2.8),(250,5.7,7.7,1.85),(256.2,4.8,8.8,2.0),
              (302.5,5.6,12.8,2.85)]
        mounts=[(205,13),(264,13)]
    relief=[_crag(top,*spec) for spec in crags]
    for tree in firs:
        relief.extend(_fir(top,*tree))
    if side=='left':
        relief.extend(_gable(top,68.3,4.4))
    ramps = [_sleeve_ramp(x,y) for x,y in mounts] if side == "right" else []
    return _fuse(shape,relief+ramps)

def _wall_motif(mapper,start,end,seed,scale=1):
    """Decorate straight portions of the enclosure, leaving all datums clear."""
    span=end-start
    count=max(2,round(span/26))
    dx=span/count
    pieces=[]
    for i in range(count):
        x=start+dx*(i+.5)
        h=scale*(12.7,15.0,10.7,13.9,12.2)[(i+seed)%5]
        pieces.append(_crag(mapper,x,-13.5+h*.50,dx*.96,h,
                           scale*(1.04,1.30,1.12)[i%3],(-.14,.12,.03)[(i+seed)%3]))
        if scale>.7:
            for shift,ht,depth in ((-.24,7.9,1.38),(.22,9.5,1.55)):
                tree_x=x+dx*shift
                pieces.extend(_fir(mapper,tree_x,-14.35,ht+(i%3)*.38,depth))
    return pieces

def build_tray(shape,side):
    left=side=='left'
    x0,x1=(-2.6,150.9) if left else (153.9,307.4)
    end_x=-7.50 if left else 312.30
    end_sign=-1 if left else 1
    front=lambda x,z,d:V(x,-105.-d,z)
    end=lambda u,z,d:V(end_x+end_sign*d,u,z)
    rear=lambda x,z,d:V(x,26.+d,z)
    pieces=_wall_motif(front,x0,x1,1 if left else 4)
    pieces+=_wall_motif(end,-99.6,21.0,0 if left else 2)
    # Lower rear band ends below the selector/port; keep all plug openings clear.
    pieces+=_wall_motif(rear,x0,x1,0 if left else 3,.46)
    return _fuse(shape,pieces)
