"""Architectural relief. All lengths and assembly coordinates are in mm.

The skyline reads from the typing edge. Wall relief is laid out in local
elevation coordinates, then folded onto the front and outer end surfaces.
"""
import math

import FreeCAD as App
import Part

V = App.Vector


def _profile(points, z, height, lean):
    vertices = [V(x, y, z) for x, y in points]
    polygon = Part.makePolygon(vertices + vertices[:1])
    return Part.Face(polygon).extrude(V(0, lean * height, height))


def _rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def _stroke(points, width):
    a, b = points
    length = math.dist(a, b)
    dx = (b[1] - a[1]) * width / (2 * length)
    dy = (a[0] - b[0]) * width / (2 * length)
    return [(a[0]+dx, a[1]+dy), (b[0]+dx, b[1]+dy),
            (b[0]-dx, b[1]-dy), (a[0]-dx, a[1]-dy)]


def _tower(x, floor, width, height, depth, crown, lean):
    """Stepped crowns, split setback spires and a second recessed facade."""
    # Most rooftops have two distinct setbacks and a narrower central lantern.
    outlines = {
        'spire': [(0,0),(1,0),(1,.65),(.78,.65),(.78,.84),(.59,.84),
                  (.59,1),(.43,1),(.43,.84),(.24,.84),(.24,.68),(0,.68)],
        'crown': [(0,0),(1,0),(1,.76),(.82,.76),(.82,.88),(.64,1),
                  (.36,1),(.12,.85),(0,.85)],
        'slant': [(0,0),(1,0),(1,.68),(.76,.68),(.76,.84),(.27,1),(0,1)],
        'fork': [(0,0),(1,0),(1,1),(.76,1),(.76,.85),(.33,.85),(.33,.95),(0,.95)],
        'step': [(0,0),(1,0),(1,.5),(.77,.5),(.77,.79),(.55,.79),(.55,1),(0,1)],
    }
    def at(u,v):
        return x+u*width, floor+v*height
    body = _profile([at(u,v) for u,v in outlines[crown]], -.025, depth+.025, lean)
    # Vertical channels cut the facade into pilasters. Broad alternating windows
    # remain distinct at the design nozzle width in single-colour material.
    channels = []
    spacing = 2.15 if width < 7 else 2.5
    j = 0
    offset = 1.05
    while offset + .82 < width - .45:
        y = floor + lean*depth + (2.0 if j%2 else 1.45)
        top = floor + lean*depth + height*.62
        while y+.95 < top:
            channels.append(Part.makeBox(.88, min(1.75,top-y), 1.1,
                                         V(x+offset,y,depth-.46)))
            y += 2.65
        j += 1
        offset += spacing
    if channels:
        body = body.cut(Part.makeCompound(channels))
    return body


def _building_group(shapes, x, road_length, blocks):
    """A plinth, stepped towers, and an elevated line with diamond-tipped cars."""
    slope = -1.12
    # Narrow faceted plinth reminiscent of a concrete canal embankment.
    base = [(x,4.7),(x+road_length-2,4.7),(x+road_length,6.1),
            (x+road_length,7.95),(x+2,7.95),(x,6.4)]
    shapes.append(_profile(base,-.03,1.10,slope))
    for dx,w,h,d,kind,y0 in blocks:
        shapes.append(_tower(x+dx,y0,w,h,d,kind,slope))
    # Broken viaduct pier sections project in front of the middle-distance facades.
    for edge in ((x+2.13,x+road_length-4.07) if road_length > 12 else ()):
        shapes.append(_profile([(edge,3.9),(edge+1.5,3.9),(edge+2.2,7.5),(edge+1,7.5)],
                               -.025,1.02,slope))


def _cover_art(side):
    slopes = -1.12
    shapes = []
    if side == 'left':
        _building_group(shapes,16,103,[
            (1,7,8.5,1.35,'step',7.1),(6.8,8.7,15,2.35,'fork',7.5),
            (13,5.9,12.3,1.6,'slant',7.5),(18.4,6.6,10.2,2.5,'crown',7.7),
            (24.4,8.4,17,3.65,'spire',7.4),(32.3,8,13.7,2.0,'fork',7.4),
            (39.1,7.7,10.8,2.7,'slant',7.3),(46,9.6,16.3,3.25,'crown',7.3),
            (55,6.3,9.1,2.0,'step',7.3),(60.2,8,11.8,2.75,'slant',7.4),
            (67.2,10.3,17.3,3.95,'spire',7.5),(77.4,6.4,10,1.55,'slant',7.3),
            (82.6,8.6,13.1,2.85,'fork',7.2),(90.2,6.7,9.3,1.9,'crown',7.1),
            (96.5,5.7,8.0,1.60,'step',7.0)])
        # Open double-faced portals and small satellite district beyond the OLED.
        _building_group(shapes,171.5,7.5,[(1,5.5,10,1.65,'crown',6.2)])
        _building_group(shapes,185,5.5,[(.25,4.5,10.7,1.38,'step',6.0)])
    else:
        _building_group(shapes,212,45.5,[
            (.5,6.4,10,1.65,'step',7.3),(5.5,8.2,15.2,2.9,'slant',7.45),
            (13.35,7.3,11.8,2.0,'fork',7.3),(19.8,9.2,16.8,3.75,'spire',7.30),
            (29,7.2,10.2,1.7,'crown',7.3),(35.3,6,13.4,2.1,'fork',7.4),
            (40.8,4.4,8.5,1.5,'step',7.4)])
        _building_group(shapes,297.4,11.3,[(.3,6.0,14.4,2.1,'slant',7.35),
                                                    (6.4,4.5,9,1.5,'step',7.2)])
    # Silhouette of the rising sun behind the spires. Open horizontal
    # bands have the same 45 degree rear facet as the tower silhouettes.
    if side == 'left':
        sun_x, sun_y, radius = 73.1, 19.9, 5.15
        disc = [(sun_x+radius*math.cos(i*math.pi/40),sun_y+radius*math.sin(i*math.pi/40))
                for i in range(80)]
        sun=_profile(disc,-.025,.91,slopes)
        for gap in (17.2, 19.0, 20.7):
            sun=sun.cut(Part.makeBox(12,.70,1.2,V(sun_x-6,gap,-.07)))
        shapes.append(sun)
        # Air traffic runs above the horizon between the stepped spires.
        for xx,yy,size in [(18.1,22.9,1.0),(110.5,23.1,.86)]:
            ship=[(0,0),(3,.10),(4.35,1.04),(7.5,1.04),(6.2,.25),
                  (11.5,.25),(9.7,-.73),(2.1,-.73)]
            shapes.append(_profile([(xx+u*size,yy+v*size) for u,v in ship],
                                   -.025,.98,slopes))
    # The cantilevered railway breaks into spans with chamfered station ends.
    spans = [(18,38),(62,48)] if side=='left' else [(213.5,38)]
    for xx,length in spans:
        shapes.append(_profile([(xx,6.0),(xx+length-2,6.0),(xx+length,7.15),
                                (xx+length-1.2,8.05),(xx+2.1,8.05),(xx,7.0)],
                               -.025,2.52,slopes))
    return shapes


def _buttress(x,y):
    # A permanent wedge from the rear of each sleeve allows it to grow out
    # along the upright cover. Leave a 0.4 mm gap to the bare PCB everywhere.
    thickness=6.35
    pts=[V(x-thickness/2,yy,zz) for yy,zz in
         [(y+.1,.4),(y+2.75,.4),(y+9.05,6.07),(y+.1,6.07)]]
    return Part.Face(Part.makePolygon(pts+pts[:1])).extrude(V(thickness,0,0))


def build_cover(shape, side):
    centers = [(8,13),(126,5),(181,13)] if side == 'left' else [(205,13),(264,13)]
    buttresses = []
    for x,y in (centers if side == 'right' else []):
        hole = Part.makeCylinder(1.4,9,V(x,y,-.1))
        buttresses.append(_buttress(x,y).cut(hole))
    forms = _cover_art(side)
    if side == 'left':
        # This interchangeable face lies flat on the common carrier split.
        # Reorient facets for an art-up print with a 0.68:1 side projection.
        shear = App.Matrix()
        shear.A23 = .44
        forms = [form.transformGeometry(shear) for form in forms]
    for form in forms:
        form.translate(V(0,0,8.4))
    out = shape.multiFuse(forms+buttresses).removeSplitter()
    assert out.isValid() and len(out.Solids)==1, ('cover',side)
    return out


def _wall_street(run):
    """Segment of elevated double-track through five groups of buildings."""
    shapes = []
    y0 = 4.0
    # Faceted continuous retaining wall with sloped approach and exit.
    bed = [(0,4.8),(run-2,4.8),(run,6.15),(run-1.4,7.35),
           (2.2,7.35),(0,6.15)]
    shapes.append(_profile(bed,-.03,.85,1.10))
    heights = [8.2,13,9.6,15.6,11.5,8.8,12.6,16.2,9.4,13.9,10.4,
               8.8,15.1,12.9,9.9,14.2,10.7,13.1,9.5,15.5,10.8]
    pitch = run/len(heights)
    types = ('slant','fork','step','spire','crown')
    for n,h in enumerate(heights):
        w=pitch*(.83 if n%4 else .70)
        x=n*pitch+.4
        shapes.append(_tower(x,y0,w,h,.75+.16*(n%3),types[n%5],1.1))
    # A monorail girder breaks across the foreground into two angular tracks.
    for x0,x1,dy in [(2,.48*run,.0),(.53*run,run-2,1.3)]:
        pts=[(x0,7.35+dy),(x1-3,7.35+dy),(x1,8.6+dy),
             (x1-2.4,9.25+dy),(x0+2,9.25+dy),(x0,8.2+dy)]
        shapes.append(_profile(pts,-.025,1.55,1.1))
    return shapes


def build_tray(shape, side):
    # Positive local height points out of the wall. Keep the rear wall clear
    # around the port, selector, and radio reservation.
    front_x = -1.8 if side=='left' else 155.4
    front_run = 150.4 if side=='left' else 150.7
    art = []
    for solid in _wall_street(front_run):
        solid.rotate(V(),V(1,0,0),90)
        solid.translate(V(front_x,-105,-17))
        art.append(solid)
    for solid in _wall_street(115):
        solid.rotate(V(),V(1,0,0),90)
        if side=='left':
            solid.rotate(V(),V(0,0,1),-90)
            solid.translate(V(-7.5,19.1,-17))
        else:
            solid.rotate(V(),V(0,0,1),90)
            solid.translate(V(312.3,-98,-17))
        art.append(solid)
    out = shape.multiFuse(art).removeSplitter()
    assert out.isValid() and len(out.Solids)==1, ('tray',side)
    return out

def left_art_face(full_cover):
    """Separate the city surface from the shared Z=7.55 left OLED carrier."""
    limit=Part.makeBox(201,27,12,V(-8,-.1,7.55))
    face=full_cover.common(limit).removeSplitter()
    assert face.isValid() and len(face.Solids)==1
    return face
