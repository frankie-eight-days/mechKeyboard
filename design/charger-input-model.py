"""BQ25622 charge-mode screening. Uses A, V, µs, µF, µH and MHz."""

import math
import cmath

# Typical Samsung data at 4.75, 5.00 and 5.50 V, see the linked part pages.
C602_OLD = {4.75: 4.478, 5: 4.263, 5.5: 3.868}
C602_NEW = {4.75: 7.485, 5: 7.276, 5.5: 6.839}
C601 = {4.75: 0.839, 5: 0.825, 5.5: 0.797}


def cycle(vin, vsys, charge, led_amps, freq=1.5, inductance=1):
    duty = vsys / vin
    average = charge + (0.12 + 5 * led_amps / 0.85) / vsys
    ripple = vin * duty * (1 - duty) / (freq * inductance)
    # RMS of the ramped high-side input pulses with the DC component subtracted.
    rms = math.sqrt(average**2 * duty * (1 - duty) + duty * ripple**2 / 12)

    # Integrate i_cap = average*duty - i_L while the high side conducts.
    # End points and the optional single zero-crossing give all charge extrema.
    def charge_at(frac):
        return (
            (average * (duty - 1) + ripple / 2) * frac - ripple * frac**2 / (2 * duty)
        ) / freq

    zero = duty * (average * (duty - 1) + ripple / 2) / ripple
    extrema = [0.0, charge_at(duty)]
    if 0 < zero < duty:
        extrema.append(charge_at(zero))
    swing = max(extrema) - min(extrema)
    return duty, average, ripple, rms, swing


def network_fundamental():
    """One illustrative revision D network. Resistances and ESL are screening assumptions."""
    freq = 1.5
    jw = 2j * math.pi * freq
    par = lambda *zs: 1 / sum(1 / z for z in zs)

    def cap(c, r, l_nh):
        return r + jw * l_nh / 1000 + 1 / (jw * c)

    cable = 0.15 + jw * 0.7
    raw = par(cable, cap(0.825, 0.01, 0.6), 1 + cap(4, 0.01, 0.8))
    # Cable and capacitors use µH and µF with frequency in MHz.
    pass_path = 0.020 + jw * 0.008
    bulk_branch = 0.10 + cap(141, 0.04, 2)
    c800 = cap(7.276, 0.00446, 0.6)
    protected = par(pass_path + raw, c800, bulk_branch)
    limited = par(0.034 + jw * 0.005 + protected, cap(0.825, 0.0096, 0.6))
    q1 = 0.026 + jw * 0.003
    duty, avg, ripple, _, _ = cycle(5, 3.52, 1.04, 0.15)
    k = 2j * math.pi
    e = cmath.exp(-k * duty)
    i0 = (1 - e) / k
    i1 = (i0 - duty * e) / k
    pulse = math.sqrt(2) * ((avg - ripple / 2) * i0 + ripple / duty * i1)
    for tag, c, esr in [("old", 4.263, 0.00367), ("new", 7.276, 0.00446)]:
        bank = par(cap(c, esr, 0.6), cap(0.1, 0.02, 0.5))
        vpmid = pulse * par(bank, q1 + limited)
        vlimited = vpmid * limited / (q1 + limited)
        vphy = vlimited * protected / (0.034 + jw * 0.005 + protected)
        vraw = vphy * raw / (pass_path + raw)
        print(
            tag,
            "fundamental RMS mA, Q2 / C602 / C603 / C601 / cable / R204 / 3-cap reservoir / C800",
            *(
                round(1000 * abs(v), 2)
                for v in (
                    pulse,
                    vpmid / cap(c, esr, 0.6),
                    vpmid / cap(0.1, 0.02, 0.5),
                    vlimited / cap(0.825, 0.0096, 0.6),
                    vraw / cable,
                    vraw / (1 + cap(4, 0.01, 0.8)),
                    vphy / bulk_branch,
                    vphy / c800,
                )
            ),
        )


if __name__ == "__main__":
    print(
        "VIN, SYS, LED A, f MHz, L µH, charge A, IL A, inductor pp A, AC RMS A, old/new mVpp"
    )
    for vi, vo, led, f, l, ib, cscale in [
        (5, 3.52, 0, 1.5, 1, 1.04, 1),
        (5, 3.52, 0.15, 1.5, 1, 1.04, 1),
        (5, 4.18, 0.15, 1.5, 1, 1.04, 1),
        (4.75, 4.18, 0.15, 1.5, 1, 1.04, 1),
        (5.5, 3.52, 0.15, 1.35, 0.8, 1.097, 0.7),
    ]:
        d, mean, di, rms, q = cycle(vi, vo, ib, led, f, l)
        old, new = (
            1000 * q / (part[vi] * cscale + 0.1 * cscale)
            for part in (C602_OLD, C602_NEW)
        )
        print(*(round(z, 3) for z in (vi, vo, led, f, l, ib, mean, di, rms, old, new)))
    network_fundamental()
