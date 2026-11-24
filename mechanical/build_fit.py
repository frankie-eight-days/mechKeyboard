"""Build the fit-study documents with FreeCAD 1.1 and an offscreen Qt GUI.

Run in FreeCAD's bundled Python with its lib directory on PYTHONPATH.
Set KICAD10_3DMODEL_DIR if the standard LED STEP library is outside the default macOS bundle.
"""
from pathlib import Path
import csv
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
import MeshPart
import panel_controls as panel
import haptic_mount
import panel_art
import tray_joint
import case_fasteners
import display_harness
import pack_harness

out = Path(__file__).resolve().parent
models = Path(os.environ.get('KICAD10_3DMODEL_DIR', '/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels'))
Gui.showMainWindow()
V = App.Vector
pitch = 19.05
travel = 4.0
pcb_t = 1.60
led_offset = 5.08
floor = -17.0
floor_top = -14.4
seam = 152.4
rows = [
    'Esc 1 2 3 4 5 6 7 8 9 0 − = Backspace:2 Delete',
    'Tab:1.5 Q W E R T Y U I O P [ ] \\:1.5 Home',
    'Caps:1.75 A S D F G H J K L ; Quote Enter:2.25 PgUp',
    'Shift:2.25 Z X C V B N M , . / Shift:1.75 ↑ PgDn',
    'Ctrl:1.25 GUI:1.25 Alt:1.25 Space:6.25 Alt:1.25 Fn:1.25 Gap:0.5 ← ↓ →',
]
keys = []
for row, line in enumerate(rows):
    x_u = 0
    for token in line.split():
        legend, _, width = token.partition(':')
        width = float(width or '1')
        if legend != 'Gap':
            keys.append((len(keys) + 1, legend, width, (x_u + width / 2) * pitch, -(row + .5) * pitch))
        x_u += width
    assert x_u == 16
assert len(keys) == 67


def box(x, y, z, w, d, h):
    return Part.makeBox(w, d, h, V(x, y, z))


def center_box(w, d, z, h, x=0, y=0):
    return box(x - w / 2, y - d / 2, z, w, d, h)


def cyl(r, z, h, x=0, y=0):
    return Part.makeCylinder(r, h, V(x, y, z))


def move(shape, x=0, y=0, z=0):
    s = shape.copy()
    s.translate(V(x, y, z))
    return s


def rounded(w, d, r, z, h):
    shape = center_box(w, d, z, h)
    vertical = [e for e in shape.Edges if e.BoundBox.ZLength > h - .0001]
    return shape.makeFillet(r, vertical)


def rectangle(w, d, z):
    pts = [V(x*w/2, y*d/2, z) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]]
    return Part.makePolygon(pts)


def loft(w0, d0, z0, w1, d1, z1):
    return Part.makeLoft([rectangle(w0,d0,z0), rectangle(w1,d1,z1)], True, True)


def join(shapes):
    return Part.makeCompound(shapes)


def feature(doc, name, shape, color, transparency=0, group=None):
    obj = doc.addObject('Part::Feature', 'Body')
    obj.Label, obj.Shape = name, shape
    obj.ViewObject.ShapeColor = tuple(int(color[i:i+2],16)/255.0 for i in (0,2,4))
    obj.ViewObject.Transparency = transparency
    obj.ViewObject.DisplayMode = 'Flat Lines'
    obj.ViewObject.LineWidth = 0.4
    if group: group.addObject(obj)
    return obj


def in_group(doc, title):
    g = doc.addObject('App::DocumentObjectGroup', 'Group')
    g.Label = title
    return g


def save(doc, filename):
    doc.recompute()
    av = Gui.activeDocument().activeView()
    section = filename.startswith('key-section')
    rotation = App.Rotation(V(0,0,1), 65 if section else 0).multiply(App.Rotation(V(1,0,0),65 if section else 37))
    target = V(0,0,8) if section else V(152,-40,0)
    distance = 100 if section else 650
    eye = target + rotation.multVec(V(0,0,distance))
    axis,angle = rotation.Axis, rotation.Angle
    camera = (f'#Inventor V2.1 ascii\nOrthographicCamera {{ position {eye.x} {eye.y} {eye.z} '
              f'orientation {axis.x} {axis.y} {axis.z} {angle} '
              f'nearDistance 1 farDistance {distance*3} focalDistance {distance} height {34 if section else 220} }}')
    av.setCamera(camera)
    doc.saveAs(str(out/filename))


def cap(width):
    # Generic top-legend purchasing envelope. The rim and a roof surround the switch.
    skirt = width*pitch-1.05
    outer = loft(skirt,18,10.6,skirt-3.5,14.5,19.9)
    cavity = loft(skirt-1.9,16.1,10.59,skirt-4.85,13.15,18.65)
    socket = cyl(2.8,12.05,6.65)
    cross = center_box(4.14,1.32,12,3.45).fuse(center_box(1.32,4.14,12,3.45))
    return outer.cut(cavity).fuse(socket.cut(cross))


# Coordinates are +X right, +Y towards the rear, Z=0 on the top of the FR-4.
# In KiCad top view y grows towards the spacebar. Rotate the stock switch 180 degrees.
hole_coords = [(0,0,2.0),(-5.08,0,.85),(5.08,0,.85),(-2.54,-5.08,.75),(3.81,-2.54,.75)]
hole_tools = [cyl(r,-2.2,3.2,x,y) for x,y,r in hole_coords]
aperture = move(rounded(4.2,3.8,.5,-2.2,3.2),y=led_offset)
base_switch = center_box(13.85,13.85,0,5).fuse(center_box(15.6,15.6,5,1))
base_switch = base_switch.fuse(loft(15.6,15.6,6,11.6,11.6,11.35))
stem_well = center_box(6.6,6.6,6.2,9)
lens = center_box(3.6,3.1,0,12,0,led_offset)
housing = base_switch.cut(stem_well).cut(lens)
stem = center_box(5.8,5.8,10.25,1.8).fuse(center_box(4.0,1.2,12,3.2))
stem = stem.fuse(center_box(1.2,4,12,3.2))
pins = join([cyl(.43,-3.6,3.6,x,y) for x,y,r in hole_coords[-2:]])
pegs = join([cyl(r-.12,-2.9,2.9,x,y) for x,y,r in hole_coords[:3]])
switch_fixed = join([housing, pins, pegs])

led_step = models/'LED_SMD.3dshapes/LED_SK6812MINI-E_3.2x2.8mm_P1.5mm_ReverseMount.step'
led = Part.read(str(led_step))
led.rotate(V(), V(1,0,0), 180)
led.translate(V(0,led_offset,-pcb_t))
local_board = center_box(pitch,pitch,-pcb_t,pcb_t).cut(join([aperture,*hole_tools]))
local_plate = center_box(pitch,pitch,3.5,1.5).cut(center_box(14.05,14.05,3,3))
cap_one = cap(1)
insert = cap_one.common(center_box(4.0,2.1,17,3.5,0,led_offset))
cap_one = cap_one.cut(insert)
down = move(cap_one,z=-travel)
assert min(housing.distToShape(down)[0],local_plate.distToShape(down)[0]) > .01
assert led.common(local_board).Volume < .0001
assert led.common(housing).Volume < .0001
print('Pressed cap / housing, plate clearances',down.distToShape(housing)[0],down.distToShape(local_plate)[0],flush=True)
print('LED / switch housing clearance',led.distToShape(housing)[0],flush=True)

slice_doc = App.newDocument('KeySection')
slice_doc.Label = 'One key • light path and travel'
# Keep half at x>=0 so the section passes through the LED and key stem.
half = box(0,-13,-4,14,26,27)
cutparts = [('Keycap • generic outer and inner shape',cap_one,'d6dbd5'),
            ('Translucent legend area • target envelope',insert,'cbe58b'),
            ('Stem • released',stem,'bb403f'),
            ('Transparent switch • optical recess envelope',housing,'72acac'),
            ('Plate • 1.50 mm',local_plate,'808998'),
            ('PCB • 1.60 mm',local_board,'316c5c'),
            ('Reverse-mounted LED • KiCad STEP',led,'f2c84f'),
            ('Switch contacts and locating pins',join([pins,pegs]),'bd8461')]
for title,shape,color in cutparts:
    feature(slice_doc,title,shape.common(half),color)
down_group=in_group(slice_doc,'Bottom of travel • toggle after hiding released cap and stem')
for name,shape,color in [('Cap at 4 mm travel',down,'db9f58'),('Stem at 4 mm travel',move(stem,z=-travel),'bb403f')]:
    feature(slice_doc,name,shape.common(half),color,group=down_group).Visibility=False
down_group.Visibility=False
save(slice_doc, 'key-section.FCStd')

doc = App.newDocument('KeyboardPlacement')
doc.Label = '65% keyboard • fit study'
pcb_cuts,plate_cuts,stab_shapes=[],[],[]
switch_shapes,pixel_shapes,cap_shapes=[],[],[]
cap_cache={}
def stab_distance(width):
    return 50.0 if width==6.25 else 11.9

for n,legend,w,x,y in keys:
    pcb_cuts.extend(move(h,x,y) for h in [*hole_tools,aperture])
    plate_cuts.append(center_box(14.05,14.05,3,3,x,y))
    switch_shapes.append(move(join([switch_fixed,stem]),x,y))
    pixel_shapes.append(move(led,x,y))
    if w not in cap_cache: cap_cache[w]=cap(w)
    cap_shapes.append(move(cap_cache[w],x,y))
    if w<2: continue
    span = stab_distance(w)
    for side in (-1,1):
        sx=x+side*span
        pcb_cuts.extend([cyl(1.525,-2.2,3.2,sx,y-7), cyl(2,-2.2,3.2,sx,y+8.24)])
        # Reserve PCB-stabilizer housing and protruding fastener.
        plate_cuts.append(center_box(7.1,16,2.8,3.2,sx,y+.65))
        stab_shapes.extend([center_box(6.3,14.6,0,7,sx,y+.65),cyl(2.4,-3.5,1.9,sx,y-7)])
    # North-side wire sweep, separated from both switch and LED lands.
    wire=Part.makeCylinder(.8,2*span,V(x-span,y+8.35,1.5),V(1,0,0))
    stab_shapes.append(wire)
    # The wire top is at Z=2.30; the plate underside is at Z=3.50.
mounts = [(x,-98.9) for x in (8,139,166,269)] + panel.rear_mounts
pcb_cuts.extend(panel.pcb_tools())
pcb_cuts.extend(cyl(1.375,-2.2,3.2,x,y) for x,y in mounts)
outline = move(rounded(312.8,123,2.0,-pcb_t,pcb_t),x=152.4,y=-40.5)
selector_tab = box(62,20,-pcb_t,13,3.05,pcb_t)
pcb = outline.fuse(selector_tab).removeSplitter().cut(join(pcb_cuts))
plate_cuts.append(box(303.9,-10,3,5,15,3))
plate=box(-1.4,-96.25,3.5,307.6,97.65,1.5).cut(join(plate_cuts))
hardware = in_group(doc,'Switch stack')
feature(doc,'PCB • keybed holes and no-copper antenna strip',pcb,'397968',group=hardware)
feature(doc,'Plate • steel envelope, stabilizer reliefs and antenna notch',plate,'91a0aa',group=hardware)
feature(doc,'67 switch, stem and pin envelopes',join(switch_shapes),'aebfbb',group=hardware)
feature(doc,'67 reverse-mounted LED models',join(pixel_shapes),'e8bf50',group=hardware)
feature(doc,'Four stabilizer wire and housing reservations',join(stab_shapes),'757779',group=hardware)
feature(doc,'67 keycap envelopes • hide to view the switch stack',join(cap_shapes),'d9dcd7',group=hardware)

# The tray is cut from one dimensioned shell, then split to preserve the continuous wall profile.
outer = move(rounded(319.8,131,4,floor,23),x=152.4,y=-39.5)
inner = move(rounded(314.6,125.8,2.2,floor_top,24),x=152.4,y=-39.5)
shell = outer.cut(inner)
# Rear USB + selector openings extend through the full wall thickness.
shell = shell.cut(box(34.5,21.0,-2.1,15,6.5,8.2))
shell = shell.cut(box(64.0,21.0,-.4,9,6.5,3.2))
bosses = [case_fasteners.nut_boss(x,y,-pcb_t,floor_top,1 if y<0 else -1) for x,y in mounts]
shell=shell.fuse(join(bosses))
# Pack guide walls reserve 1.5 mm around the pack. East remains open for its harness.
bay_x, bay_y = pack_harness.BAY_X, pack_harness.BAY_Y
pack_box = box(bay_x,bay_y,-13.6,68,35,7.5)
pack_limit = box(bay_x-1.5,bay_y-1.5,-13.6,71,38,8.75)
guides = [box(bay_x-3.5,bay_y-3.5,floor_top,2,42,2.8),
          box(bay_x-1.5,bay_y-3.5,floor_top,70,2,2.8),
          box(bay_x-1.5,bay_y+36.5,floor_top,70,2,2.8)]
shell=shell.fuse(join(guides))
# Both strap slots and the connecting recess follow the pouch centerline.
for yc in (bay_y-5.5,bay_y+39):
    shell=shell.cut(center_box(10,2.5,floor-.2,3.3,bay_x+34,yc))
shell=shell.cut(center_box(10,47,floor-.2,1.0,bay_x+34,bay_y+16.75))
left=shell.common(box(-15,-115,floor-1,seam+15-.10,160,27))
right=shell.common(box(seam+.10,-115,floor-1,175,160,27))
left, right, seam_lugs = tray_joint.add_joint(left, right, seam, floor, floor_top)
case_group=in_group(doc,'Printable tray • joined below a one-piece PCB')
for name,shape in [('Left tray section',left),('Right tray section',right)]:
    assert shape.isValid() and all(max(sol.BoundBox.XLength,sol.BoundBox.YLength) <220 for sol in shape.Solids)
    feature(doc,name,shape,'475966',group=case_group)
assert len(left.Solids)==1 and len(right.Solids)==1
lids=[]
for x0,x1,label in [(-7.3,panel.lid_seam-.1,'Left'),(panel.lid_seam+.1,312.1,'Right')]:
    lid=move(rounded(x1-x0,25.1,2.0,6,2.4),x=(x0+x1)/2,y=13.35)
    for xc,yc in panel.rear_mounts:
        if x0 < xc < x1:
            lid=lid.fuse(cyl(3.3,0,6.01,xc,yc))
            lid=lid.cut(cyl(1.4,-.1,9,xc,yc))
    lid=panel.prepare_lid(lid,label=='Left')
    lids.append(lid)
    feature(doc,label+' rear cover and mounting sleeves',lid,'526873',group=case_group)
knob,knob_fasteners,drag_ring,pot = panel.make_dial()
mesh_dir = out/'tray-fit-meshes'
mesh_dir.mkdir(exist_ok=True)
for name,shape in [('tray-left',left),('tray-right',right),('rear-cover-left',lids[0]),('rear-cover-right',lids[1]),('volume-knob',knob)]:
    assert shape.isValid() and len(shape.Solids)==1, name
    if name.startswith('rear-cover') or name=='volume-knob':
        shape = shape.copy()
        shape.rotate(V(),V(1,0,0),180)
    # Rebase each part onto the print plane so the STL opens in its intended orientation.
    bounds = shape.BoundBox
    solid = move(shape,-bounds.XMin,-bounds.YMin,-bounds.ZMin)
    mesh=MeshPart.meshFromShape(Shape=solid,LinearDeflection=.06,AngularDeflection=.20)
    assert mesh.isSolid(), name
    mesh.translate(0, 0, -mesh.BoundBox.ZMin)
    mesh.write(str(mesh_dir/(name+'.stl')))

panel_art.export_variants(lids, out/'rear-cover-options')

control_group=in_group(doc,'Top controls • volume and status display')
display_board,glass,back,display_screws=panel.make_display(out/'vendor'/'Adafruit-4440.step')
main_qt,qt_harness,wire_len,cable_bounds=panel.make_harness()
for name,shape,color in [('Volume dial • D socket and optional radial seal groove',knob,'455460'),
                         ('Dial captive M3 nut and flat-point set screw',knob_fasteners,'a7acb1'),
                         ('ALPS RK09K1130A6S envelope, D shaft and leads',pot,'515a57'),
                         ('Adafruit 4440 • vendor PCB',display_board,'284c61'),
                         ('OLED panel and wrapped flex',glass,'14242b'),
                         ('OLED rear components and QT socket',back,'838b87'),
                         ('Display retention • M2×6 countersunk screws and M2 nuts',display_screws,'8b949b'),
                         ('J1000 • XY-SM04B-SRSS-TB socket envelope',main_qt,'bdb8a5'),
                         ('50 mm STEMMA QT • mated plugs and harness route',qt_harness,'705e55'),
                         ('Screen preview • simulated 144 FPS',panel.sample_pixels(),'a2e1f0')]:
    feature(doc,name,shape,color,group=control_group)
feature(doc,'Optional radial 11 × 1.5 mm drag ring • free-section envelope',drag_ring,'3e3630',group=control_group).Visibility=False
parts=in_group(doc,'Components, pack and service volumes')
usb=box(37.53,15.7,0,8.94,7.30,3.30)
slider=box(65.15,20.15,0,6.7,2.8,1.5)
slider_tip=box(66.8,22.95,.45,3.4,1.45,.9)
radio=box(293.8,10.75,0,15,10.2,2.0)
antenna=box(304.4,-9.15,-pcb_t,4.4,50,5.6)
bulk=join([box(x,4.0,0,7.3,4.3,3.8) for x in (108,235)])
usb_bank=join([box(x,3.0,0,7.3,4.3,3.1) for x in (79,88,97)])
for name,shape,color in [('J200 USB-C shell envelope',usb,'b5bdc2'),('SW400 selector body + actuator sweep',join([slider,slider_tip]),'797d80'),('U100 BMD-340 radio envelope',radio,'b0bfc2'),('C204/C206/C208 • protected input bank',usb_bank,'af7e51'),('C904/C905 • 7.3 × 4.3 × 3.8 mm each',bulk,'bd8c59'),('CU-J450-V3 cell pack',pack_box,'93b4ba')]:
    feature(doc,name,shape,color,group=parts)
keep=in_group(doc,'Service and clearance volumes')
feature(doc,'Antenna keepout • copper and metal',antenna,'cfa35b',65,keep)
feature(doc,'Pack clearance • 1.25 mm thickness reserve',pack_limit,'da9e57',80,keep)
keep.Visibility=False
assert antenna.common(plate).Volume<.0001
assert plate.common(join(stab_shapes)).Volume < .0001
pack_group = pack_harness.apply(doc)
assert doc.PackHarnessHeader.Shape.common(pack_limit).Volume < .0001
assert left.common(right).Volume<.0001
assert pcb.common(join([left,right])).Volume<.0001
for shape in (usb,slider,slider_tip,radio,bulk):
    assert shape.common(join(lids)).Volume < .0001
for shape in (usb,slider,slider_tip,radio,bulk,pack_box):
    assert (shape.common(left).Volume+shape.common(right).Volume)<.0001
# Include moving travel and swept diameter in the ECAD–MCAD interface review.
dial_sweep=cyl(11,9,7.6,panel.wheel_x,panel.wheel_y)
lid_pair=join(lids)
for name,shape in [('dial',knob),('dial hardware',knob_fasteners),('pot',pot),('glass',glass),
                   ('display board',display_board),('display underside',back),('main QT',main_qt),
                   ('USB bank',usb_bank)]:
    for target,obstacle in [('cover',lid_pair),('tray',join([left,right])),('PCB',pcb),('RF keepout',antenna)]:
        interference=shape.common(obstacle).Volume
        assert interference<1e-4,(name,target,interference)
for state,g in [('released',join(cap_shapes)),('bottom',move(join(cap_shapes),z=-4))]:
    assert dial_sweep.distToShape(g)[0]>2.0,state
assert knob.common(pot).Volume < .0001
assert knob.common(knob_fasteners).Volume < .0001
assert display_screws.common(pcb).Volume < .0001
for fixed in [display_board,glass,back,*lids]:
    assert display_screws.common(fixed).Volume < .0001
# The routed cable is above the main board, below the cover and inside the
# rectangular part of the tray cavity. Check each wire envelope against each
# support, component body, fastener and spike in this channel, including seam lugs.
cable_obstacles=[s.BoundBox for shape in [usb_bank,bulk,display_screws,radio,
                                           antenna,usb,slider,slider_tip,join(seam_lugs)]
                           for s in shape.Solids]
cable_obstacles.extend(cyl(3.35,0,6,x,y).BoundBox for x,y in panel.rear_mounts)
for wire_length in (45,50,55):
    bounds=cable_bounds if wire_length==50 else panel.make_harness(wire_length)[3]
    for cell in bounds:
        assert cell.XMin>80 and cell.XMax<139 and cell.YMin>1 and cell.YMax<23.4
        assert cell.ZMin>.1 and cell.ZMax<5.9
        assert not any(cell.intersect(o) for o in cable_obstacles),('wire envelope',wire_length,cell)
assert antenna.distToShape(dial_sweep)[0] > 9
print('Controls: diametral sweep vs bottomed keys, mm',dial_sweep.distToShape(move(join(cap_shapes),z=-4))[0],flush=True)
print('Controls: QT wire route length, mm',wire_len,'underside QT/main board',back.distToShape(pcb)[0],flush=True)
# Add the underside actuator, solder terminals and flexible wire routes.
motor, red_pad, blue_pad, lead_tape = haptic_mount.reservations()
haptics = in_group(doc, 'WASD haptics • PCB underside')
feature(doc, 'M1100 • LEADER LD0832AA-0099F actuator envelope', motor, '167465', group=haptics)
feature(doc, 'M1100.1 • OUT+ hand-solder joint', red_pad, 'c9a26a', group=haptics)
feature(doc, 'M1100.2 • OUT− hand-solder joint', blue_pad, 'c9a26a', group=haptics)
feature(doc, 'Insulating tape • lead strain relief', lead_tape, '4a3d61', 65, haptics)

# Limit solid checks to the left-hand region occupied by the wire.
def near_haptics(shape):
    return join([solid for solid in shape.Solids
                 if solid.BoundBox.XMin < 60 and solid.BoundBox.XMax > 35
                 and solid.BoundBox.YMin < 12 and solid.BoundBox.YMax > -33])

haptic_obstacles = {
    'PCB': pcb,
    'switches': near_haptics(join(switch_shapes)),
    'LEDs': near_haptics(join(pixel_shapes)),
    'tray': left,
    'battery reserve': pack_limit,
}
for part_name, shape in [('actuator', motor), ('red solder joint', red_pad),
                         ('blue solder joint', blue_pad), ('tape', lead_tape)]:
    for obstacle_name, obstacle in haptic_obstacles.items():
        interference = shape.common(obstacle).Volume
        assert interference < 1e-4, (part_name, obstacle_name, interference)
    if part_name == 'actuator':
        print('Haptic actuator clearance, mm',
              {key: round(obs.distToShape(shape)[0], 3)
               for key, obs in haptic_obstacles.items() if key != 'PCB'}, flush=True)

wire_clearances = {key: float('inf') for key in haptic_obstacles if key != 'PCB'}
for length in (25, 27, 29):
    red_lead, blue_lead = (haptic_mount.sweep_lead(side, length) for side in (-1, 1))
    assert red_lead.common(blue_lead).Volume < 1e-4
    for wire in (red_lead, blue_lead):
        for obstacle_name, obstacle in haptic_obstacles.items():
            interference = wire.common(obstacle).Volume
            assert interference < 1e-4, (length, obstacle_name, interference)
            if obstacle_name != 'PCB':
                distance = obstacle.distToShape(wire)[0]
                wire_clearances[obstacle_name] = min(wire_clearances[obstacle_name], distance)
    if length == 27:
        feature(doc, 'M1100 red lead • 27 mm routed', red_lead, 'ad382a', group=haptics)
        feature(doc, 'M1100 blue lead • 27 mm routed', blue_lead, '245ab3', group=haptics)
print('Haptic lead clearance across 25–29 mm, mm',
      {key: round(value, 3) for key, value in wire_clearances.items()}, flush=True)
mount_hardware = in_group(doc, 'Case fasteners • click to inspect')
mount_nuts = join([case_fasteners.seated_nut(x,y,-pcb_t) for x,y in mounts])
assert len(mount_nuts.Solids)==9 and mount_nuts.isValid()
nut_feature = feature(doc,'M2.5 hex nuts • nine side-loaded DIN 934 nuts',mount_nuts,'9da5aa',group=mount_hardware)
nut_feature.addProperty('App::PropertyString','Installation','Hardware')
nut_feature.Installation = 'Slide each nut flat from the tray interior. The pocket holds the flats as the screw seats the nut against its roof.'
for obstacle in (left,right,pcb,antenna):
    assert mount_nuts.common(obstacle).Volume < .0001
front_screws = [case_fasteners.button_screw(x,y,0,6) for x,y in mounts[:4]]
rear_screws = [case_fasteners.button_screw(x,y,8.4,16) for x,y in panel.rear_mounts]
seam_screws, seam_nuts = case_fasteners.seam_hardware()
for label,shape in [('Front PCB screws • four M2.5 × 6', join(front_screws)),
                    ('Rear cover screws • five M2.5 × 16', join(rear_screws)),
                    ('Seam screw • two M3 × 12', seam_screws),
                    ('Seam nut • two captured M3 nuts', seam_nuts)]:
    feature(doc,label,shape,'97a0a3',group=mount_hardware)
display_harness.apply(doc, Path(os.environ.get('KEYBOARD_QT_SOCKET_STEP', out.parent/'electronics'/'Keyboard_Controls.3dshapes'/'XY-SM04B-SRSS-TB.step')))
# Carry the electrical identifiers into the MCAD tree so the nine wires can be audited.
for prefix,ref,pin,net in [('M1100 red lead','M1100',1,'Net-(U1100-OUT+)'),
                           ('M1100 blue lead','M1100',2,'Net-(U1100-OUT-)')]:
    obj = next(o for o in doc.Objects if o.Label.startswith(prefix))
    obj.addProperty('App::PropertyString','FromPin','Wiring')
    obj.FromPin = f'{ref}.{pin}'
    obj.addProperty('App::PropertyString','Net','Wiring')
    obj.Net = net
for pin,tag,net in [(1,'POS','PACK_POS'),(2,'NTC','PACK_NTC'),(3,'GND','GND')]:
    obj = doc.getObject('PackHarness'+tag)
    for field,val in [('FromPin',f'J600.{pin}'),('Net',net)]:
        if field not in obj.PropertiesList:
            obj.addProperty('App::PropertyString',field,'Wiring')
        setattr(obj,field,val)
save(doc,'keyboard-placement.FCStd')
with (out/'key-centers.csv').open('w',newline='') as f:
    writer=csv.writer(f)
    writer.writerow(['switch','legend','width_u','stem_x_mm','stem_y_mm','led_x_mm','led_y_mm'])
    for n,legend,w,x,y in keys:
        writer.writerow([f'SW{n}',legend,w,f'{x:.5f}',f'{-y:.5f}',f'{x:.5f}',f'{-y-led_offset:.5f}'])
for obj in (left,right,pcb,plate): print('Size',obj.BoundBox,'solid count',len(obj.Solids),flush=True)
print('Case / pack separation:',pack_box.distToShape(join([left,right]))[0],flush=True)
print('PCB / aperture and corner validation complete',flush=True)
