"""Expose the four OLED wires and their keyed endpoints in the native assembly.

Coordinates are millimetres in the existing assembly. CONN4 is R90 in
Adafruit's rev B Eagle file, with package pad 1 at local X=-1.5. The OLED
placement flips about Y, leaving that pad at assembly Y10.84721. Kaweei's
CBH-100-04-050-A drawing wires P1.1 to P2.1 through P1.4 to P2.4.
"""
from pathlib import Path

import FreeCAD as App
import Part

V = App.Vector
PINS = (
    ('GND', 'black', (.09, .10, .13)),
    ('OLED_VIN_SW', 'red', (.89, .10, .13)),
    ('UI_SDA', 'blue', (.13, .42, .93)),
    ('UI_SCL', 'yellow', (.98, .74, .10)),
)
Y_CENTER = 12.34721
SOCKET_LABEL = 'J1000 • XY-SM04B-SRSS-TB socket'
CABLE_LABEL = '50 mm STEMMA QT'
SIGNAL_METAL = (.76, .78, .80)
PLUG_COLOR = (.15, .16, .19)


def _find(doc, prefix):
    return next(obj for obj in doc.Objects if obj.Label.startswith(prefix))


def _group(doc, name, label, parent):
    group = doc.getObject(name) or doc.addObject('App::DocumentObjectGroup', name)
    group.Label = label
    parent.addObject(group)
    return group


def _feature(doc, name, label, shape, color, owner):
    feature = doc.getObject(name) or doc.addObject('Part::Feature', name)
    feature.Label = label
    feature.Shape = shape
    owner.addObject(feature)
    if feature.ViewObject:
        feature.ViewObject.ShapeColor = color
        feature.ViewObject.DisplayMode = 'Flat Lines'
        feature.ViewObject.LineWidth = 0.4
    return feature


def _prop(feature, field, value):
    if field not in feature.PropertiesList:
        feature.addProperty('App::PropertyString', field, 'Wiring')
    setattr(feature, field, value)


def _project_socket(step_file):
    shape = Part.read(str(step_file))
    assert len(shape.Solids) == 7, 'Expected project housing, four contacts and two anchors'
    shape.rotate(V(), V(0,0,1), 90)
    shape.translate(V(85.55, Y_CENTER, 0))
    return shape


def _place_copy(shape, placement):
    result = shape.copy()
    result.Placement = placement.multiply(result.Placement)
    return result


def _plug_parts(envelope, number):
    """Keep the reserved housing envelope, with visible wire entries and split crimps.

    The Kaweei drawing establishes four 1 mm centers, 28 AWG crimp leads,
    insulation diameter 0.8 mm and opposite keyed housings. Individual spring
    beams and the latch undercut have no dimensions on the harness drawing.
    The terminal sections are illustrative envelopes inside each reserved plug.
    """
    bb = envelope.BoundBox
    # Both wire endpoints leave their plug backs here before the service bends.
    back_x, inward, center_z = (bb.XMax,-1,1.65) if number==1 else (bb.XMin,1,2.55)
    axis = V(inward,0,0)
    bores = []
    crimps = []
    for i in range(4):
        cy=Y_CENTER+i-1.5
        def tube(radius, start, length):
            return Part.makeCylinder(radius,length,V(back_x+inward*start,cy,center_z),axis)
        # Break out the terminal mouth only on the back/flared entry face.
        bores.append(tube(.45,-.03,3.96))
        # A raised pair of wire crimp wings and a hollow contact-entry barrel.
        outer=tube(.405,.10,1.1).fuse(tube(.31,1.18,2.64))
        mouth=tube(.31,.09,1.06).fuse(tube(.145,1.11,2.73))
        terminal=outer.cut(mouth)
        # The openings face opposite sides, as shown in the two cable-end views.
        split_z=center_z+(0.24 if number==2 else -.64)
        xpos=min(back_x+inward*.09,back_x+inward*1.15)
        slit=Part.makeBox(1.06,.20,.40,V(xpos,cy-.10,split_z))
        # The stripped 28 AWG conductor runs from the drawn insulation end into
        # the crimp. Kaweei specifies seven 0.127 mm strands; the consolidated
        # radius below preserves their total copper cross-sectional area.
        core_radius = .127 * 7**.5 / 2
        core = tube(core_radius,0,1.31)
        crimps.append(terminal.cut(slit).fuse(core).removeSplitter())
    housing=envelope.cut(Part.makeCompound(bores))
    return housing,Part.makeCompound(crimps)


def _copper(x, y, length, width):
    shape = Part.makeBox(length, width, .035, V(x-length/2,y-width/2,0))
    # The front copper in the KiCad footprint has a 20% corner radius.
    vertical = [edge for edge in shape.Edges if edge.BoundBox.ZLength>.034]
    return shape.makeFillet(min(length,width)*.2, vertical)


def apply(doc, socket_step=None):
    """Split the existing cable compound. Preserve its route and the exploded offsets."""
    original = _find(doc, CABLE_LABEL)
    cable_pose = original.Placement
    cable = original.Shape.copy()
    cable.Placement = App.Placement()
    parts = cable.Solids
    assert len(parts) == 6, 'Expected two 4399 plug envelopes and four insulation solids'
    controls = next(obj for obj in original.InList if obj.TypeId=='App::DocumentObjectGroup')
    assembly = _group(doc, 'DisplayCableAssembly', 'Adafruit 4399 • OLED interconnect', controls)
    _prop(assembly, 'CableDrawing', 'Kaweei CBH-100-04-050-A, straight through, 28 AWG, 50 ±5 mm free wire')
    _prop(assembly, 'ContactGeometry', 'Cable housings and exposed crimp entry faces are placement envelopes.')
    for index,(net, color_name, rgb) in enumerate(PINS, 1):
        wire = _feature(doc, 'DisplayWire'+str(index), f'Pin {index} • {net} • {color_name}',
                        _place_copy(parts[index+1],cable_pose), rgb, assembly)
        _prop(wire,'Net',net)
        _prop(wire,'FromPin',f'J1000.{index} via P1.{index}')
        _prop(wire,'ToPin',f'Adafruit 4440 CONN4.{index} via P2.{index}')
        _prop(wire,'InsulationColor',color_name)
    for index,(part,name) in enumerate(zip(parts[:2],('main-board','OLED')),1):
        housing, contacts = _plug_parts(part,index)
        item = _feature(doc, 'DisplayCableP'+str(index), f'P{index} • {name} cable plug',
                        _place_copy(housing,cable_pose),PLUG_COLOR,assembly)
        _prop(item,'Manufacturer','Kaweei 4-position 1.0 mm SH-compatible housing, color black')
        _prop(item,'Representation','External clearance envelope with four wire-entry cavities; latch geometry approximate')
        terminals = _feature(doc,'DisplayCrimpsP'+str(index),f'P{index} • four crimp contact envelopes',
                             _place_copy(contacts,cable_pose),SIGNAL_METAL,assembly)
        _prop(terminals,'Representation','Illustrative tinned crimp and receptacle envelopes within Kaweei housing. Exact spring shape and mating depth are unspecified.')
    original.Visibility = False
    if original.ViewObject:
        original.ViewObject.Visibility = False
    # Existing project model retains the exact same nominal socket envelope.
    socket = _find(doc, 'J1000 •')
    # Capture pose before replacing the shape: exploded models move the socket
    # with the board, independently of the harness and OLED.
    if 'OriginalPose' not in socket.PropertiesList:
        socket.addProperty('App::PropertyPlacement','OriginalPose','Wiring')
        socket.OriginalPose = socket.Placement
    socket_pose = socket.OriginalPose
    if socket_step is None:
        socket_step = (Path(__file__).resolve().parent.parent/'electronics'/
                       'Keyboard_Controls.3dshapes'/'XY-SM04B-SRSS-TB.step')
    detailed = _project_socket(socket_step)
    socket.Shape = _place_copy(detailed,socket_pose)
    socket.Label = SOCKET_LABEL
    _prop(socket,'Representation','Project STEP housing, signal contacts and hold-down feet, drawing-based envelope')
    if socket.ViewObject:
        socket.ViewObject.DiffuseColor = [color for solid,color in zip(detailed.Solids,
            [(.81,.83,.83), *([SIGNAL_METAL]*6)]) for face in solid.Faces]
    pad_parts = []
    for i in range(4):
        pad_parts.append(_copper(83.55, Y_CENTER+i-1.5, 1.60, .60))
    for offset in (-2.80,2.80):
        pad_parts.append(_copper(87.55, Y_CENTER+offset, 2, 1.20))
    # Give the copper a top face and remove the volume already occupied by
    # the connector's solder tails. PCB surface datum is Z0.
    copper = Part.makeCompound(pad_parts).cut(detailed)
    pads = _feature(doc, 'DisplaySocketPads', 'J1000 • PCB lands 1–4 and grounded hold-downs',
                    _place_copy(copper,socket_pose),(.83,.58,.22),controls)
    _prop(pads,'Footprint','Keyboard_Controls:XY-SM04B-SRSS-TB (F.Cu)')
    doc.recompute()
    return assembly
