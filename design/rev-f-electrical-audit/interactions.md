# Power, analog and placement checks

The positive and negative headroom columns in supply-pins.csv distinguish a **stated operating case** from a device limit. A blank value means that the source or data sheet does not bound that side. The zeroes for ground pads establish schematic connectivity. Real return paths can have voltage drop. The file enumerates all 19 U-designated parts, all 67 pixel supplies/returns, connected external power contacts, internal bias/energy-storage nodes and deliberate NC U600.5. The raw pin inventory also includes the supply-strapped logic inputs. Distinct internal absolute limits for SW and BTST must be applied to their specified voltage references.

## Supply behavior by state

| Condition | Result and weakest link |
|---|---|
| Regulated 3V3 | U700 at 3.3 V ±1.5% gives 3.2505–3.3495 V **at the data sheet's 1 mA accuracy test**. The FUSB supply minimum is 2.85 V. The radio's normal-mode VCC maximum is 3.6 V. The upper operating headroom of both U100 VCC and U1102 VCCB is 250.5 mV in this screen. At cold boot U100 separately requires VCC to rise from 0 to 1.7 V within 60 ms. The board's loaded transient is open. [u-blox Tables 6–7](https://content.u-blox.com/sites/default/files/BMD-340_DataSheet_UBX-19033353.pdf) · [TPS63900 §6.5](https://www.ti.com/lit/ds/symlink/tps63900.pdf) |
| USB high and low | At 4.40 V under a 1.30 A load and 40 mΩ combined warm resistance, the protected PHY feed is 4.348 V, 2 mV below its 4.35 V requirement. A 5.50 V feed leaves zero upper operating margin before a transient. The prior live 6 V source fault reaches 5.824 V at the radio against 5.80 V absolute. At a 9 V source step the prior protected-node sample also exceeds U800's 6 V absolute rating. These are modeled fault stimuli. No 9 V contract is requested. [Reproduction](../usb-live-ov-check.py) · [USB transient study](../usb-input-transient.md) |
| No-pack suspend | For 4.35 V protected input, assumed 0.38 V diode and 3.353 kΩ, maximum power available to a resistive-equivalent retention load is (4.35−0.38)²/(4×3353) = 1.175 mW at an optimal 1.985 V load point. At 80% converter efficiency that is 0.285 mA at 3.3 V. Real converter input need not sit at that optimum. The separately required connector suspend-current limit cannot establish logic-rail survival. [Limiter study](../usb-limit.md) |
| SYS and pack | The 3.20–4.30 V SYS interval in the supply ledger is a planning screen for normal active accessories. The battery can legally reach 2.75 V, and SYS drops under load. Once at the cell floor, U700 requires SYS−VD800 ≥1.8 V. U900 should already be inhibited near 3.07 V. Neither event guarantees pack disconnection. A high SYS bound must include charger regulation and haptic braking. The 4.18 V CV plus 0.4% test gives 4.19672 V. [Charger §§7.3–7.5](https://www.ti.com/lit/ds/symlink/bq25622.pdf) |
| RGB | The 4.844–5.145 V range is the boost divider/reference screen. A pixel at the high end has 355 mV of upper working margin to 5.50 V. At the low end it has 1.144 V of lower working margin to 3.70 V before route loss or ripple. PG and data levels can fail earlier. No separate absolute supply rating was identified for the LED. Addressable output data levels, aligned PWM, bus current and load-release overshoot remain separate checks. [RGB study](../rgb-power.md) |
| Haptics | 1.8 V ±1.5% gives 1.773–1.827 V at the LDO accuracy test, with actual input headroom and load/line regulation still to include. U1100 draws motor energy from SYS, with an absolute VDD maximum of 5.5 V. The TCA9416 isolates the logic branch after power-off. Driver EN does not independently cycle its SYS supply. Recovery after REG brownout has a >3.6 kV/s supply-ramp condition. [TI DRV2605L](https://www.ti.com/lit/ds/symlink/drv2605l.pdf) |
| Off-board OLED | J1000 pin 2 may see 3.231 V in the 35 mA harness/switch screen. Even a zero-drop module regulator then misses the UG-2832HSWEG02 VBAT minimum of 3.3 V by 69 mV. Its VDD limit is 3.3 V maximum. The rev B breakout ties these rails. Nominal module performance and the two bare-glass limits are separate evidence. The module reset suffix, actual panel revision and guaranteed assembled VIN range remain open. [Breakout study](../display-and-volume.md) |

The capacitor audit uses a deliberately broader 4.45 V SYS stress allowance where specified, and 3.45 V on selected core parts for component screening. Those allowances serve a different purpose from the regulation and operating-point calculations. Neither set is a measured upper envelope. The [state table](states.csv) records 15 distinct states and faults.

## Input protection tolerance and recovery

A second calculation enumerated the fitted R205–R207 and R212–R213 initial tolerances plus their individual TCRs. It applies the LTC4365 492.5–507.5 mV input thresholds, 20–32 mV hysteresis and a ±10 nA leakage sensitivity. The leakage specification is characterized at VIN = 34 V. The test sweeps ±65 °C from the 25 °C reference for resistor tolerance, without assuming their TCR signs track. [LTC4365 electrical characteristics, p4](https://www.analog.com/media/en/technical-documentation/data-sheets/LTC4365.pdf) · [Run the calculation](check-corners.py)

| At the raw port | Initial resistor tolerance | With resistor temperature allowance |
|---|---:|---:|
| OV rising trip | 5.5435–5.7569 V | 5.5103–5.7916 V |
| OV falling re-enable threshold | 5.1826–5.5304 V | 5.1516–5.5638 V |
| UV falling trip | 3.7301–3.9384 V | 3.6987–3.9720 V |
| UV rising recovery threshold | 3.8820–4.1861 V | 3.8493–4.2219 V |

At the low trip corner, only 10 mV separates a static 5.50 V source from the OV decision. After an OV trip, a source returning to 5.50 V can still sit above that unit's falling recovery threshold. At the high UV corner the PHY can already be below 4.35 V long before protection trips. These facts require a recovery and brownout policy. The prior **5.775 V** detector threshold in the transient model is a separate sensitivity point. Replaying the same zero-rise model at a 5.7916 V detector threshold gives 5.834 V at the protected node after 23.345 µs for the 6 V step, and 6.724 V after 4.240 µs for the 9 V step. These are voltages at the sampled crossing before additional turn-off delay. The model still uses the original room-value cable and passive network. The result is a threshold sensitivity, not a single correlated full-temperature worst case.

## Battery thermistor window

The audit used **min/max sensor resistance from the actual 3602 resistance table** at 0, 25 and 45 °C. R602/603 and R607/608/609 vary independently by their 1% initial tolerance and 100 ppm/°C TCR over a conservative 65 °C displacement. Each margin below includes a 4.4 V reference, ±8 mV comparator offset and half the 25 mV maximum hysteresis window as an adverse threshold displacement. The 4.4 V REGN minimum is specified at a particular adapter/load test and U601 offset/hysteresis are characterized at the section's specified supplies and common-mode. No guaranteed full-assembly threshold at every temperature is inferred. [Sensor table p1](../../datasheets/mechanical/NTC-3602.pdf) · [TLV7042 §5.9](https://www.ti.com/lit/ds/symlink/tlv7042.pdf) · [Reproduction](check-corners.py)

| Case | Smallest modeled margin to intended comparator decision |
|---|---:|
| 0 °C, cold inhibit | +43.98 mV |
| 25 °C, inside window | +294.35 mV |
| 45 °C, hot inhibit | +99.12 mV |
| Open NTC, inhibit | +603.68 mV |
| NTC shorted to ground, inhibit | +2138.80 mV |

The static window is materially better supported than a nominal divider check alone. Open BAT+ with a still-connected NTC, a sensor displaced from the cell, REGN startup/decay, leakage and deglitch, and removing a valid charge request remain separate faults. Firmware needs to requalify charger state and recover the 100 mA startup limit in a source-qualified sequence. Full charge within two hours remains an estimate.

## Schematic-to-case transfer

Using the reviewed MX pads and switch-center CSV, the independent transfer check rotated **each actual assigned MX footprint by 180°** and compared every drilled hole diameter and coordinate with the mechanical model. All **351 drills for 67 switches** matched, including the stabilizers on the wide keys. The footprint origin is electrical pad 1. In board top-view coordinates, its position must be **stem X − 2.54 mm, stem Y + 5.08 mm**. The underside LED center is stem X, stem Y − 5.08 mm. Esc therefore has stem (9.525, 9.525), footprint origin (6.985, 14.605), LED center (9.525, 4.445) mm. The CSV retains the same conversion for each individual reference. [67 checked placements](key-placement-check.csv) · [Mechanical key map](../../mechanical/key-centers.csv)

The minimum nominal clearance between the nine Ø8 mm boss disks and a rectangular envelope around an LED window is 3.545 mm at SW7. The minimum to the switch contact copper disks is 3.109 mm at SW59. Neither calculation includes routing or copper pours. The radio keepout maps from the top-side module's local negative-X end to the keyboard's right edge by an in-plane 180° rotation. Keep FreeCAD +Y (rearward) distinct from PCB/key-map +Y (toward the typist). Cross-check J600 underside pin 1, the actuator pads, switch heights, plate and wire keepouts when transferring to the real PCB. Existing U200 land and J200 slot deviations are still open. No PCB layout or physical prototype was generated in this audit. [Pack connector transform](../pack-harness-review.md) · [Original library findings](../prelayout-review.md)
