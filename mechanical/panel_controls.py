"""Rear control assembly in the keyboard coordinate system, millimetres.

The PCB top is Z=0. X increases to the right and Y toward the cable exits.
Vendor reference surfaces for the OLED are from Adafruit's 4440 STEP.
"""
from pathlib import Path
import math
import FreeCAD as App
import Part

V = App.Vector
wheel_x, wheel_y = 282.5, 13.0
pixel_x, pixel_y = 152.4, 13.0
lid_seam = 192.0
rear_mounts = [(8,13), (126,5), (181,13), (205,13), (264,13)]
# Convert the vendor model to display face up and QT port opening to the left.
display_dx = pixel_x + 18.96507
display_dy = pixel_y - 11.57479
display_face = 5.65
display_mounts = [(display_dx-x, display_dy+y)
                  for x in (2.54,30.48) for y in (2.413,18.923)]


def box(x,y,z,w,d,h):
    return Part.makeBox(w,d,h,V(x,y,z))


def disk(x,y,z,r,h):
    return Part.makeCylinder(r,h,V(x,y,z))


def rect_wire(x,y,z,w,d):
    points = [V(x+w*a/2,y+d*b/2,z) for a,b in
              ((-1,-1),(1,-1),(1,1),(-1,1),(-1,-1))]
    return Part.makePolygon(points)


def hex_prism(center, flat, length, axis):
    r = flat/math.sqrt(3)
    points = []
    for n in range(6):
        c,s = r*math.cos(n*math.pi/3),r*math.sin(n*math.pi/3)
        offset = V(0,c,s) if axis.x else V(c,s,0)
        points.append(center+offset)
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(axis*length)


def pcb_tools():
    # ALPS mounting drawing is viewed from the component side, row toward keys.
    slots = [box(wheel_x+side*4.4-.9,wheel_y-1.05,-2,1.8,2.1,3)
             for side in (-1,1)]
    return slots + [disk(wheel_x+x,wheel_y-7,-2,.50,3) for x in (-2.5,0,2.5)]


def make_dial():
    x,y = wheel_x,wheel_y
    # The broad outer face is the print bed. A 45-degree rim starts on a flat land.
    knob = disk(x,y,9.0,11,7.0).fuse(Part.makeCone(11,10.4,.6,V(x,y,16.0)))
    # Lower neck lips retain an optional standard 11 ID × 1.5 mm elastomer ring.
    knob = knob.fuse(disk(x,y,6.28,6.45,.13))
    knob = knob.fuse(Part.makeCone(6.45,5.60,.86,V(x,y,6.40)))
    knob = knob.fuse(disk(x,y,7.25,5.60,1.37))
    knob = knob.fuse(disk(x,y,8.61,6.65,.45))
    for n in range(28):
        angle=2*math.pi*n/28
        knob=knob.cut(disk(x+11.50*math.cos(angle),y+11.50*math.sin(angle),9.0,.72,7.6))
    full_bore=disk(x,y,6.1,3.32,3.43)
    upper_bore=disk(x,y,9.52,3.11,5.78).common(box(x-4,y-4,9.5,5.64,8,6))
    knob=knob.cut(full_bore.fuse(upper_bore))
    # Horizontal M3 set screw presses on the shaft flat. Its nut installs from below.
    screw_z=12.3
    nut_clear=hex_prism(V(x+6.95,y,screw_z),5.75,2.65,V(1,0,0))
    feed=box(x+6.95,y-5.75/math.sqrt(3),8.95,2.65,2*5.75/math.sqrt(3),screw_z-8.95)
    radial_bore=Part.makeCylinder(1.64,11,V(x+1.4,y,screw_z),V(1,0,0))
    # The pointed roof follows the face-down build direction and clears the screw.
    a=1.64/math.sqrt(2)
    p=[V(x+1.4,y-a,screw_z-a),V(x+1.4,y,screw_z-2*a),V(x+1.4,y+a,screw_z-a)]
    roof=Part.Face(Part.makePolygon(p+p[:1])).extrude(V(11,0,0))
    knob=knob.cut(nut_clear.fuse(feed).fuse(radial_bore).fuse(roof))
    # An index line references the flat. Index orientation is set at assembly.
    knob=knob.cut(box(x-.40,y+6.0,16.21,.8,3.20,.70)).removeSplitter()
    screw=Part.makeCylinder(1.50,8,V(x+1.5,y,screw_z),V(1,0,0))
    nut=hex_prism(V(x+7.04,y,screw_z),5.5,2.4,V(1,0,0)).cut(radial_bore)
    # Nominal installed envelope. Actual ring compression deforms its section.
    ring=Part.makeTorus(6.345,.745,V(x,y,7.71))
    # Load the nut before fitting the optional ring. The ring clears the seated nut.
    for dz in range(0,10):
        inserted=nut.copy()
        inserted.translate(V(0,0,-dz))
        assert inserted.common(knob).Volume<1e-5
    assert ring.common(knob).Volume<1e-5 and ring.common(nut).Volume<1e-5
    body=box(x-4.9,y-7.7,0,9.8,13.2,5.65)
    pins=[disk(x+i,y-7,-3.2,.29,3.2) for i in (-2.5,0,2.5)]
    pins.extend(box(x+i*4.4-.30,y-.70,-3.8,.60,1.40,3.8) for i in (-1,1))
    shaft=disk(x,y,5.65,3,9.35).cut(box(x+1.5,y-4,9,3,8,7))
    return knob,Part.makeCompound([screw,nut]),ring,Part.makeCompound([body,shaft,*pins])


def prepare_lid(lid,left_side):
    if not left_side:
        return lid.cut(disk(wheel_x,wheel_y,5.5,7.0,4)).removeSplitter()
    # Glass is recessed into the inner face. Bevel widens the viewing cone.
    cx=display_dx-17.25707
    cy=display_dy+10.71679
    lid=lid.cut(box(cx-15.55,cy-6.3,5.9,31.1,12.60,1.18))
    opening=Part.makeLoft([rect_wire(pixel_x,pixel_y,6.95,24,7.25),
                          rect_wire(pixel_x,pixel_y,8.50,27.2,10.45)],True,True)
    lid=lid.cut(opening)
    # Flex turns around the edge of the glass. Leave its full path unobstructed.
    lid=lid.cut(box(display_dx-4.9, display_dy+4.7,5.85,6.65,10.2,1.22))
    for x,y in display_mounts:
        lid=lid.fuse(disk(x,y,display_face,2.05,.36))
        lid=lid.cut(disk(x,y,5.45,1.12,3.2))
        lid=lid.cut(Part.makeCone(1.12,2.05,.93,V(x,y,7.47)))
    return lid.removeSplitter()


def make_display(step_path):
    shape=Part.read(str(step_path))
    # Vendor solid 0 is the PCB, 22–28 are panel and wrapped flex (pinned revision).
    solids=shape.Solids
    assert len(solids)==31 and abs(solids[0].BoundBox.XLength-33.02)<.001
    shape.rotate(V(),V(0,1,0),180)
    shape.translate(V(display_dx,display_dy,display_face))
    solids=shape.Solids
    panel=Part.makeCompound(solids[22:29])
    back=Part.makeCompound(solids[1:22]+solids[29:])
    fix=[]
    for x,y in display_mounts:
        screw=disk(x,y,2.4,1,5.1).fuse(Part.makeCone(1,1.95,.95,V(x,y,7.45)))
        nut=hex_prism(V(x,y,2.48),4,1.60,V(0,0,1)).cut(disk(x,y,2.45,1.02,2))
        fix.extend((screw,nut))
    return solids[0],panel,back,Part.makeCompound(fix)


def make_harness(wire_length=50):
    # Fitted connector bodies, mated plug envelopes and four insulated wires.
    yc=display_dy+10.922
    main=box(83.39,yc-3.10,0,5.01,6.20,2.90)
    p1=box(88.4,yc-2.7,.55,4.0,5.4,2.15)
    p2=box(134.4,yc-2.7,1.47,4.0,5.4,2.15)
    from oled_route import sweeps
    wires, bounds, edges = sweeps(yc, wire_length)
    bounds.extend((p1.BoundBox, p2.BoundBox))
    return main, Part.makeCompound([p1, p2, *wires]), edges[0].Length, bounds



def sample_pixels():
    # Illustrative SSD1306 contents using a doubled 5×7 cell.
    glyphs={'1':['00100','01100','00100','00100','00100','00100','01110'],
            '4':['00010','00110','01010','10010','11111','00010','00010'],
            'F':['11111','10000','10000','11110','10000','10000','10000'],
            'P':['11110','10001','10001','11110','10000','10000','10000'],
            'S':['01111','10000','10000','01110','00001','00001','11110']}
    lit=[]
    for index,char in enumerate('144 FPS'):
        if char==' ': continue
        for row,line in enumerate(glyphs[char]):
            for col,v in enumerate(line):
                if v=='1':
                    lit.append(box(pixel_x-7+index*2.1+.35*col,pixel_y+.84-.35*row,
                                   display_face+.897,.32,.32,.015))
    return Part.makeCompound(lit)
