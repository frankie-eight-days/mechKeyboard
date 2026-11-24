"""Four independently swept conductors, offset normal to a two-bend shelf route."""
import math
import FreeCAD as App
import Part

V = App.Vector
WIRE_RADIUS = .43
OFFSETS = (-1.5, -.5, .5, 1.5)


def wire_path(y_center, desired_length, offset):
    # Conductor center spacing is 1 mm at the crimps. Offsetting an undulating
    # centerline in its local normal preserves this spacing around each bend.
    def make_curve(amplitude):
        points = []
        for station in range(65):
            t = station / 64
            phase = 4 * math.pi * t
            y = amplitude * (1 - math.cos(phase)) / 2
            slope = amplitude * 2 * math.pi * math.sin(phase) / 42
            normal_y = 1 / math.sqrt(1+slope*slope)
            z = 1.65 + .90 * (3*t*t - 2*t*t*t)
            points.append(V(92.4 + 42*t - offset*slope*normal_y,
                            y_center + y + offset*normal_y, z))
        spline = Part.BSplineCurve()
        spline.interpolate(points, Parameters=[i/64 for i in range(65)])
        return spline.toShape()

    lo, hi = 0., 10.
    for _ in range(20):
        amplitude = (lo + hi) / 2
        edge = make_curve(amplitude)
        if edge.Length < desired_length:
            lo = amplitude
        else:
            hi = amplitude
    assert abs(edge.Length - desired_length) < .001
    return edge


def sweeps(y_center, length):
    edges = [wire_path(y_center, length, offset) for offset in OFFSETS]
    for i,edge in enumerate(edges):
        for adjacent in edges[:i]:
            # Bound the circular insulation envelopes by their centerline spacing.
            clearance = edge.distToShape(adjacent)[0] - 2*WIRE_RADIUS
            assert clearance > .11, (i, length, clearance)
    wires = []
    bounds = []
    for edge in edges:
        count = math.ceil(edge.Length/.4)
        # Every point on the tube is within this radius of a sampled centerline station.
        radius = WIRE_RADIUS + edge.Length/(2*count) + .001
        for i in range(count+1):
            parameter = edge.LastParameter if i == count else edge.getParameterByLength(edge.Length*i/count)
            p = edge.valueAt(parameter)
            bounds.append(App.BoundBox(p.x-radius,p.y-radius,p.z-radius,
                                       p.x+radius,p.y+radius,p.z+radius))
        rings = []
        for i in range(65):
            param = edge.FirstParameter + (edge.LastParameter - edge.FirstParameter)*i/64
            center = edge.valueAt(param)
            normal = edge.tangentAt(param)
            circle = Part.Circle(center, normal, WIRE_RADIUS)
            circle.XAxis = V(0,0,1).sub(normal.multiply(normal.z))
            rings.append(Part.Wire([circle.toShape()]))
        wire = Part.makeLoft(rings, True, True)
        assert wire.isValid() and len(wire.Solids)==1
        wires.append(wire)
    return wires,bounds,edges
