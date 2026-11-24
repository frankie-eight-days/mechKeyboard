"""BatterySpace CU-J450-V3 and Molex DuraClik routing study, millimetres.

The PCB is at Z=0 with its mounting face for J600 at Z=-1.60. Coordinate
axes match build_fit.py. Positive Y points toward the USB-C connector.
"""
import math
import FreeCAD as App
import Part

V=App.Vector
WIRE_LENGTH=42.0
WIRE_RADIUS=.70
EXIT_X=143.0
YAW=-30.
ENTRY_R=8.25
JACK_Y=-37.0
JACK_Z=-4.7
# Pouch corner nearest the front/left, in keyboard assembly coordinates.
BAY_X=41.0
BAY_Y=-75.0
PACK_X=BAY_X+68.0
PACK_Y=BAY_Y+31.0
PACK_Z=-8.5
COLORS={'Header':(.72,.72,.63),'Plug':(.88,.83,.69),
        'POS':(.76,.15,.10),'NTC':(.84,.82,.76),'GND':(.17,.18,.19)}
LABELS={'Header':'J600 • Molex 502352-0300 underside header envelope',
        'Plug':'CU-J450-V3 • mated Molex 502351-0300 plug envelope',
        'POS':'Pack pin 1 • PACK_POS • 42 mm nominal',
        'NTC':'Pack pin 2 • PACK_NTC • 42 mm nominal',
        'GND':'Pack pin 3 • GND • 42 mm nominal'}
SIGNALS=('POS','NTC','GND')

def _box(x,y,z,w,d,h):
    return Part.makeBox(w,d,h,V(x,y,z))

def connectors():
    """Keyed seating models from SD-502351-001 and SD-502352-001.

    Nominal three-position outer limits, 2 mm pitch and 11 mm mated extent.
    The cavities, latch detail and SMT leads are simplified. No crimp profile.
    """
    x,y=EXIT_X,JACK_Y
    # Header front is toward -X. The PCB mounting face is above the latch.
    housing=_box(x+1.60,y-5,-8,7.60,10,6.35)
    chamber=_box(x+1.59,y-4.13,-7.57,5.24,8.26,5.61)
    latch_space=_box(x+1.59,y-1.91,-7.91,4.75,3.82,.62)
    header=housing.cut(chamber.fuse(latch_space))
    metal=[]
    for side in (-1,1):
        metal.append(_box(x+2.1,y+side*4.55-.33,-2.12,4.85,.66,.52))
    for i in (-2.,0,2.):
        metal.extend([_box(x+8.7,y+i-.25,-2.05,2.3,.5,.45),
                      _box(x+5.45,y+i-.23,JACK_Z-.23,1.55,.46,.46)])
    header=header.multiFuse(metal).removeSplitter()
    nose=_box(x+.40,y-3.93,-7.42,6.10,7.86,5.2)
    lip=_box(x,y-4.05,-7.47,.40,8.10,5.35)
    latch=_box(x,y-1.75,-7.85,4.35,3.5,1.14)
    plug=nose.fuse(lip).fuse(latch)
    for off in (-2.,0,2.):
        opening=Part.makeCylinder(.82,6.60,V(x-.03,y+off,JACK_Z),V(1,0,0))
        plug=plug.cut(opening)
    plug=plug.removeSplitter()
    assert header.isValid() and plug.isValid()
    assert header.common(plug).Volume<1e-6
    for shape in (header,plug):
        shape.rotate(V(x,y,0),V(0,0,1),YAW)
    return header,plug

def move_board(shape,angle=0,dy=0):
    s=shape.copy()
    s.rotate(V(0,23,0),V(1,0,0),angle)
    s.translate(V(0,dy,0))
    return s

def wire_route(pin, angle=0., board_dy=0., withdraw=0.):
    """A 42 mm service bow formed by three tangent circular arcs.

    Offsetting each planar path along its normal retains conductor separation.
    The signed turning angles sum to zero, preserving each lead's arc length.
    The bend straightens at the 12-degree keybed insertion posture.
    """
    angle=math.radians(angle)
    offset=(pin-2)*2.
    # Front of the keyboard is at -Y. Viewed into the underside-mounted header
    # from the pack, circuit 1 is on the -Y side of the latch and circuit 3 +Y.
    source=V(PACK_X,PACK_Y,PACK_Z)
    beta=math.radians(-YAW)
    curved_length=(ENTRY_R+offset)*beta
    main_length=WIRE_LENGTH-curved_length
    tangent_x=EXIT_X-ENTRY_R*math.sin(beta)-withdraw*math.cos(beta)
    tangent_y=JACK_Y+ENTRY_R*(1-math.cos(beta))+offset+withdraw*math.sin(beta)
    ey=23+(tangent_y-23)*math.cos(angle)-JACK_Z*math.sin(angle)+board_dy
    ez=(tangent_y-23)*math.sin(angle)+JACK_Z*math.cos(angle)
    dx=tangent_x-PACK_X
    v=V(0,ey-offset-PACK_Y,ez-PACK_Z)
    transverse=v.Length
    chord=math.hypot(dx,transverse)
    assert chord<main_length
    v.normalize()
    ux=V(1,0,0)
    normal=ux.cross(v)
    # The chord of the three arcs has magnitude 4 R sin(m), L = 4 R m.
    lo,hi=0.,math.pi/2
    for _ in range(42):
        m=(lo+hi)/2
        if math.sin(m)/m>chord/main_length:lo=m
        else:hi=m
    radius=main_length/(4*m)
    skew=math.atan2(transverse,dx)
    a,b=m-skew,m+skew
    straight=0.
    if a<0:
        # Near full extension, there is insufficient excess for a reverse
        # bow. Two tangent arcs and one inclined straight give the same
        # station and length while preserving both connector tangents.
        lo,hi=skew,2*skew
        def arc_straight(theta):
            c,s=math.cos(theta),math.sin(theta)
            rad=(dx*s-transverse*c)/(2*(1-c))
            run=dx*c+transverse*s-2*rad*s
            return rad,run
        for _ in range(48):
            theta=(lo+hi)/2
            rad,run=arc_straight(theta)
            if 2*rad*theta+run < main_length: lo=theta
            else: hi=theta
        radius,straight=arc_straight(theta)
        assert radius>abs(offset*v.y) and straight>=-1e-7
        a,b=-theta,0.
    # First curve away from the destination then turn back toward the connector.
    # Offset at both end faces is (0,offset,0), matching the 2 mm pitch.
    heading=0.; origin=source
    edges=[];radii=[]
    turns=(theta,-theta) if straight>0 else (-a,a+b,-b)
    for number,turn in enumerate(turns):
        if abs(turn)<1e-9:continue
        sign=math.copysign(1,turn)
        rad=sign*radius
        def p(phi):
            return (origin + ux*(rad*(math.sin(phi)-math.sin(heading)))
                    +v*(rad*(-math.cos(phi)+math.cos(heading))))
        def offset_at(phi):
            return (-ux*math.sin(phi)+v*math.cos(phi))*(offset*v.y)+normal*(offset*normal.y)
        middle=heading+turn/2; end=heading+turn
        startpt=origin+offset_at(heading)
        midpt=p(middle)+offset_at(middle)
        endpt=p(end)+offset_at(end)
        edges.append(Part.Arc(startpt,midpt,endpt).toShape())
        radii.append(abs(rad-offset*v.y))
        origin=p(end)
        heading=end
        if straight>0 and number==0:
            shift=(ux*math.cos(heading)+v*math.sin(heading))*straight
            edges.append(Part.makeLine(endpt,endpt+shift))
            origin+=shift
    # A concentric 30° entry follows the connector axis. This keeps the
    # straight withdrawal corridor clear of the switch and neighboring LED.
    curve_r=ENTRY_R+offset
    def entry(phi):
        local_y=tangent_y-curve_r*(1-math.cos(phi))
        return V(tangent_x+curve_r*math.sin(phi),
                 23+(local_y-23)*math.cos(angle)-JACK_Z*math.sin(angle)+board_dy,
                 (local_y-23)*math.sin(angle)+JACK_Z*math.cos(angle))
    assert (edges[-1].Vertexes[-1].Point-entry(0)).Length<1e-6
    edges.append(Part.Arc(entry(0),entry(beta/2),entry(beta)).toShape())
    radii.append(curve_r)
    path=Part.Wire(edges)
    assert abs(path.Length-WIRE_LENGTH)<1e-6
    section=Part.Wire([Part.makeCircle(WIRE_RADIUS,edges[0].Vertexes[0].Point,ux)])
    tube=path.makePipeShell([section],True,False)
    assert tube.isValid() and len(tube.Solids)==1
    return tube,path,min(radii)

def shapes(angle=0.,board_dy=0.,withdraw=0.):
    header,plug=connectors()
    yaw=math.radians(YAW)
    plug.translate(V(-withdraw*math.cos(yaw),-withdraw*math.sin(yaw),0))
    result={'Header':move_board(header,angle,board_dy),'Plug':move_board(plug,angle,board_dy)}
    for pin,key in enumerate(SIGNALS,1):
        result[key]=wire_route(pin,angle,board_dy,withdraw)[0]
    return result

def apply(doc):
    """Replace both legacy reservation boxes in the assembled placement document."""
    group=next((o for o in doc.Objects if o.Label=='Battery pack wiring • J600'),None)
    if group is None:
        group=doc.addObject('App::DocumentObjectGroup','PackWiring')
        group.Label='Battery pack wiring • J600'
    for obj in list(doc.Objects):
        if obj.Label.startswith(('J600 pack connector','Pack harness exit reservation')):
            doc.removeObject(obj.Name)
    for key,shape in shapes().items():
        ob=doc.getObject('PackHarness'+key)
        if ob is None:ob=doc.addObject('Part::Feature','PackHarness'+key)
        ob.Label=LABELS[key];ob.Shape=shape
        if ob.ViewObject:
            ob.ViewObject.ShapeColor=COLORS[key]
        group.addObject(ob)
    doc.recompute()
    return group
