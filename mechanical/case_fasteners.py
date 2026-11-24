"""Seated case hardware in assembly coordinates. Threads are nominal envelopes."""
import math
import FreeCAD as App
import Part

V = App.Vector


def polygon(points):
    return Part.Face(Part.makePolygon(points + points[:1]))


# M2.5 DIN 934 steel hex nuts load horizontally before the keybed is fitted.
NUT_FLATS = 5.0
NUT_HEIGHT = 2.0
BOSS_RADIUS = 4.0
ROOF = 1.8
SLOT_HEIGHT = 2.35
SLOT_FLATS = 5.30
BORE_DEPTH = 8.0


def hex_prism(x, y, z, flats, height):
    radius = flats / math.sqrt(3)
    points = [V(x + radius*math.sin(i*math.pi/3),
                y + radius*math.cos(i*math.pi/3), z) for i in range(6)]
    return polygon(points).extrude(V(0,0,height))


def nut_boss(x, y, top, floor, entry_y):
    """Cut a horizontal nut seat and a vertical clearance hole in the PCB support."""
    boss = Part.makeCylinder(BOSS_RADIUS, top-floor, V(x,y,floor))
    bore = Part.makeCylinder(1.4, BORE_DEPTH+.01, V(x,y,top-BORE_DEPTH))
    bottom = top-ROOF-SLOT_HEIGHT
    seat = hex_prism(x,y,bottom,SLOT_FLATS,SLOT_HEIGHT)
    # A straight channel extends the two parallel hex flats to the inside of the tray.
    reach = BOSS_RADIUS+1
    start_y = y if entry_y>0 else y-reach
    entry = Part.makeBox(SLOT_FLATS,reach,SLOT_HEIGHT,V(x-SLOT_FLATS/2,start_y,bottom))
    return boss.cut(bore.fuse(seat).fuse(entry)).removeSplitter()


def seated_nut(x, y, top):
    lower = top-ROOF-NUT_HEIGHT
    nut = hex_prism(x,y,lower,NUT_FLATS,NUT_HEIGHT)
    # Match the simplified representation of the screw's major thread diameter.
    bore = Part.makeCylinder(1.25,NUT_HEIGHT+.02,V(x,y,lower-.01))
    return nut.cut(bore)


def button_screw(x, y, z, length):
    shaft = Part.makeCylinder(1.25, length, V(x,y,z-length))
    land = Part.makeCylinder(2.35, .35, V(x,y,z))
    radius = (2.35**2+1.15**2)/(2*1.15)
    dome = Part.makeSphere(radius,V(x,y,z+1.5-radius)).common(
        Part.makeBox(4.8,4.8,1.16,V(x-2.4,y-2.4,z+.35)))
    socket = [V(x+1.5/math.sqrt(3)*math.cos(i*math.pi/3),
                y+1.5/math.sqrt(3)*math.sin(i*math.pi/3),z+.64) for i in range(6)]
    return shaft.fuse(land).fuse(dome).cut(polygon(socket).extrude(V(0,0,1))).removeSplitter()


def seam_hardware():
    screws, nuts = [], []
    for y in (-12,-87):
        z = -9.4
        axis = V(1,0,0)
        shaft = Part.makeCylinder(1.5,12,V(146.8,y,z),axis)
        head = Part.makeCylinder(2.75,3,V(143.8,y,z),axis)
        def hex_face(x, flats):
            return polygon([V(x, y+flats/math.sqrt(3)*math.sin(i*math.pi/3),
                              z+flats/math.sqrt(3)*math.cos(i*math.pi/3)) for i in range(6)])
        screws.append(head.fuse(shaft).cut(hex_face(143.79,2.5).extrude(V(1.75,0,0))))
        nuts.append(hex_face(155.5,5.5).extrude(V(2.4,0,0)).cut(
            Part.makeCylinder(1.5,3,V(155.3,y,z),axis)))
    return Part.makeCompound(screws),Part.makeCompound(nuts)
