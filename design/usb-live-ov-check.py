"""Screen protected VBUS up to the first filtered-OV threshold crossing.

Run with Python 3 and NumPy installed. This model starts with the
MOSFETs conducting and examines the response before comparing or turning them
off. It assumes a zero-rise source step and no pre-existing load.
"""

from pathlib import Path
from runpy import run_path

import numpy as np


model = run_path(str(Path(__file__).resolve().with_name('usb-input-model.py')))
# Cable L/R, C202/C201, MOSFET path L/R, C800, reservoir C/R, R204.
component_values = (0.7, 0.15, 0.825, 4.0, 0.008, 0.020, 7.276, 141.0, 0.14, 1.0)
ov_divider_r = 1 / (1 / 1.03e6 + 1 / 100e3)
ov_tau_us = 100e-12 * ov_divider_r * 1e6

# Add the input-referred OV divider pole as a seventh state following raw VBUS.
matrix = np.zeros((7, 7))
matrix[:6, :6] = model['live_matrix'](component_values)
matrix[6, 1] = 1 / ov_tau_us
matrix[6, 6] = -1 / ov_tau_us
poles, modes = np.linalg.eig(matrix)
time_us = np.arange(0, 30, 0.005)
initial = np.array([0, 5.5, 5.5, 0, 5.5, 5.5, 5.5])
threshold = 5.775

print(f'OV pole: {ov_tau_us:.3f} µs, VBUS thresholds are input-referred')
for source_voltage in (6.0, 9.0):
    steady = np.array([0, source_voltage, source_voltage, 0, source_voltage,
                       source_voltage, source_voltage])
    coefficients = np.linalg.solve(modes, initial - steady)
    modal_response = coefficients[:, None] * np.exp(poles[:, None] * time_us)
    response = steady[:, None] + np.einsum('nm,mt->nt', modes, modal_response).real
    crossing = np.flatnonzero(response[6] >= threshold)[0]
    print(f'5.50 → {source_voltage:.2f} V: OV reaches {threshold:.3f} V after '
          f'{time_us[crossing]:.3f} µs, raw VBUS {response[1, crossing]:.3f} V, '
          f'protected VBUS {response[4, crossing]:.3f} V')
