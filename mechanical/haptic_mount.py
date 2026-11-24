"""Underside actuator, hand-solder pads and lead envelope for the W key cluster."""
import FreeCAD as App
import Part

Vector = App.Vector
# Same datum as build_fit.py: +Y toward USB and Z=0 on the top of the PCB.
BODY_X, BODY_Y, PCB_BOTTOM = 47.75, -24.0, -1.60
PAD_Y = 5.00
PAD_PITCH = 2.54
LEAD_RADIUS = 0.30


def oblong_pad(x, y):
    """1.80 × 2.80 mm, bottom copper only, with a 0.25 mm solder halo."""
    radius = 1.15
    z = PCB_BOTTOM - 0.85
    height = 0.85
    left = x - radius
    shape = Part.makeBox(2 * radius, 1.00, height, Vector(left, y - 0.50, z))
    for dy in (-0.50, 0.50):
        shape = shape.fuse(Part.makeCylinder(radius, height, Vector(x, y + dy, z)))
    return shape.removeSplitter()


def lead_curve(side, depth):
    """Guide the insulated lead below number-row contacts before it rises to its land."""
    x0 = BODY_X + side * 0.70
    x1 = BODY_X + side * PAD_PITCH / 2
    start = Vector(x0, BODY_Y + 5.75, -3.30)
    trough = Vector(x1, -9.50, -depth)
    rise = Vector(x1, 0.75, -1.90)
    pad = Vector(x1, PAD_Y, -1.90)

    def bend(*poles):
        curve = Part.BezierCurve()
        curve.setPoles(poles)
        return curve.toShape()

    drop = bend(start, Vector(x0, -14.25, -3.30), Vector(x1, -12.5, -depth), trough)
    up = bend(trough, Vector(x1, -5.00, -depth), Vector(x1, -3.00, -1.90), rise)
    return Part.Wire([drop, up, Part.makeLine(rise, pad)])


def sweep_lead(side, length):
    min_depth, max_depth = 4.20, 12.00
    assert lead_curve(side, min_depth).Length < length < lead_curve(side, max_depth).Length
    for _ in range(22):
        depth = (min_depth + max_depth) / 2
        if lead_curve(side, depth).Length < length:
            min_depth = depth
        else:
            max_depth = depth
    edge = lead_curve(side, depth)
    assert abs(edge.Length - length) < 0.001
    start = edge.Edges[0]
    section = Part.Wire([Part.makeCircle(
        LEAD_RADIUS, start.valueAt(start.FirstParameter), start.tangentAt(start.FirstParameter)
    )])
    envelope = edge.makePipeShell([section], True, False)
    assert envelope.isValid() and len(envelope.Solids) == 1
    return envelope


def reservations():
    body = Part.makeCylinder(4.25, 3.90, Vector(BODY_X, BODY_Y, PCB_BOTTOM - 3.9))
    exit_tab = Part.makeBox(
        3.90, 3.60, 3.90, Vector(BODY_X - 1.95, BODY_Y + 3.50, PCB_BOTTOM - 3.90)
    )
    motor = body.fuse(exit_tab).removeSplitter()
    red_pad, blue_pad = (oblong_pad(BODY_X + side * PAD_PITCH / 2, PAD_Y) for side in (-1, 1))
    # Tape spans both insulated leads on the rise-to-pad side of the PCB.
    tape = Part.makeBox(5.40, 2.00, 0.85, Vector(BODY_X - 2.70, 1.0, PCB_BOTTOM - 0.85))
    return motor, red_pad, blue_pad, tape
