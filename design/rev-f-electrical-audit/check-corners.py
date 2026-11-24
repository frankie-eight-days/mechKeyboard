"""Recalculate selected Rev F DC corners. Run with Python 3; no dependencies."""
from itertools import product


def bounds(value, initial, ppm, temperature_delta):
    drift = ppm * 1e-6 * temperature_delta
    return (value * (1 - initial) * (1 - drift), value * (1 + initial) * (1 + drift))


def protection(name, upper, lower, direction):
    trip = []
    release = []
    for tops in product(*upper):
        rt = sum(tops)
        for rb, vref, current, hysteresis in product(lower, (.4925, .5075), (-10e-9, 10e-9), (.020, .032)):
            gain = 1 + rt / rb
            threshold = vref * gain + current * rt
            trip.append(threshold)
            release.append(threshold + direction * hysteresis * gain)
    print(f"{name}: trip {min(trip):.4f} to {max(trip):.4f} V, "
          f"return {min(release):.4f} to {max(release):.4f} V")


def thermistor(temp, resistance, threshold):
    # R602/603 form the sensor network. R607/608/609 form the independent window.
    # Use independent tolerance and TCR signs. This is deliberately conservative.
    values = [bounds(r, .01, 100, 65) for r in (5.23, 30.1, 30.1, 20., 49.9)]
    margins = []
    for top, shunt, ra, rb, rc in product(*values):
        for r in resistance:
            sensor = 0 if r == 0 else 1 / (1 + top / shunt + top / r)
            high = (rb + rc) / (ra + rb + rc)
            low = rc / (ra + rb + rc)
            if threshold == "cold inhibit":
                delta = sensor - high
            elif threshold == "hot inhibit":
                delta = low - sensor
            else:
                delta = min(sensor - low, high - sensor)
            margins.append(delta * 4.4 - .008 - .025 / 2)
    print(f"NTC {temp}, {threshold}: minimum margin {min(margins) * 1000:.2f} mV")


if __name__ == "__main__":
    # -40 to +85 C component stress envelope around the 25 C initial reference.
    # ILEAK limit test point is 34 V. Applied at the keyboard's 5 V as a sensitivity.
    for delta in (0, 65):
        print(f"Divider tolerance with up to {delta} °C displacement from 25 °C")
        protection("OV rising", [bounds(1e6, .001, 50, delta), bounds(30e3, .01, 100, delta)],
                   bounds(100e3, .001, 50, delta), -1)
        protection("UV falling", [bounds(1e6, .001, 50, delta)],
                   bounds(150e3, .01, 100, delta), +1)
    # BatterySpace 3602 resistance limits in kohms, p1. The comparator's 4.4 V
    # supply and 20.5 mV offset+hysteresis envelope are assumptions explained in report.
    for case in (("0 °C", (25.531, 28.606), "cold inhibit"), ("25 °C", (9.7, 10.3), "enable"),
                 ("45 °C", (4.7480, 5.2008), "hot inhibit"),
                 ("open circuit", (float('inf'),), "cold inhibit"), ("short to GND", (0,), "hot inhibit")):
        thermistor(*case)
