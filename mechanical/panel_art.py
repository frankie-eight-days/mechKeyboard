"""Engraved rear-cover options for the keyboard. Dimensions are in millimetres."""

from pathlib import Path
import math

import FreeCAD as App
import MeshPart
import Part

V = App.Vector
STYLES = ('circuit', 'forest', 'skyline')
FACE_Z = 8.4
DEPTH = 0.4
STROKE = 0.90


def _trace(points, width, bottom, height):
    """Make a constant-width tool with round ends and corners."""
    radius = width / 2
    segments = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        dx, dy = (x1 - x0) / length, (y1 - y0) / length
        offset = V(-dy * radius, dx * radius, 0)
        p, q = V(x0, y0, bottom), V(x1, y1, bottom)
        corners = [p + offset, q + offset, q - offset, p - offset]
        segments.append(Part.Face(Part.makePolygon(corners + corners[:1])).extrude(V(0, 0, height)))
    segments.extend(Part.makeCylinder(radius, height, V(x, y, bottom)) for x, y in points)
    return segments


def _circuit(side):
    if side == 'left':
        traces = [
            [(20, 6), (34, 6), (38, 10), (54, 10), (57, 13), (65, 13)],
            [(20, 10), (31, 10), (36, 15), (51, 15)],
            [(20, 15), (28, 15), (34, 21), (59, 21), (63, 17), (65, 17)],
            [(27, 19), (31, 23), (75, 23), (81, 17), (92, 17)],
            [(65, 8), (75, 8), (80, 13), (104, 13), (111, 20), (118, 20)],
            [(81, 7), (97, 7), (100, 10), (114, 10)],
            [(63, 5), (47, 5), (44, 8)],
            [(86, 21), (99, 21), (103, 17)],
        ]
    else:
        traces = [
            [(215, 7), (223, 7), (227, 11), (241, 11), (247, 5), (254, 5)],
            [(215, 12), (220, 12), (225, 17), (239, 17)],
            [(215, 18), (220, 18), (225, 23), (243, 23), (250, 16), (255, 16)],
            [(246, 11), (248, 13), (255, 13)],
            [(298, 7), (304, 7), (308, 11), (308, 18), (304, 22)],
        ]
    dots = [(points[0][0], points[0][1], 1.95) for points in traces]
    return traces, dots


def _tree(x, y, height):
    """A three-tier evergreen outline at the given ground line."""
    half = height * .28
    return [(x-half, y), (x+half, y), (x+half*.51, y+height*.33),
            (x+half*.75, y+height*.33), (x+half*.30, y+height*.61),
            (x+half*.53, y+height*.61), (x, y+height),
            (x-half*.53, y+height*.61), (x-half*.30, y+height*.61),
            (x-half*.75, y+height*.33), (x-half*.51, y+height*.33), (x-half, y)]


def _forest(side):
    if side == 'left':
        traces = [
            [(19, 12), (34, 22), (42, 17), (52, 22.5), (60, 16), (75, 23),
             (90, 15), (103, 20), (119, 11)],
            [(19, 5), (29, 5), (44, 6.2), (58, 4.7), (72, 5.8), (84, 4.7),
             (101, 6.4), (118, 5.2)],
            *[_tree(x, y, h) for x, y, h in [(28, 6.5, 8.4), (38, 7.2, 11),
              (49, 7.2, 7.0), (65, 6.2, 8.4), (77, 7.5, 11.2), (94, 7.4, 5.2), (111, 6.9, 9.3)]],
        ]
        dots = [(100, 22, 1.65), (106, 22.8, 1.15), (114.5, 20.3, 1.05)]
    else:
        traces = [
            [(214, 14), (224, 21), (234, 16), (241, 22), (253, 17), (257, 13)],
            [(214, 4.4), (221, 4.9), (232, 5.4), (245, 4.8), (258, 5.7)],
            *[_tree(x, y, h) for x, y, h in [(220, 6.5, 7), (230, 7.2, 10),
              (241, 6.5, 7), (253, 7.5, 9.1), (303, 5.3, 11)]],
        ]
        dots = [(303, 20.2, 1.80)]
    return traces, dots


def _skyline(side):
    if side == 'left':
        traces = [
            [(18, 6), (33, 6), (33, 12), (39, 12), (39, 17), (47, 17), (47, 10),
             (53, 10), (53, 21), (66, 21), (66, 9), (75, 9), (75, 15), (82, 15),
             (82, 12), (88, 12), (88, 22), (99, 22), (99, 14), (106, 14),
             (106, 8), (118, 8)],
            [(54.5, 23), (63.5, 23)],
            [(91.5, 23.6), (95.5, 23.6)],
            [(36, 8), (48, 8), (50.5, 5.5), (80, 5.5)],
            [(78, 8), (83, 8), (86, 5), (118, 5)],
            [(17, 20), (28, 20), (31, 17)],
            [(21, 16), (26, 16)],
            [(104, 22), (111, 22), (118, 15)],
        ]
        dots = [(x, y, 1.05) for x, columns in
                [(43, [14.5, 12, 9.9]), (57, [18, 15, 12]), (62.5, [18, 15, 12]),
                 (92, [19.5, 17, 14.5, 12]), (96, [19.5, 17, 14.5])]
                for y in columns]
    else:
        traces = [
            [(214, 7), (221, 7), (221, 12), (225, 12), (225, 20), (235, 20),
             (235, 10), (243, 10), (243, 16), (248, 16), (248, 8), (256, 8)],
            [(229, 22), (231.5, 22)],
            [(215, 4.4), (253, 4.4)],
            [(298, 6), (304, 6), (304, 13), (308, 13), (308, 21), (298, 21)],
        ]
        dots = [(x, y, 1.10) for x, rows in [(228, [17.5, 15, 12.5]), (232, [17.5, 15, 12.5]),
                                (302, [18, 15.7, 13.3])] for y in rows]
    return traces, dots


_PATTERN = {'circuit': _circuit, 'forest': _forest, 'skyline': _skyline}


def build_variant(cover, style, side):
    """Return an existing cover with shallow grooves cut into its outer face."""
    paths, stipples = _PATTERN[style](side)
    bottom, cutter_height = FACE_Z - DEPTH, DEPTH + 0.06
    primitives = []
    for path in paths:
        primitives.extend(_trace(path, STROKE, bottom, cutter_height))
    primitives.extend(Part.makeCylinder(d/2, cutter_height, V(x, y, bottom))
                      for x, y, d in stipples)
    cutter = primitives[0].multiFuse(primitives[1:]).removeSplitter()
    assert cutter.isValid()
    groove = cover.common(cutter)
    # Art may not cross an external edge, a mounting hole, or the controls'
    # windows. Complete area coverage is required through the engraving depth.
    area = cutter.Volume / cutter_height
    assert abs(groove.Volume - area * DEPTH) < 0.001, (style, side, groove.Volume, area * DEPTH)
    # Prove the full 2.0 mm web below every groove, including stipples.
    web = cutter.copy()
    web.translate(V(0, 0, -cutter_height))
    for step in range(4):
        assert abs(cover.common(web).Volume - cutter.Volume) < 0.001, (style, side, step)
        web.translate(V(0, 0, -cutter_height))
    web.translate(V(0, 0, 5 * cutter_height - 2.0))
    assert abs(cover.common(web).Volume - cutter.Volume) < 0.001, (style, side)
    variant = cover.cut(cutter).removeSplitter()
    assert variant.isValid() and len(variant.Solids) == 1, (style, side)
    assert abs(cover.Volume - variant.Volume - groove.Volume) < 0.001
    return variant


def export_variants(covers, destination):
    """Export the existing mounting interfaces with each of the three motifs."""
    destination = Path(destination)
    destination.mkdir(exist_ok=True)
    for style in STYLES:
        for side, cover in zip(('left', 'right'), covers):
            variant = build_variant(cover, style, side)
            variant.rotate(V(), V(1, 0, 0), 180)
            b = variant.BoundBox
            # OCC can overestimate Z extent at the OLED loft. The outer
            # panel face is the exact print datum after the flip.
            variant.translate(V(-b.XMin, -b.YMin, FACE_Z))
            mesh = MeshPart.meshFromShape(Shape=variant, LinearDeflection=.06, AngularDeflection=.20)
            assert mesh.isSolid(), (style, side)
            printed = mesh.BoundBox
            assert abs(printed.ZMin) < 1e-4, (style, side, printed.ZMin)
            assert max(printed.XLength, printed.YLength) < 220
            mesh.write(str(destination / f'{style}-rear-cover-{side}.stl'))
            print(f'{style} {side}: {printed.XLength:.2f} × {printed.YLength:.2f} × {printed.ZLength:.2f} mm, '
                  f'{mesh.CountFacets:,} facets, closed solid', flush=True)
