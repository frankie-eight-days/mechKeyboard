"""Regenerate a themed FreeCAD assembly from the current keyboard-placement.FCStd.

Use FreeCAD's bundled Python with its lib folder on PYTHONPATH. Pass forest or
city. The STL orientations match the assembly guide. All lengths are in mm.
"""
import argparse
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

import city_relief
import forest_relief

base = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('theme', choices=('forest', 'city'))
parser.add_argument('--assembly', type=Path, default=base.parent/'keyboard-placement.FCStd')
parser.add_argument('--output', type=Path, default=base)
args = parser.parse_args()
target = args.output / args.theme
target.mkdir(parents=True, exist_ok=True)
doc = App.openDocument(str(args.assembly.resolve()))
theme = forest_relief if args.theme == 'forest' else city_relief
color = (.33, .55, .43) if args.theme == 'forest' else (.79, .49, .32)
split_z = 7.55
V = App.Vector

def print_mesh(name, shape, angle=0, folder=target):
    assert shape.isValid() and len(shape.Solids) == 1, name
    oriented = shape.copy()
    if angle:
        oriented.rotate(V(), V(1, 0, 0), angle)
    mesh = MeshPart.meshFromShape(Shape=oriented, LinearDeflection=.045, AngularDeflection=.15)
    assert mesh.isSolid(), name
    bounds = mesh.BoundBox
    assert max(bounds.XLength, bounds.YLength, bounds.ZLength) <= 220, name
    mesh.translate(-bounds.XMin, -bounds.YMin, -bounds.ZMin)
    mesh.write(str(folder/(name+'.stl')))

for side in ('left', 'right'):
    tray = next(o for o in doc.Objects if o.Label.startswith(side.title()+' tray section'))
    cover = next(o for o in doc.Objects if o.Label.startswith(side.title()+' rear cover'))
    tray.Shape = theme.build_tray(tray.Shape, side)
    if App.GuiUp: tray.ViewObject.ShapeColor = color
    print_mesh(args.theme+'-tray-'+side, tray.Shape)
    plain = cover.Shape.copy()
    art = theme.build_cover(plain, side)
    if App.GuiUp: cover.ViewObject.ShapeColor = color
    if side == 'right':
        cover.Shape = art
        print_mesh(args.theme+'-cover-right', art, -90)
        continue
    lower = Part.makeBox(230,40,split_z+1,V(-10,-1,-1))
    upper = Part.makeBox(230,40,15,V(-10,-1,split_z))
    carrier = plain.common(lower).removeSplitter()
    skin = art.common(upper).removeSplitter()
    assert abs(skin.Volume + carrier.Volume - art.Volume) < .001
    cover.Shape = carrier
    cover.Label = 'Shared left OLED carrier and mounting sleeves'
    group = next(g for g in doc.Objects if g.TypeId == 'App::DocumentObjectGroup' and cover in g.Group)
    top = doc.addObject('Part::Feature', 'SculptedFace')
    top.Label = args.theme.title()+' • left relief face'
    top.Shape = skin
    if App.GuiUp: top.ViewObject.ShapeColor = color
    group.addObject(top)
    print_mesh(args.theme+'-cover-left-skin', skin)
    print_mesh('shared-left-carrier', carrier, 180, args.output)
doc.Label = args.theme.title()+' • 65% keyboard'
doc.recompute()
model = target/(args.theme+'-keyboard.FCStd')
doc.saveAs(str(model))
if not App.GuiUp:
    from theme_view import restore_view
    restore_view(args.assembly, model, top.Name, color)
