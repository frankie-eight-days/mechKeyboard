"""Integral case joint in assembly coordinates, millimetres."""
import math

import FreeCAD as App
import Part

V = App.Vector


def add_joint(left, right, seam, floor, floor_top):
    lugs = []
    for y, key_y in [(-12, 1), (-87, -76)]:
        z = -9.4
        # The wall split has 0.20 mm relief. The opposing lug faces contact at X=seam.
        def lug(x, length):
            half_width = 6
            profile = [(-8, floor_top - .3), (8, floor_top - .3),
                       (8, floor_top), (half_width, floor_top + 2),
                       (half_width, z + 4), (-half_width, z + 4),
                       (-half_width, floor_top + 2), (-8, floor_top)]
            pts = [V(x, y + dy, h) for dy, h in profile]
            return Part.Face(Part.makePolygon(pts + pts[:1])).extrude(V(length, 0, 0))

        # A 45° roof above the circular clearance leaves the horizontal bore printable.
        hole = Part.makeCylinder(1.7, 15, V(seam - 6.2, y, z), V(1, 0, 0))
        a = 1.7 / math.sqrt(2)
        roof = [V(seam-6.2, y-a, z+a), V(seam-6.2, y, z+2*a), V(seam-6.2, y+a, z+a)]
        hole = hole.fuse(Part.Face(Part.makePolygon(roof + roof[:1])).extrude(V(15, 0, 0)))
        head_lug = lug(seam-5.6, 5.6).cut(hole)
        nut_lug = lug(seam, 7.7).cut(hole)

        # V-seat locates the lower corner of the top-loaded AF 5.5 mm nut.
        socket_x = seam + 2.9
        bottom = z - 5.5 / math.sqrt(3) - .04
        pocket = [V(socket_x, y+dy, h) for dy, h in [
            (0, bottom), (2.9, bottom + 2.9 / math.sqrt(3)), (2.9, z+5),
            (-2.9, z+5), (-2.9, bottom + 2.9 / math.sqrt(3))]]
        slot = Part.Face(Part.makePolygon(pocket + pocket[:1])).extrude(V(2.8, 0, 0))
        nut_lug = nut_lug.cut(slot)
        left = left.fuse(head_lug)
        right = right.fuse(nut_lug)
        lugs.extend([head_lug, nut_lug])

        # Coplanar floor tongues align the halves without a snap fit or support.
        def key(x0, end, half, z0, height):
            shape = [(x0, -half), (end-1, -half), (end, -half+1),
                     (end, half-1), (end-1, half), (x0, half)]
            pts = [V(x, key_y+dy, z0) for x, dy in shape]
            return Part.Face(Part.makePolygon(pts + pts[:1])).extrude(V(0, 0, height))
        tongue = key(seam-2, seam+5, 3.2, floor, floor_top-floor)
        relief = key(seam-2, seam+5.3, 3.5, floor-.2, floor_top-floor+.4)
        left = left.fuse(tongue)
        right = right.cut(relief)
    return left.removeSplitter(), right.removeSplitter(), lugs
