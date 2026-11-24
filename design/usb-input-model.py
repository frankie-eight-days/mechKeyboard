"""Cold and already-powered USB contact screening. Run with Python 3 and NumPy 2 or later.

Time is in microseconds, capacitance in microfarads, inductance in
microhenries, and resistance in ohms. The divider state is input-referred.
See usb-input-transient.md for the circuit, corner choices and limitations.
"""

from itertools import product

import numpy as np


def transient(inductance, source_r, direct_c, damping_c, damping_r, rise):
    # State order: cable current, raw VBUS, damping capacitor, filtered OV input.
    monitor_tau = 8.55
    a = np.array(
        [
            [-source_r / inductance, -1 / inductance, 0, 0],
            [1 / direct_c, -1 / (damping_r * direct_c), 1 / (damping_r * direct_c), 0],
            [0, 1 / (damping_r * damping_c), -1 / (damping_r * damping_c), 0],
            [0, 1 / monitor_tau, 0, -1 / monitor_tau],
        ]
    )
    poles, modes = np.linalg.eig(a)
    settled = np.array([0, 1, 1, 1])
    residues = modes * np.linalg.solve(modes, -settled)
    time = np.arange(0, rise + 110, 0.02)
    exponential = np.exp(poles[:, None] * time)
    if rise:
        # A linear ramp is a moving average of the unit-step response.
        delayed = np.exp(poles[:, None] * np.maximum(time - rise, 0))
        kernel = (exponential - delayed) / (poles[:, None] * rise)
        steady = settled[:, None] * np.minimum(time / rise, 1)
    else:
        kernel = exponential
        steady = settled[:, None]
    response = (steady + np.einsum("ij,jk->ik", residues, kernel)).real
    cable_i, raw, damped, monitor = response
    resistor_power = (raw - damped) ** 2 / damping_r
    energy = np.sum((resistor_power[:-1] + resistor_power[1:]) * 0.01)
    return np.array(
        [cable_i.max(), raw.max(), monitor.max(), resistor_power.max(), energy]
    )


def sweep(direct_capacitances, rise):
    parameters = product(
        [0.15, 0.35, 0.7, 1.2, 2.0],
        [0.08, 0.15, 0.3, 0.5],
        direct_capacitances,
        [3.0, 4.0, 5.17],
        [0.99, 1.01],
    )
    return np.max([transient(*corner, rise) for corner in parameters], axis=0)


def live_matrix(corner):
    """State: cable A, raw V, C201 V, pass-path A, protected V, reservoir V."""
    l, rs, c0, c1, lq, rq, c8, cb, rb, r1 = corner
    return np.array(
        [
            [-rs / l, -1 / l, 0, 0, 0, 0],
            [1 / c0, -1 / (r1 * c0), 1 / (r1 * c0), -1 / c0, 0, 0],
            [0, 1 / (r1 * c1), -1 / (r1 * c1), 0, 0, 0],
            [0, 1 / lq, 0, -rq / lq, -1 / lq, 0],
            [0, 0, 0, 1 / c8, -1 / (rb * c8), 1 / (rb * c8)],
            [0, 0, 0, 0, 1 / (rb * cb), -1 / (rb * cb)],
        ]
    )


def live_sweep():
    # Pre-event initial charge is equilibrium at specified source and load.
    # An on-state rail during an arbitrary contact sequence may start elsewhere.
    times = np.r_[
        np.arange(0, 12, 0.02), np.arange(12, 80, 0.1), np.arange(80, 390, 0.5)
    ]
    limits = np.zeros(16)
    for k in product(
        [0.15, 0.7, 2],
        [0.08, 0.5],
        [0.6, 1.2],
        [3, 5.17],
        [0.003, 0.03],
        [0.012, 0.04],
        [4.7, 9],
        [106, 170],
        [0.098, 0.152, 0.252],
        [0.99, 1.01],
    ):
        val, vec = np.linalg.eig(live_matrix(k))
        phase = np.exp(val[:, None] * times)
        rs, rq, rb = k[1], k[5], k[8]
        sources = np.array(
            [[0, -1, -1, 0, -1, -1], [1, -rs, -rs, 1, -rs - rq, -rs - rq]]
        ).T
        drives = np.linalg.solve(vec, sources)
        step, release = np.einsum("pi,pt->it", vec[4, :, None] * drives, phase).real
        cap_step, cap_release = (
            np.einsum("pi,pt->it", (vec[4] - vec[5])[:, None] * drives, phase).real / rb
        )
        # Independent peak alignment over all relative event phases is an upper bound.
        a = max(0, step.max())
        b = max(0, release.max())
        currents = [
            1.85 * cap_step,
            2.66 * cap_release,
            1.15 * cap_step + 2.66 * cap_release,
        ]
        peak_current = max(abs(w).max() for w in currents)
        power = 0.102 * peak_current**2
        energy = max(0.102 * np.trapezoid(w**2, times) for w in currents)
        group = [
            5.5 + 1.15 * a,
            5.5 + 1.85 * a,
            5.5 + 1.30 * b,
            5.5 + 2.66 * b,
            5.5 + 1.15 * a + 1.30 * b,
            5.5 + 1.15 * a + 2.66 * b,
            5.5 + 1.85 * a + 1.30 * b,
            5.5 + 1.85 * a + 2.66 * b,
            peak_current,
            power,
            energy,
            1.85 * abs(cap_step).max() + 2.66 * abs(cap_release).max(),
            0.102 * (1.85 * abs(cap_step).max() + 2.66 * abs(cap_release).max()) ** 2,
            0.102
            * (
                1.85 * np.sqrt(np.trapezoid(cap_step**2, times))
                + 2.66 * np.sqrt(np.trapezoid(cap_release**2, times))
            )
            ** 2,
            0.0,
            0.0,
        ]
        # Open contact interrupts cable current. Until UV trips, a 1.3 A load
        # discharges protected ceramics first. Keep all five capacitor/FET
        # states through a sampled 1..150 us interruption and recover at zero load.
        aopen = live_matrix(k)[1:, 1:]
        initial_raw = 5.50 - 1.30 * rs
        initial_protected = initial_raw - 1.30 * rq
        state = np.array(
            [initial_raw, initial_raw, 1.30, initial_protected, initial_protected]
        )
        affine = np.zeros((6, 6))
        affine[:5, :5] = aopen
        affine[3, 5] = -1.30 / k[6]
        # Affine open system has an integrator. Use a Taylor matrix exponential
        # for its fixed 1-us propagator (squaring keeps the Taylor norm small).
        block = affine / 256
        delta = np.eye(6)
        trans = delta.copy()
        for order in range(1, 15):
            delta = delta @ block / order
            trans += delta
        for _ in range(8):
            trans = trans @ trans
        aug = np.r_[state, 1.0]
        raw_min = 10.0
        starts = []
        for gap in range(1, 151):
            aug = trans @ aug
            raw_min = min(raw_min, aug[0])
            if raw_min < 3.65:
                break
            if gap in (1, 2, 5, 10, 20, 35, 50, 75, 100, 125, 150):
                starts.append(np.r_[0.0, aug[:5]] - [0, 5.5, 5.5, 0, 5.5, 5.5])
        if starts:
            coeff = vec[4, :, None] * np.linalg.solve(vec, np.array(starts).T)
            group[-2] = 5.5 + np.max(np.einsum("pi,pt->it", coeff, phase).real)
            group[-1] = len(starts)
        if not np.isfinite(group).all():
            raise ArithmeticError(f"Non-finite response at corner {k}")
        limits = np.maximum(limits, group)
    return limits


def ripple(harmonics=25):
    """Specified CCM current ramp Fourier coefficients, realistic illustrative PDN.
    Units MHz, uH, uF, volts, ohms. Circuit reconstruction uses complex RMS phasors.
    """
    from math import pi, sqrt
    from cmath import exp

    frequency, duty = 1.5, 3.52 / 5
    mean = 1.04 + (0.12 + 0.75 / 0.85) / 3.52
    di = 5 * duty * (1 - duty) / frequency
    parallel = lambda *z: 1 / sum(1 / x for x in z)
    rows = []
    for n in range(1, harmonics + 1):
        jw = 2j * pi * frequency * n
        cap = lambda c, r, nh: r + jw * nh / 1000 + 1 / (jw * c)
        cable = 0.15 + jw * 0.7
        c202, rcraw = cap(0.825, 0.01, 0.6), 1 + cap(4, 0.01, 0.8)
        raw = parallel(cable, c202, rcraw)
        pair = 0.020 + jw * 0.008
        c800, rcprot = cap(7.276, 0.00446, 0.6), 0.10 + cap(141, 0.04, 2)
        prot = parallel(pair + raw, c800, rcprot)
        u800 = 0.034 + jw * 0.005
        c601 = cap(0.825, 0.0096, 0.6)
        limited = parallel(u800 + prot, c601)
        q1 = 0.026 + jw * 0.003
        c602, c603 = cap(7.276, 0.00446, 0.6), cap(0.1, 0.02, 0.5)
        k = 2j * pi * n
        e = exp(-k * duty)
        integral = (1 - e) / k
        ramp_integral = (integral - duty * e) / k
        pulse = sqrt(2) * ((mean - di / 2) * integral + di / duty * ramp_integral)
        # 10 ns linear edge spread (centred moving average).
        pulse *= np.sinc(n * frequency * 0.010)
        pmid = pulse * parallel(c602, c603, q1 + limited)
        vlim = pmid * limited / (q1 + limited)
        vprot = vlim * prot / (u800 + prot)
        vraw = vprot * raw / (pair + raw)
        rows.append(
            [
                pulse,
                pmid / c602,
                pmid / c603,
                vlim / c601,
                vprot / c800,
                vprot / rcprot,
                vraw / c202,
                vraw / rcraw,
                vraw / cable,
                pmid,
                vlim,
                vprot,
                vraw,
            ]
        )
    vals = np.array(rows)
    phase = np.exp(
        2j * np.pi * np.arange(1, harmonics + 1)[:, None] * np.arange(1200) / 1200
    )
    waves = np.sqrt(2) * np.einsum("hi,ht->it", vals, phase).real
    return (
        1000 * abs(vals[0]),
        1000 * np.sqrt((abs(vals) ** 2).sum(axis=0)),
        1000 * np.ptp(waves, axis=1),
    )


if __name__ == "__main__":
    print("Cold: rise us, cable A, raw V, input-referred OV V, R204 W and uJ.")
    for rise in (0, 1, 10, 100):
        print(
            rise,
            np.round(sweep([0.6, 0.9, 1.2], rise) * [5.5, 5.5, 5.5, 30.25, 30.25], 3),
        )
    print(
        "Live: 4.35/3.65-5.5 steps; 1.30/2.66A load removal; 4.35/3.65-asynchronous combined 1.30/2.66A; branch I A, R208 W, uJ; arbitrary-phase sum bounds A/W/uJ, gap-reconnect V and gap count."
    )
    print(np.round(live_sweep(), 4))
    print(
        "AC order: Q2 C602 C603 C601 C800 R208 C202 R204 cable PMID LIMITED USB_VBUS raw."
    )
    print("Fundamental RMS, reconstructed RMS, reconstructed pp; mA or mV.")
    print(np.round(ripple(), 3))
